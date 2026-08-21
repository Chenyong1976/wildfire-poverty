# Research Plan: Wildfire Impact on Poverty and Economic Outcomes

**Last Updated**: 2026-08-16 (In-migration mechanism decomposition added; estimation complete)  
**Principal Investigator**: [Your Name]  
**Project Directory**: `~/wildfire-poverty-analysis/`

---

## 1. Research Question & Motivation

### Primary Question
**How do large wildfires (≥1,000 acres) causally affect poverty rates, household incomes, net migration, and employment in US census tracts? What role does population displacement play in these effects?**

### Motivation
Wildfire frequency and severity have increased dramatically across the US over recent decades, yet causal empirical evidence on economic impacts—particularly distributional effects on poverty—remains limited. Most prior work focuses on Western states, county-level aggregation (which masks within-county heterogeneity), or health/property outcomes rather than poverty. This study shifts to **national census-tract resolution** using **raster-based spatial matching** (USFS WHP 2012 at 270m resolution) to identify treated and control tracts with precision, improving both statistical power and causal identification. We examine distributional impacts across all lower-48 states and explicitly model net migration as a mediating mechanism: if wildfires displace lower-income households, tract poverty rates may change compositionally even if individual incomes fall unchanged.

### Contribution
- **Empirical**: First **national, tract-level** quasi-experimental study of wildfire poverty impacts (not county-level or Western-only)
- **Spatial precision**: Leverage 270m resolution WHP raster for matching, capturing within-county hazard heterogeneity
- **Mechanism**: Explicit descriptive decomposition of poverty effects via net migration (income loss vs. compositional change)
- **Design quality**: Single clean cohort (fires 2015–2017) eliminates overlapping-window biases that plague multi-cohort designs
- **Policy**: Estimates inform disaster relief design, climate adaptation, migration assistance, and hyper-local vulnerability assessments

---

## 2. Identification Strategy

### Design: Single Clean Cohort + Simple Difference-in-Differences

**Core insight**: A single, **non-overlapping fire window with multiple post-fire measurement periods** provides clean causal identification without the mutual-exclusivity violations of overlapping-cohort staggered DiD.

#### Treatment Definition

**Fire cohort**:
- **First large fire year**: 2015, 2016, or 2017 (single 3-year window)
- **Cohort assignment (g)**: g=2016 if tract has first fire ∈ {2015, 2016, 2017}; g=0 (never-treated) otherwise
- **Fire definition**: MTBS fire polygon ≥1,000 acres with any spatial overlap with tract boundary
- **Extensive margin**: Binary indicator (any fire vs. none) — primary treatment
- **Intensive margins** (robustness): 
  - Burned share: % of tract area within fire perimeters (continuous, [0, 100])
  - Fire count: Number of fires in cohort window per tract (0, 1, 2, 3+)

#### Sample Definition

**Treated tracts** (g=2016):
- First large fire (MTBS ≥1,000 acres) in 2015–2017
- Expected: ~600–800 tracts nationally (across all lower-48 states)

**Never-treated (control) tracts** (g=0):
- No large fire in entire period 2013–2023 (broader window ensures no recent fire influence)
- AND outside 100 km buffer around all MTBS fire perimeters (smoke spillover exclusion)
- Expected: ~35,000–40,000 tracts after filtering

**Excluded groups**:
- Tracts with fires 2013–2014 or 2018–2023 (no overlap with g=2016 cohort)
- Tracts within 100 km smoke buffer (avoid smoke exposure confounding)
- Tracts with poverty denominator < 100 (AX7AA + AX7AB < 100; insufficient base for rate estimation)
- Tracts with population < 500 (ACS reliability threshold, especially rural)

#### Temporal Structure

**Six measurement periods** (ACS 5-year estimates) — three pre-treatment for robust parallel-trends testing, three post-treatment for trajectory estimation:

| Period | ACS Vintage | Window | Relative to Fires | Event-study h |
|--------|-------------|--------|------------------|---------------|
| **Pre 1** | ACS 2010 | 2006–2010 | Far pre-fire | h = −3 |
| **Pre 2** | ACS 2012 | 2008–2012 | Pre-fire | h = −2 |
| **Reference** | ACS 2014 | 2010–2014 | Reference (normalized to 0) | h = −1 |
| **Post 1** | ACS 2022 | 2018–2022 | 1–4 years post-fire | h = 0 |
| **Post 2** | ACS 2023 | 2019–2023 | 2–6 years post-fire | h = +1 |
| **Post 3** | ACS 2024 | 2020–2024 | 3–7 years post-fire | h = +2 |

**Design advantages**:
- Three pre-periods provide two independent pre-trend tests (β₋₃ and β₋₂) with h = −1 as reference
- Three post-periods allow trajectory estimation: fade, persist, or amplify
- Primary pre-trend tests are h = −2 and h = −1 (both on 2010 tract boundaries); h = −3 is an auxiliary extended pre-trend check (see boundary note below)

**Tract boundary harmonization — approach and fallback**:

