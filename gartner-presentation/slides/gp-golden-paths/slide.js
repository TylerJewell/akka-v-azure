(function() {
  const wrapper = document.getElementById('gp-wrapper');
  if (!wrapper) return;
  const reveals = Array.from(wrapper.querySelectorAll('.gp-reveal'));
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const idx = reveals.indexOf(entry.target);
      entry.target.style.transitionDelay = (Math.max(idx, 0) * 65) + 'ms';
      entry.target.classList.add('is-visible');
      io.unobserve(entry.target);
    });
  }, { threshold: 0.2 });
  reveals.forEach(el => io.observe(el));
})();
