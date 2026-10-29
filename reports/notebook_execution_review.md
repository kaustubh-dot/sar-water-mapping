# Independent review of executed notebook smoke

29 October 2026. **Accept the actual cached Linux CPU notebook execution.**
All ten executable cells completed in order, with no error outputs, on the
reviewed source commit. Calibration and evaluation artifacts have consistent
identities and scientific outputs. This run does not close the fresh Colab
under-30-minute gate or establish fresh full-data-download runtime.

The [public summary](notebook_smoke_summary.json) preserves measured values and
hashes while omitting absolute host paths. The original executed notebook,
timing sidecar and copied run artifacts remain under ignored
`outputs/notebook-smoke-evidence/`. No implementation change was needed.

## Source and execution identity

Compared every cell against the notebook in commit
`61b09f9bfa61114d83bd7be19eba3de67d5621db`. The only source change is cell 3:
`REPO_REF` changes from the development branch to that exact full commit SHA.
All other code and Markdown sources are identical. Kernel metadata identifies
the dedicated Python 3.12.3 kernel; code execution counts are exactly 1–10.
The saved scientific-check output records **76 passed in 5.33 seconds**.
Checkout output and runtime artifacts agree on the exact commit, and the
evaluation runtime records a clean source checkout. All six calibration code
hashes match that commit's file bytes.

The execution owner reports that the initial smoke-runner attempt used a
short commit SHA and stopped during fetch, before data access. Its failed
notebook was preserved outside Git. The successful run used the full SHA in
a separate isolated clone; the failed attempt contributes no scientific
result to this review.

## Input and calibration checks

Independently checked the copied manifest, splits, configuration, training
looks, validation report, provenance and download log:

- Exactly 100 manual-label VV/VH dB pairs retain official 60/20/20 membership.
  Source-object names, generations, sizes and SHA-256 values match the prior
  reviewed 200-object download record. The copied selection and all three
  official source-list hashes match their recorded identities. Manifest paths
  use portable relative separators.
- Six 32 × 32 training ROIs belong to three training patches. Five 32 × 32 ENL
  ROIs belong to four held-out patches. All recorded bounds fit the native
  512 × 512 images. This checks membership and bounds; the raw-image
  homogeneity decisions remain the previously recorded ROI selection.
- Configuration paths/hashes bind the actual copied manifest, split, training
  ROI and looks files. The validation report binds the same inputs and exact
  configuration bytes. The exported result configuration has that same hash.
  Validation source identities contain no test patch, and the report records
  zero test source files opened during calibration.
- Calibration produced 98 candidates and four separate cleanup records.
  Selected choices exactly match reviewed calibration v2: common VV fixed
  −18 dB; Median window 5; Lee window 5; bilateral color sigma 3 dB, window 5,
  spatial sigma 2; selected filtered input Median. Constant-image fallbacks
  remain VV −18 and VH −24 dB.

Cross-platform numerical equality is not claimed. Four of the 98 validation
candidates differ from the Windows v2 run by one or two FP/TN pixels, with no
TP/FN changes. These differences do not change the selected settings. The
largest relative training-looks difference is approximately `1.62e-10`.

## Held-out outputs and visual checks

The real table has four primary rows with cleanup disabled, 80 per-patch rows,
and a separate four-row cleanup ablation. Every primary method uses the same
ground-truth-water-positive macro set and retains dry-patch false-positive
reporting. All four primary held-out confusion counts exactly match the
previously reviewed classical run. Water IoUs are raw `0.6084145491`, Median
`0.6304119335`, Lee `0.6069724595`, and bilateral `0.6303737615`.

The ENL table has 40 band/ROI/method observations, all with `ok` status, from
the preselected test ROIs. Synthetic evidence remains separate: 126 validation
rows, 72 test rows, eight selected settings and eight summary rows. Test rows
identify simulated backscatter and test-only phantom membership.

Inspected the notebook's embedded training contact sheet and sampled aligned
held-out diagnostic grids. VV/VH, filtered images, masked labels, prediction,
FP/FN errors and the power ratio are visible and aligned. The sample includes
substantial missed water, so the figures do not hide threshold failure. This
is sampled visual review; the reviewer did not inspect every exported image.

## Timing and archive evidence

The authoritative sidecar records **91.7843061760068 seconds**, from the first
executable cell through the single ZIP write and checksum. Its exact contents
match the final cell's printed evidence. The outer execution script records
92.72281846194528 seconds. Cell execution timestamps agree with that duration.
The stage durations are nonnegative and consistent with the total; download
verification is explicitly included in the nonadditive data-access stage.
Final ZIP work contributes 1.9844690489117056 seconds. The primary evaluation
runtime is a narrower inner measurement and is not substituted for the
notebook total.

The execution owner recomputed the original remote ZIP checksum and supplied
its complete entry listing in ignored
`outputs/notebook-archive-verification.json`. This reviewer checked that
evidence against the timing sidecar and expected outputs, rather than fetching
and independently rehashing the entire 103,740,669-byte ZIP. It records 659
entries and SHA-256
`70455a43e8041bd2e11ee190fbb78d855062c6a7e5e3b6a68252582b4dcb3c90`.
The listing contains all 80 expected held-out diagnostic PNGs, the audit
contact sheet, tables, input snapshots and bundle manifest. It contains 90
PNGs overall because test fixtures also generate images. No selected real
source TIFF is included; TIFFs under `pytest/` are generated fixtures.

The exact authoritative sibling timing-sidecar name is absent from the ZIP,
as designed. Other fixture runtime files inside `pytest/` are not that
sidecar. The in-ZIP bundle manifest agrees with the sidecar on identities and
pre-archive stages. The public summary retains the original sidecar SHA-256
`e96898840f9c7554d0700fc23c2d8206e524ba9ae852aea01c450db1a298e5c3`
and hashes of the other original evidence files.

## Limits and remaining gate

This was a fresh execution kernel on an authorized Linux CPU, using an
existing dedicated environment, existing clean isolated clone and 200 cached
TIFFs. Initial clone/cache preparation and nbclient/ipykernel setup preceded
the notebook clock. The notebook did execute its installation commands and
installed the pinned SciPy, matplotlib and pytest versions; NumPy and rasterio
were already installed. These conditions cannot establish uncached setup or
data-download speed. Calibration metadata records 24 CPU threads; RAM was not
recorded by this smoke.

Runtime fields consistently say `local_cpu_not_colab`, neural training is
disabled, and fresh-runtime attestation remains unverified. The sidecar's
`measured_below_30_minutes=true` applies only to this measured cached run.
It is not a fresh-Colab acceptance flag. A fresh compatible Colab run with
documented uncached access, actual CPU/RAM conditions, installation, calibration,
evaluation and exports remains required. Organizer delivery and organizer
calibration support remain open, and no full-training Colab claim follows
from this classical execution.
