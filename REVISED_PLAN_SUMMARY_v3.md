# Research Plan Update Summary — Version 3.0
**Date**: 2026-06-18  
**Focus**: Simplified design with single treatment cohort; COVID avoidance; enhanced statistical power

---

## Major Changes from v2.0 to v3.0

### 1. **Treatment Window: Staggered (2013–2021) → Single Cohort (2012–2016)**

| Feature | v2.0 | v3.0 |
|---------|------|------|
| Treatment period | 2013–2021 (staggered cohorts: g=2017, g=2022) | 2012–2016 (single cohort) |
| Estimator | Callaway & Sant'Anna (staggered DiD) | Simple difference-in-differences |
| Cohort structure | 2 cohorts (limited power for g=2022) | 1 cohort (full power) |
| Pre-fire observation | Limited (2 pre-periods) | Stronger (2007–2011 baseline) |
| COVID exposure | Risk (2020 ACS included) | **Eliminated** (2016–2019 outcome only) |

**Rationale**: Single cohort with fixed timeline avoids:
- Staggered DiD complexity and limited power
- COVID-2020 confound in outcomes
- Thin pre-trend testing (only 1 lag)

---

### 2. **Analysis Period: 4 Census Periods → 3 ACS Windows (2 Analysis Periods)**

| Feature | v2.0 | v3.0 |
|---------|------|------|
| ACS periods | 2007, 2012, 2017, 2022 (4 obs) | 2007–2011, 2016–2019 (2 obs) |
| Pre-treatment | 2007, 2012 (2 obs) | 2007–2011 (1 pooled period) |
| Post-treatment | 2017, 2022 (2 obs) | 2016–2019 (1 pooled period) |
| Interpretation | Event-study path (dynamic) | Aggregate effect (fixed) |

**Rationale**: 
- Reduces to simple pre-post comparison (cleaner, more powerful)
- ACS 5-year overlap naturally creates 2 quasi-independent periods
- Avoids disclosure avoidance noise in 2020+ ACS

---

### 3. **Estimand & Estimation**

| Feature | v2.0 | v3.0 |
|---------|------|------|
| Estimand | ATT with dynamic adjustment ($\beta_h$ path) | ATT (aggregate effect, pre to post) |
| Model | Event-study: outcome ~ relative year + FE | Simple DID: outcome ~ (treated × post) + FE |
| Pre-trends testing | Event-study $\beta_h$ (h<0) with visual inspect | Covariate balance check (PS-IPW at baseline) |
| Complexity | Moderate (staggered, event-study) | **Low** (standard 2-way FE) |

**Equation (v3.0)**:
$$\text{Outcome}_{c,t} = \alpha_c + \lambda_t + \tau \cdot (\text{treated}_c \times \text{post}_t) + X_{c,\text{pre}} \gamma + \epsilon_{c,t}$$

where $\tau$ = ATT (main coefficient of interest)

---

### 4. **Robustness Tests: Reorganized**

| v2.0 | v3.0 | Rationale |
|------|------|-----------|
| Smoke radius (3 variants) | Smoke radius (3 variants) | Unchanged |
| Fire threshold (500, 1k, 2k acres) | Fire threshold (500, 1k, 2k acres) | Unchanged |
| Event-study window variation | Treatment window timing (2011–2015, 2012–2016, 2013–2017) | Replaced window variation with timing sensitivity (more policy-relevant) |
| Specification (state FE, division FE) | Specification (state FE, division FE) | Unchanged |
| Estimator: Sun-Abraham, Two-Stage DiD | Estimator: CEM matching (alternative to PS-IPW) | Simplified; CEM more interpretable for binary outcome |
| **New**: Placebo (pre-period) | **New**: ACS disclosure avoidance sensitivity | Tests differential privacy impact (2020+) |

---

### 5. **Sample & Power Implications**

| Metric | v2.0 | v3.0 |
|--------|------|------|
| N observations | ~3,100 counties × 4 periods = ~12,400 obs | ~3,100 counties × 2 periods = ~6,200 obs |
| Pre-trend degrees of freedom | Multiple (allows dynamic effects) | Single (pre vs. post only) |
| Treatment events | 2 cohorts with staggered timing | 1 cohort, 5-year window |
| Expected power | Moderate (especially g=2022) | **Strong** (single large cohort) |
| COVID risk | Present (2017, 2022 post-treatment) | **Eliminated** (2016–2019 pre-COVID) |

---

### 6. **Pre-Analysis Plan (PAP) Updates**

