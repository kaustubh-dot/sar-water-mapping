# Independent notebook readiness review

29 October 2026. **Accept for classical notebook implementation readiness.**
No unresolved material finding remains in the reviewed notebook path. This is
not acceptance of a fresh Colab Run all, the under-30-minute execution gate,
the organizer subset, or neural training reproduction.

## Scope and controlling requirements

Reviewed `AGENTS.md`, `README.md`, `ROADMAP.md`,
`docs/EVALUATION_PROTOCOL.md`, `docs/IMPLEMENTATION_LOCK.md`,
`reports/notebook_completion.md`, the current notebook and its executable
regressions. Inspected the downloader, audit/calibration command interfaces,
frozen configuration bindings, evaluation runner and paired-training identity
interface. No GPU was used and no model or method was added.

The review baseline is `f9f6e56284caed9fed8d5bb7e0c806d40782f8cd`.
The reviewed notebook worktree SHA-256 is
`68a7f3e6a64651a3fc01dbcb8c66df2d483eebfdf2d38e939caba42c54d895aa`.

## Accepted behavior

- Run all defaults to the frozen 100 upstream manual-label pairs and checks
  official list hashes, exact pair membership, inventory identity and explicit
  60/20/20 splits. The downloader receives the copied selection before any
  download; it verifies all 200 object sizes and MD5 values. Its run-specific
  log is bundled without overwriting prior source reports.
- Recorded training and held-out ENL ROI files are snapshotted and hashed.
  Training ROIs are restricted to train; ENL ROIs to test. Calibration uses the
  reviewed CLI with training looks and validation-only selection. The notebook
  verifies manifest, split, training ROI, looks artifact and validation/config
  hashes before held-out scoring. The command flags and evaluation call match
  their actual Python interfaces.
- Source checkout, installation, access, checks, audit, calibration,
  evaluation/export, display and final archive work are measured. Download
  verification is explicitly a nonadditive access substage. Source commit and
  dependency lock hashes are retained. `checkout_source` and `export_bundle`
  have identical ASTs to the baseline; both original regressions pass.
- Upstream source and known cross-partition correlation are disclosed in the
  notebook and bundled provenance. Surface-water results make no new-flood
  separation claim. The organizer override requires its own inputs and stops
  before the upstream-specific calibrator can mislabel or score them.
- The full profile is explicitly classical with neural training disabled.
  Checkpoint evaluation and remote training remain separate measurements.
  The notebook contains ten parseable executable cells with empty outputs and
  execution counts.

## Resolved cross-platform finding

The selection JSON initially had LF bytes in Git and CRLF bytes in the Windows
worktree. Its recorded download/configuration identity used the CRLF SHA-256;
an LF checkout therefore changed that byte identity. The parent preserved the
existing bytes with `reports/development_data_selection.json -text` and
renormalized the index, without changing selected pairs or using semantic
hashing. This review verified index and worktree both have SHA-256
`e7cbd62911647be8ad0fa0d6c08be3f98dc1bc335bf0e780ff180005b2642acf`,
matching `reports/development_data_download.json`. Both ROI index/worktree
hashes also match. The selection copy and guards remain exact-byte checks.

## Dependency and verification evidence

The project environment is Python 3.14.3. Its installed versions exactly match
`requirements-colab.txt`: NumPy 2.5.4, SciPy 1.17.1, rasterio 1.5.2,
matplotlib 3.10.9 and pytest 9.0.3. Installed NumPy and rasterio metadata require
Python >=3.12, consistent with the notebook's pre-installation gate. The setup
installs that lock and the local package with `--no-deps`; it does not install
or change the CUDA/PyTorch stack. These are local stack checks, not proof of
fresh Linux/Colab installation compatibility.

- `.venv/Scripts/python.exe -m pytest -q tests/test_notebook.py
  tests/test_evaluate.py tests/test_calibration.py tests/test_development_data.py
  -k 'not checkout_supports' --basetemp outputs/pytest-notebook-review-venv`:
  **21 passed, one deselected in 19.90 s**.
- The unchanged local Git checkout regression, executed outside the Windows
  sandbox because MSYS named-object creation is denied inside it:
  **one passed in 2.67 s**.
- The notebook's complete nine-file scientific check selection, excluding that
  separately verified checkout case:
  **75 passed, one deselected in 17.86 s**. Files were `test_data.py`,
  `test_metrics.py`, `test_filters.py`, `test_segment.py`, `test_benchmark.py`,
  `test_evaluate.py`, `test_notebook.py`, `test_development_data.py` and
  `test_calibration.py`; temporary output was
  `outputs/pytest-notebook-science-review`.
- All three CLI `--help` interfaces were executed, and the notebook's
  `run_evaluation` call was bound against its actual inspected signature.
- A diagnostic whole-environment `pip check` reports an installed, unused
  numba 0.65.1 requirement of NumPy <2.5. The classical package/notebook does
  not import numba; the locked scientific stack passed the checks above.
  This is not reported as a clean whole-environment dependency check.

An initial command used system Python, which lacks rasterio, and also hit the
known sandbox Git restriction: 17 passed, one skipped and four failed. Those
were environment-selection failures; the project-environment runs above
provide the review evidence. No failing test was hidden or weakened.

## Execution gates still open

Publish the reviewed source and select its exact commit. Then run all cells
in a fresh compatible Colab runtime without cached data, record actual
installation/access conditions and CPU/RAM information, inspect exported
tables and aligned figures, and retain the result ZIP plus authoritative
sibling timing sidecar. Only this measured run can close the complete
classical under-30-minute gate. Organizer-data delivery and organizer-specific
calibrator support remain open. Remote GPU training results cannot close any
full-training Colab runtime gate.
