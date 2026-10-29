# Frozen neural held-out results review

29 October 2026. Independent GPT-6.1 Sol review at xhigh of `outputs/final-neural-development-v1/`, after the [completed-pair training review](phase5_execution_review.md) released the checkpoints for frozen held-out evaluation.

**Decision: ACCEPT the recorded neural checkpoint-evaluation results.** All persisted predictions, validity masks, confusion counts, aggregate scores, and checkpoint/configuration/source bindings passed independent verification. The lower score after Median preprocessing is an accepted negative result. No threshold, filter, checkpoint, architecture, split, or training setting was changed. No scientific inference or training rerun was launched by this reviewer.

This accepts one seed on the correlated upstream development subset. It does not establish organizer-subset acceptance, unseen-event/geography generalization, statistical superiority, bitwise replay across inference backends, or fresh Colab feasibility. Phase 6's fresh-runtime gate remains open.

## Fresh verification

The focused command completed with **8 passed in 19.16 seconds**:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_neural_evaluation.py --basetemp=outputs/pytest-neural-results-review
```

These fixtures cover checkpoint and configuration preflight before held-out access, separate input/label masks, native int8 exports and their hashes, independent confusion recounting, fixed macro membership and dry false positives, and separation of native-export time from inference/scoring time. They also reject incomplete training, changed normalization/filter provenance, changed configuration, and changed held-out source bytes.

A separate actual-artifact check verified all 40 original held-out image/mask file hashes and read their native input and label validity masks directly. It verified every entry of `native_predictions.csv` against its `.npz` bytes, with pickle loading disabled. Exactly **40 distinct condition/patch artifacts** exist: raw and filtered predictions for each of the same 20 held-out identifiers. Every prediction has native **512 x 512** shape and int8 dtype, uses only `{0,1}` on SAR-valid pixels, and uses `-1` on SAR-invalid pixels. Every stored `input_valid`, `label_valid`, and `score_valid` boolean array exactly matches the original source-derived masks. Label-invalid pixels do not become inference-invalid pixels or scored land.

Independent boolean recounting from each persisted prediction and the original labels exactly reproduced all **40 per-patch confusion matrices**, both pooled matrices, per-patch IoU/F1/precision/recall, macro means and undefined counts, and dry-patch diagnostics. CSV values agree with JSON. Both conditions score **4,505,202 pixels**, including **689,313 ground-truth water pixels**, on the same source-derived validity intersections. They share the same **19 ground-truth-water-positive macro patches**. The one dry patch, `Ghana_97059`, contributes to pooled counts and remains outside both macro means. Neither condition has a no-valid-pixel patch.

The seven small files preserved under `reports/neural_results-v1/` are byte-identical to the reviewed original outputs and match their artifact index. The complete 40-file native predictions remain outside Git. This review verified the originals referenced by that index rather than inferring their correctness from reported metrics alone.

## Frozen model and execution provenance

Training and evaluation both record clean source commit **`61b09f9bfa61114d83bd7be19eba3de67d5621db`**. All seven recorded evaluation-source SHA-256 values independently match the current reviewed source and that commit: evaluator, model, training adapter, data loader, filters, metrics, and classical configuration validator.

The executed v3 configuration SHA-256 is `3b54e43f217ad80e2c029554289acd483538ecbd09837bcfb9c9b689a653f4af`; its v4 source-identity manifest and split hashes match the accepted migration. The filtered condition is exactly **Median window 5**, chosen before test access. The loader retains exact image/mask file identity and the portable decoded-source contract. No learned threshold search is performed: both segmenters use strict probability **`>0.5`**, with equality assigned land and cleanup disabled. This behavior is verified in the executed source and regressions; saved NPZs contain final masks, not probabilities for a later threshold search. Model outputs correctly label ENL and denoising PSNR as `not_applicable`.

The reviewer independently loaded both trusted checkpoints through the evaluator's `_preflight` on CPU, without predicting any actual test patch. Strict architecture/state reconstruction, shared raw-training normalization, saved best epoch/update count, filtered identity, canonical data/split identity, and checkpoint/report metadata all passed. Whole-file hashes match the accepted Phase 5 artifacts:

| Artifact | SHA-256 |
| --- | --- |
| Training report | `b2fc6c5efdca617a2009ce74ccd42d7f5e977027ce870128e1347d9906c91140` |
| Raw checkpoint | `2b6545a63c91bfa3f226ba47c92ccf4ff07fd2ca71553b318750df22c64868af` |
| Filtered checkpoint | `4916665108b1e83258467f82511e80fb3d373dabdd11bf2e337db54a6e56e63f` |

The shared raw-training normalization remains based on 15,417,377 SAR-valid pixels from the same 60 train IDs. The checkpoints are the validation-selected epochs **6 raw / 8 filtered**, not the last epochs. Actual training totals remain **11 epochs / 327 updates raw** and **13 epochs / 387 updates filtered**, with the allowed early-stopping difference visible. The accepted training review supplies the initialization/crop and validation-replay evidence; this test-results review did not refit normalization or select another checkpoint.

The output's `config.json` is semantically identical to the original executed input. It is a text-serialized display copy with SHA-256 `eb4d2ddbf84d7dc21a2f28048ce1296a53486d144a565b479b1eb1311cc062a5`, while runtime correctly binds the original frozen input's byte hash above. Do not substitute the display-copy byte identity for the executed input identity. The preserved original configuration remains authoritative for reproduction.

## Held-out result and negative findings

| Condition | TP | FP | FN | TN | Water IoU | Water F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Raw U-Net | 445,016 | 70,800 | 244,297 | 3,745,089 | 0.5854603197 | 0.7385367044 |
| Median-5 U-Net | 408,996 | 75,691 | 280,317 | 3,740,198 | 0.5346324987 | 0.6967563884 |

| Condition | Pooled precision | Pooled recall | Fixed-set macro IoU | Macro F1 | Dry FP pixels / 27,394 | Dry FP rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Raw U-Net | 0.862742 | 0.645594 | 0.396597 | 0.498098 | 355 | 0.012959 |
| Median-5 U-Net | 0.843835 | 0.593339 | 0.384958 | 0.497799 | 343 | 0.012521 |

Both models make false positives on the one dry patch, so the fraction of dry patches with any false positives is 1.0 for both. One dry patch cannot establish general specificity. Its per-patch water IoU/F1 are zero and recall is null, rather than treating it as perfect water segmentation.

**Median preprocessing lowers pooled water IoU by 0.0508278 and F1 by 0.0417803**, with 36,020 fewer true positives and 4,891 more false positives. Its slightly smaller dry false-positive count does not reverse this result. Macro recall increases from 0.506841 to 0.525111 while pooled recall falls; patch-size weighting and mixed behavior make those different summaries compatible. Preserve both summaries and the fixed set instead of choosing a favorable one.

The raw U-Net also has lower pooled IoU than the classical raw threshold baseline (0.608415) and classical Median threshold pipeline (0.630412) in the accepted companion experiment. These are measured small-subset comparisons, not proof that classical processing universally beats learning. The neural branch remains a valid controlled negative experiment; it does not require a rescue model or test-based retuning.

The runner exports per-patch counts but no separate event table. The reviewer pooled those independently verified counts by frozen event ID to expose mixed behavior:

| Event | Raw U-Net IoU | Median-5 U-Net IoU |
| --- | ---: | ---: |
| Ghana | 0.214539 | 0.233491 |
| India | 0.543497 | 0.464786 |
| Mekong | 0.676474 | 0.663098 |
| Nigeria | 0.790276 | 0.668016 |
| Pakistan | 0.310071 | 0.404748 |
| Paraguay | 0.307933 | 0.204074 |
| Somalia | 0.205614 | 0.295339 |
| Spain | 0.211120 | 0.233740 |
| Sri-Lanka | 0.851252 | 0.683835 |
| USA | 0.382476 | 0.337611 |

These groups share the official-subset correlation limitations. They are not held-out-event tests. Some improve after filtering, while large losses include Sri-Lanka_713926 (0.8513 to 0.6838), Nigeria_812045 (0.8036 to 0.6797), India_591317 (0.6580 to 0.5364), and Paraguay_913449 (0.3079 to 0.2041).

## Actual figure inspection

The reviewer opened the learning-curve PNG and **all five aligned prediction figures**. They use the first five sorted held-out identifiers, rather than a performance-based selection. Raw/filtered VV displays share raw-derived limits; ground truth and error maps mask invalid scored regions; errors identify red false positives and blue false negatives. The figure collection contains raw VV/VH, selected-filter VV, each model's native mask, and each error map.

- **India_591317:** both predictions contain holes and missed water throughout the broad river; the filtered model misses visibly more, consistent with water recall falling from 0.6615 to 0.5372. The classical Median figure's stronger broad-water recovery must not be confused with the separately trained filtered U-Net result.
- **Ghana_313799:** both models miss most labeled channels and water bodies. Filtering raises IoU from 0.0219 to 0.0513, but this remains a severe failure, not a successful water map.
- **India_1018327:** predictions recover only broken parts of the river and miss substantial labeled water beyond it. Filtering improves IoU from 0.2284 to 0.2657 while most water still remains missed.
- **Ghana_406026:** dark ponds are mostly captured, but shoreline mismatches and small extra predictions remain. Filtering slightly lowers IoU from 0.8049 to 0.7883.
- **Ghana_97059:** both networks mark the dark target despite no valid ground-truth water on the scored patch. The red error component corresponds to the independently checked dry false positives.

The learning curves are legible and agree with declining training objectives, nonmonotonic validation scores, different stopping epochs, and the selected validation peaks at raw epoch 6 and filtered epoch 8. A lower late training loss is not represented as evidence to replace the already-selected checkpoint. Figures alone do not identify whether particular misses arise from backscatter physics, annotation/acquisition mismatch, limited training, or the preprocessing/model interaction.

## Runtime, environment, and reproducibility limits

Runtime correctly identifies **`checkpoint-evaluation`**, `training_included=false`, `fresh_colab_verified=false`, seed 42, CUDA on an NVIDIA RTX 4000 Ada Generation, Python 3.12.3, PyTorch 2.15.0+cu132, and NumPy 2.5.4. It carries the separate **122.063888-second remote paired-training** measurement rather than folding it into inference time. The recorded **6.853086-second evaluation subtotal** includes checkpoint preflight/loading, held-out loading, compute, native-mask writes/checksums, tables, learning curves, and five figures; it explicitly excludes the final results/runtime JSON and configuration serialization.

Condition compute times are **0.667571 seconds raw / 3.164706 seconds filtered**, including input filtering, native inference, and scoring. Native NPZ write/checksum times are separately **0.057285 / 0.059997 seconds**, totalling 0.117283 seconds. GPU predictions transfer outputs back to CPU before the measured prediction returns; the recorded condition timers therefore include completion of those predictions. No download/setup, final archive transfer, or training reproduction is included in the 6.85-second subtotal. It cannot establish a fresh full Colab workflow below 30 minutes.

The captured evaluation environment explicitly records **SciPy 1.17.1**, whereas the original completed training snapshot records **SciPy 1.18.1**. Preserve the two snapshots separately. The change is disclosed rather than claiming an identical environment; source/checkpoint/configuration and exact persisted masks establish which recorded run the scores describe.

**Backend reproducibility limitation:** the training setup explicitly enables deterministic algorithms and disables TF32. The standalone evaluation command does not call that setup and its runtime does not record deterministic-algorithm, cuDNN, or TF32 backend flags. Do not claim this evaluation used identical backend settings or that its masks will reproduce bit-for-bit under another default backend. The immutable saved predictions and independently verified counts are sound evidence for this recorded run. No discrepancy requiring a new inference run was found, so the reviewer did not introduce a post-test rerun or a new setting. Evaluation peak memory is also unmeasured; the training peak allocation belongs to the separate training record.

Remaining delivery/acceptance work is to retain public checkpoint references and exact original-byte hashes, preserve these results and environment snapshots, complete the final report, and obtain organizer data/fresh Colab evidence where required. This review independently verifies the local checkpoint originals; publication authorization and remote release digest were handled by the coordinating agent. No unseen-geography, newly flooded-versus-permanent-water, multi-seed, or statistical-superiority claim follows from acceptance.

## Reviewed output identities

| File under `outputs/final-neural-development-v1/` | SHA-256 |
| --- | --- |
| `results_neural.json` | `d4ac409314b4480bdc35048233ee47f0dc515570de9f727dc628336a14dd1857` |
| `results_neural.csv` | `815602e524e6e2f2abc744b4e9d73a5a37490508fdc2d923d95629ba88bf29da` |
| `per_patch_neural.csv` | `861f470a4465e235ad14d4a66b611f50638227993e8a457a66af131a5e86b839` |
| `runtime_neural.json` | `124a0436961b53b9c73530e4f6f51dc3e5786cba2e92473a1bce8e681fa5be7b` |
| `native_predictions.csv` | `ee563120327e234f7b7ab1ea6a2976d6b40e0ff99f29a08d8f4286fb1d09d1da` |
| `evaluation-environment.txt` | `a38c9bf34568067981fbc86f33ea7b9c608cc49ccf2fde9b36b585c0e02cde73` |
| `learning_curves.png` | `500c64e097b4303a1f0aa7c9065b0e963575bbd42315978ab717f15f0db9c062` |

The native prediction index binds every one of the 40 NPZ files separately. All reviewed original artifact bytes remain unchanged; only this report was added by the reviewer.
