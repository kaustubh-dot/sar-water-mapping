# Independent review: fresh-kernel setup import fix

29 October 2026. **ACCEPTED for the bounded startup fix; no blocking findings.**
Fresh uncached Colab completion remains an unverified, separate acceptance gate.

Reviewed the uncommitted notebook/test diff against
`3d3ff7a33869a1650fde4128b20376eacd9f2ddb`, the implementation account in
[colab_setup_fix.md](colab_setup_fix.md), and the project roadmap/evaluation
guardrails. No commit was created during this review.

## Scope and correctness

Only notebook cell `sar-water-04` (zero-based index 4) differs from HEAD.
The added code resolves the verified checkout's `src` path, requires the
`sar_water/__init__.py` package marker, then inserts that path into the current
kernel's `sys.path` after the existing two pip calls. This directly addresses
the parent-kernel import failure without a restart. The editable installation
continues to serve later Python subprocesses.

Independent JSON/AST comparison confirmed that every other cell, the first
timer cell and the `checkout_source` helper are unchanged. All 10 code cells
compile, with empty outputs and null execution counts; the notebook remains
14 cells in total. There are no changes to source selection, data/splits,
calibration, methods, training, numeric conversions, masks, metrics or result
tables. Setup still records its elapsed time inside the existing total clock.

## Independent verification

- `.venv/Scripts/python.exe -m pytest -q tests/test_notebook.py --basetemp outputs/pytest-colab-setup-independent`
  exited zero: **12 passed in 9.22 seconds**.
- Repeated the two new cases with a temporary copy of the current tests and
  the untouched HEAD notebook under `outputs/colab-review-red-byvmcvug`.
  Both failed as expected: **2 failed, 10 deselected in 3.42 seconds**. The
  source-present case reproduced `ModuleNotFoundError: No module named
  'sar_water'`; the source-missing case failed because old setup did not stop.
  The shared working notebook was never reverted or modified for this check.
- `git diff --check` exited zero. Git emitted only its existing LF/CRLF
  normalization warning for the test file.

The regression executes the actual complete setup cell in an isolated Python
process with `-I -S`, asserts `sar_water` is initially undiscoverable, and uses
a new fixture checkout. It then checks that the next import resolves to that
exact fixture file and its marker. This prevents the test runner's configured
`src` path or an earlier editable installation from masking the bug. The
negative case validates explicit rejection of a missing source package. Git
and pip are deliberately stubbed, and both pip calls are observed. The
RED/GREEN check demonstrates this test detects the reported startup failure;
it does not establish network installation or Colab environment compatibility.

Reviewed file SHA-256 values:

- Notebook: `7d2299758a6eb738ddd195a76f76c62d67ba1db3aa4245e56dc8be6b3c366632`
- Test file: `5815f13142b0ac2696a18958933545f7e40a1124303085dd93bb1182c8c33b07`

No scientific rerun or new result acceptance is implied. The actual fresh
Colab run must use the reviewed source, complete uncached acquisition and
retain the final timing/export evidence before S2 can close. This review also
does not certify a full neural-training run inside the challenge budget.
