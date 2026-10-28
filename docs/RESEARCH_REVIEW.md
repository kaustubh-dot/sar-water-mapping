# Research Review and Method Selection

**Search cutoff:** 28 October 2026. **Task:** denoise 100 Sentinel-1 VV/VH patches, segment surface water, and produce defensible ENL, PSNR, and IoU/F1 comparisons.

This is a targeted review of **30 research items**, with primary paper, author code, package, and model-card checks. It covers foundational filters, nonlocal methods, deep despeckling, current diffusion/self-supervision, and flood segmentation/foundation models. It is not an exhaustive review of every SAR paper. Full text and source were inspected where accessible; some items were assessed from publisher abstracts and author releases. Availability findings describe what was verifiable at the cutoff, not a guarantee that missing artifacts do not exist elsewhere. No models have been benchmarked by this project yet.

## Recommended direction

The strongest project is a controlled comparison whose input assumptions are correct. A recent publication, a high ENL, and a large foundation model each answer different questions; none establishes the best water map on this subset.

| Role | Selection | Reason and admission condition |
| --- | --- | --- |
| Required controls | Raw SAR, Median, multiplicative Lee | Fast, interpretable controls demanded by the problem; retain them even if a learned model wins. |
| Guaranteed processing comparator | Log-domain bilateral | Small dependency burden and bounded compute. A practical fallback, not a claim of research novelty or statistical optimality. |
| Stronger non-neural candidate | Scalar MIDAL + BM3D from MuLoG | Released likelihood-aware plug-and-play approach; pilot installation and iterative runtime. Replace bilateral if admitted. |
| First pretrained segmentation reference | UDL4FL `sm_unet_s1`, RSE 2025 | Released SAR GRD weights and distinct declared supervised training datasets. Resolve input-order inconsistency and measure runtime. |
| GPU training baseline | Compact two-channel U-Net | Learn the actual water task with controlled raw-versus-filtered training. A baseline for testing the value of preprocessing, not an assertion that this is the newest architecture. |
| First foundation-model candidate for a later bounded upgrade | TerraMind Tiny, radar-only adaptation | Actual S1GRD support and released weights; still needs a segmentation head and training. Do not inherit multimodal scores as SAR-only evidence. |

The remote development GPU was verified as an RTX 4000 Ada with approximately 20 GB VRAM. This makes bounded training feasible to investigate; it does not establish convergence, generalization, or a Colab training runtime. Credentials and connection details do not belong in this repository.

## Foundations and non-neural methods

