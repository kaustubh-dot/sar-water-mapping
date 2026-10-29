# Supplied-set held-out results review

29 October 2026. Independent GPT-6.1 Sol review at xhigh of the frozen
supplied-first100 classical and neural evaluations.

**Decision: ACCEPT the recorded supplied-set results.** No unresolved P1/P2
scientific execution finding was identified. This closes the result-audit
gate for this experiment, with the exposure, mask-coverage and ENL limitations
below. It does not establish fresh Colab execution or a pristine project-level
blind test.

Both evaluations record clean source commit
`0cdb7874e3699cd1e6c0f68a98b5eea6c6e9ff50`; the scientific source files match
that commit and every recorded neural evaluation-source hash. Configuration,
manifest and split hashes match the accepted calibration and training chain:

- Configuration: `a04fc6e52b01dff1ddb2684d9b2a198963acd7a0d658404e11264779dea6843b`
- Manifest: `4c196542778daefb2f03b53634f8f0ef579f91851677c606d5ae77750ab93ea3`
- Splits: `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`

The neural runtime binds the accepted original training-report hash
`2bf40f37c37b46a08566dac1607f2949322168a60a6033eb78cb0d0b846e259b`
and both checkpoint file hashes from the
[training review](supplied_training_review.md). The corresponding local files
were rehashed. No old checkpoint, calibration transfer, retraining, parameter
selection or new neural inference entered this audit.

The 14 classical and seven neural public artifacts match their original local
outputs byte for byte; all 21 artifact-index entries verify. Exported
`config.json` files have SHA-256
`49cb0ff9bf2c77c3f85169bbdb0149e3fc51fabdb494122f2c215d83ec42bf62`:
they differ from the pinned input only by CRLF-to-LF normalization during
export. The runtime hashes correctly bind the original input bytes.

## Shared scoring population and native-mask recount

All methods retain all **31 frozen Ghana test IDs**. The reviewer independently
opened only their 62 source TIFFs, rechecked source-file/native-content hashes,
and reconstructed SAR validity from raster masks plus finite VV/VH samples.
Label validity was derived separately from its raster mask and `-1` codes.
No training or validation TIFF was opened during this result audit.

Every method scores the same **4,940,307 pixels**, including 144,891 water
pixels. All six methods use the same **15 ground-truth-water-positive macro
IDs**. The 15 scored dry patches contribute 2,066,885 dry pixels and have
separate false-positive summaries. `Ghana_26376` remains present with zero
scored pixels and undefined water metrics, rather than being dropped or
credited as perfect. `Ghana_24858` contributes only **484 scored pixels**;
its full image area is not treated as labeled ground truth.

All **186 primary per-patch rows** cross-sum to their saved pooled counts,
pooled metrics and fixed-set macro metrics. Undefined macro denominators,
no-valid counts, dry false-positive pixels/rates and fractions of affected dry
patches were independently recalculated. The four separate raw/Median
cleanup-ablation rows reproduce their saved JSON/CSV arithmetic and preserve
the same macro/scoring population; their cleanup-off summaries equal the
corresponding primary rows.

All **62 exported native neural masks** pass their recorded SHA-256, shape,
int8 land/water/invalid encoding and independent input/label/scoring-mask
checks. Direct boolean recount against the independently read truth reproduces
every raw/filtered per-patch TP/FP/FN/TN exactly. These masks were audited
without running a model.

## Accepted real-data measurements

The primary classical table has exactly four families, shared **VH below
−20 dB**, and cleanup disabled. Parameters remain raw identity, Median 5,
Lee 5, and log-bilateral window 5 / spatial sigma 2 / color sigma 3 dB.
See the [classical table](supplied_classical-v1/results_real.csv).

| Classical method | Pooled water IoU | Water F1 | Dry false-positive pixels |
| --- | ---: | ---: | ---: |
| Raw | 0.2771988739 | 0.4340731574 | 39,098 |
| Median 5 | 0.4135010817 | 0.5850735978 | 1,727 |
| Lee 5 | 0.4050834736 | 0.5765970225 | 1,094 |
| Log-bilateral | 0.3825381486 | 0.5533853066 | 6,580 |

The separate [neural table](supplied_neural-v1/results_neural.csv) preserves
native strict probability `>0.5`, no cleanup, matched architecture and the
accepted scratch-trained checkpoints. ENL/PSNR are correctly not applicable
to segmentation masks.

| U-Net input | Pooled water IoU | Water F1 | Dry false-positive pixels |
| --- | ---: | ---: | ---: |
| Raw VV/VH | 0.4207908518 | 0.5923332787 | 3,877 |
| Median-5 VV/VH | 0.4042517948 | 0.5757540012 | 11,487 |

Median preprocessing reduced pooled U-Net IoU/F1 in this single-seed run.
The negative learned result is retained. These frozen scores do not authorize
a rescue model or parameter search.

## ENL, synthetic controls and artifacts

The [five frozen ENL regions](supplied_heldout_enl_rois-v1.csv) produce exactly
**40 records** (five regions × two bands × four methods) and **eight
aggregates**. A bounded replay on those fixed regions, from three source
patches, independently recomputed positive-power population-variance ENL.
All numeric records agree within `5.30e-9` relative difference; every region
has 1,024 valid SAR pixels. Counts, finite/undefined status, medians and quartiles
agree with the saved tables.

These are visually interpreted **land** regions, not water ENL measurements.
Four regions are also fully land in valid manual labels. `supplied_enl_05`
has all 1,024 labels invalid, so its land tag remains the explicitly recorded
SAR-only visual interpretation. Label validity does not gate ENL; this region
must not be described as independently label-confirmed land. No water-region
ENL or broad unbiased-denoising claim is supported.

The separate [synthetic table](supplied_classical-v1/results_synthetic.csv)
contains **72 known-reference test records and eight means**. Every record
declares simulated backscatter, unit data range, fixed test phantom identities,
looks 1/4 and seeds 42/43/44; parameters match the saved synthetic-validation
selection. All PSNR values reproduce `-10*log10(MSE)`, and every nine-record
mean recomputes correctly. These values are not real-SAR clean-reference
measurements. The 248 radiometry rows' percentage changes also recompute.
All **124 classical PNG artifacts** pass filename coverage and PNG integrity
checks; this is file verification, not an assertion that every shoreline is
accurate.

Measured classical runner time is **59.3764 seconds**; neural checkpoint
evaluation took **9.0617 seconds**. Both correctly report that fresh Colab was
not verified. Remote paired training remains a separate 76.7675-second
measurement. Local audit evidence is retained at
`outputs/supplied_results_review_probe.json`; the successful focused probe
took 16.51 seconds. No broad test suite or new neural inference was run.

The internal event split is 29/40/31, all selected from upstream training
membership. Historical project training exposure is still 5/9/8 IDs across
the new partitions, including eight current test IDs. The recipe authority is
unverified. These results identify observed surface water on the stated
correlated sample; they do not establish unseen-geography superiority or
separate new flooding from permanent water.
