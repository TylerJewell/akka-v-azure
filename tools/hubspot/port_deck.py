#!/usr/bin/env python3
"""Generic per-deck HubSpot port.

Usage:
    python tools/hubspot/port_deck.py <deck>

<deck> ∈ {overview, sdk, verify, optimize, specify}

Reads the fresh source file, scopes CSS to the deck's wrapper class, preserves
the appended port-transform CSS block from the LIVE styles partial, appends the
R2 header-offset block, splits into styles/body/scripts, writes them to
scratchpad/hs-out/, then PUTs each to draft AND published under
`custom-templates/partials/<deck>-*.html`.
"""

import os, re, sys, json, subprocess

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'sales-presentation', 'builder'))
from hubspot import to_hubspot_fragment  # noqa: E402

HUBL_HEADER = '<!--\n  templateType: "none"\n  isAvailableForNewContent: false\n-->\n'


# R4 auto-fit v4 — runtime JS, works with the R5 top-anchored layout.
# Title sits at padding-top:90px. Content flows down from there. When natural
# content extent exceeds (viewport - 90 - buffer), scale from origin (50%, 90px)
# so the title stays put and content below shrinks to fit.
#
# For sections that intentionally stay centered (Pattern B — heroes, closes,
# cakes), R5 keeps justify-content:center, and the JS falls back to
# center-center scaling for those.
#
# Design (fixes v2's bottom-clip issue on 2026-07-27):
#   1. Transform on SECTION itself (v1 wrapped, which broke flex:1 layouts).
#   2. transform-origin: center center — scale symmetrically around center.
#   3. **Override overflow to visible before scaling.** THIS IS THE KEY FIX.
#      Sections have overflow:hidden in the base CSS, which clips content
#      that overflows the section box BEFORE transform is applied. For a 900px
#      content in an 852px section (justify-content:center), content spans
#      [-24, 876] naturally — overflow:hidden clips 24 top and 24 bottom
#      BEFORE the scale runs, so the resulting visual is missing chunks.
#      Setting overflow:visible during scale lets transform work on the full
#      natural content.
#   4. **No margin-bottom compensation.** v2 used
#      margin-bottom: -(sh*(1-scale)), which was wrong: it compressed sections
#      too aggressively and broke PgDn alignment. v3 lets sections stack at
#      natural 100dvh — PgDn scrolls exactly one viewport, each section aligns
#      cleanly. The visual gap between adjacent sections is section background
#      only, which is uniform.
#   5. Target = window.innerHeight - 2*(HDR + BUFFER). Since content is
#      justify-center'd in section, the tightest constraint is equal clearance
#      above the top and below the bottom of visible area.
#   6. Skips absolute/fixed overlays via getComputedStyle position check.
#   7. Re-measures on resize with rAF debounce; resets transforms and overflow
#      before re-measuring.
def _r4_runtime(wrapper, slide_wrappers=None, skip_ids=None, slugs=None):
    slide_wrappers = slide_wrappers or []
    skip_ids = skip_ids or []
    slugs = slugs or {}
    extra_selectors = ''.join(f', .{wrapper} {sid}' for sid in slide_wrappers)
    skip_check = (
        'if (' + ' || '.join(f"section.id === {sid[1:]!r}" for sid in skip_ids) + ') return;'
        if skip_ids else ''
    )
    # JSON serialize the id → slug map for JS
    slug_json = json.dumps(slugs)
    return f"""
<script>
/* === R4 auto-fit v4 (2026-07-27) — top-anchored scale for .{wrapper} === */
(function(){{
  /* Disable browser scroll-restoration so a stale saved scroll position from
     the previous visit doesn't yank the user back after PgDn on a fresh load. */
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

  /* Deep-link support with friendly slugs.
     id → slug map (both directions accepted in URL; slug wins on output). */
  var SLUG_BY_ID = {slug_json};
  var ID_BY_SLUG = {{}};
  Object.keys(SLUG_BY_ID).forEach(function(k){{ ID_BY_SLUG[SLUG_BY_ID[k]] = k; }});
  var HDR_LINK = 78;
  function resolveHash(hash) {{
    /* Accept either the friendly slug or the raw element id */
    if (ID_BY_SLUG[hash]) return ID_BY_SLUG[hash];
    if (document.getElementById(hash)) return hash;
    return null;
  }}
  function scrollToSlide(id, smooth) {{
    var el = document.getElementById(id);
    if (!el) return false;
    var y = el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
    window.scrollTo({{ top: Math.max(0, y - HDR_LINK), behavior: smooth ? 'smooth' : 'instant' }});
    return true;
  }}
  function initialScroll() {{
    var raw = (location.hash || '').replace(/^#/, '');
    if (!raw) return;
    var id = resolveHash(raw);
    if (!id) return;
    setTimeout(function(){{ scrollToSlide(id, false); }}, 300);
    setTimeout(function(){{ scrollToSlide(id, false); }}, 900);
  }}
  if (document.readyState === 'complete') initialScroll();
  else window.addEventListener('load', initialScroll);
  window.addEventListener('hashchange', function(){{
    var raw = (location.hash || '').replace(/^#/, '');
    var id = resolveHash(raw);
    if (id) scrollToSlide(id, true);
  }});
  /* Reflect current slide in URL hash using the FRIENDLY slug (falls back to
     raw id if no slug is mapped). Uses replaceState — no history spam. */
  var lastHash = null, hashRaf = 0;
  function updateHash() {{
    var vy = (window.scrollY || window.pageYOffset) + HDR_LINK + 20;
    var slides = document.querySelectorAll('.{wrapper} section[id], .{wrapper} [id$="-sticky"]');
    var best = null, bestY = -Infinity;
    slides.forEach(function(s){{
      var top = s.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
      if (top <= vy && top > bestY) {{ bestY = top; best = s; }}
    }});
    if (!best || !best.id) return;
    var slug = SLUG_BY_ID[best.id] || best.id;
    var nh = '#' + slug;
    if (nh === lastHash) return;
    lastHash = nh;
    try {{ history.replaceState(null, '', nh); }} catch (e) {{}}
  }}
  window.addEventListener('scroll', function(){{
    cancelAnimationFrame(hashRaf);
    hashRaf = requestAnimationFrame(updateHash);
  }}, {{ passive: true }});
  var HDR = 78;
  var BUFFER = 12;
  var TITLE_Y = 90;  /* matches R5 padding-top */
  /* Detect any position:fixed banner sitting at the viewport bottom (cookie
     prompt, chat widget, etc.) and treat that area as NOT part of the visible
     content zone. R4 targets shrink accordingly so scaled content clears it. */
  function bottomBannerHeight() {{
    var maxH = 0, vh = window.innerHeight;
    var els = document.querySelectorAll('*');
    for (var i = 0; i < els.length; i++) {{
      var el = els[i];
      var cs = getComputedStyle(el);
      if (cs.position !== 'fixed') continue;
      var r = el.getBoundingClientRect();
      if (r.height < 30 || r.height > 260) continue;
      if (r.bottom < vh - 4 || r.bottom > vh + 4) continue;
      if (r.height > maxH) maxH = r.height;
    }}
    return maxH;
  }}
  /* Cover ALL slide-level container patterns:
     - <section>
     - <div id="X-sticky"> (spec-sticky, stax-sticky, cog-sticky, ts*-sticky…)
     - EXPLICITLY-listed 100vh wrappers (pkg-wrapper, eco-wrapper, arc-wrapper)
     Never a blanket [id$="-wrapper"] — that catches scroll-range containers. */
  var SEL = '.{wrapper} section, .{wrapper} [id$="-sticky"]{extra_selectors}';

  function reset(section){{
    section.style.transform = '';
    section.style.transformOrigin = '';
    section.style.overflow = '';
  }}

  function isCentered(section){{
    /* R5 keeps some sections centered (heroes/closes). Detect via computed style. */
    return getComputedStyle(section).justifyContent === 'center';
  }}

  function isDesktop(){{ return window.innerWidth >= 1001; }}

  function fit(section){{
    reset(section);
    /* Mobile: fall back to the source CSS responsive layout entirely. Auto-fit
       only applies on desktop viewports where the fixed-header + 100dvh section
       pattern is in play. */
    if (!isDesktop()) return;
    /* Sections with designed internal scrolling (e.g. #cog-sticky's clipped
       dashboard track) must NOT be scaled — the tall content is intentional. */
    {skip_check}

    /* Read computed padding-top — sticky sections have padding-top:20 while
       non-sticky sections have padding-top:90. transform-origin depends on it. */
    var padTop = parseFloat(getComputedStyle(section).paddingTop) || 0;
    /* Measure natural content extent via Range.selectNodeContents(section).
       Rationale: scrollHeight gets clamped when the element has explicit
       height + overflow:hidden (which is exactly what our sticky overrides
       create). A Range covering the section's children returns their true
       visual bounding rect regardless of the container's overflow/height
       constraints, and it naturally picks up descendants inside
       display:contents wrappers (sp-02-specs .spec-diagram). */
    var range = document.createRange();
    range.selectNodeContents(section);
    var contentRect = range.getBoundingClientRect();
    var contentH = contentRect.height;
    /* If content bounding is empty (edge case: no children), fall back to
       scrollHeight minus padding. */
    if (contentH < 10) {{
      contentH = Math.max(0, section.scrollHeight - padTop);
    }}

    var vh = window.innerHeight;
    var centered = isCentered(section);
    /* Target — how much vertical space content can visually occupy WHEN the
       section is scrolled into view. Includes bottom banner (cookie prompt)
       subtraction so scaled content isn't hidden behind it. */
    var BOTTOM_BUFFER = 16;   /* tighter — reclaim vertical budget for content readability */
    var bottomBanner = bottomBannerHeight();
    var isSticky = getComputedStyle(section).position === 'sticky';
    /* Always include HDR in effective content top: nav go() scrolls sections to
       viewport y=HDR, and even without nav-hijack, sticky pins at y=HDR. */
    var effectiveContentTop = HDR + padTop;
    var target = centered
      ? vh - 2 * (HDR + BUFFER) - bottomBanner
      : vh - effectiveContentTop - BOTTOM_BUFFER - bottomBanner;
    if (contentH <= target) {{
      section.setAttribute('data-fit', 'fits contentH=' + Math.round(contentH) + ' target=' + Math.round(target) + ' vh=' + vh + ' padTop=' + padTop + ' sticky=' + isSticky);
      return;
    }}

    /* Floor scale at 0.7 — with reclaimed padding budget most sections don't
       need to shrink below 0.85 anyway. Only very tall slides push lower.
       Below 0.7 text becomes hard to read; content stays fit-priority. */
    var scale = Math.max(0.7, target / contentH);
    section.style.overflow = 'visible';
    section.style.transform = 'scale(' + scale + ')';
    /* Top-anchored: origin at the .inner's top-left corner (section padding-left,
       padTop). Standard title X across all decks is ~92px (section 6vw padding).
       Pinning origin there means the title stays exactly where it would on an
       unscaled sibling slide — no horizontal drift regardless of scale.
       Centered: origin at true center. */
    /* Origin at horizontal center + content-top. Scaled content stays visually
       centered in the viewport instead of clustering to the left with dead
       space on the right. Title X shifts inward with scale but overall slide
       feels balanced and matches the visual weight of unscaled sibling slides. */
    section.style.transformOrigin = centered ? '50% 50%' : ('50% ' + padTop + 'px');
    section.setAttribute('data-fit', (centered ? 'centered ' : 'top-anchored ') + 'scale=' + scale.toFixed(3) + ' contentH=' + Math.round(contentH) + ' target=' + Math.round(target) + ' vh=' + vh + ' padTop=' + padTop + ' sticky=' + isSticky);
  }}

  function fitAll(){{
    var vh = window.innerHeight;
    document.querySelectorAll(SEL).forEach(function(el){{
      /* Skip scroll-range wrappers (140vh+): they aren't slides, they're
         containers for a sticky inner child that IS the slide. */
      var h = el.getBoundingClientRect().height;
      if (h > vh * 1.4) return;
      fit(el);
    }});
    /* R5 centered-slide correction: chrome above the section (HubSpot theme
       often pushes .wrapper-content down 90-100px, more than the 78px header).
       Recompute exact offset needed for content to center in the VISIBLE
       viewport (header + rest) and apply as padding-bottom to shift the
       flex-centered content upward. */
    document.querySelectorAll(SEL).forEach(function(el){{
      if (getComputedStyle(el).justifyContent !== 'center') return;
      /* R5 only sizes these boxes at >=1001px. Below that the section keeps its
         full height, so this correction would compute a large padding and apply
         it late - the viewer sees the title jump up once the intro finishes.
         Match the media query and leave narrow layouts alone. */
      if (window.innerWidth < 1001) {{ el.style.paddingBottom = ''; return; }}
      /* Reset any prior correction so we measure a fresh state */
      el.style.paddingBottom = '';
      var rect = el.getBoundingClientRect();
      var chromeAbove = rect.top;          /* section top in viewport at scroll=0 */
      if (chromeAbove < 0 || chromeAbove > 300) return;  /* not on first screen */
      var visibleCenter = (HDR + vh) / 2;
      var sectionCenter = rect.top + rect.height / 2;
      var offset = sectionCenter - visibleCenter;
      if (offset > 4) {{
        /* Content is BELOW visible center. Add padding-bottom to shift the
           flex-centered content up by the amount needed. */
        el.style.paddingBottom = Math.round(offset * 2) + 'px';
      }}
    }});
  }}

  function schedule(){{
    /* First rAF pair handles the fast-path (CSS parsed, DOM laid out).
       Additional timeouts catch late-loading images, fonts, iframes that
       change section heights after load. */
    requestAnimationFrame(function(){{ requestAnimationFrame(fitAll); }});
    setTimeout(fitAll, 400);
    setTimeout(fitAll, 1200);
  }}

  if (document.readyState === 'complete') schedule();
  else window.addEventListener('load', schedule);

  var raf = 0;
  window.addEventListener('resize', function(){{
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(function(){{
      document.querySelectorAll(SEL).forEach(reset);
      requestAnimationFrame(fitAll);
    }});
  }});
}})();
</script>
"""


