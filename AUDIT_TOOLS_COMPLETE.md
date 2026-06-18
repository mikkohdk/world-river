# World River — Complete Audit Toolkit

Your news aggregator now has industrial-strength tools to validate sources, detect paywalls, monitor feed health, and discover new free outlets.

---

## 📦 What's New

**3 audit tools + 1 batch runner + 5 docs:**

| File | Purpose |
|------|---------|
| `audit_links.py` | Visit article links, detect paywalls |
| `find_sources.py` | Research & validate new sources |
| `watch_feeds.py` | Monitor feed health & response times |
| `run_audit.bat` (Windows) | Run all 3 tools with one click |
| `run_audit.sh` (Linux/Mac) | Same for Unix shells |
| `AUDIT_README.md` | Full reference & workflows |
| `AUDIT_SUITE_SUMMARY.md` | Quick overview & examples |
| `SOURCES_MAINTENANCE.md` | How to edit feeds.py + troubleshoot |

---

## 🚀 30-Second Start

### Install
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
```

**Output:** Three JSON files with detailed results.

---

## 🎯 What Each Tool Does

### `audit_links.py` — Paywall Detective

Visits the article links in your generated `index.html` and checks for subscription/login walls.

```bash
# Quick audit (2 links/source, ~5 min)
python audit_links.py --quick

# Full audit (all links, 30–60 min)
python audit_links.py

# Find free alternatives by country
python audit_links.py --find-free

# Audit feed URLs only (faster)
python audit_links.py --sources
```

**Output:** `audit_results.json`, `suggested_sources.json`

**Why:** Ensure your river only shows free-to-read news.

---

### `find_sources.py` — Source Discoverer

Browse and validate candidate news feeds to expand coverage or replace paywalled outlets.

```bash
# See candidates by country/type
python find_sources.py --list

# Check if URLs are live feeds
python find_sources.py --validate

# Generate Python code to add to feeds.py
python find_sources.py --export
```

**Output:** `candidate_sources.json`

**Why:** Find alternatives when sources go behind paywalls.

---

### `watch_feeds.py` — Feed Monitor

Check RSS feed availability, response times, and item counts. Run once or continuously.

```bash
# One-time health check
python watch_feeds.py

# Continuous monitoring (every hour)
python watch_feeds.py --watch 3600

# Faster timeout for fast networks
python watch_feeds.py --timeout 3
```

**Output:** `feed_health.json`

**Why:** Catch dead feeds early, monitor performance.

---

## 📋 Common Workflows

### "Weekly: Is everything working?"
```bash
python watch_feeds.py              # 1 min
python audit_links.py --quick      # 5 min
```
→ Total: ~6 minutes. Identifies obvious problems.

### "Monthly: Full health audit"
```bash
python audit_links.py              # 30–60 min
python audit_links.py --find-free  # 10 sec
```
→ Find all paywalled sources and free replacements.

### "Add/replace a source"
```bash
python find_sources.py --list      # Browse
python find_sources.py --validate  # Check URLs
python find_sources.py --export    # Copy into feeds.py
python build.py                    # Rebuild
python watch_feeds.py              # Verify
```

### "Source went behind paywall"
```bash
python audit_links.py --quick
# → See paywalled source in results
python audit_links.py --find-free
# → Get free alternatives
# → Edit feeds.py, comment out paywalled source
python build.py
python watch_feeds.py
```

---

## 📊 Understanding Results

### feed_health.json
Which feeds are alive, response times, item counts.

```json
{
  "feeds": {
    "GB BBC UK": {"status": "OK", "response_time": 2.1},
    "KE The Standard": {"status": "HTTP 403"}  // DEAD
  }
}
```

### audit_results.json
Which sources have paywalled articles.

```json
{
  "sources": {
    "BBC UK": {"status": "✓ FREE"},
    "FT": {"status": "❌ PAYWALLED"}
  }
}
```

### suggested_sources.json
Free alternatives for each country.

```json
{
  "GB": {"alternatives": [
    {"name": "Independent", "url": "..."}
  ]}
}
```

---

## ✨ Key Features

| Feature | Tool | Use Case |
|---------|------|----------|
| Feed availability | `watch_feeds.py` | Catch dead feeds |
| Response time tracking | `watch_feeds.py` | Monitor performance |
| Paywall detection | `audit_links.py` | Ensure free-to-read |
| Alternative suggestions | `audit_links.py --find-free` | Replace paywalled outlets |
| Source validation | `find_sources.py --validate` | Vet new candidates |
| Code generation | `find_sources.py --export` | Auto-generate feeds.py edits |

---

## 🔍 How Paywalls Are Detected

✅ **Works well:**
- Standard paywall selectors (`.paywall`, `.subscription`)
- Login/signup prompts in page text
- HTTP redirects to login pages
- Dead feeds (404, 403, timeouts)

⚠️ **Limitations:**
- JavaScript-based paywalls (harder to detect)
- Soft paywalls ("read 3/month") are tricky
- Heuristic-based, not 100% accurate
- Some sites have dynamic paywalls

**Bottom line:** Good for finding obvious paywalls. Manual spot-checks recommended.

---

## 🛠️ Installation & Requirements

```bash
pip install requests feedparser playwright
playwright install chromium
```

**Approximate runtimes:**
- `watch_feeds.py` — ~1 min (47 feeds)
- `audit_links.py --quick` — ~5 min (94 samples)
- `audit_links.py` (full) — 30–60 min (all articles)
- `find_sources.py --validate` — ~2 min (50 candidates)

**Disk space:** ~100MB for Chromium; ~10MB for results JSON files.

---

## 🎓 Examples

### Example 1: Clean Out Paywalled Sources
```bash
# Identify paywalls
python audit_links.py --quick
# Results show: BBC=free, FT=paywalled, Reuters=free

