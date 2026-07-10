"""
Fetch the curated roster and render a calm, single-file news river -> index.html

  python build.py            # fetch + render index.html
  python build.py --health   # just report which feeds are live / quiet / dead

Design goals: per-feed fault isolation (one dead feed never kills the run),
no server, no API keys, one static file you can open or schedule.

Personalization is client-side (localStorage), so it survives rebuilds:
sticky filter, read-dimming, new-since-last-visit dots,
muted words (gear panel). Country selection is a continent->country tree
behind the filter button; times are rendered in the visitor's own timezone.
"""
import re
import sys
import time
import html
import calendar
import argparse
from datetime import datetime, timezone

import requests
import feedparser

# feeds.flag() (cc -> emoji) is intentionally left in feeds.py for future use.
from feeds import COUNTRIES, REGIONS, REGION_OF

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Browser-like prefix (several news CDNs 403 non-browser UAs) + honest bot tag.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
      "WorldRiver/1.0 (personal news aggregator; fetches each feed 2x/hour)")

PER_SOURCE_CAP = 12     # stop one prolific feed (e.g. DW ~149) from flooding the river
TOTAL_CAP      = 250    # max items rendered
TIMEOUT        = 15


def clean_summary(raw, title):
    """Feed description -> a clean one-line standfirst (the 'inset'). Strips HTML,
    boilerplate tails, and anything that just echoes the headline."""
    s = re.sub(r"<[^>]+>", " ", raw or "")
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(?i)\s*(continue reading.*|read more.*|the post .*?appeared first.*)$", "", s).strip()
    if len(s) < 25:
        return ""                                   # too short to be a real dek
    if s[:40].lower() == (title or "")[:40].lower():
        return ""                                   # just repeats the title
    return s[:240]


