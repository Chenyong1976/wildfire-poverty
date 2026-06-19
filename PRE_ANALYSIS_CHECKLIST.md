# Pre-Analysis Checklist
**Start Date**: [TBD]  
**Project**: Wildfire Impact on Poverty & Net Migration (National, 2013–2021)

---

## Phase 0: Pre-Analysis Setup (Week 0)

- [ ] **Collaborator sign-off**: Review RESEARCH_PLAN.md v2.0 and UPDATED_PLAN_SUMMARY.md; obtain approval to proceed
- [ ] **PAP registration**: Register on OSF, AEA RCT Registry, or SSRN with spec freeze (see RESEARCH_PLAN.md §6)
  - [ ] Record PAP DOI and submission date in project README
- [ ] **Literature review**: Run `/deep-research` (lit-review mode) to populate bibliography
  - [ ] Query: "Wildfire economic impacts, poverty, migration mechanisms, environmental shocks"
  - [ ] Output: Annotated bibliography → save to `docs/LITERATURE_NOTES.md`
- [ ] **Project setup**: Initialize Git repo, create `.gitignore`, set up remote backup
  - [ ] Add data/raw/ and .RData, *.rds, .pyc to .gitignore
  - [ ] Create initial commit with RESEARCH_PLAN.md, CLAUDE.md

---

## Phase 1: Data Acquisition & Cleaning (Weeks 1–3)

### Data Sources: Acquisition

- [ ] **ACS 5-year estimates (IPUMS)**: Download 2007–2022 for all lower-48 counties
  - Variables: Poverty rate, median HH income, employment rate, net migration (5-yr residence change)
  - [ ] Clarify vintage windows (e.g., 2011–2015 labeled "2015")
  - [ ] Identify & document missing values; flag if MOE > 30% of estimate
  - [ ] Save to `data/raw/acs_extracts/acs_2007_2022_lower48.csv`

- [ ] **MTBS fire perimeters**: Confirm available from wildfire-finance project
  - [ ] If not available: Download from USGS MTBS website (1984–2022, nationwide)
  - [ ] Verify file format (shapefile or GeoJSON); ensure FIPS-county overlay possible
  - [ ] Save symlink or copy to `data/raw/mtbs_perimeters/`

- [ ] **WFP 2012**: Confirm available from wildfire-finance
  - [ ] Check for file: `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/wfp2012_cnt`
  - [ ] If not available: Download from USFS website (ESRI Grid format, EPSG:5070)
  - [ ] Save to `data/raw/whp_rasters/`

- [ ] **WHP 2014** (robustness only): Confirm available from wildfire-health
  - [ ] File: `wildfire-health/data/raw/WHP/Data/whp_2014_continuous/whp2014_cnt`
  - [ ] Save to `data/raw/whp_rasters/` if needed for analysis

- [ ] **County boundaries**: Download TIGER shapefiles (lower-48) for spatial ops
  - [ ] Save to `data/raw/county_shapefiles/`

- [ ] **BEA per-capita income** (optional): Acquire from FRED API
  - [ ] Fallback: Use ACS median income as primary, BEA as cross-check

### Data Processing

- [ ] **Implement `code/01_build/01_whp_to_county.py`** (reuse from wildfire-finance if available)
  - [ ] Input: WFP 2012 raster (270m)
  - [ ] Output: `data/processed/whp_2012_county.parquet` (county-level mean/percentile)
  - [ ] Test on 10 sample counties; verify values in [0, 100+] range

- [ ] **Implement `code/01_build/02_mtbs_to_county.py`** (reuse from wildfire-finance)
  - [ ] Input: MTBS fire perimeters (2013–2021)
  - [ ] Output: `data/processed/fire_treatment_assignment.parquet`
  - [ ] Columns: FIPS, year_first_fire (2013–2021 or NA), fire_count, total_acres, cohort (g=2017, g=2022, g=0)
  - [ ] **Quality check**: Verify n_treated ≥ 600 counties total; note distribution across g=2017 vs. g=2022

- [ ] **Implement `code/01_build/03_acs_pull.py`**
  - [ ] Input: IPUMS ACS CSV extracts (2007–2022)
  - [ ] Output: `data/processed/acs_2007_2022_county_clean.parquet`
  - [ ] Columns: FIPS, year (2007, 2012, 2017, 2022), poverty_rate, median_income_nominal, employment_rate, net_migration_rate, population
  - [ ] Deflate income to 2019$ using national CPI-U
  - [ ] **Quality check**: Flag cells with MOE > 30% point estimate; count missing by variable

