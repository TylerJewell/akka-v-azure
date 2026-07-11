#!/usr/bin/env python3
"""
Turn a standalone Akka HTML page into a HubSpot-ready import fragment.

Our pages are authored as full documents (GitHub Pages). Pasted into HubSpot
they sit *inside* HubSpot's own page (header/nav/footer), so three things have
to change before Darin can drop them in without hand-editing:

  1. Global CSS is scoped under a wrapper so our reset / html / body rules
     can't leak onto HubSpot's chrome (see scope_css).
  2. Relative image paths (images/...) become absolute HubSpot CDN URLs.
  3. Relative external stylesheets are inlined and the <html>/<head>/<body>
     wrapper is stripped, leaving a paste-ready fragment.

Public entry point: to_hubspot_fragment(html, base_dir, image_base, ...).
"""

import os, re

DEFAULT_SCOPE = 'akka-embed'


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# ── CSS scoping ────────────────────────────────────────────────────────────
# We prefix EVERY selector with the wrapper class so nothing our stylesheet
# declares can match HubSpot's surrounding markup (and vice-versa). Root-ish
# selectors (html/body/:root) are *replaced* by the wrapper rather than
# prefixed, since ".wrapper html" would never match anything.

def _split_commas(sel):
    """Split a selector list on top-level commas (ignoring parens/strings)."""
    parts, buf, depth, i, n = [], '', 0, 0, len(sel)
    while i < n:
        c = sel[i]
        if c in '"\'':
            q = c; buf += c; i += 1
            while i < n and sel[i] != q:
                if sel[i] == '\\' and i + 1 < n:
                    buf += sel[i:i+2]; i += 2; continue
                buf += sel[i]; i += 1
            if i < n:
                buf += sel[i]
            i += 1; continue
        if c in '([':
            depth += 1
        elif c in ')]':
            depth -= 1
        if c == ',' and depth == 0:
            parts.append(buf); buf = ''
        else:
            buf += c
        i += 1
    parts.append(buf)
    return parts


def _scope_one(sel, scope):
    sel = sel.strip()
    if not sel:
        return ''
    m = re.match(r'^(:root|html|body)\b', sel)
    if m:                                   # root-ish: replace the leading token
        return scope + sel[m.end():]
    return scope + ' ' + sel                # everything else: prefix


def _scope_selector_list(sel, scope):
    return ', '.join(p for p in (_scope_one(s, scope) for s in _split_commas(sel)) if p)


def _strip_comments(css):
    """Remove /* ... */ comments, but not ones inside strings."""
    out, i, n = [], 0, len(css)
    while i < n:
        c = css[i]
        if c == '/' and i + 1 < n and css[i+1] == '*':
            end = css.find('*/', i + 2)
            i = n if end == -1 else end + 2
            continue
        if c in '"\'':
            q = c; out.append(c); i += 1
            while i < n and css[i] != q:
                if css[i] == '\\' and i + 1 < n:
                    out.append(css[i:i+2]); i += 2; continue
                out.append(css[i]); i += 1
            if i < n:
                out.append(css[i]); i += 1
            continue
        out.append(c); i += 1
    return ''.join(out)


def _scan_rules(css):
    """Yield (prelude, block, has_block) top-level items, comment/string-aware."""
    items, i, n, start = [], 0, len(css), 0
    while i < n:
        c = css[i]
        if c == '/' and i + 1 < n and css[i+1] == '*':          # comment
            end = css.find('*/', i + 2)
            i = n if end == -1 else end + 2
            continue
        if c in '"\'':                                          # string
            q = c; i += 1
            while i < n and css[i] != q:
                i += 2 if css[i] == '\\' else 1
            i += 1; continue
        if c == ';' and _depth_zero(css, start, i):             # bare @statement
            stmt = css[start:i+1].strip()
            if stmt:
                items.append((stmt, None, False))
            start = i + 1; i += 1; continue
        if c == '{':
            prelude = css[start:i]
            depth, j = 1, i + 1
            while j < n and depth > 0:
                cj = css[j]
                if cj == '/' and j + 1 < n and css[j+1] == '*':
                    end = css.find('*/', j + 2); j = n if end == -1 else end + 2; continue
                if cj in '"\'':
                    q = cj; j += 1
                    while j < n and css[j] != q:
                        j += 2 if css[j] == '\\' else 1
                    j += 1; continue
                if cj == '{':
                    depth += 1
                elif cj == '}':
                    depth -= 1
                j += 1
            items.append((prelude, css[i+1:j-1], True))
            i = start = j
            continue
        i += 1
    return items


