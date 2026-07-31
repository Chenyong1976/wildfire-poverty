# Empirical Design: Wildfire Impact on Poverty

**Last Updated**: 2026-07-30  
**Design Status**: Ready for critical assessment (Iteration 1/4)

---

## 1. Panel Design: Census Tract × ACS Period

### Structure
**Unbalanced panel**: Census tract $i$ × ACS period $t$

| Dimension | Definition | Notes |
|-----------|-----------|-------|
| **Units** | Census tracts, Census 2010 definition | ~70,000 tracts lower-48 US; after MOE screening & pop ≥500: ~40,000–50,000 tracts |
| **Time periods** | ACS 5-year estimates | 2012 (baseline, 2008–2012 window), 2017 (2013–2017), 2022 (2018–2022) |
| **Unbalanced**: | Not all tracts in all periods | ACS tract data sparse in earlier periods; panel becomes denser over time |
| **Treatment cohorts** | Staggered | g=2017 (first fire 2013–2016), g=2022 (first fire 2017–2021), g=0 (never-treated) |
| **N observations** | ~120,000–150,000 | 40k–50k tracts × 3 periods (accounting for missing data) |
| **Control group** | Never-treated, smoke-excluded | Tracts with no MTBS fires 2013–2021, outside 100 km buffer |

### Data Quality Screen (Rural Focus)
- **ACS 5-year estimates only**: Restrict to 2012, 2017, 2022 (no 3-year or 1-year estimates; unreliable for rural tracts where fires concentrate)
- **MOE threshold**: Drop tracts if poverty-rate MOE > 30% of point estimate
- **Population minimum**: Drop tracts if population < 500
- **Report by urbanicity**: Document MOE distribution and sample counts separately for rural (RUCC 4–9) and urban/suburban (RUCC 1–3) tracts

---

## 2. Wildfire Exposure Measures

### Extensive Margin (Binary Treatment)
**Primary measure**: Tract-fire intersection
- **Treatment**: Tract = 1 if tract polygon intersects MTBS fire polygon (≥1,000 acres), 0 otherwise
- **Timing**: First large fire in 2013–2021 defines treatment cohort (g=2017 or g=2022)
- **Spatial definition**: Any overlap of tract boundary with MTBS perimeter counts as treated

### Intensive Margin (Dose-Response)

#### 1. Fire Frequency
- **Fire count**: Number of MTBS fires (≥1,000 acres) per tract in treatment window
- **Categories**: 1 fire, 2 fires, 3+ fires
- **Interpretation**: Tests whether repeated fire exposure compounds poverty effects

#### 2. Burned Acreage
- **Total acres burned**: Sum of acres from all fires overlapping tract (may exceed tract area if fire spans multiple tracts)
- **Burned share**: % of tract area burned (computed from tract-fire intersection; max 100%)
- **Normalization**: Report per 10,000 acres for interpretability

#### 3. Wildfire Hazard Intensity (Raster-Based)
- **Mean WFP 2012 percentile**: Average USFS Wildfire Potential (0–100 scale) across all 270m pixels overlapping tract
- **Predetermined**: Finalized before 2013 treatment window; use as continuous treatment proxy in intensive-margin specification
- **Rationale**: Captures baseline hazard heterogeneity; tracts with higher pre-treatment WFP may experience different fire-poverty dynamics

#### 4. Distance to Fire Perimeter
- **Nearest fire distance**: Minimum distance from tract boundary to nearest MTBS fire perimeter
- **Definition**: Continuous measure (kilometers)
- **Interpretation**: Tests whether effects attenuate with distance (smoke spillover, commuting disruption)
- **Threshold**: Tracts within X km treated; use in robustness (X = 0, 50, 100, 150 km)

### Smoke Exposure (If Data Available)
- **Smoke plume modeling**: NOAA HYSPLIT or equivalent (not yet acquired; flag as TBD)
- **Fallback**: Use 100 km smoke buffer (baseline) and vary in robustness (50, 150 km)
- **Uncertainty**: Actual smoke transport varies by fire size, season, wind; 100 km is proxy only

