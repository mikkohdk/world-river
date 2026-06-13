const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  const r = {};

  await p.goto(file);
  // 0. ONE entry point: a single #menu button, no separate #gear
  r.menuButtons = await p.locator('header button').count();
  r.hasGear = await p.locator('#gear').count();
  r.menuLabelDefault = (await p.locator('#mlabel').textContent()).trim();

  // 1. menu opens everything; continents collapsed; settings section present
  await p.click('#menu');
  r.treeVisible = await p.locator('#tree').isVisible();
  r.openDetailsOnFreshOpen = await p.locator('#tree details[open]').count();
  r.continentCount = await p.locator('#tree details[data-region]').count();
  r.hasMutedSection = await p.locator('#setgrp summary').textContent().then(t => t.includes('Muted'));

  // 2. select France, Bosnia? (Bosnia removed) -> France + Brazil across two continents
  await p.click('#tree summary:has-text("Europe")');
  await p.click('#tree .row[data-cc="FR"] .nm');
  r.staysOpen = await p.locator('#tree').isVisible();
  await p.click('#tree summary:has-text("Americas")');
  await p.click('#tree .row[data-cc="BR"] .nm');
  r.visibleCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  r.labelTwo = (await p.locator('#mlabel').textContent()).trim();

  // 3. pin via the star on a row (not selection) — pin Japan, don't select it
  await p.click('#tree summary:has-text("Asia")');
  await p.click('#tree .row[data-cc="JP"] .pin');
  r.jpPinnedNotSelected = await p.locator('#tree .row[data-cc="JP"]').evaluate(
    e => e.classList.contains('pinned') && !e.classList.contains('sel'));
  r.pinnedQuickActionShown = await p.locator('#selpins').isVisible();
  // persists across reload
  await p.reload();
  await p.click('#menu');
  r.labelAfterReload = (await p.locator('#mlabel').textContent()).trim();
  await p.click('#tree summary:has-text("Asia")');
  r.jpStillPinned = await p.locator('#tree .row[data-cc="JP"]').evaluate(e => e.classList.contains('pinned'));

  // 4. muted words live in the same menu; badge + count update
  await p.click('#setgrp summary');
  await p.fill('#mute', 'world cup, royals');
  await p.locator('#mute').dispatchEvent('change');
  r.muteBadge = (await p.locator('#mutebadge').textContent()).trim();
  r.muteCount = (await p.locator('#mutecount').textContent()).trim();

  // 5. quick actions: ★ Pinned then All
  await p.click('#selpins');
  r.pinnedViewCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  await p.click('#menu'); await p.click('#selall');
  r.allCount = await p.locator('article:visible').count();

  // 6. search hides the settings section + non-matching continents
  await p.click('#menu');
  await p.fill('#search', 'jap');
  r.searchSettingsHidden = !(await p.locator('#setgrp').isVisible());
  r.searchVisibleRows = await p.locator('#tree .row:visible .nm').allTextContents();

  await p.fill('#search', '');
  await p.click('#tree summary:has-text("Asia")');
  await p.screenshot({ path: 'preview_menu.png' });

  const ctx2 = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p2 = await ctx2.newPage();
  await p2.goto(file);
  await p2.screenshot({ path: 'preview.png' });

  console.log(JSON.stringify(r, null, 2));
  await b.close();
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
