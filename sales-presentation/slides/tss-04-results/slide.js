/* ── tss-04-results reveals ───────────────────────── */
const tss4Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss4]').forEach(el => tss4Obs.observe(el));
