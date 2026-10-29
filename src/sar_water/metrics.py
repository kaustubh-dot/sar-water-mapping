"""Water scores, positive-power ENL, and known-reference synthetic PSNR.

Undefined numbers are None. PSNR identity is the sole infinite numeric result,
with an explicit status; serialize that status rather than nonstandard JSON inf.
"""
from __future__ import annotations

import numpy as np


def _mask(shape, valid):
    if valid is None:
        return np.ones(shape, dtype=bool)
    mask = np.asarray(valid, dtype=bool)
    if mask.shape != shape:
        raise ValueError('validity mask shape mismatch')
    return mask


def confusion_counts(prediction, target, *, input_valid=None, label_valid=None):
    """Score the input/label validity intersection; -1 labels are invalid.

    Predictions must be binary on scored pixels. Unsupported labels are always
    rejected, even behind a validity mask, matching the data adapter contract.
    """
    prediction, target = np.asarray(prediction), np.asarray(target)
    if prediction.shape != target.shape:
        raise ValueError('prediction/target shape mismatch')
    if not np.isin(target, [-1, 0, 1]).all():
        raise ValueError('unsupported target labels')
    valid = _mask(target.shape, input_valid) & _mask(target.shape, label_valid) & (target != -1)
    if not np.isin(prediction[valid], [0, 1]).all():
        raise ValueError('scored predictions must be binary')
    p, t = prediction[valid] == 1, target[valid] == 1
    return dict(tp=int(np.sum(p & t)), fp=int(np.sum(p & ~t)),
                fn=int(np.sum(~p & t)), tn=int(np.sum(~p & ~t)))


def _counts(counts):
    if set(counts) != {'tp', 'fp', 'fn', 'tn'}:
        raise ValueError('expected tp/fp/fn/tn counts')
    if any(not isinstance(v, (int, np.integer)) or v < 0 for v in counts.values()):
        raise ValueError('counts must be nonnegative integers')
    return counts


def _ratio(numerator, denominator):
    return float(numerator / denominator) if denominator else None


def water_scores(counts):
    c = _counts(counts)
    tp, fp, fn = c['tp'], c['fp'], c['fn']
    return dict(iou=_ratio(tp, tp+fp+fn), f1=_ratio(2*tp, 2*tp+fp+fn),
                precision=_ratio(tp, tp+fp), recall=_ratio(tp, tp+fn))


def summarize_water(patches, *, macro_patch_ids=None):
    """Summarize patch_id -> confusion counts from a shared scoring mask.

    The eligible macro set depends ONLY on ground truth water counts. Passing
    a fixed set from another method verifies it equals this eligible set; callers
    must also keep their source patch collection and masks identical.
    """
    patches = {key: _counts(value) for key, value in patches.items()}
    eligible = sorted(key for key, c in patches.items() if c['tp']+c['fn'] > 0)
    if macro_patch_ids is not None and (len(macro_patch_ids) != len(eligible) or set(macro_patch_ids) != set(eligible)):
        raise ValueError('fixed macro patch set must equal ground-truth-water-positive set')
    total = {name: sum(c[name] for c in patches.values()) for name in ('tp','fp','fn','tn')}
    per_patch = {key: water_scores(c) for key, c in patches.items()}
    macro, undefined = {}, {}
    for name in ('iou','f1','precision','recall'):
        values = [per_patch[key][name] for key in eligible if per_patch[key][name] is not None]
        macro[name] = float(np.mean(values)) if values else None
        undefined[name] = len(eligible)-len(values)
    dry = [c for c in patches.values() if c['tp']+c['fn'] == 0 and sum(c.values()) > 0]
    dry_pixels, dry_fp = sum(c['tn']+c['fp'] for c in dry), sum(c['fp'] for c in dry)
    return dict(counts=total, pooled=water_scores(total), per_patch=per_patch,
                macro=macro, macro_patch_ids=eligible, macro_undefined_counts=undefined,
                undefined_water_patch_count=sum(s['iou'] is None for s in per_patch.values()),
                no_valid_patch_count=sum(sum(c.values()) == 0 for c in patches.values()),
                dry=dict(patch_count=len(dry), valid_pixels=dry_pixels,
                         false_positive_pixels=dry_fp, false_positive_rate=_ratio(dry_fp,dry_pixels),
                         fraction_with_false_positives=_ratio(sum(c['fp']>0 for c in dry),len(dry))))


def enl(power, *, valid=None):
    """ENL for ONE preselected homogeneous positive-power ROI, ddof=0."""
    power = np.asarray(power, dtype=np.float64)
    values = power[_mask(power.shape, valid)]
    if not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError('ENL requires finite positive power')
    n = int(values.size)
    if n < 2:
        return dict(value=None, status='insufficient_samples', n=n)
    # Scale invariance avoids overflow/underflow in the ratio of squared units.
    scaled = values / values.max()
    variance = np.var(scaled, ddof=0)
    if variance == 0:
        return dict(value=None, status='zero_variance', n=n)
    result = float(np.mean(scaled)**2 / variance)
    return dict(value=result if np.isfinite(result) else None,
                status='ok' if np.isfinite(result) else 'nonfinite', n=n)


def psnr(reference, estimate, *, data_range, valid=None):
    """Known-reference PSNR; callers must supply the controlled float range."""
    if not np.isfinite(data_range) or data_range <= 0:
        raise ValueError('data_range must be finite and positive')
    reference, estimate = np.asarray(reference,dtype=np.float64), np.asarray(estimate,dtype=np.float64)
    if reference.shape != estimate.shape:
        raise ValueError('reference/estimate shape mismatch')
    mask = _mask(reference.shape,valid)
    if not np.isfinite(reference[mask]).all() or not np.isfinite(estimate[mask]).all():
        raise ValueError('PSNR requires finite scored values')
    n = int(mask.sum())
    if n == 0:
        return dict(value=None, status='no_valid_pixels', mse=None, n=0)
    mse = float(np.mean((reference[mask]-estimate[mask])**2))
    if mse == 0:
        return dict(value=float('inf'), status='identity', mse=0., n=n)
    value = float(20*np.log10(data_range)-10*np.log10(mse))
    return dict(value=value, status='ok', mse=mse, n=n)
