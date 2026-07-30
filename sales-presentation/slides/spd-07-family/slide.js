/* ── family-platform: reveals + product/component selection ──────────────
   Mirrors the #s-routes behaviour in akka-overview/index.html. The box that
   starts selected comes from the section's data-active, set per deck by the
   registry's "product" key. */
(function () {
  var famObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.15 });
  document.querySelectorAll('.fam-reveal').forEach(function (el) { famObs.observe(el); });

  var root = document.getElementById('family');
  if (!root) return;
  var picks  = root.querySelectorAll('.rt-pick');
  var comps  = root.querySelectorAll('.rt-comp');
  var bodies = root.querySelectorAll('.rt-panel-body');
  if (!picks.length) return;

  /* bodyKey = which summary shows; boxKey = which product box stays lit. */
  function show(bodyKey, boxKey) {
    picks.forEach(function (p) { p.setAttribute('aria-pressed', String(p.dataset.rt === boxKey)); });
    comps.forEach(function (c) { c.setAttribute('aria-pressed', String(c.dataset.comp === bodyKey)); });
    bodies.forEach(function (b) { b.hidden = (b.dataset.rtBody !== bodyKey); });
  }

  picks.forEach(function (p) {
    p.addEventListener('click', function () { show(p.dataset.rt, p.dataset.rt); });
    p.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(p.dataset.rt, p.dataset.rt); }
    });
  });

  comps.forEach(function (c) {
    c.addEventListener('click', function (e) {
      e.stopPropagation();
      show(c.dataset.comp, 'sdk');
    });
    c.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); e.stopPropagation();
        show(c.dataset.comp, 'sdk');
      }
    });
  });

  // This deck's own product starts selected; fall back to Specify.
  var active = root.dataset.active || 'specify';
  if (!root.querySelector('.rt-pick[data-rt="' + active + '"]')) active = 'specify';
  show(active, active);
})();
