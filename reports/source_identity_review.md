# Portable source-identity execution gate review

Independent scoped review dated 29 October 2026. Reviewed the changes since `f9f6e56284caed9fed8d5bb7e0c806d40782f8cd` in `data.py`, `train.py`, `evaluate.py`, `calibrate_classical.py`, `evaluate_neural.py`, and the focused regressions; the cross-platform probe; and the provenance-only v3 migration.

**Decision: ACCEPT the portable identity fix and `configs/development-calibrated-v3.json`.** No unresolved critical or important findings remain within this scope. The ordinary resource/source preflight and already-authorized paired training may proceed with the unchanged scientific choices and compute cap. This is an input-integrity/preparation gate, not evidence that training has completed, converged, or fits a fresh Colab budget. No selection was rerun and no GPU job was launched by this reviewer.

## Failure and bounded correction

`cross_platform_conversion_probe.json` records exactly equal decoded dB arrays and SAR validity between the Windows and Linux inputs, using NumPy 2.5.4, but 378 of 524,288 converted float32 power samples differ by one ULP. The maximum relative difference is approximately 1.19e-7. An exact hash of derived power therefore rejects unchanged source data across those platforms. This is a numeric portability failure, not evidence of a changed input file or permission to weaken file identity.

The new `source_float32_vv_vh_validity_v1` digest hashes decoded source samples before dB-to-power arithmetic. Its canonical representation explicitly includes the domain, declared units, shape, `[VV,VH]` band order, little-endian float32 sample bytes, and the SAR-only two-dimensional validity mask as unsigned bytes. Invalid sample payloads are canonicalized to zero. Label validity does not enter this input digest. The original derived-power digest is retained for provenance and duplicate checking.

The exact source digest is preferred when a frozen manifest supplies it. A changed or missing audited source digest cannot fall back to a matching legacy power digest. A legacy manifest without a source digest must still supply and exactly match its original power digest; missing all decoded identity is rejected. Consequently the correction does not silently make old manifests portable or waive their original identity contract.

All four consumers retain mandatory, exact **image and mask file SHA-256 checks before loading**: classical calibration, paired training, classical held-out evaluation, and neural held-out evaluation. The shared decoded-identity check supplements those checks. Source sample normalization does not permit altered GeoTIFF bytes, labels, metadata, or compression to substitute for a frozen source file. The audit's existing shapes, units, georeferencing, labels, and independent mask validation remain in force. Split validation keeps file/power duplicate checks and adds exact source-digest duplicate checks.

## ROI tolerance stays confined to derived numbers

The training loader still uses the frozen effective looks for filtering. It recomputes the looks/ROI diagnostic only to verify its provenance. The changed comparisons allow relative error at most `1e-6`, with absolute tolerance zero, for the derived looks vector and individual ENL `value` fields. They do not recalibrate, average in new data, or replace the frozen numeric values.

Every other ROI-record field must compare exactly, including patch ID, train split, band, coordinates, valid sample count, status, key set, order, and record count. Per-band usable ROI counts also remain exact. The reviewer ran adversarial checks: a 5e-7 relative ENL difference is accepted, a 2e-6 difference is rejected, and changes to each listed identity/count/status field are rejected. Missing, NaN, or infinite ENL values do not match an expected finite value. Portable-source mismatch/missing-identity and legacy-hash bypass attempts are rejected. The regression suite additionally rejects a material 1% ROI ENL change and modified source-file bytes.

## Migration verified independently

The one-off `outputs/migrate_portable_identity.py` creates new versioned paths; it does not invoke calibration, validation search, training, or method selection. It preserves the earlier artifacts. Independent comparisons established:

- All 100 manifest rows retain every old field exactly and add only `image_source_content_sha256` and `image_source_content_hash_domain`.
- All 200 old/new image and mask paths resolve to the same files, and every file still matches its original SHA-256. No source was rewritten, replaced, resampled, or relabeled.
- An independent implementation recomputed all 100 canonical source digests directly from Rasterio source samples and masks; each matched the new manifest.
- The old and new split CSVs are byte-identical, retaining exactly 60 train / 20 validation / 20 test members. New split validation passes without changing membership.
- The v3 configuration differs from accepted v2 only in five provenance fields: `manifest_path`, `splits_path`, `manifest_sha256`, `looks_artifact_path`, and `looks_artifact_sha256`. Every other top-level and real-data field is exactly unchanged.
- The migrated looks artifact differs only in its manifest-hash binding. Its two looks values, all 12 per-band ROI records, usable counts, ROI/split hashes, interpretation, and original pre-validation freeze timestamp are exact. That timestamp describes the original scientific freeze; the separate migration record supplies the new metadata-creation time.
- Training ROI bytes and the selected source membership, units, band order, label provenance, channel, threshold, filter parameters, cleanup rule, normalization/training design, seed, model, and compute limits remain fixed. The v3 configuration still selects Median window 5 and effective looks `[4.859278122453718, 4.020813607183419]`.
- The preserved evidence copies in `reports/source_identity-v3/manifest.csv` and `splits.csv` are byte-identical to the new execution audit. Their relative file paths must be reconstructed at the recorded `data/development-v1/audit-v4-sourceidentity/` depth when moving an execution tree.

