# Supplied-set execution ledger

Started 29 October 2026. User explicitly authorized closing the supplied-set
critical gate and deferring uncached Colab. Existing development files/results
remain preserved. Base implementation commit: 612040e20ecb69fa2c2a875aec4ca32c18249208.

## Approved execution contract

Use exactly the first 100 ordered source rows recorded in
`supplied_subset_selection.csv`, bound to source CSV SHA-256
`57be4dc440bf8a526effa77e06d4b8cb7a8484589c0bffa201d8e0f49e994beb`.
No replacement, reordering to choose membership, new model or grid change.
New files use `supplied-v1` data/run identities. Existing metadata audit gives
Ghana31, India40, Mekong18, Nigeria10, Pakistan1.

Ruling: reuse the existing seed-42 event-group split generator before reading
imagery/labels. It assigns Mekong/Nigeria/Pakistan to train (29 patches), India
to validation (40), Ghana to test (31). Group separation takes precedence over
exact patch proportions; no search for a better-scoring split is allowed.
Previous development training exposure is 5 new-train, 9 new-validation and
8 new-test patches. New U-Nets start from scratch. The prior project exposure
is disclosed; this is not a claim of pristine blind evaluation.

## Phase gates

- [x] Acquisition implementation: exact identities, pinned object integrity,
  event membership freeze, cache reuse, safe immutable artifacts; focused tests.
- [x] Independent Sol xhigh acquisition/data audit acceptance.
- [ ] Source-aware calibration + supplied notebook profile implementation;
  preserve development profile and exactly one notebook; independent review.
- [ ] Inspect raw training and test-only ENL regions, freeze training looks and
  validation choices under unchanged method grids; independent review.
- [ ] Remote GPU resource preflight, dedicated environment, seed42 paired
  scratch training under one-hour cap; completed-pair independent review.
- [ ] Frozen classical/synthetic and neural held-out evaluation, separate
  outputs, figures/counts/hash evidence; independent result review.
- [ ] Notebook supplied-profile execution smoke, report/reproduction/roadmap
  update, final integration review and branch publication.

Uncached Colab, its under-30-minute acceptance and final submission tag are
explicitly deferred. A local/remote cached smoke cannot close them.

Phase1 accepted:100pairs/200objects169393092bytes,44verifiedcachedcopies156downloads,148.656s acquisition. All512squareVV/VHmanuallabels; frozen29/40/31 preserved. No cross-partition overlap/touch;20within-partitiontouchingpairs. Scoredpixels train6769828,val8788754,test4940307; Ghana26376testno-score andGhana24858test484pixels retained. FourtrainROIs andfivetestlandROIs independentlyaccepted, no waterENLregionpromised. Traininglooks nextfreezeexpectedVV4.60203,VH2.58204. Sourceprofileimplementationpausedbrieflybyusageerror; usercontinuedandusageavailable. Transferapprovalreviewfailurewasaccountusage,notasafetydetermination; retrynowauthorizedsameGPUhost.
