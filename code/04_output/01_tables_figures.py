"""
Publication-ready tables and figures for wildfire-poverty event study.

Outputs (results/tables/ and results/figures/):
  table2_main_results.tex     Event-study ATT across outcomes (Table 2 in paper)
  table3_robustness.tex       Robustness comparison: unweighted / IPW / DR-TWFE / HonestDiD
  fig1_es_income.png/.pdf     Event-study: log median income (primary outcome)
  fig2_es_income_no_h3.png    Sensitivity: drop h=-3 (income)
  fig3_es_poverty.png/.pdf    Event-study: poverty rate (secondary)
  fig4_es_migration.png/.pdf  Event-study: in-migration rate (mechanism)
  fig5_honestdid_income.png   Rambachan-Roth sensitivity: income
  fig6_honestdid_migration.png Rambachan-Roth sensitivity: migration

Notes on outcome framing (from estimation results):
  Log income:    cleanest causal result; HonestDiD breakdown M=1.0; unweighted -2.3%
  In-migration:  most robust to trend violations (breakdown M=1.5); +1.15pp
  Poverty rate:  DR-TWFE sign reversal; HonestDiD CI includes 0 at M=0 → downgraded
  Employment:    breakdown M=0 → robustness check only
  IPW income/migration: sign reversal vs. unweighted; flagged in notes
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
import matplotlib.ticker as mticker

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
RES  = ROOT / "results"
TABS = RES / "tables"
FIGS = RES / "figures"
TABS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

# ── Palette (AER-style publication colours) ───────────────────────────────────
BLUE   = "#2166ac"
ORANGE = "#d6604d"
GREY   = "#aaaaaa"

# ── Outcome metadata ──────────────────────────────────────────────────────────
OUTCOMES = {
    "log_med_income_2020": {
        "label": "Log median HH income",
        "unit":  "log pts",
        "scale": 1,
        "table_col": "(1)",
    },
    "poverty_rate": {
        "label": "Poverty rate",
        "unit":  "pp",
        "scale": 100,
        "table_col": "(2)",
    },
    "in_migration_rate": {
        "label": "In-migration rate",
        "unit":  "pp",
        "scale": 100,
        "table_col": "(3)",
    },
    "employment_rate": {
        "label": "Employment rate",
        "unit":  "pp",
        "scale": 100,
        "table_col": "(4)",
    },
}

YEAR_TO_H  = {2010: -3, 2012: -2, 2014: -1, 2022: 0, 2023: 1, 2024: 2}
H_TO_ACS   = {-3: "2010", -2: "2012", -1: "2014", 0: "2022", 1: "2023", 2: "2024"}
H_LABEL    = {
    -3: r"$h=-3$\ (ACS 2010)",
    -2: r"$h=-2$\ (ACS 2012)",
    -1: r"$h=-1$\ (ACS 2014, ref.)",
     0: r"$h=0$\ \ (ACS 2022)",
     1: r"$h=+1$\ (ACS 2023)",
     2: r"$h=+2$\ (ACS 2024)",
}
XTICKLABELS = {
    -3: "$h\\!=\\!-3$\n(2010)",
    -2: "$h\\!=\\!-2$\n(2012)",
    -1: "$h\\!=\\!-1$\n(2014)\nref.",
     0: "$h\\!=\\!0$\n(2022)",
     1: "$h\\!=\\!+1$\n(2023)",
     2: "$h\\!=\\!+2$\n(2024)",
}

# ── Load results ──────────────────────────────────────────────────────────────

def load_es(outcome: str) -> pd.DataFrame:
    df = pd.read_csv(RES / f"es_coefs_{outcome}.csv")
    # Add reference row (h=-1, coef=0)
    ref_rows = pd.DataFrame([
        {"outcome": outcome, "spec": s, "h": -1, "coef": 0.0, "se": 0.0, "ci_lo": 0.0, "ci_hi": 0.0}
        for s in ["unweighted", "ipw"]
    ])
    return pd.concat([df, ref_rows], ignore_index=True).sort_values("h")


def load_all() -> dict:
    att  = pd.read_csv(RES / "att_aggregate.csv")
    dr   = pd.read_csv(RES / "dr_twfe_att.csv")
    wald = pd.read_csv(RES / "wald_tests_R.csv")
    hd   = {nm: pd.read_csv(RES / f"honestdid_{nm}.csv") for nm in OUTCOMES}
    es   = {nm: load_es(nm) for nm in OUTCOMES}
    return dict(att=att, dr=dr, wald=wald, hd=hd, es=es)


# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_coef(coef, se, scale=1, digits=3) -> str:
    """Return 'X.XXX\\n(X.XXX)' LaTeX cell (coef over SE in parens)."""
    c = coef * scale
    s = se   * scale
    fmt = f"{{:.{digits}f}}"
    return fmt.format(c) + r" \\ " + "(" + fmt.format(s) + ")"


def fmt_ci(lo, hi, scale=1, digits=3) -> str:
    fmt = f"{{:.{digits}f}}"
    return f"[{fmt.format(lo*scale)}, {fmt.format(hi*scale)}]"


def stars(pval) -> str:
    if pval < 0.01:  return "^{***}"
    if pval < 0.05:  return "^{**}"
    if pval < 0.10:  return "^{*}"
    return ""


# ── TABLE 2: Main event-study results ─────────────────────────────────────────

def make_table2(data: dict) -> str:
    """
    Panel A: Event-study coefficients (unweighted, h = -3,-2,0,+1,+2).
    Panel B: Aggregate ATT, pre-trend Wald test, sample counts.
    Outcomes as columns; income first as primary result.
    """
    outcomes  = list(OUTCOMES.keys())
    att_df    = data["att"]
    wald_df   = data["wald"]

    lines = []
    ncols = len(outcomes)
    col_spec = "l" + "r" * ncols

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\caption{Wildfire Impact on Local Economic Outcomes: Event-Study DiD}")
    lines.append(r"\label{tab:main_results}")
    lines.append(r"\begin{tabular}{" + col_spec + "}")
    lines.append(r"\toprule")

    # Column headers
    header = " & " + " & ".join(
        rf"\multicolumn{{1}}{{c}}{{{OUTCOMES[nm]['table_col']}}}" for nm in outcomes
    ) + r" \\"
    lines.append(header)
    sub = " & " + " & ".join(
        rf"\multicolumn{{1}}{{c}}{{{OUTCOMES[nm]['label']}}}" for nm in outcomes
    ) + r" \\"
    lines.append(sub)
    unit_row = " & " + " & ".join(
        rf"\multicolumn{{1}}{{c}}{{({OUTCOMES[nm]['unit']})}}" for nm in outcomes
    ) + r" \\"
    lines.append(unit_row)
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(ncols+1) + r"}{l}{\textit{Panel A: Event-study coefficients (unweighted TWFE)}} \\[2pt]")

    for h in [-3, -2, 0, 1, 2]:
        row_label = H_LABEL.get(h, str(h))
        row_label = row_label.replace(r"\ ", " ").replace(r"\ ", " ")
        cells = []
        for nm in outcomes:
            sc  = OUTCOMES[nm]["scale"]
            sub = data["es"][nm]
            sub = sub[(sub["spec"] == "unweighted") & (sub["h"] == h)]
            if sub.empty:
                cells.append("---")
            else:
                r = sub.iloc[0]
                c  = r["coef"] * sc
                s  = r["se"]   * sc
                dig = 4 if nm == "log_med_income_2020" else 3
                fmt = f"{{:.{dig}f}}"
                # rough p-val from z-test for star display
                z_p = 2 * (1 - min(abs(c/s), 100) / 100) if s > 0 else 1.0
                from scipy import stats as sps
                z_p = 2 * sps.norm.sf(abs(c / max(s, 1e-10)))
                cells.append(rf"${fmt.format(c)}{stars(z_p)}$")
        lines.append(f"$h = {h:+d}$ (ACS {H_TO_ACS[h]}) & " + " & ".join(cells) + r" \\")

    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(ncols+1) + r"}{l}{\textit{Panel B: Aggregate ATT and pre-trend tests}} \\[2pt]")

    # ATT row (unweighted)
    cells = []
    for nm in outcomes:
        sc  = OUTCOMES[nm]["scale"]
        dig = 4 if nm == "log_med_income_2020" else 3
        fmt = f"{{:.{dig}f}}"
        row = att_df[(att_df["outcome"] == nm) & (att_df["spec"] == "unweighted")]
        if row.empty:
            cells.append("---")
        else:
            r = row.iloc[0]
            from scipy import stats as sps
            z_p = 2 * sps.norm.sf(abs(r["att"] / max(r["se"], 1e-10)))
            cells.append(
                rf"${fmt.format(r['att']*sc)}{stars(z_p)}$" + "\n"
                rf"$[{fmt.format(r['ci_lo']*sc)},\, {fmt.format(r['ci_hi']*sc)}]$"
            )
    lines.append(r"ATT (average $h=0,+1,+2$) & " + " & ".join(cells) + r" \\")
    lines.append(r"\quad Unweighted TWFE & & & & \\")

    # ATT row (IPW)
    cells = []
    for nm in outcomes:
        sc  = OUTCOMES[nm]["scale"]
        dig = 4 if nm == "log_med_income_2020" else 3
        fmt = f"{{:.{dig}f}}"
        row = att_df[(att_df["outcome"] == nm) & (att_df["spec"] == "ipw")]
        if row.empty:
            cells.append("---")
        else:
            r = row.iloc[0]
            from scipy import stats as sps
            z_p = 2 * sps.norm.sf(abs(r["att"] / max(r["se"], 1e-10)))
            cells.append(
                rf"${fmt.format(r['att']*sc)}{stars(z_p)}$" + "\n"
                rf"$[{fmt.format(r['ci_lo']*sc)},\, {fmt.format(r['ci_hi']*sc)}]$"
            )
    lines.append(r"ATT (IPW-weighted TWFE) & " + " & ".join(cells) + r" \\[4pt]")

    # Pre-trend Wald p-value
    cells = []
    for nm in outcomes:
        row = wald_df[(wald_df["outcome"] == nm) & (wald_df["spec"] == "unweighted") &
                      (wald_df["test"].str.contains("primary"))]
        if row.empty:
            cells.append("---")
        else:
            p = row.iloc[0]["pval"]
            cells.append(f"${p:.3f}$")
    lines.append(r"Wald $p$-val: $H_0$: $\beta_{-2}=0$ & " + " & ".join(cells) + r" \\")

    lines.append(r"\midrule")
    lines.append(r"Tract FE & \multicolumn{" + str(ncols) + r"}{c}{Yes} \\")
    lines.append(r"Year FE  & \multicolumn{" + str(ncols) + r"}{c}{Yes} \\")
    lines.append(r"Cluster SE & \multicolumn{" + str(ncols) + r"}{c}{County} \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{tablenotes}")
    lines.append(r"\small")
    lines.append(r"\item \textit{Notes:} Single clean cohort (fires 2015--2017) event-study TWFE.")
    lines.append(r"Sample: lower-48 US census tracts, ACS 5-year estimates for")
    lines.append(r"$h \in \{-3,-2,-1,0,+1,+2\}$ corresponding to ACS 2010, 2012, 2014 (reference),")
    lines.append(r"2022, 2023, 2024. Treated = any MTBS fire $\geq 1{,}000$ acres in 2015--2017.")
    lines.append(r"Control = never-treated tracts (no fires 2013--2023, outside 100\,km smoke buffer).")
    lines.append(r"Unweighted: $N \approx 69{,}700$ tracts $\times$ 6 periods.")
    lines.append(r"IPW-weighted: WFP-2012-restricted common-support sample.")
    lines.append(r"Income scaled to percentage points (log unit $\approx$\% for small changes).")
    lines.append(r"$h=-3$ uses 2000-vintage tract boundaries (auxiliary pre-trend check).")
    lines.append(r"*** $p<0.01$, ** $p<0.05$, * $p<0.10$ (clustered by county).")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


# ── TABLE 3: Robustness ───────────────────────────────────────────────────────

def make_table3(data: dict) -> str:
    """
    Robustness: unweighted / IPW / DR-TWFE ATTs + HonestDiD CI at M=0, M=0.5, breakdown M.
    Rows = primary outcomes; columns = specifications.
    """
    att_df = data["att"]
    dr_df  = data["dr"]

    # Primary outcomes only (income + migration as clearest results)
    outcomes_rob = ["log_med_income_2020", "poverty_rate", "in_migration_rate", "employment_rate"]

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\caption{Robustness: Alternative Specifications and Sensitivity Analysis}")
    lines.append(r"\label{tab:robustness}")
    lines.append(r"\begin{tabular}{lrrrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Outcome & Unweighted & IPW-wtd. & DR-TWFE & HonestDiD & HonestDiD & Breakdown \\")
    lines.append(r"        & ATT        & ATT      & ATT     & CI (M=0)   & CI (M=0.5) & $\bar{M}$ \\")
    lines.append(r"\midrule")

    for nm in outcomes_rob:
        sc  = OUTCOMES[nm]["scale"]
        dig = 4 if nm == "log_med_income_2020" else 3
        fmt = f"{{:.{dig}f}}"

        uw_row = att_df[(att_df["outcome"] == nm) & (att_df["spec"] == "unweighted")]
        ip_row = att_df[(att_df["outcome"] == nm) & (att_df["spec"] == "ipw")]
        dr_row = dr_df[dr_df["outcome"] == nm]
        hd     = data["hd"].get(nm, pd.DataFrame())

        uw_val = f"${fmt.format(uw_row['att'].values[0]*sc)}$" if not uw_row.empty else "---"
        ip_val = f"${fmt.format(ip_row['att'].values[0]*sc)}$" if not ip_row.empty else "---"
        dr_val = f"${fmt.format(dr_row['att'].values[0]*sc)}$" if not dr_row.empty else "---"

        if not hd.empty and "lb" in hd.columns:
            m0  = hd[hd["Mbar"] == 0.0]
            m05 = hd[hd["Mbar"] == 0.5]
            ci0  = f"$[{fmt.format(m0['lb'].values[0]*sc)},\\, {fmt.format(m0['ub'].values[0]*sc)}]$"  if not m0.empty  else "---"
            ci05 = f"$[{fmt.format(m05['lb'].values[0]*sc)},\\, {fmt.format(m05['ub'].values[0]*sc)}]$" if not m05.empty else "---"
            # Breakdown M = smallest M where 0 is in CI
            zero_in = hd[(hd["lb"] <= 0) & (hd["ub"] >= 0)]
            bm = f"${zero_in['Mbar'].min():.1f}$" if not zero_in.empty else "$> 2.0$"
        else:
            ci0 = ci05 = bm = "---"

        label = OUTCOMES[nm]["label"]
        lines.append(f"{label} & {uw_val} & {ip_val} & {dr_val} & {ci0} & {ci05} & {bm} \\\\")

    lines.append(r"\midrule")
    lines.append(r"\multicolumn{7}{l}{\textit{Specification details:}} \\")
    lines.append(r"Unweighted & \multicolumn{6}{l}{All never-treated tracts as controls; no reweighting} \\")
    lines.append(r"IPW-wtd.   & \multicolumn{6}{l}{WFP-2012 propensity-score reweighted, common-support sample} \\")
    lines.append(r"DR-TWFE    & \multicolumn{6}{l}{Baseline covariates $\times$ year interactions (pov.\ rate, log income, WFP, emp.\ rate)} \\")
    lines.append(r"HonestDiD  & \multicolumn{6}{l}{Rambachan--Roth (2023) $\Delta_{\rm RM}$ sensitivity; $M$ = max.\ pre-trend violation / max.\ $|\hat\beta_{h<0}|$} \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{tablenotes}")
    lines.append(r"\small")
    lines.append(r"\item \textit{Notes:} ATT = simple average of $\hat\beta_0 + \hat\beta_{+1} + \hat\beta_{+2}$.")
    lines.append(r"HonestDiD CIs are ``honest'' confidence intervals that remain valid under")
    lines.append(r"violations of parallel trends of magnitude $\leq M$.")
    lines.append(r"Breakdown $\bar{M}$: smallest $M$ at which the honest CI contains zero.")
    lines.append(r"Income units: log points (approximately percent); all other outcomes: percentage points.")
    lines.append(r"IPW income and in-migration ATTs reverse sign vs.\ unweighted; see text for discussion.")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


# ── FIGURE helper: event-study plot ──────────────────────────────────────────

def plot_event_study(
    outcome: str,
    label: str,
    scale: float,
    unit: str,
    es_df: pd.DataFrame,
    out_stem: str,
    h_range: list = None,
    show_ipw: bool = True,
) -> None:
    if h_range is None:
        h_range = [-3, -2, -1, 0, 1, 2]

    uw  = es_df[(es_df["spec"] == "unweighted") & es_df["h"].isin(h_range)].sort_values("h")
    ipw = es_df[(es_df["spec"] == "ipw")        & es_df["h"].isin(h_range)].sort_values("h")

    for df_s in [uw, ipw]:
        for col in ["coef", "ci_lo", "ci_hi"]:
            df_s[col] = df_s[col] * scale

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)

    # Pre-treatment shading
    ax.axvspan(min(h_range) - 0.5, -0.5, color="grey", alpha=0.10, zorder=0)
    ax.axhline(0, linewidth=0.5, color="grey", zorder=1)
    ax.axvline(-0.5, linewidth=0.5, linestyle="--", color="grey", zorder=1)

    if show_ipw and not ipw.empty:
        ax.fill_between(ipw["h"], ipw["ci_lo"], ipw["ci_hi"],
                        color=ORANGE, alpha=0.12, zorder=2)
        ax.plot(ipw["h"], ipw["coef"], color=ORANGE, linewidth=0.9,
                linestyle="--", label="IPW-weighted (robustness)", zorder=3)

    ax.fill_between(uw["h"], uw["ci_lo"], uw["ci_hi"],
                    color=BLUE, alpha=0.18, zorder=4)
    ax.plot(uw["h"], uw["coef"], color=BLUE, linewidth=1.4,
            label="Unweighted TWFE (primary)", zorder=5)
    ax.scatter(uw["h"], uw["coef"], color=BLUE, s=30, zorder=6)

    ax.set_xticks(h_range)
    ax.set_xticklabels([XTICKLABELS[h] for h in h_range], fontsize=8)
    ax.set_xlabel("Relative period ($h$)", fontsize=9)
    ax.set_ylabel(f"{label} ({unit})", fontsize=9)
    ax.set_title(f"Effect of wildfire on {label.lower()}", fontsize=10, fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="upper left")

    # Caption below figure
    caption = (
        "Note: Single-cohort event-study TWFE. $h=-1$ (ACS 2014) is reference period (normalized to 0). "
        "Shaded region: pre-treatment. 95\\% CIs, SE clustered by county."
    )
    ax.text(0.5, -0.22, caption, transform=ax.transAxes,
            ha="center", fontsize=7, color="dimgrey",
            wrap=True)

    fig.tight_layout(rect=[0, 0.04, 1, 1])

    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{out_stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out_stem}.png/.pdf")


# ── FIGURE helper: HonestDiD sensitivity ─────────────────────────────────────

def plot_honestdid(
    hd_df: pd.DataFrame,
    outcome_label: str,
    scale: float,
    unit: str,
    out_stem: str,
) -> None:
    if hd_df.empty or "lb" not in hd_df.columns:
        print(f"  [SKIP] {out_stem}: no HonestDiD data")
        return

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)

    ax.fill_between(hd_df["Mbar"], hd_df["lb"] * scale, hd_df["ub"] * scale,
                    color=BLUE, alpha=0.20, zorder=2)
    ax.plot(hd_df["Mbar"], hd_df["lb"] * scale, color=BLUE, linewidth=1.2, zorder=3)
    ax.plot(hd_df["Mbar"], hd_df["ub"] * scale, color=BLUE, linewidth=1.2, zorder=3)
    ax.axhline(0, linewidth=0.5, color=GREY, zorder=1)

    # Mark breakdown M
    zero_in = hd_df[(hd_df["lb"] <= 0) & (hd_df["ub"] >= 0)]
    if not zero_in.empty:
        bm = zero_in["Mbar"].min()
        ax.axvline(bm, linewidth=0.8, linestyle=":", color=ORANGE, zorder=4)
        ax.text(bm + 0.02, ax.get_ylim()[1] * 0.9,
                f"Breakdown $\\bar{{M}}={bm:.1f}$",
                color=ORANGE, fontsize=8, ha="left")

    ax.set_xlabel(r"$M$ (max.\ trend violation / max.\ $|\hat\beta_{h<0}|$)", fontsize=9)
    ax.set_ylabel(f"{outcome_label} ({unit})", fontsize=9)
    ax.set_title(f"Rambachan--Roth sensitivity: {outcome_label.lower()}", fontsize=10, fontweight="bold")

    caption = (
        "Honest CI ($\\Delta_{\\rm RM}$, relative magnitudes). $M=0$ recovers standard parallel-trends CI. "
        "Shaded band valid under trend violations $\\leq M$. ATT = average $h=0,+1,+2$."
    )
    ax.text(0.5, -0.20, caption, transform=ax.transAxes,
            ha="center", fontsize=7, color="dimgrey")

    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    fig.tight_layout(rect=[0, 0.04, 1, 1])

    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{out_stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out_stem}.png/.pdf")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("PUBLICATION OUTPUT: Tables and Figures")
    print("=" * 70)

    data = load_all()

    # ── Tables ────────────────────────────────────────────────────────────────
    print("\nGenerating LaTeX tables ...")

    tex2 = make_table2(data)
    (TABS / "table2_main_results.tex").write_text(tex2, encoding="utf-8")
    print("  [OK] results/tables/table2_main_results.tex")

    tex3 = make_table3(data)
    (TABS / "table3_robustness.tex").write_text(tex3, encoding="utf-8")
    print("  [OK] results/tables/table3_robustness.tex")

    # ── Event-study figures ───────────────────────────────────────────────────
    print("\nGenerating event-study figures ...")

    # Fig 1: Log income (primary outcome)
    plot_event_study(
        "log_med_income_2020", "Log median HH income", 1, "log pts",
        data["es"]["log_med_income_2020"], "fig1_es_income",
    )

    # Fig 2: Poverty rate
    plot_event_study(
        "poverty_rate", "Poverty rate", 100, "pp",
        data["es"]["poverty_rate"], "fig2_es_poverty",
    )

    # Fig 3: In-migration
    plot_event_study(
        "in_migration_rate", "In-migration rate", 100, "pp",
        data["es"]["in_migration_rate"], "fig3_es_migration",
    )

    # Fig 4: Employment (robustness check)
    plot_event_study(
        "employment_rate", "Employment rate", 100, "pp",
        data["es"]["employment_rate"], "fig4_es_employment",
    )

    # Fig 5: Drop h=-3 sensitivity (income)
    es_no3 = pd.read_csv(RES / "es_coefs_log_med_income_2020_no_h3.csv")
    ref_row = pd.DataFrame([
        {"outcome": "log_med_income_2020", "spec": s, "h": -1,
         "coef": 0.0, "se": 0.0, "ci_lo": 0.0, "ci_hi": 0.0}
        for s in ["unweighted", "ipw"]
    ])
    es_no3 = pd.concat([es_no3, ref_row], ignore_index=True).sort_values("h")
    plot_event_study(
        "log_med_income_2020", "Log median HH income", 1, "log pts",
        es_no3, "fig5_es_income_no_h3",
        h_range=[-2, -1, 0, 1, 2],
        show_ipw=False,
    )

    # ── HonestDiD figures ─────────────────────────────────────────────────────
    print("\nGenerating HonestDiD sensitivity figures ...")

    # Fig 6: HonestDiD — income (primary)
    plot_honestdid(
        data["hd"]["log_med_income_2020"],
        "Log median HH income", 1, "log pts",
        "fig6_honestdid_income",
    )

    # Fig 7: HonestDiD — in-migration (most robust)
    plot_honestdid(
        data["hd"]["in_migration_rate"],
        "In-migration rate", 100, "pp",
        "fig7_honestdid_migration",
    )

    # ── Console summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY: Key estimates for paper (unweighted TWFE)")
    print("=" * 70)
    att_df = data["att"]
    for nm, info in OUTCOMES.items():
        sc = info["scale"]
        row = att_df[(att_df["outcome"] == nm) & (att_df["spec"] == "unweighted")]
        if row.empty:
            continue
        r = row.iloc[0]
        hd  = data["hd"].get(nm, pd.DataFrame())
        bm  = "n/a"
        if not hd.empty and "lb" in hd.columns:
            zi = hd[(hd["lb"] <= 0) & (hd["ub"] >= 0)]
            bm = f"{zi['Mbar'].min():.1f}" if not zi.empty else "> 2.0"
        print(f"\n  {info['label']} ({info['unit']}):")
        print(f"    ATT = {r['att']*sc:+.4f}  [{r['ci_lo']*sc:+.4f}, {r['ci_hi']*sc:+.4f}]")
        print(f"    HonestDiD breakdown M = {bm}")

    print("\n[OK] All outputs saved:")
    print("     results/tables/table2_main_results.tex")
    print("     results/tables/table3_robustness.tex")
    print("     results/figures/fig1–fig7 (.png + .pdf)")


if __name__ == "__main__":
    main()
