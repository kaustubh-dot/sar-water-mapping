"""Disk-to-mask scoring and bounded validation-only classical selection.

Search returns development choices with pending_real_calibration status; it
never edits or freezes configs/experiment.json. Callers must separately complete
the actual data audit, frozen splits and looks gates before real calibration.
"""
from __future__ import annotations

from time import perf_counter
import numpy as np

from .data import audit_pair, power_to_db
from .filters import FILTER_GRID, filter_power
from .metrics import confusion_counts, summarize_water
from .segment import FIXED_GRID, cleanup_water, threshold_db


def _segment_filtered(patch, filtered, *, channel, rule, threshold=None,
                      fallback_threshold=None, cleanup=False):
    if channel not in FIXED_GRID:
        raise ValueError('channel must be VV or VH')
    result = threshold_db(power_to_db(filtered)[('VV', 'VH').index(channel)],
                          patch.input_valid, rule=rule, threshold=threshold,
                          fallback_threshold=fallback_threshold)
    if cleanup:
        result['prediction'] = cleanup_water(result['prediction'])
    result['counts'] = confusion_counts(result['prediction'], patch.labels,
                                        input_valid=patch.input_valid, label_valid=patch.label_valid)
    return result


def evaluate_patch(patch, *, method, channel, rule, parameters=None, looks=None,
                   threshold=None, fallback_threshold=None, cleanup=False):
    """Power filtering -> dB threshold -> independent-mask confusion counts."""
    start = perf_counter()
    filtered = (filter_power(patch.power, patch.input_valid, method=method,
                             **(parameters or {}), **({'looks': looks} if method == 'lee' else {}))
                if patch.input_valid.any() else np.full_like(patch.power, np.nan))
    result = _segment_filtered(patch, filtered, channel=channel, rule=rule,
                               threshold=threshold, fallback_threshold=fallback_threshold, cleanup=cleanup)
    result['seconds'] = perf_counter() - start
    result['cleanup'] = bool(cleanup)
    return result


def benchmark_pair(pair, **settings):
    """One audited disk pair to native mask and scores; no parameter selection."""
    row, patch = audit_pair(pair)
    result = evaluate_patch(patch, **settings)
    result['audit'] = row
    return result


def select_validation(rows):
    """Select settings by pooled IoU, then common rule by mean four-family IoU.

    Exact ties use total measured filter-plus-segmentation compute seconds.
    Undefined pooled IoU blocks selection rather than manufacturing a score.
    """
    groups = {}
    for row in rows:
        if row.get('cleanup', False):
            raise ValueError('primary selection requires cleanup disabled')
        iou = row['summary']['pooled']['iou']
        if iou is None or not np.isfinite(iou):
            raise ValueError('validation requires defined pooled water IoU')
        key = (row['channel'], row['rule'], row['threshold'])
        methods = groups.setdefault(key, {})
        previous = methods.get(row['method'])
        if previous is None or (-iou, row['seconds']) < (-previous['summary']['pooled']['iou'], previous['seconds']):
            methods[row['method']] = row
    candidates = []
    for key, methods in groups.items():
        if set(methods) != set(FILTER_GRID):
            raise ValueError('every common candidate requires all four families')
        chosen = [methods[name] for name in FILTER_GRID]
        candidates.append((float(np.mean([r['summary']['pooled']['iou'] for r in chosen])),
                           sum(r['seconds'] for r in chosen), key, chosen))
    if not candidates:
        raise ValueError('empty validation table')
    score, seconds, key, primary = min(candidates, key=lambda item: (-item[0], item[1]))
    selected = min((r for r in primary if r['method'] != 'raw'),
                   key=lambda r: (-r['summary']['pooled']['iou'], r['seconds']))
    return dict(common=dict(channel=key[0], rule=key[1], threshold=key[2],
                            mean_pooled_iou=score, seconds=seconds), primary=primary,
                selected_filter=selected)


def validation_search(patches, membership, *, looks, fallback_thresholds):
    """Evaluate exact bounded grid on explicitly validation-only Patch mapping.

    Filter outputs (SAR only) are cached once per setting and patch, outside
    threshold loops. Labels are used only for validation metrics. Reported row
    time includes filtering once plus that row's segmentation/scoring, without
    disk I/O. Otsu threshold/status records retain constant-patch fallbacks.
    """
    if not patches or any(membership.get(key) != 'validation' for key in patches):
        raise ValueError('selection accepts validation membership only')
    if set(fallback_thresholds) != set(FIXED_GRID) or any(not np.isfinite(v) for v in fallback_thresholds.values()):
        raise ValueError('finite calibrated fallback thresholds required for VV/VH')
    rows, cache = [], {}
    macro_ids = sorted(key for key, patch in patches.items()
                       if np.any((patch.labels == 1) & patch.input_valid & patch.label_valid))
    for method, settings in FILTER_GRID.items():
        for setting_index, parameters in enumerate(settings):
            filtered, filter_seconds = {}, 0.
            for key, patch in patches.items():
                start = perf_counter()
                filtered[key] = (filter_power(patch.power, patch.input_valid, method=method,
                                             **parameters, **({'looks': looks} if method == 'lee' else {}))
                                 if patch.input_valid.any() else np.full_like(patch.power, np.nan))
                filter_seconds += perf_counter() - start
            cache[(method, setting_index)] = filtered
            for channel, thresholds in FIXED_GRID.items():
                for rule, threshold in [('otsu', None)] + [('fixed', t) for t in thresholds]:
                    counts, records = {}, {}
                    start = perf_counter()
                    for key, patch in patches.items():
                        result = _segment_filtered(patch, filtered[key], channel=channel, rule=rule,
                                                   threshold=threshold, fallback_threshold=fallback_thresholds[channel])
                        counts[key] = result['counts']
                        records[key] = dict(threshold_db=result['threshold_db'], status=result['status'])
                    rows.append(dict(method=method, parameters=dict(parameters), setting_index=setting_index,
                                     channel=channel, rule=rule, threshold=threshold, cleanup=False,
                                     seconds=filter_seconds + perf_counter() - start,
                                     summary=summarize_water(counts, macro_patch_ids=macro_ids), patches=records))
    selection = select_validation(rows)
    ablation = []
    for row in (selection['primary'][0], selection['selected_filter']):
        for cleanup in (False, True):
            counts = {}
            start = perf_counter()
            for key, patch in patches.items():
                result = _segment_filtered(patch, cache[(row['method'], row['setting_index'])][key],
                                           channel=row['channel'], rule=row['rule'], threshold=row['threshold'],
                                           fallback_threshold=fallback_thresholds[row['channel']], cleanup=cleanup)
                counts[key] = result['counts']
            ablation.append(dict(method=row['method'], parameters=row['parameters'], cleanup=cleanup,
                                 seconds=perf_counter() - start, timing_scope='segmentation_and_scoring_only_cached_filter',
                                 summary=summarize_water(counts, macro_patch_ids=macro_ids)))
    return dict(status='pending_real_calibration', validation_table=rows, cleanup_ablation=ablation,
                fallback_thresholds=dict(fallback_thresholds), **selection)
