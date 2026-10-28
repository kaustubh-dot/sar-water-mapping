"""Scientific fixtures; these are not organizer data or experiment results."""
import csv
import importlib.util
from pathlib import Path

import numpy as np
import pytest


def api():
    assert importlib.util.find_spec("sar_water.data") is not None, "data adapter missing"
    from sar_water import data
    return data


def test_explicit_units_band_order_and_zero_db():
    d = api()
    x = np.array([[[0, -10]], [[-20, -30]]], dtype=np.float32)
    p = d.adapt_arrays(x, np.array([[0, 1]]), units="db", band_order="VH,VV")
    np.testing.assert_allclose(p.power[:, 0, 0], [0.01, 1])
    np.testing.assert_allclose(d.power_to_db(p.power), x[::-1], atol=1e-5)
    assert p.input_valid.all()
    assert p.power.dtype == np.float32
    with pytest.raises(ValueError, match="units"):
        d.adapt_arrays(x, np.array([[0, 1]]), units="amplitude", band_order="VV,VH")
    with pytest.raises(ValueError, match="band"):
        d.adapt_arrays(x, np.array([[0, 1]]), units="db", band_order="VV,VV")


def test_input_label_validity_are_independent_and_fill_is_sar_only():
    d = api()
    x = np.array([[[0, np.nan], [-10, -20]]] * 2)
    p = d.adapt_arrays(x, np.array([[-1, 1], [0, 1]]), units="db", band_order="VV,VH")
    assert p.input_valid[0, 0] and not p.label_valid[0, 0]
    assert not p.input_valid[0, 1] and p.label_valid[0, 1]
    assert p.score_valid.sum() == 2
    filled = d.nearest_valid_fill(p.power, p.input_valid)
    assert np.isfinite(filled).all()
    np.testing.assert_array_equal(filled, d.nearest_valid_fill(p.power, p.input_valid))
    np.testing.assert_array_equal(filled[:, p.input_valid], p.power[:, p.input_valid])
    with pytest.raises(ValueError, match="all-invalid"):
        d.nearest_valid_fill(p.power, np.zeros((2, 2), dtype=bool))


@pytest.mark.parametrize("labels", [np.array([[0, 2]]), np.array([[0, np.nan]])])
def test_unknown_labels_rejected(labels):
    with pytest.raises(ValueError, match="label"):
        api().adapt_arrays(np.ones((2, 1, 2)), labels, units="linear_power", band_order="VV,VH")


def test_masks_nodata_power_and_shape_validation():
    d = api()
    p = d.adapt_arrays(np.ones((2, 1, 2)), np.array([[0, 1]]), units="linear_power",
                       band_order="VV,VH", input_mask=np.array([[[1, 0]], [[1, 1]]], bool),
                       label_mask=np.array([[0, 1]], bool))
    assert p.input_valid.tolist() == [[True, False]]
    assert p.label_valid.tolist() == [[False, True]]
    assert not p.score_valid.any()
    for x in (np.zeros((2, 1, 2)), np.ones((3, 1, 2))):
        with pytest.raises(ValueError):
            d.adapt_arrays(x, np.array([[0, 1]]), units="linear_power", band_order="VV,VH")


def records(n=10):
    return [dict(patch_id=f"p{i}", image_sha256=f"i{i}", mask_sha256=f"m{i}",
                 event_id=f"e{i}", scene_id="", crs="", bounds="") for i in range(n)]


def test_splits_reproducible_grouped_and_frozen(tmp_path):
    d = api()
    rows = records()
    rows[1]["event_id"] = rows[0]["event_id"]
    a, policy = d.create_splits(rows)
    b, _ = d.create_splits(list(reversed(rows)))
    assert a == b and policy == "event_id"
    assert a["p0"] == a["p1"]
    assert set(a.values()) == {"train", "validation", "test"}
    d.write_frozen_artifacts(rows, a, tmp_path, policy)
    assert (tmp_path / "manifest.csv").is_file()
    with pytest.raises(FileExistsError):
        d.write_frozen_artifacts(rows, a, tmp_path, policy)


