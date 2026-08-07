#!/usr/bin/env python3
"""House-voice auditor for every prose artifact in the repo.

Scans HTML and Markdown for the constructions banned in
`.claude/skills/house-voice/SKILL.md`. Reports file, line, rule and matched
text. Exit code 1 on any hit at or above the failure threshold.

    python tools/auditors/voice/audit.py website/*.html
    python tools/auditors/voice/audit.py --context guide website/guides*.html
    python tools/auditors/voice/audit.py --context deck akka-overview/index.html
    python tools/auditors/voice/audit.py --format json --only-headings case-studies/*.html
    python tools/auditors/voice/audit.py --check-drift

Context matters. A question is the correct form for an FAQ heading and the
wrong form for a section heading, so rules carry the contexts they apply to
and `--context` selects them. Running without a context applies every rule,
which is right for a first pass and noisy for a page type that legitimately
uses one of the shapes.

What this cannot do: hear diction. "An unwritten convention holds inside the
team" and "a typical system lands on 30 to 60 controls" are caught here only
because those exact verbs are listed. A construction nobody has met yet passes.
Read the prose aloud; this is a backstop.
"""

import argparse
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ALL = ('web', 'guide', 'faq', 'blog', 'deck', 'case-study', 'battlecard', 'internal')
# Sales enablement, playbooks, and battlecard notes. Trade terms are precise
# there and vague in customer copy, so a few rules are scoped away from it.
CUSTOMER_FACING = tuple(c for c in ALL if c != 'internal')

# ── Rule bank ───────────────────────────────────────────────────
# (pattern, rule name, scope, contexts)
#   scope    : 'prose' | 'heading' | 'both'
#   contexts : tuple of contexts the rule applies to, or ALL

