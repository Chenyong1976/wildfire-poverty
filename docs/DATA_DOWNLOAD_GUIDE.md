# Week 1: Data Download Guide

> **DEPRECATED (2026-08-15)**: This guide references the original county-level IPUMS microdata approach and an outdated ACS period selection. It is retained for audit purposes only.
> 
> **Use instead**: `docs/NHGIS_DOWNLOAD_GUIDE.md` (current) and `docs/DATA_ACQUISITION_CHECKLIST.md` (current).

**Status**: Superseded — do not follow these instructions.

---

## **Task #2: ACS Data from IPUMS** ⏱️ ~30 min

### **Steps**:

1. **Go to https://usa.ipums.org/** (register if needed; free account)
2. Login → Click **"SELECT DATA"**
3. **Survey selection**:
   - Check: "American Community Survey (ACS)"
   - Select samples: 
     - ACS 2007-2011 (5-year estimate)
     - ACS 2015-2019 (5-year estimate)
4. **Variable selection**:
   - Search/select:
     - POVERTY (poverty status)
     - HHINCOME (household income)
     - MIGRATE1 (residence 1 year ago)
     - EMPSTAT (employment status)
     - Add any demographic variables you need
5. **Geographic level**: County (all lower-48 states)
6. **Create extract**:
   - View extract → Customize (if needed)
   - Click "Submit"
7. **Download**:
   - Once ready (usually <1 hour), download as **CSV**
   - You'll get two files: one per survey year

### **Save as**:
- `data/raw/acs_extracts/acs_2011_extract.csv` (2007-2011)
- `data/raw/acs_extracts/acs_2019_extract.csv` (2015-2019)

---

## **Task #3: MTBS Fire Perimeters** ⏱️ ~10 min

### **Steps**:

1. **Go to https://www.mtbs.gov/**
2. Click **"Download"** (or "Data Download")
3. **Select**:
   - Fire perimeters (polygon shapefile)
   - All states (lower-48)
   - Years: 1984–2019
   - Format: Shapefile (.shp)
4. **Download** (typically 100–300 MB)
5. **Unzip** to `data/raw/mtbs_perimeters/`

### **Verify**:
- Should contain: `*.shp`, `*.shx`, `*.dbf`, `*.prj` files

---

## **Task #5: US County Boundaries** ⏱️ ~5 min

### **Steps**:

1. **Go to https://www.census.gov/cgi-bin/geo/shapefiles/index.php**
2. **Select**:
   - Year: 2012 (or latest available)
   - Layer: Counties
   - Download (shapefile)
3. **Unzip** to `data/raw/county_shapefiles/`
   - File should be named like: `tl_2012_us_county.shp`

### **Verify**:
- Contains: `*.shp`, `*.shx`, `*.dbf`, `*.prj` files
- ~3,100 counties when loaded

---

## **Task #4: WFP 2012 Raster** ✅ ALREADY AVAILABLE

No action needed. Found at:
```
../../wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/
```

---

## **USDA RUCC (Optional)** ⏱️ ~2 min

If you want to include Rural-Urban Continuum Code (optional matching covariate):

1. **Go to**: https://www.ers.usda.gov/webdocs/DataFiles/17749/
2. **Download**: `ruralurbancodes2013.xlsx`
3. **Save to**: `data/raw/ruralurbancodes2013.xlsx`

---

## **After Downloads Complete**

Once you have the files in place:

✅ Post here or in a message that downloads are done  
✅ I'll run the processing scripts (Tasks #6-14)

---

## **Troubleshooting**

**Q: IPUMS registration taking too long?**  
A: Try https://international.ipums.org/ or use Census Bureau's own tools as fallback.

**Q: MTBS file too large?**  
A: Download by region instead (Western states first), then merge later.

**Q: Can't find County boundaries?**  
A: Alternative: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line.html

---

**Timeline**: 
- Download all (parallel): ~30–45 min
- Once done, processing scripts run automatically (~20 min)

*Ready to start downloads? Begin with IPUMS (slowest) in parallel with MTBS & Census downloads.*
