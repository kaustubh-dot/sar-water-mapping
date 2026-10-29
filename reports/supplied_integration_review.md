# Supplied execution integration review

29 October 2026. Independent **GPT-6.1 Sol, xhigh** review of the final S1
integration and documentation.

**Decision: ACCEPT S1 closure. No unresolved P1/P2 finding remains within this
supplied-execution scope.** Final submission remains **NOT READY**: S2 fresh
uncached Colab is explicitly deferred and unverified; S3 publication to `main`
and the final acceptance tag remain pending. This review performs no new
calibration, training, inference, source-mask recount or test-suite run.

## Evidence chain accepted

The independent phase records provide a complete, separately versioned chain:

| Gate | Accepted evidence and identity |
| --- | --- |
| Exact supplied recipe, acquisition, audit, split and ROIs | [Data review](supplied_data_review.md): 100 ordered manual pairs, 200 integrity-checked objects; internal event split 29/40/31; independent validity masks; frozen training and held-out ENL ROIs |
| Source-aware calibration and notebook wiring | [Profile review](supplied_profile_review.md): strict metadata-only source configuration; default supplied notebook profile and preserved development option |
| Validation choices | [Calibration review](supplied_calibration_review.md): 98 unchanged candidates; train-only looks; shared VH below −20 dB; Median 5 selected; no test access |
| New learned comparison | [Training review](supplied_training_review.md): matched scratch initialization, raw-training normalization and crop plans; 80 validation confusion matrices independently verified |
| Frozen held-out measurements | [Results review](supplied_results_review.md): four classical and two neural rows; 62 saved neural masks recounted; separate ENL/synthetic records and unchanged scoring population |
| Actual notebook execution | [Notebook review](supplied_notebook_review.md): ten executed cells, zero errors, 96 passing checks; cached Linux integration in 123.04392588 seconds through ZIP/checksum at pin `9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f` |

The frozen experiment remains SHA-256
`a04fc6e52b01dff1ddb2684d9b2a198963acd7a0d658404e11264779dea6843b`.
The original supplied source configuration remains
`7c121d63328d90c1850b419647d6964131a6138d468e686c02d6ba1c5d93fbbe`;
manifest `4c196542778daefb2f03b53634f8f0ef579f91851677c606d5ae77750ab93ea3`
and splits `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`
remain bound to it. The strict source verifier passed again using metadata only.
Seven frozen calibration/training/delivery anchor files and all **21 indexed
supplied result files** were rehashed and match the accepted records.

Scientific source, scripts, tests and notebook bytes have no changes since
accepted implementation commit `72ef16a`. The locked filtering, metrics,
selection, segmentation, data and synthetic sources remain byte-identical to
base `612040e`. The previously recorded 130-test integrated suite and actual
96-check notebook execution therefore remain applicable; documentation-only
integration received link/content verification instead of artificial tests.

## Documentation and publication boundary

Read README, ROADMAP, data README, reproduction guide, final report, demo,
[submission audit](submission_audit.md), verification JSON and supplied ledger.
The supplied six-row table, 76.77-second scratch training pair, 59.38-second
classical runner, 9.06-second checkpoint evaluation and 123.04-second cached
notebook measurement are separately labeled with their timing scopes. The
earlier development results/checkpoints remain distinct. Two stale historical
demo statements and the old source-binding wording were corrected before
acceptance.

The documents preserve the material limits: all 100 source IDs come from
upstream training; recipe sender authority is unverified; 22 IDs have prior
project training exposure, distributed 5/9/8 including eight current test IDs.
All methods score the same 4,940,307 pixels, with 15 water-positive macro
patches, 15 scored dry patches and one explicit no-score member. The 484-pixel
test member is retained. Five fixed ENL regions are visually interpreted land;
one has no valid labels and is not independently label-confirmed land. ENL uses
SAR validity, and synthetic known-reference PSNR stays separate. The worse
Median-input U-Net is retained without test-driven rescue changes.

The supplied checkpoint ZIP is verified **local delivery only**, 3,666,469
bytes, SHA-256
`9605d1906802434d73d5ef73239e127395779a03df11596004c94e4acb5aa6d6`.
It has no public release; the older development release cannot substitute for
it. The notebook smoke used 200 cached TIFFs, an existing clean clone and
preinstalled prerequisites, with initial clone/cache preparation outside the
clock. Neither its timing nor remote training closes fresh Colab acceptance.

Independently verified **159 local links across eight current documents**.
The coordinating agent's final publication probe reports 208 proposed Git
files and 239 local links, with no missing/unpublished local targets, forbidden
data/checkpoint/archive binaries, files over 5 MB or credential/connection
matches; three reproduction Python blocks parse. Its machine evidence is
retained under ignored outputs and summarized in
[submission verification](submission_verification.json). These counts precede
this new review file and will be refreshed by the coordinator. The original
notebook archive, real data, model binaries and bulky generated artifacts remain
outside Git. This verifies proposed branch contents rather than final `main`
publication.

The [roadmap](../ROADMAP.md) and [submission audit](submission_audit.md) correctly
retain S2/S3 as the remaining acceptance gates. Keep the implementation in the
draft PR and do not create the final submission tag from the cached smoke.
The coordinator verified PR #1 remains open/draft and `main` unchanged. Updating
its descriptive metadata was blocked by connector HTTP 403 and unavailable CLI
authentication; that publication-metadata limitation does not reopen S1.
