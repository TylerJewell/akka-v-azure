# Port-CSS snippets — R2 header offset

Ready-to-paste CSS blocks for the 5 deck pages, implementing rule 7 from
`audit.py` PORT TRANSFORM CHECKLIST (the akka.io fixed header, 78px desktop /
64px mobile).

**Where to paste:** Append to each deck's LIVE `styles.html` partial, after
the existing `/* === Neutralize HubSpot wrapper containers … */` block and
before the closing `</style>`. Push via `PUT /cms/v3/source-code/{draft,published}`.

Sticky sections were identified from a 2026-07-27 audit run
(`tools/auditors/viewport-fit/audit.py`). Non-sticky sections just need the
uniform padding-top bump; sticky sections need `top` + `height` overrides so
they pin below the header instead of tucking under it.

---

## overview (`.overview-content`)

Sticky sections: `#s6-wrapper > #s6` (Resilience).
Non-sticky sections whose padding-top < 78px: `#s-platform`.

```css
/* === R2 header offset — akka.io fixed header 78px desktop / 64px mobile === */
@media (min-width: 1001px) {
  .overview-content section { padding-top: 88px !important; }
  .overview-content #s6-wrapper #s6 {
    top: 78px !important;
    height: calc(100dvh - 78px) !important;
    min-height: calc(100dvh - 78px) !important;
  }
}
@media (max-width: 1000px) {
  .overview-content section { padding-top: 74px !important; }
}
```

---

## sdk (`.sdk-content`)

Audit clean — no sticky slides need remap, all sections have padding-top ≥ 78.
Still safe to append the uniform padding-top bump so it survives future edits.

```css
/* === R2 header offset === */
@media (min-width: 1001px) {
  .sdk-content section { padding-top: 88px !important; }
}
@media (max-width: 1000px) {
  .sdk-content section { padding-top: 74px !important; }
}
```

---

## verify (`.verify-content`)

Non-sticky sections needing header clearance: `#s-risk` (padding-top 67px).

```css
/* === R2 header offset === */
@media (min-width: 1001px) {
  .verify-content section { padding-top: 88px !important; }
}
@media (max-width: 1000px) {
  .verify-content section { padding-top: 74px !important; }
}
```

---

## optimize (`.optimize-content`)

Sticky sections: `#cog-sticky` (opt-07 cost-gov console — the one already
documented in PUBLISHING.md §1).

```css
/* === R2 header offset === */
@media (min-width: 1001px) {
  .optimize-content section { padding-top: 88px !important; }
  .optimize-content #cog-sticky {
    top: 78px !important;
    height: calc(100dvh - 78px) !important;
  }
}
@media (max-width: 1000px) {
  .optimize-content section { padding-top: 74px !important; }
}
```

---

## specify (`.specify-content`)

Sticky sections: `#platform-pattern` (sp-04-runs), `#s5` (sp-03-weeks).

```css
/* === R2 header offset === */
@media (min-width: 1001px) {
  .specify-content section { padding-top: 88px !important; }
  .specify-content #platform-pattern,
  .specify-content #s5 {
    top: 78px !important;
    height: calc(100dvh - 78px) !important;
  }
}
@media (max-width: 1000px) {
  .specify-content section { padding-top: 74px !important; }
}
```

---

## After pasting

Re-run the auditor to confirm nothing regressed:

```bash
python tools/auditors/viewport-fit/audit.py
```

Note this auditor is run against the SOURCE files (which don't have the port
CSS injected). It will continue to report clip findings until the port CSS
lands on the live pages. To verify the LIVE page post-port, load
`https://akka.io/platform/<deck>` in a browser and check that section
eyebrows and headlines sit cleanly below the header at every scroll position.
