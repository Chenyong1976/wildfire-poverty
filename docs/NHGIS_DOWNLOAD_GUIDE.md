# NHGIS Tract-Level ACS Download Guide

**Purpose**: Download all six ACS 5-year extracts at census tract level required to build `analysis_sample_final.parquet` from scratch. Re-downloading everything ensures data quality from a clean source.

**Why NHGIS, not IPUMS microdata**: The study unit is the census tract (~74,000 nationally). IPUMS microdata are individual-level with geography masked below PUMA; they cannot produce tract-level estimates. NHGIS provides pre-tabulated ACS summary tables at tract resolution.

---

## Boundary Harmonization: Why Nominal (N) Is the Correct Download

**The current time series file (`nhgis0012_ts_nominal_tract.csv`) is correct and does not need to be re-downloaded.**

NHGIS offers two time series integration methods:
- **Nominal (N)**: links tracts by their name/code across years; does not adjust for boundary changes.
- **Standardized (S)**: interpolates data to a consistent boundary using block-level population weights.

For **ACS data at the census tract level, Standardized (S) tables do not exist**. NHGIS only offers standardized integration for decennial census data (1990/2000/2010/2020). The nominal series is the only ACS option.

**How the nominal balanced panel addresses the boundary problem**: By restricting to tracts that appear in all six ACS periods, we retain only tracts whose code was in use consistently across the 2000, 2010, and 2020 boundary vintages. Tracts dropped from the balanced panel are those that were split, merged, or renumbered at a decennial boundary change. The current balanced panel retains ~60,000–70,000 tracts from ~97,000 with at least one period. Western rural tracts — where fires predominantly occur — have low boundary-change rates, so treated-tract retention is expected to be high.

**If nominal balanced panel is inadequate** (determined by diagnostic after fire treatment assignment — see RESEARCH_PLAN.md §2): Apply the Census Bureau's 2010–2020 Tract Relationship File (`tab20_tract20_tract10_natl.zip`) to aggregate ACS 2022/2023/2024 counts from 2020 boundaries to 2010 definitions. Download from: https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html

---

## What You Are Downloading

Four outcome tables (poverty, income, employment, population) as Nominal (N) time series at Census Tract — the only ACS option. Migration as source tables (one file per period). Both downloads are **complete**.

| Period label | ACS window | Event-study h | Tract boundary vintage | Status |
|---|---|---|---|---|
| ACS 2010 | 2006–2010 | h = −3 (auxiliary pre-trend) | 2000 | ✓ complete |
| ACS 2012 | 2008–2012 | h = −2 (primary pre-trend) | 2010 | ✓ complete |
| ACS 2014 | 2010–2014 | h = −1 (reference) | 2010 | ✓ complete |
| ACS 2022 | 2018–2022 | h = 0 | 2020 | ✓ complete |
| ACS 2023 | 2019–2023 | h = +1 | 2020 | ✓ complete |
| ACS 2024 | 2020–2024 | h = +2 | 2020 | ✓ complete |

**h = −3 note**: ACS 2010 uses 2000-vintage boundaries. In the nominal balanced panel, h = −3 is retained only for tracts consistent across all three decennial definitions. Treat h = −3 as an auxiliary pre-trend check; the two primary pre-trend tests are h = −2 and h = −1 (both on 2010 boundaries).

Migration source tables (B07003) — all six periods complete in `data/raw/acs_extracts/nhgis_mig/`.

---

## Which Table Type to Use: Nominal (N) — the Only ACS Option

NHGIS provides two table categories:

- **Source Tables**: standard cross-sectional ACS tables at their original geography for each release year.
- **Time Series Tables**: NHGIS-constructed series across years, in two variants:
  - **Nominal (N)**: original geographic units per time point — boundaries are NOT harmonized.
  - **Standardized (S)**: interpolated to consistent boundaries via block-level population weights.

**For ACS data at the census tract level, Standardized (S) is not available.** NHGIS only offers standardized integration for decennial census data (1990/2000/2010/2020). The Nominal (N) time series is the correct and only ACS option. Boundary consistency is handled by restricting to a balanced panel of tracts present in all six periods — see RESEARCH_PLAN.md §2 for the full boundary harmonization strategy and fallback crosswalk.

In the NHGIS Data Finder, select the **"Time Series Tables"** tab. Filter by topic, then add the **Nominal (N), Census Tract** variant.

### Variables to Locate (Search by Topic)

