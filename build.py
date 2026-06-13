"""
Fetch the curated roster and render a calm, single-file news river -> index.html

  python build.py            # fetch + render index.html
  python build.py --health   # just report which feeds are live / quiet / dead

Design goals: per-feed fault isolation (one dead feed never kills the run),
no server, no API keys, one static file you can open or schedule.

Personalization is client-side (localStorage), so it survives rebuilds:
pinned countries, sticky filter, read-dimming, new-since-last-visit dots,
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
    for e in d.entries[:PER_SOURCE_CAP]:
        title = (e.get("title") or "").strip()
        link = e.get("link") or ""
        if not title or not link:
            continue
        tstruct = e.get("published_parsed") or e.get("updated_parsed")
        ts = calendar.timegm(tstruct) if tstruct else None  # feedparser dates are UTC
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
<title>World River</title>
<style>
  :root {
    --bg:#faf9f7; --ink:#1d1d1f; --meta:#9a958c; --line:#eceae5; --accent:#3a6ea5;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif;
  }
  header {
    position:sticky; top:0; background:rgba(250,249,247,.94);
    backdrop-filter:blur(8px); border-bottom:1px solid var(--line);
    padding:14px 24px; z-index:10;
  }
  .wrap { max-width:720px; margin:0 auto; }
  .hrow { display:flex; align-items:center; gap:10px; }
  h1 { font:600 15px/1 -apple-system,sans-serif; letter-spacing:.14em;
       text-transform:uppercase; color:var(--meta); margin:0; }
  #upd { font-size:12px; color:var(--meta); }
  #mlabel { margin-left:auto; font-size:13px; color:var(--meta);
            max-width:55%; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
  #menu { margin-left:10px; border:1px solid var(--line); background:#fff;
          color:var(--ink); border-radius:9px; padding:5px 7px; cursor:pointer;
          display:flex; align-items:center; }
  #menu:hover { border-color:#d8d4cc; }

  /* country picker (multi-select: click rows to toggle, stays open) */
  #tree { border-top:1px solid var(--line); margin-top:13px; padding-top:12px;
          max-height:60vh; overflow:auto; }
  #search { width:100%; border:1px solid var(--line); border-radius:8px;
            padding:7px 10px; margin-bottom:8px; background:#fff;
            font:14px -apple-system,"Segoe UI",sans-serif; color:var(--ink);
            outline:none; }
  #search:focus { border-color:#c9c4ba; }
  #tree .acts { display:flex; gap:7px; margin-bottom:6px; }
  #tree .grp { border-bottom:1px solid var(--line); }
  #tree summary { list-style:none; cursor:pointer; user-select:none;
                  padding:9px 10px; display:flex; align-items:center; gap:8px;
                  font:600 11px/1 -apple-system,sans-serif; letter-spacing:.1em;
                  text-transform:uppercase; color:var(--meta); }
  #tree summary::-webkit-details-marker { display:none; }
  #tree summary::before { content:"\\25B8"; font-size:10px; color:var(--meta);
                          transition:transform .15s; }
  #tree details[open] summary::before { transform:rotate(90deg); }
  #tree summary:hover { color:var(--ink); }
  #tree .gn { color:var(--meta); font-weight:400; letter-spacing:0; }
  #tree .gsel { margin-left:auto; color:var(--accent); font-weight:600;
                letter-spacing:0; font-size:11px; }
  #tree .gsel:empty { display:none; }
  #tree .rows { padding-bottom:6px; }
  #tree .row { padding:7px 10px 7px 26px; border-radius:8px; cursor:pointer;
               font-size:14.5px; display:flex; align-items:center; gap:6px; }
  #tree .row:hover { background:#f1efe9; }
  #tree .row .nm { flex:1; }
  #tree .row .pin { border:none; background:none; cursor:pointer; padding:0 4px;
                    font-size:13px; line-height:1; color:#d3cec4; }
  #tree .row .pin:hover { color:var(--accent); }
  #tree .row.pinned .pin { color:var(--accent); }
  #tree .row .ck { width:14px; text-align:center; color:var(--accent);
                   font-weight:600; visibility:hidden; }
  #tree .row.sel .ck { visibility:visible; }

  /* quick-action chips + muted-words setting */
  .chips { display:flex; flex-wrap:wrap; gap:7px; }
  .chip { border:1px solid var(--line); background:#fff; color:var(--ink);
          border-radius:999px; padding:5px 12px; font-size:13px; cursor:pointer;
          user-select:none; transition:.12s; }
  .chip:hover { border-color:#d8d4cc; }
  .chip.on { background:var(--ink); color:#fff; border-color:var(--ink); }
  #mute { width:100%; border:1px solid var(--line); border-radius:8px;
          padding:7px 10px; font:14px -apple-system,"Segoe UI",sans-serif;
          background:#fff; color:var(--ink); outline:none; }
  #mute:focus { border-color:#c9c4ba; }
  #mutecount { font-size:12px; color:var(--meta); margin-top:6px; }

  /* river */
  main { max-width:720px; margin:0 auto; padding:8px 24px 80px; }
  article { padding:20px 0; border-bottom:1px solid var(--line); }
  article.read { opacity:.45; }
  .m { font-size:12.5px; color:var(--meta); margin-bottom:6px;
       display:flex; gap:8px; align-items:center; }
  .m .dot { opacity:.5; }
  .m time { margin-left:auto; }
  .nd { width:6px; height:6px; border-radius:50%; background:var(--accent);
        display:inline-block; flex:0 0 auto; }
  a.t { color:var(--ink); text-decoration:none; font-size:19px;
        line-height:1.34; display:block; }
  a.t:hover { color:var(--accent); }
  .d { margin:6px 0 0; color:#6f6a62; font-size:14px; line-height:1.46;
       display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
       overflow:hidden; }
  footer { max-width:720px; margin:0 auto; padding:0 24px 60px;
           color:var(--meta); font-size:12.5px; }
  .hide, .hideF, .hideM { display:none !important; }
</style></head>
<body>
<header><div class="wrap">
  <div class="hrow">
    <h1>World River</h1><span id="upd" data-ts="__BUILT__"></span>
    <span id="mlabel">All</span>
    <button id="menu" aria-label="Menu"><svg width="20" height="20" viewBox="0 0 20 20"
      aria-hidden="true"><path d="M3 6h14M3 10h14M3 14h14" stroke="currentColor"
      stroke-width="1.7" stroke-linecap="round"/></svg></button>
  </div>
  <div id="tree" class="hide">
    <input id="search" placeholder="Search countries&hellip;">
    <div class="acts"><span class="chip" id="selall">All countries</span><span
      class="chip hide" id="selpins">&#9733; Pinned</span></div>
    __PICKER__
    <details class="grp" id="setgrp"><summary>Muted words<span class="gsel" id="mutebadge"></span></summary>
      <div class="rows" style="padding:4px 10px 10px">
        <input id="mute" placeholder="comma-separated, e.g. world cup, royals">
        <div id="mutecount"></div>
      </div>
    </details>
  </div>
</div></header>
<main id="feed">
__ITEMS__
</main>
<footer>__FOOTER__<br>
&#9776; menu: pick countries, pin (&#9733;) &amp; mute words &middot; clicked headlines dim &middot;
<span style="color:var(--accent)">&#9679;</span> = new since your last visit</footer>
<script>
  const LS = k => { try { return JSON.parse(localStorage.getItem('wr:'+k)); } catch(e){ return null; } };
  const SV = (k,v) => { try { localStorage.setItem('wr:'+k, JSON.stringify(v)); } catch(e){} };

  let pins   = LS('pins')   ?? ['FI','DK'];     // default: home + home-away-from-home
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
  const mlabel   = document.getElementById('mlabel');
  const searchEl = document.getElementById('search');
  const articles = [...document.querySelectorAll('article')];
  const rows     = [...tree.querySelectorAll('.row')];
  const groups   = [...tree.querySelectorAll('.grp[data-region]')];   // continents only
  const setgrp   = document.getElementById('setgrp');

  // ---- multi-select picker ----
  function applyFilter() {
    rows.forEach(r => r.classList.toggle('sel', sel.includes(r.dataset.cc)));
    groups.forEach(g => {                              // per-continent selected count
      const n = [...g.querySelectorAll('.row')].filter(r => r.classList.contains('sel')).length;
      g.querySelector('.gsel').textContent = n ? n + ' selected' : '';
    });
    articles.forEach(a =>
      a.classList.toggle('hideF', sel.length > 0 && !sel.includes(a.dataset.code)));
    const nameOf = cc => rows.find(r => r.dataset.cc === cc).dataset.label;
    mlabel.textContent =
        sel.length === 0 ? 'All'
      : sel.length === 1 ? nameOf(sel[0])
      : sel.length <= 3  ? sel.map(nameOf).join(', ')
      : sel.length + ' countries';
    SV('sel', sel);
  }
  function applyPins() {
    rows.forEach(r => r.classList.toggle('pinned', pins.includes(r.dataset.cc)));
    document.getElementById('selpins').classList.toggle('hide', pins.length === 0);
  }
  tree.addEventListener('click', e => {
    const r = e.target.closest('.row'); if (!r) return;
    const cc = r.dataset.cc;
    if (e.target.closest('.pin')) {                 // star toggles PIN, not selection
      pins = pins.includes(cc) ? pins.filter(x => x !== cc) : [...pins, cc];
      SV('pins', pins); applyPins();
      return;
    }
    sel = sel.includes(cc) ? sel.filter(x => x !== cc) : [...sel, cc];
    applyFilter();                                  // picker stays open for more picks
  });
  document.getElementById('selall').onclick =
    () => { sel = []; applyFilter(); tree.classList.add('hide'); };
  document.getElementById('selpins').onclick =
    () => { sel = [...pins]; applyFilter(); tree.classList.add('hide'); };
  searchEl.addEventListener('input', () => {
    const q = searchEl.value.trim().toLowerCase();
    rows.forEach(r => r.classList.toggle('hide',
      !!q && !r.dataset.label.toLowerCase().includes(q)
          && !r.dataset.cc.toLowerCase().includes(q)));
    groups.forEach(g => {
      const hasMatch = [...g.querySelectorAll('.row')].some(r => !r.classList.contains('hide'));
      g.classList.toggle('hide', !!q && !hasMatch);
      if (q) g.open = hasMatch;                        // searching expands matches
    });
    setgrp.classList.toggle('hide', !!q);              // hide settings while searching
  });
  // open the picker: collapse all continents, expand only those with a pick
  function resetPicker() {
    searchEl.value = '';
    rows.forEach(r => r.classList.remove('hide'));
    groups.forEach(g => {
      g.classList.remove('hide');
      g.open = [...g.querySelectorAll('.row')].some(r => r.classList.contains('sel'));
    });
    setgrp.classList.remove('hide'); setgrp.open = false;
  }
  document.getElementById('menu').onclick = e => {
    e.stopPropagation();
    tree.classList.toggle('hide');
    if (!tree.classList.contains('hide')) { resetPicker(); searchEl.focus(); }
  };
  document.addEventListener('click', e => {            // click outside closes
    if (!e.target.closest('header')) tree.classList.add('hide');
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

  // ---- read-dim + new-dots ----
  document.getElementById('feed').addEventListener('click', e => {
    const l = e.target.closest('a.t'); if (!l) return;
    read.add(l.href); SV('read', [...read].slice(-500));
    l.closest('article').classList.add('read');
  });
  articles.forEach(a => {
    if (read.has(a.querySelector('a.t').href)) a.classList.add('read');
    const ts = +a.dataset.ts || 0;
    if (prevVisit && ts > prevVisit)
      a.querySelector('time').insertAdjacentHTML('beforebegin', '<span class="nd"></span>');
  });

  // ---- times in the visitor's own timezone (browser locale + tz) ----
  const fmtT = new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' });
  const fmtD = new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short' });
  const today = new Date().toDateString();
  articles.forEach(a => {
    const ts = +a.dataset.ts, t = a.querySelector('time');
    if (!ts) { t.textContent = ''; return; }
    const d = new Date(ts * 1000);
    t.textContent = d.toDateString() === today
      ? fmtT.format(d) : fmtD.format(d) + ' ' + fmtT.format(d);
    t.title = d.toLocaleString();
  });
  const upd = document.getElementById('upd');
  upd.textContent = 'updated ' + fmtT.format(new Date(+upd.dataset.ts * 1000));

  applyPins(); applyFilter(); applyMute();
</script>
</body></html>"""


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
            f'<details class="grp" data-region="{region}"><summary>{region}'
            f'<span class="gn">{len(ccs)}</span><span class="gsel"></span></summary>'
            f'<div class="rows">'
        )
        for cc in ccs:
            label = cmap[cc]["name"]
            parts.append(
                f'<div class="row" data-cc="{cc}" data-label="{label}">'
                f'<span class="nm">{label}</span>'
                f'<button class="pin" title="Pin" aria-label="Pin">&#9733;</button>'
                f'<span class="ck">&#10003;</span></div>'
            )
        parts.append('</div></details>')
    return "".join(parts)


def render(items, health):
    rows = []
    for it in items:
        rows.append(
            f'<article data-code="{it["code"]}" data-region="{it["region"]}" data-ts="{it["ts"] or 0}">'
            f'<div class="m">'
            f'<span>{html.escape(it["country"])}</span><span class="dot">·</span>'
            f'<span>{html.escape(it["source"])}</span>'
            f'<time></time></div>'
            f'<a class="t" href="{html.escape(it["link"])}" target="_blank" rel="noopener">'
            f'{html.escape(it["title"])}</a>'
            + (f'<p class="d">{html.escape(it["summary"])}</p>' if it.get("summary") else "")
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
                .replace("__BUILT__", str(int(time.time()))))


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
