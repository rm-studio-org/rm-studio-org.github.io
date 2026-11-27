/* Georu site — shared behaviour: language, theme, mobile nav, on-page TOC, API filter */
(function () {
  var d = document.documentElement;

  /* language */
  function setLang(l) {
    d.setAttribute('data-lang', l); d.lang = l;
    try { localStorage.setItem('rm-lang', l); } catch (e) {}
    document.querySelectorAll('[data-set-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.setLang === l ? 'true' : 'false');
    });
    var t = d.getAttribute('data-title-' + l);
    if (t) document.title = t;
    buildToc();
  }
  document.querySelectorAll('[data-set-lang]').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.setLang); });
  });

  /* theme */
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  function isDark() { var t = d.getAttribute('data-theme'); return t ? t === 'dark' : mq.matches; }
  var themeBtn = document.getElementById('themeBtn');
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    d.setAttribute('data-theme', next);
    try { localStorage.setItem('rm-theme', next); } catch (e) {}
  });

  /* mobile side nav */
  var menuBtn = document.getElementById('menuBtn');
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { document.body.classList.toggle('nav-open'); });
    document.querySelectorAll('.side a').forEach(function (a) {
      a.addEventListener('click', function () { document.body.classList.remove('nav-open'); });
    });
  }

  /* landing header: dark while over the hero */
  var top = document.querySelector('.g-top[data-hero]');
  var hero = document.querySelector('.hero');
  if (top && hero) {
    var onScroll = function () {
      top.classList.toggle('on-dark', window.scrollY < hero.offsetHeight - 70);
    };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  /* on-page TOC + heading anchors */
  var toc = document.getElementById('toc');
  var spyItems = [];
  function visible(el) { return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length); }
  function buildToc() {
    if (!toc) return;
    var list = toc.querySelector('.list');
    list.innerHTML = '';
    spyItems = [];
    document.querySelectorAll('.content h2[id], .content h3[id]').forEach(function (h) {
      if (!visible(h) || h.hasAttribute('data-notoc')) return;
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.className = h.tagName === 'H3' ? 'h3' : 'h2';
      var clone = h.cloneNode(true);
      clone.querySelectorAll('.anchor,.no').forEach(function (x) { x.remove(); });
      var l = d.getAttribute('data-lang');
      clone.querySelectorAll('[lang]').forEach(function (x) { if (x.getAttribute('lang') !== l) x.remove(); });
      a.textContent = clone.textContent.trim();
      list.appendChild(a);
      spyItems.push({ h: h, a: a });
    });
    spy();
  }
  function spy() {
    if (!spyItems.length) return;
    var cur = spyItems[0];
    for (var i = 0; i < spyItems.length; i++) {
      if (spyItems[i].h.getBoundingClientRect().top < 120) cur = spyItems[i];
    }
    spyItems.forEach(function (it) { it.a.classList.toggle('active', it === cur); });
  }
  window.addEventListener('scroll', spy, { passive: true });
  document.querySelectorAll('.content h2[id], .content h3[id]').forEach(function (h) {
    var a = document.createElement('a');
    a.className = 'anchor'; a.href = '#' + h.id; a.textContent = '#'; a.setAttribute('aria-hidden', 'true');
    h.appendChild(a);
  });

  /* API filter */
  var q = document.getElementById('apiQuery');
  if (q) {
    var cnt = document.getElementById('apiCount');
    var eps = Array.prototype.slice.call(document.querySelectorAll('.ep'));
    var groups = Array.prototype.slice.call(document.querySelectorAll('.api-group'));
    var run = function () {
      var v = q.value.trim().toLowerCase(), n = 0;
      eps.forEach(function (e) {
        var hit = !v || e.textContent.toLowerCase().indexOf(v) >= 0;
        e.style.display = hit ? '' : 'none'; if (hit) n++;
      });
      groups.forEach(function (g) {
        var any = g.querySelector('.ep:not([style*="none"])');
        g.style.display = any ? '' : 'none';
      });
      cnt.textContent = n + ' / ' + eps.length;
    };
    q.addEventListener('input', run); run();
  }

  setLang(d.getAttribute('data-lang') || 'ko');
})();
