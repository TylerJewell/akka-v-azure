#!/usr/bin/env python3
"""Deploy the blog post template and its stylesheet to HubSpot.

The stylesheet is generated, not stored: theme/base.css is the source, scoped to
.blog-technical the same way port.py scopes it for a preview, so a preview and a
migrated post render from one set of values.

    python tools/blog-technical/deploy_template.py

Note the blog's template is a property of the BLOG, not of a post
(BLOG_POST_TEMPLATE_PATH_NOT_SETTABLE). Uploading here changes nothing on its
own — a blog has to be pointed at the template:

    PUT /content/api/v2/blogs/<id> {"item_template_path": TEMPLATE_PATH}

Staging blog 185742639222 already points here. The live blog (162235293071)
still renders AKKA-2024/templates/blog-post.html.
"""

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import port  # noqa: E402

ROOT = port.ROOT
TEMPLATE_SRC = os.path.join(ROOT, 'blog-technical', 'hubspot', 'blog-post-technical.html')
THEME_SRC = os.path.join(ROOT, 'blog-technical', 'posts',
                         'akka-memory-durable-in-memory-and-sharded-data.html')
BUILD = os.path.join(ROOT, 'scratchpad', 'hs-out')

TEMPLATE_PATH = 'AKKA-2024/templates/blog-post-technical.html'
CSS_PATH = 'AKKA-2024/css/blog-technical.css'


def build_css():
    """Scope theme/base.css to .blog-technical, via a post that links it."""
    src = port.read(THEME_SRC)
    scoped = port.scope_css(port.collect_css(src, os.path.dirname(THEME_SRC)), 'blog-technical')
    out = os.path.join(BUILD, 'blog-technical.css')
    port.write(out, scoped)
    return out, len(scoped)


def main():
    token = port.get_token()
    css_file, size = build_css()
    print(f'built {CSS_PATH} ({size} bytes)')
    for path, local in ((CSS_PATH, css_file), (TEMPLATE_PATH, TEMPLATE_SRC)):
        for env in ('draft', 'published'):
            code = port.curl_put_source(env, urllib.parse.quote(path), local, token)
            print(f'  PUT {env:<9} {path}  HTTP {code}')
    # The asset URL is content-hashed, so a re-upload publishes at a new URL and
    # pages pick it up on their next render.
    print('done — pages serve the new stylesheet on next render')


if __name__ == '__main__':
    main()
