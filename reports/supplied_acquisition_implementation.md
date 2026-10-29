# Supplied-set acquisition implementation

29 October 2026. This implements acquisition for the already frozen supplied
definition. It does not establish a successful real download, raster audit,
calibration, training, evaluation or fresh Colab run. Those execution records
must be retained separately. Existing development artifacts are preserved.

The CLI verifies the original 13,574-byte, 252-row upstream training CSV against
SHA-256 `57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
It also requires the exact ordered [selection](supplied_subset_selection.csv)
SHA-256 `9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2`,
checks every first-100 image/mask pair and its recipe position, and reconciles
the 22 prior training identifiers with the [recipe](supplied_subset_recipe.json).
It does not select IDs using imagery, labels or prior exposure.

Before accessing object metadata or any image/label bytes, the implementation
calls the existing `create_splits(..., seed=42)` on identifier/event metadata
and writes exclusive `split_freeze.json` and `splits.csv` artifacts. The event
policy gives 29 train patches (Mekong, Nigeria, Pakistan), 40 validation patches
(India), and 31 test patches (Ghana). Prior development-training exposure is
5/9/8 respectively. All 100 retain `upstream_split=train`; their operative
internal `split` is separate. These are internal event partitions, not official
upstream test membership. The existing public
[split freeze](supplied_evaluation_splits-v1.csv) has the same sorted mapping
and SHA-256 `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`.

## Execute acquisition

From the repository root:

```powershell
python scripts/prepare_supplied_data.py --data-root data/supplied-v1 --output reports/supplied_acquisition-v1 --source-csv data/development-v1/flood_train_data.csv --cache-root data/development-v1
```

`--source-csv` is optional: without it, the public source CSV is fetched and its
exact bytes checked. `--cache-root` is optional: omit it for fresh acquisition.
Both the dataset and evidence paths must be new/empty or belong to a compatible
earlier invocation of this CLI. All writes are exclusive; existing bytes must
match exactly. Complete repeats reverify all 200 files and their local SHA-256s,
reuse frozen source/object metadata without network access, and leave artifact
contents and modification times unchanged. A failed download can resume from
valid files without replacing them. Corrupt existing or cached files fail
closed instead of being silently repaired.

Only the 200 exact selected objects are requested. Each object's GCS generation,
size and MD5 are frozen before TIFF fetching; payload requests explicitly use
the recorded generation. Four workers are used for metadata and objects, with
an aggregate selected-size cap of 500,000,000 bytes. HTTP reads are bounded by
the expected size plus one detection byte. Each object is length/MD5 checked,
assigned a local SHA-256 and atomically published from a temporary file.
Optional cache copies require matching pinned GCS metadata and identical
length/MD5 checks. Cache files are read only; origin counts distinguish cache,
download and previously acquired destination bytes. This CLI uses a dedicated
bounded fetcher because the older development helper reads unbounded responses.

## Outputs and handoff

`data/supplied-v1` contains the original source CSV, exact supplied selection,
`split_freeze.json`, operative `splits.csv`, pinned `selection.json`, long-form
`inventory.csv`, per-file `download.json`, and the 200 TIFFs. All paths inside
the inventory/download record are relative. The evidence directory contains
the split freeze, split CSV, selection metadata and byte-integrity result;
TIFFs remain under the ignored data directory. No existing development path or
report is modified.

The generic audit loads all 100 pairs and their operative split from the new
inventory. Run it separately after byte acquisition:

```powershell
sar-water-audit data/supplied-v1/inventory.csv --splits data/supplied-v1/splits.csv --output data/supplied-v1/audit-v1 --contact-sheet
```

For the later source-aware calibrator, the dataset metadata path is
`data/supplied-v1/selection.json`, the audited manifest is
`data/supplied-v1/audit-v1/manifest.csv`, and the operative split path is
`data/supplied-v1/splits.csv`. Hash these new artifacts and create new supplied
configuration/results paths; no old calibration is transferred by acquisition.
The separate raster audit must check native shape, independent validity,
georeferencing, label provenance, duplicates and cross-partition overlaps.
The byte-integrity status explicitly leaves raster audit, calibration,
training and fresh Colab verification false.

## Verification

Tests were written and observed failing before implementation. Focused offline
checks passed: `python -m pytest -q tests/test_supplied_data.py` — **7 passed**.
They exercise exact CSV hashes/order/exposure, split freeze before object
requests, event counts and audit-compatible inventory, verified cache reuse,
corrupt cache/download/destination rejection, the 500 MB cap, unrelated-path
protection, and repeat verification with no overwrite/network access.
The compressed source-CSV test fixture is upstream dataset metadata and retains
its original terms; original project licensing does not relicense it.

Source: [official upstream training CSV](https://storage.googleapis.com/sen1floods11/v1.1/splits/flood_handlabeled/flood_train_data.csv).
