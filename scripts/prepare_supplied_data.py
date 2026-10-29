"""Acquire only the frozen supplied first-100 manual Sen1Floods11 pairs.

Freeze label-blind internal event splits before object metadata or image/label
access. Metadata, inventory and evidence are immutable. A repeat verifies the
same objects and resumes incomplete acquisition without replacing any file.
This performs byte-integrity acquisition; run sar-water-audit separately.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import quote
from urllib.request import urlopen
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sar_water.data import create_splits

PROJECT = Path(__file__).resolve().parents[1]
BUCKET = "sen1floods11"
ROOT = "https://storage.googleapis.com/"
PREFIX = "v1.1/data/flood_events/HandLabeled/"
SOURCE_URL = ROOT + BUCKET + "/v1.1/splits/flood_handlabeled/flood_train_data.csv"
SOURCE_SHA256 = "57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb"
SELECTION_SHA256 = "9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2"
MAX_BYTES = 500_000_000


def fetch(url, *, max_bytes):
    """Bound every response, including unexpectedly large error/object bodies."""
    for attempt in range(3):
        try:
            with urlopen(url, timeout=90) as response:
                content = response.read(max_bytes + 1)
            if len(content) > max_bytes:
                raise ValueError("response exceeds its declared byte bound")
            return content
        except ValueError:
            raise
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _json(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()


def _write_once(path, content):
    """Atomic publication with exclusive final creation, even across processes."""
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError("immutable artifact differs; use a new directory: " + str(path))
        return
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".partial")
    try:
        with temporary.open("xb") as stream:
            stream.write(content)
        # Windows rename is exclusive and works in restricted app sandboxes.
        # POSIX rename replaces existing files, so use an exclusive hard link.
        if os.name == "nt":
            os.rename(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _csv(rows, fields):
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def validate_selection(source_csv, selection_csv, recipe):
    """Verify both exact upstream source bytes and frozen ordered recipe rows."""
    if _sha(source_csv) != SOURCE_SHA256 or len(source_csv) != 13574:
        raise ValueError("source CSV SHA-256/length differs from supplied recipe")
    if _sha(selection_csv) != SELECTION_SHA256:
        raise ValueError("selection SHA-256 differs from frozen supplied identities/order")
    if (recipe.get("source_csv_sha256") != SOURCE_SHA256 or
            recipe.get("selection_sha256") != SELECTION_SHA256 or
            recipe.get("source_csv_url") != SOURCE_URL or recipe.get("patch_count") != 100):
        raise ValueError("recipe identity fields differ from the frozen supplied definition")
    upstream = list(csv.reader(StringIO(source_csv.decode())))
    rows = list(csv.DictReader(StringIO(selection_csv.decode())))
    if len(upstream) != 252 or len(rows) != 100:
        raise ValueError("source/selection must contain exactly 252/100 rows")
    for index, row in enumerate(rows):
        match = re.fullmatch(r"([A-Za-z][A-Za-z-]*_[0-9]+)_S1Hand\.tif", row["image_name"])
        if (not match or row["mask_name"] != match[1] + "_LabelHand.tif" or
                row["patch_id"] != match[1] or row["event_id"] != match[1].rsplit("_", 1)[0] or
                row["recipe_index"] != str(index) or row["upstream_split"] != "train" or
                row["evaluation_split"] != "unassigned" or
                upstream[index] != [row["image_name"], row["mask_name"]]):
            raise ValueError("supplied selection must match the exact first 100 ordered manual pairs")
    identifiers = [row["patch_id"] for row in rows]
    exposure = [row["patch_id"] for row in rows if row["previous_development_split"] == "train"]
    if (len(set(identifiers)) != 100 or len(exposure) != 22 or
            set(recipe.get("previous_training_overlap_ids", [])) != set(exposure) or
            any(row["previous_development_split"] not in ("", "train") for row in rows)):
        raise ValueError("duplicate identifiers or inconsistent previous training exposure")
    return rows


def _checked_objects(selected):
    objects = []
    for row in selected:
        expected = [PREFIX + folder + row[field] for folder, field in
                    (("S1Hand/", "image_name"), ("LabelHand/", "mask_name"))]
        if len(row.get("objects", [])) != 2:
            raise ValueError("each selected pair requires exactly two frozen objects")
        for item, name in zip(row["objects"], expected):
            try:
                valid = (item["name"] == name and str(item["generation"]).isdigit() and
                         int(item["size"]) > 0 and len(base64.b64decode(item["md5Hash"], validate=True)) == 16)
            except (KeyError, ValueError, TypeError):
                valid = False
            if not valid:
                raise ValueError("invalid frozen GCS object metadata")
            objects.append(item)
    if len(objects) != 200 or len({item["name"] for item in objects}) != 200:
        raise ValueError("only the exact 100 pairs / 200 unique objects can be acquired")
    if sum(int(item["size"]) for item in objects) > MAX_BYTES:
        raise ValueError("selection exceeds 500 MB; refusing object acquisition")
    return objects


def _verify_object(content, item):
    if (len(content) != int(item["size"]) or
            base64.b64encode(hashlib.md5(content).digest()).decode() != item["md5Hash"]):
        raise ValueError("object length/MD5 mismatch: " + item["name"])
    return _sha(content)


def prepare_supplied_data(data_root, output, *, source_csv_path=None, cache_root=None,
                          recipe_path=None, selection_path=None, fetcher=fetch):
    """Acquire a bounded immutable dataset and return its byte-integrity record.

    The optional cache is read only. Its selection.json must pin matching GCS
    metadata; cached bytes receive the same size/MD5 verification as downloads.
    No TIFF decoding, audit, calibration, scoring or training happens here.
    """
    started = time.perf_counter()
    destination, evidence = Path(data_root).resolve(), Path(output).resolve()
    cache_root = Path(cache_root).resolve() if cache_root is not None else None
    if destination == evidence or (cache_root is not None and destination == cache_root):
        raise ValueError("data, evidence and optional cache must use distinct directories")
    for directory in (destination, evidence):
        if directory.exists() and any(directory.iterdir()) and not (directory / "split_freeze.json").exists():
            raise FileExistsError("use a new or empty acquisition/evidence directory: " + str(directory))
    recipe_path = Path(recipe_path or PROJECT / "reports/supplied_subset_recipe.json")
    selection_path = Path(selection_path or PROJECT / "reports/supplied_subset_selection.csv")
    recipe_bytes, selection_bytes = recipe_path.read_bytes(), selection_path.read_bytes()
    recipe = json.loads(recipe_bytes)
    local_source = destination / "flood_train_data.csv"
    if source_csv_path is not None:
        source_bytes = Path(source_csv_path).read_bytes()
    elif local_source.exists():
        source_bytes = local_source.read_bytes()
    else:
        source_bytes = fetcher(SOURCE_URL, max_bytes=13574)
    rows = validate_selection(source_bytes, selection_bytes, recipe)
    membership, policy = create_splits(rows, seed=42)
    selected = [dict(row, split=membership[row["patch_id"]], source_patch_id=row["patch_id"], scene_id="")
                for row in rows]
    split_counts = dict(sorted(Counter(membership.values()).items()))
    exposure = dict(sorted(Counter(row["split"] for row in selected
                                   if row["previous_development_split"] == "train").items()))
    split_rows = [dict(patch_id=key, split=value) for key, value in sorted(membership.items())]
    split_bytes = _csv(split_rows, ["patch_id", "split"])
    freeze = dict(status="label_blind_internal_splits_frozen_before_object_access", seed=42,
                  split_policy=policy, source_csv_sha256=SOURCE_SHA256,
                  selection_sha256=SELECTION_SHA256, recipe_sha256=_sha(recipe_bytes),
                  splits_sha256=_sha(split_bytes), split_counts=split_counts,
                  events_by_split={split: sorted({row["event_id"] for row in selected if row["split"] == split})
                                   for split in ("train", "validation", "test")},
                  previous_training_exposure_by_split=exposure,
                  upstream_split_counts={"train": 100},
                  limitation="Internal event splits are not official upstream test membership; prior exposure is disclosed, never a selection criterion.",
                  selected=[{key: row[key] for key in ("recipe_index", "patch_id", "event_id", "split",
                            "upstream_split", "previous_development_split")} for row in selected])
    if (destination / "split_freeze.json").exists():
        frozen = json.loads((destination / "split_freeze.json").read_bytes())
        if {key: value for key, value in frozen.items() if key != "frozen_utc"} != freeze:
            raise ValueError("existing split freeze differs from exact supplied definition")
        freeze = frozen
    else:
        freeze["frozen_utc"] = datetime.now(timezone.utc).isoformat()
    for directory in (destination, evidence):
        directory.mkdir(parents=True, exist_ok=True)
        _write_once(directory / "split_freeze.json", _json(freeze))
        _write_once(directory / "splits.csv", split_bytes)
    _write_once(local_source, source_bytes)
    _write_once(destination / "supplied_subset_selection.csv", selection_bytes)

    # This is the first object-related access: splits are already immutable.
    metadata_path = destination / "selection.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_bytes())
        stored = metadata.get("selected", [])
        if [{k: v for k, v in row.items() if k != "objects"} for row in stored] != selected:
            raise ValueError("frozen object selection differs from exact supplied identities/splits")
        if metadata.get("split_freeze_sha256") != _sha(_json(freeze)):
            raise ValueError("object metadata split freeze hash mismatch")
        selected = stored
    else:
        def metadata_for(row):
            row = dict(row)
            row["objects"] = []
            for folder, field in (("S1Hand/", "image_name"), ("LabelHand/", "mask_name")):
                name = PREFIX + folder + row[field]
                url = ROOT + "storage/v1/b/" + BUCKET + "/o/" + quote(name, safe="")
                item = json.loads(fetcher(url, max_bytes=65536))
                row["objects"].append({key: item[key] for key in
                                       ("name", "generation", "size", "md5Hash", "crc32c", "updated")})
            return row
        with ThreadPoolExecutor(max_workers=4) as pool:
            selected = list(pool.map(metadata_for, selected))
        _checked_objects(selected)
        metadata = dict(status="selection_and_internal_splits_frozen_before_imagery_read", seed=42,
                        purpose="user-supplied first100 training-row profile; distinct from development",
                        source_csv_url=SOURCE_URL, source_csv_sha256=SOURCE_SHA256,
                        selection_sha256=SELECTION_SHA256, split_freeze_sha256=_sha(_json(freeze)),
                        split_counts=split_counts, upstream_split_counts={"train": 100},
                        previous_training_exposure_by_split=exposure, selected=selected,
                        frozen_utc=datetime.now(timezone.utc).isoformat())
        _write_once(metadata_path, _json(metadata))
    objects = _checked_objects(selected)
    _write_once(evidence / "selection.json", _json(metadata))
    cached_metadata = {}
    if cache_root is not None and (cache_root / "selection.json").exists():
        cache_selection = json.loads((cache_root / "selection.json").read_bytes())
        cached_metadata = {obj["name"]: obj for row in cache_selection["selected"] for obj in row["objects"]}

    def acquire(item):
        path = destination / Path(item["name"]).name
        origin = "existing_destination"
        if path.exists():
            content = path.read_bytes()
        elif cache_root is not None and (cache_root / path.name).exists():
            original = cached_metadata.get(item["name"], {})
            if any(str(original.get(key)) != str(item[key]) for key in ("name", "generation", "size", "md5Hash")):
                raise ValueError("cached object generation/size/MD5 metadata mismatch: " + item["name"])
            content = (cache_root / path.name).read_bytes()
            origin = "cache"
        else:
            url = ROOT + BUCKET + "/" + item["name"] + "?generation=" + str(item["generation"])
            content = fetcher(url, max_bytes=int(item["size"]))
            origin = "download"
        digest = _verify_object(content, item)
        if origin != "existing_destination":
            _write_once(path, content)
        return dict(name=item["name"], path=path.name, sha256=digest, bytes=len(content),
                    generation=str(item["generation"]), md5Hash=item["md5Hash"], origin=origin)

    with ThreadPoolExecutor(max_workers=4) as pool:
        acquired = list(pool.map(acquire, objects))
    inventory = []
    for row in selected:
        for kind, key, folder in (("image", "image_name", "S1Hand/"), ("mask", "mask_name", "LabelHand/")):
            inventory.append(dict(patch_id=row["patch_id"], kind=kind, path=row[key], units="db",
                                  band_order="VV,VH", label_source="manual", source="gs://" + BUCKET + "/" + PREFIX + folder + row[key],
                                  event_id=row["event_id"], scene_id="", source_patch_id=row["patch_id"],
                                  split=row["split"], upstream_split="train", recipe_index=row["recipe_index"],
                                  previous_development_split=row["previous_development_split"]))
    inventory_bytes = _csv(inventory, sorted(inventory[0]))
    _write_once(destination / "inventory.csv", inventory_bytes)
    result_path = destination / "download.json"
    if result_path.exists():
        result = json.loads(result_path.read_bytes())
        actual = [{k: v for k, v in row.items() if k != "origin"} for row in acquired]
        frozen = [{k: v for k, v in row.items() if k != "origin"} for row in result["objects"]]
        if actual != frozen or result.get("inventory_sha256") != _sha(inventory_bytes):
            raise ValueError("completed acquisition SHA-256/inventory identity mismatch")
    else:
        result = dict(status="download_verified_not_raster_audited", pairs=100, files=200,
                      bytes=sum(row["bytes"] for row in acquired), objects=acquired,
                      origin_counts=dict(sorted(Counter(row["origin"] for row in acquired).items())),
                      source_csv_sha256=SOURCE_SHA256, selection_sha256=_sha(_json(metadata)),
                      supplied_selection_sha256=SELECTION_SHA256, split_freeze_sha256=_sha(_json(freeze)),
                      splits_sha256=_sha(split_bytes), inventory_sha256=_sha(inventory_bytes),
                      split_counts=split_counts, previous_training_exposure_by_split=exposure,
                      acquisition_elapsed_seconds=time.perf_counter() - started,
                      downloaded_utc=datetime.now(timezone.utc).isoformat(),
                      raster_audit_complete=False, calibration_complete=False, training_complete=False,
                      fresh_colab_verified=False)
        _write_once(result_path, _json(result))
    _write_once(evidence / "download.json", _json(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data/supplied-v1"))
    parser.add_argument("--output", type=Path, required=True, help="new dedicated acquisition evidence directory")
    parser.add_argument("--source-csv", type=Path, help="optional exact original source bytes; otherwise fetched and checked")
    parser.add_argument("--cache-root", type=Path, help="optional read-only verified development TIFF cache")
    args = parser.parse_args(argv)
    result = prepare_supplied_data(args.data_root, args.output, source_csv_path=args.source_csv, cache_root=args.cache_root)
    print(json.dumps({key: value for key, value in result.items() if key != "objects"}, indent=2))


if __name__ == "__main__":
    main()
