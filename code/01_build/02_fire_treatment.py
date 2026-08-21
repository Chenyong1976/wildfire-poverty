# -*- coding: utf-8 -*-
"""
Assign fire treatment status to census tracts (single clean cohort design).

Treatment definition (single non-overlapping cohort):
  - Treated (g=2016): first large wildfire (>=1,000 acres) in 2015-2017 overlaps tract
  - Never-treated (g=0): no large wildfire in 2013-2023; outside 100 km smoke buffer
  - Excluded: tracts with fires only in 2013-2014 or 2018-2023 (contaminated for controls,
    not part of treatment cohort); tracts within 100 km smoke buffer from 2015-2017 fires

Intensive margins (treated tracts only):
  - burned_share_pct: % of tract area within 2015-2017 fire perimeters
  - fire_count_2015_2017: number of distinct fires in cohort window

Diagnostic: Reports % of treated tracts retained in ACS nominal balanced panel.

Inputs:
  data/raw/mtbs_perimeters/S_USA.MTBS_BURN_AREA_BOUNDARY.shp
  data/raw/tract_shapefiles/nhgis0010_shapefile_tl2010_us_tract_2010/US_tract_2010.shp
  data/processed/acs_tract_panel.parquet  (for retention diagnostic)

Outputs:
  data/processed/fire_treatment_tracts.parquet
    One row per tract (GISJOIN, GEOID10, STATEFP10, COUNTYFP10)
    Key columns: treated, never_treated, excluded, first_fire_year,
                 burned_share_pct, fire_count_2015_2017, in_smoke_buffer
"""

import sys
import io
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

MTBS_FILE = RAW / "mtbs_perimeters" / "S_USA.MTBS_BURN_AREA_BOUNDARY.shp"
TRACT_FILE = (
    RAW
    / "tract_shapefiles"
    / "nhgis0010_shapefile_tl2010_us_tract_2010"
    / "US_tract_2010.shp"
)
ACS_PANEL = PROCESSED / "acs_tract_panel.parquet"

# Tract CRS (Albers Equal Area, meters) -- MTBS will be reprojected to match
TRACT_CRS = "ESRI:102003"

LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56",
}

MIN_ACRES = 1_000
COHORT_YEARS = (2015, 2016, 2017)
ANY_FIRE_EXCLUSION_YEARS = set(range(2013, 2024))  # 2013-2023 inclusive
SMOKE_BUFFER_M = 100_000  # 100 km in metres

# Sensitivity specifications for the first-fire restriction.
# prior_fire_start=1984 is the baseline (no prior fire 1984-2014).
# prior_fire_start=2000 → allow fires 1984-1999 (S1a).
# prior_fire_start=2005 → allow fires 1984-2004 (S1b).
# prior_fire_start=None → no restriction; all cohort-fire tracts treated (S2-pooled).
SENSITIVITY_SPECS = [
    {"prior_fire_start": 1984, "label": "baseline"},
    {"prior_fire_start": 2000, "label": "s1a"},
    {"prior_fire_start": 2005, "label": "s1b"},
    {"prior_fire_start": None, "label": "s2_pooled"},
]


def load_mtbs() -> gpd.GeoDataFrame:
    """Load MTBS Wildfire perimeters >= MIN_ACRES, reprojected to TRACT_CRS."""
    print(f"\nLoading MTBS: {MTBS_FILE.name}")
    mtbs = gpd.read_file(MTBS_FILE)
    print(f"  Raw records: {len(mtbs):,}")

    # Restrict to wildfires only (exclude prescribed burns)
    mtbs = mtbs[mtbs["FIRE_TYPE"] == "Wildfire"].copy()
    mtbs = mtbs[mtbs["ACRES"] >= MIN_ACRES].copy()
    print(f"  After Wildfire + >={MIN_ACRES:,} acres filter: {len(mtbs):,}")

    mtbs = mtbs.to_crs(TRACT_CRS)
    return mtbs[["FIRE_ID", "FIRE_NAME", "YEAR", "ACRES", "geometry"]]


