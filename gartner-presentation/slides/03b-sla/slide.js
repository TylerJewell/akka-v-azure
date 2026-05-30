/* ── Slide 03b: AI Platform + AI SLA ── */
const sSlaObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-sla]').forEach(el => sSlaObs.observe(el));
