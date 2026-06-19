const views = [
    document.getElementById('title'),
    document.getElementById('hero-wrapper'),
    document.getElementById('st-wrapper'),
    document.getElementById('stax-wrapper'),
    document.getElementById('s2-wrapper'),
    document.getElementById('s4-wrapper'),
    document.getElementById('spec-wrapper'),
    document.getElementById('platform-pattern-wrapper'),
    document.getElementById('s6b-wrapper'),
    document.getElementById('s13-wrapper'),
    document.getElementById('s5-wrapper'),
    document.getElementById('s6-wrapper'),
    document.getElementById('s7-problem'),
    document.getElementById('s7-answer-frame'),
    document.getElementById('cust-wrapper'),
    document.getElementById('pkg-wrapper'),
    document.getElementById('s10-delivery-wrapper'),
    document.getElementById('s9-wrapper'),
    document.getElementById('demo-wrapper'),
    document.getElementById('closing')
  ].filter(Boolean);

  function currentViewIndex() {
    var scrollY = window.scrollY || window.pageYOffset;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (views[i].offsetTop <= scrollY + 10) best = i;
    }
    return best;
  }

  function navNext() {
    var idx = currentViewIndex();
    if (idx < views.length - 1) {
      views[idx + 1].scrollIntoView({ behavior: 'smooth' });
    }
  }
  function navPrev() {
    var idx = currentViewIndex();
    var scrollY = window.scrollY || window.pageYOffset;
    if (scrollY > views[idx].offsetTop + 10 && idx >= 0) {
      views[idx].scrollIntoView({ behavior: 'smooth' });
    } else if (idx > 0) {
      views[idx - 1].scrollIntoView({ behavior: 'smooth' });
    }
  }
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
  // Iframe slides (e.g. governance.html) forward nav keys via postMessage
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'akka-deck-nav' && e.data.key) {
      handleNavKey(e.data.key);
    }
  });
})();
