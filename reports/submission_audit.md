# Final pre-submission audit

29 October 2026. **Verdict: S1 and S2 accepted; S3 publication pending.**
Supplied scientific execution and fresh uncached classical Colab are independently
accepted. Colab completed in **566.40 seconds**, including installation, one
dependency restart, 200 downloads, checks, calibration, evaluation and export.
The original ZIP/sidecar are retained locally outside Git. See the
[independent execution review](colab_execution_review.md).

## Connection map

| Connection | Verified evidence | Submission status |
| --- | --- | --- |
| Earlier selection → files → frozen split | 100 manual pairs, official 60/20/20, exact source identities | Development passed; correlated partitions disclosed |
| Frozen split → calibration → selected methods | 98 validation candidates, train-only looks, common VV -18 dB, cleanup separate | Development passed |
| Frozen config → four classical result rows | Same scored pixels, fixed macro set, ENL/radiometry and separate synthetic PSNR | Development passed |
| Config → paired training → checkpoints → neural results | Shared normalization/crops, original checkpoint hashes, 40 native masks and counts verified | Development passed; one seed |
| Public release → downloaded ZIP → model preflight | Published digest and inner hashes match; both checkpoints load | Development passed |
| Development notebook → setup/access/audit/calibration/export | Ten cells completed on cached Linux in 91.78 seconds | Development smoke only |
| Supplied first-100 recipe → executable acquisition/notebook | Exact ordered IDs, pinned objects, metadata-only source binding and default supplied notebook profile | Accepted implementation |
| Supplied data → internal split → new calibration/results | 100 audited pairs; event split 29/40/31; 98 validation candidates; new scratch pair and separately scored outputs | Accepted data/calibration/training/results |
| Supplied notebook → setup/access/audit/calibration/export | Ten cells, 96 checks, cached Linux run 123.04 seconds through export/hash; original ZIP/sidecar retained and verified | Accepted cached integration; **S1 closed** |
| Fresh Colab → uncached download → full timed export | Original ZIP/sidecar retained; source/data/config hashes, CRC and scientific tables verified; 566.40 seconds | **Accepted; S2 closed** |
| Reviewed implementation → default public branch | Public repo exists; implementation is in draft PR #1, not `main` | Final publication pending |

## Material findings and fixes

**S1 / P1 — Supplied execution: CLOSED after independent phase reviews.**
The exact first 100 ordered official manual-training rows now drive
the bounded acquisition helper and the single notebook's default profile.
All 200 objects and 100 rasters are verified. The existing seed-42 event rule
was frozen before object access: Mekong/Nigeria/Pakistan train (29), India
validation (40), Ghana test (31), with no cross-partition overlap or touching.
Four inspected training ROIs determine looks, and all method choices come
from validation. New models start from matched scratch initialization.

The source/calibration chain, paired training and six held-out score rows are
independently accepted. All 80 validation confusion matrices and 62 test-mask
recounts match exactly. Real ENL and synthetic PSNR remain separate. One test
patch has no scored pixels and stays explicit; every method shares the same
15 water-positive macro patches and 15 dry patches. Five SAR-only ENL regions
retain visual land tags; the fifth has invalid labels and is not independent
ground-truth land. No test-guided model, threshold or ROI changes were made.

Prior project training exposure is still disclosed: 22 supplied IDs, including
eight current test IDs. This is not a pristine project-level blind test. Recipe
sender authority is not independently authenticated. Earlier development
results and checkpoint identities remain preserved and separately labeled.
See the [supplied execution ledger](supplied_execution_ledger.md) and
[accepted notebook review](supplied_notebook_review.md). The retained original
notebook export has SHA-256
`968b9065b9ded3fb0c3c472e10e4fccf60c12a1f10c5f82481698de841577cef`.

