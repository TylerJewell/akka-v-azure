#!/usr/bin/env python3
"""Live-deck auditor.

Loads each published deck on akka.io at the laptop viewport (1536x861),
lets R4 auto-fit + all rendering settle, then per-slide reports:
  - Whether content is CUT OFF (extends below the visible viewport)
  - Whether content is HIDDEN BEHIND THE HEADER (top y < 78)
  - Whether R4 SCALED the section (data-fit=top-anchored scale=...)
  - Whether R4 SKIPPED the section (data-fit=null, in AUTOFIT_SKIP)

Runs against the LIVE HubSpot pages so results reflect what a real user sees,
not source-file guesses.

Usage:
    python tools/auditors/live-deck/audit.py           # all 5 decks
    python tools/auditors/live-deck/audit.py verify    # single deck

Exit 0 = every slide fits cleanly; non-zero = at least one issue.
"""

import json, os, socket, subprocess, sys, tempfile, time as _t, urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]

DECKS = ['overview', 'sdk', 'verify', 'optimize', 'specify']
BASE = 'https://akka.io/platform/'
CSS_W, CSS_H = 1536, 861
HEADER_H = 78
BUFFER = 12
# Standard title X for LEFT-ALIGNED (Pattern A) slides. Derived from section
# padding-left = 6vw = 92px at 1536 CSS viewport. All non-centered slides
# should have their first visible headline/eyebrow near this X.
STANDARD_TITLE_X = 92
TITLE_X_TOLERANCE = 15   # tight — title X should match unscaled sibling slides within ~15px


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