---

## 3. Poverty Outcomes: Primary & Secondary

### Primary Outcome
**Poverty rate** (%)
- **Definition**: % of tract population below official federal poverty line (Census Bureau definition; thresholds vary by family size, age, composition)
- **Source**: ACS 5-year tract-level estimate
- **Measurement error**: ACS MOE larger for rural tracts; document separately
- **Interpretation**: Tract-level poverty headcount; sensitive to both individual income changes and selective migration

### Secondary Outcomes

#### Economic Outcomes
| Outcome | Definition | Source | Rural Consideration |
|---------|-----------|--------|-----------|
| **Median HH income** (primary) | Median household income (nominal, 2020$) | ACS 5-yr | Tract-level estimates; larger MOE in rural areas |
| **Employment rate** | % civilian labor force employed | ACS 5-yr | Labor market adjustment; rural measurement via 5-yr pooling |
| **Per capita income** | Per capita income (county-level) | BEA NIPA, FRED API | Robustness cross-check only; county-level less precise for tract impacts |
| **Industry employment** | % employed in agriculture, forestry, extraction | ACS 5-yr | Sector vulnerability (rural tracts typically high); measure if IPUMS sample adequate |

#### Poverty Subgroup Outcomes (If IPUMS Sample Adequate)
- **Child poverty rate**: % of persons age <18 in poverty
- **Deep poverty rate**: % below 50% of poverty line
- **Poverty by race/ethnicity**: Disaggregated by racial/ethnic groups (if n sufficient)
- **Poverty by age**: Separately for children, working-age, elderly

### Mediator Outcome (for Mediation Analysis)
**Net-migration rate** (%)
- **Definition**: % of tract population that moved into tract during past 5 years minus % that moved out (ACS "residence 5 years ago")
- **Interpretation**: Proxy for population displacement; larger MOE in rural tracts; cannot separately identify gross in- vs. out-flows

---

## 4. Causal Identification Strategy

### Recommended Approach: Staggered Difference-in-Differences (C&S 2021)

#### Baseline Specification
$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \neq -1} \beta_h \cdot \mathbb{1}[g_i = t - h] \cdot \mathbb{1}[t \geq g_i] + X_{i,2012} \gamma + \epsilon_{i,t}$$

where:
- $i$ = tract; $t$ = ACS period (2012, 2017, 2022)
- $g_i$ = cohort (year of first fire; g=2017, g=2022, g=0)
- $h$ = relative time to treatment (h<0 pre-fire, h≥0 post-fire)
- $\beta_h$ = treatment effect $h$ periods relative to fire
- $\alpha_i$ = tract fixed effects; $\lambda_t$ = period fixed effects
- $X_{i,2012}$ = pre-treatment covariates (WFP raster summaries, fire history, baseline poverty/income, RUCC, demographics)
- **Weighting**: Inverse-probability weights from PS-IPW raster matching

#### Why Callaway & Sant'Anna 2021 (Not Simple DID)
1. **Staggered treatment**: g=2017 and g=2022 cohorts have different treatment onset times
2. **Heterogeneous effects**: C&S robust to treatment effect heterogeneity across cohorts & time periods
3. **Avoids contaminated controls**: Never-treated (g=0) never transition to treatment; only cohort-by-cohort comparison valid
4. **Appropriate for disasters**: Multi-year treatment window aligns with reality of staggered fire years

#### Event-Study Interpretation
- **$\beta_h$ for h<0**: Pre-trends (should be ~zero if parallel trends holds)
- **$\beta_h$ for h=0, 1, 2, ...**: Post-treatment dynamic effects
- **Aggregate ATT**: $\widehat{\text{ATT}} = \frac{1}{k} \sum_{h \geq 0} \beta_h$ (simple average, or weighted by time-at-risk)

### Propensity-Score Matching (PS-IPW)
To reduce selection bias from endogenous fire location:

