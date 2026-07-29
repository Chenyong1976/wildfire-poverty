"""
Download MTBS and Census county boundaries shapefiles automatically.
Uses publicly available sources that don't require manual web interaction.
"""

import requests
import zipfile
import tempfile
from pathlib import Path
import sys


def download_file(url: str, dest_path: Path, description: str) -> bool:
    """
    Download file from URL with progress indicator.

    Args:
        url: URL to download from
        dest_path: Where to save file
        description: Description for logging

    Returns:
        True if successful
    """
    print(f"\nDownloading {description}...")
    print(f"  Source: {url}")

    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        sys.stdout.write(f'\r  Progress: {pct:.1f}% ({downloaded/1e6:.1f} MB)')
                        sys.stdout.flush()

        print(f"\n  [OK] Downloaded {downloaded/1e6:.1f} MB")
        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract zip file to directory."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        print(f"  [OK] Extracted to {extract_to}")
        return True
    except Exception as e:
        print(f"  ERROR extracting: {e}")
        return False


def download_mtbs(output_dir: Path) -> bool:
    """
    Download MTBS fire perimeters.
    Source: USGS via direct download link (requires ~300 MB)
    """
    print("\n" + "=" * 60)
    print("MTBS FIRE PERIMETERS DOWNLOAD")
    print("=" * 60)

    # MTBS data: This attempts to get the USGS-hosted data
    # If this URL is unavailable, user will need to visit https://www.mtbs.gov/
    url = "https://www.mtbs.gov/direct-download"

    print("\nMTBS requires manual download due to USGS hosting constraints.")
    print("Please download from: https://www.mtbs.gov/")
    print("  1. Go to https://www.mtbs.gov/viewer/")
    print("  2. Click 'Download' (or navigate to data download page)")
    print("  3. Select 'Fire Perimeters' shapefile")
    print("  4. Extract to:", output_dir)
    print("\nAlternatively, if you have GDAL/OGR installed:")
    print("  ogr2ogr can access MTBS WFS service directly")

    return False  # Return False since manual step required


def download_county_boundaries(output_dir: Path) -> bool:
    """
    Download Census county boundaries shapefile.
    Source: Census Bureau TIGER/Line via direct link.
    """
    print("\n" + "=" * 60)
    print("CENSUS COUNTY BOUNDARIES DOWNLOAD")
    print("=" * 60)

    # Census TIGER/Line: Available via direct HTTP link
    # Using 2023 vintage
    url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_20m.zip"

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_file = output_dir / "county_boundaries.zip"

    if download_file(url, zip_file, "Census county boundaries"):
        if extract_zip(zip_file, output_dir):
            zip_file.unlink()  # Clean up zip
            print(f"\n[OK] County boundaries ready at {output_dir}")
            return True

    return False


def download_mtbs_via_gdal(output_dir: Path) -> bool:
    """
    Attempt to download MTBS via WFS service if GDAL available.
    Fallback for programmatic access.
    """
    try:
        from osgeo import ogr
        print("GDAL detected; attempting WFS download...")

        # USGS MTBS WFS endpoint
        wfs_url = "WFS:https://www.mtbs.gov/geoserver/ows"
        driver = ogr.GetDriverByName('WFS')

        # This would require proper WFS layer name and connection
        # Implementation deferred as requires GDAL configuration
        print("(WFS download not fully implemented; please manually download)")
        return False

    except ImportError:
        return False


def main():
    """Download required shapefiles."""
    print("=" * 60)
    print("SHAPEFILE DOWNLOADS: MTBS & County Boundaries")
    print("=" * 60)

    base = Path(__file__).parent.parent.parent / "data" / "raw"

    # County boundaries (fully automated)
    county_dir = base / "county_shapefiles"
    county_success = download_county_boundaries(county_dir)

    # MTBS (requires manual step)
    mtbs_dir = base / "mtbs_perimeters"
    mtbs_dir.mkdir(parents=True, exist_ok=True)
    mtbs_success = download_mtbs(mtbs_dir)

    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"County boundaries: {'[OK]' if county_success else '[MANUAL REQUIRED]'}")
    print(f"MTBS perimeters:   [MANUAL REQUIRED - visit https://www.mtbs.gov/]")
    print("\nTo continue:")
    print("  1. Download MTBS from https://www.mtbs.gov/")
    print("  2. Extract to: data/raw/mtbs_perimeters/")
    print("  3. Re-run this script or proceed to next tasks")


if __name__ == "__main__":
    main()
