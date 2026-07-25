/* ── opt-02-economics reveals ─────────────────────── */
const ecoObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
document.querySelectorAll('[data-eco]').forEach(el => ecoObs.observe(el));
