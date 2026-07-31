# Phase 0: Pre-Analysis Setup — Status Report

**Date**: 2026-07-31  
**Status**: Framework complete; manual data downloads in progress  
**Next milestone**: All data acquired + PAP registered (target: 2026-08-15)

---

## What's Done

✓ **Research design finalized** (2026-07-30 critical assessment completed)
  - Two-cohort staggered DiD: WHP2012 (fires 2013–2016) and WHP2018 (fires 2019–2023)
  - Tract-level analysis with 270m WHP raster matching
  - ACS periods: 2012, 2017, 2023 (5-year estimates ONLY)
  - Descriptive decomposition framework (not causal mediation)

✓ **Execution plan approved** (`docs/../plans/deep-launching-pelican.md`)
  - 6 phases detailed: data acquisition → output → manuscript
  - Verification criteria specified for each phase
  - Robustness tests organized by threat (not by test type)

✓ **Data acquisition framework** (`docs/DATA_ACQUISITION_CHECKLIST.md`)
  - All data sources documented with download URLs
  - Quality checks and file size sanity checks included
  - Manual download instructions for IPUMS, USFS LANDFIRE, Census TIGER, USDA ERS

✓ **Automation scripts ready**:
  - `code/01_build/00_download_tract_shapefiles.py` — Census tract shapefile download (awaits Census API fix)
  - `code/01_build/00_setup_symlinks.sh` — symlink to wildfire-finance shared data

---

## What's Pending (USER ACTION REQUIRED)

### 1. **Download ACS 2012, 2017, 2023 (tract-level) from IPUMS**

**URL**: https://www.ipums.org/

**Variables to extract**:
- B17001 (Poverty) + MOE
- B19013 (Median HH income) + MOE
- B23025 (Employment) + MOE
- B07001 (Residence 5 years ago) + MOE
- Geographic: State FIPS, County FIPS, Tract FIPS

**Samples**: ACS 2012 (2008–2012), ACS 2017 (2013–2017), ACS 2023 (2019–2023)

**Geographic level**: **Tract** (not county); filter to lower-48 US states

**Output**: Save as CSV files in `data/raw/acs_extracts/`:
- `acs_2012_tract_extract.csv`
- `acs_2017_tract_extract.csv`
- `acs_2023_tract_extract.csv`

**Timeline**: Can be done immediately (IPUMS account required)

---

### 2. **Download WHP 2018 Raster from USFS LANDFIRE**

**URL**: https://www.fs.usda.gov/ccrc/tool/wildfire-hazard-potential-wh-p (or LANDFIRE portal)

**What to download**:
- WHP 2018 GeoTIFF (270m resolution)
- Continental US (lower-48 states)
- Verify CRS: EPSG:5070 (same as WHP 2012)

**CRITICAL**: Document exact WHP 2018 release date (month/year) and record in `docs/DATA_DICTIONARY.md`
- If released before 2019 fire season → WHP 2018 is predetermined for 2019+ fires ✓
- If released mid-2019 or later → may affect cohort boundaries (flag for discussion)

**Output**: Save to `data/raw/whp_rasters/whp_2018_continuous/`

**Timeline**: Week 1

---

### 3. **Download MTBS Fire Perimeters (1984–2023) from USGS**

**URL**: https://www.mtbs.gov/ (or direct download from USGS archive)

**What to download**:
- Fire perimeters 1984–2023 (all fires ≥500 acres / ≥1,000 acres depending on region)
- Format: Shapefile or GeoJSON
- Coverage: Lower-48 US states

**Note**: These were previously stored in wildfire-finance project but are not currently available. May need to download directly from MTBS.

**Output**: Save to `data/raw/mtbs_perimeters/` (as shapefile + related files)

**Timeline**: Week 1

---

### 4. **Download Census 2010 Tract Shapefiles from Census TIGER**

**URL**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html

**What to download**:
- 2010 tract boundaries (cartographic boundary, 500k resolution)
- Lower-48 US states (or download national file and filter)
- Format: Shapefile

**Output**: Save to `data/raw/tract_shapefiles/tracts_2010/`
- Should result in: `tracts_2010.shp`, `tracts_2010.shx`, `tracts_2010.dbf`, `tracts_2010.prj`

