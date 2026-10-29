# Remaining-phase execution ledger

Started 28 October 2026. User authorized phasewise implementation and GPT-6.1 Sol xhigh review/fixes after each phase. Work uses branch `implementation/remaining-phases` in the existing project checkout.

- Baseline: committed the previously verified Phase 1-4 implementation as `33a9f7b`. No raw data, credentials, environments or checkpoints were committed.
- Data gate: 100 upstream hand-labeled development pairs downloaded (200 objects, 164,663,453 bytes); all upstream object sizes and MD5 checks passed. Official membership retained (60 train, 20 validation, 20 test), selected by label-blind hash ranking before imagery download. Organizer-specific acceptance cannot be closed from upstream data.
- Actual-data compatibility finding: exact input/mask affine equality rejected harmless upstream floating serialization differences. A bounded pixel-displacement comparison is being regression-tested; no resampling or source rewriting is allowed. Audit review must pass before calibration execution.
- Phase 5 implementation: exact locked compact U-Net and deterministic paired training APIs pass 21 focused CPU fixture tests. Exact parameter count is 487,857. Independent review is pending; GPU scientific training has not started. No architecture search authorized.
- Phase 6 packaging: evaluation runner and notebook are in progress; scientific execution depends on frozen real calibration. A generated notebook does not establish successful Colab execution.
- GPU: fresh hardware inspection confirms RTX 4000 Ada and approximately 18 GB free memory. A dedicated user virtual environment was created in a separate project directory. PyTorch `2.15.0+cu132` reports CUDA available; a CUDA tensor forward/backward smoke check passed on the RTX 4000 Ada. Exact dependencies were saved remotely with `pip freeze`. No system packages changed. The existing relocated conda executable is unusable; the dedicated Python venv avoids modifying it.
- Review policy: independent GPT-6.1 Sol xhigh reviewer must inspect each new phase, with material fixes and re-review before that phase is accepted. Concurrent code preparation does not imply downstream execution gates have passed.

29 October continuation:

- Phase 5 code/fixture review completed by independent GPT-6.1 Sol xhigh: no critical/important findings. Report `phase5_review.md`; 23 focused neural tests plus adversarial checks passed. Exact U-Net strict-determinism CUDA backward also passed remotely (parent-executed evidence). Actual training remains gated by real calibration.
- Data review independently verified all 200 upstream object hashes and label-blind official subset selection. One important finding: manifest paths are Windows-absolute. Fix is in progress using a new relative-path audit version; the original frozen audit is preserved.
- Phase 6 reviewer found primary timing includes cleanup-ablation calls for only some methods. Fix/re-review required before runtime results. Notebook environment and source-reference handling also need correction. No actual held-out or Colab acceptance is claimed.
- Subagents were temporarily interrupted by an account usage limit. After the user requested continuation, the account tool reported ordinary usage allowed and the requested Sol xhigh reviews resumed.

No remaining scientific execution phase is marked complete at this checkpoint.

Fresh combined implementation run: 79 tests passed in 28.56 seconds while the new data/model/evaluation modules were being prepared. This is fixture verification, not certification of all execution gates.

29 October resumed execution:

- Portable audit v3 is accepted: 100 manual-label upstream pairs, official 60/20/20 membership, verified object and decoded hashes. Seven touching cross-partition pairs require correlated-development claims; organizer acceptance remains open.
- Classical calibration v1 is superseded because ROI byte hashes changed during execution. Its evidence is preserved. The unchanged v2 rerun restores the original ROI bytes and rejects changing inputs before freezing configuration. Independent Sol xhigh acceptance is pending.
- Version 2 selects common VV fixed -18 dB, Median 5, Lee 5 and bilateral color sigma 3 dB on validation only. These are validation choices, not held-out results.
- Exact-byte Git attributes protect frozen ROI, configuration and calibration artifacts during Windows/Linux transfer.
- Fresh resource inspection: remote GPU has approximately 18.8 GB free memory; dedicated environment still reports CUDA available. No scientific training has started at this checkpoint.
- Neural native-mask export timing is receiving a focused fix/review. Notebook defaults and calibration integration are being completed independently. Fresh Colab execution remains unverified.

Subsequent verified execution:

