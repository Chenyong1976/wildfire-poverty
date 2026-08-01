# Research Plan: Wildfire Impact on Poverty and Economic Outcomes

**Last Updated**: 2026-07-31 (MAJOR REVISION: Single Clean Cohort Design)  
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
- Tracts with ACS poverty MOE > 30% of point estimate (data quality)
- Tracts with population < 500 (ACS reliability threshold, especially rural)

#### Temporal Structure

**Three non-overlapping measurement periods** (ACS 5-year estimates):

| Period | ACS Vintage | Window | Relative to Fires | Sample Size |
|--------|-------------|--------|------------------|-------------|
| **Baseline (Pre)** | ACS 2012 | 2008–2012 | Pre-fire (before 2015) | All tracts |
| **Medium-run (Post1)** | ACS 2022 | 2018–2022 | 1–4 years post-fire | ~700 treated + ~40k control |
| **Later medium-run (Post2)** | ACS 2023 | 2019–2023 | 2–6 years post-fire | ~700 treated + ~40k control |

**Critical clarification on temporal overlap**:
- ACS 2022 (2018–2022) and ACS 2023 (2019–2023) share years 2019–2022 — this is **expected and acceptable**
- What matters for identification is that **fire years 2015–2017 are NOT within either ACS measurement window**
- Two post-fire periods allow estimation of **event-study dynamics** (effects at 1–4 years vs. 2–6 years)
- Overlapping measurement windows are standard in panel data and provide independent information

#### Control Group Construction

**Propensity-score inverse-probability weighting (PS-IPW)**:

1. **Propensity score model** (logistic, matching on pre-treatment covariates):
   $$\Pr(\text{Treated} | X) = \Lambda(\alpha + X \beta)$$
   
   Where $X$ includes:
   - **WFP 2012 raster summaries** (270m resolution, predetermined):
     - Mean WFP 2012 percentile (0–100) across pixels in tract
     - % tract area in each WFP hazard quintile (5 indicators)
     - Distance from tract centroid to nearest pixel WFP > 75th percentile
   - **Pre-2013 fire history**: Any fire 1984–2012; log total acres burned 1984–2012
   - **Pre-treatment covariates** (2012 ACS, tract-level):
     - Poverty rate, median HH income, population density
     - % age 65+, % race/ethnicity groups (White, Black, Hispanic, Asian)
   - **RUCC 2013**: County-level rural-urban classification (merged to tracts)

2. **Inverse-probability weights**:
   - Treated tracts: $w_i = 1$
   - Control tracts: $w_i = \hat{e}_i / (1 - \hat{e}_i)$ where $\hat{e}_i$ = estimated propensity score
   - Trim at 99th percentile to stabilize variance

3. **Balance diagnostics**:
   - Standardized mean differences (SMD) before and after weighting
   - Target: SMD < 0.10 for all covariates post-weighting
   - Report effective sample size (ESS) of reweighted controls
   - Plot propensity score distributions (treated vs. control, pre/post reweighting)

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

**Event-study variant** (three time periods allow limited event-study):

$$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \sum_{h \in \{-1, 0, +1\}} \beta_h \cdot \text{Treated}_i \cdot \mathbb{1}[t = t_h] + X_{i,2012} \gamma + \epsilon_{i,t}$$

Where $h$ indexes relative time:
- $h = -1$: ACS 2012 (normalized to 0, reference period)
- $h = 0$: ACS 2022 (1–4 years post-fire)
- $h = +1$: ACS 2023 (2–6 years post-fire)

**Interpretation**:
- $\beta_h$ = ATT $h$ periods relative to fires (treatment year normalized to 2015–2017 midpoint ≈ 2016)
- $\beta_0$ = medium-run effect (1–4 years post-fire)
- $\beta_1$ = later medium-run effect (2–6 years post-fire)
- If $\beta_1 \approx \beta_0$, effects persist; if $\beta_1 > \beta_0$, effects amplify; if $\beta_1 < \beta_0$, effects decay

**Robustness variants**:

1. **Regression adjustment** (include covariates as regressors instead of matching):
   $$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \beta \cdot \text{Treated}_i \cdot \text{Post}_t + X_{i,2012} \gamma + \text{State}_i \cdot \lambda_t + \epsilon_{i,t}$$
   (Add state × period fixed effects to absorb region-specific time trends)

