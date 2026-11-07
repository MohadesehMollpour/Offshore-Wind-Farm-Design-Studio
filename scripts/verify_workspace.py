from pathlib import Path
import hashlib,json
from backend.catalog import ROOT,CATEGORIES,load

required=['SYSTEM_PROMPT.md','SPECIFICATION.md','README.md','AGENT_MAPPING.yaml','INPUT_SCHEMA.json','OUTPUT_SCHEMA.json','CHARTS.yaml','DATA_SOURCES.md','CHANGELOG.md','src/controller.py','tests/test_contract.py','examples/missing_data.json','outputs/.gitkeep']
assert len(CATEGORIES)==70
assert {c['id'] for c in CATEGORIES}=={f'C{i:02}' for i in range(1,71)}
for c in CATEGORIES:
    for f in required:assert (ROOT/'categories'/c['id']/f).is_file(),(c['id'],f)
    for f in ['INPUT_SCHEMA.json','OUTPUT_SCHEMA.json','CHARTS.yaml']:json.loads((ROOT/'categories'/c['id']/f).read_text(encoding='utf-8'))
assert len(load('agents'))==22 and len(load('sites'))==len(load('layouts'))==5
assert len(load('assessment')['topics'])==16
assert [r['weight'] for r in load('assessment')['rubric']]==[40,20,20,20]
# Course materials are kept out of the public repository; check their checksums wherever they are present.
present=[s for s in json.loads((ROOT/'sources/manifest.json').read_text(encoding='utf-8')) if (ROOT/s['relative_path']).is_file()]
for source in present:
    assert hashlib.sha256((ROOT/source['relative_path']).read_bytes()).hexdigest()==source['sha256']
print(f'Verified the file structure of 70 category packages (not engineering completion), 22 agent profiles, 5×5 presets, 16 assessment mappings and {len(present)} unchanged source checksums'+('.' if present else ' (course materials are not in this checkout).'))
