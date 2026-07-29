# Week 2: Estimation Pipeline

**Status**: Ready to execute  
**Primary Deliverable**: DiD estimates (ATT), pre-trend tests, robustness checks  
**Timeline**: Weeks 3-4 (concurrent execution possible)

---

## **Overview: 9 Tasks → Publication-Ready Results**

### **Phase 1-4: Core Estimation** (Days 1-3)
1. ✏️ **PS-IPW Matching** — Construct weights, check balance (SMD < 0.1)
2. ✏️ **C&S DiD Main** — Estimate ATT (poverty, income, employment, migration)
3. ✏️ **Pre-trend Testing** — Validate parallel trends (visual, magnitude-based)
4. ✏️ **Mediation Analysis** — Decompose poverty effect via migration

### **Phase 5-6: Robustness & Heterogeneity** (Days 3-4)
5. ✏️ **Robustness Checks** — 5+ specs (smoke buffer radius, fire threshold, regional FE, alternative matching)
6. ✏️ **Subgroup Effects** — By region, baseline poverty, fire frequency (exploratory)

### **Phase 7-9: Publication & Documentation** (Day 5)
7. ✏️ **Tables & Figures** — Summary stats, ATT tables, event-study plots (300 DPI)
8. ✏️ **Results Documentation** — Methods, findings, limitations memo
9. ✏️ **Git Commit** — All code, outputs, documentation

---

## **Methodology: C&S DiD with PS-IPW Matching**

**Main specification**:
$$\text{Outcome}_{c,t} = \alpha_c + \lambda_t + \tau \cdot (\text{early\_treated}_c \times \text{post}_t) + X_{c,\text{pre}} \gamma + \epsilon_{c,t}$$

- **Estimator**: Callaway & Sant'Anna (2021) for staggered treatment
- **Weighting**: Inverse-probability weights from PS logit (WFP quintile + pre-2012 fire history + baseline poverty/income)
- **Outcomes**: Poverty (primary), income, employment, net migration (mediator)
- **Treatment**: Binary indicator (early-treated vs. never-treated controls)
- **SE clustering**: County level; bootstrap 1,000 replications
- **Sample**: 79 counties (66 early-treated, 64 never-treated controls; 2 periods)

**Key validations**:
- Covariate balance post-IPW (SMD < 0.1 for all variables)
- Parallel trends via pre-period coefficients (1990, 2000, 2007-2011)
- No unobserved confounding (conditional on observables)

---

## **Input Data**

**`data/processed/analysis_sample_final.parquet`** (158 obs × 24 cols)
- County × year panel (2 periods: 2007-2011, 2015-2019)
- Outcomes: poverty_rate, median_hh_income, employment_rate, net_migration_rate
- Treatment: early_treated, late_treated flags
- Covariates: baseline poverty/income, WFP quintile, pre-2012 fire count/acres

---

## **Output Structure**

```
results/
├── rds/                              [R model objects]
│   ├── cs_main_results.rds           ← C&S ATT, covariance
│   ├── balance_diagnostics.rds       ← Pre/post-IPW balance
│   ├── robustness_results.rds        ← All robustness specs
│   └── heterogeneity_results.rds     ← Subgroup ATTs
├── tables/                           [Publication-ready]
│   ├── table_1_summary_stats.tex     ← Pre/post-IPW summary
│   ├── table_2_main_att.tex          ← Main DiD results
│   ├── table_3_robustness.tex        ← Robustness specs
│   ├── table_4_heterogeneity.csv     ← Subgroup effects
│   └── balance_table.csv             ← SMD before/after
└── figures/                          [300 DPI]
    ├── figure_1_balance.pdf          ← SMD plot
    ├── figure_2_event_study.pdf      ← Pre-trends & ATT
    └── figure_3_mediation.pdf        ← Direct/indirect effects
```

---

## **Key Methodological Notes**

### **Pre-trend Testing (Roth 2022 critique)**
- Report pre-period coefficients β_{h<0} with 95% CIs
- **Do NOT report p-values** (null tests underpowered)
- Visual assessment: are pre-trends flat and parallel?
- If trends diverge, discuss as robustness sensitivity

