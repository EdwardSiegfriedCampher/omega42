/* Information integrity: build a Navigator prompt on the visitor's device (nothing is sent anywhere). */
(function () {
  var f = document.getElementById('ii-form'); if (!f) return;
  var T = {comprehensive: 'a comprehensive investigation (all six modules, combined as the material requires)',
    origin: 'AI-origin and synthetic-content analysis', claims: 'claim and evidence verification', provenance: 'source and provenance reconstruction',
    propagation: 'coordination and information-propagation analysis', temporal: 'historical and temporal verification'};
  var D = {quick: 'Quick: the main claims and the decisive checks only.', detailed: 'Detailed: every claim, every source, the timeline.',
    research: 'Research grade: full method, calculations, alternative explanations and what further evidence would settle each open point.'};
  function build() {
    var m = document.getElementById('ii-material').value.trim() || '[paste the article, claim, transcript or URL here]';
    document.getElementById('ii-prompt').textContent = 'Welcome Navigator\n\nInformation integrity investigation: ' + T[document.getElementById('ii-type').value] + '. ' +
      D[document.getElementById('ii-depth').value] + '\n\nMaterial:\n' + m + '\n\n' +
      'Keep origin, accuracy and intent apart. Break the material into individual claims and give each one a status: VERIFIED, SUPPORTED, PARTIALLY SUPPORTED, CONTRADICTED, UNVERIFIED, INSUFFICIENT EVIDENCE, OUTDATED or MISREPRESENTED. ' +
      'Count independent confirmations, not repetitions. Report missing provenance as missing evidence, not as proof of fabrication. Never present a detector score as proof of AI authorship, and never infer deliberate deception without evidence of intent. ' +
      'Give an integrity profile (origin evidence, factual support, source independence, temporal consistency, provenance, propagation), not a single trust score. ' +
      'Report sections: material examined; question and scope; origin assessment; claim analysis; source and provenance; timeline; network; mathematical analysis; alternative explanations; findings and uncertainty; further investigation. ' +
      'Say which findings came from internal Omega42 mathematics and which needed outside research, with sources.';
  }
  f.addEventListener('input', build); f.addEventListener('change', build); build();
})();
