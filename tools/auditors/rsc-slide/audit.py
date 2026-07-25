#!/usr/bin/env python3
"""Audit the overview deck's Runtime/Stack/Cloud (RSC) slide.

Compares three sources for accuracy and consistency:

  1. existing slide  — akka-overview/images/platform-rsc.png (a raster image; its text
                       content is transcribed below as EXISTING, the source of truth for
                       what the slide must still say).
  2. approved graphic — demos/stack-diagram/index.html (the signed-off stack diagram; the
                       source of truth for the embedded diagram's labels).
  3. new slide       — akka-overview/index.html, the redrawn RSC section that replaced the
                       image and inlines the approved diagram.

Checks:
  CONSISTENCY — the diagram inlined in the new slide reproduces the approved graphic's label
                set exactly (nothing added, dropped, or reworded on the way in).
  ACCURACY    — every text element from the existing slide is still accounted for in the new
                slide: titles, subtitles, the Runtime capability list, and the cloud
                environments must appear verbatim; each old Stack detail must map to a label
                that exists in the diagram (STACK_MAP), or be explicitly allow-listed as
                intentionally dropped (STACK_DROPPED).

Exit code 0 = verified; non-zero = discrepancies found (printed).
"""

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
APPROVED = os.path.join(ROOT, 'demos', 'stack-diagram', 'index.html')
NEW_SLIDE = os.path.join(ROOT, 'akka-overview', 'index.html')

# ---- source of truth 1: the existing slide (transcribed from platform-rsc.png) -------------
EXISTING = {
    'titles': ['Runtime', 'Stack', 'Cloud'],
    'subtitles': [
        'The clustering that executes your system reliably',
        'Commodity, multi-tenant cloud infrastructure',
        'Managed in any environment, with a sovereign option',
    ],
    'runtime_list': [
        'Actor-based concurrency', 'Streaming & backpressure', 'Durable execution',
        'In-memory sharded data', 'Split-brain resolution', 'Brokerless messaging',
        'Event sourcing',
    ],
    'cloud_envs': ["Akka's Cloud", 'Your VPC', 'Your Kubernetes'],
    # old Stack column details (replaced by the diagram). Each must map to a diagram label...
    'stack_items': [
        'Active-Active HA/DR', 'Rolling updates', 'Elastic scaling', 'Scale-to-zero',
        'Training', 'Runtime patching', 'Inference', 'Shared compute', 'Models', 'Scoring',
    ],
}

# old Stack detail -> the diagram label that now represents it (must exist in the diagram)
STACK_MAP = {
    'Active-Active HA/DR': 'HA/DR',
    'Rolling updates': 'Rolling Updater',
    'Elastic scaling': 'Elasticity',
    'Scale-to-zero': 'Elasticity',      # sign-off 2026-07-24: scale-to-zero is an Elasticity behavior
    'Runtime patching': 'Patching',
    'Inference': 'Inference',
    'Models': 'Model Routing',
    'Shared compute': 'Akka Clustering',
}
# old Stack details with no diagram equivalent, intentionally dropped (requires sign-off).
# Keep EMPTY until a human approves each drop — an unmapped, un-dropped item fails the audit.
STACK_DROPPED = {
    'Training',   # sign-off 2026-07-24: model training (AdaptiveML/SLM) is out of scope for this stack diagram
    'Scoring',    # sign-off 2026-07-24: dropped from the stack story
}


def norm(s):
    """Collapse a label to comparable text: strip tags, decode the few entities we use."""
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    (s := s.replace('&amp;', '&').replace('&rsquo;', "'").replace('&middot;', '·')
        .replace('&frasl;', '/').replace('&nbsp;', ' '))
    return re.sub(r'\s+', ' ', s).strip()


class LabelExtractor(HTMLParser):
    """Collect the normalized inner text of every element whose class contains a target token."""

    def __init__(self, classes):
        super().__init__(convert_charrefs=False)
        self.targets = set(classes)
        self.found = []
        self._stack = []   # (matched_bool, depth) frames
        self._buf = []
        self._capture_depth = 0

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        tokens = set(cls.split())
        if self._capture_depth:
            self._capture_depth += 1
        elif tokens & self.targets:
            self._capture_depth = 1
            self._buf = []

    def handle_endtag(self, tag):
        if self._capture_depth:
            self._capture_depth -= 1
            if self._capture_depth == 0:
                text = norm(''.join(self._buf))
                if text:
                    self.found.append(text)

    def handle_data(self, data):
        if self._capture_depth:
            self._buf.append(data)

    def handle_entityref(self, name):
        if self._capture_depth:
            self._buf.append('&%s;' % name)

    def handle_charref(self, name):
        if self._capture_depth:
            self._buf.append('&#%s;' % name)


