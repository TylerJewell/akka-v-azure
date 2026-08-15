#!/usr/bin/env python3
"""Publish a blog-technical post to HubSpot as a preview page.

Mirrors scratchpad/port_capabilities.py — extracts the inline <style> and body
content from blog-technical/<slug>.html, scopes the CSS to a .blog-technical
wrapper, and pushes one body partial. Creates or updates the HubSpot wrapper
template + CMS page.

Usage:
    python tools/blog-technical/port.py <slug>          # publish/update
    python tools/blog-technical/port.py <slug> --preview blog-preview

<slug> is the filename in blog-technical/ minus .html. Trailing --preview <path>
sets the URL slug on akka.io (default: blog-preview/<slug>).
"""

import argparse
import io
import os
import re
import subprocess
import sys
import urllib.request

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HUBL_HEADER = '<!--\n  templateType: "none"\n  isAvailableForNewContent: false\n-->\n'
# Lean wrapper: loads only what the site header/footer need (Font Awesome +
# fonts + Prism). Skips HubSpot's four theme stylesheets, whose global rules
# on table/blockquote/list defaults were overriding our scoped CSS and forcing
# us into !important battles.
WRAPPER_PATH = 'custom-templates/akka-blog-technical-wrapper-lean.html'

WRAPPER_TEMPLATE = '''<!--
    templateType: page
    isAvailableForNewContent: true
    label: Akka Blog Technical (Lean)
-->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    {% if content.html_title %}<title>{{ content.html_title }}</title>{% endif %}
    <meta name="description" content="{{ content.meta_description }}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- A preview is a second copy of a post that is already published at
         /blog/<slug>. It self-canonicalises and robots.txt does not cover the
         path, so without this it competes with the post it previews. -->
    <meta name="robots" content="noindex,nofollow">
    <link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    {{ standard_header_includes }}
  </head>
  <body>
    {% global_partial path="AKKA-2024/templates/partials/header-april.html" %}

    <div class="blog-technical">
      {{ content.widgets.rich_text.body.html }}
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <script>
      if (window.Prism && Prism.plugins && Prism.plugins.autoloader) {
        Prism.plugins.autoloader.languages_path =
          'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/';
      }
      if (window.Prism) { Prism.highlightAll(); }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    {% global_partial path="AKKA-2024/templates/partials/footer.html" %}
    {{ standard_footer_includes }}
  </body>
</html>
'''


def read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def write(p, content):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)


def get_token():
    tok = os.environ.get('HUBSPOT_TOKEN', '')
    if tok:
        return tok
    env_txt = read(os.path.join(ROOT, 'scratchpad', '.hs_env'))
    m = re.search(r'HUBSPOT_TOKEN=(\S+)', env_txt)
    if not m:
        sys.exit('HUBSPOT_TOKEN not found in scratchpad/.hs_env')
    return m.group(1)


def curl_put_source(env, path, local_file, token):
    url = f'https://api.hubapi.com/cms/v3/source-code/{env}/content/{path}'
    r = subprocess.run(
        ['curl', '-s', '-w', '%{http_code}', '-X', 'PUT',
         '-H', f'Authorization: Bearer {token}',
         '-F', f'file=@{local_file}', url],
        capture_output=True, text=True,
    )
    body = r.stdout
    return body[-3:] if body else '???'


def _scope_selector_list(sel, scope):
    parts = [p.strip() for p in sel.split(',') if p.strip()]
    scoped = []
    for p in parts:
        if p == '*':
            scoped.append(f'.{scope} *')
        elif p.startswith('html') or p.startswith('body'):
            scoped.append(re.sub(r'^(html|body)', f'.{scope}', p))
        elif p.startswith(':root'):
            scoped.append(re.sub(r'^:root', f'.{scope}', p))
        else:
            scoped.append(f'.{scope} {p}')
    return ', '.join(scoped)


