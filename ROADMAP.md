# SAR Water Mapping: Phasewise Roadmap

**Created:** 28 October 2026. **Goal:** finish a defensible hackathon submission, with a complete Colab run under 30 minutes.

**Architecture:** a small Python package does data loading, denoising, segmentation, and scoring; one notebook orchestrates it and presents results. Synthetic denoising evaluation is separate from real SAR water mapping. The [README](README.md) defines scope; the [evaluation protocol](docs/EVALUATION_PROTOCOL.md) fixes scientific rules; the [research review](docs/RESEARCH_REVIEW.md) records evidence behind method selection.

**Execution:** work sequentially through the checkboxes. Open one phase at a time. Each phase ends with an inspectable artifact and a verification gate. Development timeboxes below are planning estimates, separate from the measured Colab runtime requirement.

## Scope contract

- Required: raw baseline, Median, Lee, one lightweight processing pipeline, water thresholding, ENL, PSNR, IoU/F1, figures, and reproducibility.
- First processing upgrade: scalar MIDAL + BM3D from the author MuLoG package, independently per polarization; it replaces bilateral only if a bounded pilot passes.
- Neural candidate: the released UDL4FL `sm_unet_s1` segmentation checkpoint (2025). This does not produce denoised images, so its ENL/PSNR are not applicable.
- A remote RTX 4000 Ada with approximately 20 GB VRAM is available for development; credentials stay outside the repository.
- At most two neural architectures: one frozen pretrained reference and one compact trained segmentation model. No foundation-model pretraining, diffusion training, or new self-supervised despeckling research.
- TerraMind Tiny is a replacement candidate after the baseline works, not an automatic third model. Record any replacement and its budget before starting.
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
| 5. GPU training and neural reference | 60 min engineering + 60 min remote compute cap | Controlled compact training pair; admitted frozen reference or rejection | Correct inputs, logs/checkpoints, bounded compute |
| 6. Final benchmark and Colab | 75 min | Final tables, notebook, figures, timed execution | All mandatory outputs; fresh run below 30 min |
| 7. Submission | 45 min | Short report, demo outline, tagged final commit | Another person can reproduce and understand the result |

Phases 1-7 total approximately **7 hours engineering plus up to 1 hour remote training** if every cap is used. Adjust available development time by cutting Phase 5 first, then optional analysis; preserve the evaluation and submission gates.

## Phase 0: Research and project contract

**Files:** `README.md`, `ROADMAP.md`, `docs/RESEARCH_REVIEW.md`, `docs/EVALUATION_PROTOCOL.md`, `AGENTS.md`, `.gitignore`, `LICENSE`.

- [ ] Publish the public repository and verify its visibility and initial commit.
- [ ] Finish the cited review, with publication status and code/weight availability distinguished.
- [ ] Record the candidate choices and fallback before implementing experiments.

**Done when:** these documents agree, contain no fabricated performance numbers, and expose the next task clearly. These checkboxes are closed only after remote publication is verified.

## Phase 1: Audit the actual data

**Create:** `src/sar_water/data.py`, `data/README.md`, `data/manifest.csv`, `data/splits.csv`, `reports/data_audit.md`, `tests/test_data.py`, and the minimal `pyproject.toml` needed to run them.

- [ ] Obtain the kickoff archive; record its source, archive hash, patch count, dimensions, band order, units, nodata, and label provenance.
- [ ] Pair SAR and masks by identifiers, not directory order. Reject missing pairs, duplicate identifiers, unsupported labels, and mismatched shape/georeferencing.
- [ ] Inspect VV, VH, histograms, and masks for five representative development patches.
- [ ] Keep independent manual masks distinct from Otsu/other weak labels. If only weak masks exist, label all resulting IoU/F1 as weak-label agreement and record the missing independent evaluation.
- [ ] Use organizer splits if supplied; otherwise use the split hierarchy in the evaluation protocol. Audit duplicates and overlaps in either case.
- [ ] Verify dB/power conversion, invalid-pixel handling, and no cross-split duplicates with small fixtures.

**Gate:** one patch round-trips through the loader without swapping VV/VH or treating valid `0 dB` as nodata. The split manifest is saved and frozen. Missing independent masks blocks real-data ground-truth claims, but not filter development or synthetic evaluation.

## Phase 2: Establish trustworthy metrics

**Create:** `src/sar_water/metrics.py`, `src/sar_water/synthetic.py`, `tests/test_metrics.py`, `tests/test_synthetic.py`, `configs/experiment.json`.

- [ ] Verify IoU/F1 against a hand-computed confusion matrix, including invalid and empty-water cases.
- [ ] Verify ENL on known constant and varying positive-intensity arrays; keep undefined results explicit.
- [ ] Generate deterministic 256 x 256 intensity phantoms with known boundaries, homogeneous areas, and texture; split phantom identities before corruption.
- [ ] Corrupt the reference with mean-one Gamma speckle at `L = 1` and `L = 4`, using three fixed realizations per image and identical corruption across methods.
- [ ] Verify PSNR against known MSE, explicit data range, and identity output. Make the raw/noisy PSNR a required baseline.

**Gate:** metric tests pass. Synthetic references are explicitly labeled simulated backscatter, and no real noisy image is called clean ground truth.

## Phase 3: Implement the bounded denoiser set

**Create:** `src/sar_water/filters.py`, `tests/test_filters.py`.

