# OSF Pre-Analysis Plan Submission
## Wildfire Incidence and Local Poverty: A National Difference-in-Differences Analysis

**Submission Date**: 2026-06-19  
**Author(s)**: [Your Name], [Collaborators]  
**Project Category**: Economics / Environmental Economics / Applied Microeconomics

---

## **1. Research Question**

How do large wildfires (≥1,000 acres) affect county-level poverty rates, household incomes, and population migration in the United States?

**Mechanism Focus**: Do wildfires reduce individual incomes (direct welfare loss) or trigger out-migration of low-income households (compositional effect)?

---

## **2. Study Design Overview**

**Design Type**: Difference-in-Differences (two-group) with propensity-score inverse-probability weighting

**Identification Strategy**: Variation in wildfire exposure timing (2012–2015 vs. 2016–2019) across US counties, compared to never-treated counties, with formal parallel trends testing across three pre-treatment periods (1990, 2000, 2007–2011).

**Sample**: ~3,100 lower-48 US counties × 4 time periods = ~12,400 observations

---

## **3. Treatment Definition**

### **Early-Treated Cohort (Primary)**
- Counties with first large fire (MTBS ≥1,000 acres) in **2012–2015**
- Expected N: ~400–500 counties
- Observation window: 3–8 years post-fire (2015–2019 outcome measurement)

### **Late-Treated Cohort (Diagnostic)**
- Counties with first large fire (MTBS ≥1,000 acres) in **2016–2019**
- Expected N: ~100–150 counties
- Observation window: 0–3 years post-fire (concurrent with outcome measurement; used to diagnose outcome-window contamination)

### **Never-Treated Control Group**
- Counties with **no fires 2012–2019**
- Outside **100 km smoke buffer** (robustness: 50, 150 km variants)
- Expected N: ~2,500–2,700 counties

---

## **4. Outcomes (Primary & Secondary)**

### **Primary Outcome**
**Poverty Rate**: Percentage of population below federal poverty line
- **Measurement**: ACS 5-year average, 2015–2019
- **Rationale**: Avoids COVID-19 economic shock (2020+); represents 3–8 year adjustment period for early-treated fires

### **Secondary Outcomes**
1. **Median Household Income** (nominal, 2019$)
   - Measurement: ACS 5-year, 2015–2019
   - Tests income loss mechanism

2. **Net Migration Rate** (% moved in − % moved out, past 5 years)
   - Measurement: ACS 5-year, 2015–2019
   - Tests out-migration (compositional) mechanism
   - Flag as exploratory (ACS residence-change variable has measurement noise)

3. **Employment Rate** (% labor force employed)
   - Measurement: ACS 5-year, 2015–2019
   - Secondary outcome (labor market adjustment)

---

## **5. Pre-Treatment Periods (Parallel Trends Testing)**

| Period | Data Source | Role |
|--------|-------------|------|
| 1990 | Decennial Census | Pre-treatment observation; allows trend testing |
| 2000 | Decennial Census | Pre-treatment observation; allows trend testing |
| 2007–2011 | ACS 5-year | Pre-treatment baseline |
| 2015–2019 | ACS 5-year | Post-treatment outcome |

**Key Feature**: Three pre-treatment periods enable formal testing of parallel trends assumption via estimation of pre-period treatment effect coefficients. Under null of no treatment effect before treatment occurs, all three coefficients should ≈ 0.

---

## **6. Main Estimating Equation**

$$\text{Outcome}_{c,t} = \alpha_c + \lambda_t + \tau_{\text{early}} \cdot (\text{Early}_c \times \text{Post}_t) + \tau_{\text{late}} \cdot (\text{Late}_c \times \text{Post}_t) + X_{c,\text{pre}} \gamma + \epsilon_{c,t}$$

where:
- $\text{Outcome}_{c,t}$ = outcome in county $c$ at period $t$
- $\alpha_c$ = county fixed effect
- $\lambda_t$ = period fixed effect (1990, 2000, 2007–2011, 2015–2019)
- $\text{Early}_c$ = 1 if county $c$ has first fire ≥1,000 acres in 2012–2015; 0 otherwise
- $\text{Late}_c$ = 1 if county $c$ has first fire ≥1,000 acres in 2016–2019; 0 otherwise
- $\text{Post}_t$ = 1 if $t \in \{2015\text{-}2019\}$; 0 otherwise
- $X_{c,\text{pre}}$ = pre-treatment covariates (see Section 7)
- $\tau_{\text{early}}$ = ATT for early-treated cohort (primary estimand)
- $\tau_{\text{late}}$ = ATT for late-treated cohort (diagnostic for contamination)

