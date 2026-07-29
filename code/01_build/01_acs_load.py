"""
Load and clean ACS 5-year estimates (2007-2011, 2015-2019) from IPUMS exports.
Outputs: poverty_rate, median_hh_income, net_migration_rate, employment_rate by county-year.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_acs_raw(survey_year: int) -> pd.DataFrame:
    """
    Load raw ACS 5-year extract from IPUMS CSV.

    Args:
        survey_year: Final year of ACS estimate (2011 for 2007-2011, 2019 for 2015-2019)

    Returns:
        DataFrame with county-level observations
    """
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "acs_extracts"

    # IPUMS filename convention: usa_00XXX.csv where XXX is extraction #
    # ADJUST THIS to match your actual IPUMS extract filename
    filepath = raw_dir / f"acs_{survey_year}_extract.csv"

    if not filepath.exists():
        raise FileNotFoundError(
            f"ACS extract not found: {filepath}\n"
            f"Download from IPUMS (https://usa.ipums.org/) and save as: "
            f"data/raw/acs_extracts/acs_{{survey_year}}_extract.csv"
        )

    df = pd.read_csv(filepath, dtype={'COUNTYFIP': str})
    df['year'] = survey_year

    print(f"Loaded ACS {survey_year}: {len(df):,} rows")
    return df


def aggregate_to_county(df: pd.DataFrame, survey_year: int) -> pd.DataFrame:
    """
    Aggregate individual-level ACS data to county level.

    Args:
        df: Individual-level ACS records
        survey_year: Final year of survey

    Returns:
        County-level aggregated data
    """
    county = df.groupby('COUNTYFIP').agg({
        'POVERTY': lambda x: (x == 1).sum() / len(x) * 100,  # % below poverty line
        'HHINCOME': 'median',
        'MIGRATE1': lambda x: (x == 1).sum() / len(x) * 100,  # % who moved 1yr ago (proxy for net migration)
        'EMPSTAT': lambda x: (x == 1).sum() / len(x) * 100,  # % employed
    }).reset_index()

    county.columns = ['GEOID', 'poverty_rate', 'median_hh_income', 'net_migration_rate', 'employment_rate']
    county['year'] = survey_year
    county['GEOID'] = county['GEOID'].str.zfill(5)  # Ensure 5-digit FIPS

    # Flag data quality issues
    county['poverty_missing'] = county['poverty_rate'].isna().astype(int)
    county['income_missing'] = county['median_hh_income'].isna().astype(int)

    return county


def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate county-level aggregates and flag outliers.

    Args:
        df: County-level data

    Returns:
        Cleaned DataFrame with quality flags
    """
    df = df.copy()

    # Expected ranges
    assert (df['poverty_rate'] >= 0) & (df['poverty_rate'] <= 100).all(), "Poverty rate out of range"
    assert (df['employment_rate'] >= 0) & (df['employment_rate'] <= 100).all(), "Employment rate out of range"
    assert (df['median_hh_income'] >= 0).all(), "Income cannot be negative"

    # Flag high missingness
    df['high_missingness'] = (df['poverty_missing'] | df['income_missing']).astype(int)

    missing_summary = df[['year', 'poverty_missing', 'income_missing']].sum()
    print(f"\nMissingness summary:\n{missing_summary}\n")

    return df


def main():
    """Load and combine ACS 2007-2011 and 2015-2019."""

    dfs = []
    for year in [2011, 2019]:
        try:
            raw = load_acs_raw(year)
            county = aggregate_to_county(raw, year)
            county = clean_and_validate(county)
            dfs.append(county)
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
    print(f"\n✓ Saved: {out_file}")
    print(f"  Shape: {result.shape}")
    print(f"  Years: {sorted(result['year'].unique())}")
    print(f"  Counties: {result['GEOID'].nunique():,}")


if __name__ == "__main__":
    main()
