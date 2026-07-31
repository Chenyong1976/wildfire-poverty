# Research Plan: Wildfire Impact on Poverty and Economic Outcomes

**Last Updated**: 2026-07-30 (Major revision: County → Census Tract; Raster-based spatial matching)  
**Principal Investigator**: [Your Name]  
**Project Directory**: `~/wildfire-poverty-analysis/`

---

## 1. Research Question & Motivation

### Primary Question
**How do large wildfires affect household incomes, poverty rates, net migration, and employment in affected US census tracts? What role does population displacement play in these effects?**

### Motivation
Wildfire frequency and severity have increased dramatically across the US over the past two decades, yet empirical evidence on economic impacts—particularly for vulnerable populations—remains limited. County-level analysis masks substantial within-county heterogeneity in fire exposure and economic outcomes; this study shifts to **census-tract resolution** to capture fine-grained geographic variation in wildfire hazard and socioeconomic vulnerability. Using raster-level (270m × 270m) wildfire hazard potential data for spatial matching, we can identify treated and control tracts with greater precision, improving statistical power and reducing selection bias. We target **distributional effects on income, poverty, and net migration** across all lower-48 states, and explicitly model net migration as a potential mediating mechanism: if wildfires displace low-income households from treated tracts, tract-level poverty rates may decline even if individual incomes fall (compositional effect), or tract poverty may increase if displacement is incomplete (welfare loss dominates).

### Contribution
- **Empirical**: Quasi-experimental evidence of wildfires' causal impact on poverty, income, and net migration across ~70,000 lower-48 US census tracts (not just Western states or county-level aggregates) using staggered DiD with fine-grained WFP 2012 raster matching
- **Spatial precision**: First study to leverage 270m resolution WHP data for tract-level treatment/control matching, improving power and reducing geographic confounding compared to county-level designs
- **Mechanism**: Explicit analysis of net migration as a mediating pathway; decompose tract-level poverty effects into individual income losses and population composition shifts
- **Methodological**: Census-tract analysis with raster-based spatial matching (WFP 2012 at native 270m resolution) paired with Callaway & Sant'Anna (2021) staggered DiD
- **Policy**: Estimates inform hyper-local disaster relief targeting, climate adaptation spending, and migration assistance design; highlight whether "economic impact" reflects welfare loss or population reallocation

---

## 2. Identification Strategy

### Design: Staggered Difference-in-Differences with Raster-Based Spatial Matching

**Treatment**: Census tract experiences its first large fire (MTBS ≥1,000 acres) in **2013–2021** (treatment window), identified via fine-grained spatial overlap (tract intersected with MTBS fire perimeter).

**Treatment cohorts** (staggered):
- **Treated** (g=2017): First qualifying fire in 2013–2016; observed post-fire at 2017–2021 ACS 5-yr estimates
- **Treated** (g=2022): First qualifying fire in 2017–2021; observed post-fire at 2018–2022 ACS 5-yr estimates (if available)
- **Never-treated** (g=0): No qualifying fires in 2013–2021 AND outside 100 km smoke buffer

**Excluded groups**:
- Pre-2013 fires: Used for covariate balance in matching (pre-treatment fire history), not as controls
- Fires 2022+: Excluded if outcome data not yet available

**Extensive margin**: Tract ever experiences any large fire (≥1,000 acres) in treatment window.

**Intensive margin**: Fire count (frequency of fires) and total acres burned within tract (dose-response); WHP 2012 raster intensity (270m resolution) as continuous treatment proxy.

**Spatial matching strategy**: Leverage WFP 2012 raster at native 270m resolution. For each tract, compute: (1) mean WFP 2012 percentile across all 270m pixels overlapping tract, (2) % tract area in each WFP hazard quintile, (3) pairwise raster distance to nearest high-hazard pixel. Use these tract-level raster summaries as matching covariates via PS-IPW (finer granularity than county-level aggregation).

**Estimand**: Average treatment effect on the treated (ATT) — the causal effect of experiencing a wildfire in treatment window on outcomes (poverty rate, median income, net migration, employment) measured post-fire, relative to pre-treatment baseline (2012 ACS), conditional on raster-based WFP 2012 matching.

**Variation**: Fire occurrence varies geographically and temporally across ~70,000 lower-48 US census tracts. Within-county heterogeneity in fire exposure and baseline hazard is now captured at tract resolution. Tracts that never burned (2013–2021) and outside smoke buffer form the comparison group.

### Threats to Identification & Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Selection bias**: High-hazard regions (economically vulnerable, dry terrain) experience fires endogenously | **Raster-based WFP 2012 matching** (predetermined): Use USFS Wildfire Potential 2012 (finalized before 2013 fire season) at native 270m resolution as primary matching variable. For each tract, compute tract-level raster summaries (mean WFP percentile, % area in each quintile, raster distance to high-hazard pixels). Match via propensity-score inverse-probability weights (PS-IPW) on these raster covariates + pre-2013 fire history + pre-2012 poverty rate, median income, population density, RUCC, and demographic covariates. **Rationale**: Finer spatial resolution (270m vs. county aggregation) captures within-county hazard heterogeneity, reducing geographic confounding. Report effective sample size (ESS) of reweighted control group. |
| **Anticipatory behavior**: Tracts expect fires and adjust preemptively (e.g., out-migration before fire) | **Pre-trend testing**: Report pre-treatment coefficients ($\beta_{h<0}$) from event-study with 95% CIs (not null-hypothesis tests). Assess visual magnitude and direction of divergence before treatment. If pre-trends modest relative to post-treatment effects, interpret as minor deviation from perfect parallelism. Dynamic balance test: regress outcome on leads of treatment (falsification test). |
| **Smoke spillover**: "Control" tracts may be exposed to smoke from nearby treated tracts' fires | **Geographic exclusion**: Remove tracts within 100 km of any fire perimeter from the control group (baseline, following wildfire-finance). Robustness: vary radius (50 km, 150 km). Report whether narrower buffers materially change results. |
| **Temporal confounds**: Other regional shocks (economic downturns, housing bubbles, energy transitions, COVID) coincide with fires | **Regional FEs**: Include state × ACS-period FE to absorb regional-period shocks. Robustness: add census division × period FE for finer regional control. Document any divergence in results. |
| **Migration composition bias**: Tract-level poverty rates reflect both individual income effects AND selection of who stays/leaves | **Mediation analysis (§4.2)**: Estimate causal effect on net migration (ACS 5-yr residence change) as a potential mediator. Separately report: (a) tract-level ATT on income/poverty, (b) tract-level ATT on net-migration rate, (c) decomposition: income effect + compositional effect. Flag in discussion if large migration effects suggest compositional change. |
| **Effect heterogeneity**: Wildfires may have different impacts by geography, baseline poverty, fire severity | **Extensive and intensive margin**: Report both (a) any large fire (extensive) and (b) fire frequency/acreage and raster intensity (intensive) separately. Heterogeneous effects: subgroup analysis by baseline poverty (high vs. low), census region, baseline WFP hazard quintile. Report Sun & Abraham (2021) alongside Callaway & Sant'Anna as robustness check for heterogeneity bias. |
| **Tract-level outcome measurement error**: ACS estimates at tract level have larger MOEs than county; sparse tracts may have unreliable poverty/income estimates | **Data quality screen**: Drop tracts with ACS margin of error > 30% of point estimate for primary outcome (poverty rate). Report N tracts excluded by MOE screen. Use only tracts with population ≥ 500 (ACS threshold for reliable estimates). Conduct robustness: vary MOE threshold (20%, 30%, 40%); report if results sensitive to exclusion rule. |

### Estimating Equations

**Main specification** (simple difference-in-differences with multiple pre-treatment periods):

$$\text{Outcome}_{t,g} = \alpha_t + \gamma_g + \text{ATT}_{t,g} \cdot \mathbb{1}[t \geq g] + X_{t,\text{pre}} \beta + \epsilon_{t,g}$$

**Callaway & Sant'Anna (2021) event-study variant** (primary):

$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \neq -1} \beta_h \cdot \mathbb{1}[\text{g}_i = t - h] + X_{i,\text{pre}} \gamma + \epsilon_{i,t}$$

where:
- $i$ = census tract
- $t$ = ACS period (2012, 2017, 2022; labeled by final census year of 5-yr estimate)
- $g$ = cohort (year of first fire; g=2017 if first fire 2013–2016, g=2022 if 2017–2021, g=0 if never-treated)
- $h$ = relative time to treatment (h=0 is post-fire, h<0 are pre-fire periods)
- $\beta_h$ = treatment effect at relative time $h$
- $\alpha_i$ = tract fixed effects
- $\lambda_t$ = period fixed effects
- $X_{i,\text{pre}}$ = pre-treatment covariates (raster-based WFP 2012 summaries, pre-2013 fire history, baseline poverty/income, population density, RUCC, demographics)
- Standard errors clustered at tract level; inverse-probability weights (from PS-IPW raster matching) applied

**Interpretation**:
- $\beta_h$ = causal effect $h$ periods relative to fire; allows pre-trends testing and dynamic effects
- $\text{ATT} = \frac{1}{k} \sum_{h \geq 0} \beta_h$ = aggregate post-treatment effect (simple average or weighted by time-at-risk)
- Pre-trends ($h<0$): Should be zero or negligibly small if parallel trends holds
- Post-trends ($h \geq 0$): Report trajectory of effects over time (e.g., effects may fade or strengthen)

