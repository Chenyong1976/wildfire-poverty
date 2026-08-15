# NHGIS Tract-Level ACS Download Guide

**Purpose**: Download all six ACS 5-year extracts at census tract level required to build `analysis_sample_final.parquet` from scratch. Re-downloading everything ensures data quality from a clean source.

**Why NHGIS, not IPUMS microdata**: The study unit is the census tract (~74,000 nationally). IPUMS microdata are individual-level with geography masked below PUMA; they cannot produce tract-level estimates. NHGIS provides pre-tabulated ACS summary tables at tract resolution.

---

## What You Are Downloading

Five ACS 5-year periods, each at census tract geography, four outcome tables each:

| Period label | ACS window | Event-study h | Status |
|---|---|---|---|
| ACS 2010 | 2006–2010 | h = −3 | **Download** |
| ACS 2012 | 2008–2012 | h = −2 | **Download** |
| ACS 2014 | 2010–2014 | h = −1 (reference) | **Download** |
| ACS 2022 | 2018–2022 | h = 0 | **Download** |
| ACS 2023 | 2019–2023 | h = +1 | **Download** |
| ACS 2024 | 2020–2024 | h = +2 | **Download** |

**Note on existing ACS 2014 file**: A previous download exists at `data/raw/acs_extracts/nhgis0008_csv/nhgis0008_ds206_20145_tract.csv`. Re-download fresh to ensure data quality; you can delete or archive the old file after verifying the new extract.

---

## Which Table Type to Use: Time Series Standardized, Not Source Tables

NHGIS provides two table categories:

- **Source Tables**: the standard cross-sectional ACS tables (B17001, B19013, etc.) at their original geography for each release year.
- **Time Series Tables**: NHGIS-constructed harmonized series across years, available in two variants:
  - **Nominal (N)**: original geographic units for each time point — boundaries are NOT harmonized.
  - **Standardized (S)**: data are interpolated via block-level population weights to a consistent set of boundaries across all years.

**Use the Standardized (S) variant of Time Series Tables.** This is essential because census tract boundaries change between decennial censuses. Your study spans ACS 2010 (which uses 2000 tract definitions) through ACS 2024 (which uses 2020 tract definitions). Without harmonization, a GEOID in the 2010 data refers to a different geographic area than the same GEOID in the 2022 data. The standardized series handles this automatically.

In the NHGIS Data Finder, select the **"Time Series Tables"** tab (not "Source Tables"). Filter by the relevant topic, then add the **Standardized (S)** version of each table to your cart.

### Variables to Locate (Search by Topic)

| Outcome | Search term in NHGIS | What to look for |
|---|---|---|
| Poverty rate | `poverty` | "Persons Below Poverty Level" — ACS time series, Standardized (S) |
| Median household income | `median household income` | NHGIS B79 or equivalent — ACS time series, Standardized (S) |
| Employment rate | `employment status` | "Civilian Labor Force / Employment Status" — ACS time series, Standardized (S) |
| Net migration proxy | `geographical mobility` | B07003 equivalent — check availability as time series; see note below |

NHGIS assigns its own table codes to time series tables (e.g., B79, A57). The exact codes visible in the interface change as NHGIS updates its library; identify the correct table by topic label rather than memorizing a code.

