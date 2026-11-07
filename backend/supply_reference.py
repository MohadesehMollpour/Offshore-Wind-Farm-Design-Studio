"""The user-supplied Lattice directory is a contextual snapshot, not a vendor qualification."""
import hashlib
import json
import math
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from .catalog import ROOT

REFERENCE_DIR = ROOT / 'sources/references/lattice_supply'


def validate_supply_reference(kg, geo):
    """Validate inert JSON before it is bundled in the isolated explorer."""
    arrays = ['subsystems', 'components', 'clusters', 'countries', 'phases', 'primaries',
              'vesselClasses', 'suppliers', 'sites', 'links', 'vessels', 'ports']
    if not isinstance(kg, dict) or any(not isinstance(kg.get(k), list) for k in arrays):
        raise ValueError('Expected Lattice directory arrays')
    if not 1 <= len(kg['suppliers']) <= 10000 or not 1 <= len(kg['components']) <= 200:
        raise ValueError('Unexpected supplier/component count')
    def index(v, key):
        if type(v) is not int or not 0 <= v < len(kg[key]):
            raise ValueError('Invalid directory index: ' + key)
    keys = set()
    for c in kg['components']:
        if len(c) != 4 or not re.fullmatch(r'[a-z0-9_]+', c[0]) or c[0] in keys or c[3] not in ['fixed', 'floating', 'both'] or c[2] not in [x[0] for x in kg['subsystems']]:
            raise ValueError('Invalid component definition')
        keys.add(c[0])
    for s in kg['suppliers']:
        if len(s) != 10 or type(s[6]) is not int or not 0 <= s[6] <= 7:
            raise ValueError('Invalid supplier row')
        for v in s[5]: index(v, 'clusters')
        for v in s[7]: index(v, 'phases')
        if s[4] is not None and s[4] >= 0: index(s[4], 'countries')
        if s[8]:
            u = urlparse(s[8])
            if u.scheme != 'https' or u.hostname not in ['www.uowd.co.uk', 'uowd.co.uk'] or u.username or u.password:
                raise ValueError('Unexpected supplier profile URL')
    for row in kg['links']:
        if len(row) != 4 or row[2] not in [0, 1, 2]: raise ValueError('Invalid link evidence grade')
        index(row[0], 'suppliers'); index(row[1], 'components')
    if len({(r[0], r[1]) for r in kg['links']}) != len(kg['links']):
        raise ValueError('Duplicate supplier/component link')
    for row in kg['sites']: index(row[0], 'suppliers')
    for row in kg['vessels']:
        index(row[0], 'suppliers'); index(row[1], 'vesselClasses')
        if row[2] not in [0, 1, 2]: raise ValueError('Invalid vessel evidence grade')
    for row in kg['ports']:
        index(row[0], 'suppliers')
        if row[1] not in [0, 1, 2]: raise ValueError('Invalid port evidence grade')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', kg['meta']['extracted']):
        raise ValueError('Invalid snapshot date')
    if not isinstance(geo.get('places'), dict): raise ValueError('Expected place coordinates')
    for p in geo['places'].values():
        if len(p) != 3 or not all(type(v) in [float, int] and math.isfinite(v) for v in p) or not -90 <= p[0] <= 90 or not -180 <= p[1] <= 180 or p[2] not in [0, 1]:
            raise ValueError('Invalid place coordinate')
    return kg, geo


def _reference_key():
    path = REFERENCE_DIR / 'reference.json'
    stat = path.stat()
    return str(path), stat.st_mtime_ns, stat.st_size


def load_supply_reference():
    """Verified summary; the cache is keyed on the file's identity, so a changed file is re-verified."""
    return _verified_reference(*_reference_key())['summary']


def supply_reference_bytes():
    """The exact bytes that passed verification, so the download cannot differ from what was checked."""
    return _verified_reference(*_reference_key())['raw']


@lru_cache(maxsize=2)
def _verified_reference(path, mtime_ns, size):
    raw = Path(path).read_bytes()
    record = json.loads(raw.decode('utf-8'))
    data = record['data']
    encoded = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    if hashlib.sha256(encoded).hexdigest() != record['metadata']['data_sha256']:
        raise ValueError('Lattice reference data checksum mismatch')
    kg, geo = validate_supply_reference(data['kg'], data['geo'])
    strong = [{si for si, ci, grade, _ in kg['links'] if ci == c and grade < 2} for c in range(len(kg['components']))]
    linked = {ci for _, ci, _, _ in kg['links']}
    return {'raw': raw, 'summary': {'metadata': record['metadata'], 'counts': {**{k: len(kg[k]) for k in ['suppliers', 'sites', 'components', 'links', 'clusters', 'vessels', 'ports']},
            'thin_components': sum(len(s) <= 2 for s in strong), 'unlinked_components': len(kg['components']) - len(linked)},
            'data_notes': kg['meta']['dataNotes'], 'geography': geo['meta']}}


def original_supply_reference():
    meta = load_supply_reference()['metadata']
    path = (REFERENCE_DIR / meta['original_filename']).resolve()
    if not path.is_relative_to(REFERENCE_DIR.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != meta['original_sha256']:
        raise ValueError('Original Lattice attachment checksum mismatch')
    return path