def fetch_source(country, source_name, url):
    """Return (items, status_str). Never raises — failures become a status."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
    except Exception as e:
        return [], f"DEAD ({type(e).__name__})"
    if r.status_code != 200:
        return [], f"HTTP {r.status_code}"
    d = feedparser.parse(r.content)
    if not d.entries:
        return [], "EMPTY"

    items = []
    now = int(time.time())
    seen_urls = set()
    # Spanish stop words (simple language filter)
    spanish_stops = {"el", "la", "de", "que", "y", "es", "en", "por", "para", "con", "fubolistas", "futbolistas", "fútbol", "español"}

    for e in d.entries[:PER_SOURCE_CAP]:
        title = (e.get("title") or "").strip()
        link = e.get("link") or ""
        if not title or not link:
            continue
        # skip duplicates
        if link in seen_urls:
            continue
        seen_urls.add(link)
        # skip sponsored/promoted content
        if "/promoted/" in link or "/sponsored/" in link or "/advertorial/" in link:
            continue
        # simple Spanish language filter: if most words are Spanish stop words, skip
        title_words = set(title.lower().split())
        if len(title_words) > 3 and len(title_words & spanish_stops) > len(title_words) * 0.5:
            continue
        tstruct = e.get("published_parsed") or e.get("updated_parsed")
        ts = calendar.timegm(tstruct) if tstruct else None  # feedparser dates are UTC
        # skip articles older than 7 days
        if ts and (now - ts) > 604800:
            continue
        items.append({
            "title": title,
            "summary": clean_summary(e.get("summary") or e.get("description") or "", title),
            "link": link,
            "source": source_name,
            "country": country["name"],
            "code": country["cc"],
            "region": REGION_OF.get(country["cc"], "Other"),
            "ts": ts,
        })
    return items, f"OK ({len(items)})"


def _recency_key(x):
    return (x["ts"] is not None, x["ts"] or 0)


def gather():
    """Fetch all sources, then ROUND-ROBIN interleave by country so no single
    feed can dominate (and every country shows before any country repeats).
    Future timestamps are clamped — several feeds publish local time as UTC,
    landing 'in the future' and otherwise hijacking the top of the river."""
    now = int(time.time())
    health, by_country = [], []
    for c in COUNTRIES:
        citems = []
        for name, url in c["sources"]:
            items, status = fetch_source(c, name, url)
            health.append((c["cc"], name, status))
            citems.extend(items)
            print(f"  {c['cc']} {name:<20} {status}")
        for it in citems:
            if it["ts"] and it["ts"] > now:
                it["ts"] = now                      # clamp future dates
        citems.sort(key=_recency_key, reverse=True)  # newest first within a country
        if citems:
            by_country.append(citems)

    # order countries by their freshest headline, then take one per round
    by_country.sort(key=lambda lst: _recency_key(lst[0]), reverse=True)
    interleaved, rounds = [], max(len(l) for l in by_country)
    for r in range(rounds):
        for lst in by_country:
            if r < len(lst):
                interleaved.append(lst[r])
    return interleaved[:TOTAL_CAP], health


# ---------------------------------------------------------------- rendering
# Token-replaced (__TREE__ etc.), not str.format — the JS is full of braces.

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The River</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --paper-0: #FAF9F6; --paper-1: #FFFFFF; --paper-2: #F3F1EC; --paper-3: #ECE9E2;
    --ink-0: #1A1916; --ink-1: #2E2C28; --ink-2: #6B6760; --ink-3: #9A968D;
    --line-1: #ECE8DF; --line-2: #DCD7CC;
    --cobalt-2: #176C97; --cobalt-3: #135B80;
    --surface-app: var(--paper-0); --surface-hover: var(--paper-3);
    --text-strong: var(--ink-0); --text-body: var(--ink-1);
    --text-muted: var(--ink-2); --text-subtle: var(--ink-3);
    --border-subtle: var(--line-1); --border-default: var(--line-2);
    --accent: var(--cobalt-2); --accent-hover: var(--cobalt-3);
    --focus-ring: rgba(23, 108, 151, 0.32);

    --font-display: 'Newsreader', Georgia, 'Times New Roman', serif;
    --font-sans: 'Hanken Grotesk', system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
    --fs-xs: 12px; --fs-sm: 13px; --fs-base: 15px; --fs-md: 16px; --fs-lg: 18px;
    --tracking-caps: 0.08em;
    --radius-md: 8px; --radius-pill: 999px;
    --shadow-focus: 0 0 0 3px var(--focus-ring);
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--surface-app); color:var(--text-body);
    font-family:var(--font-sans); -webkit-font-smoothing:antialiased;
  }
  a { color:inherit; }
  :focus-visible { outline:none; box-shadow:var(--shadow-focus); border-radius:4px; }

  .col { max-width:720px; margin:0 auto; padding:0 20px; }

  /* ---- masthead / folio (sticky) ---- */
  header { position:sticky; top:0; background:var(--surface-app); z-index:10; }
  .app-head { display:flex; flex-direction:column; padding-top:18px; border-top:2px solid var(--ink-0); }
  .masthead { display:flex; align-items:center; justify-content:space-between; width:100%;
              font-family:var(--font-display); font-size:42px; font-weight:600;
              line-height:.9; color:var(--text-strong);
              text-decoration:none; }
  .masthead .orn { font-size:15px; color:var(--accent); transform:translateY(-4px); }
  .motto { font-family:var(--font-display); font-style:italic;
           font-size:var(--fs-md); color:var(--text-muted); white-space:nowrap; text-decoration:none; }
  .masthead:hover, .motto:hover { color:var(--accent); }
  .folio { display:flex; align-items:center; justify-content:space-between; width:100%;
           margin-top:14px; padding:9px 0; border-top:1px solid var(--border-subtle);
           border-bottom:1px solid var(--border-default); gap:14px; }
  .motto { min-width:0; overflow:hidden; text-overflow:ellipsis; }
  .folio-right { display:flex; align-items:center; gap:14px; flex:0 0 auto; }
  #upd { font-family:var(--font-mono); font-size:var(--fs-sm); color:var(--text-subtle); }
  #mlabel { font-size:var(--fs-base); color:var(--text-muted);
            max-width:40vw; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
  #menu { position:relative; width:28px; height:28px; border:0; background:transparent;
          color:var(--text-body); cursor:pointer; padding:0; }
  #menu:hover { color:var(--text-strong); }
  #menu.open { color:var(--accent); }
  #menu .bar { position:absolute; left:4px; right:4px; height:2px;
               background:currentColor; border-radius:2px;
               transition:transform .2s ease-out, opacity .15s ease-out; }
  #menu .bar:nth-child(1) { top:8px; }
  #menu .bar:nth-child(2) { top:13px; }
  #menu .bar:nth-child(3) { top:18px; }
  #menu.open .bar:nth-child(1) { transform:translateY(5px) rotate(45deg); }
  #menu.open .bar:nth-child(2) { opacity:0; transform:scaleX(.35); }
  #menu.open .bar:nth-child(3) { transform:translateY(-5px) rotate(-45deg); }
  @media (prefers-reduced-motion:reduce) { #menu .bar { transition:none; } .tri { transition:none; } }
  @media (max-width:480px) {
    #upd { display:none; }
    #mlabel { max-width:25vw; }
  }

  /* ---- river ---- */
  main { padding:4px 0 60px; }
  article.row { padding:28px 0; border-bottom:1px solid var(--border-subtle); position:relative; }
  article.row:last-child { border-bottom:0; }
  .meta-line { display:flex; align-items:center; gap:8px; font-size:var(--fs-base);
               color:var(--text-muted); white-space:nowrap; overflow:hidden; }
  .meta-line .source { color:var(--text-subtle); }
  .meta-line .sep { color:var(--text-subtle); }
  .newdot { width:7px; height:7px; border-radius:50%; background:var(--accent);
            display:inline-block; flex:0 0 auto; }
  .meta-line .time { margin-left:auto; font-family:var(--font-mono); font-size:var(--fs-sm);
                      color:var(--text-subtle); flex:0 0 auto; }
  a.headline { font-family:var(--font-display); font-size:27px; font-weight:500;
               letter-spacing:-0.01em; line-height:1.22; color:var(--text-strong);
               margin-top:11px; max-width:60ch; text-decoration:none; display:block; }
  a.headline:hover { color:var(--accent); }
  a.standfirst { font-size:16.5px; line-height:1.5; color:var(--text-muted);
                 margin:9px 0 0; max-width:64ch; text-wrap:pretty; text-decoration:none; display:block; }
  a.standfirst:hover { color:var(--accent); }
  article.row.is-read .headline, article.row.is-read .standfirst { opacity:.42; }

  footer.colophon { padding:0 0 60px; color:var(--text-subtle); font-size:var(--fs-sm); }
  footer.colophon a { color:var(--accent); }

  /* ---- menu panel ---- */
  #tree { padding:10px 16px 16px; max-height:70vh; overflow:auto;
          background:rgba(23,108,151,.05); border-left:2px solid var(--accent);
          border-radius:0 var(--radius-md) var(--radius-md) 0; margin-top:14px; }
  .menu-edge { display:flex; align-items:center; gap:10px; padding:8px 0;
               font-family:var(--font-mono); font-size:var(--fs-xs);
               letter-spacing:var(--tracking-caps); text-transform:uppercase;
               color:var(--accent); font-weight:500; }
  .menu-edge .dot { width:7px; height:7px; border-radius:50%; background:var(--accent); flex:0 0 auto; }
  .menu-edge .ln { flex:1; height:1px; background:var(--accent); opacity:.28; }
  .search { width:100%; height:44px; border-radius:var(--radius-md);
            border:1px solid var(--border-default); background:var(--paper-1);
            display:flex; align-items:center; padding:0 14px; gap:10px;
            font-size:var(--fs-md); color:var(--text-body); margin-bottom:14px; }
  .search input { border:0; outline:0; background:none; flex:1; font:inherit; color:inherit; }
  .search input::placeholder { color:var(--text-subtle); }
  .search svg { width:18px; height:18px; color:var(--text-subtle); flex:0 0 auto; }

  .pill { display:inline-flex; align-items:center; height:34px; padding:0 18px;
          border-radius:var(--radius-pill); border:1px solid var(--border-default);
          background:var(--paper-1); font-size:var(--fs-sm); color:var(--text-body);
          margin:0 8px 18px 0; cursor:pointer; }
  .pill:hover { background:var(--surface-hover); }

  .selected-strip { display:flex; align-items:center; gap:12px; margin-bottom:18px; }
  .selected-strip.hide { display:none; }
  .clear-all { flex:0 0 auto; width:30px; height:30px; display:grid; place-items:center;
               border:0; background:none; padding:0; color:var(--text-subtle); cursor:pointer; }
  .clear-all:hover { color:var(--accent); }
  .clear-all svg { width:18px; height:18px; }
  .chips { flex:1; min-width:0; display:flex; align-items:center; gap:8px; overflow-x:auto;
           scrollbar-width:none; -webkit-overflow-scrolling:touch;
           -webkit-mask-image:linear-gradient(to right, transparent 0, #000 8px, #000 calc(100% - 20px), transparent 100%);
           mask-image:linear-gradient(to right, transparent 0, #000 8px, #000 calc(100% - 20px), transparent 100%); }
  .chips::-webkit-scrollbar { display:none; }
  .chip { flex:0 0 auto; display:inline-flex; align-items:center; gap:6px; height:30px;
          padding:0 7px 0 14px; border-radius:var(--radius-pill); border:1px solid var(--border-default);
          background:var(--paper-1); font-size:var(--fs-sm); color:var(--text-body); white-space:nowrap; }
  .chip-x { display:grid; place-items:center; width:18px; height:18px; border-radius:50%;
            color:var(--text-subtle); cursor:pointer; }
  .chip-x:hover { color:var(--accent); background:var(--paper-3); }
  .chip-x svg { width:11px; height:11px; }
  .sel-count { flex:0 0 auto; font-family:var(--font-mono); font-size:var(--fs-xs);
                letter-spacing:var(--tracking-caps); text-transform:uppercase;
                color:var(--text-subtle); white-space:nowrap; }

  .group { margin-bottom:4px; }
  .group-head { display:flex; align-items:center; gap:10px; padding:7px 0;
                user-select:none; list-style:none; }
  .group-head::-webkit-details-marker { display:none; }
  .tri-btn { border:0; background:none; padding:0; cursor:pointer;
             display:flex; align-items:center; flex:0 0 auto; }
  .group-name { cursor:pointer; }
  .tri { width:0; height:0; border-top:5px solid transparent; border-bottom:5px solid transparent;
         border-left:6px solid var(--text-subtle); transition:transform .12s; flex:0 0 auto; }
  details[open] > .group-head .tri { transform:rotate(90deg); }
  .group[data-region].open > .group-head .tri { transform:rotate(90deg); }
  .group[data-region] .rows { display:none; }
  .group[data-region].open .rows { display:block; }
  .group-name { font-family:var(--font-mono); font-size:var(--fs-xs); letter-spacing:var(--tracking-caps);
                text-transform:uppercase; color:var(--text-muted); font-weight:500; }
  .group-count { font-family:var(--font-mono); font-size:var(--fs-xs); color:var(--text-subtle); }
  .group-sel { margin-left:auto; font-family:var(--font-mono); font-size:var(--fs-xs);
               letter-spacing:var(--tracking-caps); text-transform:uppercase;
               color:var(--accent); font-weight:500; }
  .group-sel:empty { display:none; }

  .country-row { display:flex; align-items:center; height:46px; padding:0 10px;
                 border-radius:var(--radius-md); font-size:var(--fs-lg); color:var(--text-body);
                 cursor:pointer; }
  .country-row:hover { background:var(--surface-hover); }
  .country-row .nm { flex:1; }
  .country-row .check { width:17px; height:17px; color:var(--accent); flex:0 0 auto; }
  .country-row .check.hidden { visibility:hidden; }

  .group#setgrp { margin-top:10px; }
  #setgrp .search { margin:6px 0 0; }
  #setgrp .search input { font-family:var(--font-mono); font-size:var(--fs-sm); }
  .muted-cap { font-size:var(--fs-base); color:var(--text-subtle); margin:10px 0 6px; }

  .hide, .hideF, .hideM { display:none !important; }
</style></head>
<body>
<header><div class="col">
  <div class="app-head">
    <a class="masthead" href="."><span>T</span><span>H</span><span>E</span><span class="orn">&#9670;</span><span>R</span><span>I</span><span>V</span><span>E</span><span>R</span></a>
    <div class="folio">
      <a class="motto" href=".">The world, in its own words.</a>
      <div class="folio-right">
        <span id="upd" data-ts="__BUILT__"></span>
        <span id="mlabel">All</span>
        <button id="menu" aria-label="Open menu"><span class="bar"></span><span class="bar"></span><span class="bar"></span></button>
      </div>
    </div>
  </div>
  <div id="tree" class="hide">
    <div class="menu-edge"><span class="dot"></span><span>Menu</span><span class="ln"></span></div>
    <div class="selected-strip hide" id="selstrip">
      <button class="clear-all" id="clearsel" aria-label="Clear all selected"><svg viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
        aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/></svg></button>
      <div class="chips" id="chips"></div>
      <span class="sel-count" id="selcount"></span>
    </div>
    __PICKER__
    <details class="group" id="setgrp"><summary class="group-head"><span class="tri"></span><span class="group-name">Muted words</span><span class="group-sel" id="mutebadge"></span></summary>
      <div class="rows">
        <div class="search"><input id="mute" placeholder="comma-separated, e.g. world cup, royals"></div>
        <div id="mutecount" class="muted-cap"></div>
      </div>
    </details>
    <details class="group" id="feedbackgrp">
      <summary class="group-head"><span class="tri"></span><span class="group-name">Feedback</span></summary>
      <div style="display:flex; align-items:center; gap:8px;">
        <div class="search" style="flex:1; margin-bottom:0;">
          <input id="fbtext" placeholder="Suggest a source, report a bug, or leave feedback&hellip;">
        </div>
        <button id="fbsend" class="pill" style="margin:0; flex:0 0 auto; height:44px;">Send</button>
      </div>
      <p class="muted-cap" id="fbstatus"></p>
    </details>
    <div class="menu-edge"><span class="ln"></span><span>End</span><span class="dot"></span></div>
  </div>
</div></header>
<main id="feed" class="col">
__ITEMS__
</main>
<footer class="colophon col">__FOOTER__<br>
Menu: pick countries and mute words &middot; clicked headlines dim &middot;
<span style="color:var(--accent)">&#9679;</span> = new since your last visit</footer>
<script>
  const LS = k => { try { return JSON.parse(localStorage.getItem('wr:'+k)); } catch(e){ return null; } };
  const SV = (k,v) => { try { localStorage.setItem('wr:'+k, JSON.stringify(v)); } catch(e){} };

  let muted  = LS('muted')  ?? [];
  let sel    = LS('sel');                       // selected countries; [] = all
  if (sel == null) {
    const old = LS('filter');                   // migrate from the single-filter era
    sel = (typeof old === 'string' && /^[A-Z]{2}$/.test(old)) ? [old] : [];
  }
  const read = new Set(LS('read') ?? []);
  const prevVisit = LS('visit') ?? 0;
  SV('visit', Math.floor(Date.now()/1000));

  const tree     = document.getElementById('tree');
  const menuBtn  = document.getElementById('menu');
  const mlabel   = document.getElementById('mlabel');
  const articles = [...document.querySelectorAll('article.row')];
  const rows     = [...tree.querySelectorAll('.country-row')];
  const groups   = [...tree.querySelectorAll('.group[data-region]')];   // continents only
  const setgrp   = document.getElementById('setgrp');

  // ---- multi-select picker ----
  const CHIP_X_SVG_JS = '__CHIP_X_SVG__';
  const selstrip = document.getElementById('selstrip');
  const chipsEl  = document.getElementById('chips');
  const selcount = document.getElementById('selcount');
  function applyFilter() {
    rows.forEach(r => {
      const isSel = sel.includes(r.dataset.cc);
      r.classList.toggle('sel', isSel);
      r.querySelector('.check').classList.toggle('hidden', !isSel);
    });
    groups.forEach(g => {                              // per-continent selected count
      const n = [...g.querySelectorAll('.country-row')].filter(r => r.classList.contains('sel')).length;
      g.querySelector('.group-sel').textContent = n ? n + ' selected' : '';
    });
    articles.forEach(a =>
      a.classList.toggle('hideF', sel.length > 0 && !sel.includes(a.dataset.code)));
    const nameOf = cc => rows.find(r => r.dataset.cc === cc).dataset.label;
    mlabel.textContent =
        sel.length === 0 ? 'All'
      : sel.length === 1 ? nameOf(sel[0])
      : sel.length + ' filters';
    selstrip.classList.toggle('hide', sel.length === 0);
    chipsEl.innerHTML = sel.map(cc => {
      const label = nameOf(cc);
      return `<span class="chip" data-cc="${cc}">${label}<span class="chip-x" role="button" `
           + `aria-label="Remove ${label}">${CHIP_X_SVG_JS}</span></span>`;
    }).join('');
    selcount.textContent = sel.length ? sel.length + (sel.length === 1 ? ' country' : ' countries') : '';
    SV('sel', sel);
  }
  chipsEl.addEventListener('click', e => {
    const x = e.target.closest('.chip-x'); if (!x) return;
    const cc = x.closest('.chip').dataset.cc;
    sel = sel.filter(c => c !== cc);
    applyFilter();
  });
  document.getElementById('clearsel').onclick = () => { sel = []; applyFilter(); };
  tree.addEventListener('click', e => {
    if (e.target.closest('.tri-btn')) {
      e.target.closest('.group[data-region]').classList.toggle('open');
      return;
    }
    const gname = e.target.closest('.group-name');
    if (gname && gname.closest('[data-region]')) {
      const group = gname.closest('[data-region]');
      const regionCCs = [...group.querySelectorAll('.country-row')].map(r => r.dataset.cc);
      const allSel = regionCCs.every(cc => sel.includes(cc));
      sel = allSel
        ? sel.filter(cc => !regionCCs.includes(cc))
        : [...new Set([...sel, ...regionCCs])];
      applyFilter();
      return;
    }
    const r = e.target.closest('.country-row'); if (!r) return;
    const cc = r.dataset.cc;
    sel = sel.includes(cc) ? sel.filter(x => x !== cc) : [...sel, cc];
    applyFilter();
  });
  // open the picker: expand only continents with a pick
  function resetPicker() {
    const anySelected = sel.length > 0;
    groups.forEach(g => {
      const show = anySelected
        ? [...g.querySelectorAll('.country-row')].some(r => r.classList.contains('sel'))
        : true;
      g.classList.toggle('open', show);
    });
    setgrp.open = false;
  }
  function closeMenu() { tree.classList.add('hide'); menuBtn.classList.remove('open'); }
  menuBtn.onclick = e => {
    e.stopPropagation();
    const opening = tree.classList.contains('hide');
    tree.classList.toggle('hide');
    menuBtn.classList.toggle('open', opening);
    menuBtn.setAttribute('aria-label', opening ? 'Close menu' : 'Open menu');
    if (opening) resetPicker();
  };
  document.addEventListener('click', e => {            // click outside closes
    if (!e.target.closest('header')) closeMenu();
  });
  document.addEventListener('keydown', e => {           // Escape closes
    if (e.key === 'Escape' && !tree.classList.contains('hide')) closeMenu();
  });

  // ---- muted words (now inside the single menu) ----
  const muteEl = document.getElementById('mute');
  muteEl.value = muted.join(', ');
  muteEl.addEventListener('change', () => {
    muted = muteEl.value.split(',').map(w => w.trim().toLowerCase()).filter(Boolean);
    SV('muted', muted); applyMute();
  });
  function applyMute() {
    let n = 0;
    articles.forEach(a => {
      const hit = muted.length && muted.some(w => a.textContent.toLowerCase().includes(w));
      a.classList.toggle('hideM', !!hit);
      if (hit) n++;
    });
    document.getElementById('mutebadge').textContent = muted.length ? muted.length + ' words' : '';
    document.getElementById('mutecount').textContent =
      muted.length ? n + ' headlines muted' : '';
  }

  // ---- feedback (posts to Formspree, no mail client popup) ----
  const fbText = document.getElementById('fbtext');
  const fbStatus = document.getElementById('fbstatus');
  document.getElementById('fbsend').onclick = async () => {
    const msg = fbText.value.trim();
    if (!msg) return;
    fbStatus.textContent = 'Sending…';
    try {
      const res = await fetch('https://formspree.io/f/__FORMSPREE_ID__', {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, page: location.href })
      });
      if (!res.ok) throw new Error('bad response');
      fbText.value = '';
      fbStatus.textContent = 'Thanks — sent.';
    } catch (e) {
      fbStatus.textContent = 'Could not send — try again later.';
    }
  };

  // ---- read-dim + new-dots ----
  document.getElementById('feed').addEventListener('click', e => {
    const l = e.target.closest('a.headline, a.standfirst'); if (!l) return;
    read.add(l.href); SV('read', [...read].slice(-500));
    l.closest('article.row').classList.add('is-read');
  });
  articles.forEach(a => {
    if (read.has(a.querySelector('a.headline').href)) a.classList.add('is-read');
    const ts = +a.dataset.ts || 0;
    if (!a.classList.contains('is-read') && prevVisit && ts > prevVisit)
      a.querySelector('.time').insertAdjacentHTML('beforebegin', '<span class="newdot"></span>');
  });

  // ---- times in the visitor's own timezone (browser locale + tz) ----
  const fmtT = new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' });
  const fmtD = new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short' });
  const today = new Date().toDateString();
  articles.forEach(a => {
    const ts = +a.dataset.ts, t = a.querySelector('.time');
    if (!ts) { t.textContent = ''; return; }
    const d = new Date(ts * 1000);
    t.textContent = d.toDateString() === today
      ? fmtT.format(d) : fmtD.format(d) + ' ' + fmtT.format(d);
    t.title = d.toLocaleString();
  });
  const upd = document.getElementById('upd');
  upd.textContent = 'updated ' + fmtT.format(new Date(+upd.dataset.ts * 1000));

  applyFilter(); applyMute();
</script>
</body></html>"""


