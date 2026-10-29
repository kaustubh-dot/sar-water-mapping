# SAR Water Mapping

**Track 2: SAR & Earth Observation | SSG x Research Club**

Reproducible speckle denoising and surface-water segmentation on a 100-patch Sentinel-1 VV/VH subset of Sen1Floods11. The target is an end-to-end Google Colab run in **under 30 minutes**.

**Pre-submission audit: NOT READY for final submission.** Development scores/checkpoints are verified, but the supplied first-100 profile is not connected and executed, and fresh uncached Colab is unverified. The [submission audit](reports/submission_audit.md) lists the remaining gates and corrected provenance/documentation issues. Do not relabel the development tables as supplied-set measurements.

**Status (29 October 2026):** the upstream development experiment is implemented and measured: audited 100 manual-label pairs, frozen calibration, four classical pipelines, paired GPU U-Net training, held-out evaluation and a complete cached Linux notebook run. Phase reviews use GPT-6.1 Sol at xhigh. The organizers’ subset and a **fresh Colab Run All below 30 minutes remain unverified**. Official partitions contain touching chips and shared events, so these are correlated development results, not unseen-geography evidence.

| Held-out method | Water IoU | Water F1 |
| --- | ---: | ---: |
| Raw + shared threshold | 0.6084 | 0.7565 |
| Median 5 + shared threshold | 0.6304 | 0.7733 |
| Lee 5 + shared threshold | 0.6070 | 0.7554 |
| Log-bilateral + shared threshold | 0.6304 | 0.7733 |
| Compact U-Net, raw VV/VH | 0.5855 | 0.7385 |
| Compact U-Net, Median-5 VV/VH | 0.5346 | 0.6968 |

All classical rows use validation-selected VV below -18 dB, with cleanup disabled. Neural rows use fixed probability above 0.5. Median preprocessing did not improve this single-seed U-Net; the negative result is retained. ENL and synthetic PSNR are reported separately in the [report](reports/final_report.md), with [classical outputs](reports/classical_results-v1/results_real.csv) and [neural outputs](reports/neural_results-v1/results_neural.csv).

The GPU training pair took **122.06 seconds**, including preparation. The complete classical notebook took **91.78 seconds on Linux with cached TIFFs, an existing clone and preinstalled kernel**; this is not a fresh Colab measurement. See [notebook evidence](reports/notebook_smoke_summary.json), [current roadmap](ROADMAP.md) and [execution ledger](reports/execution_ledger.md).

[Download the reviewed development checkpoints](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1). Weights are release assets outside Git; no raw dataset is included. The [reproduction guide](docs/REPRODUCING.md) explains the exact source commit, input restoration, environments and commands. [Open the classical notebook in Colab](https://colab.research.google.com/github/kaustubh-dot/sar-water-mapping/blob/implementation/remaining-phases/notebooks/01_sar_water_mapping.ipynb); this access link does not certify its fresh-runtime timing.

**Supplied selection update:** the user has now provided a recipe selecting the first 100 rows of the upstream hand-labeled training CSV. It differs from the development subset above; only 22 identifiers overlap, all previously used for training. Its exact identities are frozen in the [recipe audit](reports/supplied_subset_recipe.md). These 100 have no supplied internal evaluation splits and have not yet been audited/calibrated as a set. The notebook currently reproduces the earlier development experiment; its result tables cannot be relabeled as this supplied subset.

## Local development

Use Python 3.12 or later for the pinned notebook profile (`pip install -r requirements-colab.txt`, then `pip install -e . --no-deps`). The core package also supports Python 3.11 with compatible dependencies. Run `python -m pytest -q --basetemp=outputs/pytest`. The [data instructions](data/README.md) describe the explicit inventory and `sar-water-audit` command. Fixtures exercise loader and split behavior; they do not replace the organizer-data audit or establish geographic generalization.

Reproduce the simulated raw/noisy baseline with `python -m sar_water.synthetic --output outputs/phase2_synthetic`. Run `python scripts/phase3_synthetic_check.py` for filter diagnostics on training/validation phantoms, and `python scripts/phase4_fixture.py` for the segmentation-selection fixture. These are local synthetic development runs, not the final held-out benchmark or a timed Colab run. The generic `configs/experiment.json` remains an unfitted template. Recorded calibration choices are in `configs/development-calibrated-v3.json`; v3 changes only portable identity bindings from accepted v2, with no retuning.

## Start here

- [Phasewise roadmap](ROADMAP.md): sequence, timeboxes, deliverables, and completion gates.
- [Implementation lock](docs/IMPLEMENTATION_LOCK.md): final method choices, exact U-Net, bounded grids, and exclusions for v1.
- [Research review](docs/RESEARCH_REVIEW.md): primary papers, recent methods, reproducibility checks, and method selection.
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md): splits, units, synthetic PSNR, real-data ENL, and water IoU/F1.

