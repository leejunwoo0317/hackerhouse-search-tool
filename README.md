# hackerhouse-search-tool
hackerhouse-search-tool
#  hackerhouse-search-tool
semi-maual-data-listing-tool
 # 🏠 Hackerhouse Search Tool

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

  ## Tech Stack

  | Layer | Tool | Why |
  |---|---|---|
  | Language | Python | Beginner-friendly, best scraping ecosystem |
  | UI | Streamlit | Write Python, get a web UI — no HTML needed |
  | Scraping | Playwright | Handles JavaScript-heavy sites like Naver |
  | Deployment | Streamlit Cloud | Free, one-click deploy from GitHub |

  ---

  ## Target Sites

  | Priority | Site | robots.txt | Status |
  |---|---|---|---|
  | Primary | [Peter Pan](https://www.peterpanz.com) | Fully open | Active |
  | Secondary | [Naver 부동산](https://land.naver.com) | Careful use | Active |
  | Excluded | Zigbang | Explicitly prohibited | Not used |

  ---

  ## Scraping Method: Semi-Manual

  This tool uses a **semi-manual** approach:

  1. Your code opens a real visible Chrome browser
  2. **You** navigate and search manually (district, price range, etc.)
  3. You press Enter in the terminal when results are loaded
  4. **The code** automatically extracts all listing data
  5. Results appear in the Streamlit UI

  This keeps the tool compliant — it looks like a real user, not a bot.

  ---

  ## Data Extracted Per Listing

  - Monthly rent (월세)
  - Deposit (보증금)
  - Size (sqm / 평)
  - Address / district
  - Floor
  - Photo
  - Link to original listing

  ---

  ## Roadmap

  - [ ] **Phase 0** — Environment setup (Python, Streamlit, Playwright, GitHub)
  - [ ] **Phase 1** — Peter Pan scraper (semi-manual, extracts 7 fields)
  - [ ] **Phase 2** — Streamlit UI (table view, photos, sidebar checklist)
  - [ ] **Phase 3** — Side-by-side comparison view
  - [ ] **Phase 4** — Add Naver 부동산 as second source
  - [ ] **Phase 5** — Polish (sorting, filtering, error handling)
  - [ ] **Phase 6** — Deploy to Streamlit Cloud

  ---

  ## Getting Started

  ### Prerequisites

  - Python 3.11+
  - Git

  ### Installation

  ```bash
  # Clone the repo
  git clone https://github.com/YOUR-USERNAME/hackerhouse-search.git
  cd hackerhouse-search

  # Install dependencies
  pip install streamlit playwright pandas

  # Install Playwright browser
  playwright install chromium

  Run the app

  streamlit run app.py

  The app opens at http://localhost:8501 in your browser.

  ---
  Project Structure

  hackerhouse-search/
  ├── app.py                  # Streamlit UI
  ├── scraper_peterpan.py     # Peter Pan scraper
  ├── scraper_naver.py        # Naver 부동산 scraper
  ├── requirements.txt        # Python dependencies
  └── README.md

  ---
  Compliance Notes

  - Peter Pan — robots.txt fully open, sitemap provided. Low risk.
  - Naver 부동산 — robots.txt restricts crawlers. Used carefully:
    - Semi-manual only (no automated mass scraping)
    - Low frequency (personal use, occasional searches)
    - No data reselling
  - Zigbang — explicitly prohibited. Not used.

  ---
  Built By leejunwoo

  Solo project — personal tool for hackerhouse hunting in Korea.
  Built as a learning project (started coding 1 month ago).

  Stack decisions, compliance research, and roadmap documented through
  conversation with Claude Code.
