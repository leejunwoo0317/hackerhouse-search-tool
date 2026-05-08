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



def load_data():
    """Load CSV(s) — from sidebar uploader first, then all local files merged."""
    uploaded_files = st.sidebar.file_uploader(
        "Upload results CSV(s)", type="csv",
        accept_multiple_files=True,
        help="Upload CSVs from scraper_peterpan.py or scraper_naver.py"
    )
    if uploaded_files:
        dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in uploaded_files]
        df = pd.concat(dfs, ignore_index=True)
        names = ", ".join(f.name for f in uploaded_files)
        return df, names

    # fallback: merge all local result CSVs
    files = sorted(glob.glob("results_*.csv"), reverse=True)
    if files:
        dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in files]
        df = pd.concat(dfs, ignore_index=True)
        return df, f"{len(files)} local file(s)"

    return None, None


def parse_amount(value):
    try:
        s = str(value).replace(",", "").strip()
        if not s or s in ("nan", "None"):
            return None
        total = 0
        if "억" in s:
            parts = s.split("억")
            total += int(parts[0].strip()) * 10000
            rest = parts[1].replace("만원", "").replace("만", "").strip()
            if rest:
                total += int(rest)
        else:
            total = int(s.replace("만원", "").replace("만", "").strip())
        return total
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
    source = listing.get("source", "")
    source_label = {"peterpan": "Peter Pan", "naver": "Naver"}.get(source, source)
    st.caption(f"[{source_label}]  Area: {listing.get('search_label', '')}")

    if pd.notna(listing.get("description")) and listing["description"]:
        st.caption(listing["description"][:80])

    if pd.notna(listing.get("link")) and listing["link"]:
        st.markdown(f"[View listing →]({listing['link']})")

    key = f"compare_{listing['link']}|{listing.get('address','')}|{listing.get('price','')}"
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
        ("Source",        "source"),
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

    df, filename = load_data()

    if df is None:
        st.info("Upload a results CSV file using the sidebar to get started.")
        st.markdown("**If you are running locally:** generate a CSV first by running the scraper:")
        st.code("python scraper_peterpan.py")
        return

    # fill source column for older CSVs that don't have it
    if "source" not in df.columns:
        df["source"] = "peterpan"

    # deduplicate: peterpan by link, naver by address+price
    pp = df[df["source"] != "naver"].drop_duplicates(subset=["link"])
    nv = df[df["source"] == "naver"].drop_duplicates(subset=["address", "price"])
    df = pd.concat([pp, nv], ignore_index=True)

    st.caption(f"Loaded from: {filename}  |  Total listings: {len(df)}")

    # ── Sidebar filters ──────────────────────────────────────────
    st.sidebar.header("Filters")

    sources = sorted(df["source"].dropna().unique().tolist())
    source_display = {"peterpan": "Peter Pan", "naver": "Naver"}
    selected_sources = st.sidebar.multiselect(
        "Source",
        sources,
        default=sources,
        format_func=lambda x: source_display.get(x, x)
    )

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
    min_deposit = st.sidebar.number_input("Min deposit", min_value=0, value=0, step=1000)
    max_deposit = st.sidebar.number_input("Max deposit", min_value=0, value=100000, step=1000)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sort by**")
    sort_option = st.sidebar.selectbox(
        "Sort listings by",
        [
            "Default",
            "Monthly rent — low to high",
            "Monthly rent — high to low",
            "Deposit — low to high",
            "Deposit — high to low",
            "Size — large to small",
            "Size — small to large",
        ]
    )

    # ── Apply filters ────────────────────────────────────────────
    filtered = df.copy()

    if selected_sources:
        filtered = filtered[filtered["source"].isin(selected_sources)]
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

    # ── Apply sort ───────────────────────────────────────────────
    if sort_option != "Default":
        if "Monthly rent" in sort_option:
            filtered["_sort"] = filtered["monthly_rent"].apply(parse_amount)
            ascending = "low to high" in sort_option
            filtered = filtered.sort_values("_sort", ascending=ascending, na_position="last")
            filtered = filtered.drop(columns=["_sort"])
        elif "Deposit" in sort_option:
            filtered["_sort"] = filtered["deposit"].apply(parse_amount)
            ascending = "low to high" in sort_option
            filtered = filtered.sort_values("_sort", ascending=ascending, na_position="last")
            filtered = filtered.drop(columns=["_sort"])
        elif "Size" in sort_option:
            filtered["_sort"] = filtered["size"].apply(
                lambda x: parse_amount(str(x).replace("m2","").replace("m²","").replace("㎡",""))
            )
            ascending = "small to large" in sort_option
            filtered = filtered.sort_values("_sort", ascending=ascending, na_position="last")
            filtered = filtered.drop(columns=["_sort"])

    if filtered.empty:
        st.info("No listings match your filters.")
        return

    # ── Collect currently selected items ─────────────────────────
    selected_for_compare = []
    for _, listing in filtered.iterrows():
        key = f"compare_{listing['link']}|{listing.get('address','')}|{listing.get('price','')}"
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
