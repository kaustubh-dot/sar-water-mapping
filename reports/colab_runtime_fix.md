# Colab loaded-dependency restart fix

29 October 2026. **Focused local regression verified; fresh uncached Colab
completion remains unverified.** No scientific result or timing gate is closed.

The second fresh Colab attempt installed the exact NumPy 2.5.4 lock over
Colab's already loaded NumPy, then cell 5 failed importing `_slice` from
`numpy._core.umath`. No SAR acquisition had started. The prior source-path fix
made the checkout importable, exposing a separate loaded-module/on-disk
dependency mismatch. A pip child cannot replace modules in its parent kernel.

Setup now compares the versions of already loaded pinned scientific packages
against their installed distribution versions after the unchanged pip calls.
A mismatch stops before source-package imports or data access and instructs
**Runtime > Restart session**, then **Run all**. It does not kill the kernel.
Only Colab persists a pending marker, outside Git at
`/content/.sar-water-mapping-restart.json`.

The marker preserves the original monotonic start, UTC start, run ID and first
setup stages. Resume requires a new kernel on the same runtime host and the
same repository/reference, resolved source SHA, dependency-lock hash, data
source and profile. First-pass setup stages gain a `pre_restart_` prefix;
restart/wait duration and the second setup pass are recorded separately.
The original total clock includes both setup passes and all restart/user
waiting time. A second conflict stops without another restart. Coherent setup
consumes the marker; a later independent Run All starts a new clock and its
data-access stage still reports the actual cached TIFF count.

Notebook edits cover timer/config/setup, restart instructions, inclusion of
the new regression file in the notebook's checks, and export timing evidence.
Acquisition, calibration, numerical processing, splits, models, thresholds,
metrics, dependency pins and result tables are unchanged. All 10 code cells
compile, and saved outputs/execution counts remain empty.

## Verification

The new test runs the actual timer helper, configuration and complete setup
cell in isolated Python subprocesses (`-I -S -B`). Its NumPy fixture starts
loaded at version 1.0; the external pip boundary replaces its source and
distribution metadata with version 2.0. The first interpreter demonstrates
the mixed-import failure while setup stops and saves the original clock.
A second interpreter imports the coherent replacement, restores the same
run ID and a clock already at least 120 seconds old, and consumes the marker.
Additional cases reject rerunning in the same kernel and a changed source.
Git/network/pip are stubbed; this is a deterministic import-lifecycle
regression, not a real NumPy-wheel installation or Colab certification.

- RED: `tests/test_notebook_runtime.py` produced **3 expected failures** before
  implementation because the restart clock protocol was absent.
- GREEN: `.venv/Scripts/python.exe -m pytest -q tests/test_notebook_runtime.py tests/test_notebook.py --basetemp outputs/pytest-colab-runtime-green`
  exited zero: **15 passed in 38.40 seconds**.
- JSON/compile inspection verified the intended cell boundaries and empty
  execution evidence. `git diff --check` passed.
- The exact notebook check list completed with **100 passed, 1 failed** in
  151.12 seconds under the Windows sandbox. Its unchanged local Git-clone
  fixture failed because Git's `sh.exe` could not create an MSYS named object
  (`NtCreateDirectoryObject`, `0xC0000022`); a focused retry reproduced that
  environment restriction. The restart regressions passed. An unsandboxed
  suite result and the actual Colab run remain separate verification evidence.

The live run must retain both passes and the final authoritative timing
sidecar. Installation, restart, uncached acquisition, scientific checks and
export must all fit strictly below 1,800 seconds before S2 can close.
