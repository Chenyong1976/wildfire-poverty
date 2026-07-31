# Data Acquisition Checklist — Phase 0

**Project**: Wildfire-Poverty Analysis (Census Tract Level)  
**Date**: 2026-07-31  
**Status**: In progress

---

## Priority 1: Critical Data (Required Before Any Analysis)

### 1a. ACS 5-year Tract-Level Extracts (IPUMS)

| Period | Window | IPUMS Status | Action Required | Checklist |
|--------|--------|--------------|-----------------|-----------|
| ACS 2012 | 2008–2012 | Must extract | Download tract-level extract from IPUMS | ☐ |
| ACS 2017 | 2013–2017 | Must extract | Download tract-level extract from IPUMS | ☐ |
| ACS 2023 | 2019–2023 | Must extract | Download tract-level extract from IPUMS; **confirm availability (released Dec 2024)** | ☐ |

**Variables to extract** (all three periods):
- `B17001`: Poverty status
- `B19013`: Median household income
- `B23025`: Employment status
- `B07001`: Residence 5 years ago (net migration proxy)
- Margins of error (MOE) for all above
- State FIPS, County FIPS, Tract FIPS (to construct 11-digit GEOID)

**Geographic level**: **Tract** (not county); filter to lower-48 US states (exclude AK, HI, PR)

**Output**: Three CSV files
- `data/raw/acs_extracts/acs_2012_tract_extract.csv` (2008–2012 window)
- `data/raw/acs_extracts/acs_2017_tract_extract.csv` (2013–2017 window)
- `data/raw/acs_extracts/acs_2023_tract_extract.csv` (2019–2023 window)

**Responsibility**: Manual download from IPUMS (requires account login)

---

### 1b. WHP 2018 Raster (USFS LANDFIRE)

| Item | Source | Action | Checklist |
|------|--------|--------|-----------|
| WHP 2018 GeoTIFF | USFS LANDFIRE portal | Download 270m resolution raster for lower-48 US | ☐ |
| WHP 2018 metadata | USFS LANDFIRE | Confirm release date (must be before 2019 fire season for predetermined status) | ☐ |
| CRS verification | GeoTIFF header | Verify EPSG:5070 (same as WHP 2012) | ☐ |

**URL**: https://www.fs.usda.gov/ccrc/tool/wildfire-hazard-potential-wh-p (or LANDFIRE portal direct download)

**Output**: `data/raw/whp_rasters/whp_2018_continuous/` (GeoTIFF, 270m resolution)

**Responsibility**: Manual download from USFS website

**Critical flag**: Document exact WHP 2018 release date in `docs/DATA_DICTIONARY.md` before PAP registration.

---

### 1c. Census 2010 Tract Shapefiles (TIGER)

| Item | Source | Action | Checklist |
|------|--------|--------|-----------|
| Tract shapefiles 2010 vintage | Census TIGER/GENZ | Download shapefiles for all lower-48 states | ☐ |
| Projection | TIGER files | Verify WGS84 (EPSG:4269 or similar); will reproject to EPSG:5070 for raster processing | ☐ |

**URL**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-geodatabase-files.html (2010 vintage)

**Output**: `data/raw/tract_shapefiles/tracts_2010.shp` (plus .shx, .dbf, .prj, etc.)

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
- [ ] WHP 2012 exact release date (month/year)
- [ ] WHP 2018 exact release date (month/year) — **CRITICAL for cohort assignment**
- [ ] Both rasters' native resolution, CRS, and data range (e.g., WFP percentile 0–100)
- [ ] Any differences in computation methodology between WHP 2012 and WHP 2018

**File**: `docs/DATA_DICTIONARY.md` (new section: "WHP Raster Metadata")

---

### 3b. ACS Variables & MOE Availability

Document:
- [ ] Exact variable names in IPUMS extract for each outcome (poverty, income, employment, migration)
- [ ] MOE variable naming convention in IPUMS (e.g., B17001_MOE)
- [ ] Confirmation that MOE available at tract level for all three periods
- [ ] Any differences in variable definitions or MOE calculations across 2012, 2017, 2023 ACS

**File**: `docs/DATA_DICTIONARY.md` (section: "ACS Variables & MOE")

---

