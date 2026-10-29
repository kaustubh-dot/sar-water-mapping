"""Development selection must not relabel official partitions or admit weak pairs."""
import importlib.util
from pathlib import Path
import pytest


def module():
    spec = importlib.util.spec_from_file_location('prepare_development_data', Path(__file__).parents[1]/'scripts'/'prepare_development_data.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_selection_preserves_official_membership_and_ignores_csv_order():
    mod = module()
    splits = {'train': [('Ghana_1_S1Hand.tif','Ghana_1_LabelHand.tif'),('India_2_S1Hand.tif','India_2_LabelHand.tif')],
              'validation': [('Spain_3_S1Hand.tif','Spain_3_LabelHand.tif')],
              'test': [('USA_4_S1Hand.tif','USA_4_LabelHand.tif')]}
    selected = mod.select_pairs(splits, {'train':2,'validation':1,'test':1})
    assert {(r['patch_id'],r['split']) for r in selected} == {('Ghana_1','train'),('India_2','train'),('Spain_3','validation'),('USA_4','test')}
    assert selected == mod.select_pairs({k:list(reversed(v)) for k,v in splits.items()}, {'train':2,'validation':1,'test':1})
    bounded = mod.select_pairs(splits, {'train':1,'validation':1,'test':1})
    assert [r['patch_id'] for r in bounded] == ['Ghana_1','Spain_3','USA_4']
    assert bounded == mod.select_pairs({k:list(reversed(v)) for k,v in splits.items()}, {'train':1,'validation':1,'test':1})


def test_selection_rejects_cross_split_duplicate_and_weak_labels():
    mod = module()
    pair = ('Ghana_1_S1Hand.tif','Ghana_1_LabelHand.tif')
    with pytest.raises(ValueError,match='duplicate'):
        mod.select_pairs({'train':[pair],'validation':[pair],'test':[('USA_4_S1Hand.tif','USA_4_LabelHand.tif')]}, {'train':1,'validation':1,'test':1})
    with pytest.raises(ValueError,match='hand-labeled'):
        mod.select_pairs({'train':[('Ghana_1_S1Hand.tif','Ghana_1_S1OtsuLabelHand.tif')]}, {'train':1})


def test_hyphenated_official_event_name_is_accepted_without_relaxing_pairing():
    selected = module().select_pairs({'train':[('Sri-Lanka_42_S1Hand.tif','Sri-Lanka_42_LabelHand.tif')]}, {'train':1})
    assert selected[0]['patch_id'] == 'Sri-Lanka_42'
