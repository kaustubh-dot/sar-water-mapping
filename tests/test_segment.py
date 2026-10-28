"""Segmentation contracts on artificial dB arrays only."""
import importlib.util
import numpy as np
import pytest


def api():
    assert importlib.util.find_spec('sar_water.segment'), 'segment implementation missing'
    from sar_water import segment
    return segment


def test_fixed_strict_low_backscatter_and_invalid():
    result = api().threshold_db(np.array([[-21., -20., np.nan]]),
                                np.array([[1, 1, 0]], bool), rule='fixed', threshold=-20)
    assert result['prediction'].tolist() == [[1, 0, -1]]
    assert result['status'] == 'fixed'


def test_otsu_uses_only_valid_pixels_and_reports_constant_fallback():
    s = api()
    db = np.array([[-30., -30., -5., -5., -1000.]])
    result = s.threshold_db(db, np.array([[1, 1, 1, 1, 0]], bool), rule='otsu', fallback_threshold=-20)
    assert result['prediction'].tolist() == [[1, 1, 0, 0, -1]]
    constant = s.threshold_db(np.full((2, 2), -20.), np.ones((2, 2), bool), rule='otsu', fallback_threshold=-20)
    assert constant['status'] == 'constant_fixed_fallback'
    assert constant['threshold_db'] == -20 and not constant['prediction'].any()
    with pytest.raises(ValueError, match='fallback'):
        s.threshold_db(np.zeros((2, 2)), np.ones((2, 2), bool), rule='otsu')


def test_all_invalid_returns_no_threshold_and_unimodal_can_invent_water():
    s = api()
    result = s.threshold_db(np.full((2, 2), np.nan), np.zeros((2, 2), bool), rule='otsu')
    assert result['status'] == 'all_invalid' and result['threshold_db'] is None
    assert (result['prediction'] == -1).all()
    result = s.threshold_db(np.arange(100.).reshape(10, 10), np.ones((10, 10), bool), rule='otsu', fallback_threshold=-20)
    assert 0 < result['prediction'].sum() < 100  # all-land ramp has artificial water


def test_cleanup_eight_connected_size16_invalid_barriers_and_no_holefill():
    s = api()
    p = np.zeros((12, 12), np.int8)
    p[0:4, 0:4] = 1  # exactly16 retained
    p[4, 4] = 1  # diagonal connection retained
    p[8:11, 8:11] = 1  # 9 removed
    p[1, 1] = 0  # hole remains; main component still16
    p[0, 11] = -1
    cleaned = s.cleanup_water(p)
    assert cleaned[4, 4] == 1 and cleaned[1, 1] == 0
    assert cleaned[8:11, 8:11].sum() == 0 and cleaned[0, 11] == -1
    barrier = np.ones((4, 9), np.int8); barrier[:, 4] = -1
    assert (s.cleanup_water(barrier)[:, :4] == 1).all()
    barrier[:, 5:] = 0; barrier[:3, 5:] = 1
    assert not s.cleanup_water(barrier)[:, 5:].any()
    separated = np.ones((3, 11), np.int8); separated[:, 5] = -1
    assert (s.cleanup_water(separated)[:, :5] == 0).all()
    assert (s.cleanup_water(separated)[:, 6:] == 0).all()