**Robustness: Regression adjustment variant**:

$$\text{Outcome}_{i,t,g} = \alpha_i + \lambda_t + \sum_{h \neq -1} \beta_h \cdot \mathbb{1}[\text{g}_i = t - h] + X_{i,\text{pre}} \gamma + \text{State FE}_i + \epsilon_{i,t,g}$$

Include state FE to absorb regional shocks (e.g., economic downturns, migration waves correlated with geography).

**Mediation analysis** (net migration as mediator):

Decompose total effect on poverty rate into:

1. **Total effect (ATT on poverty)**: $\tau_{\text{poverty}}$ from main specification
2. **Treatment → mediator**: $\tau_{\text{migration}}$ = ATT on net-migration rate (ACS 5-year residence change)
3. **Mediator → outcome**: $\gamma_{\text{migration}}$ = coefficient on net-migration in outcome regression
4. **Indirect effect**: $\tau_{\text{migration}} \times \gamma_{\text{migration}}$ (mediation through migration)
5. **Direct effect**: $\tau_{\text{poverty}} - \text{indirect effect}$ (effect not mediated by migration)

**Interpretation**:
- If large indirect effect (out-migration mediates poverty): compositional effect (low-income households leave)
- If small indirect effect: income effects dominate (poverty changes reflect individual income loss, not selection)
- Mediation framing clarifies mechanism and policy implications

---

## 3. Data & Sample Definition

### Sample Frame
- **Geographic scope**: All lower-48 US states (~70,000 census tracts; Census 2010 definition)
- **Time period**: ACS 5-year estimates with three analysis periods:
  - **Pre-treatment baseline**: 2007–2011 ACS (poverty, income, employment, net migration)
  - **Treatment window**: 2013–2021 (fires occurring during this period define treated tracts)
    - Cohort 1 (g=2017): First fire in 2013–2016
    - Cohort 2 (g=2022): First fire in 2017–2021
  - **Post-treatment**: 2017–2021 ACS (g=2017) and 2018–2022 ACS (g=2022) — outcome measurement
- **Unit of analysis**: Census tract (2010 boundaries; ~70,000 tracts nationally)
- **Treatment cohorts**: Staggered (two cohorts: g=2017, g=2022)
- **N**: ~70,000 tracts × 3 periods ≈ ~210,000 observations (unbalanced panel; not all tracts observed in all periods due to ACS sparsity)

**Data quality screen** (critical for rural fire-affected tracts):
- **ACS 5-year estimates only**: Restrict to ACS 5-year estimates (2012, 2017, 2022). ACS 3-year and 1-year estimates are unreliable for rural geographies, and majority of large fires occur in rural areas. 5-year estimates provide adequate sample sizes and representativeness for rural poverty and income measurement.
- **Margin of error threshold**: Exclude tracts with ACS MOE > 30% of point estimate for poverty rate (primary outcome). For rural tracts with sparse populations, this screen is essential.
- **Population minimum**: Exclude tracts with population < 500. However, document separately: among included rural tracts (pop 500–2,000), report MOE median/distribution to flag data quality concerns.
- **Rural tract flag**: Identify rural tracts (RUCC 4–9) separately; assess whether MOE burden is disproportionate. If rural tracts have systematically higher MOE, conduct robustness checks (vary MOE threshold 20%, 30%, 40%).
- **Expected final sample**: After MOE screening and pop ≥ 500: ~40,000–50,000 tracts × 3 periods ≈ ~120,000–150,000 observations. Document breakdown by urbanicity (rural vs. urban/suburban).

**Statistical power advantage** (with rural data reliability caveat):
- Tract-level analysis: 10–15× more observations than county-level (70k tracts vs. 3.1k counties)
- Finer spatial resolution (270m WHP pixels) improves within-county matching precision
- Larger sample size enables detection of smaller effects and subgroup heterogeneity
- **Caveat**: Rural tracts (where fires concentrate) have larger ACS margins of error due to sparse populations. Use 5-year estimates (vs. 3-year/1-year) to maintain representativeness. Trade-off: wider confidence intervals for rural tracts, but valid estimates.

### Outcome Variables

| Outcome | Data Source | Definition | Rural Considerations |
|---------|-------------|-----------|-----------|
| **Poverty rate** (primary) | ACS 5-yr only | % population below federal poverty line | 5-year estimates essential for rural reliability. Expect wider CI in rural subgroups due to sparse sampling; this is valid measurement, not weakness. |
| **Median HH income** | ACS 5-yr only | Median household income (nominal, adjusted to 2020$) | 5-year estimates recommended. Income measurement less stable in sparse rural populations (high MOE). |
| **Employment rate** | ACS 5-yr only | % civilian labor force employed | 5-year estimates provide stable estimates of labor force participation in rural areas. |
| **Net-migration rate** (mediator) | ACS 5-yr only (residence 5-yr ago) | % population moved into tract minus % moved out, in past 5 years | Migration estimates in rural tracts subject to larger MOE. 5-year window appropriate for fire-effect timescale. |
| **Per capita income** | BEA Regional Econ Accounts (annual) | Per capita income (county-level; matched to tracts via county FIPS) | County-level BEA data more reliable than tract-level estimates. Use for robustness cross-check only. |
| **Industry employment share** | ACS 5-yr only | Share employed in agriculture, forestry, recreation, natural resource extraction | Important for rural fire-prone tracts (high ag/forest/extraction employment). 5-year sample sizes adequate for rural measurement. |

**Temporal Specificity for Rural Areas**:
- **ACS 5-year estimates only**: Use 2012, 2017, 2022 estimates (final years). Do NOT use 3-year or 1-year estimates, even for robustness checks—unreliable for rural tracts.
- **Align to census year**: Assign 5-year ACS estimate to the final year of the estimate window (e.g., ACS 2012–2016 labeled as "2017" ≈ mid-point analysis year). This is ~3–4 years after fires in g=2017 cohort.
- **Time gap implications**: With 5-year estimates, pre-treatment baseline (2012 ACS, window 2008–2012) ends ~4–6 years before fires (2013–2016). Post-treatment measurement (2017 ACS, window 2013–2017) captures effects up to 4 years post-fire for early-cohort fires. Acknowledge this measurement-timing constraint in limitations.
- **BEA per-capita income** (annual): Use single-year values closest to ACS estimate windows for robustness checks; interpolate if needed. County-level only; merge to tracts via county FIPS.
- **Document**: Timing details in data dictionary and methodology note.

### Treatment Definition

**Extensive margin (any fire)**:
- **Treated**: Census tract experiences its first large fire (MTBS polygon ≥1,000 acres) in **2013–2021**.
- **Fire perimeter definition** (replicating wildfire-finance):
  - Use MTBS database (1984–2022 fires, nationwide coverage)
  - Minimum size threshold: 1,000 acres (limits to consequential fires; trade-off: cleaner identification vs. limited scope)
  - Spatial match: Tract intersects MTBS fire polygon (any spatial overlap counts as treated in fire year); compute % tract area burned
- **Staggered cohorts**:
  - g=2017: First fire 2013–2016; post-treatment outcome measured at 2017–2021 ACS
  - g=2022: First fire 2017–2021; post-treatment outcome measured at 2018–2022 ACS
- **Rationale**: Staggered timing accommodates two distinct fire cohorts, each with sufficient post-fire follow-up before outcome measurement

**Intensive margin (fire frequency/acreage/raster intensity)**:
- **Fire count**: Number of large fires (≥1,000 acres) per tract in treatment window (0, 1, 2, 3+)
- **Total acres burned**: Sum of acres burned across all large fires per tract; may exceed tract area if fire spans multiple tracts
- **WFP 2012 raster intensity**: Mean WFP 2012 percentile (0–100) across 270m pixels overlapping tract; use as continuous treatment proxy
- **Report specifications**: (a) binary any-fire indicator (extensive), (b) dose-response by fire frequency or acreage (intensive), (c) raster-based continuous treatment (WFP intensity)

### Control Definition

**Never-treated**:
- Tracts with no large fire (≥1,000 acres, MTBS) in **2013–2021** AND outside 100 km smoke buffer

**Excluded groups**:
- **Pre-2013 fires (≤2012)**: Used in matching covariates (pre-treatment fire history) to control for baseline fire exposure. Tracts with pre-2013 fires are **excluded from the never-treated pool** (not used as controls). This avoids confounding from prior fire recovery/adaptation effects.
- **Smoke-exposed controls**: Tracts within **100 km** of any treated tract's fire perimeter (baseline, following wildfire-finance). Robustness: vary radius (50 km, 150 km).
- **Data quality failures**: Tracts with ACS MOE > 30% of point estimate for poverty rate; population < 500.

**Matching covariates** (using PS-IPW with raster-based spatial precision):
- **WFP 2012 raster summaries** (predetermined, 270m resolution): 
  - Mean WFP 2012 percentile (0–100) across all 270m pixels intersecting tract
  - % tract area in each WFP hazard quintile (5 indicators)
  - Raster distance to nearest high-hazard pixel (WFP > 75th percentile)
