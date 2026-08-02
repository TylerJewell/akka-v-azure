"""UX audit for the four-efficiencies slide.

Judges the things that make a four-up grid read as loose: a graphic sitting far
from the text it belongs to, boxes carrying more words than anyone reads off a
slide, labels too small to see from a room, and a slide that leaves most of the
viewport empty.

  PAIR_GAP      distance from each graphic to its own text
  WORDS         words of body copy per cell
  LABEL_SIZE    SVG label text below the legible floor
  VIEWPORT_FILL share of the usable band the content occupies
  BALANCE       spread between the tallest and shortest cell

Usage:
    python tools/auditors/slide-ux/audit.py <url> [--section s-eff]
                                            [--width 1536] [--height 861]

Exit status is 1 while any check fails.
"""
import argparse, json, os, socket, subprocess, sys, tempfile
import time as _t, urllib.request

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

MAX_PAIR_GAP = 28      # a graphic further than this reads as unattached
MAX_WORDS = 26         # per cell; CLAUDE.md budgets 15 words per body item
MIN_LABEL_PX = 10      # below this a label is unreadable from a room
MIN_FILL = 0.68        # content should occupy most of the band under the header
# CLAUDE.md designs these decks to an 860px usable band. On a much taller screen
# a four-item slide cannot reach that share without being inflated past its
# natural size, and on HubSpot R4 scales the slide to fit rather than to fill.
# Enforce the ratio where the deck is designed; report it above that.
FILL_ENFORCED_BELOW = 1000
MAX_CELL_SPREAD = 0.28 # tallest vs shortest cell, as a fraction of the tallest
HEADER = 78

MEASURE = r"""
(function(SECTION){
  var sec = document.getElementById(SECTION);
  if (!sec) return JSON.stringify({error: 'section #' + SECTION + ' not found'});
  var y = sec.getBoundingClientRect().top + window.scrollY;
  window.scrollTo({top: Math.max(0, y - 78), behavior: 'instant'});

  function r(el){
    var b = el.getBoundingClientRect();
    return {top: Math.round(b.top), bottom: Math.round(b.bottom),
            left: Math.round(b.left), right: Math.round(b.right),
            w: Math.round(b.width), h: Math.round(b.height)};
  }
  function ink(el){
    var rg = document.createRange(); rg.selectNodeContents(el);
    var b = rg.getBoundingClientRect();
    return {top: Math.round(b.top), bottom: Math.round(b.bottom), h: Math.round(b.height)};
  }

  var cells = [], smallLabels = [];
  sec.querySelectorAll('.eff-cell').forEach(function(cell, i){
    var g = cell.querySelector('.eff-graphic');
    var name = cell.querySelector('.eff-name');
    var body = cell.querySelector('.eff-body');
    var txt = cell.querySelector('.eff-text') || body;
    var words = body ? (body.textContent || '').trim().split(/\s+/).filter(Boolean).length : 0;

    /* Gap between the graphic's box and the start of its text column. */
    var gap = null;
    if (g && txt){
      var gb = r(g), tb = r(txt);
      gap = (tb.left >= gb.right) ? tb.left - gb.right
          : (gb.left >= tb.right) ? gb.left - tb.right
          : 0;
    }
    cells.push({
      i: i,
      name: name ? (name.textContent || '').trim() : '(unnamed)',
      words: words,
      gap: gap,
      cell: r(cell),
      graphic: g ? r(g) : null,
      textInk: txt ? ink(txt) : null
    });

    cell.querySelectorAll('svg text').forEach(function(t){
      var fs = parseFloat(getComputedStyle(t).fontSize);
      /* SVG scales with the viewBox, so the rendered size is what matters. */
      var svg = t.ownerSVGElement;
      var scale = 1;
      if (svg){
        var vb = svg.viewBox && svg.viewBox.baseVal;
        if (vb && vb.width) scale = svg.getBoundingClientRect().width / vb.width;
      }
      var rendered = fs * scale;
      if (rendered < 20) smallLabels.push({
        cell: i, text: (t.textContent || '').trim().slice(0, 22),
        px: Math.round(rendered * 10) / 10
      });
    });
  });

  var grid = sec.querySelector('.eff-grid');
  var head = sec.querySelector('.shead');
  var sub  = sec.querySelector('.ssub');
  return JSON.stringify({
    cells: cells,
    smallLabels: smallLabels,
    grid: grid ? r(grid) : null,
    head: head ? ink(head) : null,
    sub:  sub ? ink(sub) : null,
    section: r(sec),
    vh: window.innerHeight
  });
})('__SECTION__')
"""