| Outcome | Search term in NHGIS | What to look for |
|---|---|---|
| Poverty rate | `poverty` | "Persons Below Poverty Level" — ACS time series, **Nominal (N)**, Census Tract |
| Median household income | `median household income` | NHGIS B79 or equivalent — ACS time series, **Nominal (N)**, Census Tract |
| Employment rate | `employment status` | "Civilian Labor Force / Employment Status" — ACS time series, **Nominal (N)**, Census Tract |
| Net migration proxy | `geographical mobility` | B07003 — download as source table (not time series); see merge note below |

NHGIS assigns its own table codes to time series tables (e.g., B79, A57). The exact codes visible in the interface change as NHGIS updates its library; identify the correct table by topic label rather than memorizing a code.

**Note on geographical mobility — merge strategy (standardized time series)**: B07003 (1-year geographical mobility by sex) has been downloaded as source tables for all six periods (`data/raw/acs_extracts/nhgis_mig/nhgis0013_ds*_tract.csv`). These source tables use year-specific tract boundaries (2000 vintage for ACS 2010; 2010 vintage for ACS 2012/2014; 2020 vintage for ACS 2022/2023/2024). The standardized time series, by contrast, places all periods on 2020 boundaries. Because the two files use **different boundary vintages for pre-treatment periods**, you cannot merge via `GISJOIN` — GISJOINs reference different geographic definitions.

**Use FIPS11 as the within-year merge key:**
1. In the standardized time series file: construct `FIPS11 = STATEFP.zfill(2) + COUNTYFP.zfill(3) + TRACTA.zfill(6)`
2. In each migration file: construct `FIPS11 = STATEA.zfill(2) + COUNTYA.zfill(3) + TRACTA.zfill(6)`
3. Merge on `(FIPS11, YEAR)` within each ACS period

Expected match rates: ACS 2022/2023/2024 will match nearly perfectly (both on 2020 boundaries). ACS 2010/2012/2014 will have some unmatched tracts where boundaries changed between the migration file's vintage and 2020. Document the match rate by period; accept unmatched rows as missing for migration (descriptive mediator, not primary outcome).

Variable prefix lookup (verified from codebooks):

| ACS period | NHGIS code | Total | Same house | In-migration formula |
|---|---|---|---|---|
| 2006–2010 | JXZ | JXZE001 | JXZE004 | (JXZE001 − JXZE004) / JXZE001 |
| 2008–2012 | Q4P | Q4PE001 | Q4PE004 | (Q4PE001 − Q4PE004) / Q4PE001 |
| 2010–2014 | ABND | ABNDE001 | ABNDE004 | (ABNDE001 − ABNDE004) / ABNDE001 |
| 2018–2022 | AQ0Z | AQ0ZE001 | AQ0ZE004 | (AQ0ZE001 − AQ0ZE004) / AQ0ZE001 |
| 2019–2023 | AS1T | AS1TE001 | AS1TE004 | (AS1TE001 − AS1TE004) / AS1TE001 |
| 2020–2024 | AU24 | AU24E001 | AU24E004 | (AU24E001 − AU24E004) / AU24E001 |

**Note on income currency**: Both the cross-sectional B19013 and NHGIS's time series income table report **nominal current-dollar income** — they are not real. Within each ACS 5-year window the Census Bureau CPI-adjusts responses to the **final year** of the window (so ACS 2022 income is approximately in 2022 dollars, ACS 2014 income in 2014 dollars). Across periods these are incomparable without deflation. The build scripts must deflate all periods to a common base year (2020 dollars) using **CPI-U annual averages** (FRED series CPIAUCSL; `data/raw/CPIAUCSL.csv`). Annual average CPI-U values (key years): 2010 = 218.1, 2012 = 229.6, 2014 = 236.7 (reference), 2022 = 292.6, 2023 = 304.7, 2024 = 313.7, 2020 = 258.9 (base). Deflation factor = 258.9 / [final-year CPI]. NHGIS does not perform this step.

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
3. Compute annual average CPI-U from `data/raw/CPIAUCSL.csv` (monthly → annual mean); deflate median household income to 2020 dollars using the final-year CPI of each ACS window
4. Merge all six periods into a long panel (tract × period) on the standardized GEOID
5. Spatially join MTBS fire perimeters at tract level to assign treatment
6. Rebuild the never-treated control group with correct smoke buffer exclusion (100 km baseline)

**Estimated download time**: 20–40 minutes (mostly waiting for NHGIS to process extracts).
