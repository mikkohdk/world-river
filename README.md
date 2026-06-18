# World River

Each country's news from its **own domestic source** — Australia from Australian
outlets, Japan from Japanese, Russia from Russian. No world desks, no wire
mirrors: the rule is *a source reports on its own country*.

One calm, chronological river across 42 countries / 47 English-language
sources, round-robin interleaved so no feed dominates.

## How it works

`build.py` fetches the roster in `feeds.py` (RSS, no API keys) and renders a
single static `index.html`. A GitHub Actions cron rebuilds and deploys to
GitHub Pages every 30 minutes.

Personalization is entirely client-side (localStorage): pinned countries,
sticky filter, read-dimming, new-since-last-visit dots, muted words (⚙ panel).
No accounts, no cookies, no tracking.

## Local use

```
pip install -r requirements.txt
python build.py            # writes index.html
python build.py --health   # report which feeds are live
```

Maintenance tooling: 

- **`audit_links.py`** — Audit all article links for paywalls; find free alternatives
- **`find_sources.py`** — Research and validate new free news sources
- **`watch_feeds.py`** — Monitor feed health and response times
- `probe_world.py`, `check_links.py` — Legacy vetting tools
- `verify.js` (Playwright) — Test the personalization layer

See **[AUDIT_README.md](AUDIT_README.md)** for detailed usage.

## Editing the roster

Add, remove, or flag sources in `feeds.py`. See **[SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)** for workflows.

House rules learned the hard way:

- Use the outlet's **national desk** feed, never "world" / "top stories".
- International broadcasters' main feeds (BBC World, France24, DW-all,
  Al Jazeera) are outward-gazing — excluded by design.
- Beware wire mirrors (a domestic *domain* republishing AP is not domestic news).
- When a source goes behind paywall, comment it out with reason (don't delete).
- Feed URLs rot; run `python watch_feeds.py` after edits to verify.
- Some feeds publish future timestamps (local time as UTC) — build.py clamps.

## Content & politeness

Headlines, short feed-provided standfirsts, and links only — every item links
out to the original publisher. Feeds are fetched twice per hour with an
identifying User-Agent. Publishers who want a source removed: open an issue.
