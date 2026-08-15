#!/usr/bin/env python3
"""Whitelist-based HTML sanitizer for blog-technical scaffolder.

Normalizes ANY source HTML shape into the template's expected form:
  - Strips every inline style/legacy attribute (bgcolor, align, height,
    cellpadding, etc.) from every element.
  - Strips the entire <colgroup> — source-editor column widths are inline
    styles we've already thrown out.
  - Unwraps decorative <span>/<font> that only carry style.
  - Rewrites known HubSpot classes to template classes:
      class="marketing-code"                      → (removed; Prism handles by <code class>)
      class="note"                                → class="enote"
      class="hs-embed-wrapper", "hs-fullwidth-embed" → (unwrapped)
      class="prettyprint"                         → (removed; add language-* per code)
  - Ensures <code> inside <pre> has a language-* class.
  - Preserves only whitelisted attributes on whitelisted tags.

Design intent: the auditor should never have to catch HubSpot leaks in the
output. This sanitizer is deterministic and shape-agnostic.
"""

import re


# Attributes allowed to survive per tag. Everything else is stripped.
ALLOWED_ATTRS = {
    'a':          {'href', 'rel', 'target'},
    'img':        {'src', 'alt', 'loading', 'srcset', 'sizes'},
    'iframe':     {'src', 'title', 'width', 'height', 'frameborder', 'allow', 'allowfullscreen'},
    'code':       {'class'},        # class="language-*"
    'pre':        set(),            # never carry a class — Prism reads class from <code>
    'blockquote': {'class'},        # pullquote / enote
    'table':      {'class'},        # rtbl / table-scroll survives if pre-applied
    'td':         {'class'},        # rtbl cell modifiers (prop, win)
    'th':         {'colspan', 'rowspan'},
    'tr':         set(),
    'thead':      set(),
    'tbody':      set(),
    'tfoot':      set(),
    'ul':         set(),
    'ol':         set(),
    'li':         set(),
    'p':          {'class'},        # standfirst / lede
    'h1':         set(),
    'h2':         set(),
    'h3':         set(),
    'h4':         set(),
    'em':         set(),
    'strong':     set(),
    'b':          set(),
    'i':          set(),
    'u':          set(),
    'br':         set(),
    'hr':         set(),
    'sup':        set(),
    'sub':        set(),
    'figure':     {'class', 'style'},   # keep --fig-w inline var
    'figcaption': set(),
    'div':        {'class'},        # keep only classes we recognize (see FILTER)
    'span':       set(),            # unwrap unless carrying data (rare)
}

# Classes we recognize on divs — everything else is unwrapped
KNOWN_DIV_CLASSES = {
    'wide', 'body', 'col', 'plot-wrap', 'plate', 'plate--flush', 'plate--paper',
    'plate--flush pair', 'pair', 'pair-label', 'table-scroll', 'blog-technical',
    'colophon', 'progress', 'byline', 'hero', 'kicker',
    'foot', 'r', 'au', 'brand', 'sep',        # template chrome
    'enote', 'pullquote',                      # callouts
    'note',                                    # legacy — will be rewritten
}

# Classes we allow on <p>
KNOWN_P_CLASSES = {'lede', 'standfirst', 'viz-title'}

# HubSpot / legacy classes we know to convert or drop
HUBSPOT_UNWRAP_DIV_CLASSES = {
    'hs-embed-wrapper', 'hs-embed-content-wrapper', 'hs-fullwidth-embed',
    'hs_cos_wrapper', 'hs_cos_wrapper_widget', 'hs_cos_wrapper_type_module',
    'hs_cos_wrapper_meta_field', 'hs_cos_wrapper_type_rich_text',
    'anchor', 'framework-examples',
}

# Java, as it appears in these posts: whole classes, but more often a fragment
# of a builder chain with no keyword in it at all.
_JAVA_SIGNS = (
    r'^\s*@[A-Z]\w*',                                    # annotation
    r'\b(?:public|private|protected|class|interface|enum|void|import'
    r'|package|final|static|new|var|return|throws|extends|implements)\b',
    r'^\s*\.\w+\(',                                      # chained call, own line
    r'\b\w+\.\w+\([^)]*\)\s*;',                          # statement call
    r'->\s*[{\w]',                                       # lambda
    r'\b[A-Z]\w+\.class\b',
)
# Shapes that would otherwise trip the chain and call patterns.
_NOT_JAVA = (
    r'^\s*[$#>]\s',            # shell prompt
    r'^\s*(?:curl|npm|mvn|sbt|docker|kubectl|akka|git|cd|export)\s',
    r'^\s*[{\[]\s*$',          # JSON / YAML document
    r'^\s*<\?xml|^\s*<[a-z]+>',
)


