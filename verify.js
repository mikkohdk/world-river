const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  const r = {};

  await p.goto(file);
  // 1. compact header: tree hidden by default, menu shows "All"
  r.treeHiddenByDefault = !(await p.locator('#tree').isVisible());
  r.menuLabel = (await p.locator('#mlabel').textContent()).trim();

  // 2. open tree -> Pinned row visible (FI/DK seeded), continents present
  await p.click('#menu');
  r.pinnedRowVisible = await p.locator('#tree [data-f="PINNED"]').isVisible();
  r.continents = await p.locator('#tree summary').allTextContents();

  // 3. country select: expand Asia, click Japan -> only JP articles, label updates
  await p.click('#tree summary:has-text("Asia")');
  await p.click('#tree .row[data-f="JP"]');
  r.treeClosesOnSelect = !(await p.locator('#tree').isVisible());
  r.onlyJPVisible = await p.locator('article:visible').evaluateAll(
    els => els.length > 0 && els.every(e => e.dataset.code === 'JP'));
  r.labelAfterJP = (await p.locator('#mlabel').textContent()).trim();

  // 4. persists across reload
  await p.reload();
  r.labelAfterReload = (await p.locator('#mlabel').textContent()).trim();

  // 5. region filter: All Europe -> only Europe articles, several countries
  await p.click('#menu');
  await p.click('#tree summary:has-text("Europe")');
  await p.click('#tree .row[data-f="R:Europe"]');
  const regions = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.region))]);
  r.europeOnlyRegion = regions;
  r.europeCountryCount = await p.locator('article:visible').evaluateAll(
    els => new Set(els.map(e => e.dataset.code)).size);

  // 6. pinned view from tree
  await p.click('#menu');
  await p.click('#tree .row[data-f="PINNED"]');
  r.pinnedViewCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());

  // 7. localized absolute times (no more "5m" relatives)
  r.sampleTime = (await p.locator('article time').first().textContent()).trim();
  r.updatedStamp = (await p.locator('#upd').textContent()).trim();

  // 8. mute via gear panel still works
  await p.click('#tree .row[data-f="ALL"]').catch(() => {});
  await p.click('#menu'); await p.click('#tree .row[data-f="ALL"]');
  const before = await p.locator('article:visible').count();
  await p.click('#gear');
  await p.fill('#mute', 'world cup, trump');
  await p.locator('#mute').dispatchEvent('change');
  r.mutedHidden = before - await p.locator('article:visible').count();

  await p.screenshot({ path: 'preview_panel.png' });

  // 9. tree open screenshot + fresh-profile default
  await p.click('#gear'); await p.click('#menu');
  await p.screenshot({ path: 'preview_tree.png' });

  const ctx2 = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p2 = await ctx2.newPage();
  await p2.goto(file);
  await p2.screenshot({ path: 'preview.png' });
  r.freshDefaultLabel = (await p2.locator('#mlabel').textContent()).trim();

  console.log(JSON.stringify(r, null, 2));
  await b.close();
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
