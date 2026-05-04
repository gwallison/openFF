"""
build_wbd.py — Extract WBD HUC boundary layers from the USGS national GDB
and upload one GeoParquet per HUC scale to GCS.

Run once locally. Downloads the USGS WBD GDB zip (~2.8 GB), extracts the
needed HUC layers, uploads minimal GeoParquet files to GCS, then cleans up.

Usage:
    python qlayer/build_wbd.py            # all 6 HUC scales
    python qlayer/build_wbd.py --huc 10   # single scale

Output: gs://open-ff-query-layer/v1/wbd/huc{scale}.parquet
Columns: geometry (EPSG:4326), name, huc{scale}
"""

import argparse
import io
import os
import shutil
import tempfile
import zipfile

import geopandas as gpd
import requests
from google.cloud import storage

WBD_ZIP_URL = (
    "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD"
    "/National/GDB/WBD_National_GDB.zip"
)
GDB_NAME = "WBD_National_GDB.gdb"
HUC_SCALES = [2, 4, 6, 8, 10, 12]
DEST_BUCKET = "open-ff-query-layer"
DEST_PREFIX = "v1/wbd"


def download_zip(dest_path: str) -> None:
    print(f"Downloading WBD GDB zip to {dest_path} ...")
    with requests.get(WBD_ZIP_URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"  {downloaded/1e9:.2f} / {total/1e9:.2f} GB  ({pct:.0f}%)", end="\r")
    print(f"\nDownload complete: {downloaded/1e9:.2f} GB")


def extract_zip(zip_path: str, dest_dir: str) -> str:
    print("Extracting zip...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    gdb_path = os.path.join(dest_dir, GDB_NAME)
    print(f"Extracted to {gdb_path}")
    return gdb_path


def upload_gdf(client: storage.Client, blob_path: str, gdf: gpd.GeoDataFrame) -> None:
    buf = io.BytesIO()
    gdf.to_parquet(buf, index=False)
    size_mb = buf.tell() / 1_048_576
    buf.seek(0)
    blob = client.bucket(DEST_BUCKET).blob(blob_path)
    blob.upload_from_file(buf, content_type="application/octet-stream")
    print(f"  uploaded gs://{DEST_BUCKET}/{blob_path}  "
          f"({len(gdf):,} features, {size_mb:.1f} MB)")


def build_huc(scale: int, gdb_path: str, client: storage.Client,
              tolerance: float = 0.005) -> None:
    """
    tolerance: geometry simplification in degrees (~111m at equator).
    Sufficient for point-in-polygon and map display; reduces file size ~20x.
    """
    layer = f"WBDHU{scale}"
    huc_col = f"huc{scale}"
    print(f"\n-- HUC{scale}: reading {layer} from GDB...")
    gdf = gpd.read_file(gdb_path, layer=layer)
    gdf = gdf[[huc_col, "name", "geometry"]].copy().to_crs(4326)
    before = len(gdf)
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    # Drop any features that degenerated to empty after simplification
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
    print(f"  simplified {before} -> {len(gdf)} features (tolerance={tolerance}°)")
    blob_path = f"{DEST_PREFIX}/huc{scale}.parquet"
    upload_gdf(client, blob_path, gdf)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--huc", type=int, choices=HUC_SCALES,
                        help="Build a single HUC scale (default: all)")
    args = parser.parse_args()
    scales = [args.huc] if args.huc else HUC_SCALES

    client = storage.Client()

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "WBD_National_GDB.zip")
        download_zip(zip_path)
        gdb_path = extract_zip(zip_path, tmpdir)

        for scale in scales:
            build_huc(scale, gdb_path, client)

    print("\nDone. Temp files cleaned up.")


if __name__ == "__main__":
    main()
