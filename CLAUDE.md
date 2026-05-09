# Hackerhouse Search Tool — Claude Context

## What This Project Does
A semi-manual real estate scraping tool for finding hackerhouses in Korea.
Playwright opens a real browser, the user searches manually, then the code extracts listings and saves a CSV.
A Streamlit web app reads the CSV and shows a filtered, sortable, comparable card view.

## Live App
https://leejunwoo0317-hackerhouse-search-tool.streamlit.app

## Key Files
- `scraper_peterpan.py` — scraper for peterpanz.com (primary source, 빌라/아파트/원룸)
- `scraper_naver.py` — scraper for new.land.naver.com (secondary, 아파트 위주)
- `app.py` — Streamlit UI (filters, comparison, sorting)
- `requirements.txt` — cloud deployment only: `streamlit`, `pandas` (no playwright)

## How to Run Locally
```
python scraper_peterpan.py   # opens browser, type label per search, 'q' to finish
python scraper_naver.py      # same pattern — click building on map first
python -m streamlit run app.py
```

## Data Format
CSV columns: `search_label, source, property_type, price, deposit, monthly_rent, address, floor, size, description, link, photo`
- `source`: `"peterpan"` or `"naver"`
- Peter Pan deposit/monthly: stored as 만원 e.g. `"3,000만원"`, `"130만원"`
- Naver deposit: stored as 억 e.g. `"3억"` — `parse_amount()` converts 억 to 만원

## Key Technical Decisions
- Semi-manual scraping (not automated) to stay compliant with ToS
- Naver has no per-unit article URL — listings use the building search page URL as link
- Deduplication: Peter Pan by `link`, Naver by `address + price`
- Compare checkbox key = `link|address|price` to avoid collisions on shared Naver URLs
- `results_*.csv` is gitignored — never commit scraped data

## Known Limitations
- Naver listing links go to the building page, not the individual unit
- Naver has no photo in list view
- Deposit range filter label says "(만원)" — Naver deposits are in 억 (1억 = 10,000만원)

## Compliance
- Peter Pan: robots.txt fully open ✓
- Naver: robots.txt restricts bots — semi-manual only, personal use only
- Zigbang: explicitly prohibited — not used
