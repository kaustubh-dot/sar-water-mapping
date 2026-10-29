# Held-out ENL region preselection

29 October 2026. Five fixed 32 x 32 rectangles were selected from raw VV/VH imagery before examining any filtered image, ENL output or held-out segmentation score. The first five held-out identifiers in the frozen manifest were rendered in `outputs/heldout_raw_roi_inspection.png` and opened with `view_image`. Only SAR arrays were loaded for this selection; held-out masks were not used for parameter tuning or ROI selection.

The three Ghana rectangles lie in visually uniform terrain away from visible water boundaries. Two rectangles in India_591317 lie inside the broad dark river. India_1018327 was inspected but not used because narrow channels, bright terrain and mixed texture make a homogeneous 32-pixel rectangle less defensible. The class tags are visual interpretation of raw imagery, not a new ground-truth annotation. Invalid SAR pixels must still be excluded and reported by the evaluator.

Coordinates are frozen in `heldout_enl_rois.csv`, with half-open pixel bounds. They will be identical across methods. All rectangles are evaluation-only: none enters effective-looks estimation or training. The small region count and imperfect real-world homogeneity limit ENL interpretation; pair it with mean intensity changes, ratio images and water segmentation scores.
