const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const url = 'file://' + path.resolve(__dirname, 'index.html');
  await page.goto(url);
  await page.click('#menu');
  await page.waitForTimeout(150);
  // select a few countries (open their groups first, then dispatch click on the row)
  for (const cc of ['GB','FR','US','CA','MX']) {
    await page.evaluate(cc => {
      const r = document.querySelector(`.country-row[data-cc="${cc}"]`);
      r.closest('details').open = true;
      r.click();
    }, cc);
  }
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'margin_chips.png' });

  // click clear-all
  await page.click('#clearsel');
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'margin_chips_cleared.png' });

  await browser.close();
  console.log('done');
})();