**Note on geographical mobility**: The 1-year mobility table (B07003 in cross-sectional ACS) may not have a standardized time series version in NHGIS. Check the Time Series Tables tab with the search term `geographical mobility`. If no standardized version appears, download B07003 as a **Source Table** for each period individually (it uses 2000, 2010, and 2020 tract boundaries respectively — note this limitation in the paper's data section). Because mobility is used only as a descriptive mediator, not a primary outcome, the boundary mismatch is less consequential for this variable than for poverty or income.

**Note on income currency**: Both the cross-sectional B19013 and NHGIS's time series income table report **nominal current-dollar income** — they are not real. Within each ACS 5-year window the Census Bureau CPI-adjusts responses to the final year of the window (so ACS 2022 income is approximately in 2022 dollars, ACS 2014 income in 2014 dollars). Across periods these are incomparable without deflation. The build scripts must CPI-deflate all periods to a common base year (target: 2020 dollars using CPI-U-RS) before running the panel regressions. NHGIS does not perform this step.

---

## Step-by-Step Download Instructions

### Step 1 — Account

Go to **https://data2.nhgis.org/** and log in. If you do not have an account, register at https://uma.pop.umn.edu/nhgis/user/new (free, takes ~2 minutes).

---

### Step 2 — Open the Data Finder

Click **"Get Data"** in the top navigation bar. You will see the NHGIS Data Finder with filter panels on the left.

---

### Step 3 — Navigate to Time Series Tables

In the NHGIS Data Finder, click the **"Time Series Tables"** tab at the top of the main content area (next to "Source Tables" and "GIS Boundary Files"). This switches the view from cross-sectional releases to NHGIS's harmonized time series.

You do not filter by year here — a time series table already contains all available periods. You select the table once, and the download includes every ACS period NHGIS has processed for it.

---

### Step 4 — Set up Extract 1: Poverty, Income, and Employment (Time Series Standardized)

**A. Find and add each table**

Use the search box or the "Topics" filter panel on the left to find each variable. For each, you will see multiple variants listed — select the one marked **"Standardized (S)"** at the **Census Tract** geographic level.

1. Search `poverty` → find the ACS time series for persons or families below poverty level → add the **Standardized (S), Census Tract** version
2. Search `median household income` → find the ACS time series (NHGIS B79 or similar label) → add the **Standardized (S), Census Tract** version
3. Search `employment status` → find the ACS time series for civilian employment → add the **Standardized (S), Census Tract** version

Each added table appears in your Data Cart (top right). You should have 3 time series tables in the cart after this step.

**B. Set geographic filter**

In the left filter panel, confirm **"Census Tract"** is selected under Geographic Levels. If results disappear, the table is not available at tract level as a standardized series — see Troubleshooting below.

**C. Review and submit**

Click **"Data Cart"** (top right) → **"Continue"**. Verify:
- All three tables show as Standardized (S) and Census Tract
- Years listed in the cart show coverage spanning your study period (should include ACS 5-year vintages)

Set format options:
- File format: **CSV**
- Structure: **Comma delimited**

Click **"Submit Extract"**.

---

### Step 5 — Set up Extract 2: Geographical Mobility (Source Table, all six periods)

Because geographical mobility (B07003) may not have a standardized time series at the tract level, download it as a source table for each period individually.

Switch back to the **"Source Tables"** tab.

**A. Set Geographic Level filter**: `Census Tract`

**B. Set Years filter** — check all six periods:
- `2006-2010` (ACS 2010, h = −3)
- `2008-2012` (ACS 2012, h = −2)
- `2010-2014` (ACS 2014, h = −1 reference)
- `2018-2022` (ACS 2022, h = 0)
- `2019-2023` (ACS 2023, h = +1)
- `2020-2024` (ACS 2024, h = +2)

> **If ACS 2020-2024 is not listed**: Download the other five periods now; check back for ACS 2024 when available.

**C. Select table**: Search for `B07003` → select **"Geographical Mobility in the Past Year by Sex for Current Residence"** for each year (6 selections total).

**D. Submit** with CSV format.

> **If B07003 IS available as a time series standardized table**: Add it to Extract 1 instead and skip this extract. Check the Time Series Tables tab first.

---

### Step 6 — ACS 2024 check for time series coverage

NHGIS time series standardized tables may not yet include ACS 2024 (2020–2024), which was released by the Census Bureau in December 2025. When you view the time series extracts, check whether ACS 2024 is included in the downloaded files. If it is absent:

- Download ACS 2024 as a **Source Table** (Source Tables tab → Year: `2020-2024` → tables B17001, B19013, B23025) with geographic level Census Tract.
- ACS 2024 uses 2020 tract boundaries — the same boundary year that the time series standardized tables use as their target geography — so merging is clean.
- Note this in the paper's data section: "ACS 2024 was downloaded as a source table and merged directly with the 2020-standardized time series, as they share the same underlying tract definitions."

---

### Step 7 — Download the files

NHGIS will email you when each extract is ready (usually 5–20 minutes). Return to **"My Extracts"** in your account.

For each completed extract:
1. Click **"Download"**
2. Save the `.zip` file to `data/raw/acs_extracts/`
3. Unzip in place — NHGIS creates a subfolder named `nhgis####_csv/`

**Do not rename the NHGIS folders or files.** The build scripts will use NHGIS naming conventions to identify datasets.

---

### Step 8 — Verify downloads

After unzipping, your `data/raw/acs_extracts/` folder should look like:

```
data/raw/acs_extracts/
├── nhgis####_csv/        ← Extract 1 (Time Series Standardized: poverty, income, employment)
│   ├── nhgis####_ts_geog2010_tract.csv     ← standardized to 2010 tract geography (all ACS periods stacked)
│   │                                           OR separate files per period — check codebook for naming
│   └── nhgis####_*_codebook.txt
├── nhgis####_csv/        ← Extract 2 (Source Tables: B07003 mobility, all 6 periods)
│   ├── nhgis####_ds###_20105_tract.csv     ← ACS 2010 mobility tract (~66k rows)
│   ├── nhgis####_ds###_20125_tract.csv     ← ACS 2012
│   ├── nhgis####_ds###_20145_tract.csv     ← ACS 2014
│   ├── nhgis####_ds###_20225_tract.csv     ← ACS 2022
│   ├── nhgis####_ds###_20235_tract.csv     ← ACS 2023
│   └── nhgis####_ds###_20245_tract.csv     ← ACS 2024 (if available)
└── nhgis####_csv/        ← Extract 3 (if needed: ACS 2024 source tables for poverty/income/employment)
```

The old `nhgis0008_csv/` folder (previous ACS 2014 source-table download) can be deleted once the new extracts pass the verification check below.

**Check 1 — Geography is tract-level:**

```python
import pandas as pd

# For the time series standardized file (adjust filename)
df = pd.read_csv("data/raw/acs_extracts/nhgis####_csv/nhgis####_ts_geog2010_tract.csv",
                 nrows=5, low_memory=False)

print("GEOID length (must be 11 for tract):", df["GEOID"].str.len().unique())
# Should print: [11]
# If 5: county-level data — recheck the Geographic Level filter
```

**Check 2 — Time series file spans all needed years:**

```python
df = pd.read_csv("data/raw/acs_extracts/nhgis####_csv/nhgis####_ts_geog2010_tract.csv",
                 low_memory=False)

print("Unique years:", sorted(df["YEAR"].unique()))
# Should include: 2010, 2012, 2014, 2022, 2023 at minimum
# 2024 may be absent — download separately if so
print("Row count per year:", df.groupby("YEAR").size())
# ~66k–84k rows per year
```

---

## Troubleshooting

**"I can't find the Time Series Tables tab"**  
It appears at the top of the main Data Finder content panel (alongside "Source Tables" and "GIS Files"). If you do not see it, make sure you have navigated to the Data Finder (click "Get Data" in the top navigation bar), not a specific dataset page.

**"Standardized (S) version is not available at Census Tract for a variable"**  
This can occur for mobility (B07003) and occasionally for older ACS periods. For those variables, fall back to Source Tables and download each ACS period separately. The boundary mismatch between periods (see introduction above) then becomes a known limitation to flag in the paper.

**"The time series file has only Nominal (N) version"**  
Do not use the Nominal version for the main analysis — it does not harmonize boundaries. Use it only as a last resort and flag the boundary mismatch explicitly. Nominal is acceptable for ACS 2012, 2014, 2022, 2023 (all on 2010 or 2020 boundaries) but not for ACS 2010 (2000 boundaries), which is the most problematic period.

**"Income table B19013 shows as unavailable at tract level for some years"**  
Substitute **B19013A** (median household income — universe: all households) if B19013 is missing. In the time series context, if the standard income series lacks a particular year, check whether NHGIS includes that year through a different aggregated measure.

**"2020-2024 ACS not listed in the time series standardized table"**  
Download ACS 2024 as a Source Table separately (Source Tables tab → Year: 2020-2024 → B17001, B19013, B23025 at Census Tract). ACS 2024 uses 2020 tract boundaries — the same as the standardized time series target — so the merge is clean.

**"NHGIS extract fails or shows no results"**  
In the Source Tables view, make sure the Geographic Level filter is set to `Census Tract` before selecting years. Some older ACS years show zero results at tract level if the geographic filter defaults to county.

---

## After Downloading

Once all files are unzipped into `data/raw/acs_extracts/`, report back. The next step is to rewrite `code/01_build/` to:

1. Read the NHGIS codebook files to identify the variable column names for each table (NHGIS uses auto-generated codes like `ABGFE001` rather than the Census Bureau's standard names)
2. For the time series standardized files: confirm which ACS periods are included and whether ACS 2024 needs to be appended from a source-table download
3. CPI-deflate median household income to 2020 dollars using CPI-U-RS annual deflators before constructing the panel
4. Merge all six periods into a long panel (tract × period) on the standardized GEOID
5. Spatially join MTBS fire perimeters at tract level to assign treatment
6. Rebuild the never-treated control group with correct smoke buffer exclusion (100 km baseline)

**Estimated download time**: 20–40 minutes (mostly waiting for NHGIS to process extracts).
