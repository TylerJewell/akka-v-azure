#!/usr/bin/env python3
"""Template-completeness auditor for the blog-technical template.

Compares a blog HTML file against the structural contract the approved
template establishes. Reports every element the post is missing or
malformed. Exit code 1 if any required element is missing.

Contract checked:
  HERO
    - kicker present (small-caps accent label at top)
    - h1.title present
    - p.standfirst present, non-empty
    - byline row with author name AND formatted date

  BODY STRUCTURE
    - first paragraph has class="lede" (drop cap trigger)
    - every h2 begins with "Section" (numbered)
    - every h2 has a following h3 subhead

  FIGURES
    - every figure.viz has:
        p.viz-title (Figure N kicker)
        h4 (figure title)
        div.plate or div.plate--paper or div.plate--flush
        figcaption
    - figure.viz has --fig-w set on the figure element

  TABLES
    - every table has class="rtbl"
    - every table has <caption>
    - every table has <tfoot> with a Note.— line

  CODE
    - every <pre> block contains <code class="language-*">

  BREAKOUTS
    - at least one pullquote in posts > 2000 words
    - at least one enote in posts > 2000 words

Usage:
    python tools/auditors/blog-technical/template-audit.py <file.html> ...
    python tools/auditors/blog-technical/template-audit.py --compare-to approved.html scaffold.html
"""

import argparse
import re
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def _wc(html):
    """Rough word count of visible body prose."""
    body_m = re.search(r'<div class="body col">(.*?)</article>', html, re.S)
    body = body_m.group(1) if body_m else html
    text = re.sub(r'<[^>]+>', ' ', body)
    return len(re.findall(r'\S+', text))


def audit_hero(html, hits):
    if not re.search(r'class="kicker"', html):
        hits.append(('HERO', 'missing kicker', 'no <div class="kicker"> at top of hero'))
    if not re.search(r'<h1[^>]*class="title"', html):
        hits.append(('HERO', 'missing h1.title', 'expected <h1 class="title">'))
    m = re.search(r'<p class="standfirst"[^>]*>(.*?)</p>', html, re.S)
    if not m:
        hits.append(('HERO', 'missing standfirst', 'no <p class="standfirst">'))
    elif len(re.sub(r'<[^>]+>', '', m.group(1)).strip()) < 20:
        hits.append(('HERO', 'empty standfirst', 'standfirst under 20 chars — needs a real dek'))
    au_m = re.search(r'<span class=["\']au["\']>(.*?)</span>', html, re.S)
    if not au_m:
        hits.append(('HERO', 'missing author', 'no <span class="au"> in byline'))
    else:
        au_text = re.sub(r'<[^>]+>', '', au_m.group(1)).strip()
        # Byline should be a person's name: 2-5 capitalized tokens, no sentence-ending punctuation
        if not au_text:
            hits.append(('HERO', 'empty author', '<span class="au"> is empty'))
        elif len(au_text) > 60:
            hits.append(('HERO', 'suspicious author (too long)', f'author string is {len(au_text)} chars — should be a name: "{au_text[:80]}…"'))
        elif re.search(r'[.!]\s+[A-Z]', au_text):
            hits.append(('HERO', 'suspicious author (contains sentences)', f'author string contains sentence punctuation: "{au_text[:80]}"'))
        elif not re.match(r'^[A-Z][a-zA-ZÀ-ÿ\-\'’]+(\s+[A-Z][a-zA-ZÀ-ÿ\-\'’]+){1,4}$', au_text.split(',')[0].strip() if ',' in au_text else au_text):
            hits.append(('HERO', 'suspicious author (not a name)', f'expected "First Last" pattern: "{au_text[:80]}"'))
    if not re.search(r'<time datetime="', html):
        hits.append(('HERO', 'missing date', 'no <time datetime="…"> in byline'))


def audit_body(html, hits):
    if not re.search(r'<p class="lede"', html):
        hits.append(('BODY', 'no lede paragraph', 'first paragraph should carry class="lede" for the drop cap'))
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    for i, h2 in enumerate(h2s):
        text = re.sub(r'<[^>]+>', '', h2).strip()
        if not re.match(r'^(Section [IVX]+|Section \d+|§)', text):
            hits.append(('BODY', 'unnumbered h2', f'h2 #{i+1} should begin with "Section I ·" — got: "{text[:60]}"'))
    # H3 subhead should follow every h2
    for m in re.finditer(r'<h2[^>]*>.*?</h2>(.*?)(?=<h2|$)', html, re.S):
        block = m.group(1)
        if '<h3' not in block[:2000]:
            snippet = re.sub(r'<[^>]+>', '', m.group(0))[:60]
            hits.append(('BODY', 'h2 without h3 subhead', f'"{snippet}…"'))


def audit_figures(html, hits):
    figs = re.findall(r'<figure class="viz"[^>]*>.*?</figure>', html, re.S)
    for i, fig in enumerate(figs):
        n = i + 1
        if 'class="viz-title"' not in fig:
            hits.append(('FIGURE', f'Fig {n} missing viz-title', 'no <p class="viz-title">Figure N</p>'))
        if not re.search(r'<h4', fig):
            hits.append(('FIGURE', f'Fig {n} missing h4', 'no <h4> figure title'))
        if 'class="plate' not in fig:
            hits.append(('FIGURE', f'Fig {n} missing plate', 'no div.plate wrapper'))
        if '<figcaption' not in fig:
            hits.append(('FIGURE', f'Fig {n} missing figcaption', 'no <figcaption>'))
    # --fig-w should be on every figure with an explicit size
    fig_openers = re.findall(r'<figure class="viz"[^>]*>', html)
    for i, opener in enumerate(fig_openers):
        if '--fig-w' not in opener:
            hits.append(('FIGURE', f'Fig {i+1} missing --fig-w', 'figure element should carry style="--fig-w:Npx" for caption alignment'))


