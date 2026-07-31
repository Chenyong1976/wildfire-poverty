# Paper Outline: Wildfire Impact on Poverty in US Census Tracts

**Target Journals**: *Journal of Urban Economics*, *Regional Science and Urban Economics*, *American Economic Journal: Applied Economics*

**Last Updated**: 2026-07-30

---

## I. Introduction (2–3 pages)

### A. Hook & Motivation
- Rising wildfire frequency and severity in US (trends 1980s–2020s; cite fire data)
- Economic impact on vulnerable populations poorly understood (gap vs. health/property focus)
- County-level prior work masks within-county heterogeneity

### B. Research Question & Contribution Preview
- Primary RQ: How do large wildfires causally affect poverty rates in census tracts?
- Contribution 1: First national, tract-level study of fire-poverty causality
- Contribution 2: Fine-grained spatial matching using 270m WFP raster (improved precision vs. county aggregates)
- Contribution 3: Explicit mediation analysis on migration (welfare loss vs. compositional change)

### C. Identifying Variation
- Staggered fire exposure across ~70,000 lower-48 census tracts (2013–2021)
- Cohorts: g=2017 (fires 2013–2016), g=2022 (fires 2017–2021)
- Spatial matching on predetermined USFS WFP 2012 hazard raster (270m resolution)

### D. Preview of Results
- [To be filled after estimation; sketch: "Exposure to large wildfire increases tract poverty rate by X percentage points in 3–5 years post-fire. Effect partially mediated by out-migration (Z% compositional, 100–Z% income loss)."]

### E. Roadmap
- Data §II, empirical strategy §III, results §IV, mechanisms §V, robustness §VI, limitations & policy §VII

