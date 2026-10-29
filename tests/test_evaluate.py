"""Final evaluation must keep frozen choices, masks and synthetic truth distinct."""
import importlib.util
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import numpy as np
import pytest

from sar_water.data import adapt_arrays


def api():
    assert importlib.util.find_spec('sar_water.evaluate'), 'final evaluation implementation missing'
    from sar_water import evaluate
    return evaluate


def frozen():
    return dict(seed=42, primary_cleanup=False, real_data=dict(
        split_frozen=True, calibration_frozen=True, selected_channel='VV',
        selected_threshold_strategy='shared_fixed_db', selected_fixed_threshold_db=-20,
        selected_filter_parameters=dict(raw={}, median={'window': 3}, lee={'window': 5},
            log_bilateral={'window': 5, 'spatial_sigma': 2., 'color_sigma_db': 1.5}),
        effective_looks_by_band={'VV': 4., 'VH': 4.},
        fallback_thresholds_db={'VV': -20., 'VH': -26.}, selected_filter='median'))


def patches():
    return {
        'wet': adapt_arrays(np.array([[[-25., -5.], [-25., -5.]]] * 2),
                            np.array([[1, 0], [-1, 1]]), units='db', band_order='VV,VH',
                            input_mask=np.array([[1, 1], [1, 0]], bool)),
        'dry': adapt_arrays(np.full((2, 2, 2), -25.), np.zeros((2, 2), np.int8),
                            units='db', band_order='VV,VH'),
    }


def test_unfrozen_run_fails_before_opening_heldout_inputs(tmp_path):
    e = api()
    config = frozen()
    config['real_data']['calibration_frozen'] = False
    path = tmp_path/'config.json'
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match='calibration'):
        e.run_evaluation(tmp_path/'missing_manifest.csv', tmp_path/'missing_splits.csv', path,
                         tmp_path/'out', synthetic=False)
    assert not (tmp_path/'out').exists()


def test_frozen_primary_preserves_ground_truth_macro_set_and_dry_false_positives():
    e = api()
    result = e.evaluate_frozen_patches(patches(), frozen(), enl_rois=[
        dict(patch_id='dry', y0=0, y1=2, x0=0, x1=2, suitability='homogeneous', roi_class='land')])
    assert len(result['primary']) == 4
    assert all(row['cleanup'] is False for row in result['primary'])
    assert all(row['summary']['macro_patch_ids'] == ['wet'] for row in result['primary'])
    raw = result['primary'][0]
    assert raw['summary']['counts'] == dict(tp=1, fp=4, fn=0, tn=1)
    assert raw['summary']['pooled']['iou'] == .2
    assert raw['summary']['dry']['false_positive_rate'] == 1.
    assert len(result['cleanup_ablation']) == 4
    assert len(result['enl_rois']) == 8
    assert all(row['value'] is None and row['status'] == 'zero_variance' for row in result['enl_rois'])
    assert len(result['per_patch']) == 8


def test_primary_timers_exclude_ablation_diagnostics_and_figures(monkeypatch, tmp_path):
    e = api()
    clock = [0.]
    monkeypatch.setattr(e, 'perf_counter', lambda: clock[0])
    segment, rois, save_figure = e._segment_filtered, e._roi_scores, e._save_figure

    def timed_segment(*args, **kwargs):
        result = segment(*args, **kwargs)
        clock[0] += 5. if kwargs.get('cleanup') else 1.
        return result

    def timed_rois(*args, **kwargs):
        result = rois(*args, **kwargs)
        clock[0] += 3.
        return result

    def timed_figure(*args, **kwargs):
        save_figure(*args, **kwargs)
        clock[0] += 7.

    monkeypatch.setattr(e, '_segment_filtered', timed_segment)
    monkeypatch.setattr(e, '_roi_scores', timed_rois)
    monkeypatch.setattr(e, '_save_figure', timed_figure)
    result = e.evaluate_frozen_patches(patches(), frozen(), figure_output=tmp_path/'figures')
    # Each primary performs two 1-second segmentations. Separate cleanup adds
    # 10 seconds only for raw/median; diagnostic and real figure work add 20.
    assert [row['seconds'] for row in result['primary']] == [2., 2., 2., 2.]
    assert [row['diagnostics_seconds'] for row in result['primary']] == [6.] * 4
    assert [row['figure_seconds'] for row in result['primary']] == [14.] * 4
    assert [row['seconds'] for row in result['cleanup_ablation'] if row['cleanup']] == [10., 10.]
    assert len(list((tmp_path/'figures').glob('*.png'))) == 8


