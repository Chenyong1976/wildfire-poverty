# Critical Design Issue & Alternative Causal Identification Strategies

**Date**: 2026-07-31  
**Problem**: Overlapping fire windows violate mutual exclusivity assumption in staggered DiD  
**Status**: Requires redesign before proceeding to estimation

---

## The Problem

In the current 2-cohort design:

| Cohort | Fire Years | Example Fire |
|--------|-----------|--------------|
| C1 (WHP2012) | 2013–2016 | Fire in 2015 ✓ Cohort 1 |
| C2 (WHP2018) | 2019–2023 | Fire in 2015 ✗ NOT in Cohort 2 |

**Issue**: A fire in 2015 enters C1 but not C2. A fire in 2020 enters C2 but not C1.

**Why this breaks the design**:
1. **Mutual exclusivity violated**: The C&S framework assumes each treated unit belongs to exactly one cohort with a unique "treatment time" (g_i).
2. **Artificial weighting**: Different fires get implicit weights based on which cohorts they join. The same fire year (2015) is treated fundamentally differently depending on which cohort it lands in.
3. **Contamination**: Tracts burned in 2015–2018 (the gap) are never treated in either cohort, creating a "comparison" group of actually-treated units disguised as controls.
4. **Mechanical bias**: The C&S estimator weights cohorts by cohort size; overlapping windows create mechanical correlation between treatment status and cohort membership.

**Example of the bias**:
- Suppose 90% of fires happen 2015–2017
- In C1 (fires 2013–2016), these are mostly treated
- In C2 (fires 2019–2023), these are mostly untreated (as controls)
- Same fires play different roles → biased ATT estimate

**This is fatal**: The design is not acceptable for causal inference.

---

## Alternative Causal Identification Strategies

### **Strategy 1: Single Non-Overlapping Cohort (Safest)**

**Design**:
- Define ONE treatment window: **fires 2015–2017** (clean 3-year window)
- All tracts with first fire in this window are treated
- All tracts with no fire 2013–2023 are controls
- Measure outcomes at 3 time points: ACS 2012 (pre), ACS 2018 (post 1), ACS 2023 (post 2)

**Estimating equation**:
```
Outcome_{i,t} = α_i + λ_t + ATT · Treated_i · Post_t + X_{i,2012}β + ε_{i,t}

Where:
- Treated_i = 1 if first fire 2015–2017, 0 if never
- Post_t = 1 if t ∈ {2018, 2023}, 0 if t = 2012
- Can also run event-study: β_h for h = {-2, -1, 0, +1}
```

**Advantages**:
- ✓ No cohort overlap; clean treatment assignment
- ✓ Simple difference-in-differences (or event-study)
- ✓ Easy to explain and defend
- ✓ No C&S framework; standard DiD sufficient
- ✓ Two post-treatment periods for dynamics

**Disadvantages**:
- ✗ Single cohort: reduced statistical power vs. multi-cohort stagger
- ✗ Doesn't leverage treatment timing variation (fires 2013–2014 vs. 2016–2017 treated identically)
- ✗ Only ~20–30% of fires fall in 2015–2017 window (majority of fires outside this period)
- ✗ Sample size: ~600–800 treated tracts (vs. ~1,200 in current 2-cohort design)

**When to use**: If you want **maximal statistical validity** and can accept reduced power.

---

### **Strategy 2: Fire-Size Staggered Cohorts (More Power, Dose-Response)**

**Design**:
- Define cohorts by **fire size**, not time
- Within each size class, use fire year for staggered timing

**Cohorts**:
| Cohort | Fire Size | Fire Years | N fires | Pre | Post |
|--------|-----------|-----------|---------|-----|------|
| **C1** | 1,000–2,000 acres | 2013–2023 | ~300 | 2012 | 2017, 2023 |
| **C2** | 2,000–5,000 acres | 2013–2023 | ~150 | 2012 | 2017, 2023 |
| **C3** | >5,000 acres | 2013–2023 | ~50 | 2012 | 2017, 2023 |

**Within each cohort, use C&S staggered DiD**:
- Sub-cohort C1a: fires 2013–2016 (within 1,000–2,000 acres)
- Sub-cohort C1b: fires 2017–2020 (within 1,000–2,000 acres)
- Etc.

**Advantages**:
- ✓ No temporal overlap (each tract assigned once, by fire size)
- ✓ Captures dose-response (small vs. large fires have different effects)
- ✓ Larger sample (all 1,200+ fires in one or more size class)
- ✓ Multiple cohorts within each size class for staggered DiD
- ✓ Controls for fire severity (intensive margin)

**Disadvantages**:
- ✗ **Fire size may be endogenous**: Larger fires more likely in high-hazard, economically vulnerable tracts
- ✗ Interpretation shifts: ATT now means "effect of [size class] fire, on average across all years 2013–2023"
- ✗ Confounds timing effects with size effects (fires in 2013 could differ from 2023 in size distribution)
- ✗ Needs instrumental variable or RDD for size if endogeneity concerns