### F. Literature Positioning (Tight, 4–5 papers)
- Wildfire economics: [Boomhower 2019; Borgschulte et al. 2024; climate-disaster literature search targets]
- Poverty & regional adjustment: [Autor; Kline-Moretti; Blanchard-Katz]
- Causal inference: [Callaway & Sant'Anna 2021]
- *(Full references after deep-research lit review)*

---

## II. Data & Sample (2–2.5 pages)

### A. Data Sources

| Dataset | Unit | Coverage | Use |
|---------|------|----------|-----|
| **MTBS** | Fire perimeter | 1984–2022, nationwide, ≥1,000 acres | Treatment assignment; extensive + intensive margins |
| **USFS WFP 2012** | 270m raster, EPSG:5070 | Nationwide, predetermined | Spatial matching; baseline hazard measure |
| **ACS 5-year** | Census tract | 2012, 2017, 2022 (2008–2012, 2013–2017, 2018–2022 windows) | Primary outcomes: poverty rate, income, migration, employment |
| **Census TIGER** | Tract boundary | Census 2010 definition | Geospatial reference |
| **USDA RUCC** | County | 2013 vintage | Rural-urban classification |
| **BEA NIPA** | County, annual | Per capita income | Robustness cross-check |

### B. Sample Definition

#### Geographic Scope
- All lower-48 US states
- ~70,000 census tracts pre-screening
- After MOE (>30% excluded), pop <500 excluded: **~40,000–50,000 tracts**

#### Temporal Scope
- Baseline: 2012 ACS (pre-treatment)
- Treatment window: 2013–2021 (MTBS fires)
- Post-treatment: 2017, 2022 ACS
- Observation: 3 ACS periods × ~45,000 tracts ≈ **135,000 observations**

#### Treatment Definition
- **Extensive**: Tract intersects MTBS fire (≥1,000 acres), 2013–2021
  - g=2017 cohort: first fire 2013–2016 (n ≈ 600–800 tracts)
  - g=2022 cohort: first fire 2017–2021 (n ≈ 200–400 tracts)
- **Never-treated controls**: No fires 2013–2021, outside 100 km smoke buffer (n ≈ 39,000–49,000)

### C. Summary Statistics

**Table 1a: Pre-Treatment Balance (Pre-IPW)**
- Rows: Treated vs. never-treated
- Cols: Poverty rate, HH income, employment, population, WFP percentile, % rural, %nonwhite, %renter
- Note: Show imbalance before matching

**Table 1b: Post-IPW Balance**
- Same rows/cols
- After PS-IPW reweighting
- Target: SMD < 0.10 all covariates
- Report: Effective sample size (ESS) of reweighted controls

**Figure 1: Geographic Coverage**
- Map of lower-48 US showing: fire perimeters (2013–2021), treated tracts, 100 km smoke buffer, never-treated controls
- Color by region; annotate fire density (West > South > Midwest/Northeast)

---

## III. Empirical Strategy (2–2.5 pages)

### A. Identification Strategy & Estimand

**Design**: Staggered difference-in-differences (Callaway & Sant'Anna 2021)

**Estimand**: Average treatment effect on treated (ATT)
- Causal effect of large fire (≥1,000 acres) on poverty rate
- Relative to matched, never-treated comparison tracts
- Conditional on baseline covariates (WFP hazard, demographics)

**Event-study specification**:
$$\text{Poverty}_{i,t} = \alpha_i + \lambda_t + \sum_{h \neq -1} \beta_h \cdot \mathbb{1}[g_i = t - h] + X_{i,2012} \gamma + \epsilon_{i,t}$$

- $\beta_h$ = effect $h$ years relative to fire (h<0 pre-fire, h≥0 post-fire)
- Aggregate ATT: $\widehat{\text{ATT}} = \frac{1}{k} \sum_{h \geq 0} \beta_h$
- Weighting: PS-IPW on raster-based WFP 2012 summaries, fire history, baseline covariates

### B. Propensity-Score Matching (Selection Bias Reduction)

**Threat**: Wildfires endogenously locate in high-hazard, economically vulnerable tracts.

**Mitigation**: PS-IPW matching on:
- **Raster-based WFP 2012** (270m resolution, predetermined): mean percentile, % per quintile, distance to high-hazard pixel
- **Pre-2013 fire history**: any large fire 1984–2012, log acres burned
- **Baseline covariates** (2012 ACS): poverty rate, median HH income, population density, demographics
- **RUCC**: rural-urban classification

**Weights**: Treated $w=1$; controls $w=\hat{e}/(1-\hat{e})$; trim 99th percentile

**Balance check**: Standardized mean differences (SMD) before/after; target SMD<0.10

### C. Parallel Trends & Validity Tests

**Assumption**: Conditional on matching covariates, treated and control tracts would follow parallel poverty trends absent fire.

**Pre-trend test** (visual, no p-values):
- Estimate $\beta_h$ for h<0 (pre-fire periods)
- Expected: $\beta_h ≈ 0$, 95% CIs near zero
- Report: Event-study plot with pre/post region shaded

**Falsification tests**:
1. **Anticipation**: Leads of treatment (future fires) on current outcomes; should be ≈0
2. **Placebo**: Assign fires to pre-2013 years; estimate C&S ATT on post-2017 outcomes; should be ≈0
3. **Alternative control**: Exclude never-treated with pre-2013 fires; ATT should remain similar
4. **Smoke spillover**: Vary 100 km buffer (50, 150 km); ATT should be stable across radii

### D. Heterogeneous Effects & Mechanisms

**Extensive vs. intensive margin**:
- Binary any-fire (extensive, primary)
- Fire count, acres burned, WFP intensity (intensive; tests dose-response)

**Mediation analysis** (net migration as mediator):
1. Estimate ATT on net-migration rate
2. Estimate coefficient of migration on poverty
3. Decompose: Total ATT = Direct (income) + Indirect (compositional)

**Subgroup heterogeneity** (exploratory):
- By baseline poverty (high/medium/low)
- By urbanicity (rural, urban)
- By geographic region (South/Midwest/Northeast/West)
- By baseline WFP hazard (high/medium/low)

---

## IV. Results (3–4 pages)

### A. Main Findings

**Table 2: Staggered C&S ATT (Primary Outcomes)**

Rows:
- Poverty rate (percentage point change)
- Median HH income ($ change, 2020 dollars)
- Employment rate (pp change)
- Net-migration rate (pp change)

Cols:
- (1) Coefficient
- (2) 95% CI (bootstrap, 1,000 replicates)
- (3) Aggregate effect size (years post-fire, range)
- (4) N observations

Note: PS-IPW weights applied; SE clustered by county

**Figure 2: Event-Study Plot (Poverty, Primary Outcome)**
- X-axis: Relative time h (h=-1, 0, 1, 2, 3 corresponding to ~3yr pre, 0yr post, +3yr, +5yr, +7yr)
- Y-axis: $\beta_h$ coefficient ± 95% CI
- Shade pre-trends region (h<0); highlight post-treatment (h≥0)
- Interpretation: Trajectory of poverty effects over time

**Figure 3: Event-Study Plot (Median Income, Secondary Outcome)**
- Same structure as Figure 2; document income trajectory

### B. Economic Magnitude & Interpretation

Example narrative:
- "Exposure to large wildfire increases tract poverty rate by **X percentage points** (95% CI: [a, b]) within 3–5 years post-fire. This corresponds to approximately **Y additional households** falling below the poverty line in the average treated tract."
- "Median household income declines by **$Z** (95% CI: [...])."
- "Effects are **largest in rural tracts** (subgroup ATT = ...) and **smallest in high-baseline-income tracts** (...)."

### C. Mediation Results

**Table 3: Decomposition of Poverty Effect via Migration**

Rows:
- Total ATT (poverty rate)
- ATT (net-migration rate)
- Mediator coefficient (migration → poverty)
- Indirect effect (mediation)
- Direct effect

Cols:
- Coefficient, 95% CI, % of total effect

Narrative interpretation:
- "Out-migration **partially** mediates poverty effects. **Z% of the poverty increase driven by selective out-migration** (compositional effect); **(100–Z)% reflects income losses** (welfare effect). This suggests that [interpret: residents leaving are poorer/younger; low-income stayers experience income loss; economy restructures]."

### D. Extensive vs. Intensive Margin

**Table 4: Dose-Response Specification**

Rows:
- Any fire (binary, extensive)
- Fire count: 1 fire, 2 fires, 3+ fires
- Acres burned: per 10,000-acre increment
- WFP intensity: per percentile point

Cols: ATT, 95% CI, interpretation

Narrative: "Effects scale with fire intensity. Tracts with 2+ fires show [Y]× the poverty effect of single-fire tracts, consistent with causal relationship."

---

## V. Heterogeneous Effects & Mechanisms (2–2.5 pages)

### A. Subgroup Analysis

**Table 5: Heterogeneous Effects by Baseline Characteristics**

Rows: Baseline poverty (high/medium/low), urbanicity (rural/urban), region (South/MW/NE/W), baseline WFP (high/med/low)

Cols: Subgroup ATT, 95% CI, N, median MOE (if rural)

Interpretation: "Poverty effects **largest in rural and high-poverty-baseline tracts**; smallest in urban and low-poverty tracts. Effects consistent across regions, suggesting national generalizability."

*Caution*: "Subgroup estimates are exploratory; do not formally test differences."

### B. Mechanisms

**Narrative on employment & sector disruption**:
- If employment rate falls: "Job loss is primary mechanism; **X% employment decline within 3–5 years**, with limited recovery."
- If employment recovers but income doesn't: "Employment recovery modest; workers displaced into lower-wage sectors (evidence from [sector breakdown])."

**Narrative on migration as mechanism**:
- If large mediation effect: "Out-migration is primary response; **Z% of poverty tracts relocate**. Low-income households disproportionately leave; remaining population experiences income shock."
- If small mediation effect: "Limited migration response; residents adapt in place. Poverty increase reflects individual income losses."

**Narrative on adaptive capacity**:
- If heterogeneity by baseline income: "High-income tracts recover quickly; low-income tracts experience persistent poverty effects, consistent with differential adaptive capacity."

---

## VI. Robustness & Sensitivity (2–2.5 pages)

### A. Threats & Robustness Tests (Organized by Threat, Not Test Type)

**Selection bias (already matched via PS-IPW; additional robustness)**:
- Placebo test (pre-2013 fires assigned as treatment; ATT ≈ 0 expected)
- Alternative control definition (exclude pre-2013 fires from controls; ATT similar)
- Alternative matching (CEM on WFP quintiles; ATT similar to PS-IPW)

**Smoke spillover**:
- Vary buffer radius: 50, 100 (baseline), 150 km
- Report: ATT across all radii; assess sensitivity

**Regional confounds**:
- Add state × period FE (already in baseline?)
- Add census-division × period FE
- Report: Whether regional controls change ATT

**ACS measurement error & rural data quality**:
- Vary MOE threshold: 20%, 30% (baseline), 40%
- Report by urbanicity (rural vs. urban)
- Document: Median MOE by subgroup; assess whether results stable

**Fire definition**:
- Vary MTBS minimum: 500, 1,000 (baseline), 2,000 acres
- Report: ATT scale with minimum threshold

**Specification**:
- Event-study window: h ∈ {-2, -1, 0, 1, 2, 3} vs. {-1, 0, 1, 2, 3, 4, 5, 7}
- Weighted vs. unweighted ATT aggregation
- Report: Sensitivity to specification

**Estimator robustness**:
- Sun & Abraham (2021) heterogeneity-robust estimator alongside C&S
- Report: Whether conclusions differ

**Table 6: Robustness Summary**
- Rows: Robustness test (smoke, MOE, fire threshold, regional FE, etc.)
- Cols: ATT, 95% CI, notes
- Highlight if any spec substantially changes conclusions

### B. Limitations & Caveats

(Narrative; 0.5 page)
- MTBS ≥1,000 acres limits to large fires; results not generalizable to smaller fires
- ACS 5-year estimates necessary for rural validity; coarse temporal resolution; pre-post measurement 4–6 years apart
- Rural tracts have larger ACS MOE; wider CIs by design, not weakness
- Cannot identify long-term persistence (>5 years) with current data
- Migration measure (ACS 5-yr residence) noisy; mediation results exploratory
- Fire severity not directly measured; use binary + acres as proxy
- Smoke impacts proxy via geographic buffer (actual smoke transport varies)

---

## VII. Discussion & Policy Implications (1.5–2 pages)

### A. Interpretation of Findings

*Restate main finding with mechanism*:
- "Large wildfires increase poverty rates in affected census tracts, with effects mediated partially by population displacement and partially by income losses."
- "Policy implication: Relief design should account for both income-support needs (for stayers) and relocation assistance (for displaced)."

### B. Scope & Generalizability

- **Geographic**: Results span all lower-48 states; fire impacts not regionally concentrated (if true; else flag regional heterogeneity)
- **Fire size**: MTBS ≥1,000 acres; trade-off cleaner identification for limited scope
- **Time horizon**: Medium-term effects (3–5 yr post-fire); long-term persistence unknown

### C. Comparison to Prior Work

- Contrast to county-level prior work; explain why tract resolution matters
- Situate vis-à-vis health/property impact studies
- Note: First study to explicitly decompose poverty effects via mediation

### D. Open Questions & Future Work

- Do effects persist beyond 5–7 years? (Requires future ACS data)
- Differential impacts by disaster relief generosity (FEMA assistance)? (Requires federal assistance micro-data)
- Intergenerational effects on children's long-run outcomes? (Requires longitudinal linkage)
- How do repeated fires compound effects? (Current design captures single-fire cohorts; future multi-event panel)

---

## VIII. Conclusion (0.5 page)

Concise restatement of primary finding + policy implication. No new results.

Example: "Large wildfires cause substantial, measurable increases in poverty rates that persist 3–5 years post-fire. Results highlight distributional dimensions of climate risks and inform targeting of disaster relief toward income support and managed retreat in fire-prone regions."

---

## Tables & Figures Summary

### Main Tables (in Results § IV)
1. **Table 1a**: Pre-treatment summary stats (pre-IPW) — shows imbalance
2. **Table 1b**: Post-treatment summary stats (post-IPW) — shows improved balance
3. **Table 2**: Staggered C&S ATT (all outcomes) — main results
4. **Table 3**: Mediation decomposition (poverty via migration)
5. **Table 4**: Dose-response (extensive vs. intensive margin)
6. **Table 5**: Heterogeneous effects (by subgroups)
7. **Table 6**: Robustness summary (tests organized by threat)

### Appendix Tables (Optional)
- A1: Balance diagnostics (SMD by covariate, pre/post-IPW)
- A2: Propensity score model coefficients
- A3: Full event-study $\beta_h$ with CIs (long table)
- A4: Subgroup analysis (extended; more granular breakdowns)
- A5: Alternative identification tests (placebo, leads, alternative controls)

### Main Figures (in Results & Robustness § IV–VI)
1. **Figure 1**: Geographic map of fires, treated tracts, control buffer
2. **Figure 2**: Event-study plot (poverty) — central figure
3. **Figure 3**: Event-study plot (income) — secondary outcome
4. **Figure 4**: Propensity score density (pre/post-IPW) — balance diagnostic
5. **Figure 5**: Event-study by subgroup (rural vs. urban, or high-poverty vs. low-poverty) — heterogeneity
6. **Figure 6**: Robustness to smoke buffer radius — sensitivity plot (ATT vs. buffer km)

### Appendix Figures (Optional)
- A1: Event-study plots (employment, migration) — secondary outcomes
- A2: Propensity score distributions by covariate — balance check
- A3: Residual spatial autocorrelation (Moran's I) — validity check
- A4: Robustness across MOE thresholds by urbanicity — rural sensitivity

---

## Proposed Abstract Structure

**Format**: Single-paragraph abstract, ~250 words; four-sentence structure

**Sentence 1 (Hook & Gap)**:
"Large wildfires affect millions of Americans annually, yet empirical evidence on causal poverty impacts remains limited. Prior research focuses on health and property damage; distributional economic effects—particularly on vulnerable populations in rural areas—are understudied."

**Sentence 2 (RQ & Design)**:
"This paper estimates the causal effects of large wildfires on poverty rates using a national sample of ~45,000 census tracts observed 2012–2022. We employ staggered difference-in-differences (Callaway & Sant'Anna 2021) with spatial matching on USFS Wildfire Hazard Potential (270m raster, predetermined)."

**Sentence 3 (Main Results)**:
"Exposure to large wildfires (≥1,000 acres) increases tract poverty rates by [X] percentage points within 3–5 years post-fire. Mediation analysis indicates that [Z]% of the effect is driven by selective out-migration; [100–Z]% reflects income losses among stayers, implying substantial welfare costs."

**Sentence 4 (Implication)**:
"Results underscore the distributional impacts of climate-driven disasters and inform disaster relief design, emphasizing trade-offs between income support for stayers and relocation assistance for displaced residents."

---

## Three Possible Article Titles

1. **"Wildfires and Poverty: Evidence from Census Tracts, 2013–2021"**
   - Straightforward, descriptive; emphasizes national scope and tract resolution

2. **"Fire and Flight: Displacement, Income Loss, and Poverty in the Wildfire Era"**
   - Evocative; emphasizes mechanism (displacement vs. income) and policy relevance

3. **"Climate Shocks and Economic Vulnerability: The Causal Effect of Wildfires on Poverty in Rural and Urban America"**
   - Academic, comprehensive; signals vulnerability/distributional focus

*(Choose based on co-author preference and target journal scope)*

