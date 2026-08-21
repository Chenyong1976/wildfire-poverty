"""
Pre-trend diagnostic tests for the wildfire DiD event study.

Tests implemented:
  (1) Wald tests: H₀: β₋₂ = 0 (primary pre-trend) and H₀: β₋₃ = β₋₂ = 0 (joint)
      for each outcome × specification (unweighted / IPW).
      Note: h=-3 uses 2000-vintage boundaries; boundary mismatch is the expected
      explanation for large β₋₃. The primary test is β₋₂ = 0 only.

  (3) Drop h=-3 specification: re-estimate with periods {-2, -1, 0, +1, +2} only,
      eliminating the boundary-contaminated pre-period. Compare ATTs to main spec.

  (4) Fake-timing placebo DiD: restrict to pre-treatment periods (ACS 2010, 2012, 2014);
      remap time as {2010: -1(ref), 2012: 0, 2014: +1}. Under parallel trends, the
      DiD coefficients at h_p=0 and h_p=+1 should be statistically indistinguishable
      from zero. A significant positive coefficient indicates pre-existing differential
      trends between treated and control tracts.

Inputs:
  data/processed/acs_tract_panel_xwalk.parquet
  data/processed/fire_treatment_tracts.parquet
  data/processed/ipw_weights.parquet

Outputs:
  results/pretrend_wald_tests.csv        Wald test statistics and p-values
  results/es_coefs_{outcome}_no_h3.csv  Event-study coefficients without h=-3
  results/att_no_h3.csv                 Aggregate ATT without h=-3
  results/placebo_coefs.csv             Fake-timing placebo DiD coefficients
  results/pretrend_summary.txt          Human-readable summary
"""

import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

YEAR_TO_H = {2010: -3, 2012: -2, 2014: -1, 2022: 0, 2023: 1, 2024: 2}

OUTCOMES = {
    "poverty_rate":        {"label": "Poverty rate (pp)",            "scale": 100},
    "log_med_income_2020": {"label": "Log median HH income (2020$)", "scale": 1},
    "employment_rate":     {"label": "Employment rate (pp)",          "scale": 100},
    "in_migration_rate":   {"label": "In-migration rate (pp)",        "scale": 100},
    "vacancy_rate":        {"label": "Vacancy rate (pp)",             "scale": 100},
    "owner_occ_rate":      {"label": "Owner-occupancy rate (pp)",     "scale": 100},
}


# ── Data loading (shared with 01_did_estimation.py) ───────────────────────────

def load_data() -> pd.DataFrame:
    panel = pd.read_parquet(
        PROCESSED / "acs_tract_panel_xwalk.parquet",
        columns=[
            "NHGISCODE", "acs_year", "COUNTYFP",
            "poverty_rate", "log_med_income_2020",
            "employment_rate", "in_migration_rate",
        ],
    )
    housing = pd.read_parquet(
        PROCESSED / "housing_tract_panel.parquet",
        columns=["NHGISCODE", "acs_year", "vacancy_rate", "owner_occ_rate"],
    )
    panel = panel.merge(housing, on=["NHGISCODE", "acs_year"], how="left")

    fire = pd.read_parquet(
        PROCESSED / "fire_treatment_tracts.parquet",
        columns=["GISJOIN", "treated", "never_treated", "COUNTYFP10"],
    )
    wts = pd.read_parquet(
        PROCESSED / "ipw_weights.parquet",
        columns=["GISJOIN", "ipw_weight"],
    )
    df = (
        panel
        .merge(fire, left_on="NHGISCODE", right_on="GISJOIN", how="left")
        .merge(wts,  left_on="NHGISCODE", right_on="GISJOIN", how="left")
    )
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()
    df["h"] = df["acs_year"].map(YEAR_TO_H).astype(int)
    df["county_cluster"] = df["COUNTYFP10"].fillna(df["COUNTYFP"])
    df["wt_ipw"] = np.where(df["treated"] == 1, 1.0, df["ipw_weight"].fillna(0.0))
    return df


def fit_es(outcome: str, df: pd.DataFrame,
           weight_col: str | None = None, h_ref: int = -1) -> pf.Feols:
    fml = f"{outcome} ~ i(h, treated, ref={h_ref}) | NHGISCODE + acs_year"
    return pf.feols(fml, data=df, vcov={"CRV1": "county_cluster"},
                    weights=weight_col)


