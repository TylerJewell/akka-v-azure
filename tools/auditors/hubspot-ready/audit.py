#!/usr/bin/env python3
"""HubSpot-readiness auditor.

Encodes the hard-won lessons from porting Akka decks into the akka.io HubSpot CMS
(TYLER_HUBSPOT_GUIDE). Run over the HubSpot-bound fragments before porting/publishing so
the known theme/CSS/terminology traps are caught in the repo instead of live.

Checks (each traces to a guide section):
  - var(--...) references   -> theme-overrides.css hijacks --black/--white/etc; hardcode hex (§4)
  - Tyler's off-brand hexes -> #4A9EFF/#ff6b60/#ff8a80/#ff5a4d/#28C840 must be swapped (§5)
  - Roboto / Roboto Mono    -> only Instrument Sans; mono only for code (§6)
  - overflow-x:hidden       -> kills position:sticky; use overflow-x:clip (§18)
  - unscoped body{ / html{  -> must be scoped under the page wrapper class (§4)
  - "actor"/"actors"        -> banned in customer-facing content (§8)
  - "AKKA" all-caps         -> never render AKKA in all-caps text (§6)

Usage:
    python tools/auditors/hubspot-ready/audit.py [file ...]
    (no args -> audits the HubSpot-bound fragments globbed below)

Exit 0 = clean; non-zero = readiness issues found.
"""

import os
import re
import sys
import glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

DEFAULT_GLOBS = [
    'sales-presentation/generated/*/hubspot.html',
    'case-studies/hubspot/*.html',
    'comparisons/hubspot/*.html',
]

OFF_BRAND_HEX = re.compile(r'#(?:4A9EFF|ff6b60|ff8a80|ff5a4d|28C840)\b', re.I)
VAR_REF = re.compile(r'var\(--(?!pad-)[a-z0-9-]+\)', re.I)   # --pad-* are theme-safe
ROBOTO = re.compile(r'Roboto(?:\s+Mono)?', re.I)
OVERFLOW_HIDDEN = re.compile(r'overflow-x\s*:\s*hidden')
UNSCOPED_BODY = re.compile(r'(?<![-\w.])body\s*\{')
UNSCOPED_HTML = re.compile(r'(?<![-\w.])html\s*\{')
ACTORS = re.compile(r'\bactor model\b|\bactors?\b(?!\s*&)', re.I)
AKKA_CAPS = re.compile(r'\bAKKA\b')

STYLE_BLOCK = re.compile(r'<style[^>]*>.*?</style>', re.S | re.I)
SCRIPT_BLOCK = re.compile(r'<script[^>]*>.*?</script>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')

# WARN: handled by the port-time transforms (VAR_REPLACEMENTS, color/font swaps, scope_css).
# Flagged as reminders so an as-is port doesn't slip through, but they don't fail the build.
WARN_CSS = [
    (VAR_REF, 'var(--) reference — theme-overrides.css hijacks these; the port hardcodes the hex (guide §4)'),
    (OFF_BRAND_HEX, 'off-brand color — the port swaps to the Akka palette (guide §5 replacement table)'),
    (ROBOTO, 'Roboto/Roboto Mono — the port swaps to Instrument Sans (guide §6)'),
    (UNSCOPED_BODY, 'unscoped "body {" — the port scopes it under the wrapper class (guide §4)'),
    (UNSCOPED_HTML, 'unscoped "html {" — the port scopes it under the wrapper class (guide §4)'),
]
# FAIL: content-level issues the port will NOT fix for you.
FAIL_CSS = [
    (OVERFLOW_HIDDEN, 'overflow-x:hidden — kills position:sticky; use overflow-x:clip (guide §18)'),
]


def line_of(raw, idx):
    return raw.count('\n', 0, idx) + 1


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    rel = os.path.relpath(path, ROOT)
    warnings, fails = [], []

    def scan(rules, bucket):
        for rx, msg in rules:
            seen = set()
            for m in rx.finditer(raw):
                key = m.group(0).lower()
                if key in seen:
                    continue
                seen.add(key)
                bucket.append(f'{rel}:{line_of(raw, m.start())}: {msg}  [{m.group(0)}]')

    scan(WARN_CSS, warnings)
    scan(FAIL_CSS, fails)

    # caps against visible text only — the port won't fix these.
    # ("actor"/"actors" is intentionally allowed — Tyler override 2026-07-25.)
    text = TAG.sub(' ', SCRIPT_BLOCK.sub(' ', STYLE_BLOCK.sub(' ', raw)))
    for m in AKKA_CAPS.finditer(text):
        before = text[max(0, m.start()-30):m.start()]
        after = text[m.end():m.end()+30]
        prev = re.search(r'([A-Za-z]{2,})\s*$', before)
        nxt = re.search(r'^\s*([A-Za-z]{2,})', after)
        if (prev and prev.group(1).isupper()) or (nxt and nxt.group(1).isupper()):
            continue  # all-caps header run — allowed
        fails.append(f'{rel}: "AKKA" all-caps in mixed-case text — use "Akka" / SVG logo (guide §6)')

    return warnings, fails


def main():
    args = sys.argv[1:]
    if args:
        files = [f for f in args if os.path.isfile(f)]
    else:
        files = []
        for g in DEFAULT_GLOBS:
            files += glob.glob(os.path.join(ROOT, g))
        files = sorted(set(files))

    all_warnings, all_fails = [], []
    for f in files:
        w, fl = audit_file(f)
        all_warnings += w
        all_fails += fl

    print('HubSpot-readiness audit')
    print(f'  files scanned: {len(files)}')
    print()
    if not files:
        print('No HubSpot fragments found to scan (build the decks first, or pass files).')
        return 0

    if all_warnings:
        # summarize port-time transforms by category rather than listing every hit
        cats = {}
        for w in all_warnings:
            key = w.split(': ', 1)[1].split(' — ')[0]
            cats[key] = cats.get(key, 0) + 1
        print('PORT-TIME REMINDERS (auto-handled by the publish transforms — informational):')
        for k, n in sorted(cats.items(), key=lambda kv: -kv[1]):
            print(f'  · {n:4}×  {k}')
        print()

    if all_fails:
        print(f'FAILED — {len(all_fails)} content issue(s) the port will NOT fix:\n')
        for i, p in enumerate(all_fails, 1):
            print(f'{i:3}. {p}')
        return 1
    print('VERIFIED — no content-level HubSpot traps (only auto-handled reminders above).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
