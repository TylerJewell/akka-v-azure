#!/usr/bin/env python3
"""Uncaught-JS-exception auditor.

An uncaught error does not just log — it abandons the rest of the script block it
was thrown from. Everything registered after the throw never runs, and nothing
visible says so.

That is how the overview deck lost its keyboard navigation. `#s-morph` was
removed in the efficiency redesign, its script block still opened with an
unguarded `document.getElementById('s-morph').querySelector('.drawbox')`, and the
`keydown` handler at the end of that same block — the deck's entire PgDn/PgUp nav
— was never registered. PageDown fell through to the browser's native
scroll-one-viewport, which parks the reader between slides. Every layout auditor
passed, because the layout was correct; only the landing position was wrong.

Run it on a local file or a URL:

    python tools/auditors/js-errors/audit.py <file.html|url> [more…]

Exit 0 = no uncaught exceptions.
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time as _t
import urllib.request

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]
SETTLE = 9          # seconds; deck scripts register on load and on font-ready


def _free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]; s.close(); return port


def check(target, width=1536, height=861):
    try:
        import websocket
    except ImportError:
        raise SystemExit('pip install -r tools/auditors/requirements.txt')
    exe = next((p for p in EDGE_CANDIDATES if os.path.isfile(p)), None)
    if not exe:
        raise SystemExit('Edge not found.')
    url = (target if target.startswith(('http://', 'https://'))
           else 'file:///' + os.path.abspath(target).replace('\\', '/'))
    port = _free_port()
    tmp = tempfile.mkdtemp(prefix='edge_jserr_')
    proc = subprocess.Popen(
        [exe, '--headless=new', '--disable-gpu', '--remote-debugging-port=' + str(port),
         '--remote-allow-origins=*', '--user-data-dir=' + tmp, 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    errors = []
    try:
        ws_url = None
        for _ in range(80):
            try:
                tabs = json.load(urllib.request.urlopen(
                    'http://127.0.0.1:%d/json' % port, timeout=1))
                ws_url = next((t['webSocketDebuggerUrl'] for t in tabs
                               if t.get('type') == 'page'), None)
                if ws_url:
                    break
            except Exception:
                _t.sleep(0.2)
        ws = websocket.create_connection(ws_url, max_size=None, timeout=60)
        cid = [0]

        def cmd(method, params=None):
            cid[0] += 1
            ws.send(json.dumps({'id': cid[0], 'method': method, 'params': params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get('method') == 'Runtime.exceptionThrown':
                    d = m['params']['exceptionDetails']
                    frames = ((d.get('stackTrace') or {}).get('callFrames') or [{}])
                    errors.append({
                        'text': d.get('text', ''),
                        'desc': str((d.get('exception') or {}).get('description', ''))
                                .split('\n')[0][:150],
                        'url': frames[0].get('url') or d.get('url') or '',
                        'line': d.get('lineNumber'),
                    })
                if m.get('id') == cid[0]:
                    return m.get('result', {})

        cmd('Runtime.enable'); cmd('Page.enable')
        cmd('Emulation.setDeviceMetricsOverride', {
            'width': width, 'height': height, 'deviceScaleFactor': 1,
            'mobile': False, 'screenWidth': width, 'screenHeight': height})
        cmd('Page.navigate', {'url': url})
        _t.sleep(SETTLE)
        cmd('Runtime.evaluate', {'expression': '1'})   # flush pending events
        ws.close()
    finally:
        proc.terminate()
    return errors


def main():
    targets = sys.argv[1:]
    if not targets:
        print(__doc__.strip().splitlines()[-3].strip(), file=sys.stderr)
        return 2
    bad = 0
    for t in targets:
        errs = check(t)
        if not errs:
            print('  ok    %s' % t)
            continue
        bad += len(errs)
        print('  FAIL  %s  (%d uncaught)' % (t, len(errs)))
        for e in errs:
            where = e['url'].rsplit('/', 1)[-1] or '(inline)'
            print('        %s  [%s:%s]' % (e['desc'] or e['text'], where, e['line']))
    print()
    if bad:
        print('FAILED - %d uncaught exception(s). Everything registered after a '
              'throw never ran.' % bad)
        return 1
    print('VERIFIED - no uncaught exceptions.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
