/* ── tss-03-where reveals ─────────────────────────── */
const tss3Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss3]').forEach(el => tss3Obs.observe(el));
