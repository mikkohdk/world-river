const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const file = 'file://' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');

function fresh(b, viewport, opts={}) {
  return b.newContext({ viewport, deviceScaleFactor: 1, ...opts });
}

(async () => {
  const b = await chromium.launch();
  const report = { consoleErrors: [], findings: [] };

  // ============ DESKTOP ============
  let ctx = await fresh(b, { width: 1200, height: 900 });
  let p = await ctx.newPage();
  p.on('console', msg => { if (['error','warning'].includes(msg.type())) report.consoleErrors.push('[desktop] ' + msg.type() + ': ' + msg.text()); });
  p.on('pageerror', err => report.consoleErrors.push('[desktop pageerror] ' + err.message));
  await p.goto(file);

  await p.screenshot({ path: 'bugtest_desktop.png', fullPage: false });

  // --- check dark theme wiring ---
  report.findings.push({
    id: 'dark-theme',
    note: 'data-theme attr on html/body: ' + await p.evaluate(() => document.documentElement.getAttribute('data-theme') + ' / ' + document.body.getAttribute('data-theme')),
  });
  // check if tokens css files are even linked
  report.findings.push({
    id: 'stylesheets-linked',
    note: 'linked stylesheets: ' + await p.evaluate(() => [...document.styleSheets].map(s => s.href).filter(Boolean).join(', ') || '(none - inline only)'),
  });

  // --- header z-index / sticky check ---
  await p.click('#menu');
  await p.waitForTimeout(150);
  const headerBox = await p.locator('header').boundingBox();
  const treeBox = await p.locator('#tree').boundingBox();
  report.findings.push({ id: 'menu-open-desktop', headerBox, treeBox });
  await p.screenshot({ path: 'bugtest_desktop_menu.png' });

  // scroll the main feed while menu open - does header stay sticky & tree overlay correctly?
  await p.evaluate(() => window.scrollBy(0, 600));
  await p.waitForTimeout(150);
  await p.screenshot({ path: 'bugtest_desktop_menu_scrolled.png' });
  const headerBoxAfterScroll = await p.locator('header').boundingBox();
  report.findings.push({ id: 'header-after-scroll', headerBoxAfterScroll });
  await p.evaluate(() => window.scrollTo(0,0));

  // ============ MULTI-CONTINENT SELECT/DESELECT ============
  await p.click('#tree summary:has-text("Europe")');
  await p.click('#tree .row[data-cc="FR"] .nm');
  await p.click('#tree .row[data-cc="DE"] .nm');
  await p.click('#tree summary:has-text("Asia")');
  await p.click('#tree .row[data-cc="JP"] .nm');
  let mlabel3 = (await p.locator('#mlabel').textContent()).trim();
  let visCodes3 = await p.locator('article:not(.hideF)').evaluateAll(els => [...new Set(els.map(e=>e.dataset.code))].sort());
  report.findings.push({ id: 'multi-select-3-countries', mlabel: mlabel3, visibleCodes: visCodes3 });

  // deselect one (Germany)
  await p.click('#tree .row[data-cc="DE"] .nm');
  let mlabel2 = (await p.locator('#mlabel').textContent()).trim();
  let visCodes2 = await p.locator('article:not(.hideF)').evaluateAll(els => [...new Set(els.map(e=>e.dataset.code))].sort());
  report.findings.push({ id: 'deselect-germany', mlabel: mlabel2, visibleCodes: visCodes2 });

  // gsel counts per continent
  const gselTexts = await p.locator('#tree .grp[data-region] .gsel').evaluateAll(els => els.map(e => ({region: e.closest('.grp').dataset.region, text: e.textContent})));
  report.findings.push({ id: 'gsel-counts', gselTexts });

  // ============ ALL COUNTRIES / PINNED quick actions ============
  // currently sel = [FR, JP]. selpins should be hidden (default pins FI, DK -- wait default pins ARE FI,DK)
  const selpinsVisibleBefore = await p.locator('#selpins').isVisible();
  report.findings.push({ id: 'selpins-visible-with-default-pins', visible: selpinsVisibleBefore });

  // click All countries
  await p.click('#selall');
  let mlabelAll = (await p.locator('#mlabel').textContent()).trim();
  let allCount = await p.locator('article:not(.hideF)').count();
  let treeHiddenAfterAll = await p.locator('#tree').evaluate(e => e.classList.contains('hide'));
  report.findings.push({ id: 'selall-click', mlabel: mlabelAll, visibleCount: allCount, treeHidden: treeHiddenAfterAll });

  // reopen, click Pinned (default pins FI, DK)
  await p.click('#menu');
  await p.click('#selpins');
  let mlabelPinned = (await p.locator('#mlabel').textContent()).trim();
  let pinnedCodes = await p.locator('article:not(.hideF)').evaluateAll(els => [...new Set(els.map(e=>e.dataset.code))].sort());
  report.findings.push({ id: 'selpins-click-default-pins', mlabel: mlabelPinned, visibleCodes: pinnedCodes });

  // ============ remove all pins -> selpins should hide ============
  await p.click('#menu');
  await p.waitForTimeout(100);
  const europeOpenState = await p.locator('#tree details[data-region="Europe"]').evaluate(e => e.open);
  if (!europeOpenState) await p.click('#tree summary:has-text("Europe")');
  await p.waitForTimeout(100);
  // unpin FI and DK (the default pins)
  await p.locator('#tree .row[data-cc="FI"] .pin').click();
  await p.locator('#tree .row[data-cc="DK"] .pin').click();
  const selpinsVisibleAfterUnpinAll = await p.locator('#selpins').isVisible();
  report.findings.push({ id: 'selpins-hidden-when-no-pins', visible: selpinsVisibleAfterUnpinAll });

  // re-pin one country for further testing (pin Japan)
  await p.click('#tree summary:has-text("Asia")');
  await p.click('#tree .row[data-cc="JP"] .pin');

  // ============ PIN PERSISTENCE ACROSS RELOAD ============
  await p.click('#selall'); // reset filter to all, closes tree
  await p.reload();
  await p.click('#menu');
  await p.click('#tree summary:has-text("Asia")');
  const jpPinnedAfterReload = await p.locator('#tree .row[data-cc="JP"]').evaluate(e => e.classList.contains('pinned'));
  const fiPinnedAfterReload = await p.locator('#tree summary:has-text("Europe")').click().then(async () =>
    p.locator('#tree .row[data-cc="FI"]').evaluate(e => e.classList.contains('pinned')));
  report.findings.push({ id: 'pin-persistence', jpPinnedAfterReload, fiPinnedAfterReload_shouldBeFalse: fiPinnedAfterReload });

  // ============ SEARCH BEHAVIOR ============
  await p.fill('#search', 'jap');
  await p.waitForTimeout(100);
  const searchSettingsHidden = !(await p.locator('#setgrp').isVisible());
  const searchVisibleRows = await p.locator('#tree .row:visible .nm').allTextContents();
  const asiaOpenDuringSearch = await p.locator('#tree details[data-region="Asia"]').evaluate(e => e.open);
  const europeHiddenDuringSearch = await p.locator('#tree details[data-region="Europe"]').evaluate(e => e.classList.contains('hide'));
  report.findings.push({ id: 'search-jap', searchSettingsHidden, searchVisibleRows, asiaOpenDuringSearch, europeHiddenDuringSearch });
  await p.screenshot({ path: 'bugtest_desktop_search.png' });

  // search for something matching nothing
  await p.fill('#search', 'zzzzznotacountry');
  await p.waitForTimeout(100);
  const noMatchVisibleRows = await p.locator('#tree .row:visible .nm').count();
  const allGroupsHiddenNoMatch = await p.locator('#tree .grp[data-region]:not(.hide)').count();
  report.findings.push({ id: 'search-no-match', noMatchVisibleRows, allGroupsHiddenNoMatch });

  // search by country code (cc)
  await p.fill('#search', 'fr');
  await p.waitForTimeout(100);
  const frSearchRows = await p.locator('#tree .row:visible .nm').allTextContents();
  report.findings.push({ id: 'search-by-cc-fr', frSearchRows });

  // clear search
  await p.fill('#search', '');
  await p.waitForTimeout(100);
  const setgrpVisibleAfterClear = await p.locator('#setgrp').isVisible();
  report.findings.push({ id: 'search-cleared', setgrpVisibleAfterClear });

  // ============ MUTED WORDS ============
  await p.click('#setgrp summary');
  await p.fill('#mute', 'world cup');
  await p.locator('#mute').dispatchEvent('change');
  await p.waitForTimeout(100);
  const muteBadge1 = (await p.locator('#mutebadge').textContent()).trim();
  const muteCount1 = (await p.locator('#mutecount').textContent()).trim();
  const hiddenCount1 = await p.locator('article.hideM').count();
  report.findings.push({ id: 'mute-world-cup', muteBadge: muteBadge1, muteCount: muteCount1, hiddenCount: hiddenCount1 });
  await p.screenshot({ path: 'bugtest_desktop_muted.png' });

  // mute with no matches
  await p.fill('#mute', 'xyzzyqqqnomatch12345');
  await p.locator('#mute').dispatchEvent('change');
  await p.waitForTimeout(100);
  const muteBadge2 = (await p.locator('#mutebadge').textContent()).trim();
  const muteCount2 = (await p.locator('#mutecount').textContent()).trim();
  const hiddenCount2 = await p.locator('article.hideM').count();
  report.findings.push({ id: 'mute-no-match', muteBadge: muteBadge2, muteCount: muteCount2, hiddenCount: hiddenCount2 });

  // mute with multiple comma-separated words, including one with leading/trailing spaces
  await p.fill('#mute', '  world cup ,  trump  , brazil');
  await p.locator('#mute').dispatchEvent('change');
  await p.waitForTimeout(100);
  const muteBadge3 = (await p.locator('#mutebadge').textContent()).trim();
  const muteCount3 = (await p.locator('#mutecount').textContent()).trim();
  const hiddenCount3 = await p.locator('article.hideM').count();
  const storedMuted = await p.evaluate(() => JSON.parse(localStorage.getItem('wr:muted')));
  report.findings.push({ id: 'mute-multi-words-trimmed', muteBadge: muteBadge3, muteCount: muteCount3, hiddenCount: hiddenCount3, storedMuted });

  // empty mute input
  await p.fill('#mute', '');
  await p.locator('#mute').dispatchEvent('change');
  await p.waitForTimeout(100);
  const muteBadge4 = (await p.locator('#mutebadge').textContent()).trim();
  const muteCount4 = (await p.locator('#mutecount').textContent()).trim();
  const hiddenCount4 = await p.locator('article.hideM').count();
  report.findings.push({ id: 'mute-empty', muteBadge: muteBadge4, muteCount: muteCount4, hiddenCount: hiddenCount4 });

  // mute persistence across reload
  await p.fill('#mute', 'iran');
  await p.locator('#mute').dispatchEvent('change');
  await p.reload();
  await p.click('#menu');
  await p.click('#setgrp summary');
  const muteValAfterReload = await p.inputValue('#mute');
  const muteBadgeAfterReload = (await p.locator('#mutebadge').textContent()).trim();
  report.findings.push({ id: 'mute-persistence', muteValAfterReload, muteBadgeAfterReload });
  // clean up mute for subsequent tests
  await p.fill('#mute', '');
  await p.locator('#mute').dispatchEvent('change');

  // ============ READ-DIMMING ============
  await p.click('#menu'); // close tree
  await p.waitForTimeout(100);
  const firstArticleHrefBefore = await p.locator('article').first().locator('a.t').getAttribute('href');
  const firstArticleClassBefore = await p.locator('article').first().getAttribute('class');
  // middle-click / new-tab links open _blank so regular click triggers handler but also opens new tab; use ctrl-click won't open in headless easily.
  // Instead dispatch click event directly to test the JS handler without navigation issues
  await p.locator('article').first().locator('a.t').evaluate(el => el.click());
  await p.waitForTimeout(150);
  const firstArticleClassAfter = await p.locator('article').first().getAttribute('class');
  const readSetAfterClick = await p.evaluate(() => JSON.parse(localStorage.getItem('wr:read')||'[]'));
  report.findings.push({ id: 'read-dim-click', firstArticleHrefBefore, firstArticleClassBefore, firstArticleClassAfter, readSetIncludes: readSetAfterClick.includes(firstArticleHrefBefore) });

  // reload, check it stays dimmed
  await p.reload();
  await p.waitForTimeout(100);
  const firstArticleClassAfterReload = await p.locator('article').first().getAttribute('class');
  report.findings.push({ id: 'read-dim-persists-reload', firstArticleClassAfterReload });

  // ============ NEW-SINCE-LAST-VISIT DOTS ============
  // First load already wrote 'visit' = now, so on THIS reload .nd dots should reflect prevVisit < article ts
  const ndCountFirstReload = await p.locator('.nd').count();
  report.findings.push({ id: 'nd-dots-after-reload-1', ndCountFirstReload });
  // reload again immediately - prevVisit was just set to ~now, so articles with ts > now (future) won't show; basically dots should disappear or shrink
  await p.reload();
  await p.waitForTimeout(100);
  const ndCountSecondReload = await p.locator('.nd').count();
  report.findings.push({ id: 'nd-dots-after-reload-2', ndCountSecondReload });

  // ============ CLICK OUTSIDE / KEYBOARD ============
  await p.click('#menu');
  await p.waitForTimeout(100);
  let treeVisibleBeforeOutsideClick = await p.locator('#tree').isVisible();
  await p.mouse.click(50, 50); // click far outside header (top-left corner, should be body/blank in main area... actually header spans full width at top)
  // click somewhere definitely outside header - in main content area
  await p.locator('main').click({ position: { x: 10, y: 10 }, force: true }).catch(()=>{});
  await p.waitForTimeout(100);
  let treeVisibleAfterOutsideClick = await p.locator('#tree').isVisible();
  report.findings.push({ id: 'click-outside-closes-menu', treeVisibleBeforeOutsideClick, treeVisibleAfterOutsideClick });

  // Escape key test
  await p.click('#menu');
  await p.waitForTimeout(100);
  let treeVisibleBeforeEsc = await p.locator('#tree').isVisible();
  await p.keyboard.press('Escape');
  await p.waitForTimeout(100);
  let treeVisibleAfterEsc = await p.locator('#tree').isVisible();
  report.findings.push({ id: 'escape-closes-menu', treeVisibleBeforeEsc, treeVisibleAfterEsc });

  // Tab order / focus indicator check
  await p.click('#menu');
  await p.waitForTimeout(100);
  const focusedAfterOpen = await p.evaluate(() => document.activeElement.id || document.activeElement.tagName);
  report.findings.push({ id: 'focus-on-menu-open', focusedAfterOpen });
  // tab a few times and capture focus outline visibility
  await p.keyboard.press('Tab');
  const focused1 = await p.evaluate(() => document.activeElement.outerHTML.slice(0,80));
  await p.keyboard.press('Tab');
  const focused2 = await p.evaluate(() => document.activeElement.outerHTML.slice(0,80));
  report.findings.push({ id: 'tab-order', focused1, focused2 });
  // check focus-visible outline style
  const focusOutline = await p.evaluate(() => {
    const el = document.activeElement;
    const cs = getComputedStyle(el);
    return { outline: cs.outline, outlineStyle: cs.outlineStyle, boxShadow: cs.boxShadow };
  });
  report.findings.push({ id: 'focus-outline-style', focusOutline });

  await p.click('#menu'); // close
  await p.waitForTimeout(100);

  // ============ DATA/CONTENT CHECKS ============
  const dataIssues = await p.evaluate(() => {
    const arts = [...document.querySelectorAll('article')];
    const issues = { emptyTitles: [], noSummary: 0, badHref: [], emptySource: [], emptyCountry: [], longTitles: [], totalArticles: arts.length };
    arts.forEach((a, i) => {
      const title = a.querySelector('a.t');
      const titleText = title ? title.textContent.trim() : '';
      const href = title ? title.getAttribute('href') : '';
      const summary = a.querySelector('p.d');
      const spans = a.querySelectorAll('.m span');
      if (!titleText) issues.emptyTitles.push(i);
      if (!summary) issues.noSummary++;
      if (!href || !/^https?:\/\//.test(href)) issues.badHref.push({i, href});
      if (spans[0] && !spans[0].textContent.trim()) issues.emptyCountry.push(i);
      if (spans[2] && !spans[2].textContent.trim()) issues.emptySource.push(i);
      if (titleText.length > 150) issues.longTitles.push({i, len: titleText.length, code: a.dataset.code, text: titleText.slice(0,60)+'...'});
    });
    return issues;
  });
  report.findings.push({ id: 'data-content-issues', dataIssues });

  // check for raw HTML entities not decoded (visual scan in text)
  const entityIssues = await p.evaluate(() => {
    const arts = [...document.querySelectorAll('article')];
    const found = [];
    arts.forEach((a,i) => {
      const txt = a.textContent;
      if (/&[a-z]+;|&#\d+;/.test(txt)) found.push({i, code: a.dataset.code, snippet: txt.match(/.{0,15}&[a-z#0-9]+;.{0,15}/)?.[0]});
    });
    return found;
  });
  report.findings.push({ id: 'unescaped-entity-check', entityIssues });

  // ============ ACCESSIBILITY CHECKS ============
  const a11y = await p.evaluate(() => {
    const out = {};
    out.menuAriaLabel = document.getElementById('menu').getAttribute('aria-label');
    out.searchHasLabel = !!document.getElementById('search').getAttribute('placeholder');
    out.searchAriaLabel = document.getElementById('search').getAttribute('aria-label');
    out.muteAriaLabel = document.getElementById('mute').getAttribute('aria-label');
    out.pinButtonsAriaLabel = [...document.querySelectorAll('.pin')].slice(0,3).map(b => b.getAttribute('aria-label'));
    out.h1Text = document.querySelector('h1')?.textContent;
    out.landmarks = { header: !!document.querySelector('header'), main: !!document.querySelector('main'), footer: !!document.querySelector('footer') };
    out.langAttr = document.documentElement.getAttribute('lang');
    out.imagesWithoutAlt = [...document.querySelectorAll('img')].filter(i=>!i.alt).length;
    out.linksWithoutText = [...document.querySelectorAll('a')].filter(a=>!a.textContent.trim() && !a.getAttribute('aria-label')).length;
    out.svgAriaHidden = document.querySelector('#menu svg')?.getAttribute('aria-hidden');
    return out;
  });
  report.findings.push({ id: 'accessibility', a11y });

  // ============ VIEWPORT TESTS ============
  // MOBILE 375px
  let ctxM = await fresh(b, { width: 375, height: 812 });
  let pM = await ctxM.newPage();
  pM.on('console', msg => { if (['error','warning'].includes(msg.type())) report.consoleErrors.push('[mobile] ' + msg.type() + ': ' + msg.text()); });
  pM.on('pageerror', err => report.consoleErrors.push('[mobile pageerror] ' + err.message));
  await pM.goto(file);
  await pM.screenshot({ path: 'bugtest_mobile.png', fullPage: false });

  // check for horizontal overflow
  const overflowMobile = await pM.evaluate(() => ({
    bodyScrollWidth: document.body.scrollWidth,
    windowInnerWidth: window.innerWidth,
    docScrollWidth: document.documentElement.scrollWidth,
  }));
  report.findings.push({ id: 'mobile-overflow', overflowMobile });

  // open menu on mobile
  await pM.click('#menu');
  await pM.waitForTimeout(100);
  await pM.screenshot({ path: 'bugtest_mobile_menu.png', fullPage: false });
  const treeBoxMobile = await pM.locator('#tree').boundingBox();
  const treeMaxHeight = await pM.locator('#tree').evaluate(e => getComputedStyle(e).maxHeight);
  report.findings.push({ id: 'mobile-menu-tree', treeBoxMobile, treeMaxHeight, viewportHeight: 812 });

  // check mlabel truncation on mobile with many selections
  await pM.click('#tree summary:has-text("Europe")');
  for (const cc of ['GB','IE','FR','DE','NL']) {
    await pM.click(`#tree .row[data-cc="${cc}"] .nm`);
  }
  const mlabelMobile = (await pM.locator('#mlabel').textContent()).trim();
  const mlabelBox = await pM.locator('#mlabel').boundingBox();
  report.findings.push({ id: 'mlabel-mobile-many-selected', mlabelMobile, mlabelBox });
  await pM.screenshot({ path: 'bugtest_mobile_many_selected.png' });
  await pM.click('#selall'); // reset

  // check article title/text overflow on mobile (find longest title)
  const longTitleOverflowMobile = await pM.evaluate(() => {
    const titles = [...document.querySelectorAll('a.t')];
    let worst = null;
    titles.forEach(t => {
      const overflow = t.scrollWidth - t.clientWidth;
      if (!worst || overflow > worst.overflow) worst = { overflow, text: t.textContent.slice(0,50), scrollWidth: t.scrollWidth, clientWidth: t.clientWidth };
    });
    return worst;
  });
  report.findings.push({ id: 'mobile-title-overflow', longTitleOverflowMobile });

  // check summary line-clamp on mobile (does -webkit-line-clamp work / any overflow)
  const summaryClampCheck = await pM.evaluate(() => {
    const d = document.querySelector('p.d');
    if (!d) return null;
    const cs = getComputedStyle(d);
    return { webkitLineClamp: cs.webkitLineClamp, overflow: cs.overflow, scrollHeight: d.scrollHeight, clientHeight: d.clientHeight };
  });
  report.findings.push({ id: 'mobile-summary-clamp', summaryClampCheck });

  // TABLET 768px
  let ctxT = await fresh(b, { width: 768, height: 1024 });
  let pT = await ctxT.newPage();
  pT.on('console', msg => { if (['error','warning'].includes(msg.type())) report.consoleErrors.push('[tablet] ' + msg.type() + ': ' + msg.text()); });
  pT.on('pageerror', err => report.consoleErrors.push('[tablet pageerror] ' + err.message));
  await pT.goto(file);
  await pT.screenshot({ path: 'bugtest_tablet.png', fullPage: false });
  const overflowTablet = await pT.evaluate(() => ({
    bodyScrollWidth: document.body.scrollWidth,
    windowInnerWidth: window.innerWidth,
  }));
  report.findings.push({ id: 'tablet-overflow', overflowTablet });
  await pT.click('#menu');
  await pT.waitForTimeout(100);
  await pT.screenshot({ path: 'bugtest_tablet_menu.png', fullPage: false });

  // Check tree max-height vs viewport on tablet (60vh of 1024 = 614px)
  const treeMaxHeightTablet = await pT.locator('#tree').evaluate(e => getComputedStyle(e).maxHeight);
  report.findings.push({ id: 'tablet-tree-maxheight', treeMaxHeightTablet });

  // DESKTOP: check #upd / #mlabel overlap at narrow-ish desktop widths (e.g. 1024)
  let ctxD2 = await fresh(b, { width: 1024, height: 800 });
  let pD2 = await ctxD2.newPage();
  await pD2.goto(file);
  // select many countries to maximize mlabel width
  await pD2.click('#menu');
  await pD2.click('#tree summary:has-text("Europe")');
  for (const cc of ['GB','IE','FR','DE']) await pD2.click(`#tree .row[data-cc="${cc}"] .nm`);
  await pD2.click('#menu');
  const hrowOverlap = await pD2.evaluate(() => {
    const h1 = document.querySelector('h1').getBoundingClientRect();
    const upd = document.getElementById('upd').getBoundingClientRect();
    const mlabel = document.getElementById('mlabel').getBoundingClientRect();
    const menu = document.getElementById('menu').getBoundingClientRect();
    return { h1, upd, mlabel, menu,
      mlabelOverlapsMenu: !(mlabel.right <= menu.left || mlabel.left >= menu.right) };
  });
  report.findings.push({ id: 'header-row-overlap-1024', hrowOverlap });
  await pD2.screenshot({ path: 'bugtest_desktop_1024_long_label.png' });

  // ============ COLOR CONTRAST SPOT CHECK (Margin tokens vs actual) ============
  const colorVars = await p.evaluate(() => {
    const cs = getComputedStyle(document.documentElement);
    return {
      bg: cs.getPropertyValue('--bg').trim(),
      ink: cs.getPropertyValue('--ink').trim(),
      meta: cs.getPropertyValue('--meta').trim(),
      accent: cs.getPropertyValue('--accent').trim(),
      line: cs.getPropertyValue('--line').trim(),
    };
  });
  report.findings.push({ id: 'color-vars-in-use', colorVars, note: 'compare to Margin tokens in tokens/colors.css for design-system drift' });

  await b.close();

  fs.writeFileSync(path.join(__dirname, 'bugtest_report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch(e => { console.error('FAIL:', e.message, e.stack); process.exit(1); });
