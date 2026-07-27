/* ── opt-06-architecture reveals ──────────────────── */
const arcObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
document.querySelectorAll('[data-arc]').forEach(el => arcObs.observe(el));

/* ── opt-06 tap-to-zoom lightbox — keeps the full-fidelity SVG (no mobile redraw) ── */
(function () {
  var wrap = document.getElementById('arc-wrapper');
  if (!wrap) return;
  var srcSvg = wrap.querySelector('.dia svg');
  var hint = wrap.querySelector('.arc-zoomhint');
  if (!srcSvg) return;

  var NW = 1440, NH = 646;                 // svg native viewBox
  var overlay, stage, svg, s = 1, x = 0, y = 0, minS = 0.1, maxS = 6;

  function apply() { svg.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + s + ')'; }
  function fit() {
    var vw = window.innerWidth, vh = window.innerHeight, f = Math.min(vw / NW, vh / NH) * 0.96;
    minS = f * 0.9; s = f; x = (vw - NW * f) / 2; y = (vh - NH * f) / 2; apply();
  }
  function zoomAt(cx, cy, factor) {
    var ns = Math.max(minS, Math.min(maxS, s * factor)), k = ns / s;
    x = cx - (cx - x) * k; y = cy - (cy - y) * k; s = ns; apply();
  }
  function open() { if (!overlay) build(); overlay.classList.add('open'); document.body.style.overflow = 'hidden'; fit(); }
  function close() { if (overlay) overlay.classList.remove('open'); document.body.style.overflow = ''; }

  function build() {
    overlay = document.createElement('div');
    overlay.className = 'arc-zoom';
    overlay.innerHTML =
      '<div class="arc-zoom-bar">' +
        '<button type="button" data-z="out" aria-label="Zoom out">−</button>' +
        '<button type="button" data-z="in" aria-label="Zoom in">+</button>' +
        '<button type="button" data-z="close" aria-label="Close">×</button>' +
      '</div><div class="arc-zoom-stage"></div>';
    stage = overlay.querySelector('.arc-zoom-stage');
    svg = srcSvg.cloneNode(true);
    svg.removeAttribute('style');
    stage.appendChild(svg);
    wrap.appendChild(overlay);

    overlay.querySelector('[data-z=close]').addEventListener('click', close);
    overlay.querySelector('[data-z=in]').addEventListener('click', function () { zoomAt(innerWidth / 2, innerHeight / 2, 1.4); });
    overlay.querySelector('[data-z=out]').addEventListener('click', function () { zoomAt(innerWidth / 2, innerHeight / 2, 1 / 1.4); });

    var pts = new Map(), last = null, pinch = null;
    function pinchState() {
      var a = Array.from(pts.values()), dx = a[1].x - a[0].x, dy = a[1].y - a[0].y;
      return { dist: Math.hypot(dx, dy) || 1, mx: (a[0].x + a[1].x) / 2, my: (a[0].y + a[1].y) / 2 };
    }
    stage.addEventListener('pointerdown', function (e) {
      stage.setPointerCapture(e.pointerId);
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size === 2) { pinch = pinchState(); last = null; } else last = { x: e.clientX, y: e.clientY };
    });
    stage.addEventListener('pointermove', function (e) {
      if (!pts.has(e.pointerId)) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size >= 2 && pinch) {
        var p = pinchState();
        zoomAt(p.mx, p.my, p.dist / pinch.dist);
        x += p.mx - pinch.mx; y += p.my - pinch.my; apply(); pinch = p;
      } else if (last) {
        x += e.clientX - last.x; y += e.clientY - last.y; last = { x: e.clientX, y: e.clientY }; apply();
      }
    });
    function endPtr(e) {
      pts.delete(e.pointerId);
      if (pts.size < 2) pinch = null;
      if (pts.size === 1) { var v = pts.values().next().value; last = { x: v.x, y: v.y }; }
      else if (pts.size === 0) last = null;
    }
    stage.addEventListener('pointerup', endPtr);
    stage.addEventListener('pointercancel', endPtr);
    stage.addEventListener('wheel', function (e) { e.preventDefault(); zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.12 : 1 / 1.12); }, { passive: false });
  }

  if (hint) hint.addEventListener('click', open);
  srcSvg.addEventListener('click', function () { if (window.matchMedia('(max-width:820px)').matches) open(); });
  window.addEventListener('resize', function () { if (overlay && overlay.classList.contains('open')) fit(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
})();