# Legacy stub kept only so the CSS side-of-things doesn't emit a stale R4 block
def _r4_shrink(wrapper):
    return ''


# Asset rewriting (rule 6). Relative iframe / href pointing to a local *.html
# becomes https://akka.io/hubfs/demos/<basename>. Skips absolute URLs, anchors,
# mailtos, and empty values.
def rewrite_assets(html):
    def repl_demo(m):
        prefix, val = m.group(1), m.group(2)
        if not val or val.startswith(('http:', 'https:', '#', 'mailto:', 'tel:', 'data:', '//', '/')):
            return m.group(0)
        # Only rewrite .html targets — leave anything else (css, js, etc.) alone
        if not val.endswith('.html'):
            return m.group(0)
        parts = val.rsplit('/', 1)
        filename = parts[-1]
        # If the file is named "index.html" inside a demo directory (e.g.
        # "risk-survey/index.html"), the HubFS file is <dirname>.html — not
        # index.html. Fix by using the directory name.
        if filename == 'index.html' and len(parts) == 2:
            filename = parts[0].rsplit('/', 1)[-1] + '.html'
        return f'{prefix}"https://akka.io/hubfs/demos/{filename}"'
    html = re.sub(r'((?:src|href)=)"([^"]*?)"', repl_demo, html)

    # Also rewrite background-image:url('images/...') inline styles to HubFS
    # image URLs (e.g. customer logos in the Runs-in-your-environment slide).
    def repl_bgimg(m):
        prefix, quote, val = m.group(1), m.group(2), m.group(3)
        if not val or val.startswith(('http:', 'https:', '/', 'data:', '//')):
            return m.group(0)
        # Convert relative image path (images/customers/foo.png) to HubFS
        # (akka.io/hubfs/images/customers/foo.png). Deck images are uploaded
        # under /hubfs/images/... during deck asset publishing.
        # Deck customer images live at /hubfs/akka-demo/images/... (per HubFS
        # files API search — see 2026-07-28 diagnostic). Map images/... -> akka-demo/images/...
        if val.startswith('images/'):
            return f"{prefix}{quote}https://akka.io/hubfs/akka-demo/{val}{quote}"
        return f"{prefix}{quote}https://akka.io/hubfs/{val}{quote}"
    html = re.sub(r"(background-image:\s*url\()(['\"]?)([^'\")]+)\2", repl_bgimg, html)
    return html

