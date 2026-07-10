(function(){
  var views = [
    'ts-title','tss1-wrapper','tss2-wrapper','tss3-wrapper','tss3b-wrapper',
    'tss4-wrapper','ts-closing'
  ].map(function(id){ return document.getElementById(id); }).filter(Boolean);

  function docTop(el){
    return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset);
  }
  function currentIndex() {
    var y = (window.scrollY || window.pageYOffset) + 4;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (docTop(views[i]) <= y) best = i;
    }
    return best;
  }
  function goTo(i) {
    if (i < 0 || i >= views.length) return;
    window.scrollTo({ top: docTop(views[i]), behavior: 'smooth' });
  }
  function navNext() { goTo(currentIndex() + 1); }
  function navPrev() { goTo(currentIndex() - 1); }
  function handleNavKey(key) {
    if (key === 'ArrowRight' || key === 'PageDown') navNext();
    else if (key === 'ArrowLeft' || key === 'PageUp') navPrev();
  }
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' ||
        e.key === 'ArrowLeft'  || e.key === 'PageUp') {
      e.preventDefault();
      handleNavKey(e.key);
    }
  });
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'akka-deck-nav' && e.data.key) {
      handleNavKey(e.data.key);
    }
  });
})();
