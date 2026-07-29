"""
Propensity-score inverse-probability weighting for covariate balance.
Input: analysis_sample_final.parquet (with treatment indicator and covariates)
Output: IPW weights, balance diagnostics
"""

library(tidyverse)
library(data.table)

# Load data
data_path <- "data/processed/analysis_sample_final.parquet"
df <- arrow::read_parquet(data_path)

# Prepare data for PS matching
# Treatment: early_treated = 1, else 0
df <- df %>%
  mutate(treated = as.numeric(early_treated == 1)) %>%
  select(GEOID, year, treated, wfp_quintile, pre2012_fire_count,
         pre2012_acres_burned, baseline_poverty_rate, baseline_median_hh_income,
         poverty_rate, median_hh_income, employment_rate, net_migration_rate)

# Check sample size
cat("Sample size:", nrow(df), "\n")
cat("Treated:", sum(df$treated), "\n")
cat("Control:", sum(df$treated == 0), "\n")

# Propensity score model (logistic regression)
# PS = Pr(treated | WFP quintile, pre-2012 fire history, baseline covariates)
ps_model <- glm(treated ~ factor(wfp_quintile) + pre2012_fire_count +
                  pre2012_acres_burned + baseline_poverty_rate +
                  baseline_median_hh_income,
                family = binomial(link = "logit"),
                data = df)

summary(ps_model)

# Extract propensity scores
df$ps <- predict(ps_model, type = "response")

# Check overlap
cat("\nPropensity score overlap:\n")
cat("Treated: mean =", mean(df$ps[df$treated == 1]),
    ", min =", min(df$ps[df$treated == 1]),
    ", max =", max(df$ps[df$treated == 1]), "\n")
cat("Control: mean =", mean(df$ps[df$treated == 0]),
    ", min =", min(df$ps[df$treated == 0]),
    ", max =", max(df$ps[df$treated == 0]), "\n")

# Compute IPW weights
# Treated: w = 1
# Control: w = e / (1 - e)
df <- df %>%
  mutate(ipw = ifelse(treated == 1, 1, ps / (1 - ps)))

# Trim extreme weights (99th percentile)
weight_99 <- quantile(df$ipw[df$treated == 0], 0.99)
df <- df %>%
  mutate(ipw_trimmed = pmin(ipw, weight_99))

cat("\nIPW weight summary (trimmed at 99th percentile):\n")
cat("Min:", min(df$ipw_trimmed), "\n")
cat("Mean:", mean(df$ipw_trimmed), "\n")
cat("Max:", max(df$ipw_trimmed), "\n")
cat("Median:", median(df$ipw_trimmed), "\n")

# Save IPW weights for next phase
weights_output <- df %>%
  select(GEOID, year, treated, ps, ipw, ipw_trimmed)

arrow::write_parquet(weights_output, "data/processed/ipw_weights.parquet")

cat("\n[OK] IPW weights saved to data/processed/ipw_weights.parquet\n")