# Per-deck configuration. Sources per PUBLISHING.md §1.
# Per-deck lists of sections that INTENTIONALLY keep centered layout
# (hero, close, cake). Everything else defaults to top-anchored.
CENTERED_EXCEPTIONS = {
    # #s-routes is the shared integrated-platform cake, centred on every other
    # deck via #family. Keep the same slide framed the same way everywhere.
    'overview': ['#s-title', '#s-morph', '#s-close', '#s-routes'],
    'sdk':      ['#s0', '#s6', '#family'],
    'verify':   ['#s0', '#s8', '#family'],
    'optimize': ['#opt-title', '#opt-closing', '#family'],
    'specify':  ['#title', '#closing', '#family'],
}

# Per-deck lists of sticky sections that need explicit top:78px + height override
# so they pin below the fixed header instead of tucking under it.
STICKY_OVERRIDES = {
    'overview': ['#s6-wrapper #s6'],
    'sdk':      [],
    'verify':   [],
    'optimize': ['#cog-sticky'],
    'specify':  ['#spec-sticky', '#s5', '#fact-sticky', '#sdlc-sticky', '#proof-sticky'],
}

# Per-deck lists of -wrapper elements that ARE slides (100vh containers with
# content directly inside, no inner sticky child). Everything else in
# [id$="-wrapper"] is a scroll-range container (140vh+) and must NOT be
# treated as a slide.
SLIDE_WRAPPERS = {
    'overview': [],
    'sdk':      [],
    'verify':   [],
    'optimize': ['#eco-wrapper', '#arc-wrapper'],
    'specify':  [],
}

