# Empirical Design: Wildfire Impact on Poverty

**Last Updated**: 2026-07-30 (Iteration 2 revisions complete — all critical assessment issues addressed)

**Design-level warnings (flagged during critical review)**:
1. **Only one pre-treatment period per cohort** — with ACS periods 2012/2017/2022, each cohort has h=−1 and h=0 (or h=+1). Pre-trend testing is minimal; parallel trends credibility depends primarily on WFP matching, not validated pre-trends.
2. **ACS 2017 window contamination for g=2022** — The 2017 ACS (2013–2017 window) overlaps the treatment onset for g=2022 tracts (first fire 2017–2021). The "pre-treatment" period for g=2022 is not cleanly pre-treatment. Design must acknowledge this and restrict g=2022 use accordingly.
3. **Burned share preferred over any-overlap for primary treatment** — Binary "any intersection" is coarse; burned share (% of tract area within MTBS perimeter) should be the primary continuous measure with a minimum-overlap threshold for the binary indicator.
4. **Mediation is descriptive decomposition, not causal mediation** — Sequential regression cannot identify causal mediation without a no-unmeasured-confounding assumption for the mediator-outcome path. Label accordingly throughout.

---

## 1. Panel Design: Census Tract × ACS Period

### Structure
**Unbalanced panel**: Census tract $i$ × ACS period $t$

| Dimension | Definition | Notes |
|-----------|-----------|-------|
| **Units** | Census tracts, Census 2010 definition | ~70,000 tracts lower-48 US; after MOE screening & pop ≥500: ~40,000–50,000 tracts |
| **Time periods** | ACS 5-year estimates ONLY | 2012 (baseline, 2008–2012 window), 2017 (2013–2017), 2022 (2018–2022) |
| **Treatment cohorts** | Staggered | g=2017 (first fire 2013–2016), g=2022 (first fire 2017–2021), g=0 (never-treated) |
| **N observations** | ~120,000–150,000 | 40k–50k tracts × 3 periods (accounting for missing data) |
| **Control group** | Never-treated, smoke-excluded | Tracts with no MTBS fires 2013–2021, outside 100 km buffer |

**CRITICAL TEMPORAL LIMITATION — Disclose in paper:**
With only three ACS periods, each cohort has at most **one pre-treatment observation** (h=−1) and **one or two post-treatment observations** (h=0, h=+1). This severely constrains pre-trend testing:

| Cohort | Pre-treatment period | Post-treatment periods | Event-study h values |
|--------|---------------------|----------------------|----------------------|
| g=2017 (fire 2013–2016) | 2012 ACS (h=−1) | 2017 ACS (h=0), 2022 ACS (h=+1) | h ∈ {−1, 0, +1} |
| g=2022 (fire 2017–2021) | 2017 ACS (h=−1) | 2022 ACS (h=0) | h ∈ {−1, 0} |

With a single pre-period, the event-study pre-trend coefficient $\beta_{h=-1}$ is **normalized to zero by construction** (C&S uses h=−1 as the reference period). Effectively there are **zero degrees of freedom for pre-trend testing**. Parallel trends credibility must rest entirely on (a) the WFP raster matching argument and (b) the falsification/placebo tests described in §5. This must be disclosed prominently in the paper's Empirical Strategy and Limitations sections.

**ACS window contamination for g=2022 (Critical):**
The 2017 ACS (window 2013–2017) is used as the **pre-treatment baseline** for g=2022 tracts. However, the g=2022 treatment window begins in 2017 — meaning fires occurring in 2017 are captured partly within the 2017 ACS averaging window. For tracts with fires in 2017, the "pre-treatment" 2017 ACS already includes the fire year. **Recommended resolution**: Restrict g=2022 inference to tracts with first fire in 2018–2021 (not 2017), making the 2017 ACS a genuinely pre-treatment period. Report g=2017 as the primary cohort; treat g=2022 as secondary/robustness.

### Data Quality Screen (Rural Focus)
- **ACS 5-year estimates only**: Restrict to 2012, 2017, 2022 (no 3-year or 1-year estimates; unreliable for rural tracts where fires concentrate)
- **MOE threshold**: Drop tracts if poverty-rate MOE > 30% of point estimate
- **Population minimum**: Drop tracts if population < 500
- **Report by urbanicity**: Document MOE distribution and sample counts separately for rural (RUCC 4–9) and urban/suburban (RUCC 1–3) tracts

---

## 2. Wildfire Exposure Measures

### Primary Measure: Burned Share (Continuous; Preferred)

