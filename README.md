# Wildfire Impact on Poverty and Economic Outcomes

A causal analysis of how large wildfires affect household incomes, poverty rates, and employment in Western US counties.

**Research Question**: Do wildfires reduce incomes and increase poverty rates?

**Identification Strategy**: Staggered difference-in-differences (Callaway & Sant'Anna 2021) with Wildfire Hazard Potential (WHP) matching

**Sample**: Western US counties (n ≈ 500), 2000–2020

---

## Quick Start

### Environment Setup
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### Run Analysis
```bash
# Full pipeline
python -m src.main

# Build data only
python -m src.data.build_analysis_dataset

# Run DiD estimation
python -m src.estimation.did_estimation

# Generate tables and figures
python -m src.output.tables_and_figures
```

### Run Tests
```bash
pytest tests/ -v
```

---

## Project Structure

```
wildfire-poverty-analysis/
├── data/
│   ├── raw/           # Original data files (not tracked)
│   ├── processed/     # Analysis-ready datasets
│   └── metadata/      # Data dictionaries, crosswalks
├── src/               # Source code
│   ├── data/          # Data loading and preprocessing
│   ├── estimation/    # Econometric models (DiD, matching)
│   ├── output/        # Tables and figures
│   └── main.py        # Pipeline orchestration
├── tests/             # Unit tests
├── notebooks/         # Exploratory notebooks
├── results/           # Output tables, figures, regression tables
├── CLAUDE.md          # Claude Code guidance
└── RESEARCH_PLAN.md   # Full research plan and methodology
```

---

## Key Files

- **CLAUDE.md**: Development guidance for Claude Code (Claude AI's code assistant)
- **RESEARCH_PLAN.md**: Full research plan with methodology, timeline, and data documentation
- **CLAUDE.md**: Data, code, and writing standards for this project

---

## Methodology Overview

### Treatment
Large wildfires (MTBS ≥1,000 acres) occurring in Western US counties, 2000–2020.

### Outcomes
- Poverty rate (primary)
- Median household income
- Employment rate
- Per capita income

### Data Sources
- **Census/ACS**: IPUMS (household income, poverty, employment)
- **Fire perimeters**: MTBS database
- **Baseline hazard**: USFS Wildfire Hazard Potential (WHP)
- **Economic data**: BEA, USDA NASS

### Identification
1. **Staggered treatment timing** across counties (2000–2020)
2. **WHP-matched controls** to minimize selection bias
3. **Smoke spillover exclusion** (150 km buffer around fires)
4. **Pre-trend testing** (Roth 2022 framework)

### Estimator
Callaway & Sant'Anna (2021) for staggered difference-in-differences, with Sun & Abraham (2021) heterogeneity-robust alternative for robustness.

---

## Standard Commands

| Task | Command |
|------|---------|
| Run analysis | `python -m src.main` |
| Run tests | `pytest tests/ -v` |
| Lint code | `ruff check src/ tests/` |
| Format code | `ruff format src/ tests/` |

---

## Data & Reproducibility

All code assumes a clean environment. To reproduce:

1. **Acquire data** (see RESEARCH_PLAN.md for sources)
2. **Place raw data** in `data/raw/` with folder structure matching `src/data/load_*.py`
3. **Run pipeline**: `python -m src.main`
4. **Check output**: `results/` folder contains tables and figures

For data access instructions and detailed sources, see the [Data Sources](RESEARCH_PLAN.md#3-data--sample-definition) section in RESEARCH_PLAN.md.

---

## Timeline

- **Weeks 1–3**: Data acquisition and cleaning
- **Week 4**: Matching and balance diagnostics
- **Weeks 5–6**: DiD estimation and event-study analysis
- **Week 7**: Robustness checks
- **Week 8**: Heterogeneous effects analysis
- **Weeks 9+**: Paper writing and revision

---

## Contact

For questions about the analysis methodology, see RESEARCH_PLAN.md.  
For development guidance, see CLAUDE.md.

---

## License

[Specify license if applicable]
