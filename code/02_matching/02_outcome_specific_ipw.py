# -*- coding: utf-8 -*-
"""
Outcome-specific PS-IPW weighting.

For each target mechanism outcome, augments the base propensity-score model
with that outcome's h=-2 (ACS 2012) level and its h=-2 to h=-1 slope (change
2012->2014). This directly targets parallel trends in the outcome of interest.

Base PS model (from 01_ipw_weights.py v2):
  treated ~ wfp_mean_pct + wfp_mean_pct2 + wfp_q4_frac + wfp_q5_frac
          + log_wfp_dist_km + pov_rate_2014 + log_inc_2014 + emp_rate_2014
          + log_pop_2014 + mig_rate_2014 + C(rucc_2013)

Augmented formula:
  ... + <outcome>_2012 + <outcome>_slope_12_14

Target outcomes (|pre-trend/ATT| > 0.5):
  med_gross_rent, log_home_value, med_age_diffcounty, inmov_poverty_rate

Outputs (per outcome):
  data/processed/ipw_weights_<outcome>.parquet   GISJOIN + treated + ps + ipw_weight
  data/processed/outcome_specific_weights_for_R.csv   all outcomes combined (for R)
  results/balance_outcome_ipw.csv                balance diagnostics
"""

import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore", category=FutureWarning)

ROOT     = Path(__file__).resolve().parents[2]
PROC     = ROOT / "data" / "processed"
RESULTS  = ROOT / "results"
TS_FILE  = ROOT / "data" / "raw" / "acs_extracts" / "nhgis_inc_pov_emp" / "nhgis0012_ts_nominal_tract.csv"

WFP_CTRL_FLOOR = 40.0
TRIM_PCT       = 0.95

BASE_FORMULA_PARTS = (
    "wfp_mean_pct + wfp_mean_pct2"
    " + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km"
    " + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014"
    " + mig_rate_2014 + C(rucc_2013)"
)

TARGET_OUTCOMES = {
    "med_gross_rent":    "Median gross rent",
    "log_home_value":    "Log home value",
    "med_age_diffcounty": "Median age of diff-county in-migrants",
    "inmov_poverty_rate": "Poverty rate of outside-county movers",
}


def load_base_data() -> pd.DataFrame:
    covs = pd.read_parquet(PROC / "matching_covariates.parquet")
    fire = pd.read_parquet(
        PROC / "fire_treatment_tracts.parquet",
        columns=["GISJOIN", "treated", "never_treated"],
    )
    df = covs.merge(fire, on="GISJOIN", how="inner")
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()

    ts_pop = pd.read_csv(TS_FILE, usecols=["NHGISCODE", "YEAR", "AV0AA"], low_memory=False)
    ts_pop = (
        ts_pop[ts_pop["YEAR"] == "2010-2014"][["NHGISCODE", "AV0AA"]]
        .rename(columns={"NHGISCODE": "GISJOIN", "AV0AA": "pop_2014_raw"})
    )
    df = df.merge(ts_pop, on="GISJOIN", how="left")
    df["log_pop_2014"]    = np.log(df["pop_2014_raw"].clip(lower=1))
    df["wfp_mean_pct2"]   = df["wfp_mean_pct"] ** 2
    df["log_wfp_dist_km"] = np.log(df["wfp_dist_km"].clip(lower=0.01))
    return df


def load_mechanism_pretrend() -> pd.DataFrame:
    """Return tract-level h=-2 (2012) levels and h=-2→h=-1 slopes per outcome."""
    mech = pd.read_parquet(PROC / "mechanism_vars_panel.parquet")
    pre2  = mech[mech["acs_year"] == 2012].set_index("NHGISCODE")[list(TARGET_OUTCOMES.keys())]
    pre1  = mech[mech["acs_year"] == 2014].set_index("NHGISCODE")[list(TARGET_OUTCOMES.keys())]
    level = pre2.rename(columns={v: f"{v}_2012" for v in TARGET_OUTCOMES})
    slope = (pre1 - pre2).rename(columns={v: f"{v}_slope" for v in TARGET_OUTCOMES})
    return pd.concat([level, slope], axis=1).reset_index().rename(columns={"NHGISCODE": "GISJOIN"})


def apply_wfp_floor(df: pd.DataFrame) -> pd.DataFrame:
    mask = (df["treated"] == 1) | (df["wfp_mean_pct"] >= WFP_CTRL_FLOOR)
    return df[mask].copy()


