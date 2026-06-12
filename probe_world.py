"""Wide candidate sweep: domestic English-language feeds across every region.
Reports liveness + item count + 3 sample headlines (to judge GAZE = is it about
its own country?). Concurrent so ~70 sources finish fast. Survivors get folded
into feeds.py after a paywall/article check.
"""
import sys, requests, feedparser
from concurrent.futures import ThreadPoolExecutor
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# (region, CC, country, source, url)
CAND = [
 # ---- EUROPE ----
 ("EU","IE","Ireland","TheJournal","https://www.thejournal.ie/feed/"),
 ("EU","IE","Ireland","RTE News","https://www.rte.ie/feeds/rss/?index=/news/"),
 ("EU","ES","Spain","El Pais EN","https://english.elpais.com/rss/feed.html?feedId=1022"),
 ("EU","IT","Italy","ANSA EN","https://www.ansa.it/english/english_rss.xml"),
 ("EU","NL","Netherlands","DutchNews","https://www.dutchnews.nl/feed/"),
 ("EU","NL","Netherlands","NL Times","https://nltimes.nl/rss.xml"),
 ("EU","FI","Finland","Yle News","https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS"),
 ("EU","SE","Sweden","Local Sweden","https://www.thelocal.se/feeds/rss.php"),
 ("EU","NO","Norway","Norway Today","https://norwaytoday.info/feed/"),
 ("EU","DK","Denmark","CPH Post","https://cphpost.dk/feed/"),
 ("EU","PL","Poland","Notes from PL","https://notesfrompoland.com/feed/"),
 ("EU","GR","Greece","Ekathimerini","https://www.ekathimerini.com/feed/"),
 ("EU","CH","Switzerland","SwissInfo","https://www.swissinfo.ch/eng/feed/"),
 ("EU","PT","Portugal","Portugal News","https://www.theportugalnews.com/rss"),
 ("EU","RO","Romania","Romania Insider","https://www.romania-insider.com/rss.xml"),
 ("EU","BE","Belgium","Brussels Times","https://www.brusselstimes.com/feed"),
 ("EU","HU","Hungary","Daily News HU","https://dailynewshungary.com/feed/"),
 ("EU","CZ","Czechia","Expats.cz","https://www.expats.cz/rss"),
 ("EU","RU","Russia","Moscow Times","https://www.themoscowtimes.com/rss/news"),
 ("EU","RU","Russia","TASS EN","https://tass.com/rss/v2.xml"),
 # ---- MIDDLE EAST ----
 ("ME","IL","Israel","Times of Israel","https://www.timesofisrael.com/feed/"),
 ("ME","IL","Israel","Jerusalem Post","https://www.jpost.com/rss/rssfeedsfrontpage.aspx"),
 ("ME","IR","Iran","Tehran Times","https://www.tehrantimes.com/rss"),
 ("ME","SA","Saudi Arabia","Arab News","https://www.arabnews.com/rss.xml"),
 ("ME","AE","UAE","Khaleej Times","https://www.khaleejtimes.com/rss"),
 ("ME","LB","Lebanon","Naharnet","https://www.naharnet.com/rss/news"),
 ("ME","JO","Jordan","Jordan Times","https://jordantimes.com/rss.xml"),
 ("ME","EG","Egypt","Egypt Indep.","https://www.egyptindependent.com/feed/"),
 ("ME","EG","Egypt","Ahram Online","https://english.ahram.org.eg/rss/1.aspx"),
 # ---- ASIA ----
 ("AS","CN","China","China Daily","https://www.chinadaily.com.cn/rss/china_rss.xml"),
 ("AS","CN","China","Global Times","https://www.globaltimes.cn/rss/china.xml"),
 ("AS","KR","South Korea","Korea Herald","https://www.koreaherald.com/rss/newsList/000000000001.xml"),
 ("AS","KR","South Korea","Korea Times","https://www.koreatimes.co.kr/www/rss/nation.xml"),
 ("AS","ID","Indonesia","Jakarta Post","https://www.thejakartapost.com/feed"),
 ("AS","ID","Indonesia","Jakarta Globe","https://jakartaglobe.id/feed"),
 ("AS","PH","Philippines","Inquirer","https://www.inquirer.net/feed/"),
 ("AS","PH","Philippines","Rappler","https://www.rappler.com/feed/"),
 ("AS","MY","Malaysia","Malay Mail","https://www.malaymail.com/feed/rss/malaysia"),
 ("AS","TH","Thailand","Nation Thailand","https://www.nationthailand.com/rss"),
 ("AS","VN","Vietnam","VnExpress","https://e.vnexpress.net/rss/news.rss"),
 ("AS","PK","Pakistan","Dawn","https://www.dawn.com/feeds/home"),
 ("AS","PK","Pakistan","Express Tribune","https://tribune.com.pk/feed/home"),
 ("AS","BD","Bangladesh","Daily Star","https://www.thedailystar.net/rss.xml"),
 ("AS","NP","Nepal","Kathmandu Post","https://kathmandupost.com/rss"),
 ("AS","TW","Taiwan","Taipei Times","https://www.taipeitimes.com/xml/index.rss"),
 ("AS","TW","Taiwan","Focus Taiwan","https://focustaiwan.tw/rss/onlinenews.xml"),
 ("AS","HK","Hong Kong","HKFP","https://hongkongfp.com/feed/"),
 ("AS","LK","Sri Lanka","Daily Mirror","https://www.dailymirror.lk/RSS_Feeds/breaking-news"),
 # ---- OCEANIA ----
 ("OC","NZ","New Zealand","RNZ","https://www.rnz.co.nz/rss/national.xml"),
 ("OC","NZ","New Zealand","Stuff","https://www.stuff.co.nz/rss"),
 ("OC","FJ","Fiji","FBC News","https://www.fbcnews.com.fj/feed/"),
 # ---- AFRICA ----
 ("AF","ZA","South Africa","Daily Maverick","https://www.dailymaverick.co.za/feed/"),
 ("AF","ZA","South Africa","Mail & Guardian","https://mg.co.za/feed/"),
 ("AF","NG","Nigeria","Premium Times","https://www.premiumtimesng.com/feed"),
 ("AF","NG","Nigeria","Punch","https://punchng.com/feed/"),
 ("AF","KE","Kenya","Standard","https://www.standardmedia.co.ke/rss/headlines.php"),
 ("AF","KE","Kenya","The Star KE","https://www.the-star.co.ke/rss/"),
 ("AF","GH","Ghana","MyJoyOnline","https://www.myjoyonline.com/feed/"),
 ("AF","ET","Ethiopia","Addis Standard","https://addisstandard.com/feed/"),
 ("AF","UG","Uganda","Daily Monitor","https://www.monitor.co.ug/uganda/rss"),
 ("AF","TZ","Tanzania","The Citizen","https://www.thecitizen.co.tz/tanzania/rss"),
 ("AF","ZW","Zimbabwe","The Herald","https://www.herald.co.zw/feed/"),
 ("AF","MA","Morocco","Morocco WN","https://www.moroccoworldnews.com/feed"),
 ("AF","RW","Rwanda","The New Times","https://www.newtimes.co.rw/rss"),
 # ---- AMERICAS ----
 ("AM","US","United States","NPR National","https://feeds.npr.org/1003/rss.xml"),
 ("AM","CA","Canada","CBC Canada","https://www.cbc.ca/webfeed/rss/rss-canada"),
 ("AM","CA","Canada","Global News","https://globalnews.ca/feed/"),
 ("AM","MX","Mexico","Mexico News Daily","https://mexiconewsdaily.com/feed/"),
 ("AM","BR","Brazil","Rio Times","https://www.riotimesonline.com/feed/"),
 ("AM","AR","Argentina","BA Times","https://www.batimes.com.ar/feed"),
]