## Download Instructions (Manual Steps)

### Step 1: IPUMS ACS Extracts

1. Visit https://www.ipums.org/ (create account if needed)
2. Navigate to IPUMS USA → Create a new extract
3. Select samples: **ACS 2012, ACS 2017, ACS 2023** (5-year estimates)
4. Select variables:
   - `B17001` (Poverty)
   - `B19013` (Median HH income)
   - `B23025` (Employment)
   - `B07001` (Residence 5 years ago)
   - Geographic variables: state, county, tract FIPS
5. Geographic level: **Tract**
6. Specify geographic filter: Include all lower-48 US states (exclude AK, HI, PR)
7. Download as CSV
8. Save to `data/raw/acs_extracts/acs_[YEAR]_tract_extract.csv`

---

### Step 2: WHP 2018 Raster

1. Visit USFS LANDFIRE: https://www.landfire.gov/
2. Navigate to WHP (Wildfire Hazard Potential) data downloads
3. Select: **WHP 2018** raster (270m, Continental US)
4. Confirm file format: GeoTIFF
5. Confirm projection: EPSG:5070 (if not explicitly stated, verify after download)
6. Download and extract to `data/raw/whp_rasters/whp_2018_continuous/`
7. **Record release date** (check metadata or USFS publication page)

---

### Step 3: Census 2010 Tract Shapefiles

1. Visit Census TIGER: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html
2. Select year: **2010**
3. Select layer: **Tract**
4. Select geography: **Cartographic Boundary Shapefile** (500k resolution, smaller file)
5. Download for each state (or national zipped file if available)
6. Extract to `data/raw/tract_shapefiles/tracts_2010/`

---

### Step 4: USDA RUCC 2013

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
- [ ] ACS 2023 tract-level data actually available (confirm IPUMS has released 2023 ACS at tract level)
- [ ] WHP 2018 GeoTIFF readable by `rasterio` (test in Python)
- [ ] Tract shapefiles have 11-digit GEOID or can be reconstructed from state/county/tract FIPS

### File Size Sanity Checks

- [ ] ACS 2012 CSV: ~200–300 MB (tract-level, ~70,000 tracts, 4 outcomes + MOE + geo variables)
- [ ] ACS 2017 CSV: ~200–300 MB
- [ ] ACS 2023 CSV: ~200–300 MB
- [ ] WHP 2018 GeoTIFF: ~200–500 MB (national raster, 270m resolution)
- [ ] Tract shapefiles: ~100–200 MB (uncompressed)

---

## Timeline

| Task | Week | Owner | Status |
|------|------|-------|--------|
| Download IPUMS ACS 2012/2017/2023 (tract-level) | Week 1 | User (manual, IPUMS.org) | ☐ |
| Download WHP 2018 raster + verify release date | Week 1 | User (manual, USFS LANDFIRE) | ☐ |
| Download MTBS fire perimeters 1984–2023 | Week 1 | User (manual, USGS) | ☐ |
| Download Census 2010 tract shapefiles | Week 1 | User (manual, Census TIGER) | ☐ |
| Download USDA RUCC 2013 | Week 1 | User (manual, USDA ERS) | ☐ |
| Verify all downloads + document metadata | Week 2 | Code review | ☐ |
| Update `docs/DATA_DICTIONARY.md` with WHP/ACS metadata | Week 2 | Documentation | ☐ |
| PAP registration (contingent on WHP 2018 release date confirmation) | Week 2 | User | ☐ |

---

## Notes

- **ACS 2023 availability**: Confirm that tract-level ACS 2023 (2019–2023 window) is available on IPUMS as of 2026-07-31. If not yet released, proceed with ACS 2012/2017 and plan for ACS 2023 data as available.
- **WHP 2018 release date is critical**: This determines whether fires in 2018 belong to the WHP2012 cohort or the gap. Document before finalizing cohort boundaries in PAP.
- **Symlink vs. copy**: For MTBS and WHP 2012 (already in wildfire-finance), create symlinks rather than copies to avoid duplication:
  ```bash
  ln -s ../../wildfire-finance/data/raw/mtbs_perims data/raw/mtbs_perimeters
  ln -s ../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous data/raw/whp_2012_continuous
  ```
