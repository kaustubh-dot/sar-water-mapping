import math

import numpy as np
import pytest

from sar_water.metrics import confusion_counts, water_scores, summarize_water, enl, psnr


def test_hand_calculated_confusion_and_independent_masks():
    target = np.array([1, 1, 1, 0, 0, 0, -1, 1])
    pred = np.array([1, 1, 0, 1, 0, 0, 1, 0])
    counts = confusion_counts(pred, target, input_valid=[1,1,1,1,1,1,1,0],
                              label_valid=[1,1,1,1,1,0,1,1])
    assert counts == dict(tp=2, fp=1, fn=1, tn=1)
    scores = water_scores(counts)
    assert scores['iou'] == .5
    assert scores['f1'] == pytest.approx(2/3)
    assert scores['precision'] == scores['recall'] == pytest.approx(2/3)


def test_empty_water_and_no_valid_scores():
    assert water_scores(dict(tp=0, fp=0, fn=0, tn=3)) == dict(iou=None, f1=None, precision=None, recall=None)
    assert all(v is None for v in water_scores(dict(tp=0, fp=0, fn=0, tn=0)).values())
    false_alarm = water_scores(dict(tp=0, fp=2, fn=0, tn=1))
    assert false_alarm == dict(iou=0., f1=0., precision=0., recall=None)
    miss = water_scores(dict(tp=0, fp=0, fn=2, tn=1))
    assert miss['precision'] is None and miss['recall'] == 0


def test_fixed_macro_membership_and_separate_dry_false_positives():
    a = dict(wet=dict(tp=1, fp=0, fn=1, tn=0), dry=dict(tp=0, fp=0, fn=0, tn=4), invalid=dict(tp=0, fp=0, fn=0, tn=0))
    b = dict(wet=dict(tp=0, fp=0, fn=2, tn=0), dry=dict(tp=0, fp=2, fn=0, tn=2), invalid=dict(tp=0, fp=0, fn=0, tn=0))
    result_a, result_b = summarize_water(a), summarize_water(b)
    assert result_a['macro_patch_ids'] == result_b['macro_patch_ids'] == ['wet']
    assert result_a['macro']['iou'] == .5
    assert result_b['pooled']['iou'] == 0
    assert result_b['dry'] == dict(patch_count=1, valid_pixels=4, false_positive_pixels=2, false_positive_rate=.5, fraction_with_false_positives=1.)
    assert result_b['no_valid_patch_count'] == 1
    with pytest.raises(ValueError, match='fixed'):
        summarize_water(b, macro_patch_ids=['dry'])


def test_pooled_scores_are_not_macro_average():
    result = summarize_water(dict(a=dict(tp=1, fp=0, fn=0, tn=0), b=dict(tp=0, fp=0, fn=3, tn=0)))
    assert result['pooled']['iou'] == .25
    assert result['macro']['iou'] == .5


@pytest.mark.parametrize('pred,target', [([1,2],[1,0]), ([1],[2]), ([1,0],[1])])
def test_confusion_rejects_unsupported_values_or_shapes(pred, target):
    with pytest.raises(ValueError):
        confusion_counts(pred, target)


def test_enl_population_variance_and_explicit_undefined_status():
    assert enl([1.,3.]) == dict(value=pytest.approx(4.), status='ok', n=2)
    assert enl([2.,2.]) == dict(value=None, status='zero_variance', n=2)
    assert enl([2.]) == dict(value=None, status='insufficient_samples', n=1)
    assert enl([np.nan,2.,4.], valid=[False,True,True])['value'] == 9
    for invalid in ([0.,1.], [-1.,1.], [np.nan,1.]):
        with pytest.raises(ValueError):
            enl(invalid)


def test_psnr_known_reference_range_and_identity():
    assert psnr([0.,1.], [.5,.5], data_range=1.) == dict(value=pytest.approx(10*math.log10(4)), status='ok', mse=.25, n=2)
    assert psnr([0.,1.], [0.,1.], data_range=1.)['status'] == 'identity'
    assert math.isinf(psnr([0.,1.], [0.,1.], data_range=1.)['value'])
    assert psnr([0.,1.], [.5,.5], data_range=2.)['value'] == pytest.approx(10*math.log10(16))
    assert psnr([np.nan,1.], [9.,.5], data_range=1., valid=[False,True])['mse'] == .25
    assert psnr([0.], [1.], data_range=1., valid=[False])['value'] is None
    for data_range in [0,-1,np.inf,np.nan]:
        with pytest.raises(ValueError):
            psnr([1.], [2.], data_range=data_range)