ACS 2010 uses 2000-vintage tract boundaries; ACS 2012–2014 use 2010-vintage boundaries; ACS 2022–2024 use 2020-vintage boundaries. NHGIS Standardized (S) time series tables do not exist for ACS data at the tract level (only decennial census 1990/2000/2010/2020 is available as standardized). The nominal (N) time series is the only NHGIS ACS option.

**Primary approach — nominal balanced panel**: Use the NHGIS nominal time series and restrict to tracts present in all six periods. NHGIS nominal integration retains a tract only when its code is in use consistently across years; dropped tracts are those split, merged, or renumbered at the 2000→2010 or 2010→2020 boundary change. The balanced panel retains ~60,000–70,000 of ~97,000 tracts. Western rural and peri-urban tracts — where nearly all MTBS fires occur — have low boundary-change rates, so treated-tract retention is expected to be high (>95%).

**Required diagnostic** (run after `02_fire_treatment.py`):
```python
pct_treated_retained = treated_tracts["NHGISCODE"].isin(balanced_panel["NHGISCODE"]).mean()
# If >= 0.95: nominal balanced panel is adequate; document and proceed.
# If < 0.95: implement fallback crosswalk (see below).
```
Report retention rate in the paper's data section, broken down by RUCC.

**Fallback — Census 2010–2020 Tract Relationship File** (implement only if diagnostic fails):
Apply `tab20_tract20_tract10_natl.zip` (Census Bureau, freely available) to aggregate ACS 2022/2023/2024 counts from 2020 boundaries back to 2010 definitions using `POPPCT_20` weights. Aggregate counts (not rates), then recompute rates from aggregated numerator and denominator. For ACS 2010 (2000 boundaries), apply the 2000–2010 relationship file or drop h = −3 from the main specification and retain it as an appendix robustness check.

**Role of h = −3 (ACS 2010)**:  
ACS 2010 is on 2000-vintage boundaries, which differ from the 2010-vintage used by h = −2 and h = −1. Under nominal integration, only tracts with consistent codes across all three decennial definitions are retained, which is a stricter requirement. Treat h = −3 as a secondary pre-trend check (report in appendix or as an additional coefficient alongside the main event-study plot). The two primary pre-trend tests are h = −2 and h = −1, which share 2010 boundary definitions and provide clean parallel-trends evidence.

#### Control Group Construction

**Matching strategy overview**: Two complementary matching approaches are implemented. The primary approach is propensity-score inverse-probability weighting (PS-IPW), using a reweighted control group in the main TWFE estimator. As an alternative, coarsened exact matching (CEM) on WFP quintiles is applied to a CEM-matched subsample with OLS, providing a robustness check under different parametric assumptions.

**A. Propensity-score inverse-probability weighting (PS-IPW)**:

1. **Propensity score model** (logistic, matching on pre-treatment covariates):
   $$\Pr(\text{Treated} | X) = \Lambda(\alpha + X \beta)$$
   
   Where $X$ includes:
   
   **WFP 2014 raster summaries** (primary matching covariate; 270m resolution, ESRI Grid, EPSG:5070; predetermined before the 2015 fire season). Three tract-level summaries capture distinct facets of wildfire hazard — all three are included in the propensity score model and reported in the covariate balance table:
   - *Mean WFP 2014 percentile* (0–100 across pixels intersecting the tract): the primary gradient along which treated and control tracts differ. The observed normalized difference on this variable is **0.43**, exceeding the Imbens (2015) threshold of 0.25 for reliable regression-adjustment-based balance, motivating both caliper trimming (§A.3 below) and the CEM robustness check (§B below).
   - *% tract area per WFP hazard quintile* (Q1–Q5; five indicators summing to 100%): accounts for within-tract heterogeneity in hazard. Two tracts with identical mean WFP can have very different risk profiles if one has a bimodal distribution (low- and high-hazard zones) while the other is uniformly moderate. Quintile shares capture this dispersion independently of the mean.
   - *Distance from tract centroid to nearest pixel with WFP > 75th percentile* (km): captures proximity to high-hazard zones outside the tract boundary. Fire is spatially continuous — tracts adjacent to high-hazard pixels face spillover risk even if their own mean WFP is moderate.
   
   **WFP 2012 raster summaries** (robustness check only): Identical tract-level summaries computed from the 2012 WFP vintage are included in sensitivity specifications to assess whether ATT estimates and balance quality are sensitive to the choice of hazard raster vintage. WFP 2012 is further predated from treatment but may capture longer-run structural hazard patterns.
   
   **Pre-2013 fire history**: Any fire 1984–2012 (binary); log total acres burned 1984–2012 (continuous, log(acres + 1)).
   
   **Pre-treatment socioeconomic covariates** (2012 ACS, tract-level):
   - Poverty rate, median household income, population density
   - % age 65+, % race/ethnicity groups (White, Black, Hispanic, Asian)
   
   **RUCC 2013**: County-level rural-urban continuum code (1 = large metro core to 9 = most remote rural), merged to tracts via county FIPS. RUCC is a key matching covariate because wildfire occurrence is strongly correlated with rurality, and rural areas differ systematically in economic structure, labor market depth, and population mobility — all of which are relevant to the outcome mechanisms of interest.

