# Local data and the Phase 1 audit

The supplied acquisition recipe selects the first 100 ordered rows of the
official hand-labeled training CSV. Its [exact selection](../reports/supplied_subset_recipe.md),
100-pair raster audit and internal event split are accepted in the
[data review](../reports/supplied_data_review.md). The existing seed-42 rule
assigns Mekong/Nigeria/Pakistan to train (29), India to validation (40) and Ghana
to test (31), before tuning. No cross-partition overlap or touching chips was
found. An earlier, distinct 100-pair development substitute has frozen official
60/20/20 membership; see the [development audit](../reports/development_data_audit.md).
Do not treat those development results or splits as the supplied-set experiment.
Keep raw files, archives and contact-sheet images outside Git. The project's MIT
license does not change dataset terms. Downloading the entire dataset is unnecessary.

Exactly 22 supplied IDs were previously used for project training: five current
train, nine validation and eight test IDs. Preserve that exposure disclosure;
these internal event holdouts are not a pristine blind test. `Ghana_26376` has
zero scored pixels, remains in test and must receive an explicit no-score
status. Four training ROIs and five test-only ENL rectangles are frozen in
separate CSVs; the test rectangles support visually homogeneous land diagnostics
only and never enter looks estimation or normalization.
`supplied_enl_05` in `Ghana_168875` has valid SAR throughout but no valid label
pixels; its land tag is visual interpretation. The other four regions are
fully manual-label land. All five remain in the shared SAR-only ENL diagnostic;
none is dropped or backfilled after scoring.

## Supplied-first100 acquisition and audit

The [single notebook](../notebooks/01_sar_water_mapping.ipynb) now defaults to
`DATA_SOURCE='supplied-first100'`. Equivalent source acquisition and audit
commands, from the repository root, are:

```text
python scripts/prepare_supplied_data.py --data-root data/supplied-v1 --output outputs/supplied-acquisition-reproduction-v1
python -m sar_water.data data/supplied-v1/inventory.csv --splits data/supplied-v1/splits.csv --output data/supplied-v1/audit-v1 --contact-sheet
```

The acquisition helper verifies the pinned source CSV and exact ordered
selection, freezes event membership before object access, requests only the
200 selected generation-pinned objects, verifies size/MD5/SHA-256 and writes
an immutable inventory. It does not perform the raster audit. It takes no cache
override by default; optional `--cache-root` is read only and verifies matching
object generation, size and MD5 before copying. Its completion log describes
the original acquisition, so the notebook also records the current run's
existing TIFF count. Use a new audit directory when files already exist.

After the raster audit, create or verify the metadata-only source configuration
with `sar_water.supplied_profile`. It binds every supplied ID, source object,
event, split and input hash before source-aware calibration. The
[reproduction guide](../docs/REPRODUCING.md) gives exact writer, calibration,
scratch-training and evaluation commands, plus restoration of the accepted
metadata bytes. The [profile review](../reports/supplied_profile_review.md)
accepts that wiring; the [actual calibration review](../reports/supplied_calibration_review.md)
also accepts the frozen validation choices. The [scratch training pair](../reports/supplied_training_review.md)
is independently accepted. Frozen held-out measurements are recorded in the
[classical table](../reports/supplied_classical-v1/results_real.csv) and
[neural table](../reports/supplied_neural-v1/results_neural.csv), accepted by
the [independent result review](../reports/supplied_results_review.md). All methods use the same 4,940,307 scored pixels,
15 water-positive macro members, 15 dry patches and one no-score member.
The [cached supplied notebook smoke](../reports/supplied_notebook_smoke_summary.json)
and its [independent review](../reports/supplied_notebook_review.md) are accepted,
closing S1. Its 123.04-second run used 200 cached TIFFs, an existing clean clone
and preinstalled kernel prerequisites; initial clone/cache preparation were
outside the clock. The exact source pin is
`9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`. Fresh uncached Colab remains unverified.
Fresh uncached Colab is deferred.

## Generic inventory contract

Install in an isolated environment: `python -m pip install -e ".[geo,audit,test]"`.
The base package uses NumPy/SciPy; GeoTIFF loading requires the `geo` extra and
the optional contact sheet requires `audit`. Versions remain compatibility ranges
until the fresh Colab gate; they are not a claim of Colab compatibility.

Create a local inventory CSV with one image and one mask row per identifier:

```csv
patch_id,kind,path,source,units,band_order,label_source,event_id,scene_id,spatial_group,source_patch_id,split
chip1,image,raw/chip1_sar.tif,organizer,db,"VV,VH",,event1,scene1,,chip1,train
chip1,mask,raw/chip1_mask.tif,organizer,,,manual,event1,scene1,,chip1,train
```

