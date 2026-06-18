# World River Audit Tools

Two tools to validate your news feed health and identify paywall-blocked sources.

## Setup

```bash
pip install playwright requests
playwright install chromium
```

## audit_links.py

Checks article links in `index.html` for paywall/subscription walls.

### Quick Audit (2 links per source)
```bash
python audit_links.py --quick
```
Samples 2 links per source, 10-second timeout each. Fast way to get a ballpark assessment.

### Full Audit (all links)
```bash
python audit_links.py
```
Tests every article in the river. Will take several minutes. Results saved to `audit_results.json`.

### Audit Feed URLs Only
```bash
python audit_links.py --sources
```
Tests only the RSS feed URLs from `feeds.py` (faster, doesn't visit article pages). Results saved to `feed_audit_results.json`.

### Find Free Alternatives
```bash
python audit_links.py --find-free
```
Suggests known free news sources for each country. Results saved to `suggested_sources.json`.

### Options
- `--timeout N` — Seconds to wait per link (default: 10)
- `--quick` — Sample only 2 links per source

### Output
- `audit_results.json` — Full audit results (link-by-link details)
- `feed_audit_results.json` — Feed URL accessibility
- `suggested_sources.json` — Free alternatives by country

---

## find_sources.py

Research and validate new free news sources to add to World River.

### List Candidates
```bash
python find_sources.py --list
```
Shows all candidate sources under consideration, organized by country and type.

### Validate All Candidates
```bash
python find_sources.py --validate
```
Tests each candidate URL. Marks valid (✓), invalid (❌), or unknown (⚠) based on HTTP response and feed format.

Results saved to `candidate_sources.json`.

### Generate feeds.py Additions
```bash
python find_sources.py --export
```
Prints Python code ready to paste into `feeds.py` for any validated candidates. Only shows sources that passed `--validate`.

---

## Quick Workflow

1. **Spot-check for paywalls:**
   ```bash
   python audit_links.py --quick
   ```
   Look at summary for sources marked ❌ PAYWALLED or ⚠ MIXED.

2. **Find free alternatives:**
   ```bash
   python audit_links.py --find-free
   ```
   See suggestions for each country (includes existing sources as reference).

3. **Research new sources:**
   ```bash
   python find_sources.py --list
   python find_sources.py --validate
   ```
   Check candidates, validate promising ones.

4. **Add to River:**
   ```bash
   python find_sources.py --export
   ```
   Copy the Python output into `feeds.py`, then run `python build.py` to regenerate.

---

## Notes

- **Paywall detection** uses heuristics: selectors like `.paywall`, keywords like "subscription", and page content patterns. It's not 100% reliable but catches most cases.
- **Feed validation** is simpler: just checks HTTP 200 and valid RSS/Atom format.
- **Timeline:** Quick audit of 250 articles ≈ 5–10 minutes (depending on site speeds). Full audit of 1000+ articles ≈ 30–60 minutes.
- **Headless browser:** Uses Playwright/Chromium to visit pages like a real browser (avoids bot blocks).
