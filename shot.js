const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  await p.goto(file, { waitUntil: 'networkidle' });
  await p.screenshot({ path: 'preview.png' });
  await b.close();
  console.log('shot ok');
})().catch(e => { console.error(e.message); process.exit(1); });
