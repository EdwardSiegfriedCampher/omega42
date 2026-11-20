/* Companion Explorer search and FAQ filter. Loads api/companion-search.json on first use; results show the passage in context. */
(function () {
  var box = document.getElementById('csearch'), out = document.getElementById('cresults');
  var data = null;
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function run(q) {
    q = q.trim().toLowerCase();
    if (q.length < 3) { out.innerHTML = ''; return; }
    var words = q.split(/\s+/), hits = [];
    data.forEach(function (d) {
      var hay = (d.t + ' ' + d.x).toLowerCase(), score = 0;
      for (var i = 0; i < words.length; i++) { var n = hay.split(words[i]).length - 1; if (!n) return; score += n + (d.t.toLowerCase().indexOf(words[i]) >= 0 ? 20 : 0); }
      hits.push([score, d]);
    });
    hits.sort(function (a, b) { return b[0] - a[0]; });
    out.innerHTML = '<p class="note">' + hits.length + ' sections match</p>' + hits.slice(0, 30).map(function (h) {
      var d = h[1], i = d.x.toLowerCase().indexOf(words[0]), start = Math.max(0, i - 120);
      var snip = esc(d.x.slice(start, start + 320));
      words.forEach(function (w) { snip = snip.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
      return '<a class="hit" href="' + d.f + (d.a ? '#' + d.a : '') + '"><b>' + esc(d.t || d.p) + '</b>' + (d.t ? '<span class="note">' + esc(d.p) + '</span>' : '') + '<span>' + (start ? '… ' : '') + snip + ' …</span></a>';
    }).join('');
  }
  if (box && out) {
    var go = function () {
      if (data) return run(box.value);
      out.innerHTML = '<p class="note">Loading the Companion…</p>';
      fetch('api/companion-search.json').then(function (r) { return r.json(); }).then(function (d) { data = d; run(box.value); })
        .catch(function () { out.innerHTML = '<p class="note">Search needs the published site (it reads api/companion-search.json).</p>'; });
    };
    box.addEventListener('input', go);
    var q = new URLSearchParams(location.search).get('q'); if (q) { box.value = q; go(); }
  }
  var f = document.getElementById('faqfilter');
  if (f) f.addEventListener('input', function () {
    var q = f.value.trim().toLowerCase();
    document.querySelectorAll('.faq details').forEach(function (d) { var hit = !q || d.textContent.toLowerCase().indexOf(q) >= 0; d.style.display = hit ? '' : 'none'; if (q && hit) d.open = true; });
  });
})();
