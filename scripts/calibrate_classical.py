"""Bounded train-ROI looks and validation-only classical calibration.

CLI outputs are exclusive: preserve previous evidence and use a new config/run
path. Held-out source files and labels are never opened. ROI homogeneity must be
visually established on raw training SAR before invoking this command.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from sar_water.benchmark import _segment_filtered,validation_search
from sar_water.data import (audit_pair,read_manifest,sha256_file,validate_splits,
                           verify_decoded_image_identity)
from sar_water.filters import FILTER_GRID,estimate_training_looks,filter_power
from sar_water.metrics import enl,summarize_water
from sar_water.segment import FIXED_GRID


def read_rois(path,membership):
    with Path(path).open(newline='',encoding='utf-8-sig') as stream:
        rois=list(csv.DictReader(stream))
    if not rois or any(membership.get(r['patch_id'])!='train' for r in rois):
        raise ValueError('looks estimation requires nonempty training-only ROIs')
    counts=Counter();seen=set()
    for row in rois:
        for name in ('y0','y1','x0','x1'):row[name]=int(row[name])
        key=tuple(row[name] for name in ('patch_id','y0','y1','x0','x1'))
        if key in seen:raise ValueError('duplicate ROI coordinates')
        seen.add(key);counts[row['patch_id']]+=1
        if row['y1']-row['y0']!=32 or row['x1']-row['x0']!=32 or min(row['y0'],row['x0'])<0:
            raise ValueError('each ROI must be a nonnegative 32 x 32 rectangle')
        if not row.get('suitability'):raise ValueError('raw visual suitability must be documented')
    if max(counts.values())>5:raise ValueError('at most five ROIs per patch')
    return rois


def _json(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')


def _relative(path,parent):
    return Path(os.path.relpath(Path(path).resolve(),Path(parent).resolve())).as_posix()


def _checked_patch(row):
    for kind in ('image','mask'):
        if not row.get(kind+'_sha256') or sha256_file(row[kind+'_path'])!=row[kind+'_sha256']:
            raise ValueError('development source hash changed: '+row['patch_id'])
    audited,patch=audit_pair(row)
    verify_decoded_image_identity(row,audited)
    if row.get('label_source')!='manual':raise ValueError('independent manual development labels required')
    return patch


def _fallbacks(patches):
    records=[];chosen={}
    for channel,thresholds in FIXED_GRID.items():
        candidates=[]
        for threshold in thresholds:
            counts={key:_segment_filtered(p,p.power,channel=channel,rule='fixed',threshold=threshold)['counts'] for key,p in patches.items()}
            summary=summarize_water(counts)
            record=dict(channel=channel,threshold_db=threshold,summary=summary)
            records.append(record);candidates.append(record)
        if any(r['summary']['pooled']['iou'] is None for r in candidates):raise ValueError('undefined raw validation fallback IoU')
        chosen[channel]=max(candidates,key=lambda r:r['summary']['pooled']['iou'])['threshold_db']
    return chosen,records


def _pilot(patches,looks):
    records=[]
    for method,settings in FILTER_GRID.items():
        for parameters in settings:
            start=perf_counter();shapes=[];means=[]
            for key,patch in patches.items():
                filtered=filter_power(patch.power,patch.input_valid,method=method,**parameters,**({'looks':looks} if method=='lee' else {}))
                assert filtered.shape==patch.power.shape
                assert np.isfinite(filtered[:,patch.input_valid]).all() and (filtered[:,patch.input_valid]>0).all()
                assert np.isnan(filtered[:,~patch.input_valid]).all()
                shapes.append(list(filtered.shape))
                means.append(dict(patch_id=key,mean_change_percent=[100*(float(np.mean(filtered[b,patch.input_valid],dtype=np.float64))/float(np.mean(patch.power[b,patch.input_valid],dtype=np.float64))-1) for b in range(2)]))
            records.append(dict(method=method,parameters=parameters,seconds=perf_counter()-start,patch_count=len(patches),bands=2,checks='native shape; finite positive valid power; invalid mask restored',radiometry=means))
    return records


def calibrate(manifest_path,splits_path,roi_path,config_path,output_path):
    manifest_path,splits_path,roi_path,config_path,output_path=map(Path,(manifest_path,splits_path,roi_path,config_path,output_path))
    if config_path.exists() or output_path.exists():raise FileExistsError('calibration outputs already exist; use new paths')
    started=perf_counter()
    input_paths=dict(manifest=manifest_path,splits=splits_path,training_roi=roi_path)
    input_hashes={name:sha256_file(path) for name,path in input_paths.items()}
    rows=read_manifest(manifest_path)
    with splits_path.open(newline='',encoding='utf-8-sig') as stream:split_rows=list(csv.DictReader(stream))
    membership={r['patch_id']:r['split'] for r in split_rows}
    if len(membership)!=len(split_rows):raise ValueError('duplicate split identifier')
    validate_splits(rows,membership)
    if any(r.get('split') and r['split']!=membership[r['patch_id']] for r in rows):raise ValueError('manifest/split membership conflict')
    rois=read_rois(roi_path,membership)
    by_id={r['patch_id']:r for r in rows};loaded={}
    def load(key):
        if membership[key]=='test':raise ValueError('calibration cannot access test source files')
        if key not in loaded:loaded[key]=_checked_patch(by_id[key])
        return loaded[key]
    train={key:load(key) for key in sorted({r['patch_id'] for r in rois})}
    for roi in rois:
        patch=train[roi['patch_id']];y0,y1,x0,x1=[roi[n] for n in ('y0','y1','x0','x1')]
        if y1>patch.input_valid.shape[0] or x1>patch.input_valid.shape[1] or not patch.input_valid[y0:y1,x0:x1].all():raise ValueError('ROI must be inside fully valid raw SAR')
        if roi.get('roi_class') in ('water','land'):
            target=1 if roi['roi_class']=='water' else 0
            if not patch.score_valid[y0:y1,x0:x1].all() or not np.all(patch.labels[y0:y1,x0:x1]==target):raise ValueError('documented ROI class must match valid training labels')
    looks=estimate_training_looks({key:dict(power=p.power,input_valid=p.input_valid) for key,p in train.items()},rois,membership)
    output_path.mkdir(parents=True);looks_path=output_path/'training_looks.json'
    looks.update(training_roi_sha256=input_hashes['training_roi'],manifest_sha256=input_hashes['manifest'],splits_sha256=input_hashes['splits'],frozen_before_validation_access_utc=datetime.now(timezone.utc).isoformat())
    _json(looks_path,looks)
    # Timing pilot uses at most five distinct-event training images, label-blind.
    pilot_keys=[];events=set()
    for row in rows:
        event=row.get('event_id') or row['patch_id']
        if membership[row['patch_id']]=='train' and event not in events:
            pilot_keys.append(row['patch_id']);events.add(event)
        if len(pilot_keys)==5:break
    pilot=_pilot({key:load(key) for key in pilot_keys},looks['looks'])
    validation={key:load(key) for key in sorted(membership) if membership[key]=='validation'}
    fallbacks,fallback_table=_fallbacks(validation)
    validation_start=perf_counter()
    result=validation_search(validation,membership,looks=looks['looks'],fallback_thresholds=fallbacks,cache_limit_bytes=100_000_000)
    validation_seconds=perf_counter()-validation_start
    repo=Path(__file__).resolve().parents[1]
    code_paths=['scripts/calibrate_classical.py']+[f'src/sar_water/{name}.py' for name in ('benchmark','data','filters','metrics','segment')]
    code_hashes={name:sha256_file(repo/name) for name in code_paths}
    config=json.loads((repo/'configs'/'experiment.json').read_text())
    pending=repo/'configs'/'development.json'
    if pending.exists():
        pending_config=json.loads(pending.read_text())
        if pending_config['real_data'].get('manifest_sha256')==sha256_file(manifest_path):config=pending_config
    real=config['real_data']
    real.update(status='upstream_development_subset_calibrated',split_frozen=True,calibration_frozen=True,
        manifest_path=_relative(manifest_path,config_path.parent),splits_path=_relative(splits_path,config_path.parent),
        manifest_sha256=sha256_file(manifest_path),splits_sha256=sha256_file(splits_path),
        training_roi_path=_relative(roi_path,config_path.parent),training_roi_sha256=sha256_file(roi_path),
        looks_artifact_path=_relative(looks_path,config_path.parent),looks_artifact_sha256=sha256_file(looks_path),
        effective_looks_by_band=dict(zip(('VV','VH'),looks['looks'])),fallback_thresholds_db=fallbacks,
        fallback_calibration='best pooled raw validation fixed-grid water IoU per band; ties retain first threshold in locked grid',
        selected_channel=result['common']['channel'],selected_threshold_strategy='shared_fixed_db' if result['common']['rule']=='fixed' else 'per_patch_otsu_db',
        selected_fixed_threshold_db=result['common']['threshold'],selected_filter_parameters={r['method']:r['parameters'] for r in result['primary']},
        selected_filter=result['selected_filter']['method'],calibration_frozen_utc=datetime.now(timezone.utc).isoformat())
    real.setdefault('provenance_limitation','Supplied development subset; spatial/event independence is not established.')
    config['methods']['midal_substitution'].update(status='not_admitted_not_piloted',reason='optional substitution declined to preserve locked dependency-light bilateral workflow and total runtime budget; no measured MIDAL compatibility or speed claim')
    config['cleanup_ablation']['status']='validation_complete_separate_from_primary'
    roi_diagnostics=[]
    for row in result['primary']:
        for key,p in train.items():
            filtered=filter_power(p.power,p.input_valid,method=row['method'],**row['parameters'],**({'looks':looks['looks']} if row['method']=='lee' else {}))
            for roi in rois:
                if roi['patch_id']!=key:continue
                y0,y1,x0,x1=[roi[n] for n in ('y0','y1','x0','x1')]
                for b,band in enumerate(('VV','VH')):roi_diagnostics.append(dict(patch_id=key,method=row['method'],band=band,roi_class=roi.get('roi_class'),coordinates=[y0,y1,x0,x1],**enl(filtered[b,y0:y1,x0:x1],valid=p.input_valid[y0:y1,x0:x1])))
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    except subprocess.SubprocessError:commit='unavailable'
    result.update(status='real_development_calibration_frozen',test_files_opened=0,source='audited_supplied_development',
        elapsed_seconds=perf_counter()-started,validation_seconds=validation_seconds,validation_patch_ids=sorted(validation),
        training_roi_patch_ids=sorted(train),source_patch_ids_opened=sorted(loaded),fallback_calibration_table=fallback_table,
        looks=looks,pilot=pilot,training_roi_filter_diagnostics=roi_diagnostics,
        manifest_sha256=real['manifest_sha256'],splits_sha256=real['splits_sha256'],training_roi_sha256=real['training_roi_sha256'],
        provenance_limitation=real['provenance_limitation'],commit_sha=commit,config_path=_relative(config_path,output_path),
        environment=dict(python=platform.python_version(),platform=platform.platform(),processor=platform.processor(),cpu_count=os.cpu_count(),versions={name:importlib.metadata.version(name) for name in ('numpy','scipy','rasterio')}),
        runtime_type='local_cpu_calibration_and_training_patch_pilot; not fresh Colab',
        input_sha256=input_hashes,code_sha256=code_hashes,
        midal_admission=config['methods']['midal_substitution'])
    for name,path in input_paths.items():
        if sha256_file(path)!=input_hashes[name]:
            raise ValueError(f'{name} changed during calibration; configuration not frozen')
    config_path.parent.mkdir(parents=True,exist_ok=True)
    _json(config_path,config);result['config_sha256']=sha256_file(config_path)
    _json(output_path/'validation.json',result)
    with (output_path/'candidates.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,['method','parameters','channel','rule','threshold','cleanup','seconds','iou','f1']);writer.writeheader()
        for row in result['validation_table']:writer.writerow({**{key:row[key] for key in ('method','channel','rule','threshold','cleanup','seconds')},'parameters':json.dumps(row['parameters'],sort_keys=True),**{name:row['summary']['pooled'][name] for name in ('iou','f1')}})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','splits','rois','config','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=calibrate(args.manifest,args.splits,args.rois,args.config,args.output)
    print(json.dumps(dict(status=result['status'],rows=len(result['validation_table']),common=result['common'],selected_filter=result['selected_filter']['method'],looks=result['looks']['looks'],seconds=result['elapsed_seconds'],config_sha256=result['config_sha256'])))


if __name__=='__main__':main()
