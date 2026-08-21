# -*- coding: utf-8 -*-
"""
Build mechanism-analysis variables panel.

Sources:
  data/raw/MigrantByAgeRaceIncPov/  -- B07002, B07004A, B07004B, B07011, B07012
  data/raw/HousingRentValue/         -- B25064, B25077

Boundary harmonization:
  Pre-treatment (2010, 2012, 2014): GISJOIN is 2010-vintage; rename to NHGISCODE.
  Post-treatment (2022, 2023, 2024): GISJOIN is 2020-vintage; apply area-weighted
    crosswalk (data/raw/nhgis_blk2010_tr2020/nhgis_blk2010_tr2020.csv) to 2010-vintage.
  Counts: weighted sum (exact).
  Medians: area-weighted mean across child 2020 tracts (approximation; noted in paper).

Output: data/processed/mechanism_vars_panel.parquet
"""

import sys, io
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT     = Path(__file__).resolve().parents[2]
RAW      = ROOT / "data" / "raw"
PROC     = ROOT / "data" / "processed"
MIG_DIR  = RAW / "MigrantByAgeRaceIncPov"
HOUS_DIR = RAW / "HousingRentValue"
XWALK_CSV = RAW / "nhgis_blk2010_tr2020" / "nhgis_blk2010_tr2020.csv"

LOWER_48 = {
    "01","04","05","06","08","09","10","11","12","13","16","17","18","19","20",
    "21","22","23","24","25","26","27","28","29","30","31","32","33","34","35",
    "36","37","38","39","40","41","42","44","45","46","47","48","49","50","51",
    "53","54","55","56",
}

# Per-year NHGIS variable code prefixes (from codebooks)
# Order: (b07002, b07004a_white, b07004b_black, b07011, b07012)
MIG_SPECS = [
    {"acs_year":2010,"vintage":"pre", "file":"nhgis0015_ds177_20105_tract.csv",
     "p02":"JXX","p4a":"JX1","p4b":"JX3","p11":"JYR","p12":"JYT"},
    {"acs_year":2012,"vintage":"pre", "file":"nhgis0015_ds192_20125_tract.csv",
     "p02":"Q4N","p4a":"Q4R","p4b":"Q4T","p11":"Q5H","p12":"Q5J"},
    {"acs_year":2014,"vintage":"pre", "file":"nhgis0015_ds207_20145_tract.csv",
     "p02":"ABNB","p4a":"ABNF","p4b":"ABNH","p11":"ABN5","p12":"ABN7"},
    {"acs_year":2022,"vintage":"post","file":"nhgis0015_ds263_20225_tract.csv",
     "p02":"AQ0X","p4a":"AQ01","p4b":"AQ03","p11":"AQ1R","p12":"AQ1T"},
    {"acs_year":2023,"vintage":"post","file":"nhgis0015_ds268_20235_tract.csv",
     "p02":"AS1R","p4a":"AS1V","p4b":"AS1X","p11":"AS2L","p12":"AS2N"},
    {"acs_year":2024,"vintage":"post","file":"nhgis0015_ds273_20245_tract.csv",
     "p02":"AU22","p4a":"AU26","p4b":"AU28","p11":"AU3W","p12":"AU3Y"},
]

HOUS_SPECS = [
    {"acs_year":2010,"vintage":"pre", "file":"nhgis0016_ds176_20105_tract.csv","rent":"JS5", "val":"JTI"},
    {"acs_year":2012,"vintage":"pre", "file":"nhgis0016_ds191_20125_tract.csv","rent":"QZT", "val":"QZ6"},
    {"acs_year":2014,"vintage":"pre", "file":"nhgis0016_ds206_20145_tract.csv","rent":"ABIH","val":"ABIT"},
    {"acs_year":2022,"vintage":"post","file":"nhgis0016_ds262_20225_tract.csv","rent":"AQUS","val":"AQU4"},
    {"acs_year":2023,"vintage":"post","file":"nhgis0016_ds267_20235_tract.csv","rent":"ASVB","val":"ASVN"},
    {"acs_year":2024,"vintage":"post","file":"nhgis0016_ds272_20245_tract.csv","rent":"AUWG","val":"AUWS"},
]


def build_crosswalk() -> pd.DataFrame:
    """Aggregate block-level crosswalk to (tr2020gj, tr2010gj, weight) pairs."""
    print(f"Loading crosswalk: {XWALK_CSV.name} ...", flush=True)
    xw = pd.read_csv(XWALK_CSV, usecols=["blk2010gj","tr2020gj","weight"],
                     dtype={"blk2010gj":str,"tr2020gj":str,"weight":float})
    xw["tr2010gj"] = xw["blk2010gj"].str[:14]
    xw = xw[xw["tr2010gj"].str[1:3].isin(LOWER_48)].copy()
    tw = (xw.groupby(["tr2020gj","tr2010gj"])["weight"]
            .sum().reset_index(name="wt"))
    tot = tw.groupby("tr2020gj")["wt"].transform("sum")
    tw["wt"] = tw["wt"] / tot.replace(0, np.nan)
    tw = tw.dropna(subset=["wt"])
    print(f"  Tract crosswalk: {tw['tr2020gj'].nunique():,} 2020-tracts → {tw['tr2010gj'].nunique():,} 2010-tracts")
    return tw


