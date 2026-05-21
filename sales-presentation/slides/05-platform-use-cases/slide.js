(function() {
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('#platform-pattern .pp-reveal').forEach(function(el) {
    observer.observe(el);
  });
})();
