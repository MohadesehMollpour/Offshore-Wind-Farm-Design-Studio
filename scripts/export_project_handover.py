"""Export the portable handover with local links resolved for an external folder."""
import argparse
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LINK=re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    source=ROOT/'PROJECT_HANDOVER.md';output=args.output.resolve()
    if output==source.resolve():raise ValueError('Keep the canonical handover portable; choose a separate export path')
    text=source.read_text(encoding='utf-8');count=0
    def resolve_link(match):
        nonlocal count
        label,target=match.groups()
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):return match.group(0)
        relative,separator,anchor=target.partition('#');path=(source.parent/relative).resolve()
        if not path.exists():raise ValueError('Handover link target is missing: '+target)
        count+=1
        return f'[{label}](<{path.as_posix()}{separator}{anchor}>)'
    exported=LINK.sub(resolve_link,text)
    if sum(line.startswith('```') for line in text.splitlines())%2:raise ValueError('Handover has an unclosed code fence')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(exported,encoding='utf-8')
    print(f'Exported {output}; verified/resolved {count} local links; canonical source unchanged.')

if __name__=='__main__':main()
