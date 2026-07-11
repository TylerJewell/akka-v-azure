/* ── tss-02-how reveals ───────────────────────────── */
const tss2Obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss2]').forEach(el => tss2Obs.observe(el));

/* ── click a step → reveal how Akka runs it ───────── */
(() => {
  const steps = document.querySelectorAll('.tss2-step');
  const cards = document.querySelectorAll('.tss2-explain-card');
  if (!steps.length) return;

  const select = id => {
    steps.forEach(s => {
      const on = s.dataset.step === id;
      s.classList.toggle('active', on);
      s.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    cards.forEach(c => c.classList.toggle('active', c.dataset.for === id));
  };

  // Target starts selected (set in markup); one step is always active.
  steps.forEach(btn => btn.addEventListener('click', () => select(btn.dataset.step)));
})();
