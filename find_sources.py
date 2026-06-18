"""
Find new free news sources for coverage gaps in World River.
Maintains a curated list of known-free, domestic-focus English-language outlets.

Additions can be validated by:
  python find_sources.py --validate <url>
"""

import re
import sys
import json
import argparse
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Candidates organized by coverage region/country
# Format: {"cc": "XX", "name": "Country Name", "source_candidates": [
#   {"name": "Outlet", "url": "feed_url", "type": "broadcast|wire|commercial|nonprofit", "notes": "..."}
# ]}

SOURCE_CANDIDATES = {
    # NORDIC & BALTIC
    "DK": [
        {
            "name": "DR (Danmarks Radio)",
            "url": "https://www.dr.dk/nyheder/service/feeds/allenyheder",
            "type": "broadcast",
            "notes": "Danish public broadcaster, free",
        },
        {
            "name": "TV 2 News",
            "url": "https://nyheder.tv2.dk/feeds/",
            "type": "broadcast",
            "notes": "Danish commercial broadcaster",
        },
    ],
    "SE": [
        {
            "name": "SVT Nyheter",
            "url": "https://www.svt.se/nyheter/rss.xml",
            "type": "broadcast",
            "notes": "Swedish public broadcaster",
        },
    ],
    "NO": [
        {
            "name": "NRK Nyheter",
            "url": "https://www.nrk.no/nyheter/toppsaker/feed/",
            "type": "broadcast",
            "notes": "Norwegian public broadcaster",
        },
        {
            "name": "TV 2",
            "url": "https://www.tv2.no/nyheter/rss",
            "type": "broadcast",
            "notes": "Norwegian commercial broadcaster",
        },
    ],
    "LT": [
        {
            "name": "LRT (Lithuanian National Radio)",
            "url": "https://www.lrt.lt/news/lt/rss/",
            "type": "broadcast",
            "notes": "Lithuanian public broadcaster",
        },
    ],
    "LV": [
        {
            "name": "LSM",
            "url": "https://www.lsm.lv/rss/",
            "type": "broadcast",
            "notes": "Latvian public media",
        },
    ],
    "EE": [
        {
            "name": "ERR (Estonian Public Broadcasting)",
            "url": "https://www.err.ee/feeds/",
            "type": "broadcast",
            "notes": "Estonian public broadcaster",
        },
    ],

    # CENTRAL & EASTERN EUROPE
    "CZ": [
        {
            "name": "Czech Radio",
            "url": "https://www.irozhlas.cz/rss",
            "type": "broadcast",
            "notes": "Czech public radio",
        },
    ],
    "SK": [
        {
            "name": "RTVS (Slovak Radio)",
            "url": "https://rtvs.sk/rss/",
            "type": "broadcast",
            "notes": "Slovak public broadcaster",
        },
    ],
    "HU": [
        {
            "name": "MTI (Hungarian News Agency)",
            "url": "https://mti.hu/rss/",
            "type": "wire",
            "notes": "Hungarian news agency",
        },
    ],
    "RO": [
        {
            "name": "Romania Insider",
            "url": "https://www.romania-insider.com/feed",
            "type": "commercial",
            "notes": "English-language Romania news",
        },
        {
            "name": "TVR (Romanian Radio-TV)",
            "url": "https://www.tvr.ro/feeds/",
            "type": "broadcast",
            "notes": "Romanian public broadcaster",
        },
    ],
    "BG": [
        {
            "name": "BNR (Bulgarian National Radio)",
            "url": "https://www.bnr.bg/rss/",
            "type": "broadcast",
            "notes": "Bulgarian public radio",
        },
    ],
    "HR": [
        {
            "name": "HRT (Croatian Radio-TV)",
            "url": "https://hrt.hr/rss",
            "type": "broadcast",
            "notes": "Croatian public broadcaster",
        },
    ],
    "SI": [
        {
            "name": "RTV SLO (Slovenian Radio-TV)",
            "url": "https://www.rtvslo.si/rss/",
            "type": "broadcast",
            "notes": "Slovenian public broadcaster",
        },
    ],
    "RS": [
        {
            "name": "RTS (Serbian Radio-TV)",
            "url": "https://www.rts.rs/feed/",
            "type": "broadcast",
            "notes": "Serbian public broadcaster",
        },
    ],

    # SOUTHERN EUROPE
    "GR": [
        {
            "name": "ERT (Hellenic Broadcasting Corporation)",
            "url": "https://ert.gr/rss/",
            "type": "broadcast",
            "notes": "Greek public broadcaster",
        },
    ],
    "CY": [
        {
            "name": "CyBC (Cyprus Broadcasting)",
            "url": "https://www.cybc.com.cy/rss/",
            "type": "broadcast",
            "notes": "Cyprus public broadcaster",
        },
    ],
    "MT": [
        {
            "name": "PBS (Public Broadcasting Services Malta)",
            "url": "https://www.pbs.com.mt/rss/",
            "type": "broadcast",
            "notes": "Maltese public broadcaster",
        },
    ],

    # IBERIAN & MEDITERRANEAN
    "ES": [
        {
            "name": "RTVE (Spanish Radio-TV)",
            "url": "https://www.rtve.es/rss/",
            "type": "broadcast",
            "notes": "Spanish public broadcaster",
        },
        {
            "name": "El Pais",
            "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
            "type": "commercial",
            "notes": "Spanish newspaper",
        },
    ],
    "PT": [
        {
            "name": "RTP (Radiotelevisao Portuguesa)",
            "url": "https://www.rtp.pt/rss/",
            "type": "broadcast",
            "notes": "Portuguese public broadcaster",
        },
    ],

    # SWITZERLAND & AUSTRIA
    "CH": [
        {
            "name": "SRF (Swiss Radio)",
            "url": "https://www.srf.ch/feed/rss/news/",
            "type": "broadcast",
            "notes": "Swiss public radio/TV",
        },
    ],
    "AT": [
        {
            "name": "ORF (Austrian Broadcasting)",
            "url": "https://orf.at/feeds/",
            "type": "broadcast",
            "notes": "Austrian public broadcaster",
        },
    ],

    # UNITED KINGDOM & IRELAND (alternatives)
    "GB": [
        {
            "name": "BBC News",
            "url": "https://feeds.bbci.co.uk/news/rss.xml",
            "type": "broadcast",
            "notes": "British public broadcaster",
        },
        {
            "name": "The Independent",
            "url": "https://www.independent.co.uk/news/uk/rss",
            "type": "commercial",
            "notes": "Free-to-read outlet",
        },
    ],
    "IE": [
        {
            "name": "RTE (Irish Broadcasting)",
            "url": "https://www.rte.ie/feeds/",
            "type": "broadcast",
            "notes": "Irish public broadcaster",
        },
    ],

    # AMERICAS
    "US": [
        {
            "name": "NPR",
            "url": "https://feeds.npr.org/1003/rss.xml",
            "type": "nonprofit",
            "notes": "US public radio",
        },
        {
            "name": "AP News",
            "url": "https://apnews.com/feed",
            "type": "wire",
            "notes": "Wire service, free",
        },
    ],
    "CA": [
        {
            "name": "CBC News",
            "url": "https://www.cbc.ca/webfeed/rss/rss-canada",
            "type": "broadcast",
            "notes": "Canadian public broadcaster",
        },
    ],
    "MX": [
        {
            "name": "Reforma",
            "url": "https://www.reforma.com/rss",
            "type": "commercial",
            "notes": "Mexican newspaper",
        },
    ],
    "AR": [
        {
            "name": "Infobae",
            "url": "https://www.infobae.com/feed/",
            "type": "commercial",
            "notes": "Argentine news",
        },
    ],
    "CL": [
        {
            "name": "La Tercera",
            "url": "https://www.latercera.com/feed/",
            "type": "commercial",
            "notes": "Chilean newspaper",
        },
    ],
    "CO": [
        {
            "name": "El Pais Colombia",
            "url": "https://www.elpais.com.co/feed",
            "type": "commercial",
            "notes": "Colombian newspaper",
        },
    ],
    "PE": [
        {
            "name": "Peru21",
            "url": "https://peru21.pe/feed/",
            "type": "commercial",
            "notes": "Peruvian newspaper",
        },
    ],
    "VE": [
        {
            "name": "Tal Cual",
            "url": "https://talcualdigital.com/feed/",
            "type": "commercial",
            "notes": "Venezuelan independent news",
        },
    ],
    "EC": [
        {
            "name": "El Comercio Ecuador",
            "url": "https://www.elcomercio.com/rss.xml",
            "type": "commercial",
            "notes": "Ecuadorian newspaper",
        },
    ],

    # AFRICA
    "ZA": [
        {
            "name": "SABC News",
            "url": "https://www.sabcnews.com/rss",
            "type": "broadcast",
            "notes": "South African public broadcaster",
        },
    ],
    "NG": [
        {
            "name": "Premium Times",
            "url": "https://www.premiumtimesng.com/feed/",
            "type": "commercial",
            "notes": "Nigerian independent news",
        },
    ],
    "KE": [
        {
            "name": "Capital FM Kenya",
            "url": "https://www.capitalfm.co.ke/feed/",
            "type": "broadcast",
            "notes": "Kenyan commercial broadcaster",
        },
    ],
    "TZ": [
        {
            "name": "Tanzania Daily News",
            "url": "https://www.dailynews.co.tz/feed/",
            "type": "commercial",
            "notes": "Tanzanian newspaper",
        },
    ],
    "UG": [
        {
            "name": "Monitor Uganda",
            "url": "https://www.monitor.co.ug/feed/",
            "type": "commercial",
            "notes": "Ugandan newspaper",
        },
    ],
    "MA": [
        {
            "name": "Hespress",
            "url": "https://www.hespress.com/feed/",
            "type": "commercial",
            "notes": "Moroccan news (Arabic/French/English)",
        },
    ],
    "EG": [
        {
            "name": "Egypt Independent",
            "url": "https://www.egyptindependent.com/feed/",
            "type": "commercial",
            "notes": "Egyptian independent news",
        },
    ],
    "ET": [
        {
            "name": "Ethiopian News Agency",
            "url": "https://www.ena.et/rss/",
            "type": "broadcast",
            "notes": "Ethiopian government news",
        },
    ],
    "GH": [
        {
            "name": "Citinews Ghana",
            "url": "https://www.citinewsroom.com/feed/",
            "type": "broadcast",
            "notes": "Ghanaian broadcaster",
        },
    ],
    "SN": [
        {
            "name": "Seneweb",
            "url": "https://www.seneweb.com/rss/",
            "type": "commercial",
            "notes": "Senegalese news (French)",
        },
    ],

    # MIDDLE EAST
    "AE": [
        {
            "name": "The National UAE",
            "url": "https://www.thenational.ae/feed",
            "type": "commercial",
            "notes": "UAE English-language news",
        },
    ],
    "SA": [
        {
            "name": "Arab News",
            "url": "https://www.arabnews.com/feed/",
            "type": "commercial",
            "notes": "Saudi Arabia English news",
        },
    ],
    "JO": [
        {
            "name": "Jordan News",
            "url": "https://www.jordannews.jo/feed/",
            "type": "commercial",
            "notes": "Jordanian news",
        },
    ],
    "LB": [
        {
            "name": "The Daily Star Lebanon",
            "url": "https://www.dailystar.com.lb/feed/",
            "type": "commercial",
            "notes": "Lebanese English newspaper",
        },
    ],

    # SOUTH ASIA
    "IN": [
        {
            "name": "India Today",
            "url": "https://www.indiatoday.in/feed/",
            "type": "commercial",
            "notes": "Indian news magazine",
        },
    ],
    "PK": [
        {
            "name": "Dawn",
            "url": "https://www.dawn.com/feed",
            "type": "commercial",
            "notes": "Pakistani newspaper",
        },
    ],
    "BD": [
        {
            "name": "The Daily Star Bangladesh",
            "url": "https://www.thedailystar.net/feed/",
            "type": "commercial",
            "notes": "Bangladeshi newspaper",
        },
    ],
    "LK": [
        {
            "name": "Daily Mirror Sri Lanka",
            "url": "https://www.dailymirror.lk/feed/",
            "type": "commercial",
            "notes": "Sri Lankan newspaper",
        },
    ],
    "NP": [
        {
            "name": "The Kathmandu Post",
            "url": "https://kathmandupost.com/feed",
            "type": "commercial",
            "notes": "Nepalese newspaper",
        },
    ],

    # SOUTHEAST ASIA
    "SG": [
        {
            "name": "CNA (Channel NewsAsia)",
            "url": "https://www.channelnewsasia.com/rss/",
            "type": "broadcast",
            "notes": "Singapore broadcaster",
        },
    ],
    "MY": [
        {
            "name": "The Edge Malaysia",
            "url": "https://www.theedgemarkets.com/rss",
            "type": "commercial",
            "notes": "Malaysian business news",
        },
    ],
    "TH": [
        {
            "name": "Bangkok Post",
            "url": "https://www.bangkokpost.com/feed/",
            "type": "commercial",
            "notes": "Thai English newspaper",
        },
    ],
    "VN": [
        {
            "name": "Vietnam Breaking News",
            "url": "https://en.vietnamplus.vn/feed/",
            "type": "broadcast",
            "notes": "Vietnamese government news",
        },
    ],
    "PH": [
        {
            "name": "ABS-CBN News",
            "url": "https://www.abs-cbnnews.com/feed/",
            "type": "broadcast",
            "notes": "Philippines broadcaster",
        },
    ],
    "ID": [
        {
            "name": "Berita Satu",
            "url": "https://www.beritasatu.com/rss/",
            "type": "broadcast",
            "notes": "Indonesian broadcaster",
        },
    ],

    # EAST ASIA
    "CN": [
        {
            "name": "CGTN",
            "url": "https://www.cgtn.com/feed/",
            "type": "broadcast",
            "notes": "China state broadcaster",
        },
    ],
    "JP": [
        {
            "name": "NHK World",
            "url": "https://www3.nhk.or.jp/nhkworld/rss/news/atom.xml",
            "type": "broadcast",
            "notes": "Japanese public broadcaster",
        },
    ],
    "KR": [
        {
            "name": "KBS World",
            "url": "https://www.kbsworld.or.kr/feed/",
            "type": "broadcast",
            "notes": "Korean public broadcaster",
        },
    ],
    "TW": [
        {
            "name": "Focus Taiwan",
            "url": "https://focustaiwan.tw/feed/",
            "type": "wire",
            "notes": "Taiwan news agency",
        },
    ],
    "HK": [
        {
            "name": "RTHK (Hong Kong Public Broadcasting)",
            "url": "https://www.rthk.hk/rss/",
            "type": "broadcast",
            "notes": "Hong Kong public broadcaster",
        },
    ],

    # OCEANIA (alternatives)
    "AU": [
        {
            "name": "SBS News",
            "url": "https://www.sbs.com.au/news/feed",
            "type": "broadcast",
            "notes": "Australian multicultural broadcaster",
        },
    ],
    "NZ": [
        {
            "name": "Radio NZ",
            "url": "https://www.rnz.co.nz/feeds/news.rss",
            "type": "broadcast",
            "notes": "New Zealand public broadcaster",
        },
    ],
    "FJ": [
        {
            "name": "Fiji Broadcasting Commission",
            "url": "https://www.fbcnews.com.fj/feed/",
            "type": "broadcast",
            "notes": "Fijian broadcaster",
        },
    ],
    "DZ": [
        {
            "name": "Tsa-Algerie",
            "url": "https://www.tsa-algerie.com/feed/",
            "type": "unknown",
            "notes": "10 items",
        },
        {
            "name": "Tsa-Algerie",
            "url": "https://www.tsa-algerie.com/comments/feed/",
            "type": "unknown",
            "notes": "10 items",
        },
        {
            "name": "Tsa-Algerie",
            "url": "https://tsa-algerie.com/feed/",
            "type": "unknown",
            "notes": "10 items",
        },
        {
            "name": "Tsa-Algerie",
            "url": "https://tsa-algerie.com/rss/",
            "type": "unknown",
            "notes": "10 items",
        },
    ],
}


