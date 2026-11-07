"""Import the reviewed Lattice attachment as inert data and an isolated local explorer.

This is a maintainer tool for this specific reference format, not a general HTML uploader.
The original is preserved; the adapted executable files must be reviewed before committing.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen
from backend.catalog import ROOT
from backend.supply_reference import validate_supply_reference


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attachment', type=Path)
    args = parser.parse_args()
    raw = args.attachment.read_bytes()
    html = raw.decode('utf-8').replace('\r\n', '\n')
    decoder = json.JSONDecoder()
    kg, _ = decoder.raw_decode(html.split('window.KG=', 1)[1])
    geo, _ = decoder.raw_decode(html.split('window.GEO=', 1)[1])
    validate_supply_reference(kg, geo)
    dest = ROOT / 'sources/references/lattice_supply'
    public = ROOT / 'dashboard/public/assets/lattice'
    dest.mkdir(parents=True, exist_ok=True); public.mkdir(parents=True, exist_ok=True)
    original_name = 'Lattice_Offshore_Wind.original.html'
    (dest / original_name).write_bytes(raw)
    data = {'kg': kg, 'geo': geo}
    data_bytes = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    meta = {'title': 'Lattice · Offshore Wind', 'author': 'Koorosh Aslansefat',
            'original_filename': original_name, 'original_sha256': hashlib.sha256(raw).hexdigest(),
            'data_sha256': hashlib.sha256(data_bytes).hexdigest(), 'snapshot_date': kg['meta']['extracted'],
            'imported_on': '2026-11-01', 'source_type': 'user_supplied_contextual_snapshot',
            'verification': 'Directory claims and capability links have not been independently reverified.',
            'scope': 'UK directory coverage; not a selected-farm supplier shortlist, quotation or delivery commitment.'}
    write_json(dest / 'reference.json', {'metadata': meta, 'data': data})
    styles = '\n'.join(re.findall(r'<style[^>]*>([\s\S]*?)</style>', html))
    # Keep the supplied seven-view renderer and its pure analytics in separately reviewable files.
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
    runtime = scripts[-1]
    if 'function exposure(' not in runtime or 'VIEW_FNS.ontology' not in runtime:
        raise ValueError('Unexpected reference renderer; review before importing')
    # Isolate pure core at its explicit export boundary (for Node regression tests).
    boundary = re.search(r'\}\)\([^\n]*\);', runtime)
    if not boundary: raise ValueError('Core export boundary not found')
    core, app = runtime[:boundary.end()], runtime[boundary.end():]
    for before, after in [
        ('explicitly tagged UK suppliers', 'explicit or declared directory suppliers'),
        ('no evidenced UK supplier', 'no supplier linked in this snapshot'),
        ('UK suppliers', 'directory suppliers'), ('UK supplier', 'directory supplier'),
        ('real suppliers', 'supplier profiles')]:
        app = app.replace(before, after)
    # Deterministic graph queries are local lookups, not an external AI service.
    app = app.replace('Questions are answered from graph facts and the core rules, with the dependency path shown. In production an LLM turns these facts into the narrative; it never invents the facts.',
                      'Questions use local graph facts and transparent rules, with the dependency path shown. Answers describe this directory snapshot and do not establish procurement commitments.')
    (public / 'core.js').write_text(core + '\n', encoding='utf-8')
    (public / 'explorer.js').write_text(app, encoding='utf-8')
    (public / 'style.css').write_text(styles + '\n/* Studio integration: the light reference palette and usable narrow layouts. */\nhtml{color-scheme:light}body{min-width:0} .rail{box-sizing:border-box} :focus-visible{outline:2px solid var(--accent);outline-offset:3px}\n', encoding='utf-8')
    # Serialization is JSON-only; no source HTML/script is evaluated during extraction.
    serialized = 'window.KG=' + json.dumps(kg, ensure_ascii=False) + ';\nwindow.GEO=' + json.dumps(geo, ensure_ascii=False) + ';\n'
    (public / 'data.js').write_text(serialized.replace('</', '<\\/'), encoding='utf-8')
    csp = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src data:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'"
    frame = f'''<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="author" content="Koorosh Aslansefat"><title>C54 · Lattice supply-chain explorer</title>
<link rel="stylesheet" href="style.css"></head><body>
<div class="app"><aside class="rail"><div class="brand">Lattice<small>Offshore Wind pack · C54</small></div>
<nav class="nav" id="nav" aria-label="Supply-chain views"></nav>
<div class="railfoot">Imported UK Offshore Wind Directory snapshot<span id="nexp"></span>.<br>
<span id="nsup"></span> supplier profiles. Capability evidence is from the attached page and has not been independently reverified.<br>Exposure scores are a transparent model, not a forecast.</div></aside>
<main id="main"></main></div><div id="tip" role="tooltip" hidden></div>
<script src="d3.min.js"></script><script src="d3-sankey.min.js"></script>
<script src="data.js"></script><script src="core.js"></script><script src="explorer.js"></script>
</body></html>'''
    (public / 'index.html').write_text(frame, encoding='utf-8')
    vendors = {
        'd3.min.js': 'https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js',
        'd3-LICENSE.txt': 'https://cdn.jsdelivr.net/npm/d3@7.9.0/LICENSE',
        'd3-sankey.min.js': 'https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js',
        'd3-sankey-LICENSE.txt': 'https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/LICENSE'}
    for filename, url in vendors.items():
        with urlopen(url, timeout=30) as response: (public / filename).write_bytes(response.read())
    write_json(dest / 'bundle_manifest.json', {
        'original_sha256': meta['original_sha256'], 'vendor_sources': vendors,
        'assets': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(public.iterdir()) if p.is_file()}})
    print(json.dumps({'imported': meta['title'], 'suppliers': len(kg['suppliers']), 'original_sha256': meta['original_sha256']}))


if __name__ == '__main__': main()
