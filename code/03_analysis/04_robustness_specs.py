"""
Robustness: Smoke buffer and fire size threshold variations.

For each (min_acres, buffer_km) specification, re-assigns treatment from raw MTBS
and re-estimates the unweighted TWFE event study on the existing ACS panel.

Specifications (all vary from baseline independently):
  Baseline:  buffer=100km, min_acres=1,000
  Buffer-50: buffer= 50km, min_acres=1,000  (narrower smoke exclusion zone)
  Buffer-150:buffer=150km, min_acres=1,000  (wider smoke exclusion zone)
  Size-500:  buffer=100km, min_acres=  500  (smaller fires included)
  Size-2000: buffer=100km, min_acres=2,000  (only large fires)

Identification threat addressed:
  Smoke buffer: if fires cause spillover smoke effects on control tracts,
    smoke-exposed "never-treated" controls are contaminated. Wider buffers
    exclude more potential controls but reduce contamination risk.
  Fire size: if mechanism varies by fire scale, minimum acreage thresholds
    define different treated populations. ATT stability across thresholds
    signals robustness of the LATE to the fire-size MAUP.

Outputs:
  results/tables/table4_buffer_size_robustness.tex
  results/rob_spec_atts.csv           ATTs per spec × outcome
  results/rob_spec_sample_counts.csv  Treated / control N per spec
"""

import sys
import io
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyfixest as pf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

ROOT      = Path(__file__).resolve().parents[2]
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESULTS   = ROOT / "results"
TABS      = RESULTS / "tables"
TABS.mkdir(parents=True, exist_ok=True)

MTBS_FILE  = RAW / "mtbs_perimeters" / "S_USA.MTBS_BURN_AREA_BOUNDARY.shp"
TRACT_FILE = (
    RAW / "tract_shapefiles"
    / "nhgis0010_shapefile_tl2010_us_tract_2010"
    / "US_tract_2010.shp"
)

TRACT_CRS = "ESRI:102003"
COHORT_YEARS = frozenset({2015, 2016, 2017})
EXCLUSION_YEARS = frozenset(range(2013, 2024))  # 2013-2023 inclusive
LOWER_48 = {
    "01","04","05","06","08","09","10","11","12","13","16","17","18","19","20",
    "21","22","23","24","25","26","27","28","29","30","31","32","33","34","35",
    "36","37","38","39","40","41","42","44","45","46","47","48","49","50","51",
    "53","54","55","56",
}

YEAR_TO_H = {2010: -3, 2012: -2, 2014: -1, 2022: 0, 2023: 1, 2024: 2}
OUTCOMES = {
    "log_med_income_2020": {"scale": 1,   "label": "Log income"},
    "poverty_rate":        {"scale": 100, "label": "Poverty rate"},
    "in_migration_rate":   {"scale": 100, "label": "In-migration"},
    "employment_rate":     {"scale": 100, "label": "Employment"},
}

SPECS = [
    {"name": "Baseline\n(100km, ≥1k ac)",  "label": "Baseline",    "buffer_km": 100, "min_acres": 1_000},
    {"name": "Buffer 50km\n(≥1k ac)",       "label": "Buffer-50km", "buffer_km":  50, "min_acres": 1_000},
    {"name": "Buffer 150km\n(≥1k ac)",      "label": "Buffer-150km","buffer_km": 150, "min_acres": 1_000},
    {"name": "Size ≥500ac\n(100km buf)",    "label": "Size-500ac",  "buffer_km": 100, "min_acres":   500},
    {"name": "Size ≥2,000ac\n(100km buf)", "label": "Size-2000ac", "buffer_km": 100, "min_acres": 2_000},
]


# ── Spatial helpers ───────────────────────────────────────────────────────────

