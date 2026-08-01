# IPUMS ACS Download Guide

**Source**: https://www.ipums.org/ (free account required)  
**Data**: ACS 5-year tract-level estimates  
**Periods**: 2012, 2014, 2022, 2023 (required for single clean cohort design: fires 2015-2017, with pre-trend testing)

---

## Why IPUMS?

- **Consistency**: Harmonized variables across Census years (variable definitions change; IPUMS standardizes)
- **Tract-level**: Directly available at census tract resolution (not all Census API endpoints support tracts)
- **MOE included**: Margins of error provided for all estimates (critical for rural data quality screening)
- **Historical access**: Long time series in one place

---

## Step-by-Step Instructions

### 1. Create IPUMS Account (if needed)

1. Go to https://www.ipums.org/
2. Click "CREATE AN ACCOUNT" (free)
3. Fill in email, password, and registration details
4. Verify email
5. Log in

---

### 2. Create ACS Extract

1. In IPUMS dashboard, click **"CREATE A NEW EXTRACT"** or navigate to IPUMS USA
2. You will see the **Data Selection** page

#### Step 2a: Select Samples (ACS Survey Years)

On the left side, you will see a list of available datasets/surveys. Look for:

- **ACS 5-year samples** (labeled by final year: 2012, 2014, 2022, 2023)

Select **ALL FOUR**:

✓ ACS 2008-2012 5-year sample (labeled as "2012")  
✓ ACS 2010-2014 5-year sample (labeled as "2014")  
✓ ACS 2018-2022 5-year sample (labeled as "2022")  
✓ ACS 2019-2023 5-year sample (labeled as "2023")

**Critical note**: Do NOT select 1-year or 3-year samples. The project requires 5-year estimates only for rural data validity. Do NOT use 2017 ACS — the 2013-2017 window overlaps with the fire cohort (2015-2017) and is contaminated.

---

#### Step 2b: Select Geographic Level

1. Scroll down to **"Geographic levels"** section
2. Select **TRACT**
3. **Important**: Do NOT select county or state level

---

#### Step 2c: Select Variables

1. Click **"Select Variables"** button (or the "+ SELECT VARIABLES" link)
2. A variable search interface will appear

Search for and select the following variables (must have all three periods):

**POVERTY**:
- Search: `poverty status`
- Select: `Poverty Status (B17001)` or similar
  - Keep all sub-categories (this creates the binary poverty indicator)

**INCOME**:
- Search: `median household income`
- Select: `Median Household Income (B19013)`

**EMPLOYMENT**:
- Search: `employment status`
- Select: `Employment Status (B23025)`
  - Keep categories: total, employed, unemployed

**MIGRATION**:
- Search: `residence 5 years ago` or `residence 1 year ago`
- Select: `Residence 5 Years Ago (B07001)` — **IMPORTANT: Use 5-year window, not 1-year**

**GEOGRAPHIC IDENTIFIERS** (automatically included):
- State FIPS
- County FIPS
- Tract FIPS
- Geographic name

---

#### Step 2d: Filter to Lower-48 US States

1. Under **"Select Cases"**, click **"Select states/regions"**
2. **Deselect**:
   - Alaska (AK)
   - Hawaii (HI)
   - Puerto Rico (PR)
3. Keep all other states selected (lower-48)

---

#### Step 2e: Select Data Format

1. Under **"Data Format"**, select: **CSV** (comma-separated values)
2. Click **"Create Extract"**

---

### 3. Submit Extract and Download

1. Review your extract summary (should show: ACS 2012, 2014, 2022, 2023; tract-level; all 4 variable groups)
2. Click **"SUBMIT EXTRACT"** or similar button
3. IPUMS will email you when the extract is ready (usually within minutes)
4. Open the email and click the download link
5. A ZIP file will download containing:
   - `*.csv` — actual data (large file, ~250–350 MB per year for all lower-48 tracts)
   - `*.pdf` — codebook (variable definitions; save this for documentation)
   - `*.do` — Stata code for data import (not needed for this project)

---

### 4. Save Files to Project Directory

After downloading, extract the ZIP and save:

```
data/raw/acs_extracts/
├── acs_2012_tract_extract.csv    (from IPUMS ACS 2012, 2008-2012 window)
├── acs_2014_tract_extract.csv    (from IPUMS ACS 2014, 2010-2014 window)
├── acs_2022_tract_extract.csv    (from IPUMS ACS 2022, 2018-2022 window)
├── acs_2023_tract_extract.csv    (from IPUMS ACS 2023, 2019-2023 window)
└── ipums_acs_codebook.pdf        (variable definitions)
```

