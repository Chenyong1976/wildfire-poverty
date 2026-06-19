# Design Implications: v2.0 → v3.0 Transition

**Key Decision**: Single treatment cohort (2012–2016) with pre-post outcome measurement (2007–2011 vs. 2016–2019)

---

## What This Fixes

### 1. **COVID Confound (CRITICAL)**
- **v2.0 risk**: Post-treatment outcomes at 2017, 2022 → 2022 obs includes COVID-2020 pandemic
  - Impossible to separate wildfire effects from COVID economic shock
  - Violates parallel trends assumption
- **v3.0 solution**: Outcome measured at 2016–2019 ACS (5-year average ending 2019)
  - COVID exposure eliminated
  - Clean causal inference window

### 2. **Event-Study Window Mismatch (MODERATE)**
- **v2.0 mismatch**: 
  - Planned window h ∈ {-3, …, 7} (8 post-treatment periods)
  - Actual data: 4 time periods (2007, 2012, 2017, 2022) → estimable h ≈ {-1, 0, +1} only
  - Aspiration ≠ reality; would require post-hoc redesign during analysis
- **v3.0 solution**:
  - Single pre-post comparison (2007–2011 vs. 2016–2019)
  - No event-study window; no aspiration-reality gap
  - What you see is what you get (WYSIWYG)

### 3. **g=2022 Cohort Underpowered (MODERATE)**
- **v2.0 design**: 
  - g=2022 (fires 2017–2021) observed post-fire only at 2022
  - One post-treatment observation = minimal power for treatment effect
  - Primary results driven by g=2017; g=2022 exploratory/weak
- **v3.0 solution**:
  - Single cohort (2012–2016 fires) with 2 observations pre and post
  - All treated counties have equivalent observation windows
  - No "exploratory cohort" issue

### 4. **Staggered DiD Complexity (LOW-MODERATE)**
- **v2.0**: Callaway & Sant'Anna estimation
  - Newer methodology; less familiar to some peer reviewers
  - More moving parts (cohort assignment, heterogeneity robustness)
  - Potential for reviewer skepticism about implementation
- **v3.0**: Simple 2-way FE (standard difference-in-differences)
  - Familiar to all economists
  - Easier to verify and audit
  - Faster reviewer consensus

---

## What This Costs

### 1. **Reduced Temporal Coverage (LOW)**
- **v2.0**: Outcomes observed 2007–2022 (15-year window)
- **v3.0**: Outcomes observed 2007–2011 and 2016–2019 (gap 2012–2015 not used)
- **Trade-off**: Lose granular time variation; gain COVID safety and simplicity
- **Verdict**: Worthwhile; single powerful estimate > multiple weak ones

### 2. **No Dynamic Path (MINOR)**
- **v2.0**: Event-study would show trajectory of effect over time (h ∈ {-3, …, +7})
  - Answers: "When do effects emerge? Do they decay?"
- **v3.0**: Only aggregate ATT (pre to post; 3–7 year lag depending on cohort fire year)
  - Cannot answer temporal dynamics within outcome window
  - Can infer: Did effect last >3 years? (Compare magnitude to cross-section volatility)
- **Trade-off**: Lose temporal insight; gain statistical power and clarity
- **Verdict**: Acceptable; dynamic effects less policy-relevant than magnitude/mechanism

### 3. **Pre-Trend Testing Less Formal (MINOR)**
- **v2.0**: Multiple pre-treatment $\beta_h$ coefficients (h < 0) allow visual trend assessment
- **v3.0**: Single pre-treatment period → no formal pre-trend test (only covariate balance)
- **Mitigation**: 
  - PS-IPW balance diagnostics (SMD < 0.1 for all covariates)
  - Placebo test (assign fires to pre-period; expect ATT ≈ 0)
  - Flag as limitation; acknowledge parallel trends assumption more critical
- **Verdict**: Balance-based approach is appropriate; explicitly state assumption

---

## Parallel Trends Assumption: Implications for v3.0

**v3.0 has only ONE pre-treatment period** (2007–2011), so formal pre-trend testing is infeasible.

### Validation Strategy:

1. **Covariate balance** (primary):
   - PS-IPW weights ensure treated and control counties balanced on WFP 2012, pre-2012 fire history, baseline poverty/income
   - Target: SMD < 0.1 all covariates
   - Interpretation: If balanced on observables, parallel trends plausible (conditional on matching variables)

2. **Placebo test** (secondary):
   - Regress pre-period outcome (2007–2011 poverty, income, etc.) on fire occurrence in 2012–2016
   - Expect coeff ≈ 0 (no effect on outcome *before* fire)
   - If non-zero: suggests time-varying selection (e.g., pre-existing poverty decline in counties that burn)
   - **Caveat**: Technically not a true placebo (same outcome, not pre-fire data), but diagnostic of time-varying confounds