- Calibration accepted: independent reviewer reproduced all 98 validation candidates and four cleanup records; 37 focused tests passed. Published freeze 9e9481a and exact-source-byte correction f9f6e56. Remote preflight verified all frozen source/configuration/ROI/looks hashes and clean checkout.
- First GPU invocation stopped in input preparation before any training update: identical TIFF SHA and decoded dB/masks but 378/524,288 converted power samples differed by one float32 ULP across Windows/Linux. Maximum relative difference 1.19e-7; probe recorded separately.
- Portable identity fix adds a versioned native decoded-source digest while preserving mandatory exact file hashes and legacy duplicate hashes. Derived ROI ENL roundoff alone receives a tight relative tolerance; identity/count/status remain exact. Implementation tests: 64 passed, one sandbox-only Git fixture deselected. Independent review remains required before training retry.
- Identity-only migration creates manifest audit-v4-sourceidentity and configuration v3. All 100 source pairs, split membership, ROIs, looks, thresholds, denoisers, selected neural input and training settings remain unchanged. No validation search or test-based selection is rerun.
- Actual frozen classical evaluation completed: 20 held-out patches, four primary rows, separate cleanup, 40 band/ROI ENLs, 72 synthetic test rows and 80 figures. Independent review accepted the scientific outputs. Runner 130.44 seconds on local CPU, excluding prior setup/download/calibration; no fresh-Colab or full-training timing claim.
- Measured pooled water IoU: raw 0.608415, Median 0.630412, Lee 0.606972, bilateral 0.630374. Negative findings include lower Lee IoU and lower Median IoU after cleanup. Full byte-preserved evidence is in reports/classical_results-v1.

Completed GPU and notebook execution:

- Portable identity gate accepted by independent Sol xhigh review; actual development-only preparation opened 80 patches and no held-out sources. Published source commit 61b09f9bfa61114d83bd7be19eba3de67d5621db; full regression suite passed 110 tests in 43.07 seconds.
- Authorized remote pair completed at that clean commit in 122.063888 seconds including 12.864063 seconds of preparation. Both models early-stopped: raw 11 epochs/327 updates, best epoch 6; Median-filtered 13/387, best epoch 8. Original environment and exact checkpoint hashes retained. Independent review replayed all 13 crop plans and all 40 native validation confusions exactly.
- Full classical notebook ran ten cells via nbclient on Linux in 91.784306 seconds through final archive/hash. Existing clone, cached TIFFs and preinstalled kernel prerequisites are disclosed; no fresh Colab claim. A first smoke wrapper used a short Git SHA and failed before data access; a new isolated attempt using the full SHA completed. The committed notebook helper already requires a full SHA for exact commit fetch.
- Independent notebook execution review checked source cells, 76 passing checks, calibration/provenance bindings, actual output arithmetic and unchanged scientific choices. All four held-out classical confusion counts match the original Windows run exactly; four unselected validation rows differ by one or two pixels across platforms. Original ZIP SHA and entry listing were parent-verified remotely and are distinguished from independently checked copied evidence.
- Frozen neural held-out evaluation completed: raw IoU 0.585460/F1 0.738537; Median-fed IoU 0.534632/F1 0.696756. Recorded checkpoint-evaluation subtotal 6.853086 seconds excludes training and final metadata writes. Independent review recomputed all 40 native-mask confusion matrices/validity arrays and aggregate metrics. No tuning follows these outcomes.
- Public checkpoint upload initially failed automatic approval review because explicit artifact publication consent was absent. The user explicitly approved publishing the 3.6 MB bundle; the development prerelease upload then succeeded. GitHub asset SHA-256 matches local ZIP b70dc5117a21ecac5b3b0e2ad9fc06f960a727370c81892089ac27b894100238. Credentials and raw TIFFs are absent from the bundle.
- Remaining acceptance work: final branch review/public instructions check, organizer archive, fresh uncached Colab run, and final submission tag. GPU development, classical/neural scientific execution and the cached notebook smoke are measured separately.

Final delivery review: GPT-6.1 Sol xhigh accepted the whole development branch with no unresolved P1/P2 findings. Independent isolated restoration ran the exact reproduction-guide block, verified all 200 cached file hashes and frozen manifest/splits, rehashed the public checkpoint ZIP/internal files, and checked the two-path-only training-report redaction. The complete final suite passed 110 tests in 83.58 seconds. Public-file pattern inspection found no raw dataset, weights, archives, credentials or private connection locations. The branch is ready for a development draft PR; organizer/fresh-Colab acceptance and final tag remain open.
