# World River — Sources Maintenance Guide

How to manage the `feeds.py` roster: adding, removing, flagging, and monitoring sources.

---

## Quick Reference

### Add a New Source
1. Find the country in `feeds.py`
2. Add a tuple: `("Outlet Name", "https://feed-url.xml")`
3. Run `python build.py` to test
4. Verify with `python watch_feeds.py`

### Disable a Broken Source
Comment it out with `#` and add reason:
```python
# ("The Standard", "https://..."),  # DISABLED: login redirect wall
```

### Replace a Paywalled Source
1. Run `python audit_links.py --find-free`
2. Find an alternative with same `cc` (country code)
3. Edit the tuple (same country block)
4. Test with `python build.py && python watch_feeds.py`

### Monitor Feed Health
```bash
python watch_feeds.py                  # One-time check
python watch_feeds.py --watch 3600     # Continuous (hourly)
```

---

## Understanding feeds.py Structure

Each country is a dict with `"cc"` (ISO 2-letter code), `"name"`, and `"sources"` list:

```python
{"cc": "AU", "name": "Australia", "sources": [
    ("ABC News",           "https://www.abc.net.au/news/feed/51120/rss.xml"),
    ("Guardian Australia", "https://www.theguardian.com/australia-news/rss"),
]},
```

Each source is a **tuple: `(outlet_name, feed_url)`**

---

## Why Sources Get Disabled

### Common Issues

| Symptom | Reason | Fix |
|---------|--------|-----|
| Redirect to login page | Paywall installed | Comment out with `# DISABLED: ...` reason |
| HTTP 404 / 403 | URL changed or feed removed | Comment out and investigate |
| Feed returns empty | Publisher stopped RSS | Monitor; may be temporary |
| Response timeout (>30s) | Server overloaded or defunct | Increase timeout or comment out |
| Articles behind paywall | Subscription wall on articles | Comment out (feed is live but gated) |

### Our Policy

