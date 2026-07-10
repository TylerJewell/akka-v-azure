/* ── ts-08-math reveals ───────────────────────────── */
const ts8Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts8]').forEach(el => ts8Obs.observe(el));
