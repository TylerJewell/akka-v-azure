# Presentations

Akka presentation decks. Each deck lives in its own `<name>-presentation/` folder,
is built from per-slide source files into self-contained HTML, and is published via
GitHub Pages.

**Live index:** https://tylerjewell.github.io/presentations/

## Public vs. internal — one rule

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

It pulls each deck's link text from its first-slide headline, the kicker from that
slide's subtitle, and the `Last updated` date from the last commit on the linked file
(`git log -1 --format=%cs`). Each deck is listed once, **ordered latest-updated first**
(by the linked file's last commit time).

To add a presentation, append an entry to the `PRESENTATIONS` list at the top of
`build-index.py` — its `dir` and the published `link` (e.g.
`<name>-presentation/generated/overview/` or a single-file deck) — then re-run it and
commit `index.html`.

## HubSpot import builds

Every sales deliverable is published in **two** forms from one source:

- **GitHub Pages page** — the standalone HTML we host (`index.html`).
- **HubSpot fragment** — a paste-ready import for marketing (`hubspot.html`),
  with our global CSS scoped under `.akka-embed` (so it can't disturb HubSpot's
  header/footer), relative `images/` rewritten to absolute `hubfs/` URLs, external
  CSS inlined, and the `<html>/<head>/<body>` wrapper stripped.

Covered: the three sales decks (`overview`, `specify`, `token-shredder`), the
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
