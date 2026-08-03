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
def _r4_runtime(wrapper, slide_wrappers=None, skip_ids=None, slugs=None, retired=None):
    slide_wrappers = slide_wrappers or []
    skip_ids = skip_ids or []
    slugs = slugs or {}
    retired = retired or {}
    extra_selectors = ''.join(f', .{wrapper} {sid}' for sid in slide_wrappers)
    skip_check = (
        'if (' + ' || '.join(f"section.id === {sid[1:]!r}" for sid in skip_ids) + ') return;'
        if skip_ids else ''
    )
    # JSON serialize the id → slug map for JS
    slug_json = json.dumps(slugs)
    retired_json = json.dumps(retired)
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
  /* Slugs from an earlier cut of the deck, pointed at whichever section now
     carries their subject. Links to them are already shared, and without this a
     retired slug matches nothing and silently leaves the reader at the top. */
  var RETIRED = {retired_json};
  var HDR_LINK = 78;
  function resolveHash(hash) {{
    /* Accept either the friendly slug or the raw element id */
    if (ID_BY_SLUG[hash]) return ID_BY_SLUG[hash];
    if (document.getElementById(hash)) return hash;
    if (RETIRED[hash] && document.getElementById(RETIRED[hash])) return RETIRED[hash];
    return null;
  }}
  function scrollToSlide(id, smooth) {{
    var el = document.getElementById(id);
    if (!el) return false;
    var y = el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
    window.scrollTo({{ top: Math.max(0, y - HDR_LINK), behavior: smooth ? 'smooth' : 'instant' }});
    return true;
  }}
  function dropHash() {{
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }}
  /* The browser re-applies the URL fragment repeatedly while the document lays
     out, and updateHash() writes a slug into the URL as the reader scrolls, so
     any reload carries a fragment that drags them back to that slide mid-scroll.
     No script here does that scrolling. The cure is to remove the fragment the
     moment the reader takes over, which also stands the deferred deep-link pass
     down. Listen for input events, not 'scroll', so our own scrollTo calls do
     not cancel themselves. A hash written later by replaceState does not restart
     fragment scrolling, so the shareable-slug behaviour is unaffected. */
  var userScrolled = false;
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function(ev){{
    window.addEventListener(ev, function(){{ userScrolled = true; dropHash(); }},
      {{ passive: true, once: true }});
  }});
  /* Scrolling done before this inline script parsed never reaches the listeners
     above, and on a slow connection that window is several seconds wide. A fresh
     load sits at 0 (scrollRestoration is manual) and the browser's fragment jump
     leaves the target at the viewport top or one header height above it, so any
     other position means the reader has already moved. */
  (function(){{
    var raw = (location.hash || '').replace(/^#/, '');
    if (!raw) return;
    var y = window.scrollY || window.pageYOffset;
    if (y < 4) return;
    var el = document.getElementById(resolveHash(raw) || '');
    if (!el) return;
    var off = el.getBoundingClientRect().top + y;   /* target's document offset */
    if (Math.abs(y - off) > 120 && Math.abs(y - (off - HDR_LINK)) > 120) {{
      userScrolled = true;
      dropHash();
    }}
  }})();
  function initialScroll() {{
    var raw = (location.hash || '').replace(/^#/, '');
    if (!raw) return;
    var id = resolveHash(raw);
    if (!id) return;
    setTimeout(function(){{ if (!userScrolled) scrollToSlide(id, false); }}, 300);
    setTimeout(function(){{ if (!userScrolled) scrollToSlide(id, false); }}, 900);
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
    section.style.height = '';
  }}

  /* Snap points are spaced by a slide's LAYOUT height, and a wheel gesture moves
     one screen. A slide whose box is taller than the band therefore puts the next
     snap point further away than one gesture can travel, and with proximity the
     reader rests between slides with nothing locking on.

     A transform does not change layout, so a slide R4 has scaled to fit still
     occupies its unscaled height: overview's architecture slide measured 978px of
     scroll while showing 686px of content. Once the content is known to fit the
     band, the box should be the band — that also keeps the slide covering
     everything below it, so no strip of the next slide shows through. */
  function boxToBand(section, vh, isSticky){{
    if (isSticky) return;   /* sticky slides are sized by their own rule */
    if (getComputedStyle(section).position === 'sticky') return;
    var band = vh - HDR;
    /* offsetHeight, not getBoundingClientRect: the latter reports the SCALED box
       on a section R4 has transformed, which is the number that already looks
       fine. The layout height is what spaces the snap points. */
    if (section.offsetHeight <= band + 1) return;
    section.style.height = band + 'px';
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
    /* Centered sections are sized to the band below the header with 40px of
       padding-bottom, so their content box is vh - HDR - 40. Targeting less than
       that shrank content that already fitted, and a scaled box is inset from its
       layout box, which pushed the layout box up and let the next slide show
       below. Target the box we actually give them. */
    var CENTERED_PAD_BOTTOM = 40;
    var target = centered
      ? vh - HDR - CENTERED_PAD_BOTTOM - bottomBanner
      : vh - effectiveContentTop - BOTTOM_BUFFER - bottomBanner;
    if (contentH <= target) {{
      /* Fits without scaling, but the box can still be taller than the band —
         a source rule setting height:100dvh leaves it a full viewport tall. */
      if (!centered) boxToBand(section, vh, isSticky);
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
    /* The content now fits the band visually, so the box should be the band too.
       Left alone, the unscaled height keeps spacing the snap points. */
    if (!centered) boxToBand(section, vh, isSticky);
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

  /* Slides taller than one screen are scroll-through regions holding a pinned
     child. Each carries a single snap point, at its top, so a wheel gesture that
     ends inside one rests wherever momentum ran out — and in the last screen of
     the region, where the child unpins, that reads as a slide caught halfway.
     PageDown is unaffected because it computes slide tops directly.
     Dropping a zero-size snap anchor at every screen height gives those regions
     the same one-stop-per-screen behaviour the short slides get from their own
     boundaries, without shortening any animation. Anchors are absolutely
     positioned and inert, so they add nothing to layout. */
  function snapAnchors(){{
    var band = window.innerHeight - HDR;
    if (band < 200) return;
    document.querySelectorAll('.{wrapper} > [id]').forEach(function(el){{
      /* querySelectorAll returns a static list. el.children is live, and removing
         while iterating it skips entries, which left duplicate anchors behind on
         every rebuild. */
      el.querySelectorAll(':scope > .r4-snap').forEach(function(c){{ c.remove(); }});
      if (getComputedStyle(el).position === 'fixed') return;
      var h = el.offsetHeight;
      if (h <= band + 10) return;
      /* A pinned child holds still only until the wrapper has that child's
         height left to give. Past that it unpins and slides up under the header,
         so an anchor there would snap to a slide with its title already cut off.
         Stop at the last pinned position; the release stretch ends at the next
         slide's own snap point, which scroll-snap-stop already forces a halt at. */
      var pinned = null;
      var kids = el.querySelectorAll('*');
      for (var k = 0; k < kids.length; k++) {{
        if (getComputedStyle(kids[k]).position === 'sticky') {{ pinned = kids[k]; break; }}
      }}
      /* Only anchor where the pinned child comes to rest at the header line. Some
         wrappers pin a full-viewport child at top:0, which leaves its first 78px
         under the header; passing through that is one thing, but landing on it
         would park the reader on a clipped title. */
      if (pinned && Math.abs(parseFloat(getComputedStyle(pinned).top) - HDR) > 4) return;
      var limit = pinned ? h - pinned.offsetHeight : h - band;
      if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
      for (var y = band; y <= limit + 4 && y + 40 < h; y += band) {{
        var a = document.createElement('div');
        a.className = 'r4-snap';
        a.style.cssText = 'position:absolute;left:0;width:1px;height:1px;'
          + 'pointer-events:none;visibility:hidden;top:' + y + 'px;'
          + 'scroll-snap-align:start;scroll-margin-top:' + HDR + 'px;';
        el.appendChild(a);
      }}
    }});
  }}

  function schedule(){{
    /* First rAF pair handles the fast-path (CSS parsed, DOM laid out).
       Additional timeouts catch late-loading images, fonts, iframes that
       change section heights after load. */
    requestAnimationFrame(function(){{ requestAnimationFrame(function(){{
      fitAll(); snapAnchors();
    }}); }});
    setTimeout(function(){{ fitAll(); snapAnchors(); }}, 400);
    setTimeout(function(){{ fitAll(); snapAnchors(); }}, 1200);
  }}

  if (document.readyState === 'complete') schedule();
  else window.addEventListener('load', schedule);

  var raf = 0;
  window.addEventListener('resize', function(){{
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(function(){{
      document.querySelectorAll(SEL).forEach(reset);
      requestAnimationFrame(function(){{ fitAll(); snapAnchors(); }});
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
DECK_FONT_FACES = """/* Akka Sans is the same font files as Instrument Sans under a family HubSpot
   does not inject font-display:swap faces for, so the type is painted once
   instead of repainting after load. Declared here rather than taken from
   theme-overrides.css, because these pages are served an older compiled copy
   of that stylesheet. The fallback families carry Instrument Sans's metrics so
   text holds its width and line height while the font arrives. */
@font-face{font-family:'Akka Sans';font-weight:400;font-style:normal;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-Regular.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:400;font-style:italic;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-Italic.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:500;font-style:normal;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-Medium.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:500;font-style:italic;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-MediumItalic.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:600;font-style:normal;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-SemiBold.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:600;font-style:italic;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-SemiBoldItalic.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:700;font-style:normal;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-Bold.woff2') format('woff2');}
@font-face{font-family:'Akka Sans';font-weight:700;font-style:italic;font-display:block;src:url('https://akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-BoldItalic.woff2') format('woff2');}
@font-face{font-family:'IS Fallback System';font-weight:400;font-style:normal;src:local('Segoe UI');size-adjust:102.36%;ascent-override:94.8%;descent-override:24.4%;line-gap-override:0%;}
@font-face{font-family:'IS Fallback System';font-weight:500;font-style:normal;src:local('Segoe UI');size-adjust:103.54%;ascent-override:93.7%;descent-override:24.1%;line-gap-override:0%;}
@font-face{font-family:'IS Fallback';font-weight:400;font-style:normal;src:local('Helvetica Neue'), local('Arial'), local('Liberation Sans');size-adjust:102.36%;ascent-override:94.8%;descent-override:24.4%;line-gap-override:0%;}
@font-face{font-family:'IS Fallback';font-weight:500;font-style:normal;src:local('Helvetica Neue'), local('Arial'), local('Liberation Sans');size-adjust:103.54%;ascent-override:93.7%;descent-override:24.1%;line-gap-override:0%;}
"""

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
    # #s-morph was retired with the efficiency redesign. Its replacements
    # (#s-thesis, #s-akka-platform, #s-eff) are content slides and take the
    # default top-anchored framing.
    'overview': ['#s-title', '#s-close', '#s-routes'],
    'sdk':      ['#s0', '#s6', '#family'],
    'verify':   ['#s0', '#s8', '#family'],
    'optimize': ['#opt-title', '#opt-closing', '#family'],
    'specify':  ['#title', '#closing', '#family'],
}

# The integrated-platform cake slide, per deck. It carries more content than the
# other centred slides, so centring alone can leave its first line against the
# header. Measured before this rule: 0px of clearance on specify against 80-102px
# elsewhere. Given padding-top on a centred box, the content moves down by half
# the padding.
CAKE_SLIDE = {
    'overview': '#s-routes',
    'sdk':      '#family',
    'verify':   '#family',
    'optimize': '#family',
    'specify':  '#family',
}

# Per-deck lists of sticky sections that need explicit top:78px + height override
# so they pin below the fixed header instead of tucking under it.
STICKY_OVERRIDES = {
    'overview': ['#s6-wrapper #s6'],
    'sdk':      ['#s13'],
    'verify':   [],
    'optimize': ['#cog-sticky', '#ts1-sticky', '#ts2-sticky', '#ts3-sticky', '#ts4-sticky'],
    'specify':  ['#spec-sticky', '#s5', '#fact-sticky', '#sdlc-sticky', '#proof-sticky',
                 '#spwhat'],
}
# Every sticky slide belongs in this table. One left out keeps the source's
# `top: 0` and full-viewport height, so the moment it pins, its first 78px sit
# under the fixed header and its title is covered. PageDown hides the fault,
# because it lands on the wrapper before the child pins; scrolling exposes it.
# Audit with: for each sticky descendant of the deck wrapper, computed `top`
# must read 78px.

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
        's-thesis': 'cost-of-intelligence',
        's-akka-platform': 'agentic-ai-platform',
        's-platform': 'resilience-and-scalability',
        's-eff': 'efficiency',
        's-proof': 'production-reliability',
        's6': 'resilience-tester',
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
        'spec-sticky': 'spec-driven-delivery',
        's5': 'delivered-in-weeks',
        'fact-sticky': 'what-changes',
        'sdlc-sticky': 'your-existing-sdlc',
        'proof-sticky': 'results',
        'family': 'platform',
        'closing': 'contact',
    },
}

# Slugs that used to resolve and no longer name a section, mapped to whichever
# section now carries their subject. Links to these are already in circulation,
# and without this a retired slug resolves to nothing and drops the reader at the
# top of the deck with no indication why. Format: retired_slug → live_id.
RETIRED_SLUGS = {
    'overview': {
        # #s-morph became #s-akka-platform in the efficiency redesign.
        'enterprise-agentic-ai': 's-akka-platform',
        # #s-scale became #s-eff.
        'scalability': 's-eff',
    },
    'sdk':      {},
    'verify':   {},
    'optimize': {},
    'specify':  {},
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


def _r2r5_block(wrapper, centered, sticky, slide_wrappers, extra_css='', cake=''):
    """Combined R2 (header clearance) + R5 (unified top-anchored layout)."""
    centered_sel = ',\n  '.join(f'.{wrapper} {sid}' for sid in centered)
    cake_css = (f"""
  /* The cake slide holds more than the other centred slides, and centring alone
     left its first line hard against the header — measured at 0px of clearance
     on specify where the other decks had 80-102px. Padding a centred box moves
     its content down by half the padding, so 32px buys 16px of clearance and
     the slide keeps its own vertical balance. */
  .{wrapper} {cake} {{ padding-top: 32px !important; }}
""" if cake else '')
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
    /* Floor the slide at the band below the header, the same box the centred
       exceptions get. Without this a top-anchored slide kept the source's
       min-height:100dvh, so its box was a full viewport tall while the band it
       lands in is 78px shorter. Snap points then sat one viewport-plus apart and
       a wheel gesture of one screen could not reach the next one — measured on
       overview at 861, 880, 909 and 978px between consecutive slides against an
       861px screen, so nothing ever locked on.

       min-height only. A hard height here would collapse any section that is
       deliberately a tall scroll-through region; the runtime clamps the ones it
       has already proved fit. */
    min-height: calc(100dvh - 78px) !important;
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
     The box fills the whole band below the header. It used to stop 40px short,
     which meant that even when a slide was landed correctly the next slide's
     first 40px showed underneath it — visible as a strip of the following
     headline. The 40px is now padding-bottom instead, so the content box and
     therefore the centred position are unchanged (box-sizing is border-box)
     while the section itself covers the band and occludes what follows. */
  {centered_sel} {{
    justify-content: center !important;
    padding-top: 0 !important;
    padding-bottom: 40px !important;
    min-height: calc(100dvh - 78px) !important;
    /* Source CSS for these sections sets an explicit height:100dvh, which beats
       min-height and leaves the box full-height. R4 then has to correct the
       centering late with padding-bottom, which the viewer sees as the content
       jumping up ~56px once the intro animation finishes. Override height so the
       box is already the right size at first paint and R4's correction is a no-op. */
    height: calc(100dvh - 78px) !important;
  }}
{sticky_block}{cake_css}
  /* Wheel scrolling stops wherever momentum runs out, so a slide could sit a
     few dozen pixels off and show a strip of the next one. Snap points at the
     slide boundaries make a wheel gesture settle exactly where PageDown lands.
     scroll-margin-top:78px on these same elements is what makes the two agree.

     proximity, never mandatory. mandatory was tried and measured: a single 100px
     wheel notch could not advance the page at all, stalling 10 times out of 10,
     because a gesture shorter than the distance to the next snap position is
     returned to the one it started from. It also made the footer unreachable,
     holding at the last slide 889px short of the document end. A reader with a
     fine-grained wheel or a trackpad would have been unable to move. */
  html {{ scroll-snap-type: y proximity; }}
  .{wrapper} > section,
  .{wrapper} > [id$="-sticky"],
  .{wrapper} > [id$="-wrapper"] {{
    scroll-snap-align: start;
    /* A fast gesture is allowed to cross at most one boundary and must stop
       there, so one wheel click always settles on a slide even if that click was
       larger than the distance to it. The next click resumes full size. Without
       this, proximity lets a long gesture sail past a boundary and rest tens of
       pixels below it. */
    scroll-snap-stop: always;
  }}
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
        CAKE_SLIDE[_name],
    )
    _cfg['slide_wrappers'] = SLIDE_WRAPPERS[_name]
    _cfg['autofit_skip'] = AUTOFIT_SKIP[_name]
    _cfg['slugs'] = SLIDE_SLUGS[_name]
    _cfg['retired_slugs'] = RETIRED_SLUGS[_name]


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
        DECK_FONT_FACES +
        fresh_css.strip() +
        '\n\n' +
        existing_port_css +
        cfg['r2'] +
        _r4_shrink(cfg['wrapper']) +
        '</style>\n'
    )
    # Point the deck's text at Akka Sans: the same font files under a family
    # HubSpot does not inject font-display:swap faces for, so the type is painted
    # once instead of repainting after load. Applied to the assembled stylesheet,
    # because the preserved port block carries its own heading rule for the
    # family. Monospace blocks name their own stack and are untouched.
    new_styles = new_styles.replace(
        "'Instrument Sans'",
        "'Akka Sans', 'IS Fallback System', 'IS Fallback'")
    new_body = HUBL_HEADER + fresh_body.strip() + '\n<!-- DEMO_HTML_MARKER -->\n'
    new_scripts = (
        HUBL_HEADER +
        '\n'.join(scripts) +
        '\n' +
        _r4_runtime(cfg['wrapper'], cfg.get('slide_wrappers'), cfg.get('autofit_skip'),
                    cfg.get('slugs'), cfg.get('retired_slugs')) +
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
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    # push() writes to `published` as well as `draft`, so a bare run is a live
    # change to akka.io. --build-only stops after writing scratchpad/hs-out/, so
    # the fragments can be inspected and audited before anything ships.
    build_only = '--build-only' in sys.argv
    if not args or args[0] not in DECKS:
        print(f'usage: python {sys.argv[0]} <{"|".join(DECKS)}> [--build-only]',
              file=sys.stderr)
        return 2
    deck = args[0]
    print(f'=== Porting {deck} ===')
    files = build(deck)
    for kind, p in files.items():
        print(f'  built  {os.path.relpath(p, ROOT)}  ({os.path.getsize(p)} bytes)')
    if build_only:
        print(f'=== {deck} built, not pushed (--build-only) ===')
        return 0
    push(deck, files)
    print(f'=== {deck} done ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
