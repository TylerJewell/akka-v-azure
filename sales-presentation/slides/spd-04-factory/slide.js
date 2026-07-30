/* ── Software factory slide reveals ─────────────────── */
const factObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('.fact-reveal').forEach(el => factObs.observe(el));
