"""Assign a role and topic set to every post from the text of the post.

Evidence is counted per 1,000 words so a 300-word announcement and a 4,000-word
guide are judged on density rather than length. Each rule below names the terms
it counts, so a disputed assignment can be traced to the words that produced it.

    python scratchpad/classify_tags.py              # proposal + diff, writes nothing
    python scratchpad/classify_tags.py --apply      # PATCH tagIds and push live
"""
import json
import os
import re
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

POSTS = os.path.join(ROOT, 'blog-technical', 'posts')
SNAPSHOT = os.path.join(ROOT, 'blog-technical', 'snapshots', 'blog-tags-before.json')
NAMES = os.path.join(ROOT, 'blog-technical', 'snapshots', 'blog-tag-names.json')
PROPOSAL = os.path.join(ROOT, 'scratchpad', 'tag-proposal.json')

# Tags that describe what a post IS rather than who it is for or what it covers.
# They are carried through untouched.
KEEP = {'News', 'Demo', 'Resources', 'Retired'}

# term -> weight. A term worth 2 is one that only appears when the subject is
# genuinely that topic; a term worth 1 also appears in passing.
TOPICS = {
    'AI': {r'\bagentic\b': 2, r'\bLLM\b': 2, r'\bgenerative ai\b': 2, r'\bAI\b': 1,
           r'\binference\b': 1, r'\bprompt\b': 1, r'\bmodel provider\b': 2},
    'Agents': {r'\bagent\b': 1, r'\bmulti-agent\b': 2, r'\btool call': 2, r'\bMCP\b': 2,
               r'\bautonomous agent\b': 2},
    'Orchestration': {r'\bworkflow\b': 2, r'\borchestrat': 2, r'\bsaga\b': 2,
                      r'\bdurable execution\b': 2, r'\bstate machine\b': 1},
    'Streaming': {r'\bakka streams\b': 2, r'\bbackpressure\b': 2, r'\bstreaming\b': 1,
                  r'\bkafka\b': 1, r'\bpub/?sub\b': 1, r'\bstream\b': 1},
    'Memory': {r'\bakka memory\b': 2, r'\bshort-term memory\b': 2, r'\blong-term memory\b': 2,
               r'\bembedding': 2, r'\bRAG\b': 2, r'\bvector (?:db|database|store)\b': 2,
               r'\bcontext window\b': 2, r'\bmemory\b': 1},
    'Libraries': {r'\bakka libraries\b': 2, r'\bactor\b': 1, r'\bscala\b': 1,
                  r'\bcluster sharding\b': 2, r'\bakka classic\b': 2, r'\bakka \d\d\.\d\d\b': 1},
    'Edge / IoT': {r'\bakka edge\b': 2, r'\bIoT\b': 2, r'\bdigital twin\b': 2,
                   # A bare "edge" matches "cutting edge" and "edge case", which
                   # put this tag on a licensing post. Every term names a place.
                   r'\bedge computing\b': 2, r'\bat the edge\b': 2,
                   r'\bedge (?:node|device|deployment|location|region)': 2,
                   r'\bdevice\b': 1},
    'Multi-region': {r'\bmulti-region\b': 2, r'\bactive-active\b': 2, r'\breplicat': 1,
                     r'\bfailover\b': 2, r'\bregion\b': 1, r'\bgeo-?distribut': 2},
    'Operations': {r'\bobservability\b': 2, r'\brolling update\b': 2, r'\bSRE\b': 2,
                   r'\bkubernetes\b': 1, r'\bdeploy': 1, r'\boperate\b': 1,
                   r'\buptime\b': 2, r'\bincident\b': 1},
    'Security': {r'\bCVE\b': 2, r'\bvulnerabilit': 2, r'\bzero trust\b': 2, r'\bSOC 2\b': 2,
                 r'\bTLS\b': 2, r'\bauthenticat': 1, r'\bsecurity\b': 1, r'\bencrypt': 1},
    'Distributed Systems': {r'\bdistributed system': 2, r'\bconsensus\b': 2, r'\bcluster\b': 1,
                            r'\bpartition\b': 1, r'\bsharding\b': 2, r'\bnode\b': 1,
                            r'\beventual consistency\b': 2, r'\bevent sourc': 1},
    'Governance': {r'\bgovernance\b': 2, r'\bEU AI Act\b': 2, r'\bregulat': 1,
                   r'\baudit trail\b': 2, r'\boversight\b': 2, r'\bcompliance\b': 1,
                   r'\bpolicy\b': 1},
    'DevEx': {r'\bdeveloper experience\b': 2, r'\blocal development\b': 2, r'\bIDE\b': 2,
              r'\bproductivity\b': 1, r'\btooling\b': 1, r'\bboilerplate\b': 2},
}

