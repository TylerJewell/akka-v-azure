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
- **A partial-only change does NOT reliably invalidate the rendered page.** After PUTting the
  three partials, `POST .../draft/push-live` alone often keeps serving a cached render (verified
  2026-07-29: the styles partial had the new CSS via the API while the page still served the old).
  What forces a re-render is marking the page dirty first: `PATCH /cms/v3/pages/site-pages/{id}`
  with any field at its current value (e.g. `{"htmlTitle": <current>}`), then push-live. Build the
  PATCH body with `json.dumps` and read the current page as UTF-8 — the deck titles contain em
  dashes and a shell-quoted body returns 400. Allow 60-90s for the CDN afterwards.
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

## The render-forcing PATCH can mojibake the page title

Forcing a re-render means PATCHing a field, and echoing `htmlTitle` back is the
least invasive choice. Decode the GET response as strict UTF-8. Reading it with
`errors='replace'`, or letting a cp1252 default apply, turns an em dash into
`\xe2\x80\x9d`-style junk (it shows in the browser tab as three garbled glyphs),
and the PATCH writes that damage back.

Send the body as a file (`--data-binary @file`) written from
`json.dumps(...).encode('utf-8')`; `ensure_ascii` keeps non-ASCII as `\uXXXX`
escapes so no shell layer can re-encode them.

To detect the damage on any page: `t.encode('cp1252').decode('utf-8')` succeeds
and returns something different only when the text is mojibaked. That expression
is also the repair.

## Reserving image space in modules

Almost every `<img>` a module emits has a HubL src, so literal `width`/`height`
would be wrong on most pages. Take the dimensions from the field instead, and
guard them so nothing is emitted when the field has none:

```
<img src="{{ module.background_image.src|escape_url }}" loading="lazy"
     {% if module.background_image.width and module.background_image.height %}
     width="{{ module.background_image.width }}"
     height="{{ module.background_image.height }}" {% endif %}>
```

Fields of `"type": "image"` carry `.width` and `.height`. Blog values do not:
`post.featured_image` and `content.blog_post_author.avatar` are bare URL strings.
Where the rendered size is fixed and square (author avatars at 25px) literal
attributes are safe; otherwise reserve the space in CSS.

Sizing only helps where CSS leaves a dimension free. `width:100%;height:100%`
and a wrapper with `aspect-ratio` already reserve the box, so attributes there
are consistency, not a fix. An absolutely positioned image inside such a wrapper
must be left alone: it renders at its intrinsic size and attributes would change
what the reader sees.

`scratchpad/cls.py` reports layout shift, the elements that moved, unsized
images, and declared-vs-intrinsic ratio per page. A non-zero `skew` means a
width/height pair is lying and the image is being distorted.

## Containers that JS fills need their line reserved

An element that is empty in the served HTML and gets text from JS is zero-height
on first paint, so everything below it jumps when the text lands. The blog
listing moved 28px this way: `#mf-results-info` is empty markup that the filter
script fills with "93 of 93 showing" once it has counted the posts. A
`min-height` matching the rendered line holds the space.

This looks like an image problem and is not one. Attribute it by timing rather
than by eye: sample the moving element's document offset every 100ms while
recording image-complete events and `document.fonts.ready`, then read which event
the move coincides with. On the blog it coincided with neither the featured
images nor the font swap.

Diff layout state with an attribute stamped onto each node, never with an index
from `querySelectorAll`. Indices shift when JS inserts nodes, so an index-keyed
diff silently compares different elements and invents movement that never
happened.

## Instrument Sans is served from this domain — do not re-add Google Fonts

The head used to link `fonts.googleapis.com/css2?family=Instrument+Sans` while
HubSpot was already injecting `@font-face` rules for the same family pointing at
its own proxy under `/_hcms/googlefonts/`. Two sources for one family, and the
Google copy is the one that rendered, behind a stylesheet request on a third
origin and then a font request on a fourth. Text painted in a fallback face and
repainted seconds later when the font finally arrived — the whole site, every
page, every load.

`base.html` now drops the Google link and preloads the same-origin files for
400/500/600/700. `crossorigin` is required on those preloads even though they are
same-origin, because fonts are always fetched in CORS mode; without it the file
is fetched twice and the preload is wasted.