def wald_test_pretrends(fit: pf.Feols,
                        h_vals: list[int]) -> dict:
    """
    Joint Wald test H₀: all β_h = 0 for h in h_vals.
    Returns chi2 statistic, degrees of freedom, and p-value.
    Uses chi2 distribution (pyfixest default for non-identity R).
    """
    names = list(fit.coef().index)
    k = len(names)
    target = [f"h::{h}:treated" for h in h_vals]
    idx = [names.index(t) for t in target if t in names]
    if not idx:
        return {"stat": np.nan, "df": 0, "pvalue": np.nan, "note": "coefficients not found"}
    R = np.zeros((len(idx), k))
    for row, col in enumerate(idx):
        R[row, col] = 1.0
    result = fit.wald_test(R=R, q=np.zeros(len(idx)))
    return {
        "stat":   float(result["statistic"]),
        "df":     len(idx),
        "pvalue": float(result["pvalue"]),
    }


# ── Test 1: Wald tests ────────────────────────────────────────────────────────

def run_wald_tests(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("TEST 1: Wald pre-trend tests")
    print("=" * 60)
    print(f"  {'Outcome':<28} {'Spec':<12} {'Test':<20} {'χ²':>8} {'df':>4} {'p-val':>8}")
    print(f"  {'-'*28} {'-'*12} {'-'*20} {'-'*8} {'-'*4} {'-'*8}")

    df_cs = df[(df["treated"] == 1) | (df["wt_ipw"] > 0)].copy()
    rows = []

    for outcome in OUTCOMES:
        for spec, df_s, wcol in [
            ("unweighted", df,    None),
            ("ipw",        df_cs, "wt_ipw"),
        ]:
            fit = fit_es(outcome, df_s, wcol)

            for test_label, h_vals in [
                ("H0: β(-2)=0 [primary]",   [-2]),
                ("H0: β(-3)=β(-2)=0 [jt]",  [-3, -2]),
            ]:
                r = wald_test_pretrends(fit, h_vals)
                flag = "[**]" if r["pvalue"] < 0.05 else (
                       "[* ]" if r["pvalue"] < 0.10 else "    ")
                print(f"  {outcome:<28} {spec:<12} {test_label:<20} "
                      f"{r['stat']:>8.3f} {r['df']:>4d} {r['pvalue']:>8.4f} {flag}")
                rows.append({
                    "outcome": outcome, "spec": spec,
                    "test": test_label,
                    **r,
                })

    note = (
        "χ² statistic (chi2 distribution). [**] p<0.05, [*] p<0.10.\n"
        "H0: β(-2)=0 is the primary pre-trend test (2010-vintage boundaries).\n"
        "H0: β(-3)=β(-2)=0 is informative but h=-3 uses 2000-vintage boundaries "
        "(expect spurious rejection due to boundary mismatch, not genuine trends)."
    )
    print(f"\n  Note: {note}")
    return pd.DataFrame(rows)


# ── Test 3: Drop h=-3 ─────────────────────────────────────────────────────────

def run_no_h3(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("\n" + "=" * 60)
    print("TEST 3: Drop h=-3 (eliminate 2000-vintage boundary period)")
    print("=" * 60)

    df_no3 = df[df["h"] != -3].copy()
    df_cs_no3 = df_no3[(df_no3["treated"] == 1) | (df_no3["wt_ipw"] > 0)].copy()

    all_coefs, att_rows = [], []

    print(f"\n  {'Outcome':<28} {'Spec':<12} {'ATT (no h-3)':>14} {'ATT (full)':>12} {'Diff':>8}")
    print(f"  {'-'*28} {'-'*12} {'-'*14} {'-'*12} {'-'*8}")

    # Load full-spec ATTs for comparison
    att_full = pd.read_csv(RESULTS / "att_aggregate.csv")

    for outcome, info in OUTCOMES.items():
        sc = info["scale"]
        for spec, df_s, wcol in [
            ("unweighted", df_no3,    None),
            ("ipw",        df_cs_no3, "wt_ipw"),
        ]:
            fit = fit_es(outcome, df_s, wcol)
            tidy = fit.tidy().reset_index()
            tidy["h"] = tidy["Coefficient"].str.extract(r"::([-\d]+):").astype(int)
            tidy = tidy.rename(columns={
                "Estimate": "coef", "Std. Error": "se",
                "2.5%": "ci_lo", "97.5%": "ci_hi",
            })
            tidy["outcome"] = outcome
            tidy["spec"] = spec
            all_coefs.append(tidy[["outcome", "spec", "h", "coef", "se", "ci_lo", "ci_hi"]])

            # Aggregate ATT
            post = tidy[tidy["h"] >= 0]
            att_est = post["coef"].mean()
            att_se  = post["se"].max()
            att_rows.append({
                "outcome": outcome, "spec": spec,
                "att": att_est, "se": att_se,
                "ci_lo": att_est - 1.96 * att_se,
                "ci_hi": att_est + 1.96 * att_se,
            })

            # Compare to full spec
            ref = att_full[(att_full["outcome"] == outcome) & (att_full["spec"] == spec)]
            att_full_val = ref["att"].values[0] * sc if not ref.empty else np.nan
            att_no3_val  = att_est * sc
            print(f"  {outcome:<28} {spec:<12} {att_no3_val:>+14.4f} "
                  f"{att_full_val:>+12.4f} {att_no3_val - att_full_val:>+8.4f}")

    all_coefs_df = pd.concat(all_coefs, ignore_index=True)
    att_df = pd.DataFrame(att_rows)
    return all_coefs_df, att_df


# ── Test 4: Fake-timing placebo DiD ──────────────────────────────────────────

def run_placebo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Restrict to pre-treatment periods (ACS 2010, 2012, 2014).
    Remap time as: 2010→-1 (reference), 2012→0, 2014→+1.
    Estimate DiD on actual treated vs. never-treated controls.

    Under parallel trends: β₀ and β₊₁ should both ≈ 0.
    A significant positive β₀ or β₊₁ indicates that treated tracts were
    already diverging from controls before any fires occurred.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Fake-timing placebo DiD (pre-treatment periods only)")
    print("=" * 60)
    print("  Mapping: ACS 2010 → h_p=-1 (ref), 2012 → h_p=0, 2014 → h_p=+1")
    print("  H₀: β(h_p=0) = β(h_p=+1) = 0 (no pre-existing differential trend)\n")

    placebo_map = {2010: -1, 2012: 0, 2014: 1}
    df_pre = df[df["acs_year"].isin([2010, 2012, 2014])].copy()
    df_pre["h_placebo"] = df_pre["acs_year"].map(placebo_map).astype(int)

    rows = []
    print(f"  {'Outcome':<28} {'h_p=0 (2012)':>14} {'h_p=+1 (2014)':>14} {'Wald joint p':>14}")
    print(f"  {'-'*28} {'-'*14} {'-'*14} {'-'*14}")

    for outcome, info in OUTCOMES.items():
        sc = info["scale"]
        # Use acs_year as the time FE (3 distinct values: 2010, 2012, 2014)
        fml = f"{outcome} ~ i(h_placebo, treated, ref=-1) | NHGISCODE + acs_year"
        fit = pf.feols(fml, data=df_pre, vcov={"CRV1": "county_cluster"})

        tidy = fit.tidy().reset_index()
        tidy["h_p"] = tidy["Coefficient"].str.extract(r"::([-\d]+):").astype(int)
        tidy = tidy.rename(columns={"Estimate": "coef", "Std. Error": "se",
                                     "2.5%": "ci_lo", "97.5%": "ci_hi"})

        names = list(fit.coef().index)
        k     = len(names)
        # Joint Wald: β(h_p=0) = β(h_p=+1) = 0
        target_names = ["h_placebo::0:treated", "h_placebo::1:treated"]
        idx = [names.index(t) for t in target_names if t in names]
        R   = np.zeros((len(idx), k))
        for row_i, col_i in enumerate(idx):
            R[row_i, col_i] = 1.0
        wald = fit.wald_test(R=R, q=np.zeros(len(idx)))
        p_joint = float(wald["pvalue"])

        for _, row in tidy.iterrows():
            flag = "[**]" if abs(row["coef"]) / max(row["se"], 1e-10) > 1.96 else "    "
            rows.append({
                "outcome": outcome,
                "h_placebo": int(row["h_p"]),
                "coef": row["coef"], "se": row["se"],
                "ci_lo": row["ci_lo"], "ci_hi": row["ci_hi"],
                "wald_joint_p": p_joint,
            })

        v = tidy.set_index("h_p")["coef"]
        s = tidy.set_index("h_p")["se"]

        def fmt(h):
            c = v.get(h, np.nan) * sc
            se = s.get(h, np.nan) * sc
            sig = "[**]" if abs(c) / max(se, 1e-10) > 1.96 else "    "
            return f"{c:+.4f} ({se:.4f}){sig}"

        flag_j = "[**]" if p_joint < 0.05 else ("[* ]" if p_joint < 0.10 else "    ")
        print(f"  {outcome:<28} {fmt(0):>14} {fmt(1):>14} {p_joint:>12.4f} {flag_j}")

    print(f"\n  Interpretation: coefficients in outcome units (pp or log pts).")
    print(f"  Standard errors in parentheses. [**] |z|>1.96, [*] p<0.10.")
    print(f"  Joint Wald tests whether h_p=0 AND h_p=+1 are jointly zero.")
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("PRE-TREND DIAGNOSTIC TESTS")
    print("=" * 70)
    RESULTS.mkdir(parents=True, exist_ok=True)

    df = load_data()
    print(f"Sample: {len(df):,} rows | "
          f"{int((df['treated']==1).sum()/6):,} treated | "
          f"{int((df['never_treated']==1).sum()/6):,} controls")

    # Test 1: Wald tests
    wald_df = run_wald_tests(df)
    wald_df.to_csv(RESULTS / "pretrend_wald_tests.csv", index=False)
    print(f"\n  [OK] Saved: results/pretrend_wald_tests.csv")

    # Test 3: Drop h=-3
    coefs_no3, att_no3 = run_no_h3(df)
    for outcome in OUTCOMES:
        sub = coefs_no3[coefs_no3["outcome"] == outcome]
        sub.to_csv(RESULTS / f"es_coefs_{outcome}_no_h3.csv", index=False)
    att_no3.to_csv(RESULTS / "att_no_h3.csv", index=False)
    print(f"\n  [OK] Saved: results/es_coefs_*_no_h3.csv + results/att_no_h3.csv")

    # Test 4: Placebo
    placebo_df = run_placebo(df)
    placebo_df.to_csv(RESULTS / "placebo_coefs.csv", index=False)
    print(f"\n  [OK] Saved: results/placebo_coefs.csv")

    # Consolidated summary
    summary_lines = [
        "PRE-TREND DIAGNOSTIC SUMMARY",
        "=" * 60,
        "",
        "TEST 1: Wald test H₀: β(-2) = 0 (primary, unweighted)",
    ]
    for _, row in wald_df[
        (wald_df["spec"] == "unweighted") &
        (wald_df["test"].str.contains("primary"))
    ].iterrows():
        sig = "FAIL p<0.05" if row["pvalue"] < 0.05 else (
              "WARN p<0.10" if row["pvalue"] < 0.10 else "PASS")
        summary_lines.append(
            f"  {row['outcome']:<30} χ²={row['stat']:.3f}  p={row['pvalue']:.4f}  [{sig}]"
        )

    summary_lines += [
        "",
        "TEST 3: ATT stability — drop h=-3 vs. full spec (unweighted, scaled)",
    ]
    att_full = pd.read_csv(RESULTS / "att_aggregate.csv")
    for _, row in att_no3[att_no3["spec"] == "unweighted"].iterrows():
        sc = OUTCOMES[row["outcome"]]["scale"]
        ref = att_full[(att_full["outcome"] == row["outcome"]) &
                       (att_full["spec"] == "unweighted")]
        full_val = ref["att"].values[0] * sc if not ref.empty else np.nan
        no3_val  = row["att"] * sc
        summary_lines.append(
            f"  {row['outcome']:<30} full={full_val:+.4f}  no-h3={no3_val:+.4f}  "
            f"diff={no3_val-full_val:+.4f}"
        )

    summary_lines += [
        "",
        "TEST 4: Fake-timing placebo (joint Wald p, unweighted)",
    ]
    for outcome in OUTCOMES:
        sub = placebo_df[placebo_df["outcome"] == outcome]
        p = sub["wald_joint_p"].iloc[0] if not sub.empty else np.nan
        sig = "FAIL p<0.05" if p < 0.05 else ("WARN p<0.10" if p < 0.10 else "PASS")
        summary_lines.append(f"  {outcome:<30} joint p={p:.4f}  [{sig}]")

    summary_lines += [
        "",
        "Note: h=-3 uses 2000-vintage tract boundaries (not 2010-vintage like h=-2/-1).",
        "      Large h=-3 coefficients are attributable to boundary mismatch, not trends.",
        "      Primary pre-trend criterion is β(-2) = 0 (Test 1, primary row).",
    ]

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)
    (RESULTS / "pretrend_summary.txt").write_text(summary_text, encoding="utf-8")
    print(f"\n  [OK] Saved: results/pretrend_summary.txt")


if __name__ == "__main__":
    main()
