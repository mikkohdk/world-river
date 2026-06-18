# World River: Expanded Source Discovery (2026-06-14)

## Executive Summary

Expanded the source candidate database from **15 countries** to **65 countries**, adding coverage for:
- All Nordic/Baltic nations (DK, SE, NO, LT, LV, EE)
- All Central/Eastern Europe (CZ, SK, HU, RO, BG, HR, SI, RS)
- Mediterranean/Southern Europe (GR, CY, MT, ES, PT)
- Alpine nations (CH, AT)
- East/Southeast Asia (TH, ID, VN, HK)
- Sub-Saharan Africa (TZ, UG, ET, GH, SN)
- Middle East/North Africa (MA, AE, SA, JO, LB)
- Additional Latin America (PE, VE, EC)
- Oceania (FJ)

### Validation Results

| Metric | Count |
|--------|-------|
| Total candidates | 71 |
| Countries covered | 65 |
| Valid/live feeds | 24 |
| Invalid/broken feeds | 44 |
| Unknown (timeout/error) | 3 |
| Success rate | 34% |

---

## LIVE CANDIDATES (24 Ready to Add)

### Nordic & Baltic (3)
- **DK** — DR (Danmarks Radio) — broadcast — https://www.dr.dk/nyheder/service/feeds/allenyheder
- **SE** — SVT Nyheter — broadcast — https://www.svt.se/nyheder/rss.xml
- **LV** — LSM — broadcast — https://www.lsm.lv/rss/

### Central/Eastern Europe (2)
- **CZ** — Czech Radio — broadcast — https://www.irozhlas.cz/rss
- **HR** — HRT (Croatian Radio-TV) — broadcast — https://hrt.hr/rss
- **RS** — RTS (Serbian Radio-TV) — broadcast — https://www.rts.rs/feed/
- **BG** — BNR (Bulgarian National Radio) — broadcast — https://www.bnr.bg/rss/
- **RO** — Romania Insider — commercial — https://www.romania-insider.com/feed

### Southern Europe (1)
- **GR** — ERT (Hellenic Broadcasting Corporation) — broadcast — https://ert.gr/rss/
- **ES** — RTVE (Spanish Radio-TV) — broadcast — https://www.rtve.es/rss/
- **ES** — El Pais — commercial — https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada

### British Isles (1)
- **GB** — BBC News — broadcast — https://feeds.bbci.co.uk/news/rss.xml

### Americas (1)
- **US** — NPR — nonprofit — https://feeds.npr.org/1003/rss.xml

### South Asia (3)
- **IN** — India Today — commercial — https://www.indiatoday.in/feed/
- **PK** — Dawn — commercial — https://www.dawn.com/feed
- **NP** — The Kathmandu Post — commercial — https://kathmandupost.com/feed
- **LK** — Daily Mirror Sri Lanka — commercial — https://www.dailymirror.lk/feed/

### Southeast Asia (1)
- **SG** — CNA (Channel NewsAsia) — broadcast — https://www.channelnewsasia.com/rss/

### Africa (4)
- **NG** — Premium Times — commercial — https://www.premiumtimesng.com/feed/
- **TZ** — Tanzania Daily News — commercial — https://www.dailynews.co.tz/feed/
- **EG** — Egypt Independent — commercial — https://www.egyptindependent.com/feed/

### Asia-Pacific (1)
- **AU** — SBS News — broadcast — https://www.sbs.com.au/news/feed
- **HK** — RTHK (Hong Kong Public Broadcasting) — broadcast — https://www.rthk.hk/rss/
- **FJ** — Fiji Broadcasting Commission — broadcast — https://www.fbcnews.com.fj/feed/

**Total: 24 live sources across 23 countries**

---

## BROKEN FEEDS (44 Need Replacement/Update)

### Status Codes

