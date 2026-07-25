#!/usr/bin/env python3
"""Marketing brand / voice / terminology auditor.

Encodes the rules from the marketing team's context (brand voice, terminology, and the
approved color palette) into a pre-publish check. Run over customer-facing HTML before
committing/publishing.

Usage:
    python tools/auditors/marketing-brand/audit.py [file ...]
    (no args  ->  audits the default publishable set below)

Exit 0 = clean; non-zero = brand violations found (printed). Color findings are reported
as warnings (they don't fail the build) since the decks carry many structural greys.
"""

import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

DEFAULT_FILES = [
    'akka-overview/index.html',
    'akka-verify/index.html',
    'index.html',
]

# ---- approved brand palette (marketing context + HubSpot guide), lowercased ----
PALETTE = {
    '#000000', '#000', '#141414', '#f1f1f1', '#ffce4a', '#00dbdd', '#ff5400',
    '#72d35b', '#a6a6a6', '#4e4e4e', '#111', '#222', '#fff', '#ffffff',
    '#9a9aa2', '#c9c9ce', '#d8d8dc', '#e9b426', '#f5c518',
}

# ---- hard rules: (regex, message). Case-sensitive where it matters. ----
# Note: "actor"/"actors" is intentionally allowed (Tyler override 2026-07-25) — Akka's actor
# heritage is a legitimate technical term in our content.
HARD_RULES = [
    (re.compile(r'\bLightbend\b'),
     'Never use "Lightbend" in marketing content (legal entity name only).'),
    (re.compile(r'\bautonomous AI\b', re.I),
     'Use "agentic AI", not "autonomous AI", for the platform.'),
]

AKKA_CAPS = re.compile(r'\bAKKA\b')


def akka_caps_violations(text, rel):
    """Flag "AKKA" only in mixed-case prose — an all-caps header run (e.g. an eyebrow like
    "AKKA ACCESS SURFACES") is allowed; "AKKA" uppercased alone inside normal text is not."""
    out = []
    for m in AKKA_CAPS.finditer(text):
        before = text[max(0, m.start()-30):m.start()]
        after = text[m.end():m.end()+30]
        prev = re.search(r'([A-Za-z]{2,})\s*$', before)
        nxt = re.search(r'^\s*([A-Za-z]{2,})', after)
        run = (prev and prev.group(1).isupper()) or (nxt and nxt.group(1).isupper())
        if run:
            continue  # part of an all-caps header — allowed
        snip = re.sub(r'\s+', ' ', text[max(0, m.start()-32):m.end()+32].strip())
        out.append(f'{rel}: "AKKA" all-caps in mixed-case text — use "Akka" (all-caps is only for '
                   f'headers where the whole label is uppercase, or the SVG logo).\n      … {snip} …')
    return out

# ---- softer voice smells: superlatives / hype (warnings) ----
HYPE = re.compile(r'\b(revolutionary|cutting-edge|world-class|best-in-class|game-chang\w*|'
                  r'unparalleled|blazing(?:-fast)?|the best|most innovative|next-generation|'
                  r'bleeding-edge|magical?)\b', re.I)

TAG = re.compile(r'<[^>]+>')
STYLE_BLOCK = re.compile(r'<style[^>]*>.*?</style>', re.S | re.I)
SCRIPT_BLOCK = re.compile(r'<script[^>]*>.*?</script>', re.S | re.I)
HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b')


def visible_text(html):
    """Strip <style>, <script>, and tags to approximate reader-visible copy."""
    h = STYLE_BLOCK.sub(' ', html)
    h = SCRIPT_BLOCK.sub(' ', h)
    h = TAG.sub(' ', h)
    return h


def audit_file(path):
    problems, warnings = [], []
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    text = visible_text(raw)
    rel = os.path.relpath(path, ROOT)

    for rx, msg in HARD_RULES:
        for m in rx.finditer(text):
            snippet = text[max(0, m.start()-32):m.end()+32].strip()
            snippet = re.sub(r'\s+', ' ', snippet)
            problems.append(f'{rel}: {msg}\n      … {snippet} …')

    problems += akka_caps_violations(text, rel)

    for m in HYPE.finditer(text):
        snippet = re.sub(r'\s+', ' ', text[max(0, m.start()-32):m.end()+32].strip())
        warnings.append(f'{rel}: hype/superlative "{m.group(0)}" — brand voice is declarative, not persuasive.\n      … {snippet} …')

    # color palette — off-palette hex colors (warning only; decks carry structural greys)
    off = {}
    for m in HEX.finditer(raw):
        c = m.group(0).lower()
        if c not in PALETTE:
            off[c] = off.get(c, 0) + 1
    if off:
        listed = ', '.join(f'{c}×{n}' for c, n in sorted(off.items(), key=lambda kv: -kv[1])[:20])
        warnings.append(f'{rel}: {len(off)} off-palette color(s) — {listed}')

    return problems, warnings


def main():
    args = sys.argv[1:]
    files = args if args else [os.path.join(ROOT, f) for f in DEFAULT_FILES]
    files = [f for f in files if os.path.isfile(f)]

    all_problems, all_warnings = [], []
    for f in files:
        p, w = audit_file(f)
        all_problems += p
        all_warnings += w

    print('Marketing brand audit')
    print('  files: ' + ', '.join(os.path.relpath(f, ROOT) for f in files))
    print()
    if all_warnings:
        print('WARNINGS (voice / color — review, non-blocking):')
        for i, w in enumerate(all_warnings, 1):
            print(f'  {i:2}. {w}')
        print()
    if all_problems:
        print(f'FAILED — {len(all_problems)} brand violation(s):\n')
        for i, p in enumerate(all_problems, 1):
            print(f'{i:2}. {p}')
        return 1
    print('VERIFIED — no hard brand violations.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
