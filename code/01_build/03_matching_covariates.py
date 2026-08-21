"""
Build matching covariates for PS-IPW weighting (2010-vintage census tracts).

Primary WFP raster: WFP 2014 (predetermined before 2015 fire season).
Secondary WFP raster: WFP 2012 (robustness check; available from wildfire-finance).

Raw WFP scores are converted to percentile ranks (0–100) using the global CONUS
pixel distribution before computing tract-level summaries.  Three summaries are
computed for each vintage and all three are reported in the balance table:
  (1) mean WFP percentile across tract pixels
  (2) % tract area in each hazard quintile (Q1–Q5)
  (3) distance (km) from tract centroid to nearest pixel > 75th pct

WFP 2014 data source: USFS LANDFIRE — confirmed present locally.

Inputs:
  data/raw/whp_rasters/whp_2014_continuous/whp2014_cnt   WFP 2014 ESRI Grid (EPSG:5070) [primary]
  data/raw/whp_rasters/wfp2012_cnt                       WFP 2012 ESRI Grid (EPSG:5070) [robustness]
  data/raw/mtbs_perimeters/S_USA.MTBS_BURN_AREA_BOUNDARY.shp
  data/raw/tract_shapefiles/.../US_tract_2010.shp
  data/raw/rucc/ruralurbancodes2013.xls
  data/processed/acs_tract_panel_xwalk.parquet

Output:
  data/processed/matching_covariates.parquet
    One row per 2010-vintage tract GISJOIN (lower-48, pop >= 500 in 2014 ACS).
    Primary WFP 2014 columns (used in PS model and balance table):
      wfp_mean_pct, wfp_q1_frac, wfp_q2_frac, wfp_q3_frac, wfp_q4_frac, wfp_q5_frac,
      wfp_dist_km
    Robustness WFP 2012 columns (sensitivity check only):
      wfp12_mean_pct, wfp12_q1_frac, wfp12_q2_frac, wfp12_q3_frac, wfp12_q4_frac,
      wfp12_q5_frac, wfp12_dist_km
    Other covariates:
      GISJOIN, FIPS11, COUNTYFP, STATEFP,
      fire_pre2013, log_acres_pre2013,
      pov_rate_2014, log_inc_2014, emp_rate_2014, pop_2014, mig_rate_2014,
      rucc_2013
"""

import sys
import io
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import rowcol
import scipy.ndimage as ndi
from rasterstats import zonal_stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# WFP 2014: primary matching covariate (predetermined before 2015 fire season).
WFP_2014_FILE = RAW / "whp_rasters" / "whp_2014_continuous" / "whp2014_cnt"
# WFP 2012: robustness check.
WFP_2012_FILE = RAW / "whp_rasters" / "wfp2012_cnt"
# Alias for backward-compatible internal calls
WFP_FILE = WFP_2014_FILE

MTBS_FILE = RAW / "mtbs_perimeters" / "S_USA.MTBS_BURN_AREA_BOUNDARY.shp"
TRACT_FILE = (
    RAW / "tract_shapefiles"
    / "nhgis0010_shapefile_tl2010_us_tract_2010"
    / "US_tract_2010.shp"
)
RUCC_FILE = RAW / "rucc" / "ruralurbancodes2013.xls"
PANEL_FILE = PROCESSED / "acs_tract_panel_xwalk.parquet"

TRACT_CRS = "ESRI:102003"   # Albers Equal Area, metres — used for MTBS
WFP_CRS = "EPSG:5070"       # WFP native CRS

LOWER_48_FIPS = {
    "01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26",
    "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47",
    "48", "49", "50", "51", "53", "54", "55", "56",
}

MIN_ACRES = 1_000
PRE2013_YEARS = set(range(1984, 2013))  # 1984–2012 inclusive


# ── WFP raster ────────────────────────────────────────────────────────────────

