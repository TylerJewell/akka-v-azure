const views = [
    'title','hero-wrapper','st-wrapper','stax-wrapper','s2-wrapper','s4-wrapper',
    'spec-wrapper','platform-pattern-wrapper','s6b-wrapper','s13-wrapper',
    's5-wrapper','s6-wrapper','s7-problem','s7-answer-frame','cust-wrapper',
    'pkg-wrapper','spwhat-wrapper','closing'
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
  // Iframe slides forward nav keys via postMessage
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'akka-deck-nav' && e.data.key) {
      handleNavKey(e.data.key);
    }
  });
})();