**REVISED from prior design**: The prior design treated any tract-fire overlap as "treated." This is too blunt — a tract 99% outside the fire perimeter would count as treated. The **burned share** (% of tract area within MTBS fire polygon) is preferred as the primary exposure measure because it is continuous, proportional to exposure, and free from the threshold-choice problem.

**Burned share definition**:
- $\text{BurnedShare}_i$ = area of intersection(tract $i$, MTBS fire polygon) / area(tract $i$) × 100
- Range: 0–100% (values > 100% truncated; can occur if fire spans tract)
- **Minimum threshold for binary indicator**: Tracts with BurnedShare ≥ 10% classified as "treated" in binary specification (threshold choice is a registered decision; robustness at 5%, 25%)
- **Rationale**: 10% threshold avoids classifying tracts that were barely grazed by a fire perimeter as treated; 5% and 25% in robustness

### Extensive Margin (Binary Treatment — Secondary)
**Derived from burned share**:
- **Treatment**: Tract = 1 if BurnedShare ≥ 10%, 0 otherwise
- **Timing**: First qualifying fire in 2013–2021 defines treatment cohort
- **Spatial definition**: Minimum 10% of tract area burned (NOT any-overlap)
- **Robustness**: Vary minimum threshold (5%, 10%, 25%)

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

**Why WFP enables this assumption (key identification argument)**:
WFP 2012 is the USFS's best pre-treatment measure of a tract's structural fire risk — terrain, vegetation, fuel loads, and climate conditions finalized before 2013. Conditional on WFP hazard class and pre-2013 fire history, the timing of when a tract first experienced a large fire after 2013 is plausibly driven by idiosyncratic ignition events (lightning, human accident) rather than trending economic characteristics. This is the heart of the identification argument: **WFP controls for structural fire vulnerability; residual variation in fire timing is quasi-random**.

This argument does NOT hold unconditionally — high-WFP counties are systematically poorer, more rural, and more economically vulnerable than low-WFP counties. The matching strategy conditions on WFP and baseline economic characteristics precisely because of this correlation.

**Limitation to state clearly**: The study has only one pre-treatment ACS period per cohort (2012 for g=2017; 2017 for g=2022). The standard h=−1 reference normalization leaves **zero pre-trend coefficients to inspect**. Parallel trends cannot be empirically tested via event-study pre-trends in the usual sense. The assumption must instead be defended argumentatively via WFP matching and through the falsification tests below.

### Threats & Tests

| Threat | Test | Expected Result | Interpretation | Priority |
|--------|------|-------|------------|------|
| **Differential pre-trends** | With only 1 pre-period per cohort, cannot run a standard multi-period pre-trend test. Instead: (a) Compare baseline covariate balance after PS-IPW; (b) Run falsification placebo below | See falsification test | The WFP matching argument must substitute for direct pre-trend evidence | **Critical — disclose in paper** |
| **Anticipatory behavior** | Lead specification: regress 2012 outcome on 2017 fire indicator (for g=2017 tracts) | Near-zero coefficient on lead | If near-zero, residents did not preemptively adjust in advance of fire | High |
| **Placebo/falsification** | Assign fires to pre-2013 dates; estimate ATT on pre-2013 ACS outcomes | ATT ≈ 0 | If placebo ATT near zero, pre-existing trend differences unlikely to drive results | High |
| **ACS window contamination (g=2022)** | Restrict g=2022 cohort to tracts with first fire 2018–2021 only; compare ATT to full g=2022 | ATT similar in restricted sample | If similar, 2017 window contamination not driving g=2022 estimates | **Critical for g=2022** |
| **Alternative exposure measure** | Replace binary with burned share (%) and log acres burned | Results scale proportionally | Dose-response consistency strengthens causal claim | High |
| **Burn threshold sensitivity** | Vary minimum burned share: 5%, 10% (baseline), 25% | ATT stable across thresholds | If sensitive, treatment classification drives results | Medium |
| **Alternative control group** | Exclude never-treated with any pre-2013 fire history | ATT similar magnitude | Stricter control group tests if prior fire exposure confounds | High |
| **Smoke spillover** | Vary 100 km buffer (50, 150 km exclusion radii) | ATT stable across radii | If sensitive to buffer, smoke spillover via economic channels threatens identification | High |
| **Migration/compositional change** | Descriptive decomposition via ATT on migration + sequential regression | Decompose total ATT | Separates income effects from compositional effects; note this is not causal mediation | Medium |
| **Sample selection** | Vary MOE threshold (20%, 30%, 40%) by urbanicity | ATT stable in rural and urban subsamples | If sharp rural-urban divergence, rural MOE measurement error may bias estimates | Medium |
| **Regional confounds** | Add state × period FE; then census-division × period FE | ATT similar to baseline | If regional controls substantially change results, regional shocks confound | High |
| **Spatial autocorrelation** | Cluster SE at county level; report Moran's I of residuals | Moran's I ≈ 0 after clustering | If still autocorrelated, consider spatial HAC or multi-way clustering | Medium |

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

