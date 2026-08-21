"""
Propensity-score inverse-probability weighting for ATT estimation.

v2 changes from v1:
  1. Hard WFP floor: restrict controls to wfp_mean_pct >= WFP_CTRL_FLOOR (40).
     Treated tracts have mean WFP percentile 68.7; low-WFP controls are off the
     common support and cause extreme IPW weights that cannot be trimmed away.
  2. Revised PS formula:
     - Drop fire_pre2013 / log_acres_pre2013: cause near-perfect separation
       (treated=79% prior-fire; controls=9%). WFP 2012 already captures long-run
       fire risk, making fire history partially collinear and destabilising.
     - Drop wfp_q2_frac / wfp_q3_frac: near-zero for treated tracts in the
       WFP-restricted sample; degenerate in logistic model.
     - Replace raw wfp_dist_km with log(wfp_dist_km + 0.01): right-skewed.
     - Add wfp_mean_pct^2: nonlinear WFP dose-response in the high-WFP range.
  3. Trim control weights at 95th percentile (from 99th).

Model (v2):
  treated ~ wfp_mean_pct + wfp_mean_pct2
          + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km
          + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014
          + mig_rate_2014 + C(rucc_2013)

  Sample: treated + (never_treated with wfp_mean_pct >= WFP_CTRL_FLOOR).

Weights (ATT):
  treated = 1         ->  w = 1
  never_treated = 1   ->  w = p̂ / (1 - p̂), trimmed at 95th pct of controls.

Inputs:
  data/processed/matching_covariates.parquet
  data/processed/fire_treatment_tracts.parquet

Outputs:
  data/processed/ipw_weights.parquet       GISJOIN + treated + ps + ipw_weight
  results/balance_table.csv                SMD before/after per covariate
  results/ps_overlap.png                   Propensity score density overlay
  results/matching_log.txt                 Full diagnostic log
"""

import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

TS_FILE = ROOT / "data" / "raw" / "acs_extracts" / "nhgis_inc_pov_emp" / "nhgis0012_ts_nominal_tract.csv"

# Hard WFP floor for controls: restricts to fire-prone tracts comparable to treated.
# Treated mean = 68.7; 40 corresponds to the bottom of the 3rd quintile nationally.
WFP_CTRL_FLOOR = 40.0

# Trim weight percentile (95th, down from 99th in v1)
TRIM_PCT = 0.95

# Covariates for PS formula — fire history dropped; log_wfp_dist_km replaces wfp_dist_km
PS_COVARS = [
    "wfp_mean_pct", "wfp_mean_pct2",
    "wfp_q4_frac", "wfp_q5_frac",
    "log_wfp_dist_km",
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014",
]

PS_FORMULA = (
    "treated ~ wfp_mean_pct + wfp_mean_pct2"
    " + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km"
    " + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014"
    " + mig_rate_2014 + C(rucc_2013)"
)

# Covariates to report in balance table (broader than PS model, includes dropped vars)
BALANCE_COVARS = [
    "wfp_mean_pct",
    "wfp_q4_frac", "wfp_q5_frac",
    "log_wfp_dist_km",
    "fire_pre2013", "log_acres_pre2013",
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014",
]


def load_data() -> pd.DataFrame:
    covs = pd.read_parquet(PROCESSED / "matching_covariates.parquet")
    fire = pd.read_parquet(
        PROCESSED / "fire_treatment_tracts.parquet",
        columns=["GISJOIN", "treated", "never_treated"],
    )

    df = covs.merge(fire, on="GISJOIN", how="inner")
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()

    # Population from raw nominal TS (not forwarded to parquet in v1)
    ts_pop = pd.read_csv(
        TS_FILE, usecols=["NHGISCODE", "YEAR", "AV0AA"], low_memory=False
    )
    ts_pop = (
        ts_pop[ts_pop["YEAR"] == "2010-2014"][["NHGISCODE", "AV0AA"]]
        .rename(columns={"NHGISCODE": "GISJOIN", "AV0AA": "pop_2014_raw"})
    )
    df = df.merge(ts_pop, on="GISJOIN", how="left")
    df["log_pop_2014"] = np.log(df["pop_2014_raw"].clip(lower=1))

    # Engineered features
    df["wfp_mean_pct2"]   = df["wfp_mean_pct"] ** 2
    df["log_wfp_dist_km"] = np.log(df["wfp_dist_km"].clip(lower=0.01))

    n_treated = (df["treated"] == 1).sum()
    n_ctrl    = (df["treated"] == 0).sum()
    print(f"  Full sample: {n_treated:,} treated + {n_ctrl:,} controls")
    return df


