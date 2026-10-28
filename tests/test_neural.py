"""CPU fixtures for the locked segmenter; these are not real training results."""
import importlib.util
import json

import numpy as np
import pytest

torch = pytest.importorskip('torch')
from sar_water.data import Patch, adapt_arrays


@pytest.fixture(autouse=True)
def one_cpu_thread():
    before = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(before)


def api():
    assert importlib.util.find_spec('sar_water.model'), 'locked neural model missing'
    assert importlib.util.find_spec('sar_water.train'), 'paired training implementation missing'
    from sar_water import model, train
    return model, train


def patch(db, labels=None, input_valid=None, label_valid=None):
    db = np.asarray(db, dtype=np.float32)
    return adapt_arrays(db, np.zeros(db.shape[1:], np.int8) if labels is None else labels,
                        units='db', band_order='VV,VH', input_mask=input_valid,
                        label_mask=label_valid)


class UnreadTestPatch:
    def __getattribute__(self, name):
        raise AssertionError('test data must not be read during training')


def development_fixture():
    rng = np.random.default_rng(11)
    labels = np.zeros((256, 256), np.int8)
    labels[:, :128] = 1
    train = patch(rng.normal(-14, 2, (2, 256, 256)), labels)
    valid_labels = np.zeros((17, 19), np.int8)
    valid_labels[:, :9] = 1
    val = patch(rng.normal(-14, 2, (2, 17, 19)), valid_labels)
    patches = {'train': train, 'val': val, 'test': UnreadTestPatch()}
    membership = {'train': 'train', 'val': 'validation', 'test': 'test'}
    rows = [dict(patch_id=key, source_patch_id=key, label_source='manual_fixture',
                 image_sha256=str(i) * 64, mask_sha256=str(i + 3) * 64)
            for i, key in enumerate(membership)]
    return patches, membership, rows


def test_unet_native_odd_shapes_finite_backward_and_locked_size():
    m, _ = api()
    net = m.CompactUNet()
    x = torch.randn(2, 2, 17, 19, requires_grad=True)
    logits = net(x)
    assert logits.shape == (2, 1, 17, 19)
    assert torch.isfinite(logits).all()
    logits.square().mean().backward()
    assert torch.isfinite(x.grad).all()
    assert sum(p.numel() for p in net.parameters()) == 487857
    norms = [layer for layer in net.modules() if isinstance(layer, torch.nn.GroupNorm)]
    assert len(norms) == 14 and all(layer.num_groups == 8 for layer in norms)
    assert not any(isinstance(layer, (torch.nn.BatchNorm2d, torch.nn.ConvTranspose2d,
                                      torch.nn.Dropout)) for layer in net.modules())
    with pytest.raises(ValueError, match='shape|size'):
        net(torch.zeros(1, 2, 7, 8))


def test_loss_hand_calculation_ignores_invalid_nan_labels_and_gradients():
    m, _ = api()
    logits = torch.zeros(1, 1, 2, 2, requires_grad=True)
    labels = torch.tensor([[[[1., 0.], [float('nan'), 123.]]]])
    valid = torch.tensor([[[[True, True], [False, False]]]])
    loss = m.masked_bce_dice_loss(logits, labels, valid)
    expected = .5 * np.log(2) + .5 * (1 - (1 + 1e-6) / (2 + 1e-6))
    assert loss.item() == pytest.approx(expected)
    loss.backward()
    assert logits.grad[0, 0, 1].tolist() == [0., 0.]
    assert m.masked_bce_dice_loss(logits, labels, torch.zeros_like(valid)) is None
    with pytest.raises(ValueError, match='binary|finite'):
        m.masked_bce_dice_loss(logits, labels, torch.ones_like(valid))
    with pytest.raises(ValueError, match='finite'):
        m.masked_bce_dice_loss(torch.full_like(logits, float('nan')), labels, valid)


def test_normalization_uses_only_valid_raw_training_pixels():
    _, t = api()
    p = patch([[[-30., -10., 20.]], [[-20., 0., 30.]]],
              input_valid=np.array([[True, True, False]]))
    stats = t.fit_raw_normalization({'a': p, 'b': UnreadTestPatch(), 'c': UnreadTestPatch()},
                                    {'a': 'train', 'b': 'validation', 'c': 'test'})
    assert stats.mean == pytest.approx((-20., -10.))
    assert stats.std == pytest.approx((10., 10.))
    assert stats.pixel_count == 2 and stats.train_ids == ('a',)
    flat = t.fit_raw_normalization({'a': patch(np.zeros((2, 1, 2)))}, {'a': 'train'})
    assert flat.std == (1e-6, 1e-6)


