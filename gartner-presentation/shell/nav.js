(function() {

const views = [
    document.getElementById('title'),
    document.getElementById('hero'),
    document.getElementById('s4-wrapper'),
    document.getElementById('platform-pattern-wrapper'),
    document.getElementById('wf1-wrapper'),
    document.getElementById('wf2-wrapper'),
    document.getElementById('wf3-wrapper'),
    document.getElementById('s2-wrapper'),
    document.getElementById('pr-readiness-wrapper'),
    document.getElementById('s13-wrapper'),
    document.getElementById('s5-wrapper'),
    document.getElementById('gp-wrapper'),
    document.getElementById('s7-problem'),
    document.getElementById('s7-answer-wrapper'),
    document.getElementById('thankyou'),
  ].filter(Boolean);

  function currentViewIndex() {
    var scrollY = window.scrollY || window.pageYOffset;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (views[i].offsetTop <= scrollY + 10) best = i;
    }
    return best;
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown') {
      e.preventDefault();
      var idx = currentViewIndex();
      if (idx < views.length - 1) {
        views[idx + 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') {
      e.preventDefault();
      var idx = currentViewIndex();
      var scrollY = window.scrollY || window.pageYOffset;
      // If we're partway into the current view, go to its top first
      if (scrollY > views[idx].offsetTop + 10 && idx >= 0) {
        views[idx].scrollIntoView({ behavior: 'smooth' });
      } else if (idx > 0) {
        views[idx - 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
  });
})();
