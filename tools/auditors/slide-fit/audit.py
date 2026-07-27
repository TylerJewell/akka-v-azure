#!/usr/bin/env python3
"""Slide-fit auditor.

For each deck at the laptop CSS viewport (1536x960 per Tyler's 3072x1920 @
200% Windows scale), simulate the akka.io fixed header (78px) covering the top
of every section and measure whether the section's natural content height fits
within the visible area.

The visible area for content is:
    viewport_h - HEADER (78) - BUFFER (24, breathing room)  = 858 by default

For every section whose scrollHeight exceeds that budget, compute the zoom
factor needed to shrink the section's content so it fits without cut-off.

Emits JSON per section (deck, id, scroll_height, target, zoom) and a
paste-ready CSS block of per-section zoom rules under the deck's wrapper
class, keyed to the laptop-and-shorter media query.

Usage:
    python tools/auditors/slide-fit/audit.py [file.html ...]

  Default targets: akka-overview, akka-sdk, akka-verify + every
  sales-presentation/generated/*/index.html.

Exit 0 = every section fits at the laptop viewport with header clearance;
non-zero = at least one section will be cut off without a shrink rule.
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
HDR_H = 78
BUFFER = 24
TARGET = CSS_H - HDR_H - BUFFER  # 858

# Wrapper class per deck source path. If the file matches, we know the
# HubSpot-scope wrapper name to emit rules against.
WRAPPER = {
    'akka-overview/index.html': 'overview-content',
    'akka-sdk/index.html': 'sdk-content',
    'akka-verify/index.html': 'verify-content',
    'sales-presentation/generated/optimize/index.html': 'optimize-content',
    'sales-presentation/generated/specify/index.html': 'specify-content',
    'sales-presentation/generated/overview/index.html': 'overview-content',
}


SCANNER_TMPL = """
<style>.reveal,.pkg-reveal,.fam-reveal,.s6-reveal,.s13-reveal,.pp-reveal,.s5-reveal,.st-card,.cust-slide{opacity:1!important;transform:none!important}
/* Simulate the R2 port CSS locally so the audit reflects what HubSpot will render */
section{padding-top:88px !important;}
</style>
<script>
addEventListener('load', function(){ setTimeout(function(){
  var HDR = %d, BUFFER = %d;
  var out = [];
  document.querySelectorAll('section, [id$="-wrapper"] > [id$="-sticky"]').forEach(function(sec){
    var sid = sec.id || (sec.parentElement && sec.parentElement.id) || '?';
    var kids = Array.from(sec.children).filter(function(el){
      if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return false;
      var r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return false;
      // Skip absolute/fixed overlays (scroll hints, absolute-positioned slide layers)
      var cs = getComputedStyle(el);
      return cs.position !== 'absolute' && cs.position !== 'fixed';
    });
    if (!kids.length) return;
    // Measure natural content extent across all flow-level children.
    // Section itself may have overflow:hidden clipping the visible area, but
    // getBoundingClientRect still reports each child's laid-out position.
    var sr = sec.getBoundingClientRect();
    var tops = kids.map(function(el){ return el.getBoundingClientRect().top; });
    var bots = kids.map(function(el){ return el.getBoundingClientRect().bottom; });
    var contentTop = Math.min.apply(null, tops);
    var contentBot = Math.max.apply(null, bots);
    var contentH = contentBot - contentTop;
    // The section's rendered (visible) area. For fixed-height sticky patterns,
    // this reflects the pinned height. For min-height:100dvh, it's the viewport.
    var visibleH = sec.clientHeight;
    // Available vertical budget for content once the header overlay is layered on top.
    var target = visibleH - HDR - BUFFER;
    if (contentH > target) {
      var zoom = Math.floor((target / contentH) * 100) / 100;
      out.push({sec: sid, contentH: Math.round(contentH), visibleH: visibleH, target: target, zoom: zoom});
    }
  });
  document.title = 'SLIDEFIT::' + JSON.stringify(out);
}, 1500); });
</script></head>
""" % (HDR_H, BUFFER)


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
    tmp = os.path.join(tempfile.gettempdir(), 'slide_fit_audit.html')
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
            if val.startswith('SLIDEFIT::'):
                payload = val[len('SLIDEFIT::'):]
                break
        ws.close()
        if payload is None:
            raise SystemExit(f'Could not read scan result for {page}.')
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
    print(f'Slide-fit audit  @ {CSS_W}x{CSS_H} CSS  (header={HDR_H}px, buffer={BUFFER}px, target={TARGET}px)')
    print()
    # Group results by wrapper class for CSS emission
    by_wrapper = {}
    total_fail = 0
    for page in targets:
        rel = os.path.relpath(page, ROOT).replace('\\', '/')
        try:
            findings = run(page)
        except SystemExit as e:
            print(f'  {rel:60}  SKIP  {e}')
            continue
        wrapper = WRAPPER.get(rel)
        if not findings:
            print(f'  {rel:60}  ok')
            continue
        total_fail += 1
        print(f'  {rel:60}  {len(findings)} section(s) overflow')
        for f in findings:
            print(f'      #{f["sec"]:<24}  content {f["contentH"]}px vs target {f["target"]}px  -> zoom {f["zoom"]}')
            if wrapper:
                by_wrapper.setdefault(wrapper, []).append(f)

    if by_wrapper:
        print()
        print('=== Suggested per-section zoom rules (paste into port CSS) ===')
        print()
        for wrapper, items in by_wrapper.items():
            # Dedupe by section id, keep the smallest zoom (most aggressive shrink)
            best = {}
            for it in items:
                cur = best.get(it['sec'])
                if cur is None or it['zoom'] < cur['zoom']:
                    best[it['sec']] = it
            print(f'/* Per-section shrink for .{wrapper} at laptop viewport */')
            print(f'@media (min-width: 1001px) and (max-height: 1000px) {{')
            for sid, it in sorted(best.items()):
                print(f'  .{wrapper} #{sid} {{ zoom: {it["zoom"]}; }}')
            print('}')
            print()

    print()
    if total_fail == 0:
        print('VERIFIED - every section fits the laptop viewport with header clearance.')
        return 0
    print(f'FAILED - {total_fail} page(s) have sections that will be cut off.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
