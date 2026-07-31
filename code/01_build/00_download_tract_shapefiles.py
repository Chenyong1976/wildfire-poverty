#!/usr/bin/env python3
"""
Download Census 2010 tract shapefiles (TIGER) for all lower-48 US states.

This script automates the download of Census tract boundary shapefiles from
the TIGER repository, filters to lower-48 states, and saves to the raw data
directory. It acts as a foundation for tract-level analysis.

Outputs:
  - data/raw/tract_shapefiles/tracts_2010.shp (+ .shx, .dbf, .prj, etc.)
"""

import os
import zipfile
from pathlib import Path
import requests
import geopandas as gpd

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "tract_shapefiles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Census TIGER tract shapefile URL (2010 vintage, 500k cartographic boundary)
# Using TIGER geodatabase files which have better national coverage
TIGER_URL = (
    "https://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_us_tract10.zip"
)

# Lower-48 state FIPS codes (exclude AK=02, HI=15, PR=72)
LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56"
}


def download_and_extract_shapefiles():
    """Download TIGER tract shapefiles and extract to output directory."""
    print("Downloading Census 2010 tract shapefiles (TIGER)...")

    # Download the zip file
    zip_path = OUTPUT_DIR / "tracts_2010_temp.zip"
    try:
        response = requests.get(TIGER_URL, stream=True, timeout=60)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Downloaded to {zip_path}")
    except requests.RequestException as e:
        print(f"Error downloading shapefile: {e}")
        return False

    # Extract the zip file
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)
        print(f"Extracted shapefile contents to {OUTPUT_DIR}")
        zip_path.unlink()  # Remove temporary zip file
    except zipfile.BadZipFile as e:
        print(f"Error extracting zip file: {e}")
        return False

    return True


def filter_to_lower_48():
    """Filter downloaded shapefile to lower-48 US states."""
    # Find the extracted shapefile
    shp_files = list(OUTPUT_DIR.glob("*.shp"))
    if not shp_files:
        print("Error: No shapefile found after extraction.")
        return False

    shp_path = shp_files[0]
    print(f"Loading shapefile: {shp_path}")

    try:
        tracts = gpd.read_file(shp_path)
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return False

    print(f"Loaded {len(tracts)} tracts (all states)")

    # Extract state FIPS from geometry properties or attributes
    # TIGER shapefiles typically have a 'STATEFP' column
    if "STATEFP" not in tracts.columns:
        print("Warning: STATEFP column not found. Checking available columns:")
        print(tracts.columns.tolist())
        return False

    # Filter to lower-48 states
    tracts_lower48 = tracts[tracts["STATEFP"].isin(LOWER_48_FIPS)].copy()
    print(f"Filtered to {len(tracts_lower48)} tracts in lower-48 states")

    # Construct 11-digit GEOID if not present
    if "GEOID" not in tracts_lower48.columns:
        if all(col in tracts_lower48.columns for col in ["STATEFP", "COUNTYFP", "TRACTCE"]):
            tracts_lower48["GEOID"] = (
                tracts_lower48["STATEFP"] +
                tracts_lower48["COUNTYFP"] +
                tracts_lower48["TRACTCE"]
            )
            print("Constructed 11-digit GEOID from state/county/tract FIPS")
        else:
            print("Warning: Cannot construct GEOID; missing FIPS columns")

    # Save to final shapefile
    output_shp = OUTPUT_DIR / "tracts_2010.shp"
    try:
        tracts_lower48.to_file(output_shp)
        print(f"Saved filtered shapefile to {output_shp}")
    except Exception as e:
        print(f"Error saving shapefile: {e}")
        return False

    # Clean up temporary files (extract detritus)
    for f in OUTPUT_DIR.glob("*.shp"):
        if f.name != "tracts_2010.shp":
            f.unlink()
    for f in OUTPUT_DIR.glob("*.shx"):
        if f.name != "tracts_2010.shx":
            f.unlink()
    for f in OUTPUT_DIR.glob("*.dbf"):
        if f.name != "tracts_2010.dbf":
            f.unlink()
    for f in OUTPUT_DIR.glob("*.prj"):
        if f.name != "tracts_2010.prj":
            f.unlink()

    return True


def verify_downloads():
    """Verify that downloads are complete and readable."""
    print("\nVerifying downloads...")

    required_files = ["tracts_2010.shp", "tracts_2010.shx", "tracts_2010.dbf", "tracts_2010.prj"]
    for fname in required_files:
        fpath = OUTPUT_DIR / fname
        if not fpath.exists():
            print(f"[MISSING] {fname}")
            return False
        print(f"[OK] {fname} ({fpath.stat().st_size / (1024**2):.1f} MB)")

    # Try to read the shapefile
    try:
        tracts = gpd.read_file(OUTPUT_DIR / "tracts_2010.shp")
        print(f"\n[OK] Successfully read shapefile: {len(tracts)} tracts")
        print(f"[OK] Columns: {tracts.columns.tolist()}")
        print(f"[OK] CRS: {tracts.crs}")
        return True
    except Exception as e:
        print(f"[ERROR] Error reading shapefile: {e}")
        return False


if __name__ == "__main__":
    import sys
    # Set output encoding to UTF-8 for Unicode characters
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=" * 80)
    print("DOWNLOAD CENSUS 2010 TRACT SHAPEFILES")
    print("=" * 80)

    success = download_and_extract_shapefiles()
    if success:
        success = filter_to_lower_48()

    if success:
        verify_downloads()
        print("\n[OK] Data acquisition complete.")
    else:
        print("\n[ERROR] Data acquisition failed.")
        exit(1)