def clean_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Coerce to numeric; replace ACS suppression code (-666666666 etc.) with NaN."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            df[c] = df[c].where(df[c] > -500000, np.nan)
    return df


def crosswalk_counts(df: pd.DataFrame, count_cols: list, tw: pd.DataFrame,
                     yr: int) -> pd.DataFrame:
    """Weighted sum of count variables: 2020-vintage → 2010-vintage."""
    m = df.merge(tw.rename(columns={"tr2020gj":"GISJOIN"}), on="GISJOIN", how="left")
    for c in count_cols:
        m[c] = m[c].fillna(0) * m["wt"]
    return (m.groupby("tr2010gj")[count_cols].sum()
             .reset_index().rename(columns={"tr2010gj":"NHGISCODE"})
             .assign(acs_year=yr))


def crosswalk_medians(df: pd.DataFrame, median_cols: list, tw: pd.DataFrame,
                      yr: int) -> pd.DataFrame:
    """Area-weighted mean of median variables: 2020-vintage → 2010-vintage (approx)."""
    m = df.merge(tw.rename(columns={"tr2020gj":"GISJOIN"}), on="GISJOIN", how="left")
    agg = m[["tr2010gj"]].copy()
    for c in median_cols:
        w = m["wt"].where(m[c].notna(), 0.0)
        num = m[c].fillna(0.0) * w
        tmp = pd.DataFrame({"tr2010gj": m["tr2010gj"], "_n": num, "_d": w})
        s = tmp.groupby("tr2010gj")[["_n","_d"]].sum()
        agg[c] = agg["tr2010gj"].map(s["_n"] / s["_d"].replace(0, np.nan))
    return (agg.drop_duplicates("tr2010gj")
               .rename(columns={"tr2010gj":"NHGISCODE"})
               .assign(acs_year=yr))


def load_mig(spec: dict, tw: pd.DataFrame) -> pd.DataFrame:
    p02=spec["p02"]; p4a=spec["p4a"]; p4b=spec["p4b"]
    p11=spec["p11"]; p12=spec["p12"]; yr=spec["acs_year"]

    # Columns: B07002 E001,E002,E004,E005 (median age total/stayer/diffcounty/diffstate)
    #          B07004A E001,E002,E004,E005,E006 (White total/stayer/diffcounty/diffstate/abroad)
    #          B07004B same for Black
    #          B07011 E001,E002,E004,E005 (median income total/stayer/diffcounty/diffstate)
    #          B07012 E013,E014,E017,E018 (outside-county movers total/poor + outside-state)
    want = (
        [f"{p02}E00{i}" for i in [1,2,4,5]] +
        [f"{p4a}E00{i}" for i in [1,2,4,5,6]] +
        [f"{p4b}E00{i}" for i in [1,2,4,5,6]] +
        [f"{p11}E00{i}" for i in [1,2,4,5]] +
        [f"{p12}E0{n}" for n in ["13","14","17","18"]]
    )
    all_cols = ["GISJOIN"] + want
    df = pd.read_csv(MIG_DIR / spec["file"],
                     usecols=lambda c: c in set(all_cols), low_memory=False)
    df = df[df["GISJOIN"].str[1:3].isin(LOWER_48)].copy()
    df = clean_numeric(df, want)

    count_cols  = [f"{p4a}E00{i}" for i in [1,2,4,5,6]] + \
                  [f"{p4b}E00{i}" for i in [1,2,4,5,6]] + \
                  [f"{p12}E0{n}"  for n in ["13","14","17","18"]]
    median_cols = [f"{p02}E00{i}" for i in [1,2,4,5]] + \
                  [f"{p11}E00{i}" for i in [1,2,4,5]]

    if spec["vintage"] == "pre":
        df = df.rename(columns={"GISJOIN":"NHGISCODE"}).assign(acs_year=yr)
        out = df[["NHGISCODE","acs_year"] + count_cols + median_cols]
    else:
        ct  = crosswalk_counts( df[["GISJOIN"]+count_cols].copy(),  count_cols,  tw, yr)
        med = crosswalk_medians(df[["GISJOIN"]+median_cols].copy(), median_cols, tw, yr)
        out = ct.merge(med, on=["NHGISCODE","acs_year"], how="outer")

    # Rename to semantic names
    rn = {
        f"{p02}E001": "med_age_total",     f"{p02}E002": "med_age_stayer",
        f"{p02}E004": "med_age_diffcounty",f"{p02}E005": "med_age_diffstate",
        f"{p4a}E001": "white_total",        f"{p4a}E002": "white_stayer",
        f"{p4a}E004": "white_in_diffcounty",f"{p4a}E005": "white_in_diffstate",
        f"{p4a}E006": "white_in_abroad",
        f"{p4b}E001": "black_total",        f"{p4b}E002": "black_stayer",
        f"{p4b}E004": "black_in_diffcounty",f"{p4b}E005": "black_in_diffstate",
        f"{p4b}E006": "black_in_abroad",
        f"{p11}E001": "med_inc_total",      f"{p11}E002": "med_inc_stayer",
        f"{p11}E004": "med_inc_diffcounty", f"{p11}E005": "med_inc_diffstate",
        f"{p12}E013": "inmov_county_total", f"{p12}E014": "inmov_county_poor",
        f"{p12}E017": "inmov_state_total",  f"{p12}E018": "inmov_state_poor",
    }
    out = out.rename(columns={k:v for k,v in rn.items() if k in out.columns})
    print(f"  {yr}: {out['NHGISCODE'].nunique():,} tracts")
    return out.reset_index(drop=True)