# Prose about code uses the same words as code — "in the `com.example` package",
# "Create a class named X". Punctuation is what separates them: across this
# corpus prose blocks run under 0.025 and code blocks over 0.08.
_CODE_PUNCT = ';{}()=.'
_MIN_PUNCT_DENSITY = 0.05


def looks_like_java(code):
    if any(re.search(p, code, re.M) for p in _NOT_JAVA):
        return False
    density = sum(code.count(c) for c in _CODE_PUNCT) / max(len(code), 1)
    if density < _MIN_PUNCT_DENSITY:
        return False
    return any(re.search(p, code, re.M) for p in _JAVA_SIGNS)


def label_java_blocks(html):
    """Relabel unlabelled code blocks that read as Java."""
    def relabel(m):
        opening, inner = m.group(1), m.group(2)
        if 'language-text' not in inner:
            return m.group(0)
        from html import unescape
        code = unescape(re.sub(r'<[^>]+>', '', inner))
        if not looks_like_java(code):
            return m.group(0)
        return opening + inner.replace('language-text', 'language-java', 1) + '</pre>'
    return re.sub(r'(<pre[^>]*>)(.*?)</pre>', relabel, html, flags=re.S)


# Legacy code classes to swap for Prism language-*
LEGACY_CODE_TO_LANG = {
    'prettyprint': 'text',           # generic — Prism autoloader falls through
    'marketing-code': None,          # keep code intact but drop class from <pre>
    'language-java': 'java',
    'language-text': 'text',
    'language-bash': 'bash',
    'language-scala': 'scala',
    'language-python': 'python',
    'language-yaml': 'yaml',
    'language-json': 'json',
    'language-xml': 'xml',
    'language-html': 'html',
    'language-css': 'css',
    'language-js': 'javascript',
    'language-javascript': 'javascript',
}


