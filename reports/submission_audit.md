# Final pre-submission audit

29 October 2026. **Verdict: development evidence is reviewed; the hackathon
submission is NOT READY.** Passing tests and a reproducible development run
cannot substitute for executing the supplied dataset and verifying fresh Colab.
Do not create the final acceptance tag or describe these open gates as passed.

## Connection map

| Connection | Verified evidence | Submission status |
| --- | --- | --- |
| Earlier selection → files → frozen split | 100 manual pairs, official 60/20/20, exact source identities | Development passed; correlated partitions disclosed |
| Frozen split → calibration → selected methods | 98 validation candidates, train-only looks, common VV -18 dB, cleanup separate | Development passed |
| Frozen config → four classical result rows | Same scored pixels, fixed macro set, ENL/radiometry and separate synthetic PSNR | Development passed |
| Config → paired training → checkpoints → neural results | Shared normalization/crops, original checkpoint hashes, 40 native masks and counts verified | Development passed; one seed |
| Public release → downloaded ZIP → model preflight | Published digest and inner hashes match; both checkpoints load | Development passed |
| Development notebook → setup/access/audit/calibration/export | Ten cells completed on cached Linux in 91.78 seconds | Development smoke only |
| Supplied first-100 recipe → executable acquisition/notebook | Exact IDs/hash recorded, but no executable supplied-set profile consumes them | **Blocked: implementation/execution required** |
| Supplied data → internal split → new calibration/results | All 100 source IDs are upstream train; internal membership unassigned | **Unrun** |
| Fresh Colab → uncached download → full timed export | No actual fresh Colab result ZIP/sidecar exists | **Unverified** |
| Reviewed implementation → default public branch | Public repo exists; implementation is in draft PR #1, not `main` | Final publication pending |

## Material findings and fixes

**S1 / P1 — Supplied dataset is not connected to the notebook.** The required
definition is now the first 100 ordered rows of the official hand-labeled
training CSV. The current executable notebook consumes the earlier 60/20/20
selection instead. Its organizer override intentionally stops before calibration.
Only 22 supplied IDs overlap, all already used by the published development
model for training. Neither copying the old ROI/config/checkpoint files nor
renaming the tables resolves this.

Remaining resolution: implement one bounded supplied-selection acquisition
profile, verify its exact objects and metadata, freeze internal event/scene/
spatial groups before tuning, establish new training-only ROIs/normalization,
carry the supplied source/split/exposure identities through calibration, then
run the locked classical and any promised learned comparison separately. Group
constraints take precedence over exact 60/20/20 patch counts. The unchanged
development results stay labeled as development. This is a new execution gate,
not a reason to search for another model or tune against observed test results.

**S2 / P1 — Fresh uncached Colab is unverified.** The recorded 91.78 seconds used
cached TIFFs, an existing clone and preinstalled notebook prerequisites on Linux.
The remote 122.06-second training pair is a different measurement. Retain an
actual fresh-Colab full-profile ZIP plus its authoritative timing sidecar,
source/configuration/data identities, hardware and setup/download/evaluation/
export times, strictly below 1,800 seconds. Earlier browser attempts reported
local browser use disabled; no successful Colab run is inferred from them.

**F1 / P2 — Misleading generic calibration provenance: fixed.** The calibration
CLI previously labeled any accepted manual manifest as upstream development.
It now uses `audited_manual_subset_calibrated` and `audited_manual_subset` for
generic status/source. A real generic fixture reproduced the failure before
the fix, then passed. This changes only new-run provenance labels; all frozen
configurations, method choices and result artifacts remain unchanged. Neutral
labels do not provide the missing supplied-profile source-configuration binding;
that remains part of S1. The organizer stop is retained and regression-tested.

**F2 — Stale submission descriptions: fixed.** The report, demo, reproduction
guide and first notebook page now state that the supplied definition is known,
is distinct from the measured development set and remains unrun. The guard
message explains the missing profile rather than the old provenance-label bug.

**S3 — Default public branch is not the implementation.** The GitHub connector
confirmed `main` is the default branch and still contains planning-only content;
draft [PR #1](https://github.com/kaustubh-dot/sar-water-mapping/pull/1) holds the
implementation. Keep the PR draft while S1/S2 remain open. Once acceptance
passes, publish the reviewed implementation and pin the submitted notebook/link
to its exact accepted commit. Existing development checkpoint references remain
at their original training commit; a documentation commit is not retraining.

## Evidence reviewed

The independent [connections review](submission_connections_review.md) traces
the supplied acquisition/CLI/notebook gaps. The independent
[scientific review](submission_scientific_review.md) verifies all 21 indexed
artifacts, six real segmentation score rows, 40 saved neural masks against
their source labels/validity, 72 synthetic measurements, 16 ENL aggregates,
validation selection and public checkpoint delivery. No new unresolved
scientific defect was found in the recorded development results.

Source/data provenance: [supplied recipe](supplied_subset_recipe.md),
[ordered supplied IDs](supplied_subset_selection.csv),
[development manifest](source_identity-v3/manifest.csv),
[checkpoint delivery](checkpoint_delivery.json),
[reproduction instructions](../docs/REPRODUCING.md).
Current verification and gate values are recorded in
[submission_verification.json](submission_verification.json).

## Finish in this order

1. Close S1 with a reviewed supplied-set profile and frozen internal data split.
2. Run its bounded validation, freeze choices, then evaluate its held-out data;
   use separate result/configuration/checkpoint identities and disclose prior
   exposure. Preserve all negative findings and current development results.
3. Close S2 with actual fresh uncached Colab evidence for the connected profile.
4. Update the report/demo from those measured results, publish the reviewed
   implementation and verified links, then create the final submission tag.

This audit fixes the bounded provenance/documentation defects and identifies
the remaining work explicitly. It does not certify a perfect or completed
submission while S1/S2 remain open.