def validate_feed(url: str) -> dict:
    """
    Check if a feed URL is valid and returns proper RSS/Atom content.
    """
    if not HAS_REQUESTS:
        return {"valid": None, "reason": "Requests library not installed"}

    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return {"valid": False, "reason": f"HTTP {r.status_code}"}

        content = r.text.lower()
        if "rss" in content or "atom" in content or "feed" in content:
            return {"valid": True, "reason": "Valid feed detected", "size_bytes": len(r.text)}
        else:
            return {
                "valid": False,
                "reason": "Does not appear to be valid RSS/Atom feed",
            }
    except requests.Timeout:
        return {"valid": None, "reason": "Timeout (feed server may be slow)"}
    except Exception as e:
        return {"valid": None, "reason": f"Error: {type(e).__name__}"}


def report_candidates(candidates=None):
    """Generate a report of candidate sources by country."""
    if candidates is None:
        candidates = SOURCE_CANDIDATES
    print("\n[*] Candidate Free News Sources by Country")
    print("=" * 70)

    by_country = {}
    for country_code, cands in candidates.items():
        print(f"\n{country_code} - {len(cands)} candidate(s)")
        print("-" * 70)
        for cand in cands:
            print(f"  {cand['name']:<30} {cand['type']:<20}")
            print(f"    {cand['url']}")
            if cand.get("notes"):
                print(f"    > {cand['notes']}")

    # Summary
    total = sum(len(v) for v in candidates.values())
    print(f"\n{'=' * 70}")
    print(f"Total candidates: {total}")
    print(f"Countries covered: {len(candidates)}")


