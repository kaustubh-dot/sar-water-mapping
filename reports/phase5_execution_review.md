# Phase 5 completed-pair execution review

29 October 2026. Independent GPT-6.1 Sol review at xhigh of the completed
seed-42 remote training pair against the implementation lock, evaluation
protocol, accepted implementation review and portable-source migration.

**Decision: ACCEPT the completed raw/Median-5 training pair for frozen neural
held-out evaluation.** No unresolved critical or important execution finding
was identified. This accepts the recorded remote experiment; it does not
establish held-out accuracy, organizer-subset validity, checkpoint availability
to another user, or a fresh Colab training runtime.

## Source, frozen inputs and model contract

The executed source is clean commit
`61b09f9bfa61114d83bd7be19eba3de67d5621db`. The local reviewed scientific
sources match that commit. Configuration
`configs/development-calibrated-v3.json` has SHA-256
`3b54e43f217ad80e2c029554289acd483538ecbd09837bcfb9c9b689a653f4af`.
Its manifest and split-file hashes are respectively
`d840b655f00df68220d5b2ccbaf9eb9c5aa4e785dd0184e05f8dec7646c46786` and
`24963a9951f318aab0cc3d687023ce849fc5c9435ed9fc8cbadced4dc6c2d1b7`.
The report's canonical subset and membership hashes also match the frozen rows.

The reviewer independently confirmed that v3 changes only the five provenance
fields identified in the [accepted source-identity migration](source_identity_review.md).
All scientific configuration fields remain equal to accepted v2, including
Median window 5, effective looks `[4.859278122453718, 4.020813607183419]`,
threshold choices, split membership, and original calibration freeze time.
There was no validation search or scientific retuning in this review.

The manifest retains 100 upstream manual-label development pairs with official
60/20/20 membership. Every row declares the versioned native source hash domain.
The actual development loader verified all 160 training/validation image and
mask files, source-domain identities, training-only ROIs and looks artifact,
then produced 80 raw and 80 Median-filtered patches. File-open guards prohibited
all 40 held-out image/mask paths throughout this review: **zero held-out source
reads** occurred. The earlier migration review establishes the complete
100-pair identity chain; this review did not reopen test files to repeat it.

The recorded architecture is the locked two-channel compact U-Net with
**487,857 parameters**. Both checkpoints load with strict state reconstruction,
finite weights, matching internal state hashes and metadata. The executed
configuration fixes seed 42, Adam learning rate 0.001, batch 8, 256-square crops,
maximum 20 epochs and validation patience 5. The accepted source implements
shared raw-training dB normalization, SAR-only filling, the masked equal-weight
BCE/Dice objective, native inference and strict water probability `>0.5`.
No architecture, optimizer, threshold or cleanup choice changed.

## Matched conditions and checkpoint selection

Both conditions record initial state SHA-256
`74ad8bdd6adc541aa9ccaed6f05be6691e6ee10a53dffeeacf0a071ff380e7ca`.
The coordinating agent independently replayed the seed-42 initialization in
the original remote PyTorch environment and obtained that exact hash.
The local Windows environment uses PyTorch 2.14.0+cpu rather than the remote
2.15.0+cu132, and produced a different initial hash; cross-version initialization
parity is not claimed. This does not affect the two conditions' matched
initialization in the recorded execution.

The reviewer recomputed all **13 epoch crop-plan hashes** from the development
inputs and seed. Every hash matched. Each epoch drew exactly 240 crops from
60 training sources; accepted/skipped counts and batch counts matched every
recorded condition history. For the 11 epochs in which both conditions remained
active, their crop plans, accepted crops and update counts matched exactly.
The raw-training normalization uses **15,417,377 SAR-valid pixels** and the same
60 sorted training IDs in both checkpoints. A fresh local recomputation differed
from the recorded mean by at most `1.23e-8` dB and std by at most `8.95e-9` dB;
it did not replace the saved normalization.

| Condition | Executed epochs | Total updates | Best epoch | Updates in saved checkpoint | Best pooled validation water IoU |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 11 | 327 | 6 | 177 | 0.6005466393 |
| Median 5 | 13 | 387 | 8 | 237 | 0.5621462142 |