**v3.0 PAP Specification Freeze**:
- Treatment cohort: Single (fires 2012–2016)
- Analysis periods: 2007–2011 (pre) vs. 2016–2019 (post)
- Estimand: ATT from simple DID
- Primary outcome: Poverty rate
- Matching: PS-IPW on WFP 2012 quintile, pre-2012 fire history, baseline covariates
- Hypothesis 1: Positive ATT on poverty (magnitude TBD)
- Hypothesis 2: Negative ATT on income (income loss mechanism)
- Hypothesis 3: Positive ATT on net migration (compositional mechanism)
- Hypothesis 4: Dose-response (effects scale with fire frequency/acreage)

---

## Methodological Advantages of v3.0 Design

1. **Simplicity**: Standard 2-way FE vs. staggered DiD complexity
   - Easier to explain, verify, and defend in peer review
   - Cleaner parallel trends interpretation (single pre-post comparison)

2. **Power**: Single large cohort vs. 2 small cohorts
   - All treated counties observed post-fire (no sample loss from late cohort)
   - Larger effective N for treatment group

3. **COVID avoidance**: Outcome in 2016–2019 vs. 2017, 2022
   - Eliminates confound from pandemic economic shocks
   - ACS 2016–2019 period (5-year average) avoids disclosure avoidance noise

4. **Parallel trends**: Balance-based testing vs. formal pre-trend tests
   - Single pre-treatment period makes event-study window moot
   - Rely on PS-IPW balance (SMD < 0.1) for credibility
   - Flagged as limitation; robustness tested via placebo

5. **Mediation mechanism**: Compositional vs. income effects clearly separated
   - Net migration ATT quantifies population displacement
   - Decomposition: indirect (via migration) vs. direct (income) pathways
   - Clearer policy implications

---

## Sample Sizes & Treatment Counts (Estimate)

Assuming:
- ~3,100 lower-48 counties
- ~15% experience fire ≥1,000 acres in 2012–2016
- ~100 km smoke buffer excludes ~5% of never-treated

**Expected**:
- Treated counties: ~450–500
- Never-treated (after smoke exclusion): ~2,600–2,650
- Observations: ~3,100 × 2 periods = 6,200 obs (balanced panel)

---

## Timeline: No Change from v2.0

- **Weeks 1–3**: Data assembly (3 ACS periods instead of 4)
- **Week 4**: PS-IPW matching & balance diagnostics
- **Week 5**: Main DID estimation (all outcomes)
- **Week 6**: Mediation & dose-response analysis
- **Week 7**: Robustness tests (8+ specs)
- **Week 8**: Output tables & figures
- **Weeks 9–10**: Manuscript drafting
- **Weeks 11+**: Peer review & submission

---

## Critical Improvements in v3.0

| Issue from v2.0 | Resolution in v3.0 |
|-----------------|-------------------|
| Staggered DiD complexity | Simple 2-way FE (single cohort) |
| Limited pre-trend testing (2 periods) | Balance-based validation (PS-IPW) + placebo test |
| COVID confound in outcomes | 2016–2019 ACS (pre-COVID) |
| Thin common support (national) | Unchanged; but reduced complexity aids diagnostics |
| Event-study window aspiration (h=-3 to +7) vs. data (h=-1 to +1) | **Eliminated**; aggregate ATT only (no dynamic path) |
| g=2022 limited power | **Eliminated**; single cohort with full 2-period observation |

---

## What Didn't Change

- National lower-48 scope (~3,100 counties)
- PS-IPW matching on WFP 2012 + baseline covariates
- Net-migration mediation analysis (novel mechanism)
- Extensive + intensive margin specifications
- 100 km smoke buffer baseline (robustness: 50, 150 km)
- Target journals (JUE, RSUE, AEJ:Applied)
- Publication-ready output standards (300 DPI, LaTeX tables)

---

## Next Steps (Pre-Analysis)

1. **Finalize PAP** with single-cohort 2012–2016 specification (register on OSF)
2. **Run `/deep-research`** (lit-review mode) for wildfire-poverty mechanisms
3. **Week 1 quick check**: Calculate PS-IPW ESS on subset to validate common support
4. **Data assembly** (Weeks 1–3) for 2007–2011 and 2016–2019 ACS, MTBS treatment, WFP 2012

---

## Status: **READY FOR EXECUTION**

✅ Design coherent (simple, powered, COVID-safe)  
✅ Identification strategy clear (PS-IPW + balance testing)  
✅ Mechanism explicit (net migration mediation)  
✅ Robustness plan concrete (8+ tests organized by threat)  
✅ PAP ready to register  

**Pending**:
- Collaborator sign-off on v3.0 design
- PAP registration
- Literature review via `/deep-research`

---

*End of Summary. v3.0 is a significant simplification that resolves power, COVID, and methodological clarity issues from v2.0.*
