"""Deterministic simulated backscatter, never clean Sentinel-1 ground truth.

Run: python -m sar_water.synthetic --output outputs/phase2_synthetic
The split map is defined before noise. Each (phantom, L, seed) realization
is regenerated identically for every method; observations are never clipped.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from .metrics import psnr


def phantom_splits():
    return {f'phantom_{i:02d}': ('train' if i < 6 else 'validation' if i < 9 else 'test') for i in range(12)}


def make_phantom(phantom_id):
    if phantom_id not in phantom_splits():
        raise ValueError('unknown phantom identity')
    index = int(phantom_id.rsplit('_',1)[1])
    y, x = np.mgrid[:256,:256]
    reference = np.full((256,256), .35+.025*index, dtype=np.float64)
    reference[:,128:] = .7+.015*index  # sharp vertical edge
    reference[32:112,24:100] = .1+.004*index  # homogeneous low power
    river = np.abs(y-(122+10*np.sin((x+index*7)/25))) <= (1+index%3)
    reference[river] = .02+.001*index  # narrow water-like structure
    circle = (x-(65+index*3))**2+(y-195)**2 < (22+index)**2
    reference[circle] = .06
    texture = .55 + .13*np.sin(x/3+index)*np.cos(y/5-index)
    reference[160:240,160:240] = texture[160:240,160:240]
    return reference.astype(np.float32)


def gamma_speckle(reference, *, looks, seed):
    reference = np.asarray(reference, dtype=np.float32)
    if not np.isfinite(looks) or looks <= 0:
        raise ValueError('looks must be finite and positive')
    if not np.isfinite(reference).all() or np.any(reference <= 0):
        raise ValueError('reference must be finite positive power')
    noise = np.random.default_rng(seed).gamma(shape=looks, scale=1/looks, size=reference.shape)
    return (reference*noise).astype(np.float32)


def run_raw_baseline(output):
    """Write split membership first, then all 72 raw/noisy PSNR records."""
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    splits = phantom_splits()
    with (output/'synthetic_splits.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['phantom_id','split','source'])
        writer.writerows((key, split, 'simulated_backscatter') for key, split in splits.items())
    path = output/'raw_noisy_psnr.csv'
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer = csv.DictWriter(stream,fieldnames=['source','phantom_id','split','looks','noise_seed','method','data_range','psnr_db','mse','status'])
        writer.writeheader()
        for key,split in splits.items():
            reference = make_phantom(key)
            for looks in (1,4):
                for seed in (42,43,44):
                    noisy = gamma_speckle(reference,looks=looks,seed=seed)
                    score = psnr(reference,noisy,data_range=1.)
                    writer.writerow(dict(source='simulated_backscatter',phantom_id=key,split=split,looks=looks,noise_seed=seed,method='raw_noisy',data_range=1.,psnr_db=score['value'],mse=score['mse'],status=score['status']))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='outputs/phase2_synthetic')
    print(run_raw_baseline(parser.parse_args().output))


if __name__ == '__main__':
    main()
