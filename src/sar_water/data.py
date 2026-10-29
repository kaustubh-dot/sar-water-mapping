"""Explicit SAR adapters and a fail-closed, inventory-driven data audit.

Arrays use [VV,VH], linear power, float32. Validity remains separate from values.
This module never downloads data or selects methods using evaluation labels.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt


@dataclass
class Patch:
    power: np.ndarray
    labels: np.ndarray
    input_valid: np.ndarray
    label_valid: np.ndarray

    @property
    def score_valid(self):
        return self.input_valid & self.label_valid


def power_to_db(power):
    """Convert positive power, preserving NaN invalid locations."""
    power = np.asarray(power, dtype=np.float32)
    if np.any(np.isinf(power) | (np.isfinite(power) & (power <= 0))):
        raise ValueError("power must be positive")
    return (10 * np.log10(power)).astype(np.float32)


def adapt_arrays(image, labels, *, units, band_order, input_mask=None, label_mask=None):
    image = np.asarray(image, dtype=np.float32)
    labels = np.asarray(labels)
    if image.ndim != 3 or image.shape[0] != 2 or labels.shape != image.shape[1:]:
        raise ValueError("expected two bands and a matching 2D label shape")
    if band_order not in ("VV,VH", "VH,VV"):
        raise ValueError("band_order must explicitly be VV,VH or VH,VV")
    if units not in ("db", "linear_power"):
        raise ValueError("units must explicitly be db or linear_power")
    # Unknown codes are rejected even behind a metadata mask.
    if not np.isin(labels, [-1, 0, 1]).all():
        raise ValueError("unsupported label code; expected -1/0/1")
    valid = np.isfinite(image).all(axis=0)
    if input_mask is not None:
        input_mask = np.asarray(input_mask, dtype=bool)
        if input_mask.shape == image.shape:
            valid &= input_mask.all(axis=0)
        elif input_mask.shape == labels.shape:
            valid &= input_mask
        else:
            raise ValueError("input mask shape mismatch")
    if not valid.any():
        raise ValueError("all-invalid SAR patch")
    if units == "linear_power" and np.any(image[:, valid] <= 0):
        raise ValueError("valid linear power must be positive")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        power = np.power(10.0, image / 10.0) if units == "db" else image.copy()
    if np.any(~np.isfinite(power[:, valid]) | (power[:, valid] <= 0)):
        raise ValueError("conversion produced nonfinite/nonpositive valid power")
    if band_order == "VH,VV":
        power = power[::-1].copy()
    power[:, ~valid] = np.nan
    label_valid = labels != -1
    if label_mask is not None:
        label_mask = np.asarray(label_mask, dtype=bool)
        if label_mask.shape != labels.shape:
            raise ValueError("label mask shape mismatch")
        label_valid &= label_mask
    return Patch(power.astype(np.float32), labels.astype(np.int8), valid, label_valid)


def nearest_valid_fill(values, valid):
    """Euclidean nearest SAR fill; SciPy's deterministic index tie handling."""
    values, valid = np.asarray(values), np.asarray(valid, dtype=bool)
    if values.ndim != 3 or values.shape[1:] != valid.shape:
        raise ValueError("fill shape mismatch")
    if not valid.any():
        raise ValueError("all-invalid SAR patch")
    if not np.isfinite(values[:, valid]).all():
        raise ValueError("valid SAR values must be finite")
    indices = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return values[:, indices[0], indices[1]].copy()


