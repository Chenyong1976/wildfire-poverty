# Week 1 Progress: Data Acquisition Phase

**Date**: 2026-07-28  
**Current Status**: 🟡 75% Complete (awaiting MTBS download)

---

## **Completed** ✅

### **Automated Downloads**
- ✅ **ACS 2007-2011 & 2015-2019**: Downloaded via Census API (6,441 county-year observations)
- ✅ **County boundaries**: Automatically downloaded from Census TIGER/Line (~3,100 counties)
- ✅ **WFP 2012 raster**: Copied from wildfire-finance project (ready for county aggregation)

### **Data Processing**
- ✅ **ACS validation & load**: Aggregated, validated, saved to `acs_county_outcomes.parquet`
  - Poverty rate: 0% – 64.5%
  - Median income: $11,391 – $142,299
  - Employment rate: 65.9% – 100%
  - Zero missing values after Census API download

### **Scripts Ready**
- ✅ `01a_acs_api_download.py` — Census API pull (automated, no browser needed)
- ✅ `01_acs_load.py` — ACS validation & aggregation
- ✅ `00b_download_shapefiles.py` — County boundaries download (auto) + MTBS prompt

### **Task Status** (14 items)
| Task | Status | Blocker |
|------|--------|---------|
| #1 | ✅ Completed | — |
| #2 | ✅ Completed | — |
| #4 | ✅ Completed | — |
| #5 | ✅ Completed | — |
| #6 | ✅ Completed | — |
| #3 | 🟡 Pending | User action (MTBS download) |
| #7-14 | ⏳ Blocked | Waiting on #3 (MTBS) |

---

## **Blocking Issue** 🚧

**MTBS fire perimeters** must be manually downloaded:
- **Why**: USGS hosting doesn't support direct automated download links
- **Source**: https://www.mtbs.gov/
- **Instructions**:
  1. Visit https://www.mtbs.gov/viewer/
  2. Click "Download" (or navigate to data download page)
  3. Select "Fire Perimeters" shapefile
  4. Download ~300 MB file
  5. Extract to: `data/raw/mtbs_perimeters/`
  6. Let me know when complete

Once MTBS is downloaded, **I can immediately run the remaining 8 tasks** (fire treatment, WFP aggregation, covariates, smoke buffer, final panel assembly, documentation, commit).

---

## **What's Waiting on MTBS**

Once you download and extract MTBS to `data/raw/mtbs_perimeters/`, these tasks will execute automatically:

| Task | Script | Output | Est. Time |
|------|--------|--------|-----------|
| #7 | `02_fire_treatment.py` | `fire_treatment_assignment.parquet` | ~3 min |
| #9 | `02b_fire_history.py` | `pre2012_fire_history.parquet` | ~3 min |
| #8 | `03b_wfp_to_county.py` | `whp_2012_county.parquet` | ~5 min |
| #10 | `03_matching_covariates.py` | `matching_covariates_2012.parquet` | ~1 min |
| #11 | `04_smoke_buffer.py` | `smoke_buffer_100km.parquet` | ~2 min |
| #12 | `05_panel_assembly.py` | **`analysis_sample_final.parquet`** | ~1 min |
| #13 | Manual | Data dictionary + sample log | ~10 min |
| #14 | Manual | Git commit | ~5 min |

**Total automation time after MTBS**: ~30 minutes

---

## **Timeline to Week 1 Completion**

- ✅ **ACS download**: ~5 min (complete)
- ✅ **County boundaries**: ~10 min (complete)
- 🟡 **MTBS download**: ~30 min (your action)
- ✅ **Remaining automation**: ~30 min (will run immediately after MTBS available)

**Grand total**: ~1.5 hours (mostly waiting on data sources)

---

## **Files Generated So Far**

```
data/
├── raw/
│   ├── acs_extracts/
│   │   ├── acs_2011_extract.csv ✅ (3,221 counties)
│   │   └── acs_2019_extract.csv ✅ (3,220 counties)
│   ├── county_shapefiles/
│   │   └── cb_2023_us_county_20m.* ✅ (shapefile files)
│   ├── whp_rasters/
│   │   └── wfp2012_cnt/* ✅ (WFP 2012 raster)
│   └── mtbs_perimeters/ 🟡 (WAITING FOR DOWNLOAD)
│
└── processed/
    └── acs_county_outcomes.parquet ✅ (6,441 obs, 10 columns)
```

---

## **Success Criteria After Week 1**

Once MTBS is downloaded and remaining tasks run, you'll have:

✅ `analysis_sample_final.parquet` — 11,000 observations (2,750 counties × 4 periods)  
✅ Complete data dictionary & sample restrictions log  
✅ All code committed to git  
✅ Ready for Week 2 (propensity-score matching)

---

## **Your Next Action**

**Download MTBS from https://www.mtbs.gov/ and extract to `data/raw/mtbs_perimeters/`**

Once complete, reply here and I'll automatically run the final 8 tasks.

---

**Estimated time to full Week 1 completion**: 30-45 min (after you download MTBS)