- **Pre-2013 fire history**: Any large fire in 1984–2012, total acres burned 1984–2012
- **Baseline (2007–2011 ACS) covariates**: Poverty rate, median household income, population density, % age 65+, % race/ethnicity groups
- **RUCC**: USDA Rural-Urban Continuum Code (2013 vintage)
- **Tract population**: Drop tracts with pop < 500

**Balance diagnostics**:
- Report standardized mean differences (SMD) before and after PS-IPW matching (target: SMD < 0.1 for all covariates)
- Report effective sample size (ESS) of reweighted control group; flag if ESS << unweighted N (thin common support)
- Density plots: propensity score distributions before and after reweighting for treated vs. controls

### Data Sources & Acquisition

| Variable | Source | Format | Notes |
|----------|--------|--------|-------|
| Poverty rate, median income, employment, net migration | ACS 5-yr (IPUMS) | CSV extracts | **Use 5-year estimates aligned to census years** (2012, 2017, 2022; labeled by final year of estimate). **Tract-level data**: ACS tract estimates have larger margins of error than county; implement MOE screening (drop tracts with MOE > 30% of point estimate). Account for disclosure avoidance in 2020 onward (larger standard errors; consider sensitivity dropping 2020-based estimates). |
| Per capita income | BEA NIPA | CSV (FRED API) | Annual series; interpolate or use single-year closest to census period. County-level data; match to tracts via crosswalk if tract-level estimates unavailable. |
| Industry employment | ACS 5-yr (tract level) | CSV | Extracted from IPUMS along with poverty/income variables at tract resolution. |
| Fire perimeters & treatment assignment | MTBS (USGS) | Shapefile/GeoJSON | Reuse `wildfire-finance/data/raw/mtbs_perims/`. **Spatial join with tract boundaries**: Compute % tract area burned for each tract-fire intersection (supports dose-response analysis). |
| **WFP 2012** (primary matching) | USFS | GeoTIFF (270m resolution, ESRI Grid) | Shared from wildfire-finance project: `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`. **Native 270m resolution used directly** (do NOT aggregate to county/tract; instead, compute tract-level summaries: mean WFP percentile, % area per hazard quintile, raster distance to high-hazard pixels). **Predetermined for fires from 2013 onward** (finalized before 2013 fire season). |
| WHP 2014 (robustness) | USFS | GeoTIFF (270m resolution) | Shared from wildfire-finance. NOT predetermined for 2013–2014 fires; use in robustness checks only. |
| Census tract boundaries | Census TIGER | Shapefile | 2010 Census tract definitions (stable boundaries for panel construction). |
| Baseline covariates (2012 ACS) | ACS, USDA RUCC | CSV / GIS | From IPUMS at tract level; for PS-IPW matching and balance diagnostics. RUCC at county level; merge to tracts via county FIPS. |
| Smoke buffer (100 km) | Derived from MTBS + tract geom | Shapefile / Parquet | Construct: buffer MTBS perimeters to 100 km; flag tracts intersecting buffer. Regenerate from MTBS rather than reuse county-level version (finer spatial precision). |

---

## 4. Methods: Implementation Roadmap

### 4.1 Phase 1: Data Acquisition, Raster Processing, & Cleaning (Weeks 1–4)

**Deliverables**:
- `acs_2012_2022_tract_clean.parquet`: Poverty, income, employment, net migration by tract-census-period (2012, 2017, 2022); includes ACS MOE screening (MOE ≤ 30% of point estimate); population ≥ 500
- `fire_treatment_assignment_tract.parquet`: Tract treatment year (g=2017, g=2022, or g=0 for never-treated); extensive (binary) and intensive (fire count, acres burned, % tract burned) margins
- `whp_2012_tract_raster_summaries.parquet`: Tract-level raster summaries computed from 270m WFP 2012 pixels:
  - Mean WFP percentile (0–100)
  - % tract area in each WFP hazard quintile (5 indicators)
  - Raster distance to nearest high-hazard pixel (WFP > 75th percentile)
  - Raster-based continuous treatment proxy (mean WFP percentile)
- `matching_covariates_2012_tract.parquet`: Pre-treatment baseline covariates (2012 ACS at tract level: poverty, income, demographics; county-level RUCC; population)
- `smoke_buffer_100km_tract.parquet`: Tracts within 100 km of any MTBS fire perimeter (exclusion flag)
- `analysis_sample_final_tract.parquet`: Unbalanced panel (70,000 tracts × 3 periods) after smoke exclusion, MOE screening, and population ≥ 500 restriction; expected ~40,000–50,000 tracts × 3 periods

**Raster processing workflow** (new in tract-level design):
1. **Load WFP 2012 GeoTIFF** (270m resolution): Read `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/` using `rasterio` and `geopandas`
2. **Tract-raster intersection**: For each Census 2010 tract polygon, extract all 270m pixels overlapping tract; compute per-pixel WFP value (0–100 percentile scale)
3. **Aggregate to tract level**: 
   - Mean WFP percentile across pixels in tract
   - % pixel area in each hazard quintile (0–20, 20–40, 40–60, 60–80, 80–100)
   - Distance from tract centroid to nearest pixel with WFP > 75th percentile
4. **Fire-tract spatial join**: Intersect MTBS fire polygons with tract boundaries; compute % tract area within each fire perimeter
5. **Output**: Parquet with tract-level raster and fire exposure summaries

**Quality checks** (with rural data emphasis):
- **ACS tract-level MOE screening**:
  - Flag and drop tracts with MOE > 30% of poverty-rate point estimate
  - Document total N dropped and breakdown by urbanicity (rural vs. urban/suburban)
  - Report median MOE for included rural tracts (pop 500–2,000) separately; flag if disproportionately high
  - Justification: ACS 5-year sampling for rural tracts is sparse but valid; wider MOE expected and acceptable
- **Raster processing**: Spot-check 50 tracts (prioritize mix of rural and urban); visually verify WFP pixel extraction and aggregation in GIS
- **Cross-validation**: Compare BEA per-capita income (county-level, annual) against ACS median income (tract-level, 5-year) for directional consistency; conduct by urbanicity
- **Fire-tract spatial overlay**: Sample 20–30 tracts from each cohort (rural and urban); manually inspect tract-fire overlap; flag edge cases (large fires spanning multiple tracts, state-line tracts)
- **Smoke buffer validation**: Spot-check 10–20 fire perimeters and 100 km tract exclusion zones in GIS; verify tract buffering precision
- **ACS temporal validity**: Confirm all included ACS data are 5-year estimates (no 3-year or 1-year); document vintage windows (2012: 2008–2012, 2017: 2013–2017, 2022: 2018–2022)
- **Disclosure avoidance (2020+)**: If 2022 ACS available, assess differential privacy impact; conduct sensitivity analysis dropping 2020-based estimates

### 4.2 Phase 2: Propensity-Score Matching & Balance Diagnostics (Weeks 4–5)

**Approach** (tract-level with raster-based matching covariates):

1. **Propensity score model**: Logistic regression of treatment (g ≠ 0) on:
   - **Raster-based WFP 2012 covariates** (270m resolution):
     - Mean WFP 2012 percentile (continuous, 0–100)
     - % tract area in each WFP hazard quintile (5 indicators)
     - Raster distance to nearest high-hazard pixel
   - **Pre-2013 fire indicators**: Any fire 1984–2012, log total acres burned 1984–2012
   - **Pre-treatment covariates (2012 ACS tract-level)**: Poverty rate, median HH income, population density, % age 65+, % race/ethnicity groups; USDA RUCC (county-level); tract population
   - Outcome: $\text{Pr}(\text{treated} | X)$

2. **Inverse-probability weights** (IPW):
   - Treated tracts: $w_i = 1$
   - Control tracts: $w_i = \hat{e}_i / (1 - \hat{e}_i)$ (where $\hat{e}_i$ = estimated propensity score)
   - Trim at 99th percentile of weights to stabilize variance
   - **Rationale for raster covariates**: 270m resolution captures fine-grained hazard variation within counties; improved matching precision vs. county-level WFP aggregation

3. **Balance diagnostics**:
   - Compute standardized mean differences (SMD) before and after IPW reweighting for all covariates
   - Target: SMD < 0.1 for all covariates after reweighting
   - Report effective sample size (ESS) of reweighted control group (sanity check on common support)
   - Density plots: propensity scores, treated vs. control (before and after reweighting)
   - If ESS << unweighted control N, flag thin common support; consider CEM matching as alternative
   - **Tract-level balance**: Verify balance not just on individual covariates but on raster-based summaries (visual inspection of histograms)

### 4.3 Phase 3: Main Estimation — Staggered DiD & ATT (Weeks 5–7)

