# Submission artifacts, 29 October 2026

The requested two-page technical note and five-slide pitch use only the
accepted **supplied-first100** experiment. They do not mix in the earlier
development scores. The original reference presentation supplied the Georgia
and Arimo typography, cream background, rust accent and muted blue. Its text
and images were excluded from content discovery.

Local deliverables are under `outputs/submission/`:

- `sar_water_mapping_technical_note.pdf`: exactly two pages, IEEE-style
  two-column layout, four requested sections, equations, a pipeline diagram,
  separate real/synthetic tables and plots, references and limitations.
- `sar_water_mapping_pitch.pptx`: exactly five slides, native editable chart,
  tables and workflow diagram, source citations in speaker notes.
- `sar_water_mapping_pitch.pdf`: the static five-page pitch export.
- `sar_water_mapping_pitch.html`: the Frontend Slides version,
  with embedded Arimo/media, local Georgia, arrow-key navigation and inline text editing
  using E. Ctrl+S saves the edited HTML.
- `sar_water_mapping_reproducible.zip`: source snapshot, one notebook,
  instructions, recorded CSVs, saved publication figures and deliverables.

The output directory is ignored by Git. The archive excludes source TIFFs,
checkpoint weights, credentials, caches, the reference deck and unrelated
local files. The supplied checkpoint bundle is a separate release asset. The
public development checkpoint release must not substitute for supplied weights.

## Scientific provenance

The canonical sources are
[`results_real.csv`](../supplied_classical-v1/results_real.csv),
[`results_neural.csv`](../supplied_neural-v1/results_neural.csv),
[`results_synthetic.csv`](../supplied_classical-v1/results_synthetic.csv),
[`enl_summary.csv`](../supplied_classical-v1/enl_summary.csv) and
[`cleanup_ablation.csv`](../supplied_classical-v1/cleanup_ablation.csv).
`figure_data.json` records their SHA-256 hashes and the figure inputs.

Run `python scripts/build_submission_figures.py` from the repository root to
recreate the benchmark figures. Raster examples additionally require the
audited local `data/supplied-v1` cache. This is figure rendering from frozen
measurements, not a new experiment or a new parameter selection.

The public runnable code is on
[main](https://github.com/kaustubh-dot/sar-water-mapping).
The [exact reproduction guide](../../docs/REPRODUCING.md) distinguishes
classical execution, new remote training and checkpoint evaluation. A source
snapshot is also included in the local delivery archive.

## Acceptance boundary

S1/S2/S3 are accepted for the complete classical core. The fresh uncached
classical Colab run took 566.40 seconds including installation, one dependency
restart, all 200 downloads, calibration, evaluation and export. The
[independent execution review](../colab_execution_review.md) records the
retained evidence. The paired remote U-Net training took 76.77 seconds
separately; full neural training in Colab remains unmeasured. Main is published
and the original `v1.0-hackathon` tag remains unchanged. The [v1.0.1-submission release](https://github.com/kaustubh-dot/sar-water-mapping/releases/tag/v1.0.1-submission) provides
the refreshed documents, code package and supplied checkpoint bundle.

This internal event holdout includes eight test IDs previously used in project
training. The note and pitch disclose that exposure, the fixed validity/macro
population, the single seed, land-only ENL and the absence of evidence that
water masks distinguish new flooding from permanent water.

Final preparation checks: recompute headline IoU/F1 from all six pooled
confusion counts, confirm common scored pixels/macro IDs, inspect both note
pages and every slide, verify five-slide/two-page counts, validate native
PPTX chart/table packaging and reference fonts, and inspect HTML at 1280 x 720
plus a phone viewport. The build receipts remain in the private output folder.

## Repository cleanup

Only `main` remains locally and remotely. There are no additional registered
worktrees. `cleanup_inventory.json` records 18 removed duplicate, invalid or
superseded files. Historical references use canonical result files or the
unchanged original tag. Current scientific evidence, source identities,
calibration, tests, training metadata and both reproducible source profiles
remain intact. The notebook now pins the exact verified Colab source SHA
instead of the deleted implementation branch. No method or score changed.
