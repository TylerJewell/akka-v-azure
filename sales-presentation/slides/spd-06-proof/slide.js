/* ── Customer results slide reveals ─────────────────── */
const proofObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('.proof-reveal').forEach(el => proofObs.observe(el));