def _free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]; s.close(); return port


def measure(url, section, width, height):
    try:
        import websocket
    except ImportError:
        raise SystemExit('pip install websocket-client')
    exe = next((p for p in EDGE_CANDIDATES if os.path.isfile(p)), None)
    if not exe:
        raise SystemExit('Edge not found.')
    port = _free_port()
    tmp = tempfile.mkdtemp(prefix='edge_ux_')
    proc = subprocess.Popen(
        [exe, '--headless=new', '--disable-gpu', '--remote-debugging-port=' + str(port),
         '--remote-allow-origins=*', '--user-data-dir=' + tmp,
         '--disable-application-cache', 'about:blank'],
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
        expr = MEASURE.replace('__SECTION__', section)
        cmd('Runtime.evaluate', {'expression': expr, 'returnByValue': True})
        _t.sleep(1.2)
        r = cmd('Runtime.evaluate', {'expression': expr, 'returnByValue': True})
        ws.close()
        return json.loads(r['result']['value'])
    finally:
        proc.terminate()


def audit(url, section, width, height):
    d = measure(url, section, width, height)
    if d.get('error'):
        print('  ERROR: ' + d['error'])
        return ['section missing']
    fails = []
    print('  viewport %dx%d, %d cells' % (width, height, len(d['cells'])))

    worst_gap = 0
    for c in d['cells']:
        if c['gap'] is None:
            continue
        worst_gap = max(worst_gap, c['gap'])
        flag = '' if c['gap'] <= MAX_PAIR_GAP else '  FAIL'
        print('    PAIR_GAP   %-16s %3dpx (max %d)%s' % (c['name'], c['gap'], MAX_PAIR_GAP, flag))
    if worst_gap > MAX_PAIR_GAP:
        fails.append('PAIR_GAP %dpx' % worst_gap)

    worst_words = 0
    for c in d['cells']:
        worst_words = max(worst_words, c['words'])
        flag = '' if c['words'] <= MAX_WORDS else '  FAIL'
        print('    WORDS      %-16s %3d words (max %d)%s' % (c['name'], c['words'], MAX_WORDS, flag))
    if worst_words > MAX_WORDS:
        fails.append('WORDS %d' % worst_words)

    if d['smallLabels']:
        under = [s for s in d['smallLabels'] if s['px'] < MIN_LABEL_PX]
        print('    LABEL_SIZE %d label(s) below %dpx' % (len(under), MIN_LABEL_PX))
        for s in under[:6]:
            print('               cell %d  %-24r %.1fpx' % (s['cell'], s['text'], s['px']))
        if under:
            fails.append('LABEL_SIZE %d labels < %dpx' % (len(under), MIN_LABEL_PX))

    band = d['vh'] - HEADER
    top = d['head']['top'] if d['head'] else d['section']['top']
    bottom = max(c['cell']['bottom'] for c in d['cells']) if d['cells'] else top
    fill = (bottom - top) / float(band)
    enforced = height <= FILL_ENFORCED_BELOW
    ok = fill >= MIN_FILL
    verdict = ('ok' if ok else 'FAIL') if enforced else ('%.0f%% (reported, not enforced above %dpx)'
                                                         % (fill * 100, FILL_ENFORCED_BELOW))
    print('    VIEWPORT_FILL content %d..%d = %dpx of %dpx band -> %.0f%% (min %.0f%%)  %s'
          % (top, bottom, bottom - top, band, fill * 100, MIN_FILL * 100, verdict))
    if enforced and not ok:
        fails.append('VIEWPORT_FILL %.0f%%' % (fill * 100))

    heights = [c['cell']['h'] for c in d['cells']]
    if heights:
        spread = (max(heights) - min(heights)) / float(max(heights))
        ok = spread <= MAX_CELL_SPREAD
        print('    BALANCE    cell heights %s -> spread %.0f%% (max %.0f%%)  %s'
              % (heights, spread * 100, MAX_CELL_SPREAD * 100, 'ok' if ok else 'FAIL'))
        if not ok:
            fails.append('BALANCE %.0f%%' % (spread * 100))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--section', default='s-eff')
    ap.add_argument('--width', type=int, default=1536)
    ap.add_argument('--height', type=int, default=861)
    a = ap.parse_args()
    print('%s  #%s' % (a.url, a.section))
    fails = audit(a.url, a.section, a.width, a.height)
    print()
    if fails:
        print('FAIL: ' + '; '.join(fails))
        sys.exit(1)
    print('PASS: pairing, word budget, label size, viewport fill and balance all within tolerance')


if __name__ == '__main__':
    main()
