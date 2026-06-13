const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 760, height: 520 }, deviceScaleFactor: 2 });
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  await p.goto(file);
  const injected = await p.evaluate(() =>
    [...document.querySelectorAll('style')].some(s => s.textContent.includes('Twemoji Country Flags')));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  // open the picker so we see a column of flags too
  await p.click('#menu').catch(() => {});
  await p.waitForTimeout(200);
  await p.screenshot({ path: 'preview_flags.png' });
  console.log('polyfill injected (native flags absent on this platform):', injected);
  await b.close();
})().catch(e => { console.error(e.message); process.exit(1); });
