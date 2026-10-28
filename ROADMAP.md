# SAR Water Mapping: Phasewise Roadmap

**Created:** 28 October 2026. **Goal:** finish a defensible hackathon submission, with a complete Colab run under 30 minutes.

**Progress:** Phase 0 complete; final method audit finished on 28 October 2026. The [implementation lock](docs/IMPLEMENTATION_LOCK.md) controls v1 method choices and exact model details. Phase 1 audit tooling and Phase 3 denoisers are implemented and reviewed, while their actual-data gates remain open. Phase 2 metrics and synthetic baseline are complete and reviewed. Phase 4 segmentation/selection tooling is fixture-tested and reviewed. All four implementation reviews used GPT-6.1 Sol at xhigh; findings are resolved. No real-data benchmark, training, or fresh Colab run has occurred.

**Fresh progress audit (28 October 2026):** 50 tests passed; the synthetic integration rerun produced 98 candidates, four primary rows and four cleanup-ablation rows. See [verified status and the remaining execution order](reports/progress_audit.md). Phase 1-4 code is ready for actual-data execution; their remaining data-dependent gates are listed there. Source changes are currently uncommitted locally.

**Architecture:** a small Python package does data loading, denoising, segmentation, and scoring; one notebook orchestrates it and presents results. Synthetic denoising evaluation is separate from real SAR water mapping. The [README](README.md) defines scope; the [evaluation protocol](docs/EVALUATION_PROTOCOL.md) fixes scientific rules; the [research review](docs/RESEARCH_REVIEW.md) records evidence behind method selection.

**Execution:** work sequentially through the checkboxes. Open one phase at a time. Each phase ends with an inspectable artifact and a verification gate. Development timeboxes below are planning estimates, separate from the measured Colab runtime requirement.

## Scope contract

- Required: raw baseline, Median, Lee, one lightweight processing pipeline, water thresholding, ENL, PSNR, IoU/F1, figures, and reproducibility.
- First processing upgrade: scalar MIDAL + BM3D from the author MuLoG package, independently per polarization; it replaces bilateral only if a bounded pilot passes.
- Primary learned model: one compact two-channel U-Net, trained separately on raw and selected filtered input. It performs segmentation, so ENL/PSNR are not applicable to its mask outputs.
- A remote RTX 4000 Ada with approximately 20 GB VRAM is available for development; credentials stay outside the repository.
- One locked neural architecture for v1. UDL4FL is reserve only because its input-order metadata remain ambiguous; it is excluded from promised deliverables. No foundation-model adaptation, diffusion training, or new self-supervised despeckling research in v1.
- No Frost unless required by judging clarification; Median and Lee already meet the classical-filter requirement.
- No UI, web app, API, database, cloud deployment, full-dataset download, ancillary-data pipeline, or broad hyperparameter search.
- Use seed `42`; freeze test membership before optimization; use validation data for decisions.
- A complete, honest classical result is preferable to an unfinished neural experiment. A neural win is a research question, never an acceptance condition.

## Phase overview

| Phase | Development cap | Deliverable | Exit gate |
| --- | --- | --- | --- |
| 0. Research and scope | Current planning deliverable | Repository, literature review, protocol, roadmap | Explicit methods and exclusions recorded |
| 1. Data audit and split | 60 min | Manifest, audit contact sheet, split file | Correct pairs, units, labels, provenance; no cross-split duplicates |
| 2. Metrics and synthetic benchmark | 45 min | Trusted scoring functions and synthetic fixtures | Hand-calculated metric cases and known-reference tests pass |
| 3. Denoising baselines | 75 min | Raw, Median, Lee, log-bilateral outputs | Valid shapes/units, finite valid output, no invalid-pixel contamination |
| 4. Water segmentation | 60 min | Bounded validation comparison and frozen configuration | A complete end-to-end classical pipeline works |
| 5. Controlled GPU training | 60 min engineering + 60 min remote compute cap | Compact U-Net raw/filtered training pair or documented failure | Correct inputs, logs/checkpoints, bounded compute |
| 6. Final benchmark and Colab | 75 min | Final tables, notebook, figures, timed execution | All mandatory outputs; fresh run below 30 min |
| 7. Submission | 45 min | Short report, demo outline, tagged final commit | Another person can reproduce and understand the result |

Phases 1-7 total approximately **7 hours engineering plus up to 1 hour remote training** if every cap is used. Adjust available development time by cutting Phase 5 first, then optional analysis; preserve the evaluation and submission gates.

## Phase 0: Research and project contract

**Files:** `README.md`, `ROADMAP.md`, `docs/IMPLEMENTATION_LOCK.md`, `docs/RESEARCH_REVIEW.md`, `docs/EVALUATION_PROTOCOL.md`, `AGENTS.md`, `.gitignore`, `LICENSE`.

