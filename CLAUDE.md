# Open-FF query layer — project context for Claude Code

## What this project is

Open-FF is a non-profit data transparency project that mirrors and normalizes
FracFocus fracking disclosure data. The existing data repository lives on Google
Cloud Storage (GCS) as flat bulk Parquet files. This project adds a **queryable
layer** on top of those existing files without modifying or removing anything.

## Goal of this script

Build `build_query_layer.py` — a standalone script that reads the existing bulk
Parquet files and writes a new set of query-optimized files to GCS. It is purely
additive. Existing users and tools are unaffected.

This project should reside in the folder `qlayer`

---

## Existing bulk files (inputs — do not modify)

| File | Contents |
|---|---|
| `disclosures.parquet` | One row per disclosure, metadata fields |
| `chemrecs.parquet` | One row per chemical record, ~50 rows per disclosure |
| `bgCAS.parquet` | one row per bgCAS value, metadata for the bgCAS in chemrecs |

Source location: `common.handles.repo_pickles_url`
(`https://storage.googleapis.com/open-ff-common/repos/current_repo/pickles/`)

Primary join key linking `disclosures` and `chemrecs`: **`DisclosureId`**
Primary join key linking `bgCAS` and `chemrecs`: **`bgCAS`**


Approximate scale:
- 100k–500k disclosure records
- ~50 chemical records per disclosure (~5–25M chemical rows total)
- ~1,500 distinct bgCAS values

---

## Output files to create

All outputs go to a new GCS subfolder: `gs://open-ff-query-layer/v1/`

### Tier 1 — Index files (small, cached by apps on startup)

**`index.parquet`** (~5 MB)
One row per disclosure. Minimum columns:
- `DisclosureId`
- `bgStateName`
- `bgCountyName`
- `date` (or equivalent date field)
- `OperatorName`
- `WellName`
- `APINumber`

**`chem_index.parquet`** (~2–4 MB)
One row per bgCAS. Columns:
- `bgCAS`
- `bgIngredientName`
- `disclosure_count` — number of distinct disclosures using this chemical
- `state_count` — number of distinct states
- `conc_valid_count` — records where concentration is usable
- `conc_pct_valid` — fraction of records with valid concentration (0.0–1.0)
- `conc_valid_max`, `conc_valid_min`, `conc_valid_median`
- `conc_flagged_count`
- `conc_missing_count`
- `mass_valid_count`
- `mass_pct_valid`
- `mass_valid_max`, `mass_valid_min`, `mass_valid_median`
- `mass_flagged_count`
- `mass_missing_count`

Note: concentration quality flag (`conc_quality`) does not yet exist in the
current data. For the initial implementation, treat all non-null concentration
values as valid and null values as missing. The flag column will be added during
a later build pipeline refactor.

### Tier 2 — Disclosures partitioned by DisclosureId hash

256 files: `disclosures/part_000.parquet` … `disclosures/part_255.parquet`

Partition assignment:
```python
import hashlib

def key_to_bucket(disclosure_key, n=256):
    return int(hashlib.md5(str(disclosure_key).encode()).hexdigest(), 16) % n
```

Use this exact function in both the build script and in any app that queries
these files — it must be consistent. Each file contains all disclosure rows
whose DisclosureId maps to that bucket.

### Tier 3 — Chemicals partitioned by bgCAS

One file per bgCAS: `chemicals_by_cas/cas_{bgCAS}.parquet`
- Replace `/` with `-` in bgCAS for safe filenames
- Each file contains all chemical rows for that bgCAS across all disclosures
- Retain all columns from `chemrecs.parquet` including any quality flags
- Do not pre-filter by quality — apps filter at query time

### Build manifest

Write `manifest.json` at the end of a successful build:
```json
{
  "build_timestamp": "2025-01-01T00:00:00Z",
  "disclosure_count": 123456,
  "chemical_count": 6172800,
  "bgcas_count": 1500,
  "partition_count": 256,
  "query_layer_version": "v1"
}
```

---

## Tech stack

- Python 3.x
- `pandas` and `pyarrow` — already in use, preferred for Parquet I/O
- `google-cloud-storage` — for GCS upload
- `duckdb` — not yet used but target query engine for apps; partition design
  must be compatible with DuckDB's `read_parquet()` over HTTP

## How apps will query this layer

```python
import duckdb, hashlib

def key_to_bucket(k, n=256):
    return int(hashlib.md5(str(k).encode()).hexdigest(), 16) % n

bucket = "https://storage.googleapis.com/open-ff-query-layer/v1"
key = "some_disclosure_key"
b = key_to_bucket(key)

disc = duckdb.query(f"""
    SELECT * FROM read_parquet('{bucket}/disclosures/part_{b:03d}.parquet')
    WHERE DisclosureId = '{key}'
""").df()

chems = duckdb.query(f"""
    SELECT * FROM read_parquet('{bucket}/chemicals_by_cas/cas_{cas}.parquet')
    WHERE DisclosureId = '{key}'
""").df()

# Chemical deep-dive (tier 3)
cas = "7647-01-0"
all_uses = duckdb.query(f"""
    SELECT * FROM read_parquet('{bucket}/chemicals_by_cas/cas_{cas}.parquet')
""").df()
```

---

## Design principles

- **Additive only** — never modify or delete existing bulk files
- **Backward compatible** — existing tools keep working throughout
- **Deterministic partitioning** — MD5-based `key_to_bucket()` is the single
  source of truth; used identically by build and query code
- **Quality-aware** — retain quality flags on all raw rows; pre-compute
  quality-stratified stats in index files; let apps decide how to display
- **Versioned output folder** — use `query-layer/v1/` so future schema changes
  can go to `v2/` without breaking apps on `v1/`

---

## Suggested build order

1. Build and upload `index.parquet` — simplest, immediately useful
2. Build and upload `chem_index.parquet` — requires quality-aware aggregation
3. Build and upload `disclosures/part_*.parquet` — 256 files
4. Build and upload `chemicals_by_cas/cas_*.parquet` — ~1500 files
5. Write and upload `manifest.json`

Test each tier independently before proceeding to the next.

---

## Notes on future refactor

The main Open-FF build pipeline is being refactored separately. When that
refactor is complete it will introduce proper `conc_quality` flags alongside
the existing `mass_quality` flags. At that point, rerun `build_query_layer.py`
against the new bulk files — the script should require only minor updates to
handle the new flag columns. The query layer folder can be bumped to `v2/` at
that point if the schema changes.