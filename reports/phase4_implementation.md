# Phase 4 implementation evidence

Date: 28 October 2026. All evidence here uses artificial arrays or known
simulated backscatter. The organizer subset is unavailable. No real channel,
threshold, filter settings, looks or calibration has been selected/frozen.

`src/sar_water/segment.py` implements strict low-backscatter (`dB < threshold`)
water masks, per-patch valid-only 256-bin Otsu, and an explicitly supplied
finite fixed-threshold fallback for constant patches. All-invalid segmentation
returns an invalid mask and null threshold. Fallback status and actual per-patch
thresholds are retained. Otsu can divide a unimodal all-land histogram into
artificial water and land; the fixture ramp demonstrates that failure. A constant
patch cannot provide histogram separation, hence the recorded calibrated-fixed
fallback requirement. Synthetic fallback values are development inputs only.

`src/sar_water/benchmark.py` provides `benchmark_pair(pair, **settings)` for
audited GeoTIFF pair -> power filtering -> native water mask -> confusion counts.
Filtering uses SAR validity alone; scoring intersects independent SAR and label
validity. The disk test uses a generated georeferenced two-band GeoTIFF and an
independent synthetic label raster, including an invalid label.

`validation_search` rejects any supplied patch whose explicit membership is not
validation, filters once per setting/patch, and evaluates all 98 candidates
(seven parameter configurations times two Otsu and twelve fixed rules). The full
per-band table retains counts, pooled/macro/dry-patch metrics, measured compute
seconds, and per-patch threshold/fallback records. Each common channel/rule uses
each family's best pooled validation water IoU; the mean of four family IoUs
selects the common rule. Exact ties use lower measured compute time. The same
numeric fixed threshold applies across all four families. Undefined pooled IoU
blocks selection. Selection uses neither ENL nor test labels.

The four-row primary comparison disables cleanup. The separate four-row
ablation compares raw and the validation-selected actual filter with cleanup
off/on. Cleanup deletes 8-connected water components smaller than 16 pixels,
treats invalid pixels as barriers, and never fills holes. The identical fixed
ground-truth-water-positive patch set is verified across summary calls; dry
patch false positives remain separate. Primary timing includes one filter
invocation plus segmentation/scoring, excludes disk I/O; ablation timing
explicitly measures segmentation/scoring on cached filter outputs.

Verification commands:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_segment.py tests/test_benchmark.py -q --basetemp=.pytest_cache/phase4_red
.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest_cache/phase4_full
.venv/Scripts/python.exe scripts/phase4_fixture.py
```

The first run produced eight expected missing-implementation assertion failures.
After implementation, the final full suite passed **50 tests in 3.82 seconds**.
Nine focused Phase 4 tests cover strict threshold ties, invalid-only behavior,
constant fallback, unimodal failure, cleanup connectivity/size/barriers/holes,
independent validity, real disk serialization, validation-only selection,
pooled versus macro selection, shared rule, and timing ties.

The synthetic integration script used only preassigned validation phantom
identities 06/07/08 (256 x 256), known Gamma looks 4, noise seeds 42/43 for
VV/VH, and known-reference water classes `reference power <0.15`. It supplied
explicit development fallback thresholds VV -10 / VH -18 dB, with no claim of
real calibration. It wrote 98 validation rows, four primary rows and four cleanup
rows in **1.742 seconds** to ignored `outputs/phase4_fixture/validation.json`.
These timings are local fixture timings, not whole-Colab runtime measurements.

The output status remains `pending_real_calibration`. The implementation never
edits/freezes `configs/experiment.json`; its actual-data choices remain null.
The real-data Phase 4 exit gate remains open, as do the prior actual-data audit,
training-only looks estimation, MIDAL admission pilot and full runtime gates.
No neural or notebook implementation is included in this phase.
