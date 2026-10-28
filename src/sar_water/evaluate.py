"""Frozen held-out classical benchmark; synthetic reference scores stay separate.

Run ``python -m sar_water.evaluate --help``. This command performs no tuning on
real test labels and never freezes a configuration. A measured local execution
is not evidence that a fresh Colab Run All fits the challenge time budget.
"""
from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
from time import perf_counter

import numpy as np

from .benchmark import _segment_filtered
from .data import audit_pair, sha256_file, validate_splits
from .filters import FILTER_GRID, filter_power
from .metrics import enl, psnr, summarize_water
from .segment import FIXED_GRID
from .synthetic import gamma_speckle, make_phantom, phantom_splits


def frozen_settings(config):
    """Fail before data access unless the exact locked classical choices exist."""
    real = config['real_data']
    if config.get('seed') != 42:
        raise ValueError('locked seed 42 required')
    if not real.get('split_frozen') or not real.get('calibration_frozen'):
        raise ValueError('frozen splits and validation calibration required before held-out evaluation')
    if config.get('primary_cleanup') is not False:
        raise ValueError('primary cleanup must be disabled')
    channel = real.get('selected_channel')
    if channel not in FIXED_GRID:
        raise ValueError('frozen channel must be VV or VH')
    strategy = real.get('selected_threshold_strategy')
    if strategy not in ('shared_fixed_db', 'per_patch_otsu_db'):
        raise ValueError('frozen shared threshold strategy required')
    threshold = real.get('selected_fixed_threshold_db')
    if strategy == 'shared_fixed_db' and threshold not in FIXED_GRID[channel]:
        raise ValueError('fixed threshold outside locked validation grid')
    parameters = real.get('selected_filter_parameters')
    if not isinstance(parameters, dict) or set(parameters) != set(FILTER_GRID):
        raise ValueError('exactly four frozen filter parameter mappings required')
    for method, chosen in parameters.items():
        if chosen not in FILTER_GRID[method]:
            raise ValueError(f'{method} parameters outside locked grid')
    looks = real.get('effective_looks_by_band')
    looks = [looks.get(band) for band in ('VV', 'VH')] if isinstance(looks, dict) else looks
    looks = np.asarray(looks, dtype=float)
    if looks.shape != (2,) or not np.isfinite(looks).all() or np.any(looks < 1):
        raise ValueError('training-estimated frozen VV/VH looks >=1 required')
    fallbacks = real.get('fallback_thresholds_db', {})
    if set(fallbacks) != set(FIXED_GRID) or any(not np.isfinite(v) for v in fallbacks.values()):
        raise ValueError('finite frozen fallback thresholds required for VV/VH')
    selected = real.get('selected_filter')
    if selected not in set(FILTER_GRID)-{'raw'}:
        raise ValueError('validation-selected actual filter required')
    return dict(channel=channel, rule='fixed' if strategy == 'shared_fixed_db' else 'otsu',
                threshold=threshold if strategy == 'shared_fixed_db' else None,
                fallback_threshold=fallbacks[channel], looks=looks.tolist(),
                parameters=parameters, selected_filter=selected)


def _roi_scores(patch_id, patch, filtered, method, rois):
    records = []
    for index, roi in enumerate(rois):
        if roi['patch_id'] != patch_id:
            continue
        coordinates = [int(roi[name]) for name in ('y0', 'y1', 'x0', 'x1')]
        y0, y1, x0, x1 = coordinates
        if not (0 <= y0 < y1 <= patch.input_valid.shape[0] and
                0 <= x0 < x1 <= patch.input_valid.shape[1]):
            raise ValueError('ENL ROI outside source patch')
        valid = patch.input_valid[y0:y1, x0:x1]
        for band_index, band in enumerate(('VV', 'VH')):
            score = enl(filtered[band_index, y0:y1, x0:x1], valid=valid)
            records.append(dict(patch_id=patch_id, method=method, roi_id=roi.get('roi_id', str(index)),
                band=band, roi_class=roi.get('roi_class', roi.get('class', 'unspecified')),
                suitability=roi.get('suitability', 'unrecorded'),
                y0=y0, y1=y1, x0=x0, x1=x1, **score))
    return records


