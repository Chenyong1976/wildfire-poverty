"""
Assemble baseline covariates for propensity-score matching.
Input: ACS 2007-2011 county data, USDA RUCC, WFP 2012 raster.
Output: matching_covariates_2012.parquet
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import rasterio
import rasterio.mask
from shapely.geometry import box


def load_acs_baseline() -> pd.DataFrame:
    """Load ACS 2007-2011 outcomes (reuse from 01_acs_load.py output)."""
    processed = Path(__file__).parent.parent.parent / "data" / "processed"
    acs_file = processed / "acs_county_outcomes.parquet"

    if not acs_file.exists():
        raise FileNotFoundError(f"Run 01_acs_load.py first to generate {acs_file}")

    acs = pd.read_parquet(acs_file)
    baseline = acs[acs['year'] == 2011][['GEOID', 'poverty_rate', 'median_hh_income']].copy()
    baseline.columns = ['GEOID', 'baseline_poverty_rate', 'baseline_median_hh_income']

    return baseline


def load_rucc() -> pd.DataFrame:
    """
    Load USDA Rural-Urban Continuum Code (2013 vintage).
    Download from: https://www.ers.usda.gov/webdocs/DataFiles/17749/ruralurbancodes2013.xls
    """
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    rucc_file = raw_dir / "ruralurbancodes2013.xlsx"

    if not rucc_file.exists():
        print(f"WARNING: RUCC file not found at {rucc_file}")
        print("Download from https://www.ers.usda.gov/webdocs/DataFiles/17749/")
        return pd.DataFrame()  # Return empty; will skip RUCC

    rucc = pd.read_excel(rucc_file, sheet_name='Codes')
    # Standardize FIPS to 5-digit GEOID
    rucc['GEOID'] = rucc['FIPS'].astype(str).str.zfill(5)

    return rucc[['GEOID', 'RUCC_2013']].rename(columns={'RUCC_2013': 'rucc'})


def load_county_attributes() -> pd.DataFrame:
    """
    Load county population density and demographics from Census.
    For now, use ACS 2007-2011 as proxy.
    """
    processed = Path(__file__).parent.parent.parent / "data" / "processed"
    acs_file = processed / "acs_county_outcomes.parquet"

    acs = pd.read_parquet(acs_file)
    baseline = acs[acs['year'] == 2011][['GEOID']].copy()

    # TODO: Add population, area, density from Census geographic data
    # For now, placeholder—will need county land area from TIGER

    return baseline


def load_wfp_2012_county() -> pd.DataFrame:
    """
    Aggregate WFP 2012 raster to county level (quintile).
    Input: WFP 2012 raster from code/01_build/03b_wfp_to_county.py
    """
    processed = Path(__file__).parent.parent.parent / "data" / "processed"
    wfp_file = processed / "whp_2012_county.parquet"

    if not wfp_file.exists():
        print(f"WARNING: WFP 2012 county file not found at {wfp_file}")
        print("Run 03b_wfp_to_county.py first.")
        return pd.DataFrame()

    return pd.read_parquet(wfp_file)


def load_pre2012_fire_history() -> pd.DataFrame:
    """
    Load fire history covariates (1984-2011).
    Input: Output from code/01_build/02b_fire_history.py
    """
    processed = Path(__file__).parent.parent.parent / "data" / "processed"
    fire_file = processed / "pre2012_fire_history.parquet"

    if not fire_file.exists():
        print(f"WARNING: Pre-2012 fire history not found at {fire_file}")
        print("Run 02b_fire_history.py first.")
        return pd.DataFrame()

    return pd.read_parquet(fire_file)


def merge_covariates(baseline: pd.DataFrame, rucc: pd.DataFrame,
                     wfp: pd.DataFrame, fire_hist: pd.DataFrame) -> pd.DataFrame:
    """Merge all covariates into single table."""
    covariates = baseline.copy()

    if not rucc.empty:
        covariates = covariates.merge(rucc, on='GEOID', how='left')
    else:
        covariates['rucc'] = np.nan

    if not wfp.empty:
        covariates = covariates.merge(wfp[['GEOID', 'wfp_quintile']], on='GEOID', how='left')
    else:
        covariates['wfp_quintile'] = np.nan

    if not fire_hist.empty:
        covariates = covariates.merge(fire_hist, on='GEOID', how='left')
    else:
        covariates['pre2012_fire_count'] = np.nan
        covariates['pre2012_acres_burned'] = np.nan

    return covariates


def validate_covariates(df: pd.DataFrame) -> None:
    """Check for missing values and ranges."""
    print("\nCovariate missingness:")
    print(df.isnull().sum())

    print("\nCovariate summary statistics:")
    print(df.describe())


def main():
    """Assemble matching covariates."""
    print("=" * 60)
    print("MATCHING COVARIATES: Assembly")
    print("=" * 60)

    baseline = load_acs_baseline()
    rucc = load_rucc()
    wfp = load_wfp_2012_county()
    fire_hist = load_pre2012_fire_history()

    covariates = merge_covariates(baseline, rucc, wfp, fire_hist)
    validate_covariates(covariates)

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "matching_covariates_2012.parquet"

    covariates.to_parquet(out_file, index=False)
    print(f"\n✓ Saved: {out_file}")
    print(f"  Shape: {covariates.shape}")


if __name__ == "__main__":
    main()
