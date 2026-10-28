"""Bounded Phase 3 synthetic development evidence; never scores test identities.

Run from repository root: python scripts/phase3_synthetic_check.py
Writes compact tracked numeric records, no images or simulated arrays.
"""
import csv
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import time

import numpy as np
import scipy
from sar_water.filters import FILTER_GRID, filter_power
from sar_water.metrics import psnr
from sar_water.synthetic import gamma_speckle, make_phantom, phantom_splits


def settings():
    for method, candidates in FILTER_GRID.items():
        for parameters in candidates:
            yield method, parameters, method + (':' + json.dumps(parameters, sort_keys=True) if parameters else '')


def main():
    rows, timing = [], []
    # Five training-identity development arrays, tiled to 512x512, both bands.
    # The VH-like band is a scaled simulated reference, not satellite data.
    development = []
    for index in range(5):
        ref = np.tile(make_phantom(f'phantom_{index:02d}'), (2,2))
        development.append(np.stack([gamma_speckle(ref, looks=4, seed=42), gamma_speckle(ref*.3, looks=4, seed=43)]))
    for method, parameters, identifier in settings():
        kwargs = dict(parameters, **({'looks':[4,4]} if method == 'lee' else {}))
        durations = []
        for power in development:
            start = time.perf_counter()
            filter_power(power, np.ones(power.shape[1:],bool), method=method, **kwargs)
            durations.append(time.perf_counter()-start)
        timing.append(dict(configuration=identifier, seconds_per_two_band_patch=durations,
                           total_five_patch_seconds=sum(durations),
                           extrapolated_100_two_band_512_patches_seconds_with_50pct_margin=sum(durations)/5*100*1.5))
    # All bounded settings on validation identities only, identical corruption.
    for key, split in phantom_splits().items():
        if split != 'validation':
            continue
        reference = make_phantom(key)
        for looks in (1,4):
            for seed in (42,43,44):
                noisy = gamma_speckle(reference, looks=looks, seed=seed)
                power = np.stack([noisy, noisy*.3])
                for method, parameters, identifier in settings():
                    kwargs = dict(parameters, **({'looks':[looks,looks]} if method == 'lee' else {}))
                    estimate = filter_power(power, np.ones(reference.shape,bool), method=method, **kwargs)
                    score = psnr(reference, estimate[0], data_range=1.)
                    rows.append(dict(source='simulated_backscatter', phantom_id=key, split=split,
                                     looks=looks, noise_seed=seed, configuration=identifier,
                                     data_range=1., psnr_db=score['value'], mse=score['mse'],
                                     vv_mean_change_percent=float((estimate[0].mean(dtype=np.float64)/noisy.mean(dtype=np.float64)-1)*100),
                                     vh_mean_change_percent=float((estimate[1].mean(dtype=np.float64)/(noisy*.3).mean(dtype=np.float64)-1)*100)))
    destination = Path('reports')
    path = destination/'phase3_synthetic_validation.csv'
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    evidence = dict(runtime_type='local_cpu_synthetic_development_only',
                    platform=platform.platform(), processor=platform.processor(),
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                    commit_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                    working_tree_changes='Phase 3 uncommitted implementation; commit SHA is base only',
                    config_sha256=hashlib.sha256(Path('configs/experiment.json').read_bytes()).hexdigest(),
                    seed=42, development_patch_count=5, shape=[2,512,512], development_known_looks=4,
                    validation_record_count=len(rows), timings=timing,
                    limitations='Synthetic arrays only; extrapolation excludes setup, I/O, scoring, other invocations and Colab hardware. No whole-notebook runtime gate passed. No synthetic settings selected or final test scoring.')
    (destination/'phase3_synthetic_runtime.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(records=len(rows), total_profile_compute_seconds=sum(t['total_five_patch_seconds'] for t in timing)),indent=2))


if __name__ == '__main__':
    main()