def evaluate_frozen_patches(patches, config, *, enl_rois=(), figure_output=None):
    """Evaluate already-loaded held-out patches under one immutable common rule.

    All primary methods use exactly the same ground-truth-water-positive macro
    set. ENL rectangles are supplied before filtering, never selected by results.
    Cleanup ablation reuses primary filter outputs and reports its own time.
    """
    settings = frozen_settings(config)
    if not patches:
        raise ValueError('no held-out patches')
    rois = list(enl_rois)
    if any(roi['patch_id'] not in patches for roi in rois):
        raise ValueError('ENL evaluation ROIs must refer to held-out patch identifiers')
    macro_ids = sorted(key for key, patch in patches.items()
                       if np.any((patch.labels == 1) & patch.score_valid))
    primary, ablation, per_patch, roi_records, radiometry = [], [], [], [], []
    for method in FILTER_GRID:
        counts, cleaned_counts, statuses = {}, {}, {}
        seconds, cleanup_seconds, diagnostics_seconds, figure_seconds = 0., 0., 0., 0.
        for patch_id, patch in patches.items():
            primary_start = perf_counter()
            filtered = filter_power(patch.power, patch.input_valid, method=method,
                **settings['parameters'][method], **({'looks': settings['looks']} if method == 'lee' else {}))
            result = _segment_filtered(patch, filtered, channel=settings['channel'], rule=settings['rule'],
                threshold=settings['threshold'], fallback_threshold=settings['fallback_threshold'])
            counts[patch_id] = result['counts']
            statuses[patch_id] = dict(threshold_db=result['threshold_db'], status=result['status'])
            seconds += perf_counter()-primary_start
            if method in ('raw', settings['selected_filter']):
                cleanup_start = perf_counter()
                clean = _segment_filtered(patch, filtered, channel=settings['channel'], rule=settings['rule'],
                    threshold=settings['threshold'], fallback_threshold=settings['fallback_threshold'], cleanup=True)
                cleaned_counts[patch_id] = clean['counts']
                cleanup_seconds += perf_counter()-cleanup_start
            diagnostics_start = perf_counter()
            roi_records.extend(_roi_scores(patch_id, patch, filtered, method, rois))
            for i, band in enumerate(('VV', 'VH')):
                raw_mean = float(np.mean(patch.power[i, patch.input_valid], dtype=np.float64))
                filtered_mean = float(np.mean(filtered[i, patch.input_valid], dtype=np.float64))
                radiometry.append(dict(patch_id=patch_id, method=method, band=band,
                    raw_mean_power=raw_mean, filtered_mean_power=filtered_mean,
                    mean_change_percent=100*(filtered_mean/raw_mean-1)))
            diagnostics_seconds += perf_counter()-diagnostics_start
            if figure_output is not None:
                figure_start = perf_counter()
                _save_figure(patch_id, patch, filtered, result['prediction'], method, figure_output)
                figure_seconds += perf_counter()-figure_start
        summary_start = perf_counter()
        summary = summarize_water(counts, macro_patch_ids=macro_ids)
        seconds += perf_counter()-summary_start
        primary.append(dict(method=method, parameters=settings['parameters'][method], cleanup=False,
            channel=settings['channel'], rule=settings['rule'], threshold=settings['threshold'],
            seconds=seconds, timing_scope='filter_segmentation_and_scoring_only',
            diagnostics_seconds=diagnostics_seconds, figure_seconds=figure_seconds, summary=summary))
        for key in patches:
            per_patch.append(dict(patch_id=key, method=method, **counts[key],
                **summary['per_patch'][key], **statuses[key], cleanup=False))
        if cleaned_counts:
            for cleanup, selected_counts in ((False, counts), (True, cleaned_counts)):
                ablation.append(dict(method=method, cleanup=cleanup,
                    seconds=cleanup_seconds if cleanup else None,
                    timing_scope='segmentation_and_cleanup_only_cached_filter' if cleanup else 'see_primary',
                    summary=summarize_water(selected_counts, macro_patch_ids=macro_ids)))
    enl_summary = []
    for method in FILTER_GRID:
        for band in ('VV', 'VH'):
            classes = sorted({row['roi_class'] for row in roi_records}) or ['unspecified']
            for roi_class in classes:
                rows = [row for row in roi_records if (row['method'], row['band'], row['roi_class']) == (method, band, roi_class)]
                values = [row['value'] for row in rows if row['status'] == 'ok']
                enl_summary.append(dict(method=method, band=band, roi_class=roi_class,
                    roi_count=len(rows), finite_count=len(values), undefined_count=len(rows)-len(values),
                    median=float(np.median(values)) if values else None,
                    q25=float(np.percentile(values, 25)) if values else None,
                    q75=float(np.percentile(values, 75)) if values else None,
                    status='ok' if values else 'no_finite_rois'))
    return dict(primary=primary, cleanup_ablation=ablation, per_patch=per_patch,
        enl_rois=roi_records, enl_summary=enl_summary, radiometry=radiometry,
        enl_status='recorded_rois' if rois else 'missing_preselected_rois', macro_patch_ids=macro_ids)


