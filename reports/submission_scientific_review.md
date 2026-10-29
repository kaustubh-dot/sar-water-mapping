# Submission scientific and evidence review

29 October 2026. Independent bounded review of the current development tree.

**Decision: the preserved development evidence is internally consistent. No new
unresolved P1 or P2 scientific implementation or artifact defect was identified
within this review. Final hackathon acceptance remains open.** The distinct
supplied selection has not been audited and scored as a new experiment, and a
fresh Colab Run All below 30 minutes has not been measured. These are existing
acceptance blockers, distinct from a newly discovered code defect.

## Scope and implementation assessment

Read the project guardrails, README, roadmap, implementation lock, evaluation
protocol, final report, reproduction guide, supplied-selection evidence and
prior execution reviews. Inspected the current data adapter, filtering,
thresholding, confusion/summary metrics, classical selection/evaluation,
compact U-Net, training/checkpoint selection and neural evaluation integration.
No experiment behavior, frozen choice, data or checkpoint was changed.

The inspected paths preserve power-domain multiplicative Lee and ENL,
SAR-only nearest-valid filling, independent SAR/label masks and scored-pixel
intersection, one shared classical numeric threshold, disabled primary cleanup,
separate cleanup ablation, synthetic-reference PSNR, and one fixed
ground-truth-water-positive macro set with separate dry-patch false positives.
Training normalization uses valid raw training pixels. Paired inputs share
normalization, initialization and deterministic crop plans; best checkpoints
use pooled validation IoU with earlier checkpoints retained on ties. Native
neural masks use strict probability above 0.5 and receive no denoising ENL/PSNR.
Frozen configuration/checkpoint identities are checked before held-out file
access. No material discrepancy with the locked contract was found in these
inspected paths.

This review does not repeat prior training, 40 validation forward passes,
classical image filtering, uncached data download or full notebook execution.
It performs fresh saved-artifact arithmetic and identity checks, including a
recount of all saved neural masks against original held-out label TIFFs. It
does not claim that reviewing source proves every possible execution correct.
The coordinator owns the current complete test-suite run.

## Fresh verification

Executed from the repository root:

```powershell
.\.venv\Scripts\python.exe outputs/submission_science_probe.py
```

The final probe exited 0. The ignored script and
`outputs/submission_science_probe.json` retain detailed local evidence.

- Verified SHA-256 and recorded sizes for all 14 classical artifact-index
  entries, and SHA-256 for all seven neural entries. The seven neural
  evaluation source-file hashes still match the measured source identities.
- Independently summed all saved per-patch confusion counts and recomputed
  pooled water IoU/F1/precision/recall for all six headline rows. Recomputed
  per-patch and macro metrics on the same 19 water-positive identifiers and
  the one dry patch, including its false-positive rate. Every method scores
  exactly 4,505,202 pixels; dry valid pixels total 27,394. All values agree
  with the delivery CSVs. The three top-level headline CSV copies are byte
  identical to their versioned artifacts.
- Recomputed pooled scores for all 98 saved calibration candidates and four
  cleanup records. Independent grouping/argmax and runtime tie-break arithmetic
  reproduces common VV fixed -18 dB and Median window 5. This checks the
  saved selection; it is not a new image-based calibration replay.
- Verified all 40 saved native prediction NPZ hashes, loaded each original
  held-out image/mask byte stream with its manifest SHA-256, and independently
  reconstructed SAR and label validity from TIFF masks and values. Exported
  SAR/label/scoring masks, invalid prediction encoding and every confusion
  matrix match. No model forward pass was performed.
- Recomputed all 72 synthetic test PSNRs from recorded MSE with explicit
  range 1.0 and all eight nine-measurement means. Recomputed all 16 ENL
  class/band summary rows from saved ROI values, including counts and
  quartiles. No real noisy image was used as a clean reference.
- Checked both saved training histories: the earliest maximum validation IoU
  occurs at epochs 6 and 8; five stale epochs lead to 11 and 13 executed
  epochs; epoch updates sum to 327 and 387. Initial state hashes match.

The verified pooled headline values are:

| Method | Water IoU | Water F1 |
| --- | ---: | ---: |
| Raw classical | 0.60841455 | 0.75653947 |
| Median 5 | 0.63041193 | 0.77331614 |
| Lee 5 | 0.60697246 | 0.75542360 |
| Log-bilateral | 0.63037376 | 0.77328742 |
| Raw U-Net | 0.58546032 | 0.73853670 |
| Median-5 U-Net | 0.53463250 | 0.69675639 |

README/report rounding agrees. Lower Lee IoU and the negative Median-fed
U-Net result remain visible; neither is grounds for test-based retuning.

## Public artifact and provenance check

A fresh connected GitHub API read confirms the
[development prerelease](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1)
is non-draft, targets measured source
`61b09f9bfa61114d83bd7be19eba3de67d5621db`, and contains the uploaded
3,648,324-byte checkpoint ZIP with digest
`b70dc5117a21ecac5b3b0e2ad9fc06f960a727370c81892089ac27b894100238`.
Compact API evidence is in ignored `outputs/submission_science_release.json`.

Independently rehashed the retained earlier public download under
`outputs/public-checkpoint-download`, inspected its six members, and verified
all four internal SHA-256 entries. Both weights retain their recorded original
hashes; public training JSON is byte identical to the committed public record.
The bundle has weights, metadata, original environment, checksums and README,
with no raw TIFFs or prediction arrays. This review verifies current metadata
plus the retained downloaded bytes; it did not make a second binary download.
The guide documents frozen restoration and checkpoint evaluation separately
from new training. Saved native outputs remain local ignored evidence and can
be regenerated with that procedure; the public release is a checkpoint bundle.

## Readiness limits and required next evidence

The supplied first-100 selection is a distinct dataset definition. Independently
confirmed 100 unique IDs, its committed selection hash, event counts and exactly
22 overlaps with the earlier development training partition. Existing outputs
cannot be relabeled as supplied-set results, and existing checkpoints cannot
establish unseen-input performance on those 22 IDs. The current README and
roadmap preserve that distinction. The next experiment gate is the supplied-set
integrity/validity/provenance/spatial audit followed by frozen defensible
internal splits, training-only statistics, validation-only calibration and a
separately versioned held-out evaluation.

The 91.78-second cached Linux notebook evidence does not measure a fresh Colab
installation or uncached access. Retain a fresh complete classical Run All,
including setup/access and final archive/checksum, below 30 minutes. If enabled
training must be inside that budget, measure its separate full profile; the
122.06-second remote training and 6.85-second checkpoint-evaluation subtotal
cannot substitute for that evidence.

The 60/20/20 development split contains touching chips and shared events; one
seed, few ENL ROIs and correlated geography limit conclusions. Current claims
correctly describe observed surface water and do not identify new flooding
separately from permanent water. Final acceptance/tagging remains unsupported
until the required supplied-set and fresh-Colab evidence exists.
