# Research Goal: Wildfire Impact on Poverty in US Census Tracts

**Last Updated**: 2026-08-02 (Updated to 6 ACS periods for robust pre-trend testing and long-run effects)  
**Status**: Design phase (tract-level + raster-based matching + trajectory estimation)

---

## Research Questions

### Primary Question
**Do large wildfires (≥1,000 acres) causally increase poverty rates in affected US census tracts, and how large are these effects in the medium run (3–5 years post-fire)?**

*Note*: This question focuses on a single estimand — the average treatment effect on the treated (ATT) for the poverty rate — against a matched control group of never-burned tracts. This is the registerable, PAP-able primary claim.

### Secondary Questions
1. **What share of the tract-level poverty effect is attributable to resident income losses vs. the selective departure of lower-income households?** (Mechanism decomposition)
2. **Do wildfire effects on poverty vary systematically by fire severity, baseline tract poverty, rurality, race/ethnicity composition, or housing tenure?** (Heterogeneous effects)
3. **Are wildfire poverty effects persistent at 3–7 years post-fire, or do they fade as labor markets and housing recover?** (Duration & trajectory)

*Design note*: Secondary question 3 is now well-addressed — with three post-treatment ACS periods (2022, 2023, 2024), the study traces a fine-grained recovery trajectory over 3–7 years post-fire, showing whether effects fade, persist, or amplify.

---

## Policy Relevance & Contribution

### Policy Relevance
Wildfires are increasing in frequency and severity across the US, affecting vulnerable populations concentrated in rural regions. Yet empirical evidence on **causal poverty impacts** remains limited—most prior work examines health outcomes or property damage, not distributional economic effects. Understanding wildfire impacts on poverty is critical for:

- **Disaster relief design**: Should relief target income replacement (for stayers) or relocation assistance (for migrants)?
- **Climate adaptation**: Are fire-prone regions experiencing permanent economic decline, or do adaptive migrations stabilize poverty?
- **Vulnerability assessments**: Which populations (poor, rural, renters) face greater poverty risk from fires?

### Scholarly Contributions

#### Applied Economics & Environmental Economics
- **First tract-level national study** of wildfire impacts on poverty (prior work: county-level or Western-only; no national tract analysis exists)
- **WFP raster as identification vehicle**: WFP 2012 (270m resolution, predetermined before the 2013 treatment window) is used not merely as a matching covariate but as the key variable enabling the **conditional parallel trends assumption** — tracts with similar WFP values and baseline characteristics would, absent fire, have followed the same poverty trajectory. This is the core causal identification argument, distinct from its use as a propensity-score regressor.
- **Poverty as primary outcome**: Prior disaster economics focuses on property values, wages, or mortality; distributional poverty outcomes remain unstudied at this scale