def evaluate_synthetic():
    """Select settings on synthetic validation identities, then score test once.

    Selection maximizes mean PSNR separately at each known L. Exact ties retain
    the earlier bounded setting. Every method receives identical corruptions.
    """
    validation, test, selection, summary = [], [], [], []

    def records(split, method, parameters, looks):
        result = []
        for phantom_id, membership in phantom_splits().items():
            if membership != split:
                continue
            reference = make_phantom(phantom_id)
            valid = np.ones(reference.shape, bool)
            for seed in (42, 43, 44):
                noisy = gamma_speckle(reference, looks=looks, seed=seed)
                start = perf_counter()
                estimate = filter_power(np.stack([noisy, noisy]), valid, method=method, **parameters,
                    **({'looks': [looks, looks]} if method == 'lee' else {}))[0]
                score = psnr(reference, estimate, data_range=1.)
                result.append(dict(source='simulated_backscatter', phantom_id=phantom_id, split=split,
                    looks=looks, noise_seed=seed, method=method, parameters=dict(parameters), data_range=1.,
                    psnr_db=score['value'] if np.isfinite(score['value']) else None,
                    mse=score['mse'], status=score['status'], seconds=perf_counter()-start))
        return result

    for looks in (1, 4):
        for method, candidates in FILTER_GRID.items():
            choices = []
            for parameters in candidates:
                rows = records('validation', method, parameters, looks)
                validation.extend(rows)
                choices.append((float(np.mean([row['psnr_db'] for row in rows])), parameters))
            score, parameters = max(choices, key=lambda item: item[0])
            selection.append(dict(method=method, looks=looks, parameters=dict(parameters),
                mean_validation_psnr_db=score, selection_split='validation'))
    # No held-out reference/observation is constructed until every choice exists.
    for choice in selection:
        rows = records('test', choice['method'], choice['parameters'], choice['looks'])
        test.extend(rows)
        summary.append(dict(method=choice['method'], looks=choice['looks'], split='test',
            parameters=choice['parameters'], mean_psnr_db=float(np.mean([row['psnr_db'] for row in rows])),
            record_count=len(rows), source='simulated_backscatter'))
    return dict(validation=validation, test=test, selection=selection, summary=summary)


def _save_figure(patch_id, patch, filtered, prediction, method, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .data import power_to_db
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    raw_db, filtered_db = power_to_db(patch.power), power_to_db(filtered)
    limits = [np.percentile(raw_db[i, patch.input_valid], [2, 98]) for i in (0, 1)]
    figure, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
    for i, band in enumerate(('VV', 'VH')):
        for axis, values, title in ((axes[i, 0], raw_db[i], f'Raw {band} (dB)'),
                                    (axes[i, 1], filtered_db[i], f'{method} {band} (dB)')):
            axis.imshow(values, cmap='gray', vmin=limits[i][0], vmax=limits[i][1]); axis.set_title(title)
    axes[0, 2].imshow(np.where(patch.score_valid, patch.labels, np.nan), vmin=0, vmax=1, cmap='Blues')
    axes[0, 2].set_title('Ground truth; invalid masked')
    axes[0, 3].imshow(np.where(patch.input_valid, prediction, np.nan), vmin=0, vmax=1, cmap='Blues')
    axes[0, 3].set_title('Water prediction')
    error = np.where(patch.score_valid, prediction-patch.labels, np.nan)
    axes[1, 2].imshow(error, vmin=-1, vmax=1, cmap='coolwarm'); axes[1, 2].set_title('Error: red FP / blue FN')
    axes[1, 3].imshow(patch.power[0]/filtered[0], vmin=0, vmax=2, cmap='gray')
    axes[1, 3].set_title('VV power ratio raw / filtered (0–2)')
    for axis in axes.flat:
        axis.set_axis_off()
    safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in patch_id)
    figure.savefig(output/f'{safe_id}_{method}.png', dpi=120)
    plt.close(figure)