### **Parallel Trends Under Selection Bias**
- PS-IPW controls for observed confounding (WFP, baseline poverty)
- Assumes no unmeasured confounding conditional on observables
- Limitations: fire-prone regions may have latent poverty drivers

### **Mediation Analysis (Net Migration)**
- Decompose ATT(poverty) into:
  - Total effect: τ_poverty
  - Indirect (via migration): τ_migration × γ_migration
  - Direct (income loss): τ_poverty − indirect
- Caveat: ACS migration variable is noisy; treat as exploratory

### **Robustness Scope**
- Organized by threat to identification, not by test type
- ≥5 specifications to demonstrate stability:
  1. Smoke buffer radius (50, 100, 150 km)
  2. Fire size threshold (500, 1000, 2000 acres)
  3. Regional fixed effects (state×period, division×period)
  4. Alternative matching (CEM on WFP + poverty bins)
  5. Sun-Abraham (2021) heterogeneity-robust estimator

---

## **Execution Flow**

```
Task 15: PS-IPW Matching
    ↓ outputs: ipw_weights.parquet
Task 16: C&S Main DiD
    ↓ outputs: cs_main_results.rds
    ├→ Task 17: Pre-trend Testing
    ├→ Task 18: Mediation Analysis
    ├→ Task 19: Robustness Checks
    └→ Task 20: Heterogeneity (parallel)
         ↓ all complete
Task 21: Tables & Figures
    ↓ outputs: .tex, .csv, .pdf
Task 22: Documentation
    ↓ outputs: results_memo.md
Task 23: Git Commit
    ↓ all changes committed
```

**Parallel execution**: Tasks 17–20 can run concurrently after Task 16 completes.

---

## **Expected Results** (ballpark)

**Poverty ATT** (primary outcome):
- Expected: +2–4 percentage points (early-treated cohort)
- Interpretation: Wildfire exposure increases poverty rate by 2–4 pp over 5–8 years

**Mediation via Net Migration**:
- Expected: 30–50% indirect effect (compositional)
- Remaining: 50–70% direct effect (income loss)

**Pre-trends**:
- Expected: β_{1990}, β_{2000}, β_{2007-2011} ≈ 0 (flat pre-treatment)
- If violated: Flag as sensitivity concern

**Robustness**:
- ATT stability across smoke buffers & fire thresholds
- Consistent direction (positive poverty effect) across specs

---

## **Success Criteria**

✅ All 4 outcomes estimated with 95% CIs  
✅ Pre-trends visualized and assessed (parallel ?)  
✅ Covariate balance: SMD < 0.1 post-IPW  
✅ ≥5 robustness specs tabulated  
✅ Publication-ready tables & figures (300 DPI, LaTeX)  
✅ All code + results committed to git

---

## **Software & Packages**

**R** (recommended for DiD estimation):
- `did` — Callaway & Sant'Anna (2021)
- `fixest` — TWFE, event-study
- `tidyverse` — Data wrangling
- `modelsummary` — Table output

**Python** (alternative, for robustness plots):
- `pandas`, `numpy` — Data ops
- `matplotlib`, `seaborn` — Figures (300 DPI)

---

## **Deviations from PAP**

Any changes to specifications locked in PAP (treatment window, outcome definitions, matching covariates) must be:
1. **Documented** in results memo
2. **Justified** by reference to data availability or methodological concern
3. **Flagged** in manuscript with amendment notice

Minor deviations (exploratory robustness not pre-registered) are acceptable if labeled exploratory.

---

## **Timeline & Milestones**

| Week | Milestone | Status |
|------|-----------|--------|
| **Week 2** | Core estimation (Tasks 15–20) | Ready |
| **Week 3** | Robustness complete, tables drafted | On track |
| **Week 4** | Writing phase: Intro, Methods, Results | Next |
| **Week 5** | Revision & manuscript finalization | Later |

---

**Ready to begin Week 2.** Task #15 (PS-IPW) next.

*Last updated: 2026-07-28*
