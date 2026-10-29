# Supplied source profile implementation review

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**. Independent review dated
29 October 2026 against accepted Phase 1 commit `f05f0e0` and the current
working-tree implementation.

**Decision: accept this implementation gate.** No P1/P2 findings remain in the
reviewed source-aware calibration and notebook wiring. Proceed with the actual
supplied calibration under the locked grids. This accepts no actual calibration
result, training run, held-out measurement, notebook execution or Colab timing.

## Scope and verification

Reviewed [`supplied_profile.py`](../src/sar_water/supplied_profile.py), the
[`calibrate_classical.py`](../scripts/calibrate_classical.py) diff, every fresh
cell of the single [notebook](../notebooks/01_sar_water_mapping.ipynb), focused
test changes, the [implementation record](supplied_profile_implementation.md),
and actual [source configuration](supplied_source-v1.json). The preceding
[data/ROI acceptance](supplied_data_review.md) remains separate. No source
implementation edits were made by this reviewer.

- Ran `.venv/Scripts/python.exe -m pytest -q tests/test_supplied_profile.py tests/test_calibration.py tests/test_supplied_data.py tests/test_notebook.py --basetemp=outputs/pytest-supplied-profile-review`:
  **30 passed in 58.02 seconds**. These are offline acquisition, metadata,
  calibration-fixture and notebook-helper checks, not actual supplied scores.
- Verified the actual source configuration against the accepted 100-pair audit.
  Its SHA-256 is
  `7c121d63328d90c1850b419647d6964131a6138d468e686c02d6ba1c5d93fbbe`;
  it retains manifest SHA-256
  `4c196542778daefb2f03b53634f8f0ef579f91851677c606d5ae77750ab93ea3`
  and split SHA-256
  `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`.
- Independently ran the writer/verifier against actual metadata while guarding
  both built-in and `Path.open` calls to reject any TIFF access. The check
  succeeded, including a newly written nested source-configuration location
  and resolution of every relative artifact binding. No pixels were opened,
  decoded, hashed or scored by this check.
- Parsed all 10 code cells in the 14-cell notebook and confirmed all execution
  counts are null and all outputs are empty. Independently compared ASTs with
  `f05f0e0`: `checkout_source`, `freeze_upstream_selection`,
  `verify_upstream_inputs` and `export_bundle` are preserved.
- Confirmed `filters.py`, `segment.py`, `benchmark.py`, the experiment template,
  implementation lock and evaluation protocol are byte-identical to `f05f0e0`.
  `git diff --check` passed. Git attributes preserve the new source helper,
  calibration script and supplied source JSON bytes.

## Accepted behavior

The source configuration contains provenance only. Top-level keys must be
exactly `schema_version`, `profile` and `real_data`; reconstructed `real_data`
must match exactly. The verifier binds the pinned source CSV and ordered
selection, recipe, split freeze, acquisition selection/download/inventory and
audited manifest. It checks the exact object identities, file SHA values,
generation/MD5/size records, source URIs, local paths, declared dB/VV-VH/manual
contract, events and membership. It preserves all 100 upstream training IDs,
internal 29/40/31 event counts and 22 previous training exposures distributed
5/9/8. Organizer authority and pristine blind-test status are not claimed.

Filter grids, selected methods, normalization, checkpoints and training
parameters cannot be injected through this interface. Supplied calibration
starts from the unchanged experiment template and bypasses the optional
development configuration. Focused tests verify rejection of altered hashes,
membership, source paths and forbidden method metadata before calibration
source access.

The calibrator verifies the complete source configuration before loading
training or validation sources and again before publishing frozen choices.
It also retains the existing manifest/split/ROI start/end hash guard. Its
loader explicitly rejects test membership. A mutation fixture confirms that
a source-configuration change during calibration prevents the final experiment
configuration from being written. The source configuration path/SHA and
provenance are carried into the experiment and validation record, with metadata
artifact paths rebased to the experiment configuration folder. The original
three-entry `input_sha256` contract remains intact. Fixture verification also
exercises the notebook's source-aware identity check from a different config
directory.

The pilot still uses training sources only. It prefers distinct events and
fills remaining places with sorted training IDs, giving five training patches
when the supplied partition contains only three events. This changes bounded
timing coverage without changing the filter/threshold search or its scientific
selection rule.

The notebook defaults to `supplied-first100`, invokes the bounded acquisition
CLI without a cache override, uses its frozen internal splits and separately
records the current run's existing TIFF count. The original immutable acquisition
origin log is labeled as historical acquisition evidence. Training and held-out
ENL ROI CSVs, recipe and acquisition metadata are snapshotted into the run
bundle. After the validity audit it writes the source configuration, passes
`--source-config` to calibration, and verifies source, manifest, split, ROI,
looks and validation/config identities before held-out evaluation. Stage timing
includes acquisition, audit and calibration. The earlier
`upstream-development` profile and explicit generic-organizer stop are preserved.

The reviewed implementation hashes are:

| File | SHA-256 |
| --- | --- |
| Source profile helper | `384ae9ffc7a855754b2caec521bc2dddfc37983f1ff20c9d8f194bf4b78437ac` |
| Calibration script | `6c5ed4ada813fde9d57ee3a06d6b1de726d727b2bb3705366d3f636dfcc6eedd` |
| Notebook | `74e8ef3d534b98d940ff04189274f1d3035ce916728804d73f7fcee7bf740102` |

Actual supplied calibration and its independent scientific review remain the
next gate. Full notebook smoke and fresh uncached Colab acceptance remain
unverified; no implementation or fixture timing establishes the under-30-minute
Colab requirement.