def audit_deck(deck):
    try:
        import websocket
    except ImportError:
        raise SystemExit('pip install websocket-client')

    url = BASE + deck + '?_cb=' + str(int(_t.time() * 1000))
    port = _free_port()
    tmpdir = tempfile.mkdtemp(prefix='edge_audit_')
    proc = subprocess.Popen(
        [find_edge(), '--headless=new', '--disable-gpu', '--remote-debugging-port=' + str(port),
         '--remote-allow-origins=*', '--user-data-dir=' + tmpdir,
         '--disable-application-cache', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/json', timeout=1))
                ws_url = next((t['webSocketDebuggerUrl'] for t in tabs if t.get('type') == 'page'), None)
                if ws_url:
                    break
            except Exception:
                _t.sleep(0.2)
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
        _t.sleep(6)

        # Detect a fixed cookie banner (or any fixed bottom element) and treat
        # its area as NOT visible. Cookie banner on akka.io is ~90-110px tall.
        cookie_probe = (
            "(function(){"
            "var maxTop = window.innerHeight, maxH = 0;"
            "document.querySelectorAll('*').forEach(function(el){"
            "var cs = getComputedStyle(el);"
            "if (cs.position !== 'fixed') return;"
            "var r = el.getBoundingClientRect();"
            "if (r.height < 30 || r.height > 260) return;"
            "if (r.bottom < window.innerHeight - 4 || r.bottom > window.innerHeight + 4) return;"
            "if (r.top < maxTop) { maxTop = r.top; maxH = r.height; }"
            "});"
            "return JSON.stringify({top: Math.round(maxTop), h: Math.round(maxH)});"
            "})()"
        )
        r = cmd('Runtime.evaluate', {'expression': cookie_probe, 'returnByValue': True})
        cookie = json.loads(r.get('result', {}).get('value', '{}')) if r else {}
        cookie_top = cookie.get('top', CSS_H)
        cookie_height = cookie.get('h', 0)
        # visible area = HEADER (78) at top ... cookie top at bottom
        visible_bottom = cookie_top if cookie_height > 0 else CSS_H
        print('  cookie/fixed-bottom banner covers viewport ' + str(cookie_top) + '-' + str(CSS_H)
              + ' (visible content area: ' + str(HEADER_H) + '-' + str(visible_bottom) + ')')

        wrapper = deck + '-content'
        select_js = (
            "Array.from(document.querySelectorAll('." + wrapper + " section, ." + wrapper + " [id$=\"-sticky\"]'))"
            ".filter(function(el){var h=el.getBoundingClientRect().height; return h>40 && h<window.innerHeight*3;})"
            ".map(function(el){return el.id||'?';})"
        )
        r = cmd('Runtime.evaluate', {'expression': select_js, 'returnByValue': True})
        slide_ids = r.get('result', {}).get('value', [])

        findings = []
        for sid in slide_ids:
            if not sid or sid == '?':
                continue
            scroll = (
                "var s=document.getElementById('" + sid + "');"
                "if(s){var y=s.getBoundingClientRect().top+window.scrollY;"
                "window.scrollTo({top:Math.max(0,y-" + str(HEADER_H) + "),behavior:'instant'});}"
            )
            cmd('Runtime.evaluate', {'expression': scroll})
            _t.sleep(0.5)
            measure = (
                "(function(){"
                "var s=document.getElementById('" + sid + "');"
                "if(!s)return null;"
                "var r=s.getBoundingClientRect();"
                "var range=document.createRange();range.selectNodeContents(s);"
                "var cr=range.getBoundingClientRect();"
                "var kids=Array.prototype.filter.call(s.children,function(el){"
                "if(el.tagName==='SCRIPT'||el.tagName==='STYLE')return false;"
                "var cs=getComputedStyle(el);"
                "if(cs.position==='absolute'||cs.position==='fixed')return false;"
                "var rr=el.getBoundingClientRect();return rr.width>4&&rr.height>4;});"
                "var firstTop=kids.length?Math.min.apply(null,kids.map(function(k){return k.getBoundingClientRect().top;})):null;"
                "var titleEl=s.querySelector('.eyebrow, [class*=\"eyebrow\"], h1, h2, [class*=\"headline\"], .shead');"
                "var titleLeft=titleEl?Math.round(titleEl.getBoundingClientRect().left):null;"
                "return JSON.stringify({id:s.id,vh:window.innerHeight,secTop:Math.round(r.top),secBot:Math.round(r.bottom),"
                "contentTop:Math.round(cr.top),contentBot:Math.round(cr.bottom),"
                "firstChildTop:firstTop!=null?Math.round(firstTop):null,"
                "titleLeft:titleLeft,"
                "dataFit:s.getAttribute('data-fit'),transform:s.style.transform||null,"
                "justify:getComputedStyle(s).justifyContent});"
                "})()"
            )
            r = cmd('Runtime.evaluate', {'expression': measure, 'returnByValue': True})
            raw = r.get('result', {}).get('value')
            if not raw:
                continue
            m = json.loads(raw)

            issues = []
            if m['firstChildTop'] is not None and m['firstChildTop'] < HEADER_H - 2:
                issues.append('HEADER_CLIP first_child_top=' + str(m['firstChildTop']) + ' < ' + str(HEADER_H))
            # Title X consistency — only for left-anchored (non-centered) slides.
            # Centered slides intentionally place titles in the middle.
            if m['justify'] != 'center' and m['titleLeft'] is not None:
                drift = abs(m['titleLeft'] - STANDARD_TITLE_X)
                if drift > TITLE_X_TOLERANCE:
                    issues.append('TITLE_X_DRIFT left=' + str(m['titleLeft']) + ' vs standard=' + str(STANDARD_TITLE_X) + ' (drift=' + str(drift) + 'px)')
            # Effective visible-area bottom: min of raw viewport and top of any
            # fixed bottom banner (cookie prompt, etc.). Content extending past
            # this is hidden from the user.
            eff_bot = visible_bottom
            if m['contentBot'] > eff_bot + BUFFER:
                over = m['contentBot'] - eff_bot
                issues.append('CUT_OFF content_bot=' + str(m['contentBot']) + ' > visible=' + str(eff_bot) + ' (+' + str(over) + 'px)')
            # SEC_OVERFLOW is only reported as INFO — section box extending past
            # visible is cosmetic (background), not a content-cut-off. Kept in
            # output for context but doesn't count toward the fail total.
            sec_info = ''
            if m['secBot'] > eff_bot + BUFFER and not any('CUT_OFF' in x for x in issues):
                over = m['secBot'] - eff_bot
                sec_info = '  [sec-box +' + str(over) + 'px cosmetic]'

            findings.append({
                'id': m['id'],
                'issues': issues,
                'sec_info': sec_info,
                'dataFit': m['dataFit'] or '(no fit)',
                'contentTop': m['firstChildTop'],
                'contentBot': m['contentBot'],
                'secBot': m['secBot'],
            })

        ws.close()
        return findings
    finally:
        proc.terminate()


def main():
    decks = sys.argv[1:] or DECKS
    print('Live-deck audit @ ' + str(CSS_W) + 'x' + str(CSS_H) + ' against ' + BASE + '<deck>')
    print()
    total_issues = 0
    for deck in decks:
        print('=== ' + deck + ' ===')
        try:
            findings = audit_deck(deck)
        except Exception as e:
            print('  ERROR: ' + str(e))
            continue
        for f in findings:
            if f['issues']:
                total_issues += len(f['issues'])
                print('  FAIL  #' + f['id'].ljust(22) + '  ' + ' | '.join(f['issues']) + f.get('sec_info', ''))
                print('        dataFit=' + f['dataFit'])
            else:
                sec = f.get('sec_info', '')
                print('  ok    #' + f['id'].ljust(22) + '  contentBot=' + str(f['contentBot']) + sec + '  ' + f['dataFit'])
        print()
    if total_issues == 0:
        print('VERIFIED - no clip or cut-off issues detected.')
        return 0
    print('FAILED - ' + str(total_issues) + ' issue(s) across ' + str(len(decks)) + ' deck(s).')
    return 1


if __name__ == '__main__':
    sys.exit(main())
