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
  intro fade.** R4's Range measurement includes in-flight child transforms.
  Slides that animate elements from `translateY(16px)` to `translateY(0)` on
  load cause R4 to measure a taller-than-final section at 400/1200ms, commit
  a scale + centering paddingBottom based on that measurement, then let the
  last animation land — result is a visible 10–20px group shift at ~2.6s.
  **Fix:** use opacity-only fade-in on title slides (`heroFade`, or drop the
  `transform:translateY(16px)` initial state entirely).
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

`snapAnchors()` in the R4 runtime drops a zero-size anchor at every screen height
inside any slide taller than the band, carrying `scroll-snap-align: start` and
the same 78px `scroll-margin-top`. Anchors are absolutely positioned, 1x1 and
hidden, so they add nothing to layout, and they are rebuilt on resize. Specify
goes from 9 snap points to 23, optimize from 10 to 25, and no deck is left with a
gap wider than one screen.

Verify with `scratchpad/sliver.py`, which must still report zero leaked pixels:
the anchors must not change slide framing.

Synthetic wheel events via CDP `Input.dispatchMouseEvent` do not reliably drive
the compositor's snap path, so headless runs under-report snapping. Confirm the
applied CSS headlessly; confirm the feel in a real browser.

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

## Port workflow

1. Edit source (`akka-overview/`, `akka-sdk/`, `akka-verify/`, or
   `sales-presentation/slides/...`).
2. `python build-all.py` — regenerates `sales-presentation/generated/<deck>/`.
3. `python scratchpad/port_deck.py <deck>` — pushes draft + published to
   HubSpot `custom-templates/partials/<deck>-{styles,body,scripts}.html`.
4. `python tools/auditors/live-deck/audit.py <deck>` — verify.
5. If publishing all: loop over `overview sdk verify optimize specify`.

## Security

- **Never** put the HubSpot token in a message or file that gets committed.
  `scratchpad/` is in `.gitignore` for this reason.
- If a token slips into the transcript, rotate it in HubSpot and update the
  local secret.