**Propensity score model** (logit):
$$\Pr(\text{treated} | X) = \text{logit}(\alpha + X \beta)$$

where $X$ includes:
- **Raster-based WFP 2012 summaries** (270m resolution): mean percentile, % per quintile, distance to high-hazard pixel
- **Pre-2013 fire history**: any MTBS fire 1984–2012, log acres burned
- **Baseline (2012 ACS) covariates**: poverty rate, median HH income, population density, % age 65+, % race/ethnicity
- **RUCC**: rural-urban classification (county-level)

**IPW weights**:
- Treated: $w_i = 1$
- Control: $w_i = \hat{e}_i / (1 - \hat{e}_i)$ (where $\hat{e}_i$ = estimated Pr(treated))
- **Trim**: 99th percentile to stabilize variance
- **Report**: Effective sample size (ESS) of reweighted control group; flag if ESS << unweighted N

---

## 5. Identifying Assumptions & Validity Tests

### Core Assumption: Conditional Parallel Trends (C&S 2021)
**Statement**: Given covariates $X_{i,2012}$ and PS-IPW matching, treated and never-treated tracts would follow parallel poverty trends absent wildfire treatment.

**Interpretation**: Post-matching, fire location is unconfounded conditional on observed baseline covariates (WFP hazard, fire history, poverty, income, demographics).

### Threats & Tests

| Threat | Test | Expected Result | Interpretation |
|--------|------|-------|------------|
| **Differential pre-trends** | Estimate $\beta_h$ for h<0 (pre-treatment periods) | $\beta_h ≈ 0$ with 95% CI excluding zero | If pre-trends negligible, parallel trends plausible |
| **Anticipatory behavior** | Lead specification: regress outcome on leads of treatment | Leads coefficients ≈ 0 | If residents pre-adjust before fire, leads will be nonzero |
| **Placebo/falsification** | Assign fires to pre-2013 years; estimate C&S ATT | ATT ≈ 0 | If result zero, confounding from pre-treatment trends unlikely |
| **Alternative exposure measure** | Replace binary with continuous (acres, WFP intensity) | Results scale proportionally | If dose-response holds, stronger causal evidence |
| **Alternative control group** | Exclude never-treated with pre-2013 fires (stricter definition) | ATT similar magnitude | If stricter control group gives same result, selection bias not driving estimates |
| **Smoke spillover** | Vary 100 km buffer (50, 150 km exclusion radii) | ATT stable across radii | If sensitive to buffer, smoke spillover threatens identification |
| **Migration/compositional change** | Mediation analysis: ATT on migration + indirect effect | Decompose total ATT | Separates income effects from migration effects |
| **Sample selection** | Vary MOE threshold (20%, 30%, 40%) by urbanicity | ATT stable in rural and urban subsamples | If results differ sharply by MOE threshold, measurement error biases estimates |
| **Regional confounds** | Add census-division × period FE to specification | ATT similar to baseline | If regional controls change results, regional shocks confound |
| **Spatial autocorrelation** | Test residual spatial correlation; use spatial clustering for SE | Report Moran's I; cluster by county | If high autocorrelation, standard error estimates understated |

---

## 6. Technical Issues: ACS, Boundaries, Repeated Fires, Displacement

### A. ACS Sampling Error & Multiyear Estimates

**Challenge**: ACS tract-level estimates have large MOE, especially for rural tracts.

**Design decision**: Use ACS 5-year estimates ONLY (2012, 2017, 2022)
- Rationale: 5-year aggregation provides adequate rural sample sizes; 3-year and 1-year estimates unreliable for sparse rural tracts
- Trade-off: Coarse temporal resolution (5-year snapshots) but valid rural measurement
- Pre-treatment baseline (2012 ACS, window 2008–2012) ends ~4–6 years before fires (2013–2016 for g=2017 cohort)
- Post-treatment (2017 ACS) captures ~1–4 years post-fire; medium-run effects (3–5 yr) primary focus

**Robustness check**: Vary MOE exclusion threshold (20%, 30%, 40%); report results separately for rural vs. urban tracts

