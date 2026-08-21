"""
PS-IPW matching for first-fire restriction sensitivity analyses.

Runs propensity-score inverse-probability weighting for four specs:
  baseline  — no prior fire 1984-2014       (N=218 treated)
  s1a       — no prior fire 2000-2014       (N=300 treated)
  s1b       — no prior fire 2005-2014       (N=371 treated)
  s2_pooled — all cohort-fire tracts        (N=1,089 treated)

And three fire-count strata for the heterogeneity analysis:
  strat_0   — 0 prior fire years 1984-2014  (= baseline treated)
  strat_1   — 1 prior fire year  1984-2014
  strat_2p  — 2+ prior fire years 1984-2014 (collapsed)

For each spec/stratum:
  1. Merges matching_covariates + prior_fire_counts + treatment flags.
  2. Applies WFP floor (>=40) to controls.
  3. Fits a logistic PS model with spec-specific formula.
  4. Computes ATT weights (treated=1; controls=ps/(1-ps) trimmed at 95th pct).
  5. Writes:
       data/processed/ipw_weights_{label}.parquet
       data/processed/fire_treatment_{label}_for_R.csv
       data/processed/ipw_weights_{label}_for_R.csv
       results/balance_table_{label}.csv

Identification notes:
  S1a/S1b: prior fire history (1984-1999 or 1984-2004) now varies among treated
    tracts; added to PS formula as a continuous control.
  S2-pooled: prior_fire_stratum (0/1/2+) included as a factor covariate.
  S2-strata: within-stratum PS model (baseline formula; no fire count covariate).
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

ROOT      = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RESULTS   = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

TS_FILE = (
    ROOT / "data" / "raw" / "acs_extracts"
    / "nhgis_inc_pov_emp" / "nhgis0012_ts_nominal_tract.csv"
)

WFP_CTRL_FLOOR = 40.0
TRIM_PCT       = 0.95

# ── PS formula base (same as 01_ipw_weights.py v2) ──────────────────────────
PS_BASE = (
    "treated ~ wfp_mean_pct + wfp_mean_pct2"
    " + wfp_q4_frac + wfp_q5_frac + log_wfp_dist_km"
    " + pov_rate_2014 + log_inc_2014 + emp_rate_2014 + log_pop_2014"
    " + mig_rate_2014 + C(rucc_2013)"
)

BALANCE_COVARS = [
    "wfp_mean_pct", "wfp_q4_frac", "wfp_q5_frac", "log_wfp_dist_km",
    "fire_pre2013", "log_acres_pre2013",
    "fire_years_1984_2014",
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014",
]

# ── Spec definitions ─────────────────────────────────────────────────────────
# ps_extra: additional terms to append to PS_BASE (empty string = baseline formula)
SPECS = [
    {
        "label":    "baseline",
        "treat_file": "fire_treatment_tracts_baseline.parquet",
        "ps_extra":   "",
        "stratum":  None,   # None = all treated + matched controls
    },
    {
        "label":    "s1a",
        "treat_file": "fire_treatment_tracts_s1a.parquet",
        "ps_extra":   " + fire_years_1984_1999",
        "stratum":  None,
    },
    {
        "label":    "s1b",
        "treat_file": "fire_treatment_tracts_s1b.parquet",
        "ps_extra":   " + fire_years_1984_2004",   # engineered below
        "stratum":  None,
    },
    {
        "label":    "s2_pooled",
        "treat_file": "fire_treatment_tracts_s2_pooled.parquet",
        "ps_extra":   " + C(prior_fire_stratum)",
        "stratum":  None,
    },
    {
        "label":    "strat_0",
        "treat_file": "fire_treatment_tracts_baseline.parquet",
        "ps_extra":   "",
        "stratum":  0,
    },
    {
        "label":    "strat_1",
        "treat_file": "fire_treatment_tracts_s2_pooled.parquet",
        "ps_extra":   "",
        "stratum":  1,
    },
    {
        "label":    "strat_2p",
        "treat_file": "fire_treatment_tracts_s2_pooled.parquet",
        "ps_extra":   "",
        "stratum":  2,    # 2+ (clipped at 2 in prior_fire_counts)
    },
]


# ── Data loading ─────────────────────────────────────────────────────────────

def load_base_data() -> pd.DataFrame:
    """Load matching covariates + prior fire counts + population; engineer features."""
    covs = pd.read_parquet(PROCESSED / "matching_covariates.parquet")
    pcnt = pd.read_parquet(PROCESSED / "prior_fire_counts.parquet",
                           columns=["GISJOIN", "fire_years_1984_1999",
                                    "fire_years_2000_2014", "fire_years_2005_2014",
                                    "fire_years_1984_2014", "prior_fire_stratum"])
    df = covs.merge(pcnt, on="GISJOIN", how="left")

    # Population (log) from raw nominal time-series
    ts = pd.read_csv(TS_FILE, usecols=["NHGISCODE", "YEAR", "AV0AA"], low_memory=False)
    ts = (
        ts[ts["YEAR"] == "2010-2014"][["NHGISCODE", "AV0AA"]]
        .rename(columns={"NHGISCODE": "GISJOIN", "AV0AA": "pop_2014_raw"})
    )
    df = df.merge(ts, on="GISJOIN", how="left")
    df["log_pop_2014"] = np.log(df["pop_2014_raw"].clip(lower=1))

    # Engineered features
    df["wfp_mean_pct2"]      = df["wfp_mean_pct"] ** 2
    df["log_wfp_dist_km"]    = np.log(df["wfp_dist_km"].clip(lower=0.01))
    df["fire_years_1984_2004"] = (
        df["fire_years_1984_1999"] + df["fire_years_2000_2014"]
    )
    return df


def load_treatment(treat_file: str) -> pd.DataFrame:
    return pd.read_parquet(
        PROCESSED / treat_file,
        columns=["GISJOIN", "treated", "never_treated", "COUNTYFP10"],
    )


def merge_and_filter(
    base: pd.DataFrame,
    treat: pd.DataFrame,
    stratum: int | None,
) -> pd.DataFrame:
    """Merge covariates with treatment flags; filter to treated + controls."""
    df = base.merge(treat, on="GISJOIN", how="inner")
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()

    if stratum is not None:
        # Within-stratum: keep treated tracts in this stratum + controls in same stratum
        df = df[
            ((df["treated"] == 1) & (df["prior_fire_stratum"] == stratum)) |
            ((df["never_treated"] == 1) & (df["prior_fire_stratum"] == stratum))
        ].copy()

    n_t = (df["treated"] == 1).sum()
    n_c = (df["never_treated"] == 1).sum()
    print(f"  After merge: {n_t:,} treated + {n_c:,} controls")
    if n_t < 20 or n_c < 50:
        print(f"  [WARNING] Stratum too thin for reliable PS estimation.")
    return df


# ── IPW pipeline ─────────────────────────────────────────────────────────────

def apply_wfp_floor(df: pd.DataFrame) -> pd.DataFrame:
    before = (df["treated"] == 0).sum()
    mask = (df["treated"] == 1) | (df["wfp_mean_pct"] >= WFP_CTRL_FLOOR)
    df = df[mask].copy()
    after = (df["treated"] == 0).sum()
    print(f"  WFP floor: {before - after:,} controls dropped, {after:,} retained")
    return df


_PS_DROPNA_COLS = [
    "wfp_mean_pct", "wfp_mean_pct2",
    "wfp_q4_frac", "wfp_q5_frac", "log_wfp_dist_km",
    "pov_rate_2014", "log_inc_2014", "emp_rate_2014", "log_pop_2014",
    "mig_rate_2014",
]


def fit_and_weight(
    df: pd.DataFrame,
    formula: str,
    extra_dropna: list[str] | None = None,
) -> pd.DataFrame:
    drop_cols = _PS_DROPNA_COLS + (extra_dropna or [])
    drop_cols = [c for c in drop_cols if c in df.columns]
    before = len(df)
    df = df.dropna(subset=drop_cols).copy()
    if len(df) < before:
        print(f"  dropna removed {before - len(df):,} rows; {len(df):,} remaining")
    if df.empty:
        raise ValueError("No rows remain after dropping NA on PS covariates.")

    model = smf.logit(formula, data=df).fit(maxiter=300, disp=False)
    print(f"  PS model: converged={model.mle_retvals['converged']}, "
          f"pseudo-R²={model.prsquared:.3f}, n={int(model.nobs):,}")

    df["ps"] = model.predict(df)

    # Common support: drop controls below min treated PS
    ps_min_t = df.loc[df["treated"] == 1, "ps"].min()
    before = (df["treated"] == 0).sum()
    df = df[(df["treated"] == 1) | (df["ps"] >= ps_min_t)].copy()
    print(f"  Common support: {before - (df['treated']==0).sum():,} controls dropped")

    # ATT weights: treated=1, controls=ps/(1-ps) trimmed at TRIM_PCT
    df["ipw_raw"] = np.where(
        df["treated"] == 1,
        1.0,
        df["ps"] / (1.0 - df["ps"].clip(upper=0.9999)),
    )
    ctrl_mask = df["treated"] == 0
    clip_val = df.loc[ctrl_mask, "ipw_raw"].quantile(TRIM_PCT)
    df["ipw_weight"] = df["ipw_raw"].clip(upper=clip_val)
    df.loc[df["treated"] == 1, "ipw_weight"] = 1.0
    print(f"  Weight trim at p{TRIM_PCT*100:.0f}: {clip_val:.2f}")
    return df


def balance_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cov in BALANCE_COVARS:
        if cov not in df.columns:
            continue
        t_vals = df.loc[df["treated"] == 1, cov].dropna()
        c_vals_uw = df.loc[df["treated"] == 0, cov].dropna()
        c_vals_wt = df.loc[df["treated"] == 0, cov]
        wt_c = df.loc[df["treated"] == 0, "ipw_weight"]

        mean_t = t_vals.mean()
        mean_c_uw = c_vals_uw.mean()
        wt_valid = wt_c.notna() & c_vals_wt.notna()
        mean_c_wt = (
            np.average(c_vals_wt[wt_valid], weights=wt_c[wt_valid])
            if wt_valid.any() else np.nan
        )
        pooled_sd = np.sqrt(
            (t_vals.var(ddof=1) + c_vals_uw.var(ddof=1)) / 2
        )
        smd_before = (mean_t - mean_c_uw) / pooled_sd if pooled_sd > 0 else np.nan
        smd_after  = (mean_t - mean_c_wt) / pooled_sd if pooled_sd > 0 else np.nan
        rows.append({
            "covariate": cov,
            "mean_treated": mean_t,
            "mean_control_unweighted": mean_c_uw,
            "mean_control_weighted": mean_c_wt,
            "smd_before": smd_before,
            "smd_after": smd_after,
        })
    return pd.DataFrame(rows)


# ── Main ─────────────────────────────────────────────────────────────────────

def run_spec(base: pd.DataFrame, spec: dict) -> None:
    label = spec["label"]
    print(f"\n{'='*65}")
    print(f"SPEC: {label}")
    print(f"{'='*65}")

    treat = load_treatment(spec["treat_file"])
    df = merge_and_filter(base, treat, stratum=spec["stratum"])

    if df.empty or (df["treated"] == 1).sum() < 5:
        print(f"  [SKIP] Insufficient treated observations for {label}")
        return

    df = apply_wfp_floor(df)
    formula = PS_BASE + spec["ps_extra"]
    # Extra columns needed for dropna per spec
    extra = {
        "s1a":      ["fire_years_1984_1999"],
        "s1b":      ["fire_years_1984_2004"],
        "s2_pooled": ["prior_fire_stratum"],
    }.get(label, [])
    df = fit_and_weight(df, formula, extra_dropna=extra)

    bal = balance_table(df)
    smd_wfp_after = bal.loc[bal["covariate"] == "wfp_mean_pct", "smd_after"].values
    if smd_wfp_after.size:
        print(f"  WFP SMD after IPW: {smd_wfp_after[0]:.3f}")

    # Outputs
    weights_out = df[["GISJOIN", "treated", "ps", "ipw_weight"]].copy()
    weights_out.to_parquet(PROCESSED / f"ipw_weights_{label}.parquet", index=False)
    bal.to_csv(RESULTS / f"balance_table_{label}.csv", index=False)

    # R-ready CSVs
    fire_for_R = (
        treat[treat["GISJOIN"].isin(df["GISJOIN"])]
        .merge(
            base[["GISJOIN", "prior_fire_stratum"]],
            on="GISJOIN", how="left"
        )
    )
    fire_for_R.to_csv(
        PROCESSED / f"fire_treatment_{label}_for_R.csv", index=False
    )
    weights_out.to_csv(
        PROCESSED / f"ipw_weights_{label}_for_R.csv", index=False
    )
    print(f"  [OK] Saved: ipw_weights_{label}.parquet + CSVs")
    print(f"       Treated={weights_out['treated'].sum():,}  "
          f"Controls={(weights_out['treated']==0).sum():,}")


def main() -> None:
    print("=" * 65)
    print("SENSITIVITY WEIGHTS: First-Fire Restriction Specs")
    print("=" * 65)

    base = load_base_data()
    print(f"Base covariates loaded: {len(base):,} tracts")

    for spec in SPECS:
        run_spec(base, spec)

    print("\n[DONE] All sensitivity weight files written.")


if __name__ == "__main__":
    main()