RULES = [
 # ── Antithesis ────────────────────────────────────────────────
 (r"\bisn['’]t\b[^.]{0,60}?\b(it['’]s|it is|but|—)\b", "antithesis (isn't X, it's Y)", 'both', ALL),
 (r"\baren['’]t\b[^.]{0,60}?\b(they['’]re|they are|but|—)\b", "antithesis (aren't X, they're Y)", 'both', ALL),
 (r"\bis not\b[^.]{0,60}?\bit is\b", 'antithesis (is not X, it is Y)', 'both', ALL),
 (r"\bnot only\b[^.]{0,40}?\bbut also\b", 'not-only-but-also', 'both', ALL),
 (r"[^.]{0,60}(, not | and not |, rather than | but rather |not just )[^.]{0,60}", 'antithesis (X, not Y)', 'both', ALL),
 # The comma-less form reads the same and slipped past the rule above.
 (r"[^.]{0,60}\brather than\b[^.]{0,60}", 'antithesis (X rather than Y)', 'both', ALL),
 (r"\b[A-Z][a-z]+ (does|is|runs|works)\b[^.]{0,80}?\.\s+[A-Z][a-z]+\s+(don['’]t|doesn['’]t|isn['’]t|aren['’]t)\b", 'parallel-negation antithesis', 'prose', ALL),

 # ── Counting ──────────────────────────────────────────────────
 (r"\bthe same (one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+", 'the-same-N pattern', 'both', ALL),
 (r"\b(all|both|every)\s+(two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+\s+in one\b", 'enumerate-then-collapse', 'both', ALL),
 (r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+,\s+(one|two|three|four|five)\s+\w+\b", 'N X, N Y collapse', 'both', ALL),
 (r"\ball (two|three|four|five|six|seven|eight|nine|ten)\s+\w+", 'count-then-collapse', 'both', ALL),
 (r"^(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)\b", 'count as label', 'heading', ALL),
 # A count with no noun after it is the named things replaced by their number.
 # "the mechanism behind all four" makes the reader carry the list themselves.
 # Split by scope: a heading ends where the count ends, and a wrapped prose line
 # ends anywhere, so end-of-line counts as a boundary only in a heading.
 (r"\b(all|both|these|those|the)\s+(two|three|four|five|six|seven|eight|nine|ten)\b(?=\s*[.,;:)\]—-]|\s*$)",
  'bare count standing for the named things', 'heading', ALL),
 (r"\b(all|both|these|those|the)\s+(two|three|four|five|six|seven|eight|nine|ten)\b(?=\s*[.,;:)\]—-])",
  'bare count standing for the named things', 'prose', ALL),
 # A count before an abstraction replaces a name. A count before a unit is a
 # measurement, and measurements are required, so the noun decides.
 (r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(input|inputs|thing|things|step|steps|way|ways|reason|reasons|factor|factors|element|elements|point|points|mode|modes|path|paths|pillar|pillars|dimension|dimensions|option|options|stage|stages|layer|layers|outcome|outcomes|position|positions|choice|choices|category|categories|kind|kinds|type|types|aspect|aspects|area|areas|approach|approaches|consideration|considerations|consequence|consequences|advantage|advantages|benefit|benefits|difference|differences|property|properties|principle|principles|rule|rules|mistake|mistakes|failure|failures|trigger|triggers|signal|signals|theme|themes|lesson|lessons|move|moves|band|bands|claim|claims|measure|measures|criterion|criteria|shape|shapes|quality|qualities|virtue|virtues|takeaway|takeaways)\b", 'counting abstractions', 'both', ALL),

 # ── Hype and AI-tells ─────────────────────────────────────────
 (r"\b(unlock|supercharge|leverage|harness|empower|revolutionize|seamless|game-changer|delve)\b", 'hype verb', 'both', ALL),
 (r"\b(at its core|make no mistake|testament to|at the end of the day|worth noting|this is where)\b", 'AI-tell phrase', 'both', ALL),
 (r"\b(throughline|tapestry|journey)\b", 'AI-metaphor noun', 'both', ALL),
 (r"(?<!-)\b(shiny|elegant|beautiful|powerful|robust|modern|critical|vital|essential|amazing|incredible|remarkable)\b(?!-)", 'colour/emotion adjective', 'both', ALL),
 (r"\b(massive|blazing[- ]fast|comprehensive|sharpest|strongest|fastest|largest)\b", 'adjective-for-number', 'both', ALL),
 (r"\b(load-bearing|the spine|north star|flywheel|substrate)\b", 'metaphor for plain word', 'both', ALL),
 # "the wedge" names a known sales motion internally and is a metaphor to a customer.
 (r"\bthe wedge\b", 'metaphor for plain word', 'both', CUSTOMER_FACING),
 # "Bar" names a physical object and is used for a number.
 (r"\b(quality bar|the bar\b|a bar\b|bar that|bar for|raise[sd]? the bar|meets? the bar|"
  r"above the bar|below the bar|sets? the bar|clears? the bar|passes? the bar|holds? at the bar)",
  "'bar' meaning a standard or level", 'both', ALL),

 # ── Reader framing ────────────────────────────────────────────
 (r"\b(Take a hard look|Ask yourself|Before you start|Let['’]s face it)\b", 'framework-lecture opener', 'both', ALL),
 (r"\b(the reason (you|the question)|why you asked|if you['’]re wondering|you have already hit)\b", 'telling the reader about themselves', 'prose', ALL),
 # A buyer's motive is not a fact we hold. State what the system does.
 (r"\b(the reason|why)\s+(enterprises|customers|companies|buyers|teams|organi[sz]ations|people|they)\s+"
  r"(choose|chooses|buy|buys|pick|picks|select|selects|prefer|prefers|come|came|switch)\b",
  'unfalsifiable claim about a buyer motive', 'both', ALL),

 # ── Hedging ───────────────────────────────────────────────────
 (r"\b(usually|generally|typically|mostly|often enough|broadly speaking|somewhat|fairly|arguably)\b", 'hedge', 'both', ALL),
 # An adverb that softens a claim before anyone has challenged it. "cannot
 # easily match" concedes the claim in the act of making it: either the thing
 # can be matched or it cannot, and the adverb is there to avoid saying which.
 (r"\b(easily|simply|merely|largely|relatively|essentially|virtually|practically|"
  r"in most cases|for the most part|more or less|to some extent|tends? to)\b", 'hedge adverb', 'both', ALL),

 # ── Diction that fails read-aloud ─────────────────────────────
 (r"\bholds? (inside|while|as|true|good)\b", "literary 'hold' for 'remain true'", 'both', ALL),
 (r"\b(lands? on|sits? (outside|inside|above|below)|walks? through|leans? on|rides? on|travels? (back|upstream|forward)|moves? the answer|absorb (them|it|changes))\b", 'verb stretched past its meaning', 'both', ALL),
 (r"\bWhat (differs|matters|changes|follows|counts) is\b", 'cleft opener', 'both', ALL),
 (r"\b(each|both|either) [a-z]+ (help|have|carry|work|move|add|apply|decide)\b", 'broken correlative / agreement', 'both', ALL),

 # ── Structure ─────────────────────────────────────────────────
 # The em-dash heading is checked structurally below, because a label before the
 # dash ("Meeting 1 — Dana Whitfield, CISO") is a title and not a payoff.
 (r"^(What|Why|How|When|Where|Which|Who)\b[^?]{0,80}[.?]\s*$", 'rhetorical question heading', 'heading',
  ('web', 'blog', 'deck', 'case-study', 'battlecard')),
 (r"\bThis is the real story:", 'colon-drama', 'both', ALL),
]

# Sentences that cannot be read on their own. Checked structurally rather than
# by pattern, because the failure is the missing subject.
#   "It runs inside the repositories" opens on a pronoun with no antecedent.
#   "This table is the spine" opens on a determiner and a noun, and reads alone.
# "It" and "They" are always pronouns. The rest are determiners too, so they
# only fail when a verb follows and the word is carrying the subject by itself.
BARE_PRONOUN = re.compile(r"^(It|They)\s+[a-z]")
BARE_DEMONSTRATIVE = re.compile(
    r"^(That|This|These|Those|Both|Either|Neither|Such)\s+"
    r"(is|are|was|were|has|have|had|means?|makes?|gives?|leaves?|comes?|goes|"
    r"runs?|works?|happens?|follows?|applies|apply|matters?|counts?|comes|comes)\b")


def bare_subject(sent):
    return bool(BARE_PRONOUN.match(sent) or BARE_DEMONSTRATIVE.match(sent))

# Wording that reads as a banned construction and is a verifiable fact.
# A superlative about a named entity is a claim with a source behind it, not an
# adjective doing a number's job: the LHC is the world's largest machine.
# "mission-critical" is a category of system, not a colour word.
EXEMPT = re.compile(
    r"\bmission[- ]critical\b"
    # A possessive proper noun before a superlative is a sourced market claim:
    # "Canada's largest virtual communities", "the world's largest machine".
    r"|\b(?:[A-Z][\w.&-]*|world|group|company)(?:'s|&rsquo;s|&#x27;s)\s+larges"
    r"|largest\s+(?:shareholder|factory\s+networks?|machine|independent)"
    r"|one of the largest\b"
    # A counted superlative selects a set by measurement: "the two largest
    # distribution centres" names which two, and the count is the criterion.
    r"|\b(?:the\s+)?(?:two|three|four|five|six|\d+)\s+larges"
    # A score in a rubric. "two points" is a unit, and units are measurements.
    r"|\b(?:zero|one|two|three|four|five|\d+)\s+points?\b"
    # "harness" and "leverage" are hype as verbs and ordinary nouns here: an
    # agent harness is a piece of software, and model leverage is a named
    # property of Akka Optimize.
    r"|\b(?:third-party|agent|evaluation|test|coding|AI)\s+harness"
    r"|harness(?:es)?\s+(?:such as|like|that|the customer)"
    r"|\b(?:model|gives|more|market)\s+leverage\b")
FRAGMENT_ANSWER = re.compile(r"^(Partly|Rarely|Yes|No|Maybe|Sometimes|Memory|Both|Neither|Correct)\.?$", re.I)

# Independent clauses chained with commas into one sentence.
CLAUSE_VERB = re.compile(
    r"\b(is|are|was|were|has|have|had|does|do|did|can|will|would|should|must|"
    r"runs?|takes?|makes?|gets?|holds?|keeps?|stays?|adds?|produces?|becomes?|needs?|costs?|"
    r"carries|carry|falls?|decides?|drives?|shares?|sets?|shows?|reaches?|covers?|compiles?|"
    r"contributes?|writes?|reads?|moves?|stops?|starts?|leaves?|arrives?|depends?|means?|"
    r"operates?|detects?|recovers?|bills?|trains?|learns?|teaches?|builds?|gives?|inherits?|"
    r"provides?|supplies|supply|prices?|names?|answers?|judges?|solves?|propagates?)\b", re.I)


SUBORDINATOR = re.compile(r"^\s*(what|when|which|that|how|who|where|while|because|if|although|after|before|since|unless|and how|and what|and where|to)\b", re.I)
OPENING_SUB = re.compile(r"^\s*(when|while|because|if|although|after|before|since|unless)\b", re.I)


# A noun phrase closed with a period. It reads as a sentence and has no verb of
# its own, so the reader has to supply one.
#
# One shape only. Deciding in general whether a sentence has a main verb needs a
# parser: a wh-opener is a fragment in "What survives a restart." and a complete
# sentence in "Where progress is stored decides what survives.", and nothing
# short of parsing separates them. The bounded case below does not need the
# verb identified, so it is the one that is enforced.
NP_RELATIVE = re.compile(r"^([A-Z][\w'’-]*(?:\s+[\w'’-]+){0,2})\s+(that|which|who)\s+(\S+)")

# "that" is a relative pronoun before a verb and a determiner before a noun.
# "Akka replaces that stack with shared compute." is a sentence; the same
# pattern with a verb after "that" is a noun phrase.
VERB_AFTER_REL = re.compile(
    r"^(?:[a-z]+(?:s|ed|ing)|come|go|run|make|take|hold|keep|need|cost|arrive|happen|"
    r"fail|pass|stop|move|read|write|have|has|had|is|are|was|were|can|will|must|do|did)\b")


def is_fragment(sent):
    """A noun phrase with a period on it, modified only by a relative clause.

    Bounded at eight words. Past that the tail is long enough to be carrying a
    main verb, which made "A task that restarts from the beginning pays for its
    completed steps twice." read as a fragment.
    """
    if sent.endswith('?') or not 4 <= len(sent.split()) <= 8:
        return False
    m = NP_RELATIVE.match(sent)
    return bool(m and not CLAUSE_VERB.search(m.group(1))
                and VERB_AFTER_REL.match(m.group(3)))


LEADING_CONJ = re.compile(r"^\s*(and|but|or|then|so)\s+", re.I)


def _independent(part):
    """A clause with a subject of its own.

    "calls a model" opens on its verb, so it shares the previous subject and is
    one predicate in a compound, not a clause in a chain.
    """
    rest = LEADING_CONJ.sub('', part).strip()
    if SUBORDINATOR.match(rest):        # "which supplies the runtime" modifies, it does not chain
        return False
    return bool(CLAUSE_VERB.search(rest)) and not CLAUSE_VERB.match(rest)


def is_comma_splice(sent):
    """Three or more independent clauses joined by commas.

    A colon introduces a list, and a series of subordinate wh-clauses is a
    single predicate rather than a chain, so neither counts.
    """
    if len(sent) <= 60 or ':' in sent:
        return False
    parts = sent.split(', ')
    if len([c for c in parts if _independent(c)]) < 3:
        return False
    if OPENING_SUB.match(sent):
        return False
    return len([c for c in parts if SUBORDINATOR.match(c)]) < 2


# Each Q&A item, matched individually so a class list like "qa rv" still counts.
FAQ_BLOCK = re.compile(r'<div class="[^"]*\b(?:q|qa|faq)\b[^"]*"[^>]*>.*?</div>', re.S)


def _in_faq(text, pos):
    return any(m.start() <= pos <= m.end() for m in FAQ_BLOCK.finditer(text))


def blocks(text, path):
    """Yield (line, kind, sentence-bearing text) for prose-bearing elements."""
    if path.lower().endswith(('.md', '.markdown')):
        for i, raw in enumerate(text.split('\n'), 1):
            s = raw.strip()
            if not s or s.startswith(('|', '```', '<!--', '    ')):
                continue
            if s.startswith('#'):
                yield i, 'heading', s.lstrip('# ').strip()
            elif len(s) > 3:
                yield i, 'prose', re.sub(r'[*_`\[\]]', '', s)
        return
    for m in re.finditer(r'<(p|h[1-4]|figcaption|blockquote|li|dd|caption)(?:\s[^>]*)?>(.*?)</\1>', text, re.S):
        tag = m.group(1).lower()
        s = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(2))).strip()
        if len(s) < 4:
            continue
        if tag.startswith('h') or tag in ('figcaption', 'caption'):
            # A question is the correct form for an FAQ heading, so classify by
            # position instead of relying on the caller to pass the right context.
            kind = 'faq-heading' if _in_faq(text, m.start()) else 'heading'
        else:
            kind = 'prose'
        # A customer said this. It is evidence, not copy, and rewriting it
        # would misquote them.
        if kind == 'prose' and re.match(r'^\s*(?:"|&ldquo;|&quot;|“)', s):
            kind = 'quote'
        yield text[:m.start()].count('\n') + 1, kind, s
    # Text inside a diagram is copy like any other, and it is where counts and
    # summary sentences hide from a rule bank that only reads HTML elements.
    for m in re.finditer(r'<text\b[^>]*>(.*?)</text>', text, re.S):
        s = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
        if len(s) >= 12:
            yield text[:m.start()].count('\n') + 1, 'diagram', s
    # Divs the guide and efficiency templates use for captions, answers and cells.
    for cls, kind in (('fig-note', 'heading'), ('area-blurb', 'prose'),
                      ('answer', 'prose'), ('sources', 'prose')):
        for m in re.finditer(r'<div class="%s"[^>]*>(.*?)</div>' % cls, text, re.S):
            s = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
            if len(s) >= 4:
                yield text[:m.start()].count('\n') + 1, kind, s


def sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+', s) if x.strip()]


EM_DASH_SPLIT = re.compile(r"\s+[—–]\s+|\s+&mdash;\s+")
PAYOFF_OPENER = re.compile(r"^(and|but|so|or|yet|then|where|what|why|how|when|which|who)\b", re.I)


def em_dash_punchline(heading):
    """An em-dash heading that withholds and then pays off.

    "Where an agent runs matters — and it changes." sets up a reveal. "Akka SDK
    — removes infrastructure cost" and "Meeting 1 — Dana Whitfield, CISO" use
    the dash the way a colon is used, which is a title. The reveal shows up as a
    conjunction or a wh-word after the dash, or as a full clause on both sides.
    """
    parts = EM_DASH_SPLIT.split(heading)
    if len(parts) != 2:
        return None
    left, right = (p.strip() for p in parts)
    if not (left and right):
        return None
    if PAYOFF_OPENER.match(right):
        return '%s — %s' % (left, right)
    if CLAUSE_VERB.search(left) and CLAUSE_VERB.search(right):
        return '%s — %s' % (left, right)
    return None


def paragraphs(text, path):
    """Yield (line, paragraph) with wrapped source lines joined.

    Antithesis built out of parallel framing spans sentences, and the line-based
    scan in `blocks` sees each wrapped line on its own, so it cannot see the
    shape at all.
    """
    if path.lower().endswith(('.md', '.markdown')):
        buf, start = [], 0
        for i, raw in enumerate(text.split('\n'), 1):
            s = raw.strip()
            item = re.match(r'^(?:[-*]|\d+\.)\s+(.*)$', s)
            # A list item is its own unit. Its wrapped continuation lines are
            # indented, so they fall through and join the buffer it opened.
            if item:
                if buf:
                    yield start, ' '.join(buf)
                buf, start = [re.sub(r'[*_`\[\]]', '', item.group(1))], i
                continue
            if not s or s.startswith(('|', '```', '#', '<!--', '>')):
                if buf:
                    yield start, ' '.join(buf)
                    buf = []
                continue
            if not buf:
                start = i
            buf.append(re.sub(r'[*_`\[\]]', '', s))
        if buf:
            yield start, ' '.join(buf)
        return
    for m in re.finditer(r'<p(?:\s[^>]*)?>(.*?)</p>', text, re.S):
        s = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
        if len(s) > 3:
            yield text[:m.start()].count('\n') + 1, s


