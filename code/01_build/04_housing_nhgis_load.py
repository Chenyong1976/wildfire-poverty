# -*- coding: utf-8 -*-
"""
Build housing outcomes panel: vacancy rate and owner-occupancy rate.
Source: NHGIS B25002 (occupancy status) and B25003 (tenure), all 6 ACS periods.

Boundary harmonization mirrors 01b_crosswalk_2020_to_2010.py:
  Pre-treatment (2010, 2012, 2014): GISJOIN is 2010-vintage -- load directly.
  Post-treatment (2022, 2023, 2024): GISJOIN is 2020-vintage -- apply area-
    weighted crosswalk (NHGIS block->2020-tract) to re-aggregate counts to
    2010 parent GISJOIN definitions, then recompute rates from allocated counts.

Output variables per (NHGISCODE, acs_year):
  housing_total   B25002 total housing units
  occupied        B25002 occupied units
  vacant          B25002 vacant units
  owner_occ       B25003 owner-occupied units
  renter_occ      B25003 renter-occupied units
  vacancy_rate    vacant / housing_total
  owner_occ_rate  owner_occ / (owner_occ + renter_occ)

Inputs:
  data/raw/Housing/nhgis0014_*.csv          (6 pairs of E files)
  data/raw/nhgis_blk2010_tr2020/*.csv       NHGIS block->tract crosswalk

Output:
  data/processed/housing_tract_panel.parquet
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

HOUSING_DIR = RAW / "Housing"
XWALK_DIR = RAW / "nhgis_blk2010_tr2020"

LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56",
}

# Per-period file name and NHGIS variable code prefixes
# B25002: occupancy status (total, occupied, vacant)
# B25003: tenure (total, owner, renter)
PERIOD_SPECS = [
    {
        "file":     "nhgis0014_ds176_20105_tract_E.csv",
        "year_str": "2006-2010",
        "acs_year": 2010,
        "vintage":  "pre",
        "b25002":   ("JRJE001", "JRJE002", "JRJE003"),
        "b25003":   ("JRKE001", "JRKE002", "JRKE003"),
    },
    {
        "file":     "nhgis0014_ds191_20125_tract_E.csv",
        "year_str": "2008-2012",
        "acs_year": 2012,
        "vintage":  "pre",
        "b25002":   ("QX7E001", "QX7E002", "QX7E003"),
        "b25003":   ("QX8E001", "QX8E002", "QX8E003"),
    },
    {
        "file":     "nhgis0014_ds206_20145_tract_E.csv",
        "year_str": "2010-2014",
        "acs_year": 2014,
        "vintage":  "pre",
        "b25002":   ("ABGWE001", "ABGWE002", "ABGWE003"),
        "b25003":   ("ABGXE001", "ABGXE002", "ABGXE003"),
    },
    {
        "file":     "nhgis0014_ds262_20225_tract_E.csv",
        "year_str": "2018-2022",
        "acs_year": 2022,
        "vintage":  "post",
        "b25002":   ("AQSPE001", "AQSPE002", "AQSPE003"),
        "b25003":   ("AQSQE001", "AQSQE002", "AQSQE003"),
    },
    {
        "file":     "nhgis0014_ds267_20235_tract_E.csv",
        "year_str": "2019-2023",
        "acs_year": 2023,
        "vintage":  "post",
        "b25002":   ("ASS8E001", "ASS8E002", "ASS8E003"),
        "b25003":   ("ASS9E001", "ASS9E002", "ASS9E003"),
    },
    {
        "file":     "nhgis0014_ds272_20245_tract_E.csv",
        "year_str": "2020-2024",
        "acs_year": 2024,
        "vintage":  "post",
        "b25002":   ("AUUDE001", "AUUDE002", "AUUDE003"),
        "b25003":   ("AUUEE001", "AUUEE002", "AUUEE003"),
    },
]


# ── Crosswalk ─────────────────────────────────────────────────────────────────

def build_tract_crosswalk() -> pd.DataFrame:
    """
    Aggregate block-level crosswalk to (tr2020gj, tr2010gj) area weights.
    Weight sums to 1.0 per tr2020gj. Mirrors 01b_crosswalk_2020_to_2010.py.
    """
    csv_files = sorted(XWALK_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV in {XWALK_DIR}")

    print(f"Loading block crosswalk: {csv_files[0].name}")
    xwalk = pd.read_csv(
        csv_files[0],
        usecols=["blk2010gj", "tr2020gj", "parea"],
        dtype={"blk2010gj": str, "tr2020gj": str, "parea": float},
    )
    xwalk["tr2010gj"] = xwalk["blk2010gj"].str[:14]
    xwalk = xwalk[xwalk["tr2010gj"].str[1:3].isin(LOWER_48_FIPS)].copy()

    tract_xwalk = (
        xwalk.groupby(["tr2020gj", "tr2010gj"])["parea"]
        .sum()
        .reset_index()
        .rename(columns={"parea": "area_contrib"})
    )
    total = tract_xwalk.groupby("tr2020gj")["area_contrib"].transform("sum")
    tract_xwalk["weight"] = tract_xwalk["area_contrib"] / total.replace(0, np.nan)
    tract_xwalk = tract_xwalk.dropna(subset=["weight"])
    print(f"  Unique 2020 tracts in crosswalk: {tract_xwalk['tr2020gj'].nunique():,}")
    return tract_xwalk[["tr2020gj", "tr2010gj", "weight"]]


# ── Per-period loader ─────────────────────────────────────────────────────────

def load_period(spec: dict) -> pd.DataFrame:
    """
    Load one ACS period's housing CSV; rename to standard count columns.
    Returns columns: GISJOIN, acs_year, housing_total, occupied, vacant,
                     owner_occ, renter_occ
    """
    fpath = HOUSING_DIR / spec["file"]
    if not fpath.exists():
        raise FileNotFoundError(f"Housing file not found: {fpath}")

    b25002 = spec["b25002"]  # (total, occupied, vacant)
    b25003 = spec["b25003"]  # (total, owner, renter)

    df = pd.read_csv(
        fpath,
        usecols=["GISJOIN", "STUSAB"] + list(b25002) + list(b25003),
        low_memory=False,
    )

    # Lower-48 filter
    state_fp = df["GISJOIN"].str[1:3]
    df = df[state_fp.isin(LOWER_48_FIPS)].copy()

    df = df.rename(columns={
        b25002[0]: "housing_total",
        b25002[1]: "occupied",
        b25002[2]: "vacant",
        b25003[1]: "owner_occ",
        b25003[2]: "renter_occ",
    })
    df["acs_year"] = spec["acs_year"]

    print(f"  {spec['year_str']}: {len(df):,} tracts (lower-48)")
    return df[["GISJOIN", "acs_year", "housing_total", "occupied", "vacant",
               "owner_occ", "renter_occ"]]


def compute_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Compute vacancy_rate and owner_occ_rate from count columns."""
    df["vacancy_rate"] = df["vacant"] / df["housing_total"].replace(0, np.nan)
    occ_total = df["owner_occ"] + df["renter_occ"]
    df["owner_occ_rate"] = df["owner_occ"] / occ_total.replace(0, np.nan)
    return df