def test_evaluation_rejects_unlocked_parameters_cleanup_and_threshold_policy():
    e = api()
    for update in ({'selected_filter_parameters': {'raw': {}}},
                   {'selected_threshold_strategy': 'fixed_per_method'},
                   {'selected_fixed_threshold_db': -19}):
        config = frozen()
        config['real_data'].update(update)
        with pytest.raises(ValueError):
            e.evaluate_frozen_patches(patches(), config)
    config = frozen()
    config['primary_cleanup'] = True
    with pytest.raises(ValueError, match='cleanup'):
        e.evaluate_frozen_patches(patches(), config)


def test_synthetic_validation_freezes_parameters_and_heldout_rows_are_separate():
    e = api()
    result = e.evaluate_synthetic()
    assert len(result['validation']) == 126
    assert len(result['test']) == 72
    assert {row['split'] for row in result['validation']} == {'validation'}
    assert {row['split'] for row in result['test']} == {'test'}
    assert all(row['source'] == 'simulated_backscatter' for row in result['test'])
    assert len(result['selection']) == 8  # one setting per method and known L
    assert len(result['summary']) == 8
    assert {row['method'] for row in result['test']} == {'raw', 'median', 'lee', 'log_bilateral'}


def test_disk_runner_checks_frozen_input_identity_and_exports_strict_json(tmp_path):
    e = api()
    rasterio = pytest.importorskip('rasterio')
    from rasterio.transform import from_origin
    from sar_water.data import audit_pair, sha256_file, write_frozen_artifacts
    rows = []
    for index, split in enumerate(('train', 'validation', 'test')):
        image, mask = tmp_path/f'{split}_sar.tif', tmp_path/f'{split}_label.tif'
        profile = dict(driver='GTiff', height=4, width=4, crs='EPSG:4326',
                       transform=from_origin(index*10, 4, 1, 1))
        db = np.full((2, 4, 4), -5.-index, np.float32)
        db[:, :2] = -25.-index
        with rasterio.open(image, 'w', count=2, dtype='float32', **profile) as dst:
            dst.write(db)
        with rasterio.open(mask, 'w', count=1, dtype='int8', **profile) as dst:
            dst.write(np.tile(np.array([[1], [1], [0], [0]], np.int8), (1, 4)), 1)
        row, _ = audit_pair(dict(patch_id=split, image_path=str(image), mask_path=str(mask),
            units='db', band_order='VV,VH', source='scientific_fixture', label_source='manual'))
        rows.append(row)
    audit = tmp_path/'audit'
    write_frozen_artifacts(rows, {s: s for s in ('train', 'validation', 'test')}, audit, 'supplied membership')
    config = frozen()
    config['real_data'].update(manifest_sha256=sha256_file(audit/'manifest.csv'),
                               splits_sha256=sha256_file(audit/'splits.csv'))
    path = tmp_path/'config.json'
    path.write_text(json.dumps(config))
    output = tmp_path/'result'
    runtime = e.run_evaluation(audit/'manifest.csv', audit/'splits.csv', path, output, synthetic=False)
    assert runtime['heldout_patch_count'] == 1
    assert runtime['fresh_colab_verified'] is False
    assert runtime['profile'] == 'full'
    assert runtime['training_included'] is False
    assert (output/'results_real.csv').is_file()
    assert (output/'per_patch_real.csv').is_file()
    assert (output/'cleanup_ablation.csv').is_file()
    saved = json.loads((output/'runtime.json').read_text())
    assert saved['config_sha256'] == sha256_file(path)
    # A changed inventory cannot silently reuse a previous calibration freeze.
    with (audit/'manifest.csv').open('a') as stream:
        stream.write('\n')
    with pytest.raises(ValueError, match='manifest.*hash|manifest.*identity'):
        e.run_evaluation(audit/'manifest.csv', audit/'splits.csv', path, tmp_path/'tampered', synthetic=False)


def notebook():
    return json.loads((Path(__file__).parents[1]/'notebooks/01_sar_water_mapping.ipynb').read_text(encoding='utf-8'))


