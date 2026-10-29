# Fresh-kernel editable-install import fix

29 October 2026. **Implementation and focused regression verified; actual
fresh Colab completion and independent review remain separate gates.**

The fresh Colab attempt completed notebook setup cell 4, including the
`pip install -e . --no-deps` subprocess, then cell 5 raised
`ModuleNotFoundError: No module named 'sar_water'`. No source TIFF download had
started. Earlier cached execution had the package available at kernel startup
and did not exercise this condition.

The editable installation writes import-path startup metadata for new Python
processes. It does not update the already running notebook kernel's `sys.path`.
The setup cell therefore cannot rely on the pip child process alone to make
the newly checked-out `src/sar_water` package importable in its parent kernel.

## Bounded change

After the existing two pip calls, setup now resolves the verified checkout's
`src` directory, checks `sar_water/__init__.py` exists and inserts that source
directory at the front of the current kernel's import path. Missing source
stops setup explicitly. Subsequent Python subprocesses retain the ordinary
editable installation. No kernel restart or notebook timer reset is required.

Only notebook cell 4 changed. The source checkout helper, first timer cell,
scientific cells, source identities, split rule, grids, methods, training and
metrics remain unchanged. The notebook still has 14 cells/10 code cells with
empty outputs and null execution counts. This fix creates no new experiment
result or fresh Colab timing claim.

## RED/GREEN evidence

The focused regression executes the actual setup cell in a new Python process
with `-I -S`: the current directory, `PYTHONPATH`, installed editable startup
hooks and test-runner imports cannot make `sar_water` available. It uses a
new temporary checkout containing a small identifiable `sar_water.data`
fixture, stubs only external Git/pip calls and checks both pip calls occurred.
It asserts that the next import comes from that exact new checkout. A second
case checks a missing source package fails during setup.

- Before the fix,
  `.venv/Scripts/python.exe -m pytest -q tests/test_notebook.py -k editable_startup --basetemp outputs/pytest-colab-setup-red`
  failed both cases: the present-source case raised the same
  `ModuleNotFoundError`, and missing source did not stop setup.
- After the fix,
  `.venv/Scripts/python.exe -m pytest -q tests/test_notebook.py --basetemp outputs/pytest-colab-setup-green`
  completed with **12 passed in 6.91 seconds** and exit code zero. This includes
  the supplied/development data-access fixtures, source/calibration identity
  guards and unsupported generic-organizer stop.
- Structural comparison against pre-fix `HEAD` confirms only setup cell 4
  differs, `checkout_source` has an identical AST, and the first timer cell is
  identical. All ten code cells compile and retain empty execution evidence.
  `git diff --check` passed.

The actual browser run must use the reviewed fix and retain its full runtime
evidence. This regression does not certify the fresh uncached under-30-minute
Colab gate or full neural training inside that budget.
