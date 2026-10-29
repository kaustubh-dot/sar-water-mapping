# Audit of the supplied 100-patch recipe

29 October 2026. The user supplied a Colab snippet received when asking about
the 100 patches. It defines a concrete acquisition recipe: read the upstream
hand-labeled training CSV without a header and take its first 100 rows. There
is no separate archive in this recipe. The sender's authority was not
independently authenticated; this records the user's supplied definition.

The public CSV was fetched again. Its 13,574 bytes and 252 rows match the
earlier upstream source exactly, SHA-256
`57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
The first 100 ordered identifiers are frozen in
[supplied_subset_selection.csv](supplied_subset_selection.csv), with numeric
zero-based recipe positions. Its hash and machine-readable findings are in
[supplied_subset_recipe.json](supplied_subset_recipe.json).

## What this changes

This is a different selection from the completed 60/20/20 development
experiment. All 100 supplied identifiers belong to the upstream **training**
partition. The snippet does not define train/validation/test membership inside
these 100. Its event composition is Ghana 31, India 40, Mekong 18, Nigeria 10,
Pakistan 1. First-row selection is deterministic once the source CSV is pinned,
but is not a balanced event sample.

Only 22 identifiers overlap the existing development selection, all from its
training partition. The existing checkpoint has therefore already trained on
those 22. It cannot be presented as evaluating unseen inputs across this full
new subset. The original results remain valid for their recorded development
selection and are preserved; they are not measurements on the supplied set.

## Required loader corrections

The source uses `S1Hand` and `LabelHand`, which upstream documents as SAR
overlapping hand-labeled water masks. Preserve VV/VH order, native shape,
declared dB units and label codes. Independently audit every downloaded pair's
actual metadata rather than treating a code comment as an audit.

Do not use `np.nan_to_num(..., nan=-30.0)` as the scientific input adapter.
It erases missing-data identity and can turn missing SAR into apparently dark
water under a -18 dB threshold. It also replaces infinities by extreme finite
values unless explicitly handled. Derive SAR validity from metadata masks and
finite values, retain label validity independently, then apply the project's
SAR-only nearest-valid filling for filtering/network input and restore the
original mask for scoring. Never use label validity to fill inference inputs.

An `exists()` check does not establish an intact TIFF. Use verified object
size/MD5/generation and local SHA-256, atomic downloads, pair/georeference
checks and the portable native-source digest. The current snippet's final
message opens one pair; it does not establish a successful audit of all 100.

## Execution order

1. Retain the supplied exact 100 identities and source hash; do not substitute
   our previous selection or change first-row membership after examining labels.
2. Download/audit only these 100 pairs in a new dataset directory, preserving
   all current data/configurations/results. Record that the source selection
   came from this user-supplied recipe.
3. Freeze internal evaluation splits before tuning. No internal organizer
   membership is supplied; use the existing event/scene/spatial hierarchy,
   audit neighbors/overlaps, and favor valid groups over exact 60/20/20 counts.
   Do not call randomly resplit training chips the official upstream test set.
4. Reuse the locked method/model definitions and bounded grids. Establish
   training ROIs and raw-training normalization anew; calibrate only on the
   new validation partition. Any learned comparison needs separate training
   and explicit disclosure of the earlier 22-patch exposure, rather than
   pretending that the published checkpoint is an unseen-data baseline.
5. Evaluate the new frozen partition as a versioned supplied-subset experiment.
   Keep old and new result tables separate. Selection provenance is now known;
   pair audit, split freeze, calibration, training and final results are unrun.
6. For the requested uncached Colab verification, run this actual acquisition
   in a fresh session and include source setup, installation, download, audit,
   calibration, scoring, figures and export in the clock. Browser access is
   still required. A new local download would not close the Colab gate.

No experiment behavior or frozen scientific choice was changed by this audit.
This is a metadata/content check; it does not need artificial model tests.

Sources: [official training CSV](https://storage.googleapis.com/sen1floods11/v1.1/splits/flood_handlabeled/flood_train_data.csv),
[upstream format and band definitions](https://github.com/cloudtostreet/Sen1Floods11),
[hand/weak label directories and official split description](https://github.com/cloudtostreet/Sen1Floods11/blob/master/docs/README.md).
Original project licensing does not relicense upstream data or metadata.