def notebook_function(name):
    """Execute notebook helpers without installing dependencies or reading data."""
    from sar_water.data import sha256_file
    namespace = dict(Path=Path, json=json, shutil=shutil, subprocess=subprocess, sha256_file=sha256_file)
    definitions = [node for cell in notebook()['cells'] if cell['cell_type'] == 'code'
                   for node in ast.parse(cell['source']).body
                   if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(definitions) == 1, f'notebook helper {name} must expose executable workflow behavior'
    exec(compile(ast.Module(body=definitions, type_ignores=[]), '<notebook>', 'exec'), namespace)
    return namespace[name], namespace


def test_notebook_rejects_python311_before_installation(monkeypatch):
    first_code = next(cell['source'] for cell in notebook()['cells'] if cell['cell_type'] == 'code')
    monkeypatch.setattr(sys, 'version_info', (3, 11, 9))
    with pytest.raises(RuntimeError, match='3.12'):
        exec(compile(first_code, '<notebook-start>', 'exec'), {})
    monkeypatch.setattr(sys, 'version_info', (3, 12, 0))
    exec(compile(first_code, '<notebook-start>', 'exec'), {})


def _git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments], text=True).strip()


def test_notebook_checkout_supports_commit_sha_and_refreshes_existing_branch(tmp_path):
    checkout, _ = notebook_function('checkout_source')
    source, target = tmp_path/'source', tmp_path/'checkout'
    source.mkdir()
    subprocess.run(['git', 'init', '--initial-branch=main', str(source)], check=True, capture_output=True)
    _git(source, 'config', 'user.email', 'fixture@example.invalid')
    _git(source, 'config', 'user.name', 'Scientific fixture')
    (source/'value.txt').write_text('first')
    _git(source, 'add', 'value.txt')
    _git(source, 'commit', '-m', 'fixture first')
    first = _git(source, 'rev-parse', 'HEAD')
    (source/'value.txt').write_text('second')
    _git(source, 'commit', '-am', 'fixture second')
    second = _git(source, 'rev-parse', 'HEAD')
    repository = source.as_posix()  # Git for Windows recognizes the local drive path.
    assert checkout(repository, first, target) == first
    assert (target/'value.txt').read_text() == 'first'
    assert checkout(repository, 'main', target) == second
    assert (target/'value.txt').read_text() == 'second'
    assert _git(target, 'rev-parse', 'HEAD') == second
    (target/'value.txt').write_text('user edit')
    with pytest.raises(RuntimeError, match='uncommitted|dirty'):
        checkout(repository, first, target)
    assert (target/'value.txt').read_text() == 'user edit'


def test_notebook_authoritative_total_includes_final_archive_and_hash(monkeypatch, tmp_path):
    export, namespace = notebook_function('export_bundle')
    clock = [1790.]
    namespace['perf_counter'] = lambda: clock[0]
    real_archive, real_hash = shutil.make_archive, namespace['sha256_file']

    def costly_archive(*args, **kwargs):
        archive = real_archive(*args, **kwargs)
        clock[0] += 20.
        return archive

    def costly_hash(path):
        result = real_hash(path)
        clock[0] += 2.
        return result

    monkeypatch.setattr(shutil, 'make_archive', costly_archive)
    namespace['sha256_file'] = costly_hash
    run_root = tmp_path/'run'
    run_root.mkdir()
    (run_root/'results.csv').write_text('method,iou\nraw,0.5\n')
    archive, timing_path, evidence = export(run_root, {'source_commit_sha': 'fixture'}, 0., {})
    assert evidence['total_wall_seconds'] == 1812.
    assert evidence['measured_below_30_minutes'] is False
    assert evidence['stages_seconds']['bundle_export_seconds'] == 22.
    assert json.loads(Path(timing_path).read_text()) == evidence
    assert Path(timing_path).parent == run_root.parent
    assert evidence['archive_sha256'] == real_hash(archive)
    with zipfile.ZipFile(archive) as bundle:
        assert 'results.csv' in bundle.namelist()
        manifest = json.loads(bundle.read('bundle_manifest.json'))
        assert manifest['source_commit_sha'] == 'fixture'
        assert manifest['authoritative_timing_sidecar'] == Path(timing_path).name
