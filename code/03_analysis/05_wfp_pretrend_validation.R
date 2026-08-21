# WFP Pre-Trend Validation (R-2 from reviewer comments)
#
# Tests whether the residual WFP imbalance (post-IPW SMD = 0.43) predicts
# differential pre-period in-migration trends.
#
# Two approaches:
#   (1) Triple-difference: treated × 1[h=-2] × wfp_mean_pct
#   (2) Split-sample: separate event studies for high-WFP vs. low-WFP treated tracts
#
# Output: results/wfp_pretrend_validation.csv

# ── 0. Library paths ───────────────────────────────────────────────────────────
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))

pkgs <- c("fixest", "dplyr", "arrow")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) install.packages(new, lib = proj_lib,
                                  repos = "https://cloud.r-project.org",
                                  type  = "binary", quiet = TRUE)
suppressPackageStartupMessages({
  library(fixest)
  library(dplyr)
  library(arrow)
})

# ── Paths ──────────────────────────────────────────────────────────────────────
root    <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../.."), mustWork = FALSE),
  error = function(e) normalizePath(".", mustWork = FALSE)
)
proc    <- file.path(root, "data", "processed")
res_dir <- file.path(root, "results")
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)

cat("======================================================================\n")
cat("WFP Pre-Trend Validation\n")
cat("======================================================================\n")

# ── Load data ──────────────────────────────────────────────────────────────────
panel <- read_parquet(file.path(proc, "acs_tract_panel.parquet"))
fire  <- read_parquet(file.path(proc, "fire_treatment_tracts.parquet")) |>
  select(GISJOIN, treated, never_treated, COUNTYFP10)
covs  <- read_parquet(file.path(proc, "matching_covariates.parquet")) |>
  select(GISJOIN, wfp_mean_pct)

# Merge
df <- panel |>
  left_join(fire, by = c("GISJOIN")) |>
  left_join(covs, by = "GISJOIN") |>
  filter(treated == 1 | (!is.na(never_treated) & never_treated == 1))

# Relative time already in panel as 'h'
df$county_cluster <- df$COUNTYFP10

cat("Analysis sample:", nrow(df), "rows |",
    sum(df$treated == 1 & df$acs_year == 2014, na.rm = TRUE), "treated tracts\n\n")

# ── Approach 1: Triple-difference ─────────────────────────────────────────────
# Interaction: treated × period × wfp_mean_pct (standardized for interpretability)
cat("--- Approach 1: Triple-difference (treated × h=-2 × WFP) ---\n")

df$wfp_std <- (df$wfp_mean_pct - mean(df$wfp_mean_pct, na.rm = TRUE)) /
              sd(df$wfp_mean_pct, na.rm = TRUE)

# Main event study + triple-difference interaction terms for each period
# feols handles 3-way by interacting i(h, treated) with wfp_std
# Key coefficient: treated:h-2:wfp_std

fit_td <- feols(
  in_migration_rate ~ i(h, treated, ref = -1) +
                      i(h, treated, ref = -1):wfp_std |
                      NHGISCODE + acs_year,
  data    = df,
  cluster = ~county_cluster
)

# Extract coefficients for the triple-interaction at h = -2 and h = -3
cn   <- names(coef(fit_td))
ci95 <- confint(fit_td, level = 0.95)

# Triple-diff at h = -2: coefficient name contains "h::-2:treated::1:wfp_std" or similar
# Print all coef names to identify
cat("Coefficient names (first 20):\n")
print(cn[1:min(20, length(cn))])

# Find triple-interaction coefficients
# fixest names these like "h::-2:treated::1 × wfp_std" (exact varies by version)
td_idx <- grep("(-2|\\-2).*wfp_std|wfp_std.*(-2|\\-2)", cn)
if (length(td_idx) == 0) {
  # Try alternate naming
  td_idx <- grep("wfp_std", cn)
}

cat("\nTriple-interaction coefficients:\n")
for (i in td_idx) {
  cat(sprintf("  %-55s  coef=%+.6f  CI=[%+.6f, %+.6f]\n",
              cn[i], coef(fit_td)[i], ci95[i, 1], ci95[i, 2]))
}

# ── Approach 2: Split-sample by WFP median among treated ──────────────────────
cat("\n--- Approach 2: Split-sample pre-trends by WFP group ---\n")

wfp_med_treated <- median(df$wfp_mean_pct[df$treated == 1], na.rm = TRUE)
cat(sprintf("  WFP median among treated tracts: %.1f percentile\n", wfp_med_treated))

df$wfp_group <- ifelse(
  df$treated == 1 & df$wfp_mean_pct >= wfp_med_treated, "high_wfp",
  ifelse(df$treated == 1 & df$wfp_mean_pct < wfp_med_treated, "low_wfp", "control")
)
df$treated_high <- as.integer(df$wfp_group == "high_wfp")
df$treated_low  <- as.integer(df$wfp_group == "low_wfp")

# Run separate event studies for each group vs. the same never-treated controls
results_split <- list()

for (grp in c("high_wfp", "low_wfp")) {
  df_sub <- df |> filter(wfp_group == grp | wfp_group == "control")
  df_sub$treated_grp <- as.integer(df_sub$wfp_group == grp)

  fit <- tryCatch(
    feols(in_migration_rate ~ i(h, treated_grp, ref = -1) | NHGISCODE + acs_year,
          data = df_sub, cluster = ~county_cluster),
    error = function(e) NULL
  )
  if (is.null(fit)) next

  cn_sub  <- names(coef(fit))
  ci_sub  <- confint(fit, level = 0.95)
  h_vals  <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn_sub))
  h_m2_idx <- which(h_vals == -2)

  if (length(h_m2_idx) > 0) {
    b   <- coef(fit)[h_m2_idx]
    lo  <- ci_sub[h_m2_idx, 1]
    hi  <- ci_sub[h_m2_idx, 2]
    n_t <- sum(df_sub$treated_grp == 1 & df_sub$acs_year == 2014, na.rm = TRUE)
    cat(sprintf("  %-10s  n_treated=%d  beta(h=-2)=%+.5f  CI=[%+.5f, %+.5f]\n",
                grp, n_t, b, lo, hi))
    results_split[[grp]] <- data.frame(
      group = grp, n_treated = n_t, beta_m2 = b, ci_lo = lo, ci_hi = hi
    )
  }
}

# ── Save output ────────────────────────────────────────────────────────────────
# Triple-diff: save all WFP-interaction coefficients
td_coefs <- data.frame(
  term  = cn[td_idx],
  coef  = coef(fit_td)[td_idx],
  ci_lo = ci95[td_idx, 1],
  ci_hi = ci95[td_idx, 2]
)

split_df <- bind_rows(results_split)

out <- list(
  triple_diff = td_coefs,
  split_sample = split_df
)

write.csv(td_coefs,  file.path(res_dir, "wfp_pretrend_tripleD.csv"),  row.names = FALSE)
write.csv(split_df,  file.path(res_dir, "wfp_pretrend_split.csv"),    row.names = FALSE)

cat("\n[OK] Saved:\n")
cat("     results/wfp_pretrend_tripleD.csv\n")
cat("     results/wfp_pretrend_split.csv\n")
cat("\n[DONE] 05_wfp_pretrend_validation.R\n")
