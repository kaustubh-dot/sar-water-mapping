"""Execute notebook provenance guards without network access or a Colab claim."""
import ast
import base64
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from time import perf_counter

import pytest

from sar_water.data import sha256_file


def helper(name):
    notebook = json.loads((Path(__file__).parents[1]/'notebooks/01_sar_water_mapping.ipynb').read_text(encoding='utf-8'))
    definitions = [node for cell in notebook['cells'] if cell['cell_type'] == 'code'
                   for node in ast.parse(cell['source']).body
                   if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(definitions) == 1, f'notebook workflow helper {name} missing'
    namespace = dict(Path=Path, json=json, csv=csv, sha256_file=sha256_file)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), '<notebook>', 'exec'), namespace)
    return namespace[name]


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)


def upstream_fixture(tmp_path):
    data = tmp_path/'data'
    data.mkdir()
    selected, inventory, official = [], [], {}
    for split, count in (('train', 60), ('validation', 20), ('test', 20)):
        pairs = []
        for index in range(count):
            key = f'{split.title()}_{index}'
            image, mask = key+'_S1Hand.tif', key+'_LabelHand.tif'
            selected.append(dict(patch_id=key, split=split, image_name=image, mask_name=mask))
            pairs.append(f'{image},{mask}\n')
            for kind, filename, folder in (('image', image, 'S1Hand'), ('mask', mask, 'LabelHand')):
                inventory.append(dict(patch_id=key, kind=kind, path=filename, units='db',
                    band_order='VV,VH', label_source='manual', split=split,
                    source=f'gs://sen1floods11/v1.1/data/flood_events/HandLabeled/{folder}/{filename}'))
        content = ''.join(pairs).encode()
        name = f'{split}.csv'
        (data/name).write_bytes(content)
        official[split] = dict(url='https://storage.googleapis.com/sen1floods11/'+name,
            sha256=hashlib.sha256(content).hexdigest(), upstream_pair_count=count)
    source = tmp_path/'locked_selection.json'
    source.write_text(json.dumps(dict(selected=selected, split_counts={'train':60, 'validation':20, 'test':20},
        official_splits=official)))
    inventory_path = data/'inventory.csv'
    write_csv(inventory_path, list(inventory[0]), inventory)
    return source, data, inventory_path


def test_notebook_freezes_exact_selection_and_refuses_changed_cached_selection(tmp_path):
    freeze = helper('freeze_upstream_selection')
    source, data, _ = upstream_fixture(tmp_path)
    selection = freeze(source, data)
    assert selection == data/'selection.json'
    assert selection.read_bytes() == source.read_bytes()
    selection.write_text('{}')
    with pytest.raises(ValueError, match='selection.*changed|selection.*match'):
        freeze(source, data)
    assert selection.read_text() == '{}'


def test_notebook_checks_official_membership_and_freezes_supplied_split_csv(tmp_path):
    verify = helper('verify_upstream_inputs')
    source, data, inventory = upstream_fixture(tmp_path)
    split_path = tmp_path/'supplied_splits.csv'
    evidence = verify(source, data, inventory, split_path)
    with split_path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 100
    assert {row['split'] for row in rows} == {'train', 'validation', 'test'}
    assert next(row['split'] for row in rows if row['patch_id'] == 'Test_0') == 'test'
    assert evidence['organizer_subset'] is False
    assert evidence['selection_sha256'] == sha256_file(source)
    assert evidence['official_membership_verified'] is True
    assert evidence['split_counts'] == {'train':60, 'validation':20, 'test':20}
    # Even a changed but internally re-hashed source list cannot move a frozen chip.
    official = data/'test.csv'
    official.write_text(official.read_text().replace('Test_0_', 'Other_0_'))
    provenance = json.loads(source.read_text())
    provenance['official_splits']['test']['sha256'] = sha256_file(official)
    source.write_text(json.dumps(provenance))
    with pytest.raises(ValueError, match='official.*membership|official.*pair'):
        verify(source, data, inventory, tmp_path/'tampered_splits.csv')
    assert not (tmp_path/'tampered_splits.csv').exists()


def test_notebook_rejects_changed_official_csv_and_weak_inventory_labels(tmp_path):
    verify = helper('verify_upstream_inputs')
    source, data, inventory = upstream_fixture(tmp_path)
    official = data/'train.csv'
    original = official.read_bytes()
    official.write_bytes(original+b'\n')
    with pytest.raises(ValueError, match='official.*hash'):
        verify(source, data, inventory, tmp_path/'hash_splits.csv')
    official.write_bytes(original)
    inventory.write_text(inventory.read_text().replace('manual', 'weak', 1))
    with pytest.raises(ValueError, match='manual|inventory'):
        verify(source, data, inventory, tmp_path/'weak_splits.csv')