def test_fill_precedes_standardization_and_never_uses_label_validity():
    _, t = api()
    stats = t.Normalization(mean=(-20., -10.), std=(2., 4.), pixel_count=1, train_ids=('a',))
    p = patch([[[-18., np.nan], [np.nan, np.nan]],
               [[-6., np.nan], [np.nan, np.nan]]], label_valid=np.zeros((2, 2), bool))
    before = p.power.copy()
    filled = t.prepare_input(p, stats)
    assert np.isfinite(filled).all() and filled.shape == (2, 2, 2)
    np.testing.assert_allclose(filled, np.ones((2, 2, 2)), rtol=1e-6)
    np.testing.assert_equal(p.power, before)
    p.label_valid[:] = True
    np.testing.assert_array_equal(t.prepare_input(p, stats), filled)
    with pytest.raises(ValueError, match='all-invalid'):
        t.prepare_input(Patch(p.power, p.labels, np.zeros((2, 2), bool), p.label_valid), stats)
    p.power[:, 0, 0] = np.inf
    with pytest.raises(ValueError, match='finite|positive'):
        t.prepare_input(p, stats)


def test_crop_policy_repeats_by_epoch_and_water_centres_clamp_to_source():
    _, t = api()
    labels = np.zeros((300, 300), np.int8)
    labels[299, 299] = 1
    p = patch(np.zeros((2, 300, 300)), labels)
    crops = t.epoch_crop_plan({'a': p}, {'a': 'train'}, epoch=0, seed=42)
    assert len(crops) == 4 and [draw.kind for draw in crops] == ['uniform'] * 2 + ['water'] * 2
    assert [(d.top, d.left) for d in crops[2:]] == [(44, 44), (44, 44)]
    assert crops == t.epoch_crop_plan({'a': p}, {'a': 'train'}, epoch=0, seed=42)
    assert crops != t.epoch_crop_plan({'a': p}, {'a': 'train'}, epoch=1, seed=42)
    assert all(0 <= d.top <= 44 and 0 <= d.left <= 44 for d in crops)
    p.label_valid[299, 299] = False
    assert all(d.kind == 'uniform' for d in t.epoch_crop_plan({'a': p}, {'a': 'train'}, epoch=0))


def test_crop_applies_identical_spatial_augmentation_to_all_arrays():
    _, t = api()
    values = np.arange(256 * 256, dtype=np.float32).reshape(256, 256)
    draw = t.CropDraw('a', 0, 0, 'uniform', True, False, 1)
    x, y, valid = t.crop_arrays(np.stack([values, values]), values,
                                values % 2 == 0, draw)
    expected = np.rot90(np.fliplr(values), 1)
    np.testing.assert_array_equal(x[0], expected)
    np.testing.assert_array_equal(y, expected)
    np.testing.assert_array_equal(valid, expected % 2 == 0)
    assert x.flags.c_contiguous and y.flags.c_contiguous and valid.flags.c_contiguous


def test_validation_monitor_uses_pooled_iou_and_keeps_earlier_ties():
    _, t = api()
    monitor = t.ValidationMonitor(patience=5)
    assert monitor.observe(.6, 1)
    for epoch in range(2, 7):
        assert not monitor.observe(.6, epoch)
    assert monitor.best_epoch == 1 and monitor.should_stop
    assert monitor.observe(.7, 7)
    assert monitor.best_epoch == 7 and not monitor.should_stop
    with pytest.raises(ValueError, match='defined|finite'):
        monitor.observe(None, 8)


def test_native_inference_strict_half_threshold_and_original_masks():
    _, t = api()
    net = torch.nn.Conv2d(2, 1, 1)
    with torch.no_grad():
        net.weight.zero_(); net.bias.zero_()
    p = patch(np.zeros((2, 17, 19)), np.ones((17, 19), np.int8))
    p.input_valid[0, 0] = False
    p.power[:, 0, 0] = np.nan
    p.label_valid[0, 1] = False
    stats = t.Normalization((0., 0.), (1., 1.), 1, ('a',))
    predicted = t.predict_patch(net, p, stats, device='cpu')
    assert predicted['prediction'].shape == (17, 19)
    assert predicted['prediction'][0, 0] == -1
    assert predicted['prediction'][0, 1] == 0
    assert np.isnan(predicted['probability'][0, 0])
    assert predicted['probability'][0, 1] == .5
    result = t.evaluate_model(net, {'a': p}, stats, device='cpu')
    assert result['summary']['counts'] == dict(tp=0, fp=0, fn=321, tn=0)
    assert result['summary']['macro_patch_ids'] == ['a']