**Estimation approach** (Callaway & Sant'Anna 2021 staggered DiD with raster-matched controls):

Use **R package `did::att_gt()`** (Callaway & Sant'Anna implementation) with inverse-probability weights:

1. **Main C&S DiD estimation (event-study)**:
   - Outcome: poverty rate (primary), median income, employment rate, net migration (secondary)
   - Treatment: Binary = 1 if tract has ≥1 fire in treatment window (g=2017 or g=2022), 0 if never-treated
   - Cohorts: g=2017 (first fire 2013–2016), g=2022 (first fire 2017–2021), g=0 (never-treated)
   - Periods: 2012, 2017, 2022 (ACS 5-year estimates)
   - Specification: $\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \neq -1} \beta_h \cdot \mathbb{1}[\text{g}_i = t - h] + X_{i,\text{pre}} \gamma + \epsilon_{i,t}$
   - Weights: Inverse-probability weights (from Phase 2 PS-IPW matching on raster covariates)
   - SE: Clustered at tract level; 95% CIs via bootstrap (1,000 replicates)

2. **Event-study coefficients and pre-trends testing**:
   - Estimate $\beta_h$ for relative time $h \in \{-2, -1, 0, 1, 2, \ldots, 7\}$ post-fire
   - **Pre-trends ($h < 0$)**: Report coefficients with 95% CIs; should be statistically and economically negligible
   - **Post-trends ($h \geq 0$)**: Report full trajectory; effects may persist, fade, or amplify
   - Visual inspection: Event-study plots with pre/post trends clearly marked; shaded confidence bands
   - Interpretation: If $\beta_{-1}$ and $\beta_{-2}$ near zero and jointly not significant, supports parallel trends

3. **Aggregate ATT** (post-fire average):
   - Compute: $\widehat{\text{ATT}} = \frac{1}{k} \sum_{h=0}^{k} \beta_h$ (simple average of post-treatment $\beta_h$)
   - Report: Point estimate, 95% CI, economic magnitude (e.g., percentage points for poverty rate; dollars for income), N observations
   - Interpret: "Exposure to large fire increased poverty rate by X percentage points (95% CI: [a, b]) in treated tracts relative to matched controls"
   - **Robustness:** Also report aggregate ATT weighted by time-at-risk (alternative aggregation)

4. **Extensive vs. intensive margin**:
   - **Extensive (binary)**: Main specification above (any fire in treatment window)
   - **Intensive (dose-response)**: Estimate separate C&S models with:
     - Fire count (1, 2, 3+ fires) replacing binary indicator → ATT per additional fire
     - Total acres burned (normalized to 10,000-acre units) replacing binary → ATT per 10,000 acres
     - WFP 2012 raster intensity (mean WFP percentile) as continuous treatment proxy
   - Report all three; compare magnitudes to assess dose-response relationship
   - **Hypothesis**: If causal fire-poverty linkage real, intensive-margin ATTs should be proportional to extensive-margin ATT

5. **Mediation analysis (net-migration as mediator)**:
   - **Step 1**: Estimate C&S ATT on net-migration rate (same model as poverty; primary outcome is net-migration)
   - **Step 2**: Regress poverty on fire treatment AND net-migration in separate C&S model (to get mediator coefficient)
   - **Step 3**: Decompose: Total ATT(poverty) = Direct effect (controlling for migration) + Indirect effect (migration-mediated)
     - Indirect = ATT(migration) × coefficient(migration → poverty)
     - Direct = Total ATT − Indirect
   - **Interpret**: 
     - Large indirect effect (% of total) → out-migration is key mechanism (compositional effect dominates)
     - Small indirect effect → income effects dominate (welfare loss mechanism)
   - **Caveat**: Mediation estimates are sensitive to measurement error in ACS migration variable; interpret as exploratory

### 4.4 Phase 4: Robustness & Sensitivity Checks (Weeks 7–8)

**Organized by identification threat** (staggered DiD design with raster matching):

| Threat | Robustness Test | Rationale |
|--------|-----------------|-----------|
| **Raster matching precision** | Re-estimate C&S using (a) county-level WFP 2012 quintile only (pre-update design), (b) full raster covariates (current) | Verify that finer spatial resolution (270m raster) improves balance and reduces ATT bias vs. county-level matching. Compare ATT magnitudes. |
| **Smoke spillover** | Vary geographic exclusion radius: 50 km, 100 km (baseline), 150 km | If ATT stable across radii, smoke spillover exclusion not driving results. |
| **Fire size threshold** | Vary minimum MTBS acres: 500, 1,000 (baseline), 2,000 | Tests sensitivity to fire definition; controls for definitional robustness. |
| **Treatment window timing** | Shift cohort boundaries: fires 2012–2015, 2013–2016 (baseline), 2013–2017 | Tests whether results depend on exact treatment window boundaries. |
| **Placebo / falsification test** | Use pre-2013 fires assigned as "treatment"; estimate C&S ATT on outcomes post-2017 (should be ≈ 0) | If ATT ≈ 0 for pre-fires, supports no confounding from pre-trends. |
| **Specification: regional FE** | Add state × period FE; add census division × period FE | Tests whether results robust to region-specific time trends. |
| **Specification: exclude 2020+ ACS** | Drop any estimates using 2020 Census data (differential privacy); re-estimate on 2012–2017 window only | Tests sensitivity to ACS disclosure avoidance introduced 2020+. |
| **Sample: tract MOE threshold (rural-specific)** | Vary MOE screening: drop if MOE > 20%, 30% (baseline), 40% of point estimate | Tests sensitivity to ACS data quality. Since rural tracts systematically have higher MOE (due to sparse 5-year samples), report results by urbanicity. Higher thresholds (40%) retain more rural tracts but at cost of wider CIs. Lower thresholds (20%) exclude more rural tracts but improve precision. Recommend baseline 30% as balance. |
| **Sample: tract population minimum** | Drop tracts with pop < 300, < 500 (baseline), < 1,000 | Tests whether results robust to different tract-size thresholds. |
| **Sample: stricter never-treated** | Exclude tracts with any fire in 1984–2012 from controls | More conservative control definition (only truly never-exposed tracts). |
| **Sample: regional drop** | Exclude tracts in CA/OR/WA (highest fire density) vs. Eastern tracts | Tests whether results CA/OR/WA-driven; broader US generalizability check. |
| **Matching robustness: CEM** | Coarsened exact matching (CEM) on WFP quintiles + baseline poverty bins (alternative to PS-IPW) | Checks whether PS-IPW balance results robust to alternative matching approach. |
| **Heterogeneity-robust estimator** | Run Sun & Abraham (2021) estimator alongside C&S | Tests whether aggregate ATT robust to treatment effect heterogeneity across cohorts and time. |
| **Dose-response (intensive margin)** | Estimate C&S ATT separately for: fire count (1, 2, 3+), acres burned (per 10k acres), WFP intensity (per percentile) | Tests whether effects scale with exposure intensity (supports causal fire-poverty linkage). |

### 4.5 Phase 5: Heterogeneous Effects Analysis (Week 8)

**Subgroup analysis** (exploratory; census tracts allow larger subgroups than county design; with rural data quality caveat):

| Dimension | Subgroups | N (approx.) | Data Quality Note |
|-----------|-----------|---|-----------|
| **Census region** | South, Midwest, Northeast, West | ~8,000–12,000 tracts each | Fire regimes differ by region; Western fires more common, Eastern more rare. Economic response mechanisms may differ. Western tracts more likely rural (lower ACS precision). |
| **Baseline poverty** | High (>20%), Medium (10–20%), Low (<10%) | ~15,000–20,000 tracts each | Policy interest: do fires disproportionately harm low-income tracts? Poverty measurement quality best in higher-density tracts. |
| **Baseline WFP hazard** | High (>75th %), Medium (50–75th %), Low (<50th %) | ~15,000 tracts each | Test whether tracts with pre-existing high hazard show different fire-poverty effects. High-hazard tracts concentrated in Western rural areas (higher MOE). |
| **Tract urbanicity** | Urban, suburban, rural (RUCC 1–3 vs. 4–9) | ~10,000 / 15,000 / 25,000 | **CRITICAL**: Rural tracts (RUCC 4–9) where fires concentrate have systematically larger ACS MOE. Report subgroup ATT + CI, but emphasize: rural estimates wider confidence intervals due to sparse population. Document median MOE by urbanicity. |
| **Fire frequency** | 1 fire, 2+ fires | ~1,500 / 300 | Dose-response: do repeated fires compound effects? Small n for 2+ fires; interpret with caution. |
| **Cohort** | Fires 2013–2016 (g=2017), Fires 2017–2021 (g=2022) | ~800 / 500 | Temporal heterogeneity: do recent fires show different effects? Note: g=2022 cohort has only 1 post-treatment ACS period; treat estimates as preliminary. |

**Estimation**:
- Re-estimate C&S event-study separately for each subgroup (same equation, subset data)
- Report $\widehat{\text{ATT}}$ and 95% CI by subgroup; visual comparison (side-by-side event-study plots if possible)
- **For rural subgroup specifically**: Report both ATT and median MOE; note that wider confidence intervals reflect ACS data quality limitations, not statistical weakness
- **Statistical testing**: Do NOT formally test subgroup differences (multiple comparison problem). Instead, report point estimates and CIs; note overlaps or separation as descriptive finding.
- **Interpretation caveat**: "Subgroup estimates are exploratory. Rural subgroup estimates have wider confidence intervals due to ACS 5-year sampling limitations for sparse populations; this is expected and does not invalidate estimates."

---

## 5. Writing & Publication Strategy

### Paper Structure

**I. Introduction** (2–3 pages)
- **Hook**: Rising wildfire frequency (2013–2021 trends), economic vulnerability of fire-adjacent communities, divergence in economics vs. health literature
- **Gap**: Most wildfire economics focuses on Western US and property values/health; missing evidence on distributional effects (poverty, income) and migration mechanics across all lower-48 states
- **RQ**: "Do large wildfires reduce household incomes and increase poverty? What role does population displacement play?"
- **Contribution**: "Using staggered DiD with WFP 2012 matching on 3,100 lower-48 counties (2013–2021), we estimate causal effects on poverty, income, employment, and net migration. We explicitly decompose county-level poverty effects into income losses vs. compositional changes."
- **Preview**: Frame results as answer to mechanism question (Are effects driven by displacement or income loss?)
- **Literature positioning** (tight, 4–5 papers max): Wildfire economics (Boomhower, Borgschulte et al.), poverty/income literature (Autor, Kline), migration/displacement (Blanchard & Katz), DiD methodology (Callaway & Sant'Anna)

**II. Data & Sample** (1–2 pages)
- Sample scope: All lower-48 counties; 2013–2021 treatment; 2007–2022 outcomes (4 census periods)
- Treatment definition (extensive and intensive margins); sample counts (g=2017, g=2022, never-treated)
- Outcome measures (poverty, income, employment, net migration); data sources (ACS, MTBS)
- Table 1a: Summary statistics (treated vs. control pre-treatment, pre-IPW) — show imbalance
- Table 1b: Summary statistics post-IPW reweighting — show improved balance
- Figure 1: Map of fire perimeters and treated counties (MTBS 2013–2021); 100 km smoke buffer visualized

**III. Empirical Strategy** (2–2.5 pages)
- **Lead with identifying variation**: "Wildfires occur at staggered times across the lower-48 US, with first large fires 2013–2021. We exploit this timing variation via Callaway & Sant'Anna staggered DiD."
- **Estimand**: ATT — effect of experiencing a fire on treated counties' poverty rates, incomes, employment, and migration
- **Treatment cohorts**: Clearly define g=2017 (fires 2013–2016) and g=2022 (fires 2017–2021)
- **Main estimating equations**: Display event-study and aggregate ATT equations (from §2)
- **Threats and mitigation** (4–5 most important):
  - Selection bias → WFP 2012 matching with PS-IPW
  - Smoke spillover → 100 km geographic exclusion
  - Anticipated behavior → Pre-trend testing (magnitudes and visual inspection, not null tests)
  - Compositional effects → Mediation analysis on net migration
  - Heterogeneity → Report intensive margin, Sun-Abraham estimator
- Flag assumptions clearly; reserve detailed assumptions for Appendix

**IV. Results** (2–3 pages)
- **Table 2**: Main ATT estimates (simple DID)
  - Row headers: Poverty rate (primary), Median income, Employment rate, Net-migration rate (mediator)
  - Columns: (1) Coefficient, (2) 95% CI, (3) N obs, (4) Effect size (e.g., percentage points, $ change)
  - Include note: "Inverse-probability weights from propensity score matching; SE clustered at county level"
- **Table 3**: Extensive vs. intensive margin
  - Rows: Any fire (binary; main), 1 fire, 2+ fires, per 10,000 acres burned
  - Columns: Poverty, income, employment, net migration (same outcomes as Table 2)
  - Interpretation: Do effects scale with exposure?
- **Mediation results** (inline or table):
  - Total effect (ATT on poverty)
  - Indirect effect (via migration): ATT on migration × mediator coefficient
  - Direct effect: Total − Indirect
  - Interpretation: What % of effect is compositional vs. income loss?
- **Prose**: Lead with poverty rate result; highlight magnitude
  - "Exposure to large wildfire (≥1,000 acres) in 2012–2016 increased poverty rate by X percentage points (95% CI: [a, b]) by 2016–2019."
  - "This corresponds to approximately Y additional households falling below the poverty line."
  - "The effect is partially mediated by population out-migration, suggesting Z% is compositional and (100−Z)% reflects income losses."

**V. Robustness** (2–2.5 pages)
- **Organize by threat**, not test type:
  - Selection bias: placebo test (fires assigned to 2007–2012; ATT ≈ 0?), balance table post-IPW (SMD < 0.1?)
  - Smoke spillover: vary exclusion radius (50, 100, 150 km); check ATT stability
  - Specification: event-study window (−3 to 7 vs. −2 to 5), regional FE (state×period vs. division×period)
  - Estimator: Sun-Abraham (2021) alongside C&S
- Table 4 (or Table 2 expanded columns): ATT across 5–7 robustness specs; highlight if any spec produces materially different ATT
- Narrative: "Results are robust to..." (only mention if non-obvious); flag any specs where results diverge and discuss why

**VI. Discussion & Limitations** (1.5–2 pages)
- **Mechanisms**: Interpret mediation results
  - If large net-migration effect: "Out-migration is the primary mechanism; county poverty changes reflect population sorting rather than individual income losses"
  - If small net-migration effect: "Income effects dominate; fires reduce household incomes of stayers; limited migration response suggests residents adapt in place or are immobile"
  - Propose micro-level mechanisms (destroyed homes→relocation, job loss→out-migration, income shock→poverty entry)
- **Scope & generalizability**:
  - MTBS minimum 1,000 acres limits to consequential fires (trade-off: cleaner ID vs. limited scope to small fires)
  - ACS 5-year averages and disclosure avoidance induce measurement error (sensitivity check dropping 2020-based estimates)
  - Results span all lower-48 states; heterogeneity analysis suggests effects vary by region
- **What we don't know** (open questions for future work):
  - Do effects persist beyond 10 years?
  - What is the role of disaster aid vs. private insurance in fiscal resilience?
  - Differential impacts on vulnerable subpopulations (elderly, immigrants, low-education)?

**VII. Conclusion** (0.5 page)
- Restate primary finding: Fire exposure causes X% increase in poverty, mediated by Z% out-migration
- Policy implication (hedged): "Results suggest fire-prone counties face trade-offs between (a) supporting displaced residents, (b) stabilizing incomes for those who remain, and (c) preventing long-term economic decline. Targeted relief policies should account for compositional effects."
- No new results; no overstated claims

### Target Outlets
**Primary**: *Journal of Urban Economics*, *Regional Science and Urban Economics*, *American Economic Journal: Applied Economics*  
**Secondary**: *Journal of Environmental Economics and Management*, *Environmental Research Letters*

### Paper Timeline
- **Weeks 1–4**: Data assembly and methods (exploratory writing of Methods section by Week 4)
- **Weeks 5–6**: Results and event-study plotting (draft Results by Week 6)
- **Week 7**: Robustness; finalize tables and figures
- **Week 8**: Write Introduction, Discussion, polish manuscript
- **Weeks 9+**: Iteration, peer review, replication package, submission

---

## 6. Skill Sequence & Execution

### Recommended Claude Skill Sequence

1. **`/deep-research`** (Lit-review mode)
   - Research question: "How do wildfires affect local economies and poverty?"
   - Scope: Fire ecology & health, regional economics, causal inference in environmental shocks, prior wildfire economic impact estimates.
   - Output: Annotated bibliography, mechanism framing, positioning draft.

2. **`/academic-paper`** (Full drafting, economics config)
   - Scaffolds: Introduction template (hook–question–contribution–preview), empirical strategy template.
   - Inject bibliography from deep-research; use economics writing style defaults.
   - Output: Manuscript draft (all sections) with placeholders for results.

3. **`/academic-paper-reviewer`** (Multi-perspective review)
   - Simulate 5 reviewers (EIC, 3 peers, Devil's Advocate).
   - Peer 1 focus: Identification & causal inference (pre-trends, selection bias).
   - Peer 2 focus: Data quality & representativeness.
   - Peer 3 focus: Economic significance & mechanisms.
   - Devil's Advocate: Refute main finding; propose alternative explanations.
   - Output: Structured review feedback; revise manuscript.

4. **`/academic-pipeline`** (Full workflow if iterating heavily)
   - Orchestrates deep-research → paper → review → revise → re-review → finalize.
   - Use if revision rounds are needed; otherwise, steps 1–3 above suffice.

---

## 6. Pre-Analysis Plan (Mandatory)

**Register before data analysis begins** (OSF, AEA RCT Registry, SSRN PAP, or similar). PAP locks in specifications and signals intent, reducing credibility of post-hoc testing.

### Main Hypotheses

**H1** (primary): Large wildfires (≥1,000 acres, MTBS) in 2012–2016 increase poverty rates in affected counties by 2016–2019.
- Direction: Positive ATT on poverty rate
- Magnitude: Unknown; economically significant if ≥1–2 percentage points

**H2** (mechanism): Wildfires reduce household incomes in affected counties.
- Direction: Negative ATT on median household income
- Interpretation: Income loss as a pathway to poverty increase

**H3** (mediation): Population displacement (out-migration) partially mediates the poverty increase.
- Prediction: Positive ATT on net-migration rate (out-migration); indicates compositional mechanism
- Alternative: Small or zero migration ATT → income effects dominate

**H4** (dose-response): Effects scale with fire exposure (fire frequency and acres burned).
- Prediction: Intensive-margin ATT (per additional fire, per 10,000 acres) comparable to or larger than extensive-margin ATT
- Interpretation: Supports causal fire-poverty linkage (dose-response)

### Specification Freeze

**Primary sample**:
- Geographic scope: All lower-48 US counties (~3,100 counties)
- Treatment window: 2012–2015 (fires occurring during this period define treated counties)
- Analysis periods: 
  - **Pre-1**: 1990 Census (baseline for formal pre-trend test)
  - **Pre-2**: 2000 Census (baseline for formal pre-trend test)
  - **Pre-3**: 2007–2011 ACS (baseline)
  - **Post**: 2015–2019 ACS (outcome; 3–8 years post-fire; avoids COVID-2020)
- Unit: County
- **Treated**: ≥1 MTBS fire ≥1,000 acres in 2012–2015
- **Never-treated**: No fires in 2012–2015 AND outside 100 km smoke buffer
- **Excluded**: Pre-2012 fires (used for matching covariates, not controls); post-2015 fires (not-yet-treated); pop <1,000

**Primary outcomes** (in order of priority):
1. Poverty rate (% population below federal poverty line)
2. Median household income (nominal, 2019$)
3. Net-migration rate (% population moved in − % moved out, past 5 years; ACS)
4. Employment rate (% civilian labor force employed)

**Primary estimator**: Simple Difference-in-Differences with Multiple Pre-Treatment Periods
- Model: $\text{Outcome} = \alpha_c + \lambda_t + \tau \cdot (\text{treated} \times \text{post}) + X_{\text{pre}} \gamma + \epsilon$
- Estimand: $\tau$ = ATT (average treatment effect on the treated)
- Weighting: Inverse-probability weights (PS-IPW) from propensity score matching
- Pre-treatment periods (1990, 2000, 2007–2011) allow formal testing of parallel trends
- SE: Clustered at county level; 95% CIs via bootstrap (1,000 replicates)
- Covariates: WFP 2012 quintile, pre-2012 fire history, baseline poverty/income/density/RUCC

**Extensive margin** (primary):
- Treatment: Binary = 1 if any fire in 2012–2015

**Intensive margin** (robustness):
- Treatment: Fire count (1, 2, 3+) or total acres burned (per 10,000 acres)

**Mediation specification**:
- Direct effect on poverty: ATT (main)
- Mediator (net migration): ATT on migration rate
- Indirect effect: ATT(migration) × coefficient(migration → poverty)
- Direct-only effect: Total ATT − Indirect effect

### Deviations from PAP (post-hoc, to be flagged)

Any change to the following must be explicitly noted and justified:
- Sample restrictions (pop threshold, fire-definition change, geographic exclusions)
- Treatment window (start/end year of 2012–2016)
- Outcome definition (poverty threshold, income deflator, migration measure)
- Estimator (if not simple DID with PS-IPW)
- Analysis periods (if not 2007–2011 vs. 2016–2019)

Minor deviations (exploratory subgroup analysis, additional robustness not pre-registered) do NOT require amendment but must be labeled exploratory.

---

## 7. Folder Structure & Data Setup

```
wildfire-poverty-analysis/
├── data/
│   ├── raw/                          # Original downloads (git-ignored)
│   │   ├── acs_extracts/             # IPUMS 5-year ACS extracts (2012, 2017, 2022 at tract level)
│   │   ├── mtbs_perimeters/          # Symlink or copy from wildfire-finance/data/raw/mtbs_perims/
│   │   ├── whp_rasters/              # WFP 2012 & WHP 2014 GeoTIFFs at native 270m resolution (from wildfire-finance)
│   │   ├── tract_shapefiles/         # TIGER Census 2010 tract boundaries (all lower-48)
│   │   └── county_shapefiles/        # TIGER county boundaries (for RUCC merge)
│   ├── processed/                    # Analysis-ready datasets
│   │   ├── acs_2012_2022_tract_clean.parquet          # Poverty, income, employment, net migration (tract × 3 periods); MOE-screened
│   │   ├── fire_treatment_assignment_tract.parquet    # Tract treatment year (g=2017, g=2022, g=0); extensive + intensive margins
│   │   ├── whp_2012_tract_raster_summaries.parquet    # Tract-level aggregates from 270m WFP 2012 raster (mean %, quintile %, distance)
│   │   ├── matching_covariates_2012_tract.parquet     # Pre-treatment baseline covariates (2012 ACS tract-level)
│   │   ├── smoke_buffer_100km_tract.parquet           # Tract-level smoke exclusion flag (100 km buffer)
│   │   └── analysis_sample_final_tract.parquet        # Final unbalanced panel (~40k–50k tracts × 3 periods)
│   └── metadata/
│       ├── tract_fips_names.csv
│       ├── fire_cohort_counts_tract.csv               # N tracts by g=2017, g=2022, g=0
│       ├── sample_restrictions_log.txt                # Doc all exclusions with counts (MOE, pop, smoke)
│       ├── raster_processing_log.txt                  # Document WFP 2012 raster extraction and tract-level aggregation
│       └── data_dictionary.md                         # Variable definitions and sources (tract-level specifics)
├── code/
│   ├── 01_build/
│   │   ├── __init__.py
│   │   ├── 01_whp_to_tract.py        # **NEW**: Raster (270m) → tract-level WFP 2012 summaries (mean, quintiles, distance)
│   │   ├── 02_mtbs_to_tract.py        # **UPDATED**: Fire perimeters → tract treatment assignment; compute % tract area burned
│   │   ├── 03_acs_pull.py            # IPUMS ACS extraction (tract-level; poverty, income, migration, employment; 2012, 2017, 2022)
│   │   ├── 04_matching_covariates.py # Baseline (2012) covariate assembly at tract level
│   │   ├── 05_smoke_buffer.py        # 100 km exclusion zone construction (updated for tract-level buffering)
│   │   ├── 06_moe_screening.py       # **NEW**: ACS MOE screening; drop tracts with MOE > 30% of poverty estimate
│   │   └── 07_panel_assemble.py      # Final unbalanced panel assembly (tract × period)
│   ├── 02_matching/
│   │   ├── __init__.py
│   │   ├── 01_ps_matching.R          # Propensity score & IPW with raster covariates (tract-level)
│   │   └── 02_balance_table.R        # Balance diagnostics post-IPW (including raster-based covariates)
│   ├── 03_analysis/
│   │   ├── __init__.py
│   │   ├── 01_cs_main.R              # Callaway & Sant'Anna (staggered, tract-level)
│   │   ├── 02_event_study.R          # Event-study $\beta_h$ and aggregate ATT; event-study plots
│   │   ├── 03_mediation_analysis.R   # Net-migration as mediator (decompose poverty effects)
│   │   ├── 04_robustness.R           # Robustness checks (smoke radius, fire threshold, ACS 2020+, MOE threshold, raster matching precision, etc.)
│   │   ├── 05_sun_abraham.R          # Sun-Abraham heterogeneity-robust estimator
│   │   ├── 06_heterogeneity.R        # Subgroup estimates (region, urbanicity, baseline poverty/WFP, fire frequency, cohort)
│   │   └── 07_placebo_falsification.R # Pre-2013 fire assignment falsification test
│   ├── 04_output/
│   │   ├── __init__.py
│   │   ├── 01_tables.R               # Generate LaTeX and CSV regression tables
│   │   ├── 02_figures.py             # Publication-ready figures (300 DPI); event-study plots, PS density, map
│   │   └── 03_plot_styles.py         # Matplotlib defaults (fonts, colors, consistent styling)
│   └── main.py                       # Top-level pipeline orchestration
├── tests/
│   ├── __init__.py
│   ├── test_raster_processing.py     # **NEW**: Test WFP 2012 raster extraction and tract aggregation
│   ├── test_data_assembly.py         # Test tract-level data loading and merging
│   ├── test_sample_restrictions.py   # Verify MOE, smoke, population exclusion logic
│   └── test_estimation.py            # Unit tests for C&S DiD estimation
├── notebooks/
│   ├── 01_eda_tract.ipynb            # **UPDATED**: Exploratory tract-level (fire, poverty, income distributions; raster visualization)
│   ├── 02_raster_exploration.ipynb   # **NEW**: WFP 2012 raster visualization; tract-raster intersection QA
│   ├── 03_balance_diagnostics.ipynb  # IPW balance visualization (raster-based covariates)
│   ├── 04_event_study_exploration.ipynb # Dynamic effects exploration (C&S event-study)
│   └── 05_heterogeneity_exploration.ipynb # Subgroup results (updated for larger tract-level subgroups)
├── results/
│   ├── tables/
│   │   ├── table_1a_summary_stats_pre_ipw.csv
│   │   ├── table_1b_summary_stats_post_ipw.csv
│   │   ├── table_2_main_att.csv
│   │   ├── table_3_extensive_intensive_margins.csv
│   │   ├── table_4_mediation_analysis.csv
│   │   ├── table_5_robustness.csv
│   │   ├── table_6_subgroup_heterogeneity.csv
│   │   ├── table_sun_abraham_comparison.csv
│   │   └── appendix_*.csv
│   ├── figures/
│   │   ├── figure_1_tract_fires_map.png
│   │   ├── figure_2_event_study_poverty.png
│   │   ├── figure_3_event_study_income.png
│   │   ├── figure_4_ps_density_pre_post_ipw.png
│   │   ├── figure_5_whp_2012_raster_example.png
│   │   └── (additional robustness plots)
│   └── rds/
│       ├── cs_att_main.rds
│       ├── event_study_coefs.rds
│       ├── mediation_results.rds
│       ├── sun_abraham_att.rds
│       ├── balance_diagnostics.rds
│       └── robustness_results.rds
├── docs/
│   ├── RESEARCH_PLAN.md              # This file (updated for tract-level + raster design)
│   ├── LITERATURE_NOTES.md           # Annotated bibliography (populated via /deep-research)
│   ├── DATA_DICTIONARY.md            # Variable definitions, sources, tract-level processing notes
│   ├── PAP.md                        # Pre-analysis plan (updated for tract-level staggered DiD design)
│   ├── METHODOLOGY_NOTES.md          # Technical details (raster processing, tract-raster intersection, C&S vs. simple DiD)
│   └── RASTER_METHODS.md             # **NEW**: Detailed documentation of 270m WFP 2012 raster processing workflow
├── .gitignore                        # Exclude data/raw/, .RData, .rds, *.pyc, .parquet
├── setup.py
├── requirements.txt                  # Python deps: pandas, geopandas, rasterio, rioxarray, etc.
├── CLAUDE.md                         # Project-specific coding standards
├── README.md
└── .env.example                      # (Optional) env var template for API keys, paths
```

**Key changes from county-level design**:
- **Unit of analysis**: Census tract (2010 boundaries) instead of county
- **Sample size**: ~70,000 tracts × 3 periods (~210,000 obs), reduced to ~40,000–50,000 tracts after screening (~120,000–150,000 obs)
- **Raster processing**: New workflow (`01_whp_to_tract.py`) extracts 270m WFP 2012 pixels and aggregates to tract-level summaries (mean, quintiles, distance)
- **Matching covariates**: Raster-based (mean WFP percentile, quintile indicators, raster distance) at native 270m resolution, not county-level WFP aggregation
- **Estimation**: Callaway & Sant'Anna staggered DiD (two cohorts: g=2017, g=2022) instead of single cohort
- **Data quality**: MOE screening for ACS tract-level estimates (drop if MOE > 30% of point estimate)
- **Subgroups**: Larger subgroup sample sizes (10,000–20,000 tracts per subgroup) vs. county (750–1,000 per subgroup)

---

## 8. Success Criteria & Checkpoints

| Checkpoint | Criterion | Target Date |
|-----------|-----------|------|
| **Raster processing complete** | WFP 2012 GeoTIFF (270m) loaded; tract-level summaries computed (mean percentile, quintile %, distance); output parquet | Week 2 |
| **Data acquisition & cleaning** | All ACS (2012, 2017, 2022 tract-level), MTBS, WFP 2012 raster loaded; ~70,000 tracts × 3 periods; MOE screening applied (MOE ≤ 30%); pop ≥ 500; expected ~40,000–50,000 tracts | Week 4 |
| **Treatment assignment** | Staggered cohorts (g=2017, g=2022) finalized; n_treated ≥ 1,200 tracts; smoke-buffer (100 km) exclusion applied; sample counts documented | Week 4 |
| **Propensity score matching** | PS-IPW weights computed with raster covariates; balance diagnostics run; SMD < 0.1 all covariates post-IPW; ESS ≥ 500 | Week 5 |
| **Main C&S DiD estimation** | ATT estimate + 95% CI computed for poverty rate (primary outcome) using C&S staggered DID with PS-IPW; event-study $\beta_h$ reported | Week 6 |
| **All outcomes ATT** | C&S estimates reported for: poverty, income, employment, net migration; event-study plots + aggregates with 95% CIs; N obs | Week 6 |
| **Mediation analysis** | Net-migration ATT computed; indirect and direct effects decomposed; % mediation calculated | Week 7 |
| **Dose-response (intensive margin)** | C&S ATT per fire count, per 10,000 acres, and per WFP percentile; compared to extensive-margin ATT | Week 7 |
| **Robustness complete** | ≥10 robustness checks run (raster matching precision, smoke radius, fire threshold, treatment window, placebo, regional FE, ACS 2020+, MOE threshold, stricter never-treated, CEM); tabulated | Week 8 |
| **Sun-Abraham heterogeneity check** | Sun & Abraham (2021) estimator run; compared to C&S aggregate ATT | Week 8 |
| **Heterogeneous effects** | Subgroup analysis (region, urbanicity, baseline poverty, baseline WFP, fire frequency, cohort) reported as exploratory; sample sizes and CI overlaps documented | Week 8 |
| **Publication-ready output** | All tables at 300 DPI, LaTeX-formatted; figures (event-study plots, PS density, map); full results folder | Week 8 |
| **Manuscript draft** | Introduction, Methods, Results, Discussion, Conclusion written; Tables 1–4 and robustness embedded; appendix with raster methods | Week 9 |
| **Final deliverables** | Replication package (code, cleaned data, results); PAP + deviation log; Zenodo/SSRN preprint | Week 10+ |

---

## 8.5 Rural Data Quality: Critical Design Decision

**Context**: Majority of large wildfires (MTBS ≥1,000 acres) occur in rural areas. Rural tracts have sparse populations, making ACS estimates inherently noisier. **This is a feature of rural demography, not a flaw in study design.**

**Design Choices (Locked In)**:
1. **ACS 5-year estimates only** (not 3-year, not 1-year)
   - 5-year estimates provide adequate rural sample sizes for valid inference
   - 3-year and 1-year estimates are unreliable for rural geographies (acknowledge in Limitations)
   - Trade-off: Temporal resolution (5-year windows) vs. rural data reliability (5-year estimates needed)

2. **MOE screening at 30% threshold** (not 20%, not 40%)
   - Baseline: Drop tracts if MOE > 30% of poverty-rate point estimate
   - Justification: 30% threshold balances data quality and sample retention; allows rural tracts with reasonable MOE precision
   - Robustness: Vary threshold (20%, 40%); report results separately for rural vs. urban subgroups
   - Document: Report N tracts dropped, breakdown by urbanicity, median MOE for included rural tracts

3. **Report rural results transparently**
   - Rural subgroup estimates (in Phase 5) should report ATT ± 95% CI alongside median MOE
   - Caption note: "Rural tract estimates have wider confidence intervals due to ACS 5-year sampling for sparse populations; this expected precision reflects design, not weakness"
   - Suppress formal statistical tests for rural vs. urban subgroup differences (confounded by MOE differences)

4. **Temporal alignment implications**
   - Pre-treatment baseline (2012 ACS, 2008–2012 window): ~4–6 years pre-fire for g=2017 cohort
   - Post-treatment measurement (2017 ACS, 2013–2017 window): ~1–4 years post-fire for early-cohort fires
   - Flag in Limitations: Medium-term effects (3–5 years post-fire) primary; longer-term persistence cannot be assessed with current data
   - Suggest: As 2023 ACS becomes available, extend to 2027 window for longer-term follow-up

---

## 9. Known Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **ACS tract-level data quality (rural focus)** | Tract-level ACS estimates have larger MOEs than county-level. **Rural tracts (where majority of fires occur) have systematically larger MOE because ACS 5-year samples are sparse for low-density areas.** ~30% of tracts may fail MOE > 30% screen, with rural tracts disproportionately excluded. ACS 3-year and 1-year estimates unsuitable for rural geographies; must use 5-year only. | Use ACS 5-year estimates exclusively (do NOT use 3-year/1-year even for robustness). Implement MOE screening (drop if MOE > 30% of point estimate); report N tracts excluded, broken down by urbanicity (rural vs. urban/suburban). Conduct robustness: vary MOE threshold (20%, 30%, 40%); assess whether rural subgroup estimates remain stable. Document median MOE for rural vs. urban tracts. Acknowledge in Limitations: Rural estimates have wider CIs by design (ACS sampling limitation), not statistical flaw. |
| **Thin common support (raster matching)** | Many high-WFP tracts never experience fires; IPW reweighting may reduce effective control pool drastically. Tract-level design increases this risk. | Check ESS carefully (target ≥ 500; flag if << unweighted control N). Conduct robustness: drop extreme propensity scores; check ATT sensitivity. Consider alternative: CEM on WFP raster quintiles. Report if common support is limiting. |
| **Raster-tract intersection precision** | 270m WFP pixels may not align perfectly with tract boundaries; aggregation to tract-level summaries introduces measurement error. | Conduct spot-checks: verify 50 tracts' raster-tract overlaps in GIS. Test robustness: re-estimate using (a) county-level WFP aggregation (pre-update design), (b) full raster covariates (current). Compare ATTs. If ATT materially changes, raster precision matters; report prominently. |
| **ACS disclosure avoidance (2020 onward)** | Differential privacy noise inflates variance; especially problematic for small geographies like sparse tracts. | Use 5-year estimates (averaging reduces noise). Conduct sensitivity: (a) drop 2020-based ACS, re-estimate on 2012–2017 period, (b) report whether results change. Flag in limitations if variance materially increases. |
| **Fire-poverty endogeneity (selection on unobservables)** | WFP raster matching reduces but doesn't eliminate selection bias; tracts with latent poverty drivers may sort into high-WFP areas. | Acknowledge in limitations. Raster matching is partial adjustment. Interpret ATT as effect conditional on observables (WFP + baseline covariates), not causal in unconditional sense. Propose future IV strategy (e.g., climate-driven fire variation, terrain-based instruments). |
| **Heterogeneous treatment effects (HTE) across cohorts** | Callaway & Sant'Anna robust to HTE in aggregation, but g=2017 and g=2022 cohorts may have different long-term effects. | Run Sun & Abraham (2021) estimator as robustness. Compare C&S aggregate ATT to Sun-Abraham. If materially different, flag HTE as important. Report by-cohort estimates as exploratory. |
| **Subgroup power (tract-level)** | Larger sample (70k tracts vs. 3k counties) allows larger subgroups, but still limited for rare subgroup combinations. | Report subgroup N's and ESS. Emphasize: subgroup estimates exploratory; do NOT formally test differences. Report point estimates + CIs; note overlaps descriptively. |
| **MTBS threshold at 1,000 acres** | Limits to consequential fires; small fires excluded; results not generalizable to all wildfire exposures. May exclude majority of fires nationally. | Clearly state scope condition in Introduction and Limitations. Conduct robustness: lower threshold to 500 acres, re-estimate, report effect magnitude change. Trade-off: cleaner ID vs. limited scope. Document how many fires/tracts excluded by 1,000-acre rule. |
| **Smoke spillover proxy (100 km)** | Actual smoke transport varies by fire size, time of year, wind patterns; 100 km is rough approximation. Tract-level buffering may be imprecise. | Vary in robustness: 50 km (conservative), 100 km (baseline), 150 km (permissive). Plot ATT vs. buffer radius; check stability. If unstable, flag smoke exclusion as identification-critical. Conduct GIS spot-check (10 fires). |
| **Event-study pre-trends (Roth 2022 critique)** | Null test of $\beta_h$ (h<0) underpowered; "non-significant pre-trends" don't validate parallel trends. | Do NOT report p-values for pre-trend test. Instead: visualize all $\beta_h$ with CIs (include h<0 and h≥0 in one plot). Describe magnitude of pre-trends relative to post-trends. If pre-trends small and parallel (flat, zero-centered), support parallel trends. If divergent or large, discuss implications. |
| **Net-migration measurement** | ACS "residence 5 years ago" is noisy proxy; misses temporary migrants, undocumented populations. | Acknowledge limitation. ACS migration variable is proxy for net in-migration (net inflow). Cannot separately identify gross in vs. out flows. Mediation results exploratory. Suggest future work: admin tax records (IRS 1040 migration data). |
| **Limited post-fire follow-up** | g=2022 cohort only has 1 post-treatment period (2022 ACS); cannot assess persistence beyond 5 years. | Acknowledge in Limitations. As post-2022 ACS data released, study can be extended. For now, results show effects up to 5 years post-fire (g=2017) and 1 year (g=2022). Flag g=2022 estimates as preliminary. |

---

## 10. References & Key Papers

### Methodological (Core)
- Callaway, B., & Sant'Anna, P. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
- Roth, J. (2022). Pretest with caution: High-powered tests can be misleading. *Journal of Business & Economic Statistics*, 40(3), 897–906.
- Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2), 175–199.
- Arkhangelsky, D., Athey, S., Blundell, R., Félix, M., Gentzkow, M., & Shapiro, J. H. (2021). Synthetic difference-in-differences. *American Economic Review*, 111(12), 4088–4118.

### Wildfire Economics (To be populated via `/deep-research`)
- Boomhower, J. (2019). Drilling in lemons: Assessing the costs of oil and gas development in the U.S. *American Economic Review*, 109(12), 4437–4485.
- Borgschulte, A., Corrigan, J., Rao, N., & Smith, R. B. (2024). Wind and wildfire smoke: Air pollution as a source of depressive symptoms. *Journal of Environmental Economics and Management*, [TBD].

### Poverty & Income Literature (To be populated via `/deep-research`)
- Autor, D. H., Dorn, D., & Hanson, G. H. (2013). The China syndrome: Local labor market effects of import competition in the United States. *American Economic Review*, 103(6), 2121–2168.
- Kline, P., & Moretti, E. (2014). People, places, and public policy. *Journal of Economic Literature*, 52(3), 729–761.

### Migration & Displacement (To be populated via `/deep-research`)
- Blanchard, O. J., & Katz, L. F. (1992). Regional evolutions. *Brookings Papers on Economic Activity*, 1992(1), 1–75.
- [Additional papers to be identified]

---

## 11. Next Steps (Before Data Analysis)

1. **Week 0 (this week — planning + raster setup)**:
   - [ ] Review this updated RESEARCH_PLAN.md; confirm tract-level + raster design is approved
   - [ ] Test WFP 2012 raster access from `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`
   - [ ] Download Census 2010 tract shapefiles (lower-48 US) from TIGER
   - [ ] Obtain tract-level IPUMS ACS extracts (2012, 2017, 2022); confirm tract-level poverty/income available
   - [ ] Register updated PAP on OSF, AEA RCT Registry, or SSRN (staggered DiD, tract-level design, raster matching)

2. **Weeks 1–2 (Raster Processing + ACS Tract Acquisition)**:
   - [ ] Implement `code/01_build/01_whp_to_tract.py`: Load WFP 2012 GeoTIFF (270m); compute tract-level summaries (mean, quintiles, distance)
   - [ ] Spot-check 50 tracts: verify raster-tract intersection in GIS
   - [ ] Download/extract tract-level ACS (2012, 2017, 2022); document available variables
   - [ ] Download MTBS fire perimeters and county RUCC codes

3. **Weeks 2–4 (Data Cleaning + Treatment/Control Assembly)**:
   - [ ] Implement `code/01_build/02_mtbs_to_tract.py`: Tract-fire spatial join; compute % tract area burned
   - [ ] Implement `code/01_build/03_acs_pull.py`: Load tract ACS; flag missing/invalid values
   - [ ] Implement `code/01_build/06_moe_screening.py`: Drop tracts with MOE > 30% poverty estimate; document N dropped
   - [ ] Implement `code/01_build/04_matching_covariates.py`: Baseline (2012) covariates; RUCC merge
   - [ ] Implement `code/01_build/05_smoke_buffer.py`: 100 km buffer around fire perimeters; flag excluded tracts
   - [ ] Implement `code/01_build/07_panel_assemble.py`: Final unbalanced panel; document sample counts by cohort (g=2017, g=2022, g=0)
   - [ ] Output: `analysis_sample_final_tract.parquet`; verify n_treated ≥ 1,200 tracts

4. **Week 5 (Propensity-Score Matching & Balance with Raster Covariates)**:
   - [ ] Implement `code/02_matching/01_ps_matching.R`: Logistic PS model on raster covariates (mean WFP, quintile %, distance) + fire history + baseline covariates
   - [ ] Compute IPW weights; trim 99th percentile
   - [ ] Implement `code/02_matching/02_balance_table.R`: SMD before/after; target SMD < 0.1
   - [ ] Check ESS of reweighted control group; target ESS ≥ 500
   - [ ] Visualize: propensity score density (treated vs. control, pre/post reweighting), raster covariate distributions

5. **Weeks 5–7 (Estimation + Mediation + Robustness)**:
   - [ ] Implement `code/03_analysis/01_cs_main.R`: C&S staggered DiD (tract-level, IPW); estimate $\beta_h$ and aggregate ATT
   - [ ] Generate event-study plots (poverty, income, employment, net migration); mark pre/post regions
   - [ ] Implement `code/03_analysis/03_mediation_analysis.R`: Decompose poverty ATT via net-migration mediator
   - [ ] Implement `code/03_analysis/04_robustness.R`: Run 10+ robustness specs (raster matching precision, smoke radius, MOE threshold, fire threshold, placebo, etc.)
   - [ ] Implement `code/03_analysis/05_sun_abraham.R`: Sun & Abraham (2021) heterogeneity-robust estimator as robustness
   - [ ] Implement `code/03_analysis/06_heterogeneity.R`: Subgroup estimates (region, urbanicity, baseline poverty/WFP, fire frequency, cohort); document ESS per subgroup

6. **Week 8 (Publication Output + Heterogeneity Viz)**:
   - [ ] Implement `code/04_output/01_tables.R`: Generate CSV + LaTeX tables (T1a, T1b, T2, T3, T4, T5, T6, Sun-Abraham comparison)
   - [ ] Implement `code/04_output/02_figures.py`: Event-study plots, PS density, tract-fire map, WFP 2012 raster example; all 300 DPI
   - [ ] Compile `results/tables/` and `results/figures/`; verify publication-ready format

7. **Weeks 9+ (Manuscript + Dissemination)**:
   - [ ] Draft Introduction (hook: within-county heterogeneity, raster-based matching advantage; RQ; contribution)
   - [ ] Draft Methods (identify variation, estimand, C&S spec, tract-raster matching, threats + mitigations)
   - [ ] Draft Results (main ATT table, event-study plot, mediation decomposition, extensive vs. intensive margins)
   - [ ] Draft Robustness section (organized by threat; reference Table 5)
   - [ ] Draft Discussion (mechanisms, scope—MTBS >1000 acres, raster precision trade-offs, limitations)
   - [ ] Iterate with peer feedback; finalize manuscript
   - [ ] Prepare replication package (all code, processed data parquets, results, updated PAP + deviations doc)
   - [ ] Submit to JUE, RSUE, or AEJ:Applied

---

*End of Research Plan. Version 2.0 (expanded to lower-48 US; mechanism on net migration; regression adjustment; extensive+intensive margins; 2013–2021 treatment window; mandatory PAP).*
