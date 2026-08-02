# HubSpot Deck Port Rules

Rules and pitfalls accumulated while porting the 5 decks (`overview`, `sdk`,
`verify`, `optimize`, `specify`) to `akka.io/platform/<deck>`. Applied by
`scratchpad/port_deck.py` and verified by `tools/auditors/live-deck/audit.py`.

Target viewport: **1536 × 861** CSS (78px fixed header + 114px cookie banner →
visible content area 78–747).

---

## R1 — Width cap 1400px

All section content wrapped in `.inner` with `max-width: 1400px; margin: 0 auto`.
Prevents ultra-wide layouts on big monitors and keeps line lengths readable.

## R2 — Header offset 78px

The HubSpot theme has a `position: fixed` header 78px tall. Every deck must
account for it:
- Non-sticky sections: `padding-top: 32px` (was 100 — reclaimed budget for R4).
- Sticky sections: `top: 78px; padding-top: 32px`.
- Nav / deep-link scroll: **always** `scrollTo({top: docTop(el) - 78})`, never
  bare `docTop(el)` — otherwise the section top gets pinned to y=0 and the
  header covers the title. Same offset in the `currentIndex()` reverse lookup.

## Header height is a shared constant — three places must agree

The akka.io header is `position: fixed`. Three things encode its height and they must
match, or every page renders offset and then jumps when the script runs:

| Where | Value |
|---|---|
| `AKKA-2024/css/theme-overrides.css` -> `body { padding-top }` | 78px at >=768, 64px at <=767 |
| `template_main.min.js` -> `hStickyPadd()` | sets `body` padding-top to `$("header.header").outerHeight()` after load |
| This file's R2 / R5 offsets | 78px |

Fixed 2026-07-30. The CSS had `95px` at >=992 and `66px` at <=991 while the real header
is 78px / 64px, so **every page on the site** rendered 17px low (or 12px high on tablet)
and jumped when `hStickyPadd()` corrected it. The CSS values now match the measured
header, which makes that script a no-op. If the header design changes height, all three
rows above change together.

Anchor targets need the same offset. Native fragment navigation scrolls the target to
viewport 0 — behind the header. Deck pages used to correct this in JS at load, +300ms and
+900ms, which the viewer saw as a jump; other pages never corrected it and left the target
hidden. Both are handled by `scroll-margin-top`: per-deck in the R2+R5 block, and
site-wide via `:target` in `theme-overrides.css`.

**The theme lives outside this repo.** `theme-overrides.css` is edited through the
source-code API only, so these values are not version controlled anywhere. Back the file
up before touching it (see `PUBLISHING.md`).

## Port tooling

`tools/hubspot/port_deck.py <deck>` builds and PUTs the three partials. It reads the token
from the gitignored `scratchpad/.hs_env` and writes fragments to `scratchpad/hs-out/`, so
secrets and build output stay out of git while the script itself is tracked.

**Anything hand-appended to a live styles partial is destroyed on the next port.** The
script strips everything from `/* Rules that apply on all viewport sizes` to the end of the
preserved block, plus several named blocks, so re-ports do not stack duplicates. Hotfix in
the generator, never in the live partial.

## R4 — Runtime auto-fit (transform:scale)

For any slide whose natural content exceeds the visible viewport, apply
`transform: scale(k)` at runtime. Details in `port_deck.py:_r4_runtime()`.
Key constraints:

- `transform-origin: 50% padTop` (top-anchored) for left-anchored slides.
- `transform-origin: 50% 50%` for centered slides (`justify-content:center`).
- Floor scale at 0.7 — below that text becomes unreadable.
- **Skip sections listed in `AUTOFIT_SKIP`** — those have designed internal
  scroll (`#cog-sticky`) and their natural height is intentionally >100vh.
- Runs at rAF+rAF (fast path), 400ms, 1200ms — catches font/iframe reflow.
- Uses `Range.selectNodeContents(section).getBoundingClientRect()` for
  measurement — bypasses `overflow:hidden` height clamps that `scrollHeight`
  otherwise honours.

