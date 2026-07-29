# Week 1: Data Assembly Checklist
**Status**: Execution phase  
**Target completion**: End of Week 1  
**Deliverables**: 5 analysis-ready datasets

---

## **Overview: What you're building**

By end of Week 1, you'll have a complete `analysis_sample_final.parquet` file with:
- ~3,100 lower-48 US counties × 4 time periods (~12,400 observations)
- Outcomes: poverty, income, net migration, employment
- Treatment indicators: fire year, fire count, acres burned
- Baseline covariates: WFP 2012 quintile, fire history, demographics
- Sample restrictions documented (exclusions with counts)

---

## **Task 1: ACS Data (Days 1–2)**

### **Objective**
Pull 5-year ACS estimates for poverty, income, migration, employment across all lower-48 counties for 4 time periods.

### **Data Source**
- **IPUMS-USA** (https://usa.ipums.org/)
- Requires free registration; login with your account

### **What to extract**

| Variable | IPUMS Code | Years | Level |
|----------|-----------|-------|-------|
| Poverty status | POVERTY | 2007–2011, 2015–2019 ACS | County |
| Household income | HHINCOME | 2007–2011, 2015–2019 ACS | County |
| Residence 1 year ago | MIGRATE1 | 2007–2011, 2015–2019 ACS | County (net migration proxy) |
| Employment status | EMPSTAT | 2007–2011, 2015–2019 ACS | County |
| Population | TOTAL | 2007–2011, 2015–2019 ACS | County |

**Steps**:
1. Go to https://usa.ipums.org/
2. Click "Select Data" → Select "American Community Survey (ACS)"
3. Choose survey samples:
   - ACS 2007–2011 (5-year estimate)
   - ACS 2015–2019 (5-year estimate)
4. Select variables (above table)
5. Specify geography: County (all lower-48 states)
6. Download as CSV
7. Save to `data/raw/acs_extracts/`

### **Quality checks**
- [ ] Files downloaded successfully
- [ ] Row count ≈ 3,100 counties × 2 periods
- [ ] Missingness < 2% per variable
- [ ] Poverty rates 0–100 (% scale)
- [ ] Income values reasonable (non-negative, no obvious topcode anomalies)
- [ ] Migration variable captures 5-year residence change

---

## **Task 2: Fire Data — MTBS Perimeters (Days 1–2)**

### **Objective**
Obtain fire perimeter shapefiles (MTBS) to assign treatment status by county and year.

### **Data Source**
- **USGS Monitoring Trends in Burn Severity (MTBS)**: https://www.mtbs.gov/
- Alternatively: Check `wildfire-finance/data/raw/mtbs_perims/` for existing data

### **What to get**
- MTBS fire perimeters (polygons), 1984–2019, nationwide
- Minimum threshold: 1,000 acres (follow wildfire-finance definition)
- Attribute: fire year, acres burned

### **Steps**
1. **Check wildfire-finance first** (faster):
   ```bash
   ls ../../wildfire-finance/data/raw/mtbs_perims/
   ```
   If files exist, symlink or copy to your `data/raw/mtbs_perimeters/`:
   ```bash
   ln -s ../../wildfire-finance/data/raw/mtbs_perims/ data/raw/mtbs_perimeters
   ```

2. **If not available**, download from USGS:
   - Go to https://www.mtbs.gov/viewer/
   - Download fire perimeters shapefile (1984–2019, all US states)
   - Save to `data/raw/mtbs_perimeters/`

### **Quality checks**
- [ ] Shapefile has all required fields (fire year, acres, geometry)
- [ ] Year range: 1984–2019
- [ ] Acres ≥ 1,000 (or separate to filter later)
- [ ] All lower-48 states represented
- [ ] CRS (coordinate system): Check if EPSG:4326 (lat/lon) or match to county boundaries

---

## **Task 3: WFP 2012 Raster (Days 1–2)**

### **Objective**
Obtain USFS Wildfire Hazard Potential (WHP) 2012 raster to use as primary matching variable.

### **Data Source**
- **USFS WHP 2012**: Predetermined (finalized before 2013 fire season)
- Check: `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`

### **What to get**
- WFP 2012 raster (GeoTIFF), 270m resolution, nationwide
- Projection: EPSG:5070 (Albers equal-area)

### **Steps**
1. Check wildfire-finance:
   ```bash
   ls ../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/
   ```
   If exists, symlink:
   ```bash
   ln -s ../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/ data/raw/whp_rasters/wfp_2012
   ```

2. If not available, download from USFS (LANDFIRE portal): https://www.landfire.gov/

### **Quality checks**
- [ ] Raster file loads without error
- [ ] Spatial extent covers all lower-48 states
- [ ] CRS: EPSG:5070 (or will reproject)
- [ ] Values: WFP scores (typically 0–100 or 0–1 scale, depending on vintage)

---

## **Task 4: County Boundaries (Days 2–3)**

### **Objective**
Get standardized county boundary shapefiles to spatially match fires to counties and aggregate WFP to county level.

### **Data Source**
- **USGS TIGER/Line**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html
- Or Census: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

### **What to get**
- County boundaries shapefile, all lower-48 US states
- Vintage: 2012 or later (to match treatment window)

### **Steps**
1. Go to Census TIGER/Line download
2. Select: Counties (and equivalent entities)
3. Select all states (or download by region and merge)
4. Save to `data/raw/county_shapefiles/`

### **Quality checks**
- [ ] Shapefile loads
- [ ] ~3,100 counties (lower-48; excludes AK, HI, PR)
- [ ] Contains GEOID (standard county FIPS code)
- [ ] CRS: EPSG:4326 (lat/lon) or known (will reproject for raster ops)

---

## **Task 5: Pre-2012 Fire History (Days 2–3)**

### **Objective**
Compile pre-treatment fire exposure (1984–2011) as a matching covariate (to control for baseline fire risk).

### **Data Source**
- MTBS (same as Task 2)

### **What to get**
- For each county, calculate:
  - Number of large fires (≥1,000 acres) 1984–2011
  - Total acres burned 1984–2011

### **Steps**
1. Use MTBS shapefile (Task 2)
2. Filter to fires with year ≤ 2011 and acres ≥ 1,000
3. Spatially join fires to county boundaries
4. Aggregate by county: fire count, total acres burned
5. Output: `data/processed/pre2012_fire_history.parquet`

### **Quality checks**
- [ ] Fire counts and acres non-negative
- [ ] Counties with no pre-2012 fires have count=0, acres=0
- [ ] ~30% of counties have ≥1 pre-2012 fire (reasonable for fire-prone regions)

---

## **Task 6: WFP 2012 to County Level (Days 3–4)**

### **Objective**
Aggregate WFP 2012 raster to county level (e.g., mean WFP quintile per county) for use as matching covariate.

### **Data Source**
- WFP 2012 raster (Task 3)
- County boundaries (Task 4)

### **Approach**
1. Load WFP 2012 raster and county boundaries (both must be same CRS or reproject)
2. For each county polygon, extract raster values (mean, median, or percentile)
3. Assign WFP quintile (0–20%, 20–40%, …, 80–100%) based on national distribution
4. Output: `data/processed/whp_2012_county.parquet` with columns: GEOID, wfp_mean, wfp_quintile

### **Quality checks**
- [ ] All ~3,100 counties have a WFP value
- [ ] Quintile distribution roughly balanced (each quintile ≈ 20% of counties)
- [ ] WFP values in reasonable range

---

## **Task 7: Treatment Assignment (Days 3–4)**

### **Objective**
Assign each county to treatment cohort based on first large fire occurrence.

### **Data Source**
- MTBS perimeters (Task 2)

### **Treatment windows** (locked in PAP)
- **Early cohort** (g=2017): First fire in 2012–2015
- **Late cohort** (g=2022): First fire in 2016–2019
- **Never-treated**: No fire 2012–2019

### **Steps**
1. For each county, find **first occurrence** of fire ≥1,000 acres in 1990–2019
2. Assign cohort based on year:
   - If fire_year ∈ 2012–2015 → early=1, late=0
   - If fire_year ∈ 2016–2019 → early=0, late=1
   - If fire_year ∉ 2012–2019 (or no fire) → early=0, late=0 (never-treated)
3. For treated counties, also calculate:
   - Fire count in treatment window (2012–2015 for early; 2016–2019 for late)
   - Total acres burned in treatment window
4. Output: `data/processed/fire_treatment_assignment.parquet`

### **Quality checks**
- [ ] Early cohort: ~400–500 counties
- [ ] Late cohort: ~100–150 counties
- [ ] Never-treated: ~2,500–2,700 counties
- [ ] Total ≈ 3,100 counties
- [ ] No county in two cohorts simultaneously

---

## **Task 8: Smoke Buffer Exclusion (Days 4–5)**

### **Objective**
Identify and exclude control counties within 100 km of any treated fire perimeter (to avoid smoke spillover contamination).

### **Data Source**
- MTBS perimeters (Task 2)
- County boundaries (Task 4)
- Treatment assignment (Task 7)

### **Approach**
1. Get all fire perimeters for fires in 2012–2019 (both early and late cohorts)
2. Create 100 km buffer around each fire perimeter
3. Spatially intersect with county boundaries
4. Flag any county (treated or control) within buffer
5. For controls only, mark as "within smoke buffer" (to exclude from analysis)

### **Output**
- `data/processed/smoke_buffer_100km.parquet`: County GEOID, within_smoke_buffer (binary)

### **Robustness variants** (to test later)
- 50 km buffer
- 150 km buffer

### **Quality checks**
- [ ] ~10–15% of control counties fall within 100 km (reasonable given fire clustering)
- [ ] Fire perimeters and buffers visualizable in GIS (spot-check 5–10)
- [ ] Counties correctly flagged/unflagged

---

## **Task 9: Baseline Covariates Assembly (Days 4–5)**

### **Objective**
Compile pre-treatment covariates (2007–2011 or 2012 ACS) for use in propensity-score matching.

### **Data Source**
- ACS 2007–2011 (from Task 1)
- USDA RUCC (Rural-Urban Continuum Code)

### **Covariates to extract**
From 2007–2011 ACS (baseline period):
- Poverty rate (%)
- Median household income ($)
- Population density (persons/sq mi)
- % population age 65+
- Population size (total, for weighting)

From USDA:
- RUCC classification (2013 vintage or closest available)

### **Steps**
1. Aggregate ACS individual-level data to county
2. Download RUCC from USDA ERS: https://www.ers.usda.gov/webdocs/DataFiles/17749/ruralurbancodes2013.xls
3. Merge ACS and RUCC by county FIPS
4. Output: `data/processed/matching_covariates_2012.parquet`

### **Quality checks**
- [ ] All ~3,100 counties present
- [ ] No negative values (except allowed: income can be 0)
- [ ] Poverty rates 0–100%
- [ ] Population > 0 (or flag very small counties for later exclusion)

---

## **Task 10: Final Panel Assembly (Day 5)**

### **Objective**
Merge all datasets into balanced panel: counties × 4 time periods.

### **Data Source**
All outputs from Tasks 1–9

### **Steps**
1. Start with county list (Task 4): ~3,100 counties
2. Create time period dummy (1990, 2000, 2007–2011, 2015–2019)
3. Merge by GEOID:
   - ACS outcomes (Task 1)
   - Treatment assignment (Task 7)
   - WFP 2012 (Task 6)
   - Pre-2012 fire history (Task 5)
   - Smoke buffer exclusion (Task 8)
   - Matching covariates (Task 9)
4. Apply sample restrictions:
   - Drop counties with population < 1,000 (unreliable ACS)
   - Drop controls within 100 km smoke buffer (primary spec)
   - Drop pre-2012-treated counties from control pool (if applicable)
5. Output: `data/processed/analysis_sample_final.parquet`

### **Quality checks**
- [ ] Balanced panel: ~3,100 counties × 4 periods (allow some attrition if early Census unavailable)
- [ ] Missingness < 2% per variable
- [ ] N_treated ≈ 500–600 (early + late)
- [ ] N_control ≈ 2,400–2,600
- [ ] All columns documented in data dictionary

---

## **Task 11: Sample Restrictions Log (Day 5)**

### **Objective**
Document all exclusions with counts (transparency for methods section).

### **Output**
Create `data/metadata/sample_restrictions_log.txt`:

```
SAMPLE CONSTRUCTION FLOWCHART
================================

Starting universe: 3,141 lower-48 US counties
  ↓
Drop population < 1,000:  -41 counties
  ↓
Remaining: 3,100 counties

TREATMENT ASSIGNMENT (using MTBS ≥1,000 acres, 2012–2019):
  Early-treated (2012–2015):    ~450 counties
  Late-treated (2016–2019):     ~140 counties
  Never-treated (2012–2019):    ~2,510 counties
  ─────────────────────────────────
  Total (no smoke exclusion):    3,100 counties

SMOKE BUFFER EXCLUSION (100 km):
  Controls within 100 km:        ~350 counties
  Controls outside 100 km:       ~2,160 counties
  Treated counties (included):   ~590 counties
  ─────────────────────────────────
  Final control pool:            ~2,160 counties
  Final treated pool:            ~590 counties
  ─────────────────────────────────
  FINAL SAMPLE:                  ~2,750 counties

PANEL STRUCTURE:
  Counties: ~2,750
  Time periods: 4 (1990, 2000, 2007–2011, 2015–2019)
  Total observations: ~11,000

NOTE: Pre-2012-treated counties (fires 1990–2011) excluded from 
      control pool but used for matching covariates.
```

### **Purpose**
- Transparency in manuscript methods
- Verification that sample sizes match PAP predictions

---

## **Task 12: Data Dictionary (Day 5)**

### **Objective**
Document all variables in final dataset for reproducibility.

### **Output**
Create `data/metadata/DATA_DICTIONARY.md`:

```markdown
# Data Dictionary: analysis_sample_final.parquet

## Geographic/Time Identifiers
- `GEOID` (integer): County FIPS code (5 digits)
- `county_name` (string): County name
- `state` (string): State abbreviation
- `year` (integer): Census year (1990, 2000) or ACS final year (2011, 2019)

## Treatment Variables
- `early_treated` (binary): 1 if first fire ≥1,000 acres in 2012–2015
- `late_treated` (binary): 1 if first fire ≥1,000 acres in 2016–2019
- `fire_year` (integer): Year of first fire (or 9999 if never-treated)
- `fire_count` (integer): Number of fires ≥1,000 acres in treatment window
- `acres_burned` (float): Total acres burned in treatment window

## Primary Outcome Variables
- `poverty_rate` (float): % population below federal poverty line (0–100)
- `median_hh_income` (float): Median household income ($, nominal)
- `net_migration_rate` (float): % moved in − % moved out (ACS 5-year residence change)
- `employment_rate` (float): % civilian labor force employed (0–100)

## Matching Covariates (2007–2011 baseline)
- `wfp_quintile` (integer): WFP 2012 quintile (1=low hazard, 5=high hazard)
- `baseline_poverty_rate` (float): Poverty rate 2007–2011
- `baseline_median_income` (float): Median income 2007–2011
- `population_density` (float): Persons per sq mi
- `pct_age_65plus` (float): % population age 65+ (0–100)
- `population` (integer): Total population 2007–2011
- `rucc` (integer): USDA Rural-Urban Continuum Code (1–9)

## Fire History Covariates
- `pre2012_fire_count` (integer): # fires ≥1,000 acres 1984–2011
- `pre2012_acres_burned` (float): Total acres burned 1984–2011

## Exclusions/Flags
- `within_smoke_buffer_100km` (binary): 1 if within 100 km of any treated fire
- `sample_restriction` (string): Reason for exclusion (if any); "included" otherwise

## Notes
- Missingness: < 2% for all variables
- Population units: All analyses exclude counties with population < 1,000 in baseline period
- ACS estimates: 5-year rolling averages; labeled by final year (2015–2019 ACS labeled "2019")
```

---

## **Week 1 Completion Checklist**

- [ ] **Task 1**: ACS data pulled (2007–2011, 2015–2019) → `data/raw/acs_extracts/`
- [ ] **Task 2**: MTBS perimeters available → `data/raw/mtbs_perimeters/` or symlinked
- [ ] **Task 3**: WFP 2012 raster available → `data/raw/whp_rasters/wfp_2012/` or symlinked
- [ ] **Task 4**: County boundaries → `data/raw/county_shapefiles/`
- [ ] **Task 5**: Pre-2012 fire history → `data/processed/pre2012_fire_history.parquet`
- [ ] **Task 6**: WFP to county level → `data/processed/whp_2012_county.parquet`
- [ ] **Task 7**: Treatment assignment → `data/processed/fire_treatment_assignment.parquet`
- [ ] **Task 8**: Smoke buffer → `data/processed/smoke_buffer_100km.parquet`
- [ ] **Task 9**: Matching covariates → `data/processed/matching_covariates_2012.parquet`
- [ ] **Task 10**: Final panel → `data/processed/analysis_sample_final.parquet`
- [ ] **Task 11**: Sample log → `data/metadata/sample_restrictions_log.txt`
- [ ] **Task 12**: Data dictionary → `data/metadata/DATA_DICTIONARY.md`
- [ ] **Commit to git**: All data processing code + documentation

---

## **Deliverables by End of Week 1**

```
data/
├── raw/
│   ├── acs_extracts/             ✅ ACS CSVs (2007–2011, 2015–2019)
│   ├── mtbs_perimeters/          ✅ MTBS shapefile
│   ├── whp_rasters/              ✅ WFP 2012 raster
│   └── county_shapefiles/        ✅ County boundaries
├── processed/
│   ├── pre2012_fire_history.parquet
│   ├── whp_2012_county.parquet
│   ├── fire_treatment_assignment.parquet
│   ├── smoke_buffer_100km.parquet
│   ├── matching_covariates_2012.parquet
│   └── analysis_sample_final.parquet       ← **PRIMARY DELIVERABLE**
└── metadata/
    ├── sample_restrictions_log.txt
    ├── DATA_DICTIONARY.md
    └── county_fips_names.csv              (optional, for reference)
```

---

## **Risk Mitigation**

| Risk | Mitigation |
|------|-----------|
| Data unavailable (e.g., Census 1990/2000 county poverty) | Use ACS 2007–2011 as only pre-period; acknowledge weaker parallel trends testing |
| IPUMS slow/unresponsive | Pre-download sample data; check IPUMS status page |
| Thin common support (WFP matching) | Document effective sample size (ESS); flag in Week 4 |
| Fire perimeter edges/overlaps | Spot-check 10–20 county-fire GIS overlaps; use consistent method |

---

**Status**: Ready to execute Week 1. Begin with Task 1 (ACS) and Task 2 (MTBS) in parallel.

*Questions on any task? Flag before starting.*
