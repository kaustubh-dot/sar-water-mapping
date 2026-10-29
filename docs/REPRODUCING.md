# Reproduce the supplied and development profiles

The supplied-first100 acquisition, raster audit, frozen internal event split,
fixed ROIs and source-aware notebook implementation are accepted. The new
calibration and paired scratch training are independently accepted. Frozen
held-out measurements are independently accepted. The cached supplied
notebook smoke is independently accepted, closing S1. Fresh uncached classical Colab is accepted at 566.40 seconds, including installation, one dependency restart and all 200 downloads. See the [retained-evidence review](../reports/colab_execution_review.md). Publication to `main` and the submission tag remain pending.

The distinct earlier development experiment remains reproducible below. Its
measured GPU pair uses source commit
`61b09f9bfa61114d83bd7be19eba3de67d5621db`; a later documentation commit does
not imply retraining. Preserve its original command blocks, checkpoints and
result labels. They do not reproduce the supplied-first100 experiment.

## Environment and the single notebook

For the pinned classical profile use Python 3.12 or later in a dedicated
environment:

```text
python -m pip install -r requirements-colab.txt
python -m pip install -e . --no-deps
```

The [single notebook](../notebooks/01_sar_water_mapping.ipynb) defaults to
`DATA_SOURCE='supplied-first100'`. Set `REPO_REF` to a reviewed full source SHA.
The notebook records checkout, installation, access, checks, audit, calibration,
scoring and exports, with neural training disabled. Its source configuration
binds the exact supplied identities before calibration and held-out access.
`DATA_SOURCE='upstream-development'` preserves the earlier 60/20/20 workflow.
The generic `organizer` override deliberately stops before calibration.

The supplied split is 29 training patches (Mekong/Nigeria/Pakistan), 40
validation (India), 31 test (Ghana), under the existing seed-42 event rule.
No cross-partition overlap or touching chips was found. Prior project training
exposure is 22 IDs, distributed 5/9/8; new neural models must start from scratch,
and the current test is not pristine blind data. `Ghana_26376` remains a
no-score test patch. Five fixed held-out ENL rectangles support visually
homogeneous land diagnostics only. See the [accepted data review](../reports/supplied_data_review.md)
and [profile review](../reports/supplied_profile_review.md).
The fifth ENL region (`supplied_enl_05`, `Ghana_168875`) has valid SAR but no
valid label pixels, so its land tag is visual only. The other four are fully
manual-label land. Preserve all five fixed regions: ENL uses SAR validity and
does not require label validity; this is separate from segmentation scoring.

The accepted cached supplied smoke used a clean isolated Linux clone pinned to
`9aef5d3b499ca49bcba5fc3c732238c2fa3ba55f` and completed in **123.04392588
seconds**, from the first executable cell through the final ZIP/checksum. All
10 cells completed without errors; 96 tests passed in 8.30 seconds. See the
[summary](../reports/supplied_notebook_smoke_summary.json) and
[independent notebook review](../reports/supplied_notebook_review.md).

This was a fresh kernel with **200 cached source TIFFs**, an existing clean
clone and preinstalled kernel prerequisites. Initial cloning/cache preparation
were outside the clock; the measured cells include pip calls, cached object
verification, checks, audit, validation, scoring, 124 figures and the only
archive write/hash. Neural training was disabled. All 98 validation scientific
summaries, four held-out classical confusion counts, ENL and synthetic records
reproduce the accepted experiment; tiny reported radiometry roundoff does not
change choices or counts. Run-local path-bound hashes appropriately differ.

The retained local export `outputs/supplied-notebook-run-v1.zip` is 164,908,503
bytes, SHA-256
`968b9065b9ded3fb0c3c472e10e4fccf60c12a1f10c5f82481698de841577cef`.
The authoritative runtime sidecar remains outside that ZIP by design. This is
cached Linux integration evidence; it does not close S2 or establish full
neural training within a fresh Colab budget.

The old notebook's 91.78-second cached Linux run applies to development only.
Neither that run nor the new wiring verifies fresh Colab. A notebook export has
an authoritative sibling timing JSON written after archive creation and its
checksum. Work performed before the first executable cell must be disclosed.

## Verified fresh Colab execution