### R4 pitfalls

- **Do NOT let content animations use `transform:translateY(...)` for the
  intro fade — on any slide, not just the title.** R4's Range measurement
  includes in-flight child transforms.
  Slides that animate elements from `translateY(16px)` to `translateY(0)` on
  load cause R4 to measure a taller-than-final section at 400/1200ms, commit
  a scale + centering paddingBottom based on that measurement, then let the
  last animation land — result is a visible 10–20px group shift at ~2.6s.
  **Fix:** use opacity-only fade-in (`heroFade`, or drop the
  `transform:translateY(16px)` initial state entirely). Overview's
  four-efficiency columns hit the same trap on a content slide: they revealed
  from `translateY(20px)`, so the section measured 20px taller than it renders.
  A staggered opacity fade still reads as a sequence and costs nothing.
- **Cookie banner** — detect any `position:fixed` element at viewport bottom
  (`bottomBannerHeight()`) and subtract from the R4 target so scaled content
  clears it. Auditor does the same via a fixed-element probe.
- **`display:contents` wrappers** — `sp-02-specs .spec-diagram` uses
  `display:contents`. `scrollHeight` misses the inner overflow; only
  `Range.selectNodeContents` recovers it.
- **Chrome above section > 78px** — HubSpot sometimes pushes the
  `.wrapper-content` down 90–100px on the first screen. R4 adds a dynamic
  `padding-bottom` on centered slides to shift flex-centered content back
  toward the true visible-area center.

## R5 — Unified top-anchored layout

Non-sticky sections use `padding-top: 32px` (title Y ≈ 110). Centered
exceptions (`CENTERED_EXCEPTIONS`) — heroes, closes, cakes — keep
`justify-content: center` and `padding-top: 0`. Ensures title X and Y line up
across the deck.

## Slides must occlude what follows them

A slide landed at the header must cover the band down to the viewport bottom.
Centred sections used to be sized `calc(100dvh - 118px)`, which stopped 40px
short, so even a correctly landed slide showed the next slide's first 40px as a
strip of stray headline. The box is now `calc(100dvh - 78px)` with
`padding-bottom: 40px`, so the content box — and therefore the centred position
— is unchanged while the section covers the whole band.

R4's target for centred sections must match that content box
(`vh - 78 - 40 - bottomBanner`). A smaller target shrank content that already
fitted, and a scaled box is inset from its layout box, which lifts the layout box
above the header and lets the next slide show underneath. Two decks leaked this
way before the target was aligned.

`scratchpad/sliver.py` lands every slide of every deck at the header and reports
how many pixels of the next slide are visible. It must report zero.

## Wheel scrolling snaps to the PageDown position

`scroll-snap-type: y proximity` on `html`, plus `scroll-snap-align: start` and
`scroll-snap-stop: always` on the deck wrapper's direct children. The snap
position equals the PageDown landing because both derive from the same
`scroll-margin-top: 78px`.

`proximity`, never `mandatory`: the tall sticky wrappers (up to 2755px) carry one
snap point at their top and the reader must be free to rest anywhere inside them
while the pinned slide animates. `mandatory` would forbid that.

`scroll-snap-stop: always` caps a gesture at one boundary crossing, so a single
wheel click settles on a slide even when the click was longer than the distance
to it, and the next click resumes full length.

### Every sticky slide belongs in STICKY_OVERRIDES

A sticky slide left out of that table keeps the source's `top: 0` and its
full-viewport height, so the moment it pins, its first 78px sit under the fixed
header and its title is covered. PageDown hides the fault, because it lands on
the wrapper before the child pins. Scrolling exposes it, which is why the two
appear to disagree and why it looks like a scrolling bug.

Six slides were missing: `#spwhat` on specify, `#s13` on sdk, and
`#ts1-sticky` through `#ts4-sticky` on optimize.

Audit it directly: for every sticky descendant of the deck wrapper, computed
`top` must read 78px. Anything else is a slide that will hide under the header
as soon as the reader scrolls.

### Do not use scroll-snap-type: mandatory