def _strip_comments(css):
    """Drop /* ... */ comments, leaving ones inside strings alone.

    The rule walker in scope_css reads everything up to the next '{' as the
    selector. A comment sitting above a rule is part of that span, so it lands
    inside the selector and the whole rule stops matching. Comments carry no
    runtime meaning, so they come out before the walk.
    """
    out, i, n = [], 0, len(css)
    while i < n:
        c = css[i]
        if c == '/' and i + 1 < n and css[i + 1] == '*':
            end = css.find('*/', i + 2)
            i = n if end == -1 else end + 2
            continue
        if c in '"\'':
            q = c
            out.append(c)
            i += 1
            while i < n and css[i] != q:
                if css[i] == '\\' and i + 1 < n:
                    out.append(css[i:i + 2])
                    i += 2
                    continue
                out.append(css[i])
                i += 1
            if i < n:
                out.append(css[i])
                i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def document_reset(scoped_css):
    """A reset for the real document, which the scoping cannot reach.

    scope_css rewrites `body{...}` and `*{margin:0}` to `.blog-technical ...`,
    so the page's own body keeps the browser default 8px margin and no
    background — an 8px white frame around a dark page. The colour is read back
    out of the scoped CSS rather than written here, so it stays one value.
    """
    paper = re.search(r'--paper:\s*([^;}]+)', scoped_css)
    paper = paper.group(1).strip() if paper else '#141414'
    return 'html,body{margin:0;padding:0;background:%s}\n' % paper


def scope_css(css, scope):
    """Recursively scope every top-level selector with .<scope>.

    Handles nested at-rules correctly:
      - @media / @supports preludes are preserved; their inner rules are
        recursively scoped.
      - @keyframes / @font-face / @property blocks pass through unchanged
        (their inner "selectors" are keyframe positions / descriptor names,
        not real selectors).
      - Regular rules get their selector list prefixed with .<scope>.

    Comments are removed first; see _strip_comments.
    """
    css = _strip_comments(css)
    result = []
    i = 0
    n = len(css)
    while i < n:
        # skip whitespace between rules
        while i < n and css[i] in ' \n\r\t':
            result.append(css[i])
            i += 1
        if i >= n:
            break
        start = i
        # walk to the next '{' or ';' at THIS depth
        while i < n and css[i] not in '{;':
            i += 1
        if i >= n:
            result.append(css[start:i])
            break
        if css[i] == ';':
            # at-statement (e.g. @import, @charset)
            result.append(css[start:i + 1])
            i += 1
            continue
        # we hit '{' — this opens a block
        sel = css[start:i].strip()
        i += 1  # past '{'
        block_start = i
        depth = 1
        while i < n and depth > 0:
            if css[i] == '{':
                depth += 1
            elif css[i] == '}':
                depth -= 1
            i += 1
        block = css[block_start:i - 1]  # inside the braces
        if sel.startswith('@keyframes') or sel.startswith('@font-face') or sel.startswith('@property'):
            result.append(sel + '{' + block + '}')
        elif sel.startswith('@media') or sel.startswith('@supports') or sel.startswith('@container'):
            result.append(sel + '{' + scope_css(block, scope) + '}')
        else:
            result.append(_scope_selector_list(sel, scope) + '{' + block + '}')
    return ''.join(result)


_HEAD_CSS = re.compile(
    r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*>|<style[^>]*>(.*?)</style>',
    re.S | re.I)

# The theme's variable block. Its presence in an inline <style> means the post
# holds a copy of the theme rather than a link to it.
_THEME_COPY = re.compile(r':root\s*\{[^}]*--paper\s*:', re.S)


def collect_css(src, base_dir):
    """Return the post's CSS: linked local stylesheets and inline <style>, in
    document order.

    A post links theme/base.css and, for the light variant, theme/light.css
    after it. Order decides which value wins, so the two are concatenated in the
    order the document lists them. Absolute hrefs are the CDN stylesheets the
    HubSpot wrapper already loads and are skipped.
    """
    parts = []
    for m in _HEAD_CSS.finditer(src):
        if m.group(1) is not None:
            if _THEME_COPY.search(m.group(1)):
                sys.exit('post carries its own copy of the theme: replace the <style> block '
                         'with <link rel="stylesheet" href="../theme/base.css">. A copy stops '
                         'tracking theme/base.css and drifts from the pages that link it.')
            parts.append(m.group(1))
            continue
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0), re.I)
        if not href or re.match(r'https?:|//', href.group(1)):
            continue
        path = os.path.normpath(os.path.join(base_dir, href.group(1)))
        if not os.path.exists(path):
            sys.exit(f'stylesheet not found: {path}')
        parts.append(read(path))
    return '\n'.join(parts)


