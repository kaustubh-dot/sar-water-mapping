# SAR Water Mapping: execution roadmap

Updated 29 October 2026. This is the remaining-work contract. Research selection is finished; the [implementation lock](docs/IMPLEMENTATION_LOCK.md) controls methods and training, and the [evaluation protocol](docs/EVALUATION_PROTOCOL.md) controls scientific claims. Do not add models or tune against the observed test results.

The [pre-submission audit](reports/submission_audit.md) retains a **NOT READY** verdict for the supplied-set submission. The completed statuses below apply to the earlier development experiment unless explicitly stated otherwise.

| Phase | Development status | Evidence / remaining gate |
| --- | --- | --- |
| 0. Research and scope | Complete | Public repo, cited review, exact implementation lock |
| 1. Data audit and split | Development and supplied data gates accepted | Exact first100 audited; seed-42 event split 29/40/31 and fixed ROIs reviewed |
| 2. Metrics and synthetic benchmark | Complete | Focused correctness tests and separate held-out synthetic PSNR |
| 3. Denoising baselines | Development and supplied calibration accepted | Four locked families; accepted source-aware calibration implementation |
| 4. Water segmentation | Development and supplied choices accepted | VH -20 dB/Median 5 frozen from validation; zero held-out access |
| 5. Controlled GPU training | Development and supplied pairs accepted | Scratch raw/Median-5 seed42 pair completed in 76.77 seconds; supplied checkpoint bundle local only |
| 6. Benchmark and notebook | Development run complete; supplied wiring accepted | Supplied results and cached notebook accepted; S1 closed; uncached Colab deferred |
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
- [x] Complete and review supplied cached notebook execution after the accepted calibration, paired scratch training and held-out evaluation; S1 is closed.

Evidence: [data review](reports/development_data_review.md), [portable-identity review](reports/source_identity_review.md), [exact manifest/splits](reports/source_identity-v3/manifest.csv). Seven touching cross-partition pairs and shared events limit claims to correlated official-subset development evaluation. No event/geography independence is claimed.

Supplied evidence: [accepted data/ROI review](reports/supplied_data_review.md), [internal split provenance](reports/supplied_split_provenance-v1.json), [accepted profile review](reports/supplied_profile_review.md) and [source configuration](reports/supplied_source-v1.json). The supplied event split is train 29 (Mekong/Nigeria/Pakistan), validation 40 (India), test 31 (Ghana); no cross-partition overlaps or touching chips were found. Prior project training exposure is 22 IDs, distributed 5/9/8, so pristine blind-test claims remain excluded. One test patch has no scored pixels and remains in membership. The five held-out ENL rectangles support land diagnostics only.

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

The completed items above describe development measurements. The supplied source-aware implementation is accepted. Its actual calibration completed 98 candidates on 40 India validation patches and froze shared VH below -20 dB, Median 5, Lee 5 and bilateral color sigma 3 dB; Median 5 is selected for neural input. The [independent calibration review](reports/supplied_calibration_review.md) accepted these frozen choices with zero held-out access. It uses four separately inspected training ROIs and the unchanged locked grids. Earlier development settings were not copied to the supplied run. See the [new configuration](configs/supplied-calibrated-v1.json).

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

The new supplied raw/Median-5 seed-42 pair is accepted by its separate
[training review](reports/supplied_training_review.md). It completed in 76.77
seconds including preparation: raw 10 epochs/150 updates (best epoch 5),
filtered nine epochs/135 updates (best epoch 4). Both began with matched fresh
initialization. [Public training metadata](reports/supplied_training-v1/summary.json)
retains the original source/configuration and environment identities. Its
reviewed checkpoint bundle is local only; no supplied public release is claimed.

## Phase 6 — Held-out benchmark and one notebook

- [x] Evaluate frozen four-family classical configuration on all 20 held-out patches; save pooled/per-patch/dry/macro results, ENL and radiometry.
- [x] Export separate synthetic PSNR and cleanup tables; inspect ratio/boundary/error figures and report failures.
- [x] Evaluate both frozen U-Net checkpoints at native resolution; export 40 masks, independent validity arrays, curves, figures and separate segmentation results.
- [x] Complete independent Sol xhigh review of actual neural outputs before accepting this execution gate.
- [x] Make the full classical notebook run setup, access, checks, audit, validation, evaluation and final export in cell order.
- [x] Run all ten code cells in a separate Linux kernel and inspect results/bundle; record 76 passing notebook checks.
- [ ] Deferred: restart a fresh Colab runtime, fetch uncached inputs, Run All and retain full setup/access/evaluation/export timing strictly below 30 minutes.
- [ ] If judging requires training within that budget, independently measure the shorter full-training profile or use the complete classical core. A checkpoint-only run is insufficient.