**Estimation Method**: Ordinary least squares (OLS) with propensity-score inverse-probability weights (PS-IPW)

**Standard Errors**: Clustered at county level; 95% confidence intervals via bootstrap (1,000 replications)

---

## **7. Identifying Assumptions & Validation**

### **Assumption 1: Parallel Trends (Early Cohort)**

**Statement**: In the absence of treatment, poverty trends in early-treated and control counties would have followed identical trajectories.

**Testing Strategy**:
- Estimate coefficients $\tau_{\text{early},1990}, \tau_{\text{early},2000}, \tau_{\text{early},2007\text{-}2011}$ for pre-treatment periods
- Under null hypothesis, all three should be statistically zero
- Visualize coefficients across time; slope should be flat pre-treatment, then jump at post-treatment

**If violated**: Document as limitation; perform sensitivity analysis by subgroup (region, baseline poverty level); consider alternative bandwidths or matching specifications

### **Assumption 2: No Unmeasured Confounding (Conditional on Observables)**

**Statement**: After controlling for observed baseline characteristics via propensity-score matching, treatment assignment is independent of potential outcomes.

**Validation Strategy**:
- **PS-IPW Matching**: Construct propensity scores based on:
  - USFS Wildfire Hazard Potential (WHP) 2012 (baseline fire risk)
  - Pre-2012 fire history (fire count, acreage 1990–2012)
  - Baseline covariates: county poverty rate, median income, population density, RUCC classification (2007–2011)
  
- **Covariate Balance Testing**: 
  - Standardized mean difference (SMD) < 0.1 for all covariates (acceptable balance)
  - Compare treated vs. control means pre/post-weighting
  
- **Placebo Test** (secondary):
  - Regress 2007–2011 poverty on 2012–2015 fire occurrence
  - Expect coefficient ≈ 0 (no effect on pre-treatment outcome)
  - If non-zero, suggests time-varying selection bias

### **Assumption 3: No Treatment Interference (Excludability)**

**Statement**: Fires in one county do not affect outcomes in control counties (except via geographic spillover explicitly modeled).

**Mitigation**:
- **Primary Specification**: Exclude all control counties within 100 km smoke buffer of any treated fire perimeter
- **Robustness**: Vary buffer to 50 km and 150 km; confirm results stable

### **Assumption 4: Homogeneous Treatment Timing (Early Cohort)**

**Statement**: All fires in 2012–2015 have sufficient time to affect 2015–2019 outcomes (minimum 3 years adjustment window).

**Mitigation**: 
- Treated fires 2012–2015 have 0–7 year lag before outcome measurement
- Average lag: ~3–5 years (sufficient for income/migration adjustment per disaster literature)
- Robustness: Vary treatment window (2011–2014, 2012–2015, 2013–2016) and confirm robustness

---

## **8. Pre-Specified Hypotheses**

### **Primary Hypothesis (H1): Early Cohort Effect on Poverty**

**Hypothesis**: Wildfires in 2012–2015 increase poverty rates in affected counties by 2026-06-19.

**Estimand**: $\tau_{\text{early}}$ (coefficient on Early × Post)

**Expected Direction**: Positive (poverty increases)

**Expected Magnitude**: +2 to +5 percentage points (based on natural disaster literature: Deryugina 2017 on hurricanes, Sadoff et al. 2020 on floods)

**Statistical Test**: Two-tailed $t$-test; reject null if 95% CI does not include zero

---

### **Diagnostic Hypothesis (H1b): Late Cohort Effect (Contamination Test)**

**Hypothesis**: Wildfires in 2016–2019 show minimal or small effects on 2015–2019 poverty (since fires occur during outcome measurement window).

**Estimand**: $\tau_{\text{late}}$ (coefficient on Late × Post)

**Expected Direction**: Approximately zero or small positive

**Expected Magnitude**: 0 to +1.5 percentage points (0–3 year adjustment window; smaller than early cohort)

**Interpretation**: If $\tau_{\text{late}} \approx 0$ (not statistically significant), outcome-window contamination is minimal and $\tau_{\text{early}}$ estimate is credible. If $\tau_{\text{late}}$ is large and significant, late fires are already affecting outcomes (contamination risk flagged).

**Statistical Test**: Two-tailed $t$-test

---

### **Secondary Hypothesis (H2a): Income Loss Mechanism**