# "On a hyperscaler, …" against "On Akka, …". The framing preposition plus a
# named subject sets up a comparison the next unit completes.
FRAME_OPENER = re.compile(r"^(On|With|Without|Under|Inside|For)\s+([^,]{2,45}),\s+\S")


def parallel_frames(units):
    """Two prose units framed identically with different subjects.

    The contrast carries the claim, which is antithesis whether or not either
    half is negated, so the parallel-negation rule in the bank does not see it.
    Bounded to adjacent units, because two identical openers pages apart are
    coincidence rather than a construction.
    """
    hits, prev = [], None
    for index, (line, para) in enumerate(units):
        for sent in sentences(para):
            m = FRAME_OPENER.match(sent)
            if not m:
                continue
            prep, subject = m.group(1).lower(), m.group(2).strip().lower()
            if prev and prev[0] == prep and prev[1] != subject and index - prev[2] <= 1:
                hits.append((line, '%s %s, … %s %s,'
                             % (m.group(1), prev[1], m.group(1), m.group(2))))
            prev = (prep, subject, index)
    return hits


LEDE_BLOCK = re.compile(r'<p class="[^"]*\blede\b[^"]*"[^>]*>(.*?)</p>', re.S)
LEDE_SUBJECT = re.compile(
    r"^(?:Each|Every|The|A|An|This|These|Our|Akka(?:'s)?)\s+([a-z][\w-]*)", re.I)
