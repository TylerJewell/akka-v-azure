# Making the scroll decks mobile-responsive

How the Token Shredder deck was converted for mobile (2026-07-10). The same recipes apply to the other decks in this repo (overview, specify, dev, gartner) — their slides share the identical sticky-scroll machinery and will show the same failure modes on phones.

**Reference implementation:** `slides/tss-01-problem` … `slides/tss-04-results`, plus `slides/ts-00-title` and `slides/ts-10-close`. Every technique below is live in those files.

## The two root problems

1. **The sticky 100vh theater breaks on phones.** Slides are `height: 100vh` sticky frames with `overflow: hidden` inside 200–300vh scroll envelopes. Mobile browsers change the real viewport as the URL bar collapses, so `100vh` overshoots and content clips against the hidden overflow. Pinned-scroll pacing also feels wrong on touch.
2. **Fixed-aspect / SVG graphics scale down proportionally.** Percent-positioned diagram stages and SVG text sized in viewBox units become unreadable at 390px width. Horizontal scrolling is not an acceptable fix — OS scrollbars don't match the deck styling and panning a diagram is a poor reading experience.

## Recipe 1 — one breakpoint that turns off the theater

Add to every slide's `slide.css` (adjust the id prefix):

```css
@media (max-width: 820px) {
  #xx-wrapper { height: auto; }              /* collapse the scroll envelope */
  #xx-sticky {
    position: static; height: auto;          /* leave pinned mode            */
    padding-top: 64px; padding-bottom: 64px; /* slide becomes a flow section */
  }
}
```

Reveal animations keep working — the IntersectionObservers don't care whether the section is sticky. Desktop is unaffected.

Also add `height: 100dvh;` immediately after every `height: 100vh;` declaration (sticky frames, title/close sections). Browsers that understand dynamic-viewport units use the correct height when browser chrome collapses; older ones keep the vh value.

## Recipe 2 — reflow diagrams, don't pan them

For a fixed-aspect stage built from a wires-SVG plus absolutely positioned HTML boxes (see `tss-03-where`):

- Wrap the platform/grouped boxes in a `<div class="xx-plat">` with `display: contents` — invisible to desktop layout (absolute children still position against the stage), but on mobile it becomes a real flex container with the dashed boundary border.
- At the breakpoint: hide the wires SVG, legend, and floating labels (`display: none !important`); neutralize the boxes' inline positioning (`position: static !important; left/top/width/height: auto !important`); switch the stage to `display: flex; flex-direction: column; aspect-ratio: auto`.
- Add small mobile-only connector elements (`.xx-m`, `display: none` on desktop) where an arrow is load-bearing — e.g. "your agents ↓ inference calls".
- A shape that only exists in the SVG (the storage cylinder) gets replaced by styling its HTML text block as a rounded card at the breakpoint.

For a diagram that is *pure SVG with text* (see `tss-02-how`): hide the SVG at the breakpoint and render a mobile-only stacked HTML variant (`.tss2-m` — same copy, cards in the node style, promote line beneath). Duplicate content, single source of truth per string is sacrificed, so keep the variants adjacent in the same `slide.html`.

## Recipe 3 — charts with SVG text

Axis ticks and series labels sized in viewBox units shrink with the chart. They're styled via CSS classes, so bump them at the breakpoint by the inverse of the scale factor (see `tss-01-problem`: 11px ticks become 22px in SVG units ≈ 12px rendered at phone width).

## Recipe 4 — tables, grids, strips

- **Tables**: step down type and padding at the breakpoint until the columns fit (`tss-04-results`). Only fall back to `overflow-x: auto` if a table genuinely cannot fit — and then style the scrollbar (`scrollbar-width: thin; scrollbar-color: rgba(245,197,24,.6) #1A1A1A` + WebKit equivalents).
- **Tile grids**: go single-column below ~600px; shrink tab/selector buttons and let them wrap (`tss-03b-capabilities`).
- **Horizontal phase/progression strips**: stack vertically, hide the connector lines (`ts-10-close`).

## Recipe 5 — typography

Wide-tracked uppercase lines overflow narrow screens. Reduce `letter-spacing` at the breakpoint (product name went 8px → 3px on `ts-00-title`) and give hero headlines a vw-based clamp suited to ~390px.

## Conversion checklist per deck

1. Every slide: Recipe 1 block + `dvh` additions.
2. Inventory each slide's graphic: fixed-aspect stage → Recipe 2a; pure-SVG diagram → Recipe 2b; chart → Recipe 3; table/grid/strip → Recipe 4.
3. Check all uppercase tracked text at 390px → Recipe 5.
4. Test at 390×844 and ~768px (DevTools device toolbar); confirm zero horizontal scrollbars anywhere.
5. Iframe demo slides (resilience/governance) — **resolved: hide the iframe at the breakpoint and swap in a mobile-only link-out card** that opens the demo full-screen in a new tab. The embedded apps have desktop-oriented layouts unusable at 390px. Reference: `.s6-mobile-card` (resilience) and `.s7gov-mobile-card` (governance) in `slides/10-resilience`, `11-governance`, `sp-06-up`, `sp-07-safe` — default `display:none`, `display:flex` inside the breakpoint, iframe + expand toggle hidden. Use this pattern for any demo iframe in the dev/gartner decks too.
