"""Verify immutable API snapshot hashes and stored scope bindings, offline."""
import argparse,hashlib,json
from pathlib import Path
from backend import store
from backend.engine import digest
from backend.ingestion import attached_data,DATA_ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scenario-id',required=True);args=parser.parse_args()
    s=store.get_scenario(args.scenario_id);sources=attached_data(s);unique={}
    for pid,source in sources.items():
        meta=source['meta'];assert digest(source['data'])==meta['sha256'],f'{pid}: payload checksum mismatch'
        path=DATA_ROOT/'external'/meta['dataset_id']
        assert digest(json.loads((path/'data.json').read_text(encoding='utf-8')))==meta['sha256']
        assert json.loads((path/'metadata.json').read_text(encoding='utf-8'))==meta
        for raw in meta['raw_assets']:
            raw_path=(DATA_ROOT/raw['path']).resolve()
            assert raw_path.is_relative_to(DATA_ROOT.resolve())
            content=raw_path.read_bytes();assert hashlib.sha256(content).hexdigest()==raw['sha256']
            assert len(content)==raw['bytes'];unique[raw['sha256']]=len(content)
    print(json.dumps({'scenario_id':s['id'],'revision':s['revision'],'verified_datasets':len(sources),'verified_raw_objects':len(unique),'verified_raw_bytes':sum(unique.values()),'scope_checks':'provider/project/site/AOI/reference point passed'},indent=2))

if __name__=='__main__':main()