def load_spatial() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load MTBS (all fires, reprojected) and tract shapefiles once."""
    print("Loading MTBS perimeters ...")
    mtbs = gpd.read_file(MTBS_FILE)
    mtbs = mtbs[mtbs["FIRE_TYPE"].isin(["Wildfire", "Wildland Fire Use"])].copy()
    mtbs = mtbs.to_crs(TRACT_CRS)
    mtbs["YEAR"] = mtbs["YEAR"].astype(int)

    print("Loading tract shapefiles ...")
    tracts = gpd.read_file(TRACT_FILE)
    tracts = tracts[tracts["STATEFP10"].isin(LOWER_48)].to_crs(TRACT_CRS).copy()
    print(f"  Tracts: {len(tracts):,}")
    return mtbs, tracts


def assign_treatment(
    mtbs: gpd.GeoDataFrame,
    tracts: gpd.GeoDataFrame,
    min_acres: int,
    buffer_km: int,
) -> pd.DataFrame:
    """
    Assign treated / never_treated using parameterized thresholds.
    Returns tract-level DataFrame with GISJOIN + treated + never_treated + COUNTYFP10.
    """
    fires = mtbs[mtbs["ACRES"] >= min_acres].copy()

    # Spatial join: which tracts intersect which fires?
    joined = gpd.sjoin(
        tracts[["GISJOIN", "COUNTYFP10", "geometry"]],
        fires[["FIRE_ID", "YEAR", "geometry"]],
        how="left",
        predicate="intersects",
    ).drop(columns=["index_right"], errors="ignore")

    # Treated: first large fire in cohort window (2015-2017)
    cohort = joined[joined["YEAR"].isin(COHORT_YEARS)].copy()
    treated_set = set(cohort["GISJOIN"].dropna())

    # First-fire restriction: exclude tracts with any large fire 1984-2014
    pre_cohort = joined[joined["YEAR"].isin(range(1984, 2015))].copy()
    prior_fire_set = set(pre_cohort["GISJOIN"].dropna())
    treated_set = treated_set - prior_fire_set

    # Excluded: any large fire 2013-2023 (contaminated controls)
    any_fire = joined[joined["YEAR"].isin(EXCLUSION_YEARS)].copy()
    any_fire_set = set(any_fire["GISJOIN"].dropna())

    # Smoke buffer: union of buffer_km buffers around cohort fire centroids
    print(f"  Building {buffer_km}km smoke buffer ...")
    cohort_fires = fires[fires["YEAR"].isin(COHORT_YEARS)]
    buf_union = cohort_fires.geometry.buffer(buffer_km * 1_000).union_all()

    # Tract centroids
    tract_idx = tracts.set_index("GISJOIN")
    centroids = tract_idx.centroid

    # Never-treated candidates: not in any_fire_set
    all_gj = set(tracts["GISJOIN"])
    candidates = all_gj - any_fire_set

    # Exclude candidates within smoke buffer
    in_buf = {gj for gj in candidates if gj in centroids.index and centroids[gj].within(buf_union)}
    never_treated_set = candidates - in_buf

    # Build output
    base = tracts[["GISJOIN", "COUNTYFP10"]].copy()
    base["treated"]       = base["GISJOIN"].isin(treated_set).astype(int)
    base["never_treated"] = base["GISJOIN"].isin(never_treated_set).astype(int)
    # treated wins over never_treated
    base.loc[base["treated"] == 1, "never_treated"] = 0
    return base[["GISJOIN", "COUNTYFP10", "treated", "never_treated"]]


# ── DiD estimation helper ─────────────────────────────────────────────────────

def estimate_did(panel: pd.DataFrame, treatment: pd.DataFrame) -> dict:
    """
    Merge panel with new treatment assignment; estimate unweighted TWFE;
    return dict of {outcome: {att, h_coefs}}.
    """
    df = (
        panel
        .merge(treatment.rename(columns={"COUNTYFP10": "COUNTYFP10_fire"}),
               left_on="NHGISCODE", right_on="GISJOIN", how="left")
    )
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()
    df["h"]             = df["acs_year"].map(YEAR_TO_H).astype("Int64")
    df["county_cluster"] = df["COUNTYFP10_fire"].fillna(df["COUNTYFP"])
    df = df.dropna(subset=["h"])

    results = {}
    for outcome in OUTCOMES:
        sub = df.dropna(subset=[outcome])
        if sub.empty:
            continue
        try:
            fit = pf.feols(
                f"{outcome} ~ i(h, treated, ref=-1) | NHGISCODE + acs_year",
                data=sub,
                vcov={"CRV1": "county_cluster"},
            )
            tidy = fit.tidy().reset_index()
            tidy["h"] = tidy["Coefficient"].str.extract(r"::([-\d]+):").astype(int)
            tidy = tidy.rename(columns={"Estimate": "coef", "Std. Error": "se",
                                        "2.5%": "ci_lo", "97.5%": "ci_hi"})
            post = tidy[tidy["h"] >= 0]
            att  = post["coef"].mean()
            att_se = post["se"].max()
            results[outcome] = {
                "att": att,
                "se":  att_se,
                "ci_lo": att - 1.96 * att_se,
                "ci_hi": att + 1.96 * att_se,
                "h_coefs": tidy[["h","coef","se","ci_lo","ci_hi"]].copy(),
            }
        except Exception as e:
            print(f"    [WARN] {outcome}: {e}")
    return results


# ── LaTeX table ───────────────────────────────────────────────────────────────

def make_robustness_table(att_rows: list[dict]) -> str:
    att_df = pd.DataFrame(att_rows)
    spec_labels = [s["label"] for s in SPECS]
    outcomes    = list(OUTCOMES.keys())

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering\small")
    lines.append(r"\caption{Robustness: Smoke Buffer and Fire Size Threshold Variations}")
    lines.append(r"\label{tab:buffer_size_robustness}")
    ncols = len(SPECS)
    col_spec = "l" + "r" * ncols
    lines.append(r"\begin{tabular}{" + col_spec + "}")
    lines.append(r"\toprule")

    # Spec header row
    header_cells = " & ".join(rf"\multicolumn{{1}}{{c}}{{{s['label']}}}" for s in SPECS)
    lines.append(r" & " + header_cells + r" \\")
    sub_cells = " & ".join(
        rf"\multicolumn{{1}}{{c}}{{\scriptsize {s['buffer_km']}km / {s['min_acres']:,}ac}}"
        for s in SPECS
    )
    lines.append(r" & " + sub_cells + r" \\")
    lines.append(r"\midrule")

    from scipy import stats as sps

    for nm, info in OUTCOMES.items():
        sc  = info["scale"]
        dig = 4 if nm == "log_med_income_2020" else 3
        fmt = f"{{:.{dig}f}}"
        cells = []
        for spec in SPECS:
            row = att_df[(att_df["spec"] == spec["label"]) & (att_df["outcome"] == nm)]
            if row.empty:
                cells.append("---")
            else:
                r   = row.iloc[0]
                z_p = 2 * sps.norm.sf(abs(r["att"] / max(r["se"], 1e-10)))
                star = "^{***}" if z_p < 0.01 else ("^{**}" if z_p < 0.05 else ("^{*}" if z_p < 0.10 else ""))
                cells.append(rf"${fmt.format(r['att']*sc)}{star}$")
        lines.append(info["label"] + " & " + " & ".join(cells) + r" \\")
        # SE row
        se_cells = []
        for spec in SPECS:
            row = att_df[(att_df["spec"] == spec["label"]) & (att_df["outcome"] == nm)]
            if row.empty:
                se_cells.append("")
            else:
                se_cells.append(rf"$({fmt.format(row.iloc[0]['se']*sc)})$")
        lines.append(r" & " + " & ".join(se_cells) + r" \\[3pt]")

    # Sample counts
    lines.append(r"\midrule")
    for count_type in ["treated", "never_treated"]:
        label = "Treated tracts" if count_type == "treated" else "Control tracts"
        cells = []
        for spec in SPECS:
            row = att_df[(att_df["spec"] == spec["label"]) & (att_df["outcome"] == "log_med_income_2020")]
            n = int(row[count_type].values[0]) if not row.empty and count_type in row.columns else "---"
            cells.append(rf"${n:,}$" if isinstance(n, int) else "---")
        lines.append(label + " & " + " & ".join(cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\begin{tablenotes}\small")
    lines.append(r"\item \textit{Notes:} Aggregate ATT (average of $\hat\beta_0, \hat\beta_{+1}, \hat\beta_{+2}$)")
    lines.append(r"from unweighted TWFE with tract and year FE. SE (clustered by county) in parentheses.")
    lines.append(r"Baseline: 100km smoke exclusion buffer, fires $\geq 1{,}000$ acres (MTBS standard).")
    lines.append(r"Buffer variants hold fire size threshold at 1,000 acres.")
    lines.append(r"Size variants hold buffer at 100km.")
    lines.append(r"*** $p<0.01$, ** $p<0.05$, * $p<0.10$.")
    lines.append(r"\end{tablenotes}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("ROBUSTNESS: Buffer × Fire Size Threshold Specifications")
    print("=" * 70)

    # Load spatial data once
    mtbs, tracts = load_spatial()

    # Load existing ACS panel (used for all specs)
    print("\nLoading ACS panel ...")
    panel = pd.read_parquet(
        PROCESSED / "acs_tract_panel_xwalk.parquet",
        columns=[
            "NHGISCODE", "acs_year", "COUNTYFP",
            "poverty_rate", "log_med_income_2020",
            "employment_rate", "in_migration_rate",
        ],
    )
    print(f"  Panel: {len(panel):,} rows, {panel['NHGISCODE'].nunique():,} tracts")

    all_att_rows = []

    for spec in SPECS:
        print(f"\n{'─'*60}")
        print(f"Spec: {spec['label']} — buffer={spec['buffer_km']}km, min_acres={spec['min_acres']:,}")
        print(f"{'─'*60}")

        treatment = assign_treatment(
            mtbs, tracts,
            min_acres=spec["min_acres"],
            buffer_km=spec["buffer_km"],
        )
        n_treated = int(treatment["treated"].sum())
        n_ctrl    = int(treatment["never_treated"].sum())
        print(f"  Treated: {n_treated:,}  |  Never-treated: {n_ctrl:,}")

        results = estimate_did(panel, treatment)

        for outcome, res in results.items():
            sc = OUTCOMES[outcome]["scale"]
            print(f"  {outcome:<28} ATT = {res['att']*sc:+.4f} "
                  f"[{res['ci_lo']*sc:+.4f}, {res['ci_hi']*sc:+.4f}]")
            all_att_rows.append({
                "spec":          spec["label"],
                "buffer_km":     spec["buffer_km"],
                "min_acres":     spec["min_acres"],
                "outcome":       outcome,
                "att":           res["att"],
                "se":            res["se"],
                "ci_lo":         res["ci_lo"],
                "ci_hi":         res["ci_hi"],
                "treated":       n_treated,
                "never_treated": n_ctrl,
            })

    att_df = pd.DataFrame(all_att_rows)
    att_df.to_csv(RESULTS / "rob_spec_atts.csv", index=False)
    print(f"\n[OK] Saved: results/rob_spec_atts.csv")

    # LaTeX table
    tex = make_robustness_table(all_att_rows)
    (TABS / "table4_buffer_size_robustness.tex").write_text(tex, encoding="utf-8")
    print("[OK] Saved: results/tables/table4_buffer_size_robustness.tex")

    # Console summary
    print("\n" + "=" * 70)
    print("ATT STABILITY ACROSS SPECS (scaled units)")
    print("=" * 70)
    print(f"  {'Outcome':<28} " + " ".join(f"{s['label']:>12}" for s in SPECS))
    print(f"  {'-'*28} " + " ".join(f"{'-'*12}" for _ in SPECS))
    for nm, info in OUTCOMES.items():
        sc = info["scale"]
        dig = 4 if nm == "log_med_income_2020" else 3
        fmt = f"{{:+{dig+4}.{dig}f}}"
        vals = []
        for spec in SPECS:
            row = att_df[(att_df["spec"] == spec["label"]) & (att_df["outcome"] == nm)]
            vals.append(fmt.format(row["att"].values[0] * sc) if not row.empty else "     ---    ")
        print(f"  {nm:<28} " + " ".join(vals))


if __name__ == "__main__":
    main()
