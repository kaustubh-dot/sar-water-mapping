# SAR speckle filtering and surface-water mapping

Development report, 29 October 2026. Organizer-subset acceptance and a fresh
Google Colab Run All remain open. This report describes measured upstream
development experiments, not a completed hackathon acceptance test.

## Question and data

Does reducing multiplicative SAR speckle improve water segmentation enough to
justify added computation and loss of detail? We compare four fixed processing
families on two-band Sentinel-1 VV/VH patches, and separately train one compact
U-Net architecture on raw versus validation-selected filtered inputs.

The organizer archive was unavailable. We selected exactly 100 upstream
Sen1Floods11 v1.1 hand-labeled pairs by label-blind hash ranking within official
train/validation/test partitions: 60/20/20 patches, each 512 by 512 pixels. All
200 object lengths, upstream MD5s and local SHA-256s were verified. Weak/Otsu
labels are excluded. Independent SAR and label validity masks control scoring;
valid zero dB is preserved. One training patch has no scored pixels and another
has only 484; neither was replaced after inspecting labels.

Seven touching cross-partition chip pairs and events shared between partitions
make this a **correlated official-subset development evaluation**. There is no
held-out-event or unseen-geography generalization claim. See the
[data review](development_data_review.md) for exact identities and limitations.

## Locked methods and selection

Convert power dB with `I = 10**(dB/10)`. Median and multiplicative local-LMMSE Lee
operate on power; bilateral filtering operates in dB and returns power. All
methods process VV/VH independently, fill missing SAR from the nearest valid SAR
pixel, reflect at borders and restore invalid locations. Label validity never
controls inference-time filling.

Six inspected homogeneous training ROIs produce effective looks 4.8593 for VV
and 4.0208 for VH, frozen before validation. These are approximate effective
noise estimates rather than independently measured physical looks. Bounded
validation evaluates 98 candidates. Each common channel/rule selects one
setting per family, then the mean of four pooled validation IoUs selects the
common rule. The frozen rule is **VV below -18 dB**, with Median window 5, Lee
window 5 and bilateral window 5/spatial sigma 2/color sigma 3 dB. Cleanup is
disabled in the primary comparison. Median 5 is the selected neural input.

Independent GPT-6.1 Sol xhigh review reproduced all 98 candidate records and four
cleanup records without opening held-out sources. Calibration version 1 had an
inconsistent ROI byte hash and is superseded; version 2 is accepted. A later
source-identity portability repair preserves every scientific choice, source
file and split; its provenance is recorded separately.

## Held-out classical results

Twenty test patches contain 4,505,202 scored pixels. The fixed macro-water set
contains 19 water-positive patches; one dry patch is reported separately.
These are water-class pooled metrics, not land/water mean IoU.

| Input | Water IoU | Water F1 | Precision | Recall | Compute, seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 0.6084 | 0.7565 | 0.9133 | 0.6457 | 1.78 |
| Median 5 | 0.6304 | 0.7733 | 0.9507 | 0.6517 | 7.49 |
| Lee 5 | 0.6070 | 0.7554 | 0.9566 | 0.6242 | 3.10 |
| Log-bilateral | 0.6304 | 0.7733 | 0.9400 | 0.6568 | 9.83 |

Timing covers filtering, segmentation and scoring on the recorded Windows CPU,
excluding figures and diagnostics. The recorded runner subtotal, including
the separate synthetic experiment and 80 diagnostic figures, was 130.44 seconds.
Its clock precedes three final metadata writes and excludes earlier installation,
access and calibration; this is not a complete fresh Colab runtime. Details are in
[the saved outputs](classical_results-v1/results_real.csv) and
[runtime record](classical_results-v1/runtime.json).

Median improves pooled IoU by 0.0220 over raw. Lee slightly reduces it despite
increased smoothness. Median and bilateral have almost equal pooled scores;
one small correlated subset and one run do not establish statistical superiority.
Median cleanup lowers IoU from 0.6304 to 0.6293, so morphology gains cannot be
assumed. No method changes follow these held-out observations.

## ENL and synthetic PSNR

Five fixed raw-selected 32 by 32 held-out regions are used identically across
methods: three visually homogeneous land ROIs and two river ROIs. VV median ENL
on land rises from 5.21 raw to 15.18 Median, 18.24 Lee and 11.83 bilateral.
On water it rises from 3.30 to 11.63, 11.53 and 6.92 respectively. Each class has
very few regions; ENL is a homogeneity-dependent diagnostic, not proof that
scene detail is preserved. Per-band values, quartiles and undefined counts are
saved in [the ENL table](classical_results-v1/enl_summary.csv).

