"""
Calculate pre-2012 fire history covariates (fire count and acres burned, 1984-2011).
Input: MTBS fire perimeters (via 02_fire_treatment.py functions)
Output: pre2012_fire_history.parquet
"""

import geopandas as gpd
import pandas as pd
import numpy as np
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
    print(f"Loaded MTBS: {len(mtbs):,} fires")

    # Counties
    county_shp = list((raw_dir / "county_shapefiles").glob("*.shp"))[0]
    counties = gpd.read_file(county_shp)

    if 'GEOID' not in counties.columns and 'STATEFP' in counties.columns:
        counties['GEOID'] = counties['STATEFP'] + counties['COUNTYFP']

    # Keep lower-48
    counties = counties[~counties['STATEFP'].isin(['02', '15', '72'])].copy()
    print(f"Loaded {len(counties):,} counties (lower-48)")

    return mtbs, counties


def calculate_pre2012_fire_history(mtbs: gpd.GeoDataFrame, counties: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    For each county, count fires and acres burned in 1984-2011.

    Args:
        mtbs: Fire perimeters
        counties: County boundaries

    Returns:
        DataFrame with GEOID, fire_count, acres_burned for 1984-2011
    """
    # Filter to 1984-2011
    fires_pre = mtbs[(mtbs['year'] >= 1984) & (mtbs['year'] <= 2011)].copy()
    print(f"Fires 1984-2011: {len(fires_pre):,}")

    # Standardize acre column name (may vary: 'ACRES', 'acres', 'Acres')
    acre_cols = [col for col in fires_pre.columns if 'acre' in col.lower()]
    if acre_cols:
        fires_pre['acres'] = fires_pre[acre_cols[0]].astype(float)
    else:
        print("WARNING: No acres column found; using 0")
        fires_pre['acres'] = 0.0

    # Filter to >=1000 acres
    fires_pre = fires_pre[fires_pre['acres'] >= 1000].copy()
    print(f"After filtering to >=1000 acres: {len(fires_pre):,}")

    # Spatial join
    fire_county = gpd.sjoin(fires_pre, counties[['GEOID', 'geometry']], how='left')

    # Aggregate by county
    history = fire_county.groupby('GEOID').agg({
        'OBJECTID': 'count',  # Fire count
        'acres': 'sum',        # Total acres
    }).reset_index()

    history.columns = ['GEOID', 'pre2012_fire_count', 'pre2012_acres_burned']
    history['pre2012_fire_count'] = history['pre2012_fire_count'].astype(int)

    # Add counties with no fires
    all_geoids = set(counties['GEOID'])
    fire_geoids = set(history['GEOID'])
    no_fire_geoids = all_geoids - fire_geoids

    no_fire = pd.DataFrame({
        'GEOID': list(no_fire_geoids),
        'pre2012_fire_count': 0,
        'pre2012_acres_burned': 0.0,
    })

    result = pd.concat([history, no_fire], ignore_index=True).sort_values('GEOID').reset_index(drop=True)

    return result


def main():
    """Calculate and save pre-2012 fire history."""
    print("=" * 60)
    print("PRE-2012 FIRE HISTORY: Calculation")
    print("=" * 60)

    mtbs, counties = load_mtbs_and_counties()
    history = calculate_pre2012_fire_history(mtbs, counties)

    print(f"\nSummary:")
    print(f"  Counties with fires 1984-2011: {(history['pre2012_fire_count'] > 0).sum():,}")
    print(f"  Mean fires per county: {history['pre2012_fire_count'].mean():.2f}")
    print(f"  Mean acres per county: {history['pre2012_acres_burned'].mean():,.0f}")

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "pre2012_fire_history.parquet"

    history.to_parquet(out_file, index=False)
    print(f"\n[OK] Saved: {out_file}")


if __name__ == "__main__":
    main()