- [x] Publish the public repository and verify its visibility and initial commit.
- [x] Finish the cited review, with publication status and code/weight availability distinguished.
- [x] Record the candidate choices and fallback before implementing experiments.

**Verified:** the repository is public, the initial documents are on `main`, local document links resolve, and the review contains 30 cited research items. The next task is the data audit, not another open-ended literature search.

## Phase 1: Audit the actual data

**Create:** `src/sar_water/data.py`, `data/README.md`, `data/manifest.csv`, `data/splits.csv`, `reports/data_audit.md`, `tests/test_data.py`, and the minimal `pyproject.toml` needed to run them.

- [ ] Obtain the kickoff archive; record its source, archive hash, patch count, dimensions, band order, units, nodata, and label provenance.
- [ ] Pair SAR and masks by identifiers, not directory order. Reject missing pairs, duplicate identifiers, unsupported labels, and mismatched shape/georeferencing.
- [ ] Inspect VV, VH, histograms, and masks for five representative development patches.
- [ ] Keep independent manual masks distinct from Otsu/other weak labels. If only weak masks exist, label all resulting IoU/F1 as weak-label agreement and record the missing independent evaluation.
- [ ] Use organizer splits if supplied; otherwise use the split hierarchy in the evaluation protocol. Audit duplicates and overlaps in either case.
- [x] Verify dB/power conversion, invalid-pixel handling, and no cross-split duplicates with small fixtures.

**Gate:** one patch round-trips through the loader without swapping VV/VH or treating valid `0 dB` as nodata. The split manifest is saved and frozen. Missing independent masks blocks real-data ground-truth claims, but not filter development or synthetic evaluation.

**Tooling evidence (28 October 2026):** the Phase 1 adapter, inventory-driven
GeoTIFF audit CLI, provenance/hash manifest writer and guarded split creation are
implemented. Fifteen scientific fixture tests pass, including GeoTIFF metadata,
valid zero dB, independent input/label masks, deterministic filling and split
conflict checks. See [implementation evidence](reports/phase1_implementation.md)
and [missing-input audit](reports/data_audit.md). The [Sol xhigh review](reports/phase1_review.md)
is resolved, including split-provenance and plotting-retry fixes. These fixtures are not the
organizer subset: all actual-data checkboxes and the frozen real-data gate remain
open. Explicit separated spatial groups are required when event/scene grouping
cannot establish usable partitions; no automatic spatial-block claim is made.

## Phase 2: Establish trustworthy metrics

**Create:** `src/sar_water/metrics.py`, `src/sar_water/synthetic.py`, `tests/test_metrics.py`, `tests/test_synthetic.py`, `configs/experiment.json`.

- [x] Verify IoU/F1 against a hand-computed confusion matrix, including invalid and empty-water cases.
- [x] Verify ENL on known constant and varying positive-intensity arrays; keep undefined results explicit.
- [x] Generate deterministic 256 x 256 intensity phantoms with known boundaries, homogeneous areas, and texture; split phantom identities before corruption.
- [x] Corrupt the reference with mean-one Gamma speckle at `L = 1` and `L = 4`, using three fixed realizations per image and identical corruption across methods.
- [x] Verify PSNR against known MSE, explicit data range, and identity output. Make the raw/noisy PSNR a required baseline.

**Gate:** metric tests pass. Synthetic references are explicitly labeled simulated backscatter, and no real noisy image is called clean ground truth.

**Synthetic development evidence (28 October 2026):** all 27 tests pass,
including 12 Phase 2 metric/synthetic cases. The raw/noisy baseline exports 72
records and a frozen 6/3/3 phantom identity split. See
[Phase 2 implementation evidence](reports/phase2_implementation.md).
The [Sol xhigh review](reports/phase2_review.md) passed with no scientific defects.
This explicitly authorized synthetic development does not close the missing
organizer-data Phase 1 gate or freeze real-data calibration. Only the shared
corruption generator and raw baseline ran in Phase 2; separate validation-only
denoiser diagnostics are recorded under Phase 3. Final synthetic test comparison remains pending.

## Phase 3: Implement the bounded denoiser set

**Create:** `src/sar_water/filters.py`, `tests/test_filters.py`.

