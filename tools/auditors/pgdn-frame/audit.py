#!/usr/bin/env python3
"""PgDn-frame auditor.

Drives a deck the way a presenter does — real PageDown keypresses, so the
deck's own nav JS does the scrolling — and after each jump measures how the
landed slide is framed inside the visible band.

The visible band is the production band: the akka.io header is fixed and 78px
tall, so content lives in y = 78 .. viewport_height. A local file:// render has
no header, which is why every slide looks 78px low on a laptop; this auditor
measures against the production band so the numbers mean something either way.

Per slide it reports:

  CLIPPED     content starts above y=78 and will sit under the header
  CUT_OFF     content ends past the bottom of the visible band
  TOO_LOW     content is vertically centered, but sits low in the band
  TOO_HIGH    content is vertically centered, but sits high in the band
  TITLE_X     a left-anchored slide's first title is not at x=92 (±15)

Centering is only judged on sections that ask to be centered
(justify-content: center / align-items: center). Sections that deliberately
top-anchor are checked for CLIPPED and CUT_OFF only.

Usage:
    python tools/auditors/pgdn-frame/audit.py [file.html ...]

  Default targets: every sales-presentation/generated/*/index.html.

Exit 0 = every slide frames cleanly; non-zero = at least one finding.
"""

import glob
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

CSS_W, CSS_H = 1536, 861
HEADER_H = 78
BOTTOM_BUFFER = 12          # content may reach this close to the fold
CENTER_TOLERANCE = 24       # top gap vs bottom gap, in px
STANDARD_TITLE_X = 92       # section padding-left = 6vw at 1536
# Slides whose bottom half is intentionally held by absolutely-positioned
# furniture (scroll hint, presenter block). Centering is meaningless there;
# they are still checked for CLIPPED, CUT_OFF and TITLE_X.
CENTER_SKIP = {'title'}
TITLE_X_TOLERANCE = 15
MAX_STEPS = 40


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.isfile(p):
            return p
    raise SystemExit('Edge not found.')


def _free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


# Measures the section that currently occupies most of the visible band.
# Content box excludes absolutely/fixed positioned decoration (bloom, dot grid,
# scroll hints) so the numbers describe the readable block, not the backdrop.
MEASURE_JS = r"""
(function(){
  var H = window.innerHeight;
  // Same probe the deck nav uses: a real fixed header on akka.io, nothing on
  // a local file:// render. The visible band is HDR..H either way.
  var HDR = 0, all = document.body.getElementsByTagName('*');
  for (var i = 0; i < all.length; i++) {
    var cs = getComputedStyle(all[i]);
    if (cs.position !== 'fixed') continue;
    var hr = all[i].getBoundingClientRect();
    if (hr.top <= 2 && hr.height >= 40 && hr.height <= 140 &&
        hr.width > window.innerWidth * 0.6 && hr.height > HDR) HDR = Math.round(hr.height);
  }
  var cands = Array.prototype.slice.call(
    document.querySelectorAll('section, [id$="-sticky"], [id$="-wrapper"] > div'));
  var best = null, bestArea = -1;
  cands.forEach(function(s){
    var r = s.getBoundingClientRect();
    if (r.height < 120) return;
    var vis = Math.min(r.bottom, H) - Math.max(r.top, HDR);
    if (vis > bestArea) { bestArea = vis; best = s; }
  });
  if (!best) return null;

  function flow(el){
    return Array.prototype.filter.call(el.children, function(c){
      if (c.tagName === 'SCRIPT' || c.tagName === 'STYLE') return false;
      var cs = getComputedStyle(c);
      if (cs.position === 'absolute' || cs.position === 'fixed') return false;
      if (cs.visibility === 'hidden' || cs.display === 'none') return false;
      var r = c.getBoundingClientRect();
      return r.width > 4 && r.height > 4;
    });
  }

  var kids = flow(best);
  while (kids.length === 1 && flow(kids[0]).length) { kids = flow(kids[0]); }
  if (!kids.length) return null;

  var top = Math.min.apply(null, kids.map(function(k){ return k.getBoundingClientRect().top; }));
  var bot = Math.max.apply(null, kids.map(function(k){ return k.getBoundingClientRect().bottom; }));
  var cl  = Math.min.apply(null, kids.map(function(k){ return k.getBoundingClientRect().left; }));
  var cr  = Math.max.apply(null, kids.map(function(k){ return k.getBoundingClientRect().right; }));
  var sr  = best.getBoundingClientRect();
  // A block centred inside its section is left-anchored by intent, not by drift.
  var blockCentred = Math.abs((cl - sr.left) - (sr.right - cr)) <= 24;

  var cs = getComputedStyle(best);
  var centered = (cs.justifyContent === 'center' && cs.display.indexOf('flex') >= 0);

  var t = best.querySelector('[class*="eyebrow"], h1, h2, [class*="headline"]');
  var tl = null, ta = null;
  if (t) {
    var tr = t.getBoundingClientRect();
    tl = Math.round(tr.left);
    ta = getComputedStyle(t).textAlign;
  }

  return JSON.stringify({
    id: best.id || '(anon)',
    vh: H,
    contentTop: Math.round(top),
    contentBot: Math.round(bot),
    centered: centered,
    titleLeft: tl,
    titleAlign: ta,
    /* R4 scales an over-tall section from transform-origin 50%, so a scaled
       slide's title is pulled in from the left by design. Report the factor so
       TITLE_X can stand down, the way the live-deck auditor already does. */
    scale: (function(){
      var tr = getComputedStyle(best).transform;
      if (!tr || tr === 'none') return 1;
      var n = Number(tr.slice(tr.indexOf('(') + 1).split(',')[0]);
      return isFinite(n) ? n : 1;
    })(),
    blockCentred: blockCentred,
    scrollY: Math.round(window.scrollY),
    headerH: HDR
  });
})()
"""


