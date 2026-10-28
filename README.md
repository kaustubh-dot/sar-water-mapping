# SAR Water Mapping

**Track 2: SAR & Earth Observation | SSG x Research Club**

Reproducible speckle denoising and surface-water segmentation on a 100-patch Sentinel-1 VV/VH subset of Sen1Floods11. The target is an end-to-end Google Colab run in **under 30 minutes**.

**Status:** research and planning. No filters, models, notebook, benchmark results, or runtime claims have been implemented or validated yet. The organizers' 100-patch subset has not been supplied in this workspace.

## Start here

- [Phasewise roadmap](ROADMAP.md): sequence, timeboxes, deliverables, and completion gates.
- [Research review](docs/RESEARCH_REVIEW.md): primary papers, recent methods, reproducibility checks, and method selection.
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md): splits, units, synthetic PSNR, real-data ENL, and water IoU/F1.

## The experiment

The central question is: **Does reducing speckle improve water segmentation enough to justify its runtime and loss of detail?**

The guaranteed core compares unfiltered input, Median, Lee, and a lightweight log-domain bilateral pipeline. Every denoiser uses the same thresholding and scoring protocol. Scalar MIDAL + BM3D from the MuLoG package can replace bilateral if a short compatibility/runtime pilot passes. The preferred pretrained neural reference is the released 2025 UDL4FL Sentinel-1 segmentation checkpoint, subject to input-order, dependency, and runtime checks.

A remote RTX 4000 Ada GPU with approximately 20 GB VRAM is available for development. The bounded training experiment is a compact VV/VH U-Net on raw versus filtered inputs. Keep at most two neural architectures: this trained model and the pretrained reference. TerraMind Tiny is a later replacement candidate, not an automatic third model. The [research review](docs/RESEARCH_REVIEW.md) records the evidence and tradeoffs.

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

Python, NumPy, SciPy, scikit-image, rasterio, pandas, matplotlib, and pytest. PyTorch and the neural package are introduced only if the neural feasibility gate passes. Exact dependency versions will be pinned after a clean Colab compatibility check.

Remote training and Colab reproduction are separate measurements. A checkpoint-based Colab evaluation under 30 minutes does not prove training also fits that limit. If full training is required within the judging budget, time that profile explicitly or submit the classical pipeline as the compliant core.

## Data and attribution

Use the organizers' subset first. If it is delayed, use only a small selection of the upstream hand-labeled SAR pairs for development; record the change and rerun on the actual subset before submission. Do not download the full dataset by default.

Bonafilia, D., Tellman, B., Anderson, T., and Issenberg, E. (2020). *Sen1Floods11: A Georeferenced Dataset to Train and Test Deep Learning Flood Algorithms for Sentinel-1*. CVPR Workshops. [Upstream citation and access](https://github.com/cloudtostreet/Sen1Floods11).

The [MIT license](LICENSE) covers original project code and documentation. Dataset files, papers, external code, and model weights retain their own terms. Raw data and checkpoints are excluded from Git.