2. **Inverse-probability weights**:
   - Treated tracts: $w_i = 1$
   - Control tracts: $w_i = \hat{e}_i / (1 - \hat{e}_i)$ where $\hat{e}_i$ = estimated propensity score
   - Trim at 99th percentile to stabilize variance

3. **Caliper trimming** (to address the high normalized difference in mean WFP 2014):
   The normalized difference of 0.43 between treated and never-treated tracts on mean WFP 2014 implies that propensity-score reweighting may extrapolate substantially outside the common support region. To restrict estimation to comparable tracts, we apply a propensity-score caliper following Cochran & Rubin (1973):
   - Estimate propensity score $\hat{e}_i$ for all tracts via the logistic model above
   - Drop control tracts with $\hat{e}_i$ below $\min(\hat{e}_{\text{treated}}) - c$ or above $\max(\hat{e}_{\text{treated}}) + c$, where $c = 0.20 \times \text{SD}(\hat{e}_{\text{treated}})$ (baseline caliper)
   - Report the share of control tracts trimmed and the effective sample size (ESS) before and after caliper trimming
   - Caliper sensitivity: vary $c \in \{0.10, 0.20, 0.25\}$ standard deviations; report ATT under each

4. **Balance diagnostics** (reported for all matching variables):
   - Standardized mean differences (SMD) before and after IPW reweighting, for mean WFP 2014 percentile, all five quintile shares (Q1–Q5), distance to high-hazard pixel, pre-2013 fire history, 2012 ACS socioeconomic covariates, and RUCC
   - Target: SMD < 0.10 for all covariates post-weighting
   - Report ESS of reweighted control group before and after caliper trimming
   - Plot propensity score distributions (treated vs. control, pre/post reweighting)

**B. Coarsened exact matching (CEM) on WFP quintiles**:

As a non-parametric alternative that makes no distributional assumptions about the propensity score:
1. Coarsen WFP 2014 into quintile bins (Q1–Q5) based on the national distribution of mean WFP 2014 percentile across all tracts
2. Optionally add a second coarsening dimension: pre-2013 fire history (binary: any fire 1984–2012), yielding a 10-cell matching grid (5 quintile bins × 2 fire-history cells)
3. Exactly match each treated tract to all control tracts in the same coarsened cell; drop unmatched cells
4. Run OLS with tract and period fixed effects on the CEM-matched sample (no IPW weights)
5. Report CEM-OLS ATT alongside IPW-TWFE in the main robustness table; large divergence flags propensity-score model misspecification or failure of common support

#### Estimating Equations

**Main specification** (two post-fire periods):

$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \beta \cdot \text{Treated}_i \cdot \text{Post}_t + X_{i,2012} \gamma + \epsilon_{i,t}$$

Where:
- $i$ = census tract (indexed 1 to ~40,700)
- $t$ = ACS period ∈ {2012, 2022, 2023}
- $\text{Treated}_i$ = 1 if first fire 2015–2017, 0 if never-treated
- $\text{Post}_t$ = 1 if t ∈ {2022, 2023}, 0 if t = 2012
- $\alpha_i$ = tract fixed effects (captures time-invariant unobservables)
- $\lambda_t$ = period fixed effects (captures time trends common to all tracts)
- $X_{i,2012}$ = vector of pre-treatment covariates (WFP raster summaries, fire history, 2012 ACS demographics)
- $\epsilon_{i,t}$ = error term, clustered by county (parent geography of tract)
- Weights: inverse-probability weights $w_i$ from PS-IPW matching

**Event-study specification** (six periods, h = −1 is reference):

$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \in \{-3,-2,0,+1,+2\}} \beta_h \cdot \text{Treated}_i \cdot \mathbb{1}[t = t_h] + X_{i,2014} \gamma + \epsilon_{i,t}$$

Where $h$ indexes relative time:
- $h = -3$: ACS 2010 (far pre-trend test)
- $h = -2$: ACS 2012 (pre-trend test)
- $h = -1$: ACS 2014 (reference period, coefficient normalized to zero — omitted from sum)
- $h = 0$: ACS 2022 (1–4 years post-fire)
- $h = +1$: ACS 2023 (2–6 years post-fire)
- $h = +2$: ACS 2024 (3–7 years post-fire)

**Interpretation**:
- Pre-trend test: β₋₃ ≈ 0 and β₋₂ ≈ 0 provide strong parallel-trends evidence (Roth 2022)
- $\beta_0$, $\beta_1$, $\beta_2$ = medium-run and long-run ATT
- Trajectory: $\beta_2 \approx \beta_0$ → persistent; $\beta_2 > \beta_0$ → amplifying; $\beta_2 < \beta_0$ → decaying
- Baseline covariates $X_{i,2014}$ use the ACS 2014 period (h = −1), the closest pre-treatment ACS period

**Robustness variants**:

1. **Unweighted TWFE** (no matching weights): Standard two-way fixed effects without IPW weights. Comparison to IPW-TWFE quantifies the selection-on-observables bias that matching corrects. Large divergence (e.g., opposite sign or substantially larger magnitude) suggests high residual confounding in the unweighted estimate.

