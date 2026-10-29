# Supplied calibration execution review

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**. Independent review dated
29 October 2026.

**Decision: ACCEPT supplied calibration v1 for subsequent paired scratch
training and frozen evaluation.** No P1/P2 findings remain. This accepts no
training result, held-out score or fresh Colab timing.

Reviewed [frozen configuration](../configs/supplied-calibrated-v1.json),
[validation record](supplied_calibration-v1/validation.json),
[candidate CSV](supplied_calibration-v1/candidates.csv),
[training looks](supplied_calibration-v1/training_looks.json), and the accepted
[source profile](supplied_source-v1.json). Execution used reviewed commit
`72ef16abaeaef1a0205de5654f302d52e4371487`. All seven recorded source-file hashes
match both that commit and the current files. No downstream scientific code or
locked grid changed.

- Independently reproduced all eight ROI/band records from the four fixed
  training regions, using only training imagery. All have 1,024 valid pixels
  and finite nonzero power variance. The frozen VV/VH median looks are
  `4.6020301257391925` / `2.582041888130562`; direct float64 moments agree within
  floating-point roundoff. ROI, manifest and split hashes agree across the
  initial inputs, looks, validation record and configuration. The looks-freeze
  timestamp precedes the calibration freeze.
- Verified all **98 unique saved candidates**: seven locked filter settings
  times 14 VV/VH common strategies, with cleanup disabled throughout. Every
  record contains exactly all 40 frozen India validation IDs, 8,788,754 scored
  pixels and 727,230 ground-truth-water pixels. All use the same 39
  water-positive macro IDs and report the one dry patch separately. Recomputed
  pooled scores from counts and macro scores from saved per-patch values;
  candidate CSV values agree exactly with JSON.
- Independently applied the documented selection/tie rule to the saved table.
  It reproduces **VH, shared fixed threshold −20 dB**, mean four-family pooled
  IoU `0.33921016078964483`, and **Median 5** as the filtered training input.
  Selected settings are Raw identity, Median 5, Lee 5, and bilateral window 5 /
  spatial sigma 2 / color sigma 3 dB. Constant-patch Otsu fallbacks are VV −14
  and VH −22 dB, correctly selected from the saved raw-validation grid.
- Separately re-read all 40 validation pairs and verified their file and
  portable decoded-source hashes. Recomputed only the four already selected
  outputs at native resolution, using independent boolean confusion counting.
  All pooled/per-patch/macro/dry summaries match exactly, as do the four
  separate raw/Median cleanup-ablation summaries. The unchanged 98-candidate
  search was not rerun, and no artifact or choice was rewritten.

| Frozen validation row | TP | FP | FN | TN | Water IoU |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 420851 | 656200 | 306379 | 7405324 | 0.3042083806 |
| Median 5 | 393182 | 371789 | 334048 | 7689735 | 0.3577572362 |
| Lee 5 | 355160 | 280497 | 372070 | 7781027 | 0.3524367215 |
| Log-bilateral | 409987 | 470028 | 317243 | 7591496 | 0.3424383049 |

The calibration's opened-source record is exactly the 40 validation sources
plus six training sources used by the ROI/pilot union; it records zero test
files. The reviewed loader rejects test membership. The independent replay
also guarded built-in, Path and rasterio file access against every held-out
TIFF name: **80 unique validation files, zero held-out files opened**. Training
ROI/filter diagnostics retain all 32 fixed region/band/method combinations.

Verified the full metadata source chain and rebased configuration paths with
the strict source verifier and the notebook identity guard. The internal
29/40/31 membership, 22 historical training exposures distributed 5/9/8,
unverified recipe authority and restriction on existing development checkpoints
remain explicit. Primary cleanup is false; synthetic controls and method grids
match the unchanged template. MIDAL remains unpiloted and unadmitted. No test
image/label, remote training or final scoring was used for this review.

| Accepted file | SHA-256 |
| --- | --- |
| `configs/supplied-calibrated-v1.json` | `a04fc6e52b01dff1ddb2684d9b2a198963acd7a0d658404e11264779dea6843b` |
| `reports/supplied_calibration-v1/validation.json` | `f44e04d7f1c8886ef106d0416d84618facf8fd391f493d3e7005f69a60d0714a` |
| `reports/supplied_calibration-v1/candidates.csv` | `f6501f8295d1237db560227a9053098bc7410153b7f4fe72f356856bc6d6e0d3` |
| `reports/supplied_calibration-v1/training_looks.json` | `97179626997d624aa1026320d950098af91f74a8e24abbfcd85e86b29ef1dac2` |
| `reports/supplied_source-v1.json` | `7c121d63328d90c1850b419647d6964131a6138d468e686c02d6ba1c5d93fbbe` |

Git attributes preserve these exact bytes. Recorded local CPU calibration time
is **260.463 seconds**, including a five-training-patch/seven-setting pilot;
validation search took 224.053 seconds. The one-setting cache is 83,886,080
bytes below its 100,000,000-byte cap, separately from source arrays/workspaces.
These are validation measurements on one event and a historically exposed
project subset. The modest validation scores are retained without rescue
tuning; they establish neither held-out superiority nor fresh Colab compliance.
