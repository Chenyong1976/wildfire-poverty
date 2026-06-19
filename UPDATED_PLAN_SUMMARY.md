# Research Plan Update Summary
**Date**: 2026-06-18  
**Version**: 2.0 (Expanded to lower-48; Mechanism + Regression Adjustment)

---

## Major Changes Implemented

### 1. Geographic Scope: Western US → All Lower-48 States
- **Previous**: 13 Western states (CA, OR, WA, ID, MT, WY, NV, UT, CO, NM, AZ, AK, HI)
- **Updated**: All lower-48 US states (~3,100 counties vs. ~500 previously)
- **Rationale**: Wildfire exposure now varies nationally; broader generalizability; expanded control pool for better common support in PS-IPW matching

### 2. Study Period: 2000–2020 → 2007–2022 (Treatment 2013–2021)
- **Previous**: Analysis period 2000–2020; treatment timing flexible
- **Updated**: Analysis period 2007, 2012, 2017, 2022 (4 ACS 5-year estimate periods); treatment window 2013–2021
- **Rationale**: Matches wildfire-finance project timeline (same cohort structure: g=2017, g=2022); aligns with WFP 2012 predetermined matching variable; reduces treatment-outcome overlap bias

### 3. Treatment Definition: Flexible → Replicates Wildfire-Finance Design
- **Previous**: First fire ≥1,000 acres anytime 2000–2020; spatial overlap rule vague
- **Updated**: 
  - First qualifying fire (MTBS ≥1,000 acres) in **2013–2021 only**
  - Two cohorts: g=2017 (fires 2013–2016), g=2022 (fires 2017–2021)
  - Extensive margin: any fire ≥1,000 acres (binary)
  - Intensive margin: fire count and total acres burned (dose-response)
  - Never-treated: no fires 2013–2021 (nationwide pool now much larger)
- **Rationale**: Replicates wildfire-finance for consistency; avoids pre-2013 fire confounds; enables straightforward cohort comparison

### 4. Matching Strategy: Manual → Propensity-Score IPW (WFP 2012)
- **Previous**: WHP matching + covariate balance; unspecified algorithm
- **Updated**: 
  - **Primary**: WFP 2012 quintile (predetermined, finalized before 2013 fire season)
  - **Model**: Logistic PS on WFP quintile, pre-2013 fire history, baseline covariates (2012 ACS: poverty, income, density; RUCC; population)
  - **Weights**: Inverse-probability weights (treated w=1, control w=ê/(1−ê)), trimmed at 99th percentile
  - **Regression adjustment**: Include WFP quintile + baseline covariates as additional covariates in C&S estimation
  - **Diagnostics**: Report SMD before/after (target <0.1), ESS of reweighted control group
- **Rationale**: Matches wildfire-finance methodology; transparent, reproducible; handles selection on observables; accommodates national expansion's thin common support concern

### 5. Mechanism Analysis: Not in Original Plan → New Mediator (Net Migration)
- **New section (§4.2 in RESEARCH_PLAN.md)**: Mediation analysis on net-migration rate
- **Variables**:
  - **Mediator**: Net-migration rate (ACS 5-year residence change: % moved in – % moved out)
  - **Direct effect**: ATT on poverty rate (main model)
  - **Indirect effect**: Treatment → migration → poverty
  - **Decomposition**: Income loss mechanism vs. compositional/displacement mechanism
- **Interpretation pathway**:
  - Large positive net-migration ATT → out-migration mediates poverty increase → compositional effect
  - Small net-migration ATT → income effects dominate → welfare loss mechanism
- **Rationale**: Addresses feedback from initial assessment (§1 criticism): clarifies whether effects reflect income losses or population sorting

### 6. Outcome Window: Fixed 5-Year Post-Fire → Extended to 7 Years
- **Previous**: Event-study $h \in \{-5, \ldots, 5\}$ relative years
- **Updated**: Event-study $h \in \{-3, \ldots, 7\}$ (captures longer-term adjustment; acknowledges limited follow-up for g=2022 cohort)
- **Rationale**: Better captures dynamic adjustment; g=2022 cohort only has 1 post-treatment observation (2022), limiting power; pre-trends window reduced to 3 years (sufficient for falsification)

### 7. Pre-Trend Testing: Significance Test → Magnitude & Visual Inspection
- **Previous**: Roth (2022) critique mentioned; unclear implementation
- **Updated**: 
  - **Do NOT report p-values** for pre-trend null tests
  - **Report $\beta_h$ (h<0) with 95% CIs** and visually assess magnitude relative to post-treatment effects
  - **Parallel trends framing**: If pre-trends small and slopes non-divergent, supports conditional parallel trends
  - **Falsification test**: Assign fires to pre-2013 years; expect ATT ≈ 0