## The experiment

The central question is: **Does reducing speckle improve water segmentation enough to justify its runtime and loss of detail?**

The locked core compares unfiltered input, Median, multiplicative Lee, and a lightweight log-domain bilateral pipeline. Every denoiser uses the same validation-selected channel and threshold policy, with cleanup disabled in the primary comparison. Scalar MIDAL + BM3D is the sole bounded substitution for bilateral, subject to a compatibility and whole-workflow runtime gate.

A remote RTX 4000 Ada GPU with approximately 20 GB VRAM is available for development. The primary learned experiment is one compact VV/VH U-Net architecture, trained separately on raw and selected filtered inputs. UDL4FL is reserve literature, excluded from promised deliverables because of unresolved input-order metadata. Foundation-model adaptation is outside v1. The [implementation lock](docs/IMPLEMENTATION_LOCK.md) fixes the details; the [research review](docs/RESEARCH_REVIEW.md) records the wider evidence.

The research review explains why a newer publication or a larger model is insufficient evidence of better performance on this particular dataset.

## Deliverables at the finish line

1. One Colab notebook that loads the subset and runs all required experiments.
2. A manifest with data provenance, fixed train/validation/test membership, and input checksums.
3. A real-data table reporting ENL, water IoU/F1, precision/recall, and runtime.
4. A separate synthetic Gamma-speckle table reporting reference-based PSNR.
5. Aligned before/after figures, masks, ratio images, and representative failures.
6. A short report, reproducible configuration, dependency versions, remote-training logs when used, and a timed fresh Colab run.

We will report negative results honestly. Completion does not require a neural model or denoiser to beat every baseline.

## Scope

Use the supplied SAR patches and their water masks. Preserve native resolution for final scoring. Exclude dashboards, APIs, deployment, additional satellite modalities, geographic data collection, and large model training from the core project. The outputs identify observed surface water; separating new floodwater from permanent water requires additional information.

The upstream documentation describes two-band, 512 x 512 Sentinel-1 images in dB and labels `-1` (invalid), `0` (land), `1` (water). The kickoff subset must be audited rather than assumed to retain this exact format. Upstream also contains threshold-generated labels: these must not be confused with independent hand labels. [Dataset](https://github.com/cloudtostreet/Sen1Floods11), [dataset structure](https://github.com/cloudtostreet/Sen1Floods11/blob/master/docs/README.md).

## Planned stack

Python, NumPy, SciPy, scikit-image, rasterio, pandas, matplotlib, and pytest. PyTorch and the neural package are introduced only if the neural feasibility gate passes. The classical pins are in `requirements-colab.txt`; actual training versions accompany the checkpoint bundle. Fresh Colab compatibility remains an execution gate.

Remote training and Colab reproduction are separate measurements. A checkpoint-based Colab evaluation under 30 minutes does not prove training also fits that limit. If full training is required within the judging budget, time that profile explicitly or submit the classical pipeline as the compliant core.

## Data and attribution

Use the organizers' subset first. If it is delayed, use only a small selection of the upstream hand-labeled SAR pairs for development; record the change and rerun on the actual subset before submission. Do not download the full dataset by default.

Bonafilia, D., Tellman, B., Anderson, T., and Issenberg, E. (2020). *Sen1Floods11: A Georeferenced Dataset to Train and Test Deep Learning Flood Algorithms for Sentinel-1*. CVPR Workshops. [Upstream citation and access](https://github.com/cloudtostreet/Sen1Floods11).

The [MIT license](LICENSE) covers original project code and documentation. Dataset files, papers, external code, and model weights retain their own terms. Raw data and checkpoints are excluded from Git.
