# Week 1 Implementation: Status Update

**Date**: 2026-07-28  
**Status**: Setup complete; awaiting manual data downloads

---

## **Completed Tasks**

✅ **Task #1**: Project setup & upstream data verification
- Created all required directories
- WFP 2012 raster copied to project (from wildfire-finance)
- MTBS confirmed missing (need to download)

✅ **Task #4**: WFP 2012 raster acquisition
- Files copied to `data/raw/whp_rasters/`
- Ready for aggregation to county level

---

## **Pending Manual Downloads** (User Action Required)

You must download these datasets from external sources and save to the specified directories:

### **1. ACS Data (Task #2)** ⏱️ ~30 min
- **Source**: https://usa.ipums.org/
- **Extract**: ACS 2007-2011 (5-year) + ACS 2015-2019 (5-year)
- **Variables**: Poverty, income, migration, employment
- **Save as**:
  - `data/raw/acs_extracts/acs_2011_extract.csv`
  - `data/raw/acs_extracts/acs_2019_extract.csv`

### **2. MTBS Fire Perimeters (Task #3)** ⏱️ ~10 min
- **Source**: https://www.mtbs.gov/
- **Download**: Fire perimeters shapefile (1984-2019, all states)
- **Save to**: `data/raw/mtbs_perimeters/`
- **Verify**: Should contain `.shp`, `.shx`, `.dbf`, `.prj` files

### **3. County Boundaries (Task #5)** ⏱️ ~5 min
- **Source**: https://www.census.gov/cgi-bin/geo/shapefiles/
- **Download**: County boundaries shapefile (2012 or latest)
- **Save to**: `data/raw/county_shapefiles/`
- **Verify**: Should contain `.shp`, `.shx`, `.dbf`, `.prj` files

### **4. USDA RUCC (Optional)** ⏱️ ~2 min
- **Source**: https://www.ers.usda.gov/webdocs/DataFiles/17749/
- **Download**: `ruralurbancodes2013.xlsx`
- **Save to**: `data/raw/ruralurbancodes2013.xlsx`

---

## **Automation-Ready Scripts**

All remaining scripts have been created and are **ready to execute** as soon as data downloads complete:

| Task | Script | Input | Output |
|------|--------|-------|--------|
| #6 | `01_acs_load.py` | ACS CSVs | `acs_county_outcomes.parquet` |
| #7 | `02_fire_treatment.py` | MTBS shapefile | `fire_treatment_assignment.parquet` |
| #8 | `03b_wfp_to_county.py` | WFP 2012 raster | `whp_2012_county.parquet` |
| #9 | `02b_fire_history.py` | MTBS shapefile | `pre2012_fire_history.parquet` |
| #10 | `03_matching_covariates.py` | All above | `matching_covariates_2012.parquet` |
| #11 | `04_smoke_buffer.py` | MTBS + counties | `smoke_buffer_100km.parquet` |
| #12 | `05_panel_assembly.py` | All datasets | `analysis_sample_final.parquet` |
| #13 | Manual | Final panel | Data dictionary + sample log |
| #14 | Manual | All above | Git commit |

---

## **Next Steps**

### **Immediate** (Your Action)
1. Open `docs/DATA_DOWNLOAD_GUIDE.md` for detailed download instructions
2. Download the 4 datasets above (ACS + MTBS + County boundaries + optional RUCC)
3. Save to `data/raw/` subdirectories as specified

### **After Downloads Complete** (I Will Execute)
1. Run scripts #6-7 (ACS load + fire treatment)
2. Run scripts #8-9 (WFP raster + fire history)
3. Run scripts #10-11 (covariates + smoke buffer)
4. Run script #12 (final panel assembly)
5. Document sample restrictions & data dictionary (task #13)
6. Commit to git (task #14)

**Expected time for automation**: ~20 min (all scripts parallelizable where possible)

---

## **File Organization**

```
data/
├── raw/
│   ├── acs_extracts/           [NEED: acs_2011_extract.csv, acs_2019_extract.csv]
│   ├── mtbs_perimeters/        [NEED: shapefile files]
│   ├── county_shapefiles/      [NEED: shapefile files]
│   ├── whp_rasters/            [READY: WFP 2012 raster]
│   └── ruralurbancodes2013.xlsx [OPTIONAL]
│
└── processed/
    ├── acs_county_outcomes.parquet           [will be created]
    ├── fire_treatment_assignment.parquet     [will be created]
    ├── whp_2012_county.parquet              [will be created]
    ├── pre2012_fire_history.parquet         [will be created]
    ├── matching_covariates_2012.parquet     [will be created]
    ├── smoke_buffer_100km.parquet           [will be created]
    └── analysis_sample_final.parquet        [FINAL OUTPUT]
```

---

## **Execution Plan After Downloads**

Once you've downloaded the data and placed files in the correct directories, run:

```bash
cd code/01_build

# Run in sequence (or in parallel with dependencies)
python 01_acs_load.py              # ~2 min
python 02_fire_treatment.py        # ~3 min
python 03b_wfp_to_county.py       # ~5 min
python 02b_fire_history.py        # ~3 min
python 03_matching_covariates.py  # ~1 min
python 04_smoke_buffer.py         # ~2 min
python 05_panel_assembly.py       # ~1 min
```

Or run all via orchestration script (once created):
```bash
python main.py  # Runs all stages with dependencies
```

---

## **Estimated Timeline**

- **Downloads**: 30-45 min (parallel, mostly waiting on IPUMS)
- **Processing**: 20 min (automatic)
- **Documentation**: 10 min (automatic)
- **Commit**: 5 min

**Total Week 1 time**: ~1.5 hours

---

## **Ready to Proceed?**

When downloads are complete, provide a status update here and I'll automatically execute the remaining 13 tasks.

*See `docs/DATA_DOWNLOAD_GUIDE.md` for step-by-step download instructions.*
