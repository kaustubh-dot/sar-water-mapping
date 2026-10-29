"""Score one completed, frozen raw/filtered checkpoint pair on held-out SAR.

This is checkpoint evaluation: remote training time remains a separate recorded
measurement. The command neither selects parameters nor certifies a fresh Colab
run. Frozen data/configuration and both checkpoints are checked before reading
any held-out raster or mask.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import numpy as np
import torch

from sar_water.data import Patch, audit_pair, power_to_db, sha256_file, validate_splits
from sar_water.evaluate import _csv, _table, frozen_settings
from sar_water.filters import filter_power
from sar_water.metrics import confusion_counts, summarize_water
from sar_water.train import (Normalization, TrainingConfig, _json_hash,
                             load_checkpoint, predict_patch, state_sha256)


def _evaluation_source_identity():
    """Record evaluation sources independently of the earlier training commit."""
    root = Path(__file__).resolve().parents[1]
    sources = ('scripts/evaluate_neural.py', 'src/sar_water/model.py', 'src/sar_water/train.py',
               'src/sar_water/data.py', 'src/sar_water/filters.py', 'src/sar_water/metrics.py',
               'src/sar_water/evaluate.py')
    try:
        commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                         text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'],
                                             text=True, stderr=subprocess.DEVNULL))
        status = 'available'
    except (OSError, subprocess.CalledProcessError):
        commit, dirty, status = None, None, 'unavailable'
    return dict(evaluation_source_commit_sha=commit, evaluation_working_tree_dirty=dirty,
                evaluation_source_git_status=status,
                evaluation_source_sha256={name: sha256_file(root / name) for name in sources})


def _preflight(manifest_path, splits_path, config_path, training_dir, device):
    config = json.loads(config_path.read_text(encoding='utf-8'))
    settings = frozen_settings(config)
    real = config['real_data']
    for name, path in (('manifest', manifest_path), ('splits', splits_path)):
        if not real.get(name + '_sha256') or sha256_file(path) != real[name + '_sha256']:
            raise ValueError(f'{name} hash differs from frozen configuration')
    with manifest_path.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    with splits_path.open(newline='', encoding='utf-8-sig') as stream:
        split_rows = list(csv.DictReader(stream))
    membership = {row['patch_id']: row['split'] for row in split_rows}
    if len(membership) != len(split_rows):
        raise ValueError('duplicate split identifier')
    validate_splits(rows, membership)
    if any(row.get('split') and row['split'] != membership[row['patch_id']] for row in rows):
        raise ValueError('manifest/splits membership conflict')
    report = json.loads((training_dir / 'training.json').read_text(encoding='utf-8'))
    if report.get('pair_complete') is not True or report.get('cap_exhausted') is not False:
        raise ValueError('evaluation requires a complete training pair inside its shared cap')
    training_config = TrainingConfig(**report['config'])
    if report.get('runtime_type') != training_config.profile:
        raise ValueError('training runtime/configuration provenance mismatch')
    if report.get('config_sha256') != _json_hash(report['config']):
        raise ValueError('training configuration hash mismatch')
    split_hash = _json_hash(membership)
    subset_hash = _json_hash(sorted(rows, key=lambda row: row['patch_id']))
    if report.get('split_sha256') != split_hash or report.get('subset_sha256') != subset_hash:
        raise ValueError('training data/split provenance differs from frozen subset')
    expected_filter = dict(method=settings['selected_filter'],
        parameters=settings['parameters'][settings['selected_filter']], looks=settings['looks'],
        config_file_sha256=sha256_file(config_path), manifest_file_sha256=real['manifest_sha256'],
        splits_file_sha256=real['splits_sha256'], training_roi_sha256=real.get('training_roi_sha256'),
        looks_artifact_sha256=real.get('looks_artifact_sha256'))
    if (not expected_filter['training_roi_sha256'] or not expected_filter['looks_artifact_sha256']
            or report.get('filtered_identity') != expected_filter):
        raise ValueError('training filter/configuration provenance differs from frozen configuration')
    normalization = Normalization(**report['normalization'])
    train_ids = tuple(sorted(key for key, split in membership.items() if split == 'train'))
    if normalization.train_ids != train_ids:
        raise ValueError('normalization training IDs differ from frozen membership')
    train_rows = [row for row in rows if membership[row['patch_id']] == 'train']
    if all(row.get('input_valid_pixels') for row in train_rows):
        if sum(int(row['input_valid_pixels']) for row in train_rows) != normalization.pixel_count:
            raise ValueError('normalization pixel count differs from audited training inputs')
    models, hashes = {}, {}
    for condition in ('raw', 'filtered'):
        state = report['conditions'][condition]
        if state.get('status') not in ('max_epochs', 'early_stopped') or state.get('best_epoch') is None:
            raise ValueError('both conditions require a validated best checkpoint')
        path = training_dir / f'{condition}_best.pt'
        model, saved_normalization, metadata = load_checkpoint(path, device=device)
        if saved_normalization != normalization or Normalization(**metadata['normalization']) != normalization:
            raise ValueError('checkpoint normalization differs from shared raw-training normalization')
        for key in ('config', 'config_sha256', 'split_sha256', 'subset_sha256', 'commit_sha', 'filtered_identity'):
            if metadata.get(key) != report.get(key):
                raise ValueError(f'{condition} checkpoint {key} provenance mismatch')
        if (metadata.get('condition') != condition or metadata.get('best_epoch') != state['best_epoch']
                or metadata.get('best_iou') != state['best_iou']
                or state_sha256(model) != state.get('final_sha256')):
            raise ValueError(f'{condition} checkpoint selection/state provenance mismatch')
        best_updates = sum(epoch['updates'] for epoch in state['history']
                           if epoch['epoch'] <= state['best_epoch'])
        if metadata.get('updates') != best_updates or not 0 < best_updates <= state['updates']:
            raise ValueError(f'{condition} checkpoint update provenance mismatch')
        models[condition], hashes[condition] = model, sha256_file(path)
    return config, settings, rows, membership, report, normalization, models, hashes


def _heldout_patches(rows, membership, manifest_path):
    patches = {}
    for row in rows:
        if membership[row['patch_id']] != 'test':
            continue
        pair = dict(row)
        for name in ('image', 'mask'):
            path = Path(pair[name + '_path'])
            path = path if path.is_absolute() else manifest_path.parent / path
            if not pair.get(name + '_sha256') or sha256_file(path) != pair[name + '_sha256']:
                raise ValueError(f'held-out {name} hash changed after audit')
            pair[name + '_path'] = str(path)
        audit, patch = audit_pair(pair)
        if (not pair.get('image_content_sha256')
                or audit['image_content_sha256'] != pair['image_content_sha256']):
            raise ValueError('held-out decoded SAR hash changed after audit')
        patches[pair['patch_id']] = patch
    if not patches:
        raise ValueError('held-out membership has no patches')
    return patches


def _learning_curves(report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    for condition, color in (('raw', '#235789'), ('filtered', '#b35806')):
        history = report['conditions'][condition]['history']
        epochs = [row['epoch'] for row in history]
        axes[0].plot(epochs, [row['train_loss'] for row in history], color=color, label=condition)
        ious = [row['validation']['summary']['pooled']['iou'] if row.get('validation') else None
                for row in history]
        axes[1].plot(epochs, ious, color=color, label=condition)
    axes[0].set_ylabel('Mean batch loss')
    axes[0].set_title('Training BCE / Dice objective')
    axes[1].set_ylabel('Pooled water IoU')
    axes[1].set_title('Validation checkpoint selection')
    axes[1].set_ylim(0, 1)
    for axis in axes:
        axis.set_xlabel('Epoch')
        axis.legend(frameon=False)
        axis.spines[['top', 'right']].set_visible(False)
    figure.savefig(output / 'learning_curves.png', dpi=150)
    plt.close(figure)


def _prediction_figures(raw, filtered, predictions, patch_ids, output):
    """First five identifiers, chosen without sorting by measured performance."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=True)
    for index, key in enumerate(patch_ids):
        patch = raw[key]
        raw_db, filtered_db = power_to_db(patch.power), power_to_db(filtered[key].power)
        figure, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
        vv_limits = np.percentile(raw_db[0, patch.input_valid], [2, 98])
        vh_limits = np.percentile(raw_db[1, patch.input_valid], [2, 98])
        for axis, values, title, limits in (
                (axes[0, 0], raw_db[0], 'Raw VV (dB)', vv_limits),
                (axes[1, 0], raw_db[1], 'Raw VH (dB)', vh_limits),
                (axes[1, 1], filtered_db[0], 'Selected filter VV (dB)', vv_limits)):
            axis.imshow(values, cmap='gray', vmin=limits[0], vmax=limits[1])
            axis.set_title(title)
        axes[0, 1].imshow(np.where(patch.score_valid, patch.labels, np.nan), cmap='Blues', vmin=0, vmax=1)
        axes[0, 1].set_title('Ground truth; scoring mask')
        for column, condition in ((2, 'raw'), (3, 'filtered')):
            prediction = predictions[condition][key]
            axes[0, column].imshow(np.where(patch.input_valid, prediction, np.nan), cmap='Blues', vmin=0, vmax=1)
            axes[0, column].set_title(f'{condition.capitalize()} U-Net water')
            axes[1, column].imshow(np.where(patch.score_valid, prediction - patch.labels, np.nan),
                                   cmap='coolwarm', vmin=-1, vmax=1)
            axes[1, column].set_title(f'{condition.capitalize()} error: red FP / blue FN')
        for axis in axes.flat:
            axis.set_axis_off()
        figure.suptitle(key)
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in key)
        figure.savefig(output / f'{index:05d}_{safe}_neural.png', dpi=120)
        plt.close(figure)


