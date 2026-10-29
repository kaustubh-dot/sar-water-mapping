# Progress audit and remaining roadmap

**Verified:** 28 October 2026, against the current local working tree. This audit does not certify a real-data benchmark or a Colab runtime. Implementation choices remain those in the [v1 lock](../docs/IMPLEMENTATION_LOCK.md).

## Finding

**Phase 1-4 implementation is present and the current fixture suite passes. The real-data exit gates are still open.** No new material scientific or implementation defect was found in this review scope.

The source, scientific fixture tests, evidence scripts and phase reports were inspected. Independent read-only checks covered data/provenance and filtering/metrics. The complete suite was rerun using the project's existing virtual environment: **50 passed in 4.21 seconds**, with no skipped tests reported.

The Phase 4 integration script was rerun in a new ignored audit output directory, preserving earlier evidence files. It produced **98 validation candidates, four primary rows and four cleanup-ablation rows in 1.725 seconds**. Its status is correctly `pending_real_calibration`, and the source is explicitly simulated backscatter. This is a small local integration run, not a full runtime result.

The 126 saved Phase 3 validation records and 72 Phase 2 raw/noisy records were also regenerated in memory during review; their numeric metrics matched. Saved timing extrapolations were arithmetically consistent, with their limits documented.

## Phase-by-phase status

| Phase | Verified implementation | Still required to close the phase on real data |
| --- | --- | --- |
| 1. Data audit | Explicit units/band order; independent masks; GeoTIFF checks; hashes; guarded split/manifest tools; audit CLI | Acquire actual pairs; verify source/terms/labels; inspect five real development patches; resolve overlaps/group limitations; save frozen manifests/splits |
| 2. Metrics and synthetic references | Masked confusion counts; pooled/macro/dry metrics; ENL; explicit-range PSNR; deterministic phantoms and shared Gamma noise | Final denoiser comparison on untouched synthetic test identities belongs to the final evaluation stage; it has not run |
| 3. Denoisers | Raw, Median, exact multiplicative Lee, log-bilateral; independent bands; correct fill/filter/restore; training-only looks estimator | Select homogeneous real training ROIs; save/freeze per-band looks; profile five real development patches; close MIDAL admission as admitted/rejected/deferred rather than treating it as implemented |
| 4. Water segmentation | Otsu/fixed thresholds; common numeric fixed threshold; bounded validation selection; separate cleanup ablation; disk-pair scoring | Supply calibrated constant-patch fallbacks; run real validation; freeze common channel/rule, filter settings and cleanup; verify a real disk-to-mask run |
| 5. Learned segmentation | No model or training module exists yet | GPU environment smoke test; compact U-Net; finite-input preprocessing; masked loss; paired raw/filtered training; checkpoints and curves |
| 6. Final benchmark and Colab | Reusable scientific functions exist; no notebook/final benchmark bundle | Frozen held-out runs; real ENL/IoU/F1; synthetic PSNR; figures and exports; dependency pins; fresh timed Colab Run All |
| 7. Submission | Project design/research documentation exists | Measured results in README; final report; demo; reproducibility check; verified submission tag |

## Evidence behind the remaining gates

- `data/` contains only `README.md`. No organizer archive, extracted SAR/masks, real manifest or frozen split was found in this workspace.
- `configs/experiment.json` still says `organizer_subset_pending`; `split_frozen=false`, `calibration_frozen=false`, with channel, threshold strategy, filter parameters and effective looks unset. This is appropriate until actual calibration is run.
- `src/sar_water/model.py`, `src/sar_water/train.py`, the Colab notebook and `reports/final_report.md` are absent.
- Local `.venv` contains PyTorch **2.14.0+cpu**, reports CUDA unavailable and has no CUDA runtime. This says nothing about the remote server's current virtual environments. The previously verified remote GPU needs a fresh CUDA forward/backward smoke check in the chosen training environment.
- The current implementation/configuration/tests/reports are uncommitted locally; the latest local commit is still the design lock. Preserve the reviewed work in a scoped commit before moving to training. This audit does not claim that another remote branch was checked.

## What to do next, in order

### A. Make a reviewed source checkpoint

Save the current Phase 1-4 implementation, tests, config and compact evidence reports in Git, excluding raw data, environments, caches and checkpoint binaries. This prevents later training changes from obscuring the verified baseline. Pin the implementation commit in future run records; a design-only base SHA does not identify uncommitted code exactly.

