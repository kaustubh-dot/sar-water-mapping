# Supplied-set raw ROI inspection

The existing seed-42 event membership was frozen in supplied_evaluation_splits-v1.csv before this new-run inspection. Four raw training regions (two Nigeria land, two Mekong river) were re-inspected in outputs/supplied-roi-inspection/training_candidates.png. Both bands have no strong visible boundaries in these rectangles, all1024SAR/scored pixels are valid and the manual training class is uniform. Existing region coordinates were reused only for identifiers in the new training partition, never Ghana test regions. No filtered new-run outputs or validation/test scores were inspected. The four train-region power ENLs will be recomputed under this membership and frozen before validation.

Historical project exposure and previous inspection of these source images are disclosed in split provenance; this is not pristine blind data selection. The fixed number of small regions and approximate real-world homogeneity limit interpretation.

Five test-only32x32land rectangles were selected from raw SAR of Ghana_103272,
Ghana_187318 and Ghana_168875 before any new filtered result or test score.
Raw full-patch candidates and final crops were opened with view_image at
outputs/supplied-roi-inspection/test_raw_candidates.png and test_roi_crops.png.
The selection did not read test label masks. SAR validity is complete in all
five rectangles; visually uniform land away from the visible small dark ponds
was preferred. No defensible32square water rectangle was identified in these
inspected images, so this experiment promises land-region ENL only. The class
tags are visual interpretation, not independent ground-truth annotations.
Coordinates are frozen in supplied_heldout_enl_rois-v1.csv and shared unchanged
by every method. These regions never enter training looks or normalization.
