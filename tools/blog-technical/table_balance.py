#!/usr/bin/env python3
"""Size table columns from the width of the text they hold.

A table spans the full .wide measure, so a browser's automatic layout hands the
slack to whichever column has the longest header. Short columns end up starting
far across the table with their text against the left edge, reading as though the
row has drifted left.

The columns are sized here instead:

  1. Estimate every cell's single-line text width from the font it renders in.
     A column's natural width is the widest cell in it.
  2. A column whose natural width fits NARROW_MAX never needs to wrap. It is
     given exactly its content plus the cell padding — it hugs.
  3. Whatever is left goes to the columns that do wrap, split in proportion to
     how much text each holds.
  4. When every column hugs there is nothing to absorb the slack, so it is split
     equally between them and their text is centred in the space. This is the
     case that reads as left-leaning when the slack lands in one column.

Widths are written as a <colgroup> and the table is set to fixed layout, which
is what makes a browser honour them.

    python tools/blog-technical/table_balance.py <post.html> [...]   # rewrite in place
"""

import re
import sys

TABLE_W = 940          # the .wide measure a table-scroll block spans
COL_W = 640            # the reading column a table stays in when it fits
CELL_PAD = 32          # .table-scroll th,td padding: 12px 16px
NARROW_MAX = 170       # above this a column is prose and expected to wrap
CENTRE_MAX = 20        # a column of cells this short reads as a single token
HEAD_WRAP = 0.62       # share of a header that lands on its longer wrapped line

# Rough advance widths. Only the ratios between columns matter, so a class per
# character shape is enough to place the boundaries.
_NARROW_CHARS = "iljtfr.,;:'!|[]() "
_WIDE_CHARS = "mwMW@%"


def text_width(text, px):
    w = 0.0
    for ch in text:
        if ch in _NARROW_CHARS:
            w += px * 0.30
        elif ch in _WIDE_CHARS:
            w += px * 0.85
        elif ch.isupper() or ch.isdigit():
            w += px * 0.60
        else:
            w += px * 0.52
    return w


_CELL = re.compile(r'<(t[hd])\b([^>]*)>([\s\S]*?)</\1>', re.I)
_ROW = re.compile(r'<tr\b[^>]*>[\s\S]*?</tr>', re.I)


def _plain(html_fragment):
    from html import unescape
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', html_fragment))).strip()


def measure(table_html):
    """Return per-column measurements.

    Body and header are measured apart. A header is free to wrap onto a second
    line, so it must not be what decides that a column of short values is wide:
    a column headed 'Application availability' holding '99.9%' is a narrow
    column with a two-line header.
    """
    cols = []
    for row in _ROW.finditer(table_html):
        for i, cell in enumerate(_CELL.finditer(row.group(0))):
            tag, _, inner = cell.groups()
            text = _plain(inner)
            head = tag.lower() == 'th'
            px = 12 * 1.14 if head else 15.0
            width = text_width(text.upper() if head else text, px)
            while len(cols) <= i:
                cols.append({'body': 0.0, 'head': 0.0, 'word': 0.0, 'text': '', 'rows': []})
            col = cols[i]
            if head:
                col['head'] = max(col['head'], width)
                for w in text.split():
                    col['word'] = max(col['word'], text_width(w.upper(), px))
            else:
                col['rows'].append(width)
                if width > col['body']:
                    col['body'], col['text'] = width, text
    return cols


def typical(col):
    """The width the column's rows actually want, ignoring one long outlier.

    Sizing a column by its widest row leaves every other row stranded against
    the left of a mostly empty column. The upper quartile is what most rows
    can use; the long row wraps.
    """
    rows = sorted(col['rows'])
    if not rows:
        return col['body']
    return rows[min(len(rows) - 1, int(len(rows) * 0.75))]


def fits_reading_column(cols):
    """True when the table wants less width than the reading column gives it.

    Such a table has no reason to break out to the wide measure: doing so
    starts it left of the prose and pads the columns past what their rows use.
    """
    want = sum(CELL_PAD + (c['body'] if c['body'] <= NARROW_MAX else typical(c))
               for c in cols)
    return want <= COL_W


def widths(cols, budget=TABLE_W):
    """Column widths in px, summing to the budget. See the module docstring."""
    # A hugging column still has to hold its header. Two lines rarely split
    # evenly, so half the header width is optimistic — HEAD_WRAP is the share
    # the longer line actually takes. A word cannot be broken at all, which is
    # the other floor.
    natural = [max(c['body'], min(c['head'], max(c['head'] * HEAD_WRAP, c['word'])))
               for c in cols]
    hugging = [i for i, c in enumerate(cols) if c['body'] <= NARROW_MAX]
    wrapping = [i for i in range(len(natural)) if i not in hugging]

    out = [0.0] * len(natural)
    for i in hugging:
        out[i] = natural[i] + CELL_PAD

    slack = budget - sum(out) - sum(CELL_PAD for _ in wrapping)
    if len(wrapping) > 1 and sum(natural[i] for i in wrapping) <= slack:
        # Every wrapping column fits on one line, so a proportional split hands
        # each of them more room than it can use and strands the text at the
        # left of a part-empty column. Cap them at their content and share what
        # is over, indenting each by half its share so the block sits centred.
        over = slack - sum(natural[i] for i in wrapping)
        per = over / len(wrapping)
        for i in wrapping:
            out[i] = natural[i] + CELL_PAD + per
        return _as_pct(out), [], (wrapping, per / 2)
    if wrapping:
        share = sum(natural[i] for i in wrapping) or 1.0
        for i in wrapping:
            out[i] = CELL_PAD + slack * (natural[i] / share)
        centred = []
    else:
        # Nothing wraps: spread the slack and centre each column's text in it.
        per = max(slack, 0) / len(out)
        out = [w + per for w in out]
        centred = [i for i, c in enumerate(cols) if len(c['text']) <= CENTRE_MAX]

    return _as_pct(out), centred, ([], 0.0)