def _csv(path, rows):
    rows = list(rows)
    fields = sorted({key for row in rows for key in row})
    with Path(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: json.dumps(value, sort_keys=True, allow_nan=False)
                          if isinstance(value, (dict, list)) else value for key, value in row.items()} for row in rows)


def _table(rows):
    result = []
    for row in rows:
        summary = row['summary']
        result.append({**{key: value for key, value in row.items() if key != 'summary'},
            **summary['counts'], **{f'pooled_{k}': v for k, v in summary['pooled'].items()},
            **{f'macro_{k}': v for k, v in summary['macro'].items()},
            **{f'dry_{k}': v for k, v in summary['dry'].items()},
            'macro_patch_ids': summary['macro_patch_ids'], 'macro_undefined_counts': summary['macro_undefined_counts'],
            'no_valid_patch_count': summary['no_valid_patch_count'],
            'undefined_water_patch_count': summary['undefined_water_patch_count']})
    return result


def run_evaluation(manifest_path, splits_path, config_path, output, *, enl_rois=None,
                   profile='full', runtime_type='local_cpu', external_setup_seconds=0.,
                   synthetic=True, figures=False):
    """Check frozen file identity, score native held-out patches, export evidence.

    ``external_setup_seconds`` comes from the notebook's monotonic first cell.
    This function times its own work; it never certifies a fresh Colab runtime.
    Classical full runs contain no training; a checkpoint profile must retain
    independent remote-training provenance for any neural result added later.
    """
    start = perf_counter()
    config_path, manifest_path, splits_path, output = map(Path, (config_path, manifest_path, splits_path, output))
    config = json.loads(config_path.read_text(encoding='utf-8'))
    frozen_settings(config)  # Must precede manifest, input or test label access.
    if profile not in ('full', 'checkpoint-evaluation'):
        raise ValueError('unknown runtime profile')
    if not np.isfinite(external_setup_seconds) or external_setup_seconds < 0:
        raise ValueError('setup seconds must be finite and nonnegative')
    real = config['real_data']
    for name, path in (('manifest', manifest_path), ('splits', splits_path)):
        if not real.get(name+'_sha256') or sha256_file(path) != real[name+'_sha256']:
            raise ValueError(f'{name} hash does not match frozen calibration identity')
    with manifest_path.open(newline='', encoding='utf-8-sig') as stream:
        manifest = list(csv.DictReader(stream))
    with splits_path.open(newline='', encoding='utf-8-sig') as stream:
        split_rows = list(csv.DictReader(stream))
    membership = {row['patch_id']: row['split'] for row in split_rows}
    if len(membership) != len(split_rows):
        raise ValueError('duplicate split identifier')
    validate_splits(manifest, membership)
    if any(row.get('split') and row['split'] != membership[row['patch_id']] for row in manifest):
        raise ValueError('manifest/splits membership conflict')
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('result directory is nonempty; use a new versioned run directory')
    patches, heldout_rows = {}, []
    for pair in manifest:
        if membership[pair['patch_id']] != 'test':
            continue
        pair = dict(pair)
        for name in ('image_path', 'mask_path'):
            path = Path(pair[name])
            pair[name] = str(path if path.is_absolute() else manifest_path.parent/path)
        for name in ('image', 'mask'):
            if sha256_file(pair[name+'_path']) != pair[name+'_sha256']:
                raise ValueError(f'held-out {name} hash changed after audit')
        audit, patch = audit_pair(pair)
        if pair.get('image_content_sha256') and audit['image_content_sha256'] != pair['image_content_sha256']:
            raise ValueError('held-out decoded image hash changed after audit')
        patches[pair['patch_id']] = patch
        heldout_rows.append(audit)
    rois = []
    if enl_rois is not None:
        with Path(enl_rois).open(newline='', encoding='utf-8-sig') as stream:
            rois = list(csv.DictReader(stream))
    loaded_seconds = perf_counter()-start
    result = evaluate_frozen_patches(patches, config, enl_rois=rois,
        figure_output=output/'figures' if figures else None)
    real_seconds = perf_counter()-start-loaded_seconds
    synthetic_start = perf_counter()
    simulated = evaluate_synthetic() if synthetic else None
    synthetic_seconds = perf_counter()-synthetic_start
    output.mkdir(parents=True, exist_ok=True)
    _csv(output/'results_real.csv', _table(result['primary']))
    _csv(output/'per_patch_real.csv', result['per_patch'])
    _csv(output/'cleanup_ablation.csv', _table(result['cleanup_ablation']))
    for name in ('enl_rois', 'enl_summary', 'radiometry'):
        _csv(output/(name+'.csv'), result[name])
    (output/'results_real.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    if simulated is not None:
        for name, rows in simulated.items():
            filename = 'results_synthetic.csv' if name == 'summary' else f'synthetic_{name}.csv'
            _csv(output/filename, rows)
    packages = {}
    for name in ('numpy', 'scipy', 'rasterio', 'matplotlib', 'torch'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    runtime = dict(profile=profile, runtime_type=runtime_type, seed=config['seed'],
        training_included=False, neural_status='not_run_by_classical_runner',
        remote_training_seconds=None, fresh_colab_verified=False,
        python=platform.python_version(), platform=platform.platform(), processor=platform.processor(),
        accelerator='not_used_by_classical_runner', dependencies=packages, commit_sha=commit, working_tree_dirty=dirty,
        config_sha256=sha256_file(config_path), manifest_sha256=sha256_file(manifest_path),
        splits_sha256=sha256_file(splits_path), enl_rois_sha256=sha256_file(enl_rois) if enl_rois else None,
        manifest_patch_count=len(manifest), heldout_patch_count=len(patches),
        heldout_shapes={key: list(patch.power.shape) for key, patch in patches.items()},
        label_claim='independent manual labels' if all(row['label_source'] == 'manual' for row in heldout_rows)
            else 'weak/unknown-label agreement only; not independent ground truth',
        external_setup_seconds=float(external_setup_seconds), load_and_verify_seconds=loaded_seconds,
        real_evaluation_seconds=real_seconds, synthetic_seconds=synthetic_seconds,
        enl_status=result['enl_status'], synthetic_status='scored_separate_known_reference' if simulated else 'disabled',
        runner_seconds=perf_counter()-start,
        limitations='No fresh Colab Run All was verified by this function. External setup includes only supplied timing. '
                    'Surface water mapping does not establish new flooding versus permanent water.')
    runtime['total_wall_seconds_including_supplied_setup'] = runtime['runner_seconds']+external_setup_seconds
    (output/'runtime.json').write_text(json.dumps(runtime, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    (output/'environment.txt').write_text('\n'.join([f'Python {platform.python_version()}']+
        [f'{key}=={value}' for key, value in packages.items()])+'\n', encoding='utf-8')
    (output/'config.json').write_text(config_path.read_text(encoding='utf-8'), encoding='utf-8')
    return runtime


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--splits', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--enl-rois', type=Path)
    parser.add_argument('--profile', choices=['full', 'checkpoint-evaluation'], default='full')
    parser.add_argument('--runtime-type', default='local_cpu')
    parser.add_argument('--setup-seconds', type=float, default=0.)
    parser.add_argument('--figures', action='store_true')
    parser.add_argument('--skip-synthetic', action='store_true')
    args = parser.parse_args(argv)
    runtime = run_evaluation(args.manifest, args.splits, args.config, args.output, enl_rois=args.enl_rois,
        profile=args.profile, runtime_type=args.runtime_type, external_setup_seconds=args.setup_seconds,
        synthetic=not args.skip_synthetic, figures=args.figures)
    print(json.dumps(runtime, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
