const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, 'index.html');

  // Desktop
  let page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  await page.goto(url);
  await page.screenshot({ path: 'margin_desktop.png' });

  // Open menu
  await page.click('#menu');
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'margin_desktop_menu.png' });

  // Scroll menu to see muted words + country rows
  await page.evaluate(() => document.getElementById('tree').scrollTo(0, 400));
  await page.screenshot({ path: 'margin_desktop_menu_scrolled.png' });
  await page.close();

  // Mobile
  page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(url);
  await page.screenshot({ path: 'margin_mobile.png' });
  await page.click('#menu');
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'margin_mobile_menu.png' });
  await page.close();

  await browser.close();
  console.log('done');
})();