def apply_wfp_floor(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict controls to wfp_mean_pct >= WFP_CTRL_FLOOR; retain all treated."""
    n_ctrl_before = (df["treated"] == 0).sum()
    mask = (df["treated"] == 1) | (df["wfp_mean_pct"] >= WFP_CTRL_FLOOR)
    df_r = df[mask].copy()
    n_ctrl_after = (df_r["treated"] == 0).sum()
    n_dropped = n_ctrl_before - n_ctrl_after
    print(f"\nWFP floor (wfp_mean_pct >= {WFP_CTRL_FLOOR}):")
    print(f"  Controls dropped:  {n_dropped:,} ({100*n_dropped/n_ctrl_before:.1f}%)")
    print(f"  Controls retained: {n_ctrl_after:,}")
    return df_r


def drop_missing_ps(df: pd.DataFrame) -> pd.DataFrame:
    needed = PS_COVARS + ["treated"]
    missing = df[needed].isna().sum()
    if missing.any():
        print("[WARNING] Missing PS covariates:")
        print(missing[missing > 0])
        df = df.dropna(subset=[c for c in needed if c != "treated"]).copy()
    return df


def fit_ps_model(df: pd.DataFrame):
    print("\nFitting logistic PS model (v2 formula) ...")
    model = smf.logit(PS_FORMULA, data=df).fit(maxiter=300, disp=False)
    print(f"  Converged:   {model.mle_retvals['converged']}")
    print(f"  Log-lik:     {model.llf:.1f}  |  Pseudo-R²: {model.prsquared:.3f}")
    print(f"  n={int(model.nobs):,}  AIC={model.aic:.1f}")
    return model


def compute_weights(df: pd.DataFrame, ps: pd.Series) -> pd.DataFrame:
    df = df.copy()
    df["ps"] = ps.values

    df["ipw_raw"] = np.where(
        df["treated"] == 1,
        1.0,
        df["ps"] / (1.0 - df["ps"]),
    )

    p_trim = df.loc[df["treated"] == 0, "ipw_raw"].quantile(TRIM_PCT)
    df["ipw_weight"] = np.where(
        df["treated"] == 1, 1.0, df["ipw_raw"].clip(upper=p_trim)
    )

    w_ctrl = df.loc[df["treated"] == 0, "ipw_weight"]
    ess = w_ctrl.sum() ** 2 / (w_ctrl ** 2).sum()

    print(f"\nIPW weight summary (controls, trimmed at p{int(TRIM_PCT*100)}={p_trim:.3f}):")
    print(f"  Min:    {w_ctrl.min():.4f}")
    print(f"  Median: {w_ctrl.median():.4f}")
    print(f"  Mean:   {w_ctrl.mean():.4f}")
    print(f"  Max:    {w_ctrl.max():.4f}")
    print(f"  ESS:    {ess:,.0f} ({100*ess/len(w_ctrl):.1f}% of {len(w_ctrl):,} controls)")
    return df


def common_support_trim(df: pd.DataFrame) -> pd.DataFrame:
    """Drop controls below the minimum PS of treated; re-estimate PS on restricted sample."""
    print("\nStep 1: Initial PS for common-support restriction ...")
    m0 = fit_ps_model(df)
    ps0 = m0.predict(df)
    df = df.copy()
    df["ps_init"] = ps0.values

    ps_min_t = df.loc[df["treated"] == 1, "ps_init"].min()
    n_before  = (df["treated"] == 0).sum()
    off       = (df["treated"] == 0) & (df["ps_init"] < ps_min_t)
    df_cs     = df[~off | (df["treated"] == 1)].copy()
    n_after   = (df_cs["treated"] == 0).sum()
    print(f"  PS range of treated: [{ps_min_t:.4f}, "
          f"{df.loc[df['treated']==1,'ps_init'].max():.4f}]")
    print(f"  Off-support controls dropped: {off.sum():,} ({100*off.sum()/n_before:.1f}%)")
    print(f"  Controls retained: {n_after:,}")

    print("\nStep 2: Re-estimate PS on common-support sample ...")
    m1 = fit_ps_model(df_cs)
    ps1 = m1.predict(df_cs)
    return compute_weights(df_cs, ps1)


def smd(tv: np.ndarray, cv: np.ndarray, wts: np.ndarray | None = None) -> float:
    t_mean = np.nanmean(tv)
    t_sd   = np.nanstd(tv, ddof=1)
    if t_sd == 0:
        return 0.0
    if wts is None:
        c_mean = np.nanmean(cv)
    else:
        mask   = ~np.isnan(cv)
        c_mean = np.average(cv[mask], weights=wts[mask])
    return (t_mean - c_mean) / t_sd


def balance_table(df: pd.DataFrame) -> pd.DataFrame:
    t = df[df["treated"] == 1]
    c = df[df["treated"] == 0]
    w = c["ipw_weight"].values

    rows = []
    for col in BALANCE_COVARS:
        if col not in df.columns:
            continue
        tv = t[col].values
        cv = c[col].values
        rows.append({
            "covariate":    col,
            "mean_treated": np.nanmean(tv),
            "mean_ctrl_raw": np.nanmean(cv),
            "mean_ctrl_wtd": np.average(cv[~np.isnan(cv)], weights=w[~np.isnan(cv)]),
            "smd_before":   smd(tv, cv),
            "smd_after":    smd(tv, cv, w),
        })

    bal = pd.DataFrame(rows)
    bal["balanced"] = bal["smd_after"].abs() < 0.1
    return bal


def print_balance(bal: pd.DataFrame) -> None:
    in_model = set(PS_COVARS)
    print("\n─── Covariate Balance ───────────────────────────────────────────────")
    print(f"  {'Covariate':<26} {'In model':>8} {'SMD before':>10} {'SMD after':>10} {'Status':>8}")
    print(f"  {'-'*26} {'-'*8} {'-'*10} {'-'*10} {'-'*8}")
    for _, row in bal.iterrows():
        in_m = "yes" if row["covariate"] in in_model else "no (report)"
        flag = "[OK]" if row["balanced"] else "[!!]"
        print(f"  {row['covariate']:<26} {in_m:>8} {row['smd_before']:>10.3f} "
              f"{row['smd_after']:>10.3f} {flag:>8}")
    n_model_ok = bal[bal["covariate"].isin(in_model)]["balanced"].sum()
    n_model    = bal["covariate"].isin(in_model).sum()
    print(f"\n  Balanced (|SMD|<0.1): {bal['balanced'].sum()}/{len(bal)} total; "
          f"{n_model_ok}/{n_model} PS-model covariates")
    worst = bal.loc[bal["smd_after"].abs().idxmax()]
    print(f"  Worst post-weighting SMD: {worst['covariate']} = {worst['smd_after']:.3f}")


def ps_overlap_plot(df: pd.DataFrame, out_path: Path) -> None:
    t_ps = df.loc[df["treated"] == 1, "ps"]
    c_ps = df.loc[df["treated"] == 0, "ps"]

    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    bins = np.linspace(0, 1, 60)
    ax.hist(c_ps, bins=bins, density=True, alpha=0.5, color="#2166ac", label="Never-treated (WFP ≥ 40)")
    ax.hist(t_ps, bins=bins, density=True, alpha=0.65, color="#d6604d", label="Treated (fire 2015–17)")
    ax.set_xlabel("Estimated propensity score (v2 model)")
    ax.set_ylabel("Density")
    ax.set_title("PS overlap: treated vs. WFP-restricted controls")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] PS overlap plot: {out_path.name}")


def main() -> None:
    print("=" * 70)
    print("PS-IPW MATCHING v2: Wildfire 2015–2017, WFP-restricted controls")
    print("=" * 70)
    RESULTS.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df = apply_wfp_floor(df)
    df = drop_missing_ps(df)
    df = common_support_trim(df)

    bal = balance_table(df)
    print_balance(bal)

    # Save
    weights_out = df[["GISJOIN", "treated", "ps", "ipw_weight"]].copy()
    weights_out.to_parquet(PROCESSED / "ipw_weights.parquet", index=False)
    weights_out.to_csv(RESULTS / "ipw_weights.csv", index=False)
    bal.to_csv(RESULTS / "balance_table.csv", index=False)
    ps_overlap_plot(df, RESULTS / "ps_overlap.png")

    # PS range summary
    t_ps = df.loc[df["treated"] == 1, "ps"]
    c_ps = df.loc[df["treated"] == 0, "ps"]
    print(f"\nPS overlap (final):")
    print(f"  Treated:  [{t_ps.min():.3f}, {t_ps.max():.3f}]  mean={t_ps.mean():.3f}")
    print(f"  Controls: [{c_ps.min():.3f}, {c_ps.max():.3f}]  mean={c_ps.mean():.3f}")

    print(f"\n[OK] Saved:")
    print(f"     data/processed/ipw_weights.parquet  ({len(weights_out):,} rows)")
    print(f"     results/balance_table.csv")
    print(f"     results/ps_overlap.png")


if __name__ == "__main__":
    main()