Tried and measured on these decks. A single 100px wheel notch could not advance
the page at all, stalling ten times out of ten, because a gesture shorter than
the distance to the next snap position is returned to the one it started from. It
also held the reader at the last slide, 889px short of the document end, putting
the footer out of reach. `proximity` is the only workable setting here.

### Tall slides need a snap point per screen

A slide taller than the viewport is a scroll-through region holding a pinned
child, and it carries one snap point, at its top. Past that, the next point is a
whole slide away, so a gesture ending inside rests wherever momentum ran out. In
the last screen of the region, where the child unpins, that reads as a slide
caught halfway. PageDown is unaffected, which is why the two disagree.

The decks differ sharply in how much of this they carry: verify has 439px of
unsnapped scroll-through in total and overview 576px, both under one screen,
while specify has 5,461px and optimize 6,264px. The same CSS therefore feels
precise on two decks and loose on the other two.

`snapAnchors()` in the R4 runtime drops a zero-size anchor at each screen height
inside a tall slide, carrying `scroll-snap-align: start` and the same 78px
`scroll-margin-top`. Anchors are absolutely positioned, 1x1 and hidden, so they
add nothing to layout, and they are rebuilt on resize.

Two conditions decide where an anchor may go, and both were learned by putting
them in the wrong places first:

- **Stop at the last pinned position.** A pinned child holds still only while the
  wrapper has that child's height left to give; past that it unpins and slides up
  under the header. An anchor there parks the reader on a half-released slide with
  its title cut off, which is exactly what an anchor at 783px did inside specify's
  1205px `spwhat-wrapper`, whose child stays pinned for only 422px.
- **Only where the child pins at the header line.** Some wrappers pin a
  full-viewport child at `top: 0`, leaving its first 78px under the header.
  Passing through that is tolerable; landing on it is not. Three of optimize's
  `ts*-wrapper` slides behave this way and take no anchors.

Remove anchors with `querySelectorAll(':scope > .r4-snap')`, never by iterating
`el.children`: that collection is live, and removing while iterating it skips
entries and leaves duplicates behind on every rebuild.

Verify with `scratchpad/sliver.py`, which must still report zero leaked pixels:
the anchors must not change slide framing.

Synthetic wheel events via CDP `Input.dispatchMouseEvent` do not reliably drive
the compositor's snap path, so headless runs under-report snapping. Confirm the
applied CSS headlessly; confirm the feel in a real browser.

## Fixed-footprint graphics need a fit step per width band

A graphic sized in pixels rather than in the layout — overview's architecture
diagram is a 1230px scene at `scale(0.9)`, so a 1107px footprint — fits only
above `1107 / 0.88 = 1258px`, because sections carry `0 6vw` of side padding.
Below that it pushes the whole document sideways and the deck grows a horizontal
scrollbar on every slide, not just the one with the graphic.

The deck had a single `zoom:0.30` rule at `max-width:640px`, which covered
phones and left the entire 641–1257px band broken: 1058px of content in a 1024px
window, 963px in an 834px one. Fixed with graduated `zoom` steps, each computed
from the **narrow** end of its range, since that is where it has to fit:

    z <= 0.88 * viewport / footprint

**Bound every step with `min-width`.** Declared after the phone rule, a bare
`@media (max-width:760px){ zoom:0.50 }` also matches a 390px phone and wins on
the cascade, putting a 553px diagram in a 390px window — worse than the overflow
being fixed. Each step reads `@media (min-width:641px) and (max-width:N)`.

Verify with `tools/auditors/mobile/audit.py <page> <width>` at 360, 390, 768 and
834, and by checking `document.documentElement.scrollWidth` against
`window.innerWidth` at 1024 and 1180. Nothing may exceed the viewport at any of
them.

## R6 — Asset rewriting

Relative `.html` in `src`/`href` becomes
`https://akka.io/hubfs/demos/<basename>.html`. `index.html` inside a demo dir
maps to `<dirname>.html`. Absolute URLs, anchors, mailtos, data: are left
alone. Handled in `port_deck.py:rewrite_assets()`.

