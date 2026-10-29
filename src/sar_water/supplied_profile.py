"""Bind the supplied first-100 audit to acquisition metadata, without pixels.

This source configuration carries provenance only. It cannot supply filter
grids, selected methods, normalization, checkpoints or training parameters.
"""
from __future__ import annotations

from collections import Counter
import csv
import json
import os
from pathlib import Path

from .data import create_splits, read_inventory, read_manifest, sha256_file, validate_splits

PROJECT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = '57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb'
SELECTION_SHA256 = '9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2'
SOURCE_URL = 'https://storage.googleapis.com/sen1floods11/v1.1/splits/flood_handlabeled/flood_train_data.csv'
PREFIX = 'v1.1/data/flood_events/HandLabeled/'


def _csv(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def _json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _bound(path, parent):
    path = Path(path)
    return (path if path.is_absolute() else parent/path).resolve()


def _binding(path, parent):
    return dict(path=Path(os.path.relpath(Path(path).resolve(), parent.resolve())).as_posix(),
                sha256=sha256_file(path))


def _source_metadata(manifest_path, splits_path, paths, parent):
    """Reconstruct expected metadata, never open or hash a TIFF."""
    manifest_path, splits_path = Path(manifest_path), Path(splits_path)
    recipe, selected = _json(paths['recipe']), _csv(paths['supplied_selection'])
    if (sha256_file(paths['source_csv']) != SOURCE_SHA256 or
            sha256_file(paths['supplied_selection']) != SELECTION_SHA256 or
            sha256_file(paths['acquired_supplied_selection']) != SELECTION_SHA256 or
            recipe.get('source_csv_sha256') != SOURCE_SHA256 or
            recipe.get('selection_sha256') != SELECTION_SHA256 or
            recipe.get('source_csv_url') != SOURCE_URL or recipe.get('patch_count') != 100):
        raise ValueError('supplied source/selection hash or recipe identity mismatch')
    with paths['source_csv'].open(newline='', encoding='utf-8') as stream:
        upstream = list(csv.reader(stream))
    if len(selected) != 100 or len(upstream) != 252:
        raise ValueError('supplied source requires exactly 100 of 252 source rows')
    for index, row in enumerate(selected):
        key = row['patch_id']
        if (row['recipe_index'] != str(index) or row['event_id'] != key.rsplit('_',1)[0]
                or row['upstream_split'] != 'train' or row['evaluation_split'] != 'unassigned'
                or upstream[index] != [key+'_S1Hand.tif', key+'_LabelHand.tif']
                or [row['image_name'], row['mask_name']] != upstream[index]):
            raise ValueError('supplied source identities/order differ from first100 recipe')
    expected, policy = create_splits(selected, seed=42)
    counts = dict(Counter(expected.values()))
    events = {split:sorted({r['event_id'] for r in selected if expected[r['patch_id']] == split})
              for split in ('train','validation','test')}
    exposed = sorted(r['patch_id'] for r in selected if r['previous_development_split'] == 'train')
    exposure = dict(Counter(expected[key] for key in exposed))
    if (counts != {'train':29,'validation':40,'test':31} or len(exposed) != 22
            or set(recipe.get('previous_training_overlap_ids', [])) != set(exposed)
            or exposure != {'train':5,'validation':9,'test':8}):
        raise ValueError('supplied source counts/prior training exposure mismatch')
    split_rows = _csv(splits_path)
    membership = {r['patch_id']:r['split'] for r in split_rows}
    if len(split_rows) != 100 or membership != expected:
        raise ValueError('supplied source split membership differs from frozen event rule')
    acquisition_splits = _csv(paths['acquisition_splits'])
    if len(acquisition_splits) != 100 or {r['patch_id']:r['split'] for r in acquisition_splits} != expected:
        raise ValueError('supplied acquisition membership differs from event rule')
    freeze, metadata, download = (_json(paths[name]) for name in ('split_freeze','acquisition_selection','download'))
    selected_freeze = [{key:row[key] for key in ('recipe_index','patch_id','event_id','upstream_split','previous_development_split')}
                       | {'split':expected[row['patch_id']]} for row in selected]
    if (freeze.get('seed') != 42 or freeze.get('split_policy') != policy
            or freeze.get('source_csv_sha256') != SOURCE_SHA256
            or freeze.get('selection_sha256') != SELECTION_SHA256
            or freeze.get('recipe_sha256') != sha256_file(paths['recipe'])
            or freeze.get('splits_sha256') != sha256_file(paths['acquisition_splits'])
            or freeze.get('selected') != selected_freeze or freeze.get('events_by_split') != events):
        raise ValueError('supplied split-freeze source hash/membership mismatch')
    for evidence in (freeze, metadata, download):
        if (evidence.get('split_counts') != counts or
                evidence.get('previous_training_exposure_by_split') != exposure):
            raise ValueError('supplied evidence counts/exposure mismatch')
    if (metadata.get('source_csv_url') != SOURCE_URL or metadata.get('source_csv_sha256') != SOURCE_SHA256
            or metadata.get('selection_sha256') != SELECTION_SHA256
            or metadata.get('split_freeze_sha256') != sha256_file(paths['split_freeze'])
            or download.get('source_csv_sha256') != SOURCE_SHA256
            or download.get('supplied_selection_sha256') != SELECTION_SHA256
            or download.get('selection_sha256') != sha256_file(paths['acquisition_selection'])
            or download.get('split_freeze_sha256') != sha256_file(paths['split_freeze'])
            or download.get('splits_sha256') != sha256_file(paths['acquisition_splits'])
            or download.get('inventory_sha256') != sha256_file(paths['inventory'])
            or download.get('pairs') != 100 or download.get('files') != 200):
        raise ValueError('supplied acquisition source hash chain mismatch')
    stored = metadata.get('selected', [])
    if len(stored) != 100:
        raise ValueError('supplied acquisition selection requires 100 identities')
    inventory = {r['patch_id']:r for r in read_inventory(paths['inventory'])}
    rows = read_manifest(manifest_path)
    validate_splits(rows, membership)
    if len(inventory) != 100 or set(inventory) != set(expected):
        raise ValueError('supplied inventory identity mismatch')
    by_id = {r['patch_id']:r for r in rows}
    objects = download.get('objects', [])
    acquired = {r['name']:r for r in objects}
    if len(objects) != 200 or len(acquired) != 200:
        raise ValueError('supplied download requires 200 unique source objects')
    data_root = paths['inventory'].parent.resolve()
    for selected_row, stored_row in zip(selected, stored):
        key = selected_row['patch_id']
        expected_row = dict(selected_row, split=expected[key], source_patch_id=key, scene_id='')
        if {k:v for k,v in stored_row.items() if k != 'objects'} != expected_row or len(stored_row.get('objects',[])) != 2:
            raise ValueError('supplied acquisition source identity/membership mismatch')
        row, inv = by_id[key], inventory[key]
        for field, value in dict(event_id=selected_row['event_id'], split=expected[key], source_patch_id=key,
                                  units='db', band_order='VV,VH', label_source='manual', upstream_split='train',
                                  recipe_index=selected_row['recipe_index'],
                                  previous_development_split=selected_row['previous_development_split']).items():
            if row.get(field) != value or inv.get(field) != value:
                raise ValueError('supplied audited source identity/membership mismatch: '+key)
        for kind, folder, obj in zip(('image','mask'), ('S1Hand/','LabelHand/'), stored_row['objects']):
            name = PREFIX+folder+selected_row[kind+'_name']
            recorded = acquired.get(name,{})
            source_field = 'source' if kind == 'image' else 'mask_source'
            if (obj.get('name') != name or recorded.get('path') != selected_row[kind+'_name']
                    or any(str(recorded.get(f)) != str(obj.get(f)) for f in ('generation','md5Hash'))
                    or str(recorded.get('bytes')) != str(obj.get('size'))
                    or len(recorded.get('sha256','')) != 64
                    or row.get(kind+'_sha256') != recorded['sha256']
                    or row.get(source_field) != 'gs://sen1floods11/'+name
                    or inv.get(source_field) != row.get(source_field)
                    or Path(row[kind+'_path']).resolve() != data_root/selected_row[kind+'_name']
                    or Path(inv[kind+'_path']).resolve() != Path(row[kind+'_path']).resolve()):
                raise ValueError('supplied audited source binding/identity mismatch: '+key)
    return dict(source='supplied-first100', organizer_subset=False, pair_count=100,
        selection_definition='first 100 ordered rows of upstream manual training CSV; user supplied recipe',
        selection_authority=recipe['selection_source'], upstream_split_counts={'train':100},
        split_frozen=True, split_seed=42, split_policy=policy, split_counts=counts,
        split_proportions={key:value/100 for key,value in counts.items()}, events_by_split=events,
        previous_training_exposure_count=22, previous_training_exposure_ids=exposed,
        previous_training_exposure_by_split=exposure, prior_models_valid_for_unseen_holdout_claim=False,
        provenance_limitation='Internal event groups use 29/40/31 patches, not official upstream test membership. '
            '22 supplied IDs were previously used in project training, including 8 current test IDs; '
            'existing development checkpoints cannot support an unseen-input claim. Recipe sender authority is unverified.',
        manifest_path=_binding(manifest_path,parent)['path'], manifest_sha256=sha256_file(manifest_path),
        splits_path=_binding(splits_path,parent)['path'], splits_sha256=sha256_file(splits_path),
        source_artifacts={name:_binding(path,parent) for name,path in paths.items()})


def write_supplied_source_config(manifest_path, splits_path, data_root, output_path, *, recipe_path=None, selection_path=None):
    """Exclusively freeze verified, portable provenance after the raster audit."""
    data_root, output_path = Path(data_root), Path(output_path)
    paths = dict(recipe=Path(recipe_path or PROJECT/'reports/supplied_subset_recipe.json'),
                 supplied_selection=Path(selection_path or PROJECT/'reports/supplied_subset_selection.csv'))
    paths.update({name:data_root/filename for name,filename in dict(source_csv='flood_train_data.csv',
        acquired_supplied_selection='supplied_subset_selection.csv', acquisition_splits='splits.csv',
        split_freeze='split_freeze.json', acquisition_selection='selection.json', download='download.json', inventory='inventory.csv').items()})
    real = _source_metadata(manifest_path, splits_path, paths, output_path.parent)
    result = dict(schema_version=1, profile='supplied-first100', real_data=real)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    return result


def verify_supplied_source_config(source_config_path, manifest_path, splits_path):
    """Reject changed metadata or source mixing before SAR or test access."""
    source_config_path = Path(source_config_path)
    config = _json(source_config_path)
    if set(config) != {'schema_version','profile','real_data'} or config.get('schema_version') != 1 or config.get('profile') != 'supplied-first100':
        raise ValueError('source configuration must contain only supplied provenance metadata')
    real = config['real_data'];parent = source_config_path.parent
    for name,path in (('manifest',manifest_path),('splits',splits_path)):
        if (real.get(name+'_sha256') != sha256_file(path) or
                _bound(real.get(name+'_path',''),parent) != Path(path).resolve()):
            raise ValueError('source configuration '+name+' hash/path mismatch')
    required = {'recipe','supplied_selection','source_csv','acquired_supplied_selection',
                'acquisition_splits','split_freeze','acquisition_selection','download','inventory'}
    bindings = real.get('source_artifacts',{})
    if set(bindings) != required:
        raise ValueError('source configuration metadata bindings incomplete')
    paths = {}
    for name,binding in bindings.items():
        paths[name] = _bound(binding['path'],parent)
        if set(binding) != {'path','sha256'} or sha256_file(paths[name]) != binding['sha256']:
            raise ValueError('source metadata hash mismatch: '+name)
    expected = _source_metadata(manifest_path,splits_path,paths,parent)
    if real != expected:
        raise ValueError('source configuration metadata differs from verified supplied evidence')
    return real