- **If feed is accessible:** Keep it, even if some articles are gated (we'll skip those in audits)
- **If feed redirects to login:** Disable with reason comment
- **If feed is dead (404/timeout):** Disable with reason comment
- **If feed is empty:** Keep for 1 month (may be temporary); then disable

---

## Maintenance Workflows

### Weekly: "Are feeds still working?"
```bash
python watch_feeds.py
```
Look for status:
- ✓ OK — Good
- ⚠ SLOW — Monitor; increase timeout if consistent
- ❌ DEAD — Check manually; disable if confirmed broken

### Monthly: "Audit for paywalls"
```bash
python audit_links.py --quick
python audit_links.py --find-free
```
Review results:
- ✓ FREE — Keep as-is
- ⚠ MIXED — Keep (some free content is fine)
- ❌ PAYWALLED — Consider replacing using suggested alternatives

### Quarterly: "Deep review"
```bash
python audit_links.py              # Full audit
python find_sources.py --validate  # Check new candidates
```
Then update `feeds.py` with improvements.

---

## Common Edits

### Scenario 1: Source Goes Behind Paywall

Example: The Guardian Australia started requiring login.

1. Identify in audit: `audit_results.json` shows Guardian as ❌ PAYWALLED
2. Get suggestion: `audit_results.json` → `suggested_sources.json` → AU section
3. Edit `feeds.py`:
   ```python
   {"cc": "AU", "name": "Australia", "sources": [
       ("ABC News",           "https://www.abc.net.au/news/feed/51120/rss.xml"),
       # ("Guardian Australia", "https://..."),  # DISABLED: paywall 2026-06-14
   ]},
   ```
4. Rebuild:
   ```bash
   python build.py
   python watch_feeds.py
   ```

### Scenario 2: Feed URL Changes

Example: DW feeds restructured URLs.

1. Check what's wrong:
   ```bash
   python watch_feeds.py  # Shows HTTP 404 for DE/DW
   ```
2. Research new URL (visit publisher site, check their feed page)
3. Update tuple in `feeds.py`:
   ```python
   {"cc": "DE", "name": "Germany", "sources": [
       ("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-ger"),  # NEW URL
   ]},
   ```
4. Verify:
   ```bash
   python build.py
   python watch_feeds.py
   ```

### Scenario 3: Add New Country

Example: Add South Africa (ZA).

1. Research free English-language sources:
   ```bash
   python find_sources.py --list
   ```
2. Validate candidates:
   ```bash
   python find_sources.py --validate
   python find_sources.py --export
   ```
3. Copy generated code into `feeds.py` (add new country block or extend existing if present):
   ```python
   # Add after Zimbabwe block
   {"cc": "ZA", "name": "South Africa", "sources": [
       ("News24",         "https://www.news24.com/rss"),
       ("SABC News",      "https://www.sabcnews.com/rss"),
   ]},
   ```
4. Update `REGIONS` dict (at bottom of `feeds.py`) if needed:
   ```python
   REGIONS = {
       ...
       "Africa": ["NG", "KE", "GH", "ZW", "ZA"],  # Add ZA here
   }
   ```
5. Test:
   ```bash
   python build.py
   python watch_feeds.py
   ```

### Scenario 4: Source Too Slow

Example: A source consistently takes 20+ seconds to respond.

Option A: Increase global timeout in `build.py`:
```python
TIMEOUT = 20  # was 15
```

Option B: Disable the slow source (if it's the only one having issues):
```python
# ("Slow Outlet", "https://..."),  # DISABLED: timeout 20+ seconds
```

---

## Feed Validation Rules

When adding or replacing a source, it must pass:

1. **HTTP 200 response** — URL returns valid feed
2. **Valid RSS/Atom XML** — Parses without error
3. **Has items** — Feed contains at least 1 article
4. **Domestic focus** — Outlet reports on its own country
5. **Free-to-read headline** — At least headline is accessible (standfirst may be gated)

### Validation Tools

```bash
# Check if a URL is a valid feed
python find_sources.py --validate  # Validates candidates from hardcoded list

# Or manually (fast check)
curl -I https://www.outlet.com/rss  # Check HTTP response
curl https://www.outlet.com/rss | head -50  # Check format
```

---

## Disabling vs. Removing

### Use `#` Comment (Keep in history)
✅ **Preferred** for:
- Sources that went behind paywall
- Feeds that redirect to login
- URLs that changed temporarily
- Slow feeds under investigation

Example:
```python
# ("The Standard", "https://..."),  # DISABLED: login redirect 2026-06
```

### Delete Entirely (Remove from file)
❌ **Only if:**
- Source was never published or is a duplicate
- Duplicate of another source in same country

---

## Monitoring Checklist

### Daily (Automated)
- ☐ Cron job runs `python build.py` (GitHub Actions)
- ☐ New index.html deployed

### Weekly (Manual)
```bash
python watch_feeds.py
```
- ☐ Check for any ❌ DEAD feeds
- ☐ Note any ⚠ SLOW feeds (>3s)
- ☐ If dead: investigate and comment out with reason

### Monthly (Manual)
```bash
python audit_links.py --quick
python audit_links.py --find-free
```
- ☐ Review paywalled sources
- ☐ Check suggested alternatives
- ☐ Edit feeds.py if replacements found

### Quarterly (Deep)
```bash
python audit_links.py
python find_sources.py --validate
```
- ☐ Full paywall audit
- ☐ Validate new candidates
- ☐ Update feeds.py comprehensively
- ☐ Rebuild and test

---

## Example: Complete Edit Session

```bash
# 1. Check current state
python watch_feeds.py

# 2. Identify issues
# Output shows: KE/The Standard → HTTP 403 (login wall)

# 3. Get suggestions
python audit_links.py --find-free | grep Kenya

# 4. Validate alternative
python find_sources.py --list | grep Kenya

# 5. Edit feeds.py
# Comment out The Standard, add alternative

# 6. Rebuild
python build.py

# 7. Verify
python watch_feeds.py
python audit_links.py --quick

# 8. Commit
git add feeds.py index.html
git commit -m "Remove paywalled The Standard, add free alternative for Kenya"
```

---

## Troubleshooting

### "Feed shows OK but articles are paywalled"
→ That's fine! Some sites gate articles but provide free headlines via RSS. Our audit detects article-level paywalls; feed-level is more important.

### "Feed validates but build.py says EMPTY"
→ Feed may return empty at build time (transient issue). Monitor for 1–2 weeks before disabling.

### "All feeds dead after URL change"
→ Double-check URL syntax (typos). Test URL manually:
```bash
curl https://feed-url.xml | head -20
```

### "How do I test without rebuilding?"
→ Use `python find_sources.py --validate` on candidate URLs before editing feeds.py.

---

## Documentation to Update After edits

After editing `feeds.py`, update these if relevant:

- `README.md` — Country count if adding new country
- Git commit message — Why source was disabled/added
- This file if documenting new policy

---

## Quick Commands

```bash
# Health check
python watch_feeds.py

# Paywall audit (fast)
python audit_links.py --quick

# Find alternatives
python audit_links.py --find-free

# Validate candidates
python find_sources.py --validate

# Rebuild
python build.py

# Rebuild + full check
python build.py && python watch_feeds.py && python audit_links.py --quick
```

---

See **[AUDIT_README.md](AUDIT_README.md)** for detailed audit tool documentation.
