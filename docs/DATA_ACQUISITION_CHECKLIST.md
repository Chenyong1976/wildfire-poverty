# Data Acquisition Checklist — Phase 0

**Project**: Wildfire-Poverty Analysis (Census Tract Level)  
**Date**: 2026-08-15 (updated: 2026-08-15 — nominal time series downloaded; standardized re-download pending)  
**Status**: In progress

---

## Priority 1: Critical Data (Required Before Any Analysis)

### 1a. ACS Tract-Level Data (NHGIS — Time Series Standardized)

**Source**: NHGIS (https://data2.nhgis.org/), not IPUMS. IPUMS microdata cannot produce pre-tabulated tract-level estimates; NHGIS provides summary table data with geographic boundary harmonization.

**Why time series standardized**: Tract boundaries changed in 2010 and 2020 decennial censuses. NHGIS Standardized (S) variants interpolate all years to a consistent 2020 geography via block-level population weights. Under nominal (N) integration, 37% of tracts drop from the balanced panel due to boundary changes — non-random attrition that biases the sample toward stable rural areas.

**See `docs/NHGIS_DOWNLOAD_GUIDE.md` for detailed download steps and how to verify S vs N in the NHGIS interface.**

#### Extract 1a-i: Time Series Standardized (S) — PENDING RE-DOWNLOAD

> **Current status**: `data/raw/acs_extracts/nhgis_inc_pov_emp/nhgis0012_ts_nominal_tract.csv` was downloaded as **Nominal (N)** and must be replaced. See "ACTION REQUIRED" section in `docs/NHGIS_DOWNLOAD_GUIDE.md`.

| Period | Window | h | NHGIS Status | Checklist |
|--------|--------|---|--------------|-----------|
| ACS 2010 | 2006–2010 | −3 | Re-download as Standardized (S) | ☐ |
| ACS 2012 | 2008–2012 | −2 | Re-download as Standardized (S) | ☐ |
| ACS 2014 | 2010–2014 | −1 (reference) | Re-download as Standardized (S) | ☐ |
| ACS 2022 | 2018–2022 | 0 | Re-download as Standardized (S) | ☐ |
| ACS 2023 | 2019–2023 | +1 | Re-download as Standardized (S) | ☐ |
| ACS 2024 | 2020–2024 | +2 | Re-download as Standardized (S); check coverage in extract | ☐ |

**Verify after download**: Open the codebook (`.txt` file in the extract zip). It must read `Geographic integration: Standardized`. If it reads `Nominal`, delete and re-download.

**Save to**: `data/raw/acs_extracts/nhgis_inc_pov_emp_std/` (separate from the nominal file)

**After downloading**: Update `TS_FILE` in `code/01_build/01_acs_nhgis_load.py` to point to the new folder; run the build script; migration merge key will automatically shift from GISJOIN to FIPS11.

**Variables (all via time series standardized extract):**
- Poverty rate: NHGIS AX7 or equivalent, Standardized (S), Census Tract
- Median household income: NHGIS B79 or equivalent, Standardized (S), Census Tract (nominal; CPI-U deflation in build script)
- Employment rate: NHGIS B84 or equivalent, Standardized (S), Census Tract
- Population: NHGIS AV0, Standardized (S), Census Tract
- MOE columns included (suffix M); flag but do not drop on 30% count-MOE threshold

#### Extract 1a-ii: Migration Source Tables (B07003) — COMPLETE

| Period | File | Status |
|--------|------|--------|
| ACS 2010 | nhgis0013_ds177_20105_tract.csv | ✓ |
| ACS 2012 | nhgis0013_ds192_20125_tract.csv | ✓ |
| ACS 2014 | nhgis0013_ds207_20145_tract.csv | ✓ |
| ACS 2022 | nhgis0013_ds263_20225_tract.csv | ✓ |
| ACS 2023 | nhgis0013_ds268_20235_tract.csv | ✓ |
| ACS 2024 | nhgis0013_ds273_20245_tract.csv | ✓ |

Migration files do not need to be re-downloaded — they are source tables on year-specific boundaries, which is correct and expected. Merge onto time series via FIPS11 within each period.

**Responsibility**: Manual download from NHGIS (requires free account login)

---

### 1b. Census 2020 Tract Shapefiles (TIGER)

Use **2020 vintage** tract shapefiles to match the NHGIS standardized time series target geography.

| Item | Source | Action | Checklist |
|------|--------|--------|-----------|
| Tract shapefiles 2020 vintage | Census TIGER/GENZ | Download shapefiles for all lower-48 states | ☐ |
| Projection | TIGER files | Verify WGS84 (EPSG:4269 or similar); reproject to EPSG:5070 for raster processing | ☐ |

**URL**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-geodatabase-files.html (2020 vintage)

**Output**: `data/raw/tract_shapefiles/tracts_2020.shp` (plus .shx, .dbf, .prj, etc.)

**Responsibility**: Script-based download (Python `urllib` or `requests`)

---

### 1d. USDA RUCC 2013 (Rural-Urban Continuum Codes)

| Item | Source | Action | Checklist |
|------|--------|--------|-----------|
| RUCC 2013 county codes | USDA ERS | Download 2013 RUCC codes (county-level classification) | ☐ |
| Format | USDA ERS | Likely Excel or CSV; extract county FIPS → RUCC mapping | ☐ |

**URL**: https://www.ers.usda.gov/webdocs/DataFiles/53251/ (RUCC 2013)

**Output**: `data/raw/rucc_2013.csv` (columns: county_fips, rucc_code, rucc_description)

**Responsibility**: Manual download from USDA ERS website; parse into CSV

---

## Priority 2: Verification Data (Quality Checks)

### 2a. MTBS Perimeter Shapefiles

**Status**: Already available at `../../wildfire-finance/data/raw/mtbs_perims/`

**Verification**:
- ☐ Confirm symlink or copy exists in `data/raw/mtbs_perimeters/`
- ☐ Verify 1984–2022 coverage with fires ≥1,000 acres (West) / ≥500 acres (East) documented

---

### 2b. WHP 2012 Raster

**Status**: Already available at `../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`

**Verification**:
- ☐ Confirm symlink or copy exists in `data/raw/whp_rasters/wfp2012_continuous/`
- ☐ Verify 270m resolution, EPSG:5070 projection
- ☐ Confirm release prior to 2013 fire season (predetermined)

---

## Priority 3: Documentation (Data Dictionary)

### 3a. WHP Release Dates & Metadata

Before PAP registration, document:
- [ ] WHP 2012 exact release date (month/year) — confirms predetermined status for 2013+ fires
- [ ] WHP 2012 native resolution, CRS, and data range (WFP percentile 0–100)

**Note**: WHP 2018 is NOT used in the current design (WHP 2012 is the sole matching raster). Remove any prior references to WHP 2018 from code and documentation.

**File**: `docs/DATA_DICTIONARY.md` (section: "WHP Raster Metadata")

---

### 3b. ACS Variables & MOE Availability

Document:
- [ ] NHGIS auto-generated column codes for each outcome in the time series standardized extract (read from codebook files shipped with each NHGIS extract)
- [ ] Whether MOE columns are included in the standardized time series files (they may or may not be)
- [x] CPI-U (CPIAUCSL) downloaded from FRED (`data/raw/CPIAUCSL.csv`); annual averages to be computed in build script
- [ ] B07003 column codes from the source-table mobility extract
- [ ] Confirmation that coverage spans all six periods (2010, 2012, 2014, 2022, 2023, 2024)

**File**: `docs/DATA_DICTIONARY.md` (section: "ACS Variables & MOE")

---

## Download Instructions (Manual Steps)

**Primary reference**: `docs/NHGIS_DOWNLOAD_GUIDE.md` — follow that guide for all ACS data. The steps below summarize the non-ACS downloads.

### Step 1: NHGIS ACS Extracts

See `docs/NHGIS_DOWNLOAD_GUIDE.md` for the complete step-by-step process. Summary:
- Extract 1 (Time Series Tables tab): poverty, income, employment — Standardized (S), Census Tract
- Extract 2 (Source Tables tab): B07003 mobility — Census Tract, all 6 ACS periods
- Extract 3 (if needed): ACS 2024 source tables for poverty/income/employment if not in time series extract

---

### Step 2: Census 2020 Tract Shapefiles

1. Visit Census TIGER: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html
2. Select year: **2020**
3. Select layer: **Tract**
4. Select geography: **Cartographic Boundary Shapefile** (500k resolution)
5. Download for each state or national zipped file
6. Extract to `data/raw/tract_shapefiles/tracts_2020/`

---

### Step 3: USDA RUCC 2013

1. Visit USDA ERS: https://www.ers.usda.gov/
2. Navigate to Rural-Urban Continuum Codes (RUCC)
3. Download **2013 RUCC** file (Excel or CSV)
4. Open in spreadsheet or text editor
5. Extract county FIPS → RUCC mapping
6. Save as CSV to `data/raw/rucc_2013.csv`

---

## Post-Download Verification

After all downloads complete:

### Integrity Checks

- [ ] Each CSV file has expected columns (state FIPS, county FIPS, tract FIPS, outcome variables, MOE)
- [ ] No obvious data corruption (e.g., all zeros, NaN, or missing values for entire columns)
- [ ] NHGIS time series standardized file spans all six ACS periods (check YEAR column)
- [ ] B07003 source-table extract has six tract-level files (one per ACS period)
- [ ] ACS 2024 coverage confirmed or flagged as separate source-table download
- [ ] Tract shapefiles have 11-digit GEOID

### File Size Sanity Checks

- [ ] NHGIS time series standardized CSV: ~400–600 MB (all periods stacked, ~74k–84k tracts × 6 periods)
- [ ] B07003 source table CSVs: ~150–250 MB each × 6 files
- [ ] Census 2020 tract shapefiles: ~150–250 MB (uncompressed)

---

## Timeline

| Task | Week | Owner | Status |
|------|------|-------|--------|
| Download NHGIS time series standardized extracts (poverty, income, employment) | Week 1 | User (manual, data2.nhgis.org) | ☐ |
| Download NHGIS B07003 source tables (mobility, all 6 periods) | Week 1 | User (manual, data2.nhgis.org) | ☐ |
| Download ACS 2024 source tables if absent from time series extract | Week 1 | User (manual, data2.nhgis.org) | ☐ |
| Download MTBS fire perimeters 1984–2023 | Week 1 | User (manual, USGS) | ☐ |
| Download Census 2020 tract shapefiles | Week 1 | User (manual, Census TIGER) | ☐ |
| Download USDA RUCC 2013 | Week 1 | User (manual, USDA ERS) | ☐ |
| Verify all downloads + document NHGIS column codes from codebook | Week 2 | Code review | ☐ |
| Update `docs/DATA_DICTIONARY.md` with WHP/ACS/CPI deflator metadata | Week 2 | Documentation | ☐ |
| PAP registration | Week 2 | User | ☐ |

---

## Notes

- **ACS data source is NHGIS, not IPUMS**: Use time series standardized (S) tables from NHGIS for all ACS outcome variables. IPUMS microdata cannot produce pre-tabulated tract-level summary statistics and should not be used for this project's primary data assembly.
- **ACS 2024 availability on NHGIS**: Confirm whether NHGIS time series standardized tables include ACS 2024 (2020–2024). If absent, download as a source table — ACS 2024 uses 2020 boundaries (same as standardized target), so the merge is clean.
- **WHP 2018 is NOT used**: The current design uses only WHP 2012 as the predetermined matching raster. Do not download WHP 2018.
- **Income CPI deflation**: Median household income in NHGIS is nominal. Deflate to 2020 dollars using **CPI-U annual averages** (FRED CPIAUCSL; `data/raw/CPIAUCSL.csv`) in `code/01_build/`. Use the final year of each ACS window as the deflation year (e.g., 2022 for ACS 2018–2022). Record deflator values in `docs/DATA_DICTIONARY.md`.
- **Symlink vs. copy**: For MTBS and WHP 2012 (already in wildfire-finance), create symlinks rather than copies to avoid duplication:
  ```bash
  ln -s ../../wildfire-finance/data/raw/mtbs_perims data/raw/mtbs_perimeters
  ln -s ../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous data/raw/whp_2012_continuous
  ```