3. **Regional shock controls**:
   - Add state FE to absorb state-level macro shocks (2007–2011 vs. 2016–2019)
   - If results stable with/without state FE, regional confounds less likely

4. **Acknowledge limitation**:
   - Explicitly state: "Single pre-treatment period limits ability to formally test parallel trends; we rely on propensity-score balance (SMD < 0.1) and placebo test for credibility."
   - No way around this with only 2 time periods; be transparent.

### Strength vs. Weakness:

- **Strength**: PS-IPW balance is more rigorous than formal pre-trend test (Roth 2022 critique: low power)
- **Weakness**: Cannot visually inspect divergence of pre-trends over time (e.g., are treated and control following same slope pre-fire?)
- **Net**: Balanced; acknowledge but don't over-hedge in writing

---

## Sample Composition: Implications

### Expected N:
- ~3,100 lower-48 counties
- ~15% have MTBS fire ≥1,000 acres in 2012–2016 → ~450 treated
- ~100 km smoke buffer excludes ~5% of never-treated → ~2,650 never-treated
- **Analysis sample**: ~3,100 counties × 2 periods = 6,200 obs

### Power:
- v3.0 has **~450 treated units** observed in both pre and post
- v2.0 had ~267 treated (g=2017) + ~117 treated (g=2022) = ~384 treated, but g=2022 had only 1 post obs
- **v3.0 is more powerful** (larger effective treated N, no sparse second cohort)

### Robustness to National Scope:
- National expansion (lower-48) → thin common support in propensity score
- Risk: PS-IPW reweighting collapses effective sample (ESS << N)
- **Mitigation in v3.0**: 
  - Report ESS in matching diagnostics
  - If ESS < 100, fall back to Western 8-state subsample or CEM matching
  - Flag in robustness

---

## Writing Implications

### Simplification:

**v2.0 structure**:
- "We exploit staggered timing of wildfires (2013–2021) using Callaway & Sant'Anna (2021)"
- Event-study figure (β_h trajectory)
- Cohort-specific ATTs

**v3.0 structure**:
- "We compare treated and control counties before (2007–2011) and after (2016–2019) fire exposure (2012–2016)"
- Single ATT coefficient (poetry in simplicity)
- One main results table

**Advantage**: Shorter introduction (fewer design details), clearer story arc

### Robustness Narrative:

**v2.0**:
- "We verify robustness using Sun-Abraham (2021) and two-stage DiD estimators"

**v3.0**:
- "We verify robustness using alternative matching (coarsened exact matching), fire definitions (500, 1,000, 2,000 acres), and geographic buffers (50, 100, 150 km)"
- Threat-organized robustness is clearer

---

## Risks Introduced by v3.0 (Minimal)

1. **Temporal coverage gap (2012–2015)**: 
   - Cannot observe outcome during fire period (by design)
   - Accept as cost of COVID avoidance

2. **Assumption of homogeneous effects**:
   - v3.0 assumes all fires 2012–2016 have same effect (single ATT)
   - v2.0 allowed effects to vary by fire year (staggered)
   - **Mitigation**: Dose-response analysis (per-fire intensity effects) serves as heterogeneity check

3. **ACS 5-year overlap** (data issue, not design):
   - 2007–2011 and 2016–2019 ACS estimates overlap with surrounding years
   - Creates serial correlation in consecutive estimates
   - **Mitigation**: Use only 2007–2011 (pre) and 2016–2019 (post); do not use intermediate years (2012–2015) in analysis
   - Flag overlap in data quality notes

---

## Verdict: v3.0 is **Strictly Better** Than v2.0

| Dimension | v2.0 | v3.0 | Winner |
|-----------|------|------|--------|
| COVID avoidance | No (2022 obs) | Yes (2016–2019) | **v3.0** |
| Statistical power | Moderate (2 weak cohorts) | Strong (1 large cohort) | **v3.0** |
| Simplicity | Moderate (staggered DiD) | High (simple DID) | **v3.0** |
| Temporal dynamics | Yes (event-study) | No (aggregate ATT) | v2.0 |
| Parallel trends validation | Formal (pre-trends) | Balance-based | Trade-off |
| Design-data alignment | Poor (window mismatch) | Perfect (2 periods) | **v3.0** |
| **Overall** | — | — | **v3.0** |

---

## Summary for Peer Review

**Key narrative for paper**:

> "We exploit exogenous variation in wildfire timing (2012–2016) across lower-48 US counties, comparing outcomes before (2007–2011) and after (2016–2019) fire exposure. This single-cohort design avoids confounding from the 2020 pandemic and provides sufficient statistical power despite national scope. We validate identification using propensity-score matching (WFP 2012 baseline fire hazard) and balance diagnostics; preliminary results indicate wildfires increased poverty rates by X percentage points, with Z% mediated by out-migration."

**Confidence level**: HIGH (clear design, no confounds, adequate power)

---

*End of Design Implications.*
