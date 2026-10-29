# Phase 2 implementation review

28 October 2026. Reviewed the uncommitted Phase 2 metrics, synthetic generator,
tests, configuration and implementation report against the project guardrails,
README, Phase 2 roadmap, evaluation protocol and implementation lock. This is a
review of authorized synthetic development; the organizer subset remains absent.

## Findings

**Critical: none found. Important: none found.**

**Minor: roadmap overview has stale execution status.** The opening Progress
paragraph in `ROADMAP.md` still says “Phase 1 is next” and “No data-processing or
training phase has been executed,” although the Phase 2 section now records the
completed synthetic baseline. Update the overview to distinguish completed
synthetic Phase 2 development from the still-open actual-data Phase 1 gate.
The detailed Phase 2 evidence and implementation report already make this
distinction correctly.

## Scientific and implementation quality

- Confusion counts use the intersection of independent input/label validity
  masks and exclude `-1` labels. Unsupported target codes are rejected even
  behind a mask; scored predictions must be binary. All counts are retained.
- Pooled water scores derive from summed counts. Empty-water and empty-validity
  cases produce the specified null/zero values. Macro IoU/F1 include the same
  ground-truth-water-positive identities regardless of predictions; the optional
  fixed identity list is checked. Undefined precision and its count are explicit.
  Dry patches remain in pooled counts and have separate false-positive pixels,
  rates and affected-patch fractions.
- ENL uses positive linear power and population variance for a selected ROI.
  Empty/singleton and constant regions return null numeric values with explicit
  statuses. Scaling by the maximum preserves the ratio while avoiding unstable
  squared physical units.
- PSNR requires an explicit finite positive range, respects the scoring mask,
  matches the hand-computed MSE case, and returns positive infinity only for
  identity with an explicit status in the controlled float32 experiment. No real
  noisy SAR reference is used or described as clean ground truth.
- All 12 deterministic 256 x 256 phantoms contain homogeneous regions, sharp
  boundaries, narrow low-power structures and texture within the specified
  bounds. Identity membership is fixed 6/3/3 before corruption. Gamma noise has
  the specified mean/variance, looks and seeds; observations are not clipped.
  Repeated generation supplies identical inputs to future methods. The report
  explicitly discloses reuse of normalized noise fields across phantom identities.
- Configuration keeps real split/calibration freezes false and selected real-data
  values null. Cleanup is disabled for the primary comparison; filter and
  threshold candidates match the lock. No method selection, real-data accuracy,
  GPU training or fresh Colab runtime is fabricated.

## Independent verification

- Targeted command: `.venv/Scripts/python.exe -m pytest -q
  tests/test_metrics.py tests/test_synthetic.py
  --basetemp=.pytest_cache/phase2-review`: **12 passed in 1.00 second**.
- Full command: `.venv/Scripts/python.exe -m pytest -q
  --basetemp=.pytest_cache/phase2-review-full`: **27 passed in 3.79 seconds**.
- Additional direct checks passed for masked invalid predictions, validity-mask
  shape rejection, masked unsupported target rejection, pooled-count arithmetic,
  dry false-positive rates, empty ENL ROIs and no-valid-pixel PSNR.
- Regenerated the raw baseline under ignored `outputs/phase2_review`. Its 72
  unique phantom/looks/seed records are byte-identical to the recorded output.
  Split membership agrees with the configuration. Mean PSNR is
  **4.492541148361972 dB** at L=1 and **10.464388317676455 dB** at L=4,
  matching the implementation report. The reported configuration and CSV
  SHA-256 hashes also match. These are simulated baseline measurements only.

**Verdict:** Phase 2 meets its specification and quality gate. The sole finding
is the minor roadmap overview inconsistency above; no implementation fix is
required. Actual subset provenance, independent labels, real-data splits,
filter validation, trained results and the under-30-minute Colab gate remain
open. No implementation code was changed during this review.
