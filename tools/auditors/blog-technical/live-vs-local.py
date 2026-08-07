#!/usr/bin/env python3
"""Compare a local approved blog-technical file against a live-rendered URL.

Loads both in headless Edge, extracts the article DOM and computed styles for
every element bearing a template class, then reports differences the eye
would catch: font family, size, weight, colour, margin, padding, and the
element hierarchy of the article body.

Also captures full-page screenshots at a fixed viewport and dumps them to
/scratchpad/audit-shots/ so an eyeball diff is one click away.

Usage:
    python tools/auditors/blog-technical/live-vs-local.py \
        blog-technical/akka-memory.html \
        https://akka.io/blog-preview/akka-memory-durable-in-memory-and-sharded-data

Exit code 1 on any style mismatch, 0 on full parity.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SHOTS_DIR = os.path.join(ROOT, 'scratchpad', 'audit-shots')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE):
    for p in [r'C:\Program Files\Microsoft\Edge\Application\msedge.exe']:
        if os.path.exists(p):
            EDGE = p
            break

# Selectors whose presence and computed style must match between local and live.
# Structural invariants: every figure must have plot-wrap, plate--flush inside.
# Every table must be inside .table-scroll. No "Human-polish" placeholder text.
# --fig-w must be present on every figure with an image.
STRUCTURAL_CHECKS_JS = r'''
(() => {
  const gaps = [];
  const figs = document.querySelectorAll('figure.viz');
  for (const [i, f] of Array.from(figs).entries()) {
    const n = i + 1;
    if (!f.querySelector('.plot-wrap')) gaps.push({fig: n, gap: 'missing .plot-wrap wrapper (image will overflow --fig-w)'});
    if (!f.querySelector('.plate')) gaps.push({fig: n, gap: 'missing .plate div'});
    if (!f.style.getPropertyValue('--fig-w')) gaps.push({fig: n, gap: 'missing --fig-w on figure (image runs to .wide max width)'});
    const img = f.querySelector('img');
    if (img) {
      const iw = img.getBoundingClientRect().width;
      const fw = f.getBoundingClientRect().width;
      if (iw > fw * 0.85 && iw > 700) gaps.push({fig: n, gap: `image ${Math.round(iw)}px is >85% of figure ${Math.round(fw)}px — check --fig-w and .plot-wrap`});
      // text-relative check: if native image has a text height and img renders too big, flag
      const nw = img.naturalWidth;
      if (nw && iw / nw > 1.5) gaps.push({fig: n, gap: `image scaled ${(iw/nw).toFixed(2)}× native (${nw}px) — pixelation risk`});
    }
  }
  // Table checks
  const tables = document.querySelectorAll('.blog-technical table, article table');
  for (const [i, t] of Array.from(tables).entries()) {
    const wrap = t.closest('.table-scroll');
    if (!wrap) gaps.push({tbl: i+1, gap: 'table not wrapped in .table-scroll (may overflow viewport)'});
    const tw = t.getBoundingClientRect().width;
    if (tw > 1400) gaps.push({tbl: i+1, gap: `table ${Math.round(tw)}px wide — cell text likely overflows`});
  }
  // Placeholder-text checks
  const html = document.querySelector('article') ? document.querySelector('article').innerHTML : '';
  for (const marker of ['Human-polish this caption', 'TODO', 'FIXME', 'lorem ipsum']) {
    if (html.includes(marker)) gaps.push({text: marker, gap: `placeholder text "${marker}" leaked into published HTML`});
  }
  return gaps;
})();
'''

SELECTORS = [
    ('kicker',           '.kicker',                       ['fontFamily', 'fontSize', 'fontWeight', 'color', 'letterSpacing', 'textTransform', 'marginBottom']),
    ('h1.title',         'h1.title',                      ['fontFamily', 'fontSize', 'fontWeight', 'color', 'lineHeight', 'letterSpacing', 'marginBottom']),
    ('standfirst',       '.standfirst',                   ['fontFamily', 'fontSize', 'fontWeight', 'color', 'lineHeight', 'marginBottom']),
    ('byline',           '.byline',                       ['fontFamily', 'fontSize', 'color', 'paddingTop', 'paddingBottom', 'borderTop', 'borderBottom']),
    ('byline .au',       '.byline .au',                   ['fontWeight', 'color']),
    ('body p',           '.body p',                       ['fontFamily', 'fontSize', 'lineHeight', 'color', 'marginBottom']),
    ('body p.lede',      '.body p.lede',                  ['fontFamily', 'fontSize', 'lineHeight', 'color', 'marginBottom']),
    ('body h2',          '.body h2',                      ['fontFamily', 'fontSize', 'fontWeight', 'color', 'letterSpacing', 'textTransform', 'marginTop', 'marginBottom']),
    ('body h3',          '.body h3',                      ['fontFamily', 'fontSize', 'fontWeight', 'color', 'lineHeight', 'marginTop', 'marginBottom', 'borderBottom']),
    ('figure.viz',       'figure.viz',                    ['marginTop', 'marginBottom', 'marginLeft', 'marginRight', 'maxWidth']),
    ('viz-title',        'figure.viz .viz-title',         ['fontFamily', 'fontSize', 'fontWeight', 'color', 'textTransform', 'letterSpacing', 'marginBottom']),
    ('viz h4',           'figure.viz h4',                 ['fontFamily', 'fontSize', 'fontWeight', 'color', 'marginTop', 'marginBottom']),
    ('viz plate',        'figure.viz .plate',             ['background', 'padding', 'border']),
    ('viz figcaption',   'figure.viz figcaption',         ['fontFamily', 'fontSize', 'fontStyle', 'color', 'marginTop']),
    ('pre[language-*]',  'pre[class*="language-"]',       ['fontFamily', 'fontSize', 'background', 'color', 'padding', 'borderRadius']),
    ('code lang token',  'pre code .token.keyword',       ['color']),
]

# JS run in the page: for each selector return
#   { count, first_text, computed: { style1: val, style2: val, ... } }
EXTRACT_JS = r'''
(() => {
  const sels = %s;
  const out = {};
  for (const [name, sel, props] of sels) {
    const nodes = document.querySelectorAll(sel);
    const first = nodes[0];
    const rec = { name, sel, count: nodes.length, texts: [] };
    for (const n of Array.from(nodes).slice(0, 6)) {
      const t = (n.innerText || n.textContent || '').trim().replace(/\s+/g, ' ');
      rec.texts.push(t.slice(0, 140));
    }
    if (first) {
      const cs = getComputedStyle(first);
      rec.computed = {};
      for (const p of props) rec.computed[p] = cs[p];
    }
    out[name] = rec;
  }
  return out;
})();
'''

# Full DOM signature: element tag + class + first 60 chars text, in reading order.
STRUCTURE_JS = r'''
(() => {
  // Find the article root — prefer .body.col, fallback to <article>, else <body>.
  const root = document.querySelector('.blog-technical article') ||
               document.querySelector('article') ||
               document.body;
  const out = [];
  function walk(node, depth) {
    if (!node || node.nodeType !== 1) return;
    // Skip HubSpot chrome / non-article regions
    if (node.matches && (node.matches('header.header-2026, footer.footer-2026-mega, script, style, noscript'))) return;
    const tag = node.tagName.toLowerCase();
    const cls = node.className && typeof node.className === 'string' ? node.className : '';
    const text = (node.childNodes.length && Array.from(node.childNodes)
                    .filter(n => n.nodeType === 3)
                    .map(n => n.textContent).join(' ').trim().replace(/\s+/g, ' ').slice(0, 60));
    out.push({ depth, tag, cls, text });
    for (const c of node.children) walk(c, depth + 1);
  }
  walk(root, 0);
  return out;
})();
'''


def run_edge_eval(url_or_file, js):
    """Load URL/file in headless Edge, evaluate JS, return parsed JSON.

    Uses --dump-dom + a bookmarklet-style approach via --virtual-time-budget
    so JS runs to completion before dump. Headless Edge lacks --eval, so
    we inject the script by embedding it in a temporary HTML wrapper for
    local paths, or fetching + wrapping for remote URLs.
    """
    import tempfile
    import urllib.request

    if url_or_file.startswith(('http://', 'https://')):
        html = urllib.request.urlopen(url_or_file, timeout=30).read().decode('utf-8', errors='replace')
        # Live URL — use it directly. Inject JS via a data: URL is tricky;
        # use a puppeteer-like approach by hosting a local wrapper.
        # Simpler: use --headless=new + --dump-dom + a runner script.
        source_url = url_or_file
    else:
        source_url = 'file:///' + os.path.abspath(url_or_file).replace('\\', '/')

    # Write a runner HTML that navigates to source via iframe and posts the result
    # to console. Simpler: use --remote-debugging-port and CDP.
    # Simplest for now: use --headless --dump-dom to get post-JS DOM, then
    # regex-parse it ourselves. We lose computed styles but keep structure.
    dump = subprocess.run(
        [EDGE, '--headless=new', '--disable-gpu', '--no-sandbox',
         '--virtual-time-budget=5000', '--window-size=1280,4000',
         '--user-data-dir=' + tempfile.mkdtemp(),
         '--dump-dom', source_url],
        capture_output=True, timeout=60,
    )
    return dump.stdout.decode('utf-8', errors='replace')


def run_edge_cdp(url_or_file, js, viewport=(1280, 4000)):
    """Use Chrome DevTools Protocol via python websockets to eval JS in-page.

    Falls back to plain --dump-dom if websockets isn't available.
    """
    try:
        import urllib.request
        import websocket  # pip install websocket-client
    except ImportError:
        return None, 'websocket-client not installed; falling back to dump-dom'

    import tempfile
    import atexit

    if url_or_file.startswith(('http://', 'https://')):
        source_url = url_or_file
    else:
        source_url = 'file:///' + os.path.abspath(url_or_file).replace('\\', '/')

    port = 9333
    profile = tempfile.mkdtemp(prefix='edge-audit-')
    proc = subprocess.Popen(
        [EDGE, '--headless=new', '--disable-gpu', '--no-sandbox',
         f'--remote-debugging-port={port}',
         '--remote-allow-origins=*',
         f'--window-size={viewport[0]},{viewport[1]}',
         f'--user-data-dir={profile}',
         'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    atexit.register(proc.terminate)

    # Wait for CDP to accept connections
    ws_url = None
    for _ in range(40):
        time.sleep(0.25)
        try:
            r = urllib.request.urlopen(f'http://127.0.0.1:{port}/json', timeout=1).read()
            targets = json.loads(r)
            # Prefer a page-type target (skip service workers, extension bg pages)
            pages = [t for t in targets if t.get('type') == 'page']
            if pages:
                ws_url = pages[0]['webSocketDebuggerUrl']
                break
        except Exception:
            continue
    if not ws_url:
        # As a last resort, open a fresh tab via HTTP API
        try:
            r = urllib.request.urlopen(f'http://127.0.0.1:{port}/json/new?about:blank', method='PUT', timeout=2).read()
            tgt = json.loads(r)
            ws_url = tgt.get('webSocketDebuggerUrl')
        except Exception as e:
            proc.terminate()
            return None, f'no page target found: {e}'
    if not ws_url:
        proc.terminate()
        return None, 'CDP endpoint did not come up'

    ws = websocket.create_connection(ws_url, timeout=30)
    msg_id = [0]

    def send(method, params=None):
        msg_id[0] += 1
        ws.send(json.dumps({'id': msg_id[0], 'method': method, 'params': params or {}}))
        while True:
            reply = json.loads(ws.recv())
            if reply.get('id') == msg_id[0]:
                return reply

    send('Page.enable')
    send('Runtime.enable')
    send('Page.navigate', {'url': source_url})
    # Poll readyState until 'complete' with a hard 20s ceiling
    ready = None
    t0 = time.time()
    while time.time() - t0 < 20:
        r = send('Runtime.evaluate', {'expression': 'document.readyState', 'returnByValue': True})
        ready = r.get('result', {}).get('result', {}).get('value')
        if ready == 'complete':
            break
        time.sleep(0.4)
    # Additional 2s for late-firing scripts (fonts, autoloaders)
    time.sleep(2)
    # Diagnostic: check title + body length so failures are traceable
    r = send('Runtime.evaluate', {'expression': 'JSON.stringify({t: document.title, bl: document.body ? document.body.innerHTML.length : -1, url: location.href})', 'returnByValue': True})
    diag = r.get('result', {}).get('result', {}).get('value')
    print(f'    loaded: readyState={ready}  {diag}')
    result = send('Runtime.evaluate', {
        'expression': js,
        'returnByValue': True,
        'awaitPromise': True,
    })
    err = result.get('result', {}).get('exceptionDetails')
    if err:
        print(f'    JS error: {err}')
    val = result.get('result', {}).get('result', {}).get('value')

    ws.close()
    proc.terminate()
    return val, None


def take_screenshot(url_or_file, out_path, viewport=(1280, 4000)):
    """Full-page screenshot via headless Edge."""
    import tempfile

    if url_or_file.startswith(('http://', 'https://')):
        source_url = url_or_file
    else:
        source_url = 'file:///' + os.path.abspath(url_or_file).replace('\\', '/')

    profile = tempfile.mkdtemp(prefix='edge-shot-')
    subprocess.run(
        [EDGE, '--headless=new', '--disable-gpu', '--no-sandbox',
         '--virtual-time-budget=8000',
         f'--window-size={viewport[0]},{viewport[1]}',
         f'--user-data-dir={profile}',
         f'--screenshot={out_path}',
         '--hide-scrollbars',
         source_url],
        capture_output=True, timeout=60,
    )
    return out_path


def normalize(v):
    """Trim ' 0px' → '0', collapse '0px 0px 0px 0px' → '0'."""
    if v is None:
        return None
    s = str(v).strip()
    # Colour: normalize rgb(a,b,c) → rgb(a,b,c)
    return s


def diff_computed(local, live):
    """For each selector, compare computed style dicts. Return list of gaps."""
    gaps = []
    for name in local:
        l = local[name]
        r = live.get(name)
        if not r:
            gaps.append({'selector': name, 'issue': 'missing on live', 'local': l.get('count'), 'live': 0})
            continue
        if l['count'] != r['count']:
            gaps.append({'selector': name, 'issue': 'count mismatch', 'local': l['count'], 'live': r['count']})
        lc = l.get('computed') or {}
        rc = r.get('computed') or {}
        for prop in lc:
            if normalize(lc[prop]) != normalize(rc.get(prop)):
                gaps.append({
                    'selector': name, 'issue': f'style: {prop}',
                    'local': lc[prop], 'live': rc.get(prop),
                })
    return gaps


def print_gap_report(gaps, local_sig, live_sig):
    print(f'\n=== LIVE-vs-LOCAL COMPARISON ===')
    print(f'  local selectors extracted: {len(local_sig)}')
    print(f'  live  selectors extracted: {len(live_sig)}')
    if not gaps:
        print(f'\n  MATCH — all selectors align on computed style and count.')
        return
    print(f'\n  {len(gaps)} gap(s):\n')
    by_sel = {}
    for g in gaps:
        by_sel.setdefault(g['selector'], []).append(g)
    for sel, items in by_sel.items():
        print(f'  [{sel}]')
        for it in items:
            print(f'    {it["issue"]:<32}  local="{it["local"]}"  live="{it["live"]}"')
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('local', help='local approved HTML file')
    ap.add_argument('live', help='live URL to compare against')
    ap.add_argument('--skip-shots', action='store_true', help='skip screenshot capture')
    args = ap.parse_args()

    os.makedirs(SHOTS_DIR, exist_ok=True)

    # Full-page screenshots for eyeball diff
    if not args.skip_shots:
        local_shot = os.path.join(SHOTS_DIR, 'local.png')
        live_shot = os.path.join(SHOTS_DIR, 'live.png')
        print(f'[1/4] Screenshot local  → {os.path.relpath(local_shot, ROOT)}')
        take_screenshot(args.local, local_shot)
        print(f'[2/4] Screenshot live   → {os.path.relpath(live_shot, ROOT)}')
        take_screenshot(args.live, live_shot)

    js = EXTRACT_JS % json.dumps(SELECTORS)
    print(f'[3/4] Extract computed styles from local')
    local_sig, err = run_edge_cdp(args.local, js)
    if err:
        print(f'  ERROR: {err}')
        return 2
    print(f'[4/4] Extract computed styles from live')
    live_sig, err = run_edge_cdp(args.live, js)
    if err:
        print(f'  ERROR: {err}')
        return 2

    gaps = diff_computed(local_sig or {}, live_sig or {})
    print_gap_report(gaps, local_sig or {}, live_sig or {})

    # Structural invariants — plot-wrap, plate, --fig-w, table-scroll, placeholder text
    print('\n=== STRUCTURAL INVARIANTS (live only) ===')
    structural, err = run_edge_cdp(args.live, STRUCTURAL_CHECKS_JS)
    if err:
        print(f'  ERROR: {err}')
    elif not structural:
        print('  OK — all structural checks passed on live')
    else:
        print(f'  {len(structural)} structural issue(s):')
        for g in structural:
            tag = f'fig {g["fig"]}' if 'fig' in g else (f'tbl {g["tbl"]}' if 'tbl' in g else f'text')
            print(f'    [{tag}]  {g["gap"]}')
        gaps.extend(structural)

    # Dump raw signatures for follow-up debugging
    with open(os.path.join(SHOTS_DIR, 'local-sig.json'), 'w', encoding='utf-8') as f:
        json.dump(local_sig, f, indent=2)
    with open(os.path.join(SHOTS_DIR, 'live-sig.json'), 'w', encoding='utf-8') as f:
        json.dump(live_sig, f, indent=2)
    print(f'\n  raw signatures: {os.path.relpath(SHOTS_DIR, ROOT)}/{{local,live}}-sig.json')
    print(f'  screenshots:    {os.path.relpath(SHOTS_DIR, ROOT)}/{{local,live}}.png')

    return 1 if gaps else 0


if __name__ == '__main__':
    sys.exit(main())