# Human-friendly deep-link slugs per deck. Format: real_id → friendly_slug.
# Deep-link JS accepts either; scroll-tracked URL prefers the friendly slug.
SLIDE_SLUGS = {
    'overview': {
        's-title': 'title',
        's-morph': 'enterprise-agentic-ai',
        's-proof': 'production-reliability',
        's-platform': 'resilience-and-scalability',
        's6': 'resilience-tester',
        's-scale': 'scalability',
        's-packages': 'deployment',
        's-routes': 'explore-platform',
        's-close': 'contact',
    },
    'sdk': {
        's0': 'title',
        's1': 'components',
        's13': 'innovations',
        's2': 'assemble-services',
        's4': 'production-ready',
        'family': 'platform',
        's6': 'contact',
    },
    'verify': {
        's0': 'title',
        's7': 'cost-of-getting-it-wrong',
        's1': 'production-readiness',
        's3': 'governance-mechanisms',
        's-risk': 'define-your-risk',
        's5': 'where-agents-run',
        'family': 'platform',
        's8': 'contact',
    },
    'optimize': {
        'opt-title': 'title',
        'ts1-sticky': 'problem',
        'ts2-sticky': 'economics',
        'ts4-sticky': 'prove',
        'ts3-sticky': 'target',
        'cog-sticky': 'console',
        'family': 'platform',
        'opt-closing': 'contact',
    },
    'specify': {
        'title': 'title',
        'spwhat': 'what-is-specify',
        'spec-sticky': 'specifications',
        's5': 'weeks-not-months',
        'platform-pattern': 'your-environment',
        'stax-sticky': 'labor-vs-spec-driven',
        'family': 'platform',
        'closing': 'contact',
    },
}


