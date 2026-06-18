"""
Automated feed discovery using Playwright.
Searches for news outlets (via browser), crawls for RSS feeds, validates them, adds to find_sources.py.

Usage:
  python auto_discover.py -c DZ -n Algeria
  python auto_discover.py -c DZ -n Algeria --no-validate (just collect URLs)
"""

import asyncio
import re
import sys
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("ERROR: playwright not installed. Run: pip install playwright")
    sys.exit(1)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Known major news outlets by country code
# Add more manually as you discover them — this is a fallback when search fails
KNOWN_OUTLETS = {
    # Nordic
    "SE": ["svt.se", "dn.se", "aftonbladet.se", "expressen.se"],
    "NO": ["nrk.no", "tv2.no", "aftenposten.no", "vg.no"],
    "DK": ["dr.dk", "tv2.dk", "politiken.dk"],
    "FI": ["yle.fi", "hs.fi"],
    # Europe
    "PL": ["tvn24.pl", "onet.pl"],
    "DE": ["spiegel.de", "tagesschau.de"],
    "FR": ["lemonde.fr", "lefigaro.fr"],
    "IT": ["repubblica.it", "corriere.it"],
    "ES": ["elpais.com", "eldiario.es"],
    "GB": ["bbc.co.uk", "theguardian.com"],
    "IE": ["thejournal.ie", "rte.ie"],
    "NL": ["nos.nl", "nrc.nl"],
    "UA": ["nv.ua", "ukrinform.net"],
    # Africa
    "DZ": ["tsa-algerie.com", "echoroukonline.com"],
    "EG": ["egyptindependent.com", "egypttoday.com"],
    "NG": ["thecable.ng", "premiumtimesng.com"],
    "KE": ["standardmedia.co.ke", "nation.co.ke"],
    "GH": ["myjoyonline.com", "ghanaweb.com"],
    "ZW": ["newzimbabwe.com", "herald.co.zw"],
    "SN": ["seneweb.com", "rewmi.com"],
}


async def search_outlets(country_code, country_name):
    """Use known outlets or suggest adding them."""
    outlets = KNOWN_OUTLETS.get(country_code.upper(), [])

    if outlets:
        print(f"\n[*] Using {len(outlets)} known outlets for {country_name}...")
        for i, outlet in enumerate(outlets, 1):
            print(f"  [{i}] {outlet}")
        return [f"https://{o}" for o in outlets]
    else:
        print(f"\n[!] No known outlets for {country_code}")
        print(f"    Add some to auto_discover.py → KNOWN_OUTLETS['{country_code}']")
        print(f"    Example: KNOWN_OUTLETS['{country_code}'] = ['outlet1.com', 'outlet2.com', ...]")
        return []


async def crawl_for_feeds(browser, url, outlet_name, max_per_site=2):
    """Crawl a website looking for RSS feed URLs."""
    base_url = url if url.startswith('http') else f"https://{url}"
    print(f"  Crawling {urlparse(base_url).netloc}...")

    context = await browser.new_context()
    page = await context.new_page()
    feed_urls = []

    try:
        await page.goto(base_url, wait_until="domcontentloaded", timeout=8000)

        # Look for feed links in HTML
        feed_patterns = [
            r'href=["\'](https?://[^\s"\']+(?:/feed|/rss|/feeds)(?:/|\.xml)?)["\']',
            r'href=["\'](/[^\s"\']*(?:feed|rss|feeds)[^\s"\']*)["\']',
        ]

        page_html = await page.content()

        for pattern in feed_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches[:max_per_site]:
                if match.startswith('/'):
                    match = urljoin(base_url, match)
                if match not in feed_urls and "http" in match:
                    feed_urls.append(match)

        # Try common feed paths
        common_paths = ['/feed/', '/feed.xml', '/rss/', '/rss.xml', '/feeds/']
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        for path in common_paths:
            url_to_try = base_domain + path
            if url_to_try not in feed_urls:
                try:
                    resp = await page.goto(url_to_try, wait_until="domcontentloaded", timeout=3000)
                    if resp and resp.status == 200:
                        feed_urls.append(url_to_try)
                except:
                    pass

        await context.close()
        return feed_urls

    except Exception as e:
        await context.close()
        return []


