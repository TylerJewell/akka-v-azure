"""Mark the posts that lead the blog index, and give each its band artwork.

    python scratchpad/set_featured.py            # show what would change
    python scratchpad/set_featured.py --apply

Widgets are merged rather than replaced: a post carries other widget values
(hide_from_listing, subtitle, eyebrow) and a bare PATCH of the widgets object
drops whatever it does not name.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# hs_api and the token it reads live in scratchpad/, which is per-machine and
# not committed. Import it from there rather than duplicating the token logic.
sys.path.insert(0, os.path.join(ROOT, 'scratchpad'))
try:
    import hs_api  # noqa: E402
except ModuleNotFoundError:
    sys.exit('scratchpad/hs_api.py not found — this tool needs the HubSpot helper '
             'and scratchpad/.hs_env on this machine')

BANDS = 'https://45500578.fs1.hubspotusercontent-na1.net/hubfs/45500578/website/blog/images/'
FEATURED = {
    'building-the-akka-mcp-gateway': BANDS + 'blog-band-mcp-gateway.jpg',
    'scaling-agentic-ai-session-gartner-2026': BANDS + 'blog-band-governance.jpg',
    'the-autonomous-operating-environment': BANDS + 'blog-band-autonomous.jpg',
}


def main():
    apply = '--apply' in sys.argv
    for slug, art in FEATURED.items():
        found = hs_api.jget('/cms/v3/blogs/posts?limit=1&slug=blog/' + slug)
        results = found.get('results') or []
        if not results:
            print('  no live post:', slug)
            continue
        post = results[0]
        widgets = dict(post.get('widgets') or {})
        widgets['featured_post'] = {'body': {'value': True}}
        widgets['band_image'] = {'body': {'src': art, 'alt': ''}}
        print('  %-46s widgets %d -> %d' % (slug[:46], len(post.get('widgets') or {}), len(widgets)))
        if not apply:
            continue
        hs_api.patch('/cms/v3/blogs/posts/%s' % post['id'], {'widgets': widgets})
        hs_api.post('/cms/v3/blogs/posts/%s/draft/push-live' % post['id'], {})
        print('     set and pushed')


if __name__ == '__main__':
    main()
