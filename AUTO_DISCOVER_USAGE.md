# Auto-Discover Workflow

Automated feed discovery using Playwright to crawl known news outlets for RSS feeds.

## One-Command Workflow

```bash
# Discover, validate, and add feeds for a country
python auto_discover.py -c DZ -n Algeria
```

Steps:
1. **Crawl** known outlet domains for feed URLs (`/feed/`, `/rss/`, etc.)
2. **Validate** each URL (check for valid RSS/Atom + item count > 0)
3. **Add** working feeds to `find_sources.py`
4. **Suggestion**: Run `python find_sources.py -c {CC} --validate` to double-check

## Supported Countries

Currently has known outlets for:
- **Nordic**: SE, NO, DK, FI
- **Europe**: PL, DE, FR, IT, ES, GB, IE, NL, UA
- **Africa**: DZ, EG, NG, KE, GH, ZW, SN

### To add a new country:

Edit `auto_discover.py` and add to `KNOWN_OUTLETS` dict:

```python
KNOWN_OUTLETS = {
    ...
    "XX": ["outlet1.com", "outlet2.com", "outlet3.com"],
}
```

Then run:
```bash
python auto_discover.py -c XX -n "Country Name"
```

(You can find outlet domains by searching "{country name} news broadcaster" on Google)

## Example: Algeria

```bash
$ python auto_discover.py -c DZ -n Algeria
======================================================================
AUTO-DISCOVERING FEEDS FOR ALGERIA (DZ)
======================================================================

[*] Crawling 5 known outlets...
  Crawling aps.dz...
  Crawling echoroukonline.com...
  Crawling tsa-algerie.com...
  Crawling algeria-watch.org...
  Crawling algeriafocus.net...

[+] Found 4 candidate feed URLs

[*] Validating feeds...
  [OK] https://www.tsa-algerie.com/feed/ (10 items)
  [OK] https://www.tsa-algerie.com/comments/feed/ (10 items)
  [OK] https://tsa-algerie.com/feed/ (10 items)
  [OK] https://tsa-algerie.com/rss/ (10 items)

[S] Added 4 feeds for DZ to find_sources.py

[+] Next step:
    python find_sources.py -c DZ --validate
```

## Next: Add to feeds.py

Once validated, add the best feed(s) to `feeds.py`:

```python
{"cc": "DZ", "name": "Algeria", "sources": [
    ("TSA", "https://www.tsa-algerie.com/feed/"),
]},
```

Then rebuild:
```bash
python build.py
```

## Quick Copy-Paste Template

```bash
# Discover feeds for a new country — just change XXX
python auto_discover.py -c XX -n "Country Name"
python find_sources.py -c XX --validate
python build.py
```

Replace:
- `XX` with country code (e.g., SN, ET, UG)
- `"Country Name"` with full country name (e.g., Senegal)

Then manually add the best feed(s) to `feeds.py` and rebuild.

## Customization

### Skip validation
```bash
python auto_discover.py -c DZ -n Algeria --no-validate
```

### Skip adding to find_sources.py
```bash
python auto_discover.py -c DZ -n Algeria --no-add
```

### Add outlet domains for a new country

Edit `auto_discover.py` → `OUTLET_DOMAINS` dict:

```python
"XX": [
    "outlet1.com",
    "outlet2.com",
    "outlet3.com",
],
```

Then run the discovery.