### B. Tract-Boundary Harmonization

**Challenge**: Census tract boundaries change over time; 2000 vs. 2010 boundaries differ.

**Solution**: Use Census 2010 tract boundaries for entire study period (2012–2022)
- Pre-2010 data (if used) harmonized to 2010 definitions via Census crosswalk
- ACS 5-year estimates already aligned to Census 2010 by IPUMS
- Fire perimeters and WFP raster both align to same projection (EPSG:5070)

**Verification**: Spot-check 50 tracts for boundary consistency across ACS periods

### C. Repeated Wildfire Exposure

**Challenge**: Some tracts experience multiple large fires in treatment window (2013–2021); cohort assignment ambiguous.

**Design choice**: **First-fire rule**
- $g_i$ = year of **first** large fire (≥1,000 acres) in 2013–2021
- Subsequent fires same tract classified as repeated exposure (intensive margin)
- Interpretation: ATT estimates effect of initial fire; intensive-margin specification tests dose-response

**Rationale**: Aligns with C&S 2021 framework (single treatment time per unit); repeated fires captured as treatment intensity

### D. Treatment Intensity (Continuous Measures)

**Challenge**: Binary treatment assumes homogeneous effect; fires vary in size, severity, location within tract.

**Specification**: Estimate C&S with continuous treatment:
$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \neq -1} T_{i,h} \cdot \mathbb{1}[g_i = t - h] \cdot \delta_h + X_{i,2012} \gamma + \epsilon_{i,t}$$

where $T_{i,h} \in \{$acres burned, % burned, fire count, WFP intensity$\}$

**Interpretation**: $\delta_h$ = effect per unit of treatment intensity; tests whether larger fires have larger poverty effects

### E. Spatial Correlation & Clustering

**Challenge**: Wildfire impacts cluster spatially (neighboring tracts affected similarly); standard errors understated.

**Solution**: Cluster standard errors at **county level**
- Rationale: County = typical unit of fire response/regional shock
- Alternative: Multi-way clustering (tract, county, state × year) in robustness
- Report: Both standard and spatial-cluster SEs in tables

**Verification**: Test residual spatial autocorrelation (Moran's I) before/after clustering

### F. Post-Disaster Population Displacement

**Challenge**: Wildfires trigger out-migration; tract population may decline, affecting poverty rate mechanically.

**Measurement**: Separate resident-level from tract-level effects
1. **Resident-level (intent-to-treat)**: Poverty of residents originally in tract (track via ACS 5-yr residence data if feasible)
2. **Tract-level (mechanical)**: Poverty rate of tract population (mix of stayers + new arrivals)
3. **Decomposition**: Total ATT = intent-to-treat + compositional change

**Mediation analysis** quantifies compositional effect:
- Indirect effect = ATT(net-migration) × coefficient(migration → poverty)
- If indirect effect large, composition change dominates

---

## 7. Heterogeneity Analyses

### Primary Dimensions

| Dimension | Subgroups | N (approx.) | Rationale |
|-----------|-----------|---|-----------|
| **Baseline poverty** | High (>20%), Medium (10–20%), Low (<10%) | ~15k–20k each | Do fires disproportionately harm poor tracts? |
| **Urbanicity** | Urban (RUCC 1–3), Rural (RUCC 4–9) | ~10k / ~25k | Rural tracts more vulnerable? Note: rural estimates have larger MOE |
| **Fire severity** | Low, medium, high (if MTBS severity data available) | TBD | Do high-severity fires have larger poverty effects? |
| **Geographic region** | South, Midwest, Northeast, West | ~8k–12k each | Regional heterogeneity (fire regimes, economic structure) |
| **Baseline WFP hazard** | High (>75th %), Medium (50–75th %), Low (<50th %) | ~15k each | Do high-hazard tracts adapted to fires? |

### Secondary Dimensions (If Data Permit)

| Dimension | Data Source | Feasibility |
|-----------|-----------|-----------|
| **Race/ethnicity** | IPUMS ACS tract-level extract | Possible if sample adequate; poverty by race subgroups |
| **Housing tenure** | IPUMS ACS; % renters | Possible; renters may be more vulnerable to displacement |
| **Social vulnerability** | CDC/ATSDR SVI or NOAA-derived indices | TBD; county-level SVI available; tract-level requires external matching |
| **Disaster declarations** | FEMA or NOAA disaster database | Possible; flag tracts with declared disasters; test if relief modifies effects |
| **Local econ structure** | BEA industry employment; ACS sector employment | Possible; test if forestry/tourism-dependent tracts have different effects |

### Estimation
- Estimate C&S event-study separately for each subgroup
- Report ATT ± 95% CI by subgroup
- **Caution**: Do NOT formally test subgroup differences (multiple comparison problem); report descriptively with CI overlaps
- **Rural subgroups**: Report alongside median MOE; note that wider CIs expected due to sparse ACS sampling

---

## 8. Separating Resident Economic Changes from Migration-Driven Changes

### Challenge
Tract-level poverty rate reflects both:
1. **Individual income changes**: Residents in tract experience income loss (welfare loss)
2. **Compositional change**: Low-income residents leave, high-income move in (mechanical poverty reduction without welfare gain)

### Solution: Mediation Analysis Framework

#### Step 1: Estimate Total Effect
$$\text{Poverty}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{pov}} \cdot \mathbb{1}[g_i = t-h] + X \gamma + \epsilon$$
- Estimand: $\text{ATT}^{\text{pov}}$ (total effect on poverty rate)

