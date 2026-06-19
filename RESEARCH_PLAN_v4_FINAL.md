# Research Plan: Wildfire Impact on Poverty (v4 — Final)
**Date**: 2026-06-19  
**Key Improvements**: Census data for parallel trends testing (1990, 2000) + narrowed treatment window (2012–2015) + adjusted outcome period (2015–2019 ACS)

---

## 1. Research Question & Motivation

**Primary Question**: How do large wildfires (≥1,000 acres) in 2012–2015 affect poverty rates, incomes, and population migration in US counties by 2015–2019?

**Mechanism Focus**: Do wildfires reduce individual incomes (direct welfare loss) or trigger out-migration of low-income households (compositional effect)? Net migration (from ACS) serves as the mediating mechanism.

**Contribution**: National causal evidence on wildfire-poverty linkage with explicit mechanism decomposition (income vs. displacement).

---

## 2. Identification Strategy

### Design: Simple Difference-in-Differences with Multiple Pre-Treatment Periods

**Treatment**: First large fire (MTBS ≥1,000 acres) in **2012–2015**

**Key feature**: Multiple pre-treatment observations (1990, 2000, 2007–2011) enable **formal parallel trends testing**

**Estimand**: ATT = causal effect of fire on treated counties' outcomes (poverty, income, migration)

**Analysis periods**:
| Period | Data Source | Role |
|--------|-------------|------|
| 1990 | Census | Pre-treatment (parallel trends test) |
| 2000 | Census | Pre-treatment (parallel trends test) |
| 2007–2011 | ACS 5-year | Pre-treatment baseline |
| 2015–2019 | ACS 5-year | Post-treatment outcome (3–8 years post-fire) |

---

## 3. Threats to Identification & Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Selection bias (fire hazard)** | WFP 2012 matching + PS-IPW; pre-2012 fire history controls for baseline exposure |
| **Parallel trends violation** | **THREE pre-treatment periods (1990, 2000, 2007–2011)** allow formal testing for early cohort; all pre-treatment coefficients should ≈ 0 |
| **Outcome contamination (late fires)** | **Separate $\tau_{\text{early}}$ (2012–2015) from $\tau_{\text{late}}$ (2016–2019)**; if $\tau_{\text{late}} \approx 0$, contamination minimal; robustness: exclude late-treated counties |
| **Smoke spillover** | 100 km buffer exclusion (baseline); robustness: 50, 150 km |
| **Regional shocks** | State × period FE + balance-checked covariates |
| **Migration measurement** | ACS residence-change variable measured 2015–2019 aligns with outcome window; flag as exploratory mediation |

---

## 4. Sample & Outcomes

**Sample**: ~3,100 lower-48 counties × 4 periods = ~12,400 observations

**Treatment groups**:
- **Early-treated** (~400–500 counties): fire ≥1,000 acres in 2012–2015
- **Late-treated** (~100–150 counties): fire ≥1,000 acres in 2016–2019 (diagnostic group)

**Never-treated**: ~2,500–2,700 counties (no fires through 2019, outside 100 km smoke buffer)

**Primary outcomes**:
1. Poverty rate (% population below poverty line)
2. Median household income (nominal, 2019$)
3. Net-migration rate (% moved in − % moved out, past 5 years)
4. Employment rate (% labor force employed)

---

## 5. Estimation & Testing

### Main Specification (v4.2: Two-Group DiD with Contamination Diagnostic)

$$\text{Outcome}_{c,t} = \alpha_c + \lambda_t + \tau_{\text{early}} \cdot (\text{Early}_c \times \text{Post}_t) + \tau_{\text{late}} \cdot (\text{Late}_c \times \text{Post}_t) + X_{c,\text{pre}} \gamma + \epsilon_{c,t}$$

