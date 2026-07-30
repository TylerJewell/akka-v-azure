# Removing the font swap on akka.io

The type repaints after load because HubSpot injects `@font-face` for Instrument
Sans with `font-display: swap`. While any swap face for a family exists, swap
behaviour applies to that family, so declaring a second face with
`font-display: optional` changes nothing. `scratchpad/facetest.py` demonstrates
this against both declaration orders.

The injection is driven by the theme setting `global_fonts.primary` and
`global_fonts.secondary` being the Google variant of Instrument Sans. It stops
when those fields no longer name a Google font.

## Outcome: the setting change is not available

The theme font picker on this portal offers Common Fonts and All Fonts only,
which are HubSpot's web-safe and Google lists. There is no custom font, so the
family cannot be named without selecting the Google entry, and the injection
cannot be stopped. Do not change those fields: a Common Font would rename the
family in `body`, `p`, `a` and `h1`-`h6` and drop the site to a web-safe face.

## What was done instead

The visible symptom was headings reshaping while body copy looked steady. The
heading font fields carry a `serif` fallback and the body field carries
`sans-serif`, so headings painted in Times and then became Instrument Sans, while
body copy painted in Arial and changed too little to notice. `theme-overrides.css`
now ends with a rule giving the 11 heading-derived selectors the same sans-serif
fallback as body copy. Verified by blocking the font files: headings render in a
near-identical sans face rather than Times.

The family in that rule still comes from `{{ primary_font }}`, so the theme
setting continues to control it.

## Prepared but not applied

1. `AKKA-2024/css/elements/_typography.css` — 8 self-hosted faces (400/500/600/700,
   upright and italic), `font-display: optional`, addressed on akka.io so they are
   same-origin with the page. Copy in `tools/hubspot/_typography.css`.
2. The `require_css` for it in `base.html` is commented out again. Loading it costs
   a 29,208 byte fetch and changes nothing while HubSpot's swap faces exist.
3. `tools/hubspot/base.flip.html` repoints the preloads at the self-hosted files.

Re-enable 2 and publish 3 only if a custom font becomes available in the theme
picker.

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
