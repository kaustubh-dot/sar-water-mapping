# SAR water mapping

Track 2: SAR & Earth Observation, SSG x Research Club

Does reducing speckle improve water segmentation? This experiment compares
four classical pipelines and a compact U-Net on 100 Sentinel-1 VV/VH patches
with manual water labels from Sen1Floods11. Median filtering improves the
threshold baseline, but lowers the U-Net's pooled water IoU in our single-seed
comparison.

The complete classical pipeline ran in a fresh, uncached Colab CPU runtime in
**566.40 seconds (9 minutes 26 seconds)**, including installation, one dependency
restart, all 200 downloads, validation, evaluation and export. The
[execution review](reports/colab_execution_review.md) records the evidence.
Neural training was measured separately on a remote GPU.

## Submission files

- [Two-page IEEE-style technical note](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/v1.0.1-submission/sar_water_mapping_technical_note.pdf)
- [Five-slide PowerPoint](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/v1.0.1-submission/sar_water_mapping_pitch.pptx)
  and [PDF](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/v1.0.1-submission/sar_water_mapping_pitch.pdf)
- [Code, notebook, results and saved plots](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/v1.0.1-submission/sar_water_mapping_reproducible.zip)
- [Supplied-set U-Net checkpoints](https://github.com/kaustubh-dot/sar-water-mapping/releases/download/v1.0.1-submission/supplied-seed42-checkpoints.zip)

[Open the notebook in Colab](https://colab.research.google.com/github/kaustubh-dot/sar-water-mapping/blob/main/notebooks/01_sar_water_mapping.ipynb).
It defaults to the supplied subset and pins the exact source used in the
verified run. If setup requests a dependency restart, choose **Runtime >
Restart session and run all**. Keep the runtime filesystem: the notebook
preserves the original timer through that restart.

## Results on the supplied subset

The primary classical comparison uses one validation-selected threshold,
**VH below -20 dB**, with cleanup disabled for every method.

| Classical method | Water IoU | Water F1 | Dry false-positive pixels |
| --- | ---: | ---: | ---: |
| Raw | 0.2772 | 0.4341 | 39,098 |
| Median 5 | 0.4135 | 0.5851 | 1,727 |
| Lee 5 | 0.4051 | 0.5766 | 1,094 |
| Log-bilateral | 0.3825 | 0.5534 | 6,580 |

The learned comparison trains the same compact VV/VH U-Net architecture
separately on raw and Median-5 inputs. Both use probability strictly above
0.5, with no cleanup.

| U-Net input | Water IoU | Water F1 | Dry false-positive pixels |
| --- | ---: | ---: | ---: |
| Raw VV/VH | 0.4208 | 0.5923 | 3,877 |
| Median-5 VV/VH | 0.4043 | 0.5758 | 11,487 |

All six rows use the same 4,940,307 scored pixels across 31 Ghana test members.
The secondary macro metric uses a fixed set of 15 patches containing water.
Fifteen dry patches contribute to pooled scores and have separate false-positive
counts; one member has no scored pixels. See the
[classical CSV](reports/supplied_classical-v1/results_real.csv),
[neural CSV](reports/supplied_neural-v1/results_neural.csv) and
[full report](reports/final_report.md).

ENL measures power variation in five fixed land regions. Synthetic PSNR uses
known procedural references and Gamma noise in a
[separate table](reports/supplied_classical-v1/results_synthetic.csv).
Neither diagnostic alone establishes better shoreline or water segmentation.
The [cleanup ablation](reports/supplied_classical-v1/cleanup_ablation.csv)
is separate from the primary comparison.

## Reproduce locally

Use a dedicated environment with Python 3.12 or later for the pinned classical
dependencies. From the repository root:

```text
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-colab.txt
python -m pip install -e . --no-deps
python -m sar_water.synthetic --output outputs/synthetic-demo
python -m pytest -q --basetemp=outputs/pytest
```

For source acquisition, frozen calibration and real-data evaluation, follow
[docs/REPRODUCING.md](docs/REPRODUCING.md). It also gives the remote training
and checkpoint-evaluation commands. Regenerate the submission charts from
saved measurements with `python scripts/build_submission_figures.py`.

The notebook defaults to `DATA_SOURCE='supplied-first100'`. The earlier
`upstream-development` profile remains available for historical reproduction;
its data, settings and results are labeled separately. Generic organizer
inputs require their own audited source binding before calibration.

## Data and limitations

The supplied profile selects the first 100 ordered upstream manual-training
rows. All pairs are audited at their native 512 x 512 resolution. The frozen
event split has 29 training patches (Mekong, Nigeria, Pakistan), 40 validation
patches (India) and 31 test patches (Ghana). No cross-partition overlaps or
touching chips were found.

This is an internal event holdout. Earlier project training had used 22 of
these IDs, including eight current test IDs, so the results do not describe a
pristine blind test. We retain that exposure disclosure and the negative
filtered U-Net result. One test patch has no scored pixels; another has only
484. One of the five visually selected land ENL regions has valid SAR but no
valid label pixels. See the [data review](reports/supplied_data_review.md) and
[split provenance](reports/supplied_split_provenance-v1.json).

The masks identify observed surface water, including permanent water.
Distinguishing new flooding requires additional observations. The evidence
uses one training seed and a small set of events. The 30-minute Colab result
covers the classical pipeline; it does not include U-Net training. The remote
training pair took 76.77 seconds, and GPU checkpoint evaluation took 9.06
seconds under separate timing scopes.

## Project files

`src/sar_water/` contains the experiment code, `scripts/` the acquisition and
execution commands, and `tests/` the correctness checks. There is one notebook
under `notebooks/`. Frozen configurations and compact scientific evidence are
in `configs/` and `reports/`. Data, weights and bulky generated outputs stay
outside Git.

The [evaluation protocol](docs/EVALUATION_PROTOCOL.md) defines scoring and
validity masks. The [implementation lock](docs/IMPLEMENTATION_LOCK.md) fixes
the methods and training details. The [research review](docs/RESEARCH_REVIEW.md)
records primary sources. The [submission audit](reports/submission_audit.md)
and [roadmap](ROADMAP.md) record accepted execution gates. Historical files
removed during cleanup remain available at the original `v1.0-hackathon` tag.

## Team

| Member | Student ID |
| --- | --- |
| Kaustubh Upadhya | S20240030379 |
| Ayush Jha | S20240010020 |
| B. Ravi Chandra | S20240010022 |

## Attribution and license

D. Bonafilia, B. Tellman, T. Anderson and E. Issenberg, *Sen1Floods11: A
Georeferenced Dataset to Train and Test Deep Learning Flood Algorithms for
Sentinel-1*, CVPR Workshops, 2020.
[Dataset and access terms](https://github.com/cloudtostreet/Sen1Floods11).

The current source and deliverables are pinned by `v1.0.1-submission`.

The [MIT license](LICENSE) covers original project code and documentation.
Dataset files, external code, fonts and other third-party materials retain
their own terms. Checkpoints and submission documents are release assets;
raw data and credentials are absent from the repository.
