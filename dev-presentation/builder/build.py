#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'builder'
SHELL = ROOT / 'shell'
GEN = ROOT / 'generated'

parser = argparse.ArgumentParser(description='Build dev presentation')
parser.add_argument('--mode', default='overview', choices=['overview', 'shareable'])
parser.add_argument('--out', default=None)
args = parser.parse_args()

out_path = Path(args.out) if args.out else GEN / args.mode / 'index.html'
registry = json.loads((BASE / 'slide-registry.json').read_text(encoding='utf-8'))
shell = (SHELL / 'shell.html').read_text(encoding='utf-8')
shared_css = (SHELL / 'shared.css').read_text(encoding='utf-8')
nav_js = (SHELL / 'nav.js').read_text(encoding='utf-8')
kiosk_js = (SHELL / 'kiosk.js').read_text(encoding='utf-8')

css_parts = []
html_parts = []
js_parts = []
for entry in registry['slides']:
    slide_dir = ROOT / entry['folder']
    meta = json.loads((slide_dir / 'meta.json').read_text(encoding='utf-8'))
    if args.mode not in meta.get('include_in', ['overview']):
        continue
    css_parts.append('/* ' + entry['id'] + ' */\n' + (slide_dir / 'slide.css').read_text(encoding='utf-8'))
    html_parts.append((slide_dir / 'slide.html').read_text(encoding='utf-8'))
    js = (slide_dir / 'slide.js').read_text(encoding='utf-8')
    if js.strip():
        js_parts.append('/* ' + entry['id'] + ' */\n' + js)

result = shell.replace('{{SHARED_CSS}}', shared_css)
result = result.replace('{{SLIDES_CSS}}', '\n\n'.join(css_parts))
result = result.replace('{{SLIDES_HTML}}', '\n\n'.join(html_parts))
result = result.replace('{{SLIDES_JS}}', '\n\n'.join(js_parts))
result = result.replace('{{NAV_JS}}', nav_js)
result = result.replace('{{KIOSK_JS}}', kiosk_js)

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(result, encoding='utf-8', newline='\n')

assets = ROOT / 'assets'
if assets.exists():
    for name in ['images', 'logos']:
        src = assets / name
        dst = out_path.parent / name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

print(f'Output: {out_path}')
print(f'Size:   {out_path.stat().st_size // 1024} KB')
