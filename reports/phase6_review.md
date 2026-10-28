# Phase 6 implementation review

29 October 2026. Independent review of `src/sar_water/evaluate.py`,
`tests/test_evaluate.py`, `notebooks/01_sar_water_mapping.ipynb`, and
`requirements-colab.txt` against `AGENTS.md`, the README, roadmap,
[implementation lock](../docs/IMPLEMENTATION_LOCK.md), and
[evaluation protocol](../docs/EVALUATION_PROTOCOL.md). Supporting reads covered
the existing data adapter, validation selector, and metrics. Source code was not
changed during this review.

**Assessment: request the bounded fixes below before accepting final benchmark
runtime evidence.** The focused tests establish fixture behavior, not actual-data
calibration or fresh Colab compatibility. Phase 6 is not complete.

## Material findings

1. **P2 — primary method runtimes include a separate ablation for only two
   methods.** `src/sar_water/evaluate.py:106` starts the primary timer before the
   patch loop; lines 116–121 run cleanup only for raw and the selected filter;
   lines 131–135 save the entire elapsed interval as primary method seconds.
   These rows therefore include extra segmentation/cleanup work that the Lee
   and bilateral rows may not perform, while that work is also exported as the
   separate cleanup time at lines 139–144. A probe wrapping cleanup with a
   50 ms delay for each of two fixture patches produced primary times of
   0.1039 s raw and 0.1050 s median, versus 0.0019 s Lee and 0.0031 s bilateral.
   The cleanup rows independently reported 0.1028 s and 0.1031 s. Separate
   comparable primary filtering/segmentation/scoring timing from cleanup and
   diagnostics/figure timing, and add a focused regression showing that extra
   cleanup cost cannot inflate primary method time.

2. **P2 — the notebook accepts Python 3.11 although the pinned Colab profile
   requires Python 3.12.** `notebooks/01_sar_water_mapping.ipynb:13` checks only
   Python >=3.11, but `requirements-colab.txt:3` pins NumPy 2.5.4 and line 5 pins
   rasterio 1.5.2; the installed distributions' `Requires-Python` metadata is
   `>=3.12` for both. Installation at notebook line 32 will fail in an otherwise
   accepted Python 3.11 runtime. Raise this profile's explicit Python gate and
   guidance to >=3.12, or establish a compatible set of pins through actual
   verification. The package's broader Python support alone does not validate
   this stricter dependency profile.

3. **P2 — the documented exact-commit reproduction path does not work.**
   `notebooks/01_sar_water_mapping.ipynb:25` invites replacing `REPO_REF` with a
   reviewed commit SHA, but line 32 supplies that value to `git clone --branch`.
   That option resolves a branch or tag rather than an arbitrary commit SHA.
   A fresh run configured as documented will fail before installation. Use a
   clone/fetch/checkout sequence that supports the recorded commit and verify
   the executed SHA; also handle the existing-checkout path explicitly before
   describing an input reference as exact reproduction.

4. **P2 — the saved notebook total omits an enabled final archive write.**
   `notebooks/01_sar_water_mapping.ipynb:91` records `total_wall_seconds` and
   `measured_below_30_minutes` before a second complete `make_archive` call.
   The second write is printed separately, but is absent from both the saved
   total and its below-budget predicate. The protocol requires the complete
   enabled workflow, including exports, in total wall time. Include the final
   packaging work in the authoritative elapsed time and budget decision, with
   a durable timing artifact that avoids an unmeasured archive refresh loop.

## Verified scientific behavior

- Frozen settings are validated before the disk runner opens the manifest or
  test inputs. The runner binds the configuration to manifest/split hashes,
  validates membership, rejects conflicting/duplicate splits through the
  existing data adapter, and checks held-out image/mask file hashes plus the
  decoded image hash when present (`evaluate.py:275`–312).
- The four primary methods use one frozen channel and rule; a shared fixed
  strategy uses the same numeric threshold. Locked filter settings, finite
  per-band looks, and cleanup disabled are required (`evaluate.py:28`–66).
- The macro population is fixed from ground-truth water-positive scored pixels
  before iterating over methods (`evaluate.py:102`–103). The focused fixture
  verifies the common macro patch IDs, pooled counts, dry false positives,
  independent validity masks, and separate raw/selected-filter cleanup rows.
- ENL is calculated from supplied rectangles in linear power, separately by
  band. ROI coordinates, suitability, class, finite/undefined status and
  median/interquartile summaries are retained; missing ROIs remain explicit.
  Actual ROI suitability and preselection remain data-dependent audit gates.
- Synthetic parameters are selected using validation identities before any
  test phantom is constructed, with shared Gamma corruption, known looks,
  explicit range 1.0, and raw/noisy included. The held-out outputs contain
  72 records in a separate synthetic table; these are simulated references,
  not clean real SAR (`evaluate.py:163`–207).
- Strict JSON exports, configuration and data hashes, label-provenance claim,
  runtime profile, source commit/dirty status and selected dependency versions
  are recorded. Aligned raw/filtered display limits, prediction/errors and
  power-ratio figures are implemented. The runner explicitly records that it
  has not verified a fresh Colab run and that classical evaluation includes
  no neural training (`evaluate.py:346`–367).

## Verification evidence

- `.venv/Scripts/python.exe -m pytest -q tests/test_evaluate.py
  --basetemp=outputs/pytest-phase6-review-venv`: **5 passed in 18.94 s**.
- Parsed the notebook JSON and compiled the AST of every code cell: all code
  cells parsed. The notebook cells are unexecuted; this is syntax verification.
