"""Exercise Phase 4 only on known synthetic validation identities.

Run from the project root: python scripts/phase4_fixture.py
Output is explicitly development evidence and cannot freeze real choices.
"""
import json
from pathlib import Path
from time import perf_counter
import numpy as np

from sar_water.benchmark import validation_search
from sar_water.data import adapt_arrays
from sar_water.synthetic import gamma_speckle, make_phantom, phantom_splits


def main():
    patches = {}
    membership = phantom_splits()
    for key, split in membership.items():
        if split != 'validation':
            continue
        reference = make_phantom(key)
        vv = gamma_speckle(reference, looks=4, seed=42)
        vh = gamma_speckle(reference * 10**(-8/10), looks=4, seed=43)
        # Known reference classes, never a noisy-image/Otsu-derived mask.
        target = (reference < .15).astype(np.int8)
        patches[key] = adapt_arrays(np.stack([vv, vh]), target,
                                    units='linear_power', band_order='VV,VH')
    start = perf_counter()
    result = validation_search(patches, membership, looks=[4, 4],
                               fallback_thresholds={'VV': -10, 'VH': -18})
    result.update(source='simulated_backscatter_only', elapsed_seconds=perf_counter()-start,
                  label_definition='known reference power <0.15; not real SAR truth',
                  fallback_source='explicit synthetic fixture thresholds; not real calibration')
    output = Path('outputs/phase4_fixture')
    output.mkdir(parents=True, exist_ok=True)
    (output/'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(dict(source=result['source'], status=result['status'],
                          rows=len(result['validation_table']), primary_rows=len(result['primary']),
                          cleanup_rows=len(result['cleanup_ablation']), seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    main()
