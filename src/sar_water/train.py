"""Bounded, paired raw/filtered training on already audited in-memory patches.

No download, split creation, filter selection, or test-label inspection occurs
here. Supply the frozen manifest/membership and the validation-selected filter.
The fixture profile is implementation evidence only. A remote run and a shorter
full-Colab run are distinct experiments, identified in every saved report.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import sys
import subprocess
from time import perf_counter

import numpy as np
import scipy
import torch

from .data import (Patch, audit_pair, nearest_valid_fill, power_to_db, sha256_file,
                   validate_splits, verify_decoded_image_identity)
from .metrics import confusion_counts, summarize_water
from .model import CompactUNet, masked_bce_dice_loss


def _json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Normalization:
    mean: tuple[float, float]
    std: tuple[float, float]
    pixel_count: int
    train_ids: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, 'mean', tuple(float(x) for x in self.mean))
        object.__setattr__(self, 'std', tuple(float(x) for x in self.std))
        object.__setattr__(self, 'train_ids', tuple(self.train_ids))
        if (len(self.mean) != 2 or len(self.std) != 2
                or not all(math.isfinite(x) for x in self.mean + self.std)
                or min(self.std) < 1e-6 or self.pixel_count < 1 or not self.train_ids
                or len(set(self.train_ids)) != len(self.train_ids)):
            raise ValueError('normalization requires finite two-band statistics and training pixels')


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 42
    max_epochs: int = 20
    patience: int = 5
    batch_size: int = 8
    learning_rate: float = .001
    crop_size: int = 256
    max_seconds: float = 3600.
    profile: str = 'remote'

    def __post_init__(self):
        if (self.seed not in (42, 43, 44) or self.batch_size != 8 or self.learning_rate != .001
                or self.crop_size != 256 or self.patience != 5
                or type(self.max_epochs) is not int or not 1 <= self.max_epochs <= 20
                or not math.isfinite(self.max_seconds) or not 0 < self.max_seconds <= 3600
                or self.profile not in ('remote', 'full', 'fixture')):
            raise ValueError('settings exceed the locked paired experiment')
        if self.profile == 'full' and (self.max_epochs > 8 or self.max_seconds > 360):
            raise ValueError('full Colab training allows at most eight epochs and six minutes per pair')


@dataclass(frozen=True)
class CropDraw:
    patch_id: str
    top: int
    left: int
    kind: str
    flip_horizontal: bool
    flip_vertical: bool
    rotations: int


@dataclass
class ValidationMonitor:
    patience: int = 5
    best_iou: float | None = None
    best_epoch: int | None = None
    stale_epochs: int = 0

    def observe(self, iou, epoch):
        if iou is None or not math.isfinite(iou) or not 0 <= iou <= 1:
            raise ValueError('checkpoint selection requires defined finite pooled validation IoU')
        improved = self.best_iou is None or iou > self.best_iou
        if improved:
            self.best_iou, self.best_epoch, self.stale_epochs = float(iou), epoch, 0
        else:
            self.stale_epochs += 1
        return improved

    @property
    def should_stop(self):
        return self.stale_epochs >= self.patience


@dataclass
class PairedTrainingResult:
    models: dict
    normalization: Normalization
    report: dict


def _sar_arrays(patch):
    power = np.asarray(patch.power)
    valid = np.asarray(patch.input_valid, dtype=bool)
    if power.ndim != 3 or power.shape[0] != 2 or power.shape[1:] != valid.shape:
        raise ValueError('expected two SAR bands and a matching input mask shape')
    if not valid.any():
        raise ValueError('all-invalid SAR patch')
    if np.any(~np.isfinite(power[:, valid]) | (power[:, valid] <= 0)):
        raise ValueError('valid SAR power must be finite and positive')
    return power, valid


def _targets(patch):
    labels, label_valid = np.asarray(patch.labels), np.asarray(patch.label_valid, dtype=bool)
    if labels.shape != patch.input_valid.shape or label_valid.shape != labels.shape:
        raise ValueError('label or label validity mask shape mismatch')
    if not np.isin(labels, [-1, 0, 1]).all():
        raise ValueError('unsupported label codes; expected -1/0/1')
    return labels, np.asarray(patch.input_valid, bool) & label_valid & (labels != -1)


def fit_raw_normalization(raw_patches, membership):
    """Population mean/std in dB from valid raw training SAR only.

    Merge per-source centered moments in float64, without reading held-out
    patch values or using label validity as a normalization mask.
    """
    if not set(membership.values()) <= {'train', 'validation', 'test'}:
        raise ValueError('unknown split membership')
    train_ids = tuple(sorted(key for key, split in membership.items() if split == 'train'))
    if not train_ids or not set(train_ids) <= set(raw_patches):
        raise ValueError('raw training patches are required for normalization')
    count, mean, m2 = 0, np.zeros(2, np.float64), np.zeros(2, np.float64)
    for key in train_ids:
        power, valid = _sar_arrays(raw_patches[key])
        db = power_to_db(power[:, valid]).astype(np.float64)
        n, local_mean = db.shape[1], db.mean(axis=1)
        delta, total = local_mean - mean, count + db.shape[1]
        m2 += ((db - local_mean[:, None]) ** 2).sum(axis=1) + delta ** 2 * count * n / total
        mean += delta * n / total
        count = total
    return Normalization(tuple(mean), tuple(np.maximum(np.sqrt(m2 / count), 1e-6)), count, train_ids)


def prepare_input(patch, normalization):
    """SAR-only nearest fill in the source, then dB and shared standardization.

    The original patch and its masks are not mutated. Label validity is never
    read here, including at inference time.
    """
    power, valid = _sar_arrays(patch)
    db = power_to_db(nearest_valid_fill(power, valid))
    standardized = ((db.astype(np.float64) - np.array(normalization.mean)[:, None, None])
                    / np.array(normalization.std)[:, None, None]).astype(np.float32)
    if not np.isfinite(standardized).all():
        raise ValueError('standardization produced nonfinite network input')
    return np.ascontiguousarray(standardized)


def epoch_crop_plan(raw_patches, membership, *, epoch, seed=42):
    """Four deterministic 256-square draws per training source, no test access.

    First two are uniform; last two use valid water centers if available. Each
    draw includes independently sampled flips and a 0/90/180/270-degree rotation.
    All draws are retained so invalid exclusions can be logged by both models.
    """
    if type(epoch) is not int or epoch < 0 or seed not in (42, 43, 44):
        raise ValueError('nonnegative epoch and locked seed required')
    rng, draws = np.random.default_rng(np.random.SeedSequence([seed, epoch])), []
    for key in sorted(k for k, split in membership.items() if split == 'train'):
        source = raw_patches[key]
        _, input_valid = _sar_arrays(source)
        labels, valid = _targets(source)
        height, width = input_valid.shape
        if min(height, width) < 256:
            raise ValueError('training source size must be at least 256 x 256')
        water = np.argwhere(valid & (labels == 1))
        for i in range(4):
            kind = 'water' if i >= 2 and len(water) else 'uniform'
            if kind == 'water':
                row, col = water[rng.integers(len(water))]
                top, left = int(np.clip(row - 128, 0, height - 256)), int(np.clip(col - 128, 0, width - 256))
            else:
                top, left = int(rng.integers(height - 255)), int(rng.integers(width - 255))
            draws.append(CropDraw(key, top, left, kind, bool(rng.integers(2)),
                                  bool(rng.integers(2)), int(rng.integers(4))))
    return draws


def crop_arrays(inputs, labels, valid, draw):
    """Extract and spatially augment one already-filled source identically."""
    height, width = labels.shape
    if (inputs.shape != (2, height, width) or valid.shape != labels.shape
            or draw.top < 0 or draw.left < 0 or draw.top + 256 > height or draw.left + 256 > width):
        raise ValueError('crop bounds or array shape mismatch')
    values = [inputs[:, draw.top:draw.top + 256, draw.left:draw.left + 256],
              labels[draw.top:draw.top + 256, draw.left:draw.left + 256],
              valid[draw.top:draw.top + 256, draw.left:draw.left + 256]]
    for index, value in enumerate(values):
        if draw.flip_horizontal:
            value = np.flip(value, axis=-1)
        if draw.flip_vertical:
            value = np.flip(value, axis=-2)
        values[index] = np.ascontiguousarray(np.rot90(value, draw.rotations, axes=(-2, -1)))
    return tuple(values)


def _device(device):
    device = torch.device(device)
    if device.type not in ('cpu', 'cuda'):
        raise ValueError('device must be CPU or CUDA')
    if device.type == 'cuda' and not torch.cuda.is_available():
        raise ValueError('CUDA requested but unavailable')
    return device


def set_reproducible(seed):
    """Seed this process; determinism still depends on hardware/library versions."""
    if seed not in (42, 43, 44):
        raise ValueError('seed must be 42, 43 or 44')
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


def state_sha256(model):
    """Stable weight/buffer identity, independent of torch.save container bytes."""
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(name.encode())
        digest.update(str(array.shape).encode())
        digest.update(str(array.dtype).encode())
        digest.update(array.tobytes())
    return digest.hexdigest()


def predict_patch(model, patch, normalization, *, device='cpu'):
    """Native-resolution probabilities; strict >0.5 means water, ties land."""
    device = _device(device)
    inputs = torch.from_numpy(prepare_input(patch, normalization))[None].to(device)
    was_training = model.training
    model.eval()
    try:
        with torch.inference_mode():
            logits = model(inputs)
            if logits.shape != (1, 1, *patch.input_valid.shape) or not torch.isfinite(logits).all():
                raise ValueError('model produced nonfinite or mismatched native logits')
            probability = torch.sigmoid(logits[0, 0]).cpu().numpy().copy()
    finally:
        model.train(was_training)
    prediction = (probability > .5).astype(np.int8)
    prediction[~patch.input_valid] = -1
    probability[~patch.input_valid] = np.nan
    return dict(probability=probability, prediction=prediction)


def evaluate_model(model, patches, normalization, *, device='cpu', deadline=None):
    """Pooled validation/frozen scoring with a fixed ground-truth macro set.

    Callers pass only the intended partition. Deadline interrupts between native
    patches; a partial validation is never used for checkpoint selection.
    """
    counts = {}
    for key in sorted(patches):
        if deadline is not None and perf_counter() >= deadline:
            raise TimeoutError('paired comparison wall-time cap reached during validation')
        patch = patches[key]
        _targets(patch)
        predicted = predict_patch(model, patch, normalization, device=device)
        counts[key] = confusion_counts(predicted['prediction'], patch.labels,
                                       input_valid=patch.input_valid, label_valid=patch.label_valid)
    if not counts:
        raise ValueError('evaluation requires patches')
    return dict(per_patch_counts=counts, summary=summarize_water(counts))


def save_checkpoint(path, model, normalization, metadata):
    """Save inference weights with reconstruction/provenance, not resume state."""
    metadata = json.loads(json.dumps(metadata, allow_nan=False))
    payload = dict(architecture='compact_vv_vh_unet_v1',
                   state_dict={key: value.detach().cpu().clone() for key, value in model.state_dict().items()},
                   normalization=asdict(normalization), metadata=metadata,
                   state_sha256=state_sha256(model), resume_supported=False)
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def load_checkpoint(path, *, device='cpu'):
    """Load a trusted project checkpoint using PyTorch's weights-only loader."""
    payload = torch.load(path, map_location='cpu', weights_only=True)
    if payload.get('architecture') != 'compact_vv_vh_unet_v1':
        raise ValueError('checkpoint architecture is outside the locked experiment')
    normalization = Normalization(**payload['normalization'])
    model = CompactUNet()
    model.load_state_dict(payload['state_dict'], strict=True)
    if not all(torch.isfinite(value).all() for value in model.state_dict().values()):
        raise ValueError('checkpoint has nonfinite weights')
    if state_sha256(model) != payload['state_sha256']:
        raise ValueError('checkpoint weight hash mismatch')
    model.to(_device(device)).eval()
    return model, normalization, payload['metadata']


