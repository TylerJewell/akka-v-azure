# Presentations

Akka presentation decks. Each deck lives in its own `<name>-presentation/` folder,
is built from per-slide source files into self-contained HTML, and is published via
GitHub Pages.

**Live index:** https://tylerjewell.github.io/presentations/

## Layout

```
<name>-presentation/
  slides/NN-*/        one folder per slide (slide.html / slide.css / slide.js / meta.json)
  shell/              shell.html template + shared.css + nav.js (+ kiosk.js)
  builder/build.py    assembles slides -> generated/<mode>/index.html
  builder/bundle.py   (Gartner) inlines images -> single-file generated/akka-gartner-deck.html
  presenters/*.json   name / title / email / linkedin for personalized builds
  generated/          build output served by Pages
index.html            the landing page that lists every deck
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

### 5. Update index.html
When adding a presentation (or changing a title/date), edit `index.html`:
- One `<li>` per presentation — **list each deck once** (no duplicate entries).
- **Link text = the deck's first-slide title** (not the file name).
- Link target = the published entry point
  (`<name>-presentation/generated/overview/` or the single-file deck).
- Summary line = the deck's subtitle + `Last updated <YYYY-MM-DD>`, where the date is the
  last commit on the linked file:
  `git log -1 --format=%cs -- <path-to-linked-file>`.
- These dates are hardcoded; refresh them whenever you republish a deck.

## Publishing

Pushing to `main` triggers a GitHub Pages rebuild (~30–60s). Each deck renders at
`https://tylerjewell.github.io/presentations/<path-in-repo>`.
