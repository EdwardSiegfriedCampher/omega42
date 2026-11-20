/* The free Strike app: runs the unchanged reference script, canonical_reference.py, in the browser under Pyodide.
   The question never leaves the page. Pyodide is loaded from jsDelivr, pinned to 0.26.4. */
(function () {
  var O = window.O42, $ = function (s) { return document.querySelector(s); };
  var form = $('#strike-form'), out = $('#strike-out'), status = $('#strike-status'), btn = $('#strike-go');
  var ready = null;

  function boot() {
    if (ready) return ready;
    status.textContent = 'Loading the reference script (about 10 MB, once)…';
    ready = new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
      s.onload = res; s.onerror = function () { rej(new Error('Pyodide could not be loaded')); };
      document.head.appendChild(s);
    }).then(function () { return window.loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/'}); })
      .then(function (py) {
        return Promise.all([fetch(O.base + 'py/canonical_reference.py').then(function (r) { return r.text(); }),
                            fetch(O.base + 'py/strike.py').then(function (r) { return r.text(); }),
                            fetch(O.base + 'py/adaptor_rules.py').then(function (r) { return r.text(); })])
          .then(function (src) {
            py.FS.writeFile('/home/pyodide/canonical_reference.py', src[0]);
            py.FS.writeFile('/home/pyodide/strike.py', src[1]);
            py.FS.writeFile('/home/pyodide/adaptor_rules.py', src[2]);
            py.runPython("import sys; sys.path.insert(0, '/home/pyodide'); import strike");
            status.textContent = 'Ready. The computation runs on your device.';
            return py;
          });
      });
    return ready;
  }

  var lastQ = '';
  function render(r) {
    if (r.zero) { out.innerHTML = '<p class="mono note">QUESTION VERBATIM: ' + O.esc(lastQ) + '</p><p>' + O.esc(r.reason) + '</p>'; return; }
    var arms = r.arms.map(function (a) {
      return '<div><span class="role">' + O.esc(a.role) + '</span><span class="pos">P' + a.position + ' ' + O.esc(a.name) + ' · ' + a.value + '</span><span class="note mono">' + a.arm + ' +' + a.offset + '</span></div>';
    }).join('');
    out.innerHTML =
      '<p class="mono note">QUESTION VERBATIM: ' + O.esc(lastQ) + '</p>' +   // Core L-499: the question travels with the result
      '<div class="coord"><span class="p">P' + r.anchor + '</span><div><h2>' + O.esc(r.name) + '</h2><span class="mono note">value ' + r.value + ' · TFI ' + r.tfi + '</span></div></div>' +
      '<div class="arms">' + arms + '</div>' +
      '<table><tbody>' +
      '<tr><th>Counted words</th><td>' + O.esc(r.words.join(' · ')) + '</td></tr>' +
      '<tr><th>Counted by</th><td>' + O.esc(r.counted_by) + '</td></tr>' +
      '<tr><th>Counts</th><td class="num">' + r.n[0] + ' words · ' + r.n[1] + ' letters · ' + r.n[2] + ' syllables → residues ' + r.r.join(', ') + '</td></tr>' +
      '<tr><th>Place in the family</th><td class="num">(' + r.state.join(', ') + ') on ' + O.esc(r.loop) + ' · its mirror (' + r.mirror.join(', ') + ')</td></tr>' +
      (r.phase ? '<tr><th>Phase (M312)</th><td>' + O.esc(r.phase) + ' · one step of the law turns it, its square keeps it</td></tr>' : '') +
      '<tr><th>Domain SHA-256</th><td class="num" style="word-break:break-all">' + r.sha256 + '</td></tr>' +
      (r.exposed ? '<tr><th>Note</th><td>This question appears in the protocol\'s own text (an exposed domain).</td></tr>' : '') +
      '</tbody></table>' +
      '<details class="walk"><summary>First strike: how this was computed, step by step</summary><ol>' +   // APE-066: an optional walkthrough, never a gate
      '<li>Your words are separated: the content words counted are ' + O.esc(r.words.join(' · ')) + '.</li>' +
      '<li>Only the words are counted, not their order: the same words in another order land on the same position.</li>' +
      '<li>Three counts are taken — ' + r.n[0] + ' words, ' + r.n[1] + ' letters, ' + r.n[2] + ' syllables — each the record of a boundary you drew.</li>' +
      '<li>Each count n becomes a residue dr(5n): ' + r.r.join(', ') + '. Only n modulo 9 is kept.</li>' +
      '<li>The residues vote for a position on the 24-cycle: P' + r.anchor + ', ' + O.esc(r.name) + '.</li>' +
      '<li>Four directions follow from that position by fixed offsets — what it rests on, what it holds out of view, where it is heading, what would complete it.</li>' +
      '<li>What any of it means is yours to judge: that is the 1/7 Aperture, the part of the reading no arithmetic and no AI fills.</li>' +
      '</ol></details>' +
      '<p class="note">This is the coordinate and its four directions, computed exactly. A full reading is written by an AI acting as Navigator: attach the protocol to any AI, type <code>Welcome Navigator</code>, and bring this question. What any of it means is for you to judge.</p>';
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = $('#strike-q').value.trim();
    if (!q) { status.textContent = 'Type a question first.'; return; }
    lastQ = q;
    btn.disabled = true;
    boot().then(function (py) {
      py.globals.set('q', q);
      render(JSON.parse(py.runPython('strike.strike(q)')));
      status.textContent = 'Computed on your device by canonical_reference.py.';
    }).catch(function (err) {
      status.textContent = 'The in-browser engine could not start here (' + err.message + '). Run it locally instead: python3 scripts/canonical_reference.py --navigate "your question".';
      ready = null;
    }).then(function () { btn.disabled = false; });
  });
  $('#strike-q').addEventListener('focus', function () { boot().catch(function () {}); }, {once: true});

  // the approach and the ready-made Navigator prompt (proposal CA-32: internal, external, hybrid, speculative, formal)
  var MODES = {auto: 'Automatic: classify the question yourself (direct, exploratory, hybrid, speculative or formal), say which approach you chose and why.',
    direct: 'Direct Omega analysis: answer from the established definitions, rules and mathematics of Omega42 only, and trace each step to them.',
    explore: 'Active exploration: navigate the Companion, the research records and outside sources; report what you could and could not establish, with sources.',
    hybrid: 'Hybrid: first establish what the Omega42 mathematics shows, then investigate the wider implications, keeping results, external findings and speculation apart.',
    speculate: 'Open speculation: develop possibilities and thought experiments freely, marked as speculation.',
    formal: 'Formal development: give definitions, equations, derivations, proofs or counterexamples.'};
  function mode() { var m = document.querySelector('input[name=mode]:checked'); return m ? m.value : 'auto'; }
  function prompt() {
    var q = $('#strike-q').value.trim() || 'your question';
    $('#nav-prompt').textContent = 'Welcome Navigator\n\nMy question: ' + q + '\n\nApproach: ' + MODES[mode()] +
      '\nIn the report, name the approach you used and give each statement its status: mathematical derivation, logical conclusion, external finding, formal connection, speculative connection, empirical finding or open question. Do not state external verification that did not happen.';
  }
  form.addEventListener('input', prompt); form.addEventListener('change', prompt); prompt();
  // arriving from the home page: the question travels in the URL fragment, which is never sent to any server
  var h = new URLSearchParams(location.hash.slice(1));
  if (h.get('q')) {
    $('#strike-q').value = h.get('q');
    var r = document.querySelector('input[name=mode][value="' + (h.get('mode') || 'auto') + '"]'); if (r) r.checked = true;
    prompt(); if (h.get('go') !== '0') form.requestSubmit(); else $('#strike-q').focus();
  }
})();
