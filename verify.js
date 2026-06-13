const { chromium } = require('playwright');
const path = require('path');

const sumOpen = region => `#tree details:has(summary:text-is("${region}"))`;

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
  const r = {};

  await p.goto(file);
  r.menuLabelDefault = (await p.locator('#mlabel').textContent()).trim();

  // 1. open picker -> all continents collapsed by default (nothing selected yet)
  await p.click('#menu');
  r.openDetailsOnFreshOpen = await p.locator('#tree details[open]').count();
  r.continentCount = await p.locator('#tree details').count();

  // 2. the scenario: expand Europe -> France + Bosnia; expand Americas -> Brazil
  await p.click('#tree summary:has-text("Europe")');
  await p.click('#tree .row[data-cc="FR"]');
  r.staysOpenAfterPick = await p.locator('#tree').isVisible();
  await p.click('#tree .row[data-cc="BA"]');
  await p.click('#tree summary:has-text("Americas")');
  await p.click('#tree .row[data-cc="BR"]');
  r.visibleCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  r.labelThree = (await p.locator('#mlabel').textContent()).trim();
  // per-continent "selected" badges visible while collapsed
  r.europeBadge = (await p.locator(sumOpen('Europe') + ' .gsel').textContent()).trim();
  r.americasBadge = (await p.locator(sumOpen('Americas') + ' .gsel').textContent()).trim();

  // 3. reopen picker -> continents with a pick auto-expand, others collapsed
  await p.mouse.click(400, 1000);                       // click outside closes
  r.closedOnOutsideClick = !(await p.locator('#tree').isVisible());
  await p.reload();
  await p.click('#menu');
  r.autoExpandedOnReopen = await p.locator('#tree details[open] summary').allTextContents()
    .then(t => t.map(s => s.replace(/[0-9].*/, '').trim()).sort());

  // 4. search expands matches and hides empty continents
  await p.fill('#search', 'fin');
  r.searchVisibleRows = await p.locator('#tree .row:visible').allTextContents();
  r.searchVisibleContinents = await p.locator('#tree details:visible summary').allTextContents()
    .then(t => t.map(s => s.replace(/[0-9].*/, '').trim()));

  // 5. quick actions
  await p.fill('#search', '');
  await p.click('#selpins');
  r.pinnedCodes = await p.locator('article:visible').evaluateAll(
    els => [...new Set(els.map(e => e.dataset.code))].sort());
  await p.click('#menu'); await p.click('#selall');
  r.allCount = await p.locator('article:visible').count();

  // 6. mute still works
  await p.click('#gear');
  await p.fill('#mute', 'world cup');
  await p.locator('#mute').dispatchEvent('change');
  r.mutedSome = (await p.locator('article:visible').count()) < r.allCount;

  // screenshots
  await p.click('#gear'); await p.click('#menu');
  await p.click('#tree summary:has-text("Asia")');
  await p.screenshot({ path: 'preview_picker.png' });

  const ctx2 = await b.newContext({ viewport: { width: 820, height: 1200 }, deviceScaleFactor: 2 });
  const p2 = await ctx2.newPage();
  await p2.goto(file);
  r.freshLabel = (await p2.locator('#mlabel').textContent()).trim();
  await p2.screenshot({ path: 'preview.png' });

  console.log(JSON.stringify(r, null, 2));
  await b.close();
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
