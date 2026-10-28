# Evaluation Protocol

Version 1.1, final audit 28 October 2026. This is a planned protocol; no experiment has been run. The [implementation lock](IMPLEMENTATION_LOCK.md) fixes architecture and training details.

## 1. Data contract and target

Input is a paired SAR image and independent surface-water mask. Upstream Sen1Floods11 provides hand-labeled data and threshold-generated labels in different directories. Record which is actually in the 100-patch subset. Use hand labels for primary segmentation evaluation; agreement with Otsu-generated masks is not independent evidence that Otsu is accurate. [Upstream structure](https://github.com/cloudtostreet/Sen1Floods11/blob/master/docs/README.md).

Audit dimensions, CRS/transform when present, band identity, numeric units, nodata, and label semantics. The adapter must explicitly declare `db` or `linear_power`; do not guess only from value signs. Upstream uses VV/VH dB and labels `-1/0/1`, but the supplied subset can differ. Reject unknown codes rather than silently remapping them. [Upstream format](https://github.com/cloudtostreet/Sen1Floods11).

The binary target is **observed surface water**, including permanent water where labeled. These observations alone do not establish which pixels were newly inundated. Urban double bounce, vegetation-covered flooding, radar shadow, rough water, and acquisition/label misalignment are expected failure modes; examples must be discussed rather than hidden.

## 2. Split and provenance

1. Respect supplied organizer split membership. If absent, use upstream official membership for identified upstream chips when it leaves usable partitions.
2. Otherwise split approximately 60/20/20 by event; use scene groups if event splitting is impossible. If there is only one scene, use spatially separated blocks and disclose within-scene evaluation.
3. If spatial metadata is unavailable, use seeded patch-level membership and explicitly limit claims to that subset. This is a fallback, not evidence of unseen-geography generalization.
4. Keep neighboring or overlapping crops, exact image duplicates, and all augmentations of a source patch in one partition. Audit image hashes and geospatial overlap where metadata permits. Report any supplied split conflicts before treating them as independent.
5. Freeze membership before parameter selection. Fit normalization and noise estimates on train; select parameters on validation; inspect final test metrics only after configuration freeze.

Save `patch_id,image_path,mask_path,event_id,scene_id,split,image_sha256,mask_sha256,units,label_source` in the manifest. Missing metadata is stored as an explicit missing value with its source limitation in the audit. Group constraints take precedence over exact 60/20/20 counts.

Pretrained weights have separate provenance: model/version, original training datasets, known benchmark overlap, URL/hash, license, adapter, and whether upstream Sen1Floods11 test chips may have been seen. Unknown pretraining overlap remains unknown; such results cannot support a clean no-leakage generalization claim.

## 3. Numeric domains and invalid pixels

For calibrated power `I`, `I = 10 ** (dB / 10)`. Amplitude is `A = sqrt(I) = 10 ** (dB / 20)`. Lee and ENL operate on power. The neural adapter must follow its own amplitude/power contract, scaling, and normalization; never feed dB directly to an amplitude model. [Earth Engine SAR units](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD).

Use float32 arrays. Preserve a SAR validity mask derived from raster metadata and finite values. `0 dB` is valid. Label validity is used only for training/scoring, never as an inference-time input feature. Score on the intersection of valid SAR pixels and label codes `{0,1}`.

For filtering, fill invalid SAR locations from the nearest valid input pixel using a deterministic distance transform, filter, then restore their invalid mask. Reject all-invalid patches. Record boundary handling and do not interpret restored invalid pixels as land. This simple imputation rule is a baseline limitation near large missing regions.

Before neural training/inference, apply the same SAR-only nearest-valid fill to raw and restored filtered inputs within each source patch, before standardization and crop extraction. Require finite network inputs and keep the original SAR mask for loss/scoring. Never use label validity for input filling. Masking the loss alone cannot prevent convolutional propagation of NaNs.

## 4. Controlled comparisons

Primary real-data denoisers: raw, Median, multiplicative Lee, and log-domain bilateral. Scalar MIDAL + BM3D can replace bilateral if its bounded feasibility pilot passes, keeping four primary families. The primary learned experiment is compact VV/VH U-Net segmentation on raw versus selected filtered input, in a separate downstream table. UDL4FL is reserve only and excluded from the locked deliverable.

Apply the same channel, threshold rule and validity mask to each denoiser in the primary filter-isolation table, with cleanup disabled. For each common channel/rule candidate, select each filter's small-grid setting by pooled validation water IoU. Select the common strategy by the mean of the four pooled validation IoUs, breaking exact ties by lower measured validation compute time. When a fixed threshold is selected, the same numeric threshold applies across denoisers. Do not tune on test.

Segmentation candidates are per-patch Otsu on dB and a fixed dB threshold calibrated on validation. The fixed grid is VV `{-20,-18,-16,-14,-12,-10}` and VH `{-28,-26,-24,-22,-20,-18}`. Water means intensity below threshold. The grids are initial engineering choices, not universal physical water thresholds. A change prompted by the data audit must be recorded before final configuration freeze.

Otsu computes a threshold from each input image at inference without labels; this is not test-label tuning. It can split a unimodal all-land image into artificial classes. For a constant patch, use the train/validation-calibrated fixed threshold and record the fallback. For all-invalid patches, return invalid without computing a threshold.

Separate cleanup ablation: none versus deleting 8-connected water components with fewer than 16 pixels, treating invalid pixels as barriers, for raw and the validation-selected filtered pipeline only. No hole filling. Preserve both outputs so removal of narrow or tiny real water bodies remains visible. The primary four-row denoiser table always has cleanup disabled.

Also save the raw baseline with identical cleanup to distinguish denoiser gains from morphology gains. More elaborate local thresholding, ensembles, or ancillary terrain masks require a documented scope change.

For the compact U-Net, use the same raw-training-set normalization, architecture, initialization and crop/augmentation sequences across separately trained raw/filtered conditions. Fix sigmoid water threshold at `>0.5`; no neural threshold search. Select each best checkpoint by pooled validation water IoU, retaining the earlier checkpoint on a tie. Input and label validity control scoring; predictions never change the scored-pixel set.

## 5. ENL on real SAR

For a homogeneous positive-power region with `n >= 2`, compute `ENL = mean(I)^2 / var(I)`, using population variance (`ddof=0`). Compute it per band; do not average VV/VH pixels into one ENL estimate.

Before inspecting filtered results, choose up to five fixed 32 x 32 homogeneous rectangles per selected patch, using the raw image and optional class annotation for evaluation only. Record coordinates and suitability in `reports/enl_rois.csv`; use exactly the same regions across methods. Prefer regions wholly within valid water or homogeneous land, away from boundaries. Do not compute ENL over the entire heterogeneous patch.

If fewer usable regions exist, report actual counts. A zero-variance region gives undefined/infinite ENL; store an explicit status and null numeric value, not a huge epsilon-generated win. Aggregate finite ROI values with median and interquartile range, separately by band and class where counts permit.

A flat blurred image can have excellent ENL. Inspect radiometric mean changes, shoreline detail, and the power ratio `raw / filtered` alongside it; visible scene structure in the ratio can indicate removed signal. Ratio statistics are diagnostic because real GRD speckle may be correlated. [Gomez et al., 2017](https://arxiv.org/abs/1704.05952).

## 6. PSNR: a separate synthetic experiment

Real SAR patches do not provide a clean backscatter reference. Do not compute a denoising PSNR against the original speckled patch, a water mask, or a Lee-filtered proxy and call it ground truth. The PSNR API requires a reference and an explicit data range for controlled float comparisons. [Metric documentation](https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.peak_signal_noise_ratio).

Create 12 deterministic 256 x 256 procedural backscatter phantoms in `[0.01,1.0]` with homogeneous areas, narrow water-like structures, sharp edges, and known textures. Divide identities 6/3/3 into train/validation/test before corruption. These are synthetic test patterns, not realistic clean Sentinel-1 targets.

Use `Y = X * N`, with `N ~ Gamma(shape=L, scale=1/L)`, for `L in {1,4}` and noise seeds `{42,43,44}`. Each method receives identical corruptions. Known `L` is supplied consistently to methods that use it; real-data estimated looks are evaluated separately. Freeze synthetic settings using only the synthetic validation identities, separately from real-data segmentation selection.

Score on linear power with `data_range=1.0`: `MSE = mean((X - X_hat)^2)` and `PSNR = 10 * log10(1.0 / MSE)`. Do not clip corrupted observations to `[0,1]`, since Gamma realizations can exceed that range. Do not change the range or stretch each output separately to inflate PSNR. MSE zero yields positive infinity with an explicit status.

Report the raw/noisy baseline and mean PSNR per `L`, with per-phantom/per-seed results. The noise seeds are repeated measurements, not independent geographic samples. Simulated independent Gamma noise does not capture every property of terrain-corrected GRD; improvements here do not establish real-data superiority.

## 7. Water segmentation metrics

Accumulate `TP`, `FP`, `FN`, and `TN` over valid pixels. Water IoU is `TP/(TP+FP+FN)`; water F1 is `2TP/(2TP+FP+FN)`; precision is `TP/(TP+FP)`; recall is `TP/(TP+FN)`.

Primary headline: pooled water IoU and F1 over the held-out subset. Also report per-patch values, macro water means over a fixed ground-truth-water-positive patch set, event/group summaries where available, and dry-patch false positives. The macro patch set must be identical across methods. Do not substitute land-plus-water mean IoU for water IoU without relabeling it.

If ground truth and prediction both contain no water, per-patch water IoU/F1 are undefined: store null and report the count. If ground truth has no water but predictions contain water, the per-patch IoU/F1 are zero. Exclude all ground-truth-water-empty patches from the secondary macro water mean for every method, regardless of prediction, and report their false-positive pixels, false-positive rate over valid dry pixels, and fraction of dry patches with any false positives separately. Their confusion counts still contribute to primary pooled scores. Precision/recall denominators of zero are null; retain all confusion counts.

No valid scored pixels means no score, not perfect performance. Pixel accuracy is optional and never the primary result because land can dominate. With this small subset, report improvements as measured differences rather than declaring statistical superiority from one seed.

## 8. Runtime and artifact requirements

Measure with a monotonic clock. Record runtime type, CPU/GPU, memory, dependency versions, seed, configuration hash, commit SHA, subset hash, actual patch count/resolution, setup/download time, per-method compute time, scoring/plotting time, and total wall time.

The final fresh Colab Run All must finish in **under 30 minutes**, including setup and documented data access. Include validation, synthetic evaluation, neural training if enabled, final scoring, and exports. No hidden precomputed predictions. Separately report any offline training represented by pretrained weights.

Remote GPU training is allowed for development. Record its independent compute time, data/split identity, seeds and checkpoint provenance. A notebook that loads these checkpoints is explicitly `checkpoint-evaluation`; it must not be described as full training reproduction. A `full` Colab profile includes training inside its measured limit. If the judging rule requires full training, validate that profile or rely on the classical core; a fast inference-only run cannot substitute for it.

If Colab uses a shorter training schedule than the remote run, report it as a separate budgeted experiment with its own results. It does not reproduce the longer run's weights or accuracy merely because the architecture matches.

Save real and synthetic tables separately, plus per-patch metrics, finite ENL ROI values/statuses, mean-intensity changes, raw/filtered ratio examples, and before/after visual comparisons using shared display limits. Label each neural result as denoising or segmentation; segmentation-only models receive `not applicable` for ENL/PSNR.

No numeric result belongs in the README or final report until it is traceable to saved outputs from a recorded run.