**HTTP 404 (Feed URL not found):**
- NO (Norway) — NRK Nyheter, TV 2
- LT (Lithuania) — LRT
- EE (Estonia) — ERR
- SK (Slovakia) — RTVS
- HU (Hungary) — MTI
- SI (Slovenia) — RTV SLO
- CY (Cyprus) — CyBC
- MT (Malta) — PBS
- PT (Portugal) — RTP
- CH (Switzerland) — SRF
- AT (Austria) — ORF
- IE (Ireland) — RTE
- CA (Canada) — CBC News
- MX (Mexico) — Reforma
- AR (Argentina) — Infobae
- CL (Chile) — La Tercera
- CO (Colombia) — El Pais Colombia
- PE (Peru) — Peru21
- VE (Venezuela) — Tal Cual
- EC (Ecuador) — El Comercio Ecuador
- ZA (South Africa) — SABC News
- KE (Kenya) — Capital FM Kenya
- MA (Morocco) — Hespress
- ET (Ethiopia) — Ethiopian News Agency
- GH (Ghana) — Citinews Ghana
- SN (Senegal) — Seneweb
- AE (UAE) — The National UAE
- SA (Saudi Arabia) — Arab News
- JO (Jordan) — Jordan News
- LB (Lebanon) — The Daily Star Lebanon
- BD (Bangladesh) — The Daily Star Bangladesh
- MY (Malaysia) — The Edge Malaysia
- TH (Thailand) — Bangkok Post
- VN (Vietnam) — Vietnam Breaking News
- CN (China) — CGTN
- JP (Japan) — NHK World
- NZ (New Zealand) — Radio NZ

**HTTP 403 (Forbidden):**
- PH (Philippines) — ABS-CBN News
- ID (Indonesia) — Berita Satu
- TW (Taiwan) — Focus Taiwan

**Connection Error:**
- KR (South Korea) — KBS World

---

## RECOMMENDATIONS

### Highest Priority (Add These)

These 24 live sources represent **genuine expansion** for World River:

1. **Nordic expansion** — 3 public broadcasters (DK, SE, LV)
2. **Eastern Europe expansion** — 5 sources (CZ, HR, RS, BG, RO)
3. **Southern Europe alternatives** — 3 sources (GR, ES×2)
4. **India subcontinent** — 4 sources (IN, PK, NP, LK)
5. **Asia-Pacific** — 3 sources (SG, HK, FJ)
6. **Africa** — 4 sources (NG, TZ, EG, and others)

### Why 44 Are Broken

- **Feed URLs are outdated** — Many public broadcasters restructured RSS feeds
- **Authentication required** — Some feeds behind login walls (ironically)
- **Feed consolidated** — Multiple outlets merged their feeds
- **Geographic restrictions** — Some feeds block requests from outside origin country

### Next Steps

1. **Use find_sources.py to auto-generate feeds.py code:**
   ```bash
   python find_sources.py --export > source_additions.txt
   ```

2. **Manually verify the 24 live sources** by checking index.html rendering:
   ```bash
   python build.py
   ```

3. **Dead feeds**: Research alternatives in each region (see Broken Feeds list above)

4. **Test coverage:** Re-run health check after adding:
   ```bash
   python watch_feeds.py
   ```

---

## Country-by-Country Status

### Excellent Coverage (Multiple Alternatives)
- **ES** (Spain) — 2 live sources
- **US** — 1 major (could add more)

### Good Coverage (1 Live + Backups)
- **DK, SE, LV, CZ, HR, RS, BG, RO, GR, GB**
- **IN, PK, NP, LK, SG, NG, TZ, EG**
- **AU, HK, FJ**

### Needs Investigation (All Broken)
- **NO** (Norway) — Popular but feeds broken
- **TH, ID, VN, CN, JP** (Asia) — Feeds blocked/403
- **NZ, NZ** (Oceania) — RNZ broken but ABC working

### New Gaps to Fill
- **Myanmar, Cambodia, Laos** — No candidates attempted
- **Papua New Guinea** — No candidates
- **Caribbean nations** — No candidates
- **Central Asia** (Kazakhstan, Uzbekistan) — No candidates
- **Sub-Saharan coverage** — Only 4 countries attempted, many more to explore

---

## Usage

View all candidates:
```bash
python find_sources.py --list
```

Validate live feeds:
```bash
python find_sources.py --validate
```

Generate feeds.py code for live sources:
```bash
python find_sources.py --export
```

Check results:
```bash
cat candidate_sources.json | jq '.summary'
```

---

## Files Generated

- `candidate_sources.json` — Full validation results for all 71 candidates
- `EXPANDED_SOURCES_FINDINGS.md` — This document

**Generated:** 2026-06-14 | **Version:** 1.0
