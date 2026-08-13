# Presentations

Akka presentation decks. Each deck lives in its own `<name>-presentation/` folder,
is built from per-slide source files into self-contained HTML, and is published via
GitHub Pages.

**Live index:** https://tylerjewell.github.io/presentations/

## Public vs. internal

**Everything tracked in this repo is published.** GitHub Pages serves the entire
committed tree at the Live index URL above — *linked or not*. A file that isn't
referenced by `index.html` is still reachable by direct URL and is crawlable, and the
source is visible in the public repo. There is no such thing as an "unlisted, private"
committed file here.

Therefore: **if it must stay private, it does not belong in the tracked tree.**
Internal / confidential material — working notes, RFP responses, sales enablement,
authoring guides/templates, fact sheets, roadmaps, positioning audits — lives under
**`_internal/`**, which is git-ignored (`/_internal/`) and never published. Keep it
there; do not copy an internal doc up into the repo root "just to view it."

Bright line for any audit or scan: **tracked ⇒ public; `_internal/` ⇒ private.** Before
adding a file, ask *"Am I OK with this on the public internet?"* — if no, it goes in
`_internal/`.

## Layout

```
<name>-presentation/
  slides/NN-*/        one folder per slide (slide.html / slide.css / slide.js / meta.json)
  shell/              shell.html template + shared.css + nav.js (+ kiosk.js)
  builder/build.py    assembles slides -> generated/<mode>/index.html
  builder/bundle.py   (Gartner) inlines images -> single-file generated/akka-gartner-deck.html
  presenters/*.json   name / title / email / linkedin for personalized builds
  generated/          build output served by Pages
build-index.py        regenerates index.html (titles from slides, dates from git log)
index.html            the landing page that lists every deck (generated — do not hand-edit)
.nojekyll             tells Pages to serve files verbatim (do not delete)
```

## Rules for creating or updating a presentation

### 1. Slide numbering
- Number slide folders as clean sequential integers: `00`, `01`, `02`, …
- **No alpha/beta suffixes** (`03b-sla`). To insert a slide, renumber the sequence —
  don't append a letter. An alpha-suffixed folder is a sign of an unfinished cleanup;
  fix or delete it.
- Keep `builder/slide-registry.json` in sync. A slide folder that isn't listed there
  won't build.

### 2. Browser-tab title
- Each presentation's `shell/shell.html` `<title>` **must match that deck's first-slide
  headline** (`<h1 class="title-headline">`), formatted `<Title> — Akka`.
- Never copy a shell from another presentation without updating `<title>` — that is how a
  deck ends up showing another deck's title in the browser tab.

### 3. Build before publishing
- Any edit to slides, shell, or presenter data requires a rebuild:
  - `python builder/build.py [--mode overview] [--presenter tyler]`
  - Gartner single-file deck also needs: `python builder/bundle.py`
- Commit the regenerated `generated/` output — Pages serves it.

### 4. What gets committed
- Track only the build that is meant to be shared:
  - **Gartner** — the generated HTML + assets (`overview/` and `akka-gartner-deck.html`).
  - **Sales** — only `generated/overview/` (the personalized overview).
- **Never commit the build `*.zip` archives** — they stay git-ignored.
- Each presentation's own `.gitignore` governs its `generated/`; the root `.gitignore`
  must not blanket-ignore a presentation's published build.

### 5. Regenerate index.html
The landing page is generated — **do not hand-edit `index.html`**. After (re)building a
deck, run:

```bash
python build-index.py
```

