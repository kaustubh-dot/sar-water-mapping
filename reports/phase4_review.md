# Phase 4 implementation review

28 October 2026. Reviewed the uncommitted segmentation and benchmark modules,
their focused tests, `scripts/phase4_fixture.py`, the saved synthetic validation
output, configuration, implementation evidence and Phase 4 roadmap against
`AGENTS.md`, the README, [implementation lock](../docs/IMPLEMENTATION_LOCK.md)
and [evaluation protocol](../docs/EVALUATION_PROTOCOL.md). This covers the
authorized synthetic development path while the organizer subset is absent.
No implementation code was changed during review.

## Findings

**Critical: none found. Important: none found. Minor: none found in this scope.**

## Specification and scientific quality

- Thresholding uses strict `dB < threshold` water classification, preserving
  threshold equality as land and input-invalid locations as `-1`. Otsu uses
  only valid finite values from the selected band, with a documented 256-bin
  histogram and deterministic first-maximum convention. Constant patches
  require an explicit finite fallback, record its actual value and status, and
  have no hidden threshold default. All-invalid segmentation returns an invalid
  mask, null threshold and explicit status. The fixture records the unimodal
  all-land failure rather than claiming Otsu establishes water classes.
- Disk-pair evaluation delegates to the existing audited GeoTIFF adapter,
  filters linear power and thresholds the selected VV/VH band in dB. Filtering
  and threshold selection do not use labels. Scoring intersects independent
  SAR and label validity. The disk fixture verifies native mask generation and
  confusion counts from independently serialized image and label rasters.
  The returned audit preserves the existing manual versus weak/unknown claim
  distinction; synthetic fixture labels are not represented as real manual
  ground truth.
- Validation search refuses missing, training or test membership for any
  supplied patch. It evaluates exactly seven bounded filter configurations
  against fourteen shared channel/rule candidates: two per-band Otsu rules
  and twelve fixed thresholds. The 98-row table retains both bands, parameters,
  pooled/macro/dry-patch summaries, aggregate confusion counts, timing, and each
  patch's actual threshold/fallback status. Cached filtering uses SAR alone.
- For each common candidate, each family chooses parameters by pooled water
  IoU; the common rule maximizes the mean of the four family IoUs. Exact ties
  use measured compute time. All four primary rows share the same channel,
  strategy and numeric fixed threshold when fixed thresholding is chosen.
  The selected filtered input is the best actual filter under that common
  rule, using pooled IoU and time rather than ENL or test performance.
  Undefined pooled IoU blocks selection explicitly.
- Primary cleanup is disabled. The separate four-row ablation compares
  unchanged raw and the selected filter with cleanup off/on. Cleanup removes
  only 8-connected water components smaller than 16 pixels, preserves invalid
  barriers and fills no holes. Its off rows reproduce the corresponding
  primary summaries. All comparisons use the same ground-truth-water-positive
  macro patch set and separate dry false-positive reporting.
- Timings are correctly scoped: primary candidate rows include one cached
  filter invocation plus that row's segmentation/scoring, excluding disk I/O;
  cleanup rows explicitly time segmentation/scoring on cached filtered data.
  These are local development timings, not a fresh Colab budget measurement.
- The integration script uses only fixed synthetic validation identities
  06/07/08, known Gamma looks and independent known-reference class masks.
  Its fallback thresholds are explicitly synthetic development inputs. Output
  remains `pending_real_calibration`; actual-data configuration choices remain
  null and no test identities or real scores are introduced.

## Independent verification

- `.venv/Scripts/python.exe -m pytest tests/test_segment.py
  tests/test_benchmark.py -q --basetemp=.pytest_cache/review-phase4`:
  **9 passed in 1.49 seconds**.
- `.venv/Scripts/python.exe -m pytest -q
  --basetemp=.pytest_cache/review-phase4-full`:
  **50 passed in 3.91 seconds**.
- `.venv/Scripts/python.exe scripts/phase4_fixture.py`: exit 0,
  **98 validation rows, four primary rows and four cleanup rows** in
  **1.4044997000019066 seconds**, with `simulated_backscatter_only` source and
  `pending_real_calibration` status.
- Independently reconstructed all candidate groups, best family settings,
  common-rule ranking and selected filter from the saved output; all matched.
  Checked unique bounded candidate keys, validation-only patch identities,
  fixed macro identities and cleanup-off equality to primary rows.
- Additional direct checks passed for 25 Otsu histograms against explicit
  two-class variance calculations; label-change invariance of thresholds and
  predictions; all-invalid benchmark outputs and zero confusion counts for
  every family; non-validation membership refusal; and refusal of cleanup
  candidates or undefined pooled IoU during primary selection.

**Verdict:** the Phase 4 implementation and synthetic evidence meet the locked
specification and quality expectations. No fix is required. This review does
not close the real-data Phase 1 audit, remaining Phase 3 admission/looks/runtime
gates, or Phase 4 actual calibration and real-patch exit gate. Actual independent
labels, frozen real splits and training-only looks, real validation selection,
configuration freeze, final test scoring and fresh Colab timing remain unrun.