def build_body(slug):
    # Prefer blog-technical/posts/<slug>.html (scaffolded from live URL) before
    # blog-technical/<slug>.html (hand-authored template render)
    candidate = os.path.join(ROOT, 'blog-technical', 'posts', f'{slug}.html')
    if not os.path.exists(candidate):
        candidate = os.path.join(ROOT, 'blog-technical', f'{slug}.html')
    src = read(candidate)
    css = collect_css(src, os.path.dirname(candidate))
    body_m = re.search(r'<body[^>]*>(.*?)</body>', src, re.S)
    body = body_m.group(1).strip() if body_m else src
    # Strip elements that only make sense in the standalone preview and
    # duplicate the HubSpot site chrome or JavaScript already loaded by the
    # wrapper template:
    #   .colophon — my own top strip (redundant against site header)
    #   .foot     — my own bottom stamp (redundant against site footer)
    #   .progress — scroll bar (script is loaded from wrapper, not needed here)
    body = re.sub(r'<div class="colophon">.*?</div>\s*', '', body, flags=re.S)
    body = re.sub(r'<div class="foot">.*?</div>\s*', '', body, flags=re.S)
    body = re.sub(r'<div class="progress"[^>]*></div>\s*', '', body, flags=re.S)
    # Strip <script> tags — Prism is loaded from the wrapper
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.S)
    scope = 'blog-technical'
    scoped_css = scope_css(css, scope)
    out = (
        HUBL_HEADER
        + '<style>\n' + document_reset(scoped_css) + scoped_css.strip() + '\n</style>\n'
        + body + '\n'
    )
    out_path = os.path.join(ROOT, 'scratchpad', 'hs-out', f'blog-technical-{slug}.html')
    write(out_path, out)
    return out_path


def upload_wrapper(token):
    """Upload the Akka Blog Technical wrapper template if not present."""
    local = os.path.join(ROOT, 'scratchpad', 'hs-out', 'akka-blog-technical-wrapper.html')
    write(local, WRAPPER_TEMPLATE)
    for env in ('draft', 'published'):
        code = curl_put_source(env, WRAPPER_PATH, local, token)
        print(f'  PUT {env:<9}  {WRAPPER_PATH}  HTTP {code}')


def upload_body_partial(slug, body_path, token):
    """Upload the body content as a HubSpot partial the wrapper includes."""
    partial_path = f'custom-templates/partials/blog-technical-{slug}.html'
    for env in ('draft', 'published'):
        code = curl_put_source(env, partial_path, body_path, token)
        print(f'  PUT {env:<9}  {partial_path}  HTTP {code}')
    return partial_path


def push_live(page_id, token):
    """Re-render the page.

    The body partial is source code, and published source code is live at once —
    but a page that already includes the partial keeps serving its cached render
    until it is pushed. Without this a re-port reports success and shows the old
    page. Returns HTTP 204 with an empty body.
    """
    subprocess.run(
        ['curl', '-s', '-X', 'POST', '-H', f'Authorization: Bearer {token}',
         f'https://api.hubapi.com/cms/v3/pages/site-pages/{page_id}/draft/push-live'],
        capture_output=True,
    )
    print(f'  PUSH-LIVE id={page_id}')


