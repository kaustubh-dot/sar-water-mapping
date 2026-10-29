# Upstream development subset: Phase 1 execution evidence

The organizer kickoff archive remains unavailable. This audit uses exactly 100 upstream Sen1Floods11 v1.1 hand-labeled SAR/mask pairs as a development substitute. It does not close the organizer-data delivery gate or establish unseen-event generalization.

## Access and frozen membership

`python scripts/prepare_development_data.py` fetched only 200 selected GeoTIFF objects, 164,663,453 bytes, in 184.323 seconds on this workstation. All object sizes and GCS MD5 hashes matched; per-file SHA-256 and pinned GCS generations are in `development_data_download.json`. The selection was saved before downloading or reading imagery/masks. Its SHA-256 is `e7cbd62911647be8ad0fa0d6c08be3f98dc1bc335bf0e780ff180005b2642acf`.

Official train/validation/test membership is retained: 60/20/20 chips. Within each upstream partition, the smallest SHA-256 ranks of `42:split:patch_id` were selected without reading labels. The source lists contain 252/89/90 pairs; the separate Bolivia split is not mixed into them. Source URLs and source-list hashes are in `development_data_selection.json`. The selected events are Ghana, India, Mekong, Nigeria, Pakistan, Paraguay, Somalia, Spain, Sri-Lanka, and USA. Events occur across supplied partitions, so claims are within the official subset, not held-out-event claims. No full dataset download occurred.

