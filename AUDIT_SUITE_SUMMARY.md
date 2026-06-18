# World River Audit Suite — Summary

You now have a complete toolkit to validate your news river for paywall-blocked sources, identify dead feeds, and discover new free alternatives.

## 📦 What You Got

### 3 Main Tools

1. **`audit_links.py`** — Visit article links, detect paywalls
   - `--quick` for fast sampling (2 links/source, ~5 min)
   - Full audit for comprehensive check (30–60 min)
   - `--find-free` to suggest alternatives
   
2. **`find_sources.py`** — Research and validate new sources
   - `--list` browse candidates by country
   - `--validate` check if URLs are live feeds
   - `--export` generate Python code for feeds.py

3. **`watch_feeds.py`** — Monitor feed health
   - One-off check or continuous `--watch`
   - Detects dead feeds, slow feeds, missing items

### 2 Run Scripts

- **`run_audit.bat`** (Windows) — Master script running all 3 tools
- **`run_audit.sh`** (Linux/Mac) — Same for Unix shells

### Documentation

- **`AUDIT_README.md`** — Full guide (workflow, options, troubleshooting)
- **`AUDIT_TOOLS.md`** — Quick reference per tool
- This file — overview

---

## 🚀 Quick Start (5 minutes)

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

Or manually (one by one):
```bash
python watch_feeds.py                    # ~1 min
python audit_links.py --quick            # ~5 min
python audit_links.py --find-free        # ~10 sec
```

### Check Results
Three JSON files appear:
- `feed_health.json` — Which feeds are live, response times
- `audit_results.json` — Which sources have paywalls
- `suggested_sources.json` — Free alternatives by country

---

## 📋 Use Cases

### **Weekly: "Is everything still working?"**
```bash
python watch_feeds.py              # Feeds alive?
python audit_links.py --quick      # Any obvious paywalls?
```
⏱️ ~5 minutes

### **Monthly: "Full health check"**
```bash
python audit_links.py              # Full paywall audit
python audit_links.py --find-free  # Get alternatives
```
⏱️ 30–60 minutes (depending on link count)

### **When adding new sources:**
```bash
python find_sources.py --list      # Browse candidates
python find_sources.py --validate  # Validate URLs
python find_sources.py --export    # Copy into feeds.py
python build.py                    # Rebuild
python audit_links.py --quick      # Verify
```

---

## 🎯 Key Features

| Feature | Tool | Command |
|---------|------|---------|
| Check if feeds are live | `watch_feeds.py` | `python watch_feeds.py` |
| Monitor continuously | `watch_feeds.py` | `python watch_feeds.py --watch 3600` |
| Quick paywall check | `audit_links.py` | `python audit_links.py --quick` |
| Full paywall audit | `audit_links.py` | `python audit_links.py` |
| Find alternatives | `audit_links.py` | `python audit_links.py --find-free` |
| Browse new sources | `find_sources.py` | `python find_sources.py --list` |
| Validate candidates | `find_sources.py` | `python find_sources.py --validate` |
| Generate code | `find_sources.py` | `python find_sources.py --export` |

---

## 🔍 What Gets Detected

### ✅ What Works Well
- RSS feed availability (HTTP + format validation)
- Common paywall selectors (`.paywall`, `.subscription`)
- Paywall keywords in page text
- Dead feeds / timeouts
- Slow feeds (response time tracking)

### ⚠️ Limitations
- JavaScript-based paywalls may not be detected
- Soft walls (e.g., "read 3 articles/month") harder to catch
- Some fast-changing sites' paywalls evolve
- Detection is heuristic, not 100% reliable

**Bottom line:** Good for spot-checking, but manual review of flagged sources recommended.

---

## 📊 Output Files

All tools save JSON results for review:

```
feed_health.json
├── feeds with status (OK/SLOW/DEAD)
├── response times
└── item counts

audit_results.json
├── sources (FREE/MIXED/PAYWALLED)
├── paywall counts per source
└── sample link details

suggested_sources.json
└── free alternatives by country
    ├── outlet type
    ├── URL
    └── notes

candidate_sources.json (if --validate used)
└── validated URLs + validation status
```

