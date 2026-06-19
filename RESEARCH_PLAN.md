# Research Plan: Wildfire Impact on Poverty and Economic Outcomes

**Last Updated**: 2026-06-18  
**Principal Investigator**: [Your Name]  
**Project Directory**: `~/wildfire-poverty-analysis/`

---

## 1. Research Question & Motivation

### Primary Question
**How do large wildfires affect household incomes, poverty rates, net migration, and employment in affected US counties? What role does population displacement play in these effects?**

### Motivation
Wildfire frequency and severity have increased dramatically across the US over the past two decades, yet empirical evidence on economic impacts—particularly for vulnerable populations—remains limited. Most prior work focuses on health outcomes or Western states; this study extends to all lower-48 states and targets **distributional effects on income, poverty, and net migration**, which are central to understanding whether wildfires cause permanent income losses or trigger selective out-migration. We explicitly model net migration as a potential mediating mechanism: if wildfires displace low-income households from treated counties, county-level poverty rates may decline even if individual incomes fall (compositional effect), or county poverty may increase if displacement is incomplete (welfare loss dominates).

### Contribution
- **Empirical**: Quasi-experimental evidence of wildfires' causal impact on poverty, income, and net migration across all lower-48 US counties (not just Western states) using staggered DiD with WFP-matched controls
- **Mechanism**: Explicit analysis of net migration as a mediating pathway; decompose county-level poverty effects into individual income losses and population composition shifts
- **Methodological**: Replicates the rigorous treatment/control definition and matching strategy from the wildfire-finance project (WFP 2012 matching, PS-IPW, Callaway & Sant'Anna 2021)
- **Policy**: Estimates inform disaster relief allocation, climate adaptation spending, and migration assistance design; highlight whether "economic impact" reflects welfare loss or population reallocation

---

## 2. Identification Strategy

### Design: Simple Difference-in-Differences (Single Treatment Cohort)

**Treatment**: County experiences its first large fire (MTBS ≥1,000 acres) in **2012–2016** (treatment window).

**Treatment cohort** (single):
- **Treated** (g=2016): First qualifying fire in 2012–2016; observed post-fire at 2016–2019 ACS
- **Never-treated** (g=0): No qualifying fires in 2012–2016 AND outside 100 km smoke buffer

**Excluded groups**:
- Pre-2012 fires: Used for covariate balance in matching (pre-treatment fire history), not as controls
- Fires 2017+: Excluded entirely (not-yet-treated; may be affected by post-2017 fires not yet observed)

**Extensive margin**: County ever experiences any large fire (≥1,000 acres) in 2012–2016.

**Intensive margin**: Fire frequency (count of fires 2012–2016) and total acres burned (dose-response).

**Estimand**: Average treatment effect on the treated (ATT) — the causal effect of experiencing a wildfire in 2012–2016 on outcomes (poverty rate, median income, net migration, employment) measured at 2016–2019 (post-fire), relative to pre-treatment baseline (2007–2011).

**Variation**: Within the 2012–2016 window, fire occurrence varies geographically and temporally across the lower-48 US counties. Counties that never burned (2012–2016) form the comparison group.

### Threats to Identification & Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Selection bias**: High-hazard regions (economically vulnerable, dry terrain) experience fires endogenously | **WFP 2012 matching** (predetermined): Use USFS Wildfire Potential 2012 (finalized before 2013 fire season) as primary matching variable via propensity-score inverse-probability weights (PS-IPW). Balance treated and control counties on WFP quintile, pre-2012 fire history, pre-2012 poverty rate, median income, population density, RUCC, and demographic covariates. Report effective sample size (ESS) of reweighted control group. |
| **Anticipatory behavior**: Counties expect fires and adjust preemptively (e.g., out-migration before fire) | **Pre-trend testing**: Report pre-treatment coefficients ($\beta_{h<0}$) from event-study with 95% CIs (not null-hypothesis tests). Assess visual magnitude and direction of divergence before treatment. If pre-trends modest relative to post-treatment effects, interpret as minor deviation from perfect parallelism. Dynamic balance test: regress outcome on leads of treatment (falsification test). |
| **Smoke spillover**: "Control" counties may be exposed to smoke from nearby treated counties' fires | **Geographic exclusion**: Remove counties within 100 km of any fire perimeter from the control group (baseline, following wildfire-finance). Robustness: vary radius (50 km, 150 km). Report whether narrower buffers materially change results. |
| **Temporal confounds**: Other regional shocks (economic downturns, housing bubbles, energy transitions, COVID) coincide with fires | **Regional FEs**: Include state × year FE (census-period basis, not annual) to absorb regional-year shocks. Robustness: add census division × year FE for finer regional control. Document any divergence in results. |
| **Migration composition bias**: County-level poverty rates reflect both individual income effects AND selection of who stays/leaves | **Mediation analysis (§4.2)**: Estimate causal effect on net migration (ACS 5-yr residence change) as a potential mediator. Separately report: (a) individual-level intent-to-treat effects (income, poverty at origin), (b) county-level ATT on poverty rate, (c) decomposition: income effect + compositional effect. Flag in discussion if large migration effects suggest compositional change. |
| **Effect heterogeneity**: Wildfires may have different impacts by geography, baseline poverty, fire severity | **Extensive and intensive margin**: Report both (a) any large fire (extensive) and (b) fire frequency/acreage (intensive) separately. Heterogeneous effects: subgroup analysis by baseline poverty (high vs. low), census region (coastal vs. interior). Report Sun & Abraham (2021) alongside Callaway & Sant'Anna as robustness check for heterogeneity bias. |

### Estimating Equations

**Main specification** (simple difference-in-differences with multiple pre-treatment periods):

$$\text{Outcome}_{c,t} = \alpha_c + \lambda_{t} + \mathbb{1}[\text{treated}_c \times \text{post}_t] \cdot \tau + X_{c,\text{pre}} \gamma + \epsilon_{c,t}$$

where:
- $c$ = county
- $t \in \{\text{pre-1990}, \text{pre-2000}, \text{pre-2007-2011}, \text{post-2015-2019}\}$ (3 pre-treatment, 1 post-treatment period)
- $\text{treated}_c$ = 1 if county has ≥1 MTBS fire ≥1,000 acres in 2012–2015, 0 otherwise
- $\text{post}_t$ = 1 if $t =$ post-treatment (2015–2019), 0 if $t \in$ pre-treatment (1990, 2000, 2007–2011)
- $\tau$ = **ATT** (average treatment effect on the treated)
- $\alpha_c$ = county fixed effects
- $\lambda_t$ = period fixed effects (1990, 2000, 2007–2011, 2015–2019)
- $X_{c,\text{pre}}$ = pre-treatment covariates (WFP 2012 quintile, pre-2012 fire history, baseline poverty/income)
- Standard errors clustered at county level; inverse-probability weights (from PS-IPW matching) applied

**Interpretation**:
- $\tau$ = difference-in-differences estimate; causal ATT under parallel trends assumption (conditional on matching covariates)
- **Multiple pre-treatment periods (1990, 2000, 2007–2011) allow formal testing of parallel trends assumption**
- Post-treatment measured at 2015–2019 ACS (3–8 years post-fire); longer adjustment window than v3.0
- No event-study window; direct estimate of aggregate treatment effect

**Robustness: Regression adjustment variant**:

$$\text{Outcome}_{c,t} = \alpha_c + \lambda_t + \tau \cdot \mathbb{1}[\text{treated}_c \times \text{post}_t] + X_{c,\text{pre}} \gamma + \text{State FE} + \epsilon_{c,t}$$

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
- **Geographic scope**: All lower-48 US states (~3,100 counties)
- **Time period**: Census and ACS data with three analysis periods:
  - **Pre-treatment baseline** (formal parallel trends test):
    - 1990 Census (poverty, income, employment)
    - 2000 Census (poverty, income, employment)
    - 2007–2011 ACS (poverty, income, employment)
  - **Treatment window**: 2012–2015 (fires occurring during this period define treated counties; ensures ≥1 year post-fire observation before outcome window)
  - **Post-treatment**: 2015–2019 ACS (outcome measurement; 3–8 years post-fire; avoids COVID-2020)
- **Unit of analysis**: County
- **Treatment cohort**: Single cohort with first qualifying fire in 2012–2015
- **N**: ~3,100 counties × 3 periods = ~9,300 observations (balanced panel; all lower-48 counties in 1990, 2000, and 2015–2019 observations)

**Pre-treatment periods allow formal parallel trends testing**:
- 1990 and 2000 Census provide two independent pre-treatment observations
- Can formally test whether treated and control counties follow parallel trends (1990→2000, 2000→2007–2011)
- Strengthens identification vs. single pre-period design

### Outcome Variables

| Outcome | Data Source | Definition | Rationale |
|---------|-------------|-----------|-----------|
| **Poverty rate** (primary) | ACS 5-yr | % population below federal poverty line | Primary outcome; distributional focus |
| **Median HH income** | ACS 5-yr | Median household income (nominal, adjusted to 2020$) | Household income measure |
| **Employment rate** | ACS 5-yr | % civilian labor force employed | Labor market adjustment |
| **Net-migration rate** (mediator) | ACS 5-yr (residence change) | % population moved into county minus % moved out, in past 5 years | **New: Explicit mediation analysis**; proxy for population displacement |
| **Per capita income** | BEA Regional Economic Accounts (annual) | Per capita income by county | Cross-check income effects; FRED API |
| **Industry employment share** | ACS 5-yr or USDA NASS | Share employed in agriculture, forestry, recreation, natural resource extraction | Sector-specific vulnerability |

**Aggregation for census-period analysis**:
- ACS 5-year estimates are available for 2007–2011, 2012–2016, 2017–2021, 2018–2022 windows (overlapping 5-year rolling averages)
- **Align to census year**: Assign 5-year ACS estimate to the final year of the estimate (e.g., ACS 2007–2011 labeled as "2011" ≈ "2012 analysis year")
- For BEA per-capita income (annual), interpolate or use the closest single year to the census period
- Document this alignment in data dictionary

### Treatment Definition

**Extensive margin (any fire)**:
- **Treated**: County experiences its first large fire (MTBS polygon ≥1,000 acres) in **2012–2015**.
- **Fire perimeter definition** (replicating wildfire-finance):
  - Use MTBS database (1984–2022 fires, nationwide coverage)
  - Minimum size threshold: 1,000 acres (limits to consequential fires; trade-off: cleaner identification vs. limited scope)
  - Spatial match: MTBS fire polygon overlaps county boundary (any overlap counts as treated in fire year)
- **Single cohort**: All treated counties have first fire in 2012–2015 window; ensures ≥1 year post-fire observation before 2015–2019 outcome measurement
- **Rationale**: Narrower treatment window (2012–2015 vs. 2012–2016) ensures homogeneous treatment exposure time; all fires have time to affect outcomes by 2015–2019 ACS

**Intensive margin (fire frequency/acreage)**:
- **Fire count**: Number of large fires (≥1,000 acres) per county in 2012–2015 (0, 1, 2, 3+)
- **Total acres burned**: Sum of acres burned across all large fires per county in 2012–2015
- **Report both specifications**: (a) binary any-fire indicator (extensive), (b) dose-response by fire frequency or acreage (intensive)

### Control Definition

**Never-treated**:
- Counties with no large fire (≥1,000 acres, MTBS) in **2012–2015** AND outside 100 km smoke buffer

**Excluded groups**:
- **Pre-2012 fires (≤2011)**: Used in matching covariates (pre-treatment fire history) to control for baseline fire exposure. Counties with pre-2012 fires are **excluded from the never-treated pool** (not used as controls). This avoids confounding from prior fire recovery/adaptation effects.
- **Post-2015 fires (≥2016)**: Counties with first fire in 2016+ are excluded entirely (not-yet-treated; would be affected by fires after outcome measurement window)
- **Smoke-exposed controls**: Counties within **100 km** of any treated county's fire perimeter (baseline, following wildfire-finance). Robustness: vary radius (50 km, 150 km).

**Matching covariates** (using PS-IPW):
- **WFP 2012 quintile** (predetermined): USFS Wildfire Potential 2012, finalized before treatment window (2012–2015)
- **Pre-2012 fire history**: Any large fire in 1984–2011, total acres burned 1984–2011
- **Baseline (2007–2011 or 2000) covariates from ACS/Census**: Poverty rate, median household income, population density, % age 65+
- **RUCC**: USDA Rural-Urban Continuum Code (2013 vintage)
- **Other**: Population (for weighting; drop counties with pop <1,000)

**Balance diagnostics**:
- Report standardized mean differences (SMD) before and after PS-IPW matching (target: SMD < 0.1 for all covariates)
- Report effective sample size (ESS) of reweighted control group; flag if ESS << unweighted N (thin common support)

### Data Sources & Acquisition

| Variable | Source | Format | Notes |
|----------|--------|--------|-------|
| Poverty rate, median income, employment, net migration | ACS 5-yr (IPUMS) | CSV extracts | **Use 5-year estimates aligned to census years** (2007, 2012, 2017, 2022; labeled by final year of estimate). Account for disclosure avoidance in 2020 onward (larger standard errors; consider 5-yr aggregation or sensitivity dropping 2020-based estimates). |
| Per capita income | BEA NIPA | CSV (FRED API) or REIS | Annual series; interpolate or use single-year closest to census period. |
| Industry employment | ACS 5-yr (reuse from poverty extract) | CSV | Extracted from IPUMS along with poverty/income variables. |
| Fire perimeters & treatment assignment | MTBS (USGS) | Shared from wildfire-finance project | Reuse `wildfire-finance/data/raw/mtbs_perims/` and treatment assignment files (g=2017, g=2022 cohorts). |
| **WFP 2012** (primary matching) | USFS | GeoTIFF (270m resolution, ESRI Grid) | Shared from wildfire-finance project: `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/wfp2012_cnt`. **Predetermined for fires from 2013 onward** (finalized before 2013 fire season). |
| WHP 2014 (robustness) | USFS | GeoTIFF (270m resolution) | Shared from wildfire-finance: `wildfire-finance/data/raw/WHP/Data/whp_2014_continuous/whp2014_cnt`. NOT predetermined for 2013–2014 fires; use in robustness only. |
| County boundaries | USGS / Census | Shapefile | Standard TIGER county geographic frame. |
| Baseline covariates (2012) | ACS, USDA RUCC | CSV / API | From IPUMS and USDA; for matching and balance diagnostics. |
| Smoke buffer (100 km) | Derived from MTBS | Parquet | Reuse from wildfire-finance: `wildfire-finance/data/processed/fire_perimeters_100km_buffer.parquet`. Regenerate for national sample if needed. |

---

## 4. Methods: Implementation Roadmap

### 4.1 Phase 1: Data Acquisition & Cleaning (Weeks 1–3)

**Deliverables**:
- `acs_2007_2022_county_clean.parquet`: Poverty, income, employment, net migration by county-census-period (2007, 2012, 2017, 2022)
- `fire_treatment_assignment.parquet`: County treatment year (g=2017, g=2022, or g=0 for never-treated); extensive and intensive margins
- `whp_2012_county.parquet`: County-level WFP 2012 percentile (from raster; reuse from wildfire-finance if available)
- `matching_covariates_2012.parquet`: Pre-treatment baseline covariates (2012 ACS: poverty, income, demographics; RUCC; population)
- `smoke_buffer_100km.parquet`: Counties within 100 km of any MTBS fire perimeter (exclusion list)
- `analysis_sample_final.parquet`: Balanced panel (~3,100 counties × 4 periods ≈ 12,400 obs) after smoke exclusion and population minimum restriction (pop ≥ 1,000)

**Quality checks**:
- Flag missing values: if ACS estimate has margin of error > 30% of point estimate, flag as unreliable
- Document disclosure avoidance impact: if 2020-based ACS estimates available, report whether dropping them changes results (sensitivity check)
- Cross-check BEA per-capita income against ACS median income for directional consistency
- Verify fire treatment assignment: sample fires from each cohort; manually inspect GIS county-fire overlap (edge cases: fires spanning state lines, large fires touching many counties)
- Confirm smoke buffer: spot-check 10–20 fire perimeters and 100 km buffer geometry in GIS

### 4.2 Phase 2: Propensity-Score Matching & Balance Diagnostics (Week 4)

**Approach** (following wildfire-finance design):

1. **Propensity score model**: Logistic regression of treatment (g ≠ 0) on:
   - WFP 2012 quintile (5 indicators)
   - Pre-2013 fire indicator and pre-2013 log acres burned
   - Pre-treatment covariates (2012 ACS: poverty rate, median HH income, population density, % 65+; USDA RUCC; population size)
   - Outcome: $\text{Pr}(\text{treated} | X)$

2. **Inverse-probability weights** (IPW):
   - Treated counties: $w_i = 1$
   - Control counties: $w_i = \hat{e}_i / (1 - \hat{e}_i)$ (where $\hat{e}_i$ = estimated propensity score)
   - Trim at 99th percentile of weights to stabilize variance

3. **Balance diagnostics**:
   - Compute standardized mean differences (SMD) before and after IPW reweighting
   - Target: SMD < 0.1 for all covariates after reweighting
   - Report effective sample size (ESS) of reweighted control group (sanity check on common support)
   - Plot: density of propensity scores, treated vs. control (before and after reweighting)
   - If ESS << unweighted control N, flag thin common support and discuss implications

### 4.3 Phase 3: Main Estimation — DiD & ATT (Weeks 5–6)

**Estimation approach** (Simple Difference-in-Differences with Multiple Pre-Periods for Parallel Trends Testing):

Use **R package `fixest::feols()`** or standard TWFE with inverse-probability weights:

1. **Main DID estimation**:
   - Outcome: poverty rate (primary), median income, employment rate, net migration (secondary)
   - Treatment: binary indicator = 1 if county has ≥1 fire in 2012–2015, 0 if never-treated
   - Periods: 4 (pre-1: 1990; pre-2: 2000; pre-3: 2007–2011; post: 2015–2019)
   - Specification: outcome ~ treated × post + county FE + period FE + covariates, weights = IPW
   - Coefficient $\tau$ (treated × post) = **ATT** (main estimand)
   - SE: clustered at county level; 95% CIs via bootstrap (1,000 replicates)

2. **Formal parallel trends testing**:
   - **Three pre-treatment observations (1990, 2000, 2007–2011)** allow formal testing of parallel trends
   - Estimate treatment coefficients for each pre-period: $\tau_{1990}, \tau_{2000}, \tau_{2007-2011}$
   - Null hypothesis: $\tau_{1990} = \tau_{2000} = \tau_{2007-2011} = 0$ (no pre-treatment effect)
   - Visual inspection: Plot coefficients by period; should see zero trend pre-treatment, jump post-treatment
   - If pre-treatment coefficients near zero and parallel, supports parallel trends assumption (conditional on covariates)
   - If pre-treatment coefficients trending or diverging, suggests differential pre-trends → flag as robustness sensitivity

3. **Aggregate ATT**:
   - Point estimate: $\widehat{\text{ATT}} = \hat{\tau}$ (coefficient on treated × post)
   - Report 95% CI, effect size (e.g., percentage point change in poverty rate), and N observations
   - Interpret economically: "A large fire in 2012–2016 increased poverty rate by X percentage points by 2016–2019"

4. **Extensive vs. intensive margin**:
   - **Extensive (binary)**: Main specification above (any fire in 2012–2016)
   - **Intensive (dose-response)**: Replace binary treatment with continuous:
     - Fire count (1, 2, 3+ fires) → estimate ATT per additional fire
     - Total acres burned (in 10,000-acre units) → estimate ATT per 10,000 acres
   - Report both; compare magnitudes to assess dose-response relationship

5. **Mediation analysis (net-migration)**:
   - **Step 1**: Estimate ATT on net-migration rate (same DID spec as poverty)
   - **Step 2**: Regress poverty on fire treatment AND net-migration (to get mediator coefficient)
   - **Step 3**: Decompose: Total ATT = Direct effect (controlling for migration) + Indirect effect (migration-mediated)
   - **Interpret**: 
     - Large indirect effect → out-migration is key mechanism (compositional effect)
     - Small indirect effect → income effects dominate (welfare loss mechanism)
   - **Flag**: Mediation estimates are sensitive to measurement error in migration variable; treat exploratory

### 4.4 Phase 4: Robustness & Sensitivity Checks (Week 7)

**Organized by identification threat** (simple DID design):

| Threat | Robustness Test | Rationale |
|--------|-----------------|-----------|
| **Smoke spillover** | Vary geographic exclusion radius: 50 km, 100 km (baseline), 150 km | If ATT stable across radii, smoke spillover exclusion not driving results. |
| **Fire size threshold** | Vary minimum MTBS acres: 500, 1,000 (baseline), 2,000 | Tests sensitivity to fire definition; controls for definitional robustness. |
| **Treatment window timing** | Shift treatment year: fires 2011–2015, 2012–2016 (baseline), 2013–2017 | Tests whether results depend on exact treatment window boundaries. |
| **Placebo / falsification test** | Use pre-period outcome (2007–2011) as dependent variable; assign fires to 2012–2016 (same as treatment) | If ATT ≈ 0 on pre-period outcome, supports no confounding from time trends. (Note: technically not a placebo since same outcome, but tests whether fires pre-treat.) |
| **Specification: add regional controls** | Add state FE; add census division FE | Tests whether results robust to regional-level confounds. |
| **Specification: exclude ACS 2020 onward** | Drop any ACS estimates with 2020+ data (to avoid differential privacy); re-estimate on 2007–2019 window only | Tests sensitivity to ACS disclosure avoidance introduced 2020+. |
| **Sample: population restriction** | Drop counties with pop < 500 or pop < 5,000 (vs. baseline 1,000) | Very small counties have unreliable ACS estimates. |
| **Sample: stricter never-treated** | Exclude counties with any fire in pre-treatment period (2007–2011) from controls | More conservative control definition (only truly never-exposed counties). |
| **Sample: drop CA, OR** | Exclude California and Oregon (highest fire density) | Tests whether results CA/OR-driven; broader generalizability check. |
| **Matching robustness: CEM** | Coarsened exact matching (CEM) on WFP quintiles + baseline poverty bins (alternative to PS-IPW) | Checks whether PS-IPW balance results are robust to alternative matching approach. |
| **Dose-response** | Estimate ATT per fire (fire count: 1, 2, 3+) and per 10,000 acres burned | Tests whether effects scale with exposure intensity. |

### 4.5 Phase 5: Heterogeneous Effects Analysis (Week 8)

**Subgroup analysis** (limited by power; emphasize exploratory nature):

| Dimension | Subgroups | N (approx.) | Rationale |
|-----------|-----------|---|-----------|
| **Census region** | South, Midwest, Northeast, West | ~750 each | Fire regimes differ by region (Western fires more common, Eastern more rare; may trigger different economic response) |
| **Baseline poverty** | High (>20%), Medium (10–20%), Low (<10%) | ~1,000 each | Policy interest: do fires hit poor counties harder? |
| **Fire frequency** | 0 fires (never), 1 fire, 2+ fires | ~2,100 / 700 / 300 | Dose-response: do repeated fires compound effects? |
| **Time period** | Fires 2013–2016 (g=2017), Fires 2017–2021 (g=2022) | ~630 / 370 | Temporal heterogeneity: do recent fires (when adaptation awareness higher) have smaller effects? |

**Estimation**:
- Re-estimate C&S event-study separately for each subgroup
- Report $\widehat{\text{ATT}}$ and 95% CI by subgroup
- **Statistical testing**: Do NOT formally test subgroup differences (low power; inflates Type I error). Instead, report point estimates and intervals; note overlaps or separation as descriptive finding.
- Flag: "Subgroup estimates are exploratory due to limited sample size per group; interpret with caution."

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
│   │   ├── acs_extracts/             # IPUMS 5-year ACS extracts (2007–2022 estimates)
│   │   ├── mtbs_perimeters/          # Symlink or copy from wildfire-finance/data/raw/mtbs_perims/
│   │   ├── whp_rasters/              # WFP 2012 & WHP 2014 rasters (from wildfire-finance)
│   │   └── county_shapefiles/        # TIGER county boundaries
│   ├── processed/                    # Analysis-ready datasets
│   │   ├── acs_2007_2022_county_clean.parquet      # Poverty, income, employment, net migration
│   │   ├── fire_treatment_assignment.parquet       # Treatment cohorts (g=2017, g=2022, g=0)
│   │   ├── whp_2012_county.parquet                 # County-level WFP 2012 percentile
│   │   ├── matching_covariates_2012.parquet        # Pre-treatment baseline covariates
│   │   ├── smoke_buffer_100km.parquet              # Exclusion list (100 km smoke buffer)
│   │   └── analysis_sample_final.parquet           # Final balanced panel (all lower-48, 4 periods)
│   └── metadata/
│       ├── county_fips_names.csv
│       ├── fire_cohort_counts.csv                  # N counties by g=2017, g=2022, g=0
│       ├── sample_restrictions_log.txt             # Doc all exclusions with counts
│       └── data_dictionary.md
├── code/
│   ├── 01_build/
│   │   ├── __init__.py
│   │   ├── 01_whp_to_county.py       # Raster → county WFP 2012 (reuse from wildfire-finance)
│   │   ├── 02_mtbs_to_county.py      # Fire perimeters → treatment assignment (reuse/adapt)
│   │   ├── 03_acs_pull.py            # IPUMS ACS extraction (poverty, income, migration, employment)
│   │   ├── 04_matching_covariates.py # Baseline (2012) covariate assembly
│   │   ├── 05_smoke_buffer.py        # 100 km exclusion zone construction (reuse)
│   │   └── 06_panel_assemble.py      # Final balanced panel assembly
│   ├── 02_matching/
│   │   ├── __init__.py
│   │   ├── 01_ps_matching.R          # Propensity score & IPW (R script)
│   │   └── 02_balance_table.R        # Balance diagnostics post-IPW
│   ├── 03_analysis/
│   │   ├── __init__.py
│   │   ├── 01_cs_main.R              # Callaway & Sant'Anna main (extensive + intensive)
│   │   ├── 02_event_study.R          # Event-study plot and dynamic effects
│   │   ├── 03_mediation_analysis.R   # Net-migration as mediator
│   │   ├── 04_robustness.R           # Robustness checks (smoke radius, fire threshold, etc.)
│   │   ├── 05_sun_abraham.R          # Sun-Abraham heterogeneity-robust estimator
│   │   ├── 06_heterogeneity.R        # Subgroup estimates (region, baseline poverty, fire frequency)
│   │   └── 07_placebo_falsification.R # Pre-2013 fire assignment falsification test
│   ├── 04_output/
│   │   ├── __init__.py
│   │   ├── 01_tables.R               # Generate LaTeX and CSV regression tables
│   │   ├── 02_figures.py             # Publication-ready figures (300 DPI)
│   │   └── 03_plot_styles.py         # Matplotlib defaults (fonts, colors, etc.)
│   └── main.py                       # Top-level pipeline orchestration
├── tests/
│   ├── __init__.py
│   ├── test_data_assembly.py         # Test data loading and merging
│   ├── test_sample_restrictions.py   # Verify exclusion logic
│   └── test_estimation.py            # Unit tests for DiD estimation
├── notebooks/
│   ├── 01_eda.ipynb                  # Exploratory: fire, poverty, income distributions
│   ├── 02_balance_diagnostics.ipynb  # IPW balance visualization
│   ├── 03_event_study_exploration.ipynb # Dynamic effects exploration
│   └── 04_heterogeneity_exploration.ipynb # Subgroup results
├── results/
│   ├── tables/
│   │   ├── table_1a_summary_stats_pre_ipw.tex
│   │   ├── table_1b_summary_stats_post_ipw.tex
│   │   ├── table_2_main_att.tex
│   │   ├── table_3_extensive_intensive.tex
│   │   ├── table_4_robustness.tex
│   │   ├── table_5_subgroup_heterogeneity.tex
│   │   └── appendix_*.tex
│   ├── figures/
│   │   ├── figure_1_fires_map.png
│   │   ├── figure_2_event_study_poverty.png
│   │   ├── figure_3_event_study_income.png
│   │   ├── figure_4_ps_density.png
│   │   └── ...
│   └── rds/
│       ├── cs_att_main.rds           # C&S ATT object
│       ├── event_study_coefs.rds     # Event-study $\beta_h$ and CIs
│       ├── mediation_results.rds     # Mediation analysis output
│       └── balance_diagnostics.rds
├── docs/
│   ├── RESEARCH_PLAN.md              # This file
│   ├── LITERATURE_NOTES.md           # Annotated bibliography (populated via /deep-research)
│   ├── DATA_DICTIONARY.md            # Variable definitions and processing notes
│   ├── PAP.md                        # Pre-analysis plan (register before analysis)
│   └── METHODOLOGY_NOTES.md          # Technical details (matching algorithms, DGP assumptions, etc.)
├── .gitignore                        # Exclude data/raw/, .RData, .rds, *.pyc
├── setup.py
├── requirements.txt                  # Python deps: pandas, geopandas, rasterio, etc.
├── CLAUDE.md                         # Project-specific coding standards
├── README.md
└── .env.example                      # (Optional) env var template for API keys, paths
```

---

## 8. Success Criteria & Checkpoints

| Checkpoint | Criterion | Target Date |
|-----------|-----------|------|
| **Data acquisition & cleaning** | All ACS (2007–2011, 2016–2019), MTBS, WFP 2012 datasets loaded; ~3,100 counties × 2 periods (~6,200 obs); missingness <2% | Week 3 |
| **Treatment assignment** | Single treated cohort (fires 2012–2016) finalized; n_treated ≥ 300 counties; smoke-buffer (100 km) exclusion applied; sample counts documented | Week 3 |
| **Propensity score matching** | PS-IPW weights computed; balance diagnostics run; SMD < 0.1 all covariates post-IPW; ESS ≥ 100 | Week 4 |
| **Main DID estimation** | ATT estimate + 95% CI computed for poverty rate (primary outcome) using simple DID with PS-IPW | Week 5 |
| **All outcomes ATT** | DID estimates reported for: poverty, income, employment, net migration; all with 95% CIs and N obs | Week 5 |
| **Mediation analysis** | Net-migration ATT computed; indirect and direct effects decomposed; % mediation calculated | Week 6 |
| **Dose-response (intensive margin)** | ATT per fire count and per 10,000 acres burned; compared to extensive-margin ATT | Week 6 |
| **Robustness complete** | ≥8 robustness checks run (smoke radius, fire threshold, treatment window timing, placebo, regional FE, pop restriction, CEM matching, dose-response); tabulated | Week 7 |
| **Heterogeneous effects** | Subgroup analysis (region, CA/OR drop) reported as exploratory; sample sizes flagged | Week 7 |
| **Manuscript draft** | Introduction, Methods, Results, Discussion, Conclusion written; Tables 1–3 and robustness table embedded | Week 9 |
| **Final deliverables** | Replication package (code, cleaned data, results); PAP + deviation log; Zenodo/SSRN preprint | Week 10+ |

---

## 9. Known Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Thin common support (national expansion)** | Many high-WFP counties never experience fires; IPW reweighting may reduce effective control pool drastically | Check ESS carefully; report if ESS << unweighted N. Conduct robustness dropping extreme propensity scores. Consider alternative matching (CEM on WFP quintiles). |
| **ACS disclosure avoidance (2020 onward)** | Differential privacy noise inflates variance; top-coding of income; especially problematic for small geographies | Use 5-year estimates (averaging reduces noise). Conduct sensitivity: (a) drop 2020-based ACS, re-estimate on 2007–2017 period, (b) report whether results change. Flag in limitations. |
| **Fire-poverty endogeneity (selection on unobservables)** | WFP matching reduces but doesn't eliminate selection bias; counties with latent poverty drivers may sort into high-fire areas | Acknowledge in limitations. WFP is partial adjustment. Interpret ATT as effect conditional on observables, not unconditional causal effect. Propose future IV strategy (e.g., climate-driven fire variation). |
| **Heterogeneous treatment effects (HTE)** | Callaway & Sant'Anna robust to HTE in aggregation, but subgroup power limited; subgroup estimates unreliable | Pre-register main (aggregate) ATT as primary. Label subgroup estimates exploratory. Emphasize: do NOT formally test subgroup differences. Report point estimates + CIs; note overlaps descriptively. |
| **MTBS threshold at 1,000 acres** | Limits to consequential fires; small fires excluded; results not generalizable to all wildfire exposures | Clearly state scope condition in Introduction and Limitations. Conduct robustness: lower threshold to 500 acres, re-estimate, report effect magnitude. Trade-off: cleaner ID vs. limited scope. |
| **Smoke spillover proxy (100 km)** | Actual smoke transport varies by fire size, time of year, wind patterns; 100 km is rough approximation | Vary in robustness: 50 km (conservative), 100 km (baseline), 150 km (permissive). Plot ATT vs. buffer radius; check stability. If unstable, flag smoke exclusion sensitivity. |
| **Pre-trend significance (Roth 2022 critique)** | Null test of pre-trends underpowered; "non-significant pre-trends" don't validate parallel trends | Do NOT report p-values for pre-trend test. Instead: visualize $\beta_h$ (h<0) with CIs; describe magnitude relative to post-treatment effects. If pre-trends small and slopes parallel (not divergent), interpret as supporting parallel trends. If pre-trends notable, discuss in limitations. |
| **Interstate migration not captured** | ACS "residence 5 years ago" misses temporary migrants, undocumented populations, and interstate moves within 5-year window | Acknowledge limitation. ACS migration variable is proxy for net migration. Cannot separately identify in vs. out migration. Suggest future work using administrative tax records (IRS 1040 migration data). |
| **Limited post-fire follow-up (max 7 years)** | g=2022 cohort only has 1 post-treatment observation (2022). Cannot assess longer-term persistence (5-10 years). | Acknowledge in Limitations. Note: as more post-2022 ACS data becomes available, study can be extended. Suggest in Future Work section. For now, results show effects up to 5–7 years post-fire. |

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

1. **Week 0 (this week)**:
   - [ ] Review this updated RESEARCH_PLAN.md with collaborators; obtain sign-off on design
   - [ ] Register PAP on OSF, AEA RCT Registry, or SSRN (lock in specifications)
   - [ ] Run `/deep-research` (lit-review mode) to populate References §10 and ground mechanism story in prior work

2. **Weeks 1–3 (Data Acquisition & Cleaning)**:
   - [ ] Download ACS 5-year estimates (2007–2022 period) for poverty, income, net migration, employment
   - [ ] Confirm MTBS fire perimeter data and WFP 2012 raster available (symlink from wildfire-finance or re-acquire)
   - [ ] Implement `code/01_build/` scripts; generate `analysis_sample_final.parquet`
   - [ ] Document all sample restrictions with counts; verify n_treated ≥ 600 counties

3. **Week 4 (Propensity-Score Matching & Balance)**:
   - [ ] Implement `code/02_matching/01_ps_matching.R`; compute IPW weights
   - [ ] Generate balance table; verify SMD < 0.1 all covariates
   - [ ] Check ESS of reweighted control group; report if < 100
   - [ ] Visualize propensity score distributions

4. **Weeks 5–7 (Estimation & Robustness)**:
   - [ ] Implement `code/03_analysis/01_cs_main.R`; estimate C&S ATT for all outcomes
   - [ ] Generate event-study plot and table; report pre-trends visually
   - [ ] Implement mediation analysis (`03_mediation_analysis.R`); quantify indirect effect
   - [ ] Run all 6+ robustness checks (`code/03_analysis/04_robustness.R`)
   - [ ] Generate heterogeneity tables (subgroups, extensive vs. intensive); flag exploratory nature

5. **Week 8 (Output & Visualization)**:
   - [ ] Generate publication-ready tables (LaTeX, 300 DPI)
   - [ ] Generate figures (event-study plot, PS density, map)
   - [ ] Compile all results into `results/` folder

6. **Weeks 9+ (Writing & Dissemination)**:
   - [ ] Draft manuscript (Introduction, Methods, Results, Discussion)
   - [ ] Iterate on peer feedback
   - [ ] Prepare replication package (data, code, results, PAP-deviations doc)
   - [ ] Submit to target journal (JUE, RSUE, or AEJ:Applied)

---

*End of Research Plan. Version 2.0 (expanded to lower-48 US; mechanism on net migration; regression adjustment; extensive+intensive margins; 2013–2021 treatment window; mandatory PAP).*
