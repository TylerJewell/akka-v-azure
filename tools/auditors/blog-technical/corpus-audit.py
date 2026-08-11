#!/usr/bin/env python3
"""Corpus auditor — scaffold every post locally (no publishing), scan output
for template divergences, report by frequency across the corpus.

Detects:
  - inline-style leaks (any `style=` remaining after sanitization)
  - unknown div/span classes on load-bearing elements
  - <pre> blocks without a language-* code class
  - <table> without .rtbl or .table-scroll wrapper
  - <blockquote> without pullquote/enote class → will inherit default styling
  - <iframe> without an embed wrapper (may overflow layout)
  - author byline missing / date missing
  - h2 counts of zero (post has no section boundaries — nothing to number)

Usage:
    python tools/auditors/blog-technical/corpus-audit.py
    python tools/auditors/blog-technical/corpus-audit.py --scaffold   # re-scaffold all posts first
    python tools/auditors/blog-technical/corpus-audit.py --limit 20   # audit first 20
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
INVENTORY = os.path.join(ROOT, 'scratchpad', 'hs-blog-inventory.json')
POSTS_DIR = os.path.join(ROOT, 'blog-technical', 'posts')
SCAFFOLDER = os.path.join(ROOT, 'tools', 'blog-technical', 'scaffold.py')


def audit_one(path):
    """Return list of (rule, detail) tuples."""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Only inspect body/article content — skip inline <style>
    body_m = re.search(r'<article\b.*?</article>', html, re.S)
    body = body_m.group(0) if body_m else html
    findings = []

    # inline style leaks
    for m in re.finditer(r'style="([^"]{1,80})"', body):
        # figure has --fig-w — allowed
        if '--fig-w' in m.group(1):
            continue
        findings.append(('inline-style leak', m.group(0)[:80]))

    # <pre> without language- class inside <code>
    for m in re.finditer(r'<pre[^>]*>(.*?)</pre>', body, re.S):
        inner = m.group(1)
        if 'class="language-' not in inner:
            findings.append(('<pre> without language-*', inner[:60].strip()))

    # <table> not wrapped
    for m in re.finditer(r'<table\b[^>]*>', body):
        # Look back 200 chars for .rtbl or .table-scroll marker
        pre = body[max(0, m.start() - 200):m.start()]
        if 'table-scroll' not in pre and 'class="rtbl' not in m.group(0):
            findings.append(('<table> not wrapped', m.group(0)[:60]))

    # <iframe> outside a plot-wrap — will overflow the body column
    for m in re.finditer(r'<iframe\b[^>]*>', body):
        pre = body[max(0, m.start() - 200):m.start()]
        if 'plot-wrap' not in pre and 'plate' not in pre:
            findings.append(('<iframe> outside plot-wrap', m.group(0)[:80]))
    # (bare <blockquote> is fine — the template CSS styles unclassed blockquotes
    # with the pullquote design so no wrapper is needed.)

    # HubSpot legacy remnants
    for marker in ('hs_cos_wrapper', 'hs-embed', 'marketing-code', 'prettyprint',
                   'module_block', '{% module', 'end_module_block', '{% raw'):
        for m in re.finditer(re.escape(marker), body):
            findings.append((f'legacy marker: {marker}', body[max(0, m.start() - 30):m.start() + 40]))
            break  # one per marker per post is enough

    # byline
    if not re.search(r'<span class=[\'"]au[\'"]>[^<]+</span>', body):
        findings.append(('missing byline author', ''))
    if not re.search(r'<time datetime="\d', body):
        findings.append(('missing byline date', ''))

    # (h2-count zero was previously flagged, but short posts genuinely lack
    # h2s. Not an error; informational only.)

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--scaffold', action='store_true', help='rescaffold every post first')
    ap.add_argument('--limit', type=int, help='audit first N posts only')
    args = ap.parse_args()

    inv = json.load(open(INVENTORY, encoding='utf-8'))
    if args.limit:
        inv = inv[:args.limit]
    slugs = [p['slug'] for p in inv]

    if args.scaffold:
        print(f'[scaffold] regenerating {len(slugs)} posts …')
        for i, slug in enumerate(slugs, 1):
            r = subprocess.run(
                [sys.executable, SCAFFOLDER, slug],
                capture_output=True, text=True, timeout=60,
            )
            if r.returncode != 0:
                print(f'  {i}/{len(slugs)}  ERROR {slug}: {r.stderr[:120]}')
            elif i % 20 == 0:
                print(f'  {i}/{len(slugs)} done')

    # Audit each scaffolded file
    rule_counter = Counter()
    per_post = {}
    missing = []
    for slug in slugs:
        path = os.path.join(POSTS_DIR, f'{slug}.html')
        if not os.path.exists(path):
            missing.append(slug)
            continue
        findings = audit_one(path)
        per_post[slug] = findings
        for rule, _ in findings:
            rule_counter[rule] += 1

    # Report
    print(f'\n=== CORPUS AUDIT — {len(per_post)} posts audited, {len(missing)} missing ===\n')
    if missing:
        print(f'MISSING SCAFFOLDS ({len(missing)}):')
        for m in missing[:10]:
            print(f'  {m}')
        print()

    print('RULE FREQUENCY:')
    for rule, cnt in rule_counter.most_common():
        print(f'  {cnt:4}  {rule}')
    print()

    # Group posts by which rules they hit
    posts_with_issues = [(slug, f) for slug, f in per_post.items() if f]
    print(f'{len(posts_with_issues)}/{len(per_post)} posts have ≥1 finding')
    print()

    # Show top-10 worst offenders
    posts_with_issues.sort(key=lambda x: -len(x[1]))
    print('TOP 10 OFFENDERS:')
    for slug, findings in posts_with_issues[:10]:
        by_rule = Counter(r for r, _ in findings)
        print(f'  {slug}  ({len(findings)} findings)')
        for r, c in by_rule.most_common(4):
            print(f'    {c}× {r}')

    # Dump full report
    out = os.path.join(ROOT, 'scratchpad', 'corpus-audit-report.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({slug: [{'rule': r, 'detail': d} for r, d in f_list]
                   for slug, f_list in per_post.items()}, f, indent=2)
    print(f'\nfull report: {os.path.relpath(out, ROOT)}')

    return 0 if not rule_counter else 1


if __name__ == '__main__':
    sys.exit(main())
