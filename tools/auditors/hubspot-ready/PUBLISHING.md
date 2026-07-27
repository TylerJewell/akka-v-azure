# HubSpot Publishing Playbook

The full deploy procedure for pushing Akka pages/decks/blogs into HubSpot. Companion to
`audit.py` (run the auditor first — it catches the CSS/content traps this doc's ports must avoid).

- **Portal** `45500578`. **Token** in `scratchpad/.hs_env` → `$HUBSPOT_TOKEN`; every call sends
  `Authorization: Bearer $HUBSPOT_TOKEN`.
- Build request JSON with Python `json.dumps` (never hand-escape); read HTML/postBody files as UTF-8.
- Verified end-to-end 2026-07-27 (5 decks, 12 compares, 16 blog refreshes, 25 retirements, /platform migration).

---

## 1. Deck pages

Each deck is a **site-page** at `platform/<deck>` using custom template
`custom-templates/akka-<deck>-wrapper.html`. The page's `layoutSections`/`widgets` are **empty** —
all content lives in **three partials** the template `{% include %}`s:
`custom-templates/partials/<deck>-{styles,body,scripts}.html`.

- **Scope / wrapper class** = `<deck>-content` (e.g. `optimize-content`). Each partial starts with a
  HubL header `<!--\n  templateType: "none"\n  isAvailableForNewContent: false\n-->` and the
  body/scripts end with `<!-- DEMO_HTML_MARKER -->` / `/* DEMO_JS_MARKER */` (preserve these).
- **Deck sources (which repo file feeds which page):**
  - `optimize` ← `sales-presentation/generated/optimize/index.html` (BUILT)
  - `specify` ← `sales-presentation/generated/specify/index.html` (BUILT)
  - `overview`, `sdk`, `verify` ← the hand-authored `akka-<deck>/index.html` at repo root (NOT the generated ones)
- **Port:** build the deck → `hubspot.py` `to_hubspot_fragment(html, base_dir=…, scope='<deck>-content')`
  (the build's own `hubspot.html` uses the default `akka-embed` scope — re-run with the right scope) →
  split the fragment into: styles = the `<style>` block, body = the `<div class="<deck>-content">…</div>`
  with `<script>`/`<style>` stripped out, scripts = all inline JS concatenated → `PUT` each to the
  source-code **draft AND published** endpoints.
- **PRESERVE the appended port-transform CSS block.** The live styles partial has HubSpot-only overrides
  appended after the deck CSS, starting at the comment `/* === Neutralize HubSpot wrapper containers …`.
  Extract that block from the current live partial and re-append it before `</style>` — regenerating from
  source drops it (headings grey out, content width-caps, tables get a grid). See `audit.py` PORT TRANSFORM CHECKLIST.
- **Sticky slides need a header offset.** The akka.io header is `position:fixed`, **78px desktop / 64px mobile**.
  A `top:0` sticky slide (e.g. the Optimize console `#cog-sticky`) tucks under it. Add to the port CSS
  (HubSpot-only): `@media (min-width:1001px){ .<deck>-content #cog-sticky{ top:78px!important; height:calc(100dvh - 78px)!important } }`
  (mobile un-stickies ≤1000px, so no offset there).

## 2. Compare pages

Each compare is a **site-page** at `compare/akka-vs-<name>` using a **single** template
`custom-templates/comparison-<name>.html` — a full page (doctype/head with inline `<style>`,
header partial, `<div class="comparison-content">…</div>`, boilerplate jQuery + `template_main` scripts,
footer partial). Shared scope `comparison-content`.

- **Source** = repo `comparisons/compare-<name>.html`. **Port:** `to_hubspot_fragment(scope='comparison-content')`
  → splice the new `<style>` inner and the new `comparison-content` div inner into the existing template
  (balance-match the wrapper `</div>`); PUT draft+published.
- **Inject the compare's inline reveal script.** The source has an `IntersectionObserver` that adds `.in`
  to reveal elements. If you drop it, reveal-animated content stays at `opacity:0` → **blank page**. Insert
  it before the boilerplate `<script src="…/jquery…">`.
- Repo has `compare-orkes` / `compare-vercel-ai-sdk` with no matching `comparison-*.html` template — skip.

## 3. Blog posts

CMS v3 Blog Posts API. Find by slug: paginate `GET /cms/v3/blogs/posts?limit=100` (slugs look like `blog/<slug>`).

- **Edit:** `PATCH /cms/v3/blogs/posts/{id}` `{"postBody": …}`. **Publish:** `POST /cms/v3/blogs/posts/{id}/draft/push-live`
  → **HTTP 204, empty body** (don't `json.load` it). Live page CDN-lags ~30–60s; the API `postBody` is source of truth.
- **Retire (drop from the blog roll, keep the URL live — NEVER unpublish, that 404s the URL):** set the per-post
  boolean widget `hide_from_listing` = true: `PATCH {"widgets": {…existing, "hide_from_listing": {"body": {"value": true}}}}`
  + push-live. The listing template respects it. Optionally add a "Retired" blog tag as metadata
  (`POST /cms/v3/blogs/tags {"name":"Retired"}` → add its id to each post's `tagIds`). Blog id `162235293071`;
  item template `AKKA-2024/templates/blog-post.html`.

## 4. Slug / URL changes

- **Rename:** `PATCH /cms/v3/pages/site-pages/{id} {"slug":"platform/<deck>"}` + push-live.
- HubSpot auto-creates a 301 for the **first** rename but NOT reliably for a batch → create explicit ones:
  `POST /cms/v3/url-redirects {routePrefix:"/offerings/<x>", destination:"https://akka.io/platform/<x>",
  redirectStyle:301, isMatchFull:true, isProtocolAgnostic:true, isTrailingSlashOptional:true}`.
- **Mega-menu deck links are hardcoded** in the module `AKKA-2024/modules/Header 2026 Mega.module/module.html`
  (source-code API, PUT draft+published). The nav-menu objects (`/content/api/v2/menus`) do NOT hold them.
  The homepage "Platform Overview" button links to the overview page **by ID**, so it auto-resolves after a slug
  rename — nothing to edit.

## 5. Files, demos, diagrams

- **Files API:** search `GET /files/v3/files/search?parentFolderIds=<id>` (`name` query ≤20 chars; paginate
  `paging.next.after`). Upload `POST /files/v3/files` multipart (`file`, `folderId`, `fileName`,
  `options={"access":"PUBLIC_INDEXABLE","overwrite":true,…}`). **Use `folderId`, NOT `folderPath` — Git Bash
  mangles a leading `/path` into a Windows path.** Folders: `/demos` = `217977738634`, `/website/diagrams/png` = `185852048914`.
- **Demo links:** deck sources use relative `<name>/index.html` (`resilience/resilience.html`, `risk-survey/index.html`)
  that 404 on HubSpot → rewrite to `https://akka.io/hubfs/demos/<name>.html` and upload the demo if missing.
- **Blog diagrams "invisible in light mode"** (iOS Smart Invert / forced-light): the transparent white/light PNGs
  under `/website/diagrams/png/` vanish on light backgrounds. Point `<img src/srcset/href>` at the black-backed
  `-N-bg` version (opaque, baked-in `#000000`); generate any missing by flattening the transparent original onto black.

## 6. Source Code API + preview

- `GET`/`PUT /cms/v3/source-code/{draft|published}/content/<path>` (PUT = multipart `file=@…`). Push to **BOTH**
  draft and published; **published source-code = live immediately** (no separate publish step).
- **No shareable draft-preview URL** (`/_hcms/preview/…` and `?hs_preview=true` both 404 unauthenticated; the page
  object has no `previewKey`). Draft template changes are viewable only in Design Manager (logged in). To canary a
  deck, push ONE to published (it's already live; changes are additive) and review the real URL.

## 7. Content rules (see `audit.py` §8)

- The **actor-terminology** rule was **removed 2026-07-27** (no longer applies).
- Never auto-fix **"Akka Agentic AI Platform"** without owner approval.
- On old posts, **preserve the historical "who-did-what" record** — leave "Lightbend" where a sentence narrates a
  past action by the company at that time (e.g. "allows Lightbend to expand our investment"); only change
  present-tense product/company references to "Akka".
- Leave "Lightbend"/"library" that appears **inside working GitHub / doc / image URLs** (e.g.
  `github.com/lightbend/akka-projection-grpc-benchmark`, `doc.akka.io/libraries/…`, `downloads.lightbend.com/…`) —
  rewriting them breaks the link.
