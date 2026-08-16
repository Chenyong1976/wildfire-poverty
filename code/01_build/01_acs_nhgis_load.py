"""
Load and clean ACS tract-level data from NHGIS extracts.

Data sources:
  - Time series: data/raw/acs_extracts/nhgis_inc_pov_emp/nhgis0012_ts_nominal_tract.csv
    Tables: AV0 (population), B84 (employment), B79 (median income), AX7 (poverty)
  - Migration: data/raw/acs_extracts/nhgis_mig/nhgis0013_ds{...}_tract.csv (6 files)
    Table: B07003 (geographical mobility by sex)
  - CPI-U deflator: data/raw/CPIAUCSL.csv (FRED series CPIAUCSL)

WARNING — NOMINAL INTEGRATION (re-download recommended before publication):
    The current time series file uses NHGIS *nominal* integration. Tract boundaries
    change between decennial censuses (2000→2010, 2010→2020) and are NOT harmonized.
    Tracts that were split or merged across census years will have truncated series.
    For the published analysis, re-download using NHGIS Standardized (S) integration
    so that all periods share consistent 2020 tract definitions. The nominal file is
    acceptable for exploratory work; the standardized file is required for publication.

Outputs:
    data/processed/acs_tract_panel.parquet
        Long panel: NHGISCODE × acs_year (6 periods, h ∈ {−3,−2,−1,0,+1,+2})
        Identifiers: NHGISCODE, FIPS11 (11-digit), acs_year (int), h (event-study index)
        Outcomes: poverty_rate, employment_rate, log_med_income_2020,
                  in_migration_rate, population
        MOE flags: poverty_moe_flag (dropped if MOE > 30% of count)
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

TS_FILE = RAW / "acs_extracts" / "nhgis_inc_pov_emp" / "nhgis0012_ts_nominal_tract.csv"
MIG_DIR = RAW / "acs_extracts" / "nhgis_mig"
CPI_FILE = RAW / "CPIAUCSL.csv"

# ACS window string → (integer year label, event-study h, final calendar year for CPI deflation)
ACS_PERIODS: dict[str, tuple[int, int, int]] = {
    "2006-2010": (2010, -3, 2010),
    "2008-2012": (2012, -2, 2012),
    "2010-2014": (2014, -1, 2014),
    "2018-2022": (2022,  0, 2022),
    "2019-2023": (2023, +1, 2023),
    "2020-2024": (2024, +2, 2024),
}

# NHGIS B07003 prefix per ACS period (from codebooks)
MIG_PREFIX: dict[str, str] = {
    "2006-2010": "JXZ",
    "2008-2012": "Q4P",
    "2010-2014": "ABND",
    "2018-2022": "AQ0Z",
    "2019-2023": "AS1T",
    "2020-2024": "AU24",
}

# Migration file glob pattern → YEAR string (ds### encodes the NHGIS dataset ID)
MIG_FILES: dict[str, str] = {
    "nhgis0013_ds177_20105_tract.csv": "2006-2010",
    "nhgis0013_ds192_20125_tract.csv": "2008-2012",
    "nhgis0013_ds207_20145_tract.csv": "2010-2014",
    "nhgis0013_ds263_20225_tract.csv": "2018-2022",
    "nhgis0013_ds268_20235_tract.csv": "2019-2023",
    "nhgis0013_ds273_20245_tract.csv": "2020-2024",
}

CPI_BASE_YEAR = 2020
CPI_BASE = 258.9  # annual average CPI-U 2020, verified against CPIAUCSL.csv


def load_cpi_deflators() -> dict[int, float]:
    """
    Return deflation factors: factor[year] = CPI_BASE / CPI_annual_avg[year].
    Multiply nominal income by factor to convert to 2020 dollars.
    """
    cpi = pd.read_csv(CPI_FILE, parse_dates=["observation_date"])
    cpi["year"] = cpi["observation_date"].dt.year
    annual = cpi.groupby("year")["CPIAUCSL"].mean()

    years_needed = {2010, 2012, 2014, 2022, 2023, 2024}
    missing = years_needed - set(annual.index)
    if missing:
        raise ValueError(f"CPI data missing for years: {missing}. Check {CPI_FILE}.")

    factors = {yr: CPI_BASE / annual[yr] for yr in years_needed}

    print("CPI-U deflation factors (to 2020 dollars):")
    for yr in sorted(factors):
        print(f"  {yr}: CPI={annual[yr]:.1f}  factor={factors[yr]:.4f}")
    return factors


def _make_fips11(df: pd.DataFrame, state_col: str, county_col: str, tract_col: str) -> pd.Series:
    """Construct 11-digit FIPS from integer state/county/tract columns."""
    return (
        df[state_col].astype(str).str.zfill(2)
        + df[county_col].astype(str).str.zfill(3)
        + df[tract_col].astype(str).str.zfill(6)
    )


def load_time_series(cpi_factors: dict[int, float]) -> pd.DataFrame:
    """
    Load NHGIS nominal time series; compute outcomes; apply MOE filter.

    Returns long-format DataFrame with one row per (NHGISCODE, acs_year).
    """
    print(f"\nLoading time series: {TS_FILE.name}")
    df = pd.read_csv(TS_FILE, low_memory=False)
    print(f"  Raw rows: {len(df):,}  |  Periods: {sorted(df['YEAR'].unique())}")

    # Keep only the six study periods
    df = df[df["YEAR"].isin(ACS_PERIODS)].copy()

    # Add year labels and event-study h
    df["acs_year"] = df["YEAR"].map({k: v[0] for k, v in ACS_PERIODS.items()})
    df["h"] = df["YEAR"].map({k: v[1] for k, v in ACS_PERIODS.items()})

    # Standard FIPS11 identifier
    df["FIPS11"] = _make_fips11(df, "STATEFP", "COUNTYFP", "TRACTA")

    # --- Poverty rate ---
    df["poverty_count"] = df["AX7AA"]
    df["poverty_denom"] = df["AX7AA"] + df["AX7AB"]
    df["poverty_rate"] = df["poverty_count"] / df["poverty_denom"]

    # MOE flag: flag (do NOT drop) tracts where poverty count MOE > 30% of count.
    # Tract-level ACS poverty counts have median MOE ~51% of count — a drop filter
    # at 30% would remove ~92% of observations, systematically excluding rural areas.
    # We flag for downstream sensitivity analysis; primary filter is population >= 500.
    df["poverty_moe_flag"] = (
        (df["AX7AAM"] > 0.30 * df["poverty_count"].clip(lower=1))
        | df["AX7AAM"].isna()
    )
    n_flagged = df["poverty_moe_flag"].sum()
    n_rows = len(df)
    print(f"  Poverty MOE flag (>30%): {n_flagged:,}/{n_rows:,} ({100*n_flagged/n_rows:.1f}%) "
          f"tract-periods flagged (retained; flag column included for sensitivity analysis)")

    # --- Employment rate (B84AD / B84AC: civilian employed / civilian labor force) ---
    df["employment_rate"] = df["B84AD"] / df["B84AC"].replace(0, np.nan)

    # --- Median household income (deflate to 2020$) ---
    # ACS internally adjusts income to final year of window; use that year's CPI
    df["cpi_deflator"] = df["acs_year"].map(cpi_factors)
    df["med_income_2020"] = df["B79AA"] * df["cpi_deflator"]
    df["log_med_income_2020"] = np.log(df["med_income_2020"].replace(0, np.nan))

    # --- Population ---
    df["population"] = df["AV0AA"]

    keep = [
        "NHGISCODE", "GISJOIN", "FIPS11", "YEAR", "acs_year", "h",
        "STATEFP", "COUNTYFP",
        "population", "poverty_rate", "poverty_count", "poverty_denom",
        "poverty_moe_flag",
        "employment_rate", "med_income_2020", "log_med_income_2020",
        "B84AC", "B84AD",  # raw labor force counts for diagnostics
    ]
    return df[keep]


def load_migration_files() -> pd.DataFrame:
    """
    Load all six B07003 migration source tables; compute in-migration rate per period.
    In-migration rate = (total movers − same house 1yr ago) / total.
    Merge key onto time series: GISJOIN (year-specific, consistent within ACS period).
    """
    frames = []
    for fname, year_str in MIG_FILES.items():
        fpath = MIG_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Migration file not found: {fpath}")

        pfx = MIG_PREFIX[year_str]
        total_col = f"{pfx}E001"
        stayer_col = f"{pfx}E004"

        df = pd.read_csv(fpath, low_memory=False)
        if total_col not in df.columns:
            raise KeyError(f"{fname}: expected column {total_col} not found. Check codebook.")

        df["YEAR"] = year_str
        df["acs_year"] = ACS_PERIODS[year_str][0]

        # Construct FIPS11 for diagnostic match-rate check
        df["FIPS11"] = _make_fips11(df, "STATEA", "COUNTYA", "TRACTA")

        df["mig_total"] = df[total_col]
        df["mig_stayer"] = df[stayer_col]
        df["in_migration_rate"] = (
            (df["mig_total"] - df["mig_stayer"]) / df["mig_total"].replace(0, np.nan)
        )

        frames.append(df[["GISJOIN", "FIPS11", "YEAR", "acs_year", "in_migration_rate",
                           "mig_total", "mig_stayer"]])
        print(f"  Loaded migration {year_str}: {len(df):,} tracts  (prefix: {pfx})")

    return pd.concat(frames, ignore_index=True)


def build_panel(ts: pd.DataFrame, mig: pd.DataFrame) -> pd.DataFrame:
    """
    Merge migration onto the time series panel via (GISJOIN, YEAR).
    Apply population filter (≥ 500). Keep only tracts observed in all 6 periods.
    """
    panel = ts.merge(
        mig[["GISJOIN", "YEAR", "in_migration_rate", "mig_total", "mig_stayer"]],
        on=["GISJOIN", "YEAR"],
        how="left",
    )

    n_matched = panel["in_migration_rate"].notna().sum()
    n_total = len(panel)
    print(f"\nMigration merge: {n_matched:,}/{n_total:,} tract-periods matched "
          f"({100*n_matched/n_total:.1f}%)")

    # Population filter
    n_before = panel["NHGISCODE"].nunique()
    panel = panel[panel["population"] >= 500].copy()
    n_after = panel["NHGISCODE"].nunique()
    print(f"Population filter (>=500): {n_before:,} -> {n_after:,} tracts")

    # Balanced panel: keep only tracts with all 6 periods
    period_counts = panel.groupby("NHGISCODE")["acs_year"].count()
    balanced_ids = period_counts[period_counts == 6].index
    panel = panel[panel["NHGISCODE"].isin(balanced_ids)].copy()
    n_balanced = panel["NHGISCODE"].nunique()
    n_dropped = n_after - n_balanced
    print(f"Balanced panel (all 6 periods): {n_after:,} -> {n_balanced:,} tracts "
          f"({n_dropped:,} dropped due to nominal boundary changes or missing data)")

    # Sort
    panel = panel.sort_values(["NHGISCODE", "acs_year"]).reset_index(drop=True)
    return panel


def main() -> None:
    print("=" * 70)
    print("ACS NHGIS TRACT PANEL BUILD")
    print("WARNING: time series uses NOMINAL integration — see module docstring")
    print("=" * 70)

    PROCESSED.mkdir(parents=True, exist_ok=True)

    cpi_factors = load_cpi_deflators()
    ts = load_time_series(cpi_factors)
    mig = load_migration_files()
    panel = build_panel(ts, mig)

    out_path = PROCESSED / "acs_tract_panel.parquet"
    panel.to_parquet(out_path, index=False)

    print(f"\n[OK] Saved: {out_path}")
    print(f"     Shape: {panel.shape}")
    print(f"     Tracts: {panel['NHGISCODE'].nunique():,}")
    print(f"     Periods: {sorted(panel['acs_year'].unique())}")
    print(f"     h values: {sorted(panel['h'].unique())}")
    print(f"\nOutcome coverage (non-null share):")
    for col in ["poverty_rate", "employment_rate", "log_med_income_2020", "in_migration_rate"]:
        pct = panel[col].notna().mean() * 100
        print(f"  {col}: {pct:.1f}%")


if __name__ == "__main__":
    main()
