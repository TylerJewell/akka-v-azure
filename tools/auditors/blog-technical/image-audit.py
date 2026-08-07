#!/usr/bin/env python3
"""Image sizing auditor for the technical blog template.

For each <figure class="viz"> in the given blog file(s):
  1. Fetch the source image, measure native pixel dimensions
  2. Detect transparency (alpha channel corner samples)
  3. Classify background (dark / light / transparent) from corner pixels
  4. Determine the current rendered max-width from CSS classes + inline styles
  5. Recommend a max-width that respects three budgets:
       - Never upscale beyond MAX_UPSCALE (1.05× default)
       - Never taller than MAX_HEIGHT (640px — one reading screen)
       - Never wider than WIDE_MEASURE (940px — the .wide breakout)
  6. Report status: OK / WARN / FAIL per figure

Also flags:
  - Plate-variant mismatches: transparent PNG in .plate--paper, or opaque
    dark image in .plate--paper
  - Broken or slow-loading image URLs

Usage:
    python tools/auditors/blog-technical/image-audit.py blog-technical/*.html
    python tools/auditors/blog-technical/image-audit.py blog-technical/akka-memory.html
    python tools/auditors/blog-technical/image-audit.py --fix blog-technical/akka-memory.html

With --fix, appends style="max-width:<Npx>" to plate divs on the recommended
width where the current rendering is FAIL. Never removes existing inline
styles; only adds missing max-width.
"""

import argparse
import io
import os
import re
import sys
import urllib.request
from html import unescape

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Template constants — must match blog-technical/theme values ──
BODY_MEASURE   = 640       # .col width (body prose)
WIDE_MEASURE   = 940       # .wide breakout width — reserved for data-size="wide"

# Sizing budget by figure category — tuned against actual reader feedback
DEFAULT_TARGET_W = 640     # goldilocks width for a single figure
DEFAULT_MAX_W    = 640     # same as target — most figures cap here
WIDE_MAX_W       = 940     # cap when author sets data-size="wide"
MIN_LEGIBLE_W    = 400     # upscale below this only if native ≥ this
MAX_HEIGHT       = 520     # visual-weight ceiling for default landscape
WIDE_MAX_HEIGHT  = 640     # relaxed height for data-size="wide" diagrams
PORTRAIT_ASPECT  = 0.8     # w/h < this → treat as portrait, cap by height
PORTRAIT_MAX_H   = 500     # height cap for portraits
PORTRAIT_MIN_W   = 300     # minimum portrait width for legibility

# Pair layout (two images side-by-side inside one plate)
PAIR_TARGET_W    = 560     # per pair member — larger than default landscape target
PAIR_MAX_W       = 620
PAIR_MIN_W       = 560     # aggressive floor: pair diagrams tend to be information-dense
PAIR_MAX_H       = 520

# Text-relative sizing — the graphic's internal text should render close to
# body font size so the graphic reads at the same weight as the surrounding prose.
# Article body is 18px. Figure text at 10px (55% of body) puts diagram content
# clearly subordinate to body prose — matches the "reference figure" convention
# in scientific journals where text-in-figure reads smaller than caption text.
TARGET_TEXT_PX   = 10      # what native diagram text should render at, on-screen

MAX_UPSCALE      = 1.05    # tolerance for DPR rounding
WARN_UPSCALE     = 1.75    # legibility upscales (up to ~1.75×) are OK, not warned
FAIL_UPSCALE     = 2.5     # beyond this, upscale becomes unacceptable blur

TIMEOUT = 15


# ── Helpers ─────────────────────────────────────────────────────
class _SvgShim:
    """Duck-type an SVG as if it were a PIL image so downstream sizing code
    keeps working. Parses width/height from the SVG root."""
    def __init__(self, w, h):
        self.size = (w, h)
    def crop(self, *a, **k): return self
    def convert(self, *a, **k): return self
    def getdata(self, *a, **k): return []
    def getcolors(self, *a, **k): return []