# Sections R4 auto-fit must NOT touch — they have designed internal scrolling
# or transform-based mechanisms that shouldn't be scaled by auto-fit.
# The dashboard's real height is much taller than the viewport by design, and
# the .cog-stage clip + .cog-track transform is the intended visualization.
AUTOFIT_SKIP = {
    'overview': [],
    'sdk':      [],
    'verify':   [],
    'optimize': ['#cog-sticky'],
    'specify':  [],
}


EXTRA_CSS = {
    'overview': '',
    'sdk':      '',
    'verify':   '',
    'optimize': """
  /* #opt-closing has min-height:760 in source which beats R5's calc(100dvh - 118px) — force override */
  .optimize-content #opt-closing { min-height: calc(100dvh - 200px) !important; }
""",
    'specify':  """
  /* Cookie banner covers the bottom ~114px. #closing is centred by R4, so lift its
     content block clear of the banner instead of letting the CTA nick it. */
  .specify-content #closing { padding-bottom: 114px !important; }
""",
}


def _r2r5_block(wrapper, centered, sticky, slide_wrappers, extra_css=''):
    """Combined R2 (header clearance) + R5 (unified top-anchored layout)."""
    centered_sel = ',\n  '.join(f'.{wrapper} {sid}' for sid in centered)
    sticky_sel = (
        ',\n  '.join(f'.{wrapper} {sid}' for sid in sticky)
        if sticky else ''
    )
    # Build the slide-level selector: sections, -sticky divs, and EXPLICITLY
    # listed 100vh -wrapper slides. Never a blanket [id$="-wrapper"] match —
    # scroll-range wrappers (140vh+) would incorrectly get slide treatment.
    slide_selectors = [f'.{wrapper} section', f'.{wrapper} [id$="-sticky"]']
    slide_selectors.extend(f'.{wrapper} {sid}' for sid in slide_wrappers)
    slide_sel = ',\n  '.join(slide_selectors)
    # Flat comma-separated version for :is(...) — must not include newlines
    slide_sel_flat = ', '.join(slide_selectors)
    sticky_block = (
        f"""
  /* Sticky sections: pin below the fixed header. Small padding-top (20px)
     because the top:78 override already positions the section below the
     header — the standard R5 padding-top:90 would DOUBLE the offset and
     push content way too low. */
  {sticky_sel} {{
    top: 78px !important;
    height: calc(100dvh - 78px) !important;
    min-height: calc(100dvh - 78px) !important;
    padding-top: 32px !important;   /* sticky sections: header at 78, so total top clearance = 110 */
  }}
""" if sticky else ''
    )
    return f"""
/* === R2 + R5 (2026-07-27) — header offset + unified top-anchored layout ===
   All desktop viewport rules are gated to min-width:1001px. Mobile falls back
   to the source CSS's own responsive rules.
   Slide-level containers targeted: sections, sticky divs, and explicit 100vh
   wrappers per deck. Scroll-range wrappers (140vh+) are NEVER matched. */
@media (min-width: 1001px) {{
  /* R5: default content slide is top-anchored with title at fixed y=32px
     from section top. Section top is at viewport y=78 (below fixed header),
     so title lands at viewport y=110 — tight but preserves ~100px of vertical
     budget we used to waste on padding, letting content stay at readable scale. */
  {slide_sel} {{
    justify-content: flex-start !important;
    padding-top: 32px !important;
  }}
  /* R5 inner-container override: many slides nest a *-inner div with its OWN
     justify-content:center + height:100%. That flex centering pushes content
     ABOVE the section's padding-top when content is tall, so the title hides
     under the fixed header. Force these inners to top-align + intrinsic height
     so the section's padding-top actually clears the header.
     Using :is() to combine slide-level selectors so ONE rule covers all
     .pp-inner descendants of any slide container (comma-splitting an inner
     selector across slide_sel would only put the descendant on the last item). */
  :is({slide_sel_flat}) :is(.pp-inner, .fam-inner, .pkg-inner, .stax-inner, .arc-inner, .eco-inner, .cog-inner, .inner) {{
    justify-content: flex-start !important;
    height: auto !important;
    max-height: none !important;
  }}
  /* R5 exceptions: intentional Pattern B (hero/close/cake) sections stay centered.
     Section box reduced by header + breathing room (78px header + 40px extra)
     so centered content doesn't creep under the fixed header when the section
     is scrolled to viewport top. Without the extra 40px, content ~600-700px
     tall centered in a 783px box lands only 5-40px below the header, visually
     touching it. */
  {centered_sel} {{
    justify-content: center !important;
    padding-top: 0 !important;
    min-height: calc(100dvh - 118px) !important;
    /* Source CSS for these sections sets an explicit height:100dvh, which beats
       min-height and leaves the box full-height. R4 then has to correct the
       centering late with padding-bottom, which the viewer sees as the content
       jumping up ~56px once the intro animation finishes. Override height so the
       box is already the right size at first paint and R4's correction is a no-op. */
    height: calc(100dvh - 118px) !important;
  }}
{sticky_block}
  /* Modest breathing between subtitle and following content — enough to
     separate visually but tight enough that supporting elements (icons,
     pills, small side rows) feel like they belong to the subhead, not a
     separate section. Was 60px which created huge dead gaps on slides like
     #s-packages where the cloud icons follow immediately from the subtext. */
  .{wrapper} section .ssub,
  .{wrapper} section .fam-sub,
  .{wrapper} section .pkg-sub,
  .{wrapper} [id$="-sticky"] .ssub,
  .{wrapper} [id$="-sticky"] .fam-sub {{ margin-bottom: 24px !important; }}
}}
/* Below R5's breakpoint the section keeps its full height, so R4's centering
   correction computes a large padding-bottom and applies it late - the viewer
   sees the title jump up once the intro animation finishes. R4 sets it as a
   non-important inline style, so !important here wins and keeps narrow layouts
   still. */
@media (max-width: 1000px) {{
  {centered_sel} {{ padding-bottom: 0 !important; }}
}}
/* Deep links (#slug) must land below the fixed header without a post-load
   correction. The browser's native anchor scroll puts the target at viewport 0,
   which is behind the 78px header; initialScroll() then fixes it at load, +300ms
   and +900ms, and the viewer sees the page jump. scroll-margin-top makes the
   native scroll land in the right place, so that correction becomes a no-op. */
.{wrapper} section,
.{wrapper} [id$="-sticky"],
.{wrapper} [id$="-wrapper"] {{ scroll-margin-top: 78px; }}
@media (max-width: 767px) {{
  .{wrapper} section,
  .{wrapper} [id$="-sticky"],
  .{wrapper} [id$="-wrapper"] {{ scroll-margin-top: 64px; }}
}}
{extra_css}
/* Rules that apply on all viewport sizes: */
/* Verify's #s7 has an inline text-align:center on the eyebrow + h2 that we neutralize */
.{wrapper} #s7 .eyebrow, .{wrapper} #s7 .shead {{ text-align: left !important; }}
/* Kill title-slide scroll hints (both desktop and mobile) */
.{wrapper} .scrollhint,
.{wrapper} .title-scroll-hint {{ display: none !important; }}
"""


