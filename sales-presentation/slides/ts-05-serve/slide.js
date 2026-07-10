/* ── ts-05-serve reveals ──────────────────────────── */
const ts5Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts5]').forEach(el => ts5Obs.observe(el));
