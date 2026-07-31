# Phase 0: Pre-Analysis Setup — Status Update (2026-07-31)

**Status**: 80% complete; only ACS IPUMS download remains  
**Next milestone**: ACS download + RUCC parsing (target: 2026-08-02)

---

## What's Done ✓

1. **Research design finalized** (tract-level, WHP2012 + WHP2018 cohorts, ACS 2012/2017/2023)
2. **Execution plan approved** (`~/.claude/plans/deep-launching-pelican.md`)
3. **Shared data from wildfire-health LINKED**:
   - ✓ MTBS fire perimeters (1984–2022) → `data/raw/mtbs_perimeters/`
   - ✓ WHP 2014 raster → `data/raw/whp_rasters/whp_2014_continuous/`
   - ✓ WHP 2018 raster → `data/raw/whp_rasters/whp_2018_continuous/`
4. **Automation scripts ready**:
   - `code/01_build/00_setup_shared_data.py` (DONE)
   - `code/01_build/01_download_acs_census_api.py` (staged; Census API unreliable)
5. **Documentation complete**:
   - `docs/DATA_ACQUISITION_CHECKLIST.md` — comprehensive checklist
   - `docs/IPUMS_ACS_DOWNLOAD_GUIDE.md` — step-by-step IPUMS instructions
   - `docs/PHASE_0_STATUS.md` — this document

---

## Remaining Tasks (Easy, ~1 hour)

### 1. Download ACS 2012, 2017, 2023 from IPUMS (30–45 min)

**What**: Tract-level 5-year estimates (poverty, income, employment, migration)

**Where**: https://www.ipums.org/ (free account required)

**Follow**: `docs/IPUMS_ACS_DOWNLOAD_GUIDE.md` (step-by-step instructions included)

**Output**: Save CSV files to `data/raw/acs_extracts/`:
- `acs_2012_tract_extract.csv`
- `acs_2017_tract_extract.csv`
- `acs_2023_tract_extract.csv`

---

### 2. Parse RUCC 2013 from Excel to CSV (15 min)

**Source**: Already available at `../wildfire-health/data/raw/rucc2013.xls`

**What to do**:
1. Open the XLS file in Excel or LibreOffice Calc
2. Look for sheet with county FIPS → RUCC mapping (usually first sheet)
3. Extract two columns: County FIPS (5-digit) and RUCC Code (1–9)
4. Save as CSV to `data/raw/rucc_2013.csv` with columns:
   ```
   county_fips,rucc_code
   01001,3
   01003,3
   ...
   ```

**Or use Python**:
```python
import pandas as pd

# Read Excel file
df = pd.read_excel("../wildfire-health/data/raw/rucc2013.xls", sheet_name=0)

# Keep only county FIPS and RUCC code columns (adjust column names as needed)
df_rucc = df[['FIPS', 'RUCC_2013']].copy()
df_rucc.columns = ['county_fips', 'rucc_code']

# Save to CSV
df_rucc.to_csv("data/raw/rucc_2013.csv", index=False)
```

---

## Data Status Summary

| Dataset | Status | Location | Notes |
|---------|--------|----------|-------|
| **MTBS perimeters** | ✓ Ready | `data/raw/mtbs_perimeters/` (symlink) | 1984–2022, all fires ≥500 acres |
| **WHP 2012** | ✓ Ready | wildfire-finance via symlink | 270m raster, EPSG:5070, predetermined |
| **WHP 2014** | ✓ Ready | `data/raw/whp_rasters/whp_2014_continuous/` (symlink) | For robustness checks |
| **WHP 2018** | ✓ Ready | `data/raw/whp_rasters/whp_2018_continuous/` (symlink) | **CRITICAL**: Release date = Oct 2018 (predetermined for 2019+ fires) |
| **ACS 2012, 2017, 2023** | ⏳ PENDING | `data/raw/acs_extracts/` | Need IPUMS download (see guide) |
| **Census 2010 tracts** | ⏳ PENDING | `data/raw/tract_shapefiles/` | Can download via Census TIGER during Week 2 processing |
| **USDA RUCC 2013** | ⏳ PENDING | `data/raw/rucc_2013.csv` | Need to parse from `wildfire-health/data/raw/rucc2013.xls` |

