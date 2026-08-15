#!/usr/bin/env python3
"""Check every converted post before it is migrated.

The embed defect reached a third of the corpus and surfaced because somebody
opened a post that happened to have a video in it. After the blog flips, a
defect like that is live on every post at once. This checks the classes that
can be checked mechanically:

  assets    every image and iframe URL resolves
  links     internal akka.io links resolve
  content   the converted body still holds the live post's paragraphs
  figures   no figure displayed wider than the image can carry
  code      no block left unlabelled that is not plain text

    python tools/blog-technical/preflight.py            # every post
    python tools/blog-technical/preflight.py <slug> ... # named posts
    python tools/blog-technical/preflight.py --checks assets,links
"""

import argparse
import concurrent.futures as futures
import html as html_mod
import os
import re
import struct
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import port  # noqa: E402
from html_sanitizer import looks_like_java  # noqa: E402

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

POSTS = os.path.join(port.ROOT, 'blog-technical', 'posts')
UA = {'User-Agent': 'Mozilla/5.0'}
ALL_CHECKS = ('assets', 'links', 'content', 'figures', 'code')


def get(url, nbytes=None):
    """(status, head-bytes). Status is 0 when the request itself failed."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return r.status, (r.read(nbytes) if nbytes else b'')
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception:
        return 0, b''


def plain(fragment):
    text = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[\s\S]*?</\1>', '', fragment))
    return re.sub(r'\s+', ' ', html_mod.unescape(text)).strip()


def signature(text):
    """Letters and digits only, lowercased — comparable across markup."""
    return re.sub(r'[^a-z0-9]+', '', text.lower())


def paragraphs(fragment):
    out = []
    for p in re.findall(r'<p[^>]*>([\s\S]*?)</p>', fragment):
        t = plain(p)
        if len(t.split()) >= 8:
            out.append(t)
    return out


def image_size(url):
    """Intrinsic (w, h) from the file header, or None."""
    status, head = get(url, 4096)
    if status != 200 or not head:
        return None
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', head[16:24])
    if head[:2] == b'\xff\xd8':
        i = 2
        while i < len(head) - 9:
            if head[i] != 0xFF:
                i += 1
                continue
            if head[i + 1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', head[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack('>H', head[i + 2:i + 4])[0]
    if b'<svg' in head:
        text = head.decode('utf-8', 'replace')
        w = re.search(r'<svg[^>]*\bwidth="(\d+)', text)
        h = re.search(r'<svg[^>]*\bheight="(\d+)', text)
        if w and h:
            return int(w.group(1)), int(h.group(1))
    return None


def check_assets(slug, src, findings):
    urls = set(re.findall(r'<(?:img|iframe)[^>]+src="([^"]+)"', src))
    for url in urls:
        if not url.startswith('http'):
            findings.append((slug, 'assets', f'relative src will not resolve: {url}'))
            continue
        status, _ = get(url, 1)
        if status != 200:
            findings.append((slug, 'assets', f'HTTP {status}: {url}'))


def check_links(slug, src, findings):
    urls = {u for u in re.findall(r'<a[^>]+href="(https?://[^"]+)"', src)
            if 'akka.io' in u}
    for url in urls:
        status, _ = get(url, 1)
        if status not in (200, 999):
            findings.append((slug, 'links', f'HTTP {status}: {url}'))


def check_content(slug, src, findings):
    """The converted body must still hold what the live post says."""
    status, raw = get(f'https://akka.io/blog/{slug}', 400_000)
    if status == 404:
        return  # a local variant (e.g. -light), not a post to migrate
    if status != 200:
        findings.append((slug, 'content', f'live post unreachable (HTTP {status})'))
        return
    live = raw.decode('utf-8', 'replace')
    # Compare against the post body alone. The page also carries the mega-menu
    # and footer, whose link lists parse as long paragraphs and would read as
    # content the conversion dropped.
    start = live.find('blog-post__body')
    if start < 0:
        findings.append((slug, 'content', 'live post body container not found'))
        return
    # The body ends at whichever of the page's trailing sections comes first.
    # Anchoring on one of them leaves the footer in whenever a post lacks it.
    end = min((p for p in (live.find(mark, start) for mark in
               ('blog-related-posts', 'SEE ALL BLOGS', 'blog_info_div',
                'Let&rsquo;s Build Trust', "Let's Build Trust", 'hs-blog-recommended'))
               if p > 0), default=len(live))
    live = live[start:end]
    # Compare on a signature with spacing and punctuation removed, against the
    # whole converted body rather than its paragraphs. A live paragraph often
    # survives as a figure caption or a pull quote, and the live pages carry
    # letter-spacing artifacts ("T he Platf orm") that no exact match survives.
    ours = signature(plain(src))
    missing = [p for p in paragraphs(live) if signature(p)[:70] not in ours]
    if missing:
        findings.append((slug, 'content',
                         f'{len(missing)} live paragraph(s) absent, first: {missing[0][:70]}'))


def check_figures(slug, src, findings):
    for fig in re.findall(r'<figure[\s\S]*?</figure>', src):
        m = re.search(r'--fig-w:(\d+)px', fig)
        url = re.search(r'src="([^"]+)"', fig)
        if not (m and url) or url.group(1).endswith('.svg'):
            continue  # vector scales without loss
        size = image_size(url.group(1))
        if size and int(m.group(1)) > size[0]:
            findings.append((slug, 'figures',
                             f'displayed at {m.group(1)}px, image is {size[0]}px: '
                             + url.group(1).rsplit('/', 1)[-1]))


def check_code(slug, src, findings):
    for block in re.findall(r'<pre[^>]*>[\s\S]*?</pre>', src):
        if 'language-text' not in block:
            continue
        code = html_mod.unescape(re.sub(r'<[^>]+>', '', block))
        if looks_like_java(code):
            findings.append((slug, 'code', f'unlabelled Java: {code.strip()[:50]!r}'))


CHECKS = {'assets': check_assets, 'links': check_links, 'content': check_content,
          'figures': check_figures, 'code': check_code}


def run(slug, checks):
    src = port.read(os.path.join(POSTS, f'{slug}.html'))
    findings = []
    for name in checks:
        try:
            CHECKS[name](slug, src, findings)
        except Exception as exc:                     # a check must not stop the sweep
            findings.append((slug, name, f'check errored: {exc}'))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('slug', nargs='*')
    ap.add_argument('--checks', default=','.join(ALL_CHECKS))
    ap.add_argument('--workers', type=int, default=8)
    args = ap.parse_args()

    checks = [c for c in args.checks.split(',') if c in CHECKS]
    slugs = args.slug or sorted(f[:-5] for f in os.listdir(POSTS) if f.endswith('.html'))
    print(f'{len(slugs)} post(s), checks: {", ".join(checks)}\n')

    findings = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(lambda s: run(s, checks), slugs):
            findings.extend(result)

    by_check = {}
    for slug, check, message in findings:
        by_check.setdefault(check, []).append((slug, message))
    for check in checks:
        rows = by_check.get(check, [])
        print(f'== {check}: {len(rows)} finding(s)')
        for slug, message in rows:
            print(f'   {slug[:46]:<46} {message}')
    print(f'\nTotal: {len(findings)} finding(s) across {len(slugs)} post(s)')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
