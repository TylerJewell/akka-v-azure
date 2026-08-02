"""Assemble a new overview deck by combining:
  - existing sections from akka-overview/index.html (kept as-is)
  - three new sections from the scratchpad previews (thesis, agentic-platform, four-efficiencies)

Order: s-title -> s-thesis -> s-agentic-platform -> s-eff ->
       s-proof -> s-platform -> s6 -> s-packages -> s-routes -> s-close
"""

import re
import pathlib

# Resolve paths relative to this script so it runs on any machine after a
# `git clone`. `SCRATCH` is _internal/overview-redesign/, siblings of the
# assembly script. The base overview lives at ../../akka-overview/index.html.
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = HERE
REPO = HERE.parent.parent
BASE_SOURCE = REPO / "akka-overview" / "index.html"

BASE = SCRATCH / "overview-new.html"
THESIS = SCRATCH / "thesis-preview.html"
PLATFORM = SCRATCH / "platform-preview.html"
EFF = SCRATCH / "four-efficiencies-preview.html"

# Fresh copy of the base overview HTML at the start of each run — the script
# mutates BASE in place, so we always start from the source of truth.
BASE.write_text(BASE_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")

def read(p): return p.read_text(encoding="utf-8")

base = read(BASE)
thesis = read(THESIS)
platform = read(PLATFORM)
eff = read(EFF)

# --- extract <style>...</style> body from each preview ---
def css_body(html: str) -> str:
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    return m.group(1).strip() if m else ""

# --- extract <section ...>...</section> for a given id from a preview ---
def section(html: str, sid: str) -> str:
    # match <section id="{sid}" ...> ... </section>  (non-greedy, DOTALL)
    pattern = r'<section id="' + re.escape(sid) + r'"[^>]*>.*?</section>'
    m = re.search(pattern, html, re.DOTALL)
    return m.group(0) if m else ""

thesis_css = css_body(thesis)
platform_css = css_body(platform)
eff_css = css_body(eff)

# Strip common CSS from previews (globals like *, html, body, section, .inner, ::before, .accent, .pos, .neg)
# — these are already defined in the base overview file, and duplicating causes conflicts.
def strip_globals(css: str) -> str:
    # Remove blocks that redefine base-file globals. Each pattern uses a
    # negative lookbehind so it only matches the bare selector (not a
    # compound selector that happens to end in the same word).
    #
    # Bug fixed: `body\{...\}` was matching `.eff-body{...}` and stripping it,
    # which is why the four-efficiencies body copy was rendering with default
    # white instead of the intended muted grey. The lookbehind fixes that.
    patterns = [
        r"\*,\*::before,\*::after\{[^}]*\}",
        r":root\{[^}]*\}",
        r"(?<![\w\-])html\{[^}]*\}",
        r"(?<![\w\-])body\{[^}]*\}",
        r"(?<![\w\-])section\{[^}]*\}",
        r"(?<![\w\-])\.inner\{[^}]*\}",
        r"(?<![\w\-])section::before\{[^}]*\}",
        r"(?<![\w\-])\.accent\{[^}]*\}",
        r"(?<![\w\-])\.pos\{[^}]*\}",
        r"(?<![\w\-])\.neg\{[^}]*\}",
    ]
    for pat in patterns:
        css = re.sub(pat, "", css)
    return css

thesis_css = strip_globals(thesis_css)
platform_css = strip_globals(platform_css)
eff_css = strip_globals(eff_css)

# --- extract sections ---
sec_thesis   = section(thesis, "s-thesis")
sec_platform = section(platform, "s-platform")
sec_eff      = section(eff, "s-eff")

# Rename platform preview's section id to avoid clashing with the existing
# integrated-diagram slide, which also uses #s-platform in the base file.
sec_platform = sec_platform.replace('id="s-platform"', 'id="s-akka-platform"', 1)
platform_css = platform_css.replace("#s-platform", "#s-akka-platform")
# Also rename #audit-panel and #audit-overlay usages if present — but we don't
# want the audit overlay leaking into the full deck. Strip them from CSS.
platform_css = re.sub(r"#audit-panel.*?\n", "", platform_css)
platform_css = re.sub(r"#audit-overlay.*?\n", "", platform_css)
platform_css = re.sub(r"body\.audit-on.*?\n", "", platform_css)

# For thesis: also strip audit CSS
thesis_css = re.sub(r"#audit-panel.*?\n", "", thesis_css)
thesis_css = re.sub(r"#audit-overlay.*?\n", "", thesis_css)
thesis_css = re.sub(r"body\.audit-on.*?\n", "", thesis_css)

# For eff: strip audit CSS
eff_css = re.sub(r"#audit-panel.*?\n", "", eff_css)
eff_css = re.sub(r"#audit-overlay.*?\n", "", eff_css)
eff_css = re.sub(r"body\.audit-on.*?\n", "", eff_css)

# --- inject CSS into base file's <style> block, just before </style> ---
new_css = f"""
/* ==================== NEW SLIDES CSS ==================== */
/* Thesis slide (three-column supply/demand/constraint) */
{thesis_css}

/* Akka Agentic AI Platform slide (renamed from #s-platform to #s-akka-platform) */
{platform_css}

/* Four efficiencies slide */
{eff_css}
/* ================================================================= */
"""

# Overrides — the base file's #s-morph animation defined `.pf-msg .seg{opacity:0}`
# and `.morph-right .pf-msg{opacity:0}` globally. Because the new
# #s-akka-platform slide reuses the same .pf-msg / .seg classes for its
# right-hand copy, those rules would hide our new slide's text until the
# (nonexistent) morph animation fires. Force it visible via higher-specificity
# selectors scoped to the new slide.
overrides = """
/* ---- overrides for the new agentic-platform slide ---- */
/* The base file's #s-morph animation hides .pf-msg / .seg by default. Force
   them visible on the new slide, which reuses the same class names. */
#s-akka-platform .pf-msg{opacity:1 !important; pointer-events:auto !important;}
#s-akka-platform .pf-msg .seg{opacity:1 !important;}

/* The base file also defines an unscoped .cake-wrap with border + background
   tint. Strip it here so the new slide's cake sits directly on the page. */
#s-akka-platform .cake-wrap{border:none !important; background:none !important; box-shadow:none !important; padding:0 !important;}

/* Right-side body copy sized up so the four paragraphs read at roughly the
   same total height as the cake box on the left. */
#s-akka-platform .pf-msg p{font-size:clamp(18px,1.55vw,24px); line-height:1.6;}
#s-akka-platform .pf-msg .seg{margin-bottom:18px;}
#s-akka-platform .pf-msg .seg:last-child{margin-bottom:0;}
"""

# Insert new_css just before the first </style>
base = re.sub(r"</style>", new_css + overrides + "\n</style>", base, count=1)

# --- remove old #s-morph section (replaced by thesis + agentic-platform) ---
base = re.sub(r'<section id="s-morph">.*?</section>\s*', '', base, count=1, flags=re.DOTALL)

# --- remove old #s-scale section (replaced by four-efficiencies) ---
# Handle possible surrounding whitespace/blank lines
base = re.sub(r'<section id="s-scale">.*?</section>\s*', '', base, count=1, flags=re.DOTALL)

# --- inject new sections in order after #s-title, before #s-proof ---
new_sections = f"""
{sec_thesis}

{sec_platform}

{sec_eff}

"""

# Insert immediately after </section> that closes #s-title.
# The base structure has: <section id="s-title">...</section> followed by other sections.
# We'll insert right before <section id="s-proof">.
base = re.sub(r'(<section id="s-proof">)', new_sections + r'\1', base, count=1)

# Reorder: move the existing "An integrated platform" slide (#s-platform, the
# wide architecture diagram) to sit immediately after the new #s-akka-platform
# slide, so the two platform slides are adjacent.
m_plat = re.search(r'<section id="s-platform">.*?</section>\s*', base, re.DOTALL)
if m_plat:
    plat_html = m_plat.group(0)
    # remove from its current spot
    base = base.replace(plat_html, '', 1)
    # insert immediately after the </section> that closes #s-akka-platform
    def _insert_after_akka(match):
        return match.group(0) + plat_html
    base = re.sub(
        r'(<section id="s-akka-platform"[^>]*>.*?</section>\s*)',
        _insert_after_akka,
        base,
        count=1,
        flags=re.DOTALL,
    )

# Strip any leftover audit-panel divs or script blocks that were inside preview sections
# (they may have been extracted with the section; remove them cleanly)
base = re.sub(r'<div id="audit-panel">.*?</div>\s*', '', base, flags=re.DOTALL)
base = re.sub(r'<div id="audit-overlay"></div>\s*', '', base)
base = re.sub(r'<script>[^<]*?function runAudit.*?</script>\s*', '', base, flags=re.DOTALL)

# Also strip the section-click JS from platform preview (state-2 click reveal)
# — we don't need click interaction in the final deck since state-2 IS the default.
base = re.sub(r'<script>\s*const section = document\.getElementById\([\'"]s-platform[\'"]\).*?</script>\s*',
              '', base, flags=re.DOTALL)
base = re.sub(r'<script>\s*const section = document\.getElementById\([\'"]s-akka-platform[\'"]\).*?</script>\s*',
              '', base, flags=re.DOTALL)

# --- semantic-memory arrow fix on the existing s-platform slide ---
# The "integrations" wire is drawn to the whole #rsc-deps container, which
# means its y coordinate lands on the vertical centre of the container (near
# the title + top chip). We want the arrowhead to hit the middle chip,
# "Semantic memory". Two edits: give that chip its own id, and re-target the
# wire.
base = base.replace(
    '<div class="chip frame">Semantic memory</div>',
    '<div class="chip frame" id="rsc-sem">Semantic memory</div>'
)
base = base.replace(
    "{from:'.platform',      to:'#rsc-deps',    label:'integrations'}",
    "{from:'.platform',      to:'#rsc-sem',     label:'integrations'}"
)

# Write output
out = SCRATCH / "overview-new.html"
out.write_text(base, encoding="utf-8")
print(f"Written {out} ({len(base)} chars, {base.count(chr(10))} lines)")

# Report the section order in the output
sections = re.findall(r'<section id="([^"]+)"', base)
print(f"Sections in output: {sections}")
