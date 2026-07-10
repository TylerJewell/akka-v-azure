/* ── tss-02-how reveals ───────────────────────────── */
const tss2Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss2]').forEach(el => tss2Obs.observe(el));