COPULA = re.compile(r"\b(is|are|was|were|means?|describes?|covers?|contains?)\b", re.I)


def lede_defines_subject(text):
    """The first sentence of a lede names a thing the reader has not met.

    A lede earns its noun by defining it ("Each guide is a short answer to …")
    or by reusing one the headline already established. Only the page's own
    subject is checked; whether a sentence sounds like speech is not something
    a pattern can decide, so that half of the rule stays with the writer.
    """
    m = LEDE_BLOCK.search(text)
    if not m:
        return None
    lede = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
    first = sentences(lede)[0] if sentences(lede) else ''
    subj = LEDE_SUBJECT.match(first)
    if not subj or COPULA.search(first):
        return None
    noun = subj.group(1).rstrip('s')
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S)
    head = re.sub(r'<[^>]+>', '', h1.group(1)).lower() if h1 else ''
    if noun in head:
        return None
    return text[:m.start()].count('\n') + 1, noun, first[:110]


def _exempt(sentence, match):
    """True when the flagged wording sits inside a verifiable factual claim.

    Scoped to the span around the match rather than the whole block, so one
    exempt phrase in a paragraph does not clear an unrelated hit later in it.
    """
    lo, hi = max(0, match.start() - 30), min(len(sentence), match.end() + 30)
    return bool(EXEMPT.search(sentence[lo:hi]))