def validate_and_report(candidates=None):
    """Validate all candidates and show which are live."""
    if candidates is None:
        candidates = SOURCE_CANDIDATES
    print("\n[?] Validating Candidate Feeds")
    print("=" * 70)

    results = {"timestamp": None, "candidates": {}, "summary": {"valid": 0, "invalid": 0, "unknown": 0}}
    import datetime
    results["timestamp"] = datetime.datetime.now().isoformat()

    for cc, cands in candidates.items():
        print(f"\n{cc}")
        print("-" * 70)
        for cand in cands:
            val = validate_feed(cand["url"])
            status = (
                "."
                if val["valid"] is True
                else ("X" if val["valid"] is False else "!")
            )
            print(f"{status} {cand['name']:<30} {val['reason']}")

            cand["validation"] = val
            if val["valid"] is True:
                results["summary"]["valid"] += 1
            elif val["valid"] is False:
                results["summary"]["invalid"] += 1
            else:
                results["summary"]["unknown"] += 1

        results["candidates"][cc] = candidates

    print(f"\n{'=' * 70}")
    print(f"Summary: {results['summary']['valid']} valid · {results['summary']['invalid']} invalid · {results['summary']['unknown']} unknown")

    # Save
    json_path = Path("candidate_sources.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[S] Saved to {json_path}")