- [x] Add identity/raw, Median, and the exact multiplicative local-LMMSE Lee variant in the implementation lock, operating on linear power.
- [x] Add log-domain bilateral filtering as the dependency-light processing comparator. Document that log/exponentiation can bias intensity; measure mean change rather than claim an unbiased estimator.
- [ ] Give scalar MIDAL + BM3D at most 15 minutes of dependency/setup investigation within this phase. Use the scalar author API, frozen/known looks and six ADMM iterations; profile five development patches on both bands. Admit only if estimated cost of all enabled invocations, with 50% timing margin, fits three minutes and the whole notebook budget. If compatibility, terms, correctness or runtime fails, retain bilateral and close the branch. If admitted, replace bilateral before full validation rather than expanding the four-family comparison.
- [x] Use only this validation grid: Median windows `{3, 5}`; Lee windows `{5, 7}`; log-bilateral window `5`, spatial sigma `2`, dB color sigma `{1.5, 3.0}`.
- [ ] Estimate Lee's effective looks from training-only homogeneous regions and freeze it; do not assume GRD is single-look. Use known `L` for synthetic data.
- [x] Filter bands independently, preserve shape, use reflection at image borders, and restore input invalid pixels after documented nearest-valid filling.
- [ ] Check constant-image behavior, invalid holes, tiny arrays, and finite positive outputs. Profile five development patches.

**Synthetic development evidence (28 October 2026):** all 41 tests pass, including 14 focused filter cases. Exact filtering and a training-only recorded-ROI looks estimator are implemented. Five synthetic two-band 512 x 512 development arrays were profiled, and all bounded settings were checked on synthetic validation identities only (126 records). See [Phase 3 implementation evidence](reports/phase3_implementation.md). No real looks/settings are frozen, no final test comparison ran, and the MIDAL admission pilot is unrun/not admitted; bilateral is retained. The actual-data pilot and whole-Colab runtime gate remain open.

The [Sol xhigh review](reports/phase3_review.md) passed with no findings.

**Gate:** all four methods generate comparable outputs and timing. Extrapolated mandatory computation fits the Colab budget. If bilateral is too slow, reduce its one fixed window and record that choice before final evaluation.

## Phase 4: Freeze water segmentation

**Create:** `src/sar_water/segment.py`, `src/sar_water/benchmark.py`, `tests/test_segment.py`, `tests/test_benchmark.py`.

- [x] Implement and fixture-test valid-dB Otsu/fixed thresholding, bounded validation-only selection, disk-to-mask scoring, and the separate cleanup ablation.

- [ ] Run per-patch Otsu on valid dB values, separately for VV and VH, for every denoiser configuration. This is the common filter comparison.
- [ ] Also compare a validation-tuned fixed dB threshold using the bounded grid in the protocol. Keep this labeled as supervised calibration.
- [ ] Choose a single common channel/threshold strategy by the pooled-validation procedure in the implementation lock. A fixed threshold must have the same numeric value across denoisers. Retain the full per-band validation table.
- [ ] Keep cleanup disabled in the primary four-row filter comparison. Separately evaluate the cleanup toggle on raw and the selected filtered pipeline: none versus remove water components smaller than 16 pixels. Use no hole filling.
- [ ] Freeze denoiser settings, channel, threshold strategy, and cleanup in `configs/experiment.json`. Record why Otsu fails on unimodal/all-land patches.

**Gate:** a real patch runs from disk to water mask and metrics with one function/command. No test labels have been used to pick parameters.

**Synthetic development evidence (28 October 2026):** all 50 tests pass,
including nine focused Phase 4 cases. The exact bounded search ran on three
synthetic validation identities, producing 98 candidate rows, four primary rows
with cleanup disabled, and four separate cleanup-ablation rows. Explicit fixture
fallback thresholds and known synthetic looks are recorded; no real choices or
`configs/experiment.json` calibration fields were frozen. See
[Phase 4 implementation evidence](reports/phase4_implementation.md). The actual
data calibration checkboxes and real-patch exit gate above remain open.

The [Sol xhigh review](reports/phase4_review.md) passed with no findings. The
combined fixture suite passes 50 tests. Continue with actual-data Phase 1 audit,
training-only ROI estimation and Phase 4 calibration when the subset arrives;
Phase 5 training depends on those frozen inputs. Phases 5–7 remain unrun.

## Phase 5: Use the GPU for one controlled training comparison

**Files:** `src/sar_water/model.py`, `src/sar_water/train.py`, `tests/test_neural.py`, and a separate neural dependency group. Remote experiments use a dedicated project directory and environment; inspect shared resource use before launching training. Architecture, loss, normalization and sampling are fixed by the implementation lock.

