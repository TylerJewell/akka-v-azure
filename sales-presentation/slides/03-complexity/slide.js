/* ── Section 3 ──────────────────────── */
const s2RevealObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-s2="0"], [data-s2="1"], [data-s2="2"]').forEach(el => s2RevealObs.observe(el));