- [ ] **Implement `code/01_build/04_matching_covariates.py`**
  - [ ] Input: ACS 2012, USDA RUCC 2013
  - [ ] Output: `data/processed/matching_covariates_2012.parquet`
  - [ ] Columns: FIPS, poverty_rate_2012, income_2012, pop_density_2012, pct_age65_2012, rucc_2013
  - [ ] Test: Merge to treatment assignment; verify no missingness on matching covariates

- [ ] **Implement `code/01_build/05_smoke_buffer.py`** (reuse from wildfire-finance)
  - [ ] Input: MTBS fire perimeters, county boundaries
  - [ ] Output: `data/processed/smoke_buffer_100km.parquet` (list of counties within 100 km of any fire)
  - [ ] Test: Spot-check 10 fires; visualize 100 km buffer in GIS

- [ ] **Implement `code/01_build/06_panel_assemble.py`**
  - [ ] Input: All datasets from above
  - [ ] Output: `data/processed/analysis_sample_final.parquet` (balanced panel)
  - [ ] Exclusions: Pop < 1,000 any year; smoke-excluded counties; pre-2013 fire counties
  - [ ] Dimensions: ~3,100 counties × 4 periods = ~12,400 obs
  - [ ] **Final check**:
    - [ ] No missing values in key variables (poverty, income, treatment, covariates)
    - [ ] Sample counts by cohort printed and saved to `data/metadata/cohort_counts.csv`
    - [ ] Smoke buffer applied: show n_treated before/after exclusion

### Documentation

- [ ] **Data dictionary**: Create `docs/DATA_DICTIONARY.md`
  - [ ] Define all variables, units, data source, processing notes
  - [ ] Document ACS disclosure avoidance impact
  - [ ] Flag any top-coded or imputed values

- [ ] **Sample restrictions log**: Save `data/metadata/sample_restrictions_log.txt`
  - [ ] Count counties excluded at each step (pop < 1,000, smoke buffer, etc.)
  - [ ] Rationale for each restriction

---

## Phase 2: Propensity-Score Matching & Balance Diagnostics (Week 4)

### Matching Implementation

- [ ] **Implement `code/02_matching/01_ps_matching.R`**
  - [ ] Model: Logistic regression of treatment (g ≠ 0) on:
    - WFP 2012 quintile (5 indicators)
    - Pre-2013 fire indicator, log acres burned 1984–2012
    - 2012 ACS baseline: poverty rate, median income, pop density, % age 65+
    - RUCC 2013
    - Population
  - [ ] Propensity score: $\hat{e}_i = \text{Pr}(\text{treated} | X)$
  - [ ] Weights: treated w=1, control w=$\hat{e}/(1-\hat{e})$, trimmed at 99th percentile
  - [ ] Save PS and weights to `results/rds/ps_match_*.rds`

### Balance Diagnostics

- [ ] **Implement `code/02_matching/02_balance_table.R`**
  - [ ] Compute standardized mean differences (SMD) before and after IPW
  - [ ] Target: SMD < 0.1 for all covariates post-reweighting
  - [ ] Output: `results/tables/balance_table.csv` and `.tex` (LaTeX for paper)
  - [ ] ESS calculation: Report effective sample size of reweighted control group
    - [ ] Alert if ESS << unweighted N (thin common support)

- [ ] **Propensity score visualization**
  - [ ] Generate density plots: PS distributions (treated vs. control) before and after reweighting
  - [ ] Save to `results/figures/ps_density_before_after.png`
  - [ ] Check for overlap (common support); flag if extreme PS values

---

## Phase 3: Event-Study & Staggered DiD Estimation (Weeks 5–6)

### Main Estimation

- [ ] **Implement `code/03_analysis/01_cs_main.R`**
  - [ ] Callaway & Sant'Anna (2021) using R package `did::att_gt()`
  - [ ] Event-study specification: $h \in \{-3, -2, -1, 0, 1, \ldots, 7\}$
  - [ ] Outcomes: poverty rate, median income, net-migration rate, employment rate
  - [ ] Weights: PS-IPW (from Phase 2)
  - [ ] FE: County + census-period FE; robustness: add state × period FE
  - [ ] SE: Clustered at county level; bootstrap CIs (1,000 reps)
  - [ ] Save results: `results/rds/cs_att_main.rds` (object), `results/tables/cs_att_table.csv`

