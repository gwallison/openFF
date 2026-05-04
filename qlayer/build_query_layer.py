#!/usr/bin/env python3
"""
build_query_layer.py

Reads bulk parquet files from GCS (via common.handles.repo_pickles_url) and writes
a query-optimized layer to gs://open-ff-query-layer/v1/

Run from within the openFF environment:
    python qlayer/build_query_layer.py

Tiers produced:
    v1/index.parquet                         — one row per disclosure
    v1/chem_index.parquet                    — one row per bgCAS, with stats
    v1/disclosures/part_000..255.parquet     — disclosures partitioned by MD5(DisclosureId)
    v1/chemrecs/part_000..255.parquet        — chemrecs partitioned by MD5(DisclosureId)
    v1/chemicals_by_cas/cas_<bgCAS>.parquet  — chemrecs partitioned by bgCAS
    v1/manifest.json                         — build metadata
"""

import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.cloud import storage

# Make common.handles importable when run from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.handles import repo_pickles_url

# --Constants --───────────────────────────────────────────────────────────────

DEST_BUCKET = "open-ff-query-layer"
DEST_PREFIX = "v1"          # overridden by --prefix at runtime
N_PARTITIONS = 256


# --Partitioning --────────────────────────────────────────────────────────────

def key_to_bucket(disclosure_id, n=N_PARTITIONS):
    """MD5-based partition assignment. Must match query-side implementation."""
    return int(hashlib.md5(str(disclosure_id).encode()).hexdigest(), 16) % n


# --GCS helpers --─────────────────────────────────────────────────────────────

def upload_df(client, blob_path, df):
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    bucket = client.bucket(DEST_BUCKET)
    bucket.blob(blob_path).upload_from_string(buf.getvalue(), content_type="application/octet-stream")
    print(f"  uploaded gs://{DEST_BUCKET}/{blob_path}  ({len(df):,} rows)")


def upload_json(client, blob_path, obj):
    data = json.dumps(obj, indent=2).encode()
    bucket = client.bucket(DEST_BUCKET)
    bucket.blob(blob_path).upload_from_string(data, content_type="application/json")
    print(f"  uploaded gs://{DEST_BUCKET}/{blob_path}")


# --Load inputs --─────────────────────────────────────────────────────────────

def load_inputs(state_filter: str | None = None):
    print("Loading input parquet files from:", repo_pickles_url)
    disclosures = pd.read_parquet(repo_pickles_url + "disclosures.parquet")
    chemrecs    = pd.read_parquet(repo_pickles_url + "chemrecs.parquet")
    bgcas       = pd.read_parquet(repo_pickles_url + "bgCAS.parquet")
    print(f"  disclosures : {len(disclosures):,} rows, {len(disclosures.columns)} cols")
    print(f"  chemrecs    : {len(chemrecs):,} rows, {len(chemrecs.columns)} cols")
    print(f"  bgCAS       : {len(bgcas):,} rows, {len(bgcas.columns)} cols")

    if state_filter:
        state_col = "bgStateName"
        if state_col not in disclosures.columns:
            raise ValueError(f"Column '{state_col}' not found in disclosures — cannot filter by state")
        n_before = len(disclosures)
        disclosures = disclosures[disclosures[state_col] == state_filter].copy()
        print(f"\n  state filter '{state_filter}': {n_before:,} -> {len(disclosures):,} disclosures")
        keep_ids = set(disclosures["DisclosureId"])
        n_before = len(chemrecs)
        chemrecs = chemrecs[chemrecs["DisclosureId"].isin(keep_ids)].copy()
        print(f"  state filter '{state_filter}': {n_before:,} -> {len(chemrecs):,} chemrec rows")

    return disclosures, chemrecs, bgcas


# --Tier 1a: index.parquet --──────────────────────────────────────────────────

def build_index(disclosures, client):
    print("\n--Tier 1a: index.parquet --")
    cols = ['DisclosureId', 'bgStateName', 'bgCountyName', 'date',
            'OperatorName', 'WellName', 'APINumber']
    missing = [c for c in cols if c not in disclosures.columns]
    if missing:
        print(f"  WARNING: columns not found, will be omitted: {missing}")
    present = [c for c in cols if c in disclosures.columns]
    upload_df(client, f"{DEST_PREFIX}/index.parquet", disclosures[present])


# --Tier 1b: chem_index.parquet --────────────────────────────────────────────