#### Step 2: Estimate Effect on Mediator
$$\text{Net-Migration}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{mig}} \cdot \mathbb{1}[g_i = t-h] + X \gamma + \epsilon$$
- Estimand: $\text{ATT}^{\text{mig}}$ (effect on net-migration rate)

#### Step 3: Estimate Mediator→Outcome Regression
$$\text{Poverty}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{pov,cond}} \cdot \mathbb{1}[g_i = t-h] + \gamma \cdot \text{Net-Migration}_{i,t} + X \gamma' + \epsilon$$
- Estimand: $\gamma$ (effect of migration on poverty, holding fire treatment constant)

#### Step 4: Decomposition
- **Indirect effect** (compositional): $\text{ATT}^{\text{mig}} \times \gamma$ (how much of poverty change driven by migration)
- **Direct effect** (income loss): $\text{ATT}^{\text{pov}} - \text{Indirect effect}$ (poverty change not mediated by migration)

#### Interpretation
- **Large indirect effect**: Out-migration is key mechanism; poverty improvement reflects sorting, not welfare gains
- **Large direct effect**: Income effects dominate; poverty increase reflects resident income losses

**Caveat**: Mediation analysis relies on ACS migration measure (noisy, 5-year window); results exploratory

---

## 9. Critical Assessment Checkpoint

**Iteration 1 Review Questions:**

1. **Identification threat not adequately addressed?** 
   - Spatial spillover (smoke, commuting) controlled via geographic buffer; varies in robustness
   - Regional shocks controlled via state×period FE; varies to division×period
   - Selection bias on observables via PS-IPW raster matching; unobservables remain threat (flag in limitations)

2. **Design choice questionable?**
   - First-fire rule: Justified by C&S framework; captured as intensity margin
   - ACS 5-year only: Necessary for rural validity; temporal coarseness acknowledged
   - 100 km smoke buffer: Proxy only; varies in robustness

3. **Sample power adequate?**
   - Expected n=40k–50k tracts; ~10–15× county-level power
   - Rural tracts have larger MOE but valid 5-year samples
   - Adequate for overall ATT; subgroup power moderate (n~15k per major subgroup)

4. **Measurement error problematic?**
   - ACS MOE documented; robustness varies threshold
   - Migration variable (5-yr window) noisy; results labeled exploratory
   - Fire severity unavailable; use binary + acres as proxy

**Proceed to empirical_design.md revision if major issues identified. Otherwise, move to paper_outline.md.**

