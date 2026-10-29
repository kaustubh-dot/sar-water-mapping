import csv

import numpy as np
import pytest

from sar_water.synthetic import phantom_splits, make_phantom, gamma_speckle, run_raw_baseline


def test_deterministic_diverse_phantoms_and_split_before_noise():
    splits = phantom_splits()
    assert len(splits) == 12
    assert list(splits.values()).count('train') == 6
    assert list(splits.values()).count('validation') == 3
    assert list(splits.values()).count('test') == 3
    refs = [make_phantom(i) for i in splits]
    assert len({x.tobytes() for x in refs}) == 12
    for i, ref in zip(splits, refs):
        assert ref.shape == (256,256) and ref.dtype == np.float32
        assert ref.min() >= .01 and ref.max() <= 1
        np.testing.assert_array_equal(ref, make_phantom(i))
        assert np.all(ref[8:24, 8:24] == ref[8,8])  # known homogeneous ROI
        assert np.max(abs(np.diff(ref, axis=1))) > .1  # sharp boundaries
        assert np.std(ref[160:240, 160:240]) > .01  # known texture


def test_gamma_mean_variance_and_unclipped_shared_realization():
    for looks in (1,4):
        ref = np.ones((512,512), dtype=np.float32)
        noisy = gamma_speckle(ref, looks=looks, seed=42)
        np.testing.assert_array_equal(noisy, gamma_speckle(ref, looks=looks, seed=42))
        assert noisy.mean() == pytest.approx(1,abs=.01)
        assert noisy.var() == pytest.approx(1/looks,rel=.03)
        assert noisy.max() > 1  # never clip to the reference range
        assert not np.array_equal(noisy, gamma_speckle(ref, looks=looks, seed=43))
    with pytest.raises(ValueError):
        gamma_speckle([1.], looks=0, seed=42)


def test_raw_baseline_exports_all_repeated_measurements(tmp_path):
    path = run_raw_baseline(tmp_path)
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 12*2*3
    assert {row['method'] for row in rows} == {'raw_noisy'}
    assert {row['source'] for row in rows} == {'simulated_backscatter'}
    assert {int(row['noise_seed']) for row in rows} == {42,43,44}
    assert all(float(row['mse']) > 0 and row['status'] == 'ok' for row in rows)
    assert (tmp_path / 'synthetic_splits.csv').exists()
