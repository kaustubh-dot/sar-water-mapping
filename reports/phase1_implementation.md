# Phase 1 implementation evidence

28 October 2026. Tooling delivery only; Phase 1 actual-data gate remains open.

Implemented `src/sar_water/data.py`, package metadata/CLI, scientific fixture tests,
inventory/schema instructions, and the honest missing-input audit report. No
real data or archive downloaded, no model added, no manifest/splits fabricated.

Test-first evidence: initial fixture run with a workspace temporary directory
reported nine expected failures (`data adapter missing`) before implementation.
After implementation, nine passed and the optional GeoTIFF integration test
skipped because rasterio was absent. Three additional regression tests then
failed as expected (source-ID metadata conflict, infinity conversion, incomplete
spatial metadata), and were fixed. Final verification is recorded below.

Environment: Python 3.14.3; initial NumPy 2.4.4, SciPy 1.17.1, pytest 9.0.3.
No system packages were changed. Workspace `.venv` creation reached an ensurepip
failure, so installation used existing pip's explicit `--python` target. The
restricted-network attempt failed DNS resolution. An approved network retry
installed rasterio 1.5.2 in `.venv`; a concurrent parent attempt hit a Windows
file lock and stopped. The completed environment was verified by imports before
testing. `.venv` uses system-site packages for existing SciPy/pytest; its local
NumPy is 2.5.4. These development versions are not a Colab compatibility claim.

Final command: `.venv/Scripts/python -m pytest -q --basetemp=outputs/pytest-geo`.
Result: **13 passed in 3.07 seconds**, including the temporary real-GeoTIFF
integration fixture; no skips. The GeoTIFF test verifies file/content hashes,
zero-dB validity, and rejection of mismatched affine transforms. Test files under
`outputs/` are ignored and are not real-data audit artifacts.

Pending: actual subset/provenance, independent labels, representative inspection,
freeze/audit on real data, and phase review. No experiment runtime or accuracy
claim follows from fixture tests. See [audit](data_audit.md).

## Phase 1 review corrections

The [Phase 1 review](phase1_review.md) found an Important provenance defect:
the split API accepted other seeds while frozen manifests always recorded 42;
supplied membership also incorrectly claimed a generation seed. Generated splits
now reject seeds other than the locked 42, and supplied membership records the
explicit value `not_applicable`. The locked default remains deterministic.

The review also identified that optional plotting failures occurred after CSV
freeze. Requested contact sheets now render into memory before freezing any CSV.
Existing audit paths are checked before plotting and no existing files are
overwritten. Regression coverage forces a rendering failure, verifies no CSV
exists, retries successfully, and confirms a subsequent run refuses overwrite.

RED command: `.venv/Scripts/python -m pytest -q
--basetemp=outputs/pytest-review-red -k "seed_provenance or failed_contact"`.
Result before fixes: **2 failed, 13 deselected in 3.74 seconds**, respectively
because seed 7 was accepted and a rendering failure left `manifest.csv` frozen.

GREEN command: `.venv/Scripts/python -m pytest -q
--basetemp=outputs/pytest-review-green`.
Result after fixes: **15 passed in 3.08 seconds**, including GeoTIFF integration
and the successful contact-sheet retry. `git diff --check` also passes.
Review corrections do not complete any actual-data gate or establish any result
on organizer SAR data. Scoped re-review remains pending.
