#!/usr/bin/env python3
"""
Regenerate the landing pages:
    index.html             - short summary: presentations + links to the two indexes
    battlecards/index.html - the competitive briefs (sales collateral)
    comparisons/index.html - the public Akka-vs-rival comparison pages

For each deck, the link text comes from its first slide's headline, the summary
descriptor from that slide's subtitle, and the "Last updated" date from the last
git commit that touched the linked file (git log -1 --format=%cs).

Run from the repo root after (re)building content, then commit:
    python build-index.py
"""

import html, os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# One entry per published deck. `link` is the Pages-relative entry point the
# landing page points at (and whose git history sets the "Last updated" date).
PRESENTATIONS = [
    {"dir": "gartner-presentation", "link": "gartner-presentation/generated/akka-gartner-deck.html"},
    {"dir": "sales-presentation",   "link": "sales-presentation/generated/overview/"},
    {"dir": "sales-presentation",   "link": "sales-presentation/generated/specify/",
     "title_src": "sales-presentation/slides/sp-00-title/slide.html"},
    {"dir": "dev-presentation",     "link": "dev-presentation/generated/overview/"},
    {"link": "sales-presentation/generated/token-shredder/",
     "title": "AI that lowers its own bill.", "sub": "AKKA TOKEN SHREDDER"},
    {"link": "case-studies/", "title": "Akka Customer Stories", "sub": "CASE STUDIES"},
    {"link": "website/", "title": "Akka Industry Stories", "sub": "INDUSTRIES"},
]

# Sales-rep battlecards, living in battlecards/ (files are basenames in that folder).
BATTLECARDS = [
    ("battlecard-langchain.html",                "Akka vs. LangChain"),
    ("battlecard-temporal.html",                 "Akka vs. Temporal"),
    ("battlecard-azure-ai-foundry.html",         "Akka vs. Azure AI Foundry"),
    ("battlecard-aws-bedrock.html",              "Akka vs. AWS Bedrock"),
    ("battlecard-google-gemini-enterprise.html", "Akka vs. Google Gemini Enterprise Agent Platform"),
    ("battlecard-nvidia.html",                   "Akka vs. NVIDIA"),
    ("battlecard-databricks.html",               "Akka vs. Databricks"),
    ("battlecard-salesforce-agentforce.html",    "Akka vs. Salesforce Agentforce"),
    ("battlecard-crewai.html",                   "Akka vs. CrewAI"),
    ("battlecard-llamaindex.html",               "Akka vs. LlamaIndex"),
    ("battlecard-n8n.html",                      "Akka vs. n8n"),
    ("battlecard-vercel-ai-sdk.html",            "Akka vs. Vercel AI SDK"),
    ("battlecard-pydantic-ai.html",              "Akka vs. PydanticAI"),
    ("battlecard-orkes.html",                    "Akka vs. Orkes (Conductor)"),
    ("battlecard-service-tiers.html",            "Akka Service Tiers & TCO"),
]

# Public comparison pages, living in comparisons/.
COMPARISONS = [
    ("compare-langchain.html",                "Akka vs. LangChain"),
    ("compare-temporal.html",                 "Akka vs. Temporal"),
    ("compare-azure-ai-foundry.html",         "Akka vs. Azure AI Foundry"),
    ("compare-aws-bedrock.html",              "Akka vs. AWS Bedrock"),
    ("compare-google-gemini-enterprise.html", "Akka vs. Google Gemini Enterprise"),
    ("compare-nvidia.html",                   "Akka vs. NVIDIA"),
    ("compare-databricks.html",               "Akka vs. Databricks"),
    ("compare-salesforce-agentforce.html",    "Akka vs. Salesforce Agentforce"),
    ("compare-crewai.html",                   "Akka vs. CrewAI"),
    ("compare-llamaindex.html",               "Akka vs. LlamaIndex"),
    ("compare-n8n.html",                      "Akka vs. n8n"),
    ("compare-vercel-ai-sdk.html",            "Akka vs. Vercel AI SDK"),
    ("compare-pydantic-ai.html",              "Akka vs. PydanticAI"),
    ("compare-orkes.html",                    "Akka vs. Orkes (Conductor)"),
]

STYLE = """    body {
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
    .back { margin: 0 0 24px; }
    .back a { font-size: 13px; font-weight: 600; }"""


def page(title, body):
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <link rel=\"icon\" href=\"https://akka.io/favicon.ico\" type=\"image/x-icon\">\n"
        "  <title>%s</title>\n  <style>\n%s\n  </style>\n</head>\n<body>\n%s\n</body>\n</html>\n"
        % (html.escape(title), STYLE, body)
    )


def slide_text(path, tag, cls):
    """Decoded, tag-stripped text of <tag ... class="cls" ...>...</tag>."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r'<%s[^>]*class="%s"[^>]*>(.*?)</%s>' % (tag, cls, tag), src, re.S)
    if not m:
        return ""
    inner = re.sub(r"<[^>]+>", "", m.group(1))
    inner = html.unescape(inner).replace("\xa0", " ")
    return re.sub(r"\s+", " ", inner).strip()


def last_commit_date(link):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", link],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or "unpublished"


def last_commit_epoch(link):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", link],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return int(out) if out.isdigit() else 0


def render_item(p):
    if p.get("title"):
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


def render_brief(folder, file, label):
    date = last_commit_date("%s/%s" % (folder, file))
    return (
        "    <li>\n"
        '      <a href="%s">%s</a>\n'
        '      <div class="desc">Last updated %s.</div>\n'
        "    </li>" % (html.escape(file), html.escape(label), html.escape(date))
    )


def build_listing(folder, title, entries):
    """Write folder/index.html listing entries latest-updated first."""
    ordered = sorted(entries, key=lambda e: last_commit_epoch("%s/%s" % (folder, e[0])), reverse=True)
    items = "\n".join(render_brief(folder, f, l) for f, l in ordered)
    body = (
        '  <p class="back"><a href="../">&larr; All presentations</a></p>\n'
        "  <h1>%s</h1>\n  <ul>\n%s\n  </ul>" % (html.escape(title), items)
    )
    with open(os.path.join(ROOT, folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page(title, body))
    return len(ordered)


# --- battlecards/ and comparisons/ index pages ---
n_briefs = build_listing("battlecards", "Battlecards", BATTLECARDS)
n_compare = build_listing("comparisons", "Comparisons", COMPARISONS)

# --- root summary: presentations, then links to the two indexes ---
ordered = sorted(PRESENTATIONS, key=lambda p: last_commit_epoch(p["link"]), reverse=True)
items = "\n".join(render_item(p) for p in ordered)

competitive = '''
  <h1 style="margin-top: 40px;">Competitive content</h1>
  <ul>
    <li>
      <a href="battlecards/">Battlecards</a>
      <div class="kicker">FOR SALES</div>
      <div class="desc">%d competitive briefs, one per rival.</div>
    </li>
    <li>
      <a href="comparisons/">Comparisons</a>
      <div class="kicker">FOR THE WEBSITE</div>
      <div class="desc">%d public Akka-vs-rival pages.</div>
    </li>
  </ul>''' % (n_briefs, n_compare)

root_body = "  <h1>Presentations</h1>\n  <ul>\n%s\n  </ul>%s" % (items, competitive)
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(page("Presentations", root_body))

print("Wrote index.html (%d presentations), battlecards/index.html (%d), comparisons/index.html (%d)."
      % (len(ordered), n_briefs, n_compare))
