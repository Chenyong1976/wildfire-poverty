# CLAUDE.md — Wildfire-Poverty Analysis Project

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Title**: Wildfire Impact on Poverty and Net Migration: A Census-Tract Study with Fine-Grained Spatial Matching (2013–2021)  
**Status**: Design phase (major revision: county → tract; raster matching at 270m resolution); PAP pending update  
**Research Question**: Do large wildfires reduce household incomes and increase poverty rates in affected US census tracts? What role does population displacement (out-migration) play? How does within-county heterogeneity in fire exposure affect outcomes?  
**Identification Strategy**: Staggered difference-in-differences (Callaway & Sant'Anna 2021) with fine-grained raster-based WFP 2012 propensity-score matching (270m resolution)
**Geographic Scope**: All lower-48 US states (~70,000 census tracts); tract-level resolution (vs. prior county-level design)  
**Spatial Matching**: WFP 2012 Wildfire Hazard Potential at native 270m resolution; tract-level raster summaries (mean WFP percentile, % area per hazard quintile, distance to high-hazard pixels) used as matching covariates
**Treatment Window**: 2013–2021 (MTBS fires ≥1,000 acres; staggered cohorts: g=2017 [fires 2013–2016], g=2022 [fires 2017–2021])  
**Analysis Period**: 2012, 2017, 2022 ACS 5-year estimates (3 periods)
**Statistical Power**: Tract-level design provides ~70,000 geographic units vs. 3,100 counties; expected 40,000–50,000 tracts after MOE/population screening
**Key Innovation**: (1) First study to leverage 270m WHP raster for tract-level treatment/control matching; (2) Mediation analysis on net-migration to decompose poverty effects into income loss vs. population composition changes

---

## Core Design

- **Sample**: All lower-48 US census tracts (~70,000); ACS 5-year tract-level estimates 2012, 2017, 2022 (3 periods); after MOE screening (MOE ≤ 30% poverty) and population ≥ 500: ~40,000–50,000 tracts
- **Treatment**: Staggered—first large fire (MTBS ≥1,000 acres) in treatment window
  - Cohort g=2017: First fire 2013–2016 (post-treatment observed 2017–2021)
  - Cohort g=2022: First fire 2017–2021 (post-treatment observed 2018–2022)
  - g=0: Never-treated (no fires 2013–2021, outside 100 km smoke buffer)
- **Treatment margins**: 
  - Extensive: Binary—any fire ≥1,000 acres in treatment window
  - Intensive: Fire count, total acres burned, WFP 2012 raster intensity (mean WFP percentile per tract)
- **Primary outcomes** (in priority order):
  1. Poverty rate (% population below federal poverty line)
  2. Median household income (nominal, 2019 dollars)
  3. Net-migration rate (% moved in – % moved out, past 5 years) **[mediator]**
  4. Employment rate (% civilian labor force employed)
- **Control group**: Never-treated (no fires 2013–2021, outside 100 km smoke buffer), balanced on raster-based matching covariates
- **Matching strategy (NEW)**: Propensity-score inverse-probability weights (PS-IPW) on:
  - **Raster-based WFP 2012 summaries** (270m resolution): Mean WFP percentile, % area per hazard quintile, distance to high-hazard pixel
  - Pre-2013 fire history (any large fire 1984–2012, log acres burned)
  - Pre-treatment baseline covariates (2012 ACS tract-level: poverty, income, demographics; county-level RUCC; population)
- **Data sources**: ACS (IPUMS, tract-level), MTBS fire perimeters, USFS WFP 2012 (270m raster; primary matching), WHP 2014 (robustness), BEA (annual, merged to tract via county)

---

## Data Sources & Known Quirks

### ACS (via IPUMS) — Critical: Rural Data Quality
- **ACS 5-year estimates ONLY** (for tract-level, rural-focused study)
  - 5-year estimates essential for rural geographic reliability
  - ACS 3-year and 1-year estimates are unreliable for rural tracts; DO NOT use even for robustness
  - Majority of fires occur in rural areas; 5-year sampling provides valid estimates despite larger MOE
- **Approved ACS periods**: 2012 (2008–2012 window), 2017 (2013–2017), 2022 (2018–2022)
  - Do not substitute 3-year or 1-year estimates
  - Acknowledge 5-year temporal resolution limits (pre-fire window ends 4–6 years before fires in g=2017 cohort)
- **MOE screening for rural validity**: Drop tracts if poverty MOE > 30% of point estimate. Report N dropped, broken down by urbanicity. Higher MOE in rural tracts expected; document median MOE by RUCC.
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

### Difference-in-Differences: Callaway & Sant'Anna (2021)
- **Primary estimator**: C&S for staggered treatment with heterogeneous effects; use R package `did::att_gt()`
- **Event-study specification**: $h \in \{-3, -2, -1, 0, 1, \ldots, 7\}$ relative to treatment year; allow effects to vary by time
- **Aggregate ATT**: Simple average of post-treatment $\beta_h$ (h ≥ 0); report bootstrap CIs (1,000 reps)
- **Pre-trend testing** (Roth 2022 critique):
  - Report pre-treatment $\beta_h$ (h < 0) with 95% CIs; do NOT report p-values
  - Assess magnitude visually: Are pre-trends negligible relative to post-treatment effects?
  - If pre-trends notable but parallel (slopes), parallel trends still plausible
  - Falsification test: Assign fires to pre-2013 years; expect ATT ≈ 0
- **Heterogeneous effects**: Report Sun & Abraham (2021) alongside C&S as robustness; no heterogeneity bias implies results robust

### Propensity-Score Matching (PS-IPW)
- **Matching variable**: WFP 2012 quintile (primary) + pre-2013 fire history + baseline covariates (2012 ACS)
- **Method**: Logistic propensity score; inverse-probability weights: w=1 for treated, w=ê/(1−ê) for controls
- **Trimming**: 99th percentile of weights to stabilize variance
- **Balance diagnostics**:
  - Standardized mean differences (SMD) before and after: target SMD < 0.1 all covariates
  - Report effective sample size (ESS) of reweighted control group
  - Density plots: propensity score distributions (treated vs. control) before/after reweighting
- **Regression adjustment** (in C&S estimation): Include WFP quintile and baseline covariates as additional covariates in the DiD model

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
