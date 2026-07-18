/* ── ts-02-product reveals ────────────────────────── */
const ts2Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts2], .ts2-flow').forEach(el => ts2Obs.observe(el));