`build-index.py` pulls each deck's link text from its first-slide headline, the kicker
from that slide's subtitle, and the `Last updated` date from the last commit on the linked file
(`git log -1 --format=%cs`). Each deck is listed once, **ordered latest-updated first**
(by the linked file's last commit time).

To add a presentation, append an entry to the `PRESENTATIONS` list at the top of
`build-index.py` — its `dir` and the published `link` (e.g.
`<name>-presentation/generated/overview/` or a single-file deck) — then re-run it and
commit `index.html`.

### 6. Corpus numbers (regulations / controls / penalties)
Compliance counts are **live from the corpus, never hardcoded from memory**. Any time you
edit content that cites them — a deck, an llms file, a battlecard, the website, anything —
re-read the numbers from the corpus before publishing. Do not carry a number forward from a
prior edit.

The corpus is a separate repository (`../explain`, i.e. `C:\Users\tyler\explain`). Before
reading:
1. Go into the corpus repo and pull the latest, so any newly merged PRs are reflected. The
   numbers depend on which branch is checked out — confirm you are on the branch that is
   canonical for publishing.
2. Read the counts with the script here, pointing it at the corpus:

   ```bash
   AKKA_CORPUS_PATH="C:/Users/tyler/explain/framework/regulations" python _build/corpus_counts.py
   ```

   `corpus_counts.py` emits `regulations`, `controls` (authored, placeholders excluded),
   and penalty-bearing `controls` / `regulations`. This script is the single source of truth and
   supersedes any manual grep counts. An unreachable corpus fails the build, so a stale
   number never ships.

3. Apply the same set everywhere the edit touches. For deck sources, fix the slide/asset then
   rebuild `generated/`; for marker-based pages, `_build/apply_corpus.py` rewrites the marked
   numbers in place.

## Design system

The rulebook for how these decks look. Every deck is dark-themed, built on the
palette below, and set in **Instrument Sans** (headings/body) with **JetBrains Mono**
for labels, code, and stat numbers.

### Color palette (canonical)

The values below are the official brand palette. Use them by name; do not invent
near-equivalents.

| Name | Hex | Use |
|---|---|---|
| **Black** | `#000000` | Primary background. |
| **Medium Black** | `#141414` | Backgrounds for tables and called-out content boxes. |
| **White** | `#F1F1F1` | Primary text — body copy and headlines. |
| **Spark Yellow** | `#FFCE4A` | Primary accent color; often used in subheadlines. |
| **River Blue** | `#00DBDD` | Primary hyperlink color (and clickable / hover affordances). |
| **Fire Red** | `#FF5400` | Signifies a negative idea or a bad outcome. |
| **Electric Green** | `#72D35B` | Signifies a positive idea or a good outcome. |
| **Soft Grey** | `#A6A6A6` | Subtext that is still important to read easily. |
| **Medium Grey** | `#4E4E4E` | Very minor points — sources, footnotes, and some backgrounds. |

Drop-in CSS custom properties for a new deck:

```css
:root {
  --black:#000000; --medium-black:#141414; --white:#F1F1F1;
  --yellow:#FFCE4A;        /* Spark Yellow — accent / subheads */
  --blue:#00DBDD;          /* River Blue — links / hover */
  --red:#FF5400;           /* Fire Red — negative */
  --green:#72D35B;         /* Electric Green — positive */
  --soft-grey:#A6A6A6;     /* important subtext */
  --medium-grey:#4E4E4E;   /* footnotes, sources, minor backgrounds */
}
```

### Page chrome

Every HTML document links the Akka favicon in `<head>`:

```html
<link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
```

Body fragments — per-slide `slide.html` sources and `hubspot.html` imports — have no
`<head>` and are exempt. Their wrapping shell carries it.

### Applying it

- **Spark Yellow is the single accent.** Reserve it for the accented span
  in a headline, subheadlines, and key emphasis — not for large fills.
- **Links and interactivity in River Blue.** Hyperlinks are River Blue; interactive
  elements signal clickability by shifting to River Blue on hover (border and label).
- **Red/Green are semantic only.** Fire Red for a bad outcome, Electric Green for a good
  one — never decoratively.
- **Text hierarchy:** White for primary copy, Soft Grey for secondary-but-readable
  subtext, Medium Grey for footnotes/sources.
- **Surfaces:** Black is the page; Medium Black lifts a table or a called-out box off it.

> Note: some earlier decks predate this guide and use near-equivalents (e.g. `#F5C518`
> yellow, `#28C840` green, `#fff` white). Reconcile to the canonical values above when
> touching those files.

## HubSpot import builds

Every sales deliverable is published in **two** forms from one source:

- **GitHub Pages page** — the standalone HTML we host (`index.html`).
- **HubSpot fragment** — a paste-ready import for marketing (`hubspot.html`),
  with our global CSS scoped under `.akka-embed` (so it can't disturb HubSpot's
  header/footer), relative `images/` rewritten to absolute `hubfs/` URLs, external
  CSS inlined, and the `<html>/<head>/<body>` wrapper stripped.

Covered: the three sales decks (`overview`, `specify`, `optimize`), the
customer case studies, and the competitor comparisons.

```bash
python build-all.py          # builds BOTH forms for everything
```

Outputs:
- Decks → `sales-presentation/generated/<deck>/hubspot.html` (beside `index.html`)
- Case studies → `case-studies/hubspot/<name>.html`
- Comparisons → `comparisons/hubspot/<name>.html`

**Every commit regenerates both forms automatically** via `.githooks/pre-commit`
(which runs `build-all.py` and stages the outputs). One-time setup per clone:

```bash
git config core.hooksPath .githooks
```

The transform lives in `sales-presentation/builder/hubspot.py`; `build.py` emits
each deck's `hubspot.html` inline. The `hubfs/` image base is set by
`build.py --hubspot-image-base` (default `https://akka.io/hubfs/akka-platform-intro/`,
which the overview and specify decks share). Case studies and comparisons use no
images today; their gallery `index.html` fragments keep relative inter-page links,
which HubSpot page setup must map.

## Publishing

Pushing to `main` triggers a GitHub Pages rebuild (~30–60s). Each deck renders at
`https://tylerjewell.github.io/presentations/<path-in-repo>`.