where:
- **$\text{Early}_c = 1$** if county has fire ≥1,000 acres in **2012–2015** (clear treatment period)
- **$\text{Late}_c = 1$** if county has fire ≥1,000 acres in **2016–2019** (overlaps outcome window)
- **Reference**: Never-treated counties (no fires through 2019)
- **$\tau_{\text{early}}$** = primary ATT (3–8 years post-fire)
- **$\tau_{\text{late}}$** = diagnostic coefficient (0–3 years post-fire; tests for contamination)

**Why two coefficients?**
- ACS 2015–2019 (5-year average) can be affected by fires occurring 2016–2019
- Fires 2016–2019 are "not-yet-treated" in the outcome period (fires during or after measurement)
- $\tau_{\text{late}}$ reveals whether late fires show immediate effects; if ≈ 0, contamination is minimal

**Estimation details**:
- **County FE** ($\alpha_c$) + **Period FE** ($\lambda_t$: 1990, 2000, 2007–2011, 2015–2019)
- **Weighting**: PS-IPW on WFP 2012, pre-2012 fire history, baseline covariates
- **SE**: Clustered at county; 95% CIs via bootstrap (1,000 reps)

### Parallel Trends Test (Early Cohort Only)

**Three pre-treatment coefficients**: $\tau_{\text{early},1990}, \tau_{\text{early},2000}, \tau_{\text{early},2007-2011}$

**Null**: All pre-treatment coefficients = 0 (no treatment effect before 2015 fires occur)

**Test**: Visualize all five coefficients (three pre + two post). If pre-treatment ≈ 0 and post-treatment ($\tau_{\text{early}}$) jumps significantly, parallel trends supported for early cohort ✓

**Late cohort**: No pre-periods available (fires occur after outcome measurement). Parallel trends untestable; assume conditional on observables via PS-IPW balance.

**If pre-trends diverge for early cohort**: Document as violation in Limitations; sensitivity-test by subgroup or geographic region.

### Mediation Analysis

1. **ATT on poverty** (direct): main DID estimate
2. **ATT on migration** (treatment → mediator): fire effect on out-migration
3. **Migration → poverty** (mediator → outcome): regress poverty on migration, conditional on fire
4. **Indirect effect**: ATT(migration) × coefficient(migration → poverty)
5. **Direct-only**: Total ATT − Indirect

---

## 6. Robustness Checks (9+)

| Test | Rationale |
|------|-----------|
| **Exclude late-treated counties** (2016–2019) | **PRIMARY**: If $\tau_{\text{early}}$ stable, contamination confirmed minimal |
| **Early cohort only** (vs. both cohorts) | Validate that including late cohort doesn't change primary result |
| Smoke radius (50, 100, 150 km) | Spillover sensitivity |
| Fire threshold (500, 1,000, 2,000 acres) | Definitional robustness |
| Treatment window (2011–2014, 2012–2015, 2013–2016) | Timing sensitivity (early cohort) |
| Dose-response (per fire; per 10k acres) | Intensive margin (early cohort) |
| Regional FE variants (state, division) | Regional shock control |
| CEM matching (vs. PS-IPW) | Alternative matching |
| Heterogeneity (region, baseline poverty) | Subgroup effects (early cohort) |

---

## 7. Pre-Analysis Plan (Locked, v4.2)

**Primary Hypothesis** ($\tau_{\text{early}}$): Positive ATT on poverty for 2012–2015 fires (fires increase poverty)
- Expected magnitude: +2 to +5 percentage points
- Window: 3–8 years post-fire (2012–2015 fires measured in 2015–2019 ACS)

**Diagnostic Hypothesis** ($\tau_{\text{late}}$): Near-zero or small ATT on poverty for 2016–2019 fires
- Expected magnitude: ≈ 0 or +0.5 to +1.5 percentage points (if any effect)
- Window: 0–3 years post-fire (concurrent/overlapping with outcome measurement)
- **Interpretation**: If $\tau_{\text{late}}$ small, contamination minimal; $\tau_{\text{early}}$ estimate is credible

**Secondary Hypotheses**:
- **H2a** (early cohort): Negative ATT on income (mechanism: direct income loss)
- **H2b** (early cohort): Positive ATT on net migration (mechanism: out-migration of low-income)
- **H3** (dose-response): Intensive margin effects scale with fire frequency/acreage