The [upstream README](https://github.com/cloudtostreet/Sen1Floods11) establishes the two-band VV/VH dB input convention. The [upstream directory documentation](https://raw.githubusercontent.com/cloudtostreet/Sen1Floods11/master/docs/README.md) separates `LabelHand` from Otsu and weak labels. Only `S1Hand` and `LabelHand` object paths were admitted. Annotation provenance is upstream manual annotation, not a new independent relabeling audit. Dataset materials retain their original terms; project MIT licensing does not relicense them.

## Numeric and geographic audit

The loader validated all 100 identifier-matched pairs: each is 512 x 512, with two float32 SAR bands, one mask band, and EPSG:4326. Unsupported labels are rejected; the observed manual label codes are -1/0/1. SAR nodata is NaN for all 100. Thirteen chips contain invalid SAR pixels; input and label masks remain independent. The adapter converts dB with `10**(dB/10)` and preserves valid zero dB.

A real-data compatibility issue was found before freezing membership. Source image/mask pixel scales differ by floating-point serialization roundoff, with the same origins and CRS. The strict equality check rejected these arrays. The authorized correction accepts a maximum displacement of 1e-6 image pixels at all four raster corners, with exact CRS equality and no reprojection or resampling. It records both transforms and maximum displacement. The recorded maximum across this subset is 7.91e-11 pixels. The bound remains far below meaningful subpixel shifts. Regression tests accept actual upstream roundoff and reject a 1/8-pixel origin shift and a scale error accumulating beyond the bound at a far corner. The original differences are retained in `development_data_georeferencing.json`.

The normal audit then froze `data/development-v1/audit/manifest.csv` and `splits.csv` with `supplied membership`, not a newly generated random split. All 100 file hashes and 100 decoded-power hashes are unique. The audit found no cross-partition source-ID duplicate or positive-area same-CRS bounding-box overlap. It does not certify that all neighboring chips are geographically independent. Full source-scene IDs are missing; event IDs derive from the documented filenames.

Two label-validity observations need to remain visible: training chip `Ghana_26376` has no valid scored pixels; training chip `Ghana_24858` declares mask nodata 0, leaving 484 valid scored pixels. The loader respects this metadata rather than treating masked land as training truth. All-invalid training draws must be skipped. These chips were retained in the label-blind frozen selection; no patch was replaced after reading labels.

## Visual inspection

The actual contact sheet at `outputs/development_data/contact_sheet.png` was opened with `view_image` and inspected. It shows raw VV, raw VH, their dB histograms, and independent manual masks for five training patches selected as the first available patch from five distinct events:

- `Ghana_103272`: sparse small water bodies against mostly homogeneous land; unimodal histograms make per-image thresholding a plausible false-positive failure.
- `India_103447`: broad braided river and label-invalid areas; radar/label boundaries require the separate scoring mask.
- `Mekong_1439641`: wide river with visible shorelines and broad dark regions, suitable for later raw-only homogeneous ROI inspection.
- `Nigeria_143329`: sparse narrow water, mostly unimodal land, and invalid label areas; whole-patch ENL would be inappropriate.
- `Pakistan_1036366`: branching channels, fine structures, and bright land returns; smoothing can remove narrow-water detail.

VV is brighter than VH in the displayed samples and their histograms; this is a consistency check against the documented band order, not an independent sensor calibration. Water is generally dark but class boundaries and invalid annotation areas remain visible. Raw displays use shared -30 to 0 dB limits. No validation/test masks were visually inspected for method tuning. Numeric inspection records are in `development_data_visual_inspection.json`.

## Verification and remaining gate

Commands run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_development_data.py
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m sar_water.data data/development-v1/inventory.csv --output data/development-v1/audit
.\.venv\Scripts\python.exe -m pytest tests/test_data.py tests/test_development_data.py -q --basetemp=outputs/pytest-alignment-final
```

The data CLI reported `Validated 100 pairs; froze supplied membership`. The focused suite passed 19 tests. The source-selection test first failed before the selector existed; the upstream hyphen-name and georeferencing regressions were observed failing before their corrections. The GeoTIFF data and contact sheet remain ignored local artifacts.

Phase 1 development-subset evidence is ready for the required independent review. Training ROI selection, effective looks, validation calibration, final test scores, remote training and fresh Colab timing are unrun. Calibration will begin only after that review. No final test labels were used to select a method.

## Independent-review corrections: portable audit and supplied adjacency

The [Sol xhigh review](development_data_review.md) found that all original manifest paths were workstation-specific and identified seven actual touching cross-partition bounding-box pairs. The original frozen audit was preserved. The final portable version is `data/development-v1/audit-v3-relative/`; the intermediate `audit-v2-relative/` is also preserved and is not the calibration identity. New manifests serialize image/mask paths relative to their own folder using POSIX separators. `sar_water.data.read_manifest` resolves them on the destination machine. The copied/moved complete-tree GeoTIFF regression failed on the old absolute paths and now verifies all source hashes and membership after relocation without editing the manifest.

The relative manifest resolves all 200 paths to exactly the same source files. All 100 image SHA-256 values, 100 mask SHA-256 values, 100 decoded-power hashes, IDs, label provenance, units, band order and split membership were compared to the original and recomputed. The split CSV is byte-identical. Final manifest SHA-256: `74d00fd2b08e6417e77a102c0cfd5b0bd5c3b1d759ff814b6fabdae4729792cc`. Split SHA-256: `24963a9951f318aab0cc3d687023ce849fc5c9435ed9fc8cbadced4dc6c2d1b7`.

A small origin-arithmetic correction now subtracts each affine origin before adding linear differences. Its regression first reproduced lost precision after a shared large coordinate translation, then passed. The final recorded maximum displacement is `5.1779135800964635e-11` pixels, matching the independent review. All 47 data, metrics, filtering and synthetic correctness tests pass. `git diff --check` reports no whitespace errors. The data README now describes the exact 1e-6-pixel admission bound rather than exact affine equality.

The seven known touching pairs remain in their official supplied partitions:

| Chip A | Split A | Chip B | Split B |
| --- | --- | --- | --- |
| Mekong_1439641 | train | Mekong_1443339 | test |
| Mekong_293769 | validation | Mekong_596495 | train |
| Spain_1167260 | train | Spain_6095801 | test |
| Spain_6095801 | test | Spain_7856615 | train |
| Spain_6537196 | validation | Spain_8104659 | train |
| USA_366607 | validation | USA_67102 | test |
| USA_527077 | test | USA_58086 | train |

This is a **correlated official-subset development benchmark**. It supports no held-out-event, unseen-geography or independent-sample statistical generalization claim. Retaining supplied membership follows the protocol's first-priority rule; no chips were moved or replaced after reading labels. The exact pairs and limitation are saved in `development_data_portability.json` and the pending `configs/development.json`. That configuration binds only the portable data identity: `calibration_frozen` remains false and method choices remain unset.

Additional commands:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m sar_water.data data/development-v1/inventory.csv --output data/development-v1/audit-v3-relative
.\.venv\Scripts\python.exe -m pytest tests/test_data.py tests/test_development_data.py tests/test_metrics.py tests/test_filters.py tests/test_synthetic.py -q --basetemp=outputs/pytest-portable-final
```

The Phase 1 corrections are ready for independent follow-up review. ROI/looks estimation and validation calibration remain unrun.