def build_chem_index(disclosures, chemrecs, bgcas, client):
    print("\n--Tier 1b: chem_index.parquet --")

    # Attach state to each chem record for state_count aggregation
    cr = chemrecs.merge(
        disclosures[['DisclosureId', 'bgStateName']],
        on='DisclosureId', how='left'
    )

    g = cr.groupby('bgCAS', sort=False)
    total = g.size()

    agg = pd.DataFrame({
        'disclosure_count': g['DisclosureId'].nunique(),
        'state_count':      g['bgStateName'].nunique(),
    })

    # --Concentration (cleanMI) — non-null = valid, null = missing (no flag yet) --
    conc = cr.groupby('bgCAS', sort=False)['cleanMI']
    conc_valid = conc.count()                          # count() excludes NaN
    agg['conc_valid_count']  = conc_valid
    agg['conc_missing_count'] = total - conc_valid
    agg['conc_pct_valid']    = (conc_valid / total).round(4)
    agg['conc_valid_max']    = conc.max()
    agg['conc_valid_min']    = conc.min()
    agg['conc_valid_median'] = conc.median()
    agg['conc_flagged_count'] = 0                      # placeholder until conc_quality exists

    # --Mass --────────────────────────────────────────────────────────────────
    # mass_valid: a usable mass value exists (not null and not zero)
    # mass_flagged: mass is absent/unusable OR MassIngredient was out of tolerance
    #   (when flagged, a calculated value is used instead — so valid and flagged can overlap)
    cr['_mass_valid']   = cr['mass'].notna() & (cr['mass'] > 0)
    cr['_mass_flagged'] = cr['mass'].isna() | (cr['mass'] <= 0) | (cr['massCompFlag'] == True)

    g2 = cr.groupby('bgCAS', sort=False)
    mass_valid_count   = g2['_mass_valid'].sum()
    mass_flagged_count = g2['_mass_flagged'].sum()

    agg['mass_valid_count']   = mass_valid_count
    agg['mass_missing_count'] = cr.groupby('bgCAS', sort=False)['mass'].apply(lambda x: x.isna().sum())
    agg['mass_flagged_count'] = mass_flagged_count
    agg['mass_pct_valid']     = (mass_valid_count / total).round(4)

    valid_mass = cr[cr['_mass_valid']].groupby('bgCAS', sort=False)['mass']
    agg['mass_valid_max']    = valid_mass.max()
    agg['mass_valid_min']    = valid_mass.min()
    agg['mass_valid_median'] = valid_mass.median()

    agg = agg.reset_index()

    # Join bgIngredientName from bgcas table
    agg = agg.merge(
        bgcas[['bgCAS', 'bgIngredientName']].drop_duplicates('bgCAS'),
        on='bgCAS', how='left'
    )

    # Put identifier columns first
    front = ['bgCAS', 'bgIngredientName']
    rest  = [c for c in agg.columns if c not in front]
    agg   = agg[front + rest]

    upload_df(client, f"{DEST_PREFIX}/chem_index.parquet", agg)


# --Tier 2: disclosures partitioned by MD5(DisclosureId) --───────────────────

def build_disclosure_partitions(disclosures, client):
    print(f"\n--Tier 2: {N_PARTITIONS} disclosure partitions --")
    disclosures = disclosures.copy()
    disclosures['_bucket'] = disclosures['DisclosureId'].apply(key_to_bucket)

    for bucket_id, part in disclosures.groupby('_bucket', sort=True):
        part = part.drop(columns=['_bucket'])
        blob_path = f"{DEST_PREFIX}/disclosures/part_{bucket_id:03d}.parquet"
        upload_df(client, blob_path, part)

    print(f"  all {N_PARTITIONS} partitions uploaded")


# --Tier 4: chemrecs partitioned by MD5(DisclosureId) --──────────────────────
#
# Mirrors the disclosures/ partition layout so the same key_to_bucket() call
# retrieves both disclosure metadata and chemical records for any DisclosureId.
# Hazard flags and regulatory list membership are joined from bgCAS so the
# partition files are self-contained for analysis.

# Columns to keep from chemrecs.parquet
_CHEMREC_BASE_COLS = [
    'DisclosureId',
    'bgCAS', 'CASNumber', 'IngredientName', 'bgIngredientName',
    'massSource', 'mass', 'calcMass', 'massCompFlag', 'cleanMI',
    'PercentHFJob', 'Supplier', 'TradeName', 'Purpose',
    'ingKeyPresent', 'in_std_filtered',
]

# Columns to join from bgCAS.parquet (hazard flags, regulatory lists, etc.)
_BGCAS_JOIN_COLS = [
    'bgCAS', 'epa_pref_name', 'rq_lbs',
    'is_on_CWA', 'is_on_DWSHA', 'is_on_AQ_CWA', 'is_on_HH_CWA',
    'is_on_IRIS', 'is_on_PFAS_list', 'is_on_NPDWR', 'is_on_prop65',
    'is_on_TEDX', 'is_on_diesel', 'is_on_UVCB', 'is_on_TSCA',
    'eh_Class_L1', 'eh_Class_L2',
]


