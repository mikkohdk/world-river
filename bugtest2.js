const { chromium } = require('playwright');
const path = require('path');
const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');

(async () => {
  const b = await chromium.launch();

  // read-dim visual
  let ctx = await b.newContext({ viewport: { width: 800, height: 600 } });
  let p = await ctx.newPage();
  await p.goto(file);
  await p.locator('article').first().locator('a.t').evaluate(el => el.click());
  await p.waitForTimeout(150);
  await p.screenshot({ path: 'bugtest_read_dim.png', clip: { x: 0, y: 60, width: 800, height: 200 } });

  // mlabel truncation zoom on mobile
  let ctxM = await b.newContext({ viewport: { width: 375, height: 200 } });
  let pM = await ctxM.newPage();
  await pM.goto(file);
  await pM.click('#menu');
  await pM.click('#tree summary:has-text("Europe")');
  for (const cc of ['GB','IE','FR','DE','NL']) await pM.click(`#tree .row[data-cc="${cc}"] .nm`);
  await pM.click('#menu'); // close to see header clearly
  await pM.waitForTimeout(100);
  await pM.screenshot({ path: 'bugtest_mlabel_truncation.png', clip: { x: 0, y: 0, width: 375, height: 70 } });

  // header overlap check - select ALL 14 europe countries to stress mlabel
  let ctxW = await b.newContext({ viewport: { width: 1200, height: 200 } });
  let pW = await ctxW.newPage();
  await pW.goto(file);
  await pW.click('#menu');
  await pW.click('#tree summary:has-text("Europe")');
  const euCodes = ['GB','IE','FR','DE','NL','IT','PT','FI','SE','DK','PL','HU','UA','RU'];
  for (const cc of euCodes) await pW.click(`#tree .row[data-cc="${cc}"] .nm`);
  await pW.click('#menu');
  await pW.waitForTimeout(100);
  await pW.screenshot({ path: 'bugtest_mlabel_14countries.png', clip: { x: 0, y: 0, width: 1200, height: 70 } });

  await b.close();
})();