For each condition, the recorded best is the earliest maximum of its full
validation history. Exactly five subsequent non-improving epochs precede its
`early_stopped` status. All epochs completed, all recorded losses are finite,
and cumulative updates agree with the histories. The saved checkpoints match
the best-epoch metadata and weight-state hashes, rather than the final trained
epoch. They explicitly contain inference weights and do not support optimizer
resume. Different final update totals are permitted by the locked early-stopping
rule and must remain visible.

Every historical validation record covers the same 20 validation identifiers
and source-derived scored-pixel counts. Independently summing their confusion
counts reproduces the recorded pooled IoU/F1. The reviewer then reran native
512-by-512 prediction for all 20 validation patches under each saved checkpoint,
using the saved normalization and frozen Median input. **All 40 per-patch
confusion matrices exactly matched the recorded best-epoch validation results**,
despite the local CPU/PyTorch environment difference. This observed agreement
does not promise bitwise parity for other hardware or versions.

Median preprocessing produced a lower best validation IoU in this single-seed
pair. That negative result is accepted without a rescue architecture, extra
threshold search, or a change to the held-out experiment.

## Runtime, environment and artifact integrity

The report records remote profile `remote`, `pair_complete=true` and
`cap_exhausted=false`. Input verification/filter preparation took
**12.864063 seconds**; the paired normalization, training, validation and
checkpoint phase took **109.195950 seconds**. The complete invocation took
**122.063888 seconds**, including preparation and final bookkeeping, inside the
shared **3,600-second** limit. Its internal remaining allocation is exactly
3,600 seconds minus preparation time. This is a remote development measurement,
not a fresh full Colab run or an inference-only timing claim about training.

The captured training environment records Python 3.12.3, PyTorch 2.15.0+cu132,
CUDA 13.2, NumPy 2.5.4, SciPy 1.18.1, and an NVIDIA RTX 4000 Ada Generation.
Deterministic algorithms were enabled. Peak allocated CUDA memory was
964,296,704 bytes; CPU peak RSS was explicitly unmeasured. The separate
`outputs/remote-training-environment.txt` agrees with the core training package
versions. Later notebook dependency work changed SciPy in that environment;
the training snapshot must remain the provenance for this completed pair.

The coordinating agent supplied fresh resource evidence before training:
18,845 MiB free GPU memory, approximately 430 GB free disk, and only the
existing desktop/background GPU allocation. Training used the dedicated project
environment. This is coordinator-observed resource evidence, distinguished
from the checkpoint/data checks independently executed by this reviewer.

Whole-file hashes of all three downloaded artifacts independently match the
remote hashes supplied by the coordinating agent:

| Artifact in `outputs/training-seed42-portable-v1/` | SHA-256 |
| --- | --- |
| `training.json` | `b2fc6c5efdca617a2009ce74ccd42d7f5e977027ce870128e1347d9906c91140` |
| `raw_best.pt` | `2b6545a63c91bfa3f226ba47c92ccf4ff07fd2ca71553b318750df22c64868af` |
| `filtered_best.pt` | `4916665108b1e83258467f82511e80fb3d373dabdd11bf2e337db54a6e56e63f` |

Checkpoint binaries and local outputs remain ignored by Git. Retrievable
checkpoint references, portable training logs/environment, learning curves and
the final results bundle remain delivery tasks; this local acceptance does not
claim those artifacts are already available to another user.

## Fresh verification and remaining gates

Executed the read-only local probe:

```powershell
.venv/Scripts/python.exe outputs/phase5_execution_review_probe.py
```

It completed with exit 0 in **88.18 seconds** and saved detailed evidence in
`outputs/phase5_execution_review_probe.json`. It checked source/configuration/
split/subset/checkpoint identities, exact file hashes, unchanged migration
choices, development-only input preparation, normalization, crop plans,
history arithmetic, early stopping, saved-checkpoint updates and both full
validation replays. A preliminary attempt stopped at the cross-version local
initialization comparison described above; it opened no held-out source and
was resolved using the original-environment initialization replay.

The accepted checkpoints may now enter the separately recorded frozen neural
held-out evaluation. Keep its segmentation table separate from denoising
ENL/PSNR, preserve both conditions and their negative findings, and do not tune
after viewing the results. Single-seed evidence remains single-seed evidence.
The official development subset has seven cross-partition touching chip pairs
and events shared across partitions; it supports correlated subset comparisons,
not unseen-event/geography claims. Organizer-specific acceptance, actual neural
held-out artifacts, delivery references and a complete fresh Colab Run All below
30 minutes remain open.
