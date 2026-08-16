# CLAUDE.md — Wildfire-Poverty Analysis Project

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Title**: Wildfire Impact on Poverty: A National Census-Tract Study with Raster-Based Spatial Matching (2015–2017)  
**Status**: Design finalized (2026-08-01, updated 2026-08-02); single clean cohort with robust pre-trend testing and long-run effects  
**Research Question**: Do large wildfires (≥1,000 acres) causally increase poverty rates in US census tracts? What role does population displacement (net migration) play? How persistent are effects?  
**Identification Strategy**: Single clean cohort (fires 2015–2017) + event-study difference-in-differences with propensity-score inverse-probability weighting on USFS WFP 2012 raster (270m resolution)  
**Geographic Scope**: All lower-48 US states (~70,000 census tracts); tract-level resolution captures within-county heterogeneity  
**Spatial Matching**: WFP 2012 Wildfire Hazard Potential at native 270m resolution; tract-level raster summaries (mean WFP percentile, % area per hazard quintile, distance to high-hazard pixels) as primary matching covariates  
**Treatment Definition**: Single non-overlapping fire cohort (2015–2017); ~700–800 treated tracts; ~40,000 never-treated controls  
**Analysis Period**: ACS 5-year estimates: 2010 (h=−3, 2006–2010), 2012 (h=−2), 2014 (h=−1, reference), 2022 (h=0), 2023 (h=+1), 2024 (h=+2); three pre-trends + three post-periods for trajectory estimation. **Note**: ACS 2006-2010 substitutes for unavailable 2005-2009  
**Statistical Power**: ~700 treated vs. ~40k controls, expected CIs ~0.5–1.0 pp on poverty rate  
**Key Innovation**: (1) First **national tract-level** study (not county-level or Western-only); (2) **Clean single-cohort design** with **robust pre-trend testing** (three pre-periods: h ∈ {−3, −2, −1}); (3) **Long-run effect documentation** via h=+2 (3–7 years post); (4) **Raster-based WHP matching** at 270m resolution; (5) Descriptive decomposition of poverty effects via net migration

---

## Core Design

- **Sample**: All lower-48 US census tracts (~70,000); ACS 5-year tract-level estimates 2010, 2012, 2014, 2022, 2023, 2024 (6 periods); after population ≥ 500 and poverty denominator ≥ 100 screens: expected ~70,000 tracts after standardized re-download (~700 treated + ~69k controls)
- **Treatment**: Single clean cohort—first large fire (MTBS ≥1,000 acres) in 2015–2017
  - Cohort g=2016: First fire 2015, 2016, or 2017
  - g=0: Never-treated (no fires 2013–2023, outside 100 km smoke buffer)
  - **Design rationale**: Single non-overlapping window avoids mutual-exclusivity violations of overlapping-cohort staggered DiD
- **Treatment margins**: 
  - Extensive: Binary—any fire ≥1,000 acres in 2015–2017 (primary)
  - Intensive: Burned share (% tract area burned; continuous), fire count, WFP 2012 raster intensity
- **Primary outcomes** (in priority order):
  1. Poverty rate (% population below federal poverty line)
  2. Median household income (nominal, 2020 dollars)
  3. Net-migration rate proxy: in-migration rate = (total − same house 1 yr ago) / total, from B07003 **[descriptive decomposition]**
  4. Employment rate (B84AD / B84AC: civilian employed / civilian labor force 16+)
- **Control group**: Never-treated (no fires 2013–2023, outside 100 km smoke buffer), balanced on raster-based matching covariates
- **Matching strategy**: Propensity-score inverse-probability weights (PS-IPW) on:
  - **Raster-based WFP 2012 summaries** (270m resolution, predetermined): Mean WFP percentile, % area per hazard quintile, distance to high-hazard pixel
  - Pre-2013 fire history (any large fire 1984–2012, log acres burned)
  - Pre-treatment baseline covariates (2012 ACS tract-level: poverty, income, demographics; county-level RUCC; population)
- **Data sources**: ACS (IPUMS, tract-level), MTBS fire perimeters, USFS WFP 2012 (270m raster; primary matching), BEA (annual, merged to tract via county)

---

## Data Sources & Known Quirks

### ACS (via IPUMS) — Critical: Rural Data Quality & Temporal Structure
- **ACS 5-year estimates ONLY** (for tract-level, rural-focused study)
  - 5-year estimates essential for rural geographic reliability
  - ACS 3-year and 1-year estimates are unreliable for rural tracts; DO NOT use even for robustness
  - Majority of fires occur in rural areas; 5-year sampling provides valid estimates despite larger MOE
