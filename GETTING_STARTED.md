# Getting Started

Welcome to the Wildfire-Poverty Analysis project. This guide walks you through the project structure and how to get started.

---

## What This Project Does

**Research question**: Do large wildfires reduce household incomes and increase poverty in Western US counties?

**Approach**: Staggered difference-in-differences (Callaway & Sant'Anna 2021) with Wildfire Hazard Potential (WHP) matching.

**Timeline**: Western US counties, 2000–2020 (21 years, ~500 counties).

---

## Key Documents

Read these **in order** when starting:

1. **README.md** (2 min) — High-level overview and quick-start commands
2. **RESEARCH_PLAN.md** (20 min) — Full research design, methodology, data sources, timeline
3. **CLAUDE.md** (5 min) — Development standards and code architecture (for you or future Claude AI sessions)
4. **docs/data_dictionary.md** (10 min) — Detailed data variable definitions and processing

---

## Quick Start (5 min)

### 1. Set up environment
```bash
cd wildfire-poverty-analysis/
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 2. Explore the project structure
```bash
# View directory layout
ls -la

# See what scripts are available
ls -la src/
```

### 3. Run tests (placeholder for now)
```bash
pytest tests/ -v
```

### 4. Run the analysis pipeline (not yet implemented)
```bash
python -m src.main
```

---

## Project Structure at a Glance

```
wildfire-poverty-analysis/
├── CLAUDE.md              ← Development guidance (read this!)
├── RESEARCH_PLAN.md       ← Full research plan (detailed methodology)
├── README.md              ← Quick overview
├── GETTING_STARTED.md     ← You are here
├── data/                  
│   ├── raw/              ← Raw data files (to be acquired)
│   ├── processed/        ← Clean analysis-ready datasets
│   └── metadata/         ← Data dictionaries, crosswalks
├── src/                  ← Source code (main modules)
│   ├── main.py           ← Pipeline orchestration
│   ├── data/             ← Data loading & cleaning
│   ├── estimation/       ← DiD models & diagnostics
│   └── output/           ← Tables & figures
├── tests/                ← Unit tests (pytest)
├── notebooks/            ← Exploratory Jupyter notebooks
├── results/              ← Output (tables, figures, regressions)
├── docs/                 ← Documentation (data dictionary, notes)
├── requirements.txt      ← Python dependencies
└── setup.py              ← Package configuration
```

---

## What's Ready vs. What Needs Work

### ✅ Ready (Framework in Place)
- Project folder structure (data/, src/, tests/, results/)
- Python package scaffolding (setup.py, requirements.txt)
- Module stubs for data loading, estimation, and output
- Testing framework (pytest)
- Documentation templates (RESEARCH_PLAN.md, CLAUDE.md, data_dictionary.md)

### ⚠️ In Progress (Needs Implementation)
- **Data loading** (`src/data/`): Load ACS, MTBS fires, WHP, merge datasets
- **Matching & diagnostics** (`src/estimation/matching.py`): Covariate balance, WHP matching
- **DiD estimation** (`src/estimation/did_estimation.py`): Callaway & Sant'Anna via csdid or R
- **Tables & figures** (`src/output/`): Publication-ready LaTeX tables and plots
- **Main pipeline** (`src/main.py`): Orchestrate full workflow

### ❌ Not Started (Post-Results Work)
- Heterogeneous effects subgroup analysis
- Robustness checks (bandwidth sensitivity, placebo tests, etc.)
- Paper writing (Introduction, Methods, Results, etc.)

---

## Development Workflow

### Phase 1: Data Acquisition & Cleaning (Weeks 1–3)
1. **Acquire data** from sources listed in RESEARCH_PLAN.md Section 3
2. **Place in** `data/raw/` with folder structure matching `src/data/load_*.py` functions
3. **Implement** data loading functions in `src/data/`
4. **Run tests** to verify data quality: `pytest tests/test_data.py -v`
5. **Output**: `data/processed/analysis_sample.parquet`

### Phase 2: Matching & Balance (Week 4)
1. **Implement** `src/estimation/matching.py` (WHP covariate balance)
2. **Generate diagnostics**: Standardized mean differences, density plots
3. **Verify**: Treated vs. control groups are balanced on pre-treatment covariates

### Phase 3: DiD Estimation (Weeks 5–6)
1. **Implement** `src/estimation/did_estimation.py` (Callaway & Sant'Anna)
2. **Run event-study**: Estimate $\beta_h$ for $h \in [-5, \ldots, 5]$
3. **Check pre-trends**: Pre-trend coefficients should be ~0
4. **Compute ATT**: Average treatment effect on treated (post-fire effect)

### Phase 4: Output & Results (Week 7)
1. **Implement** `src/output/tables.py` and `src/output/figures.py`
2. **Generate** summary statistics table, event-study plot, ATT estimates
3. **Export** as .tex files (tables) and .png/.pdf (figures)

### Phase 5: Robustness & Writing (Weeks 8–10)
1. **Implement** `src/estimation/robustness.py` (sensitivity checks)
2. **Draft paper** using `/academic-paper` skill (or manually in LaTeX)
3. **Peer review** using `/academic-paper-reviewer` skill
4. **Revise** based on feedback

---

## Key Methodological References

**Staggered DiD**:
- Callaway, B., & Sant'Anna, P. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
- Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2), 175–199.

**Pre-trending & Interpretation**:
- Roth, J. (2022). Pretest with caution: High-powered tests can be misleading. *Journal of Business & Economic Statistics*, 40(3), 897–906.

**Python DiD Packages**:
- `csdid`: Python port of Callaway & Sant'Anna
- R's `did` package (can call from Python if needed)

---

## Standard Commands

```bash
# Install dependencies
pip install -e .

# Run analysis pipeline
python -m src.main

# Run specific data module
python -m src.data.build_analysis_dataset

# Run tests
pytest tests/ -v
pytest tests/test_data.py::TestDataLoading -v  # specific test class

# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Start Jupyter
jupyter notebook notebooks/
```

---

## Common Issues & Troubleshooting

### Import errors in src/
Make sure you've installed the package: `pip install -e .`

### Data files not found
Check `data/raw/` has the correct folder structure. See RESEARCH_PLAN.md Section 3 for expected layout.

### Tests failing
Most tests are currently skipped (not yet implemented). Once data is loaded, implement tests in `tests/test_data.py`.

---

## Next Steps

1. **Read RESEARCH_PLAN.md** for full methodology and data source details (20–30 min)
2. **Identify and acquire data** from sources in Section 3 of RESEARCH_PLAN.md
3. **Implement data loading** in `src/data/build_analysis_dataset.py`
4. **Run first pipeline**: `python -m src.main` (will output placeholder for now)
5. **Iterate**: Implement estimation, output, and robustness modules as data becomes available

---

## Questions?

- **Research methodology**: See RESEARCH_PLAN.md (Sections 2–4)
- **Code architecture**: See CLAUDE.md (Code Architecture section)
- **Data details**: See docs/data_dictionary.md
- **Development workflow**: See CLAUDE.md (Development Workflow section)

---

**Last updated**: 2026-06-17  
**Status**: Framework ready; awaiting data acquisition and implementation.