def structural(line, kind, s):
    """Checks that need a whole sentence: fragments, bare subjects, splices."""
    out = []
    for sent in sentences(s):
        if FRAGMENT_ANSWER.match(sent):
            rule, match = 'fragment answer', sent
        elif is_fragment(sent):
            rule, match = 'phrase written as a sentence', sent[:110]
        elif bare_subject(sent):
            rule, match = 'sentence cannot stand alone', sent[:110]
        elif is_comma_splice(sent):
            rule, match = 'comma-spliced clause chain', sent[:110]
        else:
            continue
        out.append({'line': line, 'kind': kind, 'rule': rule,
                    'match': match, 'context': s[:170]})
    return out


def audit_file(path, context=None, standalone_zones=('answer', 'faq')):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    is_md = path.lower().endswith(('.md', '.markdown'))
    hits = []
    lede = lede_defines_subject(text)
    if lede:
        hits.append({'line': lede[0], 'kind': 'prose', 'rule': 'lede does not define its subject',
                     'match': '"%s" is not defined or in the headline' % lede[1],
                     'context': lede[2]})
    for line, match in parallel_frames(list(paragraphs(text, path))):
        hits.append({'line': line, 'kind': 'prose', 'rule': 'parallel-frame antithesis',
                     'match': match[:110], 'context': match[:170]})
    for line, kind, s in blocks(text, path):
        if kind == 'quote':
            continue
        for pat, rule, scope, ctxs in RULES:
            # A diagram label is held to the heading rules. An FAQ heading is
            # exempt from them, since a question is the form the section takes.
            k = kind
            if kind == 'diagram' or (kind == 'faq-heading' and scope == 'both'):
                k = 'heading'
            if scope != 'both' and scope != k:
                continue
            if context and context not in ctxs:
                continue
            m = re.search(pat, s, re.I | re.MULTILINE)
            if m and not _exempt(s, m):
                hits.append({'line': line, 'kind': kind, 'rule': rule,
                             'match': m.group(0)[:110], 'context': s[:170]})
        if kind in ('heading', 'diagram'):
            payoff = em_dash_punchline(s)
            if payoff:
                hits.append({'line': line, 'kind': kind, 'rule': 'em-dash-punchline heading',
                             'match': payoff[:110], 'context': s[:170]})
        # A diagram labels its parts. A sentence in one restates the drawing.
        if kind == 'diagram' and s.endswith('.') and len(s.split()) >= 6:
            hits.append({'line': line, 'kind': kind, 'rule': 'sentence inside a diagram',
                         'match': s[:110], 'context': s[:170]})
        # Structural checks read whole sentences. Markdown wraps them across
        # lines, so for markdown they run over paragraphs in a second pass and
        # a wrapped fragment of a sentence is never mistaken for a sentence.
        if kind == 'prose' and not is_md:
            hits.extend(structural(line, kind, s))
    if is_md:
        for line, para in paragraphs(text, path):
            hits.extend(structural(line, 'prose', para))
    # One hit per rule per line keeps the report readable.
    seen, out = set(), []
    for h in hits:
        k = (h['line'], h['rule'])
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out


