#!/usr/bin/env python3
"""Build a calculator page template from a cost calculator and PUT it.

Each calculator is a standalone document with all of its CSS and JS inline. This scopes
that CSS under .calculator-content, wraps the body in the same class, and drops the
result into the full-page shell the comparison pages use — header partial, theme
stylesheets, footer partial.

    python tools/hubspot/port_calculator.py                # build every page, writes hs-out/
    python tools/hubspot/port_calculator.py sovereign      # build one
    python tools/hubspot/port_calculator.py --push         # build, then PUT the template
                                                           # and publish the site page

The token comes from the gitignored scratchpad/.hs_env.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sales-presentation" / "builder"))
from hubspot import to_hubspot_fragment  # noqa: E402

CALC = ROOT.parent / "calculator"
SCOPE = "calculator-content"
OUT = ROOT / "scratchpad" / "hs-out"
API = "https://api.hubapi.com"

# The theme wins over the scoped styles on each of these. See the PORT TRANSFORM
# CHECKLIST in tools/auditors/hubspot-ready/audit.py. The checklist's wrapper-neutralize
# block is omitted: on a full-page template the content is not inside .row-fluid /
# .widget-span, and the only elements carrying those classes are the header and footer
# partials, which the resets would flatten.
SHARED_CSS = """
.calculator-content h1, .calculator-content h2, .calculator-content h3,
.calculator-content h4, .calculator-content h5, .calculator-content h6 {
  color: #F1F1F1 !important; font-family: 'Instrument Sans', sans-serif !important;
}
/* The theme draws a 3px black border on the top, left and right of every cell, which
   reads as a grid over the calculator's own bottom-rule rows. The borders reset here and
   the fill resets below; a page that paints cells of its own restores them in its own
   block. */
.calculator-content td, .calculator-content th {
  border-top: 0 !important; border-left: 0 !important; border-right: 0 !important;
}
.calculator-content tr.tot td { border-top: 3px double var(--line) !important; }
/* Cells arrive with a #1A1A1A fill the exemplar does not have. */
.calculator-content td, .calculator-content th { background-color: transparent !important; }
.calculator-content blockquote {
  border: 0 !important; background: transparent !important; padding: 0 !important;
}
/* === Header offset === The header is fixed and theme-overrides.css already clears it
   with body padding-top (78px desktop / 64px mobile), so the wrapper adds none of its
   own. Anchors still need it: fragment navigation scrolls the target to viewport 0,
   which is behind the header. */
.calculator-content [id] { scroll-margin-top: 88px; }
/* The scoped rules paint the calculator's ground inside the wrapper only; the strip
   behind the header and footer takes it here. */
body { background: #000000; }
"""

# physical.html paints four fills of its own, which the transparent-cell reset takes.
PHYSICAL_CSS = """
.calculator-content td.akka, .calculator-content th.akka {
  background-color: rgba(255, 206, 74, .10) !important;
}
/* The API-vs-Akka table marks the row at the entered volume with a fill on the whole
   row. */
.calculator-content #beTbl tr.cross td:not(.akka) {
  background-color: rgba(255, 206, 74, .09) !important;
}
/* The first column is only sticky below 900px, and only then does it need a fill of its
   own to hide the columns scrolling under it. */
@media (max-width: 900px) {
  .calculator-content #tco td:first-child, .calculator-content #tco th:first-child {
    background-color: #0C0C0C !important;
  }
}
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
"""

# /calculator serves the infrastructure-only variant: both columns show physical
# infrastructure, so the build-it-yourself total carries no support or professional
# services and the Akka figure carries no margin. index.html is the margin-bearing page
# and is not what this publishes.
#
# Sources are read from the calculator repo's working tree rather than its GitHub Pages
# URL, so a port picks up edits that have not been committed and deployed yet.
PAGES = {
    "calculator": {
        "source": CALC / "physical.html",
        "out": "akka-calculator.html",
        "template": "custom-templates/akka-calculator.html",
        "slug": "calculator",
        "label": "Agentic cost calculator",
        "title": "What your AI agents will cost — Akka",
        "description": (
            "Estimate what an agentic AI workload costs to run on AWS, Azure or Google "
            "Cloud for a year, and what the same workload costs on the Akka Agentic AI "
            "Platform."
        ),
        "extra_css": PHYSICAL_CSS,
    },
    "sovereign": {
        "source": CALC / "sovereign.html",
        "out": "akka-sovereign.html",
        "template": "custom-templates/akka-sovereign.html",
        "slug": "sovereign",
        "label": "Sovereign AI cost calculator",
        "title": "What sovereign AI can save you — Akka",
        "description": (
            "Estimate what a year of agentic AI costs against paid model APIs, and what "
            "the same workload costs under multi-model routing, session routing, "
            "self-hosted open-weight models and trained SLMs on the Akka Agentic AI "
            "Platform."
        ),
        "extra_css": "",
    },
}

SHELL = """<!--
    templateType: page
    isAvailableForNewContent: false
    label: {label}
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


