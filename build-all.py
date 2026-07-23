#!/usr/bin/env python3
"""
Build every sales deliverable in BOTH forms:

  * GitHub Pages page  — the standalone HTML we host ourselves
  * HubSpot fragment   — a paste-ready import for Darin (see
                         sales-presentation/builder/hubspot.py)

Covers the three sales presentations (overview, specify, token-shredder), the
customer case studies, and the competitor comparisons. Run automatically by
.githooks/pre-commit on every commit, or by hand:

    python build-all.py
"""

import os, sys, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'sales-presentation', 'builder'))
from hubspot import to_hubspot_fragment


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# ── 1. Sales presentations ───────────────────────────────────────────────────
# build.py writes generated/<deck>/index.html AND generated/<deck>/hubspot.html.
SP = os.path.join(ROOT, 'sales-presentation')
DECKS = [
    [],  # overview — defaults
    ['--registry', 'specify-registry.json', '--nav', 'nav-specify.js',
     '--out', 'generated/specify/index.html'],
    ['--registry', 'token-shredder-registry.json', '--nav', 'nav-shredder.js',
     '--out', 'generated/token-shredder/index.html'],
]
for extra in DECKS:
    subprocess.run([sys.executable, 'builder/build.py', '--no-zip', *extra],
                   cwd=SP, check=True)


# ── 2. Static HTML pages (case studies, comparisons) ─────────────────────────
# These are hand-authored full documents; mirror each into a hubspot/ subfolder.
def transform_dir(rel_dir, image_base=None):
    src = os.path.join(ROOT, rel_dir)
    out = os.path.join(src, 'hubspot')
    count = 0
    for name in sorted(os.listdir(src)):
        if not name.endswith('.html') or name == 'index.html':
            continue  # gallery index is GitHub Pages only (relative inter-page links)
        frag = to_hubspot_fragment(
            read(os.path.join(src, name)), base_dir=src,
            image_base=image_base, label=os.path.splitext(name)[0])
        write(os.path.join(out, name), frag)
        count += 1
    print(f'{rel_dir}: {count} HubSpot fragments -> {rel_dir}/hubspot/')


transform_dir('case-studies')   # no images; external case-study.css gets inlined
transform_dir('comparisons')    # no images; CSS already inline

print('\nAll deliverables built (GitHub Pages + HubSpot).')