def check_drift():
    """The rule bank and SKILL.md drift apart silently. Compare their sizes."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    skill = os.path.join(root, '.claude', 'skills', 'house-voice', 'SKILL.md')
    if not os.path.exists(skill):
        print('SKILL.md not found at', skill)
        return 1
    with open(skill, encoding='utf-8') as f:
        md = f.read()
    banned = md.split('## Banned constructions', 1)[-1].split('## Required voice', 1)[0]
    named = re.findall(r'^\*\*(.+?)\*\*', banned, re.M)
    print('constructions named in SKILL.md : %d' % len(named))
    print('rules in this auditor           : %d' % len(RULES))
    missing = len(named) - len(set(r[1].split(' (')[0] for r in RULES))
    if missing > 0:
        print('\nSKILL.md names more constructions than the bank encodes.')
        print('Some are diction rules a regex cannot express. Review:')
        for n in named:
            print('   -', n)
    return 0


def report(path, hits, only_headings=False):
    out = ['\n=== %s ===' % path]
    hits = [h for h in hits if not only_headings or h['kind'] == 'heading']
    if not hits:
        out.append('  ok')
        return '\n'.join(out)
    by = {}
    for h in hits:
        by.setdefault(h['rule'], []).append(h)
    out.append('  %d violation(s) across %d rule(s)' % (len(hits), len(by)))
    for rule in sorted(by):
        out.append('\n  [%s]' % rule)
        for h in by[rule]:
            out.append('    line %-5d %-8s “%s”' % (h['line'], h['kind'], h['match']))
    return '\n'.join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='*')
    p.add_argument('--context', choices=ALL, help='page type; suppresses rules that do not apply to it')
    p.add_argument('--only-headings', action='store_true')
    p.add_argument('--format', choices=('text', 'json'), default='text')
    p.add_argument('--check-drift', action='store_true', help='compare the rule bank against SKILL.md')
    a = p.parse_args()

    if a.check_drift:
        return check_drift()
    if not a.files:
        p.error('give at least one file, or use --check-drift')

    results, total = {}, 0
    for path in a.files:
        hits = audit_file(path, context=a.context)
        if a.only_headings:
            hits = [h for h in hits if h['kind'] == 'heading']
        results[path] = hits
        total += len(hits)

    if a.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        for path, hits in results.items():
            print(report(path, hits, only_headings=a.only_headings))
        print('\nTotal: %d violation(s) across %d file(s)' % (total, len(a.files)))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