2. **IPW-TWFE** (primary): Reweighted by inverse-probability weights from PS-IPW model with caliper trimming. Main specification reported throughout.

3. **CEM-OLS**: OLS on CEM-matched sample with tract and period FE; no IPW weights. Non-parametric robustness to propensity-score model form.

4. **Regression adjustment** (include covariates as regressors instead of matching):
   $$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \beta \cdot \text{Treated}_i \cdot \text{Post}_t + X_{i,2012} \gamma + \text{State}_i \cdot \lambda_t + \epsilon_{i,t}$$
   (Add state × period fixed effects to absorb region-specific time trends)

5. **Intensive margin** (dose-response by burned share):
   $$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \beta \cdot \text{BurnShare}_i \cdot \text{Post}_t + X_{i,2012} \gamma + \epsilon_{i,t}$$
   Where $\text{BurnShare}_i$ = % of tract area burned in 2015–2017 fires (continuous [0, 100])

#### Threats to Identification & Mitigation

| Threat | Mechanism | Mitigation | Robustness |
|--------|-----------|-----------|-----------|
| **Selection bias** | High-hazard/poor tracts experience fires endogenously | PS-IPW matching on WFP 2014 raster (predetermined before 2015 fire season) + caliper trimming (normalized diff = 0.43) + pre-2013 fire history + RUCC | SMD < 0.10 all covariates; CEM on WFP quintiles as alternative estimator; WFP 2012 vintage as robustness |
| **Smoke spillover** | Control tracts exposed to smoke from treated fires | 100 km buffer exclusion from controls | Vary 50 km, 150 km; check if ATT stable |
| **Parallel trends** | Treated and control tracts follow different trends absent fires | Pre-treatment covariate balance; placebo test (assign fires to pre-2013, test ATT ≈ 0) | Inspect pre-treatment balance; run falsification test |
| **Temporal confounds** | 2015–2017 fires coincide with region-specific shocks (e.g., local economic downturns, housing bubbles) | State × period FE; census division × period FE | Report results with and without regional controls |
| **Migration composition** | Tract poverty changes both from income loss AND selective out-migration | Descriptive decomposition: estimate ATT on net migration separately, then estimate conditional effect on poverty | Mediation analysis (§4.2); label as descriptive, not causal |
| **Measurement error** | ACS tract-level estimates have large MOE, especially rural | Drop tracts with poverty denominator < 100 (AX7AA + AX7AB); flag tracts where count MOE > 30% of count for sensitivity analysis (note: 90%+ of tracts exceed this threshold — tract-level ACS poverty counts typically have MOE ~50% of count) | Robustness: exclude high-MOE tracts (MOE/count > 0.5) |
| **Effect heterogeneity** | Fires affect different tracts differently (by poverty, region, fire severity) | Report extensive margin (any fire) and intensive margins separately; subgroup analysis | Sun & Abraham (2021) heterogeneity-robust estimator; subgroup ATTs by poverty quintile, region, WFP hazard |

---

## 3. Data & Sample Definition

### Sample Frame

- **Geographic scope**: All lower-48 US states (~70,000 census tracts; harmonized to 2020 boundaries via NHGIS standardized series)
- **Time period**: ACS 5-year estimates, **six periods**:
  - Pre-treatment: 2010 (h = −3), 2012 (h = −2), 2014 (h = −1, reference)
  - Post-treatment: 2022 (h = 0), 2023 (h = +1), 2024 (h = +2)
- **Unit of analysis**: Census tract (NHGIS standardized geography; ~70,000–84,000 tracts depending on vintage)
- **Expected sample after screening**: ~700 treated + ~40,000 never-treated = **~40,700 tracts total**

### Outcome Variables

| Outcome | Source | Definition | Notes |
|---------|--------|-----------|-------|
| **Poverty rate** (primary) | NHGIS time series standardized | % population below federal poverty line | 5-year estimates essential for rural reliability |
| **Median HH income** | NHGIS time series standardized | Median household income (nominal; deflate to 2020$ using CPI-U annual averages (FRED CPIAUCSL) in build scripts; deflate by final year of each ACS window) | Secondary outcome |
| **Employment rate** | NHGIS time series standardized | B84AD / B84AC: civilian employed / civilian labor force (16+); excludes Armed Forces and persons not in labor force | Captures labor market adjustment |
| **Net-migration rate** (mediator) | NHGIS B07003 source table (all 6 periods) | In-migration rate proxy: (total − same house 1 yr ago) / total; measures arrivals only (out-migration not observable from ACS) | Descriptive decomposition mechanism |

**In-migration mechanism decomposition** — the +0.92 pp in-migration rate ATT is ambiguous: the rate = movers / population can rise from more arrivals (numerator) or from population loss (denominator). The following outcomes decompose this:

| Outcome | Source | Definition | Role |
|---------|--------|-----------|------|
| **log(total population)** | NHGIS B01003 (already in panel) | log of total tract population | Denominator test: population loss → rate rise mechanically |
| **log(mover count)** | NHGIS B07003 (already in panel) | log(total − same house 1 yr ago) = absolute count of movers | Numerator test: genuine increase in arrivals |
| **Owner-occupancy rate** | NHGIS B25003 (medium priority — one ACS table) | Owner-occupied units / total occupied housing units | Compositional channel: fire displaces owners; more-mobile renters remain → rate rises mechanically |
| **Vacancy rate** | NHGIS B25002 (medium priority — same ACS table) | Vacant units / total housing units | Housing destruction channel: destroyed units inflate vacancy and reduce resident base |

**Interpretation matrix**:

| log(pop) | log(movers) | Interpretation |
|----------|-------------|----------------|
| Negative | Near zero | Denominator effect: displacement/out-migration; no genuine inflow increase |
| Near zero | Positive | Numerator effect: genuine arrival increase (reconstruction workers, recovery migration) |
| Negative | Negative, smaller | Net displacement with partial inflow — decompose magnitudes |

**IRS SOI county migration (optional)** — ACS cannot measure out-flows from a tract. As an optional supplement, the IRS Statistics of Income (SOI) publishes annual county-to-county migration tables from tax returns, including gross in-flows and out-flows. These are county-level (not tract-level) but directly answer the out-migration question. Link treated tracts to their counties and estimate whether county-level out-flows rose post-fire. See §4.4 for implementation notes.

All outcomes available at **tract level only for 5-year estimates**. No 1-year or 3-year estimates used (rural data quality constraint). NHGIS time series standardized (S) variant is required to handle tract boundary changes across the 2010–2024 study window.

### Treatment Definition

| Dimension | Definition |
|-----------|-----------|
| **Extensive margin** (primary) | Binary: first fire (MTBS ≥1,000 acres) in 2015–2017 vs. never-treated |
| **Intensive margin 1** | Burned share: % of tract area within fire perimeters (continuous [0, 100]) |
| **Intensive margin 2** | Fire count: number of fires in 2015–2017 per tract (0, 1, 2, 3+) |
| **Fire definition** | MTBS perimeter ≥1,000 acres, any spatial overlap with tract boundary |

### Data Sources & Acquisition

| Variable | Source | Format | Acquisition Status |
|----------|--------|--------|-------------------|
| Poverty, income, employment | NHGIS time series **nominal (N)**, tract — only ACS option (standardized S not available for ACS at tract level) | CSV (NHGIS extract) | ✓ `data/raw/acs_extracts/nhgis_inc_pov_emp/nhgis0012_ts_nominal_tract.csv` |
| Net migration proxy | NHGIS B07003 source table, tract, all 6 periods | CSV (NHGIS extract) | ✓ `data/raw/acs_extracts/nhgis_mig/nhgis0013_ds*_tract.csv` (6 files) |
| Fire perimeters & treatment assignment | MTBS (USGS) | Shapefile | ✓ Linked from wildfire-finance |
| WFP 2014 (**primary matching**) | USFS LANDFIRE | 270m raster, EPSG:5070; predetermined before 2015 fire season | ⏳ Download from USFS LANDFIRE; compute tract summaries (mean percentile, quintile shares, distance to high-hazard pixel) |
| WFP 2012 (robustness check) | USFS LANDFIRE | 270m raster, EPSG:5070 | ✓ Linked from wildfire-finance; compute same three tract-level summaries for sensitivity specs |
| Pre-2013 fire history | MTBS 1984–2012 | Shapefile | ✓ Linked from wildfire-finance |
| RUCC 2013 | USDA ERS | County-level codes | ⏳ To parse from wildfire-finance |
| Tract shapefiles (for fire-tract spatial join) | Census TIGER 2014 (NHGIS) | Shapefile | ✓ `data/raw/acs_extracts/nhgis2014Tiger/nhgis0012_shapefile_tl2014_us_tract_2014.zip` |
| CPI-U (income deflator) | FRED series CPIAUCSL (BLS); monthly; base 1982–84=100 | CSV | ✓ `data/raw/CPIAUCSL.csv`; retrieved 2026-08-15 from https://fred.stlouisfed.org/series/CPIAUCSL; annual averages computed in build script |
| Owner-occupancy & vacancy rates | NHGIS B25002/B25003 source tables, tract, all 6 periods | CSV (NHGIS extract) | ⏳ Medium priority — add to NHGIS extract; same extract workflow as B07003 migration tables |
| IRS SOI county migration flows | IRS Statistics of Income, county-to-county migration tables (public, annual) | CSV | ⏳ Optional — gross in/out county flows; download from IRS.gov SOI tax stats; county-level only |

### Data Quality Screening

- **ACS 5-year estimates only**: Never use 1-year or 3-year estimates (rural validity constraint)
- **MOE threshold**: Drop tracts if poverty denominator (AX7AA + AX7AB) < 100; flag but retain tracts where poverty count MOE > 30% of count (tract-level ACS poverty counts typically have MOE ~50% of count — a hard 30% drop threshold would remove ~90% of tracts)
- **Population minimum**: Drop tracts with population < 500
- **Documentation**: Report N tracts dropped by each screen, broken down by urbanicity (RUCC)
- **Expected final sample**: ~60,000–70,000 tracts (balanced panel, all 6 periods) × 6 periods = ~360,000–420,000 observations; after PS-IPW control group construction, analysis uses ~700 treated + ~40,000–50,000 controls