CHECK_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polyline points="20 6 9 17 4 12"/></svg>'
)
CHIP_X_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" aria-hidden="true">'
    '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
)

FORMSPREE_ID = "meewvvol"


def build_picker():
    cmap = {c["cc"]: c for c in COUNTRIES}
    # Continents from REGIONS, plus an "Other" bucket for any country not yet
    # mapped — so adding a country to COUNTRIES alone always works.
    groups = {r: [cc for cc in ccs if cc in cmap] for r, ccs in REGIONS.items()}
    leftover = [c["cc"] for c in COUNTRIES if c["cc"] not in REGION_OF]
    if leftover:
        groups["Other"] = leftover

    parts = []
    for region, ccs in groups.items():
        if not ccs:
            continue
        parts.append(
            f'<div class="group" data-region="{region}"><div class="group-head">'
            f'<button class="tri-btn" aria-label="Toggle {region}"><span class="tri"></span></button>'
            f'<span class="group-name">{region}</span>'
            f'<span class="group-count">{len(ccs)}</span><span class="group-sel"></span></div>'
            f'<div class="rows">'
        )
        for cc in ccs:
            label = cmap[cc]["name"]
            parts.append(
                f'<div class="country-row" data-cc="{cc}" data-label="{label}">'
                f'<span class="nm">{label}</span>'
                f'<span class="check hidden">{CHECK_SVG}</span></div>'
            )
        parts.append('</div></div>')
    return "".join(parts)


