#!/usr/bin/env python3
"""Scaffold a blog-technical/posts/<slug>.html from a live akka.io/blog/<slug> post.

Fetches the live post, extracts title/dek/author/date/body, applies URL
rewrites for the known dead-link mapping, and emits a first-pass template
render suitable for blog-technical/ + port_blog_technical.py.

Usage:
    python tools/blog-technical/scaffold.py <slug> [slug ...]
    python tools/blog-technical/scaffold.py --all       # every post in scratchpad/live-blog/urls.txt

The generated file is a starting point — headline, sections, and figure
captions inherit whatever is in the source; a human editor should still
review each post for section-eyebrow phrasing, pull quotes, and voice.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html_sanitizer import sanitize as _sanitize_html

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
POSTS_DIR = os.path.join(ROOT, 'blog-technical', 'posts')
LIVE_CACHE = os.path.join(ROOT, 'scratchpad', 'live-blog')

# Dead-link → replacement map from today's discovery pass.
URL_REWRITES = {
    'https://bsky.app/profile/akka.io': 'https://bsky.app/profile/akka.bsky.social',
    'https://x.com/lightbend': 'https://x.com/akka_io',
    'https://akka.io/customer-stories/icon-solutions-leverages-akka-to-deliver-cloud-native-payment-solutions': 'https://akka.io/customer-stories/icon-solutions',
    'https://doc.akka.io/self-managed/index.html': 'https://doc.akka.io/operations/index.html',
    'https://doc.akka.io/sdk/agent-memory.html': 'https://doc.akka.io/sdk/agents/memory.html',
    'https://doc.akka.io/sdk/entities.html': 'https://doc.akka.io/sdk/event-sourced-entities.html',
    'https://doc.akka.io/concepts/event-sourced-entities.html': 'https://doc.akka.io/sdk/event-sourced-entities.html',
}

# House-voice regex bank — patterns to FLAG (not auto-fix) in the generated post.
# Kept in sync with .claude/skills/house-voice/SKILL.md.
VOICE_FLAGS = [
    # Antithesis and its softened forms
    (r"\bisn't\b.{0,60}\b(it['’]s|it is|but|—)\b", 'antithesis (isn\'t X, it\'s Y)'),
    (r"\baren['’]t\b.{0,60}\b(they['’]re|they are|but|—)\b", 'antithesis (aren\'t X, they\'re Y)'),
    (r"\bis not\b.{0,60}\bit is\b", 'antithesis (is not X, it is Y)'),
    (r"\bnot only\b.{0,40}\bbut also\b", 'not-only-but-also'),
    (r"\b[A-Z][a-z]+ (does|is|runs|works)\b.{0,80}\b(don't|doesn't|isn't)\b\.", 'parallel-negation antithesis'),

    # Enumerate-then-collapse / counting collapse
    (r"\bthe same (one|two|three|four|five|six|seven|eight|nine|ten|\d+) \w+", 'the-same-N pattern'),
    (r"\b(all|both|every) (two|three|four|five|six|seven|eight|nine|ten|\d+) \w+ in one\b", 'enumerate-then-collapse'),
    (r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+) \w+, (one|two|three) \w+\b", 'N X, N Y collapse'),

    # Em-dash punchlines in headings/captions
    # (Scaffolder can only flag prose it processes; headings are matched via a separate pass.)

    # Hype and AI-tells
    (r"\bunlock\b|\bsupercharge\b|\bleverage\b|\bharness\b|\bempower\b|\brevolutionize\b|\bseamless\b|\bgame-changer\b|\bdelve\b", 'hype verb'),
    (r"\bat its core\b|\bmake no mistake\b|\btestament to\b|\bat the end of the day\b|\bworth noting\b|\bthis is where\b", 'AI-tell phrase'),
    (r"\bthroughline\b|\btapestry\b|\bjourney\b", 'AI-metaphor noun'),

    # Colour and emotion adjectives
    (r"\b(shiny|elegant|beautiful|powerful|robust|modern|critical|vital|essential|amazing|incredible|remarkable)\b", 'colour/emotion adjective'),

    # Adjective-for-number substitutions
    (r"\b(massive|blazing[- ]fast|comprehensive|sharpest|strongest|fastest|largest)\b", 'adjective-for-number'),

    # Framework-lecture / second-person imperatives
    (r"\bTake a hard look\b|\bAsk yourself\b|\bBefore you start\b|\bLet's face it\b", 'framework-lecture opener'),

    # Metaphors standing in for plain words
    (r"\b(load-bearing|the spine|the wedge|north star|flywheel|substrate)\b", 'metaphor for plain word'),

    # Rhetorical devices
    (r"\bThis is the real story:\b|\bThe real story here\b", 'colon-drama'),
]

# Heading-specific patterns (em-dash punchline, rhetorical question)
HEADING_FLAGS = [
    (r"^[^—]{5,60}—[^—]{5,60}[.?]?$", 'em-dash-punchline heading'),
    (r"^(What|Why|How|When|Where|Which|Who)\b[^?]*[.?]\s*$", 'rhetorical question heading'),
]



def fetch(url_or_path):
    """Fetch by URL, or read from local cache."""
    if url_or_path.startswith(('http://', 'https://')):
        req = urllib.request.Request(url_or_path, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    with open(url_or_path, 'r', encoding='utf-8') as f:
        return f.read()


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()


def extract_meta(html):
    """Pull title, dek, author, publish date."""
    title = ''
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if m:
        title = strip_tags(m.group(1))

    dek = ''
    m = re.search(r'<h2 class="blog-subtitle"[^>]*>(.*?)</h2>', html, re.S)
    if m:
        dek = strip_tags(m.group(1))

    author = ''
    author_title = ''
    date = ''
    # Byline patterns — strict name shape: "By " must be followed by
    # 2–5 capitalized-word tokens (Firstname Lastname), optionally trailed by
    # ", Title[, Company]". This avoids matching body prose like "By executing"
    # or "By decoupling" which are verbs, not bylines.
    NAME = r"[A-Z][a-zA-ZÀ-ÿ\-'’]{1,30}"                      # a single capitalized token
    FULLNAME = rf"({NAME}(?:\s+{NAME}){{1,4}})"               # 2–5 word capitalized name
    OPT_TITLE = r"(?:,\s+[A-Za-z][A-Za-z\s,&/\-]{4,80})?"     # optional ", Title, Company"
    for pat in [
        rf'<p[^>]*>\s*<em[^>]*>By\s+{FULLNAME}{OPT_TITLE}\s*</em>\s*</p>',
        rf'<a[^>]*rel="author"[^>]*>\s*{FULLNAME}\s*</a>',
        rf'<p[^>]*>\s*By\s+{FULLNAME}{OPT_TITLE}\s*</p>',
        rf'<p class="blog-eyebrow"[^>]*>By\s*{FULLNAME}{OPT_TITLE}\s*</p>',
    ]:
        m = re.search(pat, html, re.S)
        if m:
            # group(1) is FULLNAME. Try to grab optional trailing title.
            author = m.group(1).strip()
            # Search for trailing ", Title" in the full match text
            full = m.group(0)
            tail_m = re.search(r',\s+([A-Za-z][A-Za-z\s,&/\-]{4,80})', full)
            if tail_m:
                author_title = tail_m.group(1).strip().rstrip(',')
            break
    # If author found but no title, try common HubSpot title spots
    if author and not author_title:
        # Try nearby "Sr Director, ..." or bio blurb
        m = re.search(r'rel="author"[^>]*>\s*[^<]+</a>\s*</[a-z]+>\s*(?:<[^>]+>\s*)*([A-Z][a-zA-Z ,&/\-]{5,80}?)\s*(?:</|<br)', html)
        if m:
            author_title = m.group(1).strip().rstrip(',')

    # Publish date — accept HubSpot's "YYYY-MM-DD HH:MM:SS" or ISO
    m = re.search(r'datetime="([^"]+)"', html)
    if m:
        raw = m.group(1)
        date = raw.split('T')[0].split(' ')[0]

    # Tag list for the kicker (e.g. ["Multi-region", "Distributed Systems"] → "MULTI-REGION · DISTRIBUTED SYSTEMS")
    tags = []
    for m in re.finditer(r'blog-post__tag-link[^>]*>\s*([A-Za-z][A-Za-z0-9 &/\-]{1,40})\s*</a>', html):
        tag = m.group(1).strip()
        if tag and tag not in tags:
            tags.append(tag)

    # Reading time: HubSpot renders "N minute read" in the post header meta strip
    read_min = None
    m = re.search(r'(\d{1,3})\s*minute\s*read', html, re.I)
    if m:
        read_min = int(m.group(1))

    return {
        'title': title,
        'dek': dek,
        'author': author,
        'author_title': author_title,
        'date': date,
        'tags': tags[:3],   # top 3 tags for the kicker
        'read_min': read_min,
    }


def sentence_case_title(title):
    """Preserve source title; lowercase the first word after a colon (except
    known proper nouns) and ensure the string ends with a period.

    "Akka Memory: Durable, in-memory, and sharded data"
       → "Akka Memory: durable, in-memory, and sharded data."
    """
    if not title:
        return title
    PROPER = {'Akka', 'AI', 'LLM', 'HTTP', 'API', 'SDK', 'JVM', 'Java', 'Scala',
              'Kotlin', 'Kafka', 'JSON', 'YAML', 'AWS', 'GCP', 'REST', 'SQL',
              'GraphQL', 'gRPC', 'MCP', 'A2A', 'Postgres', 'PostgreSQL', 'MongoDB',
              'Redis', 'ML', 'GPU', 'CPU', 'Docker', 'Kubernetes', 'K8s'}

    def _lower_first(s):
        s = s.strip()
        if not s:
            return s
        first = s.split(None, 1)[0].rstrip(',.:;')
        if first in PROPER or (len(first) > 1 and first.isupper()):
            return s
        return s[0].lower() + s[1:]

    if ':' in title:
        head, tail = title.split(':', 1)
        title = f'{head.strip()}: {_lower_first(tail.strip())}'
    if not title.rstrip().endswith(('.', '!', '?')):
        title = title.rstrip() + '.'
    return title


def kicker_from_tags(tags):
    """Two or three tags, uppercased, separated by ' · '."""
    if not tags:
        return 'BLOG'
    return ' · '.join(t.upper() for t in tags[:3])


def promote_first_paragraph_to_standfirst(body):
    """If the body opens with a <p>, extract at most the first two sentences
    as the standfirst. Return (dek_text, body_without_that_p)."""
    m = re.match(r'\s*<p(?:\s[^>]*)?>(.*?)</p>\s*', body, re.S)
    if not m:
        return None, body
    text = strip_tags(m.group(1))
    if len(text) < 50:
        return None, body
    # Take the first 1–2 sentences: cap at ~260 chars, break at a period.
    sents = re.findall(r'[^.!?]+[.!?]', text)
    if not sents:
        # No period — take the whole thing if short enough
        if len(text) > 300:
            return None, body
        return text, body[m.end():]
    dek = sents[0].strip()
    if len(dek) < 100 and len(sents) > 1:
        candidate = (dek + ' ' + sents[1].strip()).strip()
        if len(candidate) <= 260:
            dek = candidate
    return dek, body[m.end():]


def inject_h3_subheads(body):
    """Every h2 without a following h3 subhead gets one auto-generated from
    the first sentence of the first paragraph in that section.

    The mechanical seed reads better than nothing — human editor can polish.
    """
    def add_subhead(m):
        h2_full = m.group(0)
        after = m.group(2)
        # Already has h3 within the first paragraph of the section? Leave alone.
        # Look at the next 2000 chars after the h2.
        # (Not applicable here — this regex only sees the h2 itself; do a second pass below.)
        return h2_full

    # Two-pass: find each h2 and inspect what follows it in the body string.
    out = []
    last = 0
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', body, re.S):
        out.append(body[last:m.end()])
        # Look at the next slice for an h3 or an opening paragraph
        after_start = m.end()
        # Find where the next h2/h3 starts to bound this section
        next_h = re.search(r'<h[23]\b', body[after_start:])
        section_end = after_start + (next_h.start() if next_h else len(body[after_start:]))
        section = body[after_start:section_end]
        if re.search(r'<h3\b', section):
            last = m.end()
            continue
        # Find first <p> in this section (may or may not have class="lede")
        p_m = re.search(r'<p(?:\s[^>]*)?>(.*?)</p>', section, re.S)
        if not p_m:
            last = m.end()
            continue
        p_text = strip_tags(p_m.group(1))
        # Prefer the first sentence if under 140 chars; otherwise the first
        # clause ending in a comma or semicolon; otherwise skip (better no
        # subhead than a truncation).
        sent_m = re.match(r'(.{20,170}?[.!?])(?:\s|$)', p_text)
        if sent_m:
            subhead = sent_m.group(1).strip()
        else:
            clause_m = re.match(r'(.{20,160}?[,;:])\s', p_text)
            if not clause_m:
                last = m.end()
                continue
            subhead = clause_m.group(1).strip().rstrip(',;:') + '.'
        out.append(f'\n<h3>{subhead}</h3>\n')
        last = m.end()
    out.append(body[last:])
    return ''.join(out)


def format_date(iso_date):
    """2025-07-22 → Jul 22, 2025."""
    if not iso_date or len(iso_date) < 10:
        return iso_date
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    try:
        y, m, d = iso_date[:10].split('-')
        return f'{months[int(m) - 1]} {int(d)}, {y}'
    except Exception:
        return iso_date


def find_body(html):
    """Locate the main body container.

    Akka's HubSpot posts wrap prose in `.blog-post__body` (double underscore,
    BEM naming). Extract from the opening of that div to the next known stop:
    CTA panel, related-posts strip, sharing widget, or the "Posts by this
    author" footer strip.
    """
    m = re.search(r'<div[^>]*class="[^"]*blog-post__body[^"]*"[^>]*>', html)
    if not m:
        # Fallback candidates for other HubSpot post templates
        for pat in [
            r'<div[^>]*class="[^"]*post-body[^"]*"[^>]*>',
            r'<article[^>]*>',
        ]:
            m = re.search(pat, html)
            if m:
                break
    if not m:
        return html
    start = m.end()
    tail = html[start:start + 200000]
    stops = [
        'class="cta-panel',
        'class="blog-related',
        'class="post-share',
        'class="post-body-footer',
        'blog-eyebrow">Posts by',
        'id="hs-blog-recommended-posts',
        '"blog-related-posts',
        'class="right"',            # HubSpot right sidebar with author card
        'class="blog_info_div',     # author bio card
        'class="blog-post__meta',   # HubSpot post meta panel
        'blog_author',              # inner bio class
        '>Posted By<',              # bio heading text
    ]
    end = len(tail)
    for stop in stops:
        j = tail.find(stop)
        if 0 < j < end:
            end = j
    # Back up to the enclosing tag boundary
    back = tail.rfind('<', 0, end)
    if back > 0:
        end = back
    return tail[:end]


def _unwrap_tag(body, opener_regex, tag_name):
    """For every regex match of opener_regex (e.g. `<div id="hs_cos_wrapper_...">`),
    find its balanced closing `</tag>` and remove both, keeping the inner
    content flush with the surrounding stream. Requires a bracket-matching
    scan so nested tags of the same type stay balanced."""
    out = []
    i = 0
    while i < len(body):
        m = re.search(opener_regex, body[i:])
        if not m:
            out.append(body[i:])
            break
        # Emit everything up to the opener
        out.append(body[i:i + m.start()])
        # Advance past the opener
        j = i + m.end()
        # Scan for balanced closing tag
        depth = 1
        open_re = re.compile(rf'<{tag_name}\b[^>]*>', re.I)
        close_re = re.compile(rf'</{tag_name}\s*>', re.I)
        k = j
        while k < len(body):
            no = open_re.search(body, k)
            nc = close_re.search(body, k)
            if not nc:
                # Unbalanced — treat rest as inner, no close found
                out.append(body[j:])
                return ''.join(out)
            if no and no.start() < nc.start():
                depth += 1
                k = no.end()
            else:
                depth -= 1
                if depth == 0:
                    # Emit inner content (between opener end and close start)
                    out.append(body[j:nc.start()])
                    i = nc.end()
                    break
                k = nc.end()
        else:
            out.append(body[j:])
            break
    return ''.join(out)


def _strip_hubspot_wrappers(body):
    """Remove HubSpot widget wrappers that leave nested empty <div>s
    behind. Uses balanced-tag matching so both opener and closer are
    removed together — regex-only stripping leaves orphan `</div>`s that
    break the outer scoping wrapper."""
    # Unwrap hs_cos_wrapper span/div — balanced open+close removal
    body = _unwrap_tag(body, r'<span[^>]*id="hs_cos_wrapper[^"]*"[^>]*>', 'span')
    body = _unwrap_tag(body, r'<div[^>]*id="hs_cos_wrapper[^"]*"[^>]*>', 'div')
    body = _unwrap_tag(body, r'<div[^>]*data-aos[^>]*>', 'div')
    body = _unwrap_tag(body, r'<section[^>]*>', 'section')
    return body


def _collapse_empty_divs(body):
    """Collapse only truly empty <div>s that add no content. Do NOT collapse
    nested wrappers that carry a class (they are template scaffolding like
    .plot-wrap, .plate--flush, .wide, .body col — all load-bearing)."""
    prev = None
    while prev != body:
        prev = body
        # Only fully empty <div>s (no attributes with classes, no content)
        body = re.sub(r'<div(?![^>]*class=)[^>]*>\s*</div>', '', body)
    return body


def _normalize_br_paragraphs(body):
    """<br><br> inside a <p> creates a paragraph gap. Split those into two
    <p>s so the .body p margin-bottom applies uniformly."""
    def split(m):
        inner = m.group(1)
        # Split on 2+ consecutive <br> tags
        parts = re.split(r'(?:<br\s*/?>\s*){2,}', inner)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) <= 1:
            return m.group(0)
        return ''.join(f'<p>{p}</p>' for p in parts)
    return re.sub(r'<p(?:\s[^>]*)?>(.*?)</p>', split, body, flags=re.S)


def clean_body(body_html):
    """Strip HubSpot template noise from the body region."""
    # First pass: whitelist sanitizer strips every inline style/legacy attr,
    # unwraps HubSpot widgets, normalizes code language classes, converts
    # class="note" to class="enote". Anything the template can't render
    # cleanly is removed at the source.
    body = _sanitize_html(body_html)
    # kill top-level meta blocks + byline paragraphs (which are extracted separately)
    for pat in [
        r'<h1[^>]*>.*?</h1>',
        r'<h2 class="blog-subtitle"[^>]*>.*?</h2>',
        r'<p class="blog-eyebrow"[^>]*>.*?</p>',
        r'<p[^>]*>\s*<em[^>]*>By\s+.*?</em>\s*</p>',    # <p><em>By ...</em></p> byline
        r'<p[^>]*>\s*By\s+[A-Z][a-zA-Z\-\'\. ,]{3,120}\s*</p>',   # <p>By ...</p> byline
        r'<div class="post-social-sharing[^"]*"[^>]*>.*?</div>',
        r'<div class="hs-featured-image-wrapper[^"]*"[^>]*>.*?</div>',
        r'<!--more-->',
    ]:
        body = re.sub(pat, '', body, flags=re.S)
    # HubSpot widget wrappers → strip so inner content flows into prose
    body = _strip_hubspot_wrappers(body)
    # <br><br> inside a <p> → real paragraph breaks (structural fix, not text)
    body = _normalize_br_paragraphs(body)
    # Rewrite URLs
    for old, new in URL_REWRITES.items():
        body = body.replace(old, new)
        body = body.replace(old.replace('&', '&amp;'), new)
    # (inline style + non-whitelisted class stripping is already handled by
    # the whitelist sanitizer at the top of clean_body. The old blanket
    # `_strip_class` here stripped classes off <figure> and <div>, undoing
    # the wrappers the sanitizer emits for iframes/plates.)
    # Transform bare images into figure.viz + plate--flush structure so the
    # image auditor can size them (no editorial content injected)
    body = _wrap_images_in_figures(body)
    # Apply .rtbl to tables + wrap in .wide breakout (structural only)
    body = _wrap_tables(body)
    # Section numbering ('Section I ·') is handled by CSS counter on .body h2,
    # so h2 text stays verbatim from source. No text modification here.
    # First paragraph gets lede class for the drop cap (styling, not text)
    body = _add_lede_class(body)
    # Code blocks get language-* class so Prism can highlight them
    body = _mark_code_blocks(body)
    # Collapse the empty-div cascades HubSpot widgets leave behind. Runs LAST
    # so it also swallows now-empty wrappers vacated by _strip_hubspot_wrappers.
    body = _collapse_empty_divs(body)
    return body.strip()


def _alt_to_title(alt):
    """Turn 'empty-recovered-state-agent-bg' or 'sharded-data' into a
    reasonable h4 heading. Human polishes later; this is the mechanical seed."""
    if not alt:
        return 'Figure.'
    t = alt.replace('-', ' ').replace('_', ' ').strip()
    # Kill trailing 'bg', 'alt bg', 'wide', 'small' size suffixes
    t = re.sub(r'\b(alt|bg|wide|small|tall|preview|thumbnail)\b', '', t, flags=re.I).strip()
    if not t:
        return 'Figure.'
    return t[0].upper() + t[1:] + '.'


def _wrap_images_in_figures(body):
    """Wrap every <img> in the template figure shape, numbered with
    'Figure N' kickers and h4 titles seeded from the img alt text."""
    counter = [0]

    def wrap(m):
        img_tag = m.group(0)
        src_m = re.search(r'src="([^"]+)"', img_tag)
        alt_m = re.search(r'alt="([^"]*)"', img_tag)
        alt = alt_m.group(1).strip() if alt_m else ''
        src = src_m.group(1) if src_m else ''
        if any(k in src.lower() for k in ('headshot', 'branding', 'wordmark', 'avatar', 'logo')):
            return ''  # drop entirely
        counter[0] += 1
        n = counter[0]
        # Every figure gets a caption. If the source alt is real prose, use it
        # verbatim. If it looks like a filename slug (e.g. "empty-recovered-
        # state-agent"), un-slug it to "Empty recovered state agent." so the
        # caption line is always present. Empty alt → generic "Figure N" caption.
        cap_text = ''
        if alt:
            if ' ' in alt and not re.fullmatch(r'[a-z0-9\-_.]+', alt):
                cap_text = alt
            else:
                un_slug = re.sub(r'[-_]+', ' ', alt).strip()
                if un_slug:
                    cap_text = un_slug[0].upper() + un_slug[1:] + '.'
        if not cap_text:
            cap_text = f'Figure {n}.'
        caption_html = f'  <figcaption>{cap_text}</figcaption>\n'
        return (
            '\n</div>\n\n<div class="wide">\n'
            '<figure class="viz">\n'
            f'  <p class="viz-title">Figure {n}</p>\n'
            '  <div class="plot-wrap">\n'
            f'    <div class="plate plate--flush">{img_tag}</div>\n'
            '  </div>\n'
            f'{caption_html}'
            '</figure>\n'
            '</div>\n\n<div class="body col">\n'
        )
    return re.sub(r'<img\b[^>]*/?>', wrap, body)


GENERIC_INTRO_H2 = re.compile(r'^\s*(introduction|intro|overview|summary|preface|preamble|abstract)\.?\s*$', re.I)


def _drop_intro_h2(body):
    """If the first h2 is a generic 'Introduction' header, drop it entirely
    so its body content flows straight from the byline as the lede."""
    m = re.search(r'<h2(?:\s[^>]*)?>(.*?)</h2>', body, re.S)
    if not m:
        return body
    text = strip_tags(m.group(1))
    if GENERIC_INTRO_H2.match(text):
        return body[:m.start()] + body[m.end():]
    return body


def _number_h2_sections(body):
    """Prepend 'Section I ·', 'Section II ·', … to each h2."""
    # First: drop a generic 'Introduction' h2 if present so numbering starts
    # with the first real section title.
    body = _drop_intro_h2(body)
    romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
              'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
    counter = [0]

    def bump(m):
        counter[0] += 1
        idx = counter[0] - 1
        roman = romans[idx] if idx < len(romans) else str(idx + 1)
        return f'<h2>Section {roman} · {m.group(2)}</h2>'
    # Match h2 with any attributes (id, style, class), strip them, and re-emit.
    return re.sub(r'<h2(\s[^>]*)?>(.*?)</h2>', bump, body, flags=re.S)


def _add_lede_class(body):
    """First meaningful <p> inside the first body chunk becomes class='lede'
    so the drop cap fires."""
    m = re.search(r'<p(?![^>]*class=)([^>]*)>', body)
    if m:
        return body[:m.start()] + f'<p class="lede"{m.group(1)}>' + body[m.end():]
    return body


def _mark_code_blocks(body):
    """Ensure every <pre> block contains <code class='language-*'> so Prism
    can highlight it. Handles three source shapes:
      1. <pre>code</pre>                       — wrap in <code class="language-…">
      2. <pre><code>code</code></pre>          — add language class to the <code>
      3. <pre class='…'><code>code</code></pre>— same, class stays on <code>
    Default language is Java (matches Akka source 95% of the time); YAML/JSON/
    shell content falls through to language-text."""
    JAVA_HINTS = re.compile(
        r'\b(public|private|protected|static|final|import|class|interface|@Override|@\w+|void|List<|Map<|Optional<|Effect|Stream)\b'
    )

    def detect_lang(content):
        # Strip inner tags to get plain code text
        plain = re.sub(r'<[^>]+>', '', content)
        return 'java' if JAVA_HINTS.search(plain) else 'text'

    def wrap(m):
        pre_open = m.group(1)
        content = m.group(2)
        # Case 2/3: content already starts with <code>
        inner = re.match(r'\s*<code(\b[^>]*)>(.*?)</code>\s*$', content, re.S)
        if inner:
            code_attrs = inner.group(1)
            code_body = inner.group(2)
            # If code already has language class, leave alone
            if 'language-' in code_attrs:
                return m.group(0)
            lang = detect_lang(code_body)
            # Strip other classes, replace with language-*
            new_attrs = re.sub(r'\s*class="[^"]*"', '', code_attrs)
            new_attrs = f' class="language-{lang}"' + new_attrs
            return f'{pre_open}<code{new_attrs}>{code_body}</code></pre>'
        # Case 1: plain content, no inner <code>
        if 'language-' in pre_open:
            return m.group(0)
        lang = detect_lang(content)
        return f'{pre_open}<code class="language-{lang}">{content}</code></pre>'

    return re.sub(r'(<pre\b[^>]*>)(.*?)</pre>', wrap, body, flags=re.S)


def _wrap_tables(body):
    """Wrap tables in a .wide breakout with a horizontal-scroll container so
    they never overflow the viewport. Source tables keep their own markup —
    the .rtbl compact-data style is NOT auto-applied (it's for hand-authored
    data tables only).

    Strips inline style/width/height/align attributes on every table element
    (source posts routinely set inline `border: 1px solid #99acc2` and per-cell
    heights that beat any CSS rule via inline-style specificity).
    """
    def wrap(m):
        tbl_html = m.group(0)
        # Strip inline style/width/height/align/bgcolor from every element
        # inside the table so scoped CSS can actually take effect.
        for attr in ('style', 'width', 'height', 'align', 'valign', 'bgcolor', 'cellpadding', 'cellspacing', 'border'):
            tbl_html = re.sub(rf'\s+{attr}="[^"]*"', '', tbl_html)
        # Also strip colgroup — HubSpot-editor tables usually set per-col widths
        # via inline styles that we've already stripped above; the whole
        # colgroup wrapper is inert without them.
        tbl_html = re.sub(r'<colgroup\b.*?</colgroup>\s*', '', tbl_html, flags=re.S)
        return (
            '\n</div>\n\n<div class="wide">\n'
            '<div class="table-scroll">\n'
            + tbl_html
            + '\n</div>\n</div>\n\n<div class="body col">\n'
        )
    return re.sub(r'<table\b.*?</table>', wrap, body, flags=re.S)


def extract_sections(body_html):
    """Split body by h2/h3 boundaries into ordered sections.
    Returns list of {header: str, level: 2|3|None, content: str}."""
    parts = []
    last = 0
    for m in re.finditer(r'<h([23])[^>]*>(.*?)</h\1>', body_html, re.S):
        chunk = body_html[last:m.start()].strip()
        if chunk:
            parts.append({'header': None, 'level': None, 'content': chunk})
        parts.append({'header': strip_tags(m.group(2)), 'level': int(m.group(1)), 'content': ''})
        last = m.end()
    tail = body_html[last:].strip()
    if tail:
        if parts and parts[-1]['header'] is not None and not parts[-1]['content']:
            parts[-1]['content'] = tail
        else:
            parts.append({'header': None, 'level': None, 'content': tail})
    # Merge lead-in content into first section if it's a leading paragraph
    return parts


def voice_flags(text):
    """Return list of voice-rule violations found in the given prose."""
    plain = strip_tags(text)
    found = []
    for pat, label in VOICE_FLAGS:
        if re.search(pat, plain, re.I):
            found.append(label)
    return found


# Posts link the theme rather than carrying a copy of it, so an edit to
# blog-technical/theme/ reaches every post. Paths are relative to
# blog-technical/posts/, where scaffolded posts are written.
THEME_LINK = '<link rel="stylesheet" href="../theme/base.css">'


def build_scaffold(slug, meta, sections):
    """Render the blog-technical template for one post — source content is
    passed through verbatim, no text invention. Only structural / styling
    transformations happen here."""
    date_pretty = format_date(meta['date']) if meta.get('date') else ''
    # Title verbatim from source, no case changes, no terminal punctuation.
    title_display = meta['title']
    kicker = kicker_from_tags(meta.get('tags') or [])

    # Standfirst only if source has an explicit dek. Don't invent one from the
    # first paragraph — editorial content that the source blog either has or
    # doesn't have.
    dek = meta.get('dek') or ''

    # Emit sections verbatim: source h2 stays h2, source h3 stays h3. Only h2s
    # start a new .body.col wrapper — h3s flow inline inside the current h2's
    # section so the CSS `h2 + h3` adjacent-sibling selector can promote the
    # first h3 in a section to the larger thesis-heading style.
    # No numbering (CSS counter handles that), no dropping, no injection.
    body_parts = []
    for sec in sections:
        if sec['header']:
            level = sec['level'] if sec['level'] in (2, 3) else 2
            tag = f'h{level}'
            if level == 2:
                body_parts.append(
                    f'\n</div>\n\n<div class="body col">\n\n'
                    f'<{tag}>{sec["header"]}</{tag}>\n'
                    f'{sec["content"]}\n'
                )
            else:
                # h3 stays in the current div so h2+h3 can match
                body_parts.append(
                    f'\n<{tag}>{sec["header"]}</{tag}>\n'
                    f'{sec["content"]}\n'
                )
        else:
            body_parts.append(f'\n{sec["content"]}\n')

    body_html = ''.join(body_parts)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta["title"]} — Akka</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js" defer></script>
{THEME_LINK}
</head>
<body>

<div class="progress" id="prog"></div>

<div class="colophon">
  <span class="brand">AKKA</span>
  <span class="sep">/</span>
  <span>The Technical</span>
  <span class="r">{slug}</span>
</div>

<article>

<header class="hero col">
  <div class="kicker">{kicker}</div>
  <h1 class="title">{title_display}</h1>
  {'<p class="standfirst">' + dek + "</p>" if dek else ""}
  <div class="byline">
    <div>{("<span class='au'>" + meta["author"] + "</span>" + (" · " + meta["author_title"] if meta.get("author_title") else "")) if meta["author"] else ""}</div>
    <div class="r">{'<time datetime="' + meta["date"] + '">' + date_pretty + "</time>" + (" · " + str(meta["read_min"]) + " min read" if meta.get("read_min") else "") if date_pretty else ""}</div>
  </div>
</header>

<div class="body col">
{body_html}
</div>

</article>

<div class="foot">
  Akka · The Technical · {date_pretty}
</div>

<script>
(function(){{var bar=document.getElementById('prog');function u(){{var h=document.documentElement;var s=h.scrollTop||document.body.scrollTop;var t=(h.scrollHeight||document.body.scrollHeight)-h.clientHeight;bar.style.width=(t>0?(s/t)*100:0)+'%';}}window.addEventListener('scroll',u,{{passive:true}});u();}})();
</script>

</body>
</html>
'''


def _hs_token():
    tok = os.environ.get('HUBSPOT_TOKEN', '')
    if tok:
        return tok
    env_txt = open(os.path.join(ROOT, 'scratchpad', '.hs_env'), 'r').read()
    m = re.search(r'HUBSPOT_TOKEN=(\S+)', env_txt)
    if not m:
        raise SystemExit('HUBSPOT_TOKEN not found in scratchpad/.hs_env')
    return m.group(1)


_TAG_CACHE = {}
_AUTHOR_CACHE = {}


def _resolve_author(author_id, tok):
    """/cms/v3/blogs/authors/{id} returns {name, fullName, bio, ...}. authorName
    on the post object is unreliable — often reflects last editor, not author.
    Returns (fullName, bio) or (None, None)."""
    if not author_id:
        return None, None
    if author_id in _AUTHOR_CACHE:
        return _AUTHOR_CACHE[author_id]
    try:
        req = urllib.request.Request(
            f'https://api.hubapi.com/cms/v3/blogs/authors/{author_id}',
            headers={'Authorization': f'Bearer {tok}'})
        r = json.loads(urllib.request.urlopen(req, timeout=15).read())
        pair = ((r.get('fullName') or r.get('name') or '').strip(),
                (r.get('bio') or '').strip())
    except Exception:
        pair = (None, None)
    _AUTHOR_CACHE[author_id] = pair
    return pair


def _resolve_tag_names(tag_ids, tok):
    """Turn [12345, 67890] into ["Multi-region", "Distributed Systems"]."""
    names = []
    for tid in tag_ids:
        if tid in _TAG_CACHE:
            names.append(_TAG_CACHE[tid])
            continue
        try:
            req = urllib.request.Request(
                f'https://api.hubapi.com/cms/v3/blogs/tags/{tid}',
                headers={'Authorization': f'Bearer {tok}'})
            r = json.loads(urllib.request.urlopen(req, timeout=15).read())
            _TAG_CACHE[tid] = r.get('name', '')
            names.append(_TAG_CACHE[tid])
        except Exception:
            _TAG_CACHE[tid] = ''
    return [n for n in names if n]


def _fetch_post_via_api(slug, tok):
    """Look up a post by slug via HubSpot Blog API. Returns the full post JSON
    or None if not found. Slug may be given with or without the 'blog/' prefix."""
    canonical_slug = slug if slug.startswith('blog/') else f'blog/{slug}'
    req = urllib.request.Request(
        f'https://api.hubapi.com/cms/v3/blogs/posts?slug={canonical_slug}&limit=1',
        headers={'Authorization': f'Bearer {tok}'})
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    results = r.get('results', [])
    return results[0] if results else None


def scaffold_one(slug):
    """Fetch source via HubSpot Blog API (postBody is clean authored HTML,
    no theme wrappers), transform to template shape, write to posts/<slug>.html."""
    import json as _json
    tok = _hs_token()
    post = _fetch_post_via_api(slug, tok)
    if not post:
        raise SystemExit(f'no HubSpot post found for slug {slug}')

    # Meta straight from the API — no scraping.
    tags = _resolve_tag_names(post.get('tagIds') or [], tok)
    # authorName on the post is unreliable (often reflects last editor). Prefer
    # /cms/v3/blogs/authors/{id} which has the actual byline + bio (title).
    author_full, author_bio = _resolve_author(post.get('blogAuthorId'), tok)
    date_iso = (post.get('publishDate') or '')[:10]
    # postSummary sometimes carries embedded HTML (blockquotes, inline styles)
    # AND HubL syntax ({% module_block %}, {% raw %}). Standfirst is prose
    # only — strip HTML tags, then HubL blocks, then collapse whitespace.
    raw_dek = (post.get('postSummary') or '').strip()
    dek_clean = re.sub(r'\{%.*?%\}', ' ', raw_dek, flags=re.S)
    dek_clean = re.sub(r'<[^>]+>', ' ', dek_clean)
    dek_clean = re.sub(r'\s+', ' ', dek_clean).strip()
    meta = {
        'title': post.get('name') or slug,
        'dek': dek_clean,
        'author': author_full or (post.get('authorName') or '').strip(),
        'author_title': author_bio or '',       # e.g. "Principal Engineer"
        'date': date_iso,
        'tags': tags[:3],
        'read_min': None,                       # optional; compute from body length
    }
    # Rough read-time from word count
    text = re.sub(r'<[^>]+>', ' ', post.get('postBody') or '')
    words = len(re.findall(r'\S+', text))
    if words:
        meta['read_min'] = max(1, round(words / 220))

    body = clean_body(post.get('postBody') or '')
    sections = extract_sections(body)
    scaffold = build_scaffold(slug, meta, sections)
    out_path = os.path.join(POSTS_DIR, f'{slug}.html')
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(scaffold)
    return out_path, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slugs', nargs='*')
    ap.add_argument('--all', action='store_true',
                    help='scaffold every slug in scratchpad/live-blog/urls.txt')
    args = ap.parse_args()

    slugs = list(args.slugs)
    if args.all:
        urls_file = os.path.join(LIVE_CACHE, 'urls.txt')
        with open(urls_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url:
                    slugs.append(url.rsplit('/', 1)[-1])
    slugs = list(dict.fromkeys(slugs))  # dedupe, preserve order

    for slug in slugs:
        try:
            path, meta = scaffold_one(slug)
            print(f'  {slug}  →  {os.path.relpath(path, ROOT)}   ({len(meta["title"])} title chars)')
        except Exception as e:
            print(f'  {slug}  ERROR  {e}')


if __name__ == '__main__':
    main()
