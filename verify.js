const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  const r = {};

  await p.goto(file);
  // 1. default pins seeded -> Pinned chip visible, FI/DK starred & moved to front
  r.pinnedChipVisible = await p.locator('.chip[data-code="PINNED"]').isVisible();
  const firstTwo = await p.locator('#chips .chip:nth-child(3), #chips .chip:nth-child(4)')
                          .allTextContents();
  r.firstCountryChips = firstTwo.map(s => s.trim());

  // 2. Pinned view shows only FI+DK articles
  await p.click('.chip[data-code="PINNED"]');
  const codes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))]);
  r.pinnedViewCodes = codes;

  // 3. country filter persists across reload
  await p.click('.chip[data-code="JP"]');
  await p.reload();
  r.filterAfterReload = await p.locator('#chips .chip.on').getAttribute('data-code');
  r.visibleAllJP = await p.locator('article:visible').evaluateAll(
    els => els.every(e => e.dataset.code === 'JP'));

  // 4. mute words hide matching headlines
  await p.click('.chip[data-code="ALL"]');
  const before = await p.locator('article:visible').count();
  await p.click('#gear');
  await p.fill('#mute', 'world cup, trump');
  await p.locator('#mute').dispatchEvent('change');
  const after = await p.locator('article:visible').count();
  r.mutedHidden = before - after;
  r.muteCounterText = await p.locator('#mutecount').textContent();
  await p.screenshot({ path: 'preview_panel.png' });

  // 5. mute persists across reload
  await p.reload();
  r.muteAfterReload = await p.locator('#mute').inputValue();

  // 6. read-dim: click a headline (block navigation), article gets .read, persists
  await p.click('.chip[data-code="ALL"]');
  await ctx.route('**/*', route =>
    route.request().url().startsWith('file://') ? route.continue() : route.abort());
  const pop = ctx.waitForEvent('page').catch(() => null);
  await p.locator('article:visible a.t').first().click();
  const popped = await pop; if (popped) await popped.close();
  r.readAfterClick = await p.locator('article:visible').first()
                            .evaluate(e => e.classList.contains('read'));
  await p.reload();
  r.readAfterReload = await p.locator('article').first()
                             .evaluate(e => e.classList.contains('read'));

  // 7. fresh profile -> defaults (FI/DK pinned, ALL filter)
  const ctx2 = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p2 = await ctx2.newPage();
  await p2.goto(file);
  await p2.screenshot({ path: 'preview.png' });
  r.freshDefaultFilter = await p2.locator('#chips .chip.on').getAttribute('data-code');

  console.log(JSON.stringify(r, null, 2));
  await b.close();
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
