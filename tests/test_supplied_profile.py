"""Metadata-only supplied provenance checks precede every SAR/label read."""
import csv
import json
from pathlib import Path

import pytest

from sar_water.data import read_inventory, sha256_file, write_frozen_artifacts
from test_supplied_data import module as acquisition_module, service, source_csv, selection


@pytest.fixture
def supplied_profile_inputs(tmp_path, source_csv, selection):
    data = tmp_path/'data'
    fetch, _, _ = service(source_csv, selection, data)
    acquisition_module().prepare_supplied_data(data, tmp_path/'acquisition', fetcher=fetch)
    download = json.loads((data/'download.json').read_text())
    hashes = {row['path']: row['sha256'] for row in download['objects']}
    rows = read_inventory(data/'inventory.csv')
    for row in rows:
        for kind in ('image', 'mask'):
            row[kind+'_sha256'] = hashes[Path(row[kind+'_path']).name]
        row['image_source_content_sha256'] = row['image_sha256']
    membership = {row['patch_id']: row['split'] for row in rows}
    audit = tmp_path/'audit'
    write_frozen_artifacts(rows, membership, audit, 'supplied membership')
    return audit/'manifest.csv', audit/'splits.csv', data


def test_supplied_source_config_freezes_exact_evidence_and_discloses_exposure(supplied_profile_inputs, tmp_path, monkeypatch):
    from sar_water.supplied_profile import write_supplied_source_config, verify_supplied_source_config
    manifest, splits, data = supplied_profile_inputs
    target = tmp_path/'source.json'
    frozen = write_supplied_source_config(manifest, splits, data, target)
    # Verification only reads metadata; acquired fixture TIFF bodies cannot decode.
    real = verify_supplied_source_config(target, manifest, splits)
    assert frozen['real_data'] == real
    assert real['source'] == 'supplied-first100'
    assert real['split_counts'] == {'train':29, 'validation':40, 'test':31}
    assert real['split_proportions'] == {'train':.29, 'validation':.40, 'test':.31}
    assert real['events_by_split'] == {'train':['Mekong','Nigeria','Pakistan'], 'validation':['India'], 'test':['Ghana']}
    assert real['previous_training_exposure_count'] == 22
    assert real['previous_training_exposure_by_split'] == {'train':5, 'validation':9, 'test':8}
    assert real['prior_models_valid_for_unseen_holdout_claim'] is False
    assert real['manifest_sha256'] == sha256_file(manifest)
    assert 'source_config' not in frozen.get('methods', {})
    with pytest.raises(FileExistsError):
        write_supplied_source_config(manifest, splits, data, target)


@pytest.mark.parametrize('change', ['manifest', 'membership', 'download', 'grid'])
def test_supplied_tamper_or_membership_mixup_fails_before_data_access(supplied_profile_inputs, tmp_path, monkeypatch, change):
    from sar_water.supplied_profile import write_supplied_source_config
    from test_calibration import module
    manifest, splits, data = supplied_profile_inputs
    target = tmp_path/'source.json'
    write_supplied_source_config(manifest, splits, data, target)
    if change == 'manifest':
        manifest.write_text(manifest.read_text()+'\n')
    elif change == 'membership':
        rows = list(csv.DictReader(splits.open()))
        rows[0]['split'] = 'train'
        with splits.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, ['patch_id','split']);writer.writeheader();writer.writerows(rows)
    elif change == 'download':
        (data/'download.json').write_text((data/'download.json').read_text()+'\n')
    else:
        config = json.loads(target.read_text())
        config['methods'] = {'median': {'window_candidates':[99]}}
        target.write_text(json.dumps(config))
    mod = module()
    monkeypatch.setattr(mod, '_checked_patch', lambda row: pytest.fail('source access before metadata rejection'))
    with pytest.raises(ValueError, match='source|hash|membership|metadata'):
        mod.calibrate(manifest, splits, tmp_path/'absent-rois.csv', tmp_path/'config.json', tmp_path/'run', source_config_path=target)
    assert not (tmp_path/'config.json').exists()


