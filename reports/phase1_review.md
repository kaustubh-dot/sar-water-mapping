# Phase 1 implementation review

28 October 2026. Reviewed the uncommitted Phase 1 implementation against base
`99bdd2a`, the supplied project guardrails, README, Phase 1 roadmap, evaluation
protocol and implementation lock. This is a code/tooling review, not an audit of
the unavailable organizer data.

## Findings from the initial review

**Critical: none found.**

**Important (P2): frozen manifests can record an incorrect split seed.**
`src/sar_water/data.py:196` exposes a configurable `seed`, used for the shuffle at
line 214, but `write_frozen_artifacts` unconditionally writes `split_seed=42` at
line 234. A direct reproduction using ten distinct event groups and `seed=7`
produces membership different from seed 42, then writes `42` into every manifest
row. Supplied organizer/upstream membership also receives this generated-seed
claim even though no seeded assignment occurred. This makes the frozen provenance
incorrect and prevents reproducing the recorded assignment from its metadata.
Carry the actual split-generation metadata through to the writer, or enforce the
locked seed 42 at the API boundary; use an explicit not-applicable value for
externally supplied membership. Add a focused regression test before proceeding.

**Minor: optional plotting failures leave an incomplete CLI operation frozen.**
`src/sar_water/data.py:264-279` freezes both CSVs before importing matplotlib and
building the requested contact sheet. If the optional audit dependency is absent
or rendering fails, the command fails after freezing membership, and retrying the
same command after fixing the plotting issue is rejected by overwrite protection.
Consider checking the requested plotting dependency before writing, or supporting
contact-sheet generation from an existing frozen audit. The documented complete
installation and successful rendering path work; this is a recovery-path issue.

## Verification and quality

- Independently ran `.venv/Scripts/python.exe -m pytest -q
  --basetemp=.pytest_cache/phase1-review`: **13 passed in 1.36 seconds**, including
  the GeoTIFF fixture.
- Ran the installed module CLI on three temporary, explicitly synthetic,
  georeferenced image/mask pairs with `--contact-sheet`: exit 0; manifest,
  membership and contact sheet were all created. These are development fixtures,
  not real SAR results.
- Confirmed the seed/provenance mismatch with a separate temporary-artifact
  reproduction. No implementation code was modified for this review.

The adapter correctly preserves float32 power, explicit units and VV/VH order,
valid zero dB, independent input/label validity and SAR-only deterministic filling.
Identifier pairing, shape/georeferencing checks, unknown-label rejection, exact
duplicate checks, source/spatial-group conflicts and same-CRS overlap checks are
appropriately conservative. Split fallback limitations and weak-label claim
limitations are disclosed. The package remains a small experiment with optional
GeoTIFF and plotting dependencies; no excluded model or infrastructure was added.

## Scoped re-review after fixes

Reviewed the changed adapter, regression tests and implementation evidence on
28 October 2026. Independently ran `.venv/Scripts/python.exe -m pytest -q
--basetemp=.pytest_cache/phase1-rereview`: **15 passed in 3.27 seconds**.

- **Original Important finding resolved.** Generated splits reject seeds other
  than the locked 42 (`src/sar_water/data.py:203-204`); supplied membership is
  recorded with `split_seed=not_applicable` (line 237). The new regression checks
  both persisted provenance values and rejection of a nonlocked generated seed.
- **Original Minor finding resolved.** Requested plots render to an in-memory PNG
  before the CSVs are frozen (`src/sar_water/data.py:270-296`). The regression
  injects a rendering failure, checks that neither frozen CSV exists, retries the
  same CLI arguments successfully, and checks that another completed-audit run is
  rejected. This addresses the dependency/rendering recovery path identified in
  the initial review.
- **Minor test-dependency issue also resolved.** The plotting regression now uses
  `pytest.importorskip("matplotlib")` at `tests/test_data.py:193`, consistently
  with the optional GeoTIFF dependency. Verified this final one-line correction
  by source inspection; the implementation agent also reports 15 passing tests
  after the correction.

**Current verdict:** no open implementation findings from this review;
the original findings and follow-up Minor issue are resolved. The authorized
fixture/synthetic development path may continue.
Actual archive provenance, independent manual labels, five representative real
development-patch inspections, real duplicate/overlap audit, and frozen actual-data
membership remain unverified. The roadmap correctly leaves those Phase 1 gates
open; this review does not complete them.
