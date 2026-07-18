/* ── ts-06-architecture reveals ──────────────────── */
const arcObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
document.querySelectorAll('[data-arc]').forEach(el => arcObs.observe(el));
