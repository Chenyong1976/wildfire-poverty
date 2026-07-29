# Code/01_build: Data Assembly Scripts

**Purpose**: Download raw data and construct analysis dataset (`analysis_sample_final.parquet`).

**Execution order**:

```
1. 00_setup.py              ← Run first: create directories, check upstream data
2. 01_acs_load.py           ← Load ACS 2007-2011 and 2015-2019
3. 02_fire_treatment.py     ← Assign fire treatment cohorts
4. (03b_wfp_to_county.py)   ← Aggregate WFP 2012 raster to county (pending)
5. (02b_fire_history.py)    ← Pre-2012 fire history (pending)
6. 03_matching_covariates.py ← Assemble matching covariates
7. (04_smoke_buffer.py)     ← Create 100 km smoke exclusion list (pending)
8. (05_panel_assembly.py)   ← Final balanced panel (pending)
```

---

## **Data Sources & Setup**

### Before running scripts:

1. **IPUMS ACS Data**:
   - Go to https://usa.ipums.org/
   - Extract: Poverty, household income, migration, employment
   - Save to `data/raw/acs_extracts/` as:
     - `acs_2011_extract.csv` (ACS 2007-2011)
     - `acs_2019_extract.csv` (ACS 2015-2019)

2. **MTBS Fire Perimeters**:
   - Check if available in `wildfire-finance/data/raw/mtbs_perims/`
   - If not, download from https://www.mtbs.gov/
   - Save to `data/raw/mtbs_perimeters/`

3. **WFP 2012 Raster**:
   - Check if available in `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`
   - If not, download from https://www.landfire.gov/
   - Save to `data/raw/whp_rasters/wfp_2012/`

4. **County Boundaries**:
   - Download from https://www.census.gov/cgi-bin/geo/shapefiles/index.php
   - Select counties, all states
   - Save to `data/raw/county_shapefiles/`

5. **USDA RUCC** (optional but recommended):
   - Download from https://www.ers.usda.gov/webdocs/DataFiles/17749/ruralurbancodes2013.xls
   - Save to `data/raw/ruralurbancodes2013.xlsx`

---

## **Running the Scripts**

### **Option A: Run individually**
```bash
cd code/01_build
python 00_setup.py
python 01_acs_load.py
python 02_fire_treatment.py
# ... etc
```

### **Option B: Run from project root**
```bash
python -m code.build.00_setup
python -m code.build.01_acs_load
# ... etc
```

### **Option C: Run full pipeline** (when complete)
```bash
python -m code.main  # Runs all stages in sequence
```

---

## **Outputs**

Each script produces a `.parquet` file in `data/processed/`:

| Script | Output | Rows | Columns |
|--------|--------|------|---------|
| 01_acs_load | `acs_county_outcomes.parquet` | ~6,200 | 7 |
| 02_fire_treatment | `fire_treatment_assignment.parquet` | ~3,100 | 8 |
| 03b_wfp_to_county | `whp_2012_county.parquet` | ~3,100 | 3 |
| 02b_fire_history | `pre2012_fire_history.parquet` | ~3,100 | 3 |
| 03_matching_covariates | `matching_covariates_2012.parquet` | ~3,100 | 7 |
| 04_smoke_buffer | `smoke_buffer_100km.parquet` | ~3,100 | 2 |
| 05_panel_assembly | `analysis_sample_final.parquet` | ~11,000 | 20+ |

---

## **Dependencies**

```bash
pip install pandas numpy geopandas shapely rasterio openpyxl
```

---

## **Notes**

- All scripts assume **relative paths** from project root (wildfire-poverty-analysis/)
- Output `.parquet` files are **git-ignored** (see `.gitignore`)
- To re-run: Delete output file and re-run script
- See `docs/WEEK_1_DATA_ASSEMBLY_CHECKLIST.md` for detailed task breakdown

---

## **Troubleshooting**

**Q: "FileNotFoundError: ACS extract not found"**  
A: Download ACS from IPUMS and save to `data/raw/acs_extracts/acs_XXXX_extract.csv`

**Q: "MTBS shapefile not found"**  
A: Download from https://www.mtbs.gov/ or symlink from wildfire-finance

**Q: "RUCC file not found"**  
A: Optional—script will continue with NaN values for RUCC

**Q: Memory error (large raster operations)**  
A: Reduce resolution or process state-by-state

---

For detailed instructions, see `docs/WEEK_1_DATA_ASSEMBLY_CHECKLIST.md`.
