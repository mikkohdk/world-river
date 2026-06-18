const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  page.on('console', m => console.log('console:', m.text()));
  page.on('pageerror', e => console.log('pageerror:', e));
  const url = 'file://' + path.resolve(__dirname, 'index.html');
  await page.goto(url);
  await page.click('#menu');
  await page.waitForTimeout(150);

  await page.fill('#fbtext', 'Test feedback from shot_feedback.js — please ignore.');
  await page.click('#fbsend');
  await page.waitForTimeout(5000);

  const status = await page.textContent('#fbstatus');
  console.log('status:', status);
  await page.screenshot({ path: 'margin_feedback.png' });

  await browser.close();
})();
