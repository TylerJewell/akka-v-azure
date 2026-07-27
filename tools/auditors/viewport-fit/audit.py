#!/usr/bin/env python3
"""Viewport-fit auditor.

Verifies that decks/pages meet the three overview-deck rules formalized
2026-07-27:

  R1  Every section's content is capped at max-width 1400px.
      A section whose direct-child wrapper stretches wider than that on a wide
      viewport (audited at 1536px CSS width) fails.

  R2  The akka.io persistent header (fixed, 78px desktop) must not clip section
      content when the page is published. A section whose topmost visible child
      sits within y=0..78 of the section's own top box will be clipped by the
      header once ported. Passes if every section's first meaningful content
      element is >= 78px from the section top (i.e., padding-top or content
      offset clears the header zone).

  R3  Content should render intentionally at the laptop CSS viewport (1536x960
      per Tyler's 3072x1920 @ 200% Windows scale). Content that exceeds the
      viewport width horizontally, or that overflows past the section without a
      declared scroll pattern, is flagged.

Runs Edge headless over the DevTools Protocol at exactly 1536x960 CSS pixels
(via Emulation.setDeviceMetricsOverride — same technique the mobile auditor
uses to sidestep the Windows OS-minimum window clamp).

Usage:
    python tools/auditors/viewport-fit/audit.py [file.html ...]

  Default targets: akka-overview, akka-sdk, akka-verify (top-level decks) plus
  every sales-presentation/generated/*/index.html.

Exit 0 = every audited page passes; non-zero = at least one failure.
"""

import os
import re
import sys
import json
import time
import glob
import socket
import subprocess
import tempfile
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

CSS_W = 1536
CSS_H = 960
HDR_H = 78     # akka.io fixed header height (desktop)
MAX_W = 1400   # content max-width cap

# Injected before </head>. Forces reveals visible, then walks every <section>
# and reports (a) content wider than MAX_W, (b) content that starts inside
# the top HDR_H zone of its section, (c) content that exceeds the viewport
# horizontally at CSS_W.
SCANNER_TMPL = """
<style>.reveal,.pkg-reveal,.fam-reveal,.s6-reveal,.s13-reveal,.pp-reveal,.s5-reveal,.st-card,.cust-slide{opacity:1!important;transform:none!important}</style>
<script>
addEventListener('load', function(){ setTimeout(function(){
  var VW = window.innerWidth;
  var HDR = %d, MAX = %d;
  var out = [];
  document.querySelectorAll('section, [id$="-wrapper"] > [id$="-sticky"]').forEach(function(sec){
    var sr = sec.getBoundingClientRect();
    if (sr.width < 100) return;
    var sid = sec.id || (sec.parentElement && sec.parentElement.id) || '?';
    // (a) width — any descendant wider than MAX means the section lacks a cap
    var maxContentW = 0, maxContentEl = null;
    sec.querySelectorAll(':scope > *:not(script):not(style)').forEach(function(el){
      var r = el.getBoundingClientRect();
      // Skip absolute/fixed overlays — they're intentional full-bleed chrome
      var cs = getComputedStyle(el);
      if (cs.position === 'absolute' || cs.position === 'fixed') return;
      if (r.width > maxContentW) { maxContentW = r.width; maxContentEl = el; }
    });
    if (maxContentW > MAX + 2) {
      var sel = maxContentEl.id ? '#'+maxContentEl.id : (typeof maxContentEl.className==='string' && maxContentEl.className.trim()
                 ? '.'+maxContentEl.className.trim().split(/\\s+/).slice(0,2).join('.') : maxContentEl.tagName.toLowerCase());
      out.push({sec:sid, kind:'width', sel:sel, w:Math.round(maxContentW), cap:MAX});
    }
    // (b) header clearance — the top of the first meaningful content child
    // relative to the section box must be >= HDR to clear the fixed header
    // when the section is scrolled to viewport top. We measure the min-top
    // among direct visible children.
    var kids = Array.from(sec.children).filter(function(el){
      if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return false;
      var r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return false;
      var cs = getComputedStyle(el);
      return cs.position !== 'absolute' && cs.position !== 'fixed';
    });
    if (kids.length) {
      var minTop = Infinity, topEl = null;
      kids.forEach(function(el){
        var r = el.getBoundingClientRect();
        var offset = r.top - sr.top;
        if (offset < minTop) { minTop = offset; topEl = el; }
      });
      if (minTop < HDR) {
        var sel = topEl.id ? '#'+topEl.id : (typeof topEl.className==='string' && topEl.className.trim()
                   ? '.'+topEl.className.trim().split(/\\s+/).slice(0,2).join('.') : topEl.tagName.toLowerCase());
        out.push({sec:sid, kind:'clip', sel:sel, top:Math.round(minTop), hdr:HDR});
      }
    }
    // (c) horizontal overflow at viewport width — any descendant whose right
    // edge exceeds the viewport by more than 2px is a real overflow
    sec.querySelectorAll('*').forEach(function(el){
      var r = el.getBoundingClientRect();
      if (r.width < 4) return;
      if (r.right <= VW + 2) return;
      var p = el.parentElement, pr = p ? p.getBoundingClientRect() : null;
      if (pr && pr.right > VW + 2) return;  // parent also overflows → not the breakout
      var sel = el.id ? '#'+el.id : (typeof el.className==='string' && el.className.trim()
                 ? '.'+el.className.trim().split(/\\s+/).slice(0,2).join('.') : el.tagName.toLowerCase());
      out.push({sec:sid, kind:'overflow', sel:sel, over:Math.round(r.right - VW), w:Math.round(r.width)});
    });
  });
  document.title = 'VPFIT::' + JSON.stringify(out.slice(0,120));
}, 1200); });
</script></head>
""" % (HDR_H, MAX_W)


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.isfile(p):
            return p
    raise SystemExit('Edge not found; install Microsoft Edge or edit EDGE_CANDIDATES.')


