"""
Main DiD estimation: Two-way fixed effects with IPW matching
Input: analysis_sample_final.parquet, ipw_weights.parquet
Output: ATT estimates, standard errors, 95% CIs for all outcomes
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("PHASE 2: DIFFERENCE-IN-DIFFERENCES ESTIMATION")
print("=" * 60)

# Load data
df = pd.read_parquet('data/processed/analysis_sample_final.parquet')
weights = pd.read_parquet('data/processed/ipw_weights.parquet')

# Merge weights
df = df.merge(weights[['GEOID', 'year', 'ipw_trimmed']], on=['GEOID', 'year'])

print(f"\nSample size: {len(df):,} obs")
print(f"Treated: {df['early_treated'].sum():,} obs")
print(f"Control: {(df['early_treated'] == 0).sum():,} obs")
print(f"Time periods: {df['year'].nunique()}")

# Create binary post indicator
df['post'] = (df['year'] >= 2015).astype(int)

# Create treatment × post indicator
df['treat_post'] = df['early_treated'] * df['post']

# Outcomes
outcomes = ['poverty_rate', 'median_hh_income', 'employment_rate', 'net_migration_rate']

# Results storage
results_table = []

print("\n" + "=" * 60)
print("DiD RESULTS: Two-Way Fixed Effects with IPW")
print("=" * 60)

for outcome in outcomes:
    print(f"\n{outcome.upper()}")
    print("-" * 40)

    # Prepare data for OLS
    y = df[outcome].astype(float).values

    # Create design matrix: FE for county and year, treatment × post
    X = pd.DataFrame({
        'treat_post': df['treat_post'].astype(float).values,
    }, dtype=float)

    # Add county FE (omit first for reference)
    county_fe = pd.get_dummies(df['GEOID'], prefix='county', drop_first=True, dtype=float)
    X = X.join(county_fe)

    # Add year FE (omit first for reference)
    year_fe = pd.get_dummies(df['year'], prefix='year', drop_first=True, dtype=float)
    X = X.join(year_fe)

    # Convert to float
    X = X.astype(float)

    # Add constant
    X_const = sm.add_constant(X)

    # Weights (IPW trimmed)
    weights_array = df['ipw_trimmed'].values

    # Weighted OLS
    model = sm.WLS(y, X_const, weights=weights_array)
    result = model.fit(cov_type='cluster', cov_kwds={'groups': df['GEOID']})

    # Extract ATT (coefficient on treat_post)
    att = result.params['treat_post']
    se = result.bse['treat_post']
    ci_lower = att - 1.96 * se
    ci_upper = att + 1.96 * se
    n_obs = len(y)

    print(f"ATT: {att:.4f}")
    print(f"SE: {se:.4f}")
    print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"N: {n_obs}")

    results_table.append({
        'Outcome': outcome,
        'ATT': att,
        'SE': se,
        'CI_Lower': ci_lower,
        'CI_Upper': ci_upper,
        'N': n_obs,
        'Significant': 'Yes' if 0 not in [ci_lower, ci_upper] else 'No'
    })

# Results table
results_df = pd.DataFrame(results_table)

print("\n" + "=" * 60)
print("SUMMARY TABLE: DiD ESTIMATES")
print("=" * 60)
print(results_df.to_string(index=False))

# Save
results_df.to_csv('results/tables/main_att_estimates.csv', index=False)

print("\n[OK] Results saved to results/tables/main_att_estimates.csv")
print("\nPhase 2 complete. Ready for Phase 3 (Pre-trend testing).")