def _as_pct(out):
    total = sum(out) or 1.0
    return [w / total * 100 for w in out]


def _mark(table_html, columns, cls):
    if not columns:
        return table_html

    def row(m):
        idx = [0]

        def cell(c):
            tag, attrs, inner = c.groups()
            if idx[0] in columns:
                attrs = re.sub(r'\bclass="([^"]*)"', r'class="\1 %s"' % cls, attrs) \
                    if 'class="' in attrs else attrs + ' class="%s"' % cls
            idx[0] += 1
            return f'<{tag}{attrs}>{inner}</{tag}>'
        return _CELL.sub(cell, m.group(0))
    return _ROW.sub(row, table_html)


def _reset(table_html):
    """Drop a previous run's output so re-running lands on the same result."""
    table_html = re.sub(r'<colgroup>[\s\S]*?</colgroup>\s*', '', table_html, flags=re.I)
    table_html = re.sub(r'\s*class="(?:ctr|ind)"', '', table_html)
    table_html = re.sub(r'\s+class="([^"]*?)\s*\b(?:ctr|ind)\b', r' class="\1', table_html)
    open_m = re.match(r'<table\b[^>]*>', table_html, re.I)
    return re.sub(r'\s*style="table-layout:fixed[^"]*"', '', open_m.group(0)) \
        + table_html[open_m.end():]


def balance_table(table_html, budget=TABLE_W):
    table_html = _reset(table_html)
    cols = measure(table_html)
    if len(cols) < 2:
        return table_html
    pct, centred, (indented, indent) = widths(cols, budget)

    table_html = _mark(table_html, centred, 'ctr')
    table_html = _mark(table_html, indented, 'ind')

    group = '<colgroup>' + ''.join('<col style="width:%.1f%%">' % p for p in pct) + '</colgroup>'
    open_m = re.match(r'<table\b[^>]*>', table_html, re.I)
    tag = open_m.group(0)
    # Fixed layout is what makes the browser use the widths rather than treat
    # them as a starting suggestion. The indent is one value for the table
    # because the columns that take it share the leftover equally.
    style = 'table-layout:fixed'
    if indent >= 1:
        style += ';--ind:%dpx' % round(indent)
    if 'table-layout' not in tag:
        tag = tag[:-1] + ' style="%s">' % style
    return tag + group + table_html[open_m.end():]


# The scaffolder breaks a table out of the reading column: it closes .body.col,
# opens .wide + .table-scroll, and reopens .body.col after. A table that fits the
# reading column keeps that column instead, so it starts where the prose starts.
_BREAKOUT = re.compile(
    r'</div>\s*<div class="wide">\s*<div class="table-scroll">\s*'
    r'(<table\b[\s\S]*?</table>)\s*</div>\s*</div>\s*<div class="body col">\s*',
    re.I)
# The shape this tool leaves behind, so a re-run reconsiders its own decision
# rather than freezing the first one.
_TIGHT = re.compile(
    r'<div class="table-scroll tight">\s*(<table\b[\s\S]*?</table>)\s*</div>\s*',
    re.I)

_WIDE_FORM = ('</div>\n\n<div class="wide">\n<div class="table-scroll">\n%s'
              '\n</div>\n</div>\n\n<div class="body col">\n')
_TIGHT_FORM = '<div class="table-scroll tight">\n%s\n</div>\n\n'


def balance(html):
    def place(m):
        table = _reset(m.group(1))
        cols = measure(table)
        if len(cols) >= 2 and fits_reading_column(cols):
            return _TIGHT_FORM % balance_table(table, COL_W)
        return _WIDE_FORM % balance_table(table)

    html = _BREAKOUT.sub(place, html)
    html = _TIGHT.sub(place, html)

    # Any table the breakout shape did not cover is still balanced in place.
    # One that already carries a colgroup was sized above, against a budget the
    # full-width default would overwrite.
    def leftover(m):
        return m.group(0) if '<colgroup>' in m.group(0) else balance_table(m.group(0))
    return re.sub(r'<table\b[\s\S]*?</table>', leftover, html, flags=re.I)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        with open(path, encoding='utf-8') as f:
            src = f.read()
        out = balance(src)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)
        print('%s  %d tables' % (path, len(re.findall(r'<colgroup>', out))))
