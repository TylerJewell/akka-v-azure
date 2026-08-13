#!/usr/bin/env python3
"""Build the /calculator page template from the agentic cost calculator and PUT it.

The calculator is a standalone document with all of its CSS and JS inline. This scopes
that CSS under .calculator-content, wraps the body in the same class, and drops the
result into the full-page shell the comparison pages use — header partial, theme
stylesheets, footer partial.

    python tools/hubspot/port_calculator.py            # build only, writes hs-out/
    python tools/hubspot/port_calculator.py --push     # build, then PUT draft+published

The token comes from the gitignored scratchpad/.hs_env.
"""
import argparse
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sales-presentation" / "builder"))
from hubspot import to_hubspot_fragment  # noqa: E402

SOURCE = "https://tylerjewell.github.io/agentic-cost-calculator/"
SCOPE = "calculator-content"
TEMPLATE_PATH = "custom-templates/akka-calculator.html"
OUT = ROOT / "scratchpad" / "hs-out"

TITLE = "What your AI agents will cost — Akka"
DESCRIPTION = (
    "Estimate what an agentic AI workload costs to run on AWS, Azure or Google Cloud "
    "for a year, and what the same workload costs on the Akka Agentic AI Platform."
)

# The theme wins over the scoped styles on each of these. See the PORT TRANSFORM
# CHECKLIST in tools/auditors/hubspot-ready/audit.py. The checklist's wrapper-neutralize
# block is omitted: on a full-page template the content is not inside .row-fluid /
# .widget-span, and the only elements carrying those classes are the header and footer
# partials, which the resets would flatten.
PORT_CSS = """
.calculator-content h1, .calculator-content h2, .calculator-content h3,
.calculator-content h4, .calculator-content h5, .calculator-content h6 {
  color: #F1F1F1 !important; font-family: 'Instrument Sans', sans-serif !important;
}
/* The theme draws a 3px black border on the top, left and right of every cell, which
   reads as a grid over the calculator's own bottom-rule rows. Only the borders are
   reset: the checklist pairs this with background:transparent, which would erase the
   Akka column's fill. The totals row draws its own top rule and gets it back. */
.calculator-content td, .calculator-content th {
  border-top: 0 !important; border-left: 0 !important; border-right: 0 !important;
}
.calculator-content tr.tot td { border-top: 3px double var(--line) !important; }
/* Cells arrive with a #1A1A1A fill the exemplar does not have. Reset it, then put back
   the two the calculator paints itself: the Akka column and the sticky first column. */
.calculator-content td, .calculator-content th { background-color: transparent !important; }
.calculator-content td.akka, .calculator-content th.akka {
  background-color: rgba(255, 206, 74, .10) !important;
}
/* The first column is only sticky below 900px, and only then does it need a fill of its
   own to hide the columns scrolling under it. */
@media (max-width: 900px) {
  .calculator-content #tco td:first-child, .calculator-content #tco th:first-child {
    background-color: #0C0C0C !important;
  }
}
.calculator-content blockquote {
  border: 0 !important; background: transparent !important; padding: 0 !important;
}
/* === Header offset === The header is fixed and theme-overrides.css already clears it
   with body padding-top (78px desktop / 64px mobile), so the wrapper adds none of its
   own. Anchors still need it: fragment navigation scrolls the target to viewport 0,
   which is behind the header. */
.calculator-content [id] { scroll-margin-top: 88px; }
/* .tabs is a horizontal scroll container, so overflow-y computes to auto and the
   scrollport eats the 1px top border the tabs draw on hover. A row of top padding puts
   it back inside. */
.calculator-content .tabs { padding-top: 1px; }
/* The neocloud label and its select share a line wherever the column is wide enough to
   hold both; below that they stack rather than truncating the option text. */
@media (min-width: 992px) {
  .calculator-content .srcpick { flex-wrap: nowrap; }
  .calculator-content .srcq { white-space: nowrap; }
}
/* The scoped rules paint the calculator's ground inside the wrapper only; the strip
   behind the header and footer takes it here. */
body { background: #000000; }
"""

SHELL = """<!--
    templateType: page
    isAvailableForNewContent: false
    label: Agentic cost calculator
-->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://akka.io/hubfs/hub_generated/template_assets/1/180483679747/1783700344298/template_Plugin.min.css">
    <link rel="stylesheet" href="https://akka.io/hubfs/hub_generated/template_assets/1/177749484047/1783700345343/template_main.css">
    <link rel="stylesheet" href="https://akka.io/hubfs/hub_generated/template_assets/1/177749412157/1785440087003/template_theme-overrides.css">
    <link rel="stylesheet" href="https://akka.io/hubfs/hub_generated/template_assets/1/177760109709/1783700345998/template_Dev1.min.css">
{links}
    {{{{ standard_header_includes }}}}
    <style>
{css}
{port_css}
    </style>
  </head>
  <body>
    {{% global_partial path="AKKA-2024/templates/partials/header-april.html" %}}

{body}

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://akka.io/hubfs/hub_generated/template_assets/1/177749484049/1783700343576/template_main.min.js"></script>
    {{% global_partial path="AKKA-2024/templates/partials/footer.html" %}}
    {{{{ standard_footer_includes }}}}
  </body>
</html>
"""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")


def build():
    fragment = to_hubspot_fragment(fetch(SOURCE), scope=SCOPE, label="cost calculator")

    css = re.search(r"<style>(.*?)</style>", fragment, re.S).group(1)
    links = "\n".join(
        "    " + m for m in re.findall(r'<link\b[^>]*rel="stylesheet"[^>]*>', fragment)
    )
    body = re.search(r'(<div class="%s">.*</div>)' % SCOPE, fragment, re.S).group(1)
    # The site header carries the Akka mark, so the calculator's own is a second one.
    body, n = re.subn(r'<p class="brand">.*?</p>\s*', '', body, flags=re.S)
    if n != 1:
        sys.exit(f"expected one brand mark to strip, removed {n}")

    page = SHELL.format(
        title=TITLE, description=DESCRIPTION, links=links,
        css=css, port_css=PORT_CSS, body=body,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "akka-calculator.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page), "bytes")
    return out


def push(path):
    token = None
    for line in (ROOT / "scratchpad" / ".hs_env").read_text(encoding="utf-8").splitlines():
        if line.startswith("HUBSPOT_TOKEN="):
            token = line.split("=", 1)[1].strip()
    if not token:
        sys.exit("HUBSPOT_TOKEN not found in scratchpad/.hs_env")

    import subprocess
    for env in ("draft", "published"):
        url = f"https://api.hubapi.com/cms/v3/source-code/{env}/content/{TEMPLATE_PATH}"
        r = subprocess.run(
            ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-X", "PUT", url,
             "-H", f"Authorization: Bearer {token}", "-F", f"file=@{path}"],
            capture_output=True, text=True,
        )
        print(env, r.stdout.strip())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    p = build()
    if a.push:
        push(p)
