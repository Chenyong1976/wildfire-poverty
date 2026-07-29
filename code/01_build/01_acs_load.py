"""
Load and clean ACS county-level data from Census API exports.
Outputs: poverty_rate, median_hh_income, net_migration_rate, employment_rate by county-year.
Note: Data already aggregated to county level by 01a_acs_api_download.py
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_acs_raw(survey_year: int) -> pd.DataFrame:
    """
    Load county-level ACS 5-year extract from Census API CSV.

    Args:
        survey_year: Final year of ACS estimate (2011 for 2007-2011, 2019 for 2015-2019)

    Returns:
        DataFrame with county-level observations
    """
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "acs_extracts"
    filepath = raw_dir / f"acs_{survey_year}_extract.csv"

    if not filepath.exists():
        raise FileNotFoundError(
            f"ACS extract not found: {filepath}\n"
            f"Run 01a_acs_api_download.py first to fetch data from Census API"
        )

    df = pd.read_csv(filepath)
    print(f"Loaded ACS {survey_year}: {len(df):,} counties")
    return df


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate county-level data and ensure correct format.

    Args:
        df: County-level ACS data (already aggregated)

    Returns:
        Cleaned DataFrame with quality flags
    """
    df = df.copy()

    # Ensure GEOID is string and 5-digit
    df['GEOID'] = df['GEOID'].astype(str).str.zfill(5)

    # Validate ranges
    assert ((df['poverty_rate'] >= 0) & (df['poverty_rate'] <= 100)).all(), "Poverty rate out of range"
    assert ((df['employment_rate'] >= 0) & (df['employment_rate'] <= 100)).all(), "Employment rate out of range"
    assert (df['median_hh_income'] >= 0).all(), "Income cannot be negative"

    # Flag data quality issues
    df['poverty_missing'] = df['poverty_rate'].isna().astype(int)
    df['income_missing'] = df['median_hh_income'].isna().astype(int)

    missing_summary = df[['year', 'poverty_missing', 'income_missing']].sum()
    print(f"\nMissingness summary:\n{missing_summary}\n")

    return df


def main():
    """Load and combine ACS 2007-2011 and 2015-2019."""
    print("=" * 60)
    print("ACS DATA LOAD & VALIDATION")
    print("=" * 60)

    dfs = []
    for year in [2011, 2019]:
        try:
            raw = load_acs_raw(year)
            cleaned = validate_and_clean(raw)
            dfs.append(cleaned)
        except FileNotFoundError as e:
            print(f"Error for year {year}: {e}")
            continue

    if not dfs:
        print("ERROR: No ACS data loaded. Check data/raw/acs_extracts/ for files.")
        return

    result = pd.concat(dfs, ignore_index=True)

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "acs_county_outcomes.parquet"

    result.to_parquet(out_file, index=False)
    print(f"\n[OK] Saved: {out_file}")
    print(f"  Shape: {result.shape}")
    print(f"  Years: {sorted(result['year'].unique())}")
    print(f"  Counties: {result['GEOID'].nunique():,}")


if __name__ == "__main__":
    main()