- [ ] Verify remote PyTorch/CUDA compatibility, free VRAM/disk, and a small forward/backward pass. Do not alter system packages or interfere with other GPU jobs.
- [ ] Implement the compact U-Net: `[VV,VH]` inputs; widths `16,32,64,128`; three downsampling stages; two Conv/GroupNorm/ReLU operations per block; bilinear decoder; one output logit. Verify fewer than one million parameters and the expected approximately 0.49-million scale.
- [ ] Verify SAR-only nearest-valid filling produces finite neural inputs while retaining original masks, masked `0.5*BCEWithLogits + 0.5*Dice` loss, shared raw-training-set mean/std normalization, and deterministic sampling. Each epoch draws four 256-square crops per training source, using the locked uniform/water-centered policy. Invalid labels affect neither input filling, loss nor scoring.
- [ ] Train separate raw/filtered models with matched initialization and crop/augmentation sequences, batch `8`, Adam learning rate `0.001`, seed `42`, at most `20` epochs per condition, and validation patience `5`. Use the best pooled-validation-IoU checkpoint and fixed sigmoid threshold `>0.5`, with native-resolution final inference.
- [ ] Bound the complete training comparison to one hour remote wall time. Log actual updates, including any early-stopping differences. Add paired seeds `43` and `44` only within the same cap; compare only seeds completed for both inputs.
- [ ] Save learning curves, best-validation checkpoints, configuration/hash, environment, actual time, and seeds. Keep checkpoint binaries outside Git and publish retrievable artifact references when delivering results.
- [ ] If compact training is unstable, diagnose once within budget; the classical result remains the guaranteed submission. Do not open a rescue architecture search.

**Gate:** the paired compact experiment records actual seeds, updates, checkpoints and budget, or a concrete failure. No UDL4FL or foundation-model implementation is required for v1. A failed learned experiment does not delay the classical submission.

## Phase 6: Final benchmark and notebook

**Create:** `notebooks/01_sar_water_mapping.ipynb`, `reports/results_real.csv`, `reports/results_synthetic.csv`, `reports/runtime.json`, `reports/figures/`, `reports/environment.txt`, and checkpoint provenance/download instructions when remote training is used.

- [ ] Run the frozen configuration on the held-out set. Save per-patch scores and pooled confusion counts, not only headline averages.
- [ ] Compare every frozen denoiser under the common threshold strategy with cleanup disabled. Add the separate raw/selected-filter cleanup ablation and the paired neural segmentation results, if completed.
- [ ] Produce aligned VV/VH, raw/filtered, ground truth/prediction, error overlay, ratio image, and narrow-boundary failure examples. Use common display limits.
- [ ] Make the notebook install, access data, validate inputs, run validation/frozen evaluation, generate figures, and export a results bundle in cell order. Label its profile `full` or `checkpoint-evaluation` explicitly; the latter uses remote-trained weights and does not claim to reproduce their training within the limit.
- [ ] Run the meaningful unit checks and one full smoke experiment. Restart a fresh Colab runtime, then Run All and measure every stage.

**Runtime budget:** setup and subset/checkpoint access `5 min`; audit `2`; synthetic evaluation `3`; classical filtering and bounded validation `7`; admitted neural evaluation or budgeted Colab training `6`; final scoring, figures, exports `2`; reserve `5`. Total target **30 minutes**, with measured completion strictly below it. Report network/setup and compute separately as well as the total; an exceeded download budget is not silently excluded. A full-training profile starts with at most eight epochs and the six-minute training cap; it must be measured independently of the remote 20-epoch experiment.

**Gate:** the notebook finishes from a fresh runtime in under 30 minutes, exports the required artifacts, and makes no unmeasured performance claims. Hardware, profile, and actual patch count are recorded. If timing fails, remove optional neural work first. If judging requires full training inside the limit, an inference-only pass is insufficient; verify the full profile or use the classical core.

## Phase 7: Submission and stop

**Create:** `reports/final_report.md`; update `README.md` with the verified Colab link and actual results; tag the verified commit `v1.0-hackathon`.

- [ ] Write a 2-4 page report: problem, data, methods, protocol, results, failure cases, limitations, references.
- [ ] Prepare a three-minute explanation: multiplicative noise, method choices, quantitative comparison, and one important failure.
- [ ] Verify notebook links, data-access instructions, test commands, result provenance, and the exact final commit.
- [ ] Check that the repository contains no raw dataset, large checkpoints, access tokens, or invented benchmark results.
- [ ] Mark the phases complete only from evidence and tag the reproducible submission.

**Definition of done:** all required metrics have defensible provenance; all required artifacts exist; the fresh Colab run is measured below 30 minutes; and another team member can reproduce it from the repository instructions.

## Change rule

A new method may enter only if it answers a documented failure, has accessible compatible inputs/code/weights, fits remaining time, and replaces an existing optional item. Record the reason and affected phase here. Once final test results are visible, changes require a new versioned experiment and cannot be described as an untouched holdout evaluation.

**Next action:** preserve the reviewed source checkpoint, then complete the real-data audit and classical validation freeze. Use the kickoff subset if available; otherwise prepare a clearly identified upstream hand-labeled development subset with recorded provenance and membership. The organizer-specific gate remains open until its data are audited. GPU setup and U-Net fixture implementation may proceed while data access is pending; real training depends on the frozen real inputs. Follow the [remaining-work roadmap](reports/progress_audit.md).