def load_tracts() -> gpd.GeoDataFrame:
    """Load NHGIS 2010 tracts for lower-48, project to TRACT_CRS."""
    print(f"\nLoading tract boundaries: {TRACT_FILE.parent.name}")
    tracts = gpd.read_file(TRACT_FILE)
    print(f"  Raw tracts: {len(tracts):,}")

    tracts = tracts[tracts["STATEFP10"].isin(LOWER_48_FIPS)].copy()
    print(f"  Lower-48 tracts: {len(tracts):,}")

    if tracts.crs.to_string() != TRACT_CRS:
        tracts = tracts.to_crs(TRACT_CRS)

    # Add land area in m² (from ALAND10 which is already in m²)
    tracts["tract_area_m2"] = tracts["ALAND10"].astype(float)

    return tracts[
        [
            "GISJOIN", "GEOID10", "STATEFP10", "COUNTYFP10",
            "tract_area_m2", "geometry",
        ]
    ]


def fire_tract_join(
    mtbs: gpd.GeoDataFrame, tracts: gpd.GeoDataFrame
) -> pd.DataFrame:
    """
    Spatial join: for each tract find which fires (by year) overlap it.
    Returns a DataFrame with (GISJOIN, FIRE_ID, YEAR, ACRES).
    """
    print("\nSpatial join: fires -> tracts (this may take a few minutes) ...")
    joined = gpd.sjoin(
        tracts[["GISJOIN", "geometry"]],
        mtbs[["FIRE_ID", "YEAR", "ACRES", "geometry"]],
        how="left",
        predicate="intersects",
    )
    # Drop tracts with no fire at all
    n_total = tracts["GISJOIN"].nunique()
    n_fire = joined[joined["FIRE_ID"].notna()]["GISJOIN"].nunique()
    print(f"  Tracts with >=1 large wildfire (any year): {n_fire:,} / {n_total:,}")
    return joined.drop(columns=["geometry", "index_right"]).reset_index(drop=True)


def assign_cohort(
    joined: pd.DataFrame,
    tracts: gpd.GeoDataFrame,
    prior_fire_start: int | None = 1984,
) -> pd.DataFrame:
    """
    Assign each tract to treated / never_treated / excluded.

    prior_fire_start controls the first-fire restriction:
      1984 (default): no prior large fire in 1984-2014 (baseline design)
      2000:           allow fires 1984-1999; restrict only 2000-2014 (S1a)
      2005:           allow fires 1984-2004; restrict only 2005-2014 (S1b)
      None:           no restriction; all cohort-fire tracts are treated (S2-pooled)

    Returns one-row-per-tract DataFrame with treatment indicators.
    """
    # ── step 1: fires in each relevant window ──────────────────────────────
    cohort_fires = joined[joined["YEAR"].isin(COHORT_YEARS) & joined["FIRE_ID"].notna()]
    any_excl_fires = joined[
        joined["YEAR"].isin(ANY_FIRE_EXCLUSION_YEARS) & joined["FIRE_ID"].notna()
    ]

    if prior_fire_start is not None:
        prior_fire_excl_years = set(range(prior_fire_start, 2015))
        prior_fires = joined[
            joined["YEAR"].isin(prior_fire_excl_years) & joined["FIRE_ID"].notna()
        ]
        tracts_prior_fire = set(prior_fires["GISJOIN"].unique())
    else:
        prior_fire_excl_years = set()
        tracts_prior_fire = set()

    # Tracts that ever had a fire in 2013-2023 (any window)
    tracts_any_2013_2023 = set(any_excl_fires["GISJOIN"].unique())

    # Tracts with a fire in the cohort window (2015-2017)
    tracts_cohort = set(cohort_fires["GISJOIN"].unique())

    # First fire year in cohort window (for documentation)
    first_fire_yr = (
        cohort_fires.groupby("GISJOIN")["YEAR"].min().rename("first_fire_year")
    )

    # ── step 2: fire count in cohort ────────────────────────────────────────
    fire_counts = (
        cohort_fires.groupby("GISJOIN")["FIRE_ID"]
        .nunique()
        .rename("fire_count_2015_2017")
    )

    # ── step 3: assemble one-row-per-tract table ────────────────────────────
    base = tracts[["GISJOIN", "GEOID10", "STATEFP10", "COUNTYFP10", "tract_area_m2"]].copy()

    base["treated"] = (
        base["GISJOIN"].isin(tracts_cohort) &
        ~base["GISJOIN"].isin(tracts_prior_fire)
    ).astype(int)

    n_prior_excluded = (
        base["GISJOIN"].isin(tracts_cohort) &
        base["GISJOIN"].isin(tracts_prior_fire)
    ).sum()
    window_desc = (
        f"{prior_fire_start}-2014" if prior_fire_start is not None else "none"
    )
    print(f"  Prior-fire restriction window: {window_desc}. "
          f"Cohort tracts excluded: {n_prior_excluded:,}")

    base["never_treated_candidate"] = (
        ~base["GISJOIN"].isin(tracts_any_2013_2023)
    ).astype(int)

    base = base.merge(first_fire_yr, on="GISJOIN", how="left")
    base = base.merge(fire_counts, on="GISJOIN", how="left")
    base["fire_count_2015_2017"] = base["fire_count_2015_2017"].fillna(0).astype(int)

    n_treated = base["treated"].sum()
    n_never_cand = base["never_treated_candidate"].sum()
    print(f"\nCohort assignment (before smoke buffer):")
    print(f"  Treated:                         {n_treated:,}")
    print(f"  Never-treated candidates:         {n_never_cand:,}")
    print(f"  Remaining (excluded):             "
          f"{len(base) - n_treated - n_never_cand:,}")

    return base


