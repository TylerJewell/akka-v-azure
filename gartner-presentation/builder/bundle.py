#!/usr/bin/env python3
"""
Bundle a built presentation into a single self-contained HTML file with every
local image (img src + CSS url()) inlined as a base64 data URI.

Usage:
  python3 builder/bundle.py                 # bundles generated/overview/index.html
  python3 builder/bundle.py --in <html> --out <html>

Output (default): generated/akka-gartner-deck.html
Fonts still load from Google Fonts (CDN); everything else is embedded.
"""

import os, re, sys, base64, argparse

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
GEN  = os.path.join(ROOT, 'generated')

MIME = {
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
}

parser = argparse.ArgumentParser(description='Inline images into one HTML file')
parser.add_argument('--in',  dest='inp', default=os.path.join(GEN, 'overview', 'index.html'))
parser.add_argument('--out', dest='out', default=os.path.join(GEN, 'akka-gartner-deck.html'))
args = parser.parse_args()

src_dir = os.path.dirname(args.inp)
with open(args.inp, 'r', encoding='utf-8') as f:
    html = f.read()

cache = {}
stats = {'inlined': 0, 'missing': 0, 'bytes': 0}

def data_uri(path):
    if path in cache:
        return cache[path]
    full = os.path.normpath(os.path.join(src_dir, path))
    if not os.path.isfile(full):
        stats['missing'] += 1
        print(f'  WARNING: missing {path}')
        cache[path] = None
        return None
    ext = os.path.splitext(full)[1].lower()
    mime = MIME.get(ext, 'application/octet-stream')
    with open(full, 'rb') as fh:
        raw = fh.read()
    uri = f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')
    stats['inlined'] += 1
    stats['bytes'] += len(raw)
    cache[path] = uri
    return uri

def is_local(ref):
    ref = ref.strip().strip('\'"')
    if not ref:
        return False
    return not re.match(r'^(https?:|data:|mailto:|#|//)', ref, re.I)

# 1) src="..." / href="..." for local image-like files
def repl_attr(m):
    attr, quote, ref = m.group('attr'), m.group('q'), m.group('ref')
    if not is_local(ref):
        return m.group(0)
    ext = os.path.splitext(ref.split('?')[0])[1].lower()
    if ext not in MIME:
        return m.group(0)
    uri = data_uri(ref.split('?')[0])
    if not uri:
        return m.group(0)
    return f'{attr}={quote}{uri}{quote}'

html = re.sub(
    r'(?P<attr>\bsrc|\bhref)=(?P<q>["\'])(?P<ref>[^"\']+)(?P=q)',
    repl_attr, html)

# 2) CSS url(...) references
def repl_url(m):
    ref = m.group('ref').strip().strip('\'"')
    if not is_local(ref):
        return m.group(0)
    ext = os.path.splitext(ref.split('?')[0])[1].lower()
    if ext not in MIME:
        return m.group(0)
    uri = data_uri(ref.split('?')[0])
    if not uri:
        return m.group(0)
    return f"url('{uri}')"

html = re.sub(r'url\(\s*(?P<ref>[^)]+?)\s*\)', repl_url, html)

os.makedirs(os.path.dirname(args.out), exist_ok=True)
with open(args.out, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(args.out) / (1024 * 1024)
print(f'Inlined:  {stats["inlined"]} images ({stats["bytes"]//1024} KB raw)')
if stats['missing']:
    print(f'Missing:  {stats["missing"]} (left as-is)')
print(f'Output:   {args.out}  ({size_mb:.1f} MB)')
