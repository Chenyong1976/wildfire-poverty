# Coarsened exact matching (CEM) on WFP 2014 quintiles + OLS TWFE
#
# CEM on WFP quintile × pre-2013 fire history (10-cell grid).
# After matching: OLS TWFE with tract and period FE on the CEM-matched sample.
# ATT estimates compared to IPW-TWFE in robustness table.
#
# Design:
#   - Coarsen WFP 2014 mean percentile into 5 quintile bins (Q1–Q5)
#   - Coarsen fire_pre2013 into binary (0/1) — 10 cells total
#   - Exact match treated tracts to controls in same cell
#   - OLS: outcome ~ Treated × Post + tract FE + period FE, weighted by CEM weights
#   - SE: clustered by county
#
# Inputs:
#   data/processed/analysis_panel_final.parquet
#   data/processed/matching_covariates.parquet
# Outputs:
#   results/cem_att_estimates.csv    ATT + SE + CI for each outcome
#   results/cem_balance_table.csv    Pre- and post-CEM SMD for all covariates

suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
  library(tidyr)
  library(fixest)
  library(MatchIt)
  library(cobalt)
})

ROOT    <- here::here()
PROC    <- file.path(ROOT, "data", "processed")
RESULTS <- file.path(ROOT, "results")
dir.create(RESULTS, showWarnings = FALSE, recursive = TRUE)

OUTCOMES <- c("poverty_rate", "log_med_income_2020", "in_migration_rate", "employment_rate")

# ── Load data ─────────────────────────────────────────────────────────────────

panel <- read_parquet(file.path(PROC, "analysis_panel_final.parquet"))
covs  <- read_parquet(file.path(PROC, "matching_covariates.parquet"))

# Merge covariates to the panel (GISJOIN is the tract identifier)
panel <- panel |>
  left_join(
    covs |> select(GISJOIN, wfp_mean_pct, fire_pre2013, rucc_2013,
                   pov_rate_2014, log_inc_2014, emp_rate_2014, mig_rate_2014),
    by = "GISJOIN"
  )

# Keep only treated and never-treated; restrict to pre- and post-periods used in DiD
panel <- panel |>
  filter(treated == 1 | never_treated == 1) |>
  filter(h %in% c(-2, -1, 0, 1, 2))   # drop h=-3 (2000-boundary; appendix only)

# Cross-section for matching: use h = -1 (ACS 2014 baseline)
cross <- panel |>
  filter(h == -1) |>
  select(GISJOIN, treated, wfp_mean_pct, fire_pre2013, rucc_2013,
         pov_rate_2014, log_inc_2014, emp_rate_2014, mig_rate_2014) |>
  distinct()

cat(sprintf("Cross-section for CEM: %d treated, %d never-treated\n",
            sum(cross$treated == 1), sum(cross$treated == 0)))

# ── CEM via MatchIt ───────────────────────────────────────────────────────────

# Coarsen WFP 2014 into quintile bins; fire_pre2013 is already binary
cross <- cross |>
  mutate(
    wfp_quintile = cut(wfp_mean_pct,
                       breaks = quantile(wfp_mean_pct, probs = 0:5/5, na.rm = TRUE),
                       labels = c("Q1","Q2","Q3","Q4","Q5"),
                       include.lowest = TRUE)
  )

m_out <- matchit(
  treated ~ wfp_quintile + fire_pre2013,
  data   = cross,
  method = "cem",
  estimand = "ATT"
)

cat("\nCEM summary:\n")
print(summary(m_out))

# Extract CEM weights
cem_weights <- match.data(m_out) |>
  select(GISJOIN, treated, weights, subclass) |>
  rename(cem_weight = weights, cem_cell = subclass)

# ── Balance table ─────────────────────────────────────────────────────────────

bal <- bal.tab(
  m_out,
  covs  = ~ wfp_mean_pct + fire_pre2013 + rucc_2013 +
             pov_rate_2014 + log_inc_2014 + emp_rate_2014 + mig_rate_2014,
  stats = c("mean.diffs"),
  un    = TRUE
)
cat("\nCovariate balance (SMD before / after CEM):\n")
print(bal)

bal_df <- bal$Balance |>
  tibble::rownames_to_column("covariate") |>
  rename(smd_before = Diff.Un, smd_after = Diff.Adj)
write.csv(bal_df, file.path(RESULTS, "cem_balance_table.csv"), row.names = FALSE)

# ── OLS TWFE on CEM-matched sample ────────────────────────────────────────────

# Merge CEM weights back to full panel
panel_cem <- panel |>
  inner_join(cem_weights, by = c("GISJOIN", "treated")) |>
  mutate(county_fips = substr(GISJOIN, 1, 5))   # 5-digit county FIPS for clustering

att_rows <- list()
es_rows  <- list()

for (outcome in OUTCOMES) {
  cat(sprintf("\n── CEM-OLS: %s ──\n", outcome))

  # TWFE: outcome ~ Treated × Post + tract FE + period FE
  # Reference: h = -1 (absorbed by tract FE + period FE with Post indicator)
  fml <- as.formula(sprintf(
    "%s ~ i(h, treated, ref = -1) | GISJOIN + h",
    outcome
  ))

  fit <- feols(
    fml,
    data    = panel_cem,
    weights = ~cem_weight,
    cluster = ~county_fips
  )

  coefs <- coeftable(fit) |>
    as.data.frame() |>
    tibble::rownames_to_column("term") |>
    filter(grepl("h::", term)) |>
    mutate(
      h       = as.integer(sub("h::(-?[0-9]+):treated", "\\1", term)),
      outcome = outcome,
      spec    = "cem_ols",
      coef    = Estimate,
      se      = `Std. Error`,
      ci_lo   = Estimate - 1.96 * `Std. Error`,
      ci_hi   = Estimate + 1.96 * `Std. Error`
    ) |>
    select(outcome, spec, h, coef, se, ci_lo, ci_hi)

  es_rows[[outcome]] <- coefs

  # Aggregate ATT: simple average of h = 0, +1, +2
  post_coefs <- coefs |> filter(h >= 0)
  att  <- mean(post_coefs$coef)
  se_a <- sqrt(mean(post_coefs$se^2))   # conservative; bootstrap preferred
  att_rows[[outcome]] <- data.frame(
    outcome  = outcome,
    spec     = "cem_ols",
    att      = att,
    se       = se_a,
    ci_lo    = att - 1.96 * se_a,
    ci_hi    = att + 1.96 * se_a
  )
  cat(sprintf("  ATT (avg h=0,+1,+2): %.4f  SE: %.4f\n", att, se_a))
}

# ── Save outputs ──────────────────────────────────────────────────────────────

att_out <- bind_rows(att_rows)
es_out  <- bind_rows(es_rows)

write.csv(att_out, file.path(RESULTS, "cem_att_estimates.csv"), row.names = FALSE)
write.csv(es_out,  file.path(RESULTS, "cem_es_coefs.csv"),      row.names = FALSE)
write.csv(cem_weights, file.path(RESULTS, "cem_weights_r.csv"), row.names = FALSE)

cat("\n[OK] CEM outputs saved:\n")
cat("     results/cem_att_estimates.csv\n")
cat("     results/cem_es_coefs.csv\n")
cat("     results/cem_balance_table.csv\n")
