"""
Download ACS 2007-2011 and 2015-2019 county-level data via Census API.
Extracts: poverty, income, net migration, employment rates.
Output: CSV files to data/raw/acs_extracts/
"""

import requests
import pandas as pd
import numpy as np
from pathlib import Path
import json


def load_api_key() -> str:
    """Load Census API key from .census_api_key file."""
    key_file = Path(__file__).parent / ".census_api_key"

    if not key_file.exists():
        raise FileNotFoundError(
            f"Census API key not found at {key_file}\n"
            f"Create file with your API key (https://api.census.gov/data/key_signup.html)"
        )

    key = key_file.read_text().strip()
    if not key:
        raise ValueError("API key file is empty")

    print(f"[OK] Loaded Census API key")
    return key


def get_acs_variables() -> dict:
    """
    Map ACS variables needed for analysis.
    Using ACS 5-year estimates.

    Returns:
        Dict of {variable_name: acs_code}
    """
    return {
        'B17001_002E': 'poverty_below_threshold',  # Total population for whom poverty determined
        'B17001_002EA': 'poverty_below_threshold_moe',
        'B19013_001E': 'median_hh_income',  # Median household income
        'B19013_001EA': 'median_hh_income_moe',
        'B01003_001E': 'population_total',  # Total population
        'B01003_001EA': 'population_total_moe',
        'B23025_004E': 'employed_civilian',  # Employed civilian labor force
        'B23025_004EA': 'employed_civilian_moe',
        'B23025_005E': 'unemployed_civilian',  # Unemployed civilian labor force
        'B23025_005EA': 'unemployed_civilian_moe',
        'B07001_017E': 'moved_in_past_year',  # Moved in past year (net migration proxy)
        'B07001_017EA': 'moved_in_past_year_moe',
    }


def fetch_acs_data(year_final: int, api_key: str) -> pd.DataFrame:
    """
    Fetch ACS 5-year estimates for given final year.

    Args:
        year_final: Final year of ACS estimate (2011 for 2007-2011, 2019 for 2015-2019)
        api_key: Census API key

    Returns:
        DataFrame with county-level data
    """
    # ACS 5-year dataset naming
    dataset = f"acs/acs5"
    year = year_final

    variables = get_acs_variables()
    var_string = ",".join(variables.keys())

    # Census API endpoint
    base_url = "https://api.census.gov/data/{year}/{dataset}".format(year=year, dataset=dataset)

    params = {
        'get': f'NAME,{var_string}',
        'for': 'county:*',
        'in': 'state:*',
        'key': api_key,
    }

    print(f"\nFetching ACS {year_final} (estimate {year_final - 4}-{year_final})...")
    print(f"  Variables: {len(variables)}")
    print(f"  Geography: All US counties")

    try:
        response = requests.get(base_url, params=params, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

    data = response.json()

    if not data or len(data) < 2:
        raise ValueError(f"No data returned from Census API for year {year_final}")

    # Convert to DataFrame
    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)
    print(f"  Retrieved {len(df):,} counties")

    # Clean and process
    df['year'] = year_final
    df['GEOID'] = df['state'] + df['county']

    return df


def process_acs_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw Census API response into analysis format.

    Args:
        df: Raw ACS data from API

    Returns:
        Processed DataFrame with poverty_rate, median_income, etc.
    """
    # Convert to numeric (Census returns as strings)
    numeric_cols = [col for col in df.columns if col.endswith('E') or col.endswith('EA')]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate rates
    # Poverty rate: population below poverty / total population
    df['poverty_rate'] = (df['B17001_002E'] / df['B01003_001E']) * 100

    # Median household income (already in dollars)
    df['median_hh_income'] = df['B19013_001E']

    # Employment rate: employed / (employed + unemployed)
    df['labor_force'] = df['B23025_004E'] + df['B23025_005E']
    df['employment_rate'] = (df['B23025_004E'] / df['labor_force']) * 100

    # Net migration: proxy using "moved in past year" (imperfect, but ACS limitation)
    # Note: This is NOT true net migration; it's fraction who moved in past year
    # Will use as exploratory outcome with caveat
    df['net_migration_rate'] = (df['B07001_017E'] / df['B01003_001E']) * 100

    # Keep relevant columns
    result = df[[
        'GEOID', 'year', 'NAME',
        'poverty_rate', 'median_hh_income', 'employment_rate', 'net_migration_rate',
        'B01003_001E',  # Population (for weights/checks)
    ]].copy()

    result.columns = ['GEOID', 'year', 'county_name', 'poverty_rate', 'median_hh_income',
                      'employment_rate', 'net_migration_rate', 'population']

    # Validate
    result['poverty_rate'] = result['poverty_rate'].clip(0, 100)
    result['employment_rate'] = result['employment_rate'].clip(0, 100)

    return result


def save_acs_data(df: pd.DataFrame, year_final: int) -> Path:
    """Save processed ACS data to CSV."""
    out_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "acs_extracts"
    out_file = out_dir / f"acs_{year_final}_extract.csv"

    df.to_csv(out_file, index=False)
    print(f"  [OK] Saved: {out_file}")

    return out_file


def main():
    """Download and process ACS data."""
    print("=" * 60)
    print("ACS DATA DOWNLOAD: Census API")
    print("=" * 60)

    api_key = load_api_key()

    # Download both years
    dfs = []
    for year in [2011, 2019]:
        try:
            raw = fetch_acs_data(year, api_key)
            processed = process_acs_data(raw)
            save_acs_data(processed, year)
            dfs.append(processed)
        except Exception as e:
            print(f"ERROR fetching year {year}: {e}")
            raise

    # Summary
    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nDownload Summary:")
    print(f"  Total obs: {len(combined):,}")
    print(f"  Years: {sorted(combined['year'].unique())}")
    print(f"  Counties: {combined['GEOID'].nunique():,}")
    print(f"\nData Quality Checks:")
    print(f"  Poverty rate range: {combined['poverty_rate'].min():.1f}% – {combined['poverty_rate'].max():.1f}%")
    print(f"  Median income range: ${combined['median_hh_income'].min():,.0f} – ${combined['median_hh_income'].max():,.0f}")
    print(f"  Employment rate range: {combined['employment_rate'].min():.1f}% – {combined['employment_rate'].max():.1f}%")
    print(f"  Missingness: {combined.isnull().sum().sum():,} missing values")

    print(f"\n[OK] ACS download complete via Census API")


if __name__ == "__main__":
    main()
