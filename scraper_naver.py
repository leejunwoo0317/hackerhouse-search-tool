import time
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright


def extract_listings(page, search_label=""):
    cards = page.query_selector_all("a.item_link")
    current_url = page.url
    listings = []

    for card in cards:
        try:
            title_el = card.query_selector("div.item_title span.text")
            title = title_el.inner_text().strip() if title_el else ""

            price_type_el = card.query_selector("div.price_line span.type")
            price_type = price_type_el.inner_text().strip() if price_type_el else ""

            price_el = card.query_selector("div.price_line span.price")
            price_val = price_el.inner_text().strip() if price_el else ""
            price_full = f"{price_type}{price_val}"

            prop_type_el = card.query_selector("div.info_area strong.type")
            property_type = prop_type_el.inner_text().strip() if prop_type_el else ""

            spec_els = card.query_selector_all("div.info_area p.line span.spec")
            spec = spec_els[0].inner_text().strip() if spec_els else ""
            description = spec_els[1].inner_text().strip() if len(spec_els) > 1 else ""

            # parse size and floor from spec e.g. "189A/153m², 중/25층, 남서향"
            size, floor = "", ""
            for part in spec.split(","):
                part = part.strip()
                if ("m²" in part or "m2" in part or "㎡" in part) and not size:
                    size = part.split("/")[-1].strip() if "/" in part else part
                elif "층" in part and not floor:
                    floor = part.strip()

            # parse deposit and monthly rent
            # Naver format: price_val = "3억/360" or "10억/100"
            deposit, monthly = "", ""
            if "/" in price_val and price_type in ["월세", "단기임대"]:
                parts = price_val.split("/")
                if len(parts) == 2:
                    deposit = parts[0].strip()
                    monthly = parts[1].strip() + "만원"

            listings.append({
                "search_label": search_label,
                "source": "naver",
                "property_type": property_type,
                "price": price_full,
                "deposit": deposit,
                "monthly_rent": monthly,
                "address": title,
                "floor": floor,
                "size": size,
                "description": description,
                "photo": "",
                "link": current_url,
            })
        except Exception as e:
            print(f"Error extracting card: {e}")
            continue

    return listings


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.goto("https://new.land.naver.com", wait_until="domcontentloaded")

        print("\n" + "="*55)
        print("Naver Land is open.")
        print("Steps each round:")
        print("  1. Search for an area")
        print("  2. Click a building on the map")
        print("  3. Wait for listings to appear in the left panel")
        print("  4. Come back here and type a label + press Enter")
        print("  Type 'q' to finish.")
        print("="*55)

        all_listings = []

        while True:
            command = input("\nType a label (e.g. 성수동 A단지)  |  or 'q' to finish: ").strip()
            if command.lower() == "q":
                break

            search_label = command
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)

            new_listings = extract_listings(page, search_label=search_label)
            all_listings.extend(new_listings)

            print(f"\nExtracted {len(new_listings)} listings from '{search_label}'  |  Total: {len(all_listings)}")
            for i, l in enumerate(new_listings, 1):
                print(f"  [{i}] [{l['property_type']}] {l['price']} | {l['address']} | {l['floor']} | {l['size']}")

            print("\nClick another building or search a new area, then enter the next label.")

        context.close()
        browser.close()

        # deduplicate by address + price combination (no article ID available)
        seen = set()
        unique = []
        duplicate_count = 0
        for l in all_listings:
            key = f"{l['address']}_{l['price']}"
            if key not in seen:
                seen.add(key)
                unique.append(l)
            else:
                duplicate_count += 1

        print(f"\nDone.")
        print(f"  Total collected   : {len(all_listings)}")
        print(f"  Duplicates removed: {duplicate_count}")
        print(f"  Unique listings   : {len(unique)}")

        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        fields = ["search_label", "source", "property_type", "price", "deposit",
                  "monthly_rent", "address", "floor", "size", "description", "link", "photo"]
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(unique)

        print(f"\nSaved to: {filename}")
        return unique


if __name__ == "__main__":
    run()