- **Approved ACS periods** (event-study design with robust pre-trend testing and long-run effects): 2010 (2006–2010), 2012 (2008–2012), 2014 (2010–2014), 2022 (2018–2022), 2023 (2019–2023), 2024 (2020–2024)
  - **Pre-treatment periods**: h ∈ {−3, −2, −1}
    - 2010 ACS = h=−3 (4–5 years pre-fire); **auxiliary** pre-trend check only — uses 2000-vintage tract boundaries, differs from 2012/2014; treat as appendix robustness, not primary pre-trend test
    - 2012 ACS = h=−2 (3–4 years pre-fire); **primary** pre-trend test (2010 boundaries)
    - 2014 ACS = h=−1 (1–4 years pre-fire); reference period for event study (2010 boundaries)
  - **Post-treatment periods**: h ∈ {0, +1, +2}
    - 2022 ACS = h=0 (1–4 years post-fire); medium-run effect
    - 2023 ACS = h=+1 (2–6 years post-fire); medium-run effect
    - 2024 ACS = h=+2 (3–7 years post-fire); long-run effect
  - **Advantage**: Three pre-periods robustly test parallel trends; three post-periods document trajectory (fade vs. persist)
  - Note: Window overlaps (2010/2012/2014 share portions; 2022/2023/2024 share portions) are standard and allow trajectory estimation
  - Do not substitute with 2017 ACS (2013–2017 window contaminated by fires 2015–2017)
- **MOE screening for rural validity**: Drop tracts if poverty denominator (AX7AA + AX7AB) < 100. Flag but retain tracts where poverty count MOE > 30% of count (tract-level ACS poverty counts typically have MOE ~50% of count; a hard 30% drop threshold removes ~90% of tracts and systematically excludes rural areas). Report flagged share by RUCC; use as robustness check.
- **Poverty and income**: Standard Census definitions. Account for top-coding of income (≈$250k+); flag prevalence by cell.
- **Net migration**: ACS "residence 5 years ago" (available at tract level). Use 5-year window (matches ACS estimate period and fire-effect timescale). Interpret as net migration proxy; cannot separately identify gross in vs. out flows. More noise in rural tracts (sparse populations).

### Fire Data (Reuse from wildfire-finance)
- **MTBS** (Monitoring Trends in Burn Severity): 1984–2022 fires, nationwide. Minimum threshold 1,000 acres nationwide (conservative for this tract-level study; robustness test at 500 acres).
- **WFP 2012** (primary matching variable): USFS Wildfire Potential, finalized before 2013 fire season. **Predetermined** for fires from 2013 onward. **Native 270m resolution (ESRI Grid, EPSG:5070)**. **CRITICAL: Do NOT aggregate to county/tract boundaries. Instead, extract 270m pixels and compute tract-level summaries**:
  - Mean WFP 2012 percentile (0–100) across pixels intersecting tract
  - % tract area in each WFP hazard quintile (0–20, 20–40, 40–60, 60–80, 80–100)
  - Distance from tract centroid to nearest pixel with WFP > 75th percentile
  - These tract-level summaries serve as matching covariates in PS-IPW model.
  - Use `rasterio`, `geopandas` for spatial operations.
  - Obtain from wildfire-finance: `wildfire-finance/data/raw/WHP/Data/wfp_2012_continuous/`.
- **WHP 2014** (robustness only): NOT predetermined for 2013–2014 fires. Use for sensitivity checks only.
- **Smoke spillover exclusion**: Baseline 100 km buffer around MTBS fire perimeters. Exclude tracts within buffer from control group. Vary 50 km, 150 km in robustness. Rationale: proxy for smoke transport; tract-level buffering more precise than county-level.
- **Fire-tract intersection**: Spatial join MTBS perimeters with tract boundaries; compute % tract area within fire polygon (supports dose-response analysis).
- **Fire perimeters**: Reuse MTBS data from wildfire-finance: `wildfire-finance/data/raw/mtbs_perims/`. If not available, download from USGS MTBS website.

### Economic Data
- **BEA per-capita income** (annual): Alternative income measure; available from FRED API. Use single-year value closest to ACS estimate window (linear interpolation if needed).
- **USDA NASS agricultural employment**: Optional for robustness (sector heterogeneity); secondary priority.

---

