/* ── ts-09-competitive reveals ────────────────────── */
const ts9Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts9]').forEach(el => ts9Obs.observe(el));
