# World River Audit Suite

A comprehensive toolkit to audit your news feeds for paywall blocks, dead links, and to discover new free sources.

## Quick Start

### Installation
```bash
pip install playwright requests feedparser
playwright install chromium
```

### Run All Checks
```bash
# Windows
run_audit.bat

# Linux/Mac
bash run_audit.sh

# Or manually:
python watch_feeds.py
python audit_links.py --quick
python audit_links.py --find-free
```

---

## Tools Overview

### 1. **watch_feeds.py** — Feed Health Monitor
Checks RSS feed URLs from `feeds.py` for availability and response time.

**One-off check:**
```bash
python watch_feeds.py
```

**Continuous monitoring (every hour):**
```bash
python watch_feeds.py --watch 3600
```

**Options:**
- `--timeout N` — HTTP timeout per feed (default: 5s)
- `--threshold N` — Mark ⚠ if response > N seconds (default: 3s)

**Output:** `feed_health.json`

**Use case:** Detect dead feeds, slow feeds, or feeds that stopped publishing.

---

### 2. **audit_links.py** — Paywall & Link Auditor
Visits article links in your generated `index.html` and checks for paywalls/subscription blocks.

#### Quick Audit (Fast, Representative Sample)
```bash
python audit_links.py --quick
```
Tests 2 links per source. Gives you a sense of which sources are paywalled without running for hours.

#### Full Audit (Comprehensive, Slow)
```bash
python audit_links.py
```
Tests every article link in the river. Takes 30–60 minutes depending on article count and network speed.

#### Audit Feed URLs Only (Faster)
```bash
python audit_links.py --sources
```
Only checks the RSS feed URLs (not article pages). Faster than full article audit.

#### Find Free Alternatives
```bash
python audit_links.py --find-free
```
Suggests known free news sources for each country. Useful after identifying paywalled outlets.

**Options:**
- `--timeout N` — Seconds to wait per link (default: 10)
- `--quick` — Sample only 2 links per source (default: check all)

**Outputs:**
- `audit_results.json` — Full link audit with paywall verdicts
- `feed_audit_results.json` — Feed URL accessibility
- `suggested_sources.json` — Free alternatives by country

**Use case:** Ensure your river only includes free-to-read sources.

---

### 3. **find_sources.py** — Source Discovery & Validation
Research and validate new free news sources to expand coverage.

#### Browse Candidates
```bash
python find_sources.py --list
```
Shows curated list of candidate sources organized by country and outlet type.

#### Validate Candidates
```bash
python find_sources.py --validate
```
Checks each candidate URL: does it respond? Is it a valid RSS/Atom feed?

**Output:** `candidate_sources.json`

#### Generate Code for feeds.py
```bash
python find_sources.py --export
```
Prints ready-to-paste Python code for any validated candidates.

**Use case:** Add new countries, replace paywalled sources, expand coverage.

---

## Recommended Workflow

### Weekly: Quick Health Check
```bash
python watch_feeds.py                # ~1 minute
python audit_links.py --quick        # ~5 minutes
```
→ Identify any feeds that went silent or obvious paywalls in sampled articles.

### Monthly: Deep Audit
```bash
python audit_links.py                # 30–60 minutes
python audit_links.py --find-free    # ~10 seconds
```
→ Find all paywalled sources, get replacement suggestions.

### When Adding New Sources
```bash
python find_sources.py --list
python find_sources.py --validate
python find_sources.py --export
```
→ Edit `feeds.py`, run `python build.py`, verify with quick audit.

---

## Understanding Results

### feed_health.json
```json
{
  "timestamp": "2026-06-14T10:30:00",
  "summary": {
    "ok": 42,
    "slow": 3,
    "dead": 2
  },
  "feeds": {
    "GB BBC UK": {
      "status": "OK",
      "response_time": 2.1,
      "item_count": 12
    }
  }
}
```

**Symbols:**
- ✓ OK — Feed is live, response < threshold
- ⚠ SLOW — Feed is live but slow (response > threshold)
- ❌ DEAD — Feed returned error or timeout

### audit_results.json
```json
{
  "sources": {
    "BBC UK": {
      "free_count": 12,
      "paywall_count": 0,
      "status": "✓ FREE"
    },
    "FT": {
      "free_count": 2,
      "paywall_count": 10,
      "status": "❌ PAYWALLED"
    }
  }
}
```

**Statuses:**
- ✓ FREE — All sampled links are free-to-read
- ⚠ MIXED — Some links free, some paywalled
- ❌ PAYWALLED — All sampled links are paywalled

### suggested_sources.json
Curated list of free alternatives for each country, organized by outlet type.

---

## Detection Methods

### Paywall Detection (audit_links.py)
1. **Selector-based:** Looks for elements with classes/IDs like `.paywall`, `.subscription`
2. **Text patterns:** Searches for keywords: "subscription", "sign in", "premium", "paywall", etc.
3. **HTML structure:** Checks for subscription prompts in the main content area

**Limitations:**
- Some sites use JavaScript-based paywalls (harder to detect in headless mode)
- Some sites gate content with soft walls (e.g., article limit per month)
- Detection is heuristic-based, not 100% accurate

### Feed Validation (find_sources.py)
1. **HTTP check:** Verifies server responds with 200 OK
2. **Format check:** Confirms content is valid RSS or Atom XML
3. **Item count:** Ensures feed contains actual articles

---

## Performance Tips

### Speed Up Audits
```bash
# Reduce timeout if you have fast connection
python audit_links.py --quick --timeout 5

# Or use shorter feed check
python watch_feeds.py --timeout 3
```

### Parallel Audits
Run feeds and links audit in parallel (different terminals):
```bash
# Terminal 1
python watch_feeds.py

# Terminal 2 (meanwhile)
python audit_links.py --quick
```

### Cache Results
Results are saved to JSON files. Check `audit_results.json` before re-running.

---

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Requests not found"
```bash
pip install requests
```

### Audits timing out on slow network
```bash
python audit_links.py --quick --timeout 20
```

### Feed validation incomplete
If `validate_feed()` returns `None` for many feeds, they might be slow. Increase timeout:
```bash
python find_sources.py --validate  # (uses hardcoded 5s timeout)
```

---

## Integration with build.py

After updating `feeds.py` with new sources:

```bash
python build.py                        # Generate new index.html
python watch_feeds.py                  # Verify feeds are live
python audit_links.py --quick          # Spot-check for paywalls
```

---

## Example: Replacing a Paywalled Source

1. Run audit:
   ```bash
   python audit_links.py --quick
   ```

2. Identify paywalled sources in output and JSON.

3. Find alternatives:
   ```bash
   python audit_links.py --find-free
   ```

4. Research candidates:
   ```bash
   python find_sources.py --list
   python find_sources.py --validate
   ```

5. Edit `feeds.py` (replace or add sources).

6. Regenerate:
   ```bash
   python build.py
   ```

7. Verify:
   ```bash
   python watch_feeds.py
   python audit_links.py --quick
   ```

---

## Maintenance Checklist

- **Weekly:** `python watch_feeds.py` — Catch dead feeds early
- **Monthly:** Full `python audit_links.py` — Find creeping paywalls
- **After adding sources:** Validate with `python find_sources.py --validate`
- **Quarterly:** Review `suggested_sources.json` for coverage gaps

---

## Notes

- **Paywall detection** is heuristic; some soft-wall or JS-based gates won't be caught
- **Feed checking** is simpler and more reliable
- **Article links** are live at run time; paywall status may change
- **Headless browser** uses real Chrome/Chromium (more accurate than curl, but slower)
