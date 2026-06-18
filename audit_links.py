"""
World River Link Auditor
Checks all news links in index.html for paywall blocks and source health.

Usage:
  python audit_links.py                      # audit all links
  python audit_links.py --quick              # fast audit (10s timeout, sample)
  python audit_links.py --sources            # audit feed URLs only (from feeds.py)
  python audit_links.py --find-free          # search for free alternatives
"""

import re
import sys
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict, Set, Tuple
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("WARNING: Playwright not installed. Install: pip install playwright", file=sys.stderr)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

PAYWALL_PATTERNS = [
    r"subscription",
    r"paywall",
    r"sign in to read",
    r"create account",
    r"become a member",
    r"subscribe",
    r"premium content",
    r"limited articles",
    r"log in",
    r"access denied",
    r"article limit",
]

PAYWALL_SELECTORS = [
    "[class*='paywall']",
    "[class*='subscription']",
    "[class*='subscribe']",
    "[id*='paywall']",
    "[id*='subscription']",
    "div[class*='wall']",
    "article.locked",
    ".article-locked",
    ".article-behind-paywall",
]

COMMON_NEWS_DOMAINS = {
    "bbc": "bbc.co.uk",
    "guardian": "theguardian.com",
    "ft": "ft.com",
    "wsj": "wsj.com",
    "nyt": "nytimes.com",
    "economist": "economist.com",
    "theatlantic": "theatlantic.com",
    "wapo": "washingtonpost.com",
}


