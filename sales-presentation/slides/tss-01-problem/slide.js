/* ── tss-01-problem reveals ───────────────────────── */
const tss1Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss1]').forEach(el => tss1Obs.observe(el));
