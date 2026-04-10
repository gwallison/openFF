# Open-FF Query Layer — Developer Guide

This document describes how to read the Open-FF query layer data programmatically.
It is intended to help other projects connect to the data without needing to run
the Open-FF build pipeline.

---

## Public access

The query layer files are hosted on Google Cloud Storage and are **publicly readable**
with no authentication required.

> **Note for maintainers:** Confirm that the `open-ff-query-layer` bucket has
> `allUsers` granted the *Storage Object Viewer* role (uniform bucket-level access).
> If this is not set, the URLs below will return 403 errors for unauthenticated users.

---

## Base URL

```
https://storage.googleapis.com/open-ff-query-layer/v1
```

All file paths below are relative to this base URL.

---

## Files

| File | Size | Description |
|---|---|---|
| `index.parquet` | ~5 MB | One row per disclosure — use for filtering and search |
| `chem_index.parquet` | ~2 MB | One row per bgCAS — pre-computed stats across all disclosures |
| `disclosures/part_000.parquet` … `part_255.parquet` | ~1 MB each | Disclosure rows partitioned by MD5(DisclosureId) |
| `chemicals_by_cas/cas_{bgCAS}.parquet` | varies | All chemrec rows for one bgCAS value |
| `manifest.json` | tiny | Build metadata (timestamp, record counts) |

---

## Dependencies

```
pandas
pyarrow      # required by pandas for parquet support
```

Optional, for SQL-style queries over HTTP:
```
duckdb
```

---

## Reading the index files (load once, cache in your app)

These are small enough to load into memory at startup and reuse for all queries.

```python
import pandas as pd

BASE_URL = "https://storage.googleapis.com/open-ff-query-layer/v1"

index      = pd.read_parquet(f"{BASE_URL}/index.parquet")
chem_index = pd.read_parquet(f"{BASE_URL}/chem_index.parquet")
```

### `index.parquet` columns

| Column | Description |
|---|---|
| `DisclosureId` | Primary key, links to partition files |
| `bgStateName` | Curated state name |
| `bgCountyName` | Curated county name |
| `date` | Job end date |
| `OperatorName` | Operator as reported |
| `WellName` | Well name as reported |
| `APINumber` | API well number |

### `chem_index.parquet` columns

| Column | Description |
|---|---|
| `bgCAS` | Open-FF curated CAS/identifier |
| `bgIngredientName` | Curated chemical name |
| `disclosure_count` | Number of disclosures using this chemical |
| `state_count` | Number of distinct states |
| `conc_valid_count` | Records with a usable concentration value |
| `conc_pct_valid` | Fraction with valid concentration (0.0–1.0) |
| `conc_valid_max/min/median` | Concentration stats (PercentHFJob scale) |
| `mass_valid_count` | Records with a usable mass value |
| `mass_pct_valid` | Fraction with valid mass |
| `mass_valid_max/min/median` | Mass stats (lbs) |
| `mass_flagged_count` | Records where mass is absent or out of tolerance |

---

## Fetching a specific disclosure (tier 2)

Disclosures are split across 256 partition files using a deterministic MD5 hash.
To find the right partition for a given `DisclosureId`:

```python
import hashlib

def key_to_bucket(disclosure_id, n=256):
    """Partition assignment — must match the build script exactly."""
    return int(hashlib.md5(str(disclosure_id).encode()).hexdigest(), 16) % n

disclosure_id = "your-disclosure-id-here"
bucket_id     = key_to_bucket(disclosure_id)

partition = pd.read_parquet(
    f"{BASE_URL}/disclosures/part_{bucket_id:03d}.parquet"
)
row = partition[partition["DisclosureId"] == disclosure_id]
```

Each partition file contains roughly 1/256th of all disclosures (~950 rows at
current scale) and includes all columns from the source `disclosures.parquet`.

---

## Fetching all records for a chemical (tier 3)

One file exists per `bgCAS` value, containing all chemrec rows for that chemical
across all disclosures.

```python
bgcas    = "7647-01-0"
safe_cas = bgcas.replace("/", "-")   # forward slashes are not safe in filenames

records = pd.read_parquet(
    f"{BASE_URL}/chemicals_by_cas/cas_{safe_cas}.parquet"
)
```

Note that some `bgCAS` values are Open-FF categorical identifiers rather than
real CAS numbers: `proprietary`, `ambiguousID`, `conflictingID`,
`non_chem_record`, `sysAppMeta`. These have their own files and can be
very large (e.g. `cas_proprietary.parquet` contains ~1M rows).

---

## Example: disclosures in a given county

```python
import pandas as pd

BASE_URL = "https://storage.googleapis.com/open-ff-query-layer/v1"

index = pd.read_parquet(f"{BASE_URL}/index.parquet")

county_discs = index[
    (index["bgStateName"] == "Colorado") &
    (index["bgCountyName"] == "Weld")
].sort_values("date", ascending=False)

print(f"{len(county_discs)} disclosures in Weld County, CO")
print(county_discs[["date", "OperatorName", "WellName"]].head(10))
```

---

## Example: top chemicals by disclosure count

```python
chem_index = pd.read_parquet(f"{BASE_URL}/chem_index.parquet")

top = (
    chem_index[~chem_index["bgCAS"].isin(
        {"proprietary", "ambiguousID", "conflictingID", "non_chem_record", "sysAppMeta"}
    )]
    .sort_values("disclosure_count", ascending=False)
    .head(20)
)[["bgCAS", "bgIngredientName", "disclosure_count", "state_count"]]

print(top.to_string(index=False))
```

---

## Example: load all records for a specific chemical

```python
import hashlib
import pandas as pd

BASE_URL = "https://storage.googleapis.com/open-ff-query-layer/v1"

bgcas   = "7732-18-5"   # Water
safe    = bgcas.replace("/", "-")
records = pd.read_parquet(f"{BASE_URL}/chemicals_by_cas/cas_{safe}.parquet")

print(f"{len(records)} records for {bgcas}")
```

---

## Using DuckDB for SQL-style queries

DuckDB can query the parquet files over HTTP directly, which is efficient for
column-selective queries on large files.

```python
import duckdb, hashlib

BASE_URL = "https://storage.googleapis.com/open-ff-query-layer/v1"

def key_to_bucket(disclosure_id, n=256):
    return int(hashlib.md5(str(disclosure_id).encode()).hexdigest(), 16) % n

# Filter a partition without loading the whole file into memory
disclosure_id = "your-disclosure-id-here"
bucket_id     = key_to_bucket(disclosure_id)

row = duckdb.query(f"""
    SELECT *
    FROM read_parquet('{BASE_URL}/disclosures/part_{bucket_id:03d}.parquet')
    WHERE DisclosureId = '{disclosure_id}'
""").df()
```

---

## Checking the manifest

```python
import requests

manifest = requests.get(
    "https://storage.googleapis.com/open-ff-query-layer/v1/manifest.json"
).json()
print(manifest)
# {'build_timestamp': '...', 'disclosure_count': 245126, ...}
```

---

## Notes

- All data originates from the Open-FF build pipeline. The query layer is
  regenerated periodically; check `manifest.json` for the build timestamp.
- Chemical quality flags (`massCompFlag`) are preserved on raw rows in tier-2
  and tier-3 files. The `chem_index.parquet` pre-aggregates quality stats.
  Apps should decide at query time how to handle flagged or missing values.
- The `key_to_bucket()` function must be identical in both the build script
  and any app that reads tier-2 files. Do not alter it.
