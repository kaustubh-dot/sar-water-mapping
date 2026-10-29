# Independent review: fresh uncached Colab execution

29 October 2026. **Decision: ACCEPT S2 for the complete classical profile.**
The retained artifacts and recorded browser observation support a fresh,
uncached Colab CPU execution in **566.397461905 seconds** (9 minutes 26.40
seconds), including one documented dependency restart and its wait. No
unresolved P1/P2 finding remains in this scope. Publication to `main` and the
final tag remain separate S3 actions.

Reviewed the original ZIP and authoritative sibling timing JSON retained at
`outputs/colab-20261029T105716698462Z.zip` and
`outputs/colab-20261029T105716698462Z.runtime.json`, against the
[observed-run record](colab_observed_summary.json),
[attempt ledger](colab_attempts.md), [runtime-fix review](colab_runtime_review.md)
and accepted supplied [calibration](supplied_calibration_review.md) and
[result review](supplied_results_review.md). Only archived metadata/results
were read. No source TIFF, calibration, scientific test suite, experiment,
training or inference was rerun, and no parameter was changed.

## Execution and timing

The sidecar, archive manifest, calibration record and classical runtime bind
executed source `3eecc1434991835e576e7d3d09d967fbd9388359`. The requested
reference remains `implementation/remaining-phases`; the recorded resolved
SHA is the exact reviewed execution identity. Calibration's seven scientific
source-file hashes and the dependency-lock hash match that commit. The runtime
records a clean checkout, Python 3.13.18 and the locked NumPy 2.5.4, SciPy
1.17.1, Rasterio 1.5.2 and Matplotlib 3.10.9 versions.

Browser observation records all ten original code cells completing after the
intentional first-pass dependency stop and UI session restart. The scientific
check cell completed, with 42.705531037 seconds recorded. The original executed
notebook and test stdout are not in the retained ZIP, so this review does not
assert an exact Colab test count or independently reconstruct cell execution
counts from saved notebook outputs.

Restart evidence preserves the first run's UTC start and records two setup
passes. The first install took 37.127759119 seconds, restart/user wait
34.332528187 seconds, and second install 12.713363069 seconds. Conflicts were
NumPy 2.1.3 versus installed 2.5.4 and Matplotlib 3.10.0 versus 3.10.9. The
authoritative total includes both passes, wait, uncached access, checks,
audit, train-only looks, validation, evaluation, figures, final ZIP write and
checksum. Nonnested stages sum to 565.828618576 seconds, leaving 0.568843329
seconds of ordinary overhead. Nested acquisition time is not added twice.
The total is strictly below 1,800 seconds.

The sidecar's `fresh_runtime_attestation` retains the notebook's default
`unverified` wording; the runner also retains its generic
`fresh_colab_verified=false` because that function cannot attest to the whole
browser session. These original fields were not edited. Fresh-runtime context
comes from the recorded browser observation, supported by the retained
runtime/access evidence and matching browser-reported archive hash. The
219.691052884-second runner subtotal and its 553.425814552-second value with
supplied setup are not substituted for the final sidecar measurement.

## Data, identity and scientific results

The run reports **zero existing source TIFFs** and 200 downloaded objects
(169,393,092 bytes), with 100 manual-label pairs and the frozen 29/40/31
train/validation/test split. Every acquisition-object digest matches its
audited manifest entry. All original file hashes, native source-domain SAR
hashes, independent validity/scoring counts, units, bands, provenance and
membership match the accepted supplied manifest. Only relocated file paths
and the platform-dependent legacy decoded-power hashes differ; the exact
source-domain hashes provide the accepted portable identity contract.

Independently rehashed the manifest, splits, recipe, selection, source CSV,
acquisition snapshots, source configuration, training/held-out ROIs, looks and
experiment configuration. Their sidecar, source-config, calibration and
runtime bindings agree. Run-specific timestamps and path-bound configuration
hashes appropriately differ from previous runs. All 98 validation summaries
and confusion counts match accepted calibration exactly, with zero recorded
test-file access. Shared **VH below -20 dB**, cleanup off, Median 5, Lee 5,
bilateral color sigma 3 dB and selected Median input remain unchanged.

There are 67 per-patch Otsu-threshold rounding differences, maximum
`2.466142177581787e-6` dB, without any validation-summary/count change.
Train-only look values differ by at most `9.024e-10` in an individual ROI.
No choice was revised from these diagnostic differences.

All four primary rows, 124 per-patch rows, fixed macro/dry/no-score summaries
and four separate cleanup rows reproduce the accepted scientific values
exactly, excluding measured timing fields. Cross-summing the per-patch rows
reproduces these pooled counts:

| Classical row | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: |
| Raw | 98560 | 210666 | 46331 | 4584750 |
| Median 5 | 98436 | 93164 | 46455 | 4702252 |
| Lee 5 | 91209 | 80270 | 53682 | 4715146 |
| Log-bilateral | 98170 | 111737 | 46721 | 4683679 |

Every method retains all 31 Ghana IDs, 4,940,307 scored pixels, 144,891 water
pixels, the same 15 water-positive macro patches and 15 scored dry patches
with 2,066,885 dry pixels. `Ghana_26376` remains present with zero scored
pixels and undefined water metrics.

The 40 ENL records and eight aggregates match exactly. They cover five fixed
visually selected land regions; one region lacks valid labels and remains a
SAR-only diagnostic. Separate synthetic tables match exactly: 72 known-reference
test rows, eight means, eight selected settings and 126 validation rows.
PSNR arithmetic was independently checked against saved MSE and unit range.
The 248 radiometry rows differ in 44 numeric values, maximum absolute
`2.561e-10` and relative `5.498e-9`. All 124 classical PNGs pass decoding and
integrity checks; this does not certify every shoreline prediction.

## Retained artifact integrity and limits

The original 164,922,319-byte ZIP contains 3,490 entries and 3,236 files.
All CRCs pass, with no duplicate paths, absolute/traversing paths or symlinks.
All 2,663 TIFF members are under pytest directories; none hashes to any of
the 200 actual source files. No nonfixture checkpoint is included. The
authoritative sidecar remains outside the ZIP, as designed, and its archive
digest equals the retained file and the browser-reported digest.

| Original retained artifact | SHA-256 |
| --- | --- |
| ZIP | `1e365165f95de72e623a7dd99b1078a97912d0cd99bc24a5bffa570ffc1c29e9` |
| 4,489-byte timing sidecar | `27291c222450c726baa1d933669fb317b20b692ecfe00c4d54044124c4a03b0f` |

The bulky original archive and sidecar are retained locally outside Git;
this review does not claim a public artifact release. The accepted execution
is the full **classical** profile with neural training disabled. It does not
establish full U-Net training inside 30 minutes. The supplied recipe's
authority, 22 prior project training exposures (including eight current test
IDs), manual-label coverage and land-only ENL limitations remain disclosed.
No pristine blind-test, unseen-geography superiority or new-flood-versus-
permanent-water claim is established.
