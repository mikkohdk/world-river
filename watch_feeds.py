"""
Lightweight feed health monitor.
Periodically checks all RSS feeds and reports dead/slow ones.

Usage:
  python watch_feeds.py                  # one-off health check
  python watch_feeds.py --watch 3600     # repeat every 1 hour
  python watch_feeds.py --threshold 5    # mark as dead if timeout > 5s
"""

import sys
import time
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ Requires: pip install requests", file=sys.stderr)
    sys.exit(1)

from feeds import COUNTRIES


class FeedWatcher:
    def __init__(self, timeout_sec=5, warn_threshold_sec=3):
        self.timeout = timeout_sec
        self.warn_threshold = warn_threshold_sec
        self.ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
            "WorldRiver/1.0"
        )

    def check_feed(self, name, url):
        """
        Check a single feed.
        Returns (status, response_time_sec, item_count)
        """
        start = time.time()
        try:
            r = requests.get(
                url,
                timeout=self.timeout,
                headers={"User-Agent": self.ua},
            )
            elapsed = time.time() - start

            if r.status_code != 200:
                return f"HTTP {r.status_code}", elapsed, 0

            # Quick parse to count items
            try:
                import feedparser
                d = feedparser.parse(r.content)
                item_count = len(d.entries)
                if item_count == 0:
                    return "EMPTY", elapsed, 0
                return "OK", elapsed, item_count
            except:
                return "PARSE_ERROR", elapsed, 0

        except requests.Timeout:
            elapsed = time.time() - start
            return "TIMEOUT", elapsed, 0
        except requests.ConnectionError:
            elapsed = time.time() - start
            return "CONN_ERROR", elapsed, 0
        except Exception as e:
            elapsed = time.time() - start
            return f"ERROR: {type(e).__name__}", elapsed, 0

    def run(self):
        """Single health check."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"ok": 0, "slow": 0, "dead": 0},
            "feeds": {}
        }

        total_feeds = sum(len(c["sources"]) for c in COUNTRIES)
        print(f"\nFeed Health Check -- {total_feeds} feeds")
        print("=" * 80)

        for country in COUNTRIES:
            for name, url in country["sources"]:
                status, elapsed, items = self.check_feed(name, url)
                key = f"{country['cc']} {name}"

                # Classify
                if status == "OK":
                    if elapsed > self.warn_threshold:
                        symbol = "!"
                        results["summary"]["slow"] += 1
                    else:
                        symbol = "."
                        results["summary"]["ok"] += 1
                else:
                    symbol = "X"
                    results["summary"]["dead"] += 1

                # Report
                time_str = f"{elapsed:.1f}s"
                status_str = f"{status}" if status != "OK" else f"OK ({items} items)"
                print(
                    f"{symbol} {key:<40} {time_str:>6}   {status_str}"
                )

                results["feeds"][key] = {
                    "url": url,
                    "status": status,
                    "response_time": round(elapsed, 2),
                    "item_count": items,
                }

        # Summary
        print("=" * 80)
        ok = results["summary"]["ok"]
        slow = results["summary"]["slow"]
        dead = results["summary"]["dead"]
        print(
            f"OK: {ok}  SLOW (>{self.warn_threshold}s): {slow}  DEAD: {dead}"
        )

        # Save
        json_path = Path("feed_health.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved to {json_path}\n")

        return results

    def watch(self, interval_sec):
        """Continuous monitoring loop."""
        print(f"\nFeed Watcher -- checking every {interval_sec}s")
        print("Press Ctrl+C to stop\n")

        iteration = 0
        while True:
            iteration += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{iteration}] {now}")
            print("─" * 80)
            self.run()
            print(f"Next check in {interval_sec}s...")
            try:
                time.sleep(interval_sec)
            except KeyboardInterrupt:
                print("\nStopped.")
                break


def main():
    ap = argparse.ArgumentParser(
        description="Monitor World River feed health and response times."
    )
    ap.add_argument(
        "--watch",
        type=int,
        metavar="SECONDS",
        help="Repeat check every N seconds (continuous mode)",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Feed timeout in seconds (default: 5)",
    )
    ap.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Warn if response > N seconds (default: 3)",
    )
    args = ap.parse_args()

    watcher = FeedWatcher(timeout_sec=args.timeout, warn_threshold_sec=args.threshold)

    if args.watch:
        watcher.watch(args.watch)
    else:
        watcher.run()


if __name__ == "__main__":
    main()