def build_chemrec_partitions(chemrecs, bgcas, client):
    print(f"\n--Tier 4: {N_PARTITIONS} chemrec partitions --")

    # Pre-filter: drop duplicate ingredient records (dup_rec == True).
    # Disclosure-level deduplication (is_duplicate) is handled by the well index.
    # Together these replicate: in_std_filtered = ~is_duplicate & ~dup_rec
    if 'dup_rec' in chemrecs.columns:
        n_before = len(chemrecs)
        chemrecs = chemrecs[~chemrecs['dup_rec']]
        print(f"  filtered dup_rec: {n_before:,} -> {len(chemrecs):,} rows")

    # Select available base columns
    base_present = [c for c in _CHEMREC_BASE_COLS if c in chemrecs.columns]
    base_missing = [c for c in _CHEMREC_BASE_COLS if c not in chemrecs.columns]
    if base_missing:
        print(f"  NOTE: chemrecs columns not found, skipped: {base_missing}")
    cr = chemrecs[base_present].copy()

    # Join hazard / regulatory columns from bgCAS
    ref_present = [c for c in _BGCAS_JOIN_COLS if c in bgcas.columns]
    ref_missing = [c for c in _BGCAS_JOIN_COLS if c not in bgcas.columns]
    if ref_missing:
        print(f"  NOTE: bgCAS columns not found, skipped: {ref_missing}")
    if ref_present:
        cas_ref = bgcas[ref_present].drop_duplicates('bgCAS')
        cr = cr.merge(cas_ref, on='bgCAS', how='left')

    cr['_bucket'] = cr['DisclosureId'].apply(key_to_bucket)

    for bucket_id, part in cr.groupby('_bucket', sort=True):
        part = part.drop(columns=['_bucket'])
        blob_path = f"{DEST_PREFIX}/chemrecs/part_{bucket_id:03d}.parquet"
        upload_df(client, blob_path, part)

    print(f"  all {N_PARTITIONS} partitions uploaded  ({len(cr):,} total chemrec rows)")
    return len(cr)


# --Tier 3: chemicals partitioned by bgCAS --──────────────────────────────────

def build_chemicals_by_cas(chemrecs, client):
    print("\n--Tier 3: chemicals_by_cas files --")
    cas_values = chemrecs['bgCAS'].dropna().unique()
    print(f"  {len(cas_values):,} distinct bgCAS values")

    for i, cas in enumerate(sorted(cas_values)):
        subset    = chemrecs[chemrecs['bgCAS'] == cas]
        safe_cas  = str(cas).replace('/', '-')
        blob_path = f"{DEST_PREFIX}/chemicals_by_cas/cas_{safe_cas}.parquet"
        upload_df(client, blob_path, subset)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(cas_values)} bgCAS files uploaded")

    print(f"  all {len(cas_values)} bgCAS files uploaded")
    return len(cas_values)


# --Manifest --────────────────────────────────────────────────────────────────

def write_manifest(client, disclosure_count, chemical_count, bgcas_count):
    print("\n--Manifest --")
    manifest = {
        "build_timestamp":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "disclosure_count":     disclosure_count,
        "chemical_count":       chemical_count,
        "bgcas_count":          bgcas_count,
        "partition_count":      N_PARTITIONS,
        "query_layer_version":  "v1",
        "tiers": [
            "index", "chem_index", "disclosures", "chemrecs",
            "chemicals_by_cas", "manifest",
        ],
    }
    upload_json(client, f"{DEST_PREFIX}/manifest.json", manifest)
    print(f"  {manifest}")


# --Main --────────────────────────────────────────────────────────────────────

def main(tier4_only: bool = False, state_filter: str | None = None,
         dest_prefix: str | None = None):
    global DEST_PREFIX
    if dest_prefix:
        DEST_PREFIX = dest_prefix
        print(f"Output prefix overridden to: gs://{DEST_BUCKET}/{DEST_PREFIX}/")

    client = storage.Client()
    disclosures, chemrecs, bgcas = load_inputs(state_filter=state_filter)

    if tier4_only:
        chemrec_count = build_chemrec_partitions(chemrecs, bgcas, client)
        print(f"\nTier 4 rebuild complete ({chemrec_count:,} rows).")
        return

    build_index(disclosures, client)
    build_chem_index(disclosures, chemrecs, bgcas, client)
    build_disclosure_partitions(disclosures, client)
    chemrec_count = build_chemrec_partitions(chemrecs, bgcas, client)
    bgcas_count = build_chemicals_by_cas(chemrecs, client)

    write_manifest(
        client,
        disclosure_count=len(disclosures),
        chemical_count=chemrec_count,
        bgcas_count=bgcas_count,
    )
    print("\nDone.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier4-only", action="store_true",
                        help="Rebuild only chemrec (tier 4) partitions")
    parser.add_argument("--state", type=str, default=None,
                        help="Filter to a single state (bgStateName value), e.g. 'Pennsylvania'")
    parser.add_argument("--prefix", type=str, default=None,
                        help="GCS destination prefix, e.g. 'pa/v1' (default: 'v1')")
    args = parser.parse_args()
    main(tier4_only=args.tier4_only, state_filter=args.state, dest_prefix=args.prefix)
