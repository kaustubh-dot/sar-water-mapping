# Phase 3 implementation evidence

28 October 2026. **Bounded denoiser implementation and synthetic development checks complete; real-data and fresh Colab gates remain open.** Organizer data are unavailable. This work does not freeze real-data looks, segmentation settings, or synthetic final settings.

## Implemented contract

`src/sar_water/filters.py` provides raw identity, power Median windows 3/5, the locked multiplicative local-LMMSE Lee windows 5/7, and dB bilateral window 5 / spatial sigma 2 / color sigma 1.5 or 3 dB. Lee uses float64 moments, population variance clipped at zero, the locked signal-variance expression and no absolute variance floor, then returns float32. It requires explicit per-band known/frozen looks. Bands are independent. Filtering accepts only SAR power and input validity, fills invalid locations with the existing deterministic nearest-valid adapter, and restores NaNs afterward. All-invalid inputs and nonpositive/nonfinite valid power are rejected.

Border semantics are half-sample symmetric reflection with edge repetition (SciPy `reflect`, equivalent to NumPy `symmetric`). The bilateral implementation averages in dB and exponentiates without stretching. This can change radiometric means and is not an unbiased intensity estimator.

`estimate_training_looks` computes per-band median finite nonconstant ROI ENLs, lower-bounded at one. It returns coordinates, patch identifiers, train membership, band, valid sample counts, values, statuses and contributing counts for saving/freeze. It rejects non-training ROIs and failure to obtain a usable ROI for either band. Homogeneity remains a human/data-audit assessment, not a numeric guarantee of this helper. No real ROI has been selected or real looks estimated.

## Verification

The focused test file was added first; the initial run failed because `sar_water.filters` did not yet exist. After implementation, all 14 focused filter tests pass. The complete suite passes **41 tests** using `.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest_cache/phase3_full`.

Checks include analytic border outputs for Median, Lee and dB bilateral; Lee invariance at intensity scale factors 1e-12 and 1e12; bilateral scale invariance; constant/tiny images; independent bands; invalid holes with exact fill/filter/restore comparison; finite positive valid outputs; locked-grid validation; raw identity; and training-only recorded looks estimation and empty/constant ROI rejection.

## Bounded synthetic evidence

Reproduce with `.venv/Scripts/python.exe scripts/phase3_synthetic_check.py`. The script writes the compact [timing record](phase3_synthetic_runtime.json) and [per-identity validation records](phase3_synthetic_validation.csv). It never scores synthetic test identities. It selects no settings.

Timing uses five explicitly synthetic two-band 512 x 512 arrays, derived from training phantom identities 00-04 and known L=4 Gamma speckle. Their second band is a scaled simulated reference, not a satellite acquisition. This local Windows CPU run used Python 3.14.3, NumPy 2.5.4 and SciPy 1.17.1. All seven configurations together took 8.62 seconds of measured filter compute on those arrays. Raw includes the mask/fill adapter overhead.

| Configuration | Five two-band arrays (s) | 100-array extrapolation with 50% margin (s) |
| --- | ---: | ---: |
| Raw | 0.35 | 10.36 |
| Median 3 | 0.80 | 24.04 |
| Median 5 | 1.58 | 47.42 |
| Lee 5 | 0.64 | 19.10 |
| Lee 7 | 0.53 | 15.87 |
| Bilateral 1.5 dB | 2.33 | 69.75 |
| Bilateral 3 dB | 2.40 | 71.98 |

These extrapolations cover only that number/resolution of synthetic filter calls. They exclude setup, I/O, all other validation/synthetic invocations, scoring, figures and training, and do not establish real-data or Colab runtime. The whole-workflow budget gate remains open.

The validation check contains 126 records: three validation identities (06-08), L=1/4, seeds 42/43/44, and seven configurations. All receive identical corruptions; no observation clipping or output stretching occurs. PSNR uses the known simulated reference with range 1.0. The second-band scale check is reported through its radiometric mean change; PSNR is recorded for the original reference band.

| Configuration | Mean PSNR L=1 (dB) | Mean PSNR L=4 (dB) | Mean power change L=1 (%) | Mean power change L=4 (%) |
| --- | ---: | ---: | ---: | ---: |
| Raw | 4.148 | 10.124 | 0.000 | 0.000 |
| Median 3 | 11.446 | 17.528 | -25.691 | -7.360 |
| Median 5 | 12.885 | 20.033 | -29.324 | -8.463 |
| Lee 5 | 16.722 | 21.554 | -0.095 | -0.135 |
| Lee 7 | 18.770 | 23.062 | -0.136 | -0.175 |
| Bilateral 1.5 dB | 5.152 | 12.757 | -4.854 | -4.487 |
| Bilateral 3 dB | 7.769 | 16.767 | -15.297 | -8.383 |

Means average the nine validation identity/seed records per L. These figures describe the fixed phantoms only. Bilateral and Median show substantial downward radiometric change here. This is evidence to retain mean-change reporting, not evidence of real-data performance. Synthetic PSNR does not select the real-data filtered input or establish preservation of water boundaries.

## Open execution gates

- Actual organizer subset audit, frozen real split, five representative real development-patch inspections and real-data runtime pilot.
- Training-only homogeneous ROI selection, saved/frozen real per-band effective looks.
- Scalar MIDAL+BM3D admission **not run and not admitted**: the required real five-patch/two-band pilot cannot run without data. No optional stack was downloaded or installed and no compatibility/runtime claim is made. Retain bilateral. Revisit only the existing bounded gate when actual development data arrive, before full validation; no extra comparator has been added.
- Complete enabled-invocation cost accounting and fresh Colab Run All below 30 minutes.
- Validation water segmentation and parameter freeze, followed later by final test scoring. No final synthetic or real test comparison has run in this phase.