**S2 / P1 — CLOSED: fresh uncached classical Colab accepted.** Source
`3eecc1434991835e576e7d3d09d967fbd9388359` completed in 566.397461905 seconds.
The browser-observed fresh runtime had zero existing TIFFs and downloaded all
200 objects. The original clock survives the one dependency restart and its
wait. All ten original code cells completed. The retained 164,922,319-byte ZIP
matches the browser and sidecar SHA-256
`1e365165f95de72e623a7dd99b1078a97912d0cd99bc24a5bffa570ffc1c29e9`.
The independent review verifies archive integrity, source/config/data bindings,
98 validation summaries, all four held-out confusion rows and 124 per-patch
rows, cleanup, 40 ENL records/eight aggregates and separate synthetic tables.
Tiny unselected Otsu-threshold and looks/radiometry roundoff changes no choice
or score. No retuning was performed.

Original generic unverified-attestation fields remain untouched. Acceptance
uses retained evidence together with external browser observation; the archive
alone is not a freshness attestation. Executed notebook/stdout was not retained,
so an exact Colab test count is not claimed. The classical core meets the
30-minute gate. Remote U-Net training and checkpoint evaluation remain separate;
full neural training within the Colab clock was not measured. Historical cached
Linux timings do not serve as fresh-runtime evidence.

**F1 / P2 — Misleading generic calibration provenance: fixed.** The calibration
CLI previously labeled any accepted manual manifest as upstream development.
It now uses `audited_manual_subset_calibrated` and `audited_manual_subset` for
generic status/source. A real generic fixture reproduced the failure before
the fix, then passed. This changes only new-run provenance labels; all frozen
configurations, method choices and result artifacts remain unchanged. Neutral
labels alone did not provide a supplied-profile source binding. That separate
binding is now implemented and accepted under S1. The generic organizer stop
is retained and regression-tested.

**F2 — Submission descriptions updated.** The report, demo, reproduction guide
and roadmap now distinguish measured supplied results from preserved historical
development results. The notebook defaults to the supplied profile. Generic
organizer inputs still stop before calibration; this does not block the exact
supported supplied recipe.

**S3 — Default public branch is not the implementation.** The GitHub connector
confirmed `main` is the default branch and still contains planning-only content;
draft [PR #1](https://github.com/kaustubh-dot/sar-water-mapping/pull/1) holds the
implementation. S2 is accepted and the user authorized publication. Publish the reviewed
implementation and pin the submitted notebook/link to its exact accepted commit. Existing development checkpoint references remain
at their original training commit; a documentation commit is not retraining.

An earlier PR metadata update was blocked by integration authentication.
The current authenticated update succeeded: PR #1 now describes the accepted
supplied profile, fresh Colab execution, 135 passing tests and scientific limits.

## Evidence reviewed

The historical [connections review](submission_connections_review.md) traces
the original supplied acquisition/CLI/notebook gaps. The historical
[scientific review](submission_scientific_review.md) verifies all 21 indexed
artifacts, six real segmentation score rows, 40 saved neural masks against
their source labels/validity, 72 synthetic measurements, 16 ENL aggregates,
validation selection and public checkpoint delivery. No new unresolved
scientific defect was found in the recorded development results. Current
supplied evidence is accepted in the [data review](supplied_data_review.md),
[profile review](supplied_profile_review.md),
[calibration review](supplied_calibration_review.md),
[training review](supplied_training_review.md) and
[result review](supplied_results_review.md) and
[notebook review](supplied_notebook_review.md).

Source/data provenance: [supplied recipe](supplied_subset_recipe.md),
[ordered supplied IDs](supplied_subset_selection.csv),
[development manifest](source_identity-v3/manifest.csv),
[checkpoint delivery](checkpoint_delivery.json),
[reproduction instructions](../docs/REPRODUCING.md).
Current verification and gate values are recorded in
[submission_verification.json](submission_verification.json).

## Finish in this order

1. S1 is closed: data/profile, calibration, scratch pair, frozen results and
   actual notebook execution have each passed independent Sol xhigh review.
   Final documentation/publication consistency is checked separately.
2. S2 is closed: retained original Colab ZIP/sidecar and independent review
   establish the fresh classical run below 30 minutes.
3. Publish the accepted implementation to `main`, verify its remote head and
   create `v1.0-hackathon`. Preserve source-pinned execution links and historical
   development/checkpoint identities.

No unresolved scientific P1/P2 finding remains in the accepted bounded experiment.
Publication is the remaining gate; full neural training in Colab is not claimed.