## Nav rules

- **PgDn / ArrowRight / ArrowDown / Space** → next section, target
  `docTop - 78`.
- **PgUp / ArrowLeft / ArrowUp** → previous section, same offset.
- `currentIndex()` compares `docTop(el) <= scrollY + 78 + 4` — the +78 keeps
  the reverse lookup consistent with the header-offset scroll.
- On the last section, PgDn falls through to `document.body.scrollHeight` so
  the trailing CTA / footer is reachable.

## Deep linking

Each section gets a friendly slug in `SLIDE_SLUGS` (id → slug). Both the raw
id and the slug are accepted on input. On scroll, the URL hash is updated
with the friendly slug via `history.replaceState`. **Never** use `pushState`
here — it spams history.

### The browser fights the reader when a fragment is in the URL

Because the hash tracks the current slide, every reload carries one. The browser
re-applies the URL fragment as the document lays out, so a reader who starts
scrolling during a slow load gets dragged back to the hashed slide seconds later.
No script causes this — patching `window.scrollTo`, `scrollIntoView` and
`documentElement.scrollTop` records zero calls while the page still moves.

`dropHash()` removes the fragment via `replaceState` as soon as the reader takes
over, leaving the browser nothing to scroll to. Two triggers are needed:

- a one-shot `wheel` / `touchstart` / `keydown` / `mousedown` listener, and
- a parse-time position check, because scrolling done before the inline script
  parsed never reaches those listeners and on a throttled connection that window
  is several seconds wide. A fresh load sits at 0 (`scrollRestoration` is
  `manual`) and the browser's fragment jump leaves the target at the viewport top
  or one header height above it, so any other position means the reader moved.

A hash written later by `replaceState` does not restart fragment scrolling, so
shareable slugs still work. Verify with a throttled load plus wheel events: the
scroll position must be unchanged 10s later.

Keep `SLIDE_SLUGS` in step with the deck's real section ids. A stale map silently
falls back to raw ids and the slugs stop resolving.

### A retired slug needs an alias, not deletion

Renaming or removing a section retires its slug, and links carrying it are
already in circulation — in email, in a deal thread, in someone's notes. A
retired slug matches no id and no entry in the map, so `resolveHash` returns
null and the reader lands at the top of the deck with nothing to explain why.

`RETIRED_SLUGS` maps each dead slug to whichever section now carries its subject,
and `resolveHash` consults it last, after both the live slug map and the raw ids,
so it can never shadow a current section. Overview's redesign retired two:
`enterprise-agentic-ai` (was `#s-morph`) now resolves to `#s-akka-platform`, and
`scalability` (was `#s-scale`) to `#s-eff`.

Entries are permanent. Removing one to tidy the table breaks the link again.

## LinkedIn icon

**Never** publish LinkedIn icons on the HubSpot pages. They are reserved for
the sales-presentation ZIP deliverables only. The port strips them from the
footer partial before publish.

## Auditor

`tools/auditors/live-deck/audit.py` renders each deck at 1536×861 via
headless Edge, detects the cookie banner, and reports per section:
- `HEADER_CLIP`  — first child top < 78.
- `CUT_OFF`      — content bottom > visible bottom + 12 (buffer).
- `TITLE_X_DRIFT` — title left ≠ 92 ± 15px, unscaled left-anchored only.
- `[sec-box +Npx cosmetic]` — section box (background) overflows but content
  doesn't; safe.

Expected known failures:
- `#cog-sticky` — `CUT_OFF +497` by design (AUTOFIT_SKIP; internal scroll).
- `#opt-closing` — `CUT_OFF +33` residual bottom-CTA nick by cookie banner.

Run: `python tools/auditors/live-deck/audit.py [deck…]`. Exit 0 = clean.

`tools/auditors/js-errors/audit.py <file|url…>` reports uncaught exceptions and
names the file each came from. Expected known failure on any **live akka.io URL**:
`Uncaught TypeError: e.indexOf is not a function [jquery.min.js:1]` — the theme's
own jQuery, present on the untouched `platform/overview` too. A local file or a
composed fragment must be clean.

