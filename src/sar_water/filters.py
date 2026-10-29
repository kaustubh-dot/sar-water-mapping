"""Bounded independent-band power denoisers and training-only looks estimates.

Borders use SciPy half-sample symmetric ``reflect`` (edge pixel repeated),
matching NumPy ``symmetric`` padding in the bilateral implementation. Invalid
SAR locations use data.nearest_valid_fill before filtering and return as NaN.
No method accepts labels. Log-bilateral is not an unbiased power estimator.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter, uniform_filter

from .data import nearest_valid_fill
from .metrics import enl

FILTER_GRID = {
    'raw': ({},),
    'median': ({'window': 3}, {'window': 5}),
    'lee': ({'window': 5}, {'window': 7}),
    'log_bilateral': (
        {'window': 5, 'spatial_sigma': 2., 'color_sigma_db': 1.5},
        {'window': 5, 'spatial_sigma': 2., 'color_sigma_db': 3.}),
}


def _power_input(power, input_valid):
    power = np.asarray(power, dtype=np.float32)
    valid = np.asarray(input_valid, dtype=bool)
    if power.ndim != 3 or power.shape[0] != 2 or power.shape[1:] != valid.shape or not all(valid.shape):
        raise ValueError('expected [VV,VH] power and matching nonempty 2D input mask')
    if not valid.any():
        raise ValueError('all-invalid SAR patch')
    if np.any(~np.isfinite(power[:,valid]) | (power[:,valid] <= 0)):
        raise ValueError('valid power must be finite and positive')
    return power, valid


def _bilateral_db(band, color_sigma_db):
    db = 10*np.log10(band.astype(np.float64))
    padded = np.pad(db, 2, mode='symmetric')
    numerator = np.zeros_like(db)
    denominator = np.zeros_like(db)
    height, width = db.shape
    for dy in range(-2,3):
        for dx in range(-2,3):
            neighbor = padded[2+dy:2+dy+height, 2+dx:2+dx+width]
            weight = np.exp(-(dx*dx+dy*dy)/8 - (neighbor-db)**2/(2*color_sigma_db**2))
            numerator += weight*neighbor
            denominator += weight
    return np.power(10., numerator/denominator/10)


def filter_power(power, input_valid, *, method='raw', window=None, looks=None,
                 spatial_sigma=None, color_sigma_db=None):
    """Apply one locked setting; Lee requires explicit known/frozen VV,VH looks.

    Raw is a float32 identity on valid power. Each output restores NaNs outside
    input_valid. No variance epsilon or per-image intensity stretching is used.
    """
    power, valid = _power_input(power, input_valid)
    if method not in FILTER_GRID:
        raise ValueError('unknown denoiser')
    if method != 'lee' and looks is not None:
        raise ValueError('looks is only valid for Lee')
    if method != 'log_bilateral' and (spatial_sigma is not None or color_sigma_db is not None):
        raise ValueError('bilateral parameters only apply to log_bilateral')
    if method == 'raw' and window is not None:
        raise ValueError('raw has no window')
    if method in ('median','lee'):
        window = (3 if method == 'median' else 5) if window is None else window
        if window not in ((3,5) if method == 'median' else (5,7)):
            raise ValueError('window outside locked grid')
    if method == 'lee':
        looks = np.asarray(looks, dtype=np.float64)
        if looks.shape != (2,) or not np.isfinite(looks).all() or np.any(looks <= 0):
            raise ValueError('Lee requires finite positive per-band looks')
    if method == 'log_bilateral':
        window = 5 if window is None else window
        spatial_sigma = 2. if spatial_sigma is None else spatial_sigma
        color_sigma_db = 1.5 if color_sigma_db is None else color_sigma_db
        if window != 5 or spatial_sigma != 2. or color_sigma_db not in (1.5,3.):
            raise ValueError('bilateral parameters outside locked grid')
    filled = nearest_valid_fill(power, valid)
    out = np.empty_like(power)
    for index, band in enumerate(filled):
        if method == 'raw':
            result = band
        elif method == 'median':
            result = median_filter(band, size=window, mode='reflect')
        elif method == 'lee':
            band = band.astype(np.float64)
            mean = uniform_filter(band, size=window, mode='reflect')
            variance = np.maximum(uniform_filter(band*band, size=window, mode='reflect')-mean*mean, 0.)
            signal_variance = np.maximum((variance-mean*mean/looks[index])/(1+1/looks[index]), 0.)
            weight = np.divide(signal_variance, variance, out=np.zeros_like(variance), where=variance>0)
            result = mean + np.clip(weight,0,1)*(band-mean)
        else:
            result = _bilateral_db(band, color_sigma_db)
        out[index] = result
    if np.any(~np.isfinite(out[:,valid]) | (out[:,valid] <= 0)):
        raise ValueError('filter produced nonfinite/nonpositive valid power')
    out[:,~valid] = np.nan
    return out


def estimate_training_looks(patches, rois, membership):
    """Return per-band median ENL >=1 and all ROI records for freezing.

    patches maps patch_id to dictionaries with power and input_valid. Rectangles
    are half-open y0:y1,x0:x1, selected as homogeneous from raw training SAR.
    This function checks training membership and numeric suitability; it cannot
    certify scene homogeneity. Invalid input pixels are excluded, never filled
    for estimation. Nonconstant finite ENLs alone contribute to the medians.
    """
    records, values = [], [[], []]
    for roi in rois:
        patch_id = roi['patch_id']
        if membership.get(patch_id) != 'train':
            raise ValueError('looks estimation requires training-only ROIs')
        patch = patches[patch_id]
        power, valid = _power_input(patch['power'], patch['input_valid'])
        coordinates = [roi[key] for key in ('y0','y1','x0','x1')]
        if any(not isinstance(v, (int,np.integer)) for v in coordinates):
            raise ValueError('ROI coordinates must be integers')
        y0,y1,x0,x1 = coordinates
        if not (0 <= y0 < y1 <= valid.shape[0] and 0 <= x0 < x1 <= valid.shape[1]):
            raise ValueError('ROI outside source patch')
        for index, band in enumerate(('VV','VH')):
            score = enl(power[index,y0:y1,x0:x1], valid=valid[y0:y1,x0:x1])
            records.append(dict(patch_id=patch_id, split='train', band=band,
                                coordinates=[int(v) for v in coordinates], **score))
            if score['status'] == 'ok':
                values[index].append(score['value'])
    if any(not band_values for band_values in values):
        raise ValueError('no usable nonconstant homogeneous training ROI for each band')
    return dict(looks=[max(1.,float(np.median(v))) for v in values], rois=records,
                usable_roi_counts=[len(v) for v in values],
                interpretation='effective looks estimate; not independent physical looks')