---

## 🔧 Customization

### Adjust Timeouts
```bash
python audit_links.py --timeout 20    # Slow network? Increase timeout
python watch_feeds.py --timeout 3     # Fast network? Decrease
```

### Adjust Warning Threshold
```bash
python watch_feeds.py --threshold 5   # Mark ⚠ if response > 5s
```

### Sample More/Fewer Links
```bash
python audit_links.py --quick         # 2 links/source
python audit_links.py                 # All links (slow)
```

---

## 🛠️ Common Workflows

### Scenario 1: "I want to clean out all paywalled sources"
```bash
python audit_links.py --quick              # Identify paywalled sources
python audit_links.py --find-free          # Get free alternatives
# Manually review and edit feeds.py
python build.py                            # Rebuild
python watch_feeds.py                      # Verify new feeds live
```

### Scenario 2: "My feed stopped updating"
```bash
python watch_feeds.py                      # Check all feeds
# Look for status: "HTTP 404", "EMPTY", "TIMEOUT"
# Edit feeds.py: remove dead ones or fix URLs
python build.py
```

### Scenario 3: "Add coverage for Country X"
```bash
python find_sources.py --list              # See candidates for X
python find_sources.py --validate          # Check which work
python find_sources.py --export            # Get Python code
# Copy code into feeds.py, edit COUNTRIES dict
python build.py
python watch_feeds.py                      # Verify
```

---

## 📦 Requirements

```bash
pip install requests feedparser playwright
playwright install chromium
```

**Approximate runtime:**
- `watch_feeds.py` — ~1 minute (47 feeds × 1.2s avg)
- `audit_links.py --quick` — ~5 minutes (94 samples × 3s avg)
- `audit_links.py` (full) — 30–60 minutes (depends on article count)
- `find_sources.py --validate` — ~2 minutes (50 candidates × 2.4s avg)

---

## 💡 Tips

1. **Run feeds check first** (`watch_feeds.py`) — fast, identifies obvious problems
2. **Use `--quick` for routine checks** — full audit is slow, use for monthly deep dives
3. **Check suggested sources** after finding paywalls — instant alternatives list
4. **Continuous monitoring** — set `--watch` for unattended monitoring
5. **Integrate with cron/Task Scheduler** for automated weekly checks

---

## 🤔 FAQ

**Q: How long does a full audit take?**
A: 30–60 minutes depending on network speed and article count. Use `--quick` for 5-minute sampling.

**Q: Will this detect all paywalls?**
A: No — heuristic-based detection catches most common ones, but JavaScript paywalls and soft walls are tricky. Good for finding obvious cases.

**Q: Can I schedule this to run automatically?**
A: Yes! `watch_feeds.py --watch 3600` runs forever; cron/Task Scheduler can invoke it.

**Q: What if a feed times out?**
A: Increase `--timeout`. Some feeds are genuinely slow. If consistently timing out, may be dead (check manually).

**Q: How do I add a new source?**
A: Edit `feeds.py`, add to the country's `sources` list, run `build.py`, then verify with `watch_feeds.py`.

---

## 📞 Troubleshooting

**Playwright not found**
```bash
pip install playwright
playwright install chromium
```

**Requests not found**
```bash
pip install requests
```

**Timeouts on slow network**
```bash
python audit_links.py --quick --timeout 20
```

**Want to see which specific links are paywalled?**
Check `audit_results.json` → `sources` → `details` array.

---

## 📝 Next Steps

1. **Run the audit suite** once to understand your current state
2. **Review `feed_health.json`** for dead/slow feeds
3. **Review `audit_results.json`** for paywalled sources
4. **Use `suggested_sources.json`** to replace paywalled outlets
5. **Edit `feeds.py`** with improvements
6. **Run `build.py`** to regenerate
7. **Verify with `watch_feeds.py`** and `audit_links.py --quick`

---

Enjoy a cleaner, paywall-free World River! 🌍
