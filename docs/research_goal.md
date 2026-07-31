# Research Goal: Wildfire Impact on Poverty in US Census Tracts

**Last Updated**: 2026-07-30  
**Status**: Design phase (tract-level + raster-based matching)

---

## Research Questions

### Primary Question
**How do large wildfires causally affect poverty rates and household incomes in affected US census tracts, and what role does population displacement via out-migration play in mediating these effects?**

### Secondary Questions
1. **Do wildfire effects on poverty vary by fire intensity, tract baseline poverty, urbanicity, or geographic region?** (Heterogeneous effects)
2. **Can tract-level poverty changes be decomposed into income losses (welfare effects) vs. population compositional changes (migration effects)?** (Mechanism)
3. **How persistent are wildfire effects on poverty: do they fade over 3–5 years post-fire, or compound with repeated exposure?** (Duration)

---

## Policy Relevance & Contribution

### Policy Relevance
Wildfires are increasing in frequency and severity across the US, affecting vulnerable populations concentrated in rural regions. Yet empirical evidence on **causal poverty impacts** remains limited—most prior work examines health outcomes or property damage, not distributional economic effects. Understanding wildfire impacts on poverty is critical for:

- **Disaster relief design**: Should relief target income replacement (for stayers) or relocation assistance (for migrants)?
- **Climate adaptation**: Are fire-prone regions experiencing permanent economic decline, or do adaptive migrations stabilize poverty?
- **Vulnerability assessments**: Which populations (poor, rural, renters) face greater poverty risk from fires?

### Scholarly Contributions

#### Applied Economics & Environmental Economics
- **First tract-level national study** of wildfire impacts on poverty (prior: county-level or Western-only)
- **Fine-grained spatial matching** using 270m wildfire hazard potential raster (USFS WFP 2012), improving causal precision vs. county-level matching
- **Explicit mediation analysis** decomposing poverty effects into income losses vs. migration-driven compositional changes

#### Disaster & Regional Science
- **Staggered treatment design** (Callaway & Sant'Anna 2021) avoids using already-treated units as controls; appropriate for multi-year disaster context
- **Rural data validation**: Demonstrates use of ACS 5-year estimates for sparse rural populations (where fires concentrate), addressing measurement challenges in disaster research
- **Within-county heterogeneity**: Documents how fire exposure varies at tract level within counties, explaining why county aggregates mask important economic variation

#### Poverty & Inequality Literature
- **Distributional focus** on poverty rates (not just mean income), directly addressing whether fires increase poverty headcount or just reduce mean incomes
- **Compositional effects**: Distinguishes resident-level poverty changes from tract-level poverty changes caused by selective migration—critical for understanding whether poverty "improvement" reflects genuine welfare gains or demographic sorting

---

## Time Horizons: Short-Run, Medium-Run, Long-Run

The study examines **medium-run effects** (3–5 years post-fire) with implications for understanding longer-term dynamics:

| Horizon | Definition | Measurement | Expected Dynamics |
|---------|-----------|-----------|-----------|
| **Short-run** (0–1 yr) | Immediate post-fire shock | Not directly measured; inferred from t=0 baseline | Acute job loss, housing destruction, temporary displacement |
| **Medium-run** (3–5 yr) | Primary analysis window | ATT from event-study $\beta_h$ (post-fire ACS periods 2017, 2022) | Job recovery vs. permanent restructuring; migration stabilization; second-order effects on housing/services |
| **Long-run** (5–10+ yr) | Persistence & permanent effects | Cannot assess with current data; future work as post-2025 ACS released | Regional economic reorientation; cumulative effects of repeated fires; intergenerational impacts |

**Data limitation**: ACS 5-year estimates provide 2012, 2017, 2022 snapshots. Pre-treatment baseline (2012 ACS, window 2008–2012) ends ~4–6 years before fires (2013–2016 g=2017 cohort). Post-treatment measures (2017 ACS) capture ~1–4 years post-fire. Trade-off: 5-year estimates are only reliable source for rural tracts (where fires concentrate), but temporal resolution is coarse.

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

### Measurement Strategy
- **Direct effect** (income loss): ATT on median household income, employment rate
- **Indirect effect** (migration): ATT on net-migration rate (mediator) × coefficient of migration on poverty
- **Decomposition**: Direct effect = Total ATT(poverty) − Indirect effect
- **Interpretation**: If indirect effect large, compositional change dominates; if small, income effects dominate

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

### Objective
This study estimates the causal effects of large wildfires on poverty in US census tracts using staggered difference-in-differences estimation with fine-grained spatial matching. Using data from 2012–2022 and census tracts across all lower-48 states, we leverage variation in the timing of first large fire exposure (MTBS ≥1,000 acres) and tract-level wildfire hazard potential (USFS WFP 2012 at 270m resolution) to identify treated and matched control tracts. We estimate poverty rate changes for tracts experiencing large fires in 2013–2021, decomposing effects into income losses (measured directly) and compositional changes (via mediation analysis on net-migration). The design accommodates treatment effect heterogeneity, controls for spatial spillovers (smoke exposure, regional shocks), and accounts for rural data limitations in ACS estimates.

### Contribution
First national, tract-level study of wildfire impacts on poverty. Advances the disaster economics and environmental justice literatures by: (1) documenting distributional effects (poverty rates, not just mean income) across vulnerable populations; (2) distinguishing resident welfare losses from compositional changes via migration; (3) implementing fine-grained raster-based spatial matching (270m WFP) to improve causal precision; (4) validating rural poverty measurement in ACS 5-year estimates. Results inform disaster relief design (income replacement vs. relocation support) and climate adaptation in fire-prone regions.

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