def render(items, health):
    rows = []
    for it in items:
        rows.append(
            f'<article class="row" data-code="{it["code"]}" data-source="{html.escape(it["source"])}" data-region="{it["region"]}" data-ts="{it["ts"] or 0}">'
            f'<div class="meta-line">'
            f'<span class="country">{html.escape(it["country"])}</span><span class="sep">&middot;</span>'
            f'<span class="source">{html.escape(it["source"])}</span>'
            f'<span class="time"></span></div>'
            f'<a class="headline" href="{html.escape(it["link"])}" target="_blank" rel="noopener">'
            f'{html.escape(it["title"])}</a>'
            + (f'<a class="standfirst" href="{html.escape(it["link"])}" target="_blank" rel="noopener">{html.escape(it["summary"])}</a>' if it.get("summary") else "")
            + '</article>'
        )

    live = sum(1 for _, _, s in health if s.startswith("OK"))
    dead = [f"{c}/{n} [{s}]" for c, n, s in health if not s.startswith("OK")]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    foot = f"{len(items)} headlines · {live}/{len(health)} sources live · built {stamp}"
    if dead:
        foot += "<br>quiet/dead: " + ", ".join(html.escape(d) for d in dead)

    return (PAGE.replace("__PICKER__", build_picker())
                .replace("__ITEMS__", "\n".join(rows))
                .replace("__FOOTER__", foot)
                .replace("__BUILT__", str(int(time.time())))
                .replace("__CHIP_X_SVG__", CHIP_X_SVG.replace("'", "\\'"))
                .replace("__FORMSPREE_ID__", FORMSPREE_ID))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--health", action="store_true", help="only report feed health")
    args = ap.parse_args()

    print("Fetching roster...")
    items, health = gather()

    if args.health:
        live = sum(1 for _, _, s in health if s.startswith("OK"))
        print(f"\n{live}/{len(health)} sources live.")
        return

    out = render(items, health)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"\nWrote index.html — {len(items)} headlines.")


if __name__ == "__main__":
    main()