| ID | Primary reference | What it contributes | Decision for this project |
| --- | --- | --- | --- |
| R01 | Bonafilia et al., **Sen1Floods11**, CVPR Workshops 2020. [Author release](https://github.com/cloudtostreet/Sen1Floods11), [data structure](https://github.com/cloudtostreet/Sen1Floods11/blob/master/docs/README.md) | The benchmark distinguishes hand-labeled and automatically generated water masks. | Confirm subset provenance; do not treat a threshold-generated target as independent ground truth. |
| R02 | Lee, **Digital Image Enhancement and Noise Filtering by Use of Local Statistics**, TPAMI 1980. [Paper](https://doi.org/10.1109/TPAMI.1980.4766994) | Local statistics give an efficient adaptive filtering foundation. | Implement a documented multiplicative Lee variant on power. Do not rename a generic additive Wiener smoother as Lee. |
| R03 | Frost et al., **A Model for Radar Images and Its Application to Adaptive Digital Filtering of Multiplicative Noise**, TPAMI 1982. [Paper](https://doi.org/10.1109/TPAMI.1982.4767223) | SAR-specific multiplicative modeling and adaptive spatial weighting. | Useful classical reference. Additional implementation adds limited value after Median and Lee; exclude from the core. |
| R04 | Otsu, **A Threshold Selection Method from Gray-Level Histograms**, TSMC 1979. [Paper](https://ieeexplore.ieee.org/document/4310076) | Selects a histogram threshold through class separation. | Common fast baseline. A two-class split is not proof that a dry patch contains water; include empty-water failures. |
| R05 | Parrilli et al., **A Nonlocal SAR Image Denoising Algorithm Based on LLMMSE Wavelet Shrinkage**, TGRS 2012. [Paper](https://doi.org/10.1109/TGRS.2011.2161586) | SAR-BM3D combines patch grouping and SAR-specific shrinkage. | Strong established nonlocal reference. Ordinary Gaussian BM3D on raw intensity is not SAR-BM3D. A maintained original Python/Colab release was not verified. |
| R06 | Deledalle et al., **MuLoG: MUlti-channel LOgarithm with Gaussian denoising**, TIP 2017, with later matrix-log work. [Author project](https://www.charles-deledalle.fr/pages/mulog.php), [Python package](https://pypi.org/project/mulog/) | Combines an explicit SAR likelihood with a Gaussian-denoiser prior; scalar MIDAL is available in the released implementation. | Best non-neural upgrade to pilot. Process each polarization as scalar intensity; VV/VH detected images do not supply a full complex polarimetric covariance matrix. No training is needed, but repeated BM3D calls may be expensive. |

Median is an engineering control, not a new research claim. Lee/Frost/Median are also documented in [ESA SNAP's speckle operator](https://step.esa.int/main/wp-content/help/versions/12.0.0/snap-toolboxes/eu.esa.microwavetbx.sar.op.sar.processing.ui/operators/SpeckleFilterOp.html). Use a documented noise estimate rather than a universal number of looks. GRD processing and resampling alter effective speckle statistics.

## Established deep despeckling and task-aware learning

| ID | Primary reference and release | Training/inference assumptions | Decision |
| --- | --- | --- | --- |
| R07 | Chierchia et al., **SAR-CNN**, IGARSS 2017. [Author code](https://github.com/grip-unina/SAR-CNN) | Residual learning; approximately clean targets were obtained through multitemporal processing. The documented released environment is old. | Historical deep baseline, not a priority dependency-porting project. Synthetic training and correlated real GRD are not automatically interchangeable. |
| R08 | Dalsasso et al., **SAR2SAR**, JSTARS 2021. [Paper](https://arxiv.org/abs/2006.15037), [author project](https://github.com/emanueledalsasso/SAR2SAR) | Speckle-aware learning from temporal observations with change compensation; inference can use one image. | Training data requirements do not imply multitemporal inference requirements. Existing weights are worth considering only with matching input statistics. |
| R09 | Gasnier et al., **SAR2SAR adaptation to Sentinel-1 GRD**, 2021. [Full author manuscript](https://arxiv.org/html/2102.00692), [maintained author-affiliated package](https://github.com/hi-paris/deepdespeckling) | Adapts to actual GRD speckle correlations. Package inference expects amplitude, and real checkpoint files are present. | Strong despeckling candidate with a significant calibration/domain caveat. Do not feed dB to it or assume square-root conversion alone matches training. Keep outside the default admitted branch until preprocessing compatibility is established. |
| R10 | Molini et al., **Speckle2Void**, TGRS 2022. [Paper](https://arxiv.org/abs/2007.02075), [author code](https://github.com/diegovalsesia/speckle2void) | Blind-spot Bayesian self-supervision; the released decorrelation stage requires complex SLC and manual frequency choices. | Released TerraSAR-X model is not a turnkey Sentinel-1 GRD solution. Our detected VV/VH patches do not contain the required complex components. |
| R11 | Dalsasso et al., **MERLIN**, TGRS 2022. [Paper](https://arxiv.org/abs/2110.13148) | Separates information in real and imaginary components of complex SAR data for self-supervision. | Reject for GRD-only input. A single complex image contains information absent from a single detected-intensity image. |
| R12 | Dalsasso et al., **MERLIN-Seg**, CVIU 2024. [Paper](https://doi.org/10.1016/j.cviu.2024.103940), [author manuscript](https://thome.isir.upmc.fr/papers/CVIU_MERLIN_Seg-24.pdf) | Joint despeckling/segmentation improves label efficiency in the studied building-footprint task. | Supports evaluating downstream utility. It does not establish a ready-made GRD water model or justify rebuilding complex-data training here. |

The `deepdespeckling` SAR2SAR checkpoint is actually present in its [saved-model directory](https://github.com/hi-paris/deepdespeckling/tree/main/deepdespeckling/sar2sar/saved_model). However, its [fixed normalization constants](https://raw.githubusercontent.com/hi-paris/deepdespeckling/main/deepdespeckling/utils/constants.py) and the preprocessing differences described in R29 require an input-domain audit. Weight availability and scientific compatibility are separate checks.

Do not use VV as a noisy target for VH: polarization changes the scattering signal, not just the noise realization. Do not train a denoiser to reproduce its own input, or call a classical-filter output clean truth. Those designs can make training loss look good without establishing speckle removal.

## Recent despeckling: 2024-2026

| ID | Primary reference | Recent contribution | Reproducibility and budget assessment |
| --- | --- | --- | --- |
| R13 | Pan et al., **DDPM with Swin Transformer for SAR despeckling**, Remote Sensing 2024. [Paper](https://www.mdpi.com/2072-4292/16/17/3222) | Transformer/diffusion restoration direction. | No compatible public author checkpoint was verified in this review. Publication alone does not supply a runnable experiment. |
| R14 | Guo et al., **ECDM**, Remote Sensing, August 2025. [Paper](https://www.mdpi.com/2072-4292/17/17/2970) | Accelerates conditional diffusion using fewer sampling steps. | Still iterative; the reported training uses extensive synthetic and real temporal data. No usable author weights were verified. Hardware-specific inference timing is not a Colab runtime guarantee. |
| R15 | Lin et al., **Speckle2Self**, Remote Sensing, November 2025. [Paper](https://www.mdpi.com/2072-4292/17/23/3840) | Intensity-only masked Transformer self-supervision with downsampling to address correlated noise. | Published training uses 200 epochs on eight RTX 3090 GPUs. Our one-GPU resource does not make that recipe cheap; no turnkey author checkpoint was verified. |
| R16 | Chen et al., **Self-supervised despeckling based solely on SAR intensity images: A general strategy / SDS-SAR**, ISPRS JPRS, January 2026. [Paper](https://doi.org/10.1016/j.isprsjprs.2025.11.025), [author repository](https://github.com/YYF121/SDS-SAR) | Intensity-only learning with statistically constructed training pairs. | Important negative availability check: the current [model source](https://raw.githubusercontent.com/YYF121/SDS-SAR/main/src/models/placeholder_model.py) implements a placeholder median filter, and the test script uses it. A linked external checkpoint could not be verified. Do not present that demonstration as the published neural method. |
| R17 | Heo, **S4DM**, January 2026 preprint. [Manuscript](https://arxiv.org/html/2601.14334v1) | Score-based self-supervision with a log/Yeo-Johnson construction. | Uses a much larger Sentinel-1 training set and substantial optimization. No public code/checkpoint link was verified. Interesting method, weak immediate reproducibility. |
| R18 | Hu et al., **Gamma-Bridge**, July 2026 preprint. [Paper](https://arxiv.org/abs/2607.22719) | Look-conditioned Gamma diffusion bridging and cross-sensor restoration experiments. | The manuscript-linked author repository returned 404 at checking time; weights could not be verified. Keep on the watchlist, not in the promised implementation. |
| R19 | Hu et al., **Closed-Form Nonlocal Shrinkage**, August/September 2026 preprint. [Paper](https://arxiv.org/abs/2608.15028) | Training-free nonlocal grouping and adaptive shrinkage. | Relevant recent alternative to learned restoration. The linked implementation returned 404; reproducing it from the paper exceeds the bounded comparator task. Prefer a released implementation for the hackathon. |

These checks distinguish theoretical relevance from operational readiness. A GPU helps training; it does not supply missing authors' models, complex observations, independent targets, or a verified preprocessing contract.

## Water segmentation and foundation models

| ID | Primary reference/release | Actual modality and evidence | Decision |
| --- | --- | --- | --- |
| R20 | Portalés-Julià et al., **Understanding flood detection models across Sentinel-1 and Sentinel-2 modalities and benchmark datasets**, RSE 2025. [Paper](https://doi.org/10.1016/j.rse.2025.114882), [code](https://github.com/kipoju/udl4fl), [weights](https://huggingface.co/isp-uv-es/udl4fl_models) | Releases a SAR-only GRD checkpoint. Declared supervised training uses S1S2Water/Kuro Siwo; Sen1Floods11 is a separate evaluation dataset. | Preferred frozen neural reference. Dataset-name separation does not prove geographic non-overlap. Its paper protocol differs from our pooled 100-patch evaluation, so measure our own scores. |
| R21 | Tanaka and Tsutsumida, **Sensor-Adaptive Flood Mapping with Pre-trained Multi-Modal Transformers**, September 2025 preprint. [Paper](https://arxiv.org/abs/2509.23035), [Presto release](https://github.com/nasaharvest/presto) | Presto supports SAR and missing modalities, with a small pixel/time-series backbone. The flood study uses a curated subset and a distinct geographic test. | Small parameter count does not establish cheap full-image training: the paper reports approximately 23.5 hours on RTX 4090 for its recipe. Not the first adaptation to reproduce. |
| R22 | Fuller et al., **CROMA**, NeurIPS 2023. [Paper](https://papers.neurips.cc/paper_files/paper/2023/hash/11822e84689e631615199db3b75cd0e4-Abstract-Conference.html), [code](https://github.com/antofuller/CROMA) | Genuine two-channel SAR encoder with public pretrained weights, including radar-only use. | Valid SAR foundation-model family. Encoder embeddings are not a water mask; a trained head, normalization and pretraining-overlap audit remain necessary. |
| R23 | Jakubik et al., **TerraMind**, ICCV 2025. [Paper](https://arxiv.org/abs/2504.11171), [code](https://github.com/IBM/terramind), [Tiny weights](https://huggingface.co/ibm-esa-geospatial/TerraMind-1.0-tiny) | Actual two-channel S1GRD support and released Tiny/Small variants. The [author flood configuration](https://raw.githubusercontent.com/IBM/terramind/main/configs/terramind_v1_tiny_sen1floods11.yaml) uses S1+S2 and long training. | Strongest foundation-model candidate to explore after the compact baseline. Use only S1GRD here; do not report its multimodal example as a SAR-only result. |
| R24 | Farajpoor and Narimani, **Accuracy and efficiency of compact foundation models for surface-water mapping during floods**, 26 October 2026 preprint. [Paper](https://arxiv.org/abs/2610.34904) | Evaluates Prithvi-Tiny on Sentinel-2 chips; compact pretrained inference is efficient but does not consistently beat U-Net in that study. | Very recent and relevant to model-selection reasoning, but optical-only evidence. The [released Prithvi flood checkpoint](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL-Sen1Floods11) likewise expects optical bands, not VV/VH. |
| R25 | **FM-Mamba**, Scientific Reports, June 2026. [Full paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13458292/) | Reports an efficient state-space flood network. | No author code/weights link was found. The stated three-channel input and sample accounting need clarification relative to two-band hand-labeled Sen1Floods11. Treat reported scores as author claims, not a verified deployable baseline. |
| R26 | Premananthan et al., **PFALNet**, EAI, August 2026. [Paper](https://eudl.eu/doi/10.4108/eetinis.133.12738), [full text](https://publications.eai.eu/index.php/inis/article/download/12738/4270/36232) | Lightweight polarization-fusion design; the headline experiment uses ETCI-2021 Florence, with 8-bit inputs and an added polarization-ratio channel. | Architecture inspiration. Its headline accuracy/runtime are not Sen1Floods11 results; no public code/weights were verified. |
| R27 | **OlmoEarth**, including the 23 October 2026 v1.3 release. [Author code](https://github.com/allenai/olmoearth_pretrain), [v1.3 model card](https://huggingface.co/allenai/OlmoEarth-v1_3-Base) | Genuine radar-capable representations; smaller earlier variants also exist. The current Base release is substantially larger and uses its own artifact license. | Current watchlist. A ready SAR water head and budget fit were not established; do not add its tooling before a baseline works. |
| R28 | **TEDI / TerraMind-KD**, 23 October 2026 preprint. [Paper](https://arxiv.org/html/2610.32566v1) | Recent efficient-distillation results use Sentinel-2 and high-resolution RGB; SAR-only is future work in the examined manuscript. | Reject as a currently available SAR solution. A recent efficiency headline does not establish modality compatibility or released weights. |

### UDL4FL source audit: details that affect our adapter

The [released checkpoint configuration](https://huggingface.co/isp-uv-es/udl4fl_models/blob/main/sm_unet_s1.json) specifies **MobileNetV2**, and the [model source](https://raw.githubusercontent.com/kipoju/udl4fl/main/udl4fl/models.py) uses **U-Net++**, despite a wrapper called `smp_Unet`. Do not describe this checkpoint as EfficientNet or plain U-Net.

The checkpoint has two output classes, land/water, while the generic wrapper contains stale three-class documentation. Its [prediction source](https://raw.githubusercontent.com/kipoju/udl4fl/main/udl4fl/worldfloods_model.py) applies stored normalization and returns class predictions plus softmax probabilities. Use the checkpoint's actual class order and avoid double normalization; its training hooks are stubs, so the minimal release is an inference package rather than a complete training recipe.

There is an input-order inconsistency: the stored configuration says `vh/vv`, while the [author notebook](https://raw.githubusercontent.com/kipoju/udl4fl/main/notebooks/run_in_gee_image.ipynb) exports `[VV,VH]`. Trace the adapter carefully; if unresolved, compare exactly those two interpretations on validation only, freeze the mapping, and disclose the choice. The notebook uses GRD dB. Convert classical-filter power back to dB before this branch.

Tiling also needs explicit treatment: released wrapper defaults and the paper's overlap protocol differ. Record tile size/overlap and use consistent inference for raw and filtered inputs. These issues do not invalidate the paper; they mean our implementation must be verified.

Code is LGPL-3.0 and weights are CC BY-NC 4.0 according to the [author model card](https://huggingface.co/isp-uv-es/udl4fl_models). Keep attribution and third-party terms; our MIT license does not replace them. Actual downloads, dependency compatibility and full-run speed remain untested.

## Evaluation evidence that determines the experiment

| ID | Primary reference | Finding and consequence |
| --- | --- | --- |
| R29 | Travert et al., **Evaluating the effects of preprocessing, method selection, and hyperparameter tuning on SAR-based flood mapping and water depth estimation**, NHESS, May 2026. [Full paper](https://nhess.copernicus.org/articles/26/2387/2026/) | Studies multiple filtering/mapping choices across two Garonne events. Processing choices materially affect outputs, and well-tuned unsupervised methods can be competitive in that setting. It also documents applying SAR2SAR before calibration, unlike the classical filters. Evaluate our complete denoising-to-mask pipeline and audit this domain difference; do not copy their large parameter sweep. |
| R30 | Gomez, Ospina and Frery, **Unassisted Quantitative Evaluation of Despeckling Filters**, Remote Sensing 2017. [Paper](https://arxiv.org/abs/1704.05952) | High ENL alone can reward oversmoothing. Ratio-image structure and radiometric preservation expose removed signal. Pair homogeneous-ROI ENL with downstream water metrics and ratio diagnostics. |

PSNR needs a clean reference: real Sentinel-1 patches and segmentation masks do not supply one. Use procedural known-backscatter phantoms with Gamma speckle, report synthetic PSNR separately, and retain the noisy-input baseline. See the [metric API](https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.peak_signal_noise_ratio) and our [evaluation protocol](EVALUATION_PROTOCOL.md).

Do not compare numbers across papers as a leaderboard unless input modality, labels, split, ignored pixels, class averaging, resolution and training data match. Water IoU, mean land/water IoU, newly flooded-area IoU and optical-only IoU are not interchangeable. Likewise, published milliseconds of inference do not include dependency installation, checkpoint downloads, tuning or training.

## Bounded GPU experiment

1. Finish the data/provenance audit and classical result first.
2. Run the frozen UDL4FL reference if its adapter gate passes.
3. Train one compact VV/VH U-Net on raw input and on the chosen classical-filter output using the same architecture, splits, augmentation and optimization. Start with one seed; add two fixed seeds only if the first controlled pair completes within the remote compute budget.
4. Use at most 20 epochs, validation early stopping, and a one-hour wall-time cap for the compact training comparison. Log learning curves, best-validation checkpoint, seed, environment and actual training time. No synthetic clean-target claims are needed for supervised segmentation.
5. Consider TerraMind Tiny only after those results exist, and only as a replacement for further optional model exploration. Start with a frozen S1GRD encoder and a small segmentation decoder; do not reproduce large-scale pretraining. Its separate admission gate must establish code compatibility, validation benefit, input normalization, and checkpoint provenance.

The initial experiment has four denoiser families and at most two neural architectures: one pretrained reference and one compact trained model. A foundation-model replacement requires an explicit recorded decision, not an expanding model zoo.

For Colab, report two different profiles if remote training is used: **checkpoint-based reproduction** (download frozen checkpoints and run evaluation) and **full training reproduction** (includes training). Passing the former does not establish the latter fits 30 minutes. If the judges require full training inside the limit, the compact training schedule must also be timed from a fresh Colab session or the classical core remains the compliant submission.

## Remaining uncertainties

- The organizers' archive, exact patch size, independent masks and split metadata have not yet been inspected.
- The remote hardware and Python access are verified; the system Python has no PyTorch installed. Create a dedicated environment and verify CUDA execution before training. The observed free resources were approximately 18 GB GPU memory and 440 GB disk; availability can change.
- MuLoG and UDL4FL have not been installed or run in our environment; their complete runtime is unknown.
- UDL4FL's input-order ambiguity and dataset/event overlap require recorded handling.
- No single reviewed source establishes the newest universally best method for this exact subset. The proposed controlled validation will determine our method selection.

Implementation order and acceptance gates are in the [roadmap](../ROADMAP.md).
