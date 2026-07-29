# Week 2: Estimation Progress Update

**Date**: 2026-07-28  
**Status**: Phases 1-2 Complete; Ready for Phases 3-6

---

## **Completed Milestones**

### **Phase 1: Propensity-Score IPW Matching** ✅
**Output**: `data/processed/ipw_weights.parquet`

- **Propensity score model**: Logit on WFP quintile, baseline poverty/income, pre-2012 fires
- **Covariate balance (SMD)**:
  - Baseline poverty: -0.126 → -0.018 ✓
  - Baseline income: -0.104 → -0.086 ✓
  - Pre-2012 fires: 0.000 → 0.000 ✓
  - WFP quintile: 0.067 → -0.014 ✓
- **All SMD < 0.1** post-IPW ✅
- **Effective sample size**: 90 / 92 controls

### **Phase 2: Main DiD Estimation** ✅
**Output**: `results/tables/main_att_estimates.csv`

| Outcome | ATT | 95% CI | N |
|---------|-----|--------|---|
| Poverty rate | 0.45 pp | [-1.86, 2.75] | 158 |
| Median income | -$864 | [-$3,957, $2,228] | 158 |
| Employment rate | -0.12 pp | [-1.91, 1.68] | 158 |
| Net migration | -1.61 pp | [-3.33, 0.11] | 158 |

**Key findings**:
- Poverty effect: +0.45 pp, but CI includes zero (not significant at α=0.05)
- Income effect: -$864, but CI includes zero
- Migration effect: -1.61 pp (marginally significant; CI nearly excludes zero)
- Interpretation: Small sample (n=158, 2 periods) limits power

---

## **Next Steps: Phases 3-6** 🚧

### **Phase 3: Pre-trend Testing**
- Estimate DiD separately for each pre-treatment period (1990, 2000, 2007-2011)
- Visualize: Should be flat pre-treatment, jump post-treatment
- Report: Point estimates + 95% CIs (not p-values, per Roth 2022)

### **Phase 4: Mediation Analysis**
- Decompose poverty ATT via net migration
- Direct vs. indirect effects
- % mediation calculation

### **Phase 5: Robustness Checks** (5+ specs)
- Smoke buffer radius: 50, 100, 150 km
- Fire size threshold: 500, 1000, 2000 acres
- Regional FE variations
- Alternative matching (CEM)
- Sun-Abraham estimator

### **Phase 6: Heterogeneous Effects**
- Subgroup analysis: by region, baseline poverty, fire frequency
- Exploratory (low power)

---

## **Technical Notes**

**Sample constraints**:
- Total N = 158 (79 counties, 2 periods)
- Treated = 66 obs; Control = 92 obs
- Very small for precise estimation
- Large CIs reflect limited sample size

**Estimation approach**:
- Two-way FE (county + year) with IPW weights
- County-clustered SEs
- Trimmed IPW at 99th percentile

**PS model regularization**:
- L2 regularization (C=0.1) for numerical stability
- Standardized covariates to avoid singularity
- 4 covariates: WFP, poverty, income, pre-2012 fires

---

## **Scripts Created**

- `code/02_matching/01_ps_matching.py` — IPW weights + balance diagnostics
- `code/03_analysis/01_cs_main.py` — Two-way FE DiD with IPW

Both scripts are **Python-based** (R not available in environment).

---

## **Data Flow**

```
analysis_sample_final.parquet (Week 1 output)
    ↓
01_ps_matching.py
    ↓ ipw_weights.parquet
01_cs_main.py
    ↓ main_att_estimates.csv
[Next: Pre-trends, mediation, robustness]
```

---

## **Expected Workflow for Remaining Phases**

| Phase | Script | Est. Time | Blockers |
|-------|--------|-----------|----------|
| 3 (pre-trends) | `02_pretend_testing.py` | ~1 hr | Task 16 done ✓ |
| 4 (mediation) | `03_mediation.py` | ~1 hr | Task 16 done ✓ |
| 5 (robustness) | `04_robustness.py` | ~2 hr | Tasks 3-4 done ✓ |
| 6 (heterogeneity) | `05_heterogeneity.py` | ~1 hr | Task 16 done ✓ |
| 7 (tables/figs) | Manual `results/` assembly | ~1 hr | Tasks 3-6 done ✓ |
| 8 (docs) | `results_memo.md` | ~30 min | Task 7 done ✓ |
| 9 (git commit) | Parallel execution | ~15 min | Task 8 done ✓ |

Phases 3-6 can run **in parallel after Phase 2 completes**.

---

## **Ready for Phases 3-6**

All pre-requisite data (IPW weights, main DiD) is in place. Next phase scripts can be built and executed in parallel.

**Recommendation**: Proceed with Phase 3 (pre-trend testing) to validate parallel trends assumption before investing in full robustness battery.

---

*Last updated: 2026-07-28*
