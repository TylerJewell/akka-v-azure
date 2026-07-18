(function() {
  function countUp(el, target, duration) {
    var start = performance.now();
    function frame(now) {
      var t = Math.min(1, (now - start) / duration);
      var eased = 1 - Math.pow(1 - t, 3);
      var val = Math.round(eased * target);
      el.textContent = val.toLocaleString();
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('visible');

      if (e.target.classList.contains('pp-row')) {
        var counter = e.target.querySelector('.pp-counter');
        if (counter && !counter.dataset.done) {
          counter.dataset.done = '1';
          var target = parseInt(e.target.getAttribute('data-stat'), 10);
          if (!isNaN(target)) {
            setTimeout(function() {
              countUp(counter, target, 1300);
            }, 250);
          }
        }
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('#platform-pattern .pp-reveal').forEach(function(el) {
    observer.observe(el);
  });
})();