def sanitize(html):
    """Return normalized HTML with only whitelisted tags/attrs surviving."""
    # 0. Unescape backslash-escaped quotes: some source posts have literal
    # `class=\"language-java\"` (broken markup from a paste round-trip) that
    # browsers tolerate but attribute regex can't parse.
    html = html.replace('\\"', '"').replace("\\'", "'")
    # 0a. Extract code blocks out of HubL {% module_block %} Tabs widgets.
    # The postBody can carry HubSpot custom modules — e.g. a Java/Scala tabs
    # widget — as raw `{% module_block ... "tabs": [{"columns":["<pre>..."]}] ... %}`
    # text. These need to be either rendered by HubSpot (which requires the
    # module to be available) or unwrapped to the underlying code. Simplest:
    # extract every <pre>...</pre> found inside the module_block string and
    # emit them as bare pres — the tab UI is lost but the code survives.
    html = _extract_pres_from_hubl_modules(html)
    # 1. Strip HTML comments (some HubSpot posts have <!-- ... --> junk)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)

    # 2. Strip <colgroup> — source-editor column widths already dropped as inline styles
    html = re.sub(r'<colgroup\b.*?</colgroup>', '', html, flags=re.S)

    # 3. Convert legacy <code> language classes to canonical Prism language-*
    def rewrite_code_class(m):
        attrs = m.group(1) or ''
        cls_m = re.search(r'\bclass="([^"]*)"', attrs)
        if not cls_m:
            return m.group(0)
        classes = cls_m.group(1).split()
        new_classes = []
        lang_seen = None
        for c in classes:
            if c in LEGACY_CODE_TO_LANG:
                new_lang = LEGACY_CODE_TO_LANG[c]
                if new_lang:
                    lang_seen = new_lang
            elif c.startswith('language-'):
                lang_seen = c[len('language-'):]
            else:
                new_classes.append(c)
        if lang_seen:
            new_classes = [f'language-{lang_seen}']
        elif not new_classes:
            new_classes = ['language-text']
        new_attrs = attrs[:cls_m.start()] + f'class="{" ".join(new_classes)}"' + attrs[cls_m.end():]
        return f'<code{new_attrs}>'
    html = re.sub(r'<code(\s[^>]*)?>', rewrite_code_class, html)

    # 4. If <pre> has no inner <code>, wrap its content in <code class="language-text">
    def wrap_pre_content(m):
        inner = m.group(2)
        if re.search(r'<code\b', inner):
            return m.group(0)
        return f'{m.group(1)}<code class="language-text">{inner}</code></pre>'
    html = re.sub(r'(<pre[^>]*>)(.*?)</pre>', wrap_pre_content, html, flags=re.S)

    # 4b. A block the source left unlabelled falls to language-text, which Prism
    # renders flat. Most of them are Java — label the ones that read as Java so
    # they highlight like the blocks the source did label.
    html = label_java_blocks(html)

    # 5. Rewrite source callouts to the exemplar's pullquote design (top+
    # bottom hairlines, centered). `.enote` (thin left-rail note) is reserved
    # for hand-authored editor's notes in the local exemplar — source markup
    # that reaches for a callout shape gets the same pullquote treatment as
    # bare <blockquote>. Balanced tag replacement so the closing tag is
    # rewritten to match the new opener.
    html = _rewrite_element_by_class(html, r'note', from_tag='div', to_tag='blockquote')
    html = _rewrite_element_by_class(html, r'note', from_tag='aside', to_tag='blockquote')

    # 6. Unwrap HubSpot embed wrappers (keep contents)
    for cls in HUBSPOT_UNWRAP_DIV_CLASSES:
        # Escape for regex
        safe = re.escape(cls)
        html = _unwrap_element_by_class(html, safe, tag='div')
        html = _unwrap_element_by_class(html, safe, tag='span')
        html = _unwrap_element_by_class(html, safe, tag='section')

    # 7. Strip <span>/<font>/<u> that only wrap styling; keep their content
    html = re.sub(r'<span\b[^>]*>', '', html)
    html = re.sub(r'</span>', '', html)
    html = re.sub(r'<font\b[^>]*>', '', html)
    html = re.sub(r'</font>', '', html)

    # 8. For every tag, filter attributes against ALLOWED_ATTRS
    def rewrite_open(m):
        tag = m.group(1).lower()
        raw_attrs = m.group(2) or ''
        allowed = ALLOWED_ATTRS.get(tag)
        if allowed is None:
            return ''  # unknown tag — drop opener, keep inner content
        kept = []
        for am in re.finditer(r'(\w[\w-]*)\s*=\s*"([^"]*)"', raw_attrs):
            name = am.group(1).lower()
            val = am.group(2)
            if name not in allowed:
                continue
            if tag == 'div' and name == 'class':
                classes = [c for c in val.split() if c in KNOWN_DIV_CLASSES]
                if not classes:
                    continue
                val = ' '.join(classes)
            elif tag == 'p' and name == 'class':
                classes = [c for c in val.split() if c in KNOWN_P_CLASSES]
                if not classes:
                    continue
                val = ' '.join(classes)
            elif name == 'rel':
                keep = [r for r in val.split() if not r.startswith('data-hs-')]
                if not keep:
                    continue
                val = ' '.join(keep)
            elif tag == 'figure' and name == 'style':
                # Only keep the --fig-w custom property; strip all other inline
                # style declarations (text-align, margin, etc.)
                keep = [d.strip() for d in val.split(';') if d.strip().startswith('--fig-w')]
                if not keep:
                    continue
                val = '; '.join(keep)
            kept.append(f'{name}="{val}"')
        for name in re.findall(r'\b(allowfullscreen|autoplay)\b(?!\s*=)', raw_attrs):
            if name in allowed:
                kept.append(name)
        attrs_str = (' ' + ' '.join(kept)) if kept else ''
        return f'<{tag}{attrs_str}>'

    def rewrite_close(m):
        tag = m.group(1).lower()
        if tag not in ALLOWED_ATTRS:
            return ''
        return f'</{tag}>'

    # Opening tags
    html = re.sub(r'<([a-zA-Z][a-zA-Z0-9]*)((?:\s[^>]*)?)>', rewrite_open, html)
    # Closing tags
    html = re.sub(r'</([a-zA-Z][a-zA-Z0-9]*)\s*>', rewrite_close, html)

    # 9. Wrap bare <iframe> in a figure so it respects the wide breakout and
    # gets a plot-wrap container (matches images). Source posts often embed
    # YouTube via bare iframe which otherwise overflows the body column.
    def wrap_iframe(m):
        iframe = m.group(0)
        return (
            '\n<figure class="viz">\n'
            '  <div class="plot-wrap">\n'
            f'    <div class="plate plate--flush">{iframe}</div>\n'
            '  </div>\n'
            '</figure>\n'
        )
    html = re.sub(r'<iframe\b[^>]*>.*?</iframe>', wrap_iframe, html, flags=re.S)

    # 10. Collapse whitespace-only runs
    html = re.sub(r'[ \t]+\n', '\n', html)
    html = re.sub(r'\n{4,}', '\n\n\n', html)

    return html


