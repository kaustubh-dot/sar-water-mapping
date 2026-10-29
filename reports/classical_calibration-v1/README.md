# Superseded calibration evidence

Do not use this run for training or final evaluation. During this run the
training-ROI CSV line endings changed. The looks artifact and final configuration
therefore bind different byte hashes, despite identical ROI coordinates.

The original evidence is retained without rewriting its JSON/CSV artifacts.
Version 2 reruns the unchanged scientific choices with restored original ROI
bytes and a start/end input-hash stability check. Use
`configs/development-calibrated-v2.json` only after its independent review.