### Removing a slide means removing its script

A slide's script goes with the slide. The overview redesign dropped `#s-morph`
and left its script block behind, and the block opened with an unguarded
`document.getElementById('s-morph').querySelector('.drawbox')`. That threw a
TypeError on its first statement — and a throw abandons the whole block, so the
`keydown` handler at the *end* of it never registered. That handler is the deck's
entire PgDn/PgUp nav.

PageDown then fell through to the browser's native scroll-one-viewport, which
lands wherever a viewport happens to end: the reader got the next slide's
headline 300px down the screen with its content cut off at the bottom, on every
press. Nothing in the console was surfaced, and every layout auditor passed,
because the layout was right and only the landing position was wrong.

Two rules from it:

- **Never register the nav inside a block that can throw.** Keep any lookup that
  can return null out of the same block, or guard it.
- **Run `tools/auditors/js-errors/audit.py` on every port.** It is the only check
  that catches a silently disabled feature.

`assemble_overview.py` now strips the morph block and re-emits the nav handler on
its own, and raises if the block it expects to remove is not found — a deck that
assembles without it is a deck with no keyboard navigation.

### pgdn-frame does not judge TITLE_X on a scaled section

R4 scales an over-tall section from `transform-origin: 50%`, which insets it from
its layout box and moves its title right. That is the fit working, not drift.
pgdn-frame judged it anyway and reported four correctly framed overview slides as
TITLE_X — `#s-thesis` at 127, `#s-platform` at 180, `#s6` at 168, `#s-packages`
at 127, all scaled between 0.87 and 0.95. It now reads the computed transform and
stands the check down below 0.995, which is what live-deck has always done.

### Known: centred slides sit ~36px high in the band

`padding-bottom: 40px` on a centred box lifts flex-centred content 20px above the
box centre, and R4's centring correction only ever shifts content **up**
(`if (offset > 4)`), so nothing puts it back. pgdn-frame measures 36px high on
`#s-title` and `#s-close`. It is pre-existing, arrived with the occlusion fix, and
applies to the centred slides on all five decks. Not corrected here: changing the
centring maths touches every deck at once and belongs in its own pass.

## Auditing a port before it ships

`port_deck.py <deck> --build-only` writes the three partials to
`scratchpad/hs-out/` and stops. A bare run PUTs to `published` as well as
`draft`, so it is a live change to akka.io; `--build-only` is what makes a port
reviewable first.

The partials are not a page on their own. Stitch them under a 78px fixed header
with `body{padding-top:78px}` and the deck's fonts, and the result exercises the
real ported CSS and JS — R2/R5 offsets, R4, the snap anchors, the deep-link
runtime — so slide-ux, slide-align, pgdn-frame and the mobile auditor can all run
against it before anything is pushed. Without this the only verifiable page is
one that has already shipped.

Two things the composite cannot tell you, because it has no cookie banner:
centred-slide framing, and any R4 target that subtracts `bottomBannerHeight()`.
Confirm both with live-deck after publishing.

## Port workflow

1. Edit source (`akka-overview/`, `akka-sdk/`, `akka-verify/`, or
   `sales-presentation/slides/...`).
2. `python build-all.py` — regenerates `sales-presentation/generated/<deck>/`.
3. `python tools/hubspot/port_deck.py <deck> --build-only` — build the partials.
4. Compose and audit them locally (previous section). Include
   `tools/auditors/js-errors/audit.py` — a throw disables everything registered
   after it, silently, and no layout auditor sees it.
5. `python tools/hubspot/port_deck.py <deck>` — pushes draft + published to
   HubSpot `custom-templates/partials/<deck>-{styles,body,scripts}.html`.
6. `python tools/auditors/live-deck/audit.py <deck>` — verify.
7. If publishing all: loop over `overview sdk verify optimize specify`.

## Security

- **Never** put the HubSpot token in a message or file that gets committed.
  `scratchpad/` is in `.gitignore` for this reason.
- If a token slips into the transcript, rotate it in HubSpot and update the
  local secret.