### Solution: Descriptive Decomposition Framework (Not Causal Mediation)

**Critical methodological note**: This is a **descriptive decomposition**, not causal mediation. The sequential regression approach (Baron-Kenny) can recover causal mediation only if the migration-to-poverty path is free of unmeasured confounders. There are plausible confounders (e.g., regional economic shocks that simultaneously drive migration and poverty independently of the fire). We therefore label this a decomposition and interpret the indirect effect as an upper bound on compositional change, not a causal estimate.

#### Step 1: Estimate Total Effect
$$\text{Poverty}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{pov}} \cdot \mathbb{1}[g_i = t-h] + X \gamma + \epsilon$$
- Estimand: $\text{ATT}^{\text{pov}}$ (total reduced-form effect on tract poverty rate)

#### Step 2: Estimate Effect on Migration
$$\text{Net-Migration}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{mig}} \cdot \mathbb{1}[g_i = t-h] + X \gamma + \epsilon$$
- Estimand: $\text{ATT}^{\text{mig}}$ (effect on 5-year net-migration rate)

#### Step 3: Partial-Out Migration from Poverty
$$\text{Poverty}_{i,t} = \alpha_i + \lambda_t + \sum_{h} \beta_h^{\text{pov,cond}} \cdot \mathbb{1}[g_i = t-h] + \gamma \cdot \text{Net-Migration}_{i,t} + X \gamma' + \epsilon$$
- Estimand: $\gamma$ (association of migration with poverty, conditional on fire treatment; **not causal path coefficient**)

#### Step 4: Accounting Decomposition
- **Migration-associated component**: $\text{ATT}^{\text{mig}} \times \gamma$ (fraction of poverty change associated with migration)
- **Residual component**: $\text{ATT}^{\text{pov}} - \text{ATT}^{\text{mig}} \times \gamma$ (fraction of poverty change not associated with migration)

#### Interpretation (with caveats)
- **Large migration-associated component**: Consistent with out-migration as a compositional driver of tract poverty change; interpret cautiously as possible upper bound
- **Large residual component**: Consistent with income effects on stayers; also possible that measured migration is an imperfect mediator

**Data quality caveat**: ACS 5-year "residence 5 years ago" is noisy and imprecise for sparse rural tracts. All decomposition results should be labeled exploratory and presented with wide confidence intervals.

---

## 9. Critical Assessment Checkpoint

**Iteration 2 Review — Issues Found and Addressed:**

The following major issues were identified in Iteration 1 and have been corrected in this document:

1. **Pre-trend testing infeasible** *(addressed in §1 and §5)*
   - With only 3 ACS periods, each cohort has exactly one pre-treatment observation (h=−1, normalized to 0 by C&S convention). Standard pre-trend testing cannot be conducted. The parallel trends assumption must rest primarily on the WFP raster matching strategy and placebo falsification. This is now clearly documented as a critical limitation rather than glossed over.

2. **ACS 2017 window contamination for g=2022** *(addressed in §1)*
   - The 2017 ACS (2013–2017 window) overlaps treatment onset for g=2022 tracts with first fires in 2017. Fix: restrict g=2022 to tracts with first qualifying fire 2018–2021. This restriction reduces g=2022 sample size; document explicitly.

3. **Burned share preferred over any-overlap binary** *(addressed in §2)*
   - Binary "any intersection" is too coarse for tracts that are only marginally touched by a fire perimeter. Primary treatment measure revised to burned share (% of tract area within MTBS perimeter), with 10% minimum threshold for the binary indicator. This reduces false positives in the treated group.

4. **Mediation labeled as causal when it is only descriptive** *(addressed in §8)*
   - The sequential regression (Baron-Kenny) approach cannot recover causal mediation without a no-unmeasured-confounding assumption on the migration-to-poverty path. This assumption is not credibly satisfied. All mediation results are now labeled "descriptive decomposition" and interpreted as upper bounds, not causal path estimates.

**Remaining open design questions (not yet resolved; flag in paper limitations):**
- No fine-grained fire severity measure beyond MTBS binary and acres burned
- Cannot distinguish in-migration from out-migration in ACS net-migration proxy
- Long-term persistence (>7 years) is outside the current data window

**Status**: Iteration 2 revisions complete. Proceed to paper_outline.md revision.