# Get alternatives
python audit_links.py --find-free
# Suggests: Financial Times → free alternatives list

# Manual step: Edit feeds.py
# Comment out FT, add alternative

# Verify
python build.py && python watch_feeds.py
```

### Example 2: Replace Dead Feed
```bash
# Check feed health
python watch_feeds.py
# Shows: KE/The Standard = HTTP 403

# Edit feeds.py
# Comment: # ("The Standard", "..."),  # DISABLED: login wall

# Rebuild
python build.py

# Verify
python watch_feeds.py
```

### Example 3: Add New Country
```bash
# Browse candidates
python find_sources.py --list | grep "ZA"

# Validate URLs
python find_sources.py --validate

# Get Python code
python find_sources.py --export
# Copy into feeds.py under new ZA section

# Test
python build.py && python watch_feeds.py
```

---

## 📖 Documentation Map

- **[AUDIT_README.md](AUDIT_README.md)** — Comprehensive reference
  - Detailed options per tool
  - Troubleshooting guide
  - Performance tips

- **[AUDIT_SUITE_SUMMARY.md](AUDIT_SUITE_SUMMARY.md)** — Quick overview
  - 30-second intro
  - Common workflows
  - FAQ

- **[SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)** — How to edit sources
  - Adding/removing sources
  - Disabling broken feeds
  - Maintenance checklist

- **[AUDIT_TOOLS.md](AUDIT_TOOLS.md)** — Quick reference per tool
  - Usage examples
  - Options summary

---

## 💡 Best Practices

1. **Run feeds check first** — Fast, identifies obvious problems
2. **Use `--quick` for routine checks** — Full audit is slow
3. **Check suggestions after finding paywalls** — Instant alternatives
4. **Monitor continuously** — Set `--watch` for unattended monitoring
5. **Keep disabled sources commented** — Preserves history

---

## 🔧 Customization

```bash
# Slow network? Increase timeout
python audit_links.py --timeout 20

# Fast network? Decrease threshold
python watch_feeds.py --threshold 2

# Want to audit only 5 links per source?
# Edit audit_links.py: sample_size = 5
```

---

## ⚙️ Integration Points

### With build.py
```bash
python build.py                     # Generate index.html
python watch_feeds.py               # Verify feeds live
python audit_links.py --quick       # Quick paywall check
```

### With GitHub Actions (CI/CD)
Add to your cron workflow:
```bash
python watch_feeds.py --timeout 3   # Fast online check
python build.py
```

### With cron (Linux) / Task Scheduler (Windows)
```bash
# Weekly health check
0 9 * * 1 cd /path/to/worldfeed && python watch_feeds.py
```

---

## 🚀 Next Steps

1. **Install dependencies** (5 minutes)
   ```bash
   pip install playwright requests feedparser
   playwright install chromium
   ```

2. **Run initial audit** (5–60 minutes depending on scope)
   ```bash
   python watch_feeds.py              # Quick
   python audit_links.py --quick      # Sample paywall check
   ```

3. **Review results** (10 minutes)
   - Check JSON files
   - Identify dead feeds / paywalls
   - Note alternatives

4. **Edit feeds.py** (10–30 minutes)
   - Disable broken sources
   - Add free alternatives
   - Comment with reasons

5. **Rebuild & verify** (5 minutes)
   ```bash
   python build.py
   python watch_feeds.py
   python audit_links.py --quick
   ```

6. **Commit changes** (2 minutes)
   ```bash
   git add feeds.py index.html
   git commit -m "Remove paywalled sources, add free alternatives"
   ```

---

## 📞 Quick Help

**Playwright not found?**
```bash
pip install playwright
playwright install chromium
```

**Feed validation slow?**
```bash
python find_sources.py --validate  # Uses 5s timeout
# Increase timeout in code if needed
```

**Paywall detection missing a source?**
```bash
# Run full audit, not quick sample
python audit_links.py              # Tests all links
```

**Want to see exact paywalled links?**
Check `audit_results.json` → `sources` → `details` array.

---

Enjoy a cleaner, paywall-free World River! 🌍