# ── Pre-treatment (2010-vintage boundaries, no crosswalk needed) ──────────────

def build_pre(specs: list) -> pd.DataFrame:
    print("\nLoading pre-treatment housing (2010-vintage boundaries) ...")
    frames = []
    for spec in specs:
        df = load_period(spec)
        # GISJOIN is already 2010-vintage; rename to NHGISCODE directly
        df = df.rename(columns={"GISJOIN": "NHGISCODE"})
        frames.append(df)
    pre = pd.concat(frames, ignore_index=True)
    pre = compute_rates(pre)
    return pre


# ── Post-treatment (2020-vintage boundaries, crosswalk required) ──────────────

def build_post(specs: list, tract_xwalk: pd.DataFrame) -> pd.DataFrame:
    print("\nLoading post-treatment housing (2020-vintage -> 2010-vintage crosswalk) ...")
    frames = []
    for spec in specs:
        df = load_period(spec)
        frames.append(df)
    post_raw = pd.concat(frames, ignore_index=True)

    # Join crosswalk on 2020 GISJOIN
    pre_n = post_raw["GISJOIN"].nunique()
    post_xw = post_raw.merge(
        tract_xwalk.rename(columns={"tr2020gj": "GISJOIN"}),
        on="GISJOIN",
        how="left",
    )
    n_unmapped = post_xw["tr2010gj"].isna().sum()
    if n_unmapped > 0:
        n_tracts = post_xw.loc[post_xw["tr2010gj"].isna(), "GISJOIN"].nunique()
        print(f"  [WARNING] {n_tracts} 2020 tracts not in crosswalk -- dropped")
    post_xw = post_xw.dropna(subset=["tr2010gj"])
    print(f"  Crosswalk match: {post_xw['GISJOIN'].nunique():,} / {pre_n:,} 2020 tracts")

    # Area-weighted count allocation
    count_cols = ["housing_total", "occupied", "vacant", "owner_occ", "renter_occ"]
    for col in count_cols:
        post_xw[col] = post_xw[col] * post_xw["weight"]

    # Aggregate to (2010 GISJOIN, acs_year)
    post_agg = (
        post_xw.groupby(["tr2010gj", "acs_year"])[count_cols]
        .sum()
        .reset_index()
        .rename(columns={"tr2010gj": "NHGISCODE"})
    )
    post_agg = compute_rates(post_agg)
    return post_agg


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("HOUSING PANEL: B25002/B25003 -- Vacancy & Owner-Occupancy Rates")
    print("=" * 70)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    pre_specs  = [s for s in PERIOD_SPECS if s["vintage"] == "pre"]
    post_specs = [s for s in PERIOD_SPECS if s["vintage"] == "post"]

    tract_xwalk = build_tract_crosswalk()

    pre  = build_pre(pre_specs)
    post = build_post(post_specs, tract_xwalk)

    panel = pd.concat([pre, post], ignore_index=True)
    panel = panel.sort_values(["NHGISCODE", "acs_year"]).reset_index(drop=True)

    # Balanced-panel filter: keep tracts present in all 6 periods
    period_counts = panel.groupby("NHGISCODE")["acs_year"].count()
    balanced_ids  = period_counts[period_counts == 6].index
    n_before = panel["NHGISCODE"].nunique()
    panel = panel[panel["NHGISCODE"].isin(balanced_ids)].copy()
    n_after = panel["NHGISCODE"].nunique()
    print(f"\nBalanced panel (6 periods): {n_before:,} -> {n_after:,} tracts "
          f"({n_before - n_after:,} dropped)")

    # Verify against existing ACS panel
    acs_panel_path = PROCESSED / "acs_tract_panel_xwalk.parquet"
    if acs_panel_path.exists():
        acs_ids = set(
            pd.read_parquet(acs_panel_path, columns=["NHGISCODE"])["NHGISCODE"]
        )
        overlap = set(panel["NHGISCODE"].unique()) & acs_ids
        print(f"Housing tracts in main ACS panel: {len(overlap):,} / "
              f"{panel['NHGISCODE'].nunique():,}")

    out_path = PROCESSED / "housing_tract_panel.parquet"
    panel.to_parquet(out_path, index=False)
    print(f"\n[OK] Saved: {out_path}")
    print(f"     Shape:  {panel.shape}")
    print(f"     Periods: {sorted(panel['acs_year'].unique())}")

    # Bridge CSV for R (03_robust_tests.R cannot read parquet directly)
    bridge_cols = ["NHGISCODE", "acs_year", "vacancy_rate", "owner_occ_rate"]
    bridge_path = PROCESSED / "housing_for_R.csv"
    panel[bridge_cols].to_csv(bridge_path, index=False)
    print(f"[OK] Saved: {bridge_path}  ({len(panel):,} rows)")

    print("\nOutcome coverage (non-null share):")
    for col in ["vacancy_rate", "owner_occ_rate"]:
        pct = panel[col].notna().mean() * 100
        print(f"  {col}: {pct:.1f}%")

    print("\nSample means by period:")
    print(
        panel.groupby("acs_year")[["vacancy_rate", "owner_occ_rate"]]
        .mean()
        .round(4)
        .to_string()
    )


if __name__ == "__main__":
    main()