- [ ] **Aggregate ATT**: Compute simple mean of $\beta_h$ for $h \geq 0$; report with 95% CI

- [ ] **Cohort-specific ATTs**: Report separately for g=2017 and g=2022

### Event-Study Visualization

- [ ] **Implement `code/03_analysis/02_event_study.R`**
  - [ ] Plot $\beta_h$ with 95% CIs for poverty rate (primary outcome)
  - [ ] Clearly label: pre-trends (h<0, shaded), treatment year (h=0), post-trends (h≥0)
  - [ ] Assess: Are pre-trends negligible relative to post-treatment effects?
  - [ ] Save: `results/figures/event_study_poverty.png` (300 DPI)
  - [ ] Repeat for income, migration, employment (secondary figures)

### Mediation Analysis

- [ ] **Implement `code/03_analysis/03_mediation_analysis.R`**
  - [ ] Estimate ATT on net-migration rate (mediator)
  - [ ] Quantify: Are out-migration effects driving poverty changes?
  - [ ] Decompose: Direct effect (income) vs. indirect effect (compositional)
  - [ ] Save: `results/rds/mediation_*.rds`, `results/tables/mediation_table.csv`

---

## Phase 4: Robustness & Specification Checks (Week 7)

### Robustness Tests (6+ specs)

- [ ] **Implement `code/03_analysis/04_robustness.R`**
  - [ ] **Smoke spillover**: Vary buffer (50, 100, 150 km); table ATT stability
  - [ ] **Fire threshold**: Vary MTBS acres (500, 1,000, 2,000)
  - [ ] **Placebo test**: Assign fires to 2007–2012; expect ATT ≈ 0
  - [ ] **Event-study window**: Vary $h$ (−2 to 5 vs. −3 to 7)
  - [ ] **Regional FE**: State×period vs. division×period
  - [ ] **Sample restriction**: Drop pre-2013 fire counties (stricter never-treated)
  - [ ] Output: `results/tables/robustness_table.csv` (ATT across specs)

### Heterogeneous Effects

- [ ] **Implement `code/03_analysis/06_heterogeneity.R`**
  - [ ] **Extensive vs. intensive margin**: Any fire (binary) vs. fire count / acres burned
  - [ ] **Subgroup analysis** (exploratory, due to power limits):
    - Census region (South, Midwest, Northeast, West)
    - Baseline poverty (High >20%, Medium 10–20%, Low <10%)
    - Fire frequency (0, 1, 2+)
    - Time period (g=2017 vs. g=2022)
  - [ ] Report: Point estimates + 95% CIs by subgroup
  - [ ] **Label all subgroup results as "exploratory" due to small N per subgroup**
  - [ ] Save: `results/tables/heterogeneity_*.csv`

### Alternative Estimators

- [ ] **Implement `code/03_analysis/05_sun_abraham.R`**
  - [ ] Re-estimate allowing heterogeneous effects by cohort and time
  - [ ] Compare to C&S ATT; if similar, no heterogeneity bias
  - [ ] Save: `results/tables/sun_abraham_table.csv`

- [ ] **Falsification test**: Pre-2013 fire assignment
  - [ ] Assign fires to 2007–2012; estimate C&S ATT
  - [ ] Expect ATT ≈ 0 (no effect before treatment)
  - [ ] Save: `results/tables/placebo_test.csv`

---

## Phase 5: Output & Visualization (Week 8)

### Tables (LaTeX)

- [ ] **Implement `code/04_output/01_tables.R`**
  - [ ] **Table 1a**: Summary stats (treated vs. control), pre-IPW balance
  - [ ] **Table 1b**: Post-IPW balance (SMD, effective N)
  - [ ] **Table 2**: Main ATT (poverty, income, migration, employment)
  - [ ] **Table 3**: Extensive vs. intensive margin ATTs
  - [ ] **Table 4**: Robustness specs (6+ columns)
  - [ ] **Table 5**: Subgroup heterogeneity (exploratory)
  - [ ] **Appendix**: Balance table (pre/post-IPW), cohort-specific ATTs, additional robustness
  - [ ] All tables: .csv + .tex with notes (data source, sample, SE clustering, N obs)

