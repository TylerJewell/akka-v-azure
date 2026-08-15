#!/usr/bin/env python3
"""Migrate a blog-technical post onto the real /blog/<slug> URL.

Different from port.py in what it ships. A preview page draws no chrome of its
own, so it takes the whole standalone document — kicker, title, standfirst,
byline and body. The blog template already renders a header from the post's own
HubSpot fields, so a migrated post ships the body ALONE; shipping the document
would print every heading twice.

The theme is a stylesheet on the template, not a copy in each post body — the
same reason posts link theme/base.css rather than carrying it.

    python tools/blog-technical/migrate.py <slug> --dry-run   # show what would ship
    python tools/blog-technical/migrate.py <slug>             # PATCH + push live
    python tools/blog-technical/migrate.py <slug> --revert    # restore the snapshot

Every run snapshots the live postBody to scratchpad/blog-snapshots/<slug>.html
before writing, so --revert can put it back exactly.
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import port  # noqa: E402  — shares read/write, token, and the CSS helpers

ROOT = port.ROOT
SNAPSHOTS = os.path.join(ROOT, 'scratchpad', 'blog-snapshots')
CSS_PATH = 'AKKA-2024/css/blog-technical.css'
TEMPLATE_PATH = 'AKKA-2024/templates/blog-post-technical.html'


def post_source(slug):
    p = os.path.join(ROOT, 'blog-technical', 'posts', f'{slug}.html')
    if not os.path.exists(p):
        p = os.path.join(ROOT, 'blog-technical', f'{slug}.html')
    if not os.path.exists(p):
        sys.exit(f'no converted post for {slug}')
    return port.read(p)


def body_only(src):
    """The article's content, without the header the blog template renders.

    Keeps every .body / .wide / .table-scroll block and drops .hero, .colophon,
    .foot and .progress — the standalone document's own chrome.
    """
    m = re.search(r'<article[^>]*>([\s\S]*?)</article>', src)
    inner = m.group(1) if m else re.search(r'<body[^>]*>([\s\S]*?)</body>', src).group(1)
    for pat in (r'<header class="hero[^"]*">[\s\S]*?</header>',
                r'<div class="colophon">[\s\S]*?</div>',
                r'<div class="foot">[\s\S]*?</div>',
                r'<div class="progress"[^>]*></div>'):
        inner = re.sub(pat, '', inner)
    inner = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', inner)
    # A .col wrapper that the header left behind holds nothing now.
    inner = re.sub(r'<div class="(?:body )?col">\s*</div>', '', inner)
    return inner.strip()


def api(method, path, body=None, token=None):
    args = ['curl', '-s', '-X', method, '-H', f'Authorization: Bearer {token}']
    if body is not None:
        args += ['-H', 'Content-Type: application/json; charset=utf-8',
                 '--data-binary', '@-']
    args.append('https://api.hubapi.com' + path)
    r = subprocess.run(args, input=json.dumps(body).encode('utf-8') if body else None,
                       capture_output=True)
    out = r.stdout.decode('utf-8', 'strict') if r.stdout else ''
    return json.loads(out) if out.strip().startswith('{') else out


def find_post(slug, token):
    after = None
    while True:
        q = '/cms/v3/blogs/posts?limit=100' + (f'&after={after}' if after else '')
        page = api('GET', q, token=token)
        for p in page.get('results', []):
            if p.get('slug') in (f'blog/{slug}', slug):
                return p
        after = (page.get('paging') or {}).get('next', {}).get('after')
        if not after:
            return None


def snapshot(slug, post):
    os.makedirs(SNAPSHOTS, exist_ok=True)
    path = os.path.join(SNAPSHOTS, f'{slug}.json')
    if os.path.exists(path):
        return path  # never overwrite the pre-migration state
    port.write(path, json.dumps({'id': post['id'],
                                 'postBody': post.get('postBody', ''),
                                 'templatePath': post.get('templatePath', '')},
                                ensure_ascii=False))
    return path


STAGING_BLOG = '185742639222'
# The staging blog refuses to publish a post without one; most posts have none.
STAGING_IMAGE = ('https://45500578.fs1.hubspotusercontent-na1.net/hubfs/45500578'
                 '/website/social-share-images/akka-1200-628.jpg')


def stage(slug, token):
    """Publish the converted post into the staging blog, leaving the live one alone.

    A post's template is a property of its blog, not of the post, so there is no
    way to preview one post on the new template in place — the staging blog is
    the only isolated copy of that setting.
    """
    live = find_post(slug, token)
    if not live:
        sys.exit(f'no live blog post at blog/{slug}')
    payload = {
        'contentGroupId': STAGING_BLOG,
        'name': live['name'],
        'slug': f'akka-blog-staging/{slug}',
        'postBody': body_only(post_source(slug)),
        'state': 'PUBLISHED',
        'blogAuthorId': live.get('blogAuthorId'),
        'publishDate': live.get('publishDate'),
        'metaDescription': live.get('metaDescription', ''),
        'tagIds': live.get('tagIds') or [],
        'featuredImage': live.get('featuredImage') or STAGING_IMAGE,
        'featuredImageAltText': live.get('featuredImageAltText') or 'Akka',
        'useFeaturedImage': True,
        'widgets': live.get('widgets', {}),
    }
    existing = None
    page = api('GET', f'/cms/v3/blogs/posts?limit=100&contentGroupId={STAGING_BLOG}', token=token)
    for p in page.get('results', []):
        if p.get('slug') == payload['slug']:
            existing = p['id']

    if existing:
        api('PATCH', f'/cms/v3/blogs/posts/{existing}', payload, token)
        pid = existing
    else:
        pid = api('POST', '/cms/v3/blogs/posts', payload, token).get('id')
    api('POST', f'/cms/v3/blogs/posts/{pid}/draft/push-live', {}, token)
    print(f'  staged  https://akka.io/{payload["slug"]}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slug', nargs='+')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--revert', action='store_true')
    ap.add_argument('--staging', action='store_true',
                    help='copy into the staging blog instead of touching the live post')
    args = ap.parse_args()

    if args.staging:
        token = port.get_token()
        for slug in args.slug:
            stage(slug, token)
        return
    if len(args.slug) > 1:
        sys.exit('one slug at a time unless --staging')
    args.slug = args.slug[0]

    token = port.get_token()
    post = find_post(args.slug, token)
    if not post:
        sys.exit(f'no live blog post at blog/{args.slug}')
    pid = post['id']

    if args.revert:
        snap = json.loads(port.read(os.path.join(SNAPSHOTS, f'{args.slug}.json')))
        api('PATCH', f'/cms/v3/blogs/posts/{pid}',
            {'postBody': snap['postBody'], 'templatePath': snap['templatePath']}, token)
        api('POST', f'/cms/v3/blogs/posts/{pid}/draft/push-live', {}, token)
        print(f'reverted {args.slug} to the snapshot')
        return

    body = body_only(post_source(args.slug))
    print(f'=== {args.slug} → blog/{args.slug} (id {pid}) ===')
    print('  body bytes:  ', len(body))
    print('  template:    ', post.get('templatePath'), '->', TEMPLATE_PATH)
    if args.dry_run:
        print('  dry run — nothing written')
        return

    print('  snapshot:    ', snapshot(args.slug, post))
    api('PATCH', f'/cms/v3/blogs/posts/{pid}',
        {'postBody': body, 'templatePath': TEMPLATE_PATH}, token)
    api('POST', f'/cms/v3/blogs/posts/{pid}/draft/push-live', {}, token)
    print(f'  published:    https://akka.io/blog/{args.slug}')


if __name__ == '__main__':
    main()