On the blog this moved `fonts.ready` from 6502ms to 3418ms, which is earlier than
the text's first paint, so the text renders once instead of twice. Box geometry
was byte-identical before and after, so HubSpot's static 400/500/600/700 faces
wrap the same as Google's variable font. HubSpot's proxy carries no italic face;
the site had one unused italic rule, so nothing regressed.

To check the source in use: watch `Network.responseReceived` for `.woff2` and
confirm every hit is on this domain, never `fonts.gstatic.com`.

## Rows that square up after load must reserve their space in CSS

The blog's three featured cards clamp the title to two lines and line the
descriptions up across the row. A one-line title therefore has to hold two lines
of space. That space was only being taken after load, so the text under every
short title dropped at that moment while the card with a naturally two-line title
never moved — which is what makes this look like an image or font problem and is
neither.

`min-height: 2lh` on the heading fixes it. Put it on the heading rather than the
clamp box: `lh` is the element's own line box, and the clamp box's line-height
differs from the heading's, which left a 3px mismatch.

The general rule: if a row is aligned by anything that runs after first paint,
reserve the same space in CSS so the aligned state is the first state. Verify by
sampling each column's height and its next element's offset every 100ms across
the load — they must be equal to each other and constant from the first sample.

## font-display on HubSpot-injected faces cannot be overridden

HubSpot injects `@font-face` with `font-display: swap`, which paints in a
fallback and repaints when the font lands, visibly changing the type.

Redeclaring the same family with `font-display: optional` does not fix it, in
either order. `scratchpad/facetest.py` serves one page declaring the family twice
against a font held back three seconds, and measures a probe span's width: the
width changes when the font lands whether the optional face is declared before or
after the swap face. While any swap face for a family exists, swap behaviour
applies. Do not spend time on shadowing.

What does help is the preloads in `base.html`: same-origin, highest priority, so
the font is normally in hand before first paint and there is nothing to swap. A
hard refresh bypasses the cache and will still show the swap — test with an
ordinary reload.

Eliminating it on cold loads means stopping the injection, which is a theme font
setting rather than a source-code change, and it changes font resolution site
wide.

## The font swap shows on warm loads, not cold ones

Counter-intuitive and worth measuring before theorising. A cold load of the blog
first paints at about 2830ms, by which time the preloaded font has arrived, so
the text renders once. A warm load paints from cache at about 670ms, sooner than
the font can be applied, so text shows in the fallback for roughly 30ms and then
repaints. Testing with a hard refresh hides this, because a hard refresh forces
the slow path.

`font-display` cannot fix it on this site: HubSpot injects the family with
`font-display: swap`, and swap wins for the family no matter what else is
declared.

What can be fixed is how different the fallback looks. `theme-overrides.css`
declares an `Instrument Sans Fallback` family: `local('Arial')` restated with
Instrument Sans's metrics through `size-adjust`, `ascent-override` and
`descent-override`, inserted into the font stacks ahead of the generic fallbacks.

**Choose the fallback before tuning the numbers.** One `size-adjust` can only
match x-height and advance width together if the fallback shares the target's
proportions. Arial does not: matching its x-height to Instrument Sans leaves the
advance width 4.8% short at weight 500, which renders visibly narrow and then
widens. Segoe UI leaves 0.2%. `scratchpad/bestfallback.py` measures the installed
candidates and ranks them by that residual. Segoe UI is tried first for Windows,
with an Arial-based family behind it for macOS and Linux.

**Declare only the weights you can address.** `local('Segoe UI')` resolves to one
physical file, so declaring it at 600 and 700 as well makes bold text render
un-bolded and then thicken. `local('Segoe UI Bold')` does not resolve at all.
Weights 400 and 500 carry the body copy and headings; 600 and 700 fall through to
the plain family names at the end of the stack, where ordinary matching picks the
right physical face.

**Watch the weight mapping when measuring.** Arial ships 400 and 700 only, so a
browser renders Regular at 500 and Bold at 600. Measuring 600 against Arial
Regular gives a size-adjust 5.8% too high. Measure faces through real DOM spans;
canvas `measureText` resolves weights differently and produced a false reading
that `size-adjust` was being ignored on `local()` sources.

Measured after: a probe span in the fallback matches Instrument Sans to 0.00% in
both advance width and line height at weights 400 and 500, and cold and warm
loads report one geometry state for the whole load. The swap changes letter
shapes and changes nothing else.

Derive the numbers with `scratchpad/metrics.py`, which renders the same string in
each candidate fallback on a canvas and reports width, ascent and descent.
