"""Derive AI-regulation corpus counts by reading the corpus at generation time.

The corpus is the source of truth. Nothing here caches: every call re-reads the
YAML so a deck built today reflects the corpus as it stands today. If the corpus
is not reachable, this raises — a build must fail rather than publish a stale
number.

Corpus location: $AKKA_CORPUS_PATH, else ../explainability/framework/regulations
relative to this repo.
"""

import os
import glob
import yaml

# Controls carrying this text are onboarding placeholders standing in for control
# sets that have not been extracted from the regulation's README yet. The
# regulation itself is researched; its per-article controls are not yet authored.
PLACEHOLDER_MARK = 'source corpus detail pending'

# The corpus is a separate repo cloned in a machine-specific spot. Resolution is
# flexible so the same build works on every machine without editing this file:
#   1. AKKA_CORPUS_PATH env var (explicit override, e.g. CI)
#   2. _build/corpus-path.local (a per-machine, gitignored one-line path)
#   3. auto-search the common clone spots below
# The corpus repo is named 'explain' on some machines and 'explainability' on
# others; either the repo root or its framework/regulations dir is accepted.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(THIS_DIR, '..'))
LOCAL_CONFIG = os.path.join(THIS_DIR, 'corpus-path.local')
CORPUS_NAMES = ('explain', 'explainability')
CORPUS_SUBDIR = os.path.join('framework', 'regulations')


def _as_regulations_dir(path):
    """Accept either a corpus repo root or its framework/regulations dir."""
    path = os.path.expanduser(path.strip())
    nested = os.path.join(path, CORPUS_SUBDIR)
    return nested if os.path.isdir(nested) else path


def _candidates():
    """Common per-machine clone spots, most specific first."""
    bases = [os.path.normpath(os.path.join(REPO_ROOT, '..')), os.path.expanduser('~')]
    out = []
    for base in bases:
        for name in CORPUS_NAMES:
            p = os.path.join(base, name, CORPUS_SUBDIR)
            if p not in out:
                out.append(p)
    return out


def read_only(path, root):
    """Open a corpus file for reading, structurally.

    The corpus belongs to another repository. This project reads it and must
    never write to it, so every corpus access goes through here: read mode is
    not a parameter, and the resolved path must stay inside the corpus root.
    """
    resolved = os.path.realpath(path)
    if os.path.commonpath([resolved, os.path.realpath(root)]) != os.path.realpath(root):
        raise SystemExit(f'Refusing to read outside the corpus root: {resolved}')
    return open(resolved, 'r', encoding='utf-8')


def corpus_path():
    # 1. explicit override
    env = os.environ.get('AKKA_CORPUS_PATH')
    if env:
        p = _as_regulations_dir(env)
        if os.path.isdir(p):
            return p
        raise SystemExit(f'AKKA_CORPUS_PATH is set but is not a corpus dir: {p}')
    # 2. per-machine local config (gitignored one-line path)
    if os.path.isfile(LOCAL_CONFIG):
        with open(LOCAL_CONFIG, encoding='utf-8') as f:
            p = _as_regulations_dir(f.read())
        if os.path.isdir(p):
            return p
        raise SystemExit(f'{LOCAL_CONFIG} points to a missing corpus dir: {p}')
    # 3. auto-search common clone spots
    tried = _candidates()
    for p in tried:
        if os.path.isdir(p):
            return p
    # 4. give up with actionable guidance
    rel_config = os.path.relpath(LOCAL_CONFIG, REPO_ROOT)
    raise SystemExit(
        'Corpus not found. Deck generation reads regulation/control counts live '
        'from the corpus, which is a separate repo (explain / explainability).\n'
        'Tried:\n  ' + '\n  '.join(tried) + '\n'
        'Fix by any of:\n'
        '  - set AKKA_CORPUS_PATH to the corpus repo (or its framework/regulations dir)\n'
        f'  - write that path into {rel_config} (per-machine, gitignored)\n'
        '  - clone the corpus as a sibling of this repo or in your home dir')


def pinned():
    """Escape hatch for building while the corpus is mid-edit and unparseable.

    AKKA_CORPUS_PINNED="regulations=190,controls=900,penalty-controls=632,penalty-regulations=102"

    Deliberately noisy and deliberately not a fallback: it is never consulted
    unless set, so a broken corpus still fails a normal build.
    """
    raw = os.environ.get('AKKA_CORPUS_PINNED')
    if not raw:
        return None
    values = dict(pair.split('=', 1) for pair in raw.split(','))
    missing = sorted(set(CLAIMS) - set(values))
    if missing:
        raise SystemExit(f'AKKA_CORPUS_PINNED is missing: {", ".join(missing)}')
    print('*' * 72)
    print('WARNING: corpus counts are PINNED, not read from the corpus.')
    print(f'  {raw}')
    print('  Output is only as correct as these values. Unset AKKA_CORPUS_PINNED')
    print('  and rebuild before publishing.')
    print('*' * 72)
    return {k: v.strip() for k, v in values.items()}


def counts():
    """Return {regulations, controls, penalty_controls, placeholders, corpus_path}."""
    root = corpus_path()

    regulations = sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d)) and not d.startswith('_'))

    authored, placeholders, penalty = 0, 0, 0
    penalty_regs = 0
    for reg in regulations:
        reg_has_penalty = False
        for path in glob.glob(os.path.join(root, reg, 'controls*.yaml')):
            with read_only(path, root) as f:
                doc = yaml.safe_load(f) or {}
            for control in (doc.get('controls') or []):
                if PLACEHOLDER_MARK in str(control.get('full_text_verbatim', '')):
                    placeholders += 1
                    continue
                authored += 1
                if control.get('penalty_tier') not in (None, 'n/a'):
                    penalty += 1
                    reg_has_penalty = True
        if reg_has_penalty:
            penalty_regs += 1

    if not regulations or not authored:
        raise SystemExit(f'Corpus at {root} yielded no regulations or controls; refusing to build.')

    return {
        'regulations': len(regulations),
        'controls': authored,
        'penalty_controls': penalty,
        'penalty_regulations': penalty_regs,
        'placeholders': placeholders,
        'corpus_path': root,
    }


# Token/marker name -> count key. These are the only claims wired to the corpus.
CLAIMS = {
    'regulations': 'regulations',
    'controls': 'controls',
    'penalty-controls': 'penalty_controls',
    'penalty-regulations': 'penalty_regulations',
}


def values():
    """Return {claim-name: 'formatted number'} for substitution."""
    pin = pinned()
    if pin:
        return pin
    c = counts()
    return {name: f'{c[key]:,}' for name, key in CLAIMS.items()}


if __name__ == '__main__':
    c = counts()
    print(f'corpus:            {c["corpus_path"]}')
    print(f'regulations:       {c["regulations"]}')
    print(f'controls:          {c["controls"]}  (authored)')
    print(f'penalty-bearing:   {c["penalty_controls"]} controls, across {c["penalty_regulations"]} regulations')
    print(f'placeholders:      {c["placeholders"]}  (not counted as controls)')
