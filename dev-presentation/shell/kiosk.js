(function() {
  if (!new URLSearchParams(location.search).has('kiosk')) return;
  const views = Array.from(document.querySelectorAll('[data-view]'));
  const seconds = Number(new URLSearchParams(location.search).get('kiosk')) || 35;
  let i = 0;
  function top(el) { return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset); }
  setInterval(function() {
    i = (i + 1) % views.length;
    window.scrollTo({ top: top(views[i]), behavior: 'smooth' });
  }, seconds * 1000);
})();