def _depth_zero(css, a, b):
    """True if the slice css[a:b] is balanced w.r.t. braces (top-level ;)."""
    return css.count('{', a, b) == css.count('}', a, b)


_NESTED_AT = ('media', 'supports', 'container', 'layer', 'scope')


def scope_css(css, scope):
    """Prefix every selector in `css` with `scope` (e.g. '.akka-embed')."""
    out = []
    for prelude, block, has_block in _scan_rules(_strip_comments(css)):
        p = prelude.strip()
        if not p and block is None:
            continue
        if p.startswith('@'):
            name = re.split(r'[\s(]', p[1:], 1)[0].lower()
            if not has_block:
                out.append(p + ';')                             # @import / @charset
            elif name in _NESTED_AT:
                out.append('%s {\n%s\n}' % (p, scope_css(block, scope)))
            else:
                out.append('%s {%s}' % (p, block))              # @keyframes/@font-face verbatim
        elif has_block:
            out.append('%s { %s }' % (_scope_selector_list(p, scope), block.strip()))
    return '\n'.join(out)


# ── fragment assembly ───────────────────────────────────────────────────────

def _rewrite_images(text, image_base):
    if not image_base:
        return text
    base = image_base.rstrip('/') + '/'
    text = re.sub(r"""(url\(\s*['"]?)images/""", r'\g<1>' + base + 'images/', text)
    text = re.sub(r"""((?:src|href)\s*=\s*['"])images/""", r'\g<1>' + base + 'images/', text)
    return text


def to_hubspot_fragment(html, base_dir='.', image_base=None,
                        scope=DEFAULT_SCOPE, label=''):
    """Return a paste-ready HubSpot fragment for a standalone HTML document."""
    head_m = re.search(r'<head[^>]*>(.*?)</head>', html, re.S | re.I)
    head = head_m.group(1) if head_m else ''
    body_m = re.search(r'<body[^>]*>(.*?)</body>', html, re.S | re.I)
    body = body_m.group(1) if body_m else html

    # External stylesheet <link>s: keep absolute (fonts), inline relative ones.
    styles, keep_links = [], []
    for link in re.findall(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', head, re.I):
        href = re.search(r'href=["\']([^"\']+)["\']', link, re.I)
        if href and not re.match(r'https?:', href.group(1)):
            css_path = os.path.join(base_dir, href.group(1))
            if os.path.exists(css_path):
                styles.append(read(css_path))
        else:
            keep_links.append(link)

    # Inline <style> from head + body (then strip them out of the body).
    styles = re.findall(r'<style[^>]*>(.*?)</style>', head + body, re.S | re.I) + styles
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.S | re.I)

    css = _rewrite_images('\n'.join(styles), image_base)
    body = _rewrite_images(body, image_base)
    scoped = scope_css(css, '.' + scope)

    head_scripts = re.findall(r'<script\b[^>]*>.*?</script>', head, re.S | re.I)

    parts = [
        '<!-- Akka %s — HubSpot import fragment. Auto-generated by the build; '
        'do not edit by hand. -->' % (label or 'page'),
        *keep_links,
        '<style>',
        scoped,
        '</style>',
        *head_scripts,
        '<div class="%s">' % scope,
        body.strip(),
        '</div>',
    ]
    return '\n'.join(parts) + '\n'