**Specification Freeze (v4.2)**:
- **Early treatment**: Any fire ≥1,000 acres in 2012–2015
- **Late treatment**: Any fire ≥1,000 acres in 2016–2019 (diagnostic)
- **Outcome window**: 2015–2019 ACS (5-year average)
- **Pre-periods**: 1990, 2000, 2007–2011 (test parallel trends for early cohort)
- **Estimator**: Two-group DiD with separate coefficients for early and late cohorts
- **Matching**: PS-IPW on WFP 2012, pre-2012 fire history, baseline covariates
- **Deviations from spec**: Flagged explicitly with justification

---

## 8. Timeline

- **Weeks 1–3**: Data assembly (Census 1990, 2000 + ACS 2007–2011, 2015–2019; MTBS treatment; WFP matching)
- **Week 4**: PS-IPW matching & balance diagnostics
- **Week 5**: Main DID estimation (all outcomes, pre-period tests)
- **Week 6**: Mediation + dose-response analysis
- **Week 7**: Robustness checks (8+ specs)
- **Week 8**: Output tables & figures
- **Weeks 9–10**: Manuscript drafting
- **Weeks 11+**: Peer review & submission

---

## 9. Critical Strengths of v4.2 Design

✅ **Formal parallel trends test**: 3 pre-periods (1990, 2000, 2007–2011) definitively test assumption for early cohort

✅ **Contamination diagnostic**: Separate $\tau_{\text{early}}$ and $\tau_{\text{late}}$ makes outcome-window overlap **visible & testable**

✅ **Homogeneous treatment timing (early cohort)**: 2012–2015 fires all adjust 3–8 years before outcome measurement

✅ **COVID avoidance**: 2015–2019 ACS entirely pre-pandemic

✅ **Transparent methodology**: Two coefficients show contamination risk explicitly; reader sees the trade-off

✅ **Simple + powerful**: Two-group DiD (not staggered) is easy to explain; keeps ~500–600 treated units

---

## 10. Remaining Caveats

- **Late cohort parallel trends untestable**: No pre-periods before 2015–2019 outcome window; late-treated results flagged exploratory
- **National scope**: PS-IPW common support must be validated Week 1; if ESS < 100, restrict to Western 8-state
- **Migration measurement**: ACS residence-change is noisy; mediation results should be flagged exploratory
- **Census data availability**: Confirm 1990, 2000 poverty data available at county level (should be; historical decennial)
- **Spatial autocorrelation**: Poverty in adjacent counties correlated; SE clustering at county only; consider robustness check
- **Late-treated sample size**: ~100–150 late-treated counties limits precision of $\tau_{\text{late}}$; interpretation as diagnostic (not primary)

---

## **Status: READY FOR PAP REGISTRATION & EXECUTION (v4.2)**

**v4.2 (Two-Group DiD with Contamination Diagnostic) addresses outcome-window contamination**:
- Separate $\tau_{\text{early}}$ (2012–2015 fires; 3–8 year window) from $\tau_{\text{late}}$ (2016–2019 fires; 0–3 year window)
- Makes contamination risk **visible & testable** rather than hidden
- Retains formal parallel trends testing for early cohort (3 pre-periods)
- Maintains simplicity (two-group DiD, not staggered)

**Key Improvements from v4.0**:
1. ✅ Addresses 2016–2019 fire contamination explicitly
2. ✅ Diagnostic $\tau_{\text{late}}$ tests whether contamination is material
3. ✅ If $\tau_{\text{late}} \approx 0$, primary result ($\tau_{\text{early}}$) is credible
4. ✅ Robustness check: exclude late-treated; confirm $\tau_{\text{early}}$ stable

**Next**: (1) Collaborator sign-off on v4.2, (2) Git repository initialization, (3) PAP registration on OSF, (4) `/deep-research` lit-review, (5) Week 1 ESS validation check

---

*End of v4 Plan.*
