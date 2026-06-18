"""English-language roster — DOMESTIC desks only, free to read, all probed live
2026-06-10. Flags are computed from the ISO-2 `cc` in build.py.

Rule: a source must report on ITS OWN country (national desk), not the world.
Outward-gazing international broadcasters and wire-mirrors are excluded.

Flagged (best-available, gaze imperfect): JP, EG, BR, KR.
"""

COUNTRIES = [
    # ---------- Oceania ----------
    {"cc": "AU", "name": "Australia", "sources": [
        ("ABC News",          "https://www.abc.net.au/news/feed/51120/rss.xml"),
        ("Guardian Australia","https://www.theguardian.com/australia-news/rss"),
    ]},
    {"cc": "NZ", "name": "New Zealand", "sources": [
        ("RNZ",               "https://www.rnz.co.nz/rss/national.xml"),
        ("Stuff",             "https://www.stuff.co.nz/rss"),
    ]},
    {"cc": "FJ", "name": "Fiji", "sources": [
        ("FBC News",          "https://www.fbcnews.com.fj/feed/"),
    ]},
    # ---------- Europe ----------
    {"cc": "GB", "name": "United Kingdom", "sources": [
        ("BBC UK",            "https://feeds.bbci.co.uk/news/uk/rss.xml"),
    ]},
    {"cc": "IE", "name": "Ireland", "sources": [
        ("TheJournal",        "https://www.thejournal.ie/feed/"),
    ]},
    {"cc": "FR", "name": "France", "sources": [
        ("RFI France",        "https://www.rfi.fr/en/france/rss"),
    ]},
    {"cc": "DE", "name": "Germany", "sources": [
        ("Deutsche Welle",    "https://rss.dw.com/rdf/rss-en-ger"),
    ]},
    {"cc": "NL", "name": "Netherlands", "sources": [
        ("DutchNews",         "https://www.dutchnews.nl/feed/"),
    ]},
    {"cc": "IT", "name": "Italy", "sources": [
        ("ANSA",              "https://www.ansa.it/english/english_rss.xml"),
    ]},
    {"cc": "PT", "name": "Portugal", "sources": [
        ("Portugal News",     "https://www.theportugalnews.com/rss"),
    ]},
    {"cc": "FI", "name": "Finland", "sources": [
        ("Yle News",          "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS"),
    ]},
    {"cc": "SE", "name": "Sweden", "sources": [
        ("The Local Sweden",  "https://www.thelocal.se/feeds/rss.php"),
    ]},
    {"cc": "DK", "name": "Denmark", "sources": [
        ("CPH Business",      "https://www.cphbusiness.dk/feed/"),
    ]},
    {"cc": "PL", "name": "Poland", "sources": [
        ("Notes from Poland", "https://notesfrompoland.com/feed/"),
    ]},
    {"cc": "HU", "name": "Hungary", "sources": [
        ("Hungary Today",     "https://hungarytoday.hu/feed/"),
    ]},
    {"cc": "UA", "name": "Ukraine", "sources": [
        ("The New Voice",     "https://english.nv.ua/rss/all.xml"),
        ("Ukrinform",         "https://www.ukrinform.net/rss/block-lastnews"),
    ]},
    {"cc": "RU", "name": "Russia", "sources": [
        ("The Moscow Times",  "https://www.themoscowtimes.com/rss/news"),
    ]},
    # ---------- Middle East ----------
    {"cc": "IL", "name": "Israel", "sources": [
        ("Times of Israel",   "https://www.timesofisrael.com/feed/"),
    ]},
    {"cc": "IR", "name": "Iran", "sources": [
        ("Tehran Times",      "https://www.tehrantimes.com/rss"),
    ]},
    {"cc": "EG", "name": "Egypt", "sources": [
        # FLAGGED: gaze imperfect (carries world headlines); only live free option.
        ("Egypt Independent", "https://www.egyptindependent.com/feed/"),
    ]},
    # ---------- Asia ----------
    {"cc": "IN", "name": "India", "sources": [
        ("The Hindu",         "https://www.thehindu.com/news/national/feeder/default.rss"),
        ("Times of India",    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"),
    ]},
    {"cc": "PK", "name": "Pakistan", "sources": [
        ("Dawn",              "https://www.dawn.com/feeds/home"),
    ]},
    {"cc": "BD", "name": "Bangladesh", "sources": [
        ("Bdnews24",          "https://bdnews24.com/feed.xml"),
    ]},
    {"cc": "NP", "name": "Nepal", "sources": [
        ("Kathmandu Post",    "https://kathmandupost.com/rss"),
    ]},
    {"cc": "JP", "name": "Japan", "sources": [
        # FLAGGED: best-available; blends some world news (no clean JP-domestic EN feed).
        ("Japan Times",       "https://www.japantimes.co.jp/feed/"),
    ]},
    {"cc": "KR", "name": "South Korea", "sources": [
        ("Yonhap",            "https://en.yna.co.kr/RSS/news.xml"),
    ]},
    {"cc": "CN", "name": "China", "sources": [
        ("CGTN",              "https://www.cgtn.com/subscribe/rss/section/china.xml"),
    ]},
    {"cc": "TW", "name": "Taiwan", "sources": [
        ("Taipei Times",      "https://www.taipeitimes.com/xml/index.rss"),
    ]},
    {"cc": "HK", "name": "Hong Kong", "sources": [
        ("HKFP",              "https://hongkongfp.com/feed/"),
    ]},
    {"cc": "SG", "name": "Singapore", "sources": [
        ("Channel News Asia", "https://www.channelnewsasia.com/rssfeeds/8396082"),
    ]},
    {"cc": "MY", "name": "Malaysia", "sources": [
        ("Malay Mail",        "https://www.malaymail.com/feed/rss/malaysia"),
    ]},
    {"cc": "VN", "name": "Vietnam", "sources": [
        ("VnExpress",         "https://e.vnexpress.net/rss/news.rss"),
    ]},
    {"cc": "PH", "name": "Philippines", "sources": [
        ("Inquirer",          "https://www.inquirer.net/feed/"),
        ("Rappler",           "https://www.rappler.com/feed/"),
    ]},
    # ---------- Africa ----------
    {"cc": "NG", "name": "Nigeria", "sources": [
        ("The Cable",         "https://www.thecable.ng/feed"),
    ]},
    {"cc": "KE", "name": "Kenya", "sources": [
        ("The Standard",      "https://www.standardmedia.co.ke/rss/headlines.php"),
    ]},
    {"cc": "GH", "name": "Ghana", "sources": [
        ("MyJoyOnline",       "https://www.myjoyonline.com/feed/"),
    ]},
    {"cc": "ZW", "name": "Zimbabwe", "sources": [
        ("NewZimbabwe",       "https://www.newzimbabwe.com/feed/"),
    ]},
    # ---------- Americas ----------
    {"cc": "US", "name": "United States", "sources": [
        ("NPR",               "https://feeds.npr.org/1003/rss.xml"),
    ]},
    {"cc": "CA", "name": "Canada", "sources": [
        ("CBC News",          "https://www.cbc.ca/webfeed/rss/rss-topstories.xml"),
    ]},
    {"cc": "MX", "name": "Mexico", "sources": [
        ("Mexico News Daily", "https://mexiconewsdaily.com/feed/"),
    ]},
    {"cc": "BR", "name": "Brazil", "sources": [
        # FLAGGED: investor/regional gaze; only live free EN option.
        ("Rio Times",         "https://www.riotimesonline.com/feed/"),
    ]},
    {"cc": "AR", "name": "Argentina", "sources": [
        ("Buenos Aires Times","https://www.batimes.com.ar/feed"),
    ]},
    {"cc": "DZ", "name": "Algeria", "sources": [
        ("TSA",                "https://www.tsa-algerie.com/feed/"),
    ]},
]


def flag(cc):
    """ISO-2 country code -> regional-indicator flag emoji."""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in cc.upper())


# Continent grouping for the selection tree (order = display order).
REGIONS = {
    "Europe":      ["GB", "IE", "FR", "DE", "NL", "IT", "PT", "FI", "SE", "DK", "PL", "HU", "UA", "RU"],
    "Asia":        ["IN", "PK", "BD", "NP", "JP", "KR", "CN", "TW", "HK", "SG", "MY", "VN", "PH"],
    "Middle East": ["IL", "IR", "EG"],
    "Africa":      ["NG", "KE", "GH", "ZW"],
    "Americas":    ["US", "CA", "MX", "BR", "AR"],
    "Oceania":     ["AU", "NZ", "FJ"],
}
REGION_OF = {cc: r for r, ccs in REGIONS.items() for cc in ccs}
