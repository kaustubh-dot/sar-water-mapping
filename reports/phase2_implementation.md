# Phase 2: trustworthy metrics and simulated baseline

Verified 28 October 2026. This is synthetic development authorized while the
organizer subset remains absent. The actual-data Phase 1 gate stays open.

## Implemented contract

`metrics.py` scores only the intersection of SAR validity and label validity,
ignoring label `-1`. It retains TP/FP/FN/TN and derives pooled water IoU/F1,
precision and recall. Zero denominators produce null. No valid pixels never
produce a perfect score. Macro water IoU/F1 use every ground-truth-water-positive
patch, independent of predictions; an optional fixed identity list is checked
against that set. Undefined precision is omitted from its own macro mean with
an explicit count. Dry patches contribute confusion counts to pooled scores and
receive separate false-positive pixel, rate and affected-patch summaries.

ENL accepts one explicitly selected homogeneous positive-power region, uses
population variance and requires at least two samples. Constant regions return
`value=null,status=zero_variance`; no epsilon creates an artificial finite win.
PSNR requires an explicit positive finite data range, a known reference, and
finite scored samples. Identity returns positive infinity with status `identity`;
consumers writing JSON should encode that explicit status instead of JSON Infinity.

`synthetic.py` defines 12 distinct deterministic 256 x 256 float32 simulated
backscatter references within [0.01,1.0]. They contain homogeneous blocks,
sharp boundaries, narrow low-power rivers, circular low-power regions, and
sinusoidal texture. These are procedural test patterns, not realistic clean
Sentinel-1 images. Identities 00–05 train, 06–08 validation and 09–11 test are
defined before corruption. No fitting or tuning has occurred.

Corruption is `Y=X*N`, `N~Gamma(shape=L,scale=1/L)`, for L=1,4 and seeds
42,43,44. The generator returns identical corruption on repeated calls with the
same reference, looks and seed, so future methods receive shared observations.
Seeds reuse the same normalized noise field across equal-sized phantom
identities; these repetitions are not independent geographic samples. No noisy
output is clipped. Scoring uses linear power and `data_range=1.0` throughout.

The configuration records locked bounded candidates, primary cleanup disabled,
and pending real-data splits, looks estimation and calibration. It does not
pretend that a channel, numeric threshold or denoiser has been selected.

## Verification and measured simulated baseline

Test-first evidence: the metric and synthetic tests were created before their
modules; the first pytest run failed because those modules did not exist.
The first implementation run had 11 passing tests and one floating-point ENL
comparison failure (3.9999999999999996 versus 4); the assertion now uses a
numeric tolerance. The subsequent full run passed **27 tests in 4.13 seconds**.
This test duration is not a benchmark or fresh Colab runtime.

Reproduce from the repository root using the project environment:

```powershell
.venv/Scripts/python.exe -m pytest --basetemp=.pytest_cache/phase2-check -q
.venv/Scripts/python.exe -m sar_water.synthetic --output outputs/phase2_synthetic
```

Saved local outputs (ignored by Git, reproducible using the command):

- `outputs/phase2_synthetic/synthetic_splits.csv`: all 12 identity memberships.
- `outputs/phase2_synthetic/raw_noisy_psnr.csv`: all 72 per-phantom/per-seed
  records, with source, split, looks, seed, method, range, MSE, PSNR and status.

Run provenance: Windows, Python 3.14.3, NumPy 2.5.4, SciPy 1.17.1;
base commit `99bdd2ac8587d9d14239abfb8bcc9866ac4935b8` plus the uncommitted
Phase 1/2 source changes. Configuration SHA-256:
`cd77606ecf75e45a30abd16ef0e70f18084f36d249b48616ed1b6817070a5067`.
Raw/noisy CSV SHA-256:
`b34b3309056bbae9769b10753dc6bfc423cb394a55bf3eb4a5525f294aa953fa`.

| Simulated looks | Raw/noisy mean PSNR (dB) | Records |
| --- | ---: | ---: |
| 1 | 4.4925411484 | 36 |
| 4 | 10.4643883177 | 36 |

These are arithmetic means of the saved repeated-measurement PSNR values over
all phantom identities for the mandatory raw baseline. They do not select a
method and do not establish real SAR performance, confidence intervals, or
the under-30-minute fresh Colab requirement. Filter comparison and all real-data
measurements remain unrun. No remote GPU or training was used in this phase.
