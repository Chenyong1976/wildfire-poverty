"""
Propensity-score inverse-probability weighting for ATT estimation.

Design changes from v2:
  1. WFP 2014 raster summaries replace WFP 2012 as primary matching covariate.
  2. PS caliper (0.20 SDs of treated PS) replaces hard WFP floor for common-support
     restriction.  Rationale: normalized difference in mean WFP 2014 = 0.43, above
     the Imbens (2015) threshold of 0.25; caliper trims the off-support tail of
     controls without discarding by an arbitrary absolute threshold.
  3. Balance table now reports all three WFP 2014 summaries (mean_pct, all five
     quintile fracs Q1–Q5, dist_km), plus WFP 2012 mean as robustness column.
  4. CEM matching added: coarsen WFP 2014 quintile → exact match → OLS.
     See compute_cem_weights() below.

PS model (v3):
  treated ~ wfp_mean_pct + wfp_mean_pct2
          + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km
          + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014
          + mig_rate_2014 + C(rucc_2013)

  (Q1–Q3 fracs omitted from PS formula: near-zero variation in the high-WFP
  caliper-restricted sample; all five are reported in the balance table.)

Weights (ATT):
  treated = 1         -> w = 1
  never_treated = 1   -> w = p̂ / (1 - p̂), trimmed at 95th pct of controls.

Inputs:
  data/processed/matching_covariates.parquet
  data/processed/fire_treatment_tracts.parquet

Outputs:
  data/processed/ipw_weights.parquet          GISJOIN + treated + ps + ipw_weight
  data/processed/cem_weights.parquet          GISJOIN + treated + cem_weight + cem_cell
  results/balance_table.csv                   SMD before/after for all covariates
  results/ps_overlap.png                      Propensity score density overlay
  results/matching_log.txt                    Full diagnostic log
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

# PS caliper: ±CALIPER_SD standard deviations of the treated propensity-score distribution.
# Cochran & Rubin (1973) recommend 0.20 SDs; Imbens & Rubin (2015) p. 297 use 0.20.
CALIPER_SD = 0.20

# Weight trimming percentile (controls only)
TRIM_PCT = 0.95

# Covariates in the PS logit formula
PS_FORMULA = (
    "treated ~ wfp_mean_pct + wfp_mean_pct2"
    " + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km"
    " + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014"
    " + mig_rate_2014 + C(rucc_2013)"
)

# All covariates reported in the balance table (broader than PS formula)
# Includes all three WFP 2014 summaries and WFP 2012 mean as robustness column
BALANCE_COVARS = [
    # WFP 2014 — primary matching variable (all three summaries)
    "wfp_mean_pct",
    "wfp_q1_frac", "wfp_q2_frac", "wfp_q3_frac", "wfp_q4_frac", "wfp_q5_frac",
    "log_wfp_dist_km",
    # WFP 2012 — robustness check (mean only)
    "wfp12_mean_pct",
    # Pre-2013 fire history
    "fire_pre2013", "log_acres_pre2013",
    # ACS 2014 socioeconomic covariates
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014",
    # RUCC (reported as numeric for SMD; enters PS model as factor)
    "rucc_2013",
]

# Covariates in PS formula (subset of BALANCE_COVARS; used to mark "In model" column)
PS_COVARS = {
    "wfp_mean_pct", "wfp_mean_pct2",
    "wfp_q4_frac", "wfp_q5_frac", "log_wfp_dist_km",
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014", "rucc_2013",
}


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    covs = pd.read_parquet(PROCESSED / "matching_covariates.parquet")
    fire = pd.read_parquet(
        PROCESSED / "fire_treatment_tracts.parquet",
        columns=["GISJOIN", "treated", "never_treated"],
    )

    df = covs.merge(fire, on="GISJOIN", how="inner")
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()

    # Population from raw nominal TS
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

    # Report normalized difference in WFP 2014 before any trimming
    t_wfp = df.loc[df["treated"] == 1, "wfp_mean_pct"]
    c_wfp = df.loc[df["treated"] == 0, "wfp_mean_pct"]
    nd = (t_wfp.mean() - c_wfp.mean()) / t_wfp.std()
    print(f"  Normalized difference (mean WFP 2014, pre-trimming): {nd:.3f}"
          f"  {'[HIGH: caliper will address]' if abs(nd) > 0.25 else '[OK]'}")
    return df


# ── PS caliper ────────────────────────────────────────────────────────────────

def drop_missing_ps(df: pd.DataFrame) -> pd.DataFrame:
    needed = list(PS_COVARS - {"wfp_mean_pct2", "rucc_2013"}) + ["wfp_mean_pct2", "rucc_2013", "treated"]
    missing = df[[c for c in needed if c in df.columns]].isna().sum()
    if missing.any():
        print("[WARNING] Missing PS covariates:")
        print(missing[missing > 0])
        drop_cols = [c for c in needed if c in df.columns and c != "treated"]
        df = df.dropna(subset=drop_cols).copy()
    return df


def fit_ps_model(df: pd.DataFrame):
    print("\nFitting logistic PS model ...")
    model = smf.logit(PS_FORMULA, data=df).fit(maxiter=300, disp=False)
    print(f"  Converged:   {model.mle_retvals['converged']}")
    print(f"  Log-lik:     {model.llf:.1f}  |  Pseudo-R²: {model.prsquared:.3f}")
    print(f"  n={int(model.nobs):,}  AIC={model.aic:.1f}")
    return model


def apply_ps_caliper(df: pd.DataFrame, caliper_sd: float = CALIPER_SD) -> pd.DataFrame:
    """
    Two-pass PS caliper following Cochran & Rubin (1973):
      Pass 1: Estimate initial PS on full sample.
      Pass 2: Drop controls outside [ps_min_treated - c, ps_max_treated + c]
              where c = caliper_sd * SD(ps_treated).  Re-estimate PS on trimmed sample.

    Reports number of controls dropped and resulting ESS.
    """
    print(f"\nPS caliper trimming (±{caliper_sd} SD of treated PS) ...")

    # Pass 1
    print("  Pass 1: Initial PS on full sample ...")
    m0 = fit_ps_model(df)
    ps0 = m0.predict(df)
    df = df.copy()
    df["ps_init"] = ps0.values

    t_ps    = df.loc[df["treated"] == 1, "ps_init"]
    caliper = caliper_sd * t_ps.std()
    lo      = t_ps.min() - caliper
    hi      = t_ps.max() + caliper

    n_ctrl_before = (df["treated"] == 0).sum()
    off = (df["treated"] == 0) & ((df["ps_init"] < lo) | (df["ps_init"] > hi))
    df_trimmed = df[~off | (df["treated"] == 1)].copy()
    n_ctrl_after = (df_trimmed["treated"] == 0).sum()

    print(f"  Caliper width: [{lo:.4f}, {hi:.4f}]")
    print(f"  Controls dropped: {off.sum():,} ({100*off.sum()/n_ctrl_before:.1f}%)")
    print(f"  Controls retained: {n_ctrl_after:,}")

    # Pass 2: Re-estimate PS on trimmed sample
    print("  Pass 2: Re-estimate PS on caliper-trimmed sample ...")
    m1 = fit_ps_model(df_trimmed)
    ps1 = m1.predict(df_trimmed)
    df_trimmed = df_trimmed.copy()
    df_trimmed["ps"] = ps1.values

    # Compute IPW weights
    df_trimmed["ipw_raw"] = np.where(
        df_trimmed["treated"] == 1,
        1.0,
        df_trimmed["ps"] / (1.0 - df_trimmed["ps"]),
    )
    p_trim = df_trimmed.loc[df_trimmed["treated"] == 0, "ipw_raw"].quantile(TRIM_PCT)
    df_trimmed["ipw_weight"] = np.where(
        df_trimmed["treated"] == 1, 1.0, df_trimmed["ipw_raw"].clip(upper=p_trim)
    )

    w_ctrl = df_trimmed.loc[df_trimmed["treated"] == 0, "ipw_weight"]
    ess = w_ctrl.sum() ** 2 / (w_ctrl ** 2).sum()
    print(f"\n  IPW weight summary (controls, trimmed at p{int(TRIM_PCT*100)}={p_trim:.3f}):")
    print(f"    Min:    {w_ctrl.min():.4f}")
    print(f"    Median: {w_ctrl.median():.4f}")
    print(f"    Max:    {w_ctrl.max():.4f}")
    print(f"    ESS:    {ess:,.0f} ({100*ess/len(w_ctrl):.1f}% of {len(w_ctrl):,} controls)")

    return df_trimmed


# ── Balance diagnostics ───────────────────────────────────────────────────────

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
        in_model = col in PS_COVARS or col.replace("log_", "") in PS_COVARS
        rows.append({
            "covariate":      col,
            "in_ps_model":    "yes" if in_model else "no (reported)",
            "mean_treated":   np.nanmean(tv),
            "mean_ctrl_raw":  np.nanmean(cv),
            "mean_ctrl_wtd":  np.average(cv[~np.isnan(cv)], weights=w[~np.isnan(cv)]),
            "smd_before":     smd(tv, cv),
            "smd_after":      smd(tv, cv, w),
        })

    bal = pd.DataFrame(rows)
    bal["balanced"] = bal["smd_after"].abs() < 0.1
    return bal


def print_balance(bal: pd.DataFrame) -> None:
    print("\n─── Covariate Balance ───────────────────────────────────────────────────")
    print(f"  {'Covariate':<28} {'In PS':>6} {'SMD bef':>9} {'SMD aft':>9} {'Status':>8}")
    print(f"  {'-'*28} {'-'*6} {'-'*9} {'-'*9} {'-'*8}")
    for _, row in bal.iterrows():
        flag = "[OK]" if row["balanced"] else "[!!]"
        print(f"  {row['covariate']:<28} {row['in_ps_model']:>6} "
              f"{row['smd_before']:>9.3f} {row['smd_after']:>9.3f} {flag:>8}")
    n_ok  = bal["balanced"].sum()
    worst = bal.loc[bal["smd_after"].abs().idxmax()]
    print(f"\n  Balanced (|SMD|<0.1): {n_ok}/{len(bal)} covariates")
    print(f"  Worst post-weighting SMD: {worst['covariate']} = {worst['smd_after']:.3f}")


# ── CEM matching ─────────────────────────────────────────────────────────────

def compute_cem_weights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coarsened exact matching on WFP 2014 quintile × pre-2013 fire history.

    Matching cell: (wfp_quintile [1-5]) × (fire_pre2013 [0/1]) = 10 cells max.
    Each treated tract is matched to all controls in the same cell; unmatched
    cells (no controls or no treated) are dropped.

    Returns a DataFrame with GISJOIN, treated, cem_weight, cem_cell.
    cem_weight for treated = 1; for controls = n_treated_in_cell / n_ctrl_in_cell.
    This produces balance on the coarsened dimensions exactly.
    """
    print("\n─── CEM Matching ────────────────────────────────────────────────────────")
    df = df.copy()

    # Assign WFP 2014 quintile (1–5 based on national wfp_mean_pct distribution)
    df["wfp_quintile"] = pd.qcut(
        df["wfp_mean_pct"], q=5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    df["cem_cell"] = (
        df["wfp_quintile"].astype(str) + "_fire" + df["fire_pre2013"].astype(int).astype(str)
    )

    rows = []
    for cell, grp in df.groupby("cem_cell"):
        n_t = (grp["treated"] == 1).sum()
        n_c = (grp["treated"] == 0).sum()
        if n_t == 0 or n_c == 0:
            continue
        ctrl_weight = n_t / n_c
        for _, row in grp.iterrows():
            w = 1.0 if row["treated"] == 1 else ctrl_weight
            rows.append({"GISJOIN": row["GISJOIN"], "treated": row["treated"],
                         "cem_weight": w, "cem_cell": cell})

    cem = pd.DataFrame(rows)
    n_t_matched = (cem["treated"] == 1).sum()
    n_c_matched = (cem["treated"] == 0).sum()
    n_t_total   = (df["treated"] == 1).sum()
    n_c_total   = (df["treated"] == 0).sum()
    print(f"  Cells with matched treated+controls: {cem['cem_cell'].nunique()}")
    print(f"  Treated retained: {n_t_matched:,} / {n_t_total:,} ({100*n_t_matched/n_t_total:.1f}%)")
    print(f"  Controls retained: {n_c_matched:,} / {n_c_total:,} ({100*n_c_matched/n_c_total:.1f}%)")

    # Within-cell SMD on wfp_mean_pct (should be near 0 since Q1–Q5 exactly matched)
    cem_full = df.merge(cem[["GISJOIN", "cem_weight", "cem_cell"]], on="GISJOIN", how="inner")
    t_wfp = cem_full.loc[cem_full["treated"] == 1, "wfp_mean_pct"].values
    c_wfp = cem_full.loc[cem_full["treated"] == 0, "wfp_mean_pct"].values
    c_wgt = cem_full.loc[cem_full["treated"] == 0, "cem_weight"].values
    print(f"  Post-CEM SMD (mean WFP 2014): {smd(t_wfp, c_wfp, c_wgt):.3f}")
    return cem


# ── PS overlap plot ───────────────────────────────────────────────────────────

def ps_overlap_plot(df: pd.DataFrame, out_path: Path) -> None:
    t_ps = df.loc[df["treated"] == 1, "ps"]
    c_ps = df.loc[df["treated"] == 0, "ps"]

    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    bins = np.linspace(0, 1, 60)
    ax.hist(c_ps, bins=bins, density=True, alpha=0.5, color="#2166ac",
            label="Never-treated (caliper-trimmed)")
    ax.hist(t_ps, bins=bins, density=True, alpha=0.65, color="#d6604d",
            label="Treated (fire 2015–17)")
    ax.set_xlabel("Estimated propensity score (WFP 2014 model)")
    ax.set_ylabel("Density")
    ax.set_title("PS overlap: treated vs. caliper-restricted controls")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] PS overlap plot: {out_path.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("PS-IPW MATCHING v3: WFP 2014, PS caliper, CEM robustness")
    print("=" * 70)
    RESULTS.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df = drop_missing_ps(df)
    df = apply_ps_caliper(df, caliper_sd=CALIPER_SD)

    bal = balance_table(df)
    print_balance(bal)

    cem = compute_cem_weights(df)

    # ── Save IPW outputs ──
    weights_out = df[["GISJOIN", "treated", "ps", "ipw_weight"]].copy()
    weights_out.to_parquet(PROCESSED / "ipw_weights.parquet", index=False)
    weights_out.to_csv(RESULTS / "ipw_weights.csv", index=False)
    bal.to_csv(RESULTS / "balance_table.csv", index=False)
    ps_overlap_plot(df, RESULTS / "ps_overlap.png")

    # ── Save CEM outputs ──
    cem.to_parquet(PROCESSED / "cem_weights.parquet", index=False)
    cem.to_csv(RESULTS / "cem_weights.csv", index=False)

    # ── PS range summary ──
    t_ps = df.loc[df["treated"] == 1, "ps"]
    c_ps = df.loc[df["treated"] == 0, "ps"]
    print(f"\nPS overlap (final, post-caliper):")
    print(f"  Treated:  [{t_ps.min():.3f}, {t_ps.max():.3f}]  mean={t_ps.mean():.3f}")
    print(f"  Controls: [{c_ps.min():.3f}, {c_ps.max():.3f}]  mean={c_ps.mean():.3f}")

    print(f"\n[OK] Saved:")
    print(f"     data/processed/ipw_weights.parquet  ({len(weights_out):,} rows)")
    print(f"     data/processed/cem_weights.parquet   ({len(cem):,} rows)")
    print(f"     results/balance_table.csv")
    print(f"     results/ps_overlap.png")


if __name__ == "__main__":
    main()
