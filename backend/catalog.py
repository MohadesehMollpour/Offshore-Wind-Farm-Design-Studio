from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT/'config'/f'{name}.json').read_text(encoding='utf-8'))
CATEGORIES=load('categories')
BY_ID={c['id']:c for c in CATEGORIES}