def load_hous(spec: dict, tw: pd.DataFrame) -> pd.DataFrame:
    r=spec["rent"]; v=spec["val"]; yr=spec["acs_year"]
    rc=f"{r}E001"; vc=f"{v}E001"
    df = pd.read_csv(HOUS_DIR / spec["file"], usecols=["GISJOIN",rc,vc], low_memory=False)
    df = df[df["GISJOIN"].str[1:3].isin(LOWER_48)].copy()
    df = clean_numeric(df, [rc,vc])
    # Positive values only for rent and home value
    for c in [rc,vc]:
        df[c] = df[c].where(df[c] > 0, np.nan)

    if spec["vintage"] == "pre":
        df = df.rename(columns={"GISJOIN":"NHGISCODE",rc:"med_gross_rent",vc:"med_home_value"})
        df["acs_year"] = yr
    else:
        med = crosswalk_medians(df[["GISJOIN",rc,vc]].copy(), [rc,vc], tw, yr)
        med = med.rename(columns={rc:"med_gross_rent",vc:"med_home_value"})
        df = med
    df["log_home_value"] = np.log(df["med_home_value"].clip(lower=1))
    print(f"  {yr}: {df['NHGISCODE'].nunique():,} housing tracts")
    return df[["NHGISCODE","acs_year","med_gross_rent","log_home_value"]]


def compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    # Outside-county in-migration rates by race
    for race, prefix in [("white","white"), ("black","black")]:
        inn = (df.get(f"{prefix}_in_diffcounty", pd.Series(0,index=df.index)).fillna(0) +
               df.get(f"{prefix}_in_diffstate",  pd.Series(0,index=df.index)).fillna(0) +
               df.get(f"{prefix}_in_abroad",      pd.Series(0,index=df.index)).fillna(0))
        df[f"{race}_inmig_rate"] = inn / df[f"{race}_total"].replace(0, np.nan)

    # Poverty rate among outside-county + outside-state movers (B07012)
    inmov_tot  = (df.get("inmov_county_total",pd.Series(0,index=df.index)).fillna(0) +
                  df.get("inmov_state_total", pd.Series(0,index=df.index)).fillna(0))
    inmov_poor = (df.get("inmov_county_poor", pd.Series(0,index=df.index)).fillna(0) +
                  df.get("inmov_state_poor",  pd.Series(0,index=df.index)).fillna(0))
    df["inmov_total"]        = inmov_tot
    df["inmov_poor"]         = inmov_poor
    df["inmov_poverty_rate"] = inmov_poor / inmov_tot.replace(0, np.nan)
    return df


def main():
    print("Building mechanism variables panel ...")
    tw = build_crosswalk()

    print("\nMobility tables:")
    mig = pd.concat([load_mig(s, tw) for s in MIG_SPECS], ignore_index=True)
    mig = compute_derived(mig)

    print("\nHousing tables:")
    hous = pd.concat([load_hous(s, tw) for s in HOUS_SPECS], ignore_index=True)

    panel = mig.merge(hous, on=["NHGISCODE","acs_year"], how="outer")
    panel = panel[panel["NHGISCODE"].str[1:3].isin(LOWER_48)].copy()

    out = PROC / "mechanism_vars_panel.parquet"
    panel.to_parquet(out, index=False)
    print(f"\nSaved: {out}")
    print(f"  Shape: {panel.shape}  |  Unique tracts: {panel['NHGISCODE'].nunique():,}")
    print(f"  Years: {sorted(panel['acs_year'].unique())}")
    print(f"  Columns: {[c for c in panel.columns if c not in ('NHGISCODE','acs_year')]}")


if __name__ == "__main__":
    main()