**Hypothesis**: Early-cohort wildfires decrease median household income (direct income loss mechanism).

**Estimand**: $\tau_{\text{early}}$ coefficient when outcome = median household income

**Expected Direction**: Negative (income decreases)

**Expected Magnitude**: $5–15\%$ decline in median income (household-level estimates from disaster literature)

**Statistical Test**: Two-tailed $t$-test

---

### **Secondary Hypothesis (H2b): Out-Migration Mechanism**

**Hypothesis**: Early-cohort wildfires increase net out-migration (compositional mechanism; low-income households leave).

**Estimand**: $\tau_{\text{early}}$ coefficient when outcome = net migration rate

**Expected Direction**: Positive (out-migration increases)

**Expected Magnitude**: +1 to +3 percentage points (similar magnitude to poverty effect; suggests compositional contribution)

**Caveat**: ACS residence-change variable is noisy. Results should be flagged as exploratory; interpret with caution.

**Statistical Test**: Two-tailed $t$-test

---

### **Tertiary Hypothesis (H3): Dose-Response (Intensive Margin)**

**Hypothesis**: Treatment effects scale with fire intensity (count and acreage).

**Estimand**: 
- Per-fire effect: coefficient on (number of fires in 2012–2015)
- Per-acreage effect: coefficient on (10,000 acres burned)

**Expected Direction**: Positive (more fires / more acres → larger poverty increase)

**Statistical Test**: Two-tailed $t$-test; expect dose-response coefficient significant and positive

---

## **9. Robustness Tests (Pre-Specified, 9 Total)**

| Test | Rationale | Key Specification |
|------|-----------|------------------|
| **Exclude late-treated** | Validates contamination diagnostic; confirm $\tau_{\text{early}}$ stable if late-treated removed | Re-estimate early cohort only, drop all 2016–2019-treated counties |
| **Early cohort only** | Confirms late cohort inclusion doesn't alter primary result | Report only Early × Post term; drop Late × Post |
| **Smoke radius (50 km)** | Test spillover sensitivity (narrower buffer) | Re-estimate excluding controls within 50 km of any treated fire |
| **Smoke radius (150 km)** | Test spillover sensitivity (wider buffer) | Re-estimate excluding controls within 150 km |
| **Fire threshold (500 acres)** | Lower definitional threshold | Include fires ≥500 acres (vs. primary ≥1,000) |
| **Fire threshold (2,000 acres)** | Higher definitional threshold | Include fires ≥2,000 acres only |
| **Treatment window (2011–2014)** | Earlier treatment start | Restrict to fires in 2011–2014 |
| **Treatment window (2013–2016)** | Later treatment start | Restrict to fires in 2013–2016 |
| **CEM matching (vs. PS-IPW)** | Alternative matching method | Coarsened exact matching (CEM) instead of PS-IPW; compare balance |

**Decision Rule**: If $\tau_{\text{early}}$ magnitude and significance stable across all robustness tests, main result is robust. Flag any test where coefficient changes >25% or loses significance.

---

## **10. Heterogeneous Treatment Effects (Exploratory)**

Will estimate subgroup effects (pre-specified dimensions):

1. **By Region**: Northeast, Midwest, South, West (expect larger effects in West where wildfires concentrated)
2. **By Baseline Poverty**: Quartiles (expect larger effects in high-poverty counties; cf. climate adaptation literature)
3. **By Population Density**: Urban vs. rural (expect different adjustment mechanisms)
4. **By RUCC Classification**: Metropolitan, non-metro adjacent, non-metro non-adjacent

**Caveat**: These will be reported as exploratory analyses, not primary results. Acknowledge multiple-comparisons issue.

---

## **11. Data & Methods**

### **Data Sources**

| Source | Variable(s) | Years | Level |
|--------|------------|-------|-------|
| Decennial Census (IPUMS) | Poverty rate, income | 1990, 2000 | County |
| ACS 5-year (IPUMS) | Poverty, income, migration, employment | 2007–2011, 2015–2019 | County |
| MTBS (USGS) | Fire perimeters, burn severity | 1990–2019 | Fire-level (aggregated to county) |
| USFS WHP 2012 | Baseline wildfire hazard potential | 2012 | Raster 270m (aggregated to county) |
| CDC WONDER (future extension) | Mortality by cause | 2000–2019 | County |

### **Sample Size & Power**

