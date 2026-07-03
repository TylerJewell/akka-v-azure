#!/usr/bin/env python3
"""
Regenerate the root index.html landing page that lists every presentation.

For each deck, the link text comes from its first slide's headline, the summary
descriptor from that slide's subtitle, and the "Last updated" date from the last
git commit that touched the linked file (git log -1 --format=%cs).

Run from the repo root after (re)building a deck, then commit index.html:
    python build-index.py

To add a presentation, append an entry to PRESENTATIONS below.
"""

import html, os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# One entry per published deck. `link` is the Pages-relative entry point the
# landing page points at (and whose git history sets the "Last updated" date).
# List order does not matter — the page is rendered latest-updated first.
PRESENTATIONS = [
    {"dir": "gartner-presentation", "link": "gartner-presentation/generated/akka-gartner-deck.html"},
    {"dir": "sales-presentation",   "link": "sales-presentation/generated/overview/"},
    {"dir": "sales-presentation",   "link": "sales-presentation/generated/specify/",
     "title_src": "sales-presentation/slides/sp-00-title/slide.html"},
    {"dir": "dev-presentation",     "link": "dev-presentation/generated/overview/"},
    {"link": "case-studies/", "title": "Akka Customer Stories",
     "sub": "CASE STUDIES", "title_src": None},
]

# Standalone competitive briefs (single HTML files at the repo root).
BATTLECARDS = [
    {"link": "battlecard-langchain.html",                 "label": "Akka vs. LangChain"},
    {"link": "battlecard-temporal.html",                  "label": "Akka vs. Temporal"},
    {"link": "battlecard-azure-ai-foundry.html",          "label": "Akka vs. Azure AI Foundry"},
    {"link": "battlecard-aws-bedrock.html",               "label": "Akka vs. AWS Bedrock"},
    {"link": "battlecard-google-gemini-enterprise.html",  "label": "Akka vs. Google Gemini Enterprise Agent Platform"},
    {"link": "battlecard-nvidia.html",                    "label": "Akka vs. NVIDIA"},
    {"link": "battlecard-databricks.html",                "label": "Akka vs. Databricks"},
    {"link": "battlecard-salesforce-agentforce.html",     "label": "Akka vs. Salesforce Agentforce"},
    {"link": "battlecard-crewai.html",                    "label": "Akka vs. CrewAI"},
    {"link": "battlecard-llamaindex.html",                "label": "Akka vs. LlamaIndex"},
    {"link": "battlecard-n8n.html",                       "label": "Akka vs. n8n"},
    {"link": "battlecard-vercel-ai-sdk.html",             "label": "Akka vs. Vercel AI SDK"},
    {"link": "battlecard-pydantic-ai.html",               "label": "Akka vs. PydanticAI"},
    {"link": "battlecard-orkes.html",                     "label": "Akka vs. Orkes (Conductor)"},
    {"link": "battlecard-service-tiers.html",             "label": "Akka Service Tiers & TCO"},
]


def slide_text(path, tag, cls):
    """Decoded, tag-stripped text of <tag ... class="cls" ...>...</tag>."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r'<%s[^>]*class="%s"[^>]*>(.*?)</%s>' % (tag, cls, tag), src, re.S)
    if not m:
        return ""
    inner = re.sub(r"<[^>]+>", "", m.group(1))         # drop nested tags (e.g. <span class="accent">)
    inner = html.unescape(inner).replace("\xa0", " ")  # &nbsp; -> space, &middot; -> -, etc.
    return re.sub(r"\s+", " ", inner).strip()


def last_commit_date(link):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", link],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or "unpublished"


def last_commit_epoch(link):
    """Unix timestamp of the last commit touching `link` (0 if uncommitted).
    Used to order decks latest-first — finer than the displayed YYYY-MM-DD date."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", link],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return int(out) if out.isdigit() else 0


def render_item(p):
    if p.get("title"):                                 # explicit title/sub (no title slide to read)
        title, sub = p["title"], p.get("sub", "")
    else:
        title_html = os.path.join(ROOT, p["title_src"]) if p.get("title_src") \
            else os.path.join(ROOT, p["dir"], "slides", "00-title", "slide.html")
        title = slide_text(title_html, "h1", "title-headline")
        sub = slide_text(title_html, "div", "title-sub")
    date = last_commit_date(p["link"])
    kicker = '\n      <div class="kicker">%s</div>' % html.escape(sub) if sub else ""
    return (
        "    <li>\n"
        '      <a href="%s">%s</a>%s\n'
        '      <div class="desc">Last updated %s.</div>\n'
        "    </li>" % (html.escape(p["link"]), html.escape(title), kicker, html.escape(date))
    )


def render_brief(b):
    date = last_commit_date(b["link"])
    return (
        "    <li>\n"
        '      <a href="%s">%s</a>\n'
        '      <div class="desc">Last updated %s.</div>\n'
        "    </li>" % (html.escape(b["link"]), html.escape(b["label"]), html.escape(date))
    )


# Order decks latest-updated first (by last commit on the linked file).
ordered = sorted(PRESENTATIONS, key=lambda p: last_commit_epoch(p["link"]), reverse=True)
items = "\n".join(render_item(p) for p in ordered)

ordered_briefs = sorted(BATTLECARDS, key=lambda b: last_commit_epoch(b["link"]), reverse=True)
briefs = "\n".join(render_brief(b) for b in ordered_briefs)
briefs_section = ('''
  <h1 style="margin-top: 40px;">Competitive briefs</h1>
  <ul>
%s
  </ul>''' % briefs) if BATTLECARDS else ""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
  <title>Presentations</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      max-width: 640px; margin: 0 auto; padding: 48px 24px;
      color: #1a1a1a; line-height: 1.5;
    }
    h1 { font-size: 24px; margin: 0 0 4px; }
    p.intro { color: #666; margin: 0 0 32px; }
    ul { list-style: none; padding: 0; margin: 0; }
    li { padding: 16px 0; border-top: 1px solid #e5e5e5; }
    a { color: #0b66c3; text-decoration: none; font-weight: 600; }
    a:hover { text-decoration: underline; }
    .kicker { color: #999; font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-top: 4px; }
    .desc { color: #666; font-size: 14px; margin-top: 2px; }
  </style>
</head>
<body>
  <h1>Presentations</h1>
  <ul>
%s
  </ul>%s
</body>
</html>
""" % (items, briefs_section)

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(PAGE)

print("Wrote index.html with %d presentation(s), latest first:" % len(ordered))
for p in ordered:
    print("  - %s  (%s)" % (p["link"], last_commit_date(p["link"])))
