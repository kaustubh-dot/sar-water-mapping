# Project guardrails

Read `README.md`, `ROADMAP.md`, and `docs/EVALUATION_PROTOCOL.md` before changing experiment behavior. Read `docs/RESEARCH_REVIEW.md` before adding a model.

`docs/IMPLEMENTATION_LOCK.md` controls final v1 method choices and exact model/training details. Research selection is finished; proceed with execution gates rather than repeating broad literature searches.

- Work on the earliest incomplete roadmap phase. Update its evidence and checkboxes when verified.
- Keep the project a small Python experiment and one Colab notebook; no product UI or infrastructure without an explicit request.
- Keep the complete fresh Colab run below 30 minutes. Preserve the classical fallback. Lock one trained segmentation architecture, compact VV/VH U-Net, for v1. UDL4FL and foundation models are excluded from promised deliverables.
- Use the authorized remote GPU in a dedicated environment and project directory; inspect resource use first. Keep connection details and credentials out of public files. Do not modify system packages or interfere with unrelated jobs.
- Separate remote training time from Colab checkpoint evaluation. An inference-only runtime does not establish full training fits the challenge budget.
- Freeze splits before tuning and use validation for method selection. Never tune against final test labels.
- Use one shared numeric fixed threshold across denoisers when that strategy is selected. Disable cleanup in the primary filter comparison and report the cleanup ablation separately.
- Use a fixed ground-truth-water-positive patch set for macro water metrics across methods. Report dry-patch false positives separately.
- Distinguish dB, power, and amplitude. Use power for multiplicative Lee and ENL. Respect independent input and label validity masks.
- Use synthetic known references for PSNR. Never call real noisy SAR clean ground truth. Keep real and synthetic tables separate.
- Audit manual versus weak label provenance. Otsu-generated masks are not independent evaluation ground truth.
- Do not claim water mapping separates new flooding from permanent water without supporting data.
- Keep data, checkpoints, credentials, and bulky generated artifacts out of Git. Original project licensing does not relicense third-party materials.
- Check primary sources for model assumptions, accessible weights, preprocessing, and benchmark overlap. A paper's reported accuracy/runtime is not this project's measured result.
- Add focused correctness tests for scientific conversions, masks, filters, and metrics. Documentation-only edits need link/content verification, not artificial tests.
- Every added method must address a recorded failure and replace an optional item or have explicit scope authorization.
- Report negative findings and missing inputs plainly. Never fabricate results or mark unrun experiments complete.
