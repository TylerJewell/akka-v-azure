(function() {
  const views = Array.from(document.querySelectorAll('[data-view]'));
  function top(el) { return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset); }
  function current() {
    const y = window.scrollY || window.pageYOffset;
    let best = 0;
    for (let i = 0; i < views.length; i++) if (top(views[i]) <= y + 12) best = i;
    return best;
  }
  document.addEventListener('keydown', function(e) {
    if (['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)) {
      e.preventDefault();
      const i = current();
      if (i < views.length - 1) window.scrollTo({ top: top(views[i + 1]), behavior: 'smooth' });
    }
    if (['ArrowLeft','ArrowUp','PageUp'].includes(e.key)) {
      e.preventDefault();
      const i = current();
      const y = window.scrollY || window.pageYOffset;
      if (y > top(views[i]) + 12) window.scrollTo({ top: top(views[i]), behavior: 'smooth' });
      else if (i > 0) window.scrollTo({ top: top(views[i - 1]), behavior: 'smooth' });
    }
  });
})();