DECKS = {
    'overview': {
        'src': 'akka-overview/index.html',
        'wrapper': 'overview-content',
    },
    'sdk': {
        'src': 'akka-sdk/index.html',
        'wrapper': 'sdk-content',
    },
    'verify': {
        'src': 'akka-verify/index.html',
        'wrapper': 'verify-content',
    },
    'optimize': {
        'src': 'sales-presentation/generated/optimize/index.html',
        'wrapper': 'optimize-content',
    },
    'specify': {
        'src': 'sales-presentation/generated/specify-draft/index.html',
        'wrapper': 'specify-content',
    },
}
# Populate each deck's r2 block from the shared builder
for _name, _cfg in DECKS.items():
    _cfg['r2'] = _r2r5_block(
        _cfg['wrapper'],
        CENTERED_EXCEPTIONS[_name],
        STICKY_OVERRIDES[_name],
        SLIDE_WRAPPERS[_name],
        EXTRA_CSS[_name],
    )
    _cfg['slide_wrappers'] = SLIDE_WRAPPERS[_name]
    _cfg['autofit_skip'] = AUTOFIT_SKIP[_name]
    _cfg['slugs'] = SLIDE_SLUGS[_name]


def read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def write(p, content):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)


def curl_get(env, partial):
    """GET the current live partial to preserve the appended port-CSS block."""
    token = os.environ.get('HUBSPOT_TOKEN', '')
    if not token:
        # source scratchpad/.hs_env manually
        env_txt = read(os.path.join(ROOT, 'scratchpad', '.hs_env'))
        m = re.search(r'HUBSPOT_TOKEN=(\S+)', env_txt)
        if m:
            token = m.group(1)
            os.environ['HUBSPOT_TOKEN'] = token
    url = f'https://api.hubapi.com/cms/v3/source-code/{env}/content/custom-templates/partials/{partial}'
    r = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {token}', url],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.stdout.decode('utf-8', errors='replace') if r.stdout else ''