def run_neural_evaluation(manifest_path, splits_path, config_path, training_dir,
                          output, *, device='cuda', figures=False):
    """Export native held-out segmentation scores for the completed paired seed.

    Only held-out image/mask files are opened. Training normalization is checked
    against its checkpoint/report and manifest identity, never fitted on test.
    """
    started = perf_counter()
    manifest_path, splits_path, config_path, training_dir, output = map(
        Path, (manifest_path, splits_path, config_path, training_dir, output))
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FileExistsError('neural results require a new empty output directory')
    evaluation_source = _evaluation_source_identity()
    config, settings, rows, membership, training, normalization, models, hashes = _preflight(
        manifest_path, splits_path, config_path, training_dir, device)
    verified_seconds = perf_counter() - started
    raw = _heldout_patches(rows, membership, manifest_path)
    loaded_seconds = perf_counter() - started - verified_seconds
    macro_ids = sorted(key for key, patch in raw.items()
                       if np.any((patch.labels == 1) & patch.input_valid & patch.label_valid))
    output.mkdir(parents=True, exist_ok=True)
    prediction_dir = output / 'predictions'
    prediction_dir.mkdir(exist_ok=True)
    figure_ids = sorted(raw)[:5] if figures else []
    conditions, per_patch, artifacts = [], [], []
    figure_predictions, figure_filtered = {'raw': {}, 'filtered': {}}, {}
    for condition in ('raw', 'filtered'):
        condition_started = perf_counter()
        native_export_seconds = 0.
        patches = raw
        if condition == 'filtered':
            method = settings['selected_filter']
            patches = {key: Patch(filter_power(patch.power, patch.input_valid, method=method,
                **settings['parameters'][method], **({'looks': settings['looks']} if method == 'lee' else {})),
                patch.labels.copy(), patch.input_valid.copy(), patch.label_valid.copy())
                for key, patch in raw.items()}
        counts = {}
        for index, key in enumerate(sorted(patches)):
            patch = patches[key]
            predicted = predict_patch(models[condition], patch, normalization, device=device)
            counts[key] = confusion_counts(predicted['prediction'], patch.labels,
                input_valid=patch.input_valid, label_valid=patch.label_valid)
            export_started = perf_counter()
            safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in key)
            path = prediction_dir / f'{condition}_{index:05d}_{safe}.npz'
            np.savez_compressed(path, prediction=predicted['prediction'],
                input_valid=patch.input_valid, label_valid=patch.label_valid,
                score_valid=patch.input_valid & patch.label_valid & (patch.labels != -1))
            artifacts.append(dict(condition=condition, patch_id=key,
                path=path.relative_to(output).as_posix(), sha256=sha256_file(path),
                shape=list(predicted['prediction'].shape), dtype='int8', invalid_code=-1))
            native_export_seconds += perf_counter() - export_started
            if key in figure_ids:
                figure_predictions[condition][key] = predicted['prediction']
                if condition == 'filtered':
                    figure_filtered[key] = patch
        result = dict(per_patch_counts=counts, summary=summarize_water(counts, macro_patch_ids=macro_ids))
        if result['summary']['macro_patch_ids'] != macro_ids:
            raise ValueError('raw/filtered fixed ground-truth-water-positive macro sets differ')
        conditions.append(dict(condition=condition, model_role='segmentation',
            input_filter='raw' if condition == 'raw' else settings['selected_filter'],
            water_probability_threshold=.5, threshold_comparison='strict_greater',
            cleanup=False, enl='not_applicable', psnr='not_applicable',
            seconds=perf_counter() - condition_started - native_export_seconds,
            timing_scope='input_filtering_native_inference_and_scoring_only',
            native_export_seconds=native_export_seconds,
            native_export_timing_scope='native_prediction_npz_write_and_checksum', **result))
        for key, counts in result['per_patch_counts'].items():
            per_patch.append(dict(condition=condition, patch_id=key, **counts,
                                  **result['summary']['per_patch'][key]))
    heldout_rows = [row for row in rows if membership[row['patch_id']] == 'test']
    runtime = dict(profile='checkpoint-evaluation', runtime_type=f'neural_{torch.device(device).type}',
        training_included=False, fresh_colab_verified=False,
        seed=training['config']['seed'], training_runtime_type=training['runtime_type'],
        external_training_seconds=training.get('complete_pair_seconds', training['elapsed_seconds']),
        training_config=training['config'], training_commit_sha=training.get('commit_sha'),
        training_working_tree_dirty=training.get('working_tree_dirty'),
        **evaluation_source,
        training_report_sha256=sha256_file(training_dir / 'training.json'),
        training_checkpoint_sha256=hashes, config_sha256=sha256_file(config_path),
        manifest_sha256=sha256_file(manifest_path), splits_sha256=sha256_file(splits_path),
        normalization=training['normalization'], filtered_identity=training['filtered_identity'],
        best_epochs={key: training['conditions'][key]['best_epoch'] for key in models},
        actual_training_updates={key: training['conditions'][key]['updates'] for key in models},
        heldout_patch_count=len(raw), heldout_shapes={key: list(patch.power.shape) for key, patch in raw.items()},
        fixed_macro_patch_ids=macro_ids,
        native_prediction_artifact_count=len(artifacts),
        native_export_seconds=sum(row['native_export_seconds'] for row in conditions),
        prediction_encoding=dict(dtype='int8', land=0, water=1, invalid=-1,
                                 validity='original SAR mask; label validity stored separately'),
        label_claim='independent manual labels' if all(row['label_source'] == 'manual' for row in heldout_rows)
            else 'weak/unknown-label agreement only; not independent ground truth',
        python=platform.python_version(), torch=str(torch.__version__), numpy=np.__version__,
        device=str(device), device_name=torch.cuda.get_device_name(torch.device(device))
            if torch.device(device).type == 'cuda' else platform.processor(),
        checkpoint_verification_seconds=verified_seconds, heldout_loading_seconds=loaded_seconds,
        limitations='A checkpoint evaluation does not reproduce training or establish a fresh Colab runtime. '
                    'These masks identify observed water; new flooding versus permanent water is not established.')
    _csv(output / 'results_neural.csv', _table([
        {key: value for key, value in row.items() if key != 'per_patch_counts'} for row in conditions]))
    _csv(output / 'per_patch_neural.csv', per_patch)
    _csv(output / 'native_predictions.csv', artifacts)
    if figures:
        _learning_curves(training, output)
        _prediction_figures(raw, figure_filtered, figure_predictions, figure_ids, output / 'figures')
    runtime['evaluation_seconds'] = perf_counter() - started
    runtime['evaluation_timing_scope'] = ('preflight_loading_compute_tables_native_masks_checksums_and_optional_figures; '
                                          'excludes_final_json_and_config_serialization')
    result = dict(runtime=runtime, conditions=conditions)
    (output / 'results_neural.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (output / 'runtime_neural.json').write_text(json.dumps(runtime, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (output / 'config.json').write_text(config_path.read_text(encoding='utf-8'), encoding='utf-8')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('manifest', 'splits', 'config', 'training-dir', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--figures', action='store_true', help='export learning curves and first five aligned prediction diagnostics')
    args = parser.parse_args(argv)
    result = run_neural_evaluation(args.manifest, args.splits, args.config, args.training_dir,
                                   args.output, device=args.device, figures=args.figures)
    print(json.dumps(result['runtime'], indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
