"""
Create smoke buffer exclusion list: flag control counties within 100 km of fire perimeters.
Input: MTBS fire perimeters (2012-2019), county boundaries
Output: smoke_buffer_100km.parquet
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path


def load_mtbs_and_counties():
    """Load MTBS and county boundaries."""
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"

    # MTBS
    mtbs_path = raw_dir / "mtbs_perimeters"
    shp_file = list(mtbs_path.glob("*.shp"))[0] if mtbs_path.glob("*.shp") else None

    if not shp_file:
        raise FileNotFoundError(f"No shapefile found in {mtbs_path}")

    mtbs = gpd.read_file(shp_file)

    # Counties
    county_shp = list((raw_dir / "county_shapefiles").glob("*.shp"))[0]
    counties = gpd.read_file(county_shp)

    if 'GEOID' not in counties.columns and 'STATEFP' in counties.columns:
        counties['GEOID'] = counties['STATEFP'] + counties['COUNTYFP']

    counties = counties[~counties['STATEFP'].isin(['02', '15', '72'])].copy()

    # Ensure same CRS
    if mtbs.crs != counties.crs:
        mtbs = mtbs.to_crs(counties.crs)

    print(f"Loaded MTBS: {len(mtbs):,} fires")
    print(f"Loaded counties: {len(counties):,}")
    print(f"CRS: {counties.crs}")

    return mtbs, counties


def create_smoke_buffer(mtbs: gpd.GeoDataFrame, counties: gpd.GeoDataFrame, buffer_km: int = 100) -> pd.DataFrame:
    """
    Create buffer around all fires in 2012-2019 and flag counties within buffer.

    Args:
        mtbs: Fire perimeters
        counties: County boundaries
        buffer_km: Buffer distance in kilometers

    Returns:
        DataFrame with GEOID and within_buffer flag
    """
    # Filter to 2012-2019 fires
    fires = mtbs[(mtbs['year'] >= 2012) & (mtbs['year'] <= 2019)].copy()
    print(f"\nFires 2012-2019: {len(fires):,}")

    # Create buffer (in meters, since projection typically meters)
    buffer_m = buffer_km * 1000
    fires_buffered = fires.copy()
    fires_buffered['geometry'] = fires.geometry.buffer(buffer_m)

    print(f"Created {buffer_km} km buffer around fires")

    # Union all buffers into single polygon (for efficiency)
    buffered_union = fires_buffered.unary_union
    buffered_gdf = gpd.GeoDataFrame(geometry=[buffered_union], crs=fires_buffered.crs)

    # Spatial join: find counties within buffer
    counties_in_buffer = gpd.sjoin(counties, buffered_gdf, how='inner', predicate='intersects')

    within_buffer = set(counties_in_buffer['GEOID'])
    all_geoids = set(counties['GEOID'])

    # Create result
    result = pd.DataFrame({
        'GEOID': list(all_geoids),
        'within_smoke_buffer': [1 if g in within_buffer else 0 for g in all_geoids],
    })

    print(f"\nCounties within {buffer_km} km buffer: {result['within_smoke_buffer'].sum():,}")

    return result.sort_values('GEOID').reset_index(drop=True)


def main():
    """Create smoke buffer and save."""
    print("=" * 60)
    print("SMOKE BUFFER EXCLUSION: 100 km Buffer")
    print("=" * 60)

    mtbs, counties = load_mtbs_and_counties()
    smoke_buffer = create_smoke_buffer(mtbs, counties, buffer_km=100)

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "smoke_buffer_100km.parquet"

    smoke_buffer.to_parquet(out_file, index=False)
    print(f"\n[OK] Saved: {out_file}")


if __name__ == "__main__":
    main()
