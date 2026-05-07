import glob
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hackerhouse Search", layout="wide")


def load_latest_csv():
    files = sorted(glob.glob("results_*.csv"), reverse=True)
    if not files:
        return None, None
    df = pd.read_csv(files[0], encoding="utf-8-sig")
    return df, files[0]


def parse_monthly_rent(value):
    """Convert '130만원' string to integer 130 for filtering."""
    try:
        return int(str(value).replace("만원", "").replace(",", "").strip())
    except Exception:
        return None


def main():
    st.title("Hackerhouse Search")

    df, filename = load_latest_csv()

    if df is None:
        st.warning("No results file found. Run scraper_peterpan.py first to collect listings.")
        st.code("python scraper_peterpan.py")
        return

    st.caption(f"Loaded from: {filename}  |  Total listings: {len(df)}")

    # ── Sidebar filters ──────────────────────────────────────────
    st.sidebar.header("Filters")

    # area filter
    areas = sorted(df["search_label"].dropna().unique().tolist())
    selected_areas = st.sidebar.multiselect("Area (search label)", areas, default=areas)

    # property type filter
    types = sorted(df["property_type"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect("Property type", types, default=types)

    # price type filter
    price_types = ["월세", "전세", "매매"]
    selected_price_types = st.sidebar.multiselect("Price type", price_types, default=price_types)

    # monthly rent range (only for 월세 listings)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Monthly rent range (만원)**")
    min_rent = st.sidebar.number_input("Min", min_value=0, value=0, step=10)
    max_rent = st.sidebar.number_input("Max", min_value=0, value=500, step=10)

    # ── Apply filters ────────────────────────────────────────────
    filtered = df.copy()

    if selected_areas:
        filtered = filtered[filtered["search_label"].isin(selected_areas)]

    if selected_types:
        filtered = filtered[filtered["property_type"].isin(selected_types)]

    if selected_price_types:
        filtered = filtered[filtered["price"].apply(
            lambda x: any(pt in str(x) for pt in selected_price_types)
        )]

    # monthly rent range filter — only applied to 월세 rows
    def rent_in_range(row):
        if "월세" not in str(row["price"]):
            return True
        rent = parse_monthly_rent(row["monthly_rent"])
        if rent is None:
            return True
        return min_rent <= rent <= max_rent

    filtered = filtered[filtered.apply(rent_in_range, axis=1)]

    st.markdown(f"### Results: {len(filtered)} listings")

    if filtered.empty:
        st.info("No listings match your filters.")
        return

    # ── Listing cards ────────────────────────────────────────────
    cols_per_row = 3
    rows = [filtered.iloc[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, listing) in zip(cols, row.iterrows()):
            with col:
                # photo
                if pd.notna(listing.get("photo")) and listing["photo"]:
                    st.image(listing["photo"], use_container_width=True)
                else:
                    st.markdown("_(no photo)_")

                # info
                st.markdown(f"**{listing['price']}**")
                st.markdown(f"{listing['address']}")
                st.markdown(
                    f"{listing.get('property_type','')}  ·  "
                    f"{listing.get('floor','')}  ·  "
                    f"{listing.get('size','')}"
                )
                st.caption(f"Area: {listing.get('search_label','')}")

                if pd.notna(listing.get("description")) and listing["description"]:
                    st.caption(listing["description"][:80])

                if pd.notna(listing.get("link")) and listing["link"]:
                    st.markdown(f"[View listing →]({listing['link']})")

                st.markdown("---")


if __name__ == "__main__":
    main()