#### Disaster & Regional Science
- **Staggered treatment design** (Callaway & Sant'Anna 2021) avoids forbidden comparisons between already-treated and not-yet-treated units; appropriate when treatment cohort timing is itself endogenous to local conditions
- **Rural data validation**: Demonstrates use of ACS 5-year estimates for sparse rural populations (where fires concentrate); explicitly benchmarks ACS MOE by urbanicity
- **Within-county heterogeneity**: Shows why county-level analyses mask exposure and outcome variation; tracts within the same county can have dramatically different fire exposure and poverty trajectories

#### Poverty & Inequality Literature
- **Headcount poverty focus**: Distinguishes poverty rate change from mean income change — relevant because selective out-migration can lower a tract's poverty rate even while reducing resident welfare
- **Distributional decomposition**: Distinguishes resident-level poverty change (income effect) from tract-level poverty change from selective migration (compositional effect) — a conceptual contribution to the disaster displacement literature

---

## Time Horizons: Short-Run, Medium-Run, Long-Run

The study examines **medium- to long-run effects** (1–7 years post-fire) with robust pre-trend testing:

| Horizon | Definition | Measurement in This Study | Expected Dynamics |
|---------|-----------|-----------|-----------|
| **Short-run** (0–2 yr) | Immediate post-fire shock | **Not captured.** ACS estimates have 5-year measurement windows; earliest post-fire ACS (2022) starts 3 years after first 2015 fires. | Acute job loss, housing destruction, temporary displacement; disaster assistance peaks |
| **Medium-run** (1–6 yr) | Primary analysis window | **Captured via h=0 (1–4 yrs) and h=+1 (2–6 yrs).** ACS 2022 and 2023 give overlapping snapshots of medium-run effects. | Job recovery vs. permanent restructuring; migration stabilization; housing market adjustment |
| **Long-run** (3–7 yr) | Persistence & trajectory | **Now captured via h=+2 (3–7 yrs).** ACS 2024 enables trajectory estimation — fadeout, persistence, or amplification. | Persistence of poverty effects; recovery trajectories; compositional shifts |
| **Very long-run** (7+ yr) | Permanent effects | **Not captured.** Would require post-2024 ACS. Suggest as future extension. | Regional economic reorientation; repeated-fire compounding; intergenerational poverty transmission |

**Key strength (updated 2026-08-02)**: ACS 5-year estimates now provide six snapshots (2009, 2012, 2014, 2022, 2023, 2024), yielding **three pre-treatment periods** and **three post-treatment periods**. This enables:
- **Robust parallel trends testing**: β₋₃ and β₋₂ provide two independent pre-trend tests; can formally test H₀: β₋₃ = β₋₂ = 0
- **Trajectory estimation**: β₀, β₊₁, β₊₂ trace poverty dynamics over 1–7 years post-fire
- **Much stronger identification** than the prior two-period design

---

## Mechanisms

The study examines poverty changes through the following causal pathways:

### Primary Mechanisms
1. **Employment & income losses** (direct income effect)
   - Fire destroys jobs in burned areas (property damage, business disruption)
   - Displacement of workers into lower-paying sectors
   - Temporary job loss → temporary income loss → temporary poverty entry

2. **Housing market disruption** (asset loss)
   - Property destruction reduces homeowner wealth; some losses uninsured
   - Housing cost inflation in post-fire housing shortage
   - Renters displaced; may relocate to higher-cost housing

3. **Selective migration / population displacement** (compositional effect)
   - Out-migration concentrated among lower-income, younger, less-rooted households
   - In-migration of disaster workers (temporary), insurance adjusters, contractors
   - Net effect on tract poverty rate depends on relative incomes of migrants vs. stayers

4. **Business disruption**
   - Supply-chain disruption, temporary business closures
   - Loss of self-employment / small-business income

### Secondary Mechanisms
5. **Disaster assistance offset** (mitigation)
   - FEMA relief, SBA loans, insurance payouts reduce net income loss
   - Incomplete coverage of losses (insurance gaps, means-testing)

6. **Adaptive capacity heterogeneity**
   - High-income households: greater insurance, savings, credit access → faster recovery
   - Low-income households: incomplete insurance, limited savings → slower recovery, higher poverty risk

### Measurement Strategy & Directly Observable Mechanisms

The study can directly measure reduced-form effects on income and employment; structural mechanisms are inferred, not identified.

| Mechanism | Direct Measure | Feasibility |
|-----------|---------------|-------------|
| Employment & income loss | ATT on median HH income, employment rate | Measurable (ACS 5-yr) |
| Selective migration | ATT on net-migration rate (5-yr ACS) | Measurable; noisy proxy |
| Housing disruption | Tract-level rent/home-value change | **TBD** — ACS median home value available but high MOE |
| Business disruption | Sector employment share change | Approximate (ACS sector employment) |
| Disaster assistance | FEMA IA/PA amounts by tract | **Not available** at tract level; county-level only |
| Adaptive capacity | Heterogeneity by income/tenure/race | Descriptive via subgroup ATT |

**Mediation framework** (descriptive decomposition, not causal mediation):
- Total ATT(poverty) = Direct effect (income loss channel) + Indirect effect (migration channel)
- Indirect = ATT(migration) × regression coefficient(migration → poverty)
- **Important caveat**: This decomposition requires no unmeasured confounding of the migration-to-poverty path. Without that assumption, the indirect effect is a descriptive correlation, not a causal pathway. Results are labeled "decomposition" not "causal mediation."

---

## Population, Geography, Study Period, Unit of Analysis

### Intended Population
- **Census tracts** (Census 2010 definition) in all lower-48 US states
- Focus on tracts affected by large fires (MTBS ≥1,000 acres)
- Expected ~800–1,200 treated tracts (g=2017, g=2022 cohorts) and ~40,000–50,000 never-treated comparison tracts after data screening

### Geographic Coverage
- **All lower-48 US states** (~70,000 census tracts)
- **Fire exposure** varies geographically (Western & interior states >concentrated fire activity; Eastern/coastal states <rare large fires)
- **Smoke spillover exclusion** removes comparison tracts within 100 km of fire perimeters (baseline); varies in robustness (50, 150 km)

### Study Period
- **Pre-treatment baseline**: 2012 ACS (2008–2012 window)
- **Treatment window**: 2013–2021 (MTBS fires ≥1,000 acres)
  - Cohort 1 (g=2017): First qualifying fire 2013–2016 (n≈600–800 tracts)
  - Cohort 2 (g=2022): First qualifying fire 2017–2021 (n≈200–400 tracts)
- **Post-treatment measurement**: 2017 ACS (2013–2017), 2022 ACS (2018–2022)

### Unit of Analysis
- **Census tract** (Census 2010; ~3,000–8,000 persons per tract on average; rural tracts ~100–500 persons)
- Tract-level analysis captures within-county heterogeneity in fire exposure, baseline poverty, and economic recovery

### Wildfire Exposure Definition

**Extensive margin (binary treatment)**:
- Tract = 1 if tract intersects MTBS fire polygon (≥1,000 acres) in treatment window
- Extensive measure: Any large fire vs. no fire

**Intensive margin (dose-response)**:
- Fire count: 1, 2, 3+ large fires in treatment window per tract
- Fire intensity: % of tract area burned (computed from tract-fire spatial intersection)
- Hazard intensity: Mean USFS WFP 2012 percentile (0–100) across 270m pixels in tract (predetermined, 270m resolution)

**Distance-based measure** (robustness):
- Distance from tract boundary to nearest fire perimeter
- Tests whether effects attenuate with distance (smoketransport / commuting impacts)

### Poverty Outcomes

**Primary outcome**:
- **Poverty rate**: % of tract population below federal poverty line (Census definition; varies by family size/composition)

**Secondary outcomes**:
- **Median household income**: Dollar value (nominal; adjusted to 2020 dollars for comparison)
- **Employment rate**: % of civilian labor force employed
- **Number of persons in poverty** (absolute count; flags tracts experiencing out-migration)

**Subgroup outcomes** (if data permit):
- **Child poverty rate**: % of persons under age 18 in poverty (ACS available at tract level)
- **Deep poverty rate**: % of population below 50% of poverty line (ACS available)
- **Poverty by age, race/ethnicity, citizenship status** (if IPUMS extract sufficient sample size)

**Mechanism/mediator outcome**:
- **Net-migration rate**: % of tract population that moved in during past 5 years minus % that moved out (ACS "residence 5 years ago")

---

## 150–250 Word Objective & Contribution Statement

Wildfire frequency and severity in the United States have increased sharply over recent decades, yet causal evidence on economic impacts for vulnerable populations remains scarce. This paper estimates the effect of large wildfires on poverty rates in US census tracts, using staggered difference-in-differences (Callaway & Sant'Anna 2021) applied to ~45,000 tracts across all lower-48 states, observed at three ACS five-year periods (2012, 2017, 2022). We exploit staggered variation in the timing of first large-fire exposure (MTBS ≥1,000 acres, 2013–2021) and match treated to never-burned tracts on predetermined wildfire hazard potential (USFS WFP 2012) measured at native 270-meter raster resolution. WFP is predetermined relative to the treatment window and serves as the primary basis for the conditional parallel trends assumption: conditional on tract-level WFP hazard, pre-fire poverty history, and baseline demographics, fire incidence is plausibly unconfounded. We decompose the total poverty effect into a direct channel — resident income and employment losses — and an indirect channel — selective out-migration changing tract composition — using a descriptive mediation framework. The study advances three fronts: it is the first national, tract-level quasi-experimental analysis of wildfire poverty impacts; it demonstrates the value of raster-based spatial matching for improving precision in natural disaster DiD designs; and it clarifies whether observed poverty changes reflect genuine welfare losses or demographic sorting, a distinction with direct implications for disaster relief design. (235 words)

---

## Data Availability & Known Limitations

### Verified Data Availability
- **MTBS (Monitoring Trends in Burn Severity)**: Fire perimeters 1984–2022, nationwide, ≥1,000 acres threshold. Reuse from `wildfire-finance` project.
- **USFS WFP 2012**: Wildfire Hazard Potential (270m raster, ESRI Grid, EPSG:5070). Predetermined before 2013 treatment window. Reuse from `wildfire-finance`.
- **ACS 5-year estimates**: Poverty, income, employment, net migration at tract level. IPUMS extraction required for 2012, 2017, 2022.
- **Census tracts & RUCC**: TIGER shapefiles (Census 2010) and USDA Rural-Urban Continuum Codes (2013).
- **BEA per-capita income** (annual): County-level, via FRED API (robustness cross-check).

### Unresolved Data Decisions
1. **ACS 2022 availability**: 2018–2022 ACS released late 2023; confirm data quality and differential privacy impact vs. 2017 estimate
2. **Tract-level fire severity**: MTBS provides burn severity classification; availability of high-resolution fire severity data (e.g., RAVG severity index) for dose-response analysis TBD
3. **Housing outcomes**: ACS does not provide tract-level rent/home-value data directly; future work could incorporate ACS median home value or use external housing indices
4. **Disaster assistance**: No readily available tract-level FEMA assistance data; county-level SBA loans available but may not correlate with tract-level impacts

---

## References for Literature Search

The study situates findings in the following research areas. A full bibliography will be populated via `/deep-research` lit-review.

**Target literature areas**:
- Wildfire economics & environmental disasters (Boomhower 2019; Borgschulte et al. 2024; climate/fire literature)
- Poverty & income dynamics (Autor, Moretti, Kline; regional economic adjustment literature)
- Disaster displacement & migration (Blanchard-Katz regional evolution; climate migration)
- Causal inference methods (Callaway & Sant'Anna 2021; staggered DiD; raster-based spatial matching)
- ACS data methods (Census disclosure avoidance; rural estimation; 5-year vs. 3-year estimates)

*Full citations and annotations to be added after systematic lit review.*