def read_inventory(path):
    """Pair long-form image/mask rows by explicit identifier, never row order."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"patch_id", "kind", "path", "source", "units", "band_order", "label_source"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"inventory requires {sorted(required)}")
        grouped = {}
        for row in reader:
            if not row["patch_id"] or row["kind"] not in ("image", "mask") or not row["path"]:
                raise ValueError("inventory requires identifier, kind image/mask, and path")
            group = grouped.setdefault(row["patch_id"], {})
            if row["kind"] in group:
                raise ValueError("duplicate identifier/kind")
            group[row["kind"]] = row
    pairs = []
    for identifier, group in sorted(grouped.items()):
        if set(group) != {"image", "mask"}:
            raise ValueError(f"missing pair for {identifier}")
        image, mask = group["image"], group["mask"]
        if not image["source"] or not mask["source"] or not mask["label_source"]:
            raise ValueError("source and label provenance must be explicit (use unknown if unknown)")
        pair = dict(image)
        pair.pop("path"); pair.pop("kind")
        pair.update(image_path=str((path.parent / image["path"]).resolve()),
                    mask_path=str((path.parent / mask["path"]).resolve()),
                    label_source=mask["label_source"], mask_source=mask["source"])
        for key in ("event_id", "scene_id", "spatial_group", "source_patch_id", "split"):
            a, b = image.get(key, ""), mask.get(key, "")
            if a and b and a != b:
                raise ValueError(f"pair metadata conflict: {key}")
            pair[key] = a or b
        pairs.append(pair)
    if not pairs:
        raise ValueError("empty inventory")
    return pairs


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_decoded_image_identity(frozen, audited):
    """Prefer exact source-domain identity; require legacy power hash otherwise.

    This does not replace the caller's mandatory image/mask file SHA checks.
    Legacy manifests retain their original, platform-sensitive power contract.
    """
    key = ('image_source_content_sha256' if frozen.get('image_source_content_sha256')
           else 'image_content_sha256')
    if not frozen.get(key) or audited.get(key) != frozen[key]:
        raise ValueError('decoded SAR hash changed after audit')


def read_manifest(path):
    """Load frozen rows, resolving portable paths against the manifest folder.

    Older absolute paths remain readable on their original platform. New audit
    manifests use relative POSIX paths, so copying the dataset tree preserves
    their meaning on Windows and Linux.
    """
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for name in ("image_path", "mask_path"):
            if not row.get(name):
                raise ValueError(f"manifest requires {name}")
            source = Path(row[name])
            row[name] = str((source if source.is_absolute() else path.parent/source).resolve())
    return rows


def _alignment_error_pixels(image_transform, mask_transform, width, height):
    """Largest corner displacement in image pixels; no reprojection/resampling.

    A 1e-6-pixel admission bound permits GeoTIFF serialization roundoff while
    rejecting actual subpixel misalignment. Checking all corners catches scale,
    rotation and shear errors as well as origin shifts.
    """
    linear = np.array([[image_transform.a, image_transform.b],
                       [image_transform.d, image_transform.e]], dtype=np.float64)
    differences = []
    for x, y in ((0, 0), (width, 0), (0, height), (width, height)):
        # Subtract affine coefficients before evaluation to avoid cancellation
        # from large world-coordinate origins and deprecated Affine operators.
        differences.append([(mask_transform.a-image_transform.a)*x +
                            (mask_transform.b-image_transform.b)*y +
                            (mask_transform.c-image_transform.c),
                            (mask_transform.d-image_transform.d)*x +
                            (mask_transform.e-image_transform.e)*y +
                            (mask_transform.f-image_transform.f)])
    try:
        offsets = np.linalg.solve(linear, np.asarray(differences).T).T
    except np.linalg.LinAlgError as error:
        raise ValueError("image/mask georeferencing has singular transform") from error
    if not np.isfinite(offsets).all():
        raise ValueError("image/mask georeferencing has nonfinite transform")
    return float(np.max(np.linalg.norm(offsets, axis=1)))


def audit_pair(pair):
    """Validate arrays, masks and georeferencing within 1e-6 image pixels."""
    try:
        import rasterio
    except ImportError as error:
        raise RuntimeError("GeoTIFF audit requires pip install '.[geo]'") from error
    with rasterio.open(pair["image_path"]) as image, rasterio.open(pair["mask_path"]) as mask:
        if (image.width, image.height) != (mask.width, mask.height) or image.count != 2 or mask.count != 1:
            raise ValueError("image/mask shape or band-count mismatch")
        alignment_error = _alignment_error_pixels(image.transform, mask.transform, image.width, image.height)
        if image.crs != mask.crs or alignment_error > 1e-6:
            raise ValueError("image/mask georeferencing mismatch")
        source_samples = image.read().astype(np.float32)
        patch = adapt_arrays(source_samples, mask.read(1), units=pair["units"],
                             band_order=pair["band_order"], input_mask=image.read_masks() > 0,
                             label_mask=mask.read_masks(1) > 0)
        # Hash decoded source samples before db->power transcendental arithmetic.
        # The same file can differ by one power ULP across libm/platform builds.
        # Normalize band order, byte order and invalid payloads, keeping units
        # and validity explicit. File SHA independently binds every source byte.
        source_domain = 'source_float32_vv_vh_validity_v1'
        canonical_source = source_samples[::-1] if pair['band_order'] == 'VH,VV' else source_samples
        canonical_source = np.where(patch.input_valid[None], canonical_source, 0).astype('<f4')
        header = json.dumps(dict(domain=source_domain, units=pair['units'],
                                 shape=list(canonical_source.shape)), sort_keys=True,
                            separators=(',', ':')).encode('utf-8') + b'\0'
        source_hash = hashlib.sha256(header + canonical_source.tobytes() +
                                    patch.input_valid.astype('u1').tobytes()).hexdigest()
        # Canonical decoded-power hash catches duplicates stored with different TIFF compression.
        canonical = np.nan_to_num(patch.power, nan=0).astype("<f4").tobytes()
        content_hash = hashlib.sha256(str(patch.power.shape).encode() + canonical + patch.input_valid.tobytes()).hexdigest()
        row = dict(pair, image_sha256=sha256_file(pair["image_path"]),
                   mask_sha256=sha256_file(pair["mask_path"]), image_content_sha256=content_hash,
                   image_source_content_sha256=source_hash,
                   image_source_content_hash_domain=source_domain,
                   height=image.height, width=image.width, crs=str(image.crs or ""),
                   transform=list(image.transform), mask_transform=list(mask.transform),
                   max_alignment_error_pixels=alignment_error, bounds=list(image.bounds) if image.crs else "",
                   image_nodata=image.nodata, mask_nodata=mask.nodata,
                   input_valid_pixels=int(patch.input_valid.sum()),
                   label_valid_pixels=int(patch.label_valid.sum()), score_valid_pixels=int(patch.score_valid.sum()),
                   label_claim="independent manual labels" if pair["label_source"] == "manual" else "weak/unknown-label agreement only")
    return row, patch


def _bounds(row):
    value = row.get("bounds")
    return json.loads(value) if isinstance(value, str) and value else value


def validate_splits(rows, membership):
    identifiers = [r["patch_id"] for r in rows]
    if len(set(identifiers)) != len(rows):
        raise ValueError("duplicate patch identifier")
    if set(identifiers) != set(membership) or set(membership.values()) != {"train", "validation", "test"}:
        raise ValueError("membership must cover all identifiers and all three partitions")
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            cross = membership[a["patch_id"]] != membership[b["patch_id"]]
            if not cross:
                continue
            for key in ("image_sha256", "image_content_sha256", "image_source_content_sha256"):
                if a.get(key) and a.get(key) == b.get(key):
                    raise ValueError("cross-split duplicate image")
            for key in ("spatial_group", "source_patch_id"):
                if a.get(key) and a.get(key) == b.get(key):
                    raise ValueError(f"cross-split source/group conflict: {key}")
            ba, bb = _bounds(a), _bounds(b)
            if a.get("crs") and a.get("crs") == b.get("crs") and ba and bb:
                if max(ba[0], bb[0]) < min(ba[2], bb[2]) and max(ba[1], bb[1]) < min(ba[3], bb[3]):
                    raise ValueError("cross-split geospatial overlap; supply safe groups/membership")


def create_splits(rows, supplied=None, seed=42):
    if not rows:
        raise ValueError("cannot split empty data")
    if supplied is not None:
        membership, policy = dict(supplied), "supplied membership"
    else:
        if seed != 42:
            raise ValueError("generated splits require locked seed 42")
        key = None
        for candidate in ("event_id", "scene_id", "spatial_group"):
            if all(r.get(candidate) for r in rows) and len({r[candidate] for r in rows}) >= 3:
                key = candidate
                break
        if key is None:
            if any(r.get("crs") or r.get("scene_id") or r.get("event_id") or r.get("spatial_group") for r in rows):
                raise ValueError("insufficient event/scene groups; supply >=3 separated spatial_group values or explicit membership")
            key = "patch_id"
        groups = sorted({r[key] for r in rows})
        if len(groups) < 3:
            raise ValueError("need at least three independent groups")
        np.random.default_rng(seed).shuffle(groups)
        # Group constraints take precedence over patch-count proportions.
        n_train = min(len(groups) - 2, max(1, round(0.6 * len(groups))))
        n_val = min(len(groups) - n_train - 1, max(1, round(0.2 * len(groups))))
        assignment = {g: "train" if i < n_train else "validation" if i < n_train + n_val else "test"
                      for i, g in enumerate(groups)}
        membership = {r["patch_id"]: assignment[r[key]] for r in rows}
        policy = key if key != "patch_id" else "patch_id (no spatial metadata; subset-only claims)"
    validate_splits(rows, membership)
    return membership, policy


def write_frozen_artifacts(rows, membership, destination, policy):
    """Exclusive creation with image/mask paths relative to the output folder."""
    validate_splits(rows, membership)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    manifest, splits = destination / "manifest.csv", destination / "splits.csv"
    if manifest.exists() or splits.exists():
        raise FileExistsError("frozen manifest/splits already exist; use a new audit directory")
    split_seed = "not_applicable" if policy == "supplied membership" else 42
    output = [dict(r, split=membership[r["patch_id"]], split_policy=policy, split_seed=split_seed) for r in rows]
    for row in output:
        for name in ("image_path", "mask_path"):
            if row.get(name):
                # Audit rows carry absolute native paths; serialize portable
                # separators without changing the immutable source objects.
                row[name] = Path(os.path.relpath(Path(row[name]).resolve(), destination.resolve())).as_posix()
    fields = sorted({k for r in output for k in r})
    with manifest.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields); writer.writeheader()
        for row in output:
            writer.writerow({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    with splits.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream); writer.writerow(["patch_id", "split"])
        writer.writerows(sorted(membership.items()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--splits", type=Path, help="organizer/upstream CSV with patch_id,split")
    parser.add_argument("--contact-sheet", action="store_true", help="first five training patches only")
    args = parser.parse_args(argv)
    pairs = read_inventory(args.inventory)
    rows = [audit_pair(pair)[0] for pair in pairs]
    supplied = None
    if args.splits:
        with args.splits.open(newline="", encoding="utf-8-sig") as stream:
            split_rows = list(csv.DictReader(stream))
        supplied = {r["patch_id"]: r["split"] for r in split_rows}
        if len(supplied) != len(split_rows):
            raise ValueError("duplicate split membership identifier")
    elif any(r.get("split") for r in rows):
        supplied = {r["patch_id"]: r.get("split", "") for r in rows}
    membership, policy = create_splits(rows, supplied)
    if any((args.output / name).exists() for name in ("manifest.csv", "splits.csv", "contact_sheet.png")):
        raise FileExistsError("frozen audit artifacts already exist; use a new audit directory")
    contact_sheet = None
    if args.contact_sheet:
        import matplotlib.pyplot as plt
        development = [r for r in rows if membership[r["patch_id"]] == "train"][:5]
        fig, axes = plt.subplots(len(development), 4, squeeze=False, figsize=(14, 3 * len(development)))
        for ax, row in zip(axes, development):
            _, patch = audit_pair(row)
            db = power_to_db(patch.power)
            for band in range(2):
                ax[band].imshow(db[band], vmin=-30, vmax=0, cmap="gray")
                ax[band].set_title(f"{row['patch_id']} {('VV', 'VH')[band]} dB")
                ax[2].hist(db[band][patch.input_valid], bins=60, range=(-40, 10), alpha=0.5, label=("VV", "VH")[band])
            ax[2].legend(); ax[2].set_title("Valid SAR dB histogram")
            ax[3].imshow(np.ma.array(patch.labels, mask=~patch.label_valid), vmin=0, vmax=1, cmap="Blues")
            ax[3].set_title(row["label_source"])
        try:
            fig.tight_layout()
            contact_sheet = BytesIO()
            fig.savefig(contact_sheet, format="png", dpi=120)
        finally:
            plt.close(fig)
    # Optional dependency/rendering failures must leave membership unfrozen so
    # the exact same command can be retried after correcting the plotting issue.
    write_frozen_artifacts(rows, membership, args.output, policy)
    if contact_sheet is not None:
        with (args.output / "contact_sheet.png").open("xb") as stream:
            stream.write(contact_sheet.getvalue())
    print(f"Validated {len(rows)} pairs; froze {policy} in {args.output}")


if __name__ == "__main__":
    main()