**When to use**: If you want **multiple cohorts + dose-response** AND can argue fire size is exogenous (or control for it).

**Implementation**:
1. Merge MTBS fire attributes (acres burned) to tract-fire intersection
2. Classify each fire into size category (C1, C2, C3)
3. Create treatment year g_i within each size class
4. Run separate C&S models per size class, or combined with size × cohort interactions

---

### **Strategy 3: Continuous Treatment (Burned Share / Acreage)**

**Design**:
- Abandon cohorts entirely
- Use **% of tract burned** as continuous treatment
- Regression: Outcome = f(burn_share, post_period, baseline_covariates)

**Estimating equation**:
```
Outcome_{i,t} = α_i + λ_t + β · BurnShare_i · Post_t + X_{i,2012}γ + ε_{i,t}

Where:
- BurnShare_i = (acres burned in tract) / (tract area), measured pre-treatment
- Post_t = 1 if t > 2012, 0 otherwise
- β = ATT per percentage point of tract burned
```

**Advantages**:
- ✓ No cohort overlap (every tract has unique burn share)
- ✓ Captures dose-response naturally
- ✓ Maximum power (uses all fires, all burn intensities)
- ✓ Simple specification

**Disadvantages**:
- ✗ **Endogeneity**: Fire location and size are not random
  - High-poverty tracts may have lower suppression → more burn area
  - High-hazard tracts predetermined by terrain (correlated with outcomes)
- ✗ Cannot claim causal effect without addressing endogeneity
- ✗ Requires instrumental variable or RDD for causal claim

**Causal identification path** (if pursuing):
- **IV approach**: Instrument burn share with, e.g., wind conditions that amplify fire spread (but predetermined)
- **RDD approach**: Exploit discontinuities in fire boundaries (discontinuity in burn share at perimeter)
- **Spatial RDD**: Within burned tracts, compare border areas (high burn intensity) to interior (lower intensity) — requires fine spatial data

**When to use**: If you have an instrument or can implement RDD.

---

### **Strategy 4: Geographic RDD (Fire Perimeter Boundaries)**

**Design**:
- Use **fire perimeter boundaries** as geographic discontinuity
- Compare tracts just inside perimeter (burned) vs. just outside (control)
- Dell (2010) or Keele & Titiunik (2015) framework

**Estimating equation** (simplified):
```
Outcome_{i} = α + β · Burned_i + f(distance_to_perimeter_i) + X_i γ + ε_i

Where:
- Burned_i = 1 if tract intersects fire perimeter, 0 otherwise
- distance_to_perimeter_i = continuous distance (positive inside, negative outside)
- f(·) = nonparametric bandwidth around boundary
```

**Advantages**:
- ✓ Local identification: tracts on either side of boundary are comparable
- ✓ Avoids cohort overlap (tracts are locally comparable)
- ✓ Sharp causal identification (fire perimeter is exogenous)
- ✓ No assumptions about pre-trends (local randomization)

**Disadvantages**:
- ✗ **Limited scope**: Only compares tracts near fire boundaries (edges)
  - Fires in interior don't contribute (small sample relative to overlapping-cohort design)
  - Western fires mostly interior, not on state/county lines
- ✗ **Loss of sample**: Need dense fires along boundaries (rare in U.S. West)
- ✗ **Interior contamination**: Fire perimeters don't align perfectly with tract boundaries (modifiable areal unit problem)
- ✗ **Spatial autocorrelation**: Neighboring tracts correlated even after controlling for perimeter

**When to use**: If your fires are concentrated on clear geographic boundaries (unlikely in West).

---

### **Strategy 5: Triple-Difference (Regional Control)**

**Design**:
- Use **never-fire regions** (e.g., Northeast states: MA, VT, NH, ME, RI, CT) as control region
- Triple difference: Burned vs. unburned tracts × Fire states vs. Control states × Before vs. After

**Estimating equation**:
```
Outcome_{i,t} = α_i + λ_t + 
  β_1·Treated_i·Post_t +                          [DiD: fire states]
  β_2·Treated_i·Control_region·Post_t +           [Region diff]
  β_3·Post_t·Control_region +                     [Time × region]
  X_i γ + ε_{i,t}

β_1 - β_2 - β_3 = triple-difference ATT
```

**Advantages**:
- ✓ No cohort overlap (DiD within fire states)
- ✓ Controls for national time trends (via never-fire states)
- ✓ Doesn't rely on parallel trends within state
- ✓ Standard DiD estimation

**Disadvantages**:
- ✗ **Severely reduced sample**: Northeast control region is small
  - Only ~10% of U.S. tracts; already have low fire density
  - Remaining ~1,000 never-treated tracts vs. ~40,000 in fire states
