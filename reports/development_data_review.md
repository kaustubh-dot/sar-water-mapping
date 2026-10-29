# Phase 1 upstream development-data execution review

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**. Independent review dated 29 October 2026.

**Final decision after scoped follow-up: approved for bounded development train/validation calibration using `data/development-v1/audit-v3-relative/` and `configs/development.json`.** Both important findings and the low-priority affine precision finding are resolved and freshly verified below. The original findings are retained as review history. This approval does not close the organizer-archive gate or approve a spatially independent final benchmark.

## Important findings and exact acceptance checks

### P2 — The frozen manifest is not portable

All 100 `image_path`/`mask_path` pairs in `data/development-v1/audit/manifest.csv` are absolute `C:\\Kaustubh\\Hackathon\\...` paths. Training and evaluation resolve relative entries against the manifest directory, but the Windows entries cannot resolve on the authorized Linux GPU or Colab. Re-auditing on another host changes the manifest hash after calibration has frozen it, preventing faithful reuse of that calibration identity.

Preserve the original frozen audit unchanged. Create a new versioned audit whose file paths are relative to the manifest directory, using portable separators; retain the same selected objects and membership. Bind subsequent calibration to that new manifest. A regression must copy a complete fixture tree to a different root, resolve every image and mask from the relocated manifest's parent, and verify the original file hashes and membership without editing the manifest. Check that the new real manifest has no Windows drive prefixes or absolute file entries, that all 200 paths resolve, and that patch IDs, split membership, file hashes and decoded-power hashes match the original audit. Do not change the selected patches or overwrite frozen artifacts.

### P2 — Seven supplied cross-partition adjacency conflicts require explicit disclosure

An independent comparison of all 100 image bounding boxes found no positive-area overlap, but found these seven cross-partition pairs with exactly zero bounding-box separation:

| Chip A | Chip B |
| --- | --- |
| Mekong_1439641 | Mekong_1443339 |
| Mekong_293769 | Mekong_596495 |
| Spain_1167260 | Spain_6095801 |
| Spain_6095801 | Spain_7856615 |
| Spain_6537196 | Spain_8104659 |
| USA_366607 | USA_67102 |
| USA_527077 | USA_58086 |

The protocol requires neighboring crops to remain together and supplied conflicts to be reported before the partitions are treated as independent. The audit's statement that neighbor independence is not certified is weaker than the available evidence: adjacent chips actually occur across the supplied partitions. Retain official membership under the protocol's first-priority rule, but record these concrete conflicts and the resulting exception before calibration. Treat later scores as a correlated official-subset development benchmark; do not describe them as spatially independent or unseen-event generalization. Reassigning or replacing chips after observing labels is not the remedy. This disclosure does not prohibit bounded train/validation development on the supplied split.

## Fresh verification evidence

