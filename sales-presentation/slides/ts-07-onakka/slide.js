/* ── ts-07-onakka reveals ─────────────────────────── */
const ts7Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts7]').forEach(el => ts7Obs.observe(el));
