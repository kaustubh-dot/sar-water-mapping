import numpy as np
import pytest
from sar_water import filters


def test_locked_grid():
    assert filters.FILTER_GRID == {'raw': ({},), 'median': ({'window': 3}, {'window': 5}), 'lee': ({'window': 5}, {'window': 7}), 'log_bilateral': ({'window': 5, 'spatial_sigma': 2., 'color_sigma_db': 1.5}, {'window': 5, 'spatial_sigma': 2., 'color_sigma_db': 3.})}


@pytest.mark.parametrize('method,kwargs', [('raw', {}), ('median', {'window': 3}), ('lee', {'window': 5, 'looks': [1, 4]}), ('log_bilateral', {'color_sigma_db': 1.5})])
def test_constant_tiny_masks_and_independent_bands(method, kwargs):
    power = np.array([[[.2, np.nan, .2]], [[2., -9., 2.]]], dtype=np.float32)
    valid = np.array([[True, False, True]])
    original = power.copy()
    out = filters.filter_power(power, valid, method=method, **kwargs)
    assert out.shape == power.shape and out.dtype == np.float32
    np.testing.assert_array_equal(np.isnan(out), np.broadcast_to(~valid, power.shape))
    np.testing.assert_allclose(out[:, valid], [[.2, .2], [2., 2.]], rtol=1e-6)
    np.testing.assert_array_equal(power, original)
    for band in range(2):
        solo = np.stack([power[band], power[band]])
        solo_kwargs = dict(kwargs)
        if method == 'lee':
            solo_kwargs['looks'] = [kwargs['looks'][band]] * 2
        np.testing.assert_array_equal(out[band], filters.filter_power(solo, valid, method=method, **solo_kwargs)[0])


def test_median_half_sample_reflect_border_and_raw_identity():
    power = np.array([[[1, 10, 100]], [[2, 20, 200]]], dtype=np.float32)
    valid = np.ones((1, 3), bool)
    np.testing.assert_array_equal(filters.filter_power(power, valid), power)
    # SciPy reflect repeats the edge: [1,1,10] and [10,100,100].
    np.testing.assert_array_equal(filters.filter_power(power, valid, method='median', window=3), power)


def test_lee_analytic_border_and_scale_invariance_no_epsilon_floor():
    power = np.array([[[1, 2, 9]], [[2, 4, 18]]], dtype=np.float32)
    valid = np.ones((1, 3), bool)
    # Reflect window 5 at left is [2,1,1,2,9], repeated along y.
    m, v, looks = 3., 9.2, 4.
    s2 = max((v-m*m/looks)/(1+1/looks), 0)
    expected = m+s2/v*(1-m)
    out = filters.filter_power(power, valid, method='lee', window=5, looks=[4,4])
    assert out[0,0,0] == pytest.approx(expected, rel=1e-6)
    for scale in (1e-12, 1e12):
        rescaled = filters.filter_power(power*scale, valid, method='lee', window=5, looks=[4,4])
        np.testing.assert_allclose(rescaled/scale, out, rtol=2e-6)


def test_bilateral_analytic_reflection_db_and_scale():
    power = np.array([[[1., 2., 4.]], [[.1, .2, .4]]], dtype=np.float32)
    valid = np.ones((1,3), bool)
    # At first pixel the reflected x positions are [1,0,0,1,2].
    values = 10*np.log10(np.array([2.,1.,1.,2.,4.]))
    weights = np.exp(-np.arange(-2,3)**2/8 - values**2/(2*3.**2))
    expected = 10**(np.sum(values*weights)/weights.sum()/10)
    out = filters.filter_power(power, valid, method='log_bilateral', color_sigma_db=3.)
    assert out[0,0,0] == pytest.approx(expected, rel=1e-6)
    np.testing.assert_allclose(filters.filter_power(power*1e-10, valid, method='log_bilateral', color_sigma_db=3.)/1e-10, out, rtol=2e-6)


@pytest.mark.parametrize('method', ['raw', 'median', 'lee', 'log_bilateral'])
def test_holes_fill_and_positive_outputs(method):
    rng = np.random.default_rng(42)
    power = rng.lognormal(-4, 2, (2,9,11)).astype(np.float32)
    valid = np.ones((9,11), bool); valid[2:6,3:8] = False
    power[:,~valid] = np.nan
    kwargs = {'looks': [1,4]} if method == 'lee' else {}
    out = filters.filter_power(power, valid, method=method, **kwargs)
    assert np.isfinite(out[:,valid]).all() and np.all(out[:,valid] > 0)
    from sar_water.data import nearest_valid_fill
    filled = nearest_valid_fill(power, valid)
    expected = filters.filter_power(filled, np.ones_like(valid), method=method, **kwargs)
    np.testing.assert_array_equal(out[:,valid], expected[:,valid])


def test_filter_rejects_invalid_inputs_and_unlocked_parameters():
    power = np.ones((2,3,3), np.float32); valid = np.ones((3,3), bool)
    for kwargs in ({'method':'lee'}, {'method':'lee','looks':[0,1]}, {'method':'lee','looks':[1,np.nan]}, {'method':'median','window':7}, {'method':'log_bilateral','color_sigma_db':2}, {'method':'log_bilateral','spatial_sigma':3}, {'method':'raw','window':3}, {'method':'unknown'}):
        with pytest.raises(ValueError): filters.filter_power(power, valid, **kwargs)
    with pytest.raises(ValueError): filters.filter_power(power, ~valid)
    with pytest.raises(ValueError): filters.filter_power(power, valid[:1])
    power[0,0,0] = 0
    with pytest.raises(ValueError): filters.filter_power(power, valid)


def test_training_only_looks_records_and_median_lower_bound():
    power = np.array([[[1,3,2,6]], [[1,9,1,9]]], np.float32)
    patches = {'p': {'power':power, 'input_valid':np.ones((1,4), bool)}}
    rois = [{'patch_id':'p','y0':0,'y1':1,'x0':0,'x1':2}, {'patch_id':'p','y0':0,'y1':1,'x0':2,'x1':4}]
    result = filters.estimate_training_looks(patches, rois, {'p':'train'})
    np.testing.assert_allclose(result['looks'], [4., 25/16])
    assert len(result['rois']) == 4
    assert all(r['n'] == 2 and r['status'] == 'ok' and r['split'] == 'train' for r in result['rois'])
    assert result['rois'][0]['coordinates'] == [0,1,0,2]
    for split in ('validation','test'):
        with pytest.raises(ValueError): filters.estimate_training_looks(patches, rois, {'p':split})
    patches['p']['power'][:] = 1
    with pytest.raises(ValueError): filters.estimate_training_looks(patches, rois, {'p':'train'})
    with pytest.raises(ValueError): filters.estimate_training_looks(patches, [], {'p':'train'})
