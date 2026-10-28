# Phase 3 implementation review

28 October 2026. Reviewed the uncommitted bounded denoisers, focused tests,
synthetic evidence script and outputs, configuration, implementation report and
roadmap against `AGENTS.md`, the README, implementation lock and evaluation
protocol. This review covers authorized synthetic development while the
organizer subset remains unavailable. No implementation code was changed.

## Findings

**Critical: none found. Important: none found. Minor: none found in this scope.**

## Scientific and implementation quality

- Raw is a float32 identity on valid linear power. Median uses only windows
  3/5. Lee uses only windows 5/7 and implements exactly
  `s2 = max((v - m*m/L)/(1 + 1/L), 0)`, followed by the clipped `s2/v`
  weight when variance is positive. Local moments accumulate in float64,
  negative roundoff variance is clipped to zero, and no absolute variance
  floor changes intensity scaling. Outputs return float32.
- SciPy half-sample `reflect` and NumPy `symmetric` provide matching edge
  repetition. Explicit reflected-window calculations agree with Lee on
  singleton, narrow and ordinary small arrays. Bilateral uses the locked
  5 x 5 window, spatial sigma 2 and 1.5/3 dB color sigmas, averages in dB and
  converts back to power without intensity stretching.
- Both bands are filtered independently. Every method preserves native shape,
  fills from the deterministic SAR-only nearest-valid adapter, restores the
  original input-invalid locations as NaN and checks finite positive values
  on valid pixels. Input arrays are not mutated. Label validity is not accepted
  as a filtering input. All-invalid patches and invalid valid-pixel power are
  rejected.
- The looks helper uses only explicitly training-member ROIs, excludes invalid
  SAR pixels without filling them for estimation, and takes the per-band median
  of finite, nonconstant population-variance ENL values with a lower bound of
  one. Records retain patch, membership, coordinates, band, valid counts,
  values/statuses and contributing counts. Missing usable ROIs fail explicitly.
  Homogeneity assessment and saving/freezing actual-data estimates remain
  execution responsibilities; no real estimate has been fabricated.
- The evidence script profiles five explicitly synthetic two-band 512 x 512
  arrays for each of seven bounded configurations. Saved durations sum to
  8.617380299954675 seconds; each per-configuration extrapolation correctly
  applies a 50% margin to 100 such arrays. The report clearly excludes setup,
  I/O, other invocations, scoring, figures, training and Colab hardware from
  that extrapolation. It does not claim the whole-workflow budget passed.
- The 126 diagnostic records contain exactly validation identities 06-08,
  L=1/4, seeds 42/43/44 and all seven configurations. Every method receives the
  same corruption. PSNR uses a known simulated reference and explicit range
  1.0; mean-change diagnostics cover both bands. The reported aggregate values
  agree with the CSV, including the substantial downward mean changes for
  Median and bilateral. No final test identity is scored by this script and no
  configuration is selected from these diagnostics.
- Configuration and roadmap retain open real split/calibration/looks freezes,
  the real five-patch pilot and the Colab runtime gate. MIDAL remains unrun and
  unadmitted because its required actual-data pilot is unavailable. Bilateral
  remains the fourth family; no optional method expansion or dependency stack
  was introduced. The combined fixture/runtime checkbox is conservatively
  left open because its actual-data pilot is incomplete.

## Independent verification

- `.venv/Scripts/python.exe -m pytest -q tests/test_filters.py
  --basetemp=.pytest_cache/phase3-review`: **14 passed in 1.39 seconds**.
- `.venv/Scripts/python.exe -m pytest -q
  --basetemp=.pytest_cache/phase3-review-full`: **41 passed in 3.90 seconds**.
- Additional direct checks passed for ten brute-force reflected-window Lee
  cases across both locked windows; nonconstant band independence for every
  setting; and an ROI whose effective looks must be lower-bounded to one.
- Regenerated all 126 saved validation PSNR, MSE and both-band mean-change
  values in memory: every numeric value matched exactly. Verified unique
  identity/looks/seed/configuration keys, validation-only membership, timing
  sample counts/arithmetic, the current configuration SHA-256 and the
  implementation report's evidence links.

**Verdict:** the bounded filter implementation and its synthetic development
evidence meet the locked specification and quality expectations. No fix is
required. This does not close the actual-data Phase 1 gate or the remaining
Phase 3 actual-data/runtime gates. Real looks estimation and freeze, complete
enabled-invocation accounting, validation selection, final test evaluation and
fresh Colab timing remain unrun.