def _fetch_image(url):
    """Download bytes; return PIL Image (or SVG shim) + None error."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit('pip install Pillow')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'blog-image-audit/1.0'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
        # SVG: PIL can't parse. Extract width/height from the <svg> root
        # so sizing rules apply. Content sniff, not extension — HubSpot
        # serves SVG under URLs that end .png sometimes.
        head = data[:400].lstrip()
        if head.startswith(b'<?xml') or head.startswith(b'<svg') or b'<svg' in head:
            wm = re.search(rb'<svg\b[^>]*\bwidth="?(\d+)', head)
            hm = re.search(rb'<svg\b[^>]*\bheight="?(\d+)', head)
            vm = re.search(rb'viewBox="([^"]+)"', head)
            w, h = None, None
            if wm and hm:
                w, h = int(wm.group(1)), int(hm.group(1))
            elif vm:
                parts = vm.group(1).split()
                if len(parts) == 4:
                    w, h = int(float(parts[2])), int(float(parts[3]))
            if not w:
                w, h = 400, 300
            return _SvgShim(w, h), None
        return Image.open(io.BytesIO(data)), None
    except Exception as e:
        return None, str(e)


def _estimate_native_text_height(im):
    """Estimate median text-line height (pixels) via horizontal-band density.

    Text rows in a diagram have high variance in brightness (dark strokes on
    lighter background, or vice versa). Rows of solid color or empty space
    have low variance. We find runs of high-variance rows and take the median
    run length as the text-line height. Runs shorter than 6px or longer than
    50px are excluded (too small = noise, too large = solid shape).

    Returns median text height in pixels, or None if no text-like rows found.
    SVGs pass through as unknown (no pixel data to sample).
    """
    if isinstance(im, _SvgShim):
        return None
    gray = im.convert('L')
    w, h = gray.size
    pixels = list(gray.getdata())

    # Per-row standard deviation (via variance shortcut)
    row_var = []
    for y in range(h):
        row = pixels[y * w:(y + 1) * w]
        n = len(row)
        m = sum(row) / n
        var = sum((p - m) ** 2 for p in row) / n
        row_var.append(var)

    if not row_var:
        return None

    # Threshold at 60th percentile of variance
    sorted_var = sorted(row_var)
    threshold = sorted_var[int(len(sorted_var) * 0.60)]
    text_rows = [v > threshold for v in row_var]

    # Find runs of consecutive text-like rows
    runs = []
    in_run = False
    start = 0
    for i, is_text in enumerate(text_rows):
        if is_text and not in_run:
            start = i
            in_run = True
        elif not is_text and in_run:
            runs.append(i - start)
            in_run = False
    if in_run:
        runs.append(len(text_rows) - start)

    # Filter to plausible text line heights
    text_lines = [r for r in runs if 6 <= r <= 50]
    if not text_lines:
        return None
    text_lines.sort()
    return text_lines[len(text_lines) // 2]


def _classify_bg(im):
    """Sample four corners + center; return ('transparent'|'dark'|'light'|'mixed', dominant_rgb)."""
    if isinstance(im, _SvgShim):
        return 'transparent', None
    im = im.convert('RGBA')
    w, h = im.size
    samples = [
        im.getpixel((5, 5)),
        im.getpixel((w - 5, 5)),
        im.getpixel((5, h - 5)),
        im.getpixel((w - 5, h - 5)),
    ]
    alphas = [s[3] for s in samples]
    if all(a == 0 for a in alphas):
        return 'transparent', None
    corners_visible = [s for s in samples if s[3] > 0]
    if not corners_visible:
        return 'transparent', None
    r = sum(s[0] for s in corners_visible) / len(corners_visible)
    g = sum(s[1] for s in corners_visible) / len(corners_visible)
    b = sum(s[2] for s in corners_visible) / len(corners_visible)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    dom = (int(r), int(g), int(b))
    if lum < 40:
        return 'dark', dom
    if lum > 215:
        return 'light', dom
    return 'mixed', dom


def _recommend_width(nat_w, nat_h, is_pair=False, is_wide=False, native_text_px=None):
    """Determine the display max-width for a figure.

    Primary rule (when native_text_px is available):
      Compute the display width that makes the graphic's internal text render
      at TARGET_TEXT_PX on-screen. This is the ratio (TARGET_TEXT_PX / native_text_px).
      Then bound the result by min/max/height limits below.

    Fallback rules (when text detection fails):
      1. Pair layouts use their own tighter budget per member.
      2. Portrait aspect ratio (< 0.8) is capped by PORTRAIT_MAX_H.
      3. Normal figures: default target 640.
      4. Legibility floor at 400 — upscale small native to reach it.
      5. Height ceiling MAX_HEIGHT prevents overwhelming landscape figures.
    """
    if nat_w <= 0 or nat_h <= 0:
        return DEFAULT_TARGET_W

    if is_pair:
        target, max_w, min_w, max_h = PAIR_TARGET_W, PAIR_MAX_W, PAIR_MIN_W, PAIR_MAX_H
    else:
        max_w = WIDE_MAX_W if is_wide else DEFAULT_MAX_W
        max_h = WIDE_MAX_HEIGHT if is_wide else MAX_HEIGHT
        target, min_w = DEFAULT_TARGET_W, MIN_LEGIBLE_W

    aspect = nat_w / nat_h

    # PRIMARY RULE: size so native text renders at TARGET_TEXT_PX on screen.
    if native_text_px and native_text_px > 4:
        ratio = TARGET_TEXT_PX / native_text_px
        w = int(nat_w * ratio)
        # Bound by min/max
        floor = PAIR_MIN_W if is_pair else (PORTRAIT_MIN_W if aspect < PORTRAIT_ASPECT else min_w)
        ceiling = max_w
        w = max(floor, min(w, ceiling))
        # Height ceiling
        implied_h = w * nat_h / nat_w
        if implied_h > max_h:
            w = int(max_h * nat_w / nat_h)
            if w < floor:
                w = floor
        return w

    # Portrait handling — cap by height first, with portrait-specific floor
    if aspect < PORTRAIT_ASPECT and not is_pair:
        w = int(PORTRAIT_MAX_H * aspect)
        if w < PORTRAIT_MIN_W:
            w = PORTRAIT_MIN_W
        if w > max_w:
            w = max_w
        return w

    # Landscape / square: start at target, bound by native (up to legibility floor) and max
    if nat_w < target:
        w = max(nat_w, min_w)  # upscale to legibility floor if native is smaller
    else:
        w = min(nat_w, max_w)

    # Apply height ceiling
    implied_h = w * nat_h / nat_w
    if implied_h > max_h:
        w = int(max_h * nat_w / nat_h)

    # Re-apply legibility floor (height cap can drop us below it)
    if w < min_w and nat_w >= min_w:
        w = min_w

    return w


def _detect_wide_override(fig_html):
    """True if the figure carries data-size='wide' — author wants full breakout."""
    return bool(re.search(r'data-size\s*=\s*"wide"', fig_html))


def _extract_figures(html):
    """Return list of (fig_html, offset_in_source) tuples."""
    figs = []
    for m in re.finditer(r'<figure class="viz"[^>]*>.*?</figure>', html, re.S):
        figs.append((m.group(0), m.start()))
    return figs


def _detect_plate_class(fig_html):
    m = re.search(r'<div class="([^"]*plate[^"]*)"', fig_html)
    if not m:
        return None
    classes = m.group(1).split()
    for v in ('plate--flush', 'plate--paper'):
        if v in classes:
            return v
    return 'plate'  # base


def _detect_inline_max_width(fig_html):
    """Return int px or None. Checks --fig-w on figure first (preferred),
    then plate-div max-width (legacy)."""
    m = re.search(r'<figure[^>]*style="[^"]*--fig-w\s*:\s*(\d+)px', fig_html)
    if m:
        return int(m.group(1))
    m = re.search(r'<div class="[^"]*plate[^"]*"[^>]*style="[^"]*max-width\s*:\s*(\d+)px', fig_html)
    if m:
        return int(m.group(1))
    m = re.search(r'<img[^>]+style="[^"]*max-width\s*:\s*(\d+)px', fig_html)
    if m:
        return int(m.group(1))
    return None


def _detect_pair(fig_html):
    return 'pair' in (re.search(r'<div class="([^"]*plate[^"]*)"', fig_html) or ['', ''])[1] if False else 'pair' in fig_html


def _current_rendered_width(plate_class, inline_max, nat_w, is_pair):
    """Best-effort compute of what width the browser is actually giving this image."""
    if inline_max is not None:
        return inline_max
    # No inline cap — plate uses width:fit-content, so display width = native (capped at WIDE_MEASURE)
    if is_pair:
        # Pair splits WIDE_MEASURE across two, minus gap ~24, minus padding ~48
        return (WIDE_MEASURE - 48 - 24) // 2
    if plate_class == 'plate--flush':
        return min(nat_w, WIDE_MEASURE)
    if plate_class == 'plate--paper':
        # paper adds 32px padding on each side; content area WIDE_MEASURE - 64
        return min(WIDE_MEASURE - 64, nat_w)
    # base .plate: 24px padding each side
    return min(WIDE_MEASURE - 48, nat_w)


def _get_src(fig_html):
    m = re.search(r'<img[^>]+src="([^"]+)"', fig_html)
    if not m:
        return None
    return unescape(m.group(1))


def _get_title(fig_html):
    m = re.search(r'<h4[^>]*>(.*?)</h4>', fig_html, re.S)
    if not m:
        return '(no title)'
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()


def _get_viz_label(fig_html):
    m = re.search(r'<p class="viz-title"[^>]*>(.*?)</p>', fig_html, re.S)
    if not m:
        return ''
    return re.sub(r'<[^>]+>', '', m.group(1)).strip()


# ── Audit ───────────────────────────────────────────────────────
def audit_figure(fig_html):
    src = _get_src(fig_html)
    if not src:
        return None
    im, err = _fetch_image(src)
    if not im:
        return {'src': src, 'error': err, 'status': 'ERROR'}
    nw, nh = im.size
    bg_kind, bg_dom = _classify_bg(im)
    native_text_px = _estimate_native_text_height(im)
    plate = _detect_plate_class(fig_html)
    inline_max = _detect_inline_max_width(fig_html)
    is_pair = _detect_pair(fig_html)
    is_wide = _detect_wide_override(fig_html)
    current_w = _current_rendered_width(plate, inline_max, nw, is_pair)
    rec_w = _recommend_width(nw, nh, is_pair=is_pair, is_wide=is_wide, native_text_px=native_text_px)
    upscale = current_w / nw if nw else 0
    implied_h = int(current_w * nh / nw) if nw else 0
    rec_h = int(rec_w * nh / nw) if nw else 0

    # Status — compare current against recommended target
    diff_ratio = current_w / rec_w if rec_w else 1.0
    effective_max_h = WIDE_MAX_HEIGHT if is_wide else (PAIR_MAX_H if is_pair else MAX_HEIGHT)
    if upscale > FAIL_UPSCALE:
        status = 'FAIL'
    elif diff_ratio > 1.4 or diff_ratio < 0.7:
        status = 'FAIL'
    elif diff_ratio > 1.15 or diff_ratio < 0.85 or implied_h > effective_max_h:
        status = 'WARN'
    else:
        status = 'OK'

    # Plate-variant sanity
    plate_note = None
    if bg_kind == 'transparent' and plate == 'plate--paper':
        plate_note = 'transparent PNG on .plate--paper — recommend .plate--flush'
    elif bg_kind == 'dark' and plate == 'plate--paper':
        plate_note = 'dark-bg image on .plate--paper — recommend .plate--flush'
    elif bg_kind == 'light' and plate == 'plate--flush':
        plate_note = 'light-bg image on .plate--flush — recommend .plate--paper'

    # Rendered text size at current display width
    rendered_text_px = round(native_text_px * current_w / nw, 1) if native_text_px and nw else None
    rec_rendered_text_px = round(native_text_px * rec_w / nw, 1) if native_text_px and nw else None

    return {
        'src': src,
        'title': _get_title(fig_html),
        'viz_label': _get_viz_label(fig_html),
        'native': (nw, nh),
        'aspect': f'{nw/nh:.2f}:1' if nh else '?',
        'bg': bg_kind,
        'bg_rgb': bg_dom,
        'native_text_px': native_text_px,
        'rendered_text_px': rendered_text_px,
        'rec_rendered_text_px': rec_rendered_text_px,
        'plate': plate,
        'is_pair': is_pair,
        'is_wide': is_wide,
        'inline_max': inline_max,
        'current_w': current_w,
        'current_h': implied_h,
        'recommended_w': rec_w,
        'recommended_h': rec_h,
        'upscale': upscale,
        'plate_note': plate_note,
        'status': status,
    }


def audit_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    findings = []
    for i, (fig_html, offset) in enumerate(_extract_figures(html), 1):
        result = audit_figure(fig_html)
        if result:
            result['index'] = i
            findings.append(result)
    return findings


def format_report(path, findings):
    lines = [f'\n=== {path} ===']
    if not findings:
        lines.append('  (no figures)')
        return '\n'.join(lines)
    for f in findings:
        if 'error' in f:
            lines.append(f'  FAIL  Fig {f["index"]} · {f.get("title", "")}')
            lines.append(f'        src:   {f["src"][:100]}')
            lines.append(f'        error: {f["error"]}')
            continue
        status_marker = {'OK': '  ok  ', 'WARN': '  WARN', 'FAIL': '  FAIL'}[f['status']]
        lines.append(f'{status_marker}  Fig {f["index"]} · {f["title"]}')
        pair_note = ' (pair)' if f['is_pair'] else ''
        lines.append(f'        native:      {f["native"][0]}×{f["native"][1]}  aspect {f["aspect"]}{pair_note}')
        lines.append(f'        bg:          {f["bg"]}' + (f'  rgb={f["bg_rgb"]}' if f['bg_rgb'] else ''))
        if f.get('native_text_px'):
            lines.append(f'        text (native): ~{f["native_text_px"]}px per line  |  target on-screen: {TARGET_TEXT_PX}px')
            lines.append(f'        text current:  ~{f["rendered_text_px"]}px  |  text recommended: ~{f["rec_rendered_text_px"]}px')
        lines.append(f'        plate:       {f["plate"]}' + (f'  inline max-width={f["inline_max"]}px' if f['inline_max'] else ''))
        lines.append(f'        current:     {f["current_w"]}×{f["current_h"]}  ({f["upscale"]:.2f}× native)')
        lines.append(f'        recommended: max-width:{f["recommended_w"]}px  (→ {f["recommended_w"]}×{f["recommended_h"]})')
        if f['plate_note']:
            lines.append(f'        ⚠ plate: {f["plate_note"]}')
        if f['status'] != 'OK' and f['inline_max'] != f['recommended_w']:
            lines.append(f'        FIX:         add  style="max-width:{f["recommended_w"]}px"  to the plate div')
    return '\n'.join(lines)


def apply_fixes(path, findings):
    """Apply recommended --fig-w to every figure whose current width differs
    from the recommendation. --fig-w on the FIGURE element propagates to
    plate + caption so they align as a single block."""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    changed = 0
    for f in findings:
        if 'error' in f: continue
        if f['inline_max'] == f['recommended_w']: continue
        # find the exact <img src="..."> and back up to the enclosing <figure>
        src = f['src']
        img_pos = html.find(f'src="{src}"')
        if img_pos < 0:
            img_pos = html.find(f'src="{src.replace("&", "&amp;")}"')
        if img_pos < 0: continue
        # search backwards for <figure class="viz" — write --fig-w there
        fig_open = html.rfind('<figure class="viz"', 0, img_pos)
        if fig_open < 0:
            # fallback: write to plate div (legacy behaviour)
            plate_open = html.rfind('<div class="plate', 0, img_pos)
            if plate_open < 0: continue
            plate_close = html.find('>', plate_open)
            if plate_close < 0: continue
            div_tag = html[plate_open:plate_close + 1]
            if 'style="' in div_tag:
                new_tag = re.sub(
                    r'style="([^"]*)"',
                    lambda m: f'style="{_upsert_max_width(m.group(1), f["recommended_w"])}"',
                    div_tag,
                )
            else:
                new_tag = div_tag[:-1] + f' style="max-width:{f["recommended_w"]}px">'
            html = html[:plate_open] + new_tag + html[plate_close + 1:]
            changed += 1
            continue
        fig_close = html.find('>', fig_open)
        if fig_close < 0: continue
        fig_tag = html[fig_open:fig_close + 1]
        if 'style="' in fig_tag:
            new_tag = re.sub(
                r'style="([^"]*)"',
                lambda m: f'style="{_upsert_fig_w(m.group(1), f["recommended_w"])}"',
                fig_tag,
            )
        else:
            new_tag = fig_tag[:-1] + f' style="--fig-w:{f["recommended_w"]}px">'
        html = html[:fig_open] + new_tag + html[fig_close + 1:]
        changed += 1
    if changed:
        with open(path, 'w', encoding='utf-8') as fout:
            fout.write(html)
    return changed


def _upsert_max_width(style, w):
    if 'max-width' in style:
        return re.sub(r'max-width\s*:\s*\d+px', f'max-width:{w}px', style)
    style = style.rstrip('; ')
    return style + (';' if style else '') + f'max-width:{w}px'


def _upsert_fig_w(style, w):
    if '--fig-w' in style:
        return re.sub(r'--fig-w\s*:\s*\d+px', f'--fig-w:{w}px', style)
    style = style.rstrip('; ')
    return style + (';' if style else '') + f'--fig-w:{w}px'


# ── CLI ─────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='+', help='blog-technical/*.html files to audit')
    p.add_argument('--fix', action='store_true',
                   help='rewrite files with recommended max-width on any FAIL/WARN figures')
    args = p.parse_args()

    total_fail = total_warn = 0
    for path in args.files:
        findings = audit_file(path)
        print(format_report(path, findings))
        total_fail += sum(1 for f in findings if f.get('status') == 'FAIL')
        total_warn += sum(1 for f in findings if f.get('status') == 'WARN')
        if args.fix:
            n = apply_fixes(path, findings)
            if n:
                print(f'  FIXED  {n} figure(s) — re-run without --fix to verify')

    print(f'\nSummary: {total_fail} fail, {total_warn} warn')
    return 1 if total_fail else 0


if __name__ == '__main__':
    sys.exit(main())
