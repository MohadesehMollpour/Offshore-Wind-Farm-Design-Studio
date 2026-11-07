"""A public clone omits the private course materials; the app must say so instead of failing."""
import json
from fastapi.testclient import TestClient
import backend.app as module
from backend import store
from backend.app import app

def test_missing_course_material_is_a_clear_404(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'test.sqlite');monkeypatch.setattr(module,'ROOT',tmp_path)
    (tmp_path/'sources').mkdir()
    (tmp_path/'sources/manifest.json').write_text(json.dumps([{'id':'provided-1','relative_path':'sources/provided/brief.pdf','filename':'brief.pdf','sha256':'0'*64}]),encoding='utf-8')
    with TestClient(app,raise_server_exceptions=False) as c:r=c.get('/api/sources/provided-1')
    assert r.status_code==404 and 'kept private' in r.json()['detail']