def test_notebook_access_stage_exports_download_log_without_rewriting_source_reports(tmp_path, monkeypatch):
    source, original_data, _ = upstream_fixture(tmp_path)
    repo = tmp_path/'repo'
    data = repo/'data/development-v1'
    data.parent.mkdir(parents=True)
    original_data.rename(data)
    reports, scripts = repo/'reports', repo/'scripts'
    reports.mkdir()
    scripts.mkdir()
    shutil.copy2(Path(__file__).parents[1]/'scripts/prepare_development_data.py', scripts)
    selection = json.loads(source.read_text())
    for row in selection['selected']:
        row['objects'] = []
        for kind, folder in (('image', 'S1Hand'), ('mask', 'LabelHand')):
            filename = row[kind+'_name']
            content = ('cached fixture: '+filename).encode()
            (data/filename).write_bytes(content)
            row['objects'].append(dict(name='v1.1/data/flood_events/HandLabeled/'+folder+'/'+filename,
                generation='1', size=str(len(content)), md5Hash=base64.b64encode(hashlib.md5(content).digest()).decode(),
                crc32c='fixture-not-consumed', updated='2026-10-29T00:00:00Z'))
    (reports/'development_data_selection.json').write_text(json.dumps(selection))
    for name in ('classical_training_rois.csv', 'heldout_enl_rois.csv'):
        (reports/name).write_text('patch_id,y0,y1,x0,x1,suitability,roi_class\n')
    public_log = reports/'development_data_download.json'
    public_log.write_text('previous recorded evidence\n')
    notebook = json.loads((Path(__file__).parents[1]/'notebooks/01_sar_water_mapping.ipynb').read_text(encoding='utf-8'))
    access = next(cell['source'] for cell in notebook['cells'] if cell['cell_type'] == 'code'
        and any(isinstance(node, ast.FunctionDef) and node.name == 'freeze_upstream_selection'
                for node in ast.parse(cell['source']).body))
    namespace = dict(Path=Path, json=json, csv=csv, shutil=shutil, subprocess=subprocess,
        sys=sys, perf_counter=perf_counter, REPO=repo, RUN_ID='fixture', STAGES={},
        DATA_SOURCE='upstream-development', INVENTORY=None, SUPPLIED_SPLITS=None,
        TRAINING_ROIS=None, HELDOUT_ENL_ROIS=None, ORGANIZER_DATA_CONFIG=None)
    monkeypatch.chdir(repo)
    exec(compile(access, '<notebook data access>', 'exec'), namespace)
    run = repo/'outputs/colab-fixture'
    saved = json.loads((run/'reports/development_data_download.json').read_text())
    assert saved['pairs'] == 100 and saved['files'] == 200
    assert public_log.read_text() == 'previous recorded evidence\n'
    assert (run/'inputs/training_rois.csv').read_bytes() == (reports/'classical_training_rois.csv').read_bytes()
    assert namespace['DATA_PROVENANCE']['official_membership_verified'] is True


def calibration_fixture(tmp_path):
    files = {}
    for name in ('manifest', 'splits', 'training_roi'):
        files[name] = tmp_path/(name+'.csv')
        files[name].write_text(name+'\n')
    looks = tmp_path/'looks.json'
    looks.write_text(json.dumps({name+'_sha256': sha256_file(path) for name, path in files.items()}))
    files['looks_artifact'] = looks
    real = dict(split_frozen=True, calibration_frozen=True)
    for name, path in files.items():
        real[name+'_path'] = path.name
        real[name+'_sha256'] = sha256_file(path)
    config = tmp_path/'config.json'
    config.write_text(json.dumps(dict(real_data=real)))
    validation = tmp_path/'validation.json'
    validation.write_text(json.dumps(dict(config_sha256=sha256_file(config), test_files_opened=0,
        input_sha256={name:sha256_file(files[name]) for name in ('manifest', 'splits', 'training_roi')})))
    return files, config, validation


def test_notebook_verifies_training_compatible_calibration_bindings_before_test_access(tmp_path):
    verify = helper('verify_calibration_identity')
    files, config, validation = calibration_fixture(tmp_path)
    identity = verify(config, files['manifest'], files['splits'], files['training_roi'], validation)
    assert identity['config_file_sha256'] == sha256_file(config)
    assert identity['training_roi_sha256'] == sha256_file(files['training_roi'])
    assert identity['looks_artifact_sha256'] == sha256_file(files['looks_artifact'])
    files['training_roi'].write_text('changed coordinates\n')
    with pytest.raises(ValueError, match='training_roi.*hash|training ROI.*hash'):
        verify(config, files['manifest'], files['splits'], files['training_roi'], validation)


def test_notebook_refuses_validation_evidence_for_a_different_config(tmp_path):
    verify = helper('verify_calibration_identity')
    files, config, validation = calibration_fixture(tmp_path)
    config.write_text(config.read_text()+'\n')
    with pytest.raises(ValueError, match='config.*hash'):
        verify(config, files['manifest'], files['splits'], files['training_roi'], validation)
