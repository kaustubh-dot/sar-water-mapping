"""Fixture-only orchestration and validation selection tests."""
import importlib.util
import numpy as np
import pytest
from sar_water.data import adapt_arrays
from sar_water.metrics import summarize_water


def api():
    assert importlib.util.find_spec('sar_water.benchmark'), 'benchmark implementation missing'
    from sar_water import benchmark
    return benchmark


def patch():
    return adapt_arrays(np.array([[[-25., -5., -25., -5.]]] * 2),
                        np.array([[1, 0, -1, 1]]), units='db', band_order='VV,VH',
                        input_mask=np.array([[1, 1, 1, 0]], bool))


def test_evaluate_independent_masks_and_cleanup_toggle():
    b = api()
    plain = b.evaluate_patch(patch(), method='raw', channel='VV', rule='fixed', threshold=-20)
    assert plain['counts'] == dict(tp=1, fp=0, fn=0, tn=1)
    assert plain['prediction'].tolist() == [[1, 0, 1, -1]]
    cleaned = b.evaluate_patch(patch(), method='raw', channel='VV', rule='fixed', threshold=-20, cleanup=True)
    assert cleaned['counts'] == dict(tp=0, fp=0, fn=1, tn=1)


def test_validation_search_full_grid_common_numeric_and_no_test_selection():
    b = api()
    with pytest.raises(ValueError, match='validation'):
        b.validation_search({'p': patch()}, {'p': 'test'}, looks=[1, 1], fallback_thresholds={'VV': -20, 'VH': -20})
    result = b.validation_search({'p': patch()}, {'p': 'validation'}, looks=[1, 1], fallback_thresholds={'VV': -20, 'VH': -20})
    assert len(result['validation_table']) == 98  # 7 settings x (2 Otsu +12fixed)
    assert len(result['primary']) == 4 and all(not row['cleanup'] for row in result['primary'])
    assert len(result['cleanup_ablation']) == 4
    assert result['status'] == 'pending_real_calibration'
    assert len({(r['channel'], r['rule'], r['threshold']) for r in result['primary']}) == 1
    assert all(r['summary']['macro_patch_ids'] == ['p'] for r in result['primary'])


def test_selection_uses_pooled_not_macro_and_compute_tiebreak():
    b = api()
    rows = []
    for channel, pooled, macro, seconds in [('VV', .8, .1, 2), ('VH', .7, .9, 1)]:
        for method in ('raw', 'median', 'lee', 'log_bilateral'):
            rows.append(dict(channel=channel, rule='fixed', threshold=-20, method=method,
                             parameters={}, seconds=seconds, cleanup=False,
                             summary={'pooled': {'iou': pooled}, 'macro': {'iou': macro}}))
    selected = b.select_validation(rows)
    assert selected['common']['channel'] == 'VV'
    for r in rows: r['summary']['pooled']['iou'] = .8
    assert b.select_validation(rows)['common']['channel'] == 'VH'


def test_parameter_selection_uses_summed_counts_and_reports_dry_false_positives():
    b = api()
    # A: pooled90/110, macro(.9+0)/2=.45; B: pooled60/100,
    # macro(50/90+1)/2=.7778. A must win despite its lower macro score.
    a = summarize_water({'large': dict(tp=90, fp=0, fn=10, tn=0),
                         'small': dict(tp=0, fp=0, fn=10, tn=0),
                         'dry': dict(tp=0, fp=0, fn=0, tn=10)})
    bb = summarize_water({'large': dict(tp=50, fp=0, fn=50, tn=0),
                          'small': dict(tp=10, fp=0, fn=0, tn=0),
                          'dry': dict(tp=0, fp=0, fn=0, tn=10)})
    rows = [dict(channel='VV', rule='fixed', threshold=-20, method=m,
                 parameters={'window': 3}, seconds=2, summary=a, cleanup=False)
            for m in ('raw', 'median', 'lee', 'log_bilateral')]
    rows.append(dict(rows[1], parameters={'window': 5}, summary=bb, seconds=1))
    selected = b.select_validation(rows)
    assert selected['primary'][1]['parameters'] == {'window': 3}
    assert a['pooled']['iou'] > bb['pooled']['iou'] and a['macro']['iou'] < bb['macro']['iou']
    assert a['macro_patch_ids'] == ['large', 'small'] and a['dry']['valid_pixels'] == 10


def test_disk_pair_roundtrip(tmp_path):
    rasterio = pytest.importorskip('rasterio')
    from rasterio.transform import from_origin
    b = api()
    image, mask = tmp_path/'sar.tif', tmp_path/'mask.tif'
    profile = dict(driver='GTiff', height=2, width=2, crs='EPSG:4326', transform=from_origin(0, 2, 1, 1))
    with rasterio.open(image, 'w', count=2, dtype='float32', **profile) as dst:
        dst.write(np.array([[[-25., -5.], [-25., -5.]]] * 2, dtype=np.float32))
    with rasterio.open(mask, 'w', count=1, dtype='int8', **profile) as dst:
        dst.write(np.array([[1, 0], [-1, 0]], dtype=np.int8), 1)
    pair = dict(patch_id='fixture', image_path=str(image), mask_path=str(mask), units='db',
                band_order='VV,VH', source='synthetic fixture', label_source='manual_fixture')
    result = b.benchmark_pair(pair, method='raw', channel='VV', rule='fixed', threshold=-20)
    assert result['counts'] == dict(tp=1, fp=0, fn=0, tn=2)


def test_validation_cache_holds_only_one_setting_and_enforces_budget():
    b=api();p=patch()
    result=b.validation_search({'p':p},{'p':'validation'},looks=[1,1],fallback_thresholds={'VV':-20,'VH':-20},cache_limit_bytes=p.power.nbytes)
    assert result['cache_peak_bytes']==p.power.nbytes
    assert len(result['validation_table'])==98
    with pytest.raises(ValueError,match='cache budget'):
        b.validation_search({'p':p},{'p':'validation'},looks=[1,1],fallback_thresholds={'VV':-20,'VH':-20},cache_limit_bytes=p.power.nbytes-1)