def _free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def run(page):
    try:
        import websocket
    except ImportError:
        raise SystemExit('Missing dependency. Install: pip install -r tools/auditors/requirements.txt')

    with open(page, 'r', encoding='utf-8') as f:
        html = f.read().replace('</head>', SCANNER_TMPL, 1)
    tmp = os.path.join(tempfile.gettempdir(), 'viewport_fit_audit.html')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(html)
    url = 'file:///' + tmp.replace('\\', '/')

    port = _free_port()
    proc = subprocess.Popen(
        [find_edge(), '--headless=new', '--disable-gpu', f'--remote-debugging-port={port}',
         '--remote-allow-origins=*', '--window-size=1600,1100', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json', timeout=1))
                ws_url = next((t['webSocketDebuggerUrl'] for t in tabs if t.get('type') == 'page'), None)
                if ws_url:
                    break
            except Exception:
                time.sleep(0.2)
        if not ws_url:
            raise SystemExit('Could not reach Edge DevTools endpoint.')

        ws = websocket.create_connection(ws_url, max_size=None, timeout=30)
        counter = [0]

        def cmd(method, params=None):
            counter[0] += 1
            ws.send(json.dumps({'id': counter[0], 'method': method, 'params': params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get('id') == counter[0]:
                    return msg.get('result', {})

        cmd('Page.enable')
        cmd('Runtime.enable')
        cmd('Emulation.setDeviceMetricsOverride', {
            'width': CSS_W, 'height': CSS_H, 'deviceScaleFactor': 1, 'mobile': False,
            'screenWidth': CSS_W, 'screenHeight': CSS_H})
        cmd('Page.navigate', {'url': url})

        payload = None
        for _ in range(60):
            time.sleep(0.25)
            title = cmd('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
            val = title.get('result', {}).get('value', '') or ''
            if val.startswith('VPFIT::'):
                payload = val[len('VPFIT::'):]
                break
        ws.close()
        if payload is None:
            raise SystemExit(f'Could not read scan result for {page} (page failed to render?).')
        return json.loads(payload)
    finally:
        proc.terminate()


DEFAULT_TARGETS = [
    'akka-overview/index.html',
    'akka-sdk/index.html',
    'akka-verify/index.html',
]


def resolve_targets(args):
    if args:
        return [os.path.abspath(a) for a in args]
    out = [os.path.join(ROOT, t) for t in DEFAULT_TARGETS if os.path.isfile(os.path.join(ROOT, t))]
    out.extend(sorted(glob.glob(os.path.join(ROOT, 'sales-presentation/generated/*/index.html'))))
    return out


def main():
    targets = resolve_targets(sys.argv[1:])
    print(f'Viewport-fit audit  @ {CSS_W}x{CSS_H} CSS  (header={HDR_H}px, cap={MAX_W}px)')
    print()
    total_fail = 0
    for page in targets:
        rel = os.path.relpath(page, ROOT)
        try:
            findings = run(page)
        except SystemExit as e:
            print(f'  {rel:60}  SKIP  {e}')
            continue
        by_sec = {}
        for f in findings:
            by_sec.setdefault(f['sec'], []).append(f)
        if not findings:
            print(f'  {rel:60}  ok')
            continue
        total_fail += 1
        n_w = sum(1 for f in findings if f['kind'] == 'width')
        n_c = sum(1 for f in findings if f['kind'] == 'clip')
        n_o = sum(1 for f in findings if f['kind'] == 'overflow')
        print(f'  {rel:60}  FAIL  {len(findings)} finding(s)  width:{n_w} clip:{n_c} overflow:{n_o}')
        for sec, items in sorted(by_sec.items()):
            print(f'      #{sec}:')
            for it in items[:6]:
                if it['kind'] == 'width':
                    print(f'          [width]     {it["sel"]:28}  {it["w"]}px  (cap {it["cap"]}px)')
                elif it['kind'] == 'clip':
                    print(f'          [clip]      {it["sel"]:28}  starts at {it["top"]}px  (needs >= {it["hdr"]}px to clear header)')
                elif it['kind'] == 'overflow':
                    print(f'          [overflow]  {it["sel"]:28}  +{it["over"]}px past viewport  (w={it["w"]})')
    print()
    if total_fail == 0:
        print('VERIFIED — all pages fit the laptop viewport with header clearance and width cap.')
        return 0
    print(f'FAILED — {total_fail} page(s) have viewport-fit issues.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
