import time
from playwright.sync_api import sync_playwright


def extract_listings(page):
    cards = page.query_selector_all("div.a-house")
    listings = []

    for card in cards:
        try:
            hidx = card.get_attribute("data-hidx") or ""
            link = f"https://www.peterpanz.com/house/{hidx}" if hidx else ""

            price_el = card.query_selector("div.m-content__price")
            price = price_el.inner_text().strip() if price_el else ""

            address_el = card.query_selector("div.m-content__address")
            address = address_el.inner_text().strip() if address_el else ""

            photo_el = card.query_selector("img.slider-image")
            photo = photo_el.get_attribute("src") if photo_el else ""

            desc_el = card.query_selector("div.m-content__description")
            description = desc_el.inner_text().strip() if desc_el else ""

            # floor and size are inside multiple div.m-content__text elements
            info_texts = card.query_selector_all("div.m-content__text")
            floor, size, building_type = "", "", ""
            for el in info_texts:
                text = el.inner_text().strip()
                if "층" in text:
                    floor = text
                elif "m²" in text or "m2" in text or "㎡" in text:
                    size = text
                elif text and not building_type:
                    building_type = text

            # parse deposit and monthly rent from price string
            # format: "월세 보증금/월세" e.g. "월세 1,000/48"
            deposit, monthly = "", ""
            if "월세" in price and "/" in price:
                parts = price.replace("월세", "").strip().split("/")
                if len(parts) == 2:
                    deposit = parts[0].strip() + "만원"
                    monthly = parts[1].strip() + "만원"

            listings.append({
                "price": price,
                "deposit": deposit,
                "monthly_rent": monthly,
                "address": address,
                "floor": floor,
                "size": size,
                "building_type": building_type,
                "description": description,
                "photo": photo,
                "link": link,
            })
        except Exception as e:
            print(f"Error extracting card: {e}")
            continue

    return listings


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.peterpanz.com/villa", wait_until="domcontentloaded")

        print("\n" + "="*50)
        print("Peter Pan is open in your browser.")
        print("Search for your desired area and filters.")
        print("When the listings are loaded, come back here.")
        print("="*50)
        input("\nPress Enter to extract listings...")

        # wait for page to fully settle after any navigation from searching
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        listings = extract_listings(page)
        browser.close()

        print(f"\nFound {len(listings)} listings\n")
        for i, l in enumerate(listings, 1):
            print(f"[{i}] {l['price']} | {l['address']} | {l['floor']} | {l['size']}")
            print(f"     Link: {l['link']}")
            print()

        return listings


if __name__ == "__main__":
    run()
