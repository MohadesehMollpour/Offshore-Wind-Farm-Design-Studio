"""Read-only checks for maintained project Markdown, local links and package coverage."""
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')


def documentation_files():
    return sorted([ROOT/'README.md', ROOT/'PROJECT_HANDOVER.md',
                   *[p for folder in ['docs', 'reports', 'categories', 'agents']
                     for p in (ROOT/folder).rglob('*.md')]])


def check():
    errors = []; links = 0
    for path in documentation_files():
        if not path.is_file(): errors.append(f'Missing document: {path.relative_to(ROOT)}'); continue
        source = path.read_text(encoding='utf-8')
        in_fence = None; visible = []
        for line in source.splitlines():
            match = FENCE.match(line)
            if match:
                fence = match[1]
                if in_fence is None: in_fence = fence
                elif fence[0] == in_fence[0] and len(fence) >= len(in_fence): in_fence = None
                continue
            if in_fence is None: visible.append(line)
        if in_fence: errors.append(f'Unclosed code fence: {path.relative_to(ROOT)}')
        for match in LINK.finditer('\n'.join(visible)):
            target = match[1].strip()
            if target.startswith('<'): target = target[1:-1]
            else: target = target.split(' "', 1)[0]
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'): continue
            relative = unquote(target.split('#', 1)[0])
            if not relative: continue
            resolved = (path.parent/relative).resolve()
            if not resolved.exists(): errors.append(f'{path.relative_to(ROOT)}: missing link {target}')
            links += 1
    from backend.catalog import CATEGORIES, load
    if len(CATEGORIES) != 70 or len(load('agents')) != 22: errors.append('Unexpected category/profile count')
    register = (ROOT/'docs/CATEGORIES.md').read_text(encoding='utf-8')
    for c in CATEGORIES:
        base = ROOT/'categories'/c['id']
        if f'[{c["id"]} — ' not in register: errors.append('Missing category-register row: '+c['id'])
        for name in ['README.md', 'DATA_SOURCES.md', 'SPECIFICATION.md', 'SYSTEM_PROMPT.md', 'CHANGELOG.md']:
            if not (base/name).is_file(): errors.append(f'Missing {c["id"]}/{name}')
    if errors: raise ValueError('\n'.join(errors))
    return {'markdown_files': len(documentation_files()), 'local_links': links,
            'category_packages': len(CATEGORIES), 'agent_profiles': len(load('agents')),
            'scope': 'Maintained Markdown only; preserved source originals and external URLs are not rewritten or fetched.'}


if __name__ == '__main__':
    import json
    print(json.dumps(check(), indent=2))