### Figures (300 DPI)

- [ ] **Implement `code/04_output/02_figures.py`**
  - [ ] **Figure 1**: Map of treated counties and fire perimeters (MTBS 2013–2021)
  - [ ] **Figure 2**: Event-study plot (poverty rate, primary outcome)
  - [ ] **Figure 3**: Event-study plot (median income, secondary)
  - [ ] **Figure 4**: Propensity score density (before/after IPW)
  - [ ] Save all at 300 DPI, .png format; include in `results/figures/`

---

## Phase 6: Manuscript Drafting (Weeks 9–10)

### Paper Structure (using `/academic-paper` skill)

- [ ] **Introduction** (2–3 pp)
  - [ ] Hook: Rising wildfire frequency, economic vulnerability
  - [ ] Gap: Distributional effects unknown at national scale
  - [ ] RQ: Do wildfires reduce incomes and increase poverty? Role of migration?
  - [ ] Contribution: National scope + migration mechanism
  - [ ] Lit: ~4–5 papers positioned tightly

- [ ] **Data & Sample** (1–2 pp)
  - [ ] Sample frame: Lower-48 counties, 2007–2022 ACS
  - [ ] Treatment definition: MTBS ≥1,000 acres, 2013–2021; two cohorts
  - [ ] Outcomes: Poverty, income, migration, employment
  - [ ] Tables 1a–1b: Balance pre/post-IPW
  - [ ] Figure 1: Map

- [ ] **Empirical Strategy** (2–2.5 pp)
  - [ ] Identifying variation: Staggered fires across lower-48
  - [ ] Estimand: ATT
  - [ ] Main equations: Event-study and aggregate ATT (display math)
  - [ ] Threats + mitigations (4–5 key threats)

- [ ] **Results** (3–4 pp)
  - [ ] Figure 2: Event-study (poverty rate)
  - [ ] Table 2: Main ATT
  - [ ] Table 3: Extensive vs. intensive margin
  - [ ] Mediation results: Net-migration interpretation
  - [ ] Prose: Highlight magnitude and economic significance

- [ ] **Robustness** (2–2.5 pp)
  - [ ] Organized by identification threat (not test type)
  - [ ] Table 4: 6+ robustness specs
  - [ ] Narrative: Only highlight divergent findings

- [ ] **Discussion** (1.5–2 pp)
  - [ ] Mechanism: Compositional effect vs. income loss?
  - [ ] Scope: MTBS >1,000 acres (trade-off: clean ID vs. limited scope)
  - [ ] Limitations: Disclosure avoidance, measurement error, limited follow-up
  - [ ] Open questions: Long-term persistence? Aid mechanisms? Subpopulation effects?

- [ ] **Conclusion** (0.5 pp)
  - [ ] Restate finding: X% poverty increase, mediated by Z% out-migration
  - [ ] Hedged policy implication
  - [ ] No new results

### Peer Review (using `/academic-paper-reviewer` skill)

- [ ] Simulate 5 reviewers: EIC, ID specialist, Data specialist, Economics specialist, Devil's Advocate
- [ ] Collect structured feedback; iterate on manuscript

---

## Phase 7: Final Deliverables (Weeks 11+)

- [ ] **Replication package**:
  - [ ] Code: All scripts in `code/`, documented
  - [ ] Data: Final analysis sample (`analysis_sample_final.parquet`) + sample restrictions doc
  - [ ] Results: All tables and figures
  - [ ] PAP: `docs/PAP.md` with specification freeze
  - [ ] Deviations log: Any post-hoc changes flagged

- [ ] **README**: Clear instructions to reproduce all results

- [ ] **Zenodo or SSRN**: Upload preprint + replication materials

- [ ] **Journal submission**: Choose target (JUE, RSUE, AEJ:Applied); prepare cover letter

---

## Sign-Off

- [ ] **Data assembly complete**: All datasets merged, balanced panel ready
- [ ] **Analysis complete**: All estimates, robustness tests, figures generated
- [ ] **Manuscript complete**: All sections written, reviewed, approved for submission
- [ ] **Replication package complete**: Code, data, results, documentation archived

---

**Status**: [ ] Ready to start | [ ] In progress | [ ] Complete
