"""
explorer.py — Open-FF Query Layer demo app

Demonstrates tiered data access from gs://open-ff-query-layer/v1

Run with:
    streamlit run qlayer/explorer.py
"""

import hashlib
import streamlit as st
import pandas as pd

BASE_URL = "https://storage.googleapis.com/open-ff-query-layer/v1"


# ── Partitioning (must match build script exactly) ────────────────────────────

def key_to_bucket(disclosure_id, n=256):
    return int(hashlib.md5(str(disclosure_id).encode()).hexdigest(), 16) % n


# ── Cached data loaders ───────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_index():
    """Tier 1 — one row per disclosure, loaded once on startup."""
    return pd.read_parquet(f"{BASE_URL}/index.parquet")


@st.cache_data(show_spinner=False)
def load_chem_index():
    """Tier 1 — one row per bgCAS with pre-computed stats, loaded once on startup."""
    return pd.read_parquet(f"{BASE_URL}/chem_index.parquet")


@st.cache_data(show_spinner=False)
def load_disclosure_partition(bucket_id):
    """Tier 2 — one of 256 disclosure partition files, fetched on demand."""
    return pd.read_parquet(f"{BASE_URL}/disclosures/part_{bucket_id:03d}.parquet")


@st.cache_data(show_spinner=False)
def load_chemrec_partition(bucket_id):
    """Tier 4 — chemical records for one of 256 disclosure-keyed partitions."""
    return pd.read_parquet(f"{BASE_URL}/chemrecs/part_{bucket_id:03d}.parquet")


@st.cache_data(show_spinner=False)
def load_chemicals_for_cas(bgcas):
    """Tier 3 — all chemrec rows for one bgCAS, fetched on demand."""
    safe = str(bgcas).replace("/", "-")
    return pd.read_parquet(f"{BASE_URL}/chemicals_by_cas/cas_{safe}.parquet")


# ── App layout ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Open-FF Explorer", layout="wide")
st.title("Open-FF Query Layer Explorer")
st.caption(
    "Demonstrates tiered access to `gs://open-ff-query-layer/v1` — "
    "index files cached at startup; partition files fetched on demand."
)

# Load tier-1 index files once
with st.spinner("Loading index files (tier 1)..."):
    index      = load_index()
    chem_index = load_chem_index()

tab_location, tab_chemical = st.tabs(["Browse by Location", "Browse by Chemical"])


# ── Tab 1: Browse by Location ─────────────────────────────────────────────────

