"""Fetch exactly 100 upstream manual pairs for development, never the full dataset.

Selection is frozen before imagery is downloaded. Official membership is retained.
Files remain under ignored data/development-v1; public provenance goes in reports/.
"""
from __future__ import annotations
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urlencode
from urllib.request import urlopen

BUCKET = 'sen1floods11'
PREFIX = 'v1.1/data/flood_events/HandLabeled/'
ROOT = 'https://storage.googleapis.com/'
SPLIT_FILES = {'train':'flood_train_data.csv', 'validation':'flood_valid_data.csv', 'test':'flood_test_data.csv'}


def select_pairs(splits, counts):
    """Label-blind SHA-256 ranking within supplied official partitions, seed 42."""
    seen, selected = set(), []
    for split, pairs in splits.items():
        candidates = []
        for image, mask in pairs:
            match = re.fullmatch(r'([A-Za-z][A-Za-z-]*_[0-9]+)_S1Hand\.tif', image)
            if not match or mask != match[1] + '_LabelHand.tif':
                raise ValueError('only matching hand-labeled S1Hand/LabelHand pairs accepted')
            identifier = match[1]
            if identifier in seen:
                raise ValueError('duplicate official identifier across/within partitions')
            seen.add(identifier)
            candidates.append(dict(patch_id=identifier, image_name=image, mask_name=mask, split=split))
        count = counts.get(split, 0)
        if len(candidates) < count:
            raise ValueError('insufficient official pairs for requested bounded subset')
        candidates.sort(key=lambda r:hashlib.sha256(f"42:{split}:{r['patch_id']}".encode()).hexdigest())
        selected.extend(candidates[:count])
    if set(counts) - set(splits):
        raise ValueError('missing official partition')
    return sorted(selected, key=lambda r:r['patch_id'])


def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=90) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def listing(prefix):
    items, token = [], None
    while True:
        query = {'prefix':prefix, 'maxResults':1000}
        if token:
            query['pageToken'] = token
        result = json.loads(fetch(ROOT + 'storage/v1/b/' + BUCKET + '/o?' + urlencode(query)))
        items.extend(result.get('items', []))
        token = result.get('nextPageToken')
        if not token:
            return items


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, sorted({key for row in rows for key in row}))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=Path('data/development-v1'))
    args = parser.parse_args()
    destination = args.data_root
    destination.mkdir(parents=True, exist_ok=True)
    reports = Path('reports'); reports.mkdir(exist_ok=True)
    start = time.perf_counter()
    selection_path = destination/'selection.json'
    if selection_path.exists():
        provenance = json.loads(selection_path.read_text(encoding='utf-8'))
        selected = provenance['selected']
    else:
        splits, split_provenance = {}, {}
        for split, name in SPLIT_FILES.items():
            url = ROOT + BUCKET + '/v1.1/splits/flood_handlabeled/' + name
            content = fetch(url)
            (destination/name).write_bytes(content)
            splits[split] = [tuple(row) for row in csv.reader(StringIO(content.decode())) if row]
            split_provenance[split] = dict(url=url, sha256=hashlib.sha256(content).hexdigest(),
                                           upstream_pair_count=len(splits[split]))
        selected = select_pairs(splits, {'train':60,'validation':20,'test':20})
        objects = {}
        for folder in ('S1Hand/', 'LabelHand/'):
            for item in listing(PREFIX + folder):
                objects[item['name']] = {key:item[key] for key in ('name','generation','size','md5Hash','crc32c','updated')}
        for row in selected:
            row['objects'] = [objects[PREFIX + folder + row[key]] for folder,key in (('S1Hand/','image_name'),('LabelHand/','mask_name'))]
        provenance = dict(status='selection_frozen_before_imagery_read', purpose='upstream development substitute; not organizer kickoff subset',
                          selected=selected, seed=42, selection='SHA256(42:official_split:patch_id), smallest hashes per partition',
                          split_counts={'train':60,'validation':20,'test':20}, official_splits=split_provenance,
                          frozen_utc=datetime.now(timezone.utc).isoformat(),
                          documentation=['https://github.com/cloudtostreet/Sen1Floods11', 'https://raw.githubusercontent.com/cloudtostreet/Sen1Floods11/master/docs/README.md'],
                          listing_url=ROOT+'storage/v1/b/'+BUCKET+'/o?prefix='+quote(PREFIX))
        selection_path.write_text(json.dumps(provenance,indent=2),encoding='utf-8')
        (reports/'development_data_selection.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    if len(selected) != 100 or sum(len(r['objects']) for r in selected) != 200:
        raise ValueError('only the locked 100-pair development selection can be fetched')
    expected_bytes = sum(int(o['size']) for r in selected for o in r['objects'])
    if expected_bytes > 500_000_000:
        raise ValueError('unexpectedly large selection; refusing download')
    def download(item):
        path = destination/Path(item['name']).name
        if path.exists():
            content = path.read_bytes()
        else:
            url = ROOT+BUCKET+'/'+item['name']+'?generation='+item['generation']
            content = fetch(url)
        if len(content) != int(item['size']) or base64.b64encode(hashlib.md5(content).digest()).decode() != item['md5Hash']:
            raise ValueError('object length/MD5 mismatch: '+item['name'])
        if not path.exists():
            temporary = path.with_suffix('.partial'); temporary.write_bytes(content); temporary.replace(path)
        return dict(name=item['name'],path=str(path.resolve()),sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),generation=item['generation'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        downloaded = list(pool.map(download, [o for r in selected for o in r['objects']]))
    inventory = []
    for row in selected:
        for kind,key,folder in (('image','image_name','S1Hand/'),('mask','mask_name','LabelHand/')):
            inventory.append(dict(patch_id=row['patch_id'],kind=kind,path=row[key],units='db',band_order='VV,VH',label_source='manual',
                                  source='gs://'+BUCKET+'/'+PREFIX+folder+row[key],event_id=row['patch_id'].split('_')[0],
                                  scene_id='',source_patch_id=row['patch_id'],split=row['split']))
    write_csv(destination/'inventory.csv', inventory)
    result = dict(status='download_verified',pairs=100,files=len(downloaded),bytes=expected_bytes,
                  download_elapsed_seconds=time.perf_counter()-start, selection_sha256=hashlib.sha256(selection_path.read_bytes()).hexdigest(),
                  objects=downloaded, downloaded_utc=datetime.now(timezone.utc).isoformat())
    (reports/'development_data_download.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='objects'}))


if __name__ == '__main__':
    main()
