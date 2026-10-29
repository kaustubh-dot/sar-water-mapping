# Classical calibration execution gate review

Independent review dated 29 October 2026. Scope: `scripts/calibrate_classical.py`, the bounded-cache changes in `src/sar_water/benchmark.py`, their focused tests, the training ROI CSV, `.gitattributes`, `configs/development-calibrated-v2.json`, and `reports/classical_calibration-v2/`.

**Decision: ACCEPT v2 for bounded upstream-development training and subsequent frozen evaluation.** There are no unresolved critical or important calibration findings. Version 1 is rejected and retained only as superseded evidence. This decision does not certify an organizer-subset result, remote training, final held-out scores, or a fresh Colab run.

## Findings resolved before acceptance

**P2: v1 did not bind one stable training-ROI byte identity.** Its embedded looks artifact records ROI SHA-256 `c5a5c818c2c984d6d561b86fc51872167ea5f3aa005f600bbb0224c28139b533`, while its result/configuration records `11d860349a8c9bdeacb3921d449e70d27073848365ece792a6e6ea9ad6d220cd`. Independently converting the restored ROI file to CRLF produces exactly the latter hash: the mismatch is newline conversion, not different ROI coordinates. Nevertheless, v1 is invalid evidence for a frozen run. Its README explicitly prohibits training/final evaluation from v1. The preserved v2 rerun consistently records the restored ROI hash in the starting inputs, looks artifact, result, and configuration. The calibration runner now hashes manifest, splits, and ROI before loading and verifies all three again before creating the configuration; a mutation-during-calibration regression verifies that a changed ROI blocks configuration freeze.

**P2: Git normalization could change byte-hashed source provenance.** Initially `.gitattributes` protected the frozen ROI/configuration/results but omitted the six recorded source files. With local `core.autocrlf=true`, `git hash-object` and `git hash-object --no-filters` differed for the calibration script and `filters.py`. This reviewer added `-text` only for the six exact source paths recorded by v2. Repeating the comparison produced equal raw and filtered Git blob identities for all six paths. `git check-attr text` reports `unset` for these sources and the frozen artifacts. No source or frozen v2 artifact bytes were edited. This protects the existing measured bytes rather than rewriting their recorded hashes.

## Fresh verification

