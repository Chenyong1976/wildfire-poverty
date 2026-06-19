# Implementation Ready: v4.2 Research Plan
**Date**: 2026-06-19  
**Status**: ✅ Git repository initialized; ready for PAP registration

---

## Summary of Updates

### Research Plan (RESEARCH_PLAN_v4_FINAL.md)
All sections updated to reflect v4.2 methodology:

✅ **Section 3 (Threats)**: Added contamination diagnostic as primary mitigation  
✅ **Section 4 (Sample)**: Separated early-treated (~400–500) from late-treated (~100–150) counties  
✅ **Section 5 (Estimation)**: New two-group DiD specification with τ_early and τ_late  
✅ **Section 7 (PAP)**: Locked hypotheses for both primary (early) and diagnostic (late) cohorts  
✅ **Section 6 (Robustness)**: Reordered tests; "exclude late-treated" now PRIMARY robustness  
✅ **Section 9 (Strengths)**: Updated to highlight contamination diagnostic  

### Supporting Documents
✅ **v4.2_CHANGES.md**: Detailed comparison (v4.0 → v4.2); explains contamination logic  
✅ **Git repository**: Initialized with 2 commits; clean working tree

---

## Key Methodological Advance (v4.2)

### The Problem
- ACS 2015–2019 outcome window includes fires occurring 2016–2019
- These late fires are "not-yet-treated" when measured but still affect outcomes
- v4.0 ignored this; v4.2 diagnoses it

### The Solution
```
Outcome = α_c + λ_t + τ_early·(Early_c × Post_t) + τ_late·(Late_c × Post_t) + X + ε
```

- **τ_early**: Effect of 2012–2015 fires (3–8 years post-fire) — PRIMARY
- **τ_late**: Effect of 2016–2019 fires (0–3 years post-fire) — DIAGNOSTIC

### Why This Works
1. **Transparency**: Contamination risk is visible (not hidden)
2. **Testability**: If τ_late ≈ 0, contamination is minimal
3. **Robustness**: Exclude late-treated; confirm τ_early is stable
4. **Simplicity**: Two-group DiD (not staggered); easy to explain
5. **Power**: Keep ~500–600 treated units; don't lose data

---

## Parallel Trends: Status by Cohort

### Early Cohort (2012–2015 fires) ✓ TESTABLE
- Pre-periods: 1990, 2000, 2007–2011, 2015–2019
- Test: All pre-treatment coefficients ≈ 0?
- Decision: If yes, identification credible for primary result

### Late Cohort (2016–2019 fires) ⚠️ UNTESTABLE
- Pre-periods: None (fires occur during outcome window)
- Mitigation: PS-IPW balance testing (SMD < 0.1)
- Assumption: Conditional parallel trends (given observables)
- Flag: Results labeled exploratory in manuscript

---

## Pre-Analysis Plan (Locked, v4.2)

**Primary Hypothesis** (Early Cohort):
- Wildfires 2012–2015 increase poverty rates by 2–5 pp by 2015–2019
- Testable via formal parallel trends (3 pre-periods)
- Mechanism: Direct income loss + out-migration

**Diagnostic Hypothesis** (Late Cohort):
- Wildfires 2016–2019 show ~0 to 1.5 pp effects (0–3 year window)
- If small, contamination minimal; τ_early is unbiased
- If large, suggests late fires already harming outcomes

**Dose-Response** (Secondary):
- Effects scale with fire frequency and acreage (intensive margin)

---

## Results Reporting Hierarchy

**Table 1A (Primary)**: Early cohort + pre-period tests
- Shows parallel trends visually
- **Headline result** with strongest identification

**Table 1B (Diagnostic)**: Both cohorts side-by-side
- Makes contamination risk transparent
- Reader can judge τ_late magnitude

**Table 1 Robustness**: Exclude late-treated
- Confirms τ_early stable
- Validates contamination diagnostic

---

## Git Repository

**Initialized**: 2026-06-19  
**Commits**: 2
- e5a453e: Initial research plan and project structure
- 0f354fb: v4.2 changes summary

**Status**: Clean working tree (no uncommitted changes)

**Contents**:
- Research plans (v2.0, v3.0, v4.0, v4.2)
- Design documentation
- Implementation checklist
- Code templates (data assembly, matching, estimation)
- Requirements & setup files

---

## Before PAP Registration

✅ **Research plan finalized**: v4.2 specification locked in RESEARCH_PLAN_v4_FINAL.md  
✅ **Methodological changes documented**: v4.2_CHANGES.md provides full rationale  
✅ **Git repository initialized**: Ready for version control  

🔲 **Pending**:
1. Collaborator sign-off on v4.2 two-group DiD approach
2. Register PAP on OSF or SSRN (lock specification)
3. Run `/deep-research` lit-review (wildfire-poverty mechanisms)
4. Week 1 feasibility check (PS-IPW ESS; Census data availability)

---

## Next Phase: Implementation (Weeks 1–10)

### Week 1–3: Data Assembly
- Census 1990, 2000 poverty data
- ACS 2007–2011, 2015–2019 (income, migration, employment)
- MTBS fire perimeters (1990–2019)
- USFS WFP 2012 (matching variable)

### Week 4: Matching & Balance
- PS-IPW on WFP 2012 + pre-2012 fire history + baseline covariates
- Check SMD < 0.1 for all covariates
- Calculate ESS; if < 100, contingency: Western 8-state or CEM

### Week 5: Main Estimation
- Estimate τ_early, τ_late (both outcomes)
- Test parallel trends (early cohort: 3 pre-period coefficients)
- Report 95% CIs via bootstrap (1,000 reps)

### Weeks 6–7: Mechanisms & Robustness
- Mediation analysis (net migration mechanism)
- Dose-response (per-fire, per-acreage effects)
- 9+ robustness tests (smoke buffer, fire threshold, matching method, etc.)

### Weeks 8–10: Output & Manuscript
- Publication-ready tables (LaTeX) and figures (300 DPI)
- Manuscript drafting (7 sections)
- Peer review iterations

---

## Key Files to Review

**RESEARCH_PLAN_v4_FINAL.md**: Complete specification (treatment, estimation, PAP)  
**v4.2_CHANGES.md**: Detailed explanation of v4.0 → v4.2 transition  
**DESIGN_IMPLICATIONS.md**: Costs/benefits of simplified design vs. staggered DiD  
**PRE_ANALYSIS_CHECKLIST.md**: Phase-by-phase implementation tasks

---

## Contact & Next Steps

**Current status**: Implementation-ready; awaiting PAP registration

**Immediate actions**:
1. Review RESEARCH_PLAN_v4_FINAL.md and v4.2_CHANGES.md
2. Confirm two-group DiD approach with collaborators
3. Register PAP on OSF (use specification from Section 7)
4. Begin Week 1 data assembly

**Timeline**: 11 weeks to publication-ready manuscript

---

*End of Implementation Ready. Repository at: C:/Users/chenyon/research/wildfire-poverty-analysis/*
