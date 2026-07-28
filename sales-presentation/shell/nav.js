const views = [
    'title','hero-wrapper','st-wrapper','stax-wrapper','s2-wrapper','s4-wrapper',
    'spec-wrapper','platform-pattern-wrapper','s6b-wrapper','s13-wrapper',
    's5-wrapper','s6-wrapper','s7-problem','s7-answer-frame','cust-wrapper',
    'pkg-wrapper','spwhat-wrapper','closing'
  ].map(function(id){ return document.getElementById(id); }).filter(Boolean);

  function docTop(el){
    return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
  }
  var HDR = 78;
  function currentIndex() {
    var y = (window.scrollY || window.pageYOffset) + HDR + 4;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (docTop(views[i]) <= y) best = i;
    }
    return best;
  }
  function goTo(i) {
    if (i < 0 || i >= views.length) return;
    window.scrollTo({ top: Math.max(0, docTop(views[i]) - HDR), behavior: 'smooth' });
  }
  function navNext() { goTo(currentIndex() + 1); }
  function navPrev() { goTo(currentIndex() - 1); }
  function handleNavKey(key) {
    if (key === 'ArrowRight' || key === 'PageDown') navNext();
    else if (key === 'ArrowLeft' || key === 'PageUp') navPrev();
  }
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' ||
        e.key === 'ArrowLeft'  || e.key === 'PageUp') {
      e.preventDefault();
      handleNavKey(e.key);
    }
  });
  // Iframe slides forward nav keys via postMessage
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'akka-deck-nav' && e.data.key) {
      handleNavKey(e.data.key);
    }
  });
})();

/* ── Overview deck motion — behaviour only; content and positions unchanged.
   Counts static stat numbers, grows the upgrade-path connectors, and draws the
   architecture connector lines as each slide reveals. Reveal-once on scroll-in.
   Slides that already self-animate (hero counters, use-case counters, spec/flow
   draws) are intentionally left untouched. ── */
(function(){
  function growBars(root, sel){
    root.querySelectorAll(sel).forEach(function(b){
      b.style.transformOrigin = 'left center';
      b.style.transition = 'none';
      b.style.transform = 'scaleX(0)';
      void b.offsetWidth;
      b.style.transition = 'transform .85s cubic-bezier(.16,1,.3,1)';
      b.style.transform = 'scaleX(1)';
    });
  }

  function countUp(root, sel, opts){
    opts = opts || {};
    root.querySelectorAll(sel).forEach(function(el){
      var full = el.textContent;
      var nums = full.match(/\d[\d,]*\.?\d*/g);
      if (!nums || nums.length !== 1) return;          /* single number only, so ranges/ratios stay intact */
      var raw = nums[0], clean = raw.replace(/,/g, '');
      var target = parseFloat(clean);
      if (isNaN(target) || target === 0) return;
      var dec = (clean.split('.')[1] || '').length, comma = /,/.test(raw);
      var idx = full.indexOf(raw), pre = full.slice(0, idx), post = full.slice(idx + raw.length);
      var t0 = null, dur = 1100;
      function fmt(v){
        var s = v.toFixed(dec);
        if (comma) s = Number(s).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
        return pre + s + post;
      }
      function step(t){
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3), cur = target * e;
        el.textContent = fmt(cur);
        if (p < 1) requestAnimationFrame(step); else el.textContent = full;
      }
      requestAnimationFrame(step);
    });
  }

  function drawLines(root, sel){
    var i = 0;
    root.querySelectorAll(sel).forEach(function(ln){
      var len;
      try { len = ln.getTotalLength(); } catch (e) { return; }
      if (!len) return;
      ln.style.transition = 'none';
      ln.style.strokeDasharray = len;
      ln.style.strokeDashoffset = len;
      ln.getBoundingClientRect();
      ln.style.transition = 'stroke-dashoffset .6s ease ' + (i * 0.08).toFixed(2) + 's';
      ln.style.strokeDashoffset = '0';
      i++;
    });
  }

  var CFG = [
    { id: 's13-wrapper', watch: '.s13-grid',    thr: 0.25, counts: [{ sel: '.s13-stat-num' }] },
    { id: 's6-wrapper',  watch: '.s6-stats',    thr: 0.3,  counts: [{ sel: '.s6-stat-num' }] },
    { id: 'pkg-wrapper', watch: '.pkg-upgrade', thr: 0.2,  grow: '.pkg-upgrade-line:not(.rebuild)' },
    { id: 's5-wrapper',  watch: '#s5Arch',      thr: 0.2,  draw: '#s5Arch line.el' }
  ];

  function init(){
    CFG.forEach(function(cfg){
      var root = document.getElementById(cfg.id);
      if (!root) return;
      var fired = false;
      var watch = (cfg.watch && root.querySelector(cfg.watch)) || root;
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(e){
          if (e.isIntersecting && !fired){
            fired = true;
            if (cfg.grow) growBars(root, cfg.grow);
            if (cfg.counts) cfg.counts.forEach(function(c){ countUp(root, c.sel, c); });
            if (cfg.draw) drawLines(root, cfg.draw);
            io.disconnect();
          }
        });
      }, { threshold: cfg.thr || 0.2 });
      io.observe(watch);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
