/* ── AI market taxonomy slide ─────────────────── */
const staxObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.12 });
document.querySelectorAll('[data-stax]').forEach(el => staxObs.observe(el));
