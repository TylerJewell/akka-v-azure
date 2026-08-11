#!/usr/bin/env python3
"""Voice auditor for the technical blog template.

Scans blog HTML files for house-voice violations using the pattern bank
in `.claude/skills/house-voice/SKILL.md`. Emits a report per file with
line numbers, matched text, and rule name. Exit code 1 on any hit.

Usage:
    python tools/auditors/blog-technical/voice-audit.py blog-technical/*.html
    python tools/auditors/blog-technical/voice-audit.py --only-headings blog-technical/*.html
    python tools/auditors/blog-technical/voice-audit.py --format json blog-technical/*.html

Meant as:
  - a pre-publish gate that blocks prose violations from shipping
  - a periodic sweep against live blog posts to catch regressions
  - the source of truth for the scaffolder's own inline flag pass

Patterns are grouped by rule name; the same text may hit multiple rules.
The auditor does not rewrite — that's an editorial decision.
"""

import argparse
import json
import re
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ── Pattern bank ────────────────────────────────────────────────
# Grouped by heuristic scope: PROSE runs against all prose (paragraphs,
# captions, callouts). HEADING runs only against h1–h4 text.

PROSE_PATTERNS = [
    # Antithesis and softened forms
    (r"\bisn['’]t\b[^.]{0,60}?\b(it['’]s|it is|but|—)\b", 'antithesis (isn\'t X, it\'s Y)'),
    (r"\baren['’]t\b[^.]{0,60}?\b(they['’]re|they are|but|—)\b", 'antithesis (aren\'t X, they\'re Y)'),
    (r"\bis not\b[^.]{0,60}?\bit is\b", 'antithesis (is not X, it is Y)'),
    (r"\bnot only\b[^.]{0,40}?\bbut also\b", 'not-only-but-also'),
    (r"\b[A-Z][a-z]+ (does|is|runs|works)\b[^.]{0,80}?\.\s+[A-Z][a-z]+\s+(don['’]t|doesn['’]t|isn['’]t|aren['’]t)\b", 'parallel-negation antithesis'),

    # Enumerate-then-collapse / counting collapse
    (r"\bthe same (one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+", 'the-same-N pattern'),
    (r"\b(all|both|every)\s+(two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+\s+in one\b", 'enumerate-then-collapse'),
    (r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+,\s+(one|two|three|four|five)\s+\w+\b", 'N X, N Y collapse'),

    # Hype verbs and AI-tells
    (r"\b(unlock|supercharge|leverage|harness|empower|revolutionize|seamless|game-changer|delve)\b", 'hype verb'),
    (r"\b(at its core|make no mistake|testament to|at the end of the day|worth noting|this is where)\b", 'AI-tell phrase'),
    (r"\b(throughline|tapestry|journey)\b", 'AI-metaphor noun'),

    # Colour and emotion adjectives — negative lookbehind on '-' skips
    # legitimate compound words ("business-critical", "mission-critical").
    (r"(?<!-)\b(shiny|elegant|beautiful|powerful|robust|modern|critical|vital|essential|amazing|incredible|remarkable)\b(?!-)", 'colour/emotion adjective'),

    # Adjective-for-number substitutions
    (r"\b(massive|blazing[- ]fast|comprehensive|sharpest|strongest|fastest|largest)\b", 'adjective-for-number'),

    # Framework-lecture / second-person imperatives
    (r"\b(Take a hard look|Ask yourself|Before you start|Let['’]s face it)\b", 'framework-lecture opener'),

    # Metaphors standing in for plain words
    (r"\b(load-bearing|the spine|the wedge|north star|flywheel|substrate)\b", 'metaphor for plain word'),

    # Rhetorical devices
    (r"\bThis is the real story:", 'colon-drama'),
]

HEADING_PATTERNS = [
    (r"^[^—]{5,80}—[^—]{5,80}[.?]?$", 'em-dash-punchline heading'),
    (r"^(What|Why|How|When|Where|Which|Who)\b[^?]{0,80}[.?]\s*$", 'rhetorical question heading'),
    (r"^(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)\s+\w+\.\s*$", 'pithy numeric opener'),
]

CAPTION_PATTERNS = HEADING_PATTERNS  # figure/table captions get the same heading-level check


def _extract_text_blocks(html, source_path=''):
    """Yield (line, tag, text) tuples for every prose or heading element."""
    # Word boundary after tag name so <li> doesn't match <link>, <p> doesn't match <path>, etc.
    for m in re.finditer(
        r'<(p|h[1-4]|figcaption|blockquote|li|dd)(?:\s[^>]*)?>(.*?)</\1>',
        html, re.S,
    ):
        tag = m.group(1).lower()
        raw = m.group(2)
        # Strip inline tags but keep text
        text = re.sub(r'<[^>]+>', '', raw)
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or len(text) < 4:
            continue
        line = html[:m.start()].count('\n') + 1
        yield line, tag, text
    # Also caption elements inside tables + figure figcaption is already caught above
    for m in re.finditer(r'<caption[^>]*>(.*?)</caption>', html, re.S):
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
        if not text or len(text) < 4:
            continue
        line = html[:m.start()].count('\n') + 1
        yield line, 'caption', text


# Wording that matches a pattern above and is a verifiable factual claim.
# Kept in step with the EXEMPT block in tools/auditors/voice/audit.py: the two
# banks are separate copies, and an exemption added to one and not the other
# makes the same sentence pass one auditor and fail the other.
#   "an evaluation harness" is a category of software; "harness the model" is
#   the hype verb the rule is aimed at.
EXEMPT = re.compile(
    r"\bmission[- ]critical\b"
    r"|\b(?:third-party|agent|evaluation|test|coding|AI)\s+harness"
    r"|harness(?:es)?\s+(?:such as|like|that|the customer)"
    r"|\b(?:model|gives|more|market)\s+leverage\b")


def _exempt(text, match):
    """True when the flagged wording sits inside a verifiable factual claim.

    Scoped to the span around the match so one exempt phrase in a paragraph
    does not clear an unrelated hit later in the same block.
    """
    lo, hi = max(0, match.start() - 30), min(len(text), match.end() + 30)
    return bool(EXEMPT.search(text[lo:hi]))


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    hits = []
    for line, tag, text in _extract_text_blocks(html):
        # Heading vs body pattern selection
        is_heading = tag in ('h1', 'h2', 'h3', 'h4')
        is_caption = tag in ('figcaption', 'caption')
        patterns = list(PROSE_PATTERNS)
        if is_heading or is_caption:
            patterns = HEADING_PATTERNS + PROSE_PATTERNS
        for pat, rule in patterns:
            for m in re.finditer(pat, text, re.I | re.MULTILINE):
                if _exempt(text, m):
                    continue
                hits.append({
                    'line': line,
                    'tag': tag,
                    'rule': rule,
                    'match': m.group(0)[:120],
                    'context': text[:160],
                })
                break  # one hit per rule per element is enough
    return hits


def format_report(path, hits, only_headings=False):
    lines = [f'\n=== {path} ===']
    if not hits:
        lines.append('  ok — no voice violations')
        return '\n'.join(lines)
    filtered = [h for h in hits if not only_headings or h['tag'] in ('h1', 'h2', 'h3', 'h4', 'figcaption', 'caption')]
    if not filtered:
        lines.append('  ok — no heading/caption violations')
        return '\n'.join(lines)
    by_rule = {}
    for h in filtered:
        by_rule.setdefault(h['rule'], []).append(h)
    lines.append(f'  {len(filtered)} violation(s) across {len(by_rule)} rule(s)')
    for rule in sorted(by_rule):
        lines.append(f'\n  [{rule}]')
        for h in by_rule[rule]:
            lines.append(f'    line {h["line"]} <{h["tag"]}>  “{h["match"]}”')
            if len(h['context']) > len(h['match']) + 5:
                lines.append(f'      in: {h["context"]}')
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='+')
    p.add_argument('--only-headings', action='store_true',
                   help='report only heading/caption violations (skip body prose)')
    p.add_argument('--format', choices=('text', 'json'), default='text')
    args = p.parse_args()

    all_results = {}
    total = 0
    for path in args.files:
        hits = audit_file(path)
        all_results[path] = hits
        total += len(hits)

    if args.format == 'json':
        print(json.dumps(all_results, indent=2))
    else:
        for path, hits in all_results.items():
            print(format_report(path, hits, only_headings=args.only_headings))
        print(f'\nTotal: {total} violation(s) across {len(args.files)} file(s)')

    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
