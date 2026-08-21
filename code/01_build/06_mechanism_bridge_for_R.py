# -*- coding: utf-8 -*-
"""
Export mechanism_vars_panel.parquet as CSV for R consumption.
Merges with fire treatment (treated, never_treated, COUNTYFP10).

Output: data/processed/mechanism_panel_for_R.csv
"""

import sys
import io
from pathlib import Path
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"

mech = pd.read_parquet(PROC / "mechanism_vars_panel.parquet")
fire = pd.read_parquet(
    PROC / "fire_treatment_tracts.parquet",
    columns=["GISJOIN", "treated", "never_treated", "COUNTYFP10"],
)

df = mech.merge(fire, left_on="NHGISCODE", right_on="GISJOIN", how="left")
df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()
df = df.drop(columns=["GISJOIN"])

out = PROC / "mechanism_panel_for_R.csv"
df.to_csv(out, index=False)

n_t = (df[df["acs_year"] == 2022]["treated"] == 1).sum()
n_c = (df[df["acs_year"] == 2022]["never_treated"] == 1).sum()
print(f"Saved: {out}")
print(f"  {len(df):,} rows x {df.shape[1]} cols")
print(f"  Treated tracts (2022): {n_t}")
print(f"  Control tracts (2022): {n_c}")
print(f"  Outcomes: {[c for c in df.columns if c not in ('NHGISCODE','acs_year','treated','never_treated','COUNTYFP10')]}")
