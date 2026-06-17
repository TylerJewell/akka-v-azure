/* ── Slide 04 specifications ──────────────────────── */
const specRevealObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-spec="0"], [data-spec="1"], [data-spec="2"], [data-spec="3"]').forEach(el => specRevealObs.observe(el));
