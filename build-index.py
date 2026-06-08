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
PRESENTATIONS = [
    {"dir": "gartner-presentation", "link": "gartner-presentation/generated/akka-gartner-deck.html"},
    {"dir": "sales-presentation",   "link": "sales-presentation/generated/overview/"},
    {"dir": "dev-presentation",     "link": "dev-presentation/generated/overview/"},
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


def render_item(p):
    title_html = os.path.join(ROOT, p["dir"], "slides", "00-title", "slide.html")
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


items = "\n".join(render_item(p) for p in PRESENTATIONS)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
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
  <p class="intro">Akka decks, rendered for sharing.</p>
  <ul>
%s
  </ul>
</body>
</html>
""" % items

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(PAGE)

print("Wrote index.html with %d presentation(s):" % len(PRESENTATIONS))
for p in PRESENTATIONS:
    print("  - %s  (%s)" % (p["link"], last_commit_date(p["link"])))
