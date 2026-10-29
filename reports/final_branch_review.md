# Final development-branch review

29 October 2026. Independent GPT-6.1 Sol review at xhigh of
`implementation/remaining-phases` against `main`, including the final public
documentation and small delivery artifacts. The measured scientific source is
`61b09f9bfa61114d83bd7be19eba3de67d5621db`; the reviewed delivery changes do not
alter its implementation, configuration choices, tests or notebook source.

**Decision: ACCEPT for a development draft pull request. No unresolved P1 or
P2 finding was identified in this review.** This does not authorize a main
merge or a final hackathon tag, and does not close organizer-data or fresh-Colab
acceptance. No scientific retuning, training or inference was performed here.

## Scope and scientific integration

Read the project guardrails, README, roadmap, evaluation protocol,
implementation lock and reproduction guide. Reviewed the branch's integration,
source/version bindings, checkpoint delivery, claims and phase evidence. The
accepted phase-specific reviews remain the detailed scientific evidence:
[classical execution](classical_results_review.md),
[paired training](phase5_execution_review.md),
[neural held-out results](neural_results_review.md), and
[actual notebook execution](notebook_execution_review.md). This review does not
present those reviewers' full replays as newly executed checks.

The locked four-family primary comparison retains one validation-selected
numeric VV threshold, no primary cleanup, power-domain Lee/ENL, separate
synthetic reference PSNR, independent SAR/label validity and the fixed
water-positive macro set with separate dry false positives. The compact
487,857-parameter U-Net is the sole trained architecture, with both raw and
Median-5 conditions retained. Its segmentation outputs do not receive ENL or
denoising PSNR. No additional model or test-based rescue setting entered the
delivery.

README and report values are traceable to the preserved classical/neural
tables. Both disclose lower Lee water IoU and worse Median-fed U-Net results.
They identify the 100 upstream manual-label development pairs, official
60/20/20 membership, touching chips/shared events, one neural seed and limited
geographic claims. They describe observed surface water without claiming
separation of new flooding from permanent water.

Runtime claims retain their scopes: 122.06 seconds for the remote training pair
including preparation, 6.85 seconds for the narrower checkpoint-evaluation
subtotal, and 91.78 seconds for the cached Linux classical notebook through
archive/checksum. Existing cache, checkout and kernel prerequisites are stated.
The last measurement is not labeled a fresh Colab or full-training result.
Missing organizer input and unmeasured fresh Colab acceptance remain visible
in the README, roadmap, final report and reproduction instructions.

## Fresh independent delivery checks

Executed the bounded probe:

```powershell
.\.venv\Scripts\python.exe outputs/final_branch_review_probe.py
```

Its final run exited 0. Detailed local evidence is retained in ignored
`outputs/final_branch_review_probe.json`.

- All seven SHA-256 values in the neural evaluation source record match both
  the current reviewed files and the exact source-commit blobs. The seven
  entries in the neural-result artifact index match the public delivery files.
  No implementation change was found after the measured commit.
- The connected GitHub API independently confirms a public, non-draft
  **development prerelease**, targeted at the measured source commit. Its
  3,648,324-byte uploaded asset has the recorded SHA-256
  `b70dc5117a21ecac5b3b0e2ad9fc06f960a727370c81892089ac27b894100238`.
  The actual public download was supplied by the coordinator and was
  independently rehashed and inspected here. All four internal checksum
  entries pass. The six-entry ZIP contains two checkpoint files, training
  metadata, original dependency versions, checksums and a README; no dataset
  is present. See the [public release](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/development-seed42-v1)
  and [download/preflight record](checkpoint_delivery.json).
- Compared original and public training JSON. All original fields match except
  the two absolute checkpoint paths, replaced with relative basenames. The
  public record additionally contains an explanatory publication note. The
  public record is byte-identical to `neural_training-v1/training.json`;
  checkpoint byte streams retain their original hashes. Original-versus-public
  training-report hashes are distinguished in the summary.
- Ran the reproduction guide's Python restoration block verbatim in an
  isolated archive of the recorded source. Preseeded only the 200 cached object
  files and made any network fetch fail. The wrapper created the frozen
  selection, exact-byte manifest/splits and a fresh access log in ignored
  outputs. All 200 manifest image/mask SHA-256 values passed. The source
  archive's public download record remained unchanged. This verifies the
  documented cached restoration path, not uncached download speed or scientific
  replay. Original raw inputs were not rewritten.
- Confirmed that the guide's frozen-evaluation and training CLI arguments match
  the implemented parsers, preserve the exact manifest location required by
  its relative paths, and use new output directories. Checkpoint inference and
  new training remain separate documented operations. The coordinator's
  independently recorded CPU preflight of both publicly downloaded checkpoints
  passed without opening held-out sources.
- Checked local Markdown targets in README, roadmap, reproduction guide, final
  report and demo. All resolved. Audited 134 tracked/proposed public paths:
  no raw TIFF, checkpoint, array or archive file was included. Text pattern
  checks found no credential, private-network address or remote connection
  location. This is a bounded pattern/manual audit, not a guarantee against
  every possible secret. Generated predictions, full image bundles, data and
  checkpoint binaries remain outside Git. Third-party terms remain separate
  from the project's MIT license.

Earlier probe attempts corrected review-harness assumptions about an added
publication note, restricted hard-link creation and ordinary Windows Git text
conversion. The documented restoration itself completed successfully; none of
those probe corrections changed project code, frozen scientific artifacts or
the reproduction guide.

## Combined verification and remaining gates

The coordinator executed the fresh complete suite on the final delivery tree:
**110 passed in 83.58 seconds**, exit 0. Its command and execution conditions are
preserved in [final verification](final_verification.json). This reviewer read
that evidence and did not duplicate the full suite. The separate
[publication audit](publication_audit.json) found no forbidden data/checkpoint
files or public files larger than 5 MB. No final acceptance tag exists.

The whole-branch review/public-delivery preparation gate may now be checked.
A development draft PR can expose the implementation and measured evidence
while preserving these external gates:

1. Obtain and audit the organizer archive and its source/split/label provenance;
   run a separately versioned organizer experiment without reusing test-visible
   development choices as untouched organizer validation.
2. Execute the complete classical notebook in a fresh Colab runtime, including
   compatible installation and uncached documented access, and retain its
   result ZIP plus authoritative timing sidecar strictly below 30 minutes.
3. If judging requires training inside that budget, measure the separate full
   training profile or submit the complete classical core. Checkpoint inference
   cannot substitute for that evidence.

Keep the development prerelease distinct from final acceptance. Main merge
and `v1.0-hackathon` remain outside this review's acceptance decision.