def compute_prior_fire_year_counts(
    joined: pd.DataFrame,
    all_gisjoin: pd.Series,
) -> pd.DataFrame:
    """
    Compute distinct calendar years with >=1 large fire per tract for pre-2015 windows.
    Reuses the joined fire-tract DataFrame from fire_tract_join() — no extra spatial join.

    Returns one row per tract with columns:
      fire_years_1984_1999, fire_years_2000_2014, fire_years_2005_2014,
      fire_years_1984_2014, prior_fire_stratum (0 / 1 / 2+)
    """
    pre = joined[
        (joined["YEAR"] >= 1984) & (joined["YEAR"] <= 2014) & joined["FIRE_ID"].notna()
    ].copy()

    def count_years(yr_min: int, yr_max: int) -> pd.Series:
        sub = pre[(pre["YEAR"] >= yr_min) & (pre["YEAR"] <= yr_max)]
        return (
            sub.groupby("GISJOIN")["YEAR"]
            .nunique()
            .rename(f"fire_years_{yr_min}_{yr_max}")
        )

    counts = (
        pd.DataFrame({"GISJOIN": all_gisjoin})
        .set_index("GISJOIN")
        .join(count_years(1984, 1999))
        .join(count_years(2000, 2014))
        .join(count_years(2005, 2014))
        .join(count_years(1984, 2014))
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    # Stratum: 0 = no prior fires; 1 = exactly 1 year; 2 = 2+ years (collapsed)
    counts["prior_fire_stratum"] = counts["fire_years_1984_2014"].clip(upper=2)
    return counts


def compute_burned_share(
    treated_gisjoin: set,
    tracts: gpd.GeoDataFrame,
    mtbs: gpd.GeoDataFrame,
) -> pd.Series:
    """
    For treated tracts: compute % of tract land area covered by 2015-2017 fires.
    Returns a Series indexed by GISJOIN.
    """
    print("\nComputing burned share for treated tracts ...")
    cohort_mtbs = mtbs[mtbs["YEAR"].isin(COHORT_YEARS)].copy()
    treated_tracts = tracts[tracts["GISJOIN"].isin(treated_gisjoin)].copy()

    if cohort_mtbs.empty or treated_tracts.empty:
        return pd.Series(dtype=float)

    # Dissolve all cohort fires into a single multi-polygon (union)
    cohort_dissolved = cohort_mtbs.dissolve().reset_index(drop=True)

    overlay = gpd.overlay(
        treated_tracts[["GISJOIN", "tract_area_m2", "geometry"]],
        cohort_dissolved[["geometry"]],
        how="intersection",
    )
    overlay["intersect_area_m2"] = overlay.geometry.area
    burned = overlay.groupby("GISJOIN")["intersect_area_m2"].sum()

    # Divide by tract land area; cap at 100%
    tract_areas = (
        treated_tracts.set_index("GISJOIN")["tract_area_m2"]
        .replace(0, np.nan)
    )
    burned_share = ((burned / tract_areas) * 100).clip(upper=100).rename("burned_share_pct")
    print(f"  Treated tracts with burned-share computed: {burned_share.notna().sum():,}")
    return burned_share


def build_smoke_buffer(mtbs: gpd.GeoDataFrame) -> "shapely.geometry.base.BaseGeometry":
    """
    Return the union of 100 km buffers around 2015-2017 cohort fire perimeters.
    Uses tract CRS (metres) so buffer distance is exact.
    """
    print(f"\nBuilding {SMOKE_BUFFER_M/1000:.0f} km smoke buffer ...")
    cohort_mtbs = mtbs[mtbs["YEAR"].isin(COHORT_YEARS)]
    if cohort_mtbs.empty:
        raise ValueError("No cohort fires found for smoke buffer construction.")

    buffered = cohort_mtbs.geometry.buffer(SMOKE_BUFFER_M)
    union = buffered.union_all()
    print("  Buffer constructed.")
    return union


def apply_smoke_buffer(
    base: pd.DataFrame,
    tracts: gpd.GeoDataFrame,
    smoke_union,
) -> pd.DataFrame:
    """
    Flag never-treated candidates whose centroid falls within smoke_union.
    Adds 'in_smoke_buffer' column and sets 'never_treated' = 0 for those tracts.
    """
    print("\nApplying smoke buffer exclusion ...")
    centroids = tracts.set_index("GISJOIN").centroid

    # Bug fix: candidates is a Series with integer row index; indexing into
    # in_buffer[in_buffer].index would return integer positions, not GISJOIN strings.
    # Iterate over the GISJOIN values directly to build in_buffer_set correctly.
    candidate_gisjoins = base[base["never_treated_candidate"] == 1]["GISJOIN"].tolist()
    in_buffer_set = {
        gj for gj in candidate_gisjoins
        if gj in centroids.index and centroids.loc[gj].within(smoke_union)
    }

    base["in_smoke_buffer"] = base["GISJOIN"].isin(in_buffer_set).astype(int)
    base["never_treated"] = (
        (base["never_treated_candidate"] == 1) & (base["in_smoke_buffer"] == 0)
    ).astype(int)

    n_excluded_by_smoke = base[
        (base["never_treated_candidate"] == 1) & (base["in_smoke_buffer"] == 1)
    ].shape[0]
    n_clean_controls = base["never_treated"].sum()
    print(f"  Never-treated excluded by smoke buffer: {n_excluded_by_smoke:,}")
    print(f"  Clean never-treated controls:           {n_clean_controls:,}")
    return base


def run_acs_diagnostic(base: pd.DataFrame) -> None:
    """
    Check % of treated tracts retained in the NHGIS nominal ACS balanced panel.
    Per RESEARCH_PLAN: if < 95%, fallback crosswalk required.
    """
    if not ACS_PANEL.exists():
        print("\n[SKIP] ACS panel not found -- run 01_acs_nhgis_load.py first.")
        return

    print("\n─── ACS Nominal Panel Retention Diagnostic ───")
    acs_gisjoin = set(pd.read_parquet(ACS_PANEL, columns=["NHGISCODE"])["NHGISCODE"])

    treated_gj = set(base[base["treated"] == 1]["GISJOIN"])
    retained = treated_gj & acs_gisjoin
    pct = 100 * len(retained) / len(treated_gj) if treated_gj else 0

    print(f"  Treated tracts:            {len(treated_gj):,}")
    print(f"  In ACS nominal panel:      {len(retained):,}")
    print(f"  Retention rate:            {pct:.1f}%")

    if pct >= 95:
        print("  [OK] >=95% retention -- nominal balanced panel adequate for analysis.")
    else:
        print("  [WARNING] <95% retention -- implement Census Tract Relationship File fallback")
        print("            (see RESEARCH_PLAN.md §2, 'Tract boundary harmonization').")

    # Control retention
    ctrl_gj = set(base[base["never_treated"] == 1]["GISJOIN"])
    ctrl_retained = ctrl_gj & acs_gisjoin
    ctrl_pct = 100 * len(ctrl_retained) / len(ctrl_gj) if ctrl_gj else 0
    print(f"\n  Never-treated controls:    {len(ctrl_gj):,}")
    print(f"  In ACS nominal panel:      {len(ctrl_retained):,}")
    print(f"  Control retention rate:    {ctrl_pct:.1f}%")


def main() -> None:
    print("=" * 70)
    print("FIRE TREATMENT ASSIGNMENT: Single Cohort, Tract Level")
    print("=" * 70)

    PROCESSED.mkdir(parents=True, exist_ok=True)

    mtbs = load_mtbs()
    tracts = load_tracts()

    # One spatial join reused across all specs
    joined = fire_tract_join(mtbs, tracts)

    # Prior fire year counts (all tracts, computed once from the joined table)
    print("\nComputing prior fire year counts ...")
    prior_counts = compute_prior_fire_year_counts(joined, tracts["GISJOIN"])
    prior_counts_path = PROCESSED / "prior_fire_counts.parquet"
    prior_counts.to_parquet(prior_counts_path, index=False)
    print(f"  [OK] Saved: {prior_counts_path}")
    dist = prior_counts["prior_fire_stratum"].value_counts().sort_index()
    print(f"  Stratum distribution (0/1/2+): {dist.to_dict()}")

    # Smoke buffer (same for all specs — defined by 2015-2017 fires)
    smoke_union = build_smoke_buffer(mtbs)

    # Burned share for ALL cohort-fire tracts (superset; each spec slices its own)
    all_cohort_set = set(
        joined[joined["YEAR"].isin(COHORT_YEARS) & joined["FIRE_ID"].notna()]["GISJOIN"]
    )
    burned_share_all = compute_burned_share(all_cohort_set, tracts, mtbs)

    out_cols = [
        "GISJOIN", "GEOID10", "STATEFP10", "COUNTYFP10", "tract_area_m2",
        "treated", "never_treated", "never_treated_candidate",
        "in_smoke_buffer", "excluded",
        "first_fire_year", "fire_count_2015_2017", "burned_share_pct",
    ]

    for spec in SENSITIVITY_SPECS:
        label = spec["label"]
        pfs = spec["prior_fire_start"]
        print(f"\n{'='*70}")
        print(f"SPEC: {label}  (prior_fire_start={pfs})")
        print(f"{'='*70}")

        base = assign_cohort(joined, tracts, prior_fire_start=pfs)

        base = base.merge(burned_share_all.reset_index(), on="GISJOIN", how="left")
        base["burned_share_pct"] = base["burned_share_pct"].fillna(0.0)

        base = apply_smoke_buffer(base, tracts, smoke_union)
        base["excluded"] = (
            (base["treated"] == 0) & (base["never_treated"] == 0)
        ).astype(int)

        print(f"\n─── Final sample: {label} ───")
        print(f"  Treated:         {base['treated'].sum():,}")
        print(f"  Never-treated:   {base['never_treated'].sum():,}")
        print(f"  Excluded:        {base['excluded'].sum():,}")

        if label == "baseline":
            run_acs_diagnostic(base)

        out_path = PROCESSED / f"fire_treatment_tracts_{label}.parquet"
        base[out_cols].to_parquet(out_path, index=False)
        print(f"  [OK] Saved: {out_path}")

    # Backward-compatible copy: keep the original filename pointing at baseline
    import shutil
    shutil.copy(
        PROCESSED / "fire_treatment_tracts_baseline.parquet",
        PROCESSED / "fire_treatment_tracts.parquet",
    )
    print("\n[OK] fire_treatment_tracts.parquet updated (baseline copy).")


if __name__ == "__main__":
    main()
