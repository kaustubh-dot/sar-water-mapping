# Reproduce the development experiment

Use the implementation branch and the recorded source commit. The measured GPU
pair uses `61b09f9bfa61114d83bd7be19eba3de67d5621db`. A later documentation commit
does not imply a retrained checkpoint. The organizer subset is a separate open
input; the commands below reproduce the upstream development experiment.

## Environment and notebook

For the pinned classical profile use Python 3.12 or later in a dedicated
environment:

```text
python -m pip install -r requirements-colab.txt
python -m pip install -e . --no-deps
```

The [single notebook](../notebooks/01_sar_water_mapping.ipynb) defaults to the
exact 100-pair upstream selection, official membership and recorded raw-image
ROIs. Set `REPO_REF` to the full source SHA before execution. It runs a complete
classical profile, including validation and exports, with neural training
disabled. Its organizer override deliberately stops before upstream-specific
calibration until organizer provenance is supported.

The notebook completed an actual Linux kernel execution with cached TIFFs;
this is not fresh Colab acceptance. Fresh installation, access and total Colab
runtime still need measurement. Its output ZIP has an authoritative sibling
timing JSON written after archive creation and checksum calculation.

## Restore exact frozen inputs

To reproduce the recorded checkpoint experiment rather than recalibrating,
run this Python from the repository root after installing dependencies. It
downloads only the 100 locked pairs, verifies cached object bytes, keeps access
logs under ignored outputs, and copies the committed exact-byte manifest and
split records into their expected relative directory. Existing different
selection or frozen files are rejected.

```python
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

repo = Path.cwd().resolve()
data = repo / "data/development-v1"
data.mkdir(parents=True, exist_ok=True)

def copy_exact(source, target):
    if target.exists():
        if target.read_bytes() != source.read_bytes():
            raise ValueError(f"Existing file differs: {target}")
    else:
        shutil.copyfile(source, target)

copy_exact(repo / "reports/development_data_selection.json", data / "selection.json")
access = repo / "outputs/reproduction-access-v1"
access.mkdir(parents=True, exist_ok=False)
subprocess.run([sys.executable, str(repo / "scripts/prepare_development_data.py"),
                "--data-root", str(data)], cwd=access, check=True)
audit = data / "audit-v4-sourceidentity"
audit.mkdir(exist_ok=True)
for name in ("manifest.csv", "splits.csv"):
    copy_exact(repo / "reports/source_identity-v3" / name, audit / name)
```

No label or parameter selection is performed by this restoration. File and
native decoded-source hashes are checked by downstream loaders. Original
derived-power hashes remain recorded, but portable v3 execution uses the
versioned source-domain identity. The [migration review](../reports/source_identity_review.md)
proves all scientific choices and file bytes stayed fixed.

## Execute frozen evaluation or training

From the repository root, with a new output directory:

```text
python -m sar_water.evaluate --manifest data/development-v1/audit-v4-sourceidentity/manifest.csv --splits data/development-v1/audit-v4-sourceidentity/splits.csv --config configs/development-calibrated-v3.json --enl-rois reports/heldout_enl_rois.csv --output outputs/reproduced-classical-v1 --figures
```

For a separately timed training run, install a compatible PyTorch build in the
dedicated environment, inspect GPU use, and run:

```text
python scripts/train_pair.py --manifest data/development-v1/audit-v4-sourceidentity/manifest.csv --splits data/development-v1/audit-v4-sourceidentity/splits.csv --config configs/development-calibrated-v3.json --output outputs/reproduced-training-v1 --device cuda --epochs 20 --time-limit 3600 --profile remote
```

`training.json` records the actual environment, initialization/crop identities,
normalization, updates, validation histories, selected checkpoints and budget.
Early stopping can give different update counts. The same seed does not promise
bitwise equality across hardware or software versions. The original training
environment is retained with the checkpoint artifact.

For checkpoint evaluation, extract the reviewed checkpoint bundle into an
ignored directory containing `training.json`, `raw_best.pt` and
`filtered_best.pt`. Verify its checksums, then run:

Download: [development-seed42-checkpoints.zip](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/development-seed42-v1/development-seed42-checkpoints.zip).
ZIP SHA-256: `b70dc5117a21ecac5b3b0e2ad9fc06f960a727370c81892089ac27b894100238`.

```text
python scripts/evaluate_neural.py --manifest data/development-v1/audit-v4-sourceidentity/manifest.csv --splits data/development-v1/audit-v4-sourceidentity/splits.csv --config configs/development-calibrated-v3.json --training-dir outputs/checkpoint-delivery-v1 --output outputs/reproduced-neural-v1 --device cuda --figures
```

This is a `checkpoint-evaluation` profile. It verifies identities before opening
held-out sources, saves native masks and independent validity arrays, and reports
remote training separately. It cannot establish full training within a fresh
Colab budget. Segmentation model outputs receive neither ENL nor denoising PSNR.

Tests: `python -m pytest -q --basetemp=outputs/pytest-reproduction`. A local Git
fixture can require ordinary Windows helper access outside restricted sandboxes.
No dataset or checkpoint binaries belong in Git.