def impute_with_median(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Fill missing outcome pre-trend covariates with column median (by treatment group)."""
    for c in cols:
        if c not in df.columns:
            continue
        for grp in [0, 1]:
            mask = df["treated"] == grp
            med  = df.loc[mask, c].median()
            df.loc[mask & df[c].isna(), c] = med
    return df


def standardize(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Z-score normalize outcome pre-trend covariates before entering logit."""
    for c in cols:
        if c not in df.columns:
            continue
        mu  = df[c].mean()
        sig = df[c].std()
        if sig > 0:
            df[c] = (df[c] - mu) / sig
    return df


def fit_and_weight(df: pd.DataFrame, formula: str, label: str) -> pd.DataFrame:
    """Fit PS logit on common-support sample; return df with ps + ipw_weight columns."""
    # Initial PS for common-support restriction
    m0   = smf.logit(formula, data=df).fit(maxiter=300, disp=False)
    ps0  = m0.predict(df)
    df   = df.copy()
    df["ps_init"] = ps0.values

    ps_min_t = df.loc[df["treated"] == 1, "ps_init"].min()
    off       = (df["treated"] == 0) & (df["ps_init"] < ps_min_t)
    df_cs     = df[~off | (df["treated"] == 1)].copy()

    # Re-estimate on common-support sample
    m1 = smf.logit(formula, data=df_cs).fit(maxiter=300, disp=False)
    ps1 = m1.predict(df_cs)
    df_cs["ps"] = ps1.values

    df_cs["ipw_raw"] = np.where(
        df_cs["treated"] == 1,
        1.0,
        df_cs["ps"] / (1.0 - df_cs["ps"]),
    )
    p_trim = df_cs.loc[df_cs["treated"] == 0, "ipw_raw"].quantile(TRIM_PCT)
    df_cs["ipw_weight"] = np.where(
        df_cs["treated"] == 1, 1.0, df_cs["ipw_raw"].clip(upper=p_trim)
    )

    w_ctrl = df_cs.loc[df_cs["treated"] == 0, "ipw_weight"]
    ess = w_ctrl.sum() ** 2 / (w_ctrl ** 2).sum()
    n_cs = (df_cs["treated"] == 0).sum()
    print(f"    {label}: n_ctrl={n_cs:,}  ESS={ess:,.0f}  ({100*ess/n_cs:.1f}%)  "
          f"pseudo-R2={m1.prsquared:.3f}  converged={m1.mle_retvals['converged']}")
    return df_cs[["GISJOIN", "treated", "ps", "ipw_weight"]]


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


def main() -> None:
    print("=" * 70)
    print("OUTCOME-SPECIFIC PS-IPW: Mechanism variable pre-trend correction")
    print("=" * 70)
    RESULTS.mkdir(parents=True, exist_ok=True)

    base_df  = load_base_data()
    mech_pre = load_mechanism_pretrend()
    df_all   = base_df.merge(mech_pre, on="GISJOIN", how="left")
    df_all   = apply_wfp_floor(df_all)

    all_weights = []
    balance_rows = []

    for outcome, label in TARGET_OUTCOMES.items():
        print(f"\n{'─'*60}")
        print(f"  Outcome: {outcome} ({label})")

        extra_cols = [f"{outcome}_2012", f"{outcome}_slope"]
        df_out = df_all.copy()
        df_out = impute_with_median(df_out, extra_cols)
        df_out = standardize(df_out, extra_cols)

        base_needed = [
            "wfp_mean_pct", "wfp_mean_pct2", "wfp_q4_frac", "wfp_q5_frac",
            "log_wfp_dist_km", "pov_rate_2014", "log_inc_2014", "emp_rate_2014",
            "log_pop_2014", "mig_rate_2014", "rucc_2013",
        ]
        drop_mask = df_out[base_needed].isna().any(axis=1)
        df_out = df_out[~drop_mask].copy()

        formula = (
            f"treated ~ {BASE_FORMULA_PARTS}"
            f" + {outcome}_2012 + {outcome}_slope"
        )

        wt_df = fit_and_weight(df_out, formula, label)
        wt_df["outcome"] = outcome
        all_weights.append(wt_df)

        # Balance check on the pre-trend covariate (primary target)
        merged = df_out.merge(wt_df[["GISJOIN", "ipw_weight"]], on="GISJOIN", how="left")
        t_vals = merged.loc[merged["treated"] == 1, f"{outcome}_2012"].values
        c_vals = merged.loc[merged["treated"] == 0, f"{outcome}_2012"].values
        c_wts  = merged.loc[merged["treated"] == 0, "ipw_weight"].fillna(0).values
        balance_rows.append({
            "outcome":    outcome,
            "smd_before": smd(t_vals, c_vals),
            "smd_after":  smd(t_vals, c_vals, c_wts),
        })

        # Save per-outcome parquet
        out_path = PROC / f"ipw_weights_{outcome}.parquet"
        wt_df[["GISJOIN", "treated", "ps", "ipw_weight"]].to_parquet(out_path, index=False)
        print(f"    Saved: {out_path.name}")

    # Combined CSV for R
    combined = pd.concat(all_weights, ignore_index=True)
    csv_path = PROC / "outcome_specific_weights_for_R.csv"
    combined.to_csv(csv_path, index=False)
    print(f"\nSaved combined weights: {csv_path.name}  ({len(combined):,} rows)")

    # Balance diagnostics
    bal = pd.DataFrame(balance_rows)
    bal.to_csv(RESULTS / "balance_outcome_ipw.csv", index=False)
    print("\nBalance on h=-2 pre-trend covariate (standardized):")
    print(f"  {'Outcome':<28} {'SMD before':>10} {'SMD after':>10}")
    for _, row in bal.iterrows():
        flag = "[OK]" if abs(row["smd_after"]) < 0.1 else "[!!]"
        print(f"  {row['outcome']:<28} {row['smd_before']:>10.3f} {row['smd_after']:>10.3f}  {flag}")


if __name__ == "__main__":
    main()
