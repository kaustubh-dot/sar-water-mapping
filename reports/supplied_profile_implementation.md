# Supplied source configuration and notebook implementation

29 October 2026. **Implementation verified; independent review and actual
supplied calibration/evaluation remain separate gates.** This report records
code and fixture checks, not measured supplied water scores or a fresh Colab
run. The [accepted data review](supplied_data_review.md) controls the preceding
acquisition/audit/ROI gate.

## Reusable interface

`src/sar_water/supplied_profile.py` exposes:

```python
write_supplied_source_config(
    manifest_path, splits_path, data_root, output_path,
    *, recipe_path=None, selection_path=None,
)
verify_supplied_source_config(source_config_path, manifest_path, splits_path)
```

The writer exclusively creates a metadata-only JSON configuration after the
raster audit. The verifier returns its verified `real_data` provenance. Neither
function opens, decodes, hashes or scores TIFF pixels. Source configurations
accept exactly `schema_version`, `profile` and the reconstructed provenance
fields; filter grids, method choices and training settings cannot be supplied
through this interface.

Verification covers the original source CSV SHA-256, committed ordered
first-100 selection SHA-256, recipe identity and prior training exposure; the
seed-42 event split; split-freeze/selection/download/inventory SHA chains; and
every audited patch's source URI, file SHA-256, local path, manual-label
provenance, units, band order, event and membership. It rejects changed or
mixed sources before calibration SAR/label access. All metadata bindings use
relative POSIX paths.

The provenance explicitly carries 29/40/31 patch counts and proportions,
Mekong/Nigeria/Pakistan training events, India validation, Ghana test, and 22
prior project training exposures distributed 5/9/8. It states that existing
development checkpoints cannot establish unseen-input performance and that
these are internal event partitions rather than official upstream test chips.

## Calibration and one notebook

`scripts/calibrate_classical.py` adds optional `--source-config` and the
matching keyword `source_config_path=None`. It verifies the configuration
before source access, retains its start hash, and verifies the hash and entire
metadata chain again before freezing the experiment. The frozen `real_data`
contains source configuration path/SHA and supplied provenance. Validation
evidence carries `source_config_sha256` separately, preserving the existing
three-entry `input_sha256` contract. Supplied runs start from the unchanged
experiment template; source metadata cannot import development choices.

The existing label-blind pilot prefers distinct training events and fills any
remaining places with sorted training IDs, up to five total. It records the
actual patch count. Filtering, fallback grids, validation selection, cleanup,
training and scoring code are unchanged.

The single notebook defaults to `DATA_SOURCE='supplied-first100'`. It calls the
bounded acquisition CLI into `data/supplied-v1` with run-local evidence and no
default cache override. It records the current run's existing TIFF count
separately from the immutable original acquisition log, uses the acquisition
helper's frozen internal splits, snapshots both supplied ROI files and source
metadata into `RUN_ROOT`, creates a source configuration after audit, passes it
to calibration and verifies its bindings before held-out access. The earlier
`upstream-development` option and generic organizer stop remain available.
The four existing workflow helpers (`checkout_source`,
`freeze_upstream_selection`, `verify_upstream_inputs`, `export_bundle`) are
AST-identical to the pre-change versions.

## Verification evidence

- RED observed for missing supplied source module, supplied notebook default
  wiring and the source-config verifier keyword before implementation.
- `.venv/Scripts/python.exe -m pytest -q tests/test_supplied_profile.py tests/test_calibration.py tests/test_notebook.py --basetemp outputs/pytest-supplied-profile-final`:
  **23 passed in 50.68 seconds**. Checks include exact supplied provenance,
  SHA tampering, rehashed membership/source mixing, forbidden grid metadata,
  rejection before source access, start/end source-config mutation, preserved
  generic calibration, five-patch pilot, notebook source binding, executed
  cached supplied/development access stages and the organizer stop.
- The writer and verifier succeeded against the accepted actual metadata at
  `data/supplied-v1/audit-v1/{manifest,splits}.csv`, writing only an ignored
  implementation-smoke source configuration under `outputs/`. No TIFF was
  accessed by that check.
- Every notebook code cell compiled; preserved workflow helper ASTs matched
  `HEAD`; `git diff --check` passed.

Actual supplied calibration, paired scratch training, held-out evaluation,
full notebook smoke and independent reviews are execution gates owned by their
separate records. Fresh uncached Colab and its under-30-minute claim remain
unverified and deferred. No development result or checkpoint was relabeled.
