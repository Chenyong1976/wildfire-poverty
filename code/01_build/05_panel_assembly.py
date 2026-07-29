"""
Assemble final balanced panel: merge outcomes, treatment, covariates, smoke buffer.
Inputs: All datasets from 01-04
Output: analysis_sample_final.parquet (~2,750 counties × 4 periods)
"""

import pandas as pd
from pathlib import Path


def load_all_datasets():
    """Load all processed datasets."""
    processed = Path(__file__).parent.parent.parent / "data" / "processed"

    print("Loading datasets...")

    # Outcomes (ACS)
    acs = pd.read_parquet(processed / "acs_county_outcomes.parquet")
    print(f"  ACS outcomes: {len(acs):,} obs")

    # Treatment assignment
    treatment = pd.read_parquet(processed / "fire_treatment_assignment.parquet")
    print(f"  Treatment: {len(treatment):,} counties")

    # Matching covariates
    covariates = pd.read_parquet(processed / "matching_covariates_2012.parquet")
    print(f"  Covariates: {len(covariates):,} counties")

    # Smoke buffer
    smoke = pd.read_parquet(processed / "smoke_buffer_100km.parquet")
    print(f"  Smoke buffer: {len(smoke):,} counties")

    return acs, treatment, covariates, smoke


def create_balanced_panel(acs: pd.DataFrame, treatment: pd.DataFrame,
                          covariates: pd.DataFrame, smoke: pd.DataFrame) -> pd.DataFrame:
    """
    Merge datasets into balanced panel structure.
    Structure: each county appears in 4 time periods (1990, 2000, 2011, 2019).
    """
    # Get unique counties from treatment assignment
    counties = treatment[['GEOID']].drop_duplicates().sort_values('GEOID').reset_index(drop=True)
    print(f"\nTotal counties: {len(counties):,}")

    # Create time periods
    time_periods = [1990, 2000, 2011, 2019]
    panel = []

    for period in time_periods:
        period_data = counties.copy()
        period_data['year'] = period
        panel.append(period_data)

    panel = pd.concat(panel, ignore_index=True)
    print(f"Panel structure (counties × periods): {len(panel):,}")

    # Merge outcomes (only available for 2011, 2019)
    panel = panel.merge(acs, on=['GEOID', 'year'], how='left')
    print(f"After merging ACS outcomes: {len(panel):,} obs")

    # Merge treatment assignment (same for all periods)
    treatment_merge = treatment.drop('first_fire_year', axis=1) if 'first_fire_year' in treatment.columns else treatment
    panel = panel.merge(treatment_merge, on='GEOID', how='left')
    print(f"After merging treatment: {len(panel):,} obs")

    # Merge covariates (same for all periods; baseline 2011)
    panel = panel.merge(covariates, on='GEOID', how='left')
    print(f"After merging covariates: {len(panel):,} obs")

    # Merge smoke buffer (same for all periods)
    panel = panel.merge(smoke, on='GEOID', how='left')
    print(f"After merging smoke buffer: {len(panel):,} obs")

    return panel


def apply_sample_restrictions(panel: pd.DataFrame) -> tuple:
    """
    Apply sample restrictions and return final panel + restriction log.
    Restrictions:
    - Drop counties with pop < 1,000 (baseline)
    - Drop controls within smoke buffer
    """
    print("\nApplying sample restrictions...")

    initial_n = len(panel)

    # 1. Population restriction (baseline)
    if 'population' in panel.columns:
        panel = panel[panel['population'] >= 1000].copy()
        print(f"  After pop >= 1,000: {len(panel):,} obs (dropped {initial_n - len(panel):,})")
    else:
        print("  WARNING: Population column not found; skipping pop restriction")

    # 2. Smoke buffer exclusion (for controls only)
    initial_n = len(panel)
    treated = (panel['early_treated'] == 1) | (panel['late_treated'] == 1)
    control_in_buffer = (~treated) & (panel['within_smoke_buffer'] == 1)

    panel = panel[~control_in_buffer].copy()
    print(f"  After smoke buffer exclusion: {len(panel):,} obs (dropped {initial_n - len(panel):,} control counties)")

    # Summary stats
    print("\nFinal sample composition:")
    print(f"  Total obs: {len(panel):,}")
    print(f"  Unique counties: {panel['GEOID'].nunique():,}")
    print(f"  Time periods: {panel['year'].nunique()}")

    treated_n = panel[(panel['early_treated'] == 1) | (panel['late_treated'] == 1)].shape[0]
    control_n = panel[(panel['early_treated'] == 0) & (panel['late_treated'] == 0)].shape[0]

    print(f"\nTreatment assignment (after restrictions):")
    print(f"  Early-treated (2012-2015): {panel['early_treated'].sum():,} obs")
    print(f"  Late-treated (2016-2019): {panel['late_treated'].sum():,} obs")
    print(f"  Never-treated: {(panel['early_treated'] == 0).sum() & (panel['late_treated'] == 0).sum():,} obs")

    return panel, {
        'initial_n': initial_n,
        'final_n': len(panel),
        'treated_n': treated_n,
        'control_n': control_n,
    }


def main():
    """Assemble and save final panel."""
    print("=" * 60)
    print("PANEL ASSEMBLY: Final Balanced Panel")
    print("=" * 60)

    acs, treatment, covariates, smoke = load_all_datasets()
    panel = create_balanced_panel(acs, treatment, covariates, smoke)
    panel, restrictions = apply_sample_restrictions(panel)

    # Output
    out_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    out_file = out_dir / "analysis_sample_final.parquet"

    panel.to_parquet(out_file, index=False)
    print(f"\n[OK] Saved: {out_file}")
    print(f"  Shape: {panel.shape}")
    print(f"  Columns: {panel.columns.tolist()}")


if __name__ == "__main__":
    main()
