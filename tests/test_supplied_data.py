"""Supplied acquisition freezes identities/splits before touching any TIFF."""
import base64
from collections import Counter
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import pytest

ROOT = Path(__file__).parents[1]


def module():
    spec = importlib.util.spec_from_file_location(
        "prepare_supplied_data", ROOT / "scripts/prepare_supplied_data.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


@pytest.fixture
def recipe():
    return json.loads((ROOT / "reports/supplied_subset_recipe.json").read_text())


@pytest.fixture
def selection():
    return (ROOT / "reports/supplied_subset_selection.csv").read_bytes()


@pytest.fixture
def source_csv():
    # The exact public 252-row CSV is embedded below as compressed bytes. This
    # keeps tests offline and independent of ignored local development data.
    import zlib
    return zlib.decompress(base64.b64decode(SOURCE_ZLIB_BASE64))


def test_exact_first100_order_source_hash_and_exposure_are_required(source_csv, selection, recipe):
    mod = module()
    rows = mod.validate_selection(source_csv, selection, recipe)
    assert len(rows) == 100
    assert [row["patch_id"] for row in rows[:3]] == [
        "Ghana_103272", "Ghana_24858", "Ghana_147015"]
    assert rows[-1]["patch_id"] == "Pakistan_909806"
    assert Counter(row["event_id"] for row in rows) == {
        "Ghana": 31, "India": 40, "Mekong": 18, "Nigeria": 10, "Pakistan": 1}
    assert sum(row["previous_development_split"] == "train" for row in rows) == 22
    with pytest.raises(ValueError, match="source CSV SHA"):
        mod.validate_selection(source_csv + b"\n", selection, recipe)
    lines = selection.splitlines(keepends=True)
    lines[1], lines[2] = lines[2], lines[1]
    with pytest.raises(ValueError, match="selection SHA"):
        mod.validate_selection(source_csv, b"".join(lines), recipe)
    changed_recipe = dict(recipe, previous_training_overlap_ids=[])
    with pytest.raises(ValueError, match="exposure"):
        mod.validate_selection(source_csv, selection, changed_recipe)


def service(source_csv, selection, destination, *, corrupt_name=None, oversize=False):
    """Only fake the external bytes; production writes and hashes remain real."""
    rows = list(csv.DictReader(selection.decode().splitlines()))
    objects = {}
    bodies = {}
    prefix = "v1.1/data/flood_events/HandLabeled/"
    for row in rows:
        for folder, field in (("S1Hand/", "image_name"), ("LabelHand/", "mask_name")):
            name = prefix + folder + row[field]
            body = ("verified fixture bytes: " + name).encode()
            objects[name] = dict(name=name, generation="123456789", size=str(len(body)),
                                 md5Hash=base64.b64encode(hashlib.md5(body).digest()).decode(),
                                 crc32c="AAAAAA==", updated="2020-10-01T00:00:00Z")
            bodies[name] = body
    if oversize:
        objects[next(iter(objects))]["size"] = "500000001"

    def fetch(url, *, max_bytes):
        if url.endswith("flood_train_data.csv"):
            return source_csv
        # Both object metadata and TIFF requests happen after immutable splits.
        assert (destination / "split_freeze.json").exists()
        assert (destination / "splits.csv").exists()
        parsed = urlparse(url)
        if "/storage/v1/" in parsed.path:
            name = unquote(parsed.path.split("/o/", 1)[1])
            return json.dumps(objects[name]).encode()
        name = parsed.path.split("/sen1floods11/", 1)[1]
        assert parse_qs(parsed.query) == {"generation": ["123456789"]}
        assert max_bytes == int(objects[name]["size"])
        return b"corrupt" if name == corrupt_name else bodies[name]

    return fetch, objects, bodies


def test_split_freezes_before_fetch_and_inventory_uses_internal_membership(tmp_path, source_csv, selection):
    mod = module()
    data, report = tmp_path / "data", tmp_path / "report"
    fetch, _, _ = service(source_csv, selection, data)
    result = mod.prepare_supplied_data(data, report, fetcher=fetch)
    freeze = json.loads((data / "split_freeze.json").read_text())
    assert freeze["split_policy"] == "event_id"
    assert freeze["split_counts"] == {"train": 29, "validation": 40, "test": 31}
    assert freeze["previous_training_exposure_by_split"] == {"train": 5, "validation": 9, "test": 8}
    assert freeze["events_by_split"] == {
        "train": ["Mekong", "Nigeria", "Pakistan"], "validation": ["India"], "test": ["Ghana"]}
    from sar_water.data import read_inventory
    pairs = read_inventory(data / "inventory.csv")
    assert len(pairs) == 100
    assert Counter(row["split"] for row in pairs) == {"train": 29, "validation": 40, "test": 31}
    assert {row["upstream_split"] for row in pairs} == {"train"}
    assert result["files"] == 200
    assert result["origin_counts"] == {"download": 200}
    assert all(len(row["sha256"]) == 64 for row in result["objects"])


def test_repeat_verifies_files_without_network_or_overwriting(tmp_path, source_csv, selection):
    mod = module()
    data, report = tmp_path / "data", tmp_path / "report"
    fetch, _, _ = service(source_csv, selection, data)
    initial = mod.prepare_supplied_data(data, report, fetcher=fetch)
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns)
              for root in (data, report) for path in root.iterdir() if path.is_file()}

    def offline(*args, **kwargs):
        raise AssertionError("completed repeat must use its frozen source/metadata")

    assert mod.prepare_supplied_data(data, report, fetcher=offline) == initial
    assert all((path.read_bytes(), path.stat().st_mtime_ns) == old for path, old in before.items())
    (data / "Ghana_103272_S1Hand.tif").write_bytes(b"damaged")
    with pytest.raises(ValueError, match="length/MD5"):
        mod.prepare_supplied_data(data, report, fetcher=offline)