def build_wfp_percentile_array(
    wfp_path: Path,
    label: str = "WFP",
) -> tuple[np.ndarray, object, float, float]:
    """
    Read a WFP raster and convert raw scores to percentile ranks (0–100).

    Args:
        wfp_path : path to the ESRI Grid raster (EPSG:5070)
        label    : human-readable label for print statements (e.g. "WFP 2014")

    Returns:
        wfp_pct   : 2-D float32 array, NaN where nodata
        transform : rasterio affine transform (EPSG:5070)
        p75       : raw-score value at 75th percentile (for high-hazard mask)
        bins      : 101-element array of raw score quantile breakpoints
    """
    print(f"Loading {label} raster from {wfp_path} ...")
    with rasterio.open(wfp_path) as src:
        raw = src.read(1).astype(np.float32)
        nd = float(src.nodata)
        transform = src.transform

    nodata_mask = (raw == nd) if nd is not None else np.zeros_like(raw, dtype=bool)
    valid = raw[~nodata_mask]
    print(f"  Valid pixels: {len(valid):,}  |  raw range: {valid.min():.0f}–{valid.max():.0f}")

    # 101 quantile breakpoints: bins[i] = i-th percentile of the CONUS distribution
    bins = np.percentile(valid, np.arange(0, 101)).astype(np.float32)
    p75 = float(bins[75])
    print(f"  Quintile breakpoints (20/40/60/80th pct raw): "
          f"{bins[20]:.1f} / {bins[40]:.1f} / {bins[60]:.1f} / {bins[80]:.1f}")
    print(f"  75th pct raw value (high-hazard threshold): {p75:.1f}")

    # Convert raw scores to percentile ranks via searchsorted on the 101-bin grid
    # np.searchsorted(bins, v, side='right') returns 1..101 for values in range;
    # subtract 1 to get 0..100 then clip to [0, 100].
    wfp_pct = (np.searchsorted(bins, raw, side="right") - 1).astype(np.float32)
    wfp_pct[nodata_mask] = np.nan

    print(f"  Percentile array: range [{np.nanmin(wfp_pct):.0f}, {np.nanmax(wfp_pct):.0f}]")
    return wfp_pct, transform, p75, bins


def compute_wfp_zonal_stats(
    tracts_5070: gpd.GeoDataFrame,
    wfp_pct: np.ndarray,
    transform: object,
) -> pd.DataFrame:
    """
    Compute per-tract WFP percentile summaries using zonal_stats.

    Returns DataFrame with GISJOIN + wfp_mean_pct + wfp_q[1-5]_frac.
    """
    print("\nComputing WFP zonal statistics (this takes ~5–10 min for 70k tracts) ...")

    # Custom stat functions: each receives 1-D array of non-nodata pct values [0,100]
    add_stats = {
        "q1_frac": lambda x: float(np.mean((x >= 0) & (x <= 20))),
        "q2_frac": lambda x: float(np.mean((x > 20) & (x <= 40))),
        "q3_frac": lambda x: float(np.mean((x > 40) & (x <= 60))),
        "q4_frac": lambda x: float(np.mean((x > 60) & (x <= 80))),
        "q5_frac": lambda x: float(np.mean(x > 80)),
    }

    # Replace NaN with a dedicated nodata value for rasterstats
    wfp_rs = np.where(np.isnan(wfp_pct), -1.0, wfp_pct).astype(np.float32)

    results = zonal_stats(
        tracts_5070,
        wfp_rs,
        affine=transform,
        stats=["mean"],
        nodata=-1.0,
        add_stats=add_stats,
        all_touched=True,   # include pixels that touch (not just center-within) polygon
    )

    df = pd.DataFrame(results)
    df.insert(0, "GISJOIN", tracts_5070["GISJOIN"].values)
    df = df.rename(columns={
        "mean":    "wfp_mean_pct",
        "q1_frac": "wfp_q1_frac",
        "q2_frac": "wfp_q2_frac",
        "q3_frac": "wfp_q3_frac",
        "q4_frac": "wfp_q4_frac",
        "q5_frac": "wfp_q5_frac",
    })

    n_valid = df["wfp_mean_pct"].notna().sum()
    print(f"  WFP mean coverage: {n_valid:,} / {len(df):,} tracts")
    return df[["GISJOIN", "wfp_mean_pct",
               "wfp_q1_frac", "wfp_q2_frac", "wfp_q3_frac", "wfp_q4_frac", "wfp_q5_frac"]]