def curl_put(env, partial, path):
    token = os.environ['HUBSPOT_TOKEN']
    url = f'https://api.hubapi.com/cms/v3/source-code/{env}/content/custom-templates/partials/{partial}'
    r = subprocess.run(['curl', '-s', '-w', '%{http_code}', '-X', 'PUT',
                        '-H', f'Authorization: Bearer {token}',
                        '-F', f'file=@{path}', url],
                       capture_output=True, text=True)
    # curl writes body then the %{http_code} at the very end
    body = r.stdout
    code = body[-3:] if body else '???'
    return code


def build(deck_name):
    cfg = DECKS[deck_name]
    src_path = os.path.join(ROOT, cfg['src'])
    src_html = read(src_path)
    fragment = to_hubspot_fragment(
        src_html,
        base_dir=os.path.dirname(src_path),
        scope=cfg['wrapper'],
        label=deck_name,
    )

    style_m = re.search(r'<style[^>]*>(.*?)</style>', fragment, re.S)
    fresh_css = style_m.group(1) if style_m else ''

    body_m = re.search(
        r'<div class="' + re.escape(cfg['wrapper']) + r'">(.*)</div>\s*$',
        fragment, re.S
    )
    fresh_body = ('<div class="' + cfg['wrapper'] + '">\n' + body_m.group(1).strip() + '\n</div>\n') if body_m else fragment

    scripts = []
    for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', fresh_body, re.S):
        scripts.append(m.group(0))
    fresh_body = re.sub(r'<script(?![^>]*\bsrc=)[^>]*>.*?</script>', '', fresh_body, flags=re.S)

    # Rewrite relative demo/html asset URLs -> absolute HubFS URLs (rule 6)
    fresh_body = rewrite_assets(fresh_body)

    # Grab the live port-CSS block. Fall back to nothing if missing (e.g. first port ever).
    # IMPORTANT: preserve only the ORIGINAL Neutralize block (rules 1-5), not any
    # previously-appended R2/R4 blocks — those get re-added fresh so we don't stack duplicates.
    live_styles = curl_get('published', f'{deck_name}-styles.html')
    m = re.search(r'(/\* === Neutralize HubSpot wrapper containers.*?)</style>', live_styles, re.S)
    existing_port_css = (m.group(1).rstrip() + '\n') if m else ''
    if existing_port_css:
        # Strip any previously-appended R2/R4/R5 blocks so re-ports don't
        # duplicate. Match both the old v1 headers (R2 header offset,
        # R4 shrink-to-fit) and the current combined R2+R5 header.
        for pat in [
            r'\n*/\* === R2 header offset.*?(?=/\* ===|$)',
            r'\n*/\* === R4 shrink-to-fit.*?(?=/\* ===|$)',
            r'\n*/\* === R2 \+ R5.*?(?=/\* ===|$)',
            r'\n*/\* Verify\'s #s7 has.*?text-align: left !important; \}',
            r'\n*/\* Kill title-slide scroll hints.*?display: none !important; \}',
            r'\n*/\* Breathing room between subtitle.*?margin-bottom: 60px !important; \}',
            r'\n*/\* Rules that apply on all viewport sizes.*?$',
        ]:
            existing_port_css = re.sub(pat, '', existing_port_css, flags=re.S)
        existing_port_css = existing_port_css.rstrip() + '\n'
    else:
        print(f'  WARN: no existing port-CSS block found in live {deck_name}-styles.html (fresh port?).')

    new_styles = (
        HUBL_HEADER +
        '<style>\n' +
        fresh_css.strip() +
        '\n\n' +
        existing_port_css +
        cfg['r2'] +
        _r4_shrink(cfg['wrapper']) +
        '</style>\n'
    )
    new_body = HUBL_HEADER + fresh_body.strip() + '\n<!-- DEMO_HTML_MARKER -->\n'
    new_scripts = (
        HUBL_HEADER +
        '\n'.join(scripts) +
        '\n' +
        _r4_runtime(cfg['wrapper'], cfg.get('slide_wrappers'), cfg.get('autofit_skip'), cfg.get('slugs')) +
        '\n<!-- DEMO_JS_MARKER -->\n'
    )

    out_dir = os.path.join(ROOT, 'scratchpad', 'hs-out')
    files = {}
    for kind, content in (('styles', new_styles), ('body', new_body), ('scripts', new_scripts)):
        p = os.path.join(out_dir, f'{deck_name}-{kind}.html')
        write(p, content)
        files[kind] = p
    return files


def push(deck_name, files):
    for env in ('draft', 'published'):
        for kind, path in files.items():
            partial = f'{deck_name}-{kind}.html'
            code = curl_put(env, partial, path)
            print(f'  PUT {env:<9}  {partial}  HTTP {code}')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in DECKS:
        print(f'usage: python {sys.argv[0]} <{"|".join(DECKS)}>', file=sys.stderr)
        return 2
    deck = sys.argv[1]
    print(f'=== Porting {deck} ===')
    files = build(deck)
    for kind, p in files.items():
        print(f'  built  {os.path.relpath(p, ROOT)}  ({os.path.getsize(p)} bytes)')
    push(deck, files)
    print(f'=== {deck} done ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
