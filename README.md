# SAR Water Mapping

**Track 2: SAR & Earth Observation | SSG x Research Club**

Reproducible speckle denoising and surface-water segmentation on a 100-patch Sentinel-1 VV/VH subset of Sen1Floods11. The target is an end-to-end Google Colab run in **under 30 minutes**.

**Submission status: scientific execution and fresh Colab verified; publication pending.** Supplied execution (S1) and the fresh uncached classical Colab run (S2) are accepted. The full classical Colab run took **566.40 seconds (9 minutes 26 seconds)**, including setup, one dependency restart, all 200 downloads, checks, calibration, evaluation and export. See the [retained-evidence review](reports/colab_execution_review.md). Publication to `main` and the submission tag (S3) are the remaining gate. The [submission audit](reports/submission_audit.md) records this boundary. The supplied and earlier development results stay separately labeled.

**Supplied-first100 profile:** the [recipe](reports/supplied_subset_recipe.md) selects the first 100 ordered upstream hand-labeled training rows. All 100 pairs are audited. The existing seed-42 event rule freezes 29 training patches (Mekong/Nigeria/Pakistan), 40 validation (India) and 31 test (Ghana), before tuning. No cross-partition overlap or touching chips was found. Exactly 22 IDs were previously used in development training, including eight current test IDs; this is a disclosed internal event holdout, not a pristine blind test. `Ghana_26376` remains in test with no scored pixels. The five held-out ENL regions are visually selected land regions only. See the [data review](reports/supplied_data_review.md), [source configuration](reports/supplied_source-v1.json) and [reproduction commands](docs/REPRODUCING.md).

The single notebook now defaults to `DATA_SOURCE='supplied-first100'`; `upstream-development` preserves the earlier profile. Its supplied source, acquisition, split and ROI bindings are checked before calibration and held-out access. The [accepted calibration](reports/supplied_calibration_review.md) selects shared VH below -20 dB with Median 5 for neural input. The [accepted scratch training pair](reports/supplied_training_review.md) took 76.77 seconds including preparation: raw ran 10 epochs/150 updates, Median 5 ran 9 epochs/135 updates. The [supplied result review](reports/supplied_results_review.md) accepts the held-out tables; the [cached supplied notebook review](reports/supplied_notebook_review.md) also accepts the integrated execution. The new checkpoint ZIP is verified locally and has no public release yet. These timings do not certify a fresh Colab run.

**Accepted supplied held-out measurements.** All six rows
use the same 4,940,307 scored pixels across 31 Ghana test members: a fixed
15-patch water-positive macro set, 15 dry patches and one no-score patch.
Classical rows use shared VH below -20 dB with primary cleanup off; U-Net rows
use probability strictly above 0.5.

| Supplied held-out method | Water IoU | Water F1 |
| --- | ---: | ---: |
| Raw + shared threshold | 0.2772 | 0.4341 |
| Median 5 + shared threshold | 0.4135 | 0.5851 |
| Lee 5 + shared threshold | 0.4051 | 0.5766 |
| Log-bilateral + shared threshold | 0.3825 | 0.5534 |
| Compact U-Net, raw VV/VH | 0.4208 | 0.5923 |
| Compact U-Net, Median-5 VV/VH | 0.4043 | 0.5758 |

Median preprocessing improves threshold segmentation, while the filtered U-Net
has lower pooled IoU than the raw U-Net. No method or setting is changed from
these test outcomes. See the [supplied classical table](reports/supplied_classical-v1/results_real.csv),
[neural table](reports/supplied_neural-v1/results_neural.csv) and
[full report](reports/final_report.md). ENL covers five fixed visually selected
land regions only; one has valid SAR but no valid label pixels and remains in
the shared SAR-only diagnostic. Synthetic known-reference PSNR is separate.

The supplied classical CPU runner took **59.38 seconds**, including synthetic
work and 124 figures, excluding setup/access/calibration and final metadata
writes. Neural GPU checkpoint evaluation took **9.06 seconds**, separately
from the **76.77-second** remote training pair. These are recorded runner
subtotals, not a full notebook or fresh Colab measurement.

The **accepted supplied classical notebook smoke took 123.04 seconds** through
the final ZIP/checksum at source pin
`9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`: 10 cells completed, with 96 tests
passing in 8.30 seconds. It used a fresh kernel, 200 cached source TIFFs, an
existing clean isolated clone and preinstalled kernel prerequisites. Initial
clone/cache preparation were outside the notebook clock. See the
[summary](reports/supplied_notebook_smoke_summary.json) and
[independent review](reports/supplied_notebook_review.md). This closes S1;
the subsequent fresh Colab run is recorded separately below.

**Earlier development results (29 October 2026):** the distinct upstream development experiment has measured classical/neural results and a cached Linux notebook run. Phase reviews use GPT-6.1 Sol at xhigh. Its official partitions contain touching chips and shared events, so the following are correlated development results, not unseen-geography evidence. They do not describe the supplied-first100 profile.

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

[Download the reviewed development checkpoints](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1). Weights are release assets outside Git; no raw dataset is included. The [reproduction guide](docs/REPRODUCING.md) explains the exact source commit, input restoration, environments and commands. [Open the classical notebook in Colab](https://colab.research.google.com/github/kaustubh-dot/sar-water-mapping/blob/implementation/remaining-phases/notebooks/01_sar_water_mapping.ipynb); the [verified source-pinned Colab run](https://colab.research.google.com/github/kaustubh-dot/sar-water-mapping/blob/3eecc1434991835e576e7d3d09d967fbd9388359/notebooks/01_sar_water_mapping.ipynb) completed in 566.40 seconds. Its original ZIP and timing sidecar are retained locally outside Git; see the [verification summary](reports/colab_observed_summary.json). This certifies the classical core only; remote U-Net training remains a separate measurement.

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

The locked core compares unfiltered input, Median, multiplicative Lee, and a lightweight log-domain bilateral pipeline. Every denoiser uses the same validation-selected channel and threshold policy, with cleanup disabled in the primary comparison. The optional MIDAL + BM3D branch was declined to preserve the dependency and runtime budget; bilateral was retained. MIDAL was not piloted or admitted. No further model search enters v1.

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

Python, NumPy, SciPy, scikit-image, rasterio, pandas, matplotlib, and pytest. PyTorch and the neural package are introduced only if the neural feasibility gate passes. The classical pins are in `requirements-colab.txt`; actual training versions accompany the checkpoint bundle. Fresh Colab compatibility is verified at the exact source pin linked above.

Remote training and Colab reproduction are separate measurements. A checkpoint-based Colab evaluation under 30 minutes does not prove training also fits that limit. If full training is required within the judging budget, time that profile explicitly or submit the classical pipeline as the compliant core.

## Data and attribution

Use the organizers' subset first. If it is delayed, use only a small selection of the upstream hand-labeled SAR pairs for development; record the change and rerun on the actual subset before submission. Do not download the full dataset by default.

Bonafilia, D., Tellman, B., Anderson, T., and Issenberg, E. (2020). *Sen1Floods11: A Georeferenced Dataset to Train and Test Deep Learning Flood Algorithms for Sentinel-1*. CVPR Workshops. [Upstream citation and access](https://github.com/cloudtostreet/Sen1Floods11).

The [MIT license](LICENSE) covers original project code and documentation. Dataset files, papers, external code, and model weights retain their own terms. Raw data and checkpoints are excluded from Git.