def validate_feed(url):
    """Check if URL is a valid RSS/Atom feed with content."""
    if not HAS_REQUESTS:
        return None

    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code != 200:
            return None

        content = resp.text
        if '<rss' in content or '<feed' in content:
            item_count = len(re.findall(r'<item>|<entry>', content))
            if item_count > 0:
                return {'status': 'OK', 'items': item_count}

        return None

    except:
        return None


async def auto_discover(country_code, country_name, validate=True):
    """Main discovery flow."""
    print(f"\n{'='*70}")
    print(f"AUTO-DISCOVERING FEEDS FOR {country_name.upper()} ({country_code})")
    print(f"{'='*70}")

    if not HAS_PLAYWRIGHT:
        print("ERROR: playwright required")
        return []

    # Get outlet domains (known list or empty)
    outlet_urls = await search_outlets(country_code, country_name)

    if not outlet_urls:
        return []

    # Crawl each outlet for feed URLs
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print(f"\n[*] Crawling {len(outlet_urls)} outlets for feeds...")
        all_feed_urls = []
        for outlet_url in outlet_urls:
            feeds = await crawl_for_feeds(browser, outlet_url, country_name)
            all_feed_urls.extend(feeds)

        await browser.close()

    all_feed_urls = list(dict.fromkeys(all_feed_urls))

    if not all_feed_urls:
        print("[!] No feed URLs found")
        return []

    print(f"\n[+] Found {len(all_feed_urls)} candidate feed URLs")

    if validate:
        print("\n[*] Validating feeds...")
        valid_feeds = []

        for url in all_feed_urls:
            result = validate_feed(url)
            if result:
                valid_feeds.append({'url': url, 'items': result['items']})
                print(f"  [OK] {url} ({result['items']} items)")
            else:
                print(f"  [X] {url}")

        return valid_feeds
    else:
        return [{'url': url, 'items': None} for url in all_feed_urls]


def add_to_find_sources(country_code, country_name, feeds):
    """Add validated feeds to find_sources.py."""
    if not feeds:
        print("[!] No feeds to add")
        return False

    find_sources_path = Path('find_sources.py')
    if not find_sources_path.exists():
        print("ERROR: find_sources.py not found")
        return False

    with open(find_sources_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if country already exists
    if f'"{country_code}": [' in content:
        print(f"[!] {country_code} already exists in SOURCE_CANDIDATES")
        return False

    # Generate Python code for feeds
    code_lines = []
    for i, feed in enumerate(feeds, 1):
        # Try to infer outlet name from URL
        outlet_name = urlparse(feed['url']).netloc.replace('www.', '').split('.')[0].title()
        code_lines.append(
            f'''        {{
            "name": "{outlet_name}",
            "url": "{feed['url']}",
            "type": "unknown",
            "notes": "{feed.get('items', 'N/A')} items",
        }},'''
        )

    new_entry = f''',
    "{country_code}": [
{chr(10).join(code_lines)}
    ]'''

    # Find the closing brace of SOURCE_CANDIDATES and insert before it
    # Look for the pattern: "},\n]" at the end of a country entry, then the final "}"
    insert_pos = content.rfind('},\n}')
    if insert_pos == -1:
        # Try alternate pattern
        insert_pos = content.rfind('},\n    ],\n}')
        if insert_pos == -1:
            print("ERROR: Cannot find proper insertion point in find_sources.py")
            return False
        insert_pos += len('},\n    ],')
    else:
        insert_pos += len('},')

    new_content = content[:insert_pos] + new_entry + content[insert_pos:]

    with open(find_sources_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n[S] Added {len(feeds)} feeds for {country_code} to find_sources.py")
    return True


async def main():
    ap = argparse.ArgumentParser(
        description="Automated feed discovery using Playwright"
    )
    ap.add_argument('-c', '--country', required=True, help='Country code (e.g., DZ)')
    ap.add_argument('-n', '--name', required=True, help='Country name (e.g., Algeria)')
    ap.add_argument('--no-validate', action='store_true', help='Skip validation')
    ap.add_argument('--no-add', action='store_true', help='Skip adding to find_sources.py')

    args = ap.parse_args()

    # Run discovery
    feeds = await auto_discover(args.country, args.name, validate=not args.no_validate)

    if feeds and not args.no_add:
        add_to_find_sources(args.country, args.name, feeds)
        print(f"\n[+] Next step:")
        print(f"    python find_sources.py -c {args.country} --validate")


if __name__ == "__main__":
    asyncio.run(main())