def audit_tables(html, hits):
    tables = re.findall(r'<table[^>]*>.*?</table>', html, re.S)
    for i, tbl in enumerate(tables):
        n = i + 1
        if 'class="rtbl' not in tbl:
            hits.append(('TABLE', f'Table {n} missing .rtbl', 'no class="rtbl" on <table>'))
        if '<caption' not in tbl:
            hits.append(('TABLE', f'Table {n} missing caption', 'no <caption> — table needs a "Table N · Title" heading'))
        if '<tfoot' not in tbl:
            hits.append(('TABLE', f'Table {n} missing tfoot', 'no <tfoot> with Note.— line'))


def audit_code(html, hits):
    pres = re.findall(r'<pre\b[^>]*>.*?</pre>', html, re.S)
    for i, pre in enumerate(pres):
        if 'language-' not in pre:
            snippet = re.sub(r'<[^>]+>', '', pre)[:60].strip()
            hits.append(('CODE', f'Code block {i+1} missing language class',
                         f'wrap in <code class="language-java"> (or other) for Prism to highlight: "{snippet}…"'))


def audit_breakouts(html, wc, hits):
    if wc < 2000:
        return
    if not re.search(r'class="pullquote"', html):
        hits.append(('BREAKOUT', 'no pullquote', f'post is {wc} words — long-form posts want at least one pullquote'))
    if not re.search(r'class="enote"', html):
        hits.append(('BREAKOUT', 'no enote', f'post is {wc} words — long-form posts want at least one editor\'s note'))


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    wc = _wc(html)
    hits = []
    audit_hero(html, hits)
    audit_body(html, hits)
    audit_figures(html, hits)
    audit_tables(html, hits)
    audit_code(html, hits)
    audit_breakouts(html, wc, hits)
    return wc, hits


def format_report(path, wc, hits):
    lines = [f'\n=== {path}  ({wc} words) ===']
    if not hits:
        lines.append('  ok — template contract satisfied')
        return '\n'.join(lines)
    by_group = {}
    for group, label, detail in hits:
        by_group.setdefault(group, []).append((label, detail))
    lines.append(f'  {len(hits)} gap(s) across {len(by_group)} group(s)')
    for group in ('HERO', 'BODY', 'FIGURE', 'TABLE', 'CODE', 'BREAKOUT'):
        if group not in by_group:
            continue
        lines.append(f'\n  [{group}]')
        for label, detail in by_group[group]:
            lines.append(f'    {label}')
            lines.append(f'      {detail}')
    return '\n'.join(lines)


def compare_to(approved_path, scaffold_path):
    """Diff two files element-by-element — show what the scaffold lacks vs approved."""
    def stats(path):
        h = open(path, 'r', encoding='utf-8').read()
        return {
            'standfirst':       int(bool(re.search(r'class="standfirst"[^>]*>[^<]{20,}', h))),
            'kicker':           len(re.findall(r'class="kicker"', h)),
            'byline_author':    len(re.findall(r'class="au">', h)),
            'lede_dropcap':     len(re.findall(r'p class="lede"', h)),
            'section_h2s':      len(re.findall(r'<h2>Section', h)),
            'section_h3s':      len(re.findall(r'<h3', h)),
            'figures':          len(re.findall(r'<figure class="viz"', h)),
            'fig_w':            len(re.findall(r'--fig-w:', h)),
            'viz_titles':       len(re.findall(r'class="viz-title"', h)),
            'fig_h4':           len(re.findall(r'<h4', h)),
            'figcaps':          len(re.findall(r'<figcaption', h)),
            'pullquotes':       len(re.findall(r'class="pullquote"', h)),
            'enotes':           len(re.findall(r'class="enote"', h)),
            'tables_rtbl':      len(re.findall(r'class="rtbl', h)),
            'table_caption':    len(re.findall(r'<caption', h)),
            'table_tfoot':      len(re.findall(r'<tfoot', h)),
            'code_language':    len(re.findall(r'code class="language-', h)),
        }
    a = stats(approved_path)
    b = stats(scaffold_path)
    print(f'\n=== COMPARE ===')
    print(f'  approved: {approved_path}')
    print(f'  scaffold: {scaffold_path}')
    print()
    print(f'  {"element":<20}{"approved":>10}{"scaffold":>10}   status')
    print('  ' + '-' * 55)
    for k in a:
        aa, bb = a[k], b[k]
        status = 'OK' if bb >= aa else 'GAP (' + str(aa - bb) + ' short)'
        marker = '  ' if bb >= aa else '⚠ '
        print(f'  {marker}{k:<20}{aa:>10}{bb:>10}   {status}')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='+')
    p.add_argument('--compare-to', help='path to approved reference file; diff element counts against it')
    args = p.parse_args()

    if args.compare_to:
        for f in args.files:
            compare_to(args.compare_to, f)
        return 0

    total_gaps = 0
    for path in args.files:
        wc, hits = audit_file(path)
        print(format_report(path, wc, hits))
        total_gaps += len(hits)
    print(f'\nTotal: {total_gaps} template gap(s) across {len(args.files)} file(s)')
    return 1 if total_gaps else 0


if __name__ == '__main__':
    sys.exit(main())
