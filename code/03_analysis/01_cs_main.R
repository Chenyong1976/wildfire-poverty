"""
Main DiD estimation: Callaway & Sant'Anna (2021) staggered DiD.
Input: analysis_sample_final.parquet, IPW weights
Output: ATT estimates, standard errors, 95% CIs for all outcomes
"""

library(tidyverse)
library(did)
library(data.table)

# Load analysis data
df <- arrow::read_parquet("data/processed/analysis_sample_final.parquet")
weights <- arrow::read_parquet("data/processed/ipw_weights.parquet")

# Merge weights
df <- df %>%
  left_join(weights %>% select(GEOID, year, ipw_trimmed),
            by = c("GEOID", "year"))

# Prepare data for Callaway & Sant'Anna
# Key variables:
# - GEOID: county identifier
# - year: time period
# - gname: treatment year (group), 0 for never-treated
# - tname: time period
# - yname: outcome variable
# - xformla: covariates formula

# Create treatment year variable (gname)
# early_treated: cohort year = 2016 (fires 2012-2015 affect 2016 outcomes)
# late_treated: cohort year = 2020 (fires 2016-2019 affect 2020 outcomes)
# never-treated: gname = 0

df <- df %>%
  mutate(gname = case_when(
    early_treated == 1 ~ 2016,
    late_treated == 1 ~ 2020,
    TRUE ~ 0
  ))

# Verify treatment assignment
cat("Treatment cohort distribution:\n")
print(table(df$gname, df$year))

# Outcomes to estimate
outcomes <- c("poverty_rate", "median_hh_income", "employment_rate", "net_migration_rate")

# Run C&S DiD for each outcome
cs_results <- list()

for (outcome in outcomes) {
  cat("\n==================================================\n")
  cat("Outcome:", outcome, "\n")
  cat("==================================================\n")

  # Callaway & Sant'Anna ATT
  att_gt <- att_gt(
    yname = outcome,
    tname = "year",
    idname = "GEOID",
    gname = "gname",
    data = df,
    est_method = "reg",
    xformla = ~ baseline_poverty_rate + baseline_median_hh_income,
    bstrap = TRUE,
    biters = 1000,
    clustervars = "GEOID"
  )

  # Aggregate ATT (average of all post-treatment periods)
  agg_att <- aggte(att_gt, type = "group")

  cat("\nAggregated ATT:\n")
  print(agg_att)

  # Store results
  cs_results[[outcome]] <- list(
    att_gt = att_gt,
    agg_att = agg_att
  )
}

# Summary table of main results
summary_table <- data.frame(
  Outcome = outcomes,
  ATT = NA_real_,
  SE = NA_real_,
  CI_lower = NA_real_,
  CI_upper = NA_real_,
  N_obs = NA_integer_
)

for (i in seq_along(outcomes)) {
  outcome <- outcomes[i]
  agg <- cs_results[[outcome]]$agg_att

  summary_table[i, "ATT"] <- agg$overall.att
  summary_table[i, "SE"] <- agg$overall.se
  summary_table[i, "CI_lower"] <- agg$overall.att - 1.96 * agg$overall.se
  summary_table[i, "CI_upper"] <- agg$overall.att + 1.96 * agg$overall.se
  summary_table[i, "N_obs"] <- nrow(df)
}

cat("\n==================================================\n")
cat("MAIN RESULTS: Callaway & Sant'Anna (2021)\n")
cat("==================================================\n")
print(summary_table)

# Save results
saveRDS(cs_results, "results/rds/cs_main_results.rds")
write_csv(summary_table, "results/tables/main_att_estimates.csv")

cat("\n[OK] Results saved to results/rds/cs_main_results.rds\n")
