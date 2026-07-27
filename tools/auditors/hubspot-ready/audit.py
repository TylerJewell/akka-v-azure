#!/usr/bin/env python3
"""HubSpot-readiness auditor.

Embeds the porting rules from the akka.io HubSpot operating guide
(TYLER_HUBSPOT_GUIDE, portal 45500578) so every deck/page change is checked for
the known theme/CSS/terminology traps BEFORE it is pushed into HubSpot. Run it on
any HubSpot-bound file — a generated fragment, or a source deck you are about to
port (e.g. akka-sdk/index.html):

    python tools/auditors/hubspot-ready/audit.py [file ...]
    (no args -> the generated HubSpot fragments globbed below)

Results come in three classes:
  1. PORT-TIME CSS REMINDERS — the publish transforms fix these automatically
     (var()->hex, color/font swaps, CSS scoping). Informational; never fails.
  2. CONTENT REMINDERS       — guide §8 copy rules a human/script must apply by
     hand. Context-dependent, so surfaced (with file:line) rather than failed.
  3. FAILURES                — clear traps the port will NOT fix. Non-zero exit.

Checks (each cites a guide section):
  CSS / theme, auto-handled by the port (§4-6, §18):
    - var(--...) refs                theme-overrides.css hijacks --black/--white/... (§4)
    - unscoped body{ / html{ / *{}   must be scoped under the page wrapper class (§4)
    - off-brand hex                  #4A9EFF/#ff6b60/#ff8a80/#ff5a4d/#28C840/#F5C518 (§5)
    - Roboto / Roboto Mono           only Instrument Sans; mono for code only (§6)
    - font-size:inherit!important    pulls the parent (16px) size, not yours (§6, §18)
  Content, manual & context-dependent (§8):
    - "the/The Akka" (+ punctuation)  the brand is never preceded by an article (§8)
    - "Akka Agentic AI Platform"      say "Akka" outside the Agentic Opportunity block (§8)
  Hard fails:
    - overflow-x:hidden              kills position:sticky; use overflow-x:clip (§18)
    - "AKKA" all-caps in prose       use "Akka" / the inlined SVG logo (§6)

NOT auditable from content (process rules — enforced by the publish flow, listed
here so this file stays the single rule reference):
    - create pages as DRAFT; never API-publish unless told (§2, §11)
    - upload templates to BOTH draft AND published source-code endpoints (§10)
    - edit live pages in place via Source Code API; never re-run publish (§12)
    - header/menu/footer come from the global partials; the mega-menu & footer
      are modules edited via the Source Code API, PUT to draft+published (§3, §15)
    - one wrapper class per page type; strip colons from the template YAML label (§9)
    - never upload standalone files to HubFS — inline into existing partials (§9)

PORT TRANSFORM CHECKLIST — CSS the scoped styles partial MUST append (lessons from
porting the SDK / Optimize / Overview decks, 2026-07-25). The akka.io theme wins on
each of these unless the port overrides it under the wrapper class (WRAPPER =
.sdk-content, .overview-content, …):
    1. Width cap   — .content-wrapper, .row-fluid(-wrapper), .widget-span,
                     body > .container-fluid { max-width:none !important; padding/margin:0 }
                     (else content is capped to a narrow column on wide monitors).
    2. Headings    — WRAPPER h1..h6 { color:#F1F1F1 !important; font-family:Instrument Sans !important }
                     (theme greys headings to #4E4E4E; a zero-specificity :where() rule loses).
    3. Tables      — WRAPPER table td/th { background:transparent !important;
                     border-top/left/right:0 !important } (theme draws a full cell grid; keep
                     the deck's own bottom-border row separators).
    4. Blockquotes — WRAPPER blockquote { border:0 !important; background:transparent !important;
                     padding:0 !important } (theme boxes quotes into callouts).
    5. Cake grid   — stack the integrated-platform cake (.fam-grid / .pf-grid) at
                     max-width:1250px, NOT 900 (it overflows its column between ~900-1250px).
    6. Assets      — rewrite path-relative src/href (iframes, images, demos) to ABSOLUTE
                     akka.io URLs; host demos on /hubfs (akka.io/hubfs/…). Never leave them
                     relative (404 under the page slug) or on github.io (external dependency).
                     [checked automatically below]
    7. Header offset — the akka.io header is position:fixed, 78px desktop / 64px mobile.
                     Section eyebrows / stat rows that sit at padding-top:48-64px get
                     clipped by the header (seen on #s-scale and #s6 in the Overview deck).
                     Append to the port CSS:
                       @media (min-width:1001px){
                         WRAPPER section{ padding-top:88px !important; }
                         /* sticky slides need their own: */
                         WRAPPER #<sticky-section>{ top:78px !important; height:calc(100dvh - 78px) !important; }
                       }
                       @media (max-width:1000px){ WRAPPER section{ padding-top:74px !important; } }
                     Local view is unaffected — port-only rule. Preserves existing
                     padding-bottom/side values from the shorthand.

FULL DEPLOY PLAYBOOK — see PUBLISHING.md (co-located) for the end-to-end procedure
(verified 2026-07-27): deck & compare port+split (scope, 3 partials, the preserved
port-CSS block, sticky-slide 78px header offset, injecting the compare reveal script);
blog edit/retire (hide_from_listing keeps the URL live — never unpublish); slug rename +
explicit 301 redirects; the hardcoded mega-menu module + by-ID homepage button; Files/demos
(folderId not folderPath); source-code push (draft+published = live); no shareable draft preview.

Exit 0 = no failures; non-zero = failure(s) found.
"""

