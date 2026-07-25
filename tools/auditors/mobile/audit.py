#!/usr/bin/env python3
"""Mobile-overflow auditor.

Renders a deck page at a phone viewport and reports the elements that break past the right
edge — the cause of clipped titles and graphics that don't fit on mobile.

It flags "breakout" elements: an element whose right edge exceeds the viewport while its
parent still fits, i.e. the first thing to overflow (the actual culprit, not every descendant).

IMPORTANT — why CDP, not --window-size: headless Edge on Windows clamps --window-size to a
~496px OS-window minimum, so `--window-size=390` silently renders at 496px and the audit checks
the wrong width. This drives Edge over the DevTools Protocol and calls
Emulation.setDeviceMetricsOverride to force a TRUE mobile CSS viewport (verified: innerWidth
comes back exactly 390/360). Requires the `websocket-client` package.

Usage:
    python tools/auditors/mobile/audit.py [page.html] [width]
    defaults: akka-overview/index.html at 390px

Exit 0 = nothing overflows; non-zero = overflow culprits found.
"""

import os
import re
import sys
import json
import time
import socket
import subprocess
import tempfile
import urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

SCANNER = """
<style>.reveal,.pkg-reveal,.fam-reveal,.s6-reveal,.s13-reveal{opacity:1!important;transform:none!important}</style>
<script>
addEventListener('load', function(){ setTimeout(function(){
  var vw = window.innerWidth, out = [];
  document.querySelectorAll('section, section *').forEach(function(el){
    var r = el.getBoundingClientRect();
    if (r.width < 4 || r.right <= vw + 2) return;
    var p = el.parentElement, pr = p ? p.getBoundingClientRect() : null;
    if (pr && pr.right > vw + 2) return;              // parent also overflows -> not the breakout
    var sel = el.id ? '#'+el.id : (typeof el.className==='string' && el.className.trim()
              ? '.'+el.className.trim().split(/\\s+/).slice(0,2).join('.') : el.tagName.toLowerCase());
    var sec = (el.closest('section')||{}).id || '?';
    var txt = (el.textContent||'').trim().replace(/\\s+/g,' ').slice(0,44);
    out.push({sec:sec, sel:sel, over:Math.round(r.right-vw), w:Math.round(r.width), txt:txt});
  });
  // titles/copy that clip their own text (box fits, content doesn't)
  document.querySelectorAll('section h1,section h2,section h3,section p,'
    + 'section [class*="head"],section [class*="title"],section [class*="sub"]').forEach(function(el){
    var r = el.getBoundingClientRect();
    if (r.width < 40) return;
    if (el.scrollWidth > el.clientWidth + 3){
      var sec = (el.closest('section')||{}).id || '?';
      var sel = el.id ? '#'+el.id : (typeof el.className==='string' && el.className.trim()
                ? '.'+el.className.trim().split(/\\s+/).slice(0,2).join('.') : el.tagName.toLowerCase());
      out.push({sec:sec, sel:sel, over:el.scrollWidth-el.clientWidth, w:el.clientWidth,
                txt:(el.textContent||'').trim().replace(/\\s+/g,' ').slice(0,44), kind:'text-clip'});
    }
  });
  out.sort(function(a,b){return b.over-a.over;});
  document.title = 'MOBILE::' + JSON.stringify(out.slice(0,80));
}, 900); });
</script></head>
"""


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


def run(page, width):
    try:
        import websocket  # websocket-client
    except ImportError:
        raise SystemExit('Missing dependency for true-viewport CDP emulation. '
                         'Install with: pip install -r tools/auditors/requirements.txt')

    with open(page, 'r', encoding='utf-8') as f:
        html = f.read().replace('</head>', SCANNER, 1)
    tmp = os.path.join(tempfile.gettempdir(), 'mobile_audit_page.html')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(html)
    url = 'file:///' + tmp.replace('\\', '/')

    port = _free_port()
    proc = subprocess.Popen(
        [find_edge(), '--headless=new', '--disable-gpu', f'--remote-debugging-port={port}',
         '--remote-allow-origins=*', '--window-size=900,1600', 'about:blank'],
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
            'width': width, 'height': 1600, 'deviceScaleFactor': 1, 'mobile': True,
            'screenWidth': width, 'screenHeight': 1600})
        cmd('Page.navigate', {'url': url})

        # SCANNER stamps the result into document.title ~900ms after load; poll for it.
        payload = None
        for _ in range(50):
            time.sleep(0.2)
            title = cmd('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
            val = title.get('result', {}).get('value', '') or ''
            if val.startswith('MOBILE::'):
                payload = val[len('MOBILE::'):]
                break
        ws.close()
        if payload is None:
            raise SystemExit('Could not read scan result (page failed to render?).')
        return json.loads(payload)
    finally:
        proc.terminate()


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'akka-overview/index.html')
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 390
    findings = run(page, width)

    print(f'Mobile-overflow audit  ({os.path.relpath(page, ROOT)} @ {width}px)')
    print()
    if not findings:
        print('VERIFIED — nothing overflows the viewport.')
        return 0
    # group by section
    by_sec = {}
    for f in findings:
        by_sec.setdefault(f['sec'], []).append(f)
    print(f'FAILED — {len(findings)} element(s) overflow the {width}px viewport:\n')
    for sec, items in sorted(by_sec.items(), key=lambda kv: -max(i["over"] for i in kv[1])):
        print(f'  §{sec}:')
        for it in items[:8]:
            t = f'  “{it["txt"]}”' if it['txt'] else ''
            kind = ' [text-clip]' if it.get('kind') == 'text-clip' else ' [overflow]'
            print(f'      {it["sel"]:24}{kind} +{it["over"]}px  (w={it["w"]}){t}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
