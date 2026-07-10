/* ── ts-03-target reveals ─────────────────────────── */
const ts3Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts3]').forEach(el => ts3Obs.observe(el));