def test_corrupt_download_is_rejected_before_final_path_exists(tmp_path, source_csv, selection):
    mod = module()
    data = tmp_path / "data"
    name = "v1.1/data/flood_events/HandLabeled/S1Hand/Ghana_103272_S1Hand.tif"
    fetch, _, _ = service(source_csv, selection, data, corrupt_name=name)
    with pytest.raises(ValueError, match="length/MD5"):
        mod.prepare_supplied_data(data, tmp_path / "report", fetcher=fetch)
    assert not (data / "Ghana_103272_S1Hand.tif").exists()
    assert not (data / "download.json").exists()
    assert not list(data.glob("*.partial"))


def test_cache_copy_is_verified_and_corruption_fails(tmp_path, source_csv, selection):
    mod = module()
    cache = tmp_path / "cache"
    cache.mkdir()
    data = tmp_path / "data"
    fetch, objects, bodies = service(source_csv, selection, data)
    name = "v1.1/data/flood_events/HandLabeled/S1Hand/Ghana_103272_S1Hand.tif"
    (cache / "selection.json").write_text(json.dumps({"selected": [{"objects": [objects[name]]}]}))
    cached_path = cache / "Ghana_103272_S1Hand.tif"
    cached_path.write_bytes(bodies[name])
    result = mod.prepare_supplied_data(data, tmp_path / "report", cache_root=cache, fetcher=fetch)
    assert result["origin_counts"] == {"cache": 1, "download": 199}
    assert (data / cached_path.name).read_bytes() == bodies[name]
    assert cached_path.read_bytes() == bodies[name]
    cached_path.write_bytes(b"damaged cached object")
    second = tmp_path / "second"
    fetch2, _, _ = service(source_csv, selection, second)
    with pytest.raises(ValueError, match="length/MD5"):
        mod.prepare_supplied_data(second, tmp_path / "report2", cache_root=cache, fetcher=fetch2)
    assert not (second / cached_path.name).exists()


def test_oversized_selection_fails_before_any_tiff(tmp_path, source_csv, selection):
    mod = module()
    data = tmp_path / "data"
    fetch, _, _ = service(source_csv, selection, data, oversize=True)
    with pytest.raises(ValueError, match="500"):
        mod.prepare_supplied_data(data, tmp_path / "report", fetcher=fetch)
    assert not list(data.glob("*.tif"))


def test_existing_unrelated_destination_is_never_adopted(tmp_path):
    mod = module()
    data = tmp_path / "data"
    data.mkdir()
    existing = data / "notes.txt"
    existing.write_text("preserve me")
    with pytest.raises(FileExistsError, match="new|empty"):
        mod.prepare_supplied_data(data, tmp_path / "report")
    assert existing.read_text() == "preserve me"


SOURCE_ZLIB_BASE64 = "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"
