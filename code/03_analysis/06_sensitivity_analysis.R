# First-Fire Restriction Sensitivity Analysis
#
# Runs event-study DiD for four first-fire restriction specs:
#   baseline  - no prior fire 1984-2014 (N=218)
#   s1a       - no prior fire 2000-2014 (N=300)
#   s1b       - no prior fire 2005-2014 (N=371)
#   s2_pooled - all cohort-fire tracts,  matched on prior fire stratum (N=1,089)
#
# Primary outcome: in_migration_rate (pp after *100).
# Secondary: poverty_rate, log_med_income_2020, employment_rate (appendix).
#
# For each spec: reports beta_{-2} (primary pre-trend test) and ATT
# (mean of h=0, +1, +2) with 95% CIs clustered by county.
#
# Outputs:
#   results/sensitivity_atts.csv
#   results/sensitivity_es_coefs.csv  (full event-study coefficients by spec)

# ── Package setup ──────────────────────────────────────────────────────────────
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))

pkgs <- c("fixest", "dplyr")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) install.packages(new, lib = proj_lib,
                                  repos = "https://cloud.r-project.org",
                                  type  = "binary", quiet = TRUE)
suppressPackageStartupMessages({ library(fixest); library(dplyr) })

# ── Paths ──────────────────────────────────────────────────────────────────────
root    <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../.."), mustWork = FALSE),
  error = function(e) normalizePath(".", mustWork = FALSE)
)
proc    <- file.path(root, "data", "processed")
res_dir <- file.path(root, "results")
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)

cat("======================================================================\n")
cat("SENSITIVITY ANALYSIS: First-Fire Restriction\n")
cat("======================================================================\n")

# ── Shared panel (same across all specs) ──────────────────────────────────────
panel <- read.csv(file.path(proc, "acs_panel_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
year_to_h <- c("2010" = -3, "2012" = -2, "2014" = -1,
               "2022" =  0, "2023" =  1, "2024" =  2)
panel$h <- year_to_h[as.character(panel$acs_year)]

OUTCOMES <- list(
  in_migration_rate   = list(label = "In-migration rate (pp)",  scale = 100),
  poverty_rate        = list(label = "Poverty rate (pp)",        scale = 100),
  log_med_income_2020 = list(label = "Log median income",        scale = 1),
  employment_rate     = list(label = "Employment rate (pp)",     scale = 100)
)

SPECS <- list(
  list(label = "baseline",  fire_file = "fire_treatment_baseline_for_R.csv",
       wts_file  = "ipw_weights_baseline_for_R.csv",  stratum_ctrl = FALSE),
  list(label = "s1a",       fire_file = "fire_treatment_s1a_for_R.csv",
       wts_file  = "ipw_weights_s1a_for_R.csv",       stratum_ctrl = FALSE),
  list(label = "s1b",       fire_file = "fire_treatment_s1b_for_R.csv",
       wts_file  = "ipw_weights_s1b_for_R.csv",       stratum_ctrl = FALSE),
  list(label = "s2_pooled", fire_file = "fire_treatment_s2_pooled_for_R.csv",
       wts_file  = "ipw_weights_s2_pooled_for_R.csv", stratum_ctrl = TRUE)
)

# ── Core estimation function ───────────────────────────────────────────────────
run_es_spec <- function(outcome, df, stratum_ctrl = FALSE) {
  # stratum_ctrl: add factor(prior_fire_stratum) as a covariate (S2-pooled)
  if (stratum_ctrl && "prior_fire_stratum" %in% colnames(df)) {
    fml <- as.formula(paste0(
      outcome,
      " ~ i(h, treated, ref = -1) + factor(prior_fire_stratum) | NHGISCODE + acs_year"
    ))
  } else {
    fml <- as.formula(paste0(
      outcome, " ~ i(h, treated, ref = -1) | NHGISCODE + acs_year"
    ))
  }

  fit <- tryCatch(
    feols(fml, data = df, cluster = ~county_cluster,
          panel.id = ~NHGISCODE + acs_year),
    error = function(e) { message("  [ERROR] ", conditionMessage(e)); NULL }
  )
  if (is.null(fit)) return(NULL)

  cn   <- names(coef(fit))
  ci95 <- confint(fit, level = 0.95)
  # Keep only the i(h, treated) coefficients — name starts with "h::"
  keep   <- grepl("^h::", cn)
  h_vals <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn[keep]))

  data.frame(
    outcome  = outcome,
    h        = h_vals,
    coef     = coef(fit)[keep],
    ci_lo    = ci95[keep, 1],
    ci_hi    = ci95[keep, 2],
    se       = sqrt(diag(vcov(fit)))[keep],
    stringsAsFactors = FALSE
  )
}