import os
import re
import sys
import glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

DEFAULT_GLOBS = [
    'sales-presentation/generated/*/hubspot.html',
    'case-studies/hubspot/*.html',
    'comparisons/hubspot/*.html',
]

# --- CSS / theme traps the port transforms fix automatically (WARN) ---
VAR_REF = re.compile(r'var\(--(?!pad-)[a-z0-9-]+\)', re.I)          # --pad-* are theme-safe
OFF_BRAND_HEX = re.compile(r'#(?:4A9EFF|ff6b60|ff8a80|ff5a4d|28C840|F5C518)\b', re.I)
ROBOTO = re.compile(r'Roboto(?:\s+Mono)?', re.I)
UNSCOPED_BODY = re.compile(r'(?<![-\w.])body\s*\{')
UNSCOPED_HTML = re.compile(r'(?<![-\w.])html\s*\{')
UNSCOPED_STAR = re.compile(r'(?<![.\w-])\*\s*[,{][^{}]*box-sizing')  # universal reset needs scoping
FONT_INHERIT = re.compile(r'font-size\s*:\s*inherit\s*!important')

# --- content copy rules that need a human edit (CONTENT REMINDERS) ---
ARTICLE_BRAND = re.compile(r'\b[Tt]he Akka(?=[.,;:)!?"\']|\s*$)', re.M)
FULL_PRODUCT = re.compile(r'\bAkka Agentic AI Platform\b')

# --- path-relative asset refs (iframes/images/demos): they 404 on HubSpot because they
# resolve under the page slug, not the deck root. The port must rewrite them to absolute
# akka.io URLs (host demos on /hubfs). Excludes absolute/root/anchor/data/mailto/HubL. ---
REL_ASSET = re.compile(
    r'(?:src|href)\s*=\s*"(?!https?:|//|/|#|data:|mailto:|tel:|\{\{)'
    r'([^"]+\.(?:html?|png|jpe?g|svg|gif|webp|js|css|pdf|mp4|webm|json)[^"]*)"', re.I)

# --- hard fails the port will NOT fix ---
OVERFLOW_HIDDEN = re.compile(r'overflow-x\s*:\s*hidden')
AKKA_CAPS = re.compile(r'\bAKKA\b')

STYLE_BLOCK = re.compile(r'<style[^>]*>.*?</style>', re.S | re.I)
SCRIPT_BLOCK = re.compile(r'<script[^>]*>.*?</script>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')

WARN_CSS = [
    (VAR_REF, 'var(--) reference — theme-overrides.css hijacks these; the port hardcodes the hex (guide §4)'),
    (OFF_BRAND_HEX, 'off-brand color — the port swaps to the Akka palette (guide §5 replacement table)'),
    (ROBOTO, 'Roboto/Roboto Mono — the port swaps to Instrument Sans (guide §6)'),
    (UNSCOPED_BODY, 'unscoped "body {" — the port scopes it under the wrapper class (guide §4)'),
    (UNSCOPED_HTML, 'unscoped "html {" — the port scopes it under the wrapper class (guide §4)'),
    (UNSCOPED_STAR, 'unscoped "* { box-sizing }" — the port rewrites it to ".wrapper, .wrapper *" (guide §4)'),
    (FONT_INHERIT, 'font-size:inherit!important — pulls the parent (16px) size; use a targeted override (guide §6/§18)'),
]