- Queried installed NumPy/rasterio distribution metadata for the Python-version
  finding above. No dependency installation or fresh Colab run was performed.
- The cleanup-delay probe above exercised the existing fixture without editing
  implementation or test source. It demonstrates why the passing tests do not
  establish comparable primary runtimes.

## Open execution and integration gates

The notebook invokes `scripts/calibrate_classical.py` at line 65, and explicitly
fails if it is absent. That script was absent at the review snapshot. This is
an unfinished integration gate, not evidence of completed calibration. Its
agreed CLI must create the versioned frozen config expected by the runner,
using training-only looks ROIs and validation-only method selection, then be
smoke-tested through the notebook command before actual final evaluation.

The organizer subset, its independent-label audit, suitable recorded ROIs,
real validation freeze, complete actual-data benchmark artifacts, and a fresh
Colab Run All below 30 minutes remain required execution evidence. Upstream
development data must remain identified separately. No local fixture runtime,
unexecuted notebook, or inference-only profile closes those gates, and no
neural training/accuracy result is established by this classical runner.

## Scoped re-review: four packaging fixes

29 October 2026, later working-tree snapshot. **All four material findings above
are resolved in the reviewed implementation.** This accepts the bounded
packaging changes for further execution; it does not accept a fresh Colab
runtime or mark Phase 6 complete.

- `evaluate.py:109`–138 now accumulates only primary filtering, segmentation
  and scoring work. Cleanup, ROI/radiometry diagnostics and optional figures
  have separate timers. The new regression at `tests/test_evaluate.py:72`–102
  advances a deterministic clock independently for each operation and requires
  all four primary rows to remain at two seconds while cleanup/diagnostic/
  figure costs appear only in their own fields.
- The notebook's first code cell now rejects Python below 3.12 before
  installation, and its language metadata agrees. The regression tests both
  rejection of 3.11 and acceptance of 3.12 (`tests/test_evaluate.py:193`–199).
- `checkout_source` at notebook line 36 clones without checkout, fetches the
  explicit reference, verifies a requested full SHA, checks out the resolved
  commit detached, and verifies HEAD. Existing checkouts must have the expected
  origin and no uncommitted changes. The local fixture verifies a full SHA,
  refresh to a later branch head, and preservation of a dirty checkout.
- `export_bundle` at notebook line 104 writes one archive, computes its
  checksum, and then records the authoritative total and budget decision in a
  linked sibling sidecar. The in-archive manifest points to that sidecar.
  There is no second archive refresh. The regression moves the clock from
  1790 to 1812 seconds during archive/checksum work and verifies that the saved
  below-30-minute predicate becomes false. The tiny final sidecar serialization
  and subsequent display are explicitly excluded from this internal clock;
  an actual fresh Run All remains separately required.

Fresh verification:

- `.venv/Scripts/python.exe -m pytest -q tests/test_evaluate.py
  tests/test_neural_evaluation.py --basetemp=outputs/pytest-phase6-rereview`:
  **15 passed, 1 failed in 32.35 s**. The sole failure was the local Git fixture:
  Git for Windows' helper failed with sandbox `NtCreateDirectoryObject`
  access denial, before the new checkout logic could complete.
- Re-ran only that local fixture outside the sandbox:
  `.venv/Scripts/python.exe -m pytest -q
  tests/test_evaluate.py::test_notebook_checkout_supports_commit_sha_and_refreshes_existing_branch
  --basetemp=outputs/pytest-phase6-rereview-git`: **1 passed in 3.51 s**.
  This fixture uses temporary local repositories, with no network source.

## Neural checkpoint-evaluation extension review

Also reviewed `scripts/evaluate_neural.py` and
`tests/test_neural_evaluation.py`, with supporting reads of the existing
normalization, prediction, checkpoint and best-checkpoint training code. The
seven neural-evaluation fixture cases passed in the combined run above.

`evaluate_neural.py:30`–96 validates the frozen classical configuration,
manifest/split file identities and membership before loading the training
report. It requires a completed uncapped pair, locked training configuration,
matching subset/split/filter/config/ROI identities, and raw-training
normalization IDs/counts. Both saved checkpoints must match report/config,
normalization, condition, best epoch/IoU, weight state and best-epoch update
count before `_heldout_patches` opens any test image or mask at lines 99–118.
The native predictor uses shared recorded raw-training normalization and
strict probability `>0.5`. No normalization, filter, threshold or checkpoint
selection is fitted to held-out labels in this path.

The raw/filtered evaluations retain independent input/label scoring masks,
the same ground-truth-water-positive macro set, pooled/per-patch metrics and
dry false positives. Outputs are a separate neural segmentation table, strict
JSON, per-patch rows and optional recorded training/validation curves. ENL and
PSNR are explicitly not applicable. Remote training time and actual updates
are recorded separately; profile is `checkpoint-evaluation`, training is not
included, and fresh Colab verification remains false. This helper exports
scores and learning curves; native prediction-mask artifacts are not currently
saved, despite the first test's broader name. Final native-mask/failure-figure
delivery remains an execution/output gate.

**One P2 provenance fix remains before accepting neural result exports:**
`scripts/evaluate_neural.py:187`–208 records the training source commit but not
the source commit and working-tree status of the evaluator that produced the
new scores. The protocol requires runtime source identity, and these two code
snapshots can differ. Record the evaluation commit and dirty status separately,
as the classical runner already does. No actual held-out neural experiment was
run in this review.
