# Three-minute demonstration

## Supplied-first100 measured outline

**[Independent results accepted](supplied_results_review.md).** Data/profile,
calibration and scratch training are also accepted. The cached supplied
notebook execution and review are also accepted, closing S1.
Uncached Colab is deferred; final READY status, `main` publication and the tag
remain open. The reviewed supplied checkpoint ZIP is local only.

**0:00–0:30 — Problem and data.** Explain observed surface-water mapping from
VV/VH SAR, its speckle and dark-target ambiguities. Show the exact supplied
first100 manual-pair recipe and frozen event split: 29 train, 40 validation,
31 Ghana test. Disclose 22 prior project training exposures, including eight
current test IDs; this is not pristine blind evaluation. One test member has
no scored pixels and stays in the fixed membership.

**0:30–1:00 — Controlled experiment.** Show the accepted source/calibration
bindings. Compare raw, Median 5, Lee 5 and log-bilateral with shared VH below
-20 dB and primary cleanup off. Compare the same compact U-Net trained from
scratch on raw versus Median-5 input, with fixed probability strictly above
0.5. The same 4,940,307 scored pixels and 15 water-positive/15 dry/one no-score
patch sets apply across all six rows.

**1:00–1:40 — Recorded results.** Open the
[supplied classical table](supplied_classical-v1/results_real.csv): pooled IoU
is raw 0.2772, Median 0.4135, Lee 0.4051, bilateral 0.3825. Open the
[neural table](supplied_neural-v1/results_neural.csv): raw U-Net IoU/F1 is
0.4208/0.5923; Median-input U-Net is 0.4043/0.5758. Preserve the worse filtered
model. Explain the separate fixed macro mean and dry false positives. Do not
change a method from these test outcomes.

**1:40–2:20 — Detail and limits.** Show the lexicographically first held-out
patch, [Ghana_103272 Median](figures/supplied-v1/Ghana_103272_median.png) and
[U-Net predictions](figures/supplied-v1/Ghana_103272_neural.png). Point to pond
boundary expansion and isolated dark detections scored as false positives;
dark backscatter alone does not prove labels wrong. All five ENL regions are
visually selected land, with no promised water ENL. Smoothing raises ENL but
does not guarantee better segmentation. Synthetic PSNR uses known procedural
references in a separate table, never noisy real SAR as clean truth. Cleanup
is a separate predeclared ablation: raw IoU 0.2772 to 0.3903, Median 0.4135 to
0.4175; it does not replace the primary rows.

If discussing ROI provenance, disclose that one of the five ENL regions has
valid SAR but no valid label pixels; retain its visual-land tag and shared
SAR-only ENL use without replacing the region.

**2:20–3:00 — Reproduction.** Open the single supplied-default notebook, source
identities and output tables. Distinguish 76.77 seconds of remote paired
training from 59.38 seconds of classical CPU runner work (including synthetic
work and 124 figures) and 9.06 seconds of GPU checkpoint evaluation. Their
scopes exclude setup/access/calibration and final metadata writes. The accepted cached
supplied notebook took 123.04 seconds at pin
`9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f`, with 10 cells and 96 passing checks.
It used 200 cached TIFFs, an existing clean clone and preinstalled kernel
prerequisites; initial clone/cache preparation were outside the clock.
The [summary](supplied_notebook_smoke_summary.json) and
[notebook review](supplied_notebook_review.md) accept this cached integration
and close S1.
Uncached Colab and the under-30-minute gate
remain unverified. Existing development tables stay separately labeled below.

## Earlier development demonstration reference

Development demonstration only. All reported results below use the earlier
60/20/20 selection, not the newly supplied first-100 training-row recipe.
Retain these historical measurements alongside the separately labeled,
accepted supplied-set experiment above.

**Current supplied status for the opening/closing slide:** the exact first100
acquisition, raster audit, fixed ROIs and source-aware notebook profile are
accepted. Its seed-42 event split is 29 train (Mekong/Nigeria/Pakistan), 40
validation (India), 31 test (Ghana), with no cross-partition overlap or touching
chips found. Disclose 22 prior project training exposures, including eight
current test IDs; this is not pristine blind evaluation. One test patch has no
scored pixels, and all five fixed held-out ENL rectangles are visually selected
land regions. The [accepted calibration](supplied_calibration_review.md) selected
shared VH below -20 dB with Median 5 as neural input and opened no test files.
The [accepted scratch GPU pair](supplied_training_review.md) took 76.77 seconds
including preparation: raw 10 epochs/150 updates, Median 5 nine epochs/135
updates. Supplied held-out measurements are now independently accepted in the
[result review](supplied_results_review.md). Cached supplied notebook smoke is
accepted at 123.04 seconds; S1 is closed. Uncached
Colab is deferred; final READY status, `main` publication and the tag remain open.

**0:00–0:30 — Problem.** Monsoon clouds obstruct optical mapping. Sentinel-1 SAR
provides observations through clouds, but multiplicative speckle makes a simple
dark-pixel water threshold noisy. Our output is surface water; identifying new
flooding requires information about permanent water.

**0:30–1:00 — Controlled experiment.** Show the audited 100-patch upstream manual
subset and frozen 60/20/20 membership. Acknowledge touching chips and shared
events. Compare raw, Median, multiplicative Lee and log-bilateral, with one
validation-selected VV threshold of -18 dB and no primary cleanup. All methods
share masks, test patches and scoring pixels.

**1:00–1:40 — Measured results.** Open `results_real.csv`: raw water IoU 0.6084,
Median 0.6304, Lee 0.6070, bilateral 0.6304. Explain the separate water F1 and dry
false positives. ENL increases after smoothing, yet Lee does not improve water
IoU. Show `results_synthetic.csv`: known references allow PSNR; noisy real SAR
does not supply a clean reference. Synthetic Lee PSNR gains are not a claim of
best real water segmentation.

**1:40–2:20 — Failure.** Show `figures/India_591317_median.png` and
`figures/Paraguay_913449_median.png`. Broad water remains, while some narrow
channels disappear or remain below the threshold. Point to false-negative
pixels and scene structure in the ratio. Median cleanup slightly worsens IoU;
we retain the negative result rather than selecting against test outcomes.

**2:20–3:00 — Reproduction and limitations.** Open the single notebook and
explain its classical full profile, saved checksums, fixed decisions and result
bundle. Distinguish remote U-Net training from checkpoint inference and fresh
Colab timing. The raw/Median U-Net pair completed in 122.06 seconds; test IoU
was 0.5855/0.5346, below the classical Median row. The classical notebook
completed in 91.78 seconds on Linux using cached data, an existing clone and
a preinstalled kernel; fresh Colab Run All remains unverified and deferred.
The single notebook now defaults to the accepted supplied-first100 source
profile. Its accepted held-out results appear in the separate outline above;
these development measurements remain historical reference.
Close with the practical finding: a small classical pipeline yields a measured
water-IoU gain here, while smoothing alone cannot guarantee better mapping.