The following completed with **37 passed in 5.72 seconds**:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_calibration.py tests/test_benchmark.py tests/test_filters.py tests/test_segment.py tests/test_metrics.py --basetemp=outputs/pytest-calibration-review
```

Coverage includes exact scientific conversions/filters/masks/metrics, validation-only membership, the 98-row locked grid, common numeric threshold selection, fixed water-positive macro membership, separate dry-patch false positives, exclusive output paths, portable hashed configuration, changed source rejection, changing-input freeze rejection, and the per-setting cache limit. The calibration fixture deliberately supplies nonexistent held-out images and masks; successful calibration establishes that those files are unnecessary and not opened.

A separate actual-data verification recomputed every manifest/split/ROI/looks/configuration SHA-256 and all six recorded source hashes. All matched. It recomputed selection from the saved 98 rows and verified the selected configuration and `candidates.csv` agree exactly. The saved opened-source list contains 20 validation and five training sources; none belongs to test. All six looks ROIs belong to three training patches, are 32 x 32, and have documented raw-image suitability. The recorded training-looks freeze precedes validation access.

An independent read-only rerun then loaded the three training ROI pairs and all 20 validation pairs, verifying their original image/mask and decoded-SAR hashes. A guard rejected any attempted open of a held-out source path. It exactly reproduced the six per-band training ROI records and medians, the raw-validation fallback table, all **98 candidate scientific records**, and all **four cleanup-ablation scientific records**; only measured timing fields were excluded from equality. It reproduced the selected common strategy and filtered input. No held-out source was opened and no GPU or final-test evaluation was launched.

The validation cache retains one filter setting at a time, then releases it before computing the next setting. Its recorded 41,943,040 bytes fit the 100,000,000-byte cache cap. The cap describes retained filter outputs, separately from source arrays and filter workspaces. Cleanup refiltering/scoring time is reported separately, and primary candidate timings contain no cleanup work.

## Accepted frozen identities

| Artifact | SHA-256 |
| --- | --- |
| Manifest, `data/development-v1/audit-v3-relative/manifest.csv` | `74d00fd2b08e6417e77a102c0cfd5b0bd5c3b1d759ff814b6fabdae4729792cc` |
| Splits, `data/development-v1/audit-v3-relative/splits.csv` | `24963a9951f318aab0cc3d687023ce849fc5c9435ed9fc8cbadced4dc6c2d1b7` |
| `reports/classical_training_rois.csv` | `c5a5c818c2c984d6d561b86fc51872167ea5f3aa005f600bbb0224c28139b533` |
| `reports/classical_calibration-v2/training_looks.json` | `b22e57a3a8b322cfc9021470f8f24636aa859cb6bf47301ccfce740bb3d1dbcb` |
| `reports/classical_calibration-v2/validation.json` | `f4a69e29aa6e01af816c4c28e2063bf75db89359a070def18fca502dffb1a3a1` |
| `reports/classical_calibration-v2/candidates.csv` | `f5307e75a6d9df9f55c4885ac7e63fd3cc84662717d4ba676fe2fd2769f8ab38` |
| `configs/development-calibrated-v2.json` | `a2e6da8bd81a8a345953d73e943eb2d923409e5797684bd4d3be5fef2f3e445d` |

Recorded source hashes cover `scripts/calibrate_classical.py` and `src/sar_water/{benchmark,data,filters,metrics,segment}.py`. Each matches the reviewed working bytes. The recorded base commit is `df3e73e43edad655cfe1800f4144b6ca5172110c`; the source hashes identify the then-uncommitted calibration changes.

The follow-up index-byte check initially found the previously tracked normalized `filters.py` blob still differed from the v2 working bytes, despite the new attribute. Restaging that exact file with `git add --renormalize -- src/sar_water/filters.py` applied `-text` without editing the source. A fresh `git show :<path>` SHA-256 check then confirmed all six staged source blobs exactly match the v2 recorded hashes. The staged ROI CSVs, configuration, all three v2 outputs, and `.gitattributes` also match their working bytes. Preserve this source-byte correction in the commit used for remote transfer.

## Accepted choices and limits

The shared policy is **VV, fixed threshold -18 dB, water below threshold, cleanup disabled**. Selected settings are raw identity, Median window 5, multiplicative Lee window 5, and log-bilateral window 5 / spatial sigma 2 / color sigma 3 dB. Lee effective looks are **VV 4.859278122453718, VH 4.020813607183419**, each from six finite nonconstant training ROIs. They are effective estimates, not independently established physical looks. The Otsu constant-patch fallbacks are VV -18 dB and VH -24 dB, calibrated on raw validation only.

The saved validation IoUs are raw 0.6499978566, Median 0.6816115343, Lee 0.6661330304, and log-bilateral 0.6782033574. The common strategy maximizes the mean of the four selected-family pooled validation IoUs, 0.6689864447. Median window 5 is the selected filtered neural input because it has the highest pooled validation water IoU among filters under that common policy. This is a validation choice; it is not a held-out improvement claim. All methods use the same 17 ground-truth-water-positive macro patches; the three dry validation patches are reported separately. Cleanup remains an independent raw/Median off/on ablation.

The run records 78.03 seconds of local CPU calibration elapsed time and explicitly labels it as **not fresh Colab**. MIDAL was not piloted/admitted and has no compatibility or runtime claim. No additional model or method was introduced.

The configuration retains the accepted upstream development provenance limitations: 60/20/20 official membership, shared events and seven cross-partition touching pairs. These support a correlated official-subset development benchmark, not independent-geography or unseen-event generalization. Organizer data, final held-out evaluation, remote paired training, and complete fresh Colab timing remain separate execution gates. Preserve v2 bytes; any later scientific change requires a new versioned calibration run.