def _validate_pair(raw, filtered, rows, membership):
    validate_splits(rows, membership)
    required = {key for key, split in membership.items() if split != 'test'}
    if (not required <= set(raw) or not required <= set(filtered)
            or not set(raw) <= set(membership) or not set(filtered) <= set(membership)):
        raise ValueError('raw and filtered dictionaries must cover train/validation membership')
    # Test objects may be absent or unread: the manifest alone audits their split.
    for key in sorted(required):
        a, b = raw[key], filtered[key]
        _sar_arrays(a); _sar_arrays(b)
        _targets(a); _targets(b)
        if (a.power.shape != b.power.shape
                or not np.array_equal(a.labels, b.labels)
                or not np.array_equal(a.input_valid, b.input_valid)
                or not np.array_equal(a.label_valid, b.label_valid)):
            raise ValueError('raw/filtered shape, labels and validity masks must match')
        minimum = 256 if membership[key] == 'train' else 8
        if min(a.input_valid.shape) < minimum:
            raise ValueError(f'{membership[key]} source size must be at least {minimum}')


def _environment(device):
    return dict(python=sys.version.split()[0], torch=str(torch.__version__), numpy=np.__version__,
                scipy=scipy.__version__, platform=platform.platform(), device=str(device),
                device_name=torch.cuda.get_device_name(device) if device.type == 'cuda' else platform.processor(),
                cuda=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
                cpu_threads=torch.get_num_threads(), deterministic_algorithms=torch.are_deterministic_algorithms_enabled())