def test_paired_training_matches_initialization_updates_and_checkpoint_roundtrip(tmp_path):
    _, t = api()
    patches, membership, rows = development_fixture()
    result = t.paired_train(patches, patches, rows, membership,
                            config=t.TrainingConfig(max_epochs=1, max_seconds=120, profile='fixture'),
                            output_dir=tmp_path / 'pair', device='cpu', commit_sha='fixture-commit')
    report = result.report
    assert report['pair_complete'] and report['runtime_type'] == 'fixture'
    assert report['conditions']['raw']['updates'] == report['conditions']['filtered']['updates'] == 1
    assert report['conditions']['raw']['history'][0]['accepted_crops'] == 4
    assert report['conditions']['raw']['initial_sha256'] == report['conditions']['filtered']['initial_sha256']
    assert report['conditions']['raw']['initial_sha256'] != report['conditions']['raw']['final_sha256']
    for a, b in zip(result.models['raw'].parameters(), result.models['filtered'].parameters()):
        assert torch.equal(a, b)
    restored, stats, metadata = t.load_checkpoint(tmp_path / 'pair' / 'raw_best.pt', device='cpu')
    assert stats == result.normalization and metadata['condition'] == 'raw'
    assert metadata['best_epoch'] == 1 and metadata['commit_sha'] == 'fixture-commit'
    expected = t.predict_patch(result.models['raw'], patches['val'], stats, device='cpu')
    observed = t.predict_patch(restored, patches['val'], stats, device='cpu')
    np.testing.assert_array_equal(observed['probability'], expected['probability'])
    saved = json.loads((tmp_path / 'pair' / 'training.json').read_text())
    assert saved['config_sha256'] == report['config_sha256']
    assert saved['subset_sha256'] and saved['split_sha256'] and saved['environment']['torch']
    assert len(saved['crop_plan_sha256']) == 1


def test_cross_partition_source_leakage_rejected_before_training():
    _, t = api()
    patches, membership, rows = development_fixture()
    rows[2]['source_patch_id'] = rows[0]['source_patch_id']
    with pytest.raises(ValueError, match='cross-split'):
        t.paired_train(patches, patches, rows, membership, device='cpu')


def test_condition_mask_or_label_mismatch_rejected():
    _, t = api()
    patches, membership, rows = development_fixture()
    filtered = dict(patches)
    p = patches['train']
    filtered['train'] = Patch(p.power.copy(), p.labels.copy(), p.input_valid.copy(), p.label_valid.copy())
    filtered['train'].label_valid[0, 0] = False
    with pytest.raises(ValueError, match='mask|labels'):
        t.paired_train(patches, filtered, rows, membership, device='cpu')


def test_invalid_crop_exclusions_are_logged_identically_without_false_success():
    _, t = api()
    patches, membership, rows = development_fixture()
    patches['train'].label_valid[:] = False
    result = t.paired_train(patches, patches, rows, membership,
                            config=t.TrainingConfig(max_epochs=1, profile='fixture'), device='cpu')
    assert not result.report['pair_complete']
    for condition in result.report['conditions'].values():
        assert condition['updates'] == 0 and condition['status'] == 'no_valid_training_crops'
        assert condition['history'][0]['skipped_crops'] == 4
        assert condition['best_epoch'] is None


def test_shared_cap_stops_both_without_selecting_unvalidated_weights():
    _, t = api()
    patches, membership, rows = development_fixture()
    result = t.paired_train(patches, patches, rows, membership,
                            config=t.TrainingConfig(max_seconds=1e-12, profile='fixture'), device='cpu')
    assert result.report['cap_exhausted'] and not result.report['pair_complete']
    assert all(c['updates'] == 0 and c['best_epoch'] is None for c in result.report['conditions'].values())


@pytest.mark.parametrize('settings', [dict(batch_size=4), dict(learning_rate=.01),
                                      dict(crop_size=128), dict(seed=1), dict(max_epochs=21),
                                      dict(max_seconds=3601), dict(profile='full', max_epochs=9),
                                      dict(profile='full', max_seconds=361)])
