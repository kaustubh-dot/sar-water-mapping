# Phase 5 implementation review

Reviewed 29 October 2026 by an independent GPT-6.1 Sol reviewer at xhigh.

**Decision: the implementation and CPU fixtures pass review, with no critical or important findings. This does not approve real training results or close the Phase 5 execution gate.** No scientific GPU training, held-out neural result, convergence claim, or Colab training runtime was established by this review.

## Scope and controlling requirements

Read the project guardrails, README, roadmap, implementation lock, evaluation protocol, and research review. Reviewed `src/sar_water/model.py`, `src/sar_water/train.py`, `scripts/train_pair.py`, and `tests/test_neural.py`. Consulted the existing data/split and frozen-settings functions only to check the neural call boundary; other phase implementations are outside this review.

The reviewed source was uncommitted on base `33a9f7bc1005c8fe17e17e530ba0254a0b4dbdf9`. SHA-256 source identities:

| File | SHA-256 |
| --- | --- |
| `src/sar_water/model.py` | `c943cf84f2237131df46277cedc31c9b3c72966922d3bdb333e85ccf794740cc` |
| `src/sar_water/train.py` | `ab6bc9d6e473bf61416372a634c0b441d4f735db81fde493243a22a325f6acfd` |
| `scripts/train_pair.py` | `6fe7b6810b1b146efc4f898189eee0a0cf46fa54a211e18d4ff4325a49634223` |
| `tests/test_neural.py` | `045884a14311b657eb3d23dd3a10e3bddf08330333f451a700adf6be6f9813a6` |

## Findings

No required code correction was found. The following requirements were checked against implementation and focused tests:

- **Exact architecture:** `model.py:13-48` implements widths 16/32/64/128, three max pools, fourteen bias-free 3-by-3 convolutions with eight-group GroupNorm/ReLU, bilinear skip-size upsampling with `align_corners=False`, and one output logit. Independent inspection counted **487,857 parameters**, below one million. Odd native shapes and backward gradients were exercised, including an additional 8-by-9 input.
- **Loss and independent masks:** `model.py:51-71` indexes scored pixels before BCE and batch-pooled Dice, uses the locked equal weighting and epsilon, and returns `None` for an empty scored batch. `train.py:118-174` fills SAR from input validity alone before dB standardization and retains original masks. An additional adversarial loss check put NaN/Inf logits and NaN/nonbinary targets outside the scored set: loss and all gradients remained finite, and both excluded gradients were zero. Valid bad inputs are rejected.
- **Shared normalization:** `train.py:139-159` fits population dB mean/std from valid raw training SAR only, with the locked standard-deviation floor. `train.py:424-428` uses that same vector for both conditions. Label validity and held-out inputs do not fit normalization.
- **Matched sampling and optimization:** `train.py:177-222` supplies two uniform and two valid-water-centered draws per wet training source, or four uniform draws for a dry source, with clamped bounds and only flips/right-angle rotations. `train.py:429-455` shares initialization and the exact epoch crop plan. `train.py:361-397` skips empty scored crops, logs actual processed crops/updates, and uses the locked Adam configuration. The focused fixture produces identical returned models for identical raw/filtered inputs.
- **Validation and checkpoints:** `train.py:90-108,263-329,471-507` uses pooled validation water IoU, preserves the earlier best checkpoint on exact ties, waits five stale epochs, restores the best weights, scores at native resolution, and treats sigmoid 0.5 as land. An extra controlled six-epoch tie check retained epoch 1, stopped both conditions after six updates, restored epoch-1 weights, and preserved the best-checkpoint update count separately from total updates. Altering a checkpoint weight while leaving its recorded hash unchanged was rejected. Checkpoints explicitly contain inference weights rather than optimizer/resume state.
- **Budget and failure reporting:** `train.py:56-75,400-519` enforces the locked schedule and one shared time allocation, excludes an over-budget or incomplete pair from `pair_complete`, and records actual updates/statuses. `train.py:617-639` includes file verification and filter preparation in the CLI wall budget. A short full-Colab schedule remains separately identified. Existing fixtures cover exhaustion before training and no-valid-crop failure.
- **Frozen inputs and untouched test data:** `train.py:522-604` verifies frozen manifest/split, ROI and looks-artifact hashes; requires training-only ROIs; reproduces the recorded looks; verifies development file and decoded-input hashes; and skips test file loading. Relative image/mask paths resolve against the manifest, and ROI/looks paths resolve against the configuration directory. `train.py:332-350` validates split/source conflicts and matching raw/filtered labels and masks without reading test objects. The focused tests include an unreadable test sentinel and nonexistent test files.
- **Reproducibility metadata:** `train.py:234-260,440-449,607-639` records the seed, configuration and split/subset hashes, filter identity, normalization, source commit, environment, crop-plan hashes, checkpoint weight identity, timing, memory availability and dirty-tree status. Source manifests and frozen calibration must accompany a delivered run; the commit should identify the actual executed source.

## Verification evidence

Ran in the local project environment:

```text
.venv/Scripts/python.exe -m pytest tests/test_neural.py -q --basetemp=outputs/phase5_review_pytest
23 passed in 14.36s

.venv/Scripts/python.exe scripts/train_pair.py --help
exit 0; frozen input, device, epoch, shared time-limit and profile arguments present
```

Additional one-off CPU checks passed for exact convolution/parameter structure, finite masked nonfinite-value gradients, an 8-by-9 native forward/backward, tied-validation early stopping and restoration, checkpoint tamper rejection, and no test-patch access. These controlled checks are implementation fixtures, not measured scientific training results. A first invocation of the extra checkpoint harness reused an existing temporary output directory and correctly received `FileExistsError`; rerunning with a new child output directory passed.

The coordinating agent separately reported an exact `CompactUNet` CUDA forward/backward after `set_reproducible(42)` on remote PyTorch `2.15.0+cu132` passed. That is coordinator-supplied compatibility evidence, not a GPU command independently run by this reviewer. A concern based on the installed deterministic-algorithms docstring was withdrawn after inspecting the actual `interpolate` implementation, which provides a deterministic decomposition for this path; strict determinism should not be relaxed on that stale-doc basis.

`git diff --check` also reported an existing trailing blank line in `tests/test_data.py:251`, outside this review's source scope; it is not a neural finding.

## Remaining execution gates

Actual data and classical validation must be audited/frozen before real neural training. Run only the paired seed-42 locked experiment first, in the dedicated authorized GPU environment after a fresh resource inspection. Retain the source/configuration/manifest identities and report actual updates, learning curves, checkpoint references and total paired time. Optional seeds must share the same external one-hour cap.

The wall limit is cooperative: it is checked between batches and native patches, so a currently running operation or serialization can cross the deadline. The implementation documents and reports this and rejects an over-budget pair as complete. Resource profiling and the real runtime gate remain necessary.

Single-seed accuracy, comparative benefit, organizer-subset validity, full remote completion and fresh Colab runtime remain unmeasured by this review. Preserve the classical fallback and keep the roadmap's unrun experiment checkboxes open until their own evidence exists.
