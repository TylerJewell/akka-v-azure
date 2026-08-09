# Overview deck — flywheel slide + reorder. Port handoff.

Run on the machine that already has `scratchpad/.hs_env` wired. Nothing in this
change has been pushed to HubSpot. `akka.io/platform/overview` is untouched.

---

## What changed in `akka-overview/index.html`

**1. `#s-akka-platform` — the cake's chip lists swap for a flywheel per box.**

| Cake box | Loop |
|---|---|
| Akka Specify | spec → build → check |
| Akka Verify | control → run → measure |
| Akka SDK | supervise → adapt → rebalance |
| Akka Optimize | route → observe → train |

The right-hand copy swaps at the same time, from the four platform paragraphs to
five flywheel paragraphs.

**Trigger is deliberate, never automatic.** A click on `.cake-wrap`, or ~420px of
downward wheel (about four notches) while the slide is 60% in view. The wheel
handler calls `preventDefault` on those first notches: this deck sets
`scroll-snap-stop: always`, so one notch would otherwise carry the reader to the
next slide before any count could accumulate. Keyboard nav is never intercepted,
so PgDn and the arrows always leave immediately.

**2. `#s-proof` moved** from position 6 to position 3 — after `#s-thesis`, before
`#s-akka-platform`. Retitled to "We make the smallest things efficient, so that AI
can scale." with an explicit `<br>` and `max-width:none` so it sets on two lines.
Its subtitle was removed.

**3. `#s-eff` subtitle** fixed. Was "…so that **none** exist at the largest scale",
where the antecedent of "none" is "efficiencies" — it stated that no efficiencies
exist at the largest scale. Now reads "…so that inefficiencies don't exist at the
largest." The positioning audit flagged this and noted it ships in two places:
**`llms/llms-master.txt` L39 still carries the defect and needs the same fix.**

---

## Four constraints the implementation obeys

**R4 — nothing animates `transform`.** R4 measures the section with
`Range.selectNodeContents()`, which includes in-flight child transforms. This deck
has already been bitten by that on the four-efficiency columns. The loop's centring
transform is static; only `opacity` and `stroke-dashoffset` move, and
`stroke-dashoffset` is paint-only.

**Cake geometry is frozen.** The chip lists stay in normal flow and only fade, so
each card's height is still set by its original content. The loops are
`position:absolute` and contribute no layout. Measured in both states, all four
cards are identical:

```
OFF  246,293,282,111 | 541,293,343,111 | 246,429,651,130 | 246,585,600,111
ON   246,293,282,111 | 541,293,343,111 | 246,429,651,130 | 246,585,600,111
```

**Both copy blocks share one grid cell** (`grid-area: 1/1`) rather than one being
absolute, so the panel measures the same height either way.

**Loop presentation is deliberately unscoped.** The mobile pinch-zoom feature clones
`.cake-wrap` into `#gzoom`, which is appended outside `#s-akka-platform`. Rules
scoped to the section id are lost in that clone — the arcs then paint as solid
blocks because `fill:none` never reaches them. Presentation hangs off `.fly-loop`;
only placement and choreography are scoped to the section. `#gzoom .fly-loop` puts
the clone in its settled state.

### Two traps worth not re-introducing

- **`marker-end` arrowheads ignore `stroke-dasharray`.** They render the instant the
  SVG is visible, before their line has drawn. Arrowheads are path geometry now.
- **A `var()` anywhere in the `transition` shorthand** makes the whole declaration
  pending-substitution and the draw jumps to its end value. Every delay in the
  `.fw-1`…`.fw-4` blocks is written out literally for that reason.

`fitPfMsg()` was also reworked: it collected all `<p>` and all `.seg`, so with two
stacked blocks it measured their combined ink and spread one block's slack across
nine paragraphs belonging to two. It now measures each block separately and sizes
both to the smaller fitted size, so type does not jump on swap.

---

## Verified before handoff

```
js-errors                     no uncaught exceptions
mobile 360 / 390 / 768 / 834  nothing overflows the viewport
pinch-zoom clone @ 390px      driven headlessly, renders correctly
```

**Not yet run** — these need the partials stitched under a 78px fixed header, which
needs the token:

```
live-deck    slide-ux    pgdn-frame
```

---

## Port sequence

```bash
# 1. build the three partials, push nothing
python tools/hubspot/port_deck.py overview --build-only
#    → scratchpad/hs-out/

# 2. stitch them under a 78px fixed header with body{padding-top:78px} and the
#    deck's fonts (HUBSPOT_PORT_RULES.md, "Auditing a port before it ships"),
#    then run the three that need real header offsets, R4 and snap anchors
python tools/auditors/js-errors/audit.py <composite>
python tools/auditors/slide-ux/audit.py  <composite>
python tools/auditors/pgdn-frame/audit.py <composite>

# 3. only when those are clean — this PUTs draft AND published, and published
#    source-code is live immediately with no publish step
python tools/hubspot/port_deck.py overview

# 4. verify against the live page
python tools/auditors/live-deck/audit.py overview
```

**Check the preserve step survived.** `port_deck.py` re-appends the hand-added
port-transform CSS block from the live partial (starts at
`/* === Neutralize HubSpot wrapper containers`). If it is missing from the built
styles partial, stop — regenerating from source drops it and the akka.io theme
needs it.

**After publishing, confirm the two things a local composite cannot show**, because
it has no cookie banner: centred-slide framing, and any R4 target that subtracts
`bottomBannerHeight()`. `live-deck` covers both.

---

## Rollback

```bash
git revert <this commit>          # then re-run the port sequence to restore live
```

The previous deck source is one commit back. HubSpot has no draft-preview URL
(`/_hcms/preview/…` and `?hs_preview=true` both 404 unauthenticated, and the page
object has no `previewKey`), so a bad publish is corrected by re-porting, not by
unpublishing.

## Known, pre-existing, not from this change

`tools/auditors/voice/audit.py --context web akka-overview/index.html` reports 8
violations in `#s-routes` — one antithesis at "explicit rather than implied" and
seven "sentence cannot stand alone". They are identical in `HEAD`. The prose gate
in `.githooks/pre-commit` fails on this file for that reason alone.
