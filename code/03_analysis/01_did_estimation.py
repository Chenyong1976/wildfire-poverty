"""
DiD Event-Study Estimation: Wildfire Impact on Poverty (Single Cohort)

Design: Single clean cohort (fires 2015-2017), never-treated controls.
Estimating equation:
  Y_{it} = a_i + l_t + sum_{h != -1} b_h * D_i * 1[t=h] + e_{it}
  h in {-3(2010), -2(2012), -1(2014,ref), 0(2022), +1(2023), +2(2024)}
  D_i = 1 if treated (fire 2015-2017); cluster SE by county.

With a single cohort, TWFE is numerically equivalent to
Callaway & Sant'Anna (2021) -- no Goodman-Bacon decomposition concerns.

Specifications:
  (1) Unweighted TWFE (primary)
  (2) IPW-weighted TWFE on common-support sample (robustness)

In-migration decomposition (added 2026-08-16):
  in_migration_rate = mover_count / mig_total (rate)
  log_mig_pop       = log(mig_total)           (denominator channel)
  log_mover_count   = log(mig_total - mig_stayer) (numerator channel)
  If rate ATT driven by population loss: log_mig_pop < 0, log_mover_count ~ 0
  If rate ATT driven by genuine arrivals: log_mig_pop ~ 0, log_mover_count > 0
  Note: log_mig_pop uses mig_total (B07003 pop 1yr+, r=0.9998 with B01003);
  population (B01003) is null for all pre-treatment periods in this panel.

Inputs:
  data/processed/acs_tract_panel_xwalk.parquet
  data/processed/fire_treatment_tracts.parquet
  data/processed/ipw_weights.parquet
  data/processed/housing_tract_panel.parquet  (vacancy, owner-occupancy)

Outputs:
  results/es_coefs_<outcome>.csv           event-study coefficients + 95% CI
  results/att_aggregate.csv                aggregate ATT (mean h=0,+1,+2)
  results/es_plot_<outcome>.png            event-study plot (8 outcomes)
  results/fig_migration_decomp.png/.pdf    three-panel decomposition figure
  results/fig_housing_channels.png/.pdf    two-panel housing channel figure
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
import pyfixest as pf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

YEAR_TO_H = {2010: -3, 2012: -2, 2014: -1, 2022: 0, 2023: 1, 2024: 2}
ACS_LABEL = {-3: "-3\n(2010)", -2: "-2\n(2012)", -1: "-1\n(2014)",
              0: "0\n(2022)", 1: "+1\n(2023)", 2: "+2\n(2024)"}

OUTCOMES = {
    "poverty_rate":       {"label": "Poverty rate (pp)",                   "scale": 100},
    "log_med_income_2020":{"label": "Log median HH income (2020$)",        "scale": 1},
    "employment_rate":    {"label": "Employment rate (pp)",                 "scale": 100},
    "in_migration_rate":  {"label": "In-migration rate (pp)",               "scale": 100},
    "log_mig_pop":        {"label": "Log population (mig. base)",           "scale": 1},
    "log_mover_count":    {"label": "Log mover count",                      "scale": 1},
}

# Decomposition outcomes for the three-panel figure (subset of OUTCOMES)
DECOMP_OUTCOMES = ["in_migration_rate", "log_mig_pop", "log_mover_count"]
DECOMP_LABELS   = {
    "in_migration_rate": "In-migration rate (pp)",
    "log_mig_pop":       "Log population\n(denominator channel)",
    "log_mover_count":   "Log mover count\n(numerator channel)",
}

# Housing channel outcomes (two-panel figure; medium priority)
HOUSING_OUTCOMES = {
    "vacancy_rate":    {"label": "Vacancy rate (pp)",        "scale": 100},
    "owner_occ_rate":  {"label": "Owner-occupancy rate (pp)", "scale": 100},
}


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    panel = pd.read_parquet(
        PROCESSED / "acs_tract_panel_xwalk.parquet",
        columns=[
            "NHGISCODE", "acs_year", "COUNTYFP",
            "poverty_rate", "log_med_income_2020",
            "employment_rate", "in_migration_rate",
            "mig_total", "mig_stayer",
        ],
    )
    # Decomposition outcomes: log(population proxy) and log(mover count)
    # mig_total is B07003 pop 1yr+ (r=0.9998 with B01003; B01003 null pre-2022)
    panel["log_mig_pop"]     = np.log(panel["mig_total"].clip(lower=1))
    panel["log_mover_count"] = np.log(
        (panel["mig_total"] - panel["mig_stayer"]).clip(lower=1)
    )

    # Housing outcomes (vacancy rate, owner-occupancy rate)
    housing_path = PROCESSED / "housing_tract_panel.parquet"
    if housing_path.exists():
        housing = pd.read_parquet(
            housing_path,
            columns=["NHGISCODE", "acs_year", "vacancy_rate", "owner_occ_rate"],
        )
        panel = panel.merge(housing, on=["NHGISCODE", "acs_year"], how="left")
        n_vac = panel["vacancy_rate"].notna().sum()
        print(f"Housing outcomes merged: {n_vac:,} non-null vacancy_rate rows")
    else:
        print("[WARNING] housing_tract_panel.parquet not found -- "
              "run code/01_build/04_housing_nhgis_load.py first")
        panel["vacancy_rate"]   = np.nan
        panel["owner_occ_rate"] = np.nan

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
        .merge(wts,  left_on="NHGISCODE", right_on="GISJOIN", how="left",
               suffixes=("", "_wt"))
    )

    # Restrict to treated + never-treated
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()

    # Relative time
    df["h"] = df["acs_year"].map(YEAR_TO_H)

    # County cluster: prefer COUNTYFP10 from fire file, fall back to panel
    df["county_cluster"] = df["COUNTYFP10"].fillna(df["COUNTYFP"])

    # IPW weight column: treated=1, IPW controls per weight file, off-support=0
    df["wt_ipw"] = np.where(df["treated"] == 1, 1.0, df["ipw_weight"].fillna(0.0))

    print(f"Analysis sample: {len(df):,} rows | "
          f"{int((df['treated']==1).sum() / 6):,} treated tracts | "
          f"{int((df['never_treated']==1).sum() / 6):,} control tracts")

    n_null = df["h"].isna().sum()
    if n_null:
        print(f"[WARNING] {n_null} rows have no h mapping — dropping")
        df = df.dropna(subset=["h"])
    df["h"] = df["h"].astype(int)
    return df


# ── Event-study estimation ────────────────────────────────────────────────────

def run_es(outcome: str, df: pd.DataFrame,
           weight_col: str | None = None,
           suffix: str = "") -> pd.DataFrame:
    fml = f"{outcome} ~ i(h, treated, ref=-1) | NHGISCODE + acs_year"
    fit = pf.feols(
        fml,
        data=df,
        vcov={"CRV1": "county_cluster"},
        weights=weight_col,
    )
    tidy = fit.tidy().reset_index()
    # Extract h values from coefficient names like "h::-3:treated"
    tidy["h"] = tidy["Coefficient"].str.extract(r"::([-\d]+):").astype(int)
    tidy = tidy.rename(columns={
        "Estimate":     "coef",
        "Std. Error":   "se",
        "2.5%":         "ci_lo",
        "97.5%":        "ci_hi",
    })
    tidy["outcome"] = outcome
    tidy["spec"] = suffix
    return tidy[["outcome", "spec", "h", "coef", "se", "ci_lo", "ci_hi"]]


# ── Event-study plot ──────────────────────────────────────────────────────────

def plot_es(coefs: pd.DataFrame, label: str, scale: float, out_path: Path) -> None:
    uw = coefs[coefs["spec"] == "unweighted"].copy()
    ipw = coefs[coefs["spec"] == "ipw"].copy()

    # Add reference row (h=-1, coef=0)
    ref = pd.DataFrame([{"h": -1, "coef": 0, "ci_lo": 0, "ci_hi": 0, "se": 0}])
    uw  = pd.concat([uw,  ref], ignore_index=True).sort_values("h")
    ipw = pd.concat([ipw, ref], ignore_index=True).sort_values("h")

    for df_s in [uw, ipw]:
        for col in ["coef", "ci_lo", "ci_hi"]:
            df_s[col] = df_s[col] * scale

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    ax.axvspan(-3.5, -0.5, color="grey", alpha=0.12, zorder=0)
    ax.axhline(0, linewidth=0.4, color="grey")
    ax.axvline(-0.5, linewidth=0.4, linestyle="--", color="grey")

    # IPW (robustness, dashed orange)
    ax.fill_between(ipw["h"], ipw["ci_lo"], ipw["ci_hi"],
                    color="#fc8d59", alpha=0.15)
    ax.plot(ipw["h"], ipw["coef"], color="#fc8d59", linewidth=0.8,
            linestyle="--", label="IPW-weighted (robustness)")

    # Unweighted (primary, solid blue)
    ax.fill_between(uw["h"], uw["ci_lo"], uw["ci_hi"],
                    color="#2166ac", alpha=0.20)
    ax.plot(uw["h"], uw["coef"], color="#2166ac", linewidth=1.2,
            label="Unweighted TWFE (primary)")
    ax.scatter(uw["h"], uw["coef"], color="#2166ac", s=28, zorder=5)

    h_order = sorted(YEAR_TO_H.values())
    ax.set_xticks(h_order)
    ax.set_xticklabels([ACS_LABEL[h] for h in h_order], fontsize=8)
    ax.set_xlabel("Relative period (h)", fontsize=9)
    ax.set_ylabel(label, fontsize=9)
    ax.set_title(f"Event-study DiD: {label}", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    caption = (
        "Shaded: pre-treatment region. h = -1 (ACS 2014) reference (normalized 0).\n"
        "95% CIs, cluster SE by county. IPW sample: WFP-restricted common support."
    )
    ax.text(0.5, -0.18, caption, transform=ax.transAxes,
            ha="center", fontsize=7, color="grey")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ── Two-panel housing channel figure ─────────────────────────────────────────

def plot_housing_channels(all_coefs: pd.DataFrame, out_stem: Path) -> None:
    """
    Two-panel event-study figure for housing channel outcomes.

    Panel layout:
      [A] Vacancy rate (pp)        -- if positive: housing destruction / abandonment
      [B] Owner-occupancy rate (pp) -- if negative: homeowner exit, renter replacement

    Connects to in-migration mechanism: compositional sorting via tenure shift
    (high-WFP rural areas have high owner-occupancy; post-fire, if owners exit
    and renters replace, the remaining population is mechanically more mobile).
    """
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.5), dpi=150,
                              sharey=False, sharex=True)
    fig.suptitle("Housing Channel: Vacancy and Owner-Occupancy (B25002/B25003)",
                 fontsize=10, y=1.01)

    h_order = sorted(YEAR_TO_H.values())
    ref_row  = pd.DataFrame([{"h": -1, "coef": 0, "ci_lo": 0, "ci_hi": 0}])
    outcomes = list(HOUSING_OUTCOMES.keys())
    letters  = ["A", "B"]

    for ax, outcome, letter in zip(axes, outcomes, letters):
        info = HOUSING_OUTCOMES[outcome]
        sub  = all_coefs[
            (all_coefs["outcome"] == outcome) &
            (all_coefs["spec"] == "unweighted")
        ].copy()
        if sub.empty:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center")
            continue
        sub = pd.concat([sub, ref_row], ignore_index=True).sort_values("h")
        sc  = info["scale"]
        for col in ["coef", "ci_lo", "ci_hi"]:
            sub[col] = sub[col] * sc

        ax.axvspan(-3.5, -0.5, color="grey", alpha=0.12, zorder=0)
        ax.axhline(0, linewidth=0.4, color="grey")
        ax.axvline(-0.5, linewidth=0.4, linestyle="--", color="grey")
        ax.fill_between(sub["h"], sub["ci_lo"], sub["ci_hi"],
                        color="#1a9850", alpha=0.20)
        ax.plot(sub["h"], sub["coef"], color="#1a9850", linewidth=1.2)
        ax.scatter(sub["h"], sub["coef"], color="#1a9850", s=28, zorder=5)
        ax.set_xticks(h_order)
        ax.set_xticklabels([ACS_LABEL[h] for h in h_order], fontsize=7)
        ax.set_xlabel("Relative period (h)", fontsize=8)
        ax.set_ylabel(info["label"], fontsize=8)
        ax.set_title(f"({letter})", fontsize=9, loc="left")

    footer = (
        "Unweighted TWFE; 95% CIs cluster-SE by county. h=-1 (ACS 2014) reference. "
        "Shaded: pre-treatment region.\n"
        "B25002: occupancy status. B25003: tenure. "
        "Vacancy rise -> housing destruction. Owner-occ. decline -> compositional sorting."
    )
    fig.text(0.5, -0.04, footer, ha="center", fontsize=7, color="grey")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{out_stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out_stem.name}.png / .pdf")


# ── Three-panel decomposition figure ─────────────────────────────────────────

def plot_decomposition(all_coefs: pd.DataFrame, out_stem: Path) -> None:
    """
    Three-panel event-study figure decomposing the in-migration rate ATT into
    numerator (log mover count) and denominator (log population) channels.

    Panel layout (left to right):
      [A] in_migration_rate (pp) — the combined rate effect
      [B] log_mig_pop             — denominator: if negative, population fell
      [C] log_mover_count         — numerator:   if positive, more arrivals

    Interpretation guide printed in figure footer.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), dpi=150,
                             sharey=False, sharex=True)
    fig.suptitle("In-migration Rate Decomposition: Population vs. Mover-Count Channels",
                 fontsize=10, y=1.01)

    h_order = sorted(YEAR_TO_H.values())
    ref_row  = pd.DataFrame([{"h": -1, "coef": 0, "ci_lo": 0, "ci_hi": 0}])

    for ax, outcome in zip(axes, DECOMP_OUTCOMES):
        sub = all_coefs[
            (all_coefs["outcome"] == outcome) &
            (all_coefs["spec"] == "unweighted")
        ].copy()
        sub = pd.concat([sub, ref_row], ignore_index=True).sort_values("h")

        sc = OUTCOMES[outcome]["scale"]
        for col in ["coef", "ci_lo", "ci_hi"]:
            sub[col] = sub[col] * sc

        ax.axvspan(-3.5, -0.5, color="grey", alpha=0.12, zorder=0)
        ax.axhline(0, linewidth=0.4, color="grey")
        ax.axvline(-0.5, linewidth=0.4, linestyle="--", color="grey")
        ax.fill_between(sub["h"], sub["ci_lo"], sub["ci_hi"],
                        color="#2166ac", alpha=0.20)
        ax.plot(sub["h"], sub["coef"], color="#2166ac", linewidth=1.2)
        ax.scatter(sub["h"], sub["coef"], color="#2166ac", s=28, zorder=5)
        ax.set_xticks(h_order)
        ax.set_xticklabels([ACS_LABEL[h] for h in h_order], fontsize=7)
        ax.set_xlabel("Relative period (h)", fontsize=8)
        ax.set_ylabel(DECOMP_LABELS[outcome], fontsize=8)

        panel_letter = ["A", "B", "C"][DECOMP_OUTCOMES.index(outcome)]
        ax.set_title(f"({panel_letter})", fontsize=9, loc="left")

    footer = (
        "Unweighted TWFE; 95% CIs cluster-SE by county. h=-1 (ACS 2014) reference. "
        "Shaded: pre-treatment region.\n"
        "Decomposition: rate = movers / population. "
        "Panel B negative + Panel C near zero -> displacement (denominator). "
        "Panel C positive + Panel B near zero -> genuine arrivals (numerator)."
    )
    fig.text(0.5, -0.04, footer, ha="center", fontsize=7, color="grey")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{out_stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out_stem.name}.png / .pdf")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("DiD EVENT-STUDY: Wildfire 2015-2017 -> Poverty / Income / Employment")
    print("=" * 70)
    RESULTS.mkdir(parents=True, exist_ok=True)

    df = load_data()

    # IPW sample: treated (wt=1) + controls with positive IPW weight
    df_cs = df[(df["treated"] == 1) | (df["wt_ipw"] > 0)].copy()
    n_cs_treated = int((df_cs["treated"] == 1).sum() / 6)
    n_cs_ctrl    = int((df_cs["wt_ipw"] > 0).sum() / 6)
    print(f"IPW common-support sample: {n_cs_treated:,} treated + {n_cs_ctrl:,} controls")

    all_coefs = []

    print("\nRunning event-study regressions ...")
    all_outcome_specs = {**OUTCOMES, **HOUSING_OUTCOMES}
    for outcome, info in all_outcome_specs.items():
        print(f"  {outcome} ...")

        # (1) Unweighted — full never-treated control group
        es_uw  = run_es(outcome, df,    weight_col=None,       suffix="unweighted")
        # (2) IPW-weighted — common-support sample
        es_ipw = run_es(outcome, df_cs, weight_col="wt_ipw",   suffix="ipw")

        coefs = pd.concat([es_uw, es_ipw], ignore_index=True)
        coefs.to_csv(RESULTS / f"es_coefs_{outcome}.csv", index=False)
        all_coefs.append(coefs)

    all_coefs = pd.concat(all_coefs, ignore_index=True)

    # ── Aggregate ATT (simple mean of h=0,+1,+2 coefficients) ────────────────
    print("\nComputing aggregate ATT ...")
    att_rows = []
    for outcome, info in all_outcome_specs.items():
        for spec in ("unweighted", "ipw"):
            sub = all_coefs[
                (all_coefs["outcome"] == outcome) &
                (all_coefs["spec"] == spec) &
                (all_coefs["h"] >= 0)
            ]
            if sub.empty:
                continue
            att_est = sub["coef"].mean()
            att_se  = sub["se"].max()  # conservative bound
            att_rows.append({
                "outcome":   outcome,
                "spec":      spec,
                "att":       att_est,
                "se":        att_se,
                "ci_lo":     att_est - 1.96 * att_se,
                "ci_hi":     att_est + 1.96 * att_se,
                "n_periods": len(sub),
            })

    att_table = pd.DataFrame(att_rows)
    att_table.to_csv(RESULTS / "att_aggregate.csv", index=False)

    # ── Console summary ───────────────────────────────────────────────────────
    print("\n--- Aggregate ATT (unweighted, h=0,+1,+2 mean) ---")
    for outcome, info in all_outcome_specs.items():
        row = att_table[(att_table["outcome"] == outcome) &
                        (att_table["spec"] == "unweighted")]
        if row.empty:
            continue
        sc = info["scale"]
        r = row.iloc[0]
        print(f"  {outcome:<28}  ATT = {r['att']*sc:+.4f}  "
              f"[{r['ci_lo']*sc:+.4f}, {r['ci_hi']*sc:+.4f}]")

    print("\n--- Pre-trend coefficients (unweighted) ---")
    print(f"  {'Outcome':<28}  {'h=-3 (2010)':>12}  {'h=-2 (2012)':>12}")
    for outcome, info in all_outcome_specs.items():
        sub = all_coefs[(all_coefs["outcome"] == outcome) &
                        (all_coefs["spec"] == "unweighted") &
                        (all_coefs["h"].isin([-3, -2]))]
        sc = info["scale"]
        v = sub.set_index("h")["coef"]
        print(f"  {outcome:<28}  {v.get(-3, float('nan'))*sc:>+12.4f}  "
              f"{v.get(-2, float('nan'))*sc:>+12.4f}")

    # ── Plots ─────────────────────────────────────────────────────────────────
    print("\nSaving event-study plots ...")
    for outcome, info in all_outcome_specs.items():
        coefs = all_coefs[all_coefs["outcome"] == outcome]
        out_path = RESULTS / f"es_plot_{outcome}.png"
        plot_es(coefs, info["label"], info["scale"], out_path)
        print(f"  [OK] es_plot_{outcome}.png")

    print("\nSaving migration decomposition figure ...")
    plot_decomposition(all_coefs, RESULTS / "fig_migration_decomp")

    print("\nSaving housing channel figure ...")
    plot_housing_channels(all_coefs, RESULTS / "fig_housing_channels")

    print("\n[OK] All outputs saved to results/")
    print("     es_coefs_<outcome>.csv       (8 files)")
    print("     att_aggregate.csv")
    print("     es_plot_<outcome>.png        (8 files)")
    print("     fig_migration_decomp.png/.pdf")
    print("     fig_housing_channels.png/.pdf")


if __name__ == "__main__":
    main()
