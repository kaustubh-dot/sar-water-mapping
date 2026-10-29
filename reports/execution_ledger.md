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
