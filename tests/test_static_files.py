import pytest
from fastapi.testclient import TestClient
import backend.app as module
from backend.app import app
from backend import store
from backend.catalog import ROOT

PUBLIC=ROOT/'dashboard/public'
EXPECTED={'robots.txt':'text/plain','favicon.svg':'image/svg+xml','site.webmanifest':'application/manifest+json'}

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'test.sqlite')
    # A throwaway dist keeps the test independent of whether the frontend has been rebuilt.
    built=tmp_path/'dist';built.mkdir()
    for name in EXPECTED:(built/name).write_bytes((PUBLIC/name).read_bytes())
    (built/'index.html').write_text('<!doctype html><title>SPA shell</title>',encoding='utf-8')
    (built/'secret.txt').write_text('not allowlisted',encoding='utf-8')
    monkeypatch.setattr(module,'dist',built)
    # No context manager: lifespan (database init and job recovery) is not needed for static files.
    yield TestClient(app)

def test_root_files_served_with_media_types(client):
    for name,media in EXPECTED.items():
        r=client.get('/'+name)
        assert r.status_code==200,(name,r.text)
        assert r.headers['content-type'].split(';')[0]==media
        assert r.headers['x-content-type-options']=='nosniff'
        assert r.content==(PUBLIC/name).read_bytes()
    assert 'charset=utf-8' in client.get('/robots.txt').headers['content-type']

def test_root_file_contents_are_crawler_safe(client):
    robots=client.get('/robots.txt').text
    assert 'User-agent: *' in robots and 'Disallow: /api/' in robots
    # No sitemap or absolute URL until a real public domain exists.
    assert not any(line.startswith('Sitemap:') for line in robots.splitlines())
    manifest=client.get('/site.webmanifest').json()
    assert manifest['name']=='Offshore Wind Farm Design Studio' and manifest['theme_color']=='#102b2b'
    # Relative to the manifest, so the same file works at / locally and under the GitHub Pages sub-path.
    assert manifest['icons'][0]['src']=='favicon.svg' and manifest['start_url']==manifest['scope']=='./'
    assert client.get('/favicon.svg').text.startswith('<svg')

def test_missing_root_file_is_404_not_html(client,tmp_path):
    (module.dist/'robots.txt').unlink()
    r=client.get('/robots.txt')
    assert r.status_code==404 and '<title>' not in r.text

def test_only_allowlisted_names_and_api_404_unchanged(client):
    if not any(getattr(route,'path','')=='/{path:path}' for route in app.routes):pytest.skip('SPA catch-all is only registered when dashboard/dist exists')
    # Other root names still get the SPA shell, never the file itself.
    r=client.get('/secret.txt')
    assert r.status_code==200 and 'SPA shell' in r.text and 'not allowlisted' not in r.text
    assert 'SPA shell' in client.get('/projects/x/overview').text
    r=client.get('/api/robots.txt')
    assert r.status_code==404 and r.json()['detail']=='Unknown API route'

def test_local_only_checks_still_apply(client):
    assert client.get('/robots.txt',headers={'host':'example.com'}).status_code==403
    assert client.get('/favicon.svg',headers={'origin':'https://example.com'}).status_code==403