def build(spec):
    if not spec["source"].exists():
        sys.exit(f"calculator source not found: {spec['source']}")
    src = spec["source"].read_text(encoding="utf-8")
    fragment = to_hubspot_fragment(src, scope=SCOPE, label=spec["label"].lower())

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
        label=spec["label"], title=spec["title"], description=spec["description"],
        links=links, css=css, port_css=SHARED_CSS + spec["extra_css"], body=body,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / spec["out"]
    out.write_text(page, encoding="utf-8")
    print(spec["slug"], out, len(page), "bytes")
    return out


_TOKEN = []


def token():
    if not _TOKEN:
        env = (ROOT / "scratchpad" / ".hs_env").read_text(encoding="utf-8")
        for line in env.splitlines():
            if line.startswith("HUBSPOT_TOKEN="):
                _TOKEN.append(line.split("=", 1)[1].strip())
        if not _TOKEN:
            sys.exit("HUBSPOT_TOKEN not found in scratchpad/.hs_env")
    return _TOKEN[0]


def _curl(args):
    r = subprocess.run(
        ["curl", "-s", "-H", "Authorization: Bearer " + token()] + args,
        capture_output=True,
    )
    return r.stdout.decode("utf-8", errors="strict") if r.stdout else ""


def _json_call(method, path, body):
    # The JSON goes to a file and curl reads @file. The page titles carry an em dash, and
    # a shell-quoted body holding one arrives mojibaked.
    p = ROOT / "scratchpad" / ".hs_body.json"
    p.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    try:
        return _curl(["-X", method, "-H", "Content-Type: application/json",
                      "--data-binary", "@" + str(p), API + path])
    finally:
        p.unlink()


def put_template(spec, path):
    for env in ("draft", "published"):
        url = f"{API}/cms/v3/source-code/{env}/content/{spec['template']}"
        code = subprocess.run(
            ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-X", "PUT", url,
             "-H", "Authorization: Bearer " + token(), "-F", f"file=@{path}"],
            capture_output=True, text=True,
        ).stdout.strip()
        print("  template", env, code)


def publish_page(spec):
    found = json.loads(_curl([API + "/cms/v3/pages/site-pages?limit=5&slug=" + spec["slug"]]))
    pid = next((p["id"] for p in found.get("results", []) if p["slug"] == spec["slug"]), None)
    body = {
        "name": spec["label"], "slug": spec["slug"], "templatePath": spec["template"],
        "htmlTitle": spec["title"], "metaDescription": spec["description"][:300],
        "state": "PUBLISHED", "publishImmediately": True,
        "language": "en", "subcategory": "site_page",
    }
    if pid:
        r = json.loads(_json_call("PATCH", "/cms/v3/pages/site-pages/" + pid, body))
    else:
        r = json.loads(_json_call("POST", "/cms/v3/pages/site-pages", body))
        pid = r.get("id")
    if not pid:
        sys.exit(f"page publish failed for {spec['slug']}: {str(r)[:300]}")
    _json_call("POST", "/cms/v3/pages/site-pages/%s/draft/push-live" % pid, {})
    print("  page", pid, r.get("url") or "https://akka.io/" + spec["slug"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("page", nargs="*", choices=list(PAGES), default=list(PAGES))
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    for name in (a.page or list(PAGES)):
        spec = PAGES[name]
        p = build(spec)
        if a.push:
            put_template(spec, p)
            publish_page(spec)
