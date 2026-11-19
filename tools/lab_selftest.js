// Headless check of the Construct X Lab (used by STP test CX-003).
// Usage: node tools/lab_selftest.js site/construct_x_lab.html  -> JSON {partners, offsets, errors}
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2]) + '#seeds'); await p.waitForTimeout(1500);
  const out = await p.evaluate(() => {
    const partners = {}; for (const s of Object.keys(LABELS)) partners[s] = partnerOf(s);
    return { partners, offsets: OFFSETS };
  });
  out.errors = errors; console.log(JSON.stringify(out)); await b.close();
})();
