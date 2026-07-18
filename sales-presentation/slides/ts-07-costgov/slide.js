/* ── ts-08-costgov reveals ───────────────────────── */
const cogObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
document.querySelectorAll('[data-cog]').forEach(el => cogObs.observe(el));
