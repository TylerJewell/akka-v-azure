#!/usr/bin/env python3
"""Render the enablement markdown to two self-contained HTML files.

  html/akka-field-enablement.html              participant edition
  html/akka-field-enablement-facilitator.html  every document, unfiltered

The participant edition carries the content a session discusses. It drops the
answer keys: scenario branches, hidden cast facts, scoring sheets, debriefs, the
routing-drill answers, the assessment design, and the facilitator guide. Scenarios
are reduced to the account brief and the cast, which is what a participant is
handed before a session runs.

Filtering is driven by section headings, so a new facilitator-only section is
excluded by naming it accordingly. Print either file to PDF for distribution.
"""

import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("pip install markdown")

HERE = Path(__file__).parent
OUT = HERE / "html"

CORE = [
    "_program.md",
    "00-foundation.md",
    "01-solution-akka-sdk.md",
    "02-solution-akka-specify.md",
    "03-solution-akka-optimize.md",
    "04-solution-akka-verify.md",
    "05-routing.md",
    "06-mandate-owners.md",
    "07-competitive.md",
    "08-role-tracks.md",
]
FACILITATOR_ONLY_DOCS = ["09-certification.md", "10-facilitator-guide.md", "scenarios/README.md"]
SCENARIOS = [f"scenarios/{name}" for name in (
    "01-wrong-door.md", "02-stalled-pilot.md", "03-token-bill.md", "04-regulator-letter.md",
    "05-integrator-incumbent.md", "06-hyperscaler-mandate.md", "07-sovereign-insurer.md",
    "08-partner-sourced.md", "09-transformation-officer.md", "10-the-year-long-estimate.md")]

# README is the repo maintenance index and belongs in neither edition.
NOT_CONTENT = {"README.md"}

# A section with a matching heading is an answer key or an assessment instrument.
DROP_HEADING = re.compile(
    r"facilitator"
    r"|^scoring$"
    r"|^debrief$"
    r"|^(\d+\.\s*)?certification$"
    r"|^(\d+\.\s*)?the routing drill$",
    re.IGNORECASE,
)
# A scenario participant gets the situation and the people, and nothing that scores them.
SCENARIO_KEEP = {"account brief", "cast"}