---

## 4. Methods: Implementation Roadmap

### Phase 1: Data Acquisition & Raster Processing (Weeks 1–2)

**Deliverables**:
- `acs_2012_2022_2023_tract_clean.parquet`: ACS outcomes (poverty, income, employment, migration) for 3 periods, ~70k tracts, post-MOE screening
- `fire_treatment_assignment_tract.parquet`: Treatment cohort (g=2016 or g=0), extensive & intensive margins, ~70k tracts
- `whp_2014_tract_raster_summaries.parquet`: Tract-level WFP 2014 raster summaries (mean percentile, quintile shares Q1–Q5, distance to high-hazard pixel)
- `whp_2012_tract_raster_summaries.parquet`: Same summaries computed from WFP 2012 raster (robustness check)
- `matching_covariates_2012_tract.parquet`: Pre-treatment covariates (2012 ACS demographics, fire history, RUCC)
- `smoke_buffer_100km_tract.parquet`: Smoke exclusion flags
- `analysis_sample_final_tract.parquet`: Unbalanced panel after all screens (~40k–50k tracts × 3 periods)

**Scripts**: `code/01_build/01_*.py` through `07_*`

### Phase 2: PS-IPW Matching & Balance Diagnostics (Weeks 3–4)

**Deliverables**:
- `ipw_weights_tract.parquet`: Propensity-score inverse-probability weights per tract
- Balance diagnostics: SMD < 0.10 all covariates post-IPW
- Effective sample size (ESS) of reweighted control group
- Propensity-score density plots (treated vs. control, pre/post reweighting)

**Script**: `code/02_matching/01_ps_matching.R`

### Phase 3: Main DiD Estimation & Event-Study (Weeks 4–6)

**Deliverables**:
- `main_att_estimates.csv`: ATT point estimate + 95% CI (bootstrap 1,000 reps), all four outcomes
- `event_study_coefficients.csv`: $\beta_h$ for h ∈ {−1, 0, +1}, all outcomes
- Event-study plots (poverty, income, employment, migration) with 95% CIs
- Aggregate ATT with interpretation

**Script**: `code/03_analysis/01_cs_main.R`, `02_event_study.R`

### Phase 4: Mediation/Decomposition & Robustness (Weeks 6–8)

**Deliverables**:
- Descriptive decomposition of poverty effect via net migration (indirect vs. direct)
- Robustness table: ATT across ≥8 specifications (smoke radius, fire threshold, MOE cutoff, regional FE, estimator, etc.)
- Heterogeneous effects by baseline poverty, region, WFP hazard
- Sun & Abraham (2021) comparison
- Placebo falsification test (pre-2013 fires)

**Scripts**: `code/03_analysis/03_mediation.R`, `04_robustness.R`, `05_heterogeneity.R`

### Phase 4.4: In-migration Mechanism Decomposition (after main estimation)

The primary result is a +0.92 pp in-migration rate ATT. The rate = movers / population, so this could reflect more arrivals, fewer residents, or both. This phase decomposes the effect and documents channels.

**Priority 1 — Immediate (no new data)**: Both components are already in the ACS panel via B07003/B01003.

Add to `code/03_analysis/01_did_estimation.py`:
```python
# Derive from existing B07003 columns
panel["log_pop"] = np.log(panel["total_pop"].clip(lower=1))
panel["log_mover_count"] = np.log((panel["total_pop"] - panel["same_house"]).clip(lower=1))
```
Estimate the TWFE event study on `log_pop` and `log_mover_count` alongside existing outcomes. Interpret the coefficients jointly using the matrix in §3.

**Priority 2 — Medium (one ACS table)**: Request B25002 (vacancy status) and B25003 (tenure) from NHGIS for the same 6 periods as the B07003 extraction. Compute:
```python
panel["owner_occ_rate"] = owner_occupied / total_occupied   # from B25003
panel["vacancy_rate"]   = vacant / total_housing_units      # from B25002
```
Estimate TWFE event study on both. Owner-occupancy decline + vacancy increase → housing destruction / compositional sorting channel. Target: add to `code/01_build/01_acs_nhgis_load.py` during next NHGIS extract.

**Priority 3 — Optional (new data source)**: IRS Statistics of Income county-to-county migration tables provide annual gross in-flows and out-flows by county from tax returns. Steps:
1. Download county migration files from IRS.gov SOI (public; available ~2 years after tax year).
2. Identify counties containing treated tracts.
3. Estimate DiD on county-level out-flow rates using the same fire cohort (2015–2017). Note: county-level analysis sacrifices within-county variation; treat as supplementary evidence only.
4. Script: `code/03_analysis/05_irs_outmigration.py` (create when data available).