def extract_links_from_html(html_path: str) -> Dict[str, List[Dict]]:
    """Parse index.html and extract all article links."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f" Failed to read {html_path}: {e}", file=sys.stderr)
        return {}

    links_by_source = {}
    # Match: <span class="source">SOURCE</span>...<a class="headline" href="URL"
    pattern = r'<span class="source">([^<]+)</span>.*?<a class="headline" href="([^"]+)"'
    for match in re.finditer(pattern, content, re.DOTALL):
        source = match.group(1)
        url = match.group(2)
        if source not in links_by_source:
            links_by_source[source] = []
        links_by_source[source].append({"url": url, "status": None, "paywall": None})

    return links_by_source


def extract_feed_urls() -> Dict[str, str]:
    """Extract feed URLs from feeds.py."""
    try:
        from feeds import COUNTRIES
        feeds = {}
        for country in COUNTRIES:
            for name, url in country["sources"]:
                key = f"{country['cc']} {name}"
                feeds[key] = url
        return feeds
    except Exception as e:
        print(f" Failed to extract feeds: {e}", file=sys.stderr)
        return {}


def check_link_with_playwright(url: str, timeout_sec: int = 10) -> Tuple[bool, str]:
    """
    Check if a link is paywalled using Playwright.
    Returns (is_paywalled, reason)
    """
    if not HAS_PLAYWRIGHT:
        return None, "Playwright not installed"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)

            # Check for paywall selectors
            for selector in PAYWALL_SELECTORS:
                try:
                    if page.query_selector(selector):
                        return True, f"Found paywall element: {selector}"
                except:
                    pass

            # Check page text for paywall keywords
            text = page.content().lower()
            for pattern in PAYWALL_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    # Verify it's in the main content area (not just ads/footer)
                    if re.search(
                        rf"{pattern}.*?(article|content|main)",
                        text,
                        re.IGNORECASE | re.DOTALL,
                    ):
                        return True, f"Detected paywall keyword: {pattern}"

            browser.close()
            return False, "OK"

    except PlaywrightTimeout:
        return None, "Timeout"
    except Exception as e:
        return None, f"Error: {type(e).__name__}"


def check_feed_url(url: str) -> Tuple[bool, str]:
    """Check if a feed URL is accessible and returns valid XML."""
    if not HAS_REQUESTS:
        return None, "Requests not installed"

    try:
        r = requests.head(
            url,
            timeout=5,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        if r.status_code == 200:
            return True, f"HTTP {r.status_code}"
        else:
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        return None, f"Error: {type(e).__name__}"


def find_free_alternatives(source_name: str, country_code: str) -> List[Dict]:
    """
    Suggest free alternative news sources for a given country.
    Hardcoded based on known free-to-read news outlets.
    """
    alternatives = {
        "GB": [
            {"name": "BBC News", "url": "https://www.bbc.com/news/", "type": "broadcast"},
            {
                "name": "Sky News",
                "url": "https://news.sky.com/",
                "type": "commercial",
            },
            {
                "name": "ITV News",
                "url": "https://www.itv.com/news",
                "type": "broadcast",
            },
        ],
        "US": [
            {
                "name": "NPR",
                "url": "https://www.npr.org/",
                "type": "public_radio",
                "note": "Already in River",
            },
            {"name": "AP News", "url": "https://apnews.com/", "type": "wire"},
            {"name": "Reuters", "url": "https://www.reuters.com/", "type": "wire"},
            {
                "name": "ProPublica",
                "url": "https://www.propublica.org/",
                "type": "nonprofit",
            },
        ],
        "AU": [
            {
                "name": "ABC News",
                "url": "https://www.abc.net.au/news/",
                "type": "broadcast",
                "note": "Already in River",
            },
            {
                "name": "SBS News",
                "url": "https://www.sbs.com.au/news",
                "type": "broadcast",
            },
        ],
        "FR": [
            {
                "name": "France 24",
                "url": "https://www.france24.com/",
                "type": "broadcast",
            },
            {"name": "RFI", "url": "https://www.rfi.fr/", "type": "broadcast"},
        ],
        "DE": [
            {
                "name": "Deutsche Welle",
                "url": "https://www.dw.com/",
                "type": "broadcast",
                "note": "Already in River",
            },
            {"name": "DPA", "url": "https://www.dpa.com/", "type": "wire"},
        ],
        "CA": [
            {
                "name": "CBC News",
                "url": "https://www.cbc.ca/news",
                "type": "broadcast",
                "note": "Already in River",
            },
        ],
        "IN": [
            {
                "name": "NDTV",
                "url": "https://www.ndtv.com/",
                "type": "commercial",
            },
            {
                "name": "India Today",
                "url": "https://www.indiatoday.in/",
                "type": "commercial",
            },
        ],
    }

    return alternatives.get(country_code, [])


def audit_links(html_path: str, timeout_sec: int = 10, sample_size: int = None):
    """Main audit function."""
    print(f"\n World River Link Auditor")
    print(f"" * 60)

    links_by_source = extract_links_from_html(html_path)
    if not links_by_source:
        print(
            " No links found in index.html. Check that file exists and is up-to-date.",
            file=sys.stderr,
        )
        return

    print(f" Found {sum(len(l) for l in links_by_source.values())} links from {len(links_by_source)} sources")

    # Collect results
    results = {
        "timestamp": datetime.now().isoformat(),
        "html_file": html_path,
        "sources": {},
        "summary": {"total_sources": 0, "all_free": 0, "partial_paywall": 0, "all_paywalled": 0},
    }

    print(f"\n Auditing links (timeout: {timeout_sec}s)...\n")

    for source_idx, (source, links) in enumerate(links_by_source.items(), 1):
        print(f"[{source_idx}/{len(links_by_source)}] {source:<35}", end="", flush=True)

        # Sample if requested
        test_links = links[:sample_size] if sample_size else links
        paywalls = 0
        free = 0
        unknown = 0

        for link_obj in test_links:
            url = link_obj["url"]
            is_paywalled, reason = check_link_with_playwright(url, timeout_sec)

            if is_paywalled is True:
                paywalls += 1
            elif is_paywalled is False:
                free += 1
            else:
                unknown += 1
            link_obj["status"] = reason
            link_obj["paywall"] = is_paywalled

        # Classify source
        if paywalls == 0:
            status = " FREE"
            results["summary"]["all_free"] += 1
        elif free > 0:
            status = f" MIXED ({free} free, {paywalls} paywalled)"
            results["summary"]["partial_paywall"] += 1
        else:
            status = " PAYWALLED"
            results["summary"]["all_paywalled"] += 1

        print(f" {status}")
        results["sources"][source] = {
            "link_count": len(links),
            "sampled": len(test_links),
            "free_count": free,
            "paywall_count": paywalls,
            "unknown_count": unknown,
            "status": status,
            "details": test_links[:3],  # Store first 3 for inspection
        }

    results["summary"]["total_sources"] = len(links_by_source)

    # Report
    print(f"\n{'' * 60}")
    print(f" SUMMARY")
    print(f"" * 60)
    print(f"All Free:        {results['summary']['all_free']}")
    print(f"Mixed (some free): {results['summary']['partial_paywall']}")
    print(f"All Paywalled:   {results['summary']['all_paywalled']}")

    # List paywalled sources
    paywalled = [
        s
        for s, r in results["sources"].items()
        if "PAYWALLED" in r["status"] or "MIXED" in r["status"]
    ]
    if paywalled:
        print(f"\n Sources with paywall concerns:")
        for s in paywalled:
            print(f"  - {s}: {results['sources'][s]['status']}")

    # Save results
    json_path = Path(html_path).parent / "audit_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n Saved results to {json_path}")

    return results


def audit_feed_urls():
    """Check feed URLs from feeds.py for accessibility."""
    print(f"\n World River Feed Auditor")
    print(f"" * 60)

    feeds = extract_feed_urls()
    if not feeds:
        print(" No feeds found", file=sys.stderr)
        return

    print(f" Found {len(feeds)} feeds\n")

    results = {"timestamp": datetime.now().isoformat(), "feeds": {}}

    for idx, (key, url) in enumerate(feeds.items(), 1):
        print(f"[{idx}/{len(feeds)}] {key:<40}", end="", flush=True)
        is_live, reason = check_feed_url(url)
        status = "" if is_live else ("" if is_live is None else "")
        print(f" {status} {reason}")
        results["feeds"][key] = {"url": url, "accessible": is_live, "reason": reason}

    # Summary
    live = sum(1 for r in results["feeds"].values() if r["accessible"] is True)
    dead = sum(1 for r in results["feeds"].values() if r["accessible"] is False)
    print(
        f"\n{'' * 60}\n {live} live · {dead} dead · {len(feeds) - live - dead} unknown"
    )

    json_path = Path("feed_audit_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f" Saved to {json_path}\n")


def suggest_free_alternatives():
    """Suggest free alternatives based on known paywalled sources."""
    from feeds import COUNTRIES

    print(f"\n Suggesting Free News Sources")
    print(f"" * 60)

    suggestions = {}
    for country in COUNTRIES:
        alts = find_free_alternatives("", country["cc"])
        if alts:
            suggestions[country["cc"]] = {
                "country": country["name"],
                "alternatives": alts,
            }

    if suggestions:
        for cc, data in suggestions.items():
            print(f"\n{data['country']} ({cc}):")
            for alt in data["alternatives"]:
                note = f" ({alt.get('note', '')})" if alt.get("note") else ""
                print(
                    f"  • {alt['name']:<30} {alt['type']:<15} {alt['url']}{note}"
                )

    json_path = Path("suggested_sources.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2)
    print(f"\n Saved to {json_path}\n")


def main():
    ap = argparse.ArgumentParser(
        description="Audit World River links for paywall blocks and feed health."
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="Quick audit (10s timeout, 2 links per source)",
    )
    ap.add_argument(
        "--sources",
        action="store_true",
        help="Audit feed URLs only (no article links)",
    )
    ap.add_argument(
        "--find-free",
        action="store_true",
        help="Suggest free alternative sources",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout per link in seconds (default: 10)",
    )
    args = ap.parse_args()

    if args.sources:
        audit_feed_urls()
    elif args.find_free:
        suggest_free_alternatives()
    else:
        sample = 2 if args.quick else None
        audit_links("index.html", timeout_sec=args.timeout, sample_size=sample)


if __name__ == "__main__":
    main()
