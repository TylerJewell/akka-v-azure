# Removing the font swap on akka.io

The type repaints after load because HubSpot injects `@font-face` for Instrument
Sans with `font-display: swap`. While any swap face for a family exists, swap
behaviour applies to that family, so declaring a second face with
`font-display: optional` changes nothing. `scratchpad/facetest.py` demonstrates
this against both declaration orders.

The injection is driven by the theme setting `global_fonts.primary` and
`global_fonts.secondary` being the Google variant of Instrument Sans. It stops
when those fields no longer name a Google font.

## Already applied

1. `AKKA-2024/css/elements/_typography.css` — 8 self-hosted faces (400/500/600/700,
   upright and italic), `font-display: optional`, addressed on akka.io rather than
   the portal's hubspotusercontent host so they are same-origin with the page.
   A copy is in `tools/hubspot/_typography.css`.
2. `AKKA-2024/templates/layouts/base.html` — the `require_css` for that file is no
   longer commented out, and loads ahead of the other stylesheets.

Interim cost until the setting changes: the browser fetches
`InstrumentSans-Regular.woff2` (29,208 bytes) in addition to the four proxy files
it still uses. Typography is unchanged — body, headings and weights verified
identical on the home, blog and overview pages.

## The setting change

In Design Manager, edit the theme settings for AKKA-2024. Set both
`global_fonts.primary` and `global_fonts.secondary` to a custom font named
exactly `Instrument Sans`, not the Google entry of the same name. The name has to
match, because `theme-overrides.css` emits it verbatim into `body`, `p`, `a` and
`h1`–`h6` through `{{ body_font.style }}` and `{{ h1_font.style }}`. A mismatch
drops every page to `sans-serif`.

If the portal offers no custom-font variant, stop here and revert step 2. The
preloads already in place mean the swap is only visible on a cold cache.

## Apply with the setting change

`tools/hubspot/base.flip.html` is `base.html` with the four preloads repointed at
the self-hosted files. Do not publish it earlier: until the injection stops, it
preloads four files the browser will not use.

    PUT AKKA-2024/templates/layouts/base.html   (draft and published)

## Verify

Load the blog in a fresh profile with the cache disabled and confirm:

- no request to `/_hcms/googlefonts/`
- requests to `akka.io/hubfs/AKKA-2024/Fonts/InstrumentSans-*.woff2`
- every entry in `document.fonts` with status `loaded` reports `display=optional`
- a probe span in Instrument Sans holds one width for the whole load — a second
  width means the type still repaints

Italic text becomes real italic rather than synthesised oblique, because the
proxy carried upright faces only.
