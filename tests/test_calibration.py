"""Calibrate only on hashed development inputs; held-out files can be absent."""
import csv
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from sar_water.data import audit_pair,write_frozen_artifacts,sha256_file


def module():
    spec=importlib.util.spec_from_file_location('calibrate_classical',Path(__file__).parents[1]/'scripts'/'calibrate_classical.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def fixture(tmp_path):
    import rasterio as rio
    rows=[]
    for i,key in enumerate(('train_patch','validation_patch')):
        rng=np.random.default_rng(i+42)
        reference=np.full((64,64),.1);reference[:32]=.01
        db=10*np.log10(np.stack([reference,reference*.2])*rng.gamma(4,.25,(2,64,64)))
        labels=(reference<.02).astype('int16')
        paths={kind:tmp_path/f'{key}-{kind}.tif' for kind in ('image','mask')}
        for kind,path in paths.items():
            values=db.astype('float32') if kind=='image' else labels[None]
            with rio.open(path,'w',driver='GTiff',height=64,width=64,count=len(values),dtype=values.dtype,crs='EPSG:4326',transform=rio.transform.from_origin(i*2,1,.01,.01)) as dataset:dataset.write(values)
        rows.append(audit_pair(dict(patch_id=key,image_path=str(paths['image']),mask_path=str(paths['mask']),units='db',band_order='VV,VH',label_source='manual'))[0])
    # No held-out image or mask exists; any attempted read must fail.
    rows.append(dict(patch_id='test_patch',image_path=str(tmp_path/'absent-test-image.tif'),mask_path=str(tmp_path/'absent-test-mask.tif'),image_sha256='test_i',mask_sha256='test_m',image_content_sha256='test_c',units='db',band_order='VV,VH',label_source='manual'))
    membership=dict(train_patch='train',validation_patch='validation',test_patch='test')
    write_frozen_artifacts(rows,membership,tmp_path/'audit','supplied membership')
    roi=tmp_path/'roi.csv';roi.write_text('patch_id,y0,y1,x0,x1,roi_class,suitability\ntrain_patch,0,32,0,32,water,raw fixture homogeneous region\n')
    return tmp_path/'audit'/'manifest.csv',tmp_path/'audit'/'splits.csv',roi


def test_calibration_freezes_hashed_portable_choices_without_opening_test_files(tmp_path):
    manifest,splits,roi=fixture(tmp_path)
    config=tmp_path/'config.json';out=tmp_path/'run'
    result=module().calibrate(manifest,splits,roi,config,out)
    frozen=json.loads(config.read_text());real=frozen['real_data']
    # A generic audited manual subset is not proof of upstream/organizer identity.
    assert real['status']=='audited_manual_subset_calibrated'
    assert result['source']=='audited_manual_subset'
    assert real.get('organizer_subset') is not True
    assert real['calibration_frozen'] and real['split_frozen']
    assert real['manifest_sha256']==sha256_file(manifest)
    assert real['training_roi_sha256']==sha256_file(roi)
    assert len(result['validation_table'])==98 and len(result['primary'])==4 and len(result['cleanup_ablation'])==4
    assert real['selected_filter'] in ('median','lee','log_bilateral')
    assert real['provenance_limitation']
    assert result['test_files_opened']==0
    assert result['cache_peak_bytes'] <= 100_000_000
    looks=json.loads((config.parent/real['looks_artifact_path']).read_text())
    assert looks['usable_roi_counts']==[1,1]
    assert all(row['patch_id']=='train_patch' for row in looks['rois'])
    assert not Path(real['training_roi_path']).is_absolute() and '\\' not in real['training_roi_path']
    with pytest.raises(FileExistsError):module().calibrate(manifest,splits,roi,config,out)


def test_roi_validation_rejects_heldout_or_wrong_size_before_any_source_access(tmp_path):
    mod=module();roi=tmp_path/'roi.csv'
    roi.write_text('patch_id,y0,y1,x0,x1,suitability\ntest,0,32,0,32,raw inspected\n')
    with pytest.raises(ValueError,match='training-only'):mod.read_rois(roi,{'test':'test'})
    roi.write_text('patch_id,y0,y1,x0,x1,suitability\ntrain,0,31,0,32,raw inspected\n')
    with pytest.raises(ValueError,match='32'):mod.read_rois(roi,{'train':'train'})


def test_calibration_rejects_changed_development_source_before_freezing(tmp_path):
    manifest,splits,roi=fixture(tmp_path)
    with (tmp_path/'train_patch-image.tif').open('ab') as stream:stream.write(b'changed')
    config=tmp_path/'config.json'
    with pytest.raises(ValueError,match='hash'):module().calibrate(manifest,splits,roi,config,tmp_path/'run')
    assert not config.exists()


def test_input_modified_during_calibration_blocks_configuration_freeze(tmp_path,monkeypatch):
    manifest,splits,roi=fixture(tmp_path)
    mod=module();original=mod._pilot
    def mutate_roi(patches,looks):
        result=original(patches,looks)
        with roi.open('ab') as stream:stream.write(b'\n')
        return result
    monkeypatch.setattr(mod,'_pilot',mutate_roi)
    config=tmp_path/'config.json'
    with pytest.raises(ValueError,match='changed during calibration'):
        mod.calibrate(manifest,splits,roi,config,tmp_path/'run')
    assert not config.exists()
