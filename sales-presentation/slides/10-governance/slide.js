/* ── Phase 1: scroll-driven problem reveals ── */
const s7wrapper = document.getElementById('s7-problem');
const s7els     = document.querySelectorAll('[data-s7]');

function updateS7() {
  const y       = window.scrollY;
  const wTop    = s7wrapper.offsetTop;
  const wScroll = s7wrapper.offsetHeight - window.innerHeight;
  const scrolled = y - wTop;
  const p = wScroll > 0 ? Math.max(0, Math.min(scrolled / wScroll, 1)) : 0;

  s7els.forEach(el => {
    const step = +el.dataset.s7;
    const threshold = Math.max(0, (step - 1) / 5);
    el.classList.toggle('visible', p >= threshold);
  });
}
window.addEventListener('scroll', updateS7, { passive: true });
updateS7();
