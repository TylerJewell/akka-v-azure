"""Add the CAIO / CIO role tag to the posts that address an executive reader.

    python scratchpad/tag_executive.py           # resolve and show, write nothing
    python scratchpad/tag_executive.py --apply   # PATCH tagIds and push live
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

TAG_ID = 219530652736          # CAIO / CIO
DATA = os.path.join(HERE, '..', '..', 'scratchpad', 'blog_index_data.json')

# Matched on a distinctive fragment of the title so a slug rename cannot
# silently retarget one of these.
TITLES = [
    # announcements addressing an executive reader
    'Manulife Selects Akka',
    'Akka and Deloitte Collaborate',
    'News: Akka Introduces Agentic AI Platform',
    'Announcing the Akka Agentic Platform',
    'Introducing Akka Specify',
    'News: Akka launches new deployment options',
    'Akka 3 - FAQ',
    'News: Lightbend launches Akka 3',
    'Lightbend is now Akka',
    'Akka license keys and a no SPAM promise',
    'Akka closes FY24 with record growth',
    'Lightbend achieves SOC 2 compliance',
    'Why we are changing the license for Akka',
    'Lightbend changes its software licensing model',
    '2024 predictions for the cloud native market',
    'Celebrating a milestone',
    'Lightbend and Scalac partner',
    'Lightbend releases Akka 24.05',
    # posts that are not announcements and address the same reader
    'Go Slow to Go Fast',
    'Scaling Agentic AI with Governance',
    'Trustworthy AI with Akka',
    'What is Agentic AI?',
    'Agentic AI architecture 101',
    'Agentic AI Use Cases',
    'Is community-backed open source',
    'Open source is at a crossroads',
]


def resolve():
    posts = json.load(open(DATA, encoding='utf-8'))
    hits, misses, ambiguous = [], [], []
    for fragment in TITLES:
        found = [p for p in posts if fragment.lower() in p['title'].lower()]
        if not found:
            misses.append(fragment)
        elif len(found) > 1:
            ambiguous.append((fragment, [p['title'] for p in found]))
        else:
            hits.append(found[0])
    return hits, misses, ambiguous


def main():
    apply = '--apply' in sys.argv
    hits, misses, ambiguous = resolve()

    for p in hits:
        already = 'CAIO / CIO' in p['tags']
        print('  %s %s  %s' % ('=' if already else '+', p['date'], p['title'][:62]))
    if misses:
        print('\nNO MATCH:')
        for m in misses:
            print('  ', m)
    if ambiguous:
        print('\nAMBIGUOUS:')
        for frag, names in ambiguous:
            print('  ', frag, '->', names)
    print('\nresolved %d of %d' % (len(hits), len(TITLES)))
    if misses or ambiguous:
        sys.exit('unresolved titles — nothing written')
    if not apply:
        print('dry run — pass --apply to write')
        return

    for p in hits:
        live = hs_api.jget('/cms/v3/blogs/posts?limit=1&slug=blog/' + p['slug'])
        results = live.get('results') or []
        if not results:
            print('  MISSING on live blog:', p['slug'])
            continue
        post = results[0]
        tags = list(post.get('tagIds') or [])
        if TAG_ID in tags:
            print('  already tagged:', p['slug'])
            continue
        tags.append(TAG_ID)
        hs_api.patch('/cms/v3/blogs/posts/%s' % post['id'], {'tagIds': tags})
        hs_api.post('/cms/v3/blogs/posts/%s/draft/push-live' % post['id'], {})
        print('  tagged:', p['slug'])


if __name__ == '__main__':
    main()
