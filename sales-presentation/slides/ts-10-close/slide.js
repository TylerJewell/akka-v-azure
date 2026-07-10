/* ── ts-10-close reveals ──────────────────────────── */
const tscObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.2 });
document.querySelectorAll('.tsc-reveal').forEach(el => tscObs.observe(el));