def test_rehashed_manifest_cannot_rebind_a_supplied_id_to_another_source(supplied_profile_inputs, tmp_path):
    from sar_water.supplied_profile import write_supplied_source_config
    manifest, splits, data = supplied_profile_inputs
    content = manifest.read_text()
    content = content.replace('../data/Ghana_103272_S1Hand.tif', '../data/Ghana_24858_S1Hand.tif', 1)
    manifest.write_text(content)
    with pytest.raises(ValueError, match='source.*binding|source.*identity'):
        write_supplied_source_config(manifest, splits, data, tmp_path/'source.json')


def test_rehashed_supplied_split_mixup_is_rejected(supplied_profile_inputs, tmp_path):
    from sar_water.supplied_profile import write_supplied_source_config
    manifest, splits, data = supplied_profile_inputs
    splits.write_text(splits.read_text().replace('Ghana_103272,test', 'Ghana_103272,train'))
    with pytest.raises(ValueError, match='membership'):
        write_supplied_source_config(manifest, splits, data, tmp_path/'source.json')


def test_supplied_calibration_binds_metadata_and_rejects_source_changes_at_freeze(supplied_profile_inputs, tmp_path, monkeypatch):
    from sar_water.data import read_manifest
    from sar_water.supplied_profile import write_supplied_source_config
    from test_calibration import fixture, module
    manifest, splits, data = supplied_profile_inputs
    source = tmp_path/'source.json'
    source_frozen = write_supplied_source_config(manifest,splits,data,source)
    # Use a real tiny SAR fixture for bounded compute; every supplied held-out
    # file remains the undecodable acquisition body, and any attempted read fails.
    tiny = tmp_path/'tiny';tiny.mkdir()
    tiny_manifest, _, _ = fixture(tiny)
    mod=module();patch=mod._checked_patch(read_manifest(tiny_manifest)[0])
    def checked(row):
        assert row['split'] != 'test', 'calibration must never access held-out sources'
        return patch
    monkeypatch.setattr(mod,'_checked_patch',checked)
    roi=tmp_path/'roi.csv'
    roi.write_text('patch_id,y0,y1,x0,x1,roi_class,suitability\nMekong_596495,0,32,0,32,water,raw synthetic fixture\n')
    config=tmp_path/'frozen'/'config.json'
    result=mod.calibrate(manifest,splits,roi,config,tmp_path/'run',source_config_path=source)
    frozen=json.loads(config.read_text());real=frozen['real_data']
    assert result['source']=='supplied-first100' and result['test_files_opened']==0
    assert real['source_config_sha256']==sha256_file(source)==result['source_config_sha256']
    assert (config.parent/real['source_config_path']).resolve()==source.resolve()
    assert real['previous_training_exposure_by_split']=={'train':5,'validation':9,'test':8}
    assert set(result['input_sha256'])=={'manifest','splits','training_roi'}
    assert all(row['patch_count']==5 for row in result['pilot'])
    template=json.loads((Path(__file__).parents[1]/'configs/experiment.json').read_text())
    assert frozen['segmentation_candidates']==template['segmentation_candidates']
    for name in ('raw','median','lee','log_bilateral'):
        assert frozen['methods'][name]==template['methods'][name]
    assert result['source_provenance']==source_frozen['real_data']
    from test_notebook import helper
    identity=helper('verify_calibration_identity')(config,manifest,splits,roi,tmp_path/'run/validation.json',source_config_path=source)
    assert identity['source_config_sha256']==sha256_file(source)
    with pytest.raises(ValueError,match='source configuration required'):
        helper('verify_calibration_identity')(config,manifest,splits,roi,tmp_path/'run/validation.json')
    original=mod._pilot
    def mutate_source(patches,looks):
        records=original(patches,looks)
        source.write_text(source.read_text()+'\n')
        return records
    monkeypatch.setattr(mod,'_pilot',mutate_source)
    with pytest.raises(ValueError,match='source configuration changed during calibration'):
        mod.calibrate(manifest,splits,roi,tmp_path/'changed-config.json',tmp_path/'changed-run',source_config_path=source)
    assert not (tmp_path/'changed-config.json').exists()