def _train_epoch(model, optimizer, prepared, raw, draws, config, device, deadline):
    accepted, skipped = [], 0
    for draw in draws:
        labels, valid = _targets(raw[draw.patch_id])
        crop = crop_arrays(prepared[draw.patch_id], labels, valid, draw)
        if crop[2].any():
            accepted.append(crop)
        else:
            skipped += 1
    loss_sum, updates, processed = 0., 0, 0
    model.train()
    for start in range(0, len(accepted), config.batch_size):
        if perf_counter() >= deadline:
            break
        batch = accepted[start:start + config.batch_size]
        x = torch.from_numpy(np.stack([crop[0] for crop in batch])).to(device)
        y = torch.from_numpy(np.stack([crop[1] for crop in batch]).astype(np.float32))[:, None].to(device)
        valid = torch.from_numpy(np.stack([crop[2] for crop in batch]))[:, None].to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        if not torch.isfinite(logits).all():
            raise ValueError('nonfinite training logits')
        loss = masked_bce_dice_loss(logits, y, valid)
        if loss is None:
            continue
        if not torch.isfinite(loss):
            raise ValueError('nonfinite training loss')
        loss.backward()
        if not all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()):
            raise ValueError('nonfinite training gradients')
        optimizer.step()
        loss_sum += loss.item()
        updates += 1
        processed += len(batch)
    return dict(train_loss=loss_sum / updates if updates else None, updates=updates,
                drawn_crops=len(draws), accepted_crops=len(accepted), skipped_crops=skipped,
                processed_crops=processed, epoch_complete=processed == len(accepted))


