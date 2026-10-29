# Classical development notebook completion

29 October 2026. This is implementation and local verification evidence for
`notebooks/01_sar_water_mapping.ipynb`. It does not certify a fresh Colab Run all,
the organizer subset, or neural training inside the Colab budget.

## Completed implementation

The single notebook now defaults to the already frozen 100 upstream manual
SAR/mask pairs, preserving their official 60/20/20 membership. It copies the
committed selection before invoking the bounded downloader, checks the three
official list hashes and selected membership, and rejects changed cached
selections, weak-label substitutions, duplicate/missing inventory rows and
changed paths, units, band order or split membership. It passes an explicit
verified split CSV to the audit; the audit writes portable relative paths.

Training looks use the recorded `reports/classical_training_rois.csv`.
Evaluation-only ENL uses the separately preselected
`reports/heldout_enl_rois.csv`. Both files are snapshotted into the run bundle
before calibration, checked against audited train/test membership, and hashed.
The notebook calls the existing reviewed `scripts/calibrate_classical.py`,
without duplicating threshold selection or rewriting any frozen output. Before
held-out evaluation it checks the manifest, split, training-ROI, looks-artifact
and validation/config bindings consumed by the paired training interface.

`inputs/data_provenance.json` and the final timing sidecar explicitly identify
upstream development data, the official source-list/selection identities, and
the known correlation limitation: events span partitions and seven chip pairs
touch across partitions. Fresh audit paths change manifest bytes, so this
source provenance is retained separately rather than injected into a frozen
calibration config. This is no held-out-event or unseen-geography claim.

Timing records separate checkout, installation, download/object verification,
scientific checks, audit, ROI/validation calibration, real/synthetic evaluation
and exports, table/figure display, and final ZIP/checksum work. Download time is
a substage of documented data access; those values are explicitly nonadditive.
The downloader runs with the run directory as its working directory so its
actual per-object download log is bundled and previous source reports remain
untouched. The existing tested checkout and authoritative post-archive timing
helpers retain their behavior. No neural execution was added.

The organizer override remains explicit. It requires its own inventory,
training ROIs and a source config identifying `organizer_subset=true`; it can
audit those inputs. It stops before calibration/scoring because the current
calibrator records upstream-specific source status. A reviewed explicit
organizer source-config interface is still required for that full profile.
The notebook never substitutes the upstream ROIs or claims an organizer result.

## Verification

- Six notebook regressions execute the actual guards, including the actual
  downloader against 200 isolated cached fixture objects. They cover changed
  cached selection, official membership/list hashes, independent manual labels,
  exact calibration inputs/config identity, and download-log packaging without
  overwriting prior source reports. All six passed after observing the new
  checks fail before implementation (the packaging check also failed when its
  working-directory fix was removed).
- The final clean combined notebook/evaluation/calibration/development-data run
  passed **22 tests in 19.41 s**. This includes
  the unchanged checkout and final-archive timing checks. The existing Git
  clone fixture required execution outside the Windows sandbox after MSYS
  named-object creation was denied inside it.
- The real cached upstream access cell executed locally, verifying all 100
  pairs/200 files, producing a 100-row explicit membership CSV and bundled
  download log. This used existing cached objects and is not a measured fresh
  download or Colab Run all. The guard also accepted the reviewed v2 calibration
  with its existing manifest/split/ROI/looks/config hashes unchanged.
- All ten executable cells parse as Python. Outputs and execution counts are
  empty; there is still exactly one notebook.
- An intermediate combined run overlapped active conversion-identity edits elsewhere
  in the shared checkout: **18 passed, four calibration imports failed** because
  `calibrate_classical.py` expected `verify_decoded_image_identity` while the
  process had already imported the earlier data module. The final clean rerun
  above passed after that shared edit was available.

## Actual execution gates still open

Publish the reviewed notebook source, choose its exact source commit, execute
Run all in a fresh compatible Colab runtime with no cached data, and retain the
result ZIP plus its authoritative sibling timing sidecar. Record actual CPU,
memory/runtime conditions and any upload/mount work performed before the first
cell. Inspect the exported results and aligned diagnostics. Only that run can
establish complete classical execution below 30 minutes. This work does not
close the organizer-data delivery gate or reproduce remote neural training.