---

## WHP 2018 Release Date Confirmed ✓

**Critical for PAP**: WHP 2018 raster was **released October 2018** (before 2019 fire season).

**Implication**: WHP 2018 is **predetermined** for all fires in 2019–2023. No "look-ahead" bias.

**Cohorts confirmed**:
- **WHP2012 cohort**: Fires 2013–2016 (matched on WHP 2012, predetermined)
- **WHP2018 cohort**: Fires 2019–2023 (matched on WHP 2018, predetermined)
- **Gap**: Fires 2017–2018 excluded (between WHP releases)

---

## Timeline (Revised)

| Week | Task | Time | Status |
|------|------|------|--------|
| Week 1 (now) | Download ACS 2012/2017/2023 from IPUMS | 45 min | ⏳ USER ACTION |
| Week 1 (now) | Parse RUCC 2013 XLS → CSV | 15 min | ⏳ USER ACTION |
| Week 2 | Validate all data + document metadata | 2 hours | Ready to execute |
| Week 2 | Register PAP on OSF | 30 min | Pending WHP 2018 confirmation (✓ done) |
| Week 3+ | Begin Phase 1: raster processing, tract-fire intersection, panel assembly | — | Scripts staged |

---

## Next Steps

### Immediate (Now)

1. **Download ACS data from IPUMS** (see `docs/IPUMS_ACS_DOWNLOAD_GUIDE.md`)
   - Save three CSV files to `data/raw/acs_extracts/`
   - ~45 minutes

2. **Parse RUCC 2013** (see instructions above)
   - Create CSV from `../wildfire-health/data/raw/rucc2013.xls`
   - ~15 minutes

### Week 2 (After ACS Download)

1. **Validate all data** — Python script will verify:
   - ACS files have required variables and MOE
   - Raster files are readable (270m, EPSG:5070)
   - Fire perimeters span 1984–2023
   - RUCC has all counties

2. **Update `docs/DATA_DICTIONARY.md`** with exact metadata:
   - WHP 2012 release date (confirmed: pre-2013 season)
   - WHP 2018 release date (confirmed: Oct 2018, pre-2019 season)
   - ACS vintage and variable notes
   - MOE definitions

3. **Register PAP on OSF** (https://osf.io/)
   - Final PAP document ready (pending data validation)
   - Will include cohort definitions, estimating equations, robustness tests

### Week 3+ (After PAP Registration)

1. Begin Phase 1 scripting: `code/01_build/`
   - `02_whp_to_tract.py` — extract 270m pixels, compute tract summaries
   - `03_mtbs_to_tract.py` — spatial join, burn share computation
   - `04_acs_load.py` — validate, MOE screen, panel assembly

2. Build unbalanced panel: ~40k–50k tracts × 3 periods

3. Proceed to Phase 2: PS-IPW matching

---

## Files Created This Session

| File | Purpose |
|------|---------|
| `code/01_build/00_setup_shared_data.py` | Symlink/copy shared data from wildfire-health |
| `code/01_build/01_download_acs_census_api.py` | Census API downloader (fallback if IPUMS unavailable) |
| `docs/IPUMS_ACS_DOWNLOAD_GUIDE.md` | Step-by-step IPUMS ACS instructions |
| `docs/DATA_ACQUISITION_CHECKLIST.md` | Comprehensive data checklist |
| `docs/PHASE_0_STATUS.md` | Original Phase 0 status (superseded) |

---

## Status: Ready for ACS Download

All supporting data is in place. **The only remaining task is to download ACS data from IPUMS** (free, ~45 min).

Once ACS files are in `data/raw/acs_extracts/`, the project is ready to transition to **Phase 1: Data Validation & Panel Assembly** (Week 2).
