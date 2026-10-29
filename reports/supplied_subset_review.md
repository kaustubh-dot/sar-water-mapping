# Supplied-subset recipe review

Reviewer: **GPT-6.1 Sol**, reasoning effort **xhigh**. Independent review dated 29 October 2026.

**Decision: accept the selection/provenance documentation only.** No P1/P2 findings remain in this bounded change. This does not accept a new data audit, split, calibration, trained model, benchmark or fresh Colab run; those gates remain open.

## Scope and verified evidence

Reviewed the [recipe audit](supplied_subset_recipe.md), [machine-readable record](supplied_subset_recipe.json), [ordered selection](supplied_subset_selection.csv), corresponding [README](../README.md) and [roadmap](../ROADMAP.md) changes, and byte-preservation attributes. No experiment implementation or frozen scientific configuration changed in the working-tree diff.

- Independently read the newly fetched local training CSV and the earlier development source CSV. Their bytes match exactly: 13,574 bytes, 252 headerless data rows, SHA-256 `57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
- Compared every selected image/mask pair and zero-based recipe index with the first 100 source rows, in order. All 100 IDs are unique and pair correctly as `S1Hand`/`LabelHand`. The selection SHA-256 is `9c4204b432254130a7dc7cc8e08705962b3a6eeab03824ea8fe76f9f8070b7b2`, matching the JSON record.
- Recomputed event counts: Ghana 31, India 40, Mekong 18, Nigeria 10 and Pakistan 1. All 100 come from the official upstream training list; their internal evaluation membership remains explicitly `unassigned`.
- Independently compared all IDs against `development_data_selection.json`. Exactly 22 overlap, all in the earlier training partition; the ordered overlap list in the JSON matches. The published development checkpoint cannot establish unseen-input performance on those 22 patches.
- Inspected the notebook source: it still consumes the earlier development selection and enforces its 60/20/20 membership. The documentation correctly preserves those results under their original identity and does not relabel them as measurements on this new selection.
- Confirmed that the missing-data warning agrees with the existing adapter/protocol. A direct NumPy evaluation maps NaN to -30 dB with the supplied call, which meets the existing VV water threshold; unspecified infinity handling maps infinities to extreme finite values. SAR metadata/finite validity and label metadata/code validity must remain separate before SAR-only filling and scoring.
- Verified 47 local Markdown link targets in the three reviewed Markdown documents, UTF-8 readability, `git diff --check`, and `git check-attr text` reporting `unset` for both frozen CSV/JSON artifacts. No artificial model tests were added for this documentation change.

The source comparison verifies the retained fetched bytes against the recorded recipe and earlier source. It does not independently authenticate the snippet sender's authority, inspect all new TIFFs or establish that a Colab download succeeded. The audit states these limits plainly.

## Remaining acceptance gates

Proceed with the distinct supplied-set data audit first: verify downloaded pairs, units, band order, independent validity, label provenance, integrity and spatial relationships. Freeze defensible internal event/scene/spatial splits before tuning. Re-establish training-only ROIs and normalization, calibrate on validation, and evaluate only after the new choices are frozen. Keep the earlier development results separate and disclose the 22-patch exposure.

The new set's audit, split freeze, calibration, training and held-out measurements remain unrun. A fresh uncached Colab Run All, including setup/access and final export below 30 minutes, also remains unverified. This review closes only the exact supplied-selection definition and its documentation; it does not close any of those execution gates.
