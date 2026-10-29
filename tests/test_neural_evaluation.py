"""Checkpoint-evaluation fixtures; never score an actual held-out experiment."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

torch = pytest.importorskip('torch')


def api():
    path = Path(__file__).resolve().parents[1] / 'scripts' / 'evaluate_neural.py'
    assert path.is_file(), 'neural checkpoint evaluator missing'
    spec = importlib.util.spec_from_file_location('evaluate_neural_fixture', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows):
    fields = sorted({key for row in rows for key in row})
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows({key: json.dumps(value) if isinstance(value, (list, dict)) else value
                          for key, value in row.items()} for row in rows)


@pytest.fixture(scope='module')
def checkpoint_fixture(tmp_path_factory):
    api()  # Fail on the absent feature before doing any fixture training.
    from sar_water.data import audit_pair, sha256_file
    from sar_water.filters import estimate_training_looks
    from sar_water.train import TrainingConfig, load_frozen_training_inputs, paired_train
    rasterio = pytest.importorskip('rasterio')
    from rasterio.transform import from_origin
    root = tmp_path_factory.mktemp('neural-evaluation-source')
    membership = {'train': 'train', 'validation': 'validation', 'water': 'test', 'dry': 'test'}
    rng, rows, train_power = np.random.default_rng(20), [], None
    for key, shape in [('train', (256, 256)), ('validation', (17, 19)),
                       ('water', (17, 19)), ('dry', (8, 8))]:
        db = rng.normal(-15, 2, (2, *shape)).astype(np.float32)
        power = np.power(10, db / 10).astype(np.float32)
        labels = np.zeros(shape, np.int8)
        if key != 'dry':
            labels[:, :shape[1] // 2] = 1
        if key == 'water':
            power[:, 0, 0] = np.nan
            labels[0, 1] = -1
        image, mask = root / f'{key}.tif', root / f'{key}_mask.tif'
        common = dict(driver='GTiff', height=shape[0], width=shape[1],
                      transform=from_origin(0, shape[0], 1, 1))
        with rasterio.open(image, 'w', count=2, dtype='float32', **common) as stream:
            stream.write(power)
        with rasterio.open(mask, 'w', count=1, dtype='int8', **common) as stream:
            stream.write(labels, 1)
        row, patch = audit_pair(dict(patch_id=key, image_path=str(image), mask_path=str(mask),
            units='linear_power', band_order='VV,VH', source='synthetic fixture',
            label_source='manual_fixture', source_patch_id=key))
        rows.append(dict(row, image_path=image.name, mask_path=mask.name, split=membership[key]))
        if key == 'train':
            train_power = patch.power
    manifest, splits, roi = root / 'manifest.csv', root / 'splits.csv', root / 'roi.csv'
    write_csv(manifest, rows)
    write_csv(splits, [dict(patch_id=key, split=split) for key, split in membership.items()])
    rois = [dict(patch_id='train', y0=0, y1=32, x0=0, x1=32)]
    write_csv(roi, rois)
    looks = estimate_training_looks({'train': dict(power=train_power,
        input_valid=np.ones((256, 256), bool))}, rois, membership)
    (root / 'looks.json').write_text(json.dumps(looks))
    config = dict(seed=42, primary_cleanup=False, real_data=dict(
        split_frozen=True, calibration_frozen=True, selected_channel='VV',
        selected_threshold_strategy='shared_fixed_db', selected_fixed_threshold_db=-20,
        selected_filter='median', selected_filter_parameters=dict(raw={}, median={'window': 3},
            lee={'window': 5}, log_bilateral={'window': 5, 'spatial_sigma': 2, 'color_sigma_db': 1.5}),
        effective_looks_by_band=looks['looks'], fallback_thresholds_db={'VV': -20, 'VH': -24},
        manifest_sha256=sha256_file(manifest), splits_sha256=sha256_file(splits),
        training_roi_path='roi.csv', training_roi_sha256=sha256_file(roi),
        looks_artifact_path='looks.json', looks_artifact_sha256=sha256_file(root / 'looks.json')))
    config_path = root / 'config.json'
    config_path.write_text(json.dumps(config))
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        result = paired_train(**load_frozen_training_inputs(manifest, splits, config_path),
            config=TrainingConfig(max_epochs=1, max_seconds=120, profile='fixture'),
            output_dir=root / 'training', device='cpu', commit_sha='fixture-commit')
    finally:
        torch.set_num_threads(threads)
    assert result.report['pair_complete']
    return root


@pytest.fixture
def files(checkpoint_fixture, tmp_path):
    destination = tmp_path / 'fixture'
    shutil.copytree(checkpoint_fixture, destination)
    return destination


def run(root, **kwargs):
    return api().run_neural_evaluation(root / 'manifest.csv', root / 'splits.csv',
        root / 'config.json', root / 'training', root / 'results', device='cpu', **kwargs)


def remove_heldout(root):
    for name in ('water.tif', 'water_mask.tif', 'dry.tif', 'dry_mask.tif'):
        (root / name).unlink()


def test_checkpoint_evaluation_exports_native_scores_masks_and_fixed_macro_set(files):
    # The evaluator must not need any training/validation source values.
    for name in ('train.tif', 'train_mask.tif', 'validation.tif', 'validation_mask.tif'):
        (files / name).unlink()
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        result = run(files, figures=True)
    finally:
        torch.set_num_threads(threads)
    runtime = result['runtime']
    assert runtime['profile'] == 'checkpoint-evaluation' and not runtime['training_included']
    assert runtime['fresh_colab_verified'] is False and runtime['heldout_patch_count'] == 2
    assert runtime['training_runtime_type'] == 'fixture'
    repository = Path(__file__).resolve().parents[1]
    expected_commit = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
    assert runtime['evaluation_source_commit_sha'] == expected_commit
    assert type(runtime['evaluation_working_tree_dirty']) is bool
    assert runtime['evaluation_source_git_status'] == 'available'
    for name in ('scripts/evaluate_neural.py', 'src/sar_water/model.py', 'src/sar_water/train.py'):
        assert runtime['evaluation_source_sha256'][name] == hashlib.sha256((repository / name).read_bytes()).hexdigest()
    for row in result['conditions']:
        summary = row['summary']
        assert sum(summary['counts'].values()) == 385  # 323 - 2 ignored + 64 dry
        assert summary['macro_patch_ids'] == ['water']
        assert summary['dry']['patch_count'] == 1 and summary['dry']['valid_pixels'] == 64
        assert sum(row['per_patch_counts']['water'].values()) == 321
        assert row['enl'] == row['psnr'] == 'not_applicable'
    report = json.loads((files / 'results' / 'results_neural.json').read_text())
    assert report['runtime']['training_checkpoint_sha256']['raw']
    with (files / 'results' / 'results_neural.csv').open(newline='') as stream:
        assert {row['condition'] for row in csv.DictReader(stream)} == {'raw', 'filtered'}
    with (files / 'results' / 'per_patch_neural.csv').open(newline='') as stream:
        assert len(list(csv.DictReader(stream))) == 4
    assert (files / 'results' / 'learning_curves.png').stat().st_size > 1000
    with (files / 'results' / 'native_predictions.csv').open(newline='') as stream:
        artifacts = list(csv.DictReader(stream))
    assert len(artifacts) == 4
    import rasterio
    for row in artifacts:
        with np.load(files / 'results' / row['path'], allow_pickle=False) as arrays:
            prediction = arrays['prediction']
            assert prediction.shape == ((17, 19) if row['patch_id'] == 'water' else (8, 8))
            assert prediction.dtype == np.int8
            assert all(arrays[name].dtype == bool for name in ('input_valid', 'label_valid', 'score_valid'))
            assert np.isin(prediction[arrays['input_valid']], [0, 1]).all()
            assert np.all(prediction[~arrays['input_valid']] == -1)
            with rasterio.open(files / f"{row['patch_id']}_mask.tif") as stream:
                labels = stream.read(1)
            scored = arrays['score_valid']
            assert np.array_equal(scored, arrays['input_valid'] & arrays['label_valid'] & (labels != -1))
            # Recount from the persisted artifact, independently of the scorer.
            actual_counts = dict(
                tp=int(np.sum(scored & (prediction == 1) & (labels == 1))),
                fp=int(np.sum(scored & (prediction == 1) & (labels == 0))),
                fn=int(np.sum(scored & (prediction == 0) & (labels == 1))),
                tn=int(np.sum(scored & (prediction == 0) & (labels == 0))))
            scored_condition = next(item for item in report['conditions'] if item['condition'] == row['condition'])
            assert actual_counts == scored_condition['per_patch_counts'][row['patch_id']]
            if row['patch_id'] == 'water':
                assert prediction[0, 0] == -1 and prediction[0, 1] in (0, 1)
                assert not arrays['score_valid'][0, 0] and not arrays['score_valid'][0, 1]
        assert row['sha256'] == hashlib.sha256((files / 'results' / row['path']).read_bytes()).hexdigest()
    assert len(list((files / 'results' / 'figures').glob('*_neural.png'))) == 2


def test_native_prediction_export_time_is_separate_from_condition_compute(files, monkeypatch):
    module = api()
    clock = [0.]
    monkeypatch.setattr(module, 'perf_counter', lambda: clock[0])
    predict, filtering = module.predict_patch, module.filter_power
    confusion, summary = module.confusion_counts, module.summarize_water
    save, checksum = module.np.savez_compressed, module.sha256_file

    def timed_predict(*args, **kwargs):
        result = predict(*args, **kwargs)
        clock[0] += 1.
        return result

    def timed_filter(*args, **kwargs):
        result = filtering(*args, **kwargs)
        clock[0] += 3.
        return result

    def timed_confusion(*args, **kwargs):
        result = confusion(*args, **kwargs)
        clock[0] += 2.
        return result

    def timed_summary(*args, **kwargs):
        result = summary(*args, **kwargs)
        clock[0] += 5.
        return result

    def timed_save(*args, **kwargs):
        result = save(*args, **kwargs)
        clock[0] += 7.
        return result

    def timed_checksum(path):
        result = checksum(path)
        if Path(path).suffix == '.npz':
            clock[0] += 11.
        return result

    monkeypatch.setattr(module, 'predict_patch', timed_predict)
    monkeypatch.setattr(module, 'filter_power', timed_filter)
    monkeypatch.setattr(module, 'confusion_counts', timed_confusion)
    monkeypatch.setattr(module, 'summarize_water', timed_summary)
    monkeypatch.setattr(module.np, 'savez_compressed', timed_save)
    monkeypatch.setattr(module, 'sha256_file', timed_checksum)
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        result = module.run_neural_evaluation(files / 'manifest.csv', files / 'splits.csv',
            files / 'config.json', files / 'training', files / 'results', device='cpu')
    finally:
        torch.set_num_threads(threads)
    # Two predictions and confusion matrices plus one summary cost 11 seconds.
    # Filtered input adds two 3-second filter calls. Each condition separately
    # spends 36 seconds writing and hashing two real native prediction files.
    assert [row['seconds'] for row in result['conditions']] == [11., 17.]
    assert [row['native_export_seconds'] for row in result['conditions']] == [36., 36.]
    assert {row['timing_scope'] for row in result['conditions']} == {
        'input_filtering_native_inference_and_scoring_only'}
    assert {row['native_export_timing_scope'] for row in result['conditions']} == {
        'native_prediction_npz_write_and_checksum'}
    assert result['runtime']['native_export_seconds'] == 72.
    assert result['runtime']['evaluation_seconds'] == 100.


def test_mismatched_checkpoint_normalization_rejected_before_heldout_access(files):
    from sar_water.train import Normalization, load_checkpoint, save_checkpoint
    path = files / 'training' / 'raw_best.pt'
    model, norm, metadata = load_checkpoint(path)
    altered = Normalization(norm.mean, tuple(value * 2 for value in norm.std), norm.pixel_count, norm.train_ids)
    save_checkpoint(path, model, altered, metadata)
    remove_heldout(files)
    with pytest.raises(ValueError, match='normalization'):
        run(files)
    assert not (files / 'results').exists()


def test_mismatched_filter_checkpoint_provenance_rejected_before_heldout_access(files):
    from sar_water.train import load_checkpoint, save_checkpoint
    path = files / 'training' / 'filtered_best.pt'
    model, norm, metadata = load_checkpoint(path)
    metadata['filtered_identity']['method'] = 'lee'
    save_checkpoint(path, model, norm, metadata)
    remove_heldout(files)
    with pytest.raises(ValueError, match='provenance|filter'):
        run(files)


def test_changed_frozen_configuration_rejected_before_heldout_access(files):
    config_path = files / 'config.json'
    config = json.loads(config_path.read_text())
    config['real_data']['selected_filter'] = 'lee'
    config_path.write_text(json.dumps(config))
    remove_heldout(files)
    with pytest.raises(ValueError, match='configuration|config|filter'):
        run(files)


def test_incomplete_training_pair_rejected_before_heldout_access(files):
    path = files / 'training' / 'training.json'
    report = json.loads(path.read_text())
    report['pair_complete'] = False
    path.write_text(json.dumps(report))
    remove_heldout(files)
    with pytest.raises(ValueError, match='complete|pair'):
        run(files)


def test_changed_heldout_source_hash_rejected_before_scoring(files):
    (files / 'water_mask.tif').write_bytes(b'changed fixture')
    with pytest.raises(ValueError, match='held-out.*hash'):
        run(files)


def test_unfrozen_config_rejected_before_any_manifest_or_checkpoint_access(tmp_path):
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'seed': 42, 'real_data': {'split_frozen': False}}))
    with pytest.raises(ValueError, match='frozen'):
        api().run_neural_evaluation(tmp_path / 'missing.csv', tmp_path / 'missing_splits.csv',
            config, tmp_path / 'missing_training', tmp_path / 'results', device='cpu')
