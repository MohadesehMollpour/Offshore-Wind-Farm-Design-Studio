"""Review regressions: optional render-cache loss must not hide valid sources."""
import copy
import hashlib
import json
from types import SimpleNamespace

import pytest

from backend import environment, ingestion
from backend.engine import digest
from backend.providers import ProviderError
from tests.test_ingestion import client


@pytest.fixture
def terrain_data(tmp_path, monkeypatch):
    monkeypatch.setattr(environment, 'ROOT', tmp_path)
    terrain = {
        'width': 3, 'height': 3, 'datum': 'Lowest Astronomical Tide (LAT)',
        'longitude': [1.8, 1.9, 2.0], 'latitude': [54.0, 53.9, 53.8],
        'elevation_m': [[-10, -20, None], [-20, -30, -40], [-30, -40, -50]],
    }
    return {
        'terrain': terrain, 'terrain_sha256': digest(terrain),
        'reference_point': {'lat': 53.9, 'lon': 1.9},
        'geojson': {'type': 'FeatureCollection', 'features': []},
        'limitations': [],
    }


def write_cache(data):
    directory = environment.relief_directory(data)
    directory.mkdir(parents=True, exist_ok=True)
    products = {
        'terrain-relief.png': b'fixture texture',
        'terrain-relief-preview.png': b'fixture preview',
        'terrain-relief.metadata.json': json.dumps({
            'width': 3, 'height': 3, 'datum': data['terrain']['datum'],
        }).encode(),
    }
    for name, content in products.items():
        (directory / name).write_bytes(content)
    manifest = {
        'terrain_sha256': data['terrain_sha256'], 'renderer': 'rayshader',
        'rayshader_version': 'test', 'r_version': 'test',
        'shading_exaggeration': 8, 'datum': data['terrain']['datum'],
        'nodata_policy': 'Missing nodes omitted',
        'files': {name: hashlib.sha256(content).hexdigest() for name, content in products.items()},
    }
    (directory / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return directory, manifest


@pytest.mark.parametrize('damage', [
    'missing_texture', 'corrupt_texture', 'invalid_json', 'empty_files',
    'missing_metadata_entry', 'wrong_terrain', 'bad_checksum', 'bad_grid_metadata',
])
def test_bad_derivative_cache_is_unavailable_not_source_failure(terrain_data, damage):
    directory, manifest = write_cache(terrain_data)
    if damage == 'missing_texture':
        (directory / 'terrain-relief.png').unlink()
    elif damage == 'corrupt_texture':
        (directory / 'terrain-relief.png').write_bytes(b'changed')
    elif damage == 'invalid_json':
        (directory / 'manifest.json').write_text('{', encoding='utf-8')
    elif damage == 'empty_files':
        manifest['files'] = {}
    elif damage == 'missing_metadata_entry':
        del manifest['files']['terrain-relief.metadata.json']
    elif damage == 'wrong_terrain':
        manifest['terrain_sha256'] = '0' * 64
    elif damage == 'bad_checksum':
        manifest['files']['terrain-relief.png'] = None
    elif damage == 'bad_grid_metadata':
        content = json.dumps({'width': 9, 'height': 9, 'datum': 'wrong'}).encode()
        (directory / 'terrain-relief.metadata.json').write_bytes(content)
        manifest['files']['terrain-relief.metadata.json'] = hashlib.sha256(content).hexdigest()
    if damage != 'invalid_json':
        (directory / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    original = copy.deepcopy(terrain_data)
    status = environment.relief_status(terrain_data, 'test-dataset')
    assert status['available'] is False and status['warning']
    assert 'source elevation grid' in status['note']
    assert 'texture_url' not in status
    assert terrain_data == original


@pytest.mark.parametrize('function', [environment.relief_status, environment.build_relief])
def test_changed_source_terrain_still_fails_integrity(terrain_data, function):
    write_cache(terrain_data)
    terrain_data['terrain']['elevation_m'][0][0] = 123
    with pytest.raises(ProviderError, match='terrain checksum'):
        function(terrain_data)


def test_missing_derivative_returns_404_without_hiding_source_dataset(client, terrain_data, monkeypatch):
    directory, _ = write_cache(terrain_data)
    (directory / 'terrain-relief-preview.png').unlink()
    dataset = {'provider_id': 'environment_screening', 'data': terrain_data, 'meta': {}}
    monkeypatch.setattr(ingestion, 'get_dataset', lambda did: dataset)
    response = client.get('/api/datasets/example/environment-relief/terrain-relief.png')
    assert response.status_code == 404
    response = client.get('/api/datasets/example')
    assert response.status_code == 200
    assert response.json()['data']['terrain'] == terrain_data['terrain']


def test_build_retries_incomplete_cache_and_publishes_complete_manifest(terrain_data, monkeypatch):
    directory, _ = write_cache(terrain_data)
    (directory / 'terrain-relief.png').unlink()
    runtime = environment.ROOT / 'work/rayshader/runtime/app/bin/x64/Rscript.exe'
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(b'test stub; never executed')
    calls = []

    def render(*args, **kwargs):
        calls.append(args)
        (directory / 'terrain-relief.png').write_bytes(b'regenerated texture')
        metadata = {
            'input_md5': hashlib.md5((directory / 'input.json').read_bytes()).hexdigest(),
            'width': 3, 'height': 3, 'datum': terrain_data['terrain']['datum'],
            'rayshader_version': 'test', 'r_version': 'test',
            'vertical_exaggeration': 8, 'nodata_policy': 'Missing nodes omitted',
        }
        (directory / 'terrain-relief.metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        return SimpleNamespace(returncode=0, stderr='')

    monkeypatch.setattr('subprocess.run', render)
    status = environment.build_relief(terrain_data)
    assert len(calls) == 1 and status['available'] is True
    assert len(status['files']) == 3 and not (directory / 'manifest.pending.json').exists()
    assert environment.relief_status(terrain_data)['available'] is True

