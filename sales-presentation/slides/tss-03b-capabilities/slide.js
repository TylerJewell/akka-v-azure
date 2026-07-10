/* ── tss-03b-capabilities reveals + tabs ──────────── */
const tss3bObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('[data-tss3b]').forEach(el => tss3bObs.observe(el));

document.querySelectorAll('.tss3b-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tss3b-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tss3b-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tss3b-' + tab.dataset.panel).classList.add('active');
  });
});
