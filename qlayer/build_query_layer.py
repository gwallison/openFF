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
DEST_PREFIX = "v1"
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

def load_inputs():
    print("Loading input parquet files from:", repo_pickles_url)
    disclosures = pd.read_parquet(repo_pickles_url + "disclosures.parquet")
    chemrecs    = pd.read_parquet(repo_pickles_url + "chemrecs.parquet")
    bgcas       = pd.read_parquet(repo_pickles_url + "bgCAS.parquet")
    print(f"  disclosures : {len(disclosures):,} rows, {len(disclosures.columns)} cols")
    print(f"  chemrecs    : {len(chemrecs):,} rows, {len(chemrecs.columns)} cols")
    print(f"  bgCAS       : {len(bgcas):,} rows, {len(bgcas.columns)} cols")
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
    }
    upload_json(client, f"{DEST_PREFIX}/manifest.json", manifest)
    print(f"  {manifest}")


# --Main --────────────────────────────────────────────────────────────────────

def main():
    client = storage.Client()
    disclosures, chemrecs, bgcas = load_inputs()

    build_index(disclosures, client)
    build_chem_index(disclosures, chemrecs, bgcas, client)
    build_disclosure_partitions(disclosures, client)
    bgcas_count = build_chemicals_by_cas(chemrecs, client)

    write_manifest(
        client,
        disclosure_count=len(disclosures),
        chemical_count=len(chemrecs),
        bgcas_count=bgcas_count,
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