**File naming**: Name files exactly as above so the Python scripts can find them.

**Timing note**: 
- 2012 ACS (h = −2) = 3–6 years pre-fire (2008–2012 window)
- 2014 ACS (h = −1) = 1–4 years pre-fire (2010–2014 window); reference period for event study
- 2022 ACS (h = 0) = 1–4 years post-fire (2018–2022 window)
- 2023 ACS (h = +1) = 2–6 years post-fire (2019–2023 window)
- The 2022 and 2023 windows overlap (2019–2022 shared), which is standard in panel data
- The 2012 and 2014 windows overlap (2010–2012 shared), which allows the pre-trend test (β₋₂) to be independent

---

## Expected Data Format

After download, each CSV should contain approximately:

| Column | Format | Example |
|--------|--------|---------|
| STATEFP | 2-digit FIPS | "06" (California) |
| COUNTYFP | 3-digit FIPS | "001" |
| TRACTCE | 6-digit tract code | "000100" |
| NAME | Geographic name | "Census Tract 1, Alameda County, California" |
| B17001_001E | Poverty total | 5000 |
| B17001_001M | Poverty MOE | 250 |
| B19013_001E | Median income ($) | 65000 |
| ... (more variables) | ... | ... |

**Total tracts per year**: ~70,000 (national) × 4 years = 280,000 rows + header

**Total file size**: ~1.0–1.2 GB for all four years

---

## Verification Checklist

After downloading, verify:

- [ ] Four CSV files exist: `acs_2012_tract_extract.csv`, `acs_2014_tract_extract.csv`, `acs_2022_tract_extract.csv`, `acs_2023_tract_extract.csv`
- [ ] Each file has ~70,000–75,000 rows (one per tract)
- [ ] Each file has columns for: state FIPS, county FIPS, tract code, NAME, and all 4 variable groups
- [ ] Margins of error (MOE) columns present for all outcome variables
- [ ] No entire rows are null or zero
- [ ] Median income values are > 0 and < $500,000 (reasonable range)
- [ ] Poverty totals > 0

---

## Troubleshooting

### "I don't see the 5-year ACS samples"

IPUMS updates its data holdings regularly. As of 2026, ACS 2012, 2022, and 2023 (5-year) should all be available. If you see only 1-year or 3-year samples:

1. Refresh the IPUMS page
2. Check that you're in the "IPUMS USA" project, not another IPUMS project
3. Contact IPUMS support (support@ipums.umn.edu) if samples are unavailable

### "The download is very large (>1 GB)"

This is expected for all lower-48 US tracts across 3 ACS years. Ensure you have sufficient disk space.

### "I selected too many variables"

You can go back and deselect unnecessary ones, then resubmit. The PDF codebook will list all variables in your extract.

---

## Data Processing After Download

Once files are saved to `data/raw/acs_extracts/`, the Python script `code/01_build/03_acs_load.py` will:

1. Load each CSV file (2012, 2014, 2022, 2023)
2. Construct 11-digit GEOID from state/county/tract FIPS
3. Extract poverty rate, median income, employment, and net-migration indicators from Census Bureau variables
4. Screen for MOE > 30% of point estimate on poverty (drop invalid tracts)
5. Screen for population < 500 (drop small tracts)
6. Pivot to panel format (one row per tract-year)
7. Output: `data/processed/acs_2012_2014_2022_2023_tract_clean.parquet`

---

## Time Estimate

- Account creation: 5 minutes
- Extract creation: 10 minutes (one additional year adds ~30 seconds)
- Waiting for extract: 5–10 minutes
- Download: 15–25 minutes (slightly larger file due to 4 years)
- Saving files to project: 5 minutes

**Total**: ~45–50 minutes

---

## Contact / Support

- **IPUMS FAQ**: https://www.ipums.org/help
- **Census ACS documentation**: https://www.census.gov/programs-surveys/acs/guidance/estimates.html
- **Codebook help**: The PDF codebook in your extract explains all variables

---

## References

- IPUMS ACS documentation: https://usa.ipums.org/usa/acs.shtml
- Census tract definition: https://www.census.gov/topics/housing/housing-unit-estimation/about/census-tracts.html
- MOE interpretation: https://www.census.gov/content/dam/censusshared/library/publications/2018/acs/acs_general_handbook_2018.pdf