The separate synthetic experiment uses known procedural power references,
independent Gamma speckle and shared corruptions. Three held-out phantom
identities times three noise seeds give nine measurements per method/looks.
Settings are selected on synthetic validation, separately from real-data choices.

| Looks | Raw PSNR, dB | Median | Lee | Log-bilateral |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3.55 | 12.28 | 18.13 | 7.18 |
| 4 | 9.53 | 19.39 | 22.39 | 16.17 |

Synthetic Lee selects window 7. These PSNRs use `data_range=1.0`, do not clip
Gamma observations, and never treat noisy real SAR as clean ground truth.
Procedural independent noise does not reproduce all properties of GRD SAR;
Lee's synthetic advantage does not establish the best real water mapper.

## Failures and interpretation

The [India comparison](figures/India_591317_median.png) shows a broad river
retained but narrow water channels and some shoreline pixels missed. The
[Paraguay comparison](figures/Paraguay_913449_median.png) shows thin river
structure lost by filtering/thresholding. Ratio images can retain scene
structure, indicating removed signal as well as speckle. Homogeneous-region
ENL alone would conceal these losses. Shadow, rough water, mixed pixels and
label/acquisition mismatch remain plausible errors; the experiments do not
identify each cause independently.

Predictions describe observed surface water. Distinguishing newly flooded from
permanent water requires additional information. Small data, correlated splits,
limited ROIs and hardware-dependent timing constrain conclusions.

## Learned comparison and remaining acceptance

The reviewed 487,857-parameter VV/VH U-Net uses shared raw-training dB
normalization, matched initialization/crops, masked equal BCE/Dice loss, Adam
0.001, batch 8, seed 42 and fixed probability threshold above 0.5. The remote
pair completed in **122.06 seconds**, including 12.86 seconds of input
preparation, on an RTX 4000 Ada. It remained within the shared hour cap.

| Training input | Executed epochs / updates | Best validation epoch | Test water IoU | Test water F1 |
| --- | --- | ---: | ---: | ---: |
| Raw VV/VH | 11 / 327 | 6 | 0.5855 | 0.7385 |
| Median-5 VV/VH | 13 / 387 | 8 | 0.5346 | 0.6968 |

Both conditions stopped after five stale validation epochs. Their actual
updates differ; initialization and each shared epoch's crop plan match.
Independent review verified all 13 crop plans, raw-training normalization,
checkpoint hashes and all 40 native validation confusion matrices. Only seed
42 was run. Peak PyTorch CUDA allocation was 964,296,704 bytes; CPU peak RSS was
not measured. Original environment versions are preserved.

The frozen native-resolution checkpoint evaluation took a recorded 6.85-second
subtotal on the GPU, including native-mask exports and figures but preceding
final metadata writes. This excludes training. The raw U-Net underperforms the
classical Median baseline on pooled IoU, and Median preprocessing reduces the
U-Net's IoU further. The negative learned result is retained; no architecture,
threshold or test-based rescue search follows. Mask outputs receive neither
ENL nor denoising PSNR. Small data and one seed do not establish a universal
ranking of learned and classical approaches.

Independent result review recomputed all 40 exported native-mask confusion
matrices against the original held-out labels and validity masks, along with
pooled scores, the fixed 19-patch water macro set and one dry patch. The
evaluation process did not record deterministic/TF32 backend flags; these are
measured-run results without a claim of bitwise inference replay across setups.

The approved [development checkpoint release](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1)
provides the small weights/metadata bundle outside Git. Its SHA-256 is
`b70dc5117a21ecac5b3b0e2ad9fc06f960a727370c81892089ac27b894100238`.
The [reproduction instructions](../docs/REPRODUCING.md) distinguish frozen
checkpoint evaluation from new training and fresh classical calibration.

The full classical notebook also completed all ten code cells in a separate
Linux kernel: **91.78 seconds** through archive creation and checksum, using
cached TIFFs, an existing clean clone and a preinstalled notebook kernel.
It reproduced all four held-out classical confusion counts exactly. This
smoke run does not measure fresh installation, uncached access or Colab
hardware. See the [execution evidence](notebook_smoke_summary.json).

Remaining acceptance gates are the organizer subset and a measured fresh
Colab run below 30 minutes. Remote training and checkpoint-only inference
remain separate timings. The full classical notebook is the bounded fallback.
No final submission tag is issued until its acceptance evidence exists.

Dataset attribution: Bonafilia et al. (2020),
[Sen1Floods11](https://github.com/cloudtostreet/Sen1Floods11).
Method sources and exclusions are recorded in the
[research review](../docs/RESEARCH_REVIEW.md) and
[implementation lock](../docs/IMPLEMENTATION_LOCK.md). Original project code is
MIT; dataset and other third-party materials retain their own terms.
