"""Open the first article from each source and check it (a) resolves 200 and
(b) isn't paywalled. Paywall heuristic = strong gating phrases in the HTML.
Free sites with a 'subscribe to newsletter' CTA won't trip it (those phrases
are deliberately excluded)."""
import sys, requests, feedparser
from concurrent.futures import ThreadPoolExecutor
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from feeds import COUNTRIES

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Strong paywall signals only (avoid newsletter-signup false positives)
WALL = ["subscribe to continue", "subscribe to read", "to continue reading",
        "this article is for subscribers", "subscribers only",
        "register to continue", "sign in to read the full", "premium content",
        "become a subscriber", "unlock this article"]

def first_link(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=12)
    d = feedparser.parse(r.content)
    for e in d.entries:
        if e.get("link"):
            return e["link"]
    return None

def check(country):
    cc, name = country["cc"], country["sources"][0][0]
    feed_url = country["sources"][0][1]
    try:
        link = first_link(feed_url)
        if not link:
            return (cc, name, "?", "no link", "")
        r = requests.get(link, headers={"User-Agent": UA}, timeout=15)
        body = r.text.lower()
        hit = next((w for w in WALL if w in body), "")
        verdict = "PAYWALL?" if hit else "free"
        return (cc, name, r.status_code, f"{verdict} ({len(r.content)//1000}k)", hit)
    except Exception as e:
        return (cc, name, "ERR", f"{type(e).__name__}", "")

def main():
    with ThreadPoolExecutor(max_workers=14) as ex:
        rows = list(ex.map(check, COUNTRIES))
    print(f"\n{'CC':<3}{'SOURCE':<20}{'HTTP':>5}  RESULT")
    print("-"*70)
    flagged = []
    for cc, name, status, result, hit in rows:
        bad = (status != 200) or result.startswith("PAYWALL")
        if bad: flagged.append((cc, name, status, result, hit))
        print(f"{cc:<3}{name:<20}{str(status):>5}  {result}{('  <- '+hit) if hit else ''}")
    print("-"*70)
    if flagged:
        print("NEEDS ATTENTION:")
        for cc, name, status, result, hit in flagged:
            print(f"  {cc} {name}: HTTP {status}, {result} {hit}")
    else:
        print("All first-articles resolved 200 and read free.")

if __name__ == "__main__":
    main()
