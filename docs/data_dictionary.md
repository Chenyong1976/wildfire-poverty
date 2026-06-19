# Data Dictionary

## Analysis Sample (`analysis_sample.parquet`)

**Panel structure**: County × Year (unbalanced)

### Index Variables
| Variable | Type | Description |
|----------|------|-------------|
| `fips` | int | County FIPS code (5-digit) |
| `year` | int | Calendar year (2000–2020) |

### Outcome Variables
| Variable | Type | Source | Definition |
|----------|------|--------|-----------|
| `poverty_rate` | float | ACS (IPUMS) | Fraction of population below federal poverty line |
| `median_income` | float | ACS (IPUMS) | Median household income (2020 dollars) |
| `employment_rate` | float | ACS (IPUMS) | Fraction of civilian labor force employed |
| `per_capita_income` | float | BEA NIPA | Per capita income (2020 dollars) |

### Treatment Variables
| Variable | Type | Definition |
|----------|------|-----------|
| `treated` | int | 1 if county experienced large fire by year t, 0 otherwise |
| `treatment_year` | int | Year of first large fire (MTBS ≥1,000 acres); NA if never-treated |
| `relative_year` | int | Year relative to treatment (0 = year of fire, -1 = year before, 1 = year after) |

### Matching / Covariate Variables
| Variable | Type | Source | Definition |
|----------|------|--------|-----------|
| `whp_percentile` | float | USFS WHP (2014 or 2018) | County percentile in Wildfire Hazard Potential distribution (0–100) |
| `baseline_poverty_rate` | float | ACS 2000 | County poverty rate in year 2000 (pre-treatment) |
| `baseline_income` | float | ACS 2000 | Median household income in year 2000 (2020 dollars) |
| `baseline_population` | int | Census 2000 | County population in year 2000 |

### Geographic / Administrative Variables
| Variable | Type | Definition |
|----------|------|-----------|
| `county_name` | str | County name |
| `state` | str | State abbreviation (e.g., "CA", "OR") |
| `region` | str | Geographic region ("West Coast" or "Interior West") |

### Fire Exposure Variables (Optional)
| Variable | Type | Definition |
|----------|------|-----------|
| `n_large_fires` | int | Count of MTBS fires ≥1,000 acres occurring in county |
| `total_acres_burned` | float | Total acres burned in all fires (MTBS) |
| `max_fire_severity` | str | Maximum burn severity in any fire ("low", "moderate", "high", "increased_green") |
| `distance_to_nearest_fire` | float | Distance (km) to nearest fire perimeter (for control counties) |

---

## Raw Data Files

### ACS (IPUMS) Extract
**File**: `data/raw/acs_extracts/acs_2000_2020_county.csv` (or similar)

**Columns**:
- `fips`: County FIPS code
- `year`: Census year (2000, 2010, 2015, 2016, ..., 2020)
- `poverty`: Poverty rate
- `median_income`: Median household income (nominal)
- `employment_rate`: Employment rate
- (other demographic variables as needed)

**Notes**:
- 5-year ACS windows. Clarify year labeling (vintage).
- Account for Census disclosure avoidance (differential privacy 2020).

### MTBS Fire Perimeters
**File**: `data/raw/mtbs_perimeters/` (Shapefile or GeoJSON)

**Columns**:
- `Event_ID`: Unique fire identifier
- `Year`: Fire occurrence year
- `Acres`: Fire size in acres
- `geometry`: Fire perimeter polygon (WGS84)

**Notes**:
- 1984–2022 coverage; Western US fires.
- Minimum fire size: ~300 acres (varies by region).

### WHP (Wildfire Hazard Potential)
**File**: `data/raw/whp_rasters/` (GeoTIFF)

**Columns**:
- Grid cell values: WHP class (1–6, from low to very high hazard)

**Notes**:
- 270m resolution; three vintages (2014, 2018, 2020).
- Aggregate to county level via spatial overlay (mean or modal WHP class).

### County Boundaries
**File**: `data/raw/county_shapefiles/` (Shapefile)

**Columns**:
- `FIPS`: County FIPS code
- `NAME`: County name
- `geometry`: County boundary polygon (WGS84)

---

## Data Quality Notes

### Missingness
- **Income data**: May be missing or imputed in ACS for small counties (disclosure rules).
- **Fire data**: Smaller fires (<300 acres) may be underreported in MTBS.
- **WHP data**: Missing pixels in urban areas or outside Western US scope.

### Temporal Coverage
- **ACS**: 5-year windows (2000, 2010, 2015–2020). Annual data not available; must interpolate between Census years.
- **MTBS**: Annual 1984–2022; all years covered.
- **WHP**: Static snapshots (2014, 2018, 2020); not annual.

### Known Issues
- **Census disclosure avoidance** (2020 ACS onward): Differential privacy may inflate variance in small-area estimates.
- **TopCode** (income): ACS TopCodes income values above threshold (e.g., >$250k). Affects median income in high-income counties.
- **PUMA-to-county crosswalks**: ACS data via PUMA geographies may not align perfectly with county boundaries; verify crosswalks.
- **Smoke spillover**: County-level smoke exposure not directly measured; 150 km buffer is a proxy.

---

## Data Processing Steps

1. **Load & clean ACS**: Filter to Western US counties, 2000–2020. Handle TopCode, disclosure suppression. Convert nominal to real (2020 dollars).
2. **Load & assign treatment**: Match MTBS fires to counties via spatial overlay. Assign treatment year (first fire ≥1,000 acres).
3. **Load & aggregate WHP**: Aggregate rasters to county percentile rankings.
4. **Merge**: Combine ACS, fire treatment, and WHP by county-year.
5. **Restrict sample**: Drop smoke-exposed controls (150 km buffer). Keep treated and never-treated only.
6. **Create covariates**: Compute baseline (year 2000) poverty, income, population.
7. **Export**: Save as `analysis_sample.parquet`.

---

## Reproducibility

All data processing scripts are located in `src/data/`:
- `load_acs.py`: ACS data loading and cleaning
- `load_mtbs.py`: Fire perimeter processing and treatment assignment
- `load_whp.py`: WHP raster aggregation
- `build_analysis_dataset.py`: Master coordination script

Run via: `python -m src.data.build_analysis_dataset`