def test_configuration_rejects_unlocked_search_and_excess_budget(settings):
    _, t = api()
    with pytest.raises(ValueError):
        t.TrainingConfig(**settings)


def test_file_training_gate_rejects_unfrozen_configuration_before_data_access(tmp_path):
    _, t = api()
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'seed': 42, 'real_data': {'split_frozen': False}}))
    with pytest.raises(ValueError, match='frozen'):
        t.load_frozen_training_inputs(tmp_path / 'missing_manifest.csv',
                                      tmp_path / 'missing_splits.csv', config)


def test_file_training_checks_roi_membership_hashes_and_does_not_open_test(tmp_path):
    import csv
    from sar_water.data import audit_pair, sha256_file
    from sar_water.filters import estimate_training_looks
    rasterio = pytest.importorskip('rasterio')
    from rasterio.transform import from_origin
    _, t = api()
    patches, membership, _ = development_fixture()
    rows = []
    for key in ('train', 'val'):
        p = patches[key]
        image, mask = tmp_path / f'{key}.tif', tmp_path / f'{key}_mask.tif'
        common = dict(driver='GTiff', height=p.labels.shape[0], width=p.labels.shape[1],
                      transform=from_origin(0, p.labels.shape[0], 1, 1))
        with rasterio.open(image, 'w', count=2, dtype='float32', **common) as target:
            target.write(p.power)
        with rasterio.open(mask, 'w', count=1, dtype='int8', **common) as target:
            target.write(p.labels, 1)
        pair = dict(patch_id=key, image_path=str(image), mask_path=str(mask), source_patch_id=key,
                    units='linear_power', band_order='VV,VH', source='fixture', label_source='manual')
        row, _ = audit_pair(pair)
        rows.append(dict(row, split=membership[key]))
    rows.append(dict(rows[1], patch_id='test', source_patch_id='test', split='test',
                     image_path=str(tmp_path / 'unread_test.tif'), image_sha256='a' * 64,
                     image_content_sha256='b' * 64, mask_sha256='c' * 64))

    def write_csv(path, values):
        fields = sorted({key for row in values for key in row})
        with path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fields)
            writer.writeheader()
            writer.writerows({key: json.dumps(value) if isinstance(value, (list, dict)) else value
                              for key, value in row.items()} for row in values)

    manifest, splits, roi = [tmp_path / name for name in ('manifest.csv', 'splits.csv', 'roi.csv')]
    write_csv(manifest, rows)
    write_csv(splits, [dict(patch_id=key, split=value) for key, value in membership.items()])
    rois = [dict(patch_id='train', y0=0, y1=32, x0=0, x1=32)]
    write_csv(roi, rois)
    looks = estimate_training_looks({'train': {'power': patches['train'].power,
                                              'input_valid': patches['train'].input_valid}}, rois, membership)
    artifact = tmp_path / 'looks.json'
    artifact.write_text(json.dumps(looks))
    config = dict(seed=42, primary_cleanup=False, real_data=dict(
        split_frozen=True, calibration_frozen=True, manifest_sha256=sha256_file(manifest),
        splits_sha256=sha256_file(splits), selected_channel='VV',
        selected_threshold_strategy='shared_fixed_db', selected_fixed_threshold_db=-20,
        selected_filter='median', selected_filter_parameters=dict(raw={}, median={'window': 3},
            lee={'window': 5}, log_bilateral={'window': 5, 'spatial_sigma': 2, 'color_sigma_db': 1.5}),
        effective_looks_by_band=looks['looks'], fallback_thresholds_db={'VV': -20, 'VH': -24},
        training_roi_path='roi.csv', training_roi_sha256=sha256_file(roi),
        looks_artifact_path='looks.json', looks_artifact_sha256=sha256_file(artifact)))
    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(config))
    loaded = t.load_frozen_training_inputs(manifest, splits, config_path)
    assert set(loaded['raw_patches']) == set(loaded['filtered_patches']) == {'train', 'val'}
    assert loaded['membership'] == membership
    assert loaded['filtered_identity']['method'] == 'median'
    assert loaded['filtered_identity']['config_file_sha256'] == sha256_file(config_path)
    write_csv(roi, [dict(rois[0], patch_id='val')])
    config['real_data']['training_roi_sha256'] = sha256_file(roi)
    config_path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match='training-only'):
        t.load_frozen_training_inputs(manifest, splits, config_path)
    roi.write_text('changed')
    with pytest.raises(ValueError, match='ROI.*hash'):
        t.load_frozen_training_inputs(manifest, splits, config_path)
