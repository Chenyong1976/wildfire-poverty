"""
Assign treatment status (early cohort: 2012-2015, late cohort: 2016-2019, never-treated).
Input: MTBS fire perimeters shapefile.
Output: fire_treatment_assignment.parquet with treatment indicators and fire dose metrics.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path


def load_mtbs_perimeters() -> gpd.GeoDataFrame:
    """
    Load MTBS fire perimeters from shapefile.

    Returns:
        GeoDataFrame with fire perimeters (columns: year, acres, geometry)
    """
    paths_to_check = [
        Path(__file__).parent.parent.parent / "data" / "raw" / "mtbs_perimeters",
        Path(__file__).parent.parent.parent.parent / "wildfire-finance" / "data" / "raw" / "mtbs_perims",
    ]

    for path in paths_to_check:
        # Try different filename patterns
        for shp_file in path.glob("*.shp"):
            if "mtbs" in shp_file.name.lower() or "boundary" in shp_file.name.lower():
                print(f"Loading MTBS from: {shp_file}")
                mtbs = gpd.read_file(shp_file)

                # Standardize column names if needed
                if 'year' not in mtbs.columns:
                    if 'YEAR' in mtbs.columns:
                        mtbs['year'] = mtbs['YEAR']
                    elif 'year_' in mtbs.columns:
                        mtbs['year'] = mtbs['year_']

                if 'acres' not in mtbs.columns:
                    if 'ACRES' in mtbs.columns:
                        mtbs['acres'] = mtbs['ACRES']
                    elif 'AREA' in mtbs.columns:
                        mtbs['acres'] = mtbs['AREA']

                return mtbs

    raise FileNotFoundError(
        f"MTBS shapefile not found in {paths_to_check}\n"
        f"Download from https://www.mtbs.gov/"
    )


def load_county_boundaries() -> gpd.GeoDataFrame:
    """
    Load US county boundaries.

    Returns:
        GeoDataFrame with counties (columns: GEOID, geometry)
    """
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "county_shapefiles"

    # Find any shapefile matching county pattern
    shp_files = list(raw_dir.glob("*county*.shp"))
    if not shp_files:
        raise FileNotFoundError(
            f"County shapefile not found in {raw_dir}\n"
            f"Download from https://www.census.gov/cgi-bin/geo/shapefiles/"
        )

    shp_file = shp_files[0]
    print(f"  Loading counties from: {shp_file.name}")

    counties = gpd.read_file(shp_file)
    # Standardize to GEOID
    if 'GEOID' not in counties.columns and 'STATEFP' in counties.columns:
        counties['GEOID'] = counties['STATEFP'] + counties['COUNTYFP']

    # Keep only lower-48 (exclude AK=02, HI=15, PR=72)
    counties = counties[~counties['STATEFP'].isin(['02', '15', '72'])].copy()

    print(f"Loaded {len(counties):,} counties (lower-48)")
    return counties


def assign_treatment_by_county(fires: gpd.GeoDataFrame, counties: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Assign each county to treatment cohort based on first large fire (>=1000 acres).

    Args:
        fires: MTBS fire perimeters
        counties: County boundaries

    Returns:
        DataFrame with GEOID, early_treated, late_treated, fire_year, fire_count, acres_burned
    """
    # Standardize acres column
    if 'ACRES' in fires.columns:
        fires['acres'] = fires['ACRES']

    # Filter to fires >=1000 acres
    fires_filtered = fires[fires['acres'] >= 1000].copy()
    print(f"MTBS fires >= 1000 acres: {len(fires_filtered):,}")

    # Spatial join: find which fires overlap with which counties
    fire_county = gpd.sjoin(fires_filtered, counties[['GEOID', 'geometry']], how='left')

    # Standardize year column name
    if 'YEAR' in fire_county.columns:
        fire_county['year'] = fire_county['YEAR']

    # For each county, find first fire year (1990-2019)
    fire_county_agg = fire_county.groupby('GEOID').agg({
        'year': 'min',  # First fire year
    }).reset_index()
    fire_county_agg.columns = ['GEOID', 'first_fire_year']

    # Assign cohort
    fire_county_agg['early_treated'] = (fire_county_agg['first_fire_year'] >= 2012) & \
                                       (fire_county_agg['first_fire_year'] <= 2015)
    fire_county_agg['late_treated'] = (fire_county_agg['first_fire_year'] >= 2016) & \
                                      (fire_county_agg['first_fire_year'] <= 2019)
    fire_county_agg['never_treated'] = (fire_county_agg['first_fire_year'].isna()) | \
                                       ((fire_county_agg['first_fire_year'] < 2012) |
                                        (fire_county_agg['first_fire_year'] > 2019))

    # Convert to 0/1
    fire_county_agg['early_treated'] = fire_county_agg['early_treated'].astype(int)
    fire_county_agg['late_treated'] = fire_county_agg['late_treated'].astype(int)

    # Add counties with no fires
    treated_geoids = set(fire_county_agg['GEOID'])
    all_geoids = set(counties['GEOID'])
    untreated_geoids = all_geoids - treated_geoids

    untreated = pd.DataFrame({
        'GEOID': list(untreated_geoids),
        'first_fire_year': np.nan,
        'early_treated': 0,
        'late_treated': 0,
        'never_treated': 1,
    })

    treatment = pd.concat([fire_county_agg, untreated], ignore_index=True)

    # Calculate fire dose (count and acres) by treatment window
    treatment['fire_count_early'] = 0
    treatment['acres_burned_early'] = 0.0
    treatment['fire_count_late'] = 0
    treatment['acres_burned_late'] = 0.0

    for _, fire_row in fire_county[fire_county['year'].between(2012, 2015)].iterrows():
        geoid = fire_row['GEOID']
        if geoid in treatment['GEOID'].values:
            idx = treatment[treatment['GEOID'] == geoid].index[0]
            treatment.loc[idx, 'fire_count_early'] += 1
            treatment.loc[idx, 'acres_burned_early'] += fire_row['acres']

    for _, fire_row in fire_county[fire_county['year'].between(2016, 2019)].iterrows():
        geoid = fire_row['GEOID']
        if geoid in treatment['GEOID'].values:
            idx = treatment[treatment['GEOID'] == geoid].index[0]
            treatment.loc[idx, 'fire_count_late'] += 1
            treatment.loc[idx, 'acres_burned_late'] += fire_row['acres']

    return treatment.sort_values('GEOID').reset_index(drop=True)


def validate_treatment(df: pd.DataFrame) -> None:
    """Validate treatment assignment counts."""
    early = df['early_treated'].sum()
    late = df['late_treated'].sum()
    never = (df['early_treated'] == 0).sum() & (df['late_treated'] == 0).sum()

    print(f"\nTreatment assignment:")
    print(f"  Early-treated (2012-2015): {early:,}")
    print(f"  Late-treated (2016-2019): {late:,}")
    print(f"  Never-treated: ~{never:,}")
    print(f"  Total: {len(df):,}")

    if early < 20:
        print(f"\n  WARNING: Early cohort small ({early}); may indicate fire data issue")
    if late < 10:
        print(f"  WARNING: Late cohort small ({late}); may indicate fire data issue")


def main():
    """Assign treatment and output."""
    print("=" * 60)
    print("TREATMENT ASSIGNMENT: Fire Cohorts")
    print("=" * 60)

    fires = load_mtbs_perimeters()
    counties = load_county_boundaries()

    treatment = assign_treatment_by_county(fires, counties)
    validate_treatment(treatment)

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "fire_treatment_assignment.parquet"

    treatment.to_parquet(out_file, index=False)
    print(f"\n[OK] Saved: {out_file}")


if __name__ == "__main__":
    main()
