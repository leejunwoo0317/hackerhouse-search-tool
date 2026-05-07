import glob
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hackerhouse Search", layout="wide")


def inject_back_to_top():
    """Inject a floating back-to-top button into the parent page via iframe JS."""
    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;
        if (doc.getElementById('back-to-top-btn')) return;

        var btn = doc.createElement('button');
        btn.id = 'back-to-top-btn';
        btn.innerText = '↑ Top';
        btn.style.cssText = [
            'position:fixed', 'bottom:2rem', 'right:2rem',
            'background:#ff4b4b', 'color:white', 'border:none',
            'padding:0.6rem 1.2rem', 'border-radius:8px',
            'font-size:15px', 'font-weight:bold', 'cursor:pointer',
            'z-index:9999', 'box-shadow:0 2px 8px rgba(0,0,0,0.3)'
        ].join(';');
        btn.onmouseover = function() { this.style.background='#cc3333'; };
        btn.onmouseout  = function() { this.style.background='#ff4b4b'; };
        btn.onclick = function() {
            // try every known Streamlit scroll container
            var selectors = ['section.main', '.main', '.stMain',
                             '.appview-container', '.block-container'];
            selectors.forEach(function(sel) {
                var el = doc.querySelector(sel);
                if (el) { el.scrollTop = 0; }
            });
            // also reset window-level scroll
            window.parent.scrollTo(0, 0);
            doc.documentElement.scrollTop = 0;
            doc.body.scrollTop = 0;
        };
        doc.body.appendChild(btn);
    })();
    </script>
    """, height=1)



def load_latest_csv():
    files = sorted(glob.glob("results_*.csv"), reverse=True)
    if not files:
        return None, None
    df = pd.read_csv(files[0], encoding="utf-8-sig")
    return df, files[0]


def parse_amount(value):
    try:
        return int(str(value).replace("만원", "").replace(",", "").strip())
    except Exception:
        return None



def reset_comparison():
    for key in list(st.session_state.keys()):
        if key.startswith("compare_"):
            st.session_state[key] = False


def render_card(listing):
    if pd.notna(listing.get("photo")) and listing["photo"]:
        st.image(listing["photo"], use_container_width=True)
    else:
        st.markdown("_(no photo)_")

    st.markdown(f"**{listing['price']}**")
    st.markdown(f"{listing['address']}")
    st.markdown(
        f"{listing.get('property_type', '')}  ·  "
        f"{listing.get('floor', '')}  ·  "
        f"{listing.get('size', '')}"
    )
    st.caption(f"Area: {listing.get('search_label', '')}")

    if pd.notna(listing.get("description")) and listing["description"]:
        st.caption(listing["description"][:80])

    if pd.notna(listing.get("link")) and listing["link"]:
        st.markdown(f"[View listing →]({listing['link']})")

    key = f"compare_{listing['link']}"
    checked = st.checkbox("Compare", key=key)
    st.markdown("---")
    return checked


def render_comparison(selected):
    st.markdown("## Side-by-Side Comparison")

    fields = [
        ("Price",         "price"),
        ("Deposit",       "deposit"),
        ("Monthly rent",  "monthly_rent"),
        ("Address",       "address"),
        ("Property type", "property_type"),
        ("Floor",         "floor"),
        ("Size",          "size"),
        ("Area (search)", "search_label"),
    ]

    photo_cols = st.columns(len(selected))
    for col, listing in zip(photo_cols, selected):
        with col:
            if pd.notna(listing.get("photo")) and listing["photo"]:
                st.image(listing["photo"], use_container_width=True)

    for label, field in fields:
        row_cols = st.columns([1] + [2] * len(selected))
        with row_cols[0]:
            st.markdown(f"**{label}**")
        values = [str(listing.get(field, "")) for listing in selected]
        amounts = [parse_amount(v) for v in values]
        valid = [(i, a) for i, a in enumerate(amounts) if a is not None]
        best_idx = None
        if field == "monthly_rent" and valid:
            best_idx = min(valid, key=lambda x: x[1])[0]
        if field == "size" and valid:
            best_idx = max(valid, key=lambda x: x[1])[0]

        for i, (col, val) in enumerate(zip(row_cols[1:], values)):
            with col:
                st.markdown(f"✅ **{val}**" if i == best_idx else val)

    st.markdown("---")


def render_sidebar_comparison_bar(df, selected_for_compare):
    """Always-visible sidebar panel showing selected items."""
    st.sidebar.markdown("---")
    if not selected_for_compare:
        st.sidebar.markdown("**Comparison list** — empty")
        st.sidebar.caption("Check 'Compare' on any listing to add it here.")
        return

    st.sidebar.markdown(f"**Comparison list ({len(selected_for_compare)})**")
    for listing in selected_for_compare:
        st.sidebar.markdown(
            f"- {listing.get('address', '')}  \n"
            f"  {listing.get('price', '')}  ·  {listing.get('size', '')}"
        )

    if st.sidebar.button("↑ Top", use_container_width=True):
        components.html("""<script>
            var doc = window.parent.document;
            ['section.main','.main','.stMain','.appview-container','.block-container']
            .forEach(function(s){var e=doc.querySelector(s);if(e)e.scrollTop=0;});
            window.parent.scrollTo(0,0);
            doc.documentElement.scrollTop=0;
            doc.body.scrollTop=0;
        </script>""", height=1)
    if st.sidebar.button("Reset compare", use_container_width=True):
        reset_comparison()
        st.rerun()


def main():
    inject_back_to_top()
    st.title("Hackerhouse Search")

    df, filename = load_latest_csv()

    if df is None:
        st.warning("No results file found. Run scraper_peterpan.py first to collect listings.")
        st.code("python scraper_peterpan.py")
        return

    st.caption(f"Loaded from: {filename}  |  Total listings: {len(df)}")

    # ── Sidebar filters ──────────────────────────────────────────
    st.sidebar.header("Filters")

    areas = sorted(df["search_label"].dropna().unique().tolist())
    selected_areas = st.sidebar.multiselect("Area (search label)", areas, default=areas)

    types = sorted(df["property_type"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect("Property type", types, default=types)

    price_types = ["월세", "전세", "매매"]
    selected_price_types = st.sidebar.multiselect("Price type", price_types, default=price_types)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Monthly rent range (만원)**")
    min_rent = st.sidebar.number_input("Min rent", min_value=0, value=0, step=10)
    max_rent = st.sidebar.number_input("Max rent", min_value=0, value=500, step=10)

    st.sidebar.markdown("**Deposit range (만원)**")
    min_deposit = st.sidebar.number_input("Min deposit", min_value=0, value=0, step=100)
    max_deposit = st.sidebar.number_input("Max deposit", min_value=0, value=10000, step=100)

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

    def in_rent_range(row):
        if "월세" not in str(row["price"]):
            return True
        amount = parse_amount(row["monthly_rent"])
        return True if amount is None else min_rent <= amount <= max_rent

    def in_deposit_range(row):
        if "월세" not in str(row["price"]) and "전세" not in str(row["price"]):
            return True
        amount = parse_amount(row["deposit"])
        return True if amount is None else min_deposit <= amount <= max_deposit

    filtered = filtered[filtered.apply(in_rent_range, axis=1)]
    filtered = filtered[filtered.apply(in_deposit_range, axis=1)]

    if filtered.empty:
        st.info("No listings match your filters.")
        return

    # ── Collect currently selected items ─────────────────────────
    selected_for_compare = []
    for _, listing in filtered.iterrows():
        key = f"compare_{listing['link']}"
        if st.session_state.get(key):
            selected_for_compare.append(listing)

    # ── Sidebar comparison bar (always visible) ───────────────────
    render_sidebar_comparison_bar(df, selected_for_compare)

    # ── Tabs ─────────────────────────────────────────────────────
    count = len(selected_for_compare)
    tab_label = f"Compare ({count})" if count else "Compare"
    tab_listings, tab_compare = st.tabs([f"Listings ({len(filtered)})", tab_label])

    # ── Tab 1: Listing cards ──────────────────────────────────────
    with tab_listings:
        cols_per_row = 3
        rows = [filtered.iloc[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, (_, listing) in zip(cols, row.iterrows()):
                with col:
                    render_card(listing)


    # ── Tab 2: Comparison ─────────────────────────────────────────
    with tab_compare:
        if len(selected_for_compare) >= 2:
            render_comparison(selected_for_compare)
        elif len(selected_for_compare) == 1:
            st.info("Select at least one more listing in the Listings tab to compare.")
        else:
            st.info("Go to the Listings tab, check the Compare box on 2 or more listings, then come back here.")


if __name__ == "__main__":
    main()