# Content rules (guide §8). The CSS port transforms do NOT fix these — they need a
# manual/scripted copy edit and are context-dependent (e.g. the "Agentic Opportunity"
# block legitimately keeps the full product name), so they surface as reminders, not fails.
CONTENT_RULES = [
    (ARTICLE_BRAND, '"the Akka" — the brand is never preceded by an article; drop "the" (guide §8)'),
    (FULL_PRODUCT, '"Akka Agentic AI Platform" — use "Akka" outside the Agentic Opportunity block (guide §8)'),
]


def line_of(raw, idx):
    return raw.count('\n', 0, idx) + 1


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    rel = os.path.relpath(path, ROOT)
    css_warnings, content_reminders, fails = [], [], []

    # CSS traps scan the raw source (they live in <style>/inline attributes).
    for rx, msg in WARN_CSS:
        seen = set()
        for m in rx.finditer(raw):
            key = m.group(0).lower()
            if key in seen:
                continue
            seen.add(key)
            css_warnings.append(f'{rel}:{line_of(raw, m.start())}: {msg}  [{m.group(0)}]')

    # overflow-x:hidden is a hard fail (breaks sticky).
    for m in OVERFLOW_HIDDEN.finditer(raw):
        fails.append(f'{rel}:{line_of(raw, m.start())}: overflow-x:hidden — kills position:sticky; use overflow-x:clip (guide §18)')

    # Content rules and AKKA-caps scan visible text only (strip style/script/tags).
    text = TAG.sub(' ', SCRIPT_BLOCK.sub(' ', STYLE_BLOCK.sub(' ', raw)))
    for rx, msg in CONTENT_RULES:
        n = len(rx.findall(text))
        if n:
            content_reminders.append(f'{rel}: {msg}  ({n}×)')

    # Path-relative asset refs — scan raw (attributes are stripped from `text`).
    seen_assets = set()
    for m in REL_ASSET.finditer(raw):
        val = m.group(1)
        if val in seen_assets:
            continue
        seen_assets.add(val)
        content_reminders.append(
            f'{rel}:{line_of(raw, m.start())}: relative asset "{val}" — 404s on HubSpot; '
            f'rewrite to an absolute akka.io URL, host demos on /hubfs (port lesson)')

    for m in AKKA_CAPS.finditer(text):
        before = text[max(0, m.start()-30):m.start()]
        after = text[m.end():m.end()+30]
        prev = re.search(r'([A-Za-z]{2,})\s*$', before)
        nxt = re.search(r'^\s*([A-Za-z]{2,})', after)
        if (prev and prev.group(1).isupper()) or (nxt and nxt.group(1).isupper()):
            continue  # all-caps header run — allowed
        fails.append(f'{rel}: "AKKA" all-caps in mixed-case text — use "Akka" / SVG logo (guide §6)')

    return css_warnings, content_reminders, fails


def main():
    args = sys.argv[1:]
    if args:
        files = [f for f in args if os.path.isfile(f)]
    else:
        files = []
        for g in DEFAULT_GLOBS:
            files += glob.glob(os.path.join(ROOT, g))
        files = sorted(set(files))

    all_css, all_content, all_fails = [], [], []
    for f in files:
        c, r, fl = audit_file(f)
        all_css += c
        all_content += r
        all_fails += fl

    print('HubSpot-readiness audit')
    print(f'  files scanned: {len(files)}')
    print()
    if not files:
        print('No HubSpot fragments found to scan (build the decks first, or pass files).')
        return 0

    if all_css:
        # summarize the auto-handled CSS transforms by category rather than listing every hit
        cats = {}
        for w in all_css:
            key = w.split(': ', 1)[1].split(' — ')[0]
            cats[key] = cats.get(key, 0) + 1
        print('PORT-TIME CSS REMINDERS (auto-handled by the publish transforms — informational):')
        for k, n in sorted(cats.items(), key=lambda kv: -kv[1]):
            print(f'  · {n:4}×  {k}')
        print()

    if all_content:
        print(f'CONTENT REMINDERS (guide §8 — apply by hand when porting; context-dependent):')
        for p in all_content:
            print(f'  · {p}')
        print()

    if all_fails:
        print(f'FAILED — {len(all_fails)} content issue(s) the port will NOT fix:\n')
        for i, p in enumerate(all_fails, 1):
            print(f'{i:3}. {p}')
        return 1
    print('VERIFIED — no hard failures (reminders above are informational).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
