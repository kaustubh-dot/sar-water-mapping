# SAR Water Mapping: execution roadmap

Updated 29 October 2026. This is the remaining-work contract. Research selection is finished; the [implementation lock](docs/IMPLEMENTATION_LOCK.md) controls methods and training, and the [evaluation protocol](docs/EVALUATION_PROTOCOL.md) controls scientific claims. Do not add models or tune against the observed test results.

The [pre-submission audit](reports/submission_audit.md) retains a **NOT READY** verdict for the supplied-set submission. The completed statuses below apply to the earlier development experiment unless explicitly stated otherwise.

| Phase | Development status | Evidence / remaining gate |
| --- | --- | --- |
| 0. Research and scope | Complete | Public repo, cited review, exact implementation lock |
| 1. Data audit and split | Development complete; supplied recipe now known | Exact first-100 definition recorded; new set audit/splits remain open |
| 2. Metrics and synthetic benchmark | Complete | Focused correctness tests and separate held-out synthetic PSNR |
| 3. Denoising baselines | Complete | Four locked families; train-only looks; bounded validation |
| 4. Water segmentation | Complete | Validation-frozen VV -18 dB strategy and cleanup ablation |
| 5. Controlled GPU training | Complete | Reviewed raw/Median U-Net pair, checkpoint release |
| 6. Benchmark and notebook | Development run complete | Classical/neural results reviewed; fresh Colab gate open |
| 7. Submission | Draft prepared | Report/demo/reproduction ready for review; final acceptance/tag open |

## Scope to preserve

Keep a small Python experiment and one Colab notebook. Required methods are raw, Median, multiplicative local-LMMSE Lee and log-bilateral; optional MIDAL was not admitted, and bilateral remains. One compact VV/VH U-Net architecture is trained separately on raw and validation-selected filtered inputs. No new architecture, foundation model, dashboard, API, deployment or full-dataset collection enters v1.

Use seed 42, frozen source splits, train-only normalization/noise estimates and validation-only selection. Classical primary rows share one numeric threshold and disable cleanup. Report cleanup separately. Keep the same ground-truth-water-positive macro set and disclose dry false positives. Use power for Lee/ENL and known synthetic references for PSNR. Keep data/checkpoints/credentials out of Git. Remote training and Colab checkpoint evaluation are different timings.

## Phase 0 — Research and project contract

- [x] Public GitHub repository and cited primary-source review.
- [x] Exact bounded methods, model, training and evaluation contract.
- [x] Explicit exclusions and change rule.

Evidence: [research review](docs/RESEARCH_REVIEW.md), [implementation lock](docs/IMPLEMENTATION_LOCK.md).

## Phase 1 — Data audit and frozen split

- [x] Select exactly 100 upstream hand-labeled pairs by label-blind hash ranking within official partitions, before reading imagery.
- [x] Verify all 200 object sizes/MD5s/file SHA-256s, pairing, shape, units, band order, label validity and georeferencing.
- [x] Inspect five representative development patches and preserve independent SAR/label masks.
- [x] Freeze official 60/20/20 membership and audit duplicate/overlap/adjacency constraints.
- [x] Add portable native-source identity with exact file checks, preserving original source bytes and all scientific choices.
- [x] Record the user's supplied acquisition recipe and freeze its exact first-100 upstream training identifiers and source CSV hash.
- [ ] Download/audit that distinct supplied set, establish internal splits/provenance and rerun a separately versioned experiment before claiming supplied-subset acceptance.

Evidence: [data review](reports/development_data_review.md), [portable-identity review](reports/source_identity_review.md), [exact manifest/splits](reports/source_identity-v3/manifest.csv). Seven touching cross-partition pairs and shared events limit claims to correlated official-subset development evaluation. No event/geography independence is claimed.

## Phase 2 — Trustworthy metrics and synthetic references

- [x] Test conversions, validity, confusion metrics, empty/dry cases, ENL and explicit-range PSNR.
- [x] Freeze procedural phantom identities before Gamma corruption; share seeds and corruption across methods.
- [x] Select synthetic settings on synthetic validation and export 72 held-out measurements separately from real SAR.

Evidence: [metric review](reports/phase2_review.md), [synthetic results](reports/classical_results-v1/results_synthetic.csv), [classical scientific execution review](reports/classical_results_review.md). Real noisy SAR is never a clean reference.

## Phases 3–4 — Frozen classical calibration

- [x] Implement raw, power Median, multiplicative local-LMMSE Lee and dB bilateral with mask restoration and focused tests.
- [x] Inspect six homogeneous raw training ROIs; freeze VV/VH effective looks 4.859278/4.020814 before validation.
- [x] Profile five real training patches; retain the bounded seven filter settings.
- [x] Run 98 validation candidates; select common VV fixed threshold -18 dB, Median 5, Lee 5, bilateral color sigma 3 dB.
- [x] Keep cleanup off in four primary rows; run a separate small-component cleanup ablation.
- [x] Independently reproduce validation scientific records and freeze before held-out scoring.