## Development Workflow

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install core packages
pip install -e .
```

### Standard Commands

| Task | Command |
|------|---------|
| Run analysis pipeline | `python -m src.main` |
| Run unit tests | `pytest tests/ -v` |
| Run specific test | `pytest tests/test_data.py::test_function_name -v` |
| Lint code | `ruff check src/ tests/` |
| Format code | `ruff format src/ tests/` |
| Build data | `python -m src.data.build_analysis_dataset` |
| Run DiD estimation | `python -m src.estimation.did_estimation` |
| Generate tables/figures | `python -m src.output.tables_and_figures` |

---

## Code Architecture

See RESEARCH_PLAN.md §7 for full folder structure. Summary:

```
wildfire-poverty-analysis/
├── data/                      # Raw and processed data (git-ignored)
│   ├── raw/                   # Original downloads
│   ├── processed/             # Analysis-ready parquets
│   └── metadata/              # Data dictionaries
├── code/                      # (Not src/ — following wildfire-finance convention)
│   ├── 01_build/              # Data assembly (Python/R)
│   ├── 02_matching/           # PS-IPW matching (R)
│   ├── 03_analysis/           # DiD estimation and robustness (R)
│   ├── 04_output/             # Tables and figures
│   └── main.py                # Pipeline orchestration
├── tests/                     # Unit tests (pytest)
├── notebooks/                 # EDA and exploration (Jupyter)
├── results/                   # Output (tables, figures, RDS objects)
├── docs/                      # Documentation (Markdown)
├── .gitignore                 # Exclude data/raw, .rds, .RData, .pyc
├── setup.py
├── requirements.txt           # Python + R dependencies
├── CLAUDE.md (this file)
└── RESEARCH_PLAN.md           # Full research plan
```

### Key Modules

**`src/data/`**: Data loading and preprocessing
- All functions assume clean environment; no hardcoded paths.
- Use relative paths (resolve via `pathlib.Path`).
- Output intermediate datasets with descriptive names (e.g., `acs_2000_2020_county_clean.parquet`).
- Flag data quality issues (missingness, TopCode) at load time.

**`src/estimation/`**: Econometric models
- Callaway & Sant'Anna (2021) staggered DiD via `csdid` Python port or R via `did` package.
- Always check pre-trends explicitly. Flag significant deviations and justify via Roth (2022) framework.
- Report Sun & Abraham (2021) heterogeneity-robust estimates as robustness check.
- Main estimating equation to be specified upfront in display math in code docstrings.

**`src/output/`**: Publication-ready tables and figures
- All output at 300 DPI.
- Table notes must include: data source, sample restrictions, standard error clustering.
- Follow AER Data and Code Disclosure standards.

---

## Methodological Defaults

### Difference-in-Differences: Event-Study with Single Cohort
- **Estimating equation**: $Y_{i,t} = \alpha_i + \lambda_t + \sum_{h=-3}^{2} \beta_h \cdot \text{Treated}_i \cdot \mathbb{1}[t = h] + X_i \gamma + \varepsilon_{i,t}$
  - h = {-3, -2, -1, 0, +1, +2} corresponds to ACS {2010, 2012, 2014, 2022, 2023, 2024}
  - h = -1 (ACS 2014) is the reference period (coefficient normalized to zero)
  - h ∈ {-3, -2} (ACS 2010, 2012) provide **robust pre-trend tests** (two independent tests of parallel trends). ACS 2010 (2006–2010 window) substitutes for unavailable 2005–2009
  - h ∈ {0, +1, +2} (ACS 2022, 2023, 2024) document trajectory: fade, persist, or amplify
- **Pre-trend testing** (Roth 2022 framework):
  - Report β₋₃ and β₋₂ with 95% CIs; do NOT report p-values
  - Both β₋₃ ≈ 0 and β₋₂ ≈ 0 combined with visual parallel trends provides very strong support for parallel trends assumption
  - Can formally test H₀: β₋₃ = β₋₂ = 0 (flat pre-trend)
  - Falsification test: Assign fires to pre-2013 years; expect ATT ≈ 0
- **Aggregate ATT**: Simple average of post-treatment effects β₀, β₊₁, and β₊₂; report bootstrap CIs (1,000 reps)
- **Confidence intervals**: Clustered by county; single cohort eliminates cross-cohort heterogeneity concerns

### Propensity-Score Matching (PS-IPW)
- **Matching variables**: WFP 2012 quintile + pre-2013 fire history (acres burned log) + baseline covariates (2014 ACS: poverty, income, demographics, population) + RUCC code
  - Note: 2014 ACS is used for baseline covariates (closest pre-treatment ACS period before 2015 fires begin)
- **Method**: Logistic propensity score; inverse-probability weights: w=1 for treated, w=ê/(1−ê) for controls
- **Trimming**: 99th percentile of weights to stabilize variance
- **Balance diagnostics**:
  - Standardized mean differences (SMD) before and after: target SMD < 0.1 all covariates
  - Report effective sample size (ESS) of reweighted control group
  - Density plots: propensity score distributions (treated vs. control) before/after reweighting
- **Regression adjustment** (in event-study estimation): Include WFP quintile and baseline covariates as additional covariates in the DiD model

### Robustness: Organized by Identification Threat
**NOT** by test type. See RESEARCH_PLAN.md §4.4 for full specification:
- **Selection bias**: Placebo test (fires 2007–2012 → ATT ≈ 0?), balance diagnostics post-IPW
- **Smoke spillover**: Vary geographic exclusion radius (50, 100, 150 km)
- **Fire definition**: Vary MTBS minimum acres (500, 1,000, 2,000)
- **Specification**: Event-study window variations, regional FE changes
- **Estimator**: Sun-Abraham (2021), Two-Stage DiD
- **Sample**: Exclude pre-2013 fire counties (stricter never-treated definition)

---

## Writing & Output

**Target style**: *Journal of Urban Economics*, *Regional Science and Urban Economics*, or *AEJ: Applied* — precise, parsimonious, evidence-driven.

### Paper Structure (when drafting)
See RESEARCH_PLAN.md §5 for detailed breakdown. Summary:
1. **Introduction** (2–3 pp): Hook (wildfire frequency ↑), gap (distributional effects unknown), RQ, contribution (national scope + migration mechanism), lit (4–5 papers)
2. **Data & Sample** (1–2 pp): Sample frame, treatment definition (extensive + intensive margins), outcomes, summary statistics (pre-IPW and post-IPW balance)
3. **Empirical Strategy** (2–2.5 pp): Identifying variation, estimand (ATT), main equations, threats + mitigations
4. **Results** (3–4 pp): Event-study plot (poverty), ATT tables, extensive vs. intensive margin, mediation analysis (net migration)
5. **Robustness** (2–2.5 pp): Organized by threat, not test type; ≥6 specs tabulated
6. **Discussion & Limitations** (1.5–2 pp): Mechanism interpretation (income loss vs. compositional), scope (MTBS >1000 acres), open questions
7. **Conclusion** (0.5 pp): Restate finding, hedged policy implication, no new results

### Table/Figure Guidelines
- **Publication-ready by default**: 300 DPI for figures, LaTeX for tables
- **Table notes**: Data source, sample restrictions (e.g., "National lower-48 counties, 2007–2022 ACS 5-year estimates, never-treated controls"), SE clustering ("clustered by county")
- **All equations**: Numbered and in display math; define all variables at first use
- **Event-study plot**: Clear labels on x-axis (relative year h = -3 to +7), y-axis (coefficient + 95% CIs); highlight h=0 (treatment year); shade pre-trends region (h<0)

---

## Reproducibility

- All code assumes clean environment. Use `requirements.txt` for dependencies.
- Seed all random processes.
- Use relative paths; resolve via `pathlib`.
- Output intermediate datasets with descriptive names.
- Document all sample restrictions and definitions in data module docstrings.

---

## Things to Never Do

- Do not invent p-values, coefficients, or fire-poverty linkages.
- Do not silence data warnings (missing values, TopCode, disclosure avoidance).
- Do not proceed past a methodological uncertainty without flagging it explicitly.
- Do not default to OLS when staggered DiD design requires Callaway & Sant'Anna.
- Do not produce LaTeX that does not compile.
- Do not force Python solutions for tasks better suited to R (e.g., `did` package) — flag and provide R code instead.

---

## Literature Positioning

**Key papers**:
- Callaway & Sant'Anna (2021): Staggered DiD methodology
- Roth (2022): Pre-testing critique
- Sun & Abraham (2021): Heterogeneity-robust estimators
- MTBS & fire ecology: Summarize research on fire mechanisms → poverty pathways

**Contribution framing**: [To be populated as lit review completes]

---

## Skill Sequence (Research Execution Pipeline)

**Before data analysis (Weeks 0–1)**:
1. **`/deep-research`** (lit-review mode, 2–3 hours)
   - RQ: "How do wildfires causally affect local economies, poverty, and population migration? What are the identified mechanisms?"
   - Scope: Wildfire economics, poverty/income literature, environmental shocks & displacement, migration econometrics, DiD methodology
   - Output: Annotated bibliography, mechanism framing, lit positioning for paper Introduction

**After estimation (Weeks 8–9)**:
2. **`/academic-paper`** (full mode, economics config)
   - Scaffold: Use findings from `/deep-research`; start with Introduction template; empirical strategy template (from §3, RESEARCH_PLAN.md)
   - Config: Journal = JUE/RSUE; citation = Chicago author-date; output = LaTeX
   - Outcome: Full manuscript draft (all 7 sections) with results embedded

**After draft (Week 9+)**:
3. **`/academic-paper-reviewer`** (multi-perspective review)
   - Simulate 5 reviewers: EIC, Identification/Causal specialist, Data quality specialist, Economics mechanism specialist, Devil's Advocate
   - Peer 1 focus: Parallel trends assumption, selection bias, alternative explanations
   - Peer 2 focus: ACS measurement error, sample representativeness, disclosure avoidance handling
   - Peer 3 focus: Economic significance, magnitude interpretation, policy relevance
   - Output: Structured feedback; revise manuscript

**If heavy iteration needed (optional)**:
4. **`/academic-pipeline`** (end-to-end orchestration)
   - Full workflow: deep-research → write → review → revise → re-review → finalize
   - Use if ≥2 revision rounds expected