with tab_location:
    st.markdown("**Step 1 — Filter disclosures** using `index.parquet` (tier 1, cached)")

    col1, col2, col3 = st.columns(3)

    with col1:
        states = sorted(index["bgStateName"].dropna().unique())
        state  = st.selectbox("State", states)

    with col2:
        counties = sorted(
            index.loc[index["bgStateName"] == state, "bgCountyName"].dropna().unique()
        )
        county = st.selectbox("County", counties)

    with col3:
        years = sorted(index["date"].dropna().dt.year.unique(), reverse=True)
        year  = st.selectbox("Year (optional)", ["All"] + [str(y) for y in years])

    mask = (index["bgStateName"] == state) & (index["bgCountyName"] == county)
    if year != "All":
        mask &= index["date"].dt.year == int(year)
    filtered = index[mask].sort_values("date", ascending=False)

    st.write(f"**{len(filtered):,} disclosures** in {county} County, {state}"
             + (f" ({year})" if year != "All" else ""))

    show_cols = [c for c in ["DisclosureId", "date", "OperatorName", "WellName", "APINumber"]
                 if c in filtered.columns]
    st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

    # ── Disclosure detail (tier 2) ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Step 2 — Load disclosure detail** from the matching tier-2 partition")

    if len(filtered) == 0:
        st.info("No disclosures match the filter above.")
    else:
        label_map = {
            row["DisclosureId"]: f"{row.get('date', ''):%Y-%m-%d}  |  {row.get('OperatorName', '')}  |  {row.get('WellName', '')}"
            for _, row in filtered.iterrows()
        }
        chosen_id = st.selectbox(
            "Select a disclosure",
            options=list(label_map.keys()),
            format_func=lambda x: label_map[x],
        )

        if chosen_id:
            bucket_id = key_to_bucket(chosen_id)

            col_disc, col_chem = st.columns(2)

            with col_disc:
                with st.spinner(f"Fetching disclosures/part_{bucket_id:03d}.parquet (tier 2)..."):
                    partition = load_disclosure_partition(bucket_id)
                row = partition[partition["DisclosureId"] == chosen_id]
                if len(row):
                    st.caption(
                        f"`disclosures/part_{bucket_id:03d}.parquet` "
                        f"({len(partition):,} disclosures in partition)"
                    )
                    detail = (
                        row.iloc[0]
                        .dropna()
                        .reset_index()
                        .rename(columns={"index": "Field", 0: "Value"})
                    )
                    st.dataframe(detail, use_container_width=True, hide_index=True)

            with col_chem:
                with st.spinner(f"Fetching chemrecs/part_{bucket_id:03d}.parquet (tier 4)..."):
                    chem_part = load_chemrec_partition(bucket_id)
                chems = chem_part[chem_part["DisclosureId"] == chosen_id]
                st.caption(
                    f"`chemrecs/part_{bucket_id:03d}.parquet` "
                    f"— **{len(chems):,} chemical records** for this disclosure"
                )
                show_cols = [c for c in [
                    "bgCAS", "IngredientName", "mass", "is_on_CWA",
                    "is_on_IRIS", "is_on_PFAS_list",
                ] if c in chems.columns]
                st.dataframe(chems[show_cols] if show_cols else chems,
                             use_container_width=True, hide_index=True)


# ── Tab 2: Browse by Chemical ─────────────────────────────────────────────────

with tab_chemical:
    st.markdown("**Step 1 — Explore chemicals** using `chem_index.parquet` (tier 1, cached)")

    search = st.text_input("Search by chemical name (leave blank to see all by usage)")

    if search:
        mask    = chem_index["bgIngredientName"].str.contains(search, case=False, na=False)
        matches = chem_index[mask]
    else:
        matches = chem_index.sort_values("disclosure_count", ascending=False)

    # Skip non-chem bgCAS categories for display but keep them selectable
    non_chem = {"proprietary", "ambiguousID", "conflictingID", "non_chem_record", "sysAppMeta"}
    show_cols = [c for c in [
        "bgCAS", "bgIngredientName", "disclosure_count", "state_count",
        "conc_valid_count", "conc_pct_valid",
        "mass_valid_count", "mass_pct_valid",
    ] if c in matches.columns]

    st.write(f"**{len(matches):,} bgCAS entries**" + (f' matching "{search}"' if search else ""))
    st.dataframe(matches[show_cols], use_container_width=True, hide_index=True)

    # ── Chemical detail (tier 3) ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Step 2 — Load all records for one chemical** from the tier-3 file")

    if len(matches) == 0:
        st.info("No chemicals match the search above.")
    else:
        label_map2 = {
            row["bgCAS"]: f"{row['bgCAS']}  —  {row.get('bgIngredientName', '')}"
            for _, row in matches.iterrows()
        }
        chosen_cas = st.selectbox(
            "Select a chemical",
            options=list(label_map2.keys()),
            format_func=lambda x: label_map2[x],
        )

        if st.button("Load chemical records (tier 3)"):
            safe = str(chosen_cas).replace("/", "-")
            with st.spinner(f"Fetching chemicals_by_cas/cas_{safe}.parquet (tier 3)..."):
                records = load_chemicals_for_cas(chosen_cas)

            st.caption(
                f"Loaded `chemicals_by_cas/cas_{safe}.parquet` "
                f"— **{len(records):,} records** across all disclosures"
            )
            st.dataframe(records.head(1000), use_container_width=True, hide_index=True)
            if len(records) > 1000:
                st.caption(f"Showing first 1,000 of {len(records):,} rows.")