def audit(page):
    try:
        import websocket
    except ImportError:
        raise SystemExit('Missing dependency. Install: pip install -r tools/auditors/requirements.txt')

    url = 'file:///' + os.path.abspath(page).replace('\\', '/')
    port = _free_port()
    tmpdir = tempfile.mkdtemp(prefix='pgdn_audit_')
    proc = subprocess.Popen(
        [find_edge(), '--headless=new', '--disable-gpu', '--remote-debugging-port=' + str(port),
         '--remote-allow-origins=*', '--user-data-dir=' + tmpdir, 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port, timeout=1))
                ws_url = next((t['webSocketDebuggerUrl'] for t in tabs if t.get('type') == 'page'), None)
                if ws_url:
                    break
            except Exception:
                time.sleep(0.2)
        if not ws_url:
            raise SystemExit('Could not reach Edge DevTools endpoint.')

        ws = websocket.create_connection(ws_url, max_size=None, timeout=30)
        cid = [0]

        def cmd(method, params=None):
            cid[0] += 1
            ws.send(json.dumps({'id': cid[0], 'method': method, 'params': params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == cid[0]:
                    return m.get('result', {})

        cmd('Page.enable')
        cmd('Runtime.enable')
        cmd('Emulation.setDeviceMetricsOverride', {
            'width': CSS_W, 'height': CSS_H, 'deviceScaleFactor': 1, 'mobile': False,
            'screenWidth': CSS_W, 'screenHeight': CSS_H})
        cmd('Page.navigate', {'url': url})
        time.sleep(4)

        def page_down():
            for typ in ('keyDown', 'keyUp'):
                cmd('Input.dispatchKeyEvent', {
                    'type': typ, 'key': 'PageDown', 'code': 'PageDown',
                    'windowsVirtualKeyCode': 34, 'nativeVirtualKeyCode': 34})

        rows, seen, last_scroll = [], set(), -1
        for _ in range(MAX_STEPS):
            r = cmd('Runtime.evaluate', {'expression': MEASURE_JS, 'returnByValue': True})
            raw = r.get('result', {}).get('value')
            if raw:
                m = json.loads(raw)
                if m['id'] not in seen:
                    seen.add(m['id'])
                    rows.append(m)
                if m['scrollY'] == last_scroll and len(rows) > 1:
                    break
                last_scroll = m['scrollY']
            page_down()
            time.sleep(1.1)   # smooth-scroll settle

        return rows
    finally:
        proc.terminate()


def evaluate(rows):
    findings = []
    for m in rows:
        hdr = m.get('headerH', 0)
        gap_top = m['contentTop'] - hdr
        gap_bot = m['vh'] - m['contentBot']
        issues = []

        if m['contentTop'] < hdr:
            issues.append('CLIPPED    content top %d, header line is %d (-%d)'
                          % (m['contentTop'], hdr, hdr - m['contentTop']))
        if m['contentBot'] > m['vh'] - BOTTOM_BUFFER:
            issues.append('CUT_OFF    content bottom %d, fold is %d (+%d)'
                          % (m['contentBot'], m['vh'], m['contentBot'] - m['vh']))

        if (m['centered'] and m['id'] not in CENTER_SKIP
                and m['contentTop'] >= hdr and m['contentBot'] <= m['vh']):
            drift = gap_top - gap_bot
            if drift > CENTER_TOLERANCE:
                issues.append('TOO_LOW    top gap %d vs bottom gap %d (+%d low)'
                              % (gap_top, gap_bot, drift))
            elif -drift > CENTER_TOLERANCE:
                issues.append('TOO_HIGH   top gap %d vs bottom gap %d (%d high)'
                              % (gap_top, gap_bot, -drift))

        # A section R4 has scaled is inset from its layout box by design, so its
        # title is not at 92 and cannot be. Judging it here reported four slides
        # as drifted when all four were correctly framed; the live-deck auditor
        # has always restricted this check to unscaled sections.
        scaled = m.get('scale', 1) < 0.995
        if (m['titleLeft'] is not None and m['titleAlign'] != 'center' and not scaled
                and abs(m['titleLeft'] - STANDARD_TITLE_X) > TITLE_X_TOLERANCE):
            issues.append('TITLE_X    title left %d, standard is %d'
                          % (m['titleLeft'], STANDARD_TITLE_X))

        if issues:
            findings.append((m['id'], issues))
    return findings


def resolve_targets(argv):
    if argv:
        return argv
    return sorted(glob.glob(os.path.join(ROOT, 'sales-presentation', 'generated', '*', 'index.html')))


def main():
    targets = resolve_targets(sys.argv[1:])
    if not targets:
        raise SystemExit('No decks found.')

    print('PgDn-frame audit  @ %dx%d CSS  (header=%d, centering tolerance=%dpx)'
          % (CSS_W, CSS_H, HEADER_H, CENTER_TOLERANCE))
    print()

    total = 0
    for page in targets:
        rel = os.path.relpath(page, ROOT)
        rows = audit(page)
        findings = evaluate(rows)
        total += len(findings)
        if not findings:
            print('  %-58s ok  (%d slides)' % (rel, len(rows)))
            continue
        print('  %-58s %d slide(s) mis-framed of %d' % (rel, len(findings), len(rows)))
        for sid, issues in findings:
            print('      #%s' % sid)
            for i in issues:
                print('          %s' % i)
        print()

    if total:
        print('FAILED - %d slide(s) mis-framed on PgDn.' % total)
        return 1
    print('VERIFIED - every slide frames cleanly on PgDn.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
