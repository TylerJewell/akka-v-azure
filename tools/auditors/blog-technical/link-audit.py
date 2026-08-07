#!/usr/bin/env python3
"""Link auditor for the technical blog template.

For each blog HTML file, extracts every <a href="..."> URL, fetches it with
a HEAD (falling back to GET), and reports the status. Groups results by
severity so dead links (404, DNS failure, timeout) are surfaced above
redirects (301/302), which are surfaced above successful (200) links.

Usage:
    python tools/auditors/blog-technical/link-audit.py blog-technical/*.html
    python tools/auditors/blog-technical/link-audit.py --only-broken posts/*.html
    python tools/auditors/blog-technical/link-audit.py --format json posts/*.html

Meant to run as:
  - a local pre-publish check (author runs before pushing)
  - a scheduled sweep (cron / GitHub Actions weekly) that reports drift
    when external docs sites reorganise their URL structure

Never modifies files. Reports only. Fixing dead links is a human decision
(the replacement URL may or may not cover the same topic).
"""

import argparse
import concurrent.futures
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape


def _iri_to_uri(iri):
    """Convert an IRI (which may contain non-ASCII characters) into an ASCII
    URI that urllib can request. Fixes false positives on social-share URLs
    that carry em-dashes, curly quotes, and non-breaking spaces in their
    query strings."""
    try:
        parts = urllib.parse.urlsplit(iri)
        netloc = parts.netloc.encode('idna').decode('ascii')
        path = urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=~")
        query = urllib.parse.quote(parts.query, safe="=&%:/@!$'()*+,;~")
        fragment = urllib.parse.quote(parts.fragment, safe="=&%:/@!$'()*+,;~")
        return urllib.parse.urlunsplit((parts.scheme, netloc, path, query, fragment))
    except Exception:
        return iri

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TIMEOUT = 10
USER_AGENT = 'akka-blog-link-audit/1.0'
MAX_WORKERS = 8


def _extract_links(html):
    """Return list of (url, anchor_text, source_line_hint) tuples."""
    links = []
    for m in re.finditer(r'<a\s+([^>]*?)>(.*?)</a>', html, re.S):
        attrs = m.group(1)
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(2))).strip()
        href_m = re.search(r'href\s*=\s*"([^"]+)"', attrs)
        if not href_m:
            continue
        href = unescape(href_m.group(1))
        # Skip anchors, mailto:, tel:, javascript:, data:
        if href.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
            continue
        # Skip protocol-relative for now — treat as https
        if href.startswith('//'):
            href = 'https:' + href
        # Skip pure relative links (would need base URL context)
        if not re.match(r'^https?://', href):
            continue
        # Compute line number from character offset
        line = html[:m.start()].count('\n') + 1
        links.append((href, text[:80] or '(no text)', line))
    return links


