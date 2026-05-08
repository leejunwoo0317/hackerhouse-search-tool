
# Hackerhouse Search Tool

A personal search tool for finding hackerhouse locations in Korea.
It opens a real browser window, lets you search manually on Korean real estate sites,
then automatically extracts and displays listings in a clean overview page.

---

## Why I Built This

Finding a hackerhouse in Korea requires checking multiple sites manually and
comparing listings one by one. This tool automates the boring extraction part
while keeping the human in control of the search — a semi-manual approach
that respects each site's terms of service.

---

## Live App

Deployed on Streamlit Cloud: [hackerhouse-search-tool.streamlit.app](https://hackerhouse-search-tool.streamlit.app)

Upload a CSV exported from the scraper to browse and compare listings.

---

## Tech Stack

| Layer | Tool | Why |
| --- | --- | --- |
| Language | Python | Beginner-friendly, best scraping ecosystem |
| UI | Streamlit | Write Python, get a web UI — no HTML needed |
| Scraping | Playwright | Handles JavaScript-heavy sites like Naver |
| Deployment | Streamlit Cloud | Free, one-click deploy from GitHub |

---

## Target Sites

| Priority | Site | robots.txt | Status |
| --- | --- | --- | --- |
| Primary | [Peter Pan](https://www.peterpanz.com) | Fully open | Active |
| Secondary | [Naver 부동산](https://new.land.naver.com) | Careful use | Active |
| Excluded | Zigbang | Explicitly prohibited | Not used |

---

## Scraping Method: Semi-Manual

This tool uses a **semi-manual** approach:

1. Your code opens a real visible Chrome browser
2. **You** navigate and search manually (district, price range, etc.)
3. You type a label in the terminal when results are loaded
4. **The code** automatically extracts all listing data
5. Results are saved to a CSV file
6. Upload the CSV to the Streamlit app to browse and compare

This keeps the tool compliant — it looks like a real user, not a bot.

---

## Data Extracted Per Listing

| Field | Description |
| --- | --- |
| source | Platform (peterpan / naver) |
| property_type | 아파트, 빌라/주택, etc. |
| price | Full price string (e.g. 월세 3,000/130) |
| deposit | Deposit amount |
| monthly_rent | Monthly rent amount |
| address | Building name / address |
| floor | Floor |
| size | Size in m² |
| description | Short description |
| link | Link to the listing |
| photo | Thumbnail image (Peter Pan only) |

---

## Roadmap

- [x] **Phase 0** — Environment setup (Python, Streamlit, Playwright, GitHub)
- [x] **Phase 1** — Peter Pan scraper (semi-manual, extracts listing data)
- [x] **Phase 2** — Streamlit UI (card view, photos, sidebar filters)
- [x] **Phase 3** — Side-by-side comparison view
- [x] **Phase 4** — Add Naver 부동산 as second source
- [x] **Phase 5** — Polish (sorting, filtering, multi-source merge, error handling)
- [x] **Phase 6** — Deploy to Streamlit Cloud

---

## Getting Started (Local)

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
git clone https://github.com/leejunwoo0317/hackerhouse-search-tool
cd hackerhouse-search-tool

pip install streamlit pandas playwright
playwright install chromium
```

### Run the scraper

```bash
# Peter Pan
python scraper_peterpan.py

# Naver 부동산
python scraper_naver.py
```

### View results in the UI

```bash
python -m streamlit run app.py
```

---

## Project Structure

```
hackerhouse-search-tool/
├── app.py                  # Streamlit UI
├── scraper_peterpan.py     # Peter Pan scraper
├── scraper_naver.py        # Naver 부동산 scraper
├── requirements.txt        # Python dependencies (cloud deployment)
└── README.md
```

---

## Compliance Notes

- **Peter Pan** — robots.txt fully open, sitemap provided. Low risk.
- **Naver 부동산** — robots.txt restricts crawlers. Used carefully:
  - Semi-manual only (no automated mass scraping)
  - Low frequency (personal use, occasional searches)
  - No data reselling
- **Zigbang** — explicitly prohibited. Not used.

---

## Built By leejunwoo

Solo project — personal tool for hackerhouse hunting in Korea.
Built as a learning project (started coding 1 month ago).
