/* ── ts-04-prove reveals ──────────────────────────── */
const ts4Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts4]').forEach(el => ts4Obs.observe(el));