def export_as_addition(candidates=None) -> str:
    """Generate Python code to add validated candidates to feeds.py."""
    if candidates is None:
        candidates = SOURCE_CANDIDATES
    print("\n[+] Generating feeds.py additions for validated sources\n")

    additions = {}
    for cc, cands in candidates.items():
        valid = [c for c in cands if c.get("validation", {}).get("valid") is True]
        if valid:
            additions[cc] = valid

    if not additions:
        print("(No validated candidates yet. Run with --validate first.)")
        return

    print("Copy these into feeds.py:\n")
    for cc, valids in additions.items():
        print(f"# {cc} — additions")
        for v in valids:
            print(
                f'  ("{v["name"]:<25}", "{v["url"]}"),'
            )
        print()


def main():
    ap = argparse.ArgumentParser(
        description="Find and validate new free news sources for World River."
    )
    ap.add_argument(
        "--list", action="store_true", help="List all candidate sources"
    )
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Validate all feed URLs (requires requests library)",
    )
    ap.add_argument(
        "--export",
        action="store_true",
        help="Generate feeds.py code for validated sources",
    )
    ap.add_argument(
        "-c", "--country",
        type=str,
        help="Filter by country code (e.g., DK, SE, EG) — works with --list, --validate, --export"
    )
    ap.add_argument(
        "-x", "--continent",
        type=str,
        help="Filter by continent (e.g., Europe, Africa, Asia, Americas, Oceania, MiddleEast) — works with --list, --validate, --export"
    )
    args = ap.parse_args()

    # Build filter function
    def should_include(cc):
        if args.country:
            return cc.upper() == args.country.upper()
        if args.continent:
            continent_map = {
                "DK": "Europe", "SE": "Europe", "NO": "Europe", "LT": "Europe", "LV": "Europe", "EE": "Europe",
                "CZ": "Europe", "SK": "Europe", "HU": "Europe", "RO": "Europe", "BG": "Europe", "HR": "Europe", "SI": "Europe", "RS": "Europe",
                "GR": "Europe", "CY": "Europe", "MT": "Europe", "ES": "Europe", "PT": "Europe", "IT": "Europe", "FR": "Europe", "DE": "Europe", "NL": "Europe", "BE": "Europe", "AT": "Europe", "CH": "Europe", "PL": "Europe", "UA": "Europe", "RU": "Europe", "GB": "Europe", "IE": "Europe", "FI": "Europe",
                "IL": "MiddleEast", "IR": "MiddleEast", "SA": "MiddleEast", "AE": "MiddleEast", "JO": "MiddleEast", "LB": "MiddleEast", "MA": "MiddleEast", "EG": "MiddleEast",
                "IN": "Asia", "PK": "Asia", "BD": "Asia", "NP": "Asia", "LK": "Asia", "JP": "Asia", "KR": "Asia", "CN": "Asia", "TW": "Asia", "HK": "Asia", "SG": "Asia", "MY": "Asia", "VN": "Asia", "PH": "Asia", "TH": "Asia", "ID": "Asia",
                "NG": "Africa", "KE": "Africa", "GH": "Africa", "ZW": "Africa", "TZ": "Africa", "EG": "Africa", "ET": "Africa", "UG": "Africa", "SN": "Africa",
                "US": "Americas", "CA": "Americas", "MX": "Americas", "BR": "Americas", "AR": "Americas", "PE": "Americas", "VE": "Americas", "EC": "Americas",
                "AU": "Oceania", "NZ": "Oceania", "FJ": "Oceania",
            }
            return continent_map.get(cc, "Unknown") == args.continent
        return True

    if args.list:
        filtered = {cc: sources for cc, sources in SOURCE_CANDIDATES.items() if should_include(cc)}
        report_candidates(filtered)
    elif args.validate:
        filtered = {cc: sources for cc, sources in SOURCE_CANDIDATES.items() if should_include(cc)}
        validate_and_report(filtered)
    elif args.export:
        filtered = {cc: sources for cc, sources in SOURCE_CANDIDATES.items() if should_include(cc)}
        export_as_addition(filtered)
    else:
        # Default: show usage
        ap.print_help()


if __name__ == "__main__":
    main()
