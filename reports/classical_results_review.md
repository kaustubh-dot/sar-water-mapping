# Frozen classical results review

Independent review dated 29 October 2026 of `outputs/final-classical-development-v1/`, using the accepted calibration in `configs/development-calibrated-v2.json`.

**Decision: ACCEPT the scientific classical results as a correlated upstream official-subset benchmark.** Counts, water metrics, cleanup separation, fixed-region power ENL, radiometry, and separate known-reference synthetic PSNR passed independent verification. This acceptance does not close Phase 6: organizer-specific data and a complete fresh Colab run with its required runtime/resource evidence remain open. No frozen choice was changed, no real-data selection was rerun, and no GPU action was performed by this reviewer.

## Verification evidence

The focused command completed with **6 passed, 3 deselected in 16.86 seconds**:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_evaluate.py -k 'not notebook' --basetemp=outputs/pytest-classical-results-review
```

Independent read-only verification then checked all 40 held-out source-file hashes and all 20 decoded-SAR identities against the frozen manifest, and recomputed the four fixed pipelines at native 512 x 512 resolution. It derived threshold predictions and confusion counts directly, using the intersection of SAR validity, label validity, and valid label codes. All **80 per-patch confusion records** matched exactly. All four methods score the same **4,505,202 pixels**, including **689,313 ground-truth water pixels**, across 20 held-out patches. The same 19 water-positive patches form every macro mean; the single dry patch is `Ghana_97059`. Its counts remain in the pooled scores and its false positives are reported separately. There are no no-valid-pixel test patches.

The verifier independently labeled 8-connected predicted-water components and removed components below 16 pixels for the raw/Median cleanup ablation. Its aggregate counts matched all four saved off/on rows. Primary rows contain no cleanup. All **40 ENL records**, **16 band/class summaries**, and **160 per-band radiometry records** matched recomputation; ROI ENL was also checked directly as power mean squared divided by population variance. Real CSV tables agree with their JSON records.

The synthetic files contain 126 validation records, eight saved choices, 72 test records, and eight test summary rows. Saved settings maximize validation mean PSNR among the locked settings. Test identities are `phantom_09` through `phantom_11`, with looks 1/4 and seeds 42/43/44. The reviewer recomputed all 72 test estimates under their already-saved settings and independently calculated MSE and PSNR using range 1.0. All matched. Gamma-corrupted values exceed 1.0 and are not clipped. Synthetic observations/references were not mixed into the real-data table.

Runtime identities match the accepted configuration, manifest, splits, and preselected ROI CSV. The runtime records commit `f9f6e56284caed9fed8d5bb7e0c806d40782f8cd` and truthfully reports a dirty working tree. Independent byte comparisons confirmed that `evaluate.py`, `benchmark.py`, `data.py`, `filters.py`, `metrics.py`, `segment.py`, and `synthetic.py` all exactly match that recorded commit. Thus the dirty flag does not conceal a changed scientific implementation in the reviewed outputs.

## Primary held-out results

Every row uses **VV, fixed -18 dB, water below threshold, cleanup off**. Parameters remain those chosen on validation: Median window 5, multiplicative Lee window 5 with training-estimated looks, and log-bilateral window 5 / spatial sigma 2 / color sigma 3 dB.

| Method | Pooled water IoU | Water F1 | Macro water IoU | Water recall | Dry FP pixels / 27,394 | Primary compute seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Raw | 0.608415 | 0.756539 | 0.377215 | 0.645730 | 115 | 1.783 |
| Median | 0.630412 | 0.773316 | 0.393235 | 0.651723 | 72 | 7.490 |
| Lee | 0.606972 | 0.755424 | 0.374739 | 0.624172 | 46 | 3.097 |
| Log-bilateral | 0.630374 | 0.773287 | 0.397975 | 0.656802 | 102 | 9.827 |

Dry-patch false-positive rates are respectively 0.004198, 0.002628, 0.001679, and 0.003723. Every method makes at least one false-positive prediction on the one dry patch, so the fraction of dry patches with false positives is 1.0 for all four methods. This is one dry example, not a broad dry-scene specificity estimate.

Median improves pooled IoU by about 0.0220 over raw, but its held-out advantage over log-bilateral is only 0.0000382. These small-subset differences do not establish statistical superiority. The selected neural input remains Median because of the prior validation decision, not because of these test values. **Lee slightly underperforms raw**, despite higher ENL and strong synthetic PSNR.

Cleanup changes raw IoU from 0.608415 to 0.611348, removing 14,093 false-positive pixels but also 6,470 true positives. **Median cleanup lowers IoU from 0.630412 to 0.629297**: it removes 1,275 false positives and 1,597 true positives. Preserve this negative ablation; it is not evidence to enable cleanup or retune the frozen primary policy.

## ENL, radiometry, and figure inspection

The five preselected 32 x 32 regions are three Ghana land regions and two India river regions, spanning four patches. Their source CSV hash matches the runtime. The raw-only preselection record and inspection crops predate filtered scoring; the class tags are visual interpretations, not a new label set. Exactly the same rectangles are scored across methods and bands. All 40 method/band/ROI records have 1,024 valid SAR samples and finite `ok` status; there are zero undefined records. Band/class counts are three land and two water ROIs, with the two water regions sharing a patch. These are limited, correlated homogeneous-region diagnostics.

| Method | Median ENL VV land | VV water | VH land | VH water |
| --- | ---: | ---: | ---: | ---: |
| Raw | 5.215 | 3.304 | 4.222 | 1.577 |
| Median | 15.176 | 11.627 | 14.481 | 4.968 |
| Lee | 18.242 | 11.530 | 14.201 | 4.299 |
| Log-bilateral | 11.831 | 6.925 | 9.415 | 2.489 |

The saved summaries also retain quartiles and finite/undefined counts. Higher ENL alone does not establish faithful signal preservation. Median decreases the median patch mean power by **6.41% VV / 6.06% VH**; its largest VV mean reduction is **24.62%**. Log-bilateral decreases median means by **5.34% VV / 5.56% VH**. Lee's median mean reductions are **0.80% VV / 0.75% VH**. These measured shifts prohibit an unbiased-intensity-recovery claim for these outputs.

There are 80 aligned two-band figure files. The reviewer opened `India_591317_median.png`, `Ghana_97059_median.png`, `Mekong_1443339_median.png`, `Pakistan_694942_log_bilateral.png`, `Ghana_313799_median.png`, `Mekong_254910_median.png`, and both `Paraguay_913449_raw.png` and `Paraguay_913449_median.png`, plus the original held-out ROI crops. Raw and filtered displays share per-band raw-derived limits. Masks and error maps are aligned; invalid scoring regions are masked; titles identify red false positives and blue false negatives. Ratio panels use linear power raw/filtered with the same 0–2 range.

Concrete negative examples must remain visible in the report/demo:

- **Paraguay_913449:** the narrow river is visible in SAR but becomes fragmented in the Median prediction. The river outline is also visible in the raw/Median ratio, indicating removed scene structure. Water recall falls from 0.2130 raw to 0.1013 Median; IoU falls from 0.1899 to 0.0995. The higher ENL elsewhere does not excuse this detail loss.
- **Ghana_313799:** Median detects only 25 of 14,933 scored water pixels, with IoU 0.001674. The false-negative map exposes the near-total miss of labeled channels and water bodies. This is a severe failure of the fixed-intensity pipeline on this patch; the figures alone do not establish whether vegetation, backscatter physics, timing, or annotation limitations caused it.
- **Mekong_254910:** Median misses all 135 scored water pixels and produces 3,058 false positives, giving IoU zero. Predictions in label-invalid regions remain visually present but do not enter scoring. Do not call this a correct all-land case.
- **India_591317 and Mekong_1443339:** broad dark water is captured, while the error maps retain missed narrow channels and boundaries. Strong pooled scores do not mean complete shoreline recovery.
- **Pakistan_694942:** the log-bilateral figure shows both missed labeled river pixels and false positives elsewhere. Smooth-looking imagery does not guarantee a complete water mask.

## Event summaries supplement the per-patch exports

The runner exports patch counts but has no separate event-summary file. To make the available group evidence explicit, the reviewer pooled the saved patch confusion counts by the frozen manifest's event IDs. These are descriptive subsets of the correlated official split, not held-out-event tests.

| Event | Raw IoU | Median IoU | Lee IoU | Log-bilateral IoU |
| --- | ---: | ---: | ---: | ---: |
| Ghana | 0.183720 | 0.177201 | 0.173998 | 0.180906 |
| India | 0.711061 | 0.723176 | 0.712696 | 0.726145 |
| Mekong | 0.716523 | 0.728100 | 0.696926 | 0.727886 |
| Nigeria | 0.636686 | 0.673339 | 0.625524 | 0.666197 |
| Pakistan | 0.311653 | 0.357246 | 0.346938 | 0.352269 |
| Paraguay | 0.189945 | 0.099466 | 0.081680 | 0.161509 |
| Somalia | 0.166895 | 0.123046 | 0.104969 | 0.145940 |
| Spain | 0.269400 | 0.254171 | 0.233477 | 0.275318 |
| Sri-Lanka | 0.769841 | 0.799346 | 0.782464 | 0.800703 |
| USA | 0.415614 | 0.610726 | 0.605793 | 0.556387 |

Median loses to raw in Ghana, Paraguay, Somalia, and Spain. Report the mixed group behavior alongside the pooled gain.

## Separate synthetic results

| Method | Mean test PSNR, L=1 | Mean test PSNR, L=4 |
| --- | ---: | ---: |
| Raw/noisy | 3.5523 dB | 9.5304 dB |
| Median | 12.2802 dB | 19.3913 dB |
| Lee | 18.1313 dB | 22.3877 dB |
| Log-bilateral | 7.1765 dB | 16.1701 dB |

Each cell averages three fixed test phantom identities times three noise seeds. Synthetic validation selects Median window 5, Lee window 7, and bilateral color sigma 3 dB for both known looks values. These synthetic Lee settings deliberately differ from the real-data Lee window 5 choice. Known-reference synthetic success did not imply a real-water-segmentation win. No real noisy SAR was treated as clean ground truth.

## Runtime limits and remaining evidence

The runtime truthfully identifies a **local Windows CPU development evaluation**, seed 42, Python 3.14.3, dependency versions, no accelerator use, no training, and `fresh_colab_verified=false`. Its recorded runner subtotal is **130.44 seconds**, including 2.93 seconds loading/verifying, 118.28 seconds real evaluation/figures, and 9.00 seconds synthetic work. External setup is explicitly zero. Primary compute timings exclude cleanup, diagnostics, and plotting, which are recorded separately. This is not installation/download/calibration/training time or a fresh Colab end-to-end measurement.

**Remaining runtime reporting gap:** no memory or peak-memory measurement is present in this run. The runner samples its elapsed subtotal before the final runtime/environment/configuration metadata writes. Consequently its elapsed field is not a complete fresh-workflow total through every final artifact. Preserve this run as valid scientific development evidence; collect the full runtime/resource checklist and authoritative post-export total in the required fresh Colab execution before closing Phase 6. Do not retroactively invent a memory measurement or infer the challenge budget from 130.44 seconds.

The accepted data remain the upstream substitute, with shared events and seven cross-partition touching pairs. Organizer-subset acceptance, independent-geography claims, statistical superiority, permanent-versus-new flood separation, neural results, and fresh Colab feasibility are not established here. The appropriate next work is completion of the already-authorized execution gates, without tuning from these test labels.

## Reviewed output identities

| File under `outputs/final-classical-development-v1/` | SHA-256 |
| --- | --- |
| `results_real.json` | `9ecfac6dddc6267ca515efebea9ae2a977ba70f4a80e336ab713a2dbaa887a5c` |
| `results_real.csv` | `9898e195c14797d7e6af142100ee665a7423878c0a9d9538c6dfd7fa456384f9` |
| `per_patch_real.csv` | `f2e4c2bedfb96e41ad3ae809152d9fd5787d2d332f4544c197e6d8f748a2e698` |
| `enl_rois.csv` | `a3fa282e56ea50f31dc615461dc5272a9a120633227ef709ba27027f9d8f8fa8` |
| `results_synthetic.csv` | `1402065b617483332c322d4b68180992792587151df0aa9d054eeab9617c092e` |
| `runtime.json` | `a85d7f60c2527b58e9fa2e5830ddb34cca21526e989b4b50b462978587c00668` |

The 14 small original output files are also preserved in `reports/classical_results-v1/`; independent byte comparisons confirmed every saved copy equals its reviewed original. Its artifact index records the retained evidence and representative figures. Full generated arrays/figure collections remain outside Git. This report records evidence without changing the frozen configuration or original result bytes.
