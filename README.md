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

Maintenance tooling: `probe_world.py` vets candidate feeds (liveness + domestic
gaze), `check_links.py` verifies articles resolve and aren't paywalled,
`verify.js` (Playwright) tests the personalization layer.

## Editing the roster

Add a country/source in `feeds.py`. House rules learned the hard way:

- Use the outlet's **national desk** feed, never "world" / "top stories".
- International broadcasters' main feeds (BBC World, France24, DW-all,
  Al Jazeera) are outward-gazing — excluded by design.
- Beware wire mirrors (a domestic *domain* republishing AP is not domestic news).
- Feed URLs rot; run `probe_world.py` / `--health` after edits.
- Some feeds publish future timestamps (local time as UTC) — build.py clamps.

## Content & politeness

Headlines, short feed-provided standfirsts, and links only — every item links
out to the original publisher. Feeds are fetched twice per hour with an
identifying User-Agent. Publishers who want a source removed: open an issue.
