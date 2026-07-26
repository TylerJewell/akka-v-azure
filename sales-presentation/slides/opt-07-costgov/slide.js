/* ── opt-07-costgov — pinned header + scroll-reveal of the dashboard rows ── */
(function () {
  var wrap = document.getElementById('cog-wrapper');
  if (!wrap) return;
  var track = wrap.querySelector('.cog-track');
  var stage = track ? track.parentElement : null;

  /* subtle "scroll to explore" hint on the pinned slide, fades once the rows start moving */
  var sticky = document.getElementById('cog-sticky');
  var hint = null;
  if (sticky) {
    hint = document.createElement('div');
    hint.className = 'cog-hint';
    hint.innerHTML = 'scroll to explore<i></i>';
    sticky.appendChild(hint);
  }

  /* fade-in the header + column titles as the section enters */
  var cogObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  wrap.querySelectorAll('[data-cog]').forEach(function (el) { cogObs.observe(el); });

  if (!track || !stage) return;

  var maxShift = 0, revealDist = 1, startBuf = 0;
  function clamp(x) { return Math.max(0, Math.min(1, x)); }

  function layout() {
    if (window.innerWidth <= 1000) { wrap.style.height = ''; track.style.transform = ''; return; }
    maxShift = Math.max(0, track.scrollHeight - stage.clientHeight);
    revealDist = Math.max(1, maxShift * 1.35);
    startBuf = window.innerHeight * 0.10;               /* anchor the header before the rows move */
    var dwell = window.innerHeight * 0.45;              /* hold at the end so the last rows can be read */
    wrap.style.height = (window.innerHeight + startBuf + revealDist + dwell) + 'px';
  }
  function frame() {
    if (window.innerWidth <= 1000) { if (hint) hint.style.opacity = '0'; return; }
    var p = clamp((window.scrollY - wrap.offsetTop - startBuf) / revealDist);
    track.style.transform = 'translateY(' + (-p * maxShift) + 'px)';
    if (hint) hint.style.opacity = (p > 0.02) ? '0' : '1';
  }

  window.addEventListener('scroll', frame, { passive: true });
  window.addEventListener('resize', function () { layout(); frame(); });
  window.addEventListener('load', function () { layout(); frame(); });
  layout(); frame();
})();
