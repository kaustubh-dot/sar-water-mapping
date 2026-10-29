# Implementation Lock: Version 1

**Final method audit:** 28 October 2026. Method selection is locked. For subsequent measured execution and current acceptance gates, see the [execution ledger](../reports/execution_ledger.md); this document specifies the design rather than the latest experiment status.

This is the controlling method-selection document for v1. The [roadmap](../ROADMAP.md) provides execution order; the [evaluation protocol](EVALUATION_PROTOCOL.md) provides scoring rules. The [research review](RESEARCH_REVIEW.md) preserves the wider literature and reasons for exclusions.

We can lock a defensible experimental design now. We cannot name the highest-scoring method on an unseen subset before running the controlled validation. Do not describe this lock as proof of universal state-of-the-art performance.

## 1. Fixed scope and comparison

| Component | Locked choice | Purpose |
| --- | --- | --- |
| Input | Sentinel-1 `[VV,VH]`; audit actual units and independent labels | Correct physical and evaluation contract |
| Classical controls | Raw, Median, multiplicative local-LMMSE Lee | Isolate the effect of filtering |
| Processing comparator | Log-domain bilateral | Edge-aware, dependency-light processing alternative |
| Sole processing substitution | Scalar MIDAL + BM3D, only after its bounded preflight | Test an established likelihood-aware comparator without expanding the method set |
| Classical segmentation | One shared channel and threshold rule, selected on validation | Fair comparison across denoisers |
| Primary learned model | Compact two-channel U-Net, trained separately on raw and selected filtered input | Measure whether preprocessing helps learned segmentation |
| Cleanup | None in the primary filter table; one small-component ablation separately | Separate filtering gains from morphology |
| Main quality measures | Real-data water IoU/F1 and homogeneous-ROI ENL; separate synthetic PSNR | Match each claim to available ground truth |

The U-Net is a **water segmenter**, not a learned despeckler. Its outputs are masks/probabilities, so ENL and denoising PSNR are not applicable to those outputs. The required denoising comparison is provided by the processing pipeline, which is explicitly allowed by the problem statement.

## 2. Exact filtering contract

All methods preserve native shape. Convert documented power dB using `I = 10**(dB/10)`. Filter each polarization independently. Use the input validity mask, reflection at image borders, and the protocol's deterministic nearest-valid fill followed by invalid-mask restoration. Label validity is never a filtering input.

- **Raw:** identity in linear power.
- **Median:** power-domain windows `{3,5}`.
- **Lee:** power-domain windows `{5,7}`. For local observed mean `m`, population variance `v`, and effective looks `L`, estimate signal variance `s2 = max((v - m*m/L)/(1 + 1/L), 0)`. For `v>0`, use `w = clip(s2/v, 0, 1)`; otherwise use `w=0`. Output `m + w*(I-m)`. Accumulate local moments in float64, clip negative roundoff variance to zero, and return float32. Avoid an absolute variance floor that changes behavior when intensity is rescaled. Test constant and rescaled inputs. This is the documented multiplicative local-LMMSE variant, not Refined Lee.
- **Looks estimate:** per band, take the median `mean(I)**2/var(I)` across finite, nonconstant homogeneous **training** ROIs, lower-bounded at `1`. Freeze it before validation. Save ROI coordinates, counts, values and the resulting estimate. It is an effective estimate under the multiplicative approximation, not proof of independent physical looks. If no suitable training ROI exists, resolve the data-audit failure explicitly instead of silently assuming `L=1` or borrowing test ROIs.
- **Log-bilateral:** work in dB with window `5`, spatial sigma `2`, and color sigma `{1.5,3.0}` dB, then convert back to power. Do not perform per-image min-max stretching. Quantify radiometric mean change; do not claim unbiased intensity recovery.

