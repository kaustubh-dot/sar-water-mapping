# Supplied-set execution ledger

Started 29 October 2026. User explicitly authorized closing the supplied-set
critical gate and deferring uncached Colab. Existing development files/results
remain preserved. Base implementation commit: 612040e20ecb69fa2c2a875aec4ca32c18249208.

## Approved execution contract

Use exactly the first 100 ordered source rows recorded in
`supplied_subset_selection.csv`, bound to source CSV SHA-256
`57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
No replacement, reordering to choose membership, new model or grid change.
New files use `supplied-v1` data/run identities. Existing metadata audit gives
Ghana31, India40, Mekong18, Nigeria10, Pakistan1.

Ruling: reuse the existing seed-42 event-group split generator before reading
imagery/labels. It assigns Mekong/Nigeria/Pakistan to train (29 patches), India
to validation (40), Ghana to test (31). Group separation takes precedence over
exact patch proportions; no search for a better-scoring split is allowed.
Previous development training exposure is 5 new-train, 9 new-validation and
8 new-test patches. New U-Nets start from scratch. The prior project exposure
is disclosed; this is not a claim of pristine blind evaluation.

## Phase gates

- [x] Acquisition implementation: exact identities, pinned object integrity,
  event membership freeze, cache reuse, safe immutable artifacts; focused tests.
- [x] Independent Sol xhigh acquisition/data audit acceptance.
- [x] Source-aware calibration + supplied notebook profile implementation;
  preserve development profile and exactly one notebook; independent review.
- [x] Inspect raw training and test-only ENL regions, freeze training looks and
  validation choices under unchanged method grids; independent review.
- [x] Remote GPU resource preflight, dedicated environment, seed42 paired
  scratch training under one-hour cap; completed-pair independent review.
- [x] Frozen classical/synthetic and neural held-out evaluation, separate
  outputs, figures/counts/hash evidence; independent result review.
- [x] Notebook supplied-profile execution smoke, report/reproduction/roadmap
  update, final integration review and branch publication.

Uncached Colab, its under-30-minute acceptance and final submission tag are
explicitly deferred. A local/remote cached smoke cannot close them.

Phase 1 accepted: 100 pairs / 200 objects, 169,393,092 bytes, 44 verified
cached copies and 156 downloads; acquisition took 148.656 seconds. All patches
are 512 square VV/VH with manual labels. Frozen membership is 29/40/31. There
is no cross-partition overlap or touching; 20 pairs touch within partitions.
Scored pixels: training 6,769,828, validation 8,788,754, test 4,940,307.
Ghana_26376 has no scored pixels; Ghana_24858 has 484. Both are retained.
Four training ROIs and five test land ROIs were independently accepted; no
water-region ENL is promised. A transient account-usage approval error paused
the remote transfer; the same authorized transfer later completed successfully.

Source profile gate accepted at commit 72ef16a. The metadata-only source config
SHA-256 is `7c121d63328d90c1850b419647d6964131a6138d468e686c02d6ba1c5d93fbbe`.
It verifies the source, digest, membership and exposure chain with path rebasing
and an end-of-calibration guard. The single notebook now defaults to
`supplied-first100`, preserving the development mode. Independent review passed
30 tests in 58.02 seconds; a TIFF-open sentry confirmed metadata-only APIs.
The integrated suite passed 130 tests in 125.65 seconds. Numerical grids,
filter implementations and the evaluation protocol are unchanged.

Actual calibration started on the supplied data at source 72ef16a. Training
looks were frozen at 07:10:54 UTC before validation access: VV 4.6020301257391925,
VH 2.582041888130562, four usable ROIs per band. The independent reviewer
reproduced all eight ROI records. Final validation choices and acceptance
were frozen in 260.463 seconds: 98 candidates, shared VH below -20 dB,
Median 5, Lee 5 and log-bilateral color sigma 3 dB. Median 5 is the selected
neural input. Config SHA-256:
`a04fc6e52b01dff1ddb2684d9b2a198963acd7a0d658404e11264779dea6843b`.
Independent Sol xhigh review accepted all 98 saved rows, directly reproduced
the four selected validation rows and separate cleanup summaries on all 40
India patches, and confirmed zero test access. See supplied_calibration_review.md.

Remote preflight: RTX 4000 Ada, 20,475 MiB total and 1,166 MiB used, 14% GPU
utilization; the only listed compute process was the desktop service (162 MiB).
The project disk had 433 GB free. The dedicated environment imports the current
project, PyTorch 2.15.0+cu132 reports CUDA available, and the supplied metadata
chain verifies there with the exact 29/40/31 split.

Training accepted at clean source `0cdb7874e3699cd1e6c0f68a98b5eea6c6e9ff50`.
The pair completed in 76.767525 seconds including 11.101004 seconds of input
preparation. Raw stopped at epoch 10 / 150 updates, best epoch 5; Median-5
stopped at epoch 9 / 135 updates, best epoch 4. Both have the same scratch
initialization, independently replayed in the original environment. The Sol
xhigh reviewer reproduced normalization, all ten crop plans and all 80 native
validation confusion matrices exactly, with zero test reads or attempts.
See supplied_training_review.md. The redacted 3,666,469-byte checkpoint bundle
has SHA-256 `9605d1906802434d73d5ef73239e127395779a03df11596004c94e4acb5aa6d6`;
it remains outside Git. Frozen held-out classical/synthetic and neural scoring
has now started in separate output directories at the same clean source.

Frozen evaluation accepted by independent Sol xhigh review in
supplied_results_review.md. All six summaries and 186 primary per-patch rows
agree; all 62 saved neural masks and their independent validity masks recount
exactly. Every method scores 4,940,307 pixels, with the same 15 water-positive
macro patches, 15 dry patches and one no-score patch. ENL has 40 finite records
from five fixed land rectangles, including one SAR-valid/label-invalid region
whose land class is visual interpretation only. The 72 synthetic PSNR records
and eight means are separate from real SAR. No test-driven changes were made.
Classical evaluation took 59.376433 seconds including 124 diagnostic figures;
neural checkpoint evaluation took 9.061679 seconds, separately from training.

The supplied notebook smoke completed in a separate Linux kernel, clean
checkout pinned to `9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`, with 200 cached
TIFFs. It passed independent review in supplied_notebook_review.md: all ten
cells executed, 96 checks passed, 98 validation records and every classical
held-out confusion count reproduced exactly. ENL and synthetic results also
agree; negligible radiometry roundoff is documented. The authoritative notebook
clock is 123.043926 seconds through the original ZIP and checksum. The retained
164,908,503-byte archive has SHA-256
`968b9065b9ded3fb0c3c472e10e4fccf60c12a1f10c5f82481698de841577cef`.
Clone/cache preparation and the existing execution environment are outside its
notebook clock. This verifies cached integration, not fresh Colab. S1 scientific
execution is closed. Final documentation and publication-scope consistency
passed independent Sol xhigh review in supplied_integration_review.md. All
implementation, script, test and notebook files remain unchanged from the
130-test accepted implementation. Supplied results lead the report and README;
old development measurements remain separately labeled. Raw data, checkpoints,
native mask archives and private execution artifacts remain outside Git.

The existing draft PR description could not be updated: the integration
returned 403 and the local GitHub CLI has invalid authentication. A replacement
body is saved locally. Git branch publication remains available; main, the
final acceptance tag and uncached Colab are unchanged and pending.
