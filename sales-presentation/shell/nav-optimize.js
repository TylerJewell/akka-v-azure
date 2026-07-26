(function(){
  var views = [
    'opt-title','ts1-wrapper','ts2-wrapper','arc-wrapper','ts4-wrapper',
    'eco-wrapper','ts3-wrapper','cog-wrapper','family','opt-closing'
  ].map(function(id){ return document.getElementById(id); }).filter(Boolean);

  function docTop(el){
    return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
  }
  function currentIndex() {
    var y = (window.scrollY || window.pageYOffset) + 4;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (docTop(views[i]) <= y) best = i;
    }
    return best;
  }
  function goTo(i) {
    if (i < 0 || i >= views.length) return;
    window.scrollTo({ top: docTop(views[i]), behavior: 'smooth' });
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
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'akka-deck-nav' && e.data.key) {
      handleNavKey(e.data.key);
    }
  });
})();

/* ── Optimize deck motion — behaviour only; content and positions unchanged.
   Grows bars, counts hero numbers, and draws flow lines as each slide reveals.
   Honours prefers-reduced-motion. ── */
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
      if (!nums || nums.length !== 1) return;          /* single number only, so ranges stay intact */
      var raw = nums[0], clean = raw.replace(/,/g, '');
      var target = parseFloat(clean);
      if (isNaN(target) || target === 0) return;
      var dec = (clean.split('.')[1] || '').length, comma = /,/.test(raw);
      var idx = full.indexOf(raw), pre = full.slice(0, idx), post = full.slice(idx + raw.length);
      var t0 = null, dur = 1100, greened = false;
      function fmt(v){
        var s = v.toFixed(dec);
        if (comma) s = Number(s).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
        return pre + s + post;
      }
      function step(t){
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3), cur = target * e;
        el.textContent = fmt(cur);
        if (!greened && opts.threshold != null && cur >= opts.threshold){
          greened = true;
          if (opts.color){ el.style.transition = 'color .35s ease'; el.style.setProperty('color', opts.color, 'important'); }
        }
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
      ln.style.transition = 'stroke-dashoffset .6s ease ' + (i * 0.05).toFixed(2) + 's';
      ln.style.strokeDashoffset = '0';
      i++;
    });
  }

  function fadeIn(root, sel, delay){
    root.querySelectorAll(sel).forEach(function(el){
      el.style.opacity = '0';
      el.style.transition = 'opacity .55s ease ' + (delay || 0) + 's';
      el.getBoundingClientRect();
      requestAnimationFrame(function(){ el.style.opacity = '1'; });
    });
  }

  var GREEN = '#72D35B';
  var CFG = [
    { id: 'ts1-wrapper', watch: '.ts1-charts-bars', thr: 0.3, grow: '.ts1-bar', counts: [{ sel: '.ts1-bar-val' }] },
    { id: 'eco-wrapper', watch: '.econ', thr: 0.12,
      counts: [{ sel: '.e-tile b' }, { sel: '.e-cost text[fill="#72D35B"]' }],
      fade: '.e-cost line[stroke="#72D35B"], .e-cost polygon[fill="#72D35B"]', fadeDelay: 0.4 },
    { id: 'ts3-wrapper', watch: '.ts3-table', thr: 0.2,
      counts: [{ sel: '.ts3-fit' }, { sel: '.ts3-proj, .ts3-foot-val', threshold: 15, color: GREEN }] },
    { id: 'ts4-wrapper', watch: '.ts4-diagram', thr: 0.3, draw: '.ts4-el' }
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
            if (cfg.fade) fadeIn(root, cfg.fade, cfg.fadeDelay);
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
