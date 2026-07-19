"""Single-source the integrated-platform "cake" HTML.

Canonical source: sales-presentation/slides/family-platform/slide.html, between
the <!-- CAKE:BODY:START --> / <!-- CAKE:BODY:END --> markers (the .cake-wrap +
.rt-panel block). The built decks (specify, token-shredder, overview-long)
already share that slide via the builder. This script injects the SAME cake body
into the two hand-authored standalone decks so their copies can't drift.

Only the HTML content is single-sourced. Each deck keeps its own cake CSS/JS
(scope id + accent color legitimately differ and are stable). Per-deck wrapper
chrome (section id, heading, data-active, grid class) is left untouched — this
script replaces only the cake body: from <div class="cake-wrap"> through the
matching close of <div class="rt-panel">.

The canonical body carries {{CORPUS_REGULATIONS}} (a builder token). For the
standalone files it is rewritten to the <!--corpus:regulations-->N<!--/corpus-->
marker form that _build/apply_corpus.py already keeps current.

Run:  python3 _build/sync_cake.py [--check]
--check exits non-zero if any target is out of sync (for CI / pre-commit).
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus_counts

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CANONICAL = os.path.join(ROOT, 'sales-presentation', 'slides', 'family-platform', 'slide.html')
TARGETS = ['akka-overview/index.html', 'akka-verify/index.html']

GEN_NOTE = ('<!-- CAKE:BODY (generated from sales-presentation/slides/family-platform '
            'by _build/sync_cake.py — do not edit here; edit the canonical slide) -->')


def canonical_body():
    text = open(CANONICAL, encoding='utf-8').read()
    m = re.search(r'<!-- CAKE:BODY:START.*?-->\n(.*?)\n<!-- CAKE:BODY:END -->', text, re.S)
    if not m:
        sys.exit('sync_cake: CAKE:BODY markers not found in canonical slide.')
    return m.group(1)


GEN_NOTE_PREFIX = '<!-- CAKE:BODY (generated'


def find_region(html):
    """Return (start, end) span covering the cake body — from the generated
    note (if a previous run left one) or <div class="cake-wrap">, through the
    matching close of <div class="rt-panel">. Including the note keeps
    re-injection idempotent instead of stacking notes."""
    cake = html.find('<div class="cake-wrap">')
    if cake == -1:
        return None
    note = html.rfind(GEN_NOTE_PREFIX, 0, cake)
    start = note if note != -1 else cake
    panel = html.find('<div class="rt-panel">', start)
    if panel == -1:
        return None
    # Balanced <div>/</div> scan from the rt-panel open to its matching close.
    depth = 0
    for m in re.finditer(r'<div\b|</div>', html[panel:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            end = panel + m.end()
            return (start, end)
    return None


def build_body_for(target_relpath, body, values):
    reg = values['regulations']
    body = body.replace('{{CORPUS_REGULATIONS}}',
                        f'<!--corpus:regulations-->{reg}<!--/corpus-->')
    if '{{' in body:
        leftover = re.findall(r'\{\{[^}]+\}\}', body)
        sys.exit(f'sync_cake: unresolved token(s) for {target_relpath}: {leftover}')
    # strip the leading indentation of the canonical block's first line so the
    # generated note sits flush, then re-emit the body verbatim.
    return GEN_NOTE + '\n' + body.lstrip('\n')


def main():
    check = '--check' in sys.argv
    values = {k: str(v) for k, v in corpus_counts.values().items()}
    body = canonical_body()

    problems = []
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        html = open(path, encoding='utf-8').read()
        region = find_region(html)
        if not region:
            problems.append(f'{rel}: cake-wrap/rt-panel region not found')
            continue
        start, end = region
        new_block = build_body_for(rel, body, values)
        new_html = html[:start] + new_block + html[end:]

        if new_html != html:
            if check:
                problems.append(f'{rel}: cake body out of sync')
            else:
                open(path, 'w', encoding='utf-8').write(new_html)
                print(f'sync_cake: updated {rel}')
        else:
            print(f'sync_cake: {rel} already in sync')

    if problems:
        print('\n'.join(problems), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