Evidence: [calibration review](reports/classical_calibration_review.md), [v2 calibration](reports/classical_calibration-v2/validation.json), [execution configuration v3](configs/development-calibrated-v3.json). V1 is invalid due inconsistent ROI byte hashes and is retained as superseded evidence. V3 changes provenance bindings only; it does not recalibrate v2 choices.

## Phase 5 — One controlled GPU pair

- [x] Inspect GPU/disk use and use a dedicated environment/project directory; preserve unrelated jobs and system packages.
- [x] Verify exact 487,857-parameter architecture, SAR-only filling, masked BCE/Dice, shared raw-training normalization and deterministic crop policy.
- [x] Train separate raw/Median-5 models with matched initialization/crops, seed 42, Adam 0.001, batch 8, maximum 20 epochs and patience five.
- [x] Complete within the shared one-hour cap; record actual updates and best-validation checkpoints.
- [x] Independently verify all 13 crop plans and 40 native validation confusion matrices.
- [x] Save curves, hashes, original environment and retrievable checkpoint bundle outside Git.
- [x] Retain the negative filtered-model result; no rescue architecture search. Optional seeds 43/44 were not run.

The pair completed in 122.06 seconds including 12.86 seconds of preparation. Raw stopped after 11 epochs/327 updates (best epoch 6); filtered after 13/387 (best epoch 8). Peak PyTorch CUDA allocation was 964,296,704 bytes; CPU peak RSS was not measured.

Evidence: [execution review](reports/phase5_execution_review.md), [training summary](reports/neural_training-v1/summary.json), [approved development checkpoint release](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1).

## Phase 6 — Held-out benchmark and one notebook

- [x] Evaluate frozen four-family classical configuration on all 20 held-out patches; save pooled/per-patch/dry/macro results, ENL and radiometry.
- [x] Export separate synthetic PSNR and cleanup tables; inspect ratio/boundary/error figures and report failures.
- [x] Evaluate both frozen U-Net checkpoints at native resolution; export 40 masks, independent validity arrays, curves, figures and separate segmentation results.
- [x] Complete independent Sol xhigh review of actual neural outputs before accepting this execution gate.
- [x] Make the full classical notebook run setup, access, checks, audit, validation, evaluation and final export in cell order.
- [x] Run all ten code cells in a separate Linux kernel and inspect results/bundle; record 76 passing notebook checks.
- [ ] Restart a fresh Colab runtime, fetch uncached inputs, Run All and retain full setup/access/evaluation/export timing strictly below 30 minutes.
- [ ] If judging requires training within that budget, independently measure the shorter full-training profile or use the complete classical core. A checkpoint-only run is insufficient.

The cached Linux notebook took 91.78 seconds through ZIP/checksum, with an existing clean checkout and preinstalled kernel. It reproduced all four classical held-out confusion counts exactly. This is **not fresh Colab certification**. Four unselected validation candidates differed by one or two pixels across platforms; scientific choices did not change.

Evidence: [classical review](reports/classical_results_review.md), [notebook implementation review](reports/notebook_review.md), [actual notebook execution review](reports/notebook_execution_review.md), [notebook timing summary](reports/notebook_smoke_summary.json), [real table](reports/results_real.csv), [neural result review](reports/neural_results_review.md), [neural table](reports/results_neural.csv), [synthetic table](reports/results_synthetic.csv).

## Phase 7 — Submission preparation and stop

- [x] Draft the report with data, methods, measured results, failures, limitations and references.
- [x] Prepare a three-minute explanation and exact reproduction/checkpoint instructions.
- [x] Finish whole-branch review, verify public artifact links/checksums and audit Git contents for data/credentials.
- [ ] Complete the remaining organizer/Colab acceptance gates and only then tag `v1.0-hackathon`.

Artifacts: [report](reports/final_report.md), [demo](reports/demo_outline.md), [reproduction guide](docs/REPRODUCING.md), [execution ledger](reports/execution_ledger.md), [final review](reports/final_branch_review.md). The report is a development deliverable until these acceptance gates close.

## Next actions, in order

1. Completed: independent neural-result and final branch reviews accepted the development deliverable, with no unresolved P1/P2 findings. Preserve test-visible choices.
2. Preserve the reviewed implementation branch and public development checkpoint artifact. Do not merge or issue a final acceptance tag on unverified evidence.
3. Connect the newly supplied first-100 training-row recipe to a separate supplied-subset experiment. Audit its pairs, freeze internal event/scene/spatial splits before tuning, calibrate only on its validation and evaluate its frozen held-out partition. Preserve the original development outputs and disclose prior 22-patch training exposure. See the [recipe audit](reports/supplied_subset_recipe.md).
4. Run that connected classical profile in a fresh Colab session with the pinned source SHA and uncached download. Keep its result ZIP and authoritative timing sidecar. Repeating the old development profile does not verify the supplied-set submission.
5. Update the report with those measured gates and create the final submission tag only when all required evidence exists.

A new method requires a recorded failure, scope authorization or replacement of an optional item, compatible accessible code/weights and remaining runtime. Once final test results are visible, any scientific change is a new versioned experiment rather than an untouched holdout evaluation.
