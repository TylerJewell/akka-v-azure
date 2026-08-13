# Akka Competitive Collateral — Project Rules

## Language rules come first — always

Before writing any prose in this repo, invoke the `house-voice` skill. The rules cover
**analysis and chat responses** as well as published copy. Recommendations, summaries,
audits, plans, and slide drafts are all covered.

Invoke the skill before the first sentence is written. The rules
are not intuitions — they name specific banned constructions that read as correct until
checked against the list.

Source files the skill consolidates:

| File | Governs |
|---|---|
| `case-studies/case-study-rules.md` | Voice, banned wording, structure, ROI scorecard |
| `_internal/battlecard-style-guide.md` | Battlecards and comparison pages |
| `akka-specify-modernization-positioning.md` §5 | Settled Akka Specify positioning language |

Memory files `feedback_say_less`, `feedback_no_x_across_y_slogans`,
`feedback_battlecard_style`, `feedback_marketing_copy_style`, and
`feedback_public_comparison_language` carry standing corrections and load automatically.

## HTML rules come with them

Invoke the `akka-page` skill before writing or editing any HTML here, and before
rendering Akka-styled HTML anywhere else. The skill carries the favicon, the brand
palette, the typefaces, scrollbar styling, and the banned card patterns. `house-voice` governs the
prose inside the page; `akka-page` governs the page. Writing a page needs both.

## Every HTML document carries the Akka favicon

Any HTML document this repo produces links the Akka favicon in `<head>`:

```html
<link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
```

Use that exact line. `doc.akka.io/_/img/favicon.ico` and the `hubfs/` favicon path
appear in older files and are not the canonical form.

This covers decks, case studies, battlecards, comparisons, prospect and partner pages,
website pages, ported blog posts, and one-off standalone pages. The rule reaches HTML
rendered for Akka anywhere, including files written outside this repo.

Body fragments are exempt because they have no `<head>`: per-slide `slides/NN-*/slide.html`
sources and the `hubspot.html` imports. The favicon belongs in the shell or generated
document that wraps them. Each `shell/shell.html` already carries it, and
`build-index.py` and `tools/blog-technical/port.py` emit it.

Check before committing a new page:

```bash
git ls-files '*.html' | while read f; do
  grep -qi '<head' "$f" && ! grep -qi 'rel="icon"' "$f" && echo "$f"
done
```

## Forbidden slide patterns

- **Bordered cards with a coloured bar across the top.** Do not use them. For a short
  list of parallel statements, use a thin table: hairline rules between rows, a small
  uppercase label column, and the statement beside it.
- **Content wider than the subtitle above it.** A body block sits within the measure
  the subtitle sets, never wider.

## Slide minimalism — hard budgets

Slides are cut off at the bottom because they carry too many words. Cut words. Never
shrink type, and never add a scroll.

Every content slide gets **at most three text blocks**: a headline, a subtitle, and a body
group. A slide carrying a paragraph *and* a list *and* a footnote is over budget.

| Element | Budget |
|---|---|
| Headline | 8 words, 2 rendered lines |
| Subtitle | 1 sentence, 25 words, 2 rendered lines |
| Body items | 3 items, 15 words each |
| Whole slide | 70 words visible |

A slide carries one idea. A second idea is a second slide.

**Design to 860px of usable height.** The audit viewport is 1536×960, but the
akka.io header takes 78px and a real browser adds chrome and a bookmarks bar. Content
that measures as fitting at 960 gets cut in the room.

**`overflow: hidden` hides overflow from the auditors.** `tools/auditors/slide-fit` reads
`scrollHeight`, which equals `clientHeight` inside a hidden-overflow section, so it
reports ok while text is clipped. Screenshot every slide you change and look at it.

## Deck builds

`python build-all.py` regenerates every deck; `.githooks/pre-commit` runs it on commit.
`specify-draft-registry.json` is the deck published at `platform/specify`; it is in
`build-all.py`. Genuinely unshipped drafts stay out until they ship.

`tools/auditors/pgdn-frame/audit.py` drives a deck with real PageDown keypresses and
reports how each landed slide is framed in the production band (y = 78 .. viewport):
CLIPPED, CUT_OFF, TOO_LOW, TOO_HIGH, TITLE_X. Run it on any deck whose slides "land in
the wrong place."