- **Total counties**: ~3,100 lower-48
- **Early-treated**: ~400–500
- **Late-treated**: ~100–150
- **Never-treated**: ~2,500–2,700
- **Total observations**: ~3,100 × 4 periods = 12,400
- **Expected treatment group**: 500–600 (early + late)

**Power considerations**: Large treatment group size (500+) provides adequate power for 2 pp minimum detectable effect on poverty rates.

---

## **12. Timeline**

- **Weeks 1–3**: Data assembly (Census, ACS, MTBS, WFP)
- **Week 4**: PS-IPW matching & balance diagnostics
- **Week 5**: Main DID estimation & pre-period testing
- **Week 6**: Mediation & dose-response analysis
- **Week 7**: Robustness checks (9 tests)
- **Week 8**: Output tables & figures
- **Weeks 9–10**: Manuscript drafting
- **Weeks 11+**: Peer review & submission

---

## **13. Key Specification Decisions (Locked)**

✅ **Treatment**: First fire ≥1,000 acres in 2012–2015 (early) or 2016–2019 (late)  
✅ **Outcome Period**: 2015–2019 ACS (avoids COVID; 3–8 year post-fire window)  
✅ **Pre-periods**: 1990, 2000, 2007–2011 (enables parallel trends test)  
✅ **Matching**: PS-IPW on WFP 2012 + pre-2012 fire history + baseline covariates  
✅ **Primary estimand**: $\tau_{\text{early}}$ (ATT for early-treated cohort)  
✅ **Diagnostic**: $\tau_{\text{late}}$ (tests outcome-window contamination)  
✅ **Deviations from PAP**: Any deviation will be flagged and justified in manuscript  

---

## **14. Deviations & Contingencies**

### **Contingency 1: Effective Sample Size (ESS) < 100 After PS-IPW**
- **Trigger**: ESS drops below 100 due to thin common support (national scope)
- **Response**: Restrict analysis to Western 8-state subsample (CA, OR, WA, ID, MT, NV, AZ, NM)
- **Implication**: Reduces external validity but maintains causal identification

### **Contingency 2: Parallel Trends Violated (Pre-period coefficients non-zero)**
- **Trigger**: Pre-treatment coefficients significantly differ from zero; visual inspection shows diverging trends
- **Response**: Perform sensitivity analysis by subgroup; consider alternative specifications (e.g., state × time FE)
- **Implication**: Acknowledge threat to identification; report in Limitations

### **Contingency 3: Data Unavailable (Census 1990/2000 county-level poverty)**
- **Trigger**: Historical Census poverty data not accessible at county level
- **Response**: Use 2007–2011 ACS as only pre-period; acknowledge parallel trends less formally testable
- **Implication**: Weaker causal inference; rely on PS-IPW balance as primary validation

### **Contingency 4: Late-Cohort Treatment Overlap with Early**
- **Trigger**: Some counties have fires in both 2012–2015 and 2016–2019
- **Response**: Classify by FIRST fire date; assign to early or late cohort (never both)
- **Implication**: Maintains cleanly separated cohorts

---

## **15. Code & Reproducibility**

- **Language**: Python (pandas, statsmodels, numpy)
- **Workflow**: Data assembly → matching → estimation → robustness → output
- **Intermediate outputs**: All datasets saved with descriptive names and codebooks
- **Replication**: Code & data will be published on Zenodo + GitHub upon manuscript acceptance
- **Seed**: All random processes seeded for reproducibility

---

## **16. Acknowledgments & Conflict of Interest**

- **Funding**: [Specify if applicable]
- **Conflicts**: [Specify if applicable]
- **Data Availability**: All data sources are publicly available (Census, ACS, MTBS, WFP, USGS)

---

## **References**

Boomhower, J. (2019). Drilling and disaster: How governments manage risk in the petroleum industry. *American Economic Review*, 109(8), 2842–2882.

Deryugina, T. (2017). The fiscal impact of hurricanes: Disasters don't discriminate, but disaster relief might. *Administrative Science Quarterly*, 62(3), 728–759.

Hornbeck, R., & Donovan, B. (2016). Long-run effects of infrastructure: Evidence from the U.S. Interstate Highway System. *Journal of Urban Economics*, 92, 1–17.

Sadoff, C. W., Hall, J. W., Grey, D., et al. (2020). Water and sustainable development. *Nature Sustainability*, 2(1), 26–36.

---

**PAP Version**: v4.2  
**Registration Date**: 2026-06-19  
**Status**: LOCKED — No modifications to specifications without justification

---

*End of OSF PAP Submission*
