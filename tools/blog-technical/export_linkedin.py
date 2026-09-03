#!/usr/bin/env python3
"""Export a blog-technical post as LinkedIn article assets.

LinkedIn's article editor has no table element and does not accept pasted markup,
so every figure AND every table leaves here as a PNG. The prose leaves as a
plain rendered page that pastes into the editor as rich text, with a marker
showing where each PNG is uploaded.

    python tools/blog-technical/export_linkedin.py we-ported-65-oss-projects

Writes to <out>/: one PNG per figure, INDEX.md, and article-body.html.
"""
import argparse
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parents[2]
SCALE = 2          # retina: an 802px figure lands at 1604px
PAD = 34           # breathing room baked into each PNG


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:48]


def export(post, out):
    src = ROOT / 'blog-technical' / 'posts' / f'{post}.html'
    if not src.exists():
        src = ROOT / 'blog-technical' / f'{post}.html'
    if not src.exists():
        sys.exit(f'post not found: {post}')
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={'width': 1280, 'height': 1400},
                       device_scale_factor=SCALE)
        p.goto(src.as_uri())
        p.wait_for_load_state('networkidle')
        p.wait_for_timeout(1200)

        # Each figure is captured on its own, so it needs its own margin and its
        # own ground rather than inheriting the column's.
        bg = p.evaluate("() => getComputedStyle(document.body).backgroundColor")
        p.add_style_tag(content=f"""
          figure.viz, figure.tbl {{
            padding:{PAD}px {PAD + 6}px; background:{bg}; margin:0;
          }}
          figure.tbl table {{ width:100%; }}
        """)
        p.wait_for_timeout(400)

        # Which H2 each figure sits under, so the index can be read by section.
        meta = p.evaluate("""() => {
          const heads = [...document.querySelectorAll('h2[id]')];
          return [...document.querySelectorAll('figure.viz, figure.tbl')].map(f => {
            let sec = '';
            for (const h of heads) {
              if (h.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING) continue;
              break;
            }
            const before = heads.filter(h =>
              h.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING);
            sec = before.length ? before[before.length - 1].textContent.trim() : '(intro)';
            return {
              kind: f.classList.contains('tbl') ? 'table' : 'figure',
              title: (f.querySelector('.viz-title')||{}).textContent || '',
              caption: (f.querySelector('h5')||{}).textContent || '',
              section: sec,
            };
          });
        }""")

        figs = p.query_selector_all('figure.viz, figure.tbl')
        rows = []
        for el, m in zip(figs, meta):
            el.scroll_into_view_if_needed()
            p.wait_for_timeout(120)
            n = re.sub(r'\D', '', m['title']) or '0'
            name = f"{m['kind']}-{int(n):02d}-{slug(m['caption'])}.png"
            el.screenshot(path=str(out / name))
            box = el.bounding_box()
            rows.append((m, name, int(box['width'] * SCALE), int(box['height'] * SCALE)))
            print(f"  {name}  {int(box['width']*SCALE)}x{int(box['height']*SCALE)}")

        write_index(out, post, rows)
        write_body(p, out, post, rows)
        b.close()


def write_index(out, post, rows):
    lines = [f'# LinkedIn assets — {post}', '',
             'Every figure and every table is a PNG. LinkedIn articles have no table',
             'element, so a table travels as an image.', '']
    section = None
    for m, name, w, h in rows:
        if m['section'] != section:
            section = m['section']
            lines += ['', f'## {section}', '']
        lines.append(f"- `{name}` — {m['title']}: {m['caption']}  ({w}×{h})")
    (out / 'INDEX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  INDEX.md  ({len(rows)} assets)")


def write_body(page, out, post, rows):
    """A plain page whose prose pastes into the LinkedIn editor as rich text."""
    marks = {m['title']: name for m, name, _, _ in rows}
    body = page.evaluate("""(marks) => {
      const clone = document.querySelector('article').cloneNode(true);
      clone.querySelectorAll('figure.viz, figure.tbl').forEach(f => {
        const t = (f.querySelector('.viz-title')||{}).textContent || '';
        const c = (f.querySelector('h5')||{}).textContent || '';
        const d = document.createElement('p');
        d.className = 'mark';
        d.textContent = `[ UPLOAD IMAGE: ${marks[t] || t} ]  ${t} — ${c}`;
        f.replaceWith(d);
      });
      clone.querySelectorAll('nav, .toc, script, style, .viz-title').forEach(e => e.remove());
      return clone.innerHTML;
    }""", marks)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{post} — LinkedIn paste source</title>
<link rel="icon" href="https://akka.io/favicon.ico" type="image/x-icon">
<style>
  body{{max-width:760px;margin:40px auto;padding:0 24px;background:#fff;color:#111;
       font:16px/1.65 -apple-system,Segoe UI,Roboto,sans-serif;}}
  h1{{font-size:30px;line-height:1.2;}} h2{{font-size:24px;margin-top:34px;}}
  h3{{font-size:19px;margin-top:26px;}}
  .mark{{background:#FFF4CC;border-left:4px solid #E8A800;padding:10px 14px;
         font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:#5A4300;}}
  a{{color:#0a66c2;}}
</style>
</head>
<body>
<p class="mark">Select from the first heading down, copy, and paste into the LinkedIn
article editor. Headings, bold, links and lists survive the paste. Each yellow bar
marks where to upload the named PNG.</p>
{body}
</body>
</html>
"""
    (out / 'article-body.html').write_text(html, encoding='utf-8')
    print('  article-body.html')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('post')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    out = Path(a.out) if a.out else Path(os.path.expanduser('~')) / 'Downloads' / f'li-{a.post}'
    print(f'=== Exporting {a.post} → {out} ===')
    export(a.post, out)
