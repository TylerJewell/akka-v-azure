const views = [
    'title','spwhat-wrapper','spec-wrapper','s5-wrapper',
    'fact-wrapper','sdlc-wrapper','proof-wrapper','family','closing'
  ].map(function(id){ return document.getElementById(id); }).filter(Boolean);

  function docTop(el){
    return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
  }
  /* R2 says always subtract the fixed header. Measure it instead of assuming
     78: on akka.io that finds the real header, and on a local file:// review
     there is no header, so nothing is subtracted and slides land where they
     were designed to land. */
  var _hdr = null;
  function HDR() {
    if (_hdr !== null) return _hdr;
    var best = 0, all = document.body.getElementsByTagName('*');
    for (var i = 0; i < all.length; i++) {
      var cs = getComputedStyle(all[i]);
      if (cs.position !== 'fixed') continue;
      var r = all[i].getBoundingClientRect();
      if (r.top <= 2 && r.height >= 40 && r.height <= 140 &&
          r.width > window.innerWidth * 0.6 && r.height > best) best = r.height;
    }
    _hdr = Math.round(best);
    return _hdr;
  }
  window.addEventListener('resize', function(){ _hdr = null; });
  function currentIndex() {
    var y = (window.scrollY || window.pageYOffset) + HDR() + 4;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (docTop(views[i]) <= y) best = i;
    }
    return best;
  }
  function goTo(i) {
    if (i < 0 || i >= views.length) return;
    window.scrollTo({ top: Math.max(0, docTop(views[i]) - HDR()), behavior: 'smooth' });
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

/* ── Specify deck motion — behaviour only; content and positions unchanged.
   Draws the solid architecture connector lines as the weeks slide reveals.
   The deck is otherwise word-based, and the spec-flow draws and pattern-rule
   bars already self-animate via their own CSS reveals, so they are left alone. ── */
(function(){
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
    { id: 's5-wrapper', watch: '#s5Arch', thr: 0.2, draw: '#s5Arch line.el' }
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