def test_supplied_split_duplicate_and_overlap_checks():
    d = api()
    rows = records(3)
    supplied = dict(p0="train", p1="validation", p2="test")
    assert d.create_splits(rows, supplied)[0] == supplied
    rows[1]["image_sha256"] = rows[0]["image_sha256"]
    with pytest.raises(ValueError, match="duplicate"):
        d.create_splits(rows, supplied)
    rows = records(3)
    for row in rows:
        row.update(crs="EPSG:4326", bounds=[0, 0, 2, 2])
    with pytest.raises(ValueError, match="overlap"):
        d.create_splits(rows, supplied)
    with pytest.raises(ValueError, match="membership"):
        d.create_splits(records(3), {"p0": "train"})


def test_split_hierarchy_never_silently_randomizes_spatial_data():
    d = api()
    rows = records(3)
    for row in rows:
        row.update(event_id="e", scene_id="s", crs="EPSG:4326", bounds=[0, 0, 1, 1])
    with pytest.raises(ValueError, match="spatial_group"):
        d.create_splits(rows)
    for row in rows:
        row.update(event_id="", scene_id="", crs="", bounds="")
    _, policy = d.create_splits(rows)
    assert policy == "patch_id (no spatial metadata; subset-only claims)"


def test_inventory_identifier_pairing(tmp_path):
    d = api()
    path = tmp_path / "inventory.csv"
    fields = ["patch_id", "kind", "path", "units", "band_order", "label_source", "source"]
    rows = [dict(patch_id="x", kind="mask", path="mask.tif", label_source="manual", source="organizer"),
            dict(patch_id="x", kind="image", path="image.tif", units="db", band_order="VV,VH", source="organizer")]
    def write(rs):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fields); w.writeheader(); w.writerows(rs)
    write(rows)
    pairs = d.read_inventory(path)
    assert len(pairs) == 1 and pairs[0]["patch_id"] == "x"
    assert pairs[0]["mask_path"] == str(tmp_path / "mask.tif")
    write(rows + [rows[0]])
    with pytest.raises(ValueError, match="duplicate"):
        d.read_inventory(path)
    write(rows[:1])
    with pytest.raises(ValueError, match="pair"):
        d.read_inventory(path)


def test_geotiff_metadata_and_content_hashes(tmp_path):
    rio = pytest.importorskip("rasterio")
    d = api()
    transform = rio.transform.from_origin(0, 2, 1, 1)
    def save(path, values, transform=transform):
        with rio.open(path, "w", driver="GTiff", height=2, width=2, count=len(values),
                      dtype=values.dtype, crs="EPSG:4326", transform=transform) as ds:
            ds.write(values)
    image, mask = tmp_path / "i.tif", tmp_path / "m.tif"
    save(image, np.zeros((2, 2, 2), dtype="float32"))
    save(mask, np.zeros((1, 2, 2), dtype="int16"))
    pair = dict(patch_id="p", image_path=str(image), mask_path=str(mask), units="db", band_order="VV,VH", label_source="manual", source="fixture")
    row, patch = d.audit_pair(pair)
    assert len(row["image_sha256"]) == 64 and len(row["image_content_sha256"]) == 64
    assert patch.input_valid.all()
    save(mask, np.zeros((1, 2, 2), dtype="int16"), rio.transform.from_origin(1, 2, 1, 1))
    with pytest.raises(ValueError, match="georeferencing"):
        d.audit_pair(pair)


def test_inventory_source_patch_conflicts_are_not_lost(tmp_path):
    path = tmp_path / "inventory.csv"
    path.write_text('patch_id,kind,path,source,units,band_order,label_source,source_patch_id\n'
                    'x,image,i.tif,fixture,db,"VV,VH",,parent-a\n'
                    'x,mask,m.tif,fixture,,,manual,parent-b\n', encoding="utf-8")
    with pytest.raises(ValueError, match="source_patch_id"):
        api().read_inventory(path)