- [ ] Add identity/raw, Median, and multiplicative Lee on linear power; name the actual Lee variant.
- [ ] Add log-domain bilateral filtering as the dependency-light processing comparator. Document that log/exponentiation can bias intensity; measure mean change rather than claim an unbiased estimator.
- [ ] Give scalar MIDAL + BM3D at most 15 minutes of dependency/setup investigation within this phase. Use the author implementation with known/estimated looks and one documented default configuration; profile five development patches. If setup, radiometry, or runtime fails, retain bilateral and record the rejection. If admitted, replace bilateral in the primary four-family comparison rather than expanding the grid.
- [ ] Use only this validation grid: Median windows `{3, 5}`; Lee windows `{5, 7}`; log-bilateral window `5`, spatial sigma `2`, dB color sigma `{1.5, 3.0}`.
- [ ] Estimate Lee's effective looks from training-only homogeneous regions and freeze it; do not assume GRD is single-look. Use known `L` for synthetic data.
- [ ] Filter bands independently, preserve shape, use reflection at image borders, and restore input invalid pixels after documented nearest-valid filling.
- [ ] Check constant-image behavior, invalid holes, tiny arrays, and finite positive outputs. Profile five development patches.

**Gate:** all four methods generate comparable outputs and timing. Extrapolated mandatory computation fits the Colab budget. If bilateral is too slow, reduce its one fixed window and record that choice before final evaluation.

## Phase 4: Freeze water segmentation

**Create:** `src/sar_water/segment.py`, `src/sar_water/benchmark.py`, `tests/test_segment.py`, `tests/test_benchmark.py`.

- [ ] Run per-patch Otsu on valid dB values, separately for VV and VH, for every denoiser configuration. This is the common filter comparison.
- [ ] Also compare a validation-tuned fixed dB threshold using the bounded grid in the protocol. Keep this labeled as supervised calibration.
- [ ] Choose a single common channel/threshold strategy on validation to isolate filter effects; retain the full per-band validation table.
- [ ] Evaluate one cleanup toggle on the chosen validation pipeline: none versus remove water components smaller than 16 pixels. Use no hole filling in the core.
- [ ] Freeze denoiser settings, channel, threshold strategy, and cleanup in `configs/experiment.json`. Record why Otsu fails on unimodal/all-land patches.

**Gate:** a real patch runs from disk to water mask and metrics with one function/command. No test labels have been used to pick parameters.

## Phase 5: Use the GPU for one controlled training comparison

**Potential files:** `src/sar_water/pretrained.py`, `src/sar_water/model.py`, `src/sar_water/train.py`, `tests/test_neural.py`, and a separate optional dependency group. Remote experiments use a dedicated project directory and environment; inspect shared resource use before launching training.

- [ ] Verify remote PyTorch/CUDA compatibility, free VRAM/disk, and a small forward/backward pass. Do not alter system packages or interfere with other GPU jobs.
- [ ] Give UDL4FL `sm_unet_s1` a maximum 30-minute engineering feasibility check: import, checkpoint/config download, source/weights terms, one development-patch inference, and timing. Use frozen inference; no UDL4FL fine-tuning in this submission.
- [ ] Resolve the released checkpoint's `vh/vv` configuration versus the author's `[VV,VH]` export example. Trace actual preprocessing and normalization; if ambiguity remains, predeclare the two order interpretations, select on validation only, and disclose this adaptation. Reject if neither is defensible.
- [ ] Verify checkpoint class semantics and map water to our binary target explicitly. Use its released normalization once; do not replace it with per-patch stretching or normalize twice.
- [ ] Admit it only with traceable weights/config hashes, finite same-size probabilities, correct input units, and a whole-run time estimate within budget. Audit known training datasets and geographic/benchmark overlap.
- [ ] Compare frozen inference on raw SAR and on the validation-selected classical output. Keep identical weights, adaptation, and probability decision across these two rows. This is a downstream robustness check, not a neural despeckler.
- [ ] Train the compact baseline: two input channels, base width `16`, three downsampling stages, under one million parameters, masked BCE plus Dice, batch `8`, Adam learning rate `0.001`, at most `20` epochs and validation early stopping with patience `5`. Use train-only normalization, flips/90-degree rotations, training crops of 256, and native-resolution final inference. Verify ignored pixels affect neither loss nor scoring.
- [ ] Run the same compact architecture on raw SAR and on the chosen classical-filter output, starting from the same seed. Keep split, initialization, augmentation, and training budget matched. Bound the complete training comparison to one hour remote wall time. Add seeds `43` and `44` only if the first pair leaves enough of that same budget; compare only seeds completed for both inputs.
- [ ] Save learning curves, best-validation checkpoints, configuration/hash, environment, actual time, and seeds. Keep checkpoint binaries outside Git and publish retrievable artifact references when delivering results.
- [ ] If the frozen model fails, record its rejection without opening a rescue model search. If the compact training is unstable, diagnose once within budget; the classical result remains the guaranteed submission.

**Gate:** each branch records `admitted` or a concrete rejection. Compact training results identify their seeds and budget. A rejection is a completed feasibility task, not a reason to delay submission. A later TerraMind Tiny adaptation must replace an optional branch under a new recorded gate, rather than expanding the promised model set.

## Phase 6: Final benchmark and notebook

**Create:** `notebooks/01_sar_water_mapping.ipynb`, `reports/results_real.csv`, `reports/results_synthetic.csv`, `reports/runtime.json`, `reports/figures/`, `reports/environment.txt`, and checkpoint provenance/download instructions when remote training is used.

- [ ] Run the frozen configuration on the held-out set. Save per-patch scores and pooled confusion counts, not only headline averages.
- [ ] Compare every frozen denoiser under the common threshold strategy. Add the chosen pipeline's cleanup ablation and the admitted neural row, if any.
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

**Next action:** Phase 1, inspect the actual kickoff subset. Until it arrives, use the upstream sample only for loader and plotting smoke checks, and synthetic fixtures for metric/filter development.
