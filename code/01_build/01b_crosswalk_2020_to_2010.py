"""
Re-aggregate ACS post-treatment data (2020-vintage boundaries) to 2010-vintage
tract boundaries using the NHGIS 2010-block -> 2020-tract crosswalk.

Resolves the HIGH-severity boundary harmonization problem documented in
docs/boundary_harmonization_diagnostic.md: 290 treated tracts (26.6%) are
absent from ACS 2022/2023/2024 nominal series because Census split them
at the 2010->2020 boundary revision.

Method:
  1. Aggregate block-level crosswalk (parea column) to (tr2020gj, tr2010gj)
     area-weighted pairs; normalize to allocation weights summing to 1.0
     per 2020 tract.
  2. Load pre-treatment rows DIRECTLY from raw nominal TS (not the existing
     balanced panel) so that the 290 missing treated tracts -- which are
     present in the 2010/2012/2014 nominal TS but absent from the balanced
     panel -- have pre-treatment rows to match against after crosswalk.
  3. Load 2020-vintage ACS rows for post-treatment periods; apply crosswalk
     to re-aggregate counts to 2010 GISJOIN definitions.
  4. Combine pre + post (both on 2010 GISJOINs); apply balanced-panel filter.

Limitation: median household income cannot be reconstructed from count
aggregation. We use population-weighted average of 2020-tract medians as
an approximation. Flag as a limitation; validate against the nominal panel
in robustness checks.

Inputs:
  data/raw/nhgis_blk2010_tr2020/          NHGIS block->tract crosswalk (CSV)
  data/raw/acs_extracts/nhgis_inc_pov_emp/nhgis0012_ts_nominal_tract.csv
  data/raw/acs_extracts/nhgis_mig/        B07003 files (all 6 periods)
  data/raw/CPIAUCSL.csv

Output:
  data/processed/acs_tract_panel_xwalk.parquet
"""

import sys
import io
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

XWALK_DIR = RAW / "nhgis_blk2010_tr2020"
TS_FILE = RAW / "acs_extracts" / "nhgis_inc_pov_emp" / "nhgis0012_ts_nominal_tract.csv"
MIG_DIR = RAW / "acs_extracts" / "nhgis_mig"
CPI_FILE = RAW / "CPIAUCSL.csv"

PRE_PERIODS: dict[str, tuple[int, int, int]] = {
    "2006-2010": (2010, -3, 2010),
    "2008-2012": (2012, -2, 2012),
    "2010-2014": (2014, -1, 2014),
}

POST_PERIODS: dict[str, tuple[int, int, int]] = {
    "2018-2022": (2022,  0, 2022),
    "2019-2023": (2023, +1, 2023),
    "2020-2024": (2024, +2, 2024),
}

ALL_PERIODS = {**PRE_PERIODS, **POST_PERIODS}

MIG_PREFIX: dict[str, str] = {
    "2006-2010": "JXZ",
    "2008-2012": "Q4P",
    "2010-2014": "ABND",
    "2018-2022": "AQ0Z",
    "2019-2023": "AS1T",
    "2020-2024": "AU24",
}

MIG_FILES: dict[str, str] = {
    "nhgis0013_ds177_20105_tract.csv": "2006-2010",
    "nhgis0013_ds192_20125_tract.csv": "2008-2012",
    "nhgis0013_ds207_20145_tract.csv": "2010-2014",
    "nhgis0013_ds263_20225_tract.csv": "2018-2022",
    "nhgis0013_ds268_20235_tract.csv": "2019-2023",
    "nhgis0013_ds273_20245_tract.csv": "2020-2024",
}

CPI_BASE = 258.9  # CPI-U 2020 annual average

LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56",
}


def load_cpi_factors() -> dict[int, float]:
    cpi = pd.read_csv(CPI_FILE, parse_dates=["observation_date"])
    cpi["year"] = cpi["observation_date"].dt.year
    annual = cpi.groupby("year")["CPIAUCSL"].mean()
    return {yr: CPI_BASE / annual[yr] for yr in [2010, 2012, 2014, 2022, 2023, 2024]}