The cached Linux notebook took 91.78 seconds through ZIP/checksum, with an existing clean checkout and preinstalled kernel. It reproduced all four classical held-out confusion counts exactly. This is **not fresh Colab certification**. Four unselected validation candidates differed by one or two pixels across platforms; scientific choices did not change.

Evidence: [classical review](reports/classical_results_review.md), [notebook implementation review](reports/notebook_review.md), [actual notebook execution review](reports/notebook_execution_review.md), [notebook timing summary](reports/notebook_smoke_summary.json), [real table](reports/results_real.csv), [neural result review](reports/neural_results_review.md), [neural table](reports/results_neural.csv), [synthetic table](reports/results_synthetic.csv).

Supplied measurements are now recorded in separate [classical](reports/supplied_classical-v1/results_real.csv)
and [neural](reports/supplied_neural-v1/results_neural.csv) tables, accepted by
the [independent result review](reports/supplied_results_review.md). All six rows share 4,940,307 scored pixels, 15 fixed
water-positive macro patches, 15 dry patches and one no-score member. Median
threshold IoU is 0.4135 versus raw 0.2772; raw U-Net is 0.4208 versus
Median-input U-Net 0.4043. Five land-only ENL ROIs and separate synthetic PSNR
retain their diagnostic limits; one ENL ROI has valid SAR but no valid label
pixels and remains in the fixed shared diagnostic. The remote CPU classical runner took 59.38
seconds including 124 figures/synthetic work; GPU checkpoint evaluation took
9.06 seconds, separately from the 76.77-second training pair. Runner subtotals
exclude setup/access/calibration and final metadata writes. The separate
accepted cached supplied notebook took 123.04 seconds through final ZIP/hash,
with 10 cells and 96 passing checks. S1 is closed; fresh uncached Colab remains
deferred and unverified.

The [supplied notebook summary](reports/supplied_notebook_smoke_summary.json)
and [independent review](reports/supplied_notebook_review.md) bind source pin
`9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`. The accepted 123.04-second smoke
used 200 cached TIFFs, an existing clean isolated Linux clone and preinstalled
kernel prerequisites. Initial clone/cache preparation were outside the clock;
10 code cells and 96 checks completed. This closes S1 without closing S2.

## Phase 7 — Submission preparation and stop

- [x] Draft the report with data, methods, measured results, failures, limitations and references.
- [x] Prepare a three-minute explanation and exact reproduction/checkpoint instructions.
- [x] Finish whole-branch review, verify public artifact links/checksums and audit Git contents for data/credentials.
- [ ] Complete the remaining fresh Colab and publication acceptance gates and only then tag `v1.0-hackathon`.

Artifacts: [report](reports/final_report.md), [demo](reports/demo_outline.md), [reproduction guide](docs/REPRODUCING.md), [execution ledger](reports/execution_ledger.md), [final review](reports/final_branch_review.md). The report now includes accepted supplied and development measurements; final submission acceptance remains open.

## Next actions, in order

1. Completed: independent neural-result and final branch reviews accepted the development deliverable, with no unresolved P1/P2 findings. Preserve test-visible choices.
2. Preserve the reviewed implementation branch and public development checkpoint artifact. Do not merge or issue a final acceptance tag on unverified evidence.
3. Supplied acquisition/audit/ROIs, source-aware profile and actual validation calibration are accepted. The completed scratch raw/Median-5 GPU pair is accepted; frozen classical and neural held-out measurements are independently accepted. Preserve the original development outputs and disclose prior 22-patch training exposure, including eight current test IDs. See the [supplied execution ledger](reports/supplied_execution_ledger.md).
4. Completed: the connected cached notebook execution and independent review are accepted, closing S1. Preserve the pinned source, ZIP/sidecar and separately versioned supplied artifacts; the checkpoint bundle remains local only.
5. Fresh uncached Colab is explicitly deferred. Later run the connected profile with pinned source SHA, keep its ZIP and authoritative timing sidecar, and verify the full under-30-minute gate. Final READY status, publication to `main` and the submission tag remain pending that acceptance.

A new method requires a recorded failure, scope authorization or replacement of an optional item, compatible accessible code/weights and remaining runtime. Once final test results are visible, any scientific change is a new versioned experiment rather than an untouched holdout evaluation.
