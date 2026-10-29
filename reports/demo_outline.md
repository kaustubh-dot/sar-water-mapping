# Three-minute demonstration

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
a preinstalled kernel; fresh Colab Run All remains unverified. The organizer
archive remains unavailable.
Close with the practical finding: a small classical pipeline yields a measured
water-IoU gain here, while smoothing alone cannot guarantee better mapping.