ROLE_DEVELOPER = {r'\bAPI\b': 1, r'\bSDK\b': 1, r'\bclass\b': 1, r'\bmethod\b': 1,
                  r'\bcode\b': 1, r'\bcompile': 2, r'\bimplement': 1, r'\bsnippet\b': 2,
                  r'\bjava\b': 1, r'\bscala\b': 1, r'\brepository\b': 1}
ROLE_ARCHITECT = {r'\barchitect': 2, r'\bdistributed system': 2, r'\bscal(?:e|ing|ability)\b': 1,
                  r'\bresilien': 1, r'\bthroughput\b': 1, r'\blatency\b': 1,
                  r'\bavailability\b': 1, r'\btopology\b': 2, r'\bcluster\b': 1}
ROLE_EXEC = {r'\bCAIO\b': 2, r'\bCIO\b': 2, r'\bboard\b': 1, r'\bgovernance\b': 2,
             r'\bcompliance\b': 1, r'\bprocurement\b': 2, r'\blicens': 1, r'\bbudget\b': 2,
             r'\bTCO\b': 2, r'\bROI\b': 2, r'\benterprise\b': 1, r'\bregulat': 1,
             r'\bstrateg': 1, r'\brisk\b': 1}

TOPIC_MIN = 2.0       # weighted hits per 1,000 words
TOPIC_MIN_HITS = 3    # and at least this many matches outright
TOPIC_SHARE = 0.0     # a dominant topic must not suppress the real secondary ones
MAX_TOPICS = 5

# Roles are assigned by which reader the post is written for, so they compare
# against each other rather than against a fixed floor. A post always gets the
# reader it scores highest for, and gets a second only where that reader is
# addressed nearly as much.
ROLE_SHARE = 0.55

# The 26 posts read individually and confirmed as addressing an executive.
# Density alone puts the licence-change posts below the line, because their
# vocabulary is libraries while their subject is procurement.
EXEC_CONFIRMED = {
    'manulife-selects-akka-to-operationalize-agentic-ai', 'news-akka-and-deloitte',
    'news-akka-introduces-agentic-ai-platform', 'announcing-akkas-agentic-ai-release',
    'introducing-akka-specify', 'akka-launches-new-deployment-options-for-agentic-ai-at-scale',
    'akka-3-frequently-asked-questions', 'lightbend-launches-akka-3-rebrands-company-as-akka',
    'lightbend-is-now-akka', 'akka-license-keys-and-no-spam-promise',
    'akka-record-growth-fifty-new-customers-cash-flow-positive-new-growth-executives',
    'lightbend-achieves-soc-2-compliance', 'why-we-are-changing-the-license-for-akka',
    'lightbend-changes-its-software-licensing-model-for-akka-technology',
    '2024-predictions-for-the-cloud-native-market',
    'celebrating-a-milestone-akka-surpasses-1-billion-downloads',
    'lightbend-scalac-partner-enable-enterprises-to-leverage-the-power-of-akka',
    'lightbend-releases-akka-2405-security-performance-edge-efficiency',
    'go-slow-to-go-fast', 'scaling-agentic-ai-session-gartner-2026',
    'trustworthy-ai-with-akka', 'what-is-agentic-ai', 'agentic-ai-architecture',
    'agentic-ai-use-cases', 'is-community-backed-open-source-software-worth-the-risk',
    'open-source-is-at-a-crossroads',
}


