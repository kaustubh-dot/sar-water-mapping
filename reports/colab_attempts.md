# Fresh Colab verification attempts

29 October 2026. Fresh Colab acceptance is closed by the retained third run and its independent review. These browser-observed
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
   No source TIFF acquisition had started. A restart-safe setup was subsequently
   implemented, independently reviewed and tested (135 full-suite tests passed).

3. Source `3eecc1434991835e576e7d3d09d967fbd9388359`: browser-observed full
   Colab execution completed in **566.397461905 seconds**, including one
   dependency restart and its wait. The runtime resumed the original clock,
   reported zero existing TIFFs and downloaded all 200 source objects. All ten
   original code cells completed. The original final cell reported archive
   SHA-256 `1e365165f95de72e623a7dd99b1078a97912d0cd99bc24a5bffa570ffc1c29e9`.
   See `colab_observed_summary.json`. Original archive/sidecar files were subsequently saved locally by the user; their hashes, CRC, metadata bindings and scientific results passed independent review in `colab_execution_review.md`. Automated downloads
   through both `google.colab.files.download` and the Files-panel Download
   action produced no browser download event. The original ZIP and timing JSON
   remain visible in the Colab runtime; the user was asked to save them locally.

Browser access was also interrupted by an account-usage approval failure and
later a stale browser-session error. Resetting the browser control session
restored observation. Colab displayed a reCAPTCHA service connection error;
after the user's reconnect instruction, the runtime reported connected again.
None of these intermediate states establishes a completed benchmark or timing.

Neither failed attempt produced an accepted final result ZIP and timing
sidecar. The third run produced them and passed retained-file review.
No new held-out scores, thresholds, architecture or training choices
are selected from these setup failures. Main publication and the final
acceptance tag are the final publication step after the accepted fresh-Colab evidence.