This is a schema example, not a supplied patch or complete usable inventory.
Paths resolve relative to the inventory. Identifiers are explicit and paired
independently of row order; filenames are never used to guess IDs. Use `db` or
`linear_power`, and `VV,VH` or `VH,VV`. Source/provenance must be declared: use
`manual` only with evidence of independent manual annotation; otherwise use
`weak`, `otsu`, or `unknown`. Unknown/weak labels permit agreement claims only.
Record archive source, hash and metadata evidence in the audit report separately.

After auditing actual source metadata, run:

```powershell
sar-water-audit data/inventory.csv --output data/audit-v1 --contact-sheet
```

From an uninstalled checkout, set `PYTHONPATH=src` in your shell and run
`python -m sar_water.data` with the same arguments. The command validates every
real GeoTIFF before saving anything. It writes `manifest.csv` and `splits.csv`
into the selected directory, refuses to replace either frozen file, and can
produce a training-only contact sheet (up to five images; VV/VH, histogram,
labels). No labels from validation/test are plotted by this option. Manually
inspect representative development patches; automatic plotting does not complete
that gate. Use a new output directory for an explicitly documented new data version.

New manifests store `image_path` and `mask_path` as POSIX-style relative paths
from the manifest directory. Preserve the relative dataset-tree layout when
copying to Linux, a remote GPU or Colab. `sar_water.data.read_manifest(path)`
resolves these paths against that directory before passing rows to `audit_pair`.
The original absolute-path audit remains untouched; the portable development
version is `data/development-v1/audit-v3-relative/`. Its source/decoded hashes and
official membership match the original audit. Older absolute manifests remain
readable on their original platform, but are not portable across machines.

Use `--splits organizer_splits.csv` for a two-column `patch_id,split` CSV
(`train`, `validation`, `test`). It must cover every patch exactly once and retain
all three partitions. Alternatively fill the inventory's `split` field. Organizer
membership takes precedence; provide upstream official membership explicitly when
identified and usable. The tool does not fetch or infer official upstream splits.

Without supplied membership, seed 42 assigns entire event groups, then scenes,
then explicit `spatial_group` values, requiring at least three usable groups.
The generated-split API rejects any other seed; frozen generated manifests record
`split_seed=42`. Externally supplied membership records
`split_seed=not_applicable`, since no random assignment was performed.
Approximately 60/20/20 **groups** are assigned; patch counts can differ. Group
constraints take precedence over proportions. Automatic separated spatial-block
selection is intentionally unsupported: supply defensible separated block groups
or membership when only one event/scene is available. Keep neighboring crops in
the same explicit spatial group; bounding-box checks alone cannot identify all
neighbor relationships. Only if spatial/event/scene metadata is absent may the
tool use the disclosed patch-level subset-only fallback.

When requested, the contact sheet is rendered in memory before either CSV is
frozen. A missing plotting dependency or rendering failure therefore permits
retrying the same command after correction. Existing audit files still cannot
be overwritten. Filesystem failures while writing artifacts require inspection
of any partial output and an explicitly chosen new audit directory.

Cross-partition identical file/decoded-image hashes, source IDs, explicit spatial
groups and intersecting same-CRS bounding boxes are rejected. Bounding-box overlap
is conservative for rotated rasters; different CRS pairs require an explicit
external overlap audit before a no-overlap claim. Input/mask CRS must match;
affine transforms may differ only when the largest displacement at all four
raster corners is at most `1e-6` image pixels. This admits serialization roundoff
while rejecting meaningful subpixel shifts, scale, shear or rotation errors.
Both transforms and the maximum pixel displacement are saved. Missing
georeferencing is recorded. No reprojection or resampling is performed.
Unknown label codes (including custom nodata)
are rejected until a separately documented adapter is approved.

SAR metadata/finite validity and label validity are independent. Both input bands
must be valid for a pixel to enter the shared input mask. Valid `0 dB` becomes
power 1; metadata-declared nodata still takes precedence. Labels must be -1/0/1.
Scoring uses both validity masks; label validity never controls SAR filling.
Nearest-valid filling uses SciPy's deterministic Euclidean distance-transform
indices, rejects all-invalid input, and leaves restoration of the original mask
to the downstream filter. Large missing regions remain an imputation limitation.

Exact file SHA-256 checks remain mandatory. New audits also record
`image_source_content_sha256` in the versioned
`source_float32_vv_vh_validity_v1` domain: decoded source samples in declared
units, canonical VV/VH band order, little-endian float32, invalid values replaced
by zero, and the original SAR-validity mask. This avoids platform-dependent
transcendental rounding in dB-to-power conversion. The legacy decoded-power hash
is retained for historical audits and duplicate checks; manifests without the
new digest retain their original exact legacy check. Neither digest proves
absence of near duplicates, shifted crops or unrecorded spatial overlap.

Tests: `python -m pytest -q --basetemp=outputs/pytest-run` (create `outputs/`
first). All test rasters are generated temporary scientific fixtures, not dataset
artifacts or benchmark results.
