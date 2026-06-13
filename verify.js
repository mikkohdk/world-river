const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  const r = {};

  await p.goto(file);
  r.menuLabelDefault = (await p.locator('#mlabel').textContent()).trim();

  // 1. the user's scenario: select France, Bosnia and Brazil — picker stays open
  await p.click('#menu');
  await p.click('#tree .row[data-cc="FR"]');
  r.staysOpenAfterPick = await p.locator('#tree').isVisible();
  await p.click('#tree .row[data-cc="BA"]');
  await p.click('#tree .row[data-cc="BR"]');
  r.visibleCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  r.labelThree = (await p.locator('#mlabel').textContent()).trim();   // names, joined
  r.checkedRows = await p.locator('#tree .row.sel').count();

  // 2. click outside closes; selection persists across reload
  await p.screenshot({ path: 'preview_tree.png' });
  await p.mouse.click(400, 900);
  r.closedOnOutsideClick = !(await p.locator('#tree').isVisible());
  await p.reload();
  r.labelAfterReload = (await p.locator('#mlabel').textContent()).trim();

  // 3. deselect Bosnia (toggle off)
  await p.click('#menu');
  await p.click('#tree .row[data-cc="BA"]');
  r.codesAfterDeselect = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());

  // 4. search narrows the list
  await p.fill('#search', 'fin');
  r.searchVisibleRows = await p.locator('#tree .row:visible').allTextContents();
  r.searchGroupLabels = await p.locator('#tree .glab:visible').allTextContents();

  // 5. quick actions: Pinned (FI+DK seeded) and All
  await p.click('#selpins');
  r.pinnedCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  await p.click('#menu'); await p.click('#selall');
  r.allCount = await p.locator('article:visible').count();

  // 6. mute via gear panel still works
  await p.click('#gear');
  await p.fill('#mute', 'world cup');
  await p.locator('#mute').dispatchEvent('change');
  r.mutedSome = (await p.locator('article:visible').count()) < r.allCount;

  // 7. fresh profile defaults
  const ctx2 = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p2 = await ctx2.newPage();
  await p2.goto(file);
  r.freshLabel = (await p2.locator('#mlabel').textContent()).trim();
  await p2.screenshot({ path: 'preview.png' });

  console.log(JSON.stringify(r, null, 2));
  await b.close();
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
