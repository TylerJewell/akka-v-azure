/* ── ts-01-problem reveals ────────────────────────── */
const ts1Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts1]').forEach(el => ts1Obs.observe(el));
