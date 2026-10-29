# Supplied-set completed-pair training review

29 October 2026. Independent GPT-6.1 Sol review at xhigh against the
implementation lock and evaluation protocol.

**Decision: ACCEPT the completed seed-42 raw/Median-5 training pair for frozen
held-out neural evaluation.** No unresolved critical or important execution
finding was identified. This accepts the recorded remote experiment; held-out
accuracy and fresh Colab execution are separate gates.

The executed source is clean commit
`0cdb7874e3699cd1e6c0f68a98b5eea6c6e9ff50`. The local scientific sources match
that commit. Configuration SHA-256 is
`a04fc6e52b01dff1ddb2684d9b2a198963acd7a0d658404e11264779dea6843b`,
manifest SHA-256 is
`4c196542778daefb2f03b53634f8f0ef579f91851677c606d5ae77750ab93ea3`, and
split-file SHA-256 is
`940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`.
Checkpoint metadata, canonical subset/membership hashes, selected Median-5
filter, training ROI and looks-artifact bindings all match the new frozen
supplied configuration. No development calibration or checkpoint was reused.

The event membership is 29 training patches (Mekong/Nigeria/Pakistan),
40 validation patches (India), and 31 held-out patches (Ghana). All 100 retain
upstream training provenance; these are internal evaluation partitions.
The loader reverified the 69 training/validation pairs, source-file hashes,
native source-content identities and training-only ROI/looks records. Guards
blocked every held-out TIFF path and every old/external weight path throughout
the probe. **Exactly 138 training/validation files were opened; zero held-out
source reads or attempted reads occurred.** No training or tuning was performed
by the reviewer.

The two checkpoints reconstruct the locked 487,857-parameter VV/VH U-Net with
finite weights and matching state hashes. The accepted source instantiates
fresh models and copies the initial raw state into the filtered condition;
it does not load old weights. Both conditions record initial state SHA-256
`74ad8bdd6adc541aa9ccaed6f05be6691e6ee10a53dffeeacf0a071ff380e7ca`.
The coordinating agent independently replayed scratch initialization in the
original PyTorch 2.15.0+cu132 environment and obtained that exact hash; its
[replay record](supplied_training-v1/initialization_replay.json) reports zero
image/checkpoint reads. Local PyTorch 2.14.0+cpu produces a different scratch
hash, so cross-version initialization equality is not claimed.

The locked seed 42, Adam 0.001, batch eight, 256-square crops, maximum 20 epochs,
patience five, SAR-only filling, equal-weight masked BCE/Dice objective and
native strict probability `>0.5` inference are preserved. Both checkpoints use
one raw-training normalization over **7,601,417 SAR-valid pixels** from the same
29 sorted training IDs. An independent direct population-moment calculation
reproduced the saved mean within `1.30e-8` dB and std within `9.69e-9` dB.
Label validity did not control normalization or input filling.

All **10 epoch crop-plan hashes** were independently regenerated from the raw
training inputs and seed, without calling the production crop-plan helper.
Every epoch drew 116 crops, with accepted/skipped crops and update counts
matching every active condition's history. The first nine epochs share the
same plans across conditions. Every recorded epoch completed; losses are
finite. Best checkpoints select the earliest maximum validation water IoU,
followed by exactly five non-improving epochs before stopping.

| Condition | Executed epochs | Total updates | Best epoch | Saved-checkpoint updates | Best validation water IoU |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 10 | 150 | 5 | 75 | 0.3830579431 |
| Median 5 | 9 | 135 | 4 | 60 | 0.3707202782 |

Independent CPU inference used direct SAR-only nearest-valid filling, shared
normalization and manual confusion-count calculations on the 40 native
512-square validation patches for each checkpoint. **All 80 per-patch confusion
matrices reproduced exactly**, with zero TP/FP/FN/TN differences. Raw validation
F1 is 0.5539289876; Median-5 validation F1 is 0.5409131011. The worse filtered
result is retained without a rescue search. These values are validation
measurements, not held-out results.

The complete remote pair took **76.76752544 seconds**, including 11.10100387
seconds of input preparation and 65.66078373 seconds in the paired trainer.
The shared one-hour cap was not exhausted. The original environment records
an RTX 4000 Ada, deterministic algorithms and peak CUDA allocation of
964,296,704 bytes; CPU peak RSS was not measured. This timing does not certify
a fresh Colab run or a separately shortened Colab training profile.

The pinned original artifact SHA-256s were verified before and after replay:

- `training.json`: `2bf40f37c37b46a08566dac1607f2949322168a60a6033eb78cb0d0b846e259b`
- `raw_best.pt`: `ca627a944b74ceaa01c4fb24a0de4a181a8e74751b0c5349165418c45b13c799`
- `filtered_best.pt`: `325a085a55fef3df79c653a8c63128dc2d4f71e3f5e9757ca7b0560ff61e4180`

The prepared local delivery ZIP also passed CRC and checkpoint-byte checks:
3,666,469 bytes, SHA-256
`9605d1906802434d73d5ef73239e127395779a03df11596004c94e4acb5aa6d6`.
Its public report differs only by two checkpoint-path redactions and an added
artifact note; scientific fields are identical. Public-report SHA-256 is
`46755ea263783445b2ae9f9c78cd32e14dd360279196640fa578e830436cc8b0`.
This verifies local packaging, not publication or public availability.

The focused probe completed successfully in 201.42 seconds, retaining machine
evidence locally at `outputs/supplied_training_review_probe.json`. No broad
extra tests or repeated native inference were run after the successful probe.
Prior development training exposure remains 5 new-train, 9 new-validation and
8 new-test IDs. The new models were trained from scratch, but the project has
already encountered those IDs; do not describe the supplied held-out partition
as a pristine project-level blind test or claim permanent/new-flood separation.