def paired_train(raw_patches, filtered_patches, rows, membership, *, config=None,
                 output_dir=None, device='cpu', commit_sha=None, filtered_identity=None):
    """Train separate models with shared initialization/crops and one wall cap.

    Inputs are audited Patch dictionaries and frozen source-level membership.
    The function never reads test Patch objects. Pass a recorded commit SHA and
    frozen filter identity for real runs. It only runs one paired seed; optional
    extra seeds must receive the *remaining* time from the same external cap.

    Wall limits are checked between batches/native patches. A current operation
    or final serialization can cross the deadline; actual elapsed time is logged
    and an over-budget run never receives pair_complete=True. No resume claim is
    made: checkpoints contain inference weights and reproducibility metadata.
    """
    started = perf_counter()
    config = config or TrainingConfig()
    _validate_pair(raw_patches, filtered_patches, rows, membership)
    device = _device(device)
    set_reproducible(config.seed)
    destination = None
    if output_dir is not None:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=False)
    deadline = started + config.max_seconds
    normalization = fit_raw_normalization(raw_patches, membership)
    development = sorted(key for key, split in membership.items() if split != 'test')
    conditions = {'raw': raw_patches, 'filtered': filtered_patches}
    prepared = {name: {key: prepare_input(patches[key], normalization) for key in development}
                for name, patches in conditions.items()}
    models = {name: CompactUNet().to(device) for name in conditions}
    models['filtered'].load_state_dict(models['raw'].state_dict())
    optimizers = {name: torch.optim.Adam(model.parameters(), lr=config.learning_rate)
                  for name, model in models.items()}
    monitors = {name: ValidationMonitor(config.patience) for name in conditions}
    states, best_weights = {}, {}
    for name, model in models.items():
        states[name] = dict(status='active', updates=0, history=[], best_epoch=None, best_iou=None,
                            initial_sha256=state_sha256(model), checkpoint=None)
    if device.type == 'cuda':
        torch.cuda.reset_peak_memory_stats(device)
    identity = dict(config=asdict(config), split_sha256=_json_hash(membership),
                    subset_sha256=_json_hash(sorted(rows, key=lambda row: row['patch_id'])),
                    commit_sha=commit_sha, filtered_identity=filtered_identity,
                    normalization=asdict(normalization))
    report = dict(schema_version=1, runtime_type=config.profile, architecture='compact_vv_vh_unet_v1',
                  model_role='segmentation', enl='not_applicable', psnr='not_applicable',
                  **identity, config_sha256=_json_hash(asdict(config)),
                  environment=_environment(device), conditions=states, crop_plan_sha256=[],
                  pair_complete=False, cap_exhausted=False, elapsed_seconds=None,
                  additional_seeds_share_external_cap=True, resume_supported=False)
    for epoch in range(1, config.max_epochs + 1):
        if perf_counter() >= deadline:
            report['cap_exhausted'] = True
            break
        draws = epoch_crop_plan(raw_patches, membership, epoch=epoch - 1, seed=config.seed)
        report['crop_plan_sha256'].append(_json_hash([asdict(draw) for draw in draws]))
        for name, model in models.items():
            state, monitor = states[name], monitors[name]
            if state['status'] != 'active':
                continue
            epoch_started = perf_counter()
            history = _train_epoch(model, optimizers[name], prepared[name], raw_patches, draws,
                                   config, device, deadline)
            state['updates'] += history['updates']
            history.update(epoch=epoch, validation=None, seconds=None)
            state['history'].append(history)
            if not history['accepted_crops']:
                state['status'] = 'no_valid_training_crops'
            elif not history['epoch_complete'] or perf_counter() >= deadline:
                state['status'] = 'wall_time_cap'
                report['cap_exhausted'] = True
            else:
                validation = {key: conditions[name][key] for key in development if membership[key] == 'validation'}
                try:
                    evaluated = evaluate_model(model, validation, normalization, device=device, deadline=deadline)
                except TimeoutError:
                    state['status'], report['cap_exhausted'] = 'wall_time_cap', True
                else:
                    history['validation'] = evaluated
                    iou = evaluated['summary']['pooled']['iou']
                    if iou is None:
                        state['status'] = 'undefined_validation_iou'
                    elif monitor.observe(iou, epoch):
                        state['best_epoch'], state['best_iou'] = epoch, iou
                        best_weights[name] = {key: value.detach().cpu().clone()
                                              for key, value in model.state_dict().items()}
                        if destination is not None:
                            path = destination / f'{name}_best.pt'
                            save_checkpoint(path, model, normalization,
                                            dict(**identity, condition=name, best_epoch=epoch,
                                                 best_iou=iou, updates=state['updates'],
                                                 config_sha256=report['config_sha256']))
                            state['checkpoint'] = str(path.resolve())
                    if monitor.should_stop:
                        state['status'] = 'early_stopped'
            history['seconds'] = perf_counter() - epoch_started
        if report['cap_exhausted'] or all(s['status'] != 'active' for s in states.values()):
            break
    for name, model in models.items():
        state = states[name]
        if state['status'] == 'active':
            state['status'] = 'wall_time_cap' if report['cap_exhausted'] else 'max_epochs'
        state['last_sha256'] = state_sha256(model)
        if name in best_weights:
            model.load_state_dict(best_weights[name])
        model.eval()
        state['final_sha256'] = state_sha256(model)
        state['returned_best_checkpoint'] = name in best_weights
    if device.type == 'cuda':
        torch.cuda.synchronize(device)
    report['memory'] = dict(cuda_peak_allocated_bytes=torch.cuda.max_memory_allocated(device)
                            if device.type == 'cuda' else None, cpu_peak_rss_bytes=None,
                            cpu_peak_rss_status='not_measured')
    report['elapsed_seconds'] = perf_counter() - started
    report['cap_exhausted'] |= report['elapsed_seconds'] >= config.max_seconds
    report['pair_complete'] = (not report['cap_exhausted'] and all(
        s['best_epoch'] is not None and s['status'] in ('max_epochs', 'early_stopped') for s in states.values()))
    if destination is not None:
        (destination / 'training.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return PairedTrainingResult(models, normalization, report)


def _roi_records_match(actual, expected):
    """Exact ROI identity/count/status; tolerate only derived ENL roundoff."""
    if len(actual) != len(expected):
        return False
    for observed, frozen in zip(actual, expected):
        if ({key: value for key, value in observed.items() if key != 'value'} !=
                {key: value for key, value in frozen.items() if key != 'value'}):
            return False
        a, b = observed.get('value'), frozen.get('value')
        if a is None or b is None:
            if a is not None or b is not None:
                return False
        elif not np.isclose(a, b, rtol=1e-6, atol=0):
            return False
    return True


def load_frozen_training_inputs(manifest_path, splits_path, config_path):
    """Verify disk identities/ROI provenance, load development inputs only.

    Manifest image/mask paths resolve relative to its directory. ROI and looks
    artifact paths resolve relative to the configuration directory. Recomputing
    the recorded looks estimate verifies its binding to these training sources.
    Test source files and labels are never opened by this function.
    """
    from .evaluate import frozen_settings
    from .filters import estimate_training_looks, filter_power

    manifest_path, splits_path, config_path = map(Path, (manifest_path, splits_path, config_path))
    config = json.loads(config_path.read_text(encoding='utf-8'))
    settings = frozen_settings(config)
    real = config['real_data']
    for name, path in (('manifest', manifest_path), ('splits', splits_path)):
        if not real.get(name + '_sha256') or sha256_file(path) != real[name + '_sha256']:
            raise ValueError(f'{name} hash does not match frozen calibration')

    def artifact(name, label):
        if not real.get(name + '_path') or not real.get(name + '_sha256'):
            raise ValueError(f'{label} frozen path/hash required')
        path = Path(real[name + '_path'])
        path = path if path.is_absolute() else config_path.parent / path
        if sha256_file(path) != real[name + '_sha256']:
            raise ValueError(f'{label} hash does not match frozen calibration')
        return path

    roi_path = artifact('training_roi', 'training ROI')
    looks_path = artifact('looks_artifact', 'training looks artifact')
    with manifest_path.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    with splits_path.open(newline='', encoding='utf-8-sig') as stream:
        split_rows = list(csv.DictReader(stream))
    membership = {row['patch_id']: row['split'] for row in split_rows}
    if len(membership) != len(split_rows):
        raise ValueError('duplicate split identifier')
    validate_splits(rows, membership)
    if any(row.get('split') and row['split'] != membership[row['patch_id']] for row in rows):
        raise ValueError('manifest/split membership conflict')
    with roi_path.open(newline='', encoding='utf-8-sig') as stream:
        rois = list(csv.DictReader(stream))
    if not rois or any(membership.get(roi['patch_id']) != 'train' for roi in rois):
        raise ValueError('looks estimation requires training-only ROIs')
    for roi in rois:
        for name in ('y0', 'y1', 'x0', 'x1'):
            roi[name] = int(roi[name])
    raw = {}
    for row in rows:
        key = row['patch_id']
        if membership[key] == 'test':
            continue
        pair = dict(row)
        for name in ('image', 'mask'):
            path = Path(pair[name + '_path'])
            path = path if path.is_absolute() else manifest_path.parent / path
            if not pair.get(name + '_sha256') or sha256_file(path) != pair[name + '_sha256']:
                raise ValueError(f'development {name} hash changed after audit')
            pair[name + '_path'] = str(path)
        audit, patch = audit_pair(pair)
        verify_decoded_image_identity(pair, audit)
        raw[key] = patch
    estimated = estimate_training_looks({key: dict(power=patch.power, input_valid=patch.input_valid)
                                        for key, patch in raw.items() if membership[key] == 'train'}, rois, membership)
    frozen_looks = json.loads(looks_path.read_text(encoding='utf-8'))
    if (not np.allclose(estimated['looks'], settings['looks'], rtol=1e-6, atol=0)
            or not np.allclose(estimated['looks'], frozen_looks['looks'], rtol=1e-6, atol=0)
            or estimated['usable_roi_counts'] != frozen_looks['usable_roi_counts']
            or not _roi_records_match(estimated['rois'], frozen_looks['rois'])):
        raise ValueError('training sources/ROIs do not reproduce frozen looks artifact')
    method = settings['selected_filter']
    parameters = settings['parameters'][method]
    filtered = {key: Patch(filter_power(patch.power, patch.input_valid, method=method, **parameters,
                                       **({'looks': settings['looks']} if method == 'lee' else {})),
                           patch.labels.copy(), patch.input_valid.copy(), patch.label_valid.copy())
                for key, patch in raw.items()}
    identity = dict(method=method, parameters=parameters, looks=settings['looks'],
                    config_file_sha256=sha256_file(config_path),
                    manifest_file_sha256=real['manifest_sha256'], splits_file_sha256=real['splits_sha256'],
                    training_roi_sha256=real['training_roi_sha256'],
                    looks_artifact_sha256=real['looks_artifact_sha256'])
    return dict(raw_patches=raw, filtered_patches=filtered, rows=rows, membership=membership,
                filtered_identity=identity)


def main(argv=None):
    """CLI for one reviewed paired seed; no automatic test evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('manifest', 'splits', 'config', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--time-limit', type=float, default=3600.)
    parser.add_argument('--profile', choices=('remote', 'full', 'fixture'), default='remote')
    args = parser.parse_args(argv)
    # Include disk verification/filter preparation in the paired wall budget.
    started = perf_counter()
    config = TrainingConfig(max_epochs=args.epochs, max_seconds=args.time_limit, profile=args.profile)
    inputs = load_frozen_training_inputs(args.manifest, args.splits, args.config)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True,
                                        stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    preparation_seconds = perf_counter() - started
    remaining = args.time_limit - preparation_seconds
    if remaining <= 0:
        raise TimeoutError('input verification/preparation exhausted the complete paired wall-time cap')
    config = TrainingConfig(max_epochs=config.max_epochs, max_seconds=remaining, profile=config.profile)
    result = paired_train(**inputs, config=config, output_dir=args.output,
                          device=args.device, commit_sha=commit)
    result.report.update(input_preparation_seconds=preparation_seconds,
                         complete_pair_seconds=perf_counter() - started,
                         requested_wall_limit_seconds=args.time_limit, working_tree_dirty=dirty)
    if result.report['complete_pair_seconds'] >= args.time_limit:
        result.report['cap_exhausted'], result.report['pair_complete'] = True, False
    (args.output / 'training.json').write_text(json.dumps(result.report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result.report[key] for key in
                      ('pair_complete', 'cap_exhausted', 'complete_pair_seconds', 'runtime_type')}, indent=2))
    return 0 if result.report['pair_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