**Deliverables for this phase**:
- Updated `results/event_study_coefs.csv` with `log_pop` and `log_mover_count` coefficients
- Figure: three-panel event study (in_migration_rate, log_pop, log_mover_count) displayed together
- Table (decomposition): ATT for all three with interpretation
- If B25002/B25003 extracted: two additional event-study plots (owner-occupancy, vacancy)
- If IRS SOI obtained: county-level out-migration robustness table

### Phase 5: Output Generation & Visualization (Week 8)

**Deliverables**:
- Publication-ready tables (LaTeX + CSV): balance, main results, robustness, heterogeneity
- Publication-ready figures (300 DPI): event-study plots, PS density, geographic map, robustness sensitivity
- Data dictionary with all variable definitions and sources

**Script**: `code/04_output/01_tables.R`, `02_figures.py`

---

## 5. Writing & Publication Strategy

### Target Outlets
*Journal of Urban Economics*, *Regional Science and Urban Economics*, *American Economic Journal: Applied Economics*

### Paper Structure (Refined for Single Cohort)

| Section | Length | Key Elements |
|---------|--------|-------------|
| **I. Introduction** | 2–3 pp | Hook (rising fires); gap (tract-level, poverty focus); RQ; contribution (first national tract-level study, raster matching, migration mechanism) |
| **II. Institutional Background** | 1–1.5 pp | U.S. wildfire trends; federal relief (FEMA IA/PA, SBA); WFP policy use |
| **III. Literature Review** | 1.5–2 pp | Wildfire economics; disaster-poverty links; migration; causal inference methods |
| **IV. Data & Sample** | 2–2.5 pp | Sample definition (fires 2015–2017, ~700 tracts); ACS 5-year; data sources; summary stats (Table 1a/1b balance) |
| **V. Empirical Strategy** | 2–2.5 pp | Single clean cohort design (advantage over overlapping-window designs); estimand (ATT); DiD equations; threats & mitigations (Table 2) |
| **VI. Results** | 3–4 pp | Main ATT table (Table 3); event-study plot (Figure 2); mediation results (Table 4); heterogeneity (Table 5); economic magnitude |
| **VII. Robustness** | 2–2.5 pp | Robustness table (Table 6) organized by threat; findings stable/sensitive; Sun-Abraham check |
| **VIII. Discussion & Limitations** | 1.5–2 pp | Mechanisms (income vs. migration); scope (MTBS >1k acres); temporal window (medium-run only); open questions |
| **IX. Conclusion** | 0.5 pp | Restate finding; policy implication (disaster relief design); hedged language |

### Table & Figure Checklist

- **Table 1a**: Pre-treatment balance (pre-IPW): treated vs. control means and SDs for all matching variables: mean WFP 2014 percentile, WFP 2014 quintile shares (Q1–Q5), distance to nearest high-hazard pixel, pre-2013 fire history, 2012 ACS poverty rate/income/demographics, and RUCC
- **Table 1b**: Post-treatment balance (post-IPW with caliper): SMD for all matching variables listed above; ESS before and after caliper trimming; density plots of propensity-score distributions
- **Table 2**: Threats to identification (summary)
- **Table 3**: Main ATT estimates (all 4 outcomes, point + CI)
- **Table 4**: In-migration mechanism decomposition — ATT on in_migration_rate, log_pop, log_mover_count side by side; joint interpretation of numerator vs. denominator
- **Table 4a** *(medium priority)*: Housing channel — ATT on owner-occupancy rate and vacancy rate; requires B25002/B25003 extraction
- **Table 5**: Heterogeneous effects (by poverty quintile, region, WFP hazard)
- **Table 6**: Robustness summary (smoke radius, MOE threshold, fire threshold, estimator, regional FE, etc.)
- **Table 7** *(optional)*: IRS SOI county out-migration robustness — requires separate data pull
- **Figure 1**: Geographic map (fires, treated tracts, smoke buffer)
- **Figure 2**: Event-study plot (poverty, primary outcome) — h ∈ {−3, −2, 0, +1, +2}
- **Figure 3**: Event-study plot (income, secondary outcome)
- **Figure 4**: Three-panel event study — in_migration_rate, log_pop, log_mover_count (mechanism decomposition)
- **Figure 5** *(medium priority)*: Two-panel event study — owner-occupancy rate, vacancy rate
- **Figure 6**: Propensity-score density (treated vs. control, pre/post IPW)

---

## 6. Success Criteria & Checkpoints

| Milestone | Criterion | Target |
|-----------|-----------|--------|
| **Data complete** | NHGIS time series standardized extracts (all 6 periods) + B07003 source tables + fire/WFP/RUCC downloaded and validated | Week 2 |
| **Sample finalized** | ~700 treated + ~40k control after all screens; MOE, population filters documented | Week 3 |
| **Balance achieved** | SMD < 0.10 all covariates post-IPW; ESS ≥ 500 | Week 4 |
| **Main estimation complete** | ATT point estimate + 95% CI; event-study $\beta_h$ (h ∈ {−3, −2, 0, +1, +2}) with h=−1 as reference | Week 5 |
| **Robustness complete** | ≥8 robustness specs tabulated; findings stable/sensitive documented | Week 7 |
| **Publication-ready output** | All tables LaTeX-formatted, figures 300 DPI, data dictionary | Week 8 |
| **Manuscript draft** | Introduction through Discussion drafted; results embedded; appendix methodology notes | Week 9 |