def test_nonfinite_power_rejected_by_db_conversion():
    with pytest.raises(ValueError, match="power"):
        api().power_to_db(np.array([1, np.inf]))


def test_reject_partial_or_mixed_spatial_metadata():
    rows = records(3)
    for row in rows:
        row.update(event_id="", scene_id="", crs="", bounds="")
    rows[0].update(spatial_group="a")
    with pytest.raises(ValueError, match="spatial_group"):
        api().create_splits(rows)


def test_split_seed_provenance_matches_locked_generation_or_supplied_membership(tmp_path):
    d = api()
    with pytest.raises(ValueError, match="seed 42"):
        d.create_splits(records(), seed=7)
    generated, policy = d.create_splits(records())
    d.write_frozen_artifacts(records(), generated, tmp_path / "generated", policy)
    supplied, policy = d.create_splits(records(), supplied=generated)
    d.write_frozen_artifacts(records(), supplied, tmp_path / "supplied", policy)
    for name, expected in (("generated", "42"), ("supplied", "not_applicable")):
        with (tmp_path / name / "manifest.csv").open(newline="") as stream:
            assert {r["split_seed"] for r in csv.DictReader(stream)} == {expected}


def test_failed_contact_sheet_does_not_freeze_cli_outputs_and_can_retry(tmp_path, monkeypatch):
    rio = pytest.importorskip("rasterio")
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    d = api()
    inventory = tmp_path / "inventory.csv"
    with inventory.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["patch_id", "kind", "path", "source", "units", "band_order", "label_source", "split"])
        for i, split in enumerate(("train", "validation", "test")):
            for kind, bands in (("image", 2), ("mask", 1)):
                path = tmp_path / f"{i}-{kind}.tif"
                with rio.open(path, "w", driver="GTiff", height=2, width=2, count=bands,
                              dtype="float32", crs="EPSG:4326",
                              transform=rio.transform.from_origin(i * 4, 2, 1, 1)) as ds:
                    ds.write(np.full((bands, 2, 2), -i if kind == "image" else 0, dtype="float32"))
                writer.writerow([f"p{i}", kind, path.name, "synthetic fixture", "db" if kind == "image" else "",
                                 "VV,VH" if kind == "image" else "", "manual" if kind == "mask" else "", split])
    output = tmp_path / "audit"
    arguments = [str(inventory), "--output", str(output), "--contact-sheet"]
    real_savefig = Figure.savefig
    def fail_savefig(*args, **kwargs):
        raise OSError("simulated rendering failure")
    monkeypatch.setattr(Figure, "savefig", fail_savefig)
    with pytest.raises(OSError, match="rendering failure"):
        d.main(arguments)
    assert not (output / "manifest.csv").exists()
    assert not (output / "splits.csv").exists()
    monkeypatch.setattr(Figure, "savefig", real_savefig)
    d.main(arguments)
    assert (output / "contact_sheet.png").is_file()
    assert (output / "manifest.csv").is_file()
    with pytest.raises(FileExistsError):
        d.main(arguments)


def test_geotiff_alignment_accepts_serialization_roundoff_but_rejects_subpixel_shift(tmp_path):
    """Upstream scale roundoff is harmless; 1/8-pixel shift must still fail."""
    rio = pytest.importorskip('rasterio')
    from affine import Affine
    transform = Affine(8.983152841195215e-5,0,81.6388930207821,0,-8.983152841195215e-5,7.772942490429395)
    image,mask=tmp_path/'image.tif',tmp_path/'mask.tif'
    def save(path,bands,affine):
        with rio.open(path,'w',driver='GTiff',height=512,width=512,count=bands,dtype='float32',crs='EPSG:4326',transform=affine) as dataset:
            dataset.write(np.zeros((bands,512,512),dtype='float32'))
    save(image,2,transform)
    pair=dict(patch_id='p',image_path=str(image),mask_path=str(mask),units='db',band_order='VV,VH',label_source='manual')
    roundoff=Affine(8.983152841195857e-5,0,transform.c,0,-8.983152841195857e-5,transform.f)
    save(mask,1,roundoff)
    row,patch=api().audit_pair(pair)
    assert patch.power.shape==(2,512,512)
    assert row['max_alignment_error_pixels'] <= 1e-6
    save(mask,1,Affine(transform.a,transform.b,transform.c+.125*transform.a,transform.d,transform.e,transform.f+.125*transform.d))
    with pytest.raises(ValueError,match='georeferencing'):
        api().audit_pair(pair)
    # A small scale error must be evaluated at the far corner, not origin only.
    save(mask,1,Affine(transform.a*(1+1e-7),transform.b,transform.c,transform.d*(1+1e-7),transform.e,transform.f))
    with pytest.raises(ValueError,match='georeferencing'):
        api().audit_pair(pair)