2. **Intensive margin** (dose-response by burned share):
   $$\text{Outcome}_{i,t} = \alpha_i + \lambda_t + \beta \cdot \text{BurnShare}_i \cdot \text{Post}_t + X_{i,2012} \gamma + \epsilon_{i,t}$$
   Where $\text{BurnShare}_i$ = % of tract area burned in 2015–2017 fires (continuous [0, 100])

#### Threats to Identification & Mitigation

| Threat | Mechanism | Mitigation | Robustness |
|--------|-----------|-----------|-----------|
| **Selection bias** | High-hazard/poor tracts experience fires endogenously | PS-IPW matching on WFP 2012 raster (predetermined before 2013) + pre-2013 fire history | Report SMD < 0.10; vary matching specifications (CEM on WFP quintiles); include pre-treatment covariates in regression |
| **Smoke spillover** | Control tracts exposed to smoke from treated fires | 100 km buffer exclusion from controls | Vary 50 km, 150 km; check if ATT stable |
| **Parallel trends** | Treated and control tracts follow different trends absent fires | Pre-treatment covariate balance; placebo test (assign fires to pre-2013, test ATT ≈ 0) | Inspect pre-treatment balance; run falsification test |
| **Temporal confounds** | 2015–2017 fires coincide with region-specific shocks (e.g., local economic downturns, housing bubbles) | State × period FE; census division × period FE | Report results with and without regional controls |
| **Migration composition** | Tract poverty changes both from income loss AND selective out-migration | Descriptive decomposition: estimate ATT on net migration separately, then estimate conditional effect on poverty | Mediation analysis (§4.2); label as descriptive, not causal |
| **Measurement error** | ACS tract-level estimates have large MOE, especially rural | Drop tracts with MOE > 30% of poverty point estimate; document by urbanicity | Robustness: vary MOE threshold (20%, 40%) |
| **Effect heterogeneity** | Fires affect different tracts differently (by poverty, region, fire severity) | Report extensive margin (any fire) and intensive margins separately; subgroup analysis | Sun & Abraham (2021) heterogeneity-robust estimator; subgroup ATTs by poverty quintile, region, WFP hazard |

---

## 3. Data & Sample Definition

### Sample Frame

- **Geographic scope**: All lower-48 US states (~70,000 census tracts; Census 2010 definition)
- **Time period**: ACS 5-year estimates, three periods:
  - Baseline: 2012 (2008–2012 window)
  - Post-treatment 1: 2022 (2018–2022 window)
  - Post-treatment 2: 2023 (2019–2023 window)
- **Unit of analysis**: Census tract (Census 2010; ~70,000 tracts nationally)
- **Expected sample after screening**: ~700 treated + ~40,000 never-treated = **~40,700 tracts total**

### Outcome Variables

| Outcome | Source | Definition | Notes |
|---------|--------|-----------|-------|
| **Poverty rate** (primary) | ACS 5-yr | % population below federal poverty line | 5-year estimates essential for rural reliability |
| **Median HH income** | ACS 5-yr | Median household income (nominal, adjusted to 2020$) | Secondary outcome |
| **Employment rate** | ACS 5-yr | % of civilian labor force employed | Captures labor market adjustment |
| **Net-migration rate** (mediator) | ACS 5-yr | % moved in (past 5 yrs) minus % moved out; proxy for net migration | Descriptive decomposition mechanism |

All outcomes available at **tract level only for 5-year estimates**. No 1-year or 3-year estimates used (rural data quality constraint).

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
| Poverty rate, income, employment, net migration | ACS 5-yr (IPUMS) | Tract-level CSV | ⏳ Pending IPUMS download |
| Fire perimeters & treatment assignment | MTBS (USGS) | Shapefile | ✓ Linked from wildfire-health |
| WFP 2012 (primary matching) | USFS LANDFIRE | 270m raster, EPSG:5070 | ✓ Linked from wildfire-health |
| Census tract boundaries | Census TIGER | Shapefile, Census 2010 | ⏳ To download |
| Pre-2013 fire history | MTBS 1984–2012 | Shapefile | ✓ Linked from wildfire-health |
| RUCC 2013 | USDA ERS | County-level codes | ⏳ To parse from wildfire-health |

### Data Quality Screening

