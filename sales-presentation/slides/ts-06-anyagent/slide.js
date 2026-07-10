/* ── ts-06-anyagent reveals ───────────────────────── */
const ts6Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-ts6]').forEach(el => ts6Obs.observe(el));
