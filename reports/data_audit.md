# Phase 1 data audit: awaiting the organizer subset

Status on 28 October 2026: loader/audit/split tooling implemented; actual-data
exit gate remains open. No organizer archive or upstream real sample has been
loaded in this workspace. No `data/manifest.csv` or `data/splits.csv` is fabricated.

## Known and missing inputs

| Item | Evidence/status |
| --- | --- |
| Archive origin, license/access and SHA-256 | Missing: organizer archive not provided |
| Actual patch count, shape, units and VV/VH order | Unknown until real files and source metadata are inspected |
| CRS, affine transforms, nodata | Unknown for actual subset |
| Independent manual versus weak labels | Unknown; primary ground-truth claims blocked |
| Organizer/upstream split membership | Missing; supply before tuning |
| Five representative development-patch inspections | Not run |
| Frozen manifest/splits and no-overlap audit | Not run on actual data |

## Implemented checks

The [adapter](../src/sar_water/data.py) explicitly declares units and band order,
checks paired GeoTIFF dimensions/georeferencing, metadata masks, labels and finite
power, preserves independent validity, and handles valid zero dB. Deterministic
nearest-valid SAR filling ignores label validity. The inventory pairs identifiers
and records source and mask provenance. SHA-256 covers actual files and decoded
images; split validation rejects cross-partition exact duplicates, same explicit
source/spatial groups, and same-CRS bounding-box overlap. Frozen CSV outputs refuse
overwrites. See [data instructions](../data/README.md) for schema, CLI and limits.

Split precedence is supplied organizer/upstream membership, event, scene, explicit
spatial groups, then disclosed metadata-absent patch fallback. Automated separated
spatial-block construction and cross-CRS overlap checks are unsupported; establish
those groups/audits explicitly. Unknown or weak provenance remains weak/unknown
agreement, not independent ground truth. Hash uniqueness cannot establish absence
of near duplicates or geospatial leakage without sufficient metadata.

## Next actual-data gate

Obtain and hash the archive; verify its terms and upstream identities, numeric
domain, band order, nodata and manual/weak provenance; run the CLI on a real
inventory; inspect five representative training patches and histograms; resolve
split conflicts, overlaps and group limitations; freeze the resulting manifest
and membership before method selection. Retain native resolution and original
data outside Git. This report contains no measured SAR benchmark result.