def probe(item):
    region, cc, country, source, url = item
    out = {"region":region,"cc":cc,"country":country,"source":source,"url":url}
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=12)
        out["status"] = r.status_code
        d = feedparser.parse(r.content)
        out["items"] = len(d.entries)
        out["samples"] = [(e.get("title","") or "")[:68] for e in d.entries[:3]]
    except Exception as e:
        out["status"] = "ERR"; out["items"] = 0
        out["samples"] = [f"{type(e).__name__}: {str(e)[:40]}"]
    return out

def main():
    with ThreadPoolExecutor(max_workers=14) as ex:
        results = list(ex.map(probe, CAND))
    order = ["EU","ME","AS","OC","AF","AM"]
    results.sort(key=lambda r:(order.index(r["region"]), r["cc"]))
    cur = None
    live = 0
    for r in results:
        if r["region"] != cur:
            cur = r["region"]; print(f"\n===== {cur} =====")
        ok = (r["status"] == 200 and r["items"] > 0)
        live += ok
        mark = "OK" if ok else "--"
        print(f"{mark} {r['cc']} {r['source']:<18} [{r['status']}, n={r['items']}]")
        if ok:
            for s in r["samples"]:
                print(f"       • {s}")
        else:
            print(f"       ! {r['samples'][0] if r['samples'] else ''}")
    print(f"\n{live}/{len(results)} candidate feeds live with items.")

if __name__ == "__main__":
    main()
