# Fresh Colab verification attempts

29 October 2026. Fresh Colab acceptance remains open. These browser-observed
failures are retained independently of the accepted cached Linux evidence.

1. Source `3d3ff7a33869a1650fde4128b20376eacd9f2ddb`: new Colab runtime,
   source reference pinned in the execution copy. Setup completed, including
   pip installation, then the acquisition cell failed at its first import with
   `ModuleNotFoundError: No module named 'sar_water'`. No source acquisition
   had started. The reviewed fix explicitly adds the verified checkout source
   to the existing kernel import path; see `colab_setup_review.md`.
2. Source `a37df8a9f7aa6144f65dcf30af0e6e2cf4fe7e59`: a separate notebook
   and runtime were allocated through Colab Run All. Setup confirmed this exact
   executed source. The next cell found the project package but failed during
   NumPy import: `cannot import name '_slice' from 'numpy._core.umath'` in the
   Python 3.13 site-packages directory. Installing pinned dependencies can
   replace files underneath modules Colab already loaded in its kernel.
   No source TIFF acquisition had started. A restart-safe setup is under review.

Browser access was also interrupted by an account-usage approval failure and
later a stale browser-session error. Resetting the browser control session
restored observation. Colab displayed a reCAPTCHA service connection error;
after the user's reconnect instruction, the runtime reported connected again.
None of these intermediate states establishes a completed benchmark or timing.

Neither failed attempt produced an accepted final result ZIP and timing
sidecar. No new held-out scores, thresholds, architecture or training choices
are selected from these setup failures. Main publication and the final
acceptance tag remain pending actual successful fresh-Colab evidence.
