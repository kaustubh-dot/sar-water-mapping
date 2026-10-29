# Independent review: Colab dependency restart and timing

29 October 2026. **ACCEPTED for the bounded runtime fix; no blocking findings.**
Fresh uncached Colab completion and its under-30-minute gate remain unverified.

Reviewed the final working-tree notebook and new runtime regression against
`a37df8a9f7aa6144f65dcf30af0e6e2cf4fe7e59`, the
[implementation account](colab_runtime_fix.md), prior
[setup review](colab_setup_review.md), and project evaluation/roadmap guards.
This independent review changed no implementation, Git state or scientific
result. No commit was created during review.

## Scope and correctness

The fix addresses the second observed setup failure: installing the pinned
NumPy files underneath Colab's already loaded NumPy can leave a mixed parent
kernel. Setup snapshots loaded versions of the five pinned packages, performs
the existing pip calls, and compares those snapshots with installed
distribution versions. A mismatch stops before project numerical imports and
SAR acquisition and requests one explicit UI session restart.

The pending marker lives at `/content/.sar-water-mapping-restart.json`, outside
the checkout. The next Run All requires a different kernel PID on the same
runtime boot and restores the original monotonic start, UTC and run ID.
Setup then requires the same repository/reference, resolved source SHA,
dependency-lock hash, data source and profile. A same-kernel rerun, changed
identity or second dependency conflict stops rather than resetting timing.
Only coherent setup consumes the marker. There is no automatic kernel kill,
package-pin change or method change.

The original monotonic origin is used by the existing final export clock, so
both installation passes and the restart/user wait remain in total wall time.
First-pass setup stages are retained with `pre_restart_` names; the wait and
second setup pass are recorded separately. Export evidence includes the
restart count and original conflicting package versions.

Independent JSON/AST checks confirm changed cells 1, 2, 3, 4, 6 and 13.
Cell 6 only adds `tests/test_notebook_runtime.py` to the existing checks.
Acquisition and scientific cells 5 and 7-12, the checkout helper AST, dependency
pins, calibration, splits, filters, model/training choices and metrics are
unchanged. The notebook retains 14 cells and 10 compiling code cells with
empty outputs and null execution counts.

## Independent verification

- `.venv/Scripts/python.exe -m pytest -q tests/test_notebook.py tests/test_notebook_runtime.py --basetemp outputs/pytest-colab-runtime-independent`
  exited zero: **15 passed in 21.19 seconds**.
- Ran the three new regressions against a temporary copy of the untouched
  baseline notebook. They produced **3 expected failures in 6.33 seconds**
  because the restart clock helper was absent. The working notebook was never
  reverted or modified for this check.
- Additional isolated subprocess variants verified changed-lock and
  changed-profile rejection before pip, plus rejection of a second
  loaded/installed conflict with the marker retained. All three passed.
- Final notebook structure/compile inspection and `git diff --check` passed.

The regression uses real isolated interpreters (`-I -S -B`). Its first process
loads the old fake NumPy package, replaces the package files and distribution
metadata at the pip boundary, and demonstrates the resulting mixed-import
failure. The second process imports the coherent replacement and restores the
same start/UTC/run ID, including a start at least 120 seconds old. The tests
also check same-kernel and changed-source rejection and marker consumption.
Git/network/pip are deliberately stubbed. This establishes the import and
timing lifecycle; it does not certify actual wheel compatibility or Colab
runtime performance.

Reviewed file SHA-256 values:

- Notebook: `76da06f6d76ce19f04c4881aea7c607430db3cda5145520b666e0647f412d5be`
- Existing notebook tests: `5815f13142b0ac2696a18958933545f7e40a1124303085dd93bb1182c8c33b07`
- New runtime tests: `fe1e99f91461b57854aa883b768e656048cea28dba9d07d9f45e73ad3c8c7be5`

## Assessment

No unresolved P1/P2 findings. The runtime fix is accepted for the next actual
fresh Colab attempt. Retain both setup passes and the final ZIP/authoritative
timing sidecar before closing S2. No new scientific score, fresh-Colab timing
acceptance or full neural-training budget claim follows from this review.