att_from_es <- function(es, scale = 1) {
  post <- es[es$h >= 0, ]
  if (nrow(post) == 0) return(rep(NA, 5))
  att   <- mean(post$coef) * scale
  att_se <- max(post$se) * scale
  c(att = att,
    ci_lo = att - 1.96 * att_se,
    ci_hi = att + 1.96 * att_se,
    beta_m2     = es$coef[es$h == -2][1] * scale,
    beta_m2_ci_lo = es$ci_lo[es$h == -2][1] * scale,
    beta_m2_ci_hi = es$ci_hi[es$h == -2][1] * scale)
}

# ── Main loop ──────────────────────────────────────────────────────────────────
all_es   <- list()
all_atts <- list()

for (spec in SPECS) {
  label <- spec$label
  cat(sprintf("\n%s\n", strrep("-", 60)))
  cat(sprintf("Spec: %s\n", label))

  fire <- read.csv(file.path(proc, spec$fire_file),
                   stringsAsFactors = FALSE, check.names = FALSE)
  wts  <- read.csv(file.path(proc, spec$wts_file),
                   stringsAsFactors = FALSE, check.names = FALSE)

  wts_slim <- wts[, c("GISJOIN", "ipw_weight")]  # drop duplicate 'treated' column
  df <- panel |>
    merge(fire, by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
    merge(wts_slim, by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE)
  df <- df[!is.na(df$treated) & (df$treated == 1 |
             (!is.na(df$never_treated) & df$never_treated == 1)), ]

  df$county_cluster <- ifelse(!is.na(df$COUNTYFP10), df$COUNTYFP10, df$COUNTYFP)

  n_treated <- sum(df$treated == 1 & df$acs_year == 2014, na.rm = TRUE)
  n_ctrl    <- sum(!is.na(df$never_treated) & df$never_treated == 1 &
                   df$acs_year == 2014, na.rm = TRUE)
  cat(sprintf("  Treated tracts: %d  |  Controls: %d\n", n_treated, n_ctrl))

  for (outcome in names(OUTCOMES)) {
    scale <- OUTCOMES[[outcome]]$scale
    es <- run_es_spec(outcome, df, stratum_ctrl = spec$stratum_ctrl)
    if (is.null(es)) next

    es$spec <- label
    all_es[[length(all_es) + 1]] <- es

    vals <- att_from_es(es, scale = scale)
    all_atts[[length(all_atts) + 1]] <- data.frame(
      spec          = label,
      outcome       = outcome,
      n_treated     = n_treated,
      n_ctrl        = n_ctrl,
      att           = vals["att"],
      ci_lo         = vals["ci_lo"],
      ci_hi         = vals["ci_hi"],
      beta_m2       = vals["beta_m2"],
      beta_m2_ci_lo = vals["beta_m2_ci_lo"],
      beta_m2_ci_hi = vals["beta_m2_ci_hi"],
      stringsAsFactors = FALSE
    )

    cat(sprintf("  %-25s ATT=%+.3f pp  beta(-2)=%+.3f pp  CI=[%+.3f,%+.3f]\n",
                outcome,
                vals["att"], vals["beta_m2"],
                vals["beta_m2_ci_lo"], vals["beta_m2_ci_hi"]))
  }
}

# ── Save outputs ───────────────────────────────────────────────────────────────
all_es_df  <- do.call(rbind, all_es)
all_att_df <- do.call(rbind, all_atts)

write.csv(all_es_df,  file.path(res_dir, "sensitivity_es_coefs.csv"), row.names = FALSE)
write.csv(all_att_df, file.path(res_dir, "sensitivity_atts.csv"),     row.names = FALSE)

cat("\n[OK] Saved:\n")
cat("     results/sensitivity_es_coefs.csv\n")
cat("     results/sensitivity_atts.csv\n")

# ── Print summary table for in_migration_rate ──────────────────────────────────
cat("\n--- In-migration ATT by spec (pp) ---\n")
imig <- all_att_df[all_att_df$outcome == "in_migration_rate", ]
cat(sprintf("  %-12s  %5s  %8s  %16s  %8s\n",
            "Spec", "N_trt", "ATT(pp)", "95% CI", "beta(-2)"))
for (i in seq_len(nrow(imig))) {
  r <- imig[i, ]
  cat(sprintf("  %-12s  %5d  %+7.3f  [%+6.3f,%+6.3f]  %+7.3f\n",
              r$spec, r$n_treated, r$att, r$ci_lo, r$ci_hi, r$beta_m2))
}

cat("\n[DONE] 06_sensitivity_analysis.R\n")