---

## 7. Pre-Analysis Plan Registration

**Timing**: Before any estimation begins

**Contents to register**:
- Single-cohort design (fires 2015–2017, g=2016 or g=0)
- ACS periods: 2010 (h=−3), 2012 (h=−2), 2014 (h=−1 reference), 2022 (h=0), 2023 (h=+1), 2024 (h=+2)
- Data source: NHGIS time series standardized (S) tables at census tract level
- Primary outcome: Poverty rate
- Secondary outcomes: Income (2020$), employment, migration proxy
- Main estimand: ATT via event-study DiD with PS-IPW matching on WFP 2014 raster (primary) + caliper trimming; CEM on WFP quintiles as robustness; WFP 2012 as sensitivity check
- Threats and mitigations
- Robustness tests (organized by threat)

**Registry**: OSF (https://osf.io/) or AEA RCT Registry

---

## 8. Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Sample size too small for power** | Verify via Monte Carlo using coefficient priors from wildfire-finance county-level results; expect 0.5–1.0 pp CIs on poverty |
| **Selection bias in fire location** | PS-IPW on WFP 2012 (predetermined) + pre-2013 fire history; balance diagnostics; sensitivity to matching specification |
| **ACS rural MOE large** | Drop tracts with poverty denominator < 100; flag high-MOE tracts (MOE/count > 0.5) for robustness exclusion |
| **No pre-trend test possible** | Placebo falsification: assign fires to pre-2013, test ATT ≈ 0 |
| **Measurement error in migration** | ACS 5-year residence change is noisy; label decomposition as descriptive, not causal |
| **Temporal confounds (2015–2017)** | State × period FE; robustness check with census-division × period |

---

## 9. References & Key Papers

### Methodological
- Angrist & Pischke (2009): *Mostly Harmless Econometrics*
- Callaway & Sant'Anna (2021): Staggered difference-in-differences (note: our design is simpler—single cohort, not staggered)
- Roth (2022): Pre-trend testing critique
- Sun & Abraham (2021): Heterogeneity-robust estimators

### Wildfire Economics & Disasters
- Boomhower (2019): Wildfire risk and property insurance
- Borgschulte et al. (2024): Wildfire smoke and labor markets
- [To be populated via `/deep-research` lit review]

---

## 10. Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1–2 | Data acquisition | ACS download, raster processing, sample finalization |
| 3–4 | PS-IPW matching | Balance diagnostics, weights finalized |
| 4–5 | Main estimation | ATT + 95% CI, event-study coefficients |
| 6–7 | Robustness & heterogeneity | Robustness table, subgroup analysis, Sun-Abraham |
| 8 | Output | Publication-ready tables/figures, data dictionary |
| 9+ | Manuscript | Introduction through Discussion; submission ready |

---

## 11. Project Status

**Estimation complete as of 2026-08-16. Primary result: in-migration rate ATT = +0.92 pp (robust through HonestDiD M=1.5). Income and poverty effects not significant after smoke buffer correction.**

- ✓ Research design finalized (single clean cohort)
- ✓ Identification strategy locked in
- ✓ Data acquired and pipeline built (`code/01_build/` through `code/04_output/`)
- ✓ Smoke buffer bug fixed (`02_fire_treatment.py`): never-treated 70,146 → 36,013 after correct 100km exclusion
- ✓ Main DiD estimated (`code/03_analysis/01_did_estimation.py`): ATTs for all 4 outcomes
- ✓ Pre-trend tests run (`code/03_analysis/02_pretrend_tests.py`): income/poverty/migration PASS; employment FAIL (downgraded to robustness appendix)
- ✓ Robustness estimated (`code/03_analysis/03_robust_tests.R`): DR-TWFE, HonestDiD; in-migration breakdown M=1.5
- ✓ Buffer × fire-size robustness (`code/03_analysis/04_robustness_specs.py`): Table 4 produced
- ✓ Tables and figures generated (`code/04_output/01_tables_figures.py`): Table2/3, Figures 1–7
- ⏳ **Next — Immediate**: Add `log_pop` and `log_mover_count` to `01_did_estimation.py`; estimate and add to Figure 4 (three-panel decomposition)
- ⏳ **Next — Medium**: Request B25002/B25003 from NHGIS; add `owner_occ_rate` and `vacancy_rate` to panel; estimate and produce Figure 5
- ⏳ **Next — Optional**: Download IRS SOI county migration tables; implement `code/03_analysis/05_irs_outmigration.py`
- ⏳ PAP registration (note: estimation is already complete; registration now serves as documentation of pre-specified design)
- ⏳ Paper writing: Introduction through Discussion not yet drafted; skill sequence: `/deep-research` → `/academic-paper` → `/academic-paper-reviewer`

---

*End of Research Plan. Single-cohort design provides clean causal identification with sufficient statistical power for publication-quality results.*
