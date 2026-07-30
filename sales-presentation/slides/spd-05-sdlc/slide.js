/* ── SDLC slide: vertical tabs (same pattern as the Verify deck) ── */
(function(){
  var tabsEl = document.getElementById('sdlcTabs');
  if (!tabsEl) return;
  var tabs = [].slice.call(document.querySelectorAll('#sdlcTabs .sdlc-tab'));
  var panels = [].slice.call(document.querySelectorAll('#sdlcPanels .sdlc-panel'));
  tabsEl.addEventListener('click', function(e){
    var b = e.target.closest('.sdlc-tab');
    if (!b) return;
    var i = +b.dataset.i;
    tabs.forEach(function(t){ t.classList.toggle('active', t === b); });
    panels.forEach(function(p, k){ p.classList.toggle('active', k === i); });
  });
})();

var sdlcObs = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.12 });
document.querySelectorAll('.sdlc-reveal').forEach(function(el){ sdlcObs.observe(el); });

/* Nested harness install tabs inside the AI assistants panel */
(function(){
  var wrap = document.getElementById('hzTabs');
  if (!wrap) return;
  var tabs = [].slice.call(document.querySelectorAll('#hzTabs .hz-tab'));
  var panels = [].slice.call(document.querySelectorAll('#hzPanels .hz-panel'));
  wrap.addEventListener('click', function(e){
    var b = e.target.closest('.hz-tab');
    if (!b) return;
    var i = +b.dataset.h;
    tabs.forEach(function(t){ t.classList.toggle('active', t === b); });
    panels.forEach(function(p, k){ p.classList.toggle('active', k === i); });
  });
})();