DIAGRAM_LABEL_CLASSES = ['bname', 'etitle', 'chip', 'mini', 'wrap-tag', 'k8s-tag',
                         'platform-tab', 'bsub', 'caps']


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def slice_region(html, start_marker, end_marker):
    i = html.find(start_marker)
    j = html.find(end_marker, i + 1) if i >= 0 else -1
    return html[i:j] if i >= 0 and j >= 0 else html


def extract(html, classes):
    p = LabelExtractor(classes)
    p.feed(html)
    return p.found


def diagram_labels(html):
    return sorted(set(extract(html, DIAGRAM_LABEL_CLASSES)))


def main():
    problems = []

    approved_html = read(APPROVED)
    new_html = read(NEW_SLIDE)
    # scope the new-slide extraction to the RSC section so unrelated deck text can't leak in
    # spans the subtitle paragraph (which holds the inline env icons) through the diagram
    rsc_html = slice_region(new_html, '<p class="ssub reveal">', '</script>')

    # ---- CHECK 1: consistency (approved diagram == inlined diagram) ------------------------
    approved = diagram_labels(approved_html)
    inlined = diagram_labels(rsc_html)
    missing = [x for x in approved if x not in inlined]
    added = [x for x in inlined if x not in approved]
    if missing:
        problems.append('CONSISTENCY: diagram labels in the approved graphic but MISSING from '
                        'the new slide:\n    - ' + '\n    - '.join(missing))
    if added:
        problems.append('CONSISTENCY: diagram labels in the new slide but NOT in the approved '
                        'graphic (unexpected additions):\n    - ' + '\n    - '.join(added))

    # ---- CHECK 2: accuracy (existing slide text preserved in the new slide) ----------------
    # sign-off 2026-07-25: the Runtime/Stack/Cloud column headers and subtitles were removed;
    # the Runtime capability list moved from its own column into the Akka Clusters box (.caps
    # spans). The cloud environments stay (relocated above the diagram). So we no longer check
    # titles/subtitles, and the runtime capabilities are now verified inside the diagram.
    rsc_cap_spans = [norm(x) for x in re.findall(r'<span>([^<]+)</span>', rsc_html)]
    rsc_envs = extract(rsc_html, ['rsc-env'])
    inlined_set = set(inlined)

    def want(items, present, label):
        for it in items:
            if norm(it) not in [norm(p) for p in present]:
                problems.append('ACCURACY (%s): "%s" from the existing slide is missing from the '
                                'new slide.' % (label, it))

    want(EXISTING['runtime_list'], rsc_cap_spans, 'runtime capability (Akka Clusters box)')
    want(EXISTING['cloud_envs'], rsc_envs, 'cloud environment')

    # old Stack details: each must map to a diagram label present in the diagram, or be dropped
    for it in EXISTING['stack_items']:
        if it in STACK_DROPPED:
            continue
        mapped = STACK_MAP.get(it)
        if mapped is None:
            problems.append('ACCURACY (stack detail): "%s" from the existing slide has no diagram '
                            'equivalent and is not allow-listed as dropped. Map it in STACK_MAP or '
                            'add to STACK_DROPPED after sign-off.' % it)
        elif mapped not in inlined_set:
            problems.append('ACCURACY (stack detail): "%s" is mapped to diagram label "%s", but that '
                            'label is not present in the diagram.' % (it, mapped))

    # ---- report ---------------------------------------------------------------------------
    print('RSC slide audit')
    print('  approved graphic : %s' % os.path.relpath(APPROVED, ROOT))
    print('  new slide        : %s' % os.path.relpath(NEW_SLIDE, ROOT))
    print('  diagram labels   : %d approved / %d inlined' % (len(approved), len(inlined)))
    print()
    if not problems:
        print('VERIFIED — new slide is consistent with the approved graphic and accurate to the '
              'existing slide.')
        return 0
    print('FAILED — %d discrepancy(ies):\n' % len(problems))
    for i, p in enumerate(problems, 1):
        print('%2d. %s' % (i, p))
    return 1


if __name__ == '__main__':
    sys.exit(main())