def create_or_update_page(slug, page_slug, html_title, meta_description, partial_path, token):
    """Create a CMS page or update an existing one at the given slug."""
    # Look up existing page by slug
    lookup = subprocess.run(
        ['curl', '-s', '-H', f'Authorization: Bearer {token}',
         f'https://api.hubapi.com/cms/v3/pages/site-pages?slug={page_slug}'],
        capture_output=True, text=True,
    )
    import json
    data = json.loads(lookup.stdout) if lookup.stdout else {}
    results = data.get('results', [])

    payload = {
        'name': html_title,
        'slug': page_slug,
        'htmlTitle': html_title,
        'metaDescription': meta_description,
        'templatePath': WRAPPER_PATH,
        'subcategory': 'site_page',
        'state': 'PUBLISHED',
        'contentTypeCategory': 4,
        'useFeaturedImage': False,
        'publicAccessRulesEnabled': False,
        'widgets': {
            'rich_text': {
                'body': {
                    'html': f'{{% include "{partial_path}" %}}'
                }
            }
        }
    }
    payload_bytes = json.dumps(payload).encode('utf-8')

    if results:
        page_id = results[0]['id']
        r = subprocess.run(
            ['curl', '-s', '-X', 'PATCH',
             '-H', f'Authorization: Bearer {token}',
             '-H', 'Content-Type: application/json; charset=utf-8',
             '--data-binary', '@-',
             f'https://api.hubapi.com/cms/v3/pages/site-pages/{page_id}'],
            input=payload_bytes, capture_output=True,
        )
        resp = json.loads(r.stdout) if r.stdout else {}
        print(f'  PATCH page id={page_id}  slug={resp.get("slug","?")}  state={resp.get("state","?")}')
        push_live(page_id, token)
        return resp.get('url', '?')
    else:
        r = subprocess.run(
            ['curl', '-s', '-X', 'POST',
             '-H', f'Authorization: Bearer {token}',
             '-H', 'Content-Type: application/json; charset=utf-8',
             '--data-binary', '@-',
             'https://api.hubapi.com/cms/v3/pages/site-pages'],
            input=payload_bytes, capture_output=True,
        )
        resp = json.loads(r.stdout) if r.stdout else {}
        print(f'  CREATE  id={resp.get("id","?")}  slug={resp.get("slug","?")}  state={resp.get("state","?")}')
        return resp.get('url', '?')


def extract_metadata(slug):
    candidate = os.path.join(ROOT, 'blog-technical', 'posts', f'{slug}.html')
    if not os.path.exists(candidate):
        candidate = os.path.join(ROOT, 'blog-technical', f'{slug}.html')
    src = read(candidate)
    title_m = re.search(r'<title>(.*?)</title>', src)
    title = title_m.group(1).replace(' — Akka', '').strip() if title_m else slug
    stand_m = re.search(r'<p class="standfirst"[^>]*>(.*?)</p>', src, re.S)
    if stand_m:
        desc = re.sub(r'<[^>]+>', ' ', stand_m.group(1))
        desc = re.sub(r'\s+', ' ', desc).strip()[:200]
    else:
        desc = title
    return title, desc


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slug', help='blog-technical/<slug>.html basename')
    ap.add_argument('--preview', default=None,
                    help='CMS URL slug (default: blog-preview/<slug>)')
    args = ap.parse_args()

    token = get_token()
    page_slug = args.preview or f'blog-preview/{args.slug}'
    title, desc = extract_metadata(args.slug)

    print(f'=== Publishing {args.slug} → /{page_slug} ===')
    print('  Title:', title)
    print('  Desc: ', desc[:80], '...' if len(desc) > 80 else '')

    print('\n[1/3] Upload wrapper template')
    upload_wrapper(token)

    print('\n[2/3] Build + upload body partial')
    body_path = build_body(args.slug)
    partial_path = upload_body_partial(args.slug, body_path, token)

    print('\n[3/3] Create/update CMS page')
    # ASCII-only for API safety
    title_ascii = title.encode('ascii', 'ignore').decode('ascii')
    desc_ascii = desc.encode('ascii', 'ignore').decode('ascii')
    url = create_or_update_page(args.slug, page_slug, title_ascii, desc_ascii, partial_path, token)

    print(f'\n=== Published: {url} ===')


if __name__ == '__main__':
    main()
