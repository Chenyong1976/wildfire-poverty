#!/usr/bin/env python3
"""
Download ACS 5-year tract-level data from Census API.

Downloads poverty, income, employment, and migration data for ACS periods:
2012, 2017, 2023 at census tract level for all lower-48 US states.

Requires Census API key (https://api.census.gov/data/key_signup.html)
"""

import os
import requests
import pandas as pd
from pathlib import Path
import time

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "acs_extracts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Census API base URL
CENSUS_API_URL = "https://api.census.gov/data"

# Lower-48 state FIPS codes
LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56"
}

# ACS variables mapping
# B17001: Poverty status in past 12 months
# B19013: Median household income in past 12 months
# B23025: Employment status for population 16 years and over
# B07001: Residence 1 year ago (for migration proxy)
VARIABLES = {
    "B17001_001E": "poverty_total",  # Total for poverty status
    "B17001_002E": "poverty_below_threshold",  # Income in past 12 months below poverty level
    "B17001_001M": "poverty_total_moe",
    "B17001_002M": "poverty_below_threshold_moe",
    "B19013_001E": "median_hh_income",
    "B19013_001M": "median_hh_income_moe",
    "B23025_001E": "labor_force_total",
    "B23025_002E": "labor_force_employed",
    "B23025_001M": "labor_force_total_moe",
    "B23025_002M": "labor_force_employed_moe",
    "B07001_001E": "residence_total",
    "B07001_002E": "residence_same_house_1yr",
    "B07001_001M": "residence_total_moe",
    "B07001_002M": "residence_same_house_moe",
}

ACS_YEARS = {
    2012: "acs5",     # 2008-2012 5-year estimate
    2017: "acs5",     # 2013-2017 5-year estimate
    2023: "acs5",     # 2019-2023 5-year estimate (released late 2024)
}


def get_census_api_key():
    """Get Census API key from environment or user input."""
    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        print("Census API key not found in CENSUS_API_KEY environment variable")
        print("Please set the environment variable or provide key interactively")
        api_key = input("Enter your Census API key: ").strip()
    return api_key


def build_variable_list():
    """Build comma-separated list of Census API variables."""
    return ",".join(VARIABLES.keys())


def download_acs_year(api_key, year, output_path):
    """Download ACS data for a specific year."""

    acs_type = ACS_YEARS.get(year)
    if not acs_type:
        print(f"[ERROR] ACS {year} not configured")
        return False

    # Build variable list
    var_list = build_variable_list()

    # Download data for each state (Census API requires state-by-state queries for national data)
    all_data = []

    for state_fips in sorted(LOWER_48_FIPS):
        print(f"[DOWNLOADING] ACS {year}, State FIPS {state_fips}...")

        # Census API query
        url = f"{CENSUS_API_URL}/{year}/{acs_type}"
        params = {
            "get": f"NAME,{var_list}",
            "for": f"tract:*",
            "in": f"state:{state_fips}",
            "key": api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Skip header row
            if len(data) > 1:
                # Convert to DataFrame
                df = pd.DataFrame(data[1:], columns=data[0])
                all_data.append(df)
                print(f"  [OK] Downloaded {len(df)} tracts from state {state_fips}")

            # Rate limiting: Census API recommends spacing requests
            time.sleep(0.5)

        except requests.RequestException as e:
            print(f"  [ERROR] Failed to download state {state_fips}: {e}")
            return False

    if not all_data:
        print(f"[ERROR] No data downloaded for ACS {year}")
        return False

    # Combine all states
    df_combined = pd.concat(all_data, ignore_index=True)

    # Construct 11-digit GEOID from state, county, tract
    df_combined["geoid"] = (
        df_combined["state"] +
        df_combined["county"] +
        df_combined["tract"]
    )

    # Rename columns to match variable names
    df_combined.rename(columns=VARIABLES, inplace=True)

    # Keep only essential columns
    keep_cols = ["geoid", "NAME"] + list(VARIABLES.values())
    df_combined = df_combined[[col for col in keep_cols if col in df_combined.columns]]

    # Save to CSV
    try:
        df_combined.to_csv(output_path, index=False)
        print(f"[OK] Saved ACS {year} data: {output_path}")
        print(f"  Total tracts: {len(df_combined)}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save ACS {year} data: {e}")
        return False


def main(api_key=None):
    """Download ACS data for all years."""

    print("=" * 80)
    print("DOWNLOAD ACS 5-YEAR TRACT-LEVEL DATA")
    print("=" * 80)

    if not api_key:
        api_key = get_census_api_key()

    success = True

    for year in sorted(ACS_YEARS.keys()):
        output_path = OUTPUT_DIR / f"acs_{year}_tract_extract.csv"

        if output_path.exists():
            print(f"\n[SKIP] ACS {year} already downloaded: {output_path}")
            continue

        print(f"\n[STARTING] ACS {year} download...")
        if not download_acs_year(api_key, year, output_path):
            success = False
            print(f"[FAILED] ACS {year} download failed")
        else:
            print(f"[SUCCESS] ACS {year} download complete")

    if success:
        print("\n[OK] All ACS downloads complete")
    else:
        print("\n[ERROR] Some ACS downloads failed")

    return success


if __name__ == "__main__":
    import sys

    # Accept API key as command-line argument for scripting
    api_key = sys.argv[1] if len(sys.argv) > 1 else None

    success = main(api_key)
    exit(0 if success else 1)
