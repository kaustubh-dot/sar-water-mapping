"""Locked low-backscatter water rules and separate small-component cleanup.

Otsu uses a 256-bin histogram spanning valid patch dB values. Equal maximum
between-class variances retain the first bin center. A unimodal land histogram
can still be divided into artificial water/land classes; no bimodality claim
or label-based inference correction is made.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import label

FIXED_GRID = {'VV': (-20, -18, -16, -14, -12, -10),
              'VH': (-28, -26, -24, -22, -20, -18)}


def threshold_db(db, input_valid, *, rule, threshold=None, fallback_threshold=None):
    """Return int8 -1/0/1 mask, actual threshold and explicit fallback status.

    Fixed/fallback numbers are supplied from training/validation calibration;
    this inference function receives no labels. Equality to threshold is land.
    """
    db, valid = np.asarray(db, dtype=np.float64), np.asarray(input_valid, dtype=bool)
    if db.ndim != 2 or db.shape != valid.shape:
        raise ValueError('expected matching 2D dB and input mask')
    if rule not in ('fixed', 'otsu'):
        raise ValueError('rule must be fixed or otsu')
    if not np.isfinite(db[valid]).all():
        raise ValueError('valid dB values must be finite')
    prediction = np.full(db.shape, -1, dtype=np.int8)
    if not valid.any():
        return dict(prediction=prediction, threshold_db=None, status='all_invalid')
    if rule == 'fixed':
        if threshold is None or not np.isfinite(threshold):
            raise ValueError('fixed rule requires finite threshold')
        status = 'fixed'
    else:
        if fallback_threshold is None or not np.isfinite(fallback_threshold):
            raise ValueError('Otsu requires calibrated finite fallback threshold')
        values = db[valid]
        if values.min() == values.max():
            threshold, status = fallback_threshold, 'constant_fixed_fallback'
        else:
            counts, edges = np.histogram(values, bins=256)
            centers = (edges[:-1] + edges[1:]) / 2
            weight = np.cumsum(counts).astype(np.float64)
            moment = np.cumsum(counts * centers)
            denominator = weight[:-1] * (weight[-1] - weight[:-1])
            numerator = (moment[-1] * weight[:-1] - moment[:-1] * weight[-1])**2
            variance = np.divide(numerator, denominator, out=np.zeros(255), where=denominator > 0)
            threshold, status = centers[int(np.argmax(variance))], 'otsu'
    prediction[valid] = db[valid] < threshold
    return dict(prediction=prediction, threshold_db=float(threshold), status=status)


def cleanup_water(prediction):
    """Delete 8-connected water components <16 pixels; -1 barriers; no holes."""
    prediction = np.asarray(prediction)
    if prediction.ndim != 2 or not np.isin(prediction, [-1, 0, 1]).all():
        raise ValueError('expected 2D -1/0/1 prediction')
    components, _ = label(prediction == 1, structure=np.ones((3, 3)))
    sizes = np.bincount(components.ravel())
    out = prediction.astype(np.int8, copy=True)
    out[(components > 0) & (sizes[components] < 16)] = 0
    return out