def _extract_pres_from_hubl_modules(html):
    """Find every `{% module_block %}...{% end_module_block %}` block in the
    source. For each block, extract what content we can recover:
      - <pre> code blocks (a Tabs widget carrying code samples)
      - "content" fields (FAQ modules — each entry becomes a paragraph)
      - "question"/"answer" fields (alternate FAQ shape)
    Anything else is discarded. Never leaves literal HubL text in the output.
    """
    def _unescape(s):
        return s.replace('\\n', '\n').replace('\\"', '"').replace('\\/', '/')

    def replace_block(m):
        block = m.group(0)
        pres = re.findall(r'<pre[^>]*>.*?</pre>', block, flags=re.S)
        if pres:
            labels = re.findall(r'"tab_label"\s*:\s*"([^"]+)"', block)
            parts = []
            for i, pre in enumerate(pres):
                # The pre content came from inside a JSON string in the HubL
                # module — unescape \n and \t back to real characters so the
                # source code renders on multiple lines.
                pre_clean = pre.replace('\\n', '\n').replace('\\t', '\t')
                if i < len(labels) and labels[i]:
                    parts.append(f'<p><strong>{labels[i]}</strong></p>')
                parts.append(pre_clean)
            return '\n'.join(parts)
        # FAQ module: harvest "title" / "content" pairs
        faqs = re.findall(r'"title"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"([^"]*)"', block)
        if faqs:
            parts = []
            for t, c in faqs:
                parts.append(f'<p><strong>{_unescape(t)}</strong></p>')
                parts.append(f'<p>{_unescape(c)}</p>')
            return '\n'.join(parts)
        # Otherwise drop the block entirely
        return ''
    return re.sub(
        r'\{%\s*module_block\b.*?\{%\s*end_module_block\s*%\}',
        replace_block, html, flags=re.S,
    )


def _rewrite_element_by_class(html, class_re, from_tag='div', to_tag='blockquote'):
    """Balanced-tag replacement: `<from_tag ... class="...class_re...">...</from_tag>`
    becomes `<to_tag>...</to_tag>`. Only the outer open/close are rewritten;
    inner content is preserved verbatim."""
    out = []
    i = 0
    open_re = re.compile(rf'<{from_tag}\b[^>]*class="[^"]*{class_re}[^"]*"[^>]*>', re.I)
    open_any = re.compile(rf'<{from_tag}\b[^>]*>', re.I)
    close_any = re.compile(rf'</{from_tag}\s*>', re.I)
    while True:
        m = open_re.search(html, i)
        if not m:
            out.append(html[i:])
            break
        out.append(html[i:m.start()])
        depth = 1
        j = m.end()
        while j < len(html) and depth > 0:
            no = open_any.search(html, j)
            nc = close_any.search(html, j)
            if not nc:
                out.append(f'<{to_tag}>')
                out.append(html[j:])
                return ''.join(out)
            if no and no.start() < nc.start():
                depth += 1
                j = no.end()
            else:
                depth -= 1
                if depth == 0:
                    out.append(f'<{to_tag}>')
                    out.append(html[j:nc.start()])
                    out.append(f'</{to_tag}>')
                    i = nc.end()
                    break
                j = nc.end()
    return ''.join(out)


def _unwrap_element_by_class(html, class_re, tag='div'):
    """Balanced unwrap: <tag class="...class_re..."> ... </tag> → just the ... ."""
    out = []
    i = 0
    open_re = re.compile(rf'<{tag}\b[^>]*class="[^"]*{class_re}[^"]*"[^>]*>', re.I)
    while True:
        m = open_re.search(html, i)
        if not m:
            out.append(html[i:])
            break
        out.append(html[i:m.start()])
        # Balanced closing scan
        depth = 1
        j = m.end()
        open2 = re.compile(rf'<{tag}\b[^>]*>', re.I)
        close2 = re.compile(rf'</{tag}\s*>', re.I)
        while j < len(html) and depth > 0:
            no = open2.search(html, j)
            nc = close2.search(html, j)
            if not nc:
                out.append(html[m.end():])
                return ''.join(out)
            if no and no.start() < nc.start():
                depth += 1
                j = no.end()
            else:
                depth -= 1
                if depth == 0:
                    out.append(html[m.end():nc.start()])
                    i = nc.end()
                    break
                j = nc.end()
    return ''.join(out)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('usage: html_sanitizer.py <file.html>')
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        raw = f.read()
    print(sanitize(raw))