The migrated manifest and configuration identify the same scientific experiment with a portable source-identity binding. They do not relabel the already-measured v2 Windows results as a new v3 run. Native dB identity does not promise bitwise-equal derived tensors, checkpoint weights, or metrics across operating systems; the one-ULP conversion difference remains a disclosed numeric fact.

## Fresh tests and actual preparation check

The following completed with **61 passed, 4 deselected in 31.67 seconds**:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_data.py tests/test_neural.py tests/test_calibration.py tests/test_evaluate.py tests/test_neural_evaluation.py -k 'not synthetic_validation and not notebook' --basetemp=outputs/pytest-source-identity-review
```

The scope covers source-domain identity surviving a simulated one-ULP power change, canonical band order and explicit units, retained duplicate detection, fail-closed legacy/source preference, changed source bytes, training-only ROI provenance, material ENL-change rejection, frozen held-out loading, and neural export provenance. Notebook work is a separate review; synthetic parameter selection was excluded from this scoped run.

The reviewer also executed the actual `load_frozen_training_inputs` interface with the v3 configuration and v4 manifest. A file-open guard prohibited every held-out image/mask path. Preparation succeeded with exactly **80 raw and 80 Median-filtered development patches**, **160 development source-file reads**, and **zero held-out source reads**, retaining the frozen looks and all expected input/config hashes. No optimizer update, model training, threshold selection, or final evaluation occurred.

## Accepted evidence identities

| Artifact | SHA-256 |
| --- | --- |
| Parent v2 configuration | `a2e6da8bd81a8a345953d73e943eb2d923409e5797684bd4d3be5fef2f3e445d` |
| Parent v3-relative manifest | `74d00fd2b08e6417e77a102c0cfd5b0bd5c3b1d759ff814b6fabdae4729792cc` |
| New v3 configuration | `3b54e43f217ad80e2c029554289acd483538ecbd09837bcfb9c9b689a653f4af` |
| New v4-sourceidentity manifest | `d840b655f00df68220d5b2ccbaf9eb9c5aa4e785dd0184e05f8dec7646c46786` |
| Unchanged splits | `24963a9951f318aab0cc3d687023ce849fc5c9435ed9fc8cbadced4dc6c2d1b7` |
| Unchanged training ROI CSV | `c5a5c818c2c984d6d561b86fc51872167ea5f3aa005f600bbb0224c28139b533` |
| Migrated looks artifact | `e913ffc80d7edf57f38167bb34448bb39f93447483e02b09df102902002e6233` |

Reviewed source bytes before the corrective commit:

| Source | SHA-256 |
| --- | --- |
| `src/sar_water/data.py` | `e0ef47f8f1834a6420e1b366c46b4a61bb2c9266c84fc4e0ebeb1f33f8709532` |
| `src/sar_water/train.py` | `3b7d6fb308919b1e92e2348f61f34d264ed018833a978ae4633208d6adddad67` |
| `src/sar_water/evaluate.py` | `bbd607eded10e8906a78d323e67fb7846814eadeb71873f7b6e3cd6ed86091e8` |
| `scripts/calibrate_classical.py` | `8edceba52eb27eab64c64d0e3d76cff62f1be8f2e74593da5524d47584583ba8` |
| `scripts/evaluate_neural.py` | `67aa6b72b3f7d9f4d510555bd3baa8a339511009bcf88956287257bdc5646ba3` |

The original calibration v2 artifacts and measured classical result bytes remain preserved. Correlated official-subset limitations, missing organizer data, incomplete paired training, and unverified fresh Colab timing remain unchanged by this acceptance. No new model, method, threshold, ROI, split, or broader search is justified by this portability correction.