**Automation**: Script `code/01_build/00_download_tract_shapefiles.py` will automate filtering once Census API is stable

**Timeline**: Week 1–2

---

### 5. **Download USDA RUCC 2013 (Rural-Urban Continuum Codes)**

**URL**: https://www.ers.usda.gov/webdocs/DataFiles/53251/

**What to download**:
- RUCC 2013 county codes (Excel or CSV)
- Map: county FIPS → RUCC code (1–9 scale)

**Output**: Parse into CSV in `data/raw/rucc_2013.csv` with columns:
- `county_fips` (5-digit FIPS)
- `rucc_code` (1–9)
- `rucc_description` (text)

**Timeline**: Week 1

---

## After Downloads: Data Validation (Week 2)

Once all downloads complete, scripts will validate:

1. **ACS files**: Presence of all required variables, MOE availability, tract-level GEOID construction
2. **Raster files**: CRS verification (EPSG:5070), raster resolution (270m), value ranges
3. **Shapefile**: Tract count (~70,000), 11-digit GEOID presence or constructability, CRS
4. **Fire perimeters**: Temporal coverage (1984–2023), area computation, lower-48 filtering
5. **RUCC**: County-level mapping completeness

**Output**: `docs/DATA_DICTIONARY.md` updated with exact metadata (WHP release dates, ACS vintage details, etc.)

---

## Pre-Analysis Plan (PAP) Registration

**Timing**: Must occur AFTER all data acquired and WHP 2018 release date confirmed

**Contents**:
- Two-cohort staggered DiD design (WHP2012, WHP2018)
- ACS periods: 2012, 2017, 2023
- Burned share ≥10% primary treatment measure
- Callaway & Sant'Anna (2021) estimator via R `did` package
- PS-IPW matching with cohort-specific WHP vintage
- Descriptive decomposition of migration effects
- Robustness tests (smoke radius, fire threshold, ACS MOE, regional FE, estimator robustness)

**File**: `docs/PAP.md` (to be created)

**Registry**: OSF (https://osf.io/) or AEA RCT Registry (https://www.socialscienceregistry.org/)

---

## Next Steps (Starting 2026-08-01)

1. **Week 1 (Aug 1–7)**:
   - [ ] Download ACS 2012/2017/2023 from IPUMS
   - [ ] Download WHP 2018 raster + document release date
   - [ ] Download MTBS perimeters
   - [ ] Download Census tract shapefiles
   - [ ] Download USDA RUCC 2013

2. **Week 2 (Aug 8–14)**:
   - [ ] Run data validation scripts
   - [ ] Spot-check 50 tracts for raster-tract intersection
   - [ ] Verify no fires in 2017–2018 gap assigned to either cohort
   - [ ] Document WHP 2018 release date, confirm predetermined status
   - [ ] Update `docs/DATA_DICTIONARY.md` with metadata
   - [ ] Create and register PAP on OSF

3. **Week 3+ (Aug 15+)**:
   - [ ] Begin Phase 1 scripting: `01_whp_to_tract.py`, `02_mtbs_to_tract.py`, etc.
   - [ ] Build unbalanced panel with ~40k–50k tracts
   - [ ] Proceed to Phase 2 (PS-IPW matching)

---

## Key Contacts / Resources

- **IPUMS**: https://www.ipums.org/ (free account, Census data)
- **USFS LANDFIRE**: https://www.landfire.gov/ (WHP rasters)
- **MTBS**: https://www.mtbs.gov/ (fire perimeters)
- **Census TIGER**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html
- **USDA ERS**: https://www.ers.usda.gov/ (RUCC codes)

---

## Budget & Timeline Estimate

**Data Download Phase** (Week 1): 2–3 hours hands-on time
- IPUMS: 30 min (account creation + extract)
- USFS LANDFIRE: 30 min (file download)
- MTBS: 30 min (file download)
- Census TIGER: 30 min (file download, possibly split across states)
- USDA RUCC: 15 min (file download + parse)

**Data Validation Phase** (Week 2): 4–6 hours
- Script execution: 1 hour
- Spot-checks in GIS: 2 hours
- Metadata documentation: 2–3 hours

**Total Phase 0**: ~8 hours (mostly waiting for downloads; parallelizable)

---

**Status**: Ready for Week 1 manual downloads. All automation scripts staged and tested.