def build_tract_crosswalk() -> pd.DataFrame:
    """
    Aggregate block-level crosswalk to (tr2020gj, tr2010gj) area weights.

    weight sums to 1.0 per tr2020gj. For non-split tracts (tr2020gj == tr2010gj
    after aggregation), weight = 1.0. For 2020 tracts that straddle a 2010
    boundary, weight < 1.0, allocated proportionally by parea.
    """
    csv_files = sorted(XWALK_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV found in {XWALK_DIR}")

    print(f"Loading crosswalk: {csv_files[0].name}")
    xwalk = pd.read_csv(
        csv_files[0],
        usecols=["blk2010gj", "tr2020gj", "parea"],
        dtype={"blk2010gj": str, "tr2020gj": str, "parea": float},
    )
    print(f"  Block-level rows: {len(xwalk):,}")

    # 2010 tract GISJOIN = first 14 chars of 18-char block GISJOIN
    # Block: G + state(2) + 0 + county(3) + 0 + tract(6) + block(4) = 18 chars
    # Tract: G + state(2) + 0 + county(3) + 0 + tract(6)            = 14 chars
    xwalk["tr2010gj"] = xwalk["blk2010gj"].str[:14]

    # Lower-48 filter: state FIPS in chars [1:3] of GISJOIN
    xwalk = xwalk[xwalk["tr2010gj"].str[1:3].isin(LOWER_48_FIPS)].copy()
    print(f"  Lower-48 rows: {len(xwalk):,}")

    # Sum parea per (2020 tract, 2010 parent tract)
    tract_xwalk = (
        xwalk.groupby(["tr2020gj", "tr2010gj"])["parea"]
        .sum()
        .reset_index()
        .rename(columns={"parea": "area_contrib"})
    )

    # Normalize: weight = fraction of 2020 tract's area from each 2010 parent
    total = tract_xwalk.groupby("tr2020gj")["area_contrib"].transform("sum")
    tract_xwalk["weight"] = tract_xwalk["area_contrib"] / total.replace(0, np.nan)
    tract_xwalk = tract_xwalk.dropna(subset=["weight"])

    bad = (tract_xwalk.groupby("tr2020gj")["weight"].sum() - 1.0).abs() > 0.01
    if bad.any():
        print(f"  [WARNING] {bad.sum()} 2020 tracts with weights not summing to 1.0")

    n_2020 = tract_xwalk["tr2020gj"].nunique()
    n_split = (tract_xwalk.groupby("tr2020gj")["tr2010gj"].nunique() > 1).sum()
    print(f"  Unique 2020 tracts: {n_2020:,}")
    print(f"  2020 tracts straddling >1 parent 2010 tract: {n_split:,}")

    return tract_xwalk[["tr2020gj", "tr2010gj", "weight"]]


def _gisjoin_to_fips11(gj: pd.Series) -> pd.Series:
    """Derive 11-digit FIPS from NHGIS GISJOIN (G+st2+0+co3+0+tr6 = 14 chars)."""
    return gj.str[1:3] + gj.str[4:7] + gj.str[8:14]


def load_ts_periods(
    periods: dict[str, tuple[int, int, int]],
    cpi_factors: dict[int, float],
    label: str,
) -> pd.DataFrame:
    """
    Load rows for the specified YEAR strings from the raw nominal TS file.
    Computes count-level variables; rates NOT computed here (computed after
    crosswalk for post-treatment, computed directly for pre-treatment).
    """
    print(f"\nLoading {label} periods from raw TS ...")
    df = pd.read_csv(TS_FILE, low_memory=False)
    df = df[df["YEAR"].isin(periods)].copy()
    df = df[df["STATEFP"].astype(str).str.zfill(2).isin(LOWER_48_FIPS)].copy()

    df["acs_year"] = df["YEAR"].map({k: v[0] for k, v in periods.items()})
    df["h"] = df["YEAR"].map({k: v[1] for k, v in periods.items()})
    df["cpi_deflator"] = df["acs_year"].map(cpi_factors)

    keep = [
        "NHGISCODE", "YEAR", "acs_year", "h",
        "STATEFP", "COUNTYFP", "TRACTA",
        "AV0AA",             # population
        "AX7AA", "AX7AB",   # poverty count, non-poverty count
        "AX7AAM",            # poverty count MOE
        "B84AC", "B84AD",   # civilian labor force, employed
        "B79AA",             # median HH income (nominal)
        "cpi_deflator",
    ]
    df = df[[c for c in keep if c in df.columns]].copy()
    n = len(df) // max(df["acs_year"].nunique(), 1)
    print(f"  Rows: {len(df):,} ({df['acs_year'].nunique()} periods x ~{n:,} tracts)")
    return df


def load_migration_periods(periods: dict[str, tuple[int, int, int]], label: str) -> pd.DataFrame:
    """Load B07003 migration counts for the specified periods."""
    print(f"\nLoading {label} migration files ...")
    frames = []
    for fname, year_str in MIG_FILES.items():
        if year_str not in periods:
            continue
        fpath = MIG_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Migration file not found: {fpath}")
        pfx = MIG_PREFIX[year_str]
        total_col = f"{pfx}E001"
        stayer_col = f"{pfx}E004"
        df = pd.read_csv(fpath, low_memory=False)
        if total_col not in df.columns:
            raise KeyError(f"{fname}: expected column {total_col}. Check MIG_PREFIX.")
        df["YEAR"] = year_str
        df["acs_year"] = periods[year_str][0]
        df["mig_total"] = df[total_col]
        df["mig_stayer"] = df[stayer_col]
        frames.append(df[["GISJOIN", "acs_year", "mig_total", "mig_stayer"]])
        print(f"  {year_str}: {len(df):,} tracts")
    return pd.concat(frames, ignore_index=True)


def compute_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rates and derived outcomes from count columns in-place."""
    pov_denom = df["AX7AA"] + df["AX7AB"]
    df["poverty_count"] = df["AX7AA"]
    df["poverty_denom"] = pov_denom
    df["poverty_rate"] = df["AX7AA"] / pov_denom.replace(0, np.nan)

    df["poverty_moe_flag"] = (
        (df["AX7AAM"] > 0.30 * df["AX7AA"].clip(lower=1)) | df["AX7AAM"].isna()
    )

    df["employment_rate"] = df["B84AD"] / df["B84AC"].replace(0, np.nan)
    df["B84AC"] = df["B84AC"]
    df["B84AD"] = df["B84AD"]

    df["med_income_2020"] = df["B79AA"] * df["cpi_deflator"]
    df["log_med_income_2020"] = np.log(df["med_income_2020"].replace(0, np.nan))

    if "mig_total" in df.columns:
        df["in_migration_rate"] = (
            (df["mig_total"] - df["mig_stayer"])
            / df["mig_total"].replace(0, np.nan)
        )

    return df


def build_pre_treatment(cpi_factors: dict[int, float]) -> pd.DataFrame:
    """
    Load pre-treatment rows directly from raw nominal TS.

    Loading from raw (not from acs_tract_panel.parquet) is essential: the
    existing balanced panel excluded the 290 missing treated tracts because
    they had no post-treatment nominal rows. Those tracts DO have pre-treatment
    rows in the raw TS, which the crosswalk will recover on the post-treatment
    side. Without loading raw here, those 290 tracts would still be dropped.
    """
    ts = load_ts_periods(PRE_PERIODS, cpi_factors, "pre-treatment")
    mig = load_migration_periods(PRE_PERIODS, "pre-treatment")

    # Merge migration (GISJOIN = NHGISCODE for pre-treatment periods)
    ts = ts.merge(
        mig.rename(columns={"GISJOIN": "NHGISCODE"}),
        on=["NHGISCODE", "acs_year"],
        how="left",
    )

    ts = compute_outcomes(ts)

    # Derive FIPS11 and string STATEFP/COUNTYFP from GISJOIN
    ts["FIPS11"] = _gisjoin_to_fips11(ts["NHGISCODE"])
    ts["STATEFP"] = ts["NHGISCODE"].str[1:3]
    ts["COUNTYFP"] = ts["NHGISCODE"].str[4:7]
    ts["GISJOIN"] = ts["NHGISCODE"]

    ts["population"] = ts["AV0AA"]
    ts = ts[ts["AV0AA"] >= 500].copy()
    print(f"  Pre-treatment rows after population filter: {len(ts):,} "
          f"({ts['NHGISCODE'].nunique():,} unique tracts)")
    return ts


def apply_crosswalk(
    post_ts: pd.DataFrame,
    post_mig: pd.DataFrame,
    tract_xwalk: pd.DataFrame,
    cpi_factors: dict[int, float],
) -> pd.DataFrame:
    """
    Re-aggregate 2020-vintage counts to 2010 GISJOIN definitions.

    For each (2020 tract j -> 2010 parent i) with area weight w:
        count_2010[i, t] += count_2020[j, t] * w
    Rates are recomputed from aggregated counts.
    """
    print("\nApplying crosswalk to post-treatment data ...")

    # Rename for join
    post = post_ts.rename(columns={"NHGISCODE": "tr2020gj"})

    # Merge migration
    post = post.merge(
        post_mig.rename(columns={"GISJOIN": "tr2020gj"}),
        on=["tr2020gj", "acs_year"],
        how="left",
    )

    # Join crosswalk — expands split-tract rows
    pre_n = post["tr2020gj"].nunique()
    post = post.merge(tract_xwalk, on="tr2020gj", how="left")
    n_unmapped = post["tr2010gj"].isna().sum()
    if n_unmapped > 0:
        n_tracts = post.loc[post["tr2010gj"].isna(), "tr2020gj"].nunique()
        print(f"  [WARNING] {n_tracts} 2020 tracts ({n_unmapped:,} rows) not in "
              f"crosswalk -- dropped (check lower-48 filter and crosswalk coverage)")
    post = post.dropna(subset=["tr2010gj"])
    print(f"  Crosswalk match: {post['tr2020gj'].nunique():,} / {pre_n:,} 2020 tracts")

    # Weighted count allocation
    count_cols = {
        "AV0AA":     "pop_alloc",
        "AX7AA":     "pov_count_alloc",
        "AX7AB":     "pov_nopov_alloc",
        "B84AC":     "lf_alloc",
        "B84AD":     "emp_alloc",
        "mig_total":   "mig_total_alloc",
        "mig_stayer":  "mig_stayer_alloc",
    }
    for src, dst in count_cols.items():
        if src in post.columns:
            post[dst] = post[src] * post["weight"]

    # Population-weighted income numerator
    if "B79AA" in post.columns:
        post["inc_x_pop"] = post["B79AA"] * post["AV0AA"] * post["weight"]

    # Aggregate to (2010 GISJOIN, period)
    alloc_cols = [v for v in count_cols.values() if v in post.columns]
    if "inc_x_pop" in post.columns:
        alloc_cols.append("inc_x_pop")

    grp = (
        post.groupby(["tr2010gj", "YEAR", "acs_year", "h"])[alloc_cols]
        .sum()
        .reset_index()
    )

    # Recompute outcomes from aggregated counts
    pov_denom = grp["pov_count_alloc"] + grp["pov_nopov_alloc"]
    grp["poverty_count"] = grp["pov_count_alloc"]
    grp["poverty_denom"] = pov_denom
    grp["poverty_rate"] = grp["pov_count_alloc"] / pov_denom.replace(0, np.nan)
    grp["poverty_moe_flag"] = np.nan  # MOE not re-aggregatable

    grp["B84AC"] = grp["lf_alloc"]
    grp["B84AD"] = grp["emp_alloc"]
    grp["employment_rate"] = grp["emp_alloc"] / grp["lf_alloc"].replace(0, np.nan)

    if "mig_total_alloc" in grp.columns:
        grp["mig_total"] = grp["mig_total_alloc"]
        grp["mig_stayer"] = grp["mig_stayer_alloc"]
        grp["in_migration_rate"] = (
            (grp["mig_total_alloc"] - grp["mig_stayer_alloc"])
            / grp["mig_total_alloc"].replace(0, np.nan)
        )

    # Population-weighted average income -> deflate to 2020$
    if "inc_x_pop" in grp.columns:
        grp["med_income_2020"] = (
            grp["inc_x_pop"] / grp["pop_alloc"].replace(0, np.nan)
            * grp["acs_year"].map(cpi_factors)
        )
        grp["log_med_income_2020"] = np.log(grp["med_income_2020"].replace(0, np.nan))

    grp["population"] = grp["pop_alloc"]

    # Identifiers (all on 2010 boundaries now)
    grp = grp.rename(columns={"tr2010gj": "NHGISCODE"})
    grp["GISJOIN"] = grp["NHGISCODE"]
    grp["FIPS11"] = _gisjoin_to_fips11(grp["NHGISCODE"])
    grp["STATEFP"] = grp["NHGISCODE"].str[1:3]
    grp["COUNTYFP"] = grp["NHGISCODE"].str[4:7]

    n_before = grp["NHGISCODE"].nunique()
    grp = grp[grp["population"] >= 500].copy()
    n_after = grp["NHGISCODE"].nunique()
    print(f"  Population filter (>=500): {n_before:,} -> {n_after:,} 2010-vintage tracts")
    return grp


SHARED_COLS = [
    "NHGISCODE", "GISJOIN", "FIPS11", "YEAR", "acs_year", "h",
    "STATEFP", "COUNTYFP",
    "population", "poverty_rate", "poverty_count", "poverty_denom",
    "poverty_moe_flag",
    "employment_rate", "med_income_2020", "log_med_income_2020",
    "B84AC", "B84AD",
    "in_migration_rate", "mig_total", "mig_stayer",
]


def build_panel(pre: pd.DataFrame, post: pd.DataFrame) -> pd.DataFrame:
    pre_out = pre[[c for c in SHARED_COLS if c in pre.columns]].copy()
    post_out = post[[c for c in SHARED_COLS if c in post.columns]].copy()

    # Ensure consistent dtypes before concat (both string)
    for col in ["STATEFP", "COUNTYFP", "FIPS11"]:
        for df in [pre_out, post_out]:
            if col in df.columns:
                df[col] = df[col].astype(str)

    panel = pd.concat([pre_out, post_out], ignore_index=True)

    # Balanced panel: tracts with all 6 periods
    period_counts = panel.groupby("NHGISCODE")["acs_year"].count()
    balanced_ids = period_counts[period_counts == 6].index
    n_before = panel["NHGISCODE"].nunique()
    panel = panel[panel["NHGISCODE"].isin(balanced_ids)].copy()
    n_after = panel["NHGISCODE"].nunique()
    print(f"\nBalanced panel (all 6 periods): {n_before:,} -> {n_after:,} tracts "
          f"({n_before - n_after:,} dropped)")

    return panel.sort_values(["NHGISCODE", "acs_year"]).reset_index(drop=True)


def retention_diagnostic(panel: pd.DataFrame) -> None:
    fire_path = PROCESSED / "fire_treatment_tracts.parquet"
    if not fire_path.exists():
        print("\n[SKIP] fire_treatment_tracts.parquet not found -- "
              "run 02_fire_treatment.py first, then re-check retention.")
        return

    fire = pd.read_parquet(fire_path, columns=["GISJOIN", "treated", "never_treated"])
    treated = set(fire[fire["treated"] == 1]["GISJOIN"])
    controls = set(fire[fire["never_treated"] == 1]["GISJOIN"])
    panel_ids = set(panel["NHGISCODE"].unique())

    t_pct = 100 * len(treated & panel_ids) / len(treated) if treated else 0
    c_pct = 100 * len(controls & panel_ids) / len(controls) if controls else 0

    print(f"\n--- Treated Tract Retention (crosswalk panel) ---")
    print(f"  Treated tracts total:         {len(treated):,}")
    print(f"  In crosswalk panel:           {len(treated & panel_ids):,}")
    print(f"  Retention rate:               {t_pct:.1f}%")
    print(f"  Adequacy:                     {'[OK] >=95%' if t_pct >= 95 else '[WARNING] <95%'}")
    print(f"\n  Never-treated controls:       {len(controls):,}")
    print(f"  In crosswalk panel:           {len(controls & panel_ids):,}")
    print(f"  Control retention rate:       {c_pct:.1f}%")


def main() -> None:
    print("=" * 70)
    print("ACS CROSSWALK: 2020-vintage -> 2010-vintage tract boundaries")
    print("=" * 70)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    cpi_factors = load_cpi_factors()

    tract_xwalk = build_tract_crosswalk()

    # Pre-treatment: load from raw TS (not the balanced parquet)
    pre = build_pre_treatment(cpi_factors)

    # Post-treatment: load raw 2020-vintage rows, apply crosswalk
    post_ts = load_ts_periods(POST_PERIODS, cpi_factors, "post-treatment")
    post_mig = load_migration_periods(POST_PERIODS, "post-treatment")
    post = apply_crosswalk(post_ts, post_mig, tract_xwalk, cpi_factors)

    panel = build_panel(pre, post)

    out_path = PROCESSED / "acs_tract_panel_xwalk.parquet"
    panel.to_parquet(out_path, index=False)

    print(f"\n[OK] Saved: {out_path}")
    print(f"     Shape:   {panel.shape}")
    print(f"     Tracts:  {panel['NHGISCODE'].nunique():,}")
    print(f"     Periods: {sorted(panel['acs_year'].unique())}")

    print("\nOutcome coverage (non-null share):")
    for col in ["poverty_rate", "employment_rate", "log_med_income_2020", "in_migration_rate"]:
        if col in panel.columns:
            pct = panel[col].notna().mean() * 100
            print(f"  {col}: {pct:.1f}%")

    retention_diagnostic(panel)


if __name__ == "__main__":
    main()
