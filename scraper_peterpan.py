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
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        # hide automation flags from the site
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.goto("https://www.peterpanz.com/villa", wait_until="domcontentloaded")

        print("\n" + "="*50)
        print("Peter Pan is open in your browser.")
        print("Search for your desired area and filters.")
        print("Press Enter to extract listings.")
        print("Type 'q' + Enter when you are done.")
        print("="*50)

        all_listings = []

        while True:
            command = input("\nPress Enter to extract  |  type 'q' to finish: ").strip().lower()
            if command == "q":
                break

            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)

            new_listings = extract_listings(page)
            all_listings.extend(new_listings)

            print(f"\nExtracted {len(new_listings)} listings this round  |  Total so far: {len(all_listings)}")
            for i, l in enumerate(new_listings, 1):
                print(f"  [{i}] {l['price']} | {l['address']} | {l['floor']} | {l['size']}")
                print(f"       Link: {l['link']}")

            print("\nChange filters or area in the browser, then press Enter again.")

        context.close()
        browser.close()

        # remove duplicate listings by link
        seen = set()
        unique = []
        for l in all_listings:
            if l["link"] not in seen:
                seen.add(l["link"])
                unique.append(l)

        print(f"\nDone. Total unique listings collected: {len(unique)}")
        return unique


if __name__ == "__main__":
    run()