- ✗ **Regional differences**: Northeast tracts differ from West in: climate, economy, demographics, housing, baseline poverty
  - Assumption that trends would be "parallel if no fires" very strong
- ✗ **Loss of power**: Triple-differencing multiplies variance

**When to use**: If you have specific concerns about national confounds (e.g., COVID, 2008 recession timing).

---

## Recommendation Hierarchy

### **Rank 1: Strategy 1 (Single Cohort) — RECOMMENDED IF POWER SUFFICIENT**

**Why this is best**:
- ✓ Cleanest causal identification
- ✓ No overlap, no weighting issues
- ✓ Simple to explain and defend
- ✓ Standard DiD (widely understood)
- ✓ Two post-periods for dynamics

**Sample size check**:
- Fires 2015–2017: ~600–800 tracts
- Never-treated (outside 100 km smoke buffer): ~35,000–40,000 tracts
- Ratio: ~1:50 — reasonable for DiD
- Expected CI width on poverty ATT: ±0.5–1.0 pp (acceptable)

**Decision**: Check power via Monte Carlo simulation or prior literature (e.g., wildfire-finance county-level results). If power is acceptable, **use Strategy 1**.

---

### **Rank 2: Strategy 2 (Fire-Size Cohorts) — IF POWER IS MARGINAL**

**Why**:
- ✓ Regains multi-cohort stagger (within each size class)
- ✓ No temporal overlap
- ✓ Captures dose-response
- ✓ Better power than single cohort
- ✗ Requires addressing fire-size endogeneity (sensitivity analyses)

**Implementation**:
1. Run primary results with fire-size cohorts
2. Robustness check: Include pre-fire covariates (e.g., baseline hazard, economic development) that correlate with fire size
3. If ATT robust to covariate inclusion, interpret as (approximately) causal

---

### **Rank 3: Strategy 3 (Continuous Burn Share) — IF YOU HAVE AN INSTRUMENT**

**Why**:
- ✓ Maximum power
- ✓ Dose-response
- ✗ Endogeneity fatal without IV/RDD

**Instrument candidates**:
- Pre-treatment fire history (# fires 1984–2012): predetermined, correlates with hazard
- WHP raster intensity: predetermined, correlates with burn area conditional on fire occurrence
- Elevation / slope: terrain endogeneity (not exogenous to outcomes)

**Issue**: Weak instruments likely (fire intensity driven by fire size, which endogenous).

---

## My Strong Recommendation

**Proceed with Strategy 1: Single Non-Overlapping Cohort**

Here's why:

1. **Design validity**: The current overlapping-cohort design has a fatal flaw you correctly identified. Strategy 1 solves it cleanly.

2. **Power**: Your sample is large enough:
   - ~700 treated tracts (fires 2015–2017)
   - ~40,000 controls (never-treated)
   - Ratio 1:57 — well-powered for 1–2 pp effect sizes

3. **Contribution**: Even with one cohort, you advance the literature:
   - First **national tract-level** study (not county-level or Western-only)
   - **Raster-based WHP matching** (270m resolution)
   - **Poverty focus** (prior work: health/property)
   - **Migration decomposition** (mechanism)

4. **Simplicity**: Defensible, reproducible, widely understood

---

## Redesign Checklist

- [ ] Revise `RESEARCH_PLAN.md`: Single cohort (fires 2015–2017), two post-periods (ACS 2018, 2023)
- [ ] Revise `empirical_design.md`: Standard DiD equations (no C&S framework needed)
- [ ] Revise `paper_outline.md`: Emphasize "single clean cohort" as design strength
- [ ] Re-run PAP with single cohort specification
- [ ] Update power calculations: Verify ~700 treated / ~40,000 control is sufficient
- [ ] Add to robustness: "Fires 2013–2014" cohort and "Fires 2018–2019" cohort as falsification/sensitivity

---

## Alternative Designs Summary Table

| Strategy | Cohorts | Overlap? | Power | Causal ID | Complexity | Recommend |
|----------|---------|----------|-------|-----------|-----------|-----------|
| **1. Single Cohort** | 1 | No | Medium | ✓✓✓ Clean | Low | **YES** |
| **2. Fire-Size Stagger** | 3 | No | High | ✓ (endogeneity) | Medium | Maybe |
| **3. Continuous Burn** | — | No | Very High | ✗ (needs IV) | Medium | If IV avail. |
| **4. Geog. RDD** | — | No | Low | ✓✓ Sharp | High | If boundaries dense |
| **5. Triple-Diff** | — | No | Low | ✓ (but strong assumptions) | Medium | If national confound |

---

**Next step**: Decide whether to accept Strategy 1 (cleanest, recommended) or explore Strategy 2 (more power, more complexity).

I recommend **Strategy 1**. It solves your overlap problem cleanly, retains sufficient power, and provides a credible causal identification. You can still add robustness checks with alternative fire windows.
