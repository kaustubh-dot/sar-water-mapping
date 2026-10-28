# Local data and the Phase 1 audit

The organizer archive is absent. No real-data manifest or frozen split exists yet.
Keep raw files, archives and contact-sheet images outside Git. The project's MIT
license does not change dataset terms. Downloading the entire dataset is unnecessary.

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
external overlap audit before a no-overlap claim. Matching input/mask CRS and
affine transforms are required; missing georeferencing is recorded. No reprojection
or resampling is silently performed. Unknown label codes (including custom nodata)
are rejected until a separately documented adapter is approved.

SAR metadata/finite validity and label validity are independent. Both input bands
must be valid for a pixel to enter the shared input mask. Valid `0 dB` becomes
power 1; metadata-declared nodata still takes precedence. Labels must be -1/0/1.
Scoring uses both validity masks; label validity never controls SAR filling.
Nearest-valid filling uses SciPy's deterministic Euclidean distance-transform
indices, rejects all-invalid input, and leaves restoration of the original mask
to the downstream filter. Large missing regions remain an imputation limitation.

Canonical decoded-power hashes supplement file SHA-256 to catch differently
compressed copies. They do not prove absence of near duplicates, shifted crops,
or overlap where spatial metadata is absent. Keep those limitations in the report.

Tests: `python -m pytest -q --basetemp=outputs/pytest-run` (create `outputs/`
first). All test rasters are generated temporary scientific fixtures, not dataset
artifacts or benchmark results.