def test_frozen_manifest_paths_survive_copy_and_move_of_complete_dataset(tmp_path):
    """An absolute source path would silently read the old tree after copying."""
    import shutil
    rio=pytest.importorskip('rasterio')
    d=api()
    original=tmp_path/'original'
    raw=original/'raw';raw.mkdir(parents=True)
    rows=[]
    membership={'p0':'train','p1':'validation','p2':'test'}
    for i,identifier in enumerate(membership):
        paths={kind:raw/f'{identifier}-{kind}.tif' for kind in ('image','mask')}
        for kind,path in paths.items():
            bands=2 if kind=='image' else 1
            with rio.open(path,'w',driver='GTiff',height=2,width=2,count=bands,dtype='float32',
                          crs='EPSG:4326',transform=rio.transform.from_origin(i*4,2,1,1)) as dataset:
                dataset.write(np.full((bands,2,2),-i if kind=='image' else 0,dtype='float32'))
        row,_=d.audit_pair(dict(patch_id=identifier,image_path=str(paths['image']),mask_path=str(paths['mask']),
                               units='db',band_order='VV,VH',label_source='manual'))
        rows.append(row)
    d.write_frozen_artifacts(rows,membership,original/'audit','supplied membership')
    with (original/'audit'/'manifest.csv').open(newline='') as stream:
        serialized=list(csv.DictReader(stream))
    assert serialized[0]['image_path']=='../raw/p0-image.tif'
    assert serialized[0]['mask_path']=='../raw/p0-mask.tif'
    copied=tmp_path/'copied'
    shutil.copytree(original,copied)
    # Both explicit paths are confined to this test's own temporary directory.
    moved=tmp_path/'moved'
    assert original.resolve().is_relative_to(tmp_path.resolve())
    assert moved.resolve().is_relative_to(tmp_path.resolve())
    original.rename(moved)
    for root in (copied,moved):
        restored=d.read_manifest(root/'audit'/'manifest.csv')
        assert Path(restored[0]['image_path'])==root/'raw'/'p0-image.tif'
        for frozen in restored:
            audited,patch=d.audit_pair(frozen)
            assert audited['image_sha256']==frozen['image_sha256']
            assert audited['mask_sha256']==frozen['mask_sha256']
            assert audited['image_content_sha256']==frozen['image_content_sha256']
            assert frozen['split']==membership[frozen['patch_id']]


def test_alignment_error_is_invariant_to_shared_large_world_translation():
    from affine import Affine
    d=api()
    image=Affine(1e-4,0,0,0,-1e-4,0)
    mask=Affine(1e-4+1e-14,0,0,0,-1e-4-1e-14,0)
    baseline=d._alignment_error_pixels(image,mask,512,512)
    translated_image=Affine(image.a,image.b,1e9,image.d,image.e,-1e9)
    translated_mask=Affine(mask.a,mask.b,1e9,mask.d,mask.e,-1e9)
    translated=d._alignment_error_pixels(translated_image,translated_mask,512,512)
    assert baseline > 1e-9
    assert translated==pytest.approx(baseline,rel=1e-12,abs=0)
