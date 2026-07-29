"""
Propensity-score inverse-probability weighting for covariate balance.
Input: analysis_sample_final.parquet
Output: IPW weights, balance diagnostics
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("PHASE 1: PROPENSITY-SCORE IPW MATCHING")
print("=" * 60)

# Load data
df = pd.read_parquet('data/processed/analysis_sample_final.parquet')

print(f"\nSample size: {len(df):,}")
print(f"Treated (early_treated=1): {df['early_treated'].sum()}")
print(f"Control (early_treated=0): {(df['early_treated'] == 0).sum()}")

# Define treatment
df['treated'] = df['early_treated'].astype(int)

# Select matching covariates (keep simple for small sample)
covariates = [
    'baseline_poverty_rate',
    'baseline_median_hh_income',
    'pre2012_fire_count'
]

# Add WFP quintile
df['wfp_q'] = df['wfp_quintile'].fillna(3).astype(float)
covariates.append('wfp_q')

# Impute missing
for cov in covariates:
    if df[cov].isnull().any():
        df[cov].fillna(df[cov].mean(), inplace=True)

print(f"\nCovariates in PS model: {covariates}")

# Prepare for logit
X = df[covariates].values
y = df['treated'].values

# Standardize X for numerical stability
X_mean = X.mean(axis=0)
X_std = X.std(axis=0) + 1e-6
X_scaled = (X - X_mean) / X_std

# Propensity score with regularization
print("\nEstimating propensity score model (logit with L2 regularization)...")
ps_model = LogisticRegression(
    C=0.1,  # Inverse regularization strength
    solver='lbfgs',
    max_iter=1000,
    random_state=42
)
ps_model.fit(X_scaled, y)

# Extract propensity scores
df['ps'] = ps_model.predict_proba(X_scaled)[:, 1]

print("\n" + "=" * 60)
print("PROPENSITY SCORE SUMMARY")
print("=" * 60)
print(f"Treated group (n={df['treated'].sum()}):")
print(f"  Mean PS: {df.loc[df['treated'] == 1, 'ps'].mean():.3f}")
print(f"  Min: {df.loc[df['treated'] == 1, 'ps'].min():.3f}")
print(f"  Max: {df.loc[df['treated'] == 1, 'ps'].max():.3f}")

print(f"\nControl group (n={(df['treated'] == 0).sum()}):")
print(f"  Mean PS: {df.loc[df['treated'] == 0, 'ps'].mean():.3f}")
print(f"  Min: {df.loc[df['treated'] == 0, 'ps'].min():.3f}")
print(f"  Max: {df.loc[df['treated'] == 0, 'ps'].max():.3f}")

# Compute IPW weights
df['ipw'] = np.where(
    df['treated'] == 1,
    1.0,
    (df['ps'] + 1e-6) / (1 - df['ps'] + 1e-6)
)

# Trim at 99th percentile
ipw_99 = df.loc[df['treated'] == 0, 'ipw'].quantile(0.99)
df['ipw_trimmed'] = np.minimum(df['ipw'], ipw_99)

print("\n" + "=" * 60)
print("IPW WEIGHTS (Trimmed at 99th percentile)")
print("=" * 60)
print(f"Min: {df['ipw_trimmed'].min():.3f}")
print(f"Mean: {df['ipw_trimmed'].mean():.3f}")
print(f"Median: {df['ipw_trimmed'].median():.3f}")
print(f"Max: {df['ipw_trimmed'].max():.3f}")
print(f"Trim threshold: {ipw_99:.3f}")

# Balance diagnostics
print("\n" + "=" * 60)
print("COVARIATE BALANCE: STANDARDIZED MEAN DIFFERENCE (SMD)")
print("=" * 60)

balance_table = []

for cov in covariates:
    # Before IPW
    t_mean = df.loc[df['treated'] == 1, cov].mean()
    c_mean = df.loc[df['treated'] == 0, cov].mean()
    t_std = df.loc[df['treated'] == 1, cov].std()
    c_std = df.loc[df['treated'] == 0, cov].std()
    pooled_std = np.sqrt((t_std**2 + c_std**2) / 2)
    smd_before = (t_mean - c_mean) / pooled_std if pooled_std > 0 else 0

    # After IPW
    t_wts = df.loc[df['treated'] == 1, 'ipw_trimmed']
    c_wts = df.loc[df['treated'] == 0, 'ipw_trimmed']

    t_mean_w = (df.loc[df['treated'] == 1, cov] * t_wts).sum() / t_wts.sum()
    c_mean_w = (df.loc[df['treated'] == 0, cov] * c_wts).sum() / c_wts.sum()

    t_var_w = ((df.loc[df['treated'] == 1, cov] - t_mean_w)**2 * t_wts).sum() / t_wts.sum()
    c_var_w = ((df.loc[df['treated'] == 0, cov] - c_mean_w)**2 * c_wts).sum() / c_wts.sum()
    pooled_std_w = np.sqrt((t_var_w + c_var_w) / 2)

    smd_after = (t_mean_w - c_mean_w) / pooled_std_w if pooled_std_w > 0 else 0

    balance_ok = '[OK]' if abs(smd_after) < 0.1 else '[WARN]'
    balance_table.append({
        'Covariate': cov,
        'SMD_Before': f"{smd_before:.3f}",
        'SMD_After': f"{smd_after:.3f}",
        'Status': balance_ok
    })

balance_df = pd.DataFrame(balance_table)
print(balance_df.to_string(index=False))

# Overall balance
smd_after_vals = [float(row.split()[0]) for row in balance_df['SMD_After']]
balance_ok_all = all(abs(x) < 0.1 for x in smd_after_vals)
print(f"\nOverall balance (all SMD < 0.1): {'[OK]' if balance_ok_all else '[WARNING]'}")

# ESS
c_wts = df.loc[df['treated'] == 0, 'ipw_trimmed']
ess = c_wts.sum()**2 / (c_wts**2).sum()
print(f"Effective sample size (control): {ess:.0f} / {(df['treated'] == 0).sum()}")

# Save
weights_output = df[['GEOID', 'year', 'treated', 'ps', 'ipw', 'ipw_trimmed']].copy()
weights_output.to_parquet('data/processed/ipw_weights.parquet', index=False)

balance_df.to_csv('results/tables/balance_table.csv', index=False)

print("\n[OK] Weights saved to data/processed/ipw_weights.parquet")
print("[OK] Balance saved to results/tables/balance_table.csv")
print("\nPhase 1 complete. Ready for Phase 2 (C&S DiD).")