The following command completed with **45 passed in 7.61 seconds**:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_data.py tests/test_development_data.py tests/test_metrics.py tests/test_filters.py tests/test_synthetic.py -q --basetemp=outputs/pytest-development-data-review
```

The coverage includes declared dB/power conversion, valid zero dB, independent input/label masks, deterministic SAR-only fill, unsupported labels, inventory pairing, supplied membership and overlap rejection, frozen artifact retry behavior, the real-data affine roundoff regression, rejection of a 1/8-pixel shift and an accumulating scale error, label-blind selector order invariance, manual-pair naming, metrics, filtering and synthetic references. These are scientific correctness tests, not real-data performance results.

A separate metadata/hash check recomputed selection ranks independently rather than calling `select_pairs`, verified the three saved source-list hashes and counts (252/89/90), compared selected IDs and partitions against both frozen CSVs, and verified all **200 objects / 164,663,453 bytes** using the recorded upstream MD5, local SHA-256, length and pinned generation. Only `HandLabeled/S1Hand` and `HandLabeled/LabelHand` directories were admitted. The selection hash is `e7cbd62911647be8ad0fa0d6c08be3f98dc1bc335bf0e780ff180005b2642acf`; both selection JSON copies match. Membership is exactly **60 train / 20 validation / 20 test**, selected by the smallest SHA-256 ranks of `42:split:patch_id`, without mask contents. No selected patch was replaced after labels were read.

The independent check opened SAR pixel arrays and mask metadata, but **did not read mask pixel values or select any method**. It confirmed two float32 SAR bands, single-band masks, 512 x 512 shapes, common EPSG:4326, all manifest file hashes and all 100 canonical decoded-power hashes. There are 100 distinct image-content hashes and no cross-partition positive-area bounding-box overlap. Its local evidence is `outputs/development_data_review_checks.json`; this generated artifact remains ignored.

The upstream [dataset README](https://github.com/cloudtostreet/Sen1Floods11) and [directory documentation](https://raw.githubusercontent.com/cloudtostreet/Sen1Floods11/master/docs/README.md) were checked during review. They support VV/VH dB input order, the manual label codes and the distinction between `LabelHand` and Otsu/weak-label directories. This establishes source provenance, not an independent relabeling or annotation-quality validation.

## Alignment and visual evidence

The alignment admission requires equal shape and exact CRS equality. It solves affine corner displacements in image-pixel coordinates, admitting at most 1e-6 pixels, without source rewriting, reprojection or resampling. The independent calculation with separately grouped coefficient differences found a maximum displacement of **5.18e-11 pixels**, safely below that bound. The original report retains 99 unequal transform pairs; equality in the remaining pair is expected rather than missing data.

One low-priority precision observation remains: `_alignment_error_pixels` adds the mask origin and then subtracts the image origin without parentheses around that difference, despite its cancellation-avoidance comment. Grouping each origin difference first changes the recorded tiny errors by at most **5.18e-11 pixels** in this subset. This does not change admission or create meaningful alignment error here, but grouping the subtraction and testing invariance to a shared large world-coordinate translation would make the implementation match its stated numeric intent. The recorded 7.91e-11 maximum and the independent maximum are both immaterial relative to the admission bound.

The reviewer opened `outputs/development_data/contact_sheet.png`. Its five rows match the train-only inspection JSON: Ghana_103272, India_103447, Mekong_1439641, Nigeria_143329 and Pakistan_1036366. VV/VH, shared-range displays, histograms and independently masked labels are legible and consistent with the audit's descriptions. Sparse water, unimodal land, narrow channels and label-invalid areas are visible. These support the need for later false-positive and detail-loss diagnostics; they do not establish filter quality or a usable homogeneous ROI. No validation/test mask was visually inspected in this review.

## Limits that remain open

- The organizer-specific 100-patch archive is unavailable. The bounded upstream substitute cannot close that delivery or submission requirement; rerun on the organizer subset when supplied.
- Official partitions share events and include the seven adjacent cross-partition pairs above. Full source-scene IDs are missing. No unseen-event, scene-independent or geographically independent claim is established.
- The existing audit records Ghana_26376 with no valid scored pixels and Ghana_24858 with mask nodata 0 and only 484 valid scored pixels. Preserve metadata masks, retain these label-blind selections, and skip/log all-invalid training draws. A mask nodata value must not silently become valid land.
- Raw-only training ROI selection, effective looks, validation calibration, synthetic final comparison, held-out scoring, remote scientific training and a timed fresh Colab run remain unrun at this review checkpoint. Neither tests nor a contact sheet supplies those results.
- Manual-label directory provenance does not establish perfect annotation, newly flooded versus permanent water, or immunity to acquisition/annotation mismatch. Third-party terms remain separate from the project license.

No source code was edited by this reviewer. Release development calibration only after the portable versioned audit passes the stated checks and the actual adjacency conflicts are explicitly recorded. No further model or broad literature search is indicated.

## Scoped follow-up review: all findings resolved

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**, 29 October 2026. This follow-up covers only the two required corrections above and the origin-arithmetic precision correction; it does not expand the method scope.

**P2 portability — resolved.** The writer serializes paths relative to the output manifest directory with POSIX separators. `read_manifest` resolves them against the manifest parent. The new copied/moved complete-tree regression makes the old source location unavailable and audits every relocated fixture source file and decoded image, while retaining split membership. The new real `audit-v3-relative` has 200 relative paths, with no absolute path or Windows drive prefix. An independent rerun resolved them to the same 200 source files, recomputed all 200 file hashes and all 100 decoded-power hashes, and compared source provenance, units, band order and membership to the original. The original manifest still hashes to `7e9c690fe178eab98efe5dfc3e7e7a1828140e87bee7b4e061e9b8dcfb239b56`; the original and new split CSVs are byte-identical. The intermediate v2 audit is preserved and is not the accepted calibration identity.

Accepted frozen identities:

- Manifest: `74d00fd2b08e6417e77a102c0cfd5b0bd5c3b1d759ff814b6fabdae4729792cc`.
- Splits: `24963a9951f318aab0cc3d687023ce849fc5c9435ed9fc8cbadced4dc6c2d1b7`.
- Original label-blind selection remains `e7cbd62911647be8ad0fa0d6c08be3f98dc1bc335bf0e780ff180005b2642acf`.

**P2 adjacency disclosure — resolved.** The revised development audit explicitly lists all seven pairs and their actual partitions, retains the official membership, and states that this is a correlated official-subset development benchmark. `development_data_portability.json` and `configs/development.json` contain the same explicit pair records and generalization limitation. The independent follow-up recomputed bounding-box relationships and verified the exact seven pair records, with zero positive-area cross-partition overlaps. No patches were reassigned or replaced. This is a disclosed supplied-split exception, not a claim that adjacency has disappeared.

**Affine precision — resolved.** Both origin differences are now grouped before adding the linear terms. A focused regression verifies that a shared large coordinate translation does not erase the small scale displacement. The corrected recorded maximum, independently checked against all real input/mask transforms, is `5.1779135800964635e-11` pixels. The 1e-6-pixel admission bound, exact CRS equality and no-resampling contract remain intact.

Fresh verification command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_data.py tests/test_development_data.py tests/test_metrics.py tests/test_filters.py tests/test_synthetic.py -q --basetemp=outputs/pytest-development-data-rereview
```

Result: **47 passed in 4.85 seconds**, exit code 0. The separate follow-up check also exited 0 and saved `outputs/development_data_rereview_checks.json`, recording all 200 portable paths, 300 recomputed file/content hashes, unchanged original artifacts, exact adjacency count, zero positive-area overlaps and corrected alignment maximum. Mask pixel values were not read in that check.

The development config binds the accepted portable manifest/split identities, sets `split_frozen` true, keeps `calibration_frozen` false, and leaves channel, rule, filter parameters and effective looks unset. It explicitly excludes organizer-subset and independent-geography claims. Train-only raw ROI inspection, train-only effective looks estimation and bounded validation calibration may now proceed. Final test method selection remains prohibited, and organizer data, scientific training and fresh Colab timing remain separate open gates. No source code was edited by this reviewer.