def compute_wfp_distance(
    tracts_5070: gpd.GeoDataFrame,
    wfp_pct: np.ndarray,
    transform: object,
) -> pd.Series:
    """
    Distance (km) from each tract centroid to the nearest WFP > 75th pct pixel.

    Uses scipy.ndimage.distance_transform_edt on the CONUS high-hazard boolean mask.
    Pixels that are nodata (NaN) are treated as non-high-hazard.

    Returns Series indexed by GISJOIN.
    """
    print("\nComputing distance to nearest high-hazard WFP pixel ...")

    # High-hazard mask: percentile > 75, valid (non-NaN)
    high_hazard = (wfp_pct > 75) & ~np.isnan(wfp_pct)
    print(f"  High-hazard pixels (WFP > 75th pct): {high_hazard.sum():,} "
          f"({100*high_hazard.mean():.1f}% of all pixels)")

    # Distance transform: distance in pixels from each cell to nearest True cell
    # Input is the INVERSE mask (edt measures distance from False cells to True cells,
    # i.e., from non-high-hazard to high-hazard)
    print("  Running distance transform (may take ~1 min, ~2 GB RAM) ...")
    dist_pixels = ndi.distance_transform_edt(~high_hazard)
    dist_km = (dist_pixels * 270.0 / 1000.0).astype(np.float32)
    del dist_pixels

    # Sample distance at tract centroids
    # Reproject centroids to WFP CRS (EPSG:5070 = same as wfp_5070)
    centroids = tracts_5070.geometry.centroid

    # Convert geographic coordinates to pixel row/col
    rows, cols = rowcol(
        transform,
        xs=centroids.x.values,
        ys=centroids.y.values,
    )
    rows = np.clip(np.array(rows), 0, dist_km.shape[0] - 1)
    cols = np.clip(np.array(cols), 0, dist_km.shape[1] - 1)

    dist_series = pd.Series(
        dist_km[rows, cols],
        index=tracts_5070["GISJOIN"].values,
        name="wfp_dist_km",
    )
    print(f"  Distance range: {dist_series.min():.1f}–{dist_series.max():.1f} km  "
          f"(median: {dist_series.median():.1f} km)")
    return dist_series


# ── Pre-2013 fire history ─────────────────────────────────────────────────────

