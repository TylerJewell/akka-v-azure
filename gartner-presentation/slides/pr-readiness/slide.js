(function() {
  const wrapper = document.getElementById('pr-readiness-wrapper');
  if (!wrapper) return;
  const reveals = Array.from(wrapper.querySelectorAll('.pr-reveal'));
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const idx = reveals.indexOf(entry.target);
      entry.target.style.transitionDelay = (Math.max(idx, 0) * 45) + 'ms';
      entry.target.classList.add('is-visible');
      io.unobserve(entry.target);
    });
  }, { threshold: 0.15 });
  reveals.forEach(el => io.observe(el));
})();