- **ACS 5-year estimates only**: Never use 1-year or 3-year estimates (rural validity constraint)
- **MOE threshold**: Drop tracts if poverty rate MOE > 30% of point estimate
- **Population minimum**: Drop tracts with population < 500
- **Documentation**: Report N tracts dropped by each screen, broken down by urbanicity (RUCC)
- **Expected final sample**: ~40,000–50,000 tracts × 3 periods = ~120,000–150,000 observations

---

## 4. Methods: Implementation Roadmap

### Phase 1: Data Acquisition & Raster Processing (Weeks 1–2)

**Deliverables**:
- `acs_2012_2022_2023_tract_clean.parquet`: ACS outcomes (poverty, income, employment, migration) for 3 periods, ~70k tracts, post-MOE screening
- `fire_treatment_assignment_tract.parquet`: Treatment cohort (g=2016 or g=0), extensive & intensive margins, ~70k tracts
- `whp_2012_tract_raster_summaries.parquet`: Tract-level raster summaries (mean WFP, quintile %, distance to high-hazard pixel)
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

- **Table 1a**: Pre-treatment balance (pre-IPW): treated vs. control
- **Table 1b**: Post-treatment balance (post-IPW): SMD, ESS
- **Table 2**: Threats to identification (summary)
- **Table 3**: Main ATT estimates (all 4 outcomes, point + CI)
- **Table 4**: Descriptive decomposition via net migration
- **Table 5**: Heterogeneous effects (by poverty quintile, region, WFP hazard)
- **Table 6**: Robustness summary (smoke radius, MOE threshold, fire threshold, estimator, regional FE, etc.)
- **Figure 1**: Geographic map (fires, treated tracts, smoke buffer)
- **Figure 2**: Event-study plot (poverty, primary outcome) — h ∈ {−1, 0, +1}
- **Figure 3**: Event-study plot (income, secondary outcome)
- **Figure 4**: Propensity-score density (treated vs. control, pre/post IPW)

---

## 6. Success Criteria & Checkpoints

| Milestone | Criterion | Target |
|-----------|-----------|--------|
| **Data complete** | All ACS 2012/2022/2023 + fire/WFP/RUCC downloaded and validated | Week 2 |
| **Sample finalized** | ~700 treated + ~40k control after all screens; MOE, population filters documented | Week 3 |
| **Balance achieved** | SMD < 0.10 all covariates post-IPW; ESS ≥ 500 | Week 4 |
| **Main estimation complete** | ATT point estimate + 95% CI; event-study $\beta_h$ (h ∈ {−1, 0, +1}) | Week 5 |
| **Robustness complete** | ≥8 robustness specs tabulated; findings stable/sensitive documented | Week 7 |
| **Publication-ready output** | All tables LaTeX-formatted, figures 300 DPI, data dictionary | Week 8 |
| **Manuscript draft** | Introduction through Discussion drafted; results embedded; appendix methodology notes | Week 9 |

---

## 7. Pre-Analysis Plan Registration

**Timing**: Before any estimation begins

**Contents to register**:
- Single-cohort design (fires 2015–2017, g=2016 or g=0)
- ACS periods: 2012, 2022, 2023
- Primary outcome: Poverty rate
- Secondary outcomes: Income, employment, migration
- Main estimand: ATT via DiD with PS-IPW matching on WFP 2012 raster
- Threats and mitigations
- Robustness tests (organized by threat)

**Registry**: OSF (https://osf.io/) or AEA RCT Registry

---

## 8. Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Sample size too small for power** | Verify via Monte Carlo using coefficient priors from wildfire-finance county-level results; expect 0.5–1.0 pp CIs on poverty |
| **Selection bias in fire location** | PS-IPW on WFP 2012 (predetermined) + pre-2013 fire history; balance diagnostics; sensitivity to matching specification |
| **ACS rural MOE large** | Screen tracts with MOE > 30% (documented); robustness test with MOE > 40% |
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

- ✓ Research design finalized (single clean cohort)
- ✓ Identification strategy locked in
- ✓ Data sources identified
- ⏳ Data acquisition pending (ACS download, RUCC parsing)
- ⏳ Analysis scripts staged (code/01_build through code/04_output)
- ⏳ PAP registration pending data completion
- ⏳ Estimation to follow PAP registration

---

*End of Research Plan. Single-cohort design provides clean causal identification with sufficient statistical power for publication-quality results.*
