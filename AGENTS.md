# Project guardrails

Read `README.md`, `ROADMAP.md`, and `docs/EVALUATION_PROTOCOL.md` before changing experiment behavior. Read `docs/RESEARCH_REVIEW.md` before adding a model.

- Work on the earliest incomplete roadmap phase. Update its evidence and checkboxes when verified.
- Keep the project a small Python experiment and one Colab notebook; no product UI or infrastructure without an explicit request.
- Keep the complete fresh Colab run below 30 minutes. Preserve the classical fallback. Admit at most two neural architectures: one frozen reference and one compact trained segmentation model.
- Use the authorized remote GPU in a dedicated environment and project directory; inspect resource use first. Keep connection details and credentials out of public files. Do not modify system packages or interfere with unrelated jobs.
- Separate remote training time from Colab checkpoint evaluation. An inference-only runtime does not establish full training fits the challenge budget.
- Freeze splits before tuning and use validation for method selection. Never tune against final test labels.
- Distinguish dB, power, and amplitude. Use power for multiplicative Lee and ENL. Respect independent input and label validity masks.
- Use synthetic known references for PSNR. Never call real noisy SAR clean ground truth. Keep real and synthetic tables separate.
- Audit manual versus weak label provenance. Otsu-generated masks are not independent evaluation ground truth.
- Do not claim water mapping separates new flooding from permanent water without supporting data.
- Keep data, checkpoints, credentials, and bulky generated artifacts out of Git. Original project licensing does not relicense third-party materials.
- Check primary sources for model assumptions, accessible weights, preprocessing, and benchmark overlap. A paper's reported accuracy/runtime is not this project's measured result.
- Add focused correctness tests for scientific conversions, masks, filters, and metrics. Documentation-only edits need link/content verification, not artificial tests.
- Every added method must address a recorded failure and replace an optional item or have explicit scope authorization.
- Report negative findings and missing inputs plainly. Never fabricate results or mark unrun experiments complete.