def _check_url(url):
    """Return dict: {'status': int|None, 'final_url': str, 'error': str|None, 'redirect': bool}."""
    encoded = _iri_to_uri(url)
    req = urllib.request.Request(encoded, headers={'User-Agent': USER_AGENT}, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return {
                'status': r.status,
                'final_url': r.geturl(),
                'redirect': r.geturl() != url,
                'error': None,
            }
    except urllib.error.HTTPError as e:
        # HEAD sometimes disallowed; retry with GET
        if e.code in (405, 400, 403):
            try:
                req2 = urllib.request.Request(encoded, headers={'User-Agent': USER_AGENT})
                with urllib.request.urlopen(req2, timeout=TIMEOUT) as r:
                    return {
                        'status': r.status,
                        'final_url': r.geturl(),
                        'redirect': r.geturl() != url,
                        'error': None,
                    }
            except urllib.error.HTTPError as e2:
                return {'status': e2.code, 'final_url': url, 'redirect': False,
                        'error': f'HTTP {e2.code} {e2.reason}'}
            except Exception as e2:
                return {'status': None, 'final_url': url, 'redirect': False, 'error': str(e2)}
        return {'status': e.code, 'final_url': url, 'redirect': False,
                'error': f'HTTP {e.code} {e.reason}'}
    except urllib.error.URLError as e:
        return {'status': None, 'final_url': url, 'redirect': False, 'error': f'URL error: {e.reason}'}
    except Exception as e:
        return {'status': None, 'final_url': url, 'redirect': False, 'error': str(e)}


def _classify(check):
    """OK | REDIRECT | GONE | ERROR"""
    if check.get('error') and check.get('status') is None:
        return 'ERROR'
    s = check.get('status')
    if s is None:
        return 'ERROR'
    if s == 404 or s == 410:
        return 'GONE'
    if 400 <= s < 600:
        return 'ERROR'
    if check.get('redirect'):
        return 'REDIRECT'
    return 'OK'


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    links = _extract_links(html)
    # Dedupe by URL for the network calls
    unique = {}
    for url, text, line in links:
        unique.setdefault(url, []).append({'text': text, 'line': line})
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_check_url, url): url for url in unique}
        for fut in concurrent.futures.as_completed(futures):
            url = futures[fut]
            check = fut.result()
            check['url'] = url
            check['occurrences'] = unique[url]
            check['classification'] = _classify(check)
            results.append(check)
    # Sort: GONE first, then ERROR, then REDIRECT, then OK
    priority = {'GONE': 0, 'ERROR': 1, 'REDIRECT': 2, 'OK': 3}
    results.sort(key=lambda r: (priority.get(r['classification'], 4), r['url']))
    return results


def format_text(path, results, only_broken=False):
    lines = [f'\n=== {path} ===']
    if not results:
        lines.append('  (no external links)')
        return '\n'.join(lines)
    counts = {'GONE': 0, 'ERROR': 0, 'REDIRECT': 0, 'OK': 0}
    for r in results:
        counts[r['classification']] = counts.get(r['classification'], 0) + 1
    lines.append(f'  {counts["OK"]} ok · {counts["REDIRECT"]} redirect · '
                 f'{counts["ERROR"]} error · {counts["GONE"]} gone')
    for r in results:
        cls = r['classification']
        if only_broken and cls in ('OK', 'REDIRECT'):
            continue
        marker = {
            'GONE':     '  GONE   ',
            'ERROR':    '  ERROR  ',
            'REDIRECT': '  redir  ',
            'OK':       '  ok     ',
        }[cls]
        line_hint = r['occurrences'][0]['line']
        lines.append(f'{marker}{r["url"]}')
        if r.get('error'):
            lines.append(f'          err: {r["error"]}')
        elif r.get('redirect'):
            lines.append(f'          → {r["final_url"]}')
        for occ in r['occurrences']:
            lines.append(f'          line {occ["line"]}: "{occ["text"]}"')
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='+', help='blog HTML file(s) to audit')
    p.add_argument('--only-broken', action='store_true',
                   help='report only GONE and ERROR results (skip OK and REDIRECT)')
    p.add_argument('--format', choices=('text', 'json'), default='text',
                   help='output format (default: text)')
    args = p.parse_args()

    all_results = {}
    total_gone = total_error = total_redir = 0
    t0 = time.time()

    for path in args.files:
        results = audit_file(path)
        all_results[path] = results
        for r in results:
            cls = r['classification']
            if cls == 'GONE': total_gone += 1
            elif cls == 'ERROR': total_error += 1
            elif cls == 'REDIRECT': total_redir += 1

    if args.format == 'json':
        print(json.dumps(all_results, indent=2))
    else:
        for path, results in all_results.items():
            print(format_text(path, results, only_broken=args.only_broken))
        elapsed = time.time() - t0
        print(f'\nTotal: {total_gone} gone, {total_error} error, {total_redir} redirect '
              f'(checked {sum(len(r) for r in all_results.values())} unique URLs in {elapsed:.1f}s)')

    return 1 if (total_gone or total_error) else 0


if __name__ == '__main__':
    sys.exit(main())