def text_of(slug):
    path = os.path.join(POSTS, slug + '.html')
    if not os.path.exists(path):
        return None
    src = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', open(path, encoding='utf-8').read())
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', src))


def score(text, rules):
    words = max(len(text.split()), 1)
    weighted = hits = 0
    for pattern, weight in rules.items():
        n = len(re.findall(pattern, text, re.I))
        weighted += n * weight
        hits += n
    return 1000 * weighted / words, hits


def classify(text, has_code, slug):
    topics = []
    for name, rules in TOPICS.items():
        density, hits = score(text, rules)
        if density >= TOPIC_MIN and hits >= TOPIC_MIN_HITS:
            topics.append((density, name))
    topics.sort(reverse=True)
    if topics:
        strongest = topics[0][0]
        topics = [(d, n) for d, n in topics if d >= strongest * TOPIC_SHARE]
    chosen = [n for _, n in topics[:MAX_TOPICS]]

    dev, _ = score(text, ROLE_DEVELOPER)
    arch, _ = score(text, ROLE_ARCHITECT)
    exe, _ = score(text, ROLE_EXEC)
    # Code in the post is direct evidence of its reader, so it lifts the
    # developer score rather than bypassing the comparison.
    if has_code:
        dev *= 1.5
    ranked = sorted(((dev, 'Developer'), (arch, 'Architect / CTO'), (exe, 'CAIO / CIO')),
                    reverse=True)
    top = ranked[0][0] or 1.0
    roles = [name for value, name in ranked if value >= top * ROLE_SHARE]
    if slug in EXEC_CONFIRMED and 'CAIO / CIO' not in roles:
        roles.append('CAIO / CIO')
    return roles, chosen, {'dev': dev, 'arch': arch, 'exec': exe}


def main():
    apply = '--apply' in sys.argv
    snapshot = json.load(open(SNAPSHOT, encoding='utf-8'))
    names = {int(k): v for k, v in json.load(open(NAMES, encoding='utf-8')).items()}
    ids = {v: k for k, v in names.items()}

    proposal = {}
    for pid, rec in snapshot.items():
        if rec['state'] != 'PUBLISHED':
            continue
        text = text_of(rec['slug'])
        if text is None:
            continue
        has_code = '<pre' in open(os.path.join(POSTS, rec['slug'] + '.html'),
                                  encoding='utf-8').read()
        roles, topics, scores = classify(text, has_code, rec["slug"])
        current = [names.get(t, str(t)) for t in rec['tagIds']]
        keep = [t for t in current if t in KEEP]
        final = sorted(set(roles + topics + keep))
        proposal[pid] = {'slug': rec['slug'], 'before': sorted(current), 'after': final,
                         'scores': {k: round(v, 1) for k, v in scores.items()},
                         'tagIds': sorted({ids[n] for n in final if n in ids})}

    json.dump(proposal, open(PROPOSAL, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    from collections import Counter
    after = Counter(t for p in proposal.values() for t in p['after'])
    before = Counter(t for p in proposal.values() for t in p['before'])
    print('%-22s %7s %7s' % ('tag', 'before', 'after'))
    for name in sorted(set(before) | set(after)):
        print('%-22s %7d %7d' % (name, before[name], after[name]))
    print('\nposts: %d' % len(proposal))
    print('topics per post: %.1f avg' % (
        sum(len([t for t in p['after'] if t in TOPICS]) for p in proposal.values()) / len(proposal)))
    unresolved = {n for p in proposal.values() for n in p['after']} - set(ids)
    if unresolved:
        sys.exit('tag names with no id: %s' % unresolved)

    if not apply:
        print('\ndry run — proposal written to', PROPOSAL)
        return

    for pid, p in proposal.items():
        if set(p['before']) == set(p['after']):
            continue
        hs_api.patch('/cms/v3/blogs/posts/%s' % pid, {'tagIds': p['tagIds']})
        hs_api.post('/cms/v3/blogs/posts/%s/draft/push-live' % pid, {})
        print('  retagged', p['slug'])


if __name__ == '__main__':
    main()
