# Supplied-set acquisition and data review

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**. Independent review dated
29 October 2026.

**Decision: accept the supplied acquisition, data audit and fixed ROI gate.**
No P1/P2 findings remain in this reviewed scope. The actual 100-pair set and
frozen internal membership are suitable for the next locked calibration gate,
with the limitations below. This does not accept calibration, trained models,
held-out results or a fresh Colab run.

## Verified scope

Read the project guardrails, README, roadmap, evaluation protocol,
implementation lock, supplied recipe/selection, execution ledger, internal
split provenance, training/held-out ROI records, acquisition evidence and the
[data-audit summary](supplied_data_audit-v1.json). Reviewed
[`prepare_supplied_data.py`](../scripts/prepare_supplied_data.py) and its
focused tests. No training, method selection, calibration, network access or
source implementation edits were performed by this reviewer.

- The retained source CSV is exactly 13,574 bytes and 252 headerless rows,
  SHA-256 `57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
  Every zero-based recipe position and image/mask pair matches its first 100
  ordered rows. The 100 patch IDs are unique. The supplied-selection SHA-256 is
  `9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2`.
- Independently reran the existing `create_splits` rule using seed 42 and
  recipe metadata only. It exactly reproduces the frozen membership: Mekong,
  Nigeria and Pakistan train (29 patches); India validation (40); Ghana test
  (31). The external split CSV SHA-256 is
  `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532`.
  Every event is confined to one partition. Unequal patch counts follow the
  existing group rule and were not selected by scores.
- Independently compared prior development membership. Exactly 22 supplied
  IDs previously belonged to development training: five new training, nine
  new validation and eight new test IDs. These are internal event holdouts,
  with recorded prior project exposure; they are not a pristine blind test or
  the official upstream test partition. Scratch models are required.
- All four frozen training ROIs belong to the new training partition. Each is
  32 x 32 pixels with 1,024 valid SAR pixels and 1,024 valid scored pixels.
  The two Nigeria regions are uniformly manual land and the two Mekong
  regions uniformly manual water. Inspected the retained raw VV/VH ROI image;
  no strong shoreline/class boundary crosses the rectangles. Approximate
  visual homogeneity and four regions from two source patches remain limited
  support for an effective looks estimate. No Ghana/test ROI was used.
- The acquisition implementation pins source and ordered selection hashes,
  freezes internal event membership before any object metadata/TIFF access,
  requests generation-specific source objects, verifies size and MD5 and
  records local SHA-256. It bounds the selection to 100 pairs/200 objects and
  500 MB. Verified cache reuse requires matching generation/size/MD5 and
  copies bytes without modifying the cache. Exclusive atomic publication
  prevents replacing existing artifacts. A completed repeat verifies the
  frozen objects and inventory without network access. Raster audit is
  explicitly separate from byte acquisition.
- Independently ran
  `.venv/Scripts/python.exe -m pytest -q tests/test_supplied_data.py tests/test_data.py tests/test_development_data.py --basetemp=outputs/pytest-supplied-review`:
  **31 passed in 6.86 seconds**. The fixtures cover exact identity/order,
  before-object split freezing, internal versus upstream split semantics,
  repeat verification, corruption rejection, cache integrity, bounded
  acquisition and unrelated-directory preservation. Fixture bodies are not
  TIFFs and cannot establish scientific validity of the actual dataset.
- Verified `git check-attr text` reports `unset` for the new split CSV,
  split-provenance JSON, training-ROI CSV and acquisition split artifacts.
  The integration change therefore preserves their hash-bound bytes across
  Windows/Linux checkouts.

## Actual acquisition and raster evidence

Independently re-read every one of the 200 acquired objects. All sizes, MD5s,
local file SHA-256s and recorded generations match the pinned object records.
There are exactly 100 selected pairs and 200 unique objects, totaling
169,393,092 bytes. The origin record is 44 verified cache copies and 156 network
downloads; every cache copy is byte-identical to the retained development
source. Recorded acquisition time is 148.656 seconds. This is local acquisition
timing and does not establish a fresh Colab runtime.

The public acquisition evidence is byte-identical to its dedicated data-root
copies. Recomputed identity bindings are:

| Artifact | SHA-256 |
| --- | --- |
| Pinned object selection metadata | `8cade23f9cbce0bb116ef3827d8cdffc35ab8ddc536f638ffb9372c85b2b07f0` |
| Download record | `551d3b4240e0624debb1f097f72dac8f03a283c592839c837ec7664cea2a2c8b` |
| Acquisition split freeze | `07a49d6a76beb50e1725bf1ce18a975d3196a70bba7bcfeef9dda823c5ef9d11` |
| Long-form inventory | `88e985560716774bc6a27e7daf82c0f11a030a2dd71de136d438111dcbd18cbb` |
| Audited manifest | `4c196542778daefb2f03b53634f8f0ef579f91851677c606d5ae77750ab93ea3` |
| Operative internal splits | `940f34a9a15c05af7ae61c623307577eb38ab9a4d46f638cc6f72d897a853532` |

Independently decoded all 100 pairs with rasterio, without using labels to
select a method or change membership. Each image is two-band float32,
512 x 512, with actual band descriptions `VV,VH`; each paired label is one-band
int16 with only `-1/0/1`. All use EPSG:4326. The inventory explicitly declares
upstream power dB units and the `S1Hand`/`LabelHand` manual-label sources;
the unit contract is documented provenance, not an inference from value signs.
Maximum image/mask affine disagreement is `5.1779135800964635e-11` pixels,
within the fixed `1e-6` admission bound. Opened the saved five-patch training
contact sheet as an additional visual check.

Recomputed SAR validity from both metadata masks and finite samples, label
validity from its own metadata mask and `-1` code, then scored only their
intersection. SAR and label masks differ on 84 patches, confirming that neither
may replace the other. Valid scored pixels match the audit exactly: train
6,769,828; validation 8,788,754; test 4,940,307. `Ghana_26376` has zero scored
pixels and `Ghana_24858` has only 484; both remain in the frozen test membership.
The zero-scored patch must produce an explicit no-score status, never a perfect
score or an artificial dry-patch score.

All 100 portable source-domain image digests were independently recomputed
and match the manifest; they are unique. File hashes match too. An independent
bounding-box audit found no cross-partition overlaps or touching chips.
Twenty touching pairs occur within partitions. Whole-event membership therefore
preserves these neighbors together. This does not turn the five-event,
first-row sample into a representative global benchmark or erase prior project
exposure.

## Fixed ROI acceptance and scientific limits

Rechecked the four training ROIs against the newly acquired copies; their
image/label files are byte-identical to the originally inspected cached
sources. Their CSV SHA-256 is
`06250010ee4dcc6cd43a9ff97c5ff4644c55f85b990664ea76e0fb7459abfad0`.
Independent float32 dB-to-power conversion and float64 population moments give
the bounded median training looks `[4.6020301257391925, 2.5820418881305613]`
for VV/VH. These are reproducible effective estimates from the four fixed
regions, not independently measured physical looks. The later calibration
record must retain these coordinates, per-region values and source bindings.

Reviewed the raw full-patch candidates and all five frozen test ROI crops.
The five held-out rectangles lie in the test partition, are 32 x 32, contain
1,024 valid SAR pixels each, and have finite nonzero raw power variance in both
bands. The held-out ROI CSV SHA-256 is
`ce9feec5fae46109f805c0650f27c9cc9e5193cd96d95f0c268115626a78556e`.
Their raw texture and lack of a strong visible boundary support a limited
homogeneous-land diagnostic. The land tags are visual SAR interpretation,
not independent class ground truth; no water-region ENL is promised. These
coordinates were frozen before new filtered outputs or test scores and must
be shared unchanged across methods. They never enter training looks or
normalization. The review did not use held-out labels to choose or revise ROIs.

The source/selection history proves the retained recipe identity rather than
independently authenticating its sender. Calibration, training, held-out
measurements and uncached Colab remain outside this review and unaccepted.
