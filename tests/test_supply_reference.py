import copy
import hashlib
import json
import pytest
from backend.catalog import ROOT
from backend.supply_reference import REFERENCE_DIR, load_supply_reference, original_supply_reference, validate_supply_reference
from backend.work_packages import package
from tests.test_work_packages import scenario
from tests.test_ingestion import client, create


def test_snapshot_identity_and_local_bundle():
    ref = load_supply_reference()
    assert ref['counts'] == {'suppliers':885, 'sites':711, 'components':34, 'links':214, 'clusters':8,
                             'vessels':95, 'ports':19, 'thin_components':17, 'unlinked_components':6}
    assert hashlib.sha256(original_supply_reference().read_bytes()).hexdigest() == ref['metadata']['original_sha256']
    manifest = json.loads((REFERENCE_DIR/'bundle_manifest.json').read_text(encoding='utf-8'))
    public = ROOT/'dashboard/public/assets/lattice'
    for filename, sha in manifest['assets'].items():
        assert hashlib.sha256((public/filename).read_bytes()).hexdigest() == sha, filename
    frame = (public/'index.html').read_text(encoding='utf-8')
    assert 'https://' not in frame and "connect-src 'none'" in frame
    assert 'Content-Security-Policy' in frame


@pytest.mark.parametrize('mutation', [
    lambda k,g:k['links'][0].__setitem__(0, len(k['suppliers'])),
    lambda k,g:k['links'][0].__setitem__(2, 3),
    lambda k,g:k['links'].append(k['links'][0]),
    lambda k,g:k['suppliers'][0].__setitem__(8, 'javascript:alert(1)'),
    lambda k,g:k['suppliers'][0].__setitem__(8, 'https://unrelated.example/profile'),
    lambda k,g:next(iter(g['places'].values())).__setitem__(0, float('nan')),
    lambda k,g:k['components'][0].__setitem__(3, 'unknown'),
])
def test_invalid_directory_rejected(mutation):
    data = json.loads((REFERENCE_DIR/'reference.json').read_text(encoding='utf-8'))['data']
    mutation(data['kg'], data['geo'])
    with pytest.raises(ValueError): validate_supply_reference(data['kg'], data['geo'])


def test_directory_does_not_complete_procurement_evidence():
    s = scenario('C54')
    original = copy.deepcopy(s)
    data, provenance, gaps = package('C54', s, {})
    wp = data['work_package']
    assert not wp['quantitative_ready'] # Directory metrics are not project procurement quantities.
    assert all(r['status'] == 'missing' for r in wp['draft']['evidence'])
    assert wp['supply_reference']['counts']['suppliers'] == 885
    assert provenance[0]['source_type'] == 'user_supplied_contextual_snapshot'
    assert any('delivery commitments' in g for g in gaps)
    assert s == original
    s.update(site_id='SITE_02', layout_id='LAYOUT_02')
    other = package('C54', s, {})[0]['work_package']
    assert other['supply_reference'] == wp['supply_reference'] # Same contextual directory, no invented local coverage.


def test_reference_api_and_scenario_provenance(client):
    r = client.get('/api/references/lattice-supply')
    assert r.status_code == 200 and r.json()['counts']['suppliers'] == 885
    raw = client.get('/api/references/lattice-supply/original')
    assert raw.headers['content-type'] == 'application/octet-stream'
    assert hashlib.sha256(raw.content).hexdigest() == r.json()['metadata']['original_sha256']
    data = client.get('/api/references/lattice-supply/data.json')
    assert data.json()['metadata'] == r.json()['metadata']
    _, s = create(client)
    result = client.post(f'/api/scenarios/{s["id"]}/categories/C54/run')
    assert result.status_code == 200, result.text
    assert result.json()['scenario_id'] == s['id']
    assert result.json()['provenance'][0]['data_sha256'] == r.json()['metadata']['data_sha256']