def compute_pre2013_fires(tracts: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    For each 2010-vintage tract, compute binary fire indicator and log acres
    from MTBS perimeters 1984–2012 (wildfire >= 1,000 acres).

    Returns DataFrame with GISJOIN, fire_pre2013, log_acres_pre2013.
    """
    print("\nLoading MTBS pre-2013 fire history ...")
    mtbs = gpd.read_file(MTBS_FILE)
    mtbs = mtbs[mtbs["FIRE_TYPE"] == "Wildfire"].copy()
    mtbs = mtbs[mtbs["ACRES"] >= MIN_ACRES].copy()
    mtbs = mtbs[mtbs["YEAR"].isin(PRE2013_YEARS)].copy()
    mtbs = mtbs.to_crs(TRACT_CRS)
    print(f"  MTBS 1984–2012 wildfires >= {MIN_ACRES:,} acres: {len(mtbs):,}")

    tracts_albers = tracts.to_crs(TRACT_CRS)[["GISJOIN", "geometry"]]

    print("  Spatial join: pre-2013 fires → tracts ...")
    joined = gpd.sjoin(
        tracts_albers,
        mtbs[["FIRE_ID", "ACRES", "geometry"]],
        how="left",
        predicate="intersects",
    ).drop(columns=["geometry", "index_right"])

    fire_any = joined.groupby("GISJOIN")["FIRE_ID"].any().rename("fire_pre2013")
    acres_sum = (
        joined[joined["FIRE_ID"].notna()]
        .groupby("GISJOIN")["ACRES"]
        .sum()
        .rename("acres_pre2013")
    )

    result = (
        tracts[["GISJOIN"]]
        .merge(fire_any.reset_index(), on="GISJOIN", how="left")
        .merge(acres_sum.reset_index(), on="GISJOIN", how="left")
    )
    result["fire_pre2013"] = result["fire_pre2013"].fillna(False).astype(int)
    result["acres_pre2013"] = result["acres_pre2013"].fillna(0.0)
    result["log_acres_pre2013"] = np.log1p(result["acres_pre2013"])

    n_fire = result["fire_pre2013"].sum()
    print(f"  Tracts with pre-2013 fire: {n_fire:,} / {len(result):,} "
          f"({100*n_fire/len(result):.1f}%)")
    return result[["GISJOIN", "fire_pre2013", "log_acres_pre2013"]]


# ── ACS 2014 baseline ─────────────────────────────────────────────────────────

def load_acs_baseline() -> pd.DataFrame:
    """
    Extract h=-1 (ACS 2014) covariates from the crosswalk panel.

    Returns DataFrame with GISJOIN + poverty/income/employment/migration/population.
    """
    print("\nLoading ACS 2014 baseline covariates (h=-1) ...")
    panel = pd.read_parquet(PANEL_FILE, columns=[
        "NHGISCODE", "acs_year", "h",
        "poverty_rate", "log_med_income_2020", "employment_rate",
        "population", "in_migration_rate",
    ])
    base = panel[panel["h"] == -1].copy()
    base = base.rename(columns={
        "NHGISCODE":          "GISJOIN",
        "poverty_rate":       "pov_rate_2014",
        "log_med_income_2020":"log_inc_2014",
        "employment_rate":    "emp_rate_2014",
        "population":         "pop_2014",
        "in_migration_rate":  "mig_rate_2014",
    })
    print(f"  ACS 2014 baseline: {len(base):,} tracts")
    return base[["GISJOIN", "pov_rate_2014", "log_inc_2014",
                 "emp_rate_2014", "pop_2014", "mig_rate_2014"]]


# ── RUCC ──────────────────────────────────────────────────────────────────────

def load_rucc(tracts: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Merge USDA RUCC 2013 county code to tracts via 5-digit county FIPS.

    Returns DataFrame with GISJOIN + rucc_2013.
    """
    print("\nLoading RUCC 2013 ...")
    rucc = pd.read_excel(RUCC_FILE, usecols=["FIPS", "RUCC_2013"])
    rucc = rucc.dropna(subset=["RUCC_2013"])
    rucc["FIPS"] = rucc["FIPS"].astype(int).astype(str).str.zfill(5)
    rucc["rucc_2013"] = rucc["RUCC_2013"].astype(int)

    # Derive 5-digit county FIPS from tract GISJOIN:
    #   GISJOIN: G + state(2) + 0 + county(3) + 0 + tract(6) = 14 chars
    #   county FIPS = state(2) + county(3) = chars [1:3] + [4:7]
    t = tracts[["GISJOIN"]].copy()
    t["FIPS"] = t["GISJOIN"].str[1:3] + t["GISJOIN"].str[4:7]

    result = t.merge(rucc[["FIPS", "rucc_2013"]], on="FIPS", how="left")
    n_missing = result["rucc_2013"].isna().sum()
    if n_missing > 0:
        print(f"  [WARNING] {n_missing} tracts have no RUCC match (DC/territories?)")
    print(f"  RUCC 2013 matched: {result['rucc_2013'].notna().sum():,} / {len(result):,}")
    return result[["GISJOIN", "rucc_2013"]]


# ── Main ──────────────────────────────────────────────────────────────────────

def _compute_wfp_summaries(
    tracts_5070: gpd.GeoDataFrame,
    wfp_path: Path,
    label: str,
    prefix: str,
) -> pd.DataFrame:
    """
    Helper: compute all three WFP summaries for a given raster vintage.

    Returns a DataFrame with columns:
      GISJOIN, {prefix}mean_pct, {prefix}q[1-5]_frac, {prefix}dist_km
    """
    wfp_pct, wfp_transform, _, _ = build_wfp_percentile_array(wfp_path, label)

    zs = compute_wfp_zonal_stats(tracts_5070, wfp_pct, wfp_transform)
    dist_s = compute_wfp_distance(tracts_5070, wfp_pct, wfp_transform)

    zs = zs.merge(
        dist_s.rename(f"{prefix}dist_km").reset_index().rename(columns={"index": "GISJOIN"}),
        on="GISJOIN", how="left",
    )
    del wfp_pct

    # Rename generic names to prefixed names
    rename_map = {
        "wfp_mean_pct": f"{prefix}mean_pct",
        "wfp_q1_frac":  f"{prefix}q1_frac",
        "wfp_q2_frac":  f"{prefix}q2_frac",
        "wfp_q3_frac":  f"{prefix}q3_frac",
        "wfp_q4_frac":  f"{prefix}q4_frac",
        "wfp_q5_frac":  f"{prefix}q5_frac",
    }
    zs = zs.rename(columns=rename_map)
    return zs


def main() -> None:
    print("=" * 70)
    print("MATCHING COVARIATES: WFP 2014 (primary) + WFP 2012 (robustness)")
    print("                   + Pre-2013 Fire + ACS 2014 + RUCC")
    print("=" * 70)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # ── Tract boundaries in WFP CRS (EPSG:5070) ──
    print("\nLoading 2010-vintage tract boundaries ...")
    tracts_raw = gpd.read_file(TRACT_FILE)
    tracts_raw = tracts_raw[tracts_raw["STATEFP10"].isin(LOWER_48_FIPS)].copy()
    tracts_5070 = tracts_raw[["GISJOIN", "STATEFP10", "COUNTYFP10", "geometry"]].to_crs(WFP_CRS)
    print(f"  Tracts: {len(tracts_5070):,}")

    # ── WFP 2014 (primary) ──
    print("\n" + "─" * 60)
    print("WFP 2014 — primary matching covariate")
    print("─" * 60)
    if not WFP_2014_FILE.exists():
        raise FileNotFoundError(
            f"WFP 2014 raster not found at {WFP_2014_FILE}. "
            "Check that whp_2014_continuous/whp2014_cnt exists under data/raw/whp_rasters/."
        )
    wfp14_df = _compute_wfp_summaries(
        tracts_5070, WFP_2014_FILE, label="WFP 2014", prefix="wfp_"
    )

    # ── WFP 2012 (robustness) ──
    print("\n" + "─" * 60)
    print("WFP 2012 — robustness check")
    print("─" * 60)
    if WFP_2012_FILE.exists():
        wfp12_df = _compute_wfp_summaries(
            tracts_5070, WFP_2012_FILE, label="WFP 2012", prefix="wfp12_"
        )
    else:
        print(f"  [INFO] WFP 2012 not found at {WFP_2012_FILE}; skipping robustness columns.")
        wfp12_df = tracts_5070[["GISJOIN"]].copy()

    # ── Pre-2013 fire history ──
    fire_df = compute_pre2013_fires(tracts_raw)

    # ── ACS 2014 baseline ──
    acs_df = load_acs_baseline()

    # ── RUCC ──
    rucc_df = load_rucc(tracts_5070)

    # ── Identifiers ──
    ids = tracts_5070[["GISJOIN", "STATEFP10", "COUNTYFP10"]].copy()
    ids["FIPS11"] = ids["GISJOIN"].str[1:3] + ids["GISJOIN"].str[4:7] + ids["GISJOIN"].str[8:14]
    ids = ids.rename(columns={"STATEFP10": "STATEFP", "COUNTYFP10": "COUNTYFP"})

    # ── Merge all ──
    print("\nMerging all covariate sets ...")
    covs = (
        ids
        .merge(wfp14_df, on="GISJOIN", how="left")
        .merge(wfp12_df, on="GISJOIN", how="left")
        .merge(fire_df, on="GISJOIN", how="left")
        .merge(acs_df, on="GISJOIN", how="left")
        .merge(rucc_df, on="GISJOIN", how="left")
    )

    # Restrict to tracts present in ACS 2014 (pop >= 500 already enforced there)
    pre_n = len(covs)
    covs = covs[covs["pov_rate_2014"].notna()].copy()
    print(f"  After ACS 2014 inner join: {len(covs):,} tracts (dropped {pre_n-len(covs):,} "
          f"with no 2014 ACS data)")

    out_path = PROCESSED / "matching_covariates.parquet"
    covs.to_parquet(out_path, index=False)

    print(f"\n[OK] Saved: {out_path}")
    print(f"     Shape:  {covs.shape}")
    print(f"     Tracts: {covs['GISJOIN'].nunique():,}")

    print("\nCovariate coverage (non-null share):")
    check_cols = [
        "wfp_mean_pct", "wfp_q1_frac", "wfp_q5_frac", "wfp_dist_km",
        "wfp12_mean_pct",
        "fire_pre2013", "log_acres_pre2013",
        "pov_rate_2014", "log_inc_2014", "emp_rate_2014",
        "mig_rate_2014", "rucc_2013",
    ]
    for col in check_cols:
        if col in covs.columns:
            pct = covs[col].notna().mean() * 100
            print(f"  {col:<25}: {pct:.1f}%")

    # Normalized difference in WFP 2014 between treated and controls
    fire_path = PROCESSED / "fire_treatment_tracts.parquet"
    if fire_path.exists():
        fire = pd.read_parquet(fire_path, columns=["GISJOIN", "treated"])
        covs_t = covs.merge(fire, on="GISJOIN", how="left")
        print("\nWFP 2014 balance check (treated vs. never-treated):")
        for grp, label in [(1, "Treated"), (0, "Never-treated")]:
            sub = covs_t[covs_t["treated"] == grp]
            print(f"  {label} (n={len(sub):,}): mean WFP pct = {sub['wfp_mean_pct'].mean():.1f}  "
                  f"q5_frac = {sub['wfp_q5_frac'].mean():.3f}  "
                  f"dist_km = {sub['wfp_dist_km'].mean():.1f}")
        t = covs_t[covs_t["treated"] == 1]["wfp_mean_pct"]
        c = covs_t[covs_t["treated"] == 0]["wfp_mean_pct"]
        nd = (t.mean() - c.mean()) / t.std()
        print(f"  Normalized difference (mean WFP 2014): {nd:.3f}"
              f"  {'[HIGH: apply PS caliper]' if abs(nd) > 0.25 else '[OK]'}")


if __name__ == "__main__":
    main()