The Lee expression follows the multiplicative moment relation `var(observed) = (1+1/L)*var(signal) + mean(signal)**2/L`; record this variant in results so another implementation can reproduce it. [Lee foundation](https://doi.org/10.1109/TPAMI.1980.4766994).

### MIDAL admission: one attempt, before full validation

The released scalar API in `mulog==0.0.4` is `mulog.midal_algorithm.run_midal`, with `mulog.gaussian_denoisers.run_autoscaled_bm3d`. Supply positive linear power as `sar_signal`, the frozen/known `number_looks`, and six ADMM iterations. It logs internally and returns power; do not supply amplitude or pre-logged data. [Author package](https://pypi.org/project/mulog/).

Cap dependency/setup investigation at **15 minutes**. Test shape, finite positivity, scale behavior, and a five-patch/two-band runtime pilot. Estimate the cost of **all** enabled real, synthetic and validation invocations, with a 50% timing margin. Admit only if that estimate fits **three minutes** and leaves the whole notebook below its total budget. This is a conservative engineering gate, not a published speed claim. Record actual runtime later.

If admitted, MIDAL replaces bilateral in the four-family primary comparison; keep one documented default configuration rather than searching its iteration count. If rejected for compatibility, terms, correctness or runtime, use bilateral and close the branch. Admission does not promise better scores.

Default six iterations imply about 1,200 BM3D calls for 100 two-band patches alone. The GPU does not establish acceleration of that package. MuLoG is CeCILL; BM3D has separate non-commercial binary terms. Neither is relicensed by our MIT file. [MuLoG metadata](https://pypi.org/pypi/mulog/json), [BM3D terms](https://webpages.tuni.fi/foi/GCF-BM3D/).

## 3. Exact segmentation and selection

Use the protocol's fixed grid: per-patch dB Otsu on VV or VH; or a shared fixed threshold from VV `{-20,-18,-16,-14,-12,-10}` / VH `{-28,-26,-24,-22,-20,-18}`. Low backscatter means water. These are bounded calibration candidates, not universal water thresholds.

For each common channel/rule candidate, choose each filter's small parameter setting by **pooled validation water IoU** with cleanup disabled. Then select the common channel/rule by the mean of those four pooled validation IoUs; break exact ties by lower measured validation compute time. When using fixed thresholding, the **same numeric threshold** must apply across all four denoisers. Otsu re-estimates from each image's unlabeled histogram by definition. Freeze all choices before final test scoring.

The primary filter table has exactly **four rows**, with cleanup disabled. Separately compare cleanup off/on for raw and the validation-selected filtered pipeline, deleting 8-connected water components smaller than 16 pixels. Do not fill holes. Keep the unchanged raw baseline visible even if filtering loses.

Select the filtered input for neural training using the best pooled validation water IoU among actual filters under the common rule, breaking ties by compute time. Do not choose it from ENL or test performance.

## 4. Exact learned architecture and training

One architecture, two input conditions; no attention, encoder, decoder or optimizer search:

- Input order `[VV,VH]`, in dB. Compute one mean/std vector over valid **raw training** pixels, then use it for both input conditions. Floor std at `1e-6`. Convert filtered power back to dB before standardization.
- Before neural training/inference, deterministically fill invalid SAR locations from the nearest valid SAR pixel within the source patch, separately and identically for both input conditions, before standardization and crop extraction. Keep network inputs finite and retain the original SAR validity mask for loss/scoring. Reject all-invalid patches. Label validity must never control input filling; a masked loss alone does not prevent NaNs from propagating through convolutions.
- U-Net widths `16,32,64,128`, with three max-pool stages. Each encoder/decoder block has two bias-free 3 x 3 padded convolutions, each followed by GroupNorm with eight groups and ReLU. Decoder uses bilinear upsampling (`align_corners=False`) to each skip tensor's spatial size and skip concatenation. A final 1 x 1 convolution produces one logit. No dropout or attention. Verify the implementation is below one million parameters; expected scale is approximately 0.49 million.
- Loss: `0.5 * BCEWithLogits + 0.5 * soft Dice loss`, over valid labeled pixels only. BCE is the valid-pixel mean. With sigmoid probabilities `p`, valid binary targets `y`, and sums over valid pixels across the batch, Dice loss is `1 - (2*sum(p*y)+1e-6)/(sum(p)+sum(y)+1e-6)`. Skip all-invalid training crops/batches; verify invalid labels never affect either term.
- Adam, learning rate `1e-3`, batch `8`, seed `42`, no scheduler search.
- One epoch is four 256 x 256 crops per training source patch: two uniform draws and two centered on randomly chosen valid water pixels when that source has water; otherwise all four are uniform. Clamp crop bounds within the source. Skip all-invalid draws identically across conditions and log actual updates. Flips and rotations by multiples of 90 degrees are the only augmentation.
- Train **two separate models**, raw and selected filtered, with matched initialization and crop/augmentation sequences, split, and maximum updates. Evaluate both at native resolution with sigmoid and fixed water threshold `>0.5`; ties are land.
- Maximum 20 remote epochs per condition, validation patience five, and a one-hour cap for the complete paired comparison. Save the checkpoint with highest pooled validation water IoU; ties retain the earlier checkpoint. Early-stopped conditions may use fewer updates; report actual counts rather than describing the executed update counts as identical.
- Start with one paired seed. Additional paired seeds `43,44` are permitted only within the same one-hour cap, with no new settings. Single-seed evidence remains single-seed evidence.

Four crop draws make the epoch definition explicit. On approximately 60 training patches with batch eight, that is about 30 updates per epoch before invalid-crop exclusions. Splits are created at source/event/scene level before drawing crops; a crop cannot cross partitions.

This baseline is chosen for controlled adaptation to the supplied two-channel data and a small compute budget. It is not a claim that scratch learning always beats pretraining. Underfitting or worse segmentation after filtering is a valid result.

## 5. Models outside the locked deliverable

**UDL4FL is reserve only**, not a promised benchmark or fallback that must be implemented. Its actual release is MobileNetV2/U-Net++, with a binary land/water checkpoint, but stored `vh/vv` metadata conflicts with the author's `[VV,VH]` inference export. Validation-based order selection would be an adaptation, not proof of the original training order. Its wrapper mutates inputs while normalizing, and its default tiling differs from the paper's contextual overlap. These are avoidable uncertainties for the main experiment. [Checkpoint configuration](https://huggingface.co/isp-uv-es/udl4fl_models/blob/main/sm_unet_s1.json), [author example](https://raw.githubusercontent.com/kipoju/udl4fl/main/notebooks/run_in_gee_image.ipynb), [prediction source](https://raw.githubusercontent.com/kipoju/udl4fl/main/udl4fl/worldfloods_model.py).

TerraMind Tiny and CROMA are genuine radar-capable encoders, but adapting a head and validating their contracts is outside v1. Prithvi optical flood checkpoints do not match VV/VH. MERLIN needs complex data; SAR2SAR needs a preprocessing-domain audit; current SDS-SAR public inference uses a placeholder. Diffusion/Mamba novelty does not overcome missing compatible weights or a mismatched training protocol. The research review contains the source-level evidence.

There is **no further model search in v1**. Reopening an architecture requires a recorded scope change driven by an actual implementation failure or a new user request.

## 6. Scoring and finish criteria

- Freeze source-level splits before fitting or tuning; audit independent mask provenance and duplicate/overlapping crops.
- Primary real-data scores: pooled held-out water IoU/F1, fixed ROI power-domain ENL, radiometric mean change and runtime. Keep ENL's undefined/excluded ROI counts visible.
- Secondary macro water scores use the **same ground-truth-water-positive patch set for every method**. Report dry-patch false positives separately. Model-dependent exclusion sets must not create a favorable macro average.
- PSNR uses known synthetic references with shared mean-one Gamma corruptions and explicit range. It is not real-data denoising ground truth.
- The U-Net's segmentation table is separate from the four-row denoising table; do not put mask outputs through ENL/PSNR.
- A `full` Colab run includes enabled training, installation, data access, evaluation and exports. Start its neural allocation at no more than eight epochs per condition inside a shared six-minute cap. If that pair cannot fit, the classical full run is the compliant core.
- A `checkpoint-evaluation` profile may load remotely trained checkpoints but must say training occurred remotely. Its runtime cannot establish full training reproduction below 30 minutes.
- A shorter Colab training schedule is a separately reported experiment; it is not expected to reproduce the checkpoint or accuracy of a longer remote run. Exact reproduction claims require matching the recorded training configuration.

Research selection is complete. Actual subset provenance, usable ROIs, dependency compatibility, convergence and runtime are execution gates. None establishes a need for another broad literature search before starting Phase 1.