- **Rationale**: Avoids Roth's critique; more transparent than null tests; visual inspection more credible

### 8. Robustness Tests: 7 Tests → 6+ Tests Organized by Threat
- **Updated organization** (RESEARCH_PLAN.md §4.4):
  - Threat-based, not test-type-based
  - Smoke spillover (3 radii: 50, 100, 150 km)
  - Fire threshold (500, 1,000, 2,000 acres)
  - Placebo (pre-2013 fires → ATT ≈ 0)
  - Event-study window variants
  - Regional FE variations (state × period vs. division × period)
  - Estimator checks (Sun-Abraham, Two-Stage DiD)
- **Rationale**: Clearer threat mapping; each robustness test targets specific ID assumption

### 9. Pre-Analysis Plan: Optional → Mandatory
- **Updated**: Move from §7 ("Optional but Recommended") to §6 and explicitly label Mandatory
- **Spec freeze includes**:
  - Sample frame (lower-48, 2007–2022)
  - Treatment definition (extensive + intensive margins)
  - Primary outcomes (poverty, income, net migration, employment)
  - Primary estimator (C&S)
  - Event-study window ($h \in \{-3, \ldots, 7\}$)
  - Matching spec (PS-IPW on WFP 2012)
- **Deviation protocol**: Clearly document any post-hoc changes; flag as deviations in paper appendix
- **Rationale**: Signals scientific rigor; reduces p-hacking concerns; strengthens credibility in competitive journals

### 10. Sample Restrictions: Clarified & Tightened
- **Previous**: Never-treated vs. already-treated classification loose
- **Updated**:
  - **Never-treated**: No fires 2013–2021 AND outside 100 km smoke buffer
  - **Excluded**: Pre-2013 fires (clouds pre-treatment baseline); pop < 1,000 (unreliable ACS)
  - **Smoke buffer**: Default 100 km (baseline); robustness 50, 150 km
- **Rationale**: Avoids pre-treatment confounds; cleans control group; transparent exclusion criteria

---

## Updated Outcomes (Primary Order)

1. **Poverty rate** (primary) — % below federal poverty line
2. **Median household income** — nominal 2019$
3. **Net-migration rate** (mediator) — % moved in − % moved out (past 5 yrs)
4. **Employment rate** — % labor force employed

---

## Updated Writing Plan (7 Sections)

| Section | Pages | Key Elements |
|---------|-------|--------------|
| Introduction | 2–3 | Hook (wildfire ↑), gap, RQ, contribution (national + migration), lit (4–5) |
| Data & Sample | 1–2 | Sample frame, treatment defn, outcomes, Tables 1a–1b (balance pre/post-IPW), Figure 1 (map) |
| Empirical Strategy | 2–2.5 | ID variation, estimand (ATT), equations, threats + mitigations |
| Results | 3–4 | Figure 2 (event-study), Table 2 (ATT), Table 3 (extensive/intensive), mediation results |
| Robustness | 2–2.5 | Organized by threat; Table 4 (6+ specs) |
| Discussion | 1.5–2 | Mechanism interpretation, scope, open questions |
| Conclusion | 0.5 | Restate finding, hedged policy implication |

---

## Timeline: No Change from Original
- **Weeks 1–3**: Data assembly
- **Week 4**: Matching & balance
- **Weeks 5–7**: Estimation, robustness, heterogeneity
- **Week 8**: Output (tables, figures)
- **Weeks 9+**: Writing, review, submission

---

## Key Architectural Decisions

1. **Use R for DiD estimation** (`did` package, C&S via `att_gt()`)
2. **Python for data assembly** (pandas, geopandas for spatial ops)
3. **Matching in R** (`logistf` or base `glm` for PS; compute weights)
4. **Reuse wildfire-finance data** (MTBS, WFP 2012 rasters, smoke-buffer logic)
5. **National sample alignment** but retain Western-8 subsample for robustness check

---

## Critical Path to Start

**Week 0 (before analysis)**:
- [ ] Sign off on this updated plan with collaborators
- [ ] Register PAP on OSF (lock specifications)
- [ ] Run `/deep-research` to populate literature section

**Week 1–3**:
- [ ] Assemble ACS 5-year estimates (2007–2022)
- [ ] Verify MTBS and WFP 2012 rasters available; reuse from wildfire-finance if possible
- [ ] Implement `code/01_build/` pipeline; generate final balanced panel
- [ ] Document sample restrictions and cohort counts

---

## Not Changed (Inherited from Original Plan)

- Target journals (JUE, RSUE, AEJ:Applied)
- Staggered DiD as primary estimator
- ACS and MTBS as primary data sources
- Poverty rate as primary outcome
- Publication-ready output standards (300 DPI, LaTeX)

---

**Status**: Ready for execution pending collaborator approval and PAP registration.
