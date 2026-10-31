// Publication filters: topic buttons + "All / Lead author" toggle
(function () {
  var section = document.getElementById('publications');
  if (!section) return;
  var pubs = section.querySelectorAll('.pub');
  var topicBtns = section.querySelectorAll('.topic-filter button');
  var current = 'all';

  function setTopic(topic) {
    current = topic;
    topicBtns.forEach(function (b) { b.classList.toggle('on', b.dataset.topic === topic); });
    pubs.forEach(function (p) {
      var hit = topic === 'all' || (' ' + p.dataset.topics + ' ').indexOf(' ' + topic + ' ') > -1;
      p.classList.toggle('hide', !hit);
    });
  }
  topicBtns.forEach(function (b) { b.addEventListener('click', function () { setTopic(b.dataset.topic); }); });

  // "Related publications" links on the Research cards open the matching topic
  document.querySelectorAll('a[data-topic]').forEach(function (a) {
    a.addEventListener('click', function () { setTopic(a.dataset.topic); });
  });

  var buttons = section.querySelectorAll('.toggle button');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      buttons.forEach(function (x) { x.classList.toggle('on', x === b); });
      section.classList.toggle('only-lead', b.dataset.filter === 'lead');
    });
  });
})();

// Highlight the nav link of the section currently on screen
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  var sections = Object.keys(map).map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if (!('IntersectionObserver' in window)) return;
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        links.forEach(function (a) { a.classList.remove('active'); });
        var a = map[e.target.id];
        if (a) {
          a.classList.add('active');
          // keep the active link visible in the (narrow-screen) nav bar without touching page scrolling
          var bar = a.parentNode;
          if (bar.scrollWidth > bar.clientWidth) {
            var l = a.offsetLeft - bar.offsetLeft, r = l + a.offsetWidth;
            if (l < bar.scrollLeft) bar.scrollLeft = l - 8;
            else if (r > bar.scrollLeft + bar.clientWidth) bar.scrollLeft = r - bar.clientWidth + 8;
          }
        }
      }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  sections.forEach(function (s) { obs.observe(s); });
})();

// Visitor map: hide the box until a widget code has been pasted into it (template.html, VISITOR MAP)
(function () {
  var wrap = document.querySelector('.visitor-globe');
  if (!wrap) return;
  var box = wrap.querySelector('.globe-box');
  if (!box || !box.children.length) wrap.remove();
})();

// Sidebar taller than the window: let it scroll with the page, then pin its bottom edge
(function () {
  var side = document.querySelector('.sidebar');
  if (!side) return;
  function fit() {
    var top = Math.min(58, window.innerHeight - side.offsetHeight);
    side.style.top = top + 'px';
  }
  window.addEventListener('resize', fit);
  window.addEventListener('load', fit);
  fit();
})();
