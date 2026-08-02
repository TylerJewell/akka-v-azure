"""Audit vertical rhythm and column alignment on the Akka Agentic AI Platform slide.

Three things the eye notices on this slide, each measured rather than judged:

  SUBTITLE_GAP  the graphic sitting too close under the subtitle
  TEXT_TOP      the right-hand copy not starting level with the top box
  TEXT_BOTTOM   the right-hand copy not ending level with the bottom box

Usage:
    python tools/auditors/slide-align/audit.py <url> [--width 1536] [--height 861]

Exit status is 1 while any check fails, so it can gate a build.
"""
import argparse, json, os, socket, subprocess, sys, tempfile
import time as _t, urllib.request

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

# Minimum breathing room between the subtitle's last line and the top of the
# graphic. Below this the graphic reads as attached to the subtitle.
MIN_SUBTITLE_GAP = 40
# The copy is meant to start level with the top box and finish level with the
# bottom one. A few pixels are invisible; a line height is not.
ALIGN_TOLERANCE = 12

MEASURE = r"""
(function(){
  var sec = document.querySelector('#s-akka-platform');
  if (!sec) return JSON.stringify({error: 'section #s-akka-platform not found'});

  /* Bring the slide into view so sticky/scroll-driven layout settles. */
  var y = sec.getBoundingClientRect().top + window.scrollY;
  window.scrollTo({top: Math.max(0, y - 78), behavior: 'instant'});

  function box(el){
    if (!el) return null;
    var r = el.getBoundingClientRect();
    return {top: Math.round(r.top), bottom: Math.round(r.bottom),
            left: Math.round(r.left), h: Math.round(r.height)};
  }
  /* Ink extent, not the element box: a block can be taller than its text. */
  function ink(el){
    if (!el) return null;
    var rg = document.createRange();
    rg.selectNodeContents(el);
    var r = rg.getBoundingClientRect();
    return {top: Math.round(r.top), bottom: Math.round(r.bottom),
            h: Math.round(r.height)};
  }

  var sub   = sec.querySelector('.ssub');
  var cake  = sec.querySelector('.cake');
  var msg   = sec.querySelector('.pf-msg');
  var cards = sec.querySelectorAll('.ocard');
  var paras = msg ? msg.querySelectorAll('p') : [];

  var firstCard = cards.length ? cards[0] : null;
  var lastCard  = cards.length ? cards[cards.length - 1] : null;
  var firstPara = paras.length ? paras[0] : null;
  var lastPara  = paras.length ? paras[paras.length - 1] : null;

  return JSON.stringify({
    subtitle:   ink(sub),
    cake:       box(cake),
    firstCard:  box(firstCard),
    lastCard:   box(lastCard),
    msg:        box(msg),
    msgInk:     ink(msg),
    firstPara:  ink(firstPara),
    lastPara:   ink(lastPara),
    paraCount:  paras.length,
    fontSize:   msg ? getComputedStyle(msg).fontSize : null,
    lineHeight: msg ? getComputedStyle(msg).lineHeight : null,
    vh: window.innerHeight
  });
})()
"""


def _free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def measure(url, width, height):
    try:
        import websocket
    except ImportError:
        raise SystemExit('pip install websocket-client')
    exe = next((p for p in EDGE_CANDIDATES if os.path.isfile(p)), None)
    if not exe:
        raise SystemExit('Edge not found.')
    port = _free_port()
    tmp = tempfile.mkdtemp(prefix='edge_align_')
    proc = subprocess.Popen(
        [exe, '--headless=new', '--disable-gpu', '--remote-debugging-port=' + str(port),
         '--remote-allow-origins=*', '--user-data-dir=' + tmp,
         '--disable-application-cache', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(
                    'http://127.0.0.1:%d/json' % port, timeout=1))
                ws_url = next((t['webSocketDebuggerUrl'] for t in tabs
                               if t.get('type') == 'page'), None)
                if ws_url:
                    break
            except Exception:
                _t.sleep(0.2)
        ws = websocket.create_connection(ws_url, max_size=None, timeout=40)
        cid = [0]

        def cmd(method, params=None):
            cid[0] += 1
            ws.send(json.dumps({'id': cid[0], 'method': method, 'params': params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == cid[0]:
                    return m.get('result', {})

        cmd('Page.enable'); cmd('Runtime.enable')
        cmd('Emulation.setDeviceMetricsOverride', {
            'width': width, 'height': height, 'deviceScaleFactor': 1,
            'mobile': False, 'screenWidth': width, 'screenHeight': height})
        cmd('Page.navigate', {'url': url})
        _t.sleep(6)
        cmd('Runtime.evaluate', {'expression': MEASURE, 'returnByValue': True})
        _t.sleep(1.2)          # let the scroll settle, then measure for real
        r = cmd('Runtime.evaluate', {'expression': MEASURE, 'returnByValue': True})
        ws.close()
        return json.loads(r['result']['value'])
    finally:
        proc.terminate()


def audit(url, width, height):
    d = measure(url, width, height)
    if d.get('error'):
        print('  ERROR: ' + d['error'])
        return ['section missing']

    fails = []
    print('  viewport %dx%d' % (width, height))

    gap = d['cake']['top'] - d['subtitle']['bottom']
    ok = gap >= MIN_SUBTITLE_GAP
    print('  SUBTITLE_GAP  subtitle ends %d, graphic starts %d -> %dpx (need >= %d)  %s'
          % (d['subtitle']['bottom'], d['cake']['top'], gap, MIN_SUBTITLE_GAP,
             'ok' if ok else 'FAIL'))
    if not ok:
        fails.append('SUBTITLE_GAP %dpx < %dpx' % (gap, MIN_SUBTITLE_GAP))

    dtop = d['firstPara']['top'] - d['firstCard']['top']
    ok = abs(dtop) <= ALIGN_TOLERANCE
    print('  TEXT_TOP      copy starts %d, top box starts %d -> %+dpx (tol %d)  %s'
          % (d['firstPara']['top'], d['firstCard']['top'], dtop, ALIGN_TOLERANCE,
             'ok' if ok else 'FAIL'))
    if not ok:
        fails.append('TEXT_TOP %+dpx' % dtop)

    dbot = d['lastPara']['bottom'] - d['lastCard']['bottom']
    ok = abs(dbot) <= ALIGN_TOLERANCE
    print('  TEXT_BOTTOM   copy ends %d, bottom box ends %d -> %+dpx (tol %d)  %s'
          % (d['lastPara']['bottom'], d['lastCard']['bottom'], dbot, ALIGN_TOLERANCE,
             'ok' if ok else 'FAIL'))
    if not ok:
        fails.append('TEXT_BOTTOM %+dpx' % dbot)

    print('  (copy %s/%s, %d paragraphs, ink %dpx; boxes span %dpx)'
          % (d['fontSize'], d['lineHeight'], d['paraCount'], d['msgInk']['h'],
             d['lastCard']['bottom'] - d['firstCard']['top']))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--width', type=int, default=1536)
    ap.add_argument('--height', type=int, default=861)
    a = ap.parse_args()
    print(a.url)
    fails = audit(a.url, a.width, a.height)
    print()
    if fails:
        print('FAIL: ' + '; '.join(fails))
        sys.exit(1)
    print('PASS: subtitle gap, top alignment and bottom alignment all within tolerance')


if __name__ == '__main__':
    main()