TYPOGRAPHY = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 15px; line-height: 1.55; color: #1A1A1A; background: #fff;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
  display: flex; min-height: 100vh;
}
h1 {
  font-size: 27px; font-weight: 700; line-height: 1.2;
  margin: 0 0 18px; padding-bottom: 11px; border-bottom: 3px solid #FFCE4A;
}
h2 {
  font-size: 19px; font-weight: 700; line-height: 1.3;
  border-left: 4px solid #FFCE4A; padding-left: 11px;
  margin: 30px 0 11px; page-break-after: avoid;
}
h3 { font-size: 16px; font-weight: 600; color: #333; margin: 21px 0 7px; page-break-after: avoid; }
h4 { font-size: 15px; font-weight: 600; color: #4E4E4E; margin: 16px 0 5px; }
p { margin-bottom: 11px; }
ul, ol { padding-left: 22px; margin-bottom: 12px; }
li { margin-bottom: 4px; }
strong { font-weight: 600; }
em { font-style: italic; }
code {
  font-family: 'Roboto Mono', ui-monospace, monospace; font-size: 13px;
  background: #F4F4F4; padding: 1px 5px; border-radius: 2px; white-space: nowrap;
}
pre { background: #F4F4F4; padding: 11px 14px; border-radius: 3px; margin-bottom: 13px; overflow-x: auto; }
pre code { background: none; padding: 0; white-space: pre; }
blockquote {
  border-left: 3px solid #DDD; padding: 9px 0 9px 16px; margin: 13px 0;
  color: #4E4E4E; background: #FAFAFA;
}
blockquote p:last-child { margin-bottom: 0; }
.table-wrap { overflow-x: auto; margin: 13px 0 18px; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; page-break-inside: avoid; }
th {
  background: #000; color: #fff; text-align: left; padding: 7px 9px;
  font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.4px;
}
td { padding: 7px 9px; border-bottom: 1px solid #E5E5E5; vertical-align: top; }
tr:nth-child(even) td { background: #FAFAFA; }
hr { border: none; border-top: 1px solid #E0E0E0; margin: 26px 0; }
a { color: #0B7C7D; text-decoration: none; border-bottom: 1px solid #B9DEDE; }
a:hover { border-bottom-color: #0B7C7D; }
code a { border-bottom: 1px dotted #0B7C7D; }
.toc {
  width: 268px; flex: 0 0 268px; background: #0E0E0E; color: #CFCFCF;
  height: 100vh; position: sticky; top: 0; overflow-y: auto; padding: 20px 0 40px;
}
.toc .brand { padding: 0 20px 14px; border-bottom: 1px solid #262626; margin-bottom: 14px; }
.toc .brand .wordmark { display: block; color: #fff; font-size: 20px; font-weight: 700; letter-spacing: 1px; }
.toc .brand .mark { display: block; color: #FFCE4A; font-size: 10px; font-weight: 600;
  letter-spacing: 0.5px; margin-top: 5px; line-height: 1.4; }
.toc .group { padding: 14px 20px 5px; color: #6E6E6E; font-size: 10.5px;
  text-transform: uppercase; letter-spacing: 0.9px; font-weight: 600; }
.toc a {
  display: block; padding: 6px 20px; color: #CFCFCF; font-size: 13.5px;
  border: none; border-left: 3px solid transparent; line-height: 1.35;
}
.toc a:hover { background: #1C1C1C; color: #fff; border-left-color: #FFCE4A; }
main { flex: 1; min-width: 0; padding: 34px 44px 90px; max-width: 1000px; }
section { scroll-margin-top: 18px; }
section + section { margin-top: 54px; padding-top: 40px; border-top: 4px solid #111; }
.top { display: block; margin-top: 30px; font-size: 12.5px; color: #7A7A7A; border: none; }
.top:hover { color: #0B7C7D; }
@media (max-width: 860px) {
  body { display: block; }
  .toc { width: auto; height: auto; position: static; }
  main { padding: 24px 20px 60px; }
}
@media print {
  body { display: block; font-size: 9.5pt; }
  .toc, .top { display: none; }
  main { padding: 0; max-width: none; }
  section + section { page-break-before: always; border-top: none; margin-top: 0; padding-top: 0; }
  h1 { font-size: 17pt; } h2 { font-size: 12pt; } h3 { font-size: 10pt; }
  table { font-size: 8.5pt; } th { font-size: 7.5pt; }
  @page { size: letter; margin: 0.6in 0.65in 0.55in 0.65in; }
}
"""

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Roboto+Mono:wght@400&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body>{nav}<main>{body}</main></body></html>
"""


def anchor(rel: str) -> str:
    """Section id for a source path: scenarios/01-wrong-door.md -> scn-01-wrong-door."""
    if rel == "_program.md":
        return "contents"
    if rel.startswith("scenarios/"):
        stem = rel.split("/", 1)[1][:-3]
        return "scenarios" if stem == "README" else f"scn-{stem}"
    return rel[:-3]


def strip_facilitator(text: str, is_scenario: bool) -> str:
    """Remove sections whose heading marks them as an answer key or an assessment.

    A dropped heading takes every deeper heading with it, so removing a level-2
    section removes its subsections. Scenario preamble sits between the title and
    the first kept heading and names the entry solution, so it goes too.
    """
    out, drop_from, in_preamble, fenced = [], None, False, False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            if drop_from is not None and level > drop_from:
                continue
            drop_from = None
            if level == 1:
                in_preamble = is_scenario
                out.append(line)
                continue
            drop = bool(DROP_HEADING.search(title)) or (
                is_scenario and level == 2 and title.lower() not in SCENARIO_KEEP)
            if drop:
                drop_from = level
                continue
            in_preamble = False
            out.append(line)
            continue
        if drop_from is None and not in_preamble:
            out.append(line)
    return "\n".join(out)


def convert(text: str) -> str:
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
    return html.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>")


def linkify(html: str, targets: dict) -> str:
    """Turn a `filename.md` code span into a link to that document's section.

    Documents reference each other by name inside backticks, and some of those
    names wrap across lines, so whitespace inside the span is normalised first.
    A name with no section in this edition stays plain text.
    """
    def repl(match):
        name = re.sub(r"\s+", "", match.group(1))
        target = targets.get(name.rsplit("/", 1)[-1])
        return f'<code><a href="#{target}">{name}</a></code>' if target else match.group(0)

    return re.sub(r"<code>([A-Za-z0-9_./\-\s]+?\.md)</code>", repl, html)


def build(out_name: str, order: list, groups: list, participant: bool) -> None:
    docs = []
    for rel in order:
        text = (HERE / rel).read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.MULTILINE).group(1).strip()
        if participant:
            text = strip_facilitator(text, rel.startswith("scenarios/"))
        docs.append((rel, title, convert(text)))

    targets = {rel.rsplit("/", 1)[-1]: anchor(rel) for rel, _, _ in docs}
    titles = {rel: title for rel, title, _ in docs}

    mark = ("INTERNAL &mdash; NOT FOR CUSTOMER DISTRIBUTION" if participant
            else "FACILITATOR EDITION &mdash; CONTAINS ANSWER KEYS")
    nav = ['<nav class="toc"><div class="brand"><span class="wordmark">AKKA</span>'
           f'<span class="mark">{mark}</span></div>']
    for label, members in groups:
        nav.append(f'<div class="group">{label}</div>')
        for rel in members:
            nav.append(f'<a href="#{anchor(rel)}">{titles[rel]}</a>')
    nav.append("</nav>")

    body = []
    for rel, _, html in docs:
        body.append(f'<section id="{anchor(rel)}">{linkify(html, targets)}')
        if rel != "_program.md":
            body.append('<a class="top" href="#contents">&uarr; Contents</a>')
        body.append("</section>")

    (OUT / out_name).write_text(
        PAGE.format(title="Akka Field Enablement Program", css=TYPOGRAPHY,
                    nav="".join(nav), body="".join(body)),
        encoding="utf-8")
    print(f"{out_name}  {len(docs)} documents")


def main() -> None:
    OUT.mkdir(exist_ok=True)

    known = set(CORE) | set(FACILITATOR_ONLY_DOCS) | set(SCENARIOS) | NOT_CONTENT
    found = {str(p.relative_to(HERE)).replace("\\", "/")
             for p in list(HERE.glob("*.md")) + list((HERE / "scenarios").glob("*.md"))}
    for extra in sorted(found - known):
        print(f"not listed in build.py, skipped: {extra}")

    build("akka-field-enablement.html",
          CORE + SCENARIOS,
          [("Program", CORE[:1]), ("Core", CORE[1:]), ("Scenarios", SCENARIOS)],
          participant=True)

    full_core = CORE + FACILITATOR_ONLY_DOCS[:2]
    build("akka-field-enablement-facilitator.html",
          full_core + FACILITATOR_ONLY_DOCS[2:] + SCENARIOS,
          [("Program", full_core[:1]), ("Core", full_core[1:]),
           ("Scenarios", FACILITATOR_ONLY_DOCS[2:] + SCENARIOS)],
          participant=False)

    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