### B. Finish real-data readiness — first priority

Use the organizer archive if available. Otherwise obtain a **documented development subset of upstream hand-labeled Sen1Floods11 SAR/mask pairs**, downloading only selected pairs. Record source identifiers and upstream membership; keep development findings distinct from the organizer's final evaluation.

Prepare the inventory described in [data/README.md](../data/README.md), inspect metadata, and run:

```powershell
.venv/Scripts/python.exe -m sar_water.data data/inventory.csv --output data/audit-v1 --contact-sheet
```

This command requires real inventory/files; it has not been run on actual data. Inspect the contact sheet, resolve provenance and overlap issues, and freeze membership before tuning. Organizer-specific acceptance remains open if only upstream development data are available. Do not reuse synthetic fixtures as real SAR evidence.

**Exit artifact:** audited real pairs, provenance notes, contact sheet, `manifest.csv` and `splits.csv` in a versioned audit directory. No model-selection use of test labels.

### C. Produce one complete classical validation run

Select and save homogeneous training ROIs; estimate/freeze effective looks independently per band. Profile the four methods on five real development patches. Bilateral remains the fourth family unless the single bounded MIDAL preflight is explicitly admitted; an optional method must not stall the core.

Calibrate/record constant-patch fallback thresholds from training/validation only. Run the existing 98-candidate real validation search, save the complete table and separate cleanup ablation, then write the reviewed choices and provenance into the versioned experiment configuration. A fixture's selected settings are not real calibration.

**Exit artifact:** frozen common channel/threshold policy, per-family parameters, looks, cleanup decision and their validation evidence. The next major milestone is a reproducible **real SAR pair -> filtered image -> water mask -> scores** path.

### D. Complete Phase 5 on the GPU

Create a dedicated remote environment and verify CUDA with a small forward/backward pass. Implement only the locked compact U-Net, including SAR-only nearest-valid filling, shared raw-training normalization and masked BCE/Dice. Test finite outputs, ignored pixels, deterministic crop membership and parameter count with fixtures.

Once real splits/calibration are ready, train raw and selected-filtered models separately with matched seeds and sampling. Start with paired seed 42, at most 20 epochs per condition, validation patience five and a shared one-hour remote cap. Save best-validation checkpoints, actual updates, curves, configuration and time. Add paired seeds only within that same budget.

**Can proceed while data access is pending:** model/loss/data-loader fixtures and GPU environment setup. Real training or claims of generalization cannot be replaced by fitting artificial masks.

### E. Complete Phase 6: evaluation, figures and Colab

Build the final runner/notebook around the existing functions. Freeze synthetic settings using only synthetic validation, then run the held-out synthetic comparison. Run frozen real configurations on the real holdout; export per-patch counts, pooled water scores, fixed-set macro scores, dry false positives, homogeneous-ROI ENL/status counts and radiometric mean changes.

Create shared-scale before/after images, label/prediction/error overlays, ratio images and representative failure cases. Record code/config/data hashes, environment versions and stage timings.

Run a fresh Colab session and time every enabled cell. Keep `full` training and remote-checkpoint evaluation profiles distinct. A shorter Colab schedule has its own scores; it does not reproduce a longer remote training run. The enabled workflow must finish below 30 minutes before that claim is made.

**Exit artifact:** runnable notebook, actual real/synthetic tables, figure bundle, accessible checkpoint references when used, exact environment and measured runtime.

### F. Complete Phase 7 and stop

Write the short report, update the README with measured results and the verified Colab link, prepare the three-minute explanation, and check reproduction from the recorded commit. Tag the finished submission only after its acceptance gates pass.

## Suggested effort allocation

These are development estimates, not measured execution times. Data-access delay is additional.

| Remaining milestone | Working estimate |
| --- | --- |
| Source checkpoint plus actual-data audit | 45-90 minutes after data access |
| Real training ROIs, classical validation and freeze | 45-60 minutes |
| GPU environment, model/loss/sampler and checks | 60-90 minutes |
| Paired remote training | Up to the locked one-hour compute cap |
| Final runner/notebook, results, figures and fresh Colab check | 90-150 minutes |
| Report, demo and submission check | 45-60 minutes |

No new literature search or model family is required. Keep the v1 method set and spend the remaining effort on real-data evidence, training and reproducibility.
