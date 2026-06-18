# World River Audit Suite — Navigation Index

**Start here.** Quick links to every tool, doc, and workflow.

---

## 🚀 Quick Start (5 minutes)

### Installation
```bash
pip install requests feedparser playwright
playwright install chromium
```

### Run Everything
```bash
# Windows
run_audit.bat

# Linux/Mac
bash run_audit.sh
```

---

## 📚 Documentation Map

### 🔰 Start Here (New Users)
1. **[AUDIT_SUITE_MANIFEST.md](AUDIT_SUITE_MANIFEST.md)** ← Complete overview
2. **[AUDIT_SUITE_SUMMARY.md](AUDIT_SUITE_SUMMARY.md)** ← 5-min intro with examples

### 📖 Reference Docs
- **[AUDIT_README.md](AUDIT_README.md)** — Full reference (workflows, options, troubleshooting)
- **[AUDIT_TOOLS.md](AUDIT_TOOLS.md)** — Per-tool quick reference
- **[SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)** — How to edit feeds.py

### 🎯 This File
- **[AUDIT_INDEX.md](AUDIT_INDEX.md)** — Navigation (you are here)

---

## 🛠️ Tools by Task

### "Check if everything is working"
→ **`python watch_feeds.py`** (1 min)  
→ [AUDIT_TOOLS.md](AUDIT_TOOLS.md#watch_feedspy)

### "Are there paywall sources in my river?"
→ **`python audit_links.py --quick`** (5 min)  
→ [AUDIT_TOOLS.md](AUDIT_TOOLS.md#audit_linkspy)

### "What free sources can I use instead?"
→ **`python audit_links.py --find-free`** (10 sec)  
→ [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md#scenario-1-source-goes-behind-paywall)

### "I want to add a new country"
→ **`python find_sources.py --list`**  
→ **`python find_sources.py --validate`**  
→ **`python find_sources.py --export`**  
→ [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md#scenario-3-add-new-country)

### "A source broke (404, timeout, etc.)"
→ **`python watch_feeds.py`** (identify dead feed)  
→ [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md#scenario-2-feed-url-changes)

### "Full audit of everything"
→ **`python audit_links.py`** (30–60 min, all links)  
→ [AUDIT_README.md](AUDIT_README.md#auditlinkspy--paywall--link-auditor)

---

## 📋 Tools Overview

| Tool | Purpose | Time | Output |
|------|---------|------|--------|
| [`watch_feeds.py`](watch_feeds.py) | Feed health & response times | 1 min | `feed_health.json` |
| [`audit_links.py`](audit_links.py) | Detect paywalls in articles | 5–60 min | `audit_results.json` |
| [`find_sources.py`](find_sources.py) | Discover/validate sources | 2–10 min | `candidate_sources.json` |

---

## 🎯 Common Workflows

### Weekly: "Is my river healthy?"
```bash
python watch_feeds.py                # Feeds alive?
python audit_links.py --quick        # Any obvious paywalls?
```
**Time:** ~6 minutes

**Next:** If issues found, see [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)

---

### Monthly: "Deep audit"
```bash
python audit_links.py                # Full paywall check
python audit_links.py --find-free    # Get alternatives
```
**Time:** 30–60 minutes

**Next:** Edit feeds.py, rebuild, verify

See: [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md#maintenance-workflows)

---

### When Adding Sources
```bash
python find_sources.py --list        # See candidates
python find_sources.py --validate    # Check URLs
python find_sources.py --export      # Get code
# Edit feeds.py
python build.py
python watch_feeds.py
```

See: [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md#scenario-3-add-new-country)

---

## 🔧 Command Reference

### Quick Commands
```bash
# Feed health
python watch_feeds.py

# Quick paywall check
python audit_links.py --quick

# Find free alternatives
python audit_links.py --find-free

# Browse source candidates
python find_sources.py --list

# Validate candidate URLs
python find_sources.py --validate

# Generate feeds.py code
python find_sources.py --export
```

### Advanced Options
```bash
# Slow network (increase timeout)
python audit_links.py --timeout 20

# Fast network (decrease threshold)
python watch_feeds.py --threshold 2

# Continuous monitoring (every hour)
python watch_feeds.py --watch 3600

# Feed URL audit only (faster)
python audit_links.py --sources
```

See: [AUDIT_README.md](AUDIT_README.md) for full options

---

## 💾 Output Files

After running audits, you'll get JSON files:

- **`feed_health.json`** — Feed status, response times (from `watch_feeds.py`)
- **`audit_results.json`** — Paywall verdicts per source (from `audit_links.py`)
- **`suggested_sources.json`** — Free alternatives by country (from `audit_links.py`)
- **`candidate_sources.json`** — Validation results (from `find_sources.py --validate`)

Open these files to see detailed results.

---

## 🆘 Troubleshooting

### "Module not found" → Install dependencies
```bash
pip install requests feedparser playwright
playwright install chromium
```

### "Timeout on slow sites" → Increase timeout
```bash
python audit_links.py --timeout 20
```

### "How do I edit feeds.py?" → Read SOURCES_MAINTENANCE.md
→ [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)

### "Paywall not detected" → Try full audit (not --quick)
```bash
python audit_links.py  # Test all links, not sample
```

See: [AUDIT_README.md](AUDIT_README.md#troubleshooting) for more

---

## 📊 What Gets Checked

### Feed Health (`watch_feeds.py`)
✅ HTTP response (200 = good)  
✅ RSS/Atom format (valid XML)  
✅ Item count (has articles)  
✅ Response time (performance)  

### Paywall Detection (`audit_links.py`)
✅ Paywall CSS selectors (`.paywall`, `.subscription`)  
✅ Login/signup keywords  
✅ "Sign in to read" patterns  
✅ Subscription prompts  

⚠️ **Limitations:**
- JavaScript-based paywalls (harder)
- Soft walls ("read 3/month") (tricky)
- Heuristic-based (not 100% accurate)

### Source Validation (`find_sources.py`)
✅ Feed URL accessibility  
✅ RSS/Atom format  
✅ Item count  

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Feed health check | ~1 min | 47 feeds × 1.2s |
| Quick paywall audit | ~5 min | 94 samples × 3s |
| Full paywall audit | 30–60 min | Depends on article count |
| Source validation | ~2 min | 50 candidates × 2.4s |

**Faster:** Local network, fewer sources, use `--quick`  
**Slower:** Slow internet, many articles, slow sites

---

## 📦 What You Have

```
Tools:
  audit_links.py      - Paywall detection
  find_sources.py     - Source discovery
  watch_feeds.py      - Feed monitoring

Runners:
  run_audit.bat       - Windows batch
  run_audit.sh        - Linux/Mac shell

Documentation:
  AUDIT_SUITE_MANIFEST.md     - Complete overview
  AUDIT_SUITE_SUMMARY.md      - 5-min intro
  AUDIT_README.md             - Full reference
  AUDIT_TOOLS.md              - Per-tool reference
  SOURCES_MAINTENANCE.md      - How to edit sources
  AUDIT_INDEX.md              - This file
```

---

## ✨ Key Features

- **One-click audit** → `run_audit.bat` / `bash run_audit.sh`
- **Feed monitoring** → Catch dead feeds early
- **Paywall detection** → Heuristic-based, catches most
- **Free alternatives** → Auto-suggested when paywalls found
- **Source validation** → Before adding to feeds.py
- **Continuous mode** → Can run unattended with `--watch`

---

## 🎓 Learning Path

1. **5 min:** Read [AUDIT_SUITE_SUMMARY.md](AUDIT_SUITE_SUMMARY.md)
2. **5 min:** Run `python watch_feeds.py`
3. **5 min:** Run `python audit_links.py --quick`
4. **15 min:** Read [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)
5. **30 min:** Edit feeds.py based on findings
6. **5 min:** Verify with `python build.py && python watch_feeds.py`

---

## 📝 Recent Changes

**2026-06-14:**
- Created complete audit toolkit
- Kenya example: Disabled "The Standard" (login wall)
- All documentation complete and linked

---

## 🚀 Next Steps

1. **Install:** `pip install playwright requests feedparser`
2. **Run:** `python watch_feeds.py` (1 min)
3. **Review:** Check `feed_health.json`
4. **Learn:** Read [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)
5. **Edit:** Update feeds.py as needed

---

**Questions?**
- General → [AUDIT_README.md](AUDIT_README.md)
- Editing → [SOURCES_MAINTENANCE.md](SOURCES_MAINTENANCE.md)
- Quick ref → [AUDIT_TOOLS.md](AUDIT_TOOLS.md)

**Enjoy! 🌍**