Open the [executed source notebook](https://colab.research.google.com/github/kaustubh-dot/sar-water-mapping/blob/3eecc1434991835e576e7d3d09d967fbd9388359/notebooks/01_sar_water_mapping.ipynb). For exact reproduction, set `REPO_REF` in its configuration cell to `3eecc1434991835e576e7d3d09d967fbd9388359` before Run All; the notebook's branch default can advance. Keep `DATA_SOURCE='supplied-first100'`, `PROFILE='full'` and neural training disabled.

The observed fresh CPU runtime started with zero source TIFFs and downloaded all 200 objects. Pinned installation replaced Colab's preloaded NumPy/matplotlib. When setup requests a restart, choose **Runtime > Restart session and run all**, preserving the runtime filesystem. The first cell restores the original clock, so installation, the restart and its wait remain included. Do not reset the runtime filesystem midway through this recovery.

The accepted run took **566.397461905 seconds**, including calibration, held-out evaluation, figures, archive creation and checksum. Its original ZIP and sibling timing JSON are retained under `outputs/colab-20261029T105716698462Z.*` outside Git. The [independent review](../reports/colab_execution_review.md) records hashes, result comparisons and the external freshness observation. The files retain their default unverified attestation fields unchanged; metadata alone is insufficient evidence of a fresh runtime. The executed notebook/stdout was not retained, so no exact Colab pytest count is claimed. This is the compliant classical core, separate from remote U-Net training and checkpoint evaluation.

## Supplied inputs: restore accepted metadata and objects

For exact frozen reproduction, restore the accepted metadata before invoking
acquisition. This retains original object generations, split-freeze bytes and
all relative bindings. Run this Python from the repository root after installing
dependencies. Use a new access-log directory; differing existing files stop the
restoration instead of being replaced.

```python
from pathlib import Path
import shutil
import subprocess
import sys
from sar_water.supplied_profile import verify_supplied_source_config

repo = Path.cwd().resolve()
data = repo / "data/supplied-v1"
data.mkdir(parents=True, exist_ok=True)

def copy_exact(source, target):
    if target.exists():
        if target.read_bytes() != source.read_bytes():
            raise ValueError(f"Existing file differs: {target}")
    else:
        shutil.copyfile(source, target)

for name in ("split_freeze.json", "splits.csv", "selection.json", "download.json"):
    copy_exact(repo / "reports/supplied_acquisition-v1" / name, data / name)
print("Existing TIFFs before acquisition:", len(list(data.glob("*.tif"))))
subprocess.run([sys.executable, str(repo / "scripts/prepare_supplied_data.py"),
                "--data-root", str(data),
                "--output", str(repo / "outputs/supplied-acquisition-reproduction-v1")],
               check=True)
audit = data / "audit-v1"
audit.mkdir(exist_ok=True)
for name in ("manifest.csv", "splits.csv"):
    copy_exact(repo / "reports/supplied_data-v1" / name, audit / name)
verify_supplied_source_config(repo / "reports/supplied_source-v1.json",
                              audit / "manifest.csv", audit / "splits.csv")
```

The helper retrieves the exact source CSV if missing, checks its pinned SHA,
regenerates the exact inventory and verifies every selected object's bytes. It
downloads only the 200 selected objects; no cache override is used above.
The retained completion log records the original acquisition and its origins,
not a new uncached download. Record this run's actual existing TIFF count and
wall time separately. No raw TIFF or checkpoint is restored from Git.

Restoring manifests does not replace raster validation. Downstream loaders check
file and native decoded-source identities. To independently repeat the full
100-pair audit without changing the accepted bound manifest, use a new output:

```text
python -m sar_water.data data/supplied-v1/inventory.csv --splits data/supplied-v1/splits.csv --output outputs/supplied-independent-audit-v1 --contact-sheet
```

For a new supplied run rather than exact frozen restoration, the original
acquisition/audit entry points are:

```text
python scripts/prepare_supplied_data.py --data-root data/supplied-v1 --output outputs/supplied-acquisition-newrun-v1
python -m sar_water.data data/supplied-v1/inventory.csv --splits data/supplied-v1/splits.csv --output data/supplied-v1/audit-v1 --contact-sheet
```

Run those only with new/compatible destinations. An existing audit is immutable.
A new acquisition's timestamps and metadata hashes can differ from the accepted
source configuration even when IDs and object bytes agree; generate a new source
configuration for that run. Do not replace the accepted metadata to make hashes
match.

## Supplied source configuration and calibration

The metadata-only writer and verifier are reusable outside the notebook:

```python
from pathlib import Path
from sar_water.supplied_profile import (
    write_supplied_source_config, verify_supplied_source_config,
)

manifest = Path("data/supplied-v1/audit-v1/manifest.csv")
splits = Path("data/supplied-v1/audit-v1/splits.csv")
source = Path("outputs/reproduced-supplied-source-v1.json")
write_supplied_source_config(manifest, splits, Path("data/supplied-v1"), source)
verify_supplied_source_config(source, manifest, splits)
```

The recorded execution uses `reports/supplied_source-v1.json`; verify that
existing artifact after restoring its exact inputs. The writer above uses a new
exclusive output and cannot overwrite it. A new source configuration must be
passed consistently with `--source-config`; it cannot override locked grids or
training settings. The notebook also snapshots the recipe, acquisition metadata,
training ROIs and held-out ENL ROIs into its run bundle.

The following are the versioned supplied execution targets. Existing outputs
are never overwritten: use new output/configuration names for an independent
rerun, then use that same configuration throughout training and evaluation.
Actual calibration completed with 98 candidates on the 40 India validation
patches. Its frozen common rule is VH below -20 dB, Median 5, Lee 5 and
bilateral window 5/spatial sigma 2/color sigma 3 dB; Median 5 is selected for
neural input. The [independent calibration review](../reports/supplied_calibration_review.md)
accepted these choices with zero held-out access. No held-out score is implied.

```text
python scripts/calibrate_classical.py --manifest data/supplied-v1/audit-v1/manifest.csv --splits data/supplied-v1/audit-v1/splits.csv --rois reports/supplied_training_rois-v1.csv --source-config reports/supplied_source-v1.json --config configs/supplied-calibrated-v1.json --output reports/supplied_calibration-v1
```

## Supplied scratch training and frozen evaluation

**Training independently accepted.** The raw/Median-5 scratch pair completed
from clean source `0cdb7874e3699cd1e6c0f68a98b5eea6c6e9ff50` after calibration
acceptance. Its [review](../reports/supplied_training_review.md) verifies matched
scratch initialization, training-only normalization/crops and all 80 native
validation confusion matrices, with no held-out reads. For a new run,
inspect GPU and disk use first (`nvidia-smi`,
`df -h` on the authorized Linux host), and use its dedicated project directory
and environment. Install a compatible PyTorch build there without changing
system packages or unrelated jobs. Keep connection details and credentials
out of public records. Preserve the same relative data/report/config layout.

```text
python scripts/train_pair.py --manifest data/supplied-v1/audit-v1/manifest.csv --splits data/supplied-v1/audit-v1/splits.csv --config configs/supplied-calibrated-v1.json --output outputs/supplied-training-seed42-v1 --device cuda --epochs 20 --time-limit 3600 --profile remote
```

This starts a new raw/selected-filter pair from scratch under the locked
architecture and seed. Do not substitute the old development checkpoints.
Retain `training.json`, both best checkpoints, crop/initialization/normalization
identities, curves, actual updates, environment and budget records. Public
training metadata is retained in [reports/supplied_training-v1](../reports/supplied_training-v1/summary.json);
checkpoint binaries stay outside Git. The accepted pair took 76.7675 seconds
including 11.1010 seconds of input preparation. Raw ran 10 epochs/150 updates
(best epoch 5); Median 5 ran 9 epochs/135 updates (best epoch 4). These are
training/validation records, not held-out scores. The reviewed local bundle
`outputs/supplied-seed42-checkpoints.zip` has SHA-256
`9605d1906802434d73d5ef73239e127395779a03df11596004c94e4acb5aa6d6`
and 3,666,469 bytes. It has no public release yet; the earlier development
release cannot substitute for these supplied checkpoints.

After all source/configuration/checkpoint identities are verified and the
calibration is accepted, the frozen classical and neural execution commands are:

```text
python -m sar_water.evaluate --manifest data/supplied-v1/audit-v1/manifest.csv --splits data/supplied-v1/audit-v1/splits.csv --config configs/supplied-calibrated-v1.json --enl-rois reports/supplied_heldout_enl_rois-v1.csv --output outputs/supplied-classical-v1 --figures
python scripts/evaluate_neural.py --manifest data/supplied-v1/audit-v1/manifest.csv --splits data/supplied-v1/audit-v1/splits.csv --config configs/supplied-calibrated-v1.json --training-dir outputs/supplied-training-seed42-v1 --output outputs/supplied-neural-v1 --device cuda --figures
```

The recorded [supplied classical table](../reports/supplied_classical-v1/results_real.csv)
and [supplied neural table](../reports/supplied_neural-v1/results_neural.csv)
are retained in `reports/supplied_classical-v1` and `reports/supplied_neural-v1`.
The [independent result review](../reports/supplied_results_review.md) accepts
these measurements and their shared scoring population. All six methods share 4,940,307 scored
pixels, 15 water-positive macro members, 15 dry patches and one no-score member.
Raw U-Net pooled IoU/F1 is 0.4208/0.5923; Median-input U-Net is 0.4043/0.5758.
The filtered-model negative result is retained. The classical CPU runner took
59.38 seconds including synthetic work/figures; neural GPU checkpoint
evaluation took 9.06 seconds, separately from 76.77 seconds of remote training.
These runner subtotals exclude setup/access/calibration and their final metadata
serialization; they do not establish a full notebook runtime. Keep real tables separate from synthetic PSNR, retain explicit
no-score status and dry-patch false positives, and use the same water-positive
macro set across methods. Neural outputs receive no ENL or denoising PSNR.
Remote training, checkpoint evaluation and full notebook runtime are separate
measurements. The separately executed fresh classical Colab run took 566.40 seconds; see the [timing summary](../reports/colab_observed_summary.json). It does not certify full neural training within the Colab budget.

## Earlier development: restore exact frozen inputs

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

## Earlier development: execute frozen evaluation or training

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
