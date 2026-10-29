# Supplied notebook integration review

29 October 2026. Independent **GPT-6.1 Sol, xhigh** review.

**Decision: ACCEPT the cached Linux notebook integration smoke.** No P1/P2
finding remains in this scope. This supports S1 closure after final document
integration; **S2 fresh uncached Colab remains unverified and deferred**.
No notebook, parameter search, neural inference or source-mask recount was
rerun by this reviewer.

Reviewed the retained original ZIP, executed notebook, wrapper, authoritative
runtime sidecar and extracted metadata/results under
`outputs/supplied-notebook-evidence/`, against the accepted
[training](supplied_training_review.md), [results](supplied_results_review.md)
and [calibration](supplied_calibration_review.md) reviews. The public
[smoke summary](supplied_notebook_smoke_summary.json) records the run conditions.

- All ten code cells executed in order, counts **1–10**, with **zero errors**.
  Output records **96 tests passed in 8.30 seconds**. Every source cell matches
  commit `9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`, except cell 3 replaces the
  branch-valued `REPO_REF` with that exact full SHA. Requested/fetched/executed
  commit records agree; scientific source hashes match the commit. Kernel
  metadata selection does not alter notebook code.
- The run used **200 cached source TIFFs**, an existing clean isolated clone
  and preinstalled kernel prerequisites. Initial clone/cache preparation is
  outside the notebook clock. The original acquisition log's 44 cache copies /
  156 downloads is explicitly historical, rather than this run's access claim.
  Neural training is disabled; runtime and wrapper explicitly exclude fresh
  Colab acceptance.
- Reconstructed the relative metadata layout using copies only, then ran the
  strict source verifier and the executed notebook's identity guard with TIFF
  opening blocked. Both pass. All 100 manifest source/file digests, membership,
  units, masks/counts and provenance match the accepted data. Source CSV,
  recipe, acquisition, split, ROI, looks, source configuration and experiment
  hashes bind consistently before evaluation. The run-local manifest/config
  hashes appropriately differ from the earlier path-bound files; the fixed
  split and source identities are preserved, including 5/9/8 historical
  exposure and the restriction on old development checkpoints.
- All **98 saved validation scientific summaries** match the accepted
  calibration. The shared policy remains **VH below −20 dB**, cleanup off,
  Median 5 / Lee 5 / bilateral color sigma 3 dB; Median 5 is selected. The
  validation record reports zero test-file access.
- All four held-out confusion counts, **124 per-patch rows**, fixed macro/dry/
  no-score summaries and separate cleanup summaries match the accepted
  classical results exactly. Every method retains 31 Ghana IDs, 4,940,307
  scored pixels, 144,891 water pixels, 15 water-positive macro patches,
  15 scored dry patches and one no-score patch. The 40 ENL records/eight
  aggregates match exactly. The 72 synthetic test rows, eight means and eight
  selected settings match within numeric tolerance. Radiometry differs only
  in 44 floating-point values, maximum absolute difference `2.561e-10`
  (relative `5.498e-9`). No scientific choice or count changed.

| Classical row | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: |
| Raw | 98560 | 210666 | 46331 | 4584750 |
| Median 5 | 98436 | 93164 | 46455 | 4702252 |
| Lee 5 | 91209 | 80270 | 53682 | 4715146 |
| Log-bilateral | 98170 | 111737 | 46721 | 4683679 |

The original **164,908,503-byte** ZIP has 3,428 entries; independent reads
verified CRCs for all 3,209 files. Its 2,662 TIFF members are all under pytest
directories, and none matches any of the 200 actual source-file hashes. The
flagged supplied-profile test directory contains 200 fake TIFF bodies
(87–98 bytes, `verified fixture bytes:` prefix), seven metadata files and its
directory entry. It contains no actual source TIFFs. No checkpoint occurs
outside pytest. All 38 extracted metadata/result files match their ZIP bytes.
The original archive and private execution artifacts remain outside Git.

The sidecar is outside the ZIP, as designed, and its archive SHA agrees with
the original file. Its **123.04392587998882 seconds** cover the first executable
cell through the sole final ZIP write and checksum. The wrapper's
123.90463726990856 seconds has a broader execution scope. Setup/install, data
verification, checks, audit, calibration, evaluation, display and final export
stages are present; nested data-access timing is not added twice. This is a
cached Linux integration measurement, not evidence of a fresh Colab run below
30 minutes or of full neural training inside that budget.

| Retained identity | SHA-256 |
| --- | --- |
| Original notebook ZIP | `968b9065b9ded3fb0c3c472e10e4fccf60c12a1f10c5f82481698de841577cef` |
| Executed notebook | `2c26afb4aed6f53bd85398cf3ec1e438d2fb074e4162dd62ad9a23a7ce495c4a` |
| Original timing sidecar | `ff6c329593f4c085e5cf2fa535c062b3ce40916ce1ea0dbe3e3608d48b54e374` |
| Run-local experiment | `ab03d16d768705cb01a467aa14ef1fde2dffd5b66a35ca03f7c04b838352be32` |
| Run-local manifest | `8d89ec95ec75d3fbb34aa0186b8600b166cfaed410948ff158cdaaaf399bb3ae` |
| Run-local source configuration | `f358aaa01a33cd690d63dc217a7700fb6de4d2d9586eb9f94c0d2bad2c738af0` |

Final document/status integration remains a separate review. S3 publication to
`main` and the final acceptance tag also remain pending.
