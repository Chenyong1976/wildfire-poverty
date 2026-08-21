# Robustness Tests: Wald Pre-trends, Doubly-Robust TWFE, Rambachan-Roth
#
# Tests:
#   A. Wald pre-trend tests:
#        H0: beta(-2) = 0           [primary: 2010-vintage boundary]
#        H0: beta(-3) = beta(-2) = 0 [joint; h=-3 uses 2000-vintage, expect spurious]
#
#   B. Doubly-robust TWFE:
#        Baseline covariates interacted with year FE absorb differential trends
#        predictable from observable tract characteristics (conditional PT assumption).
#        DR-TWFE is consistent if either the PS model OR the outcome model is correct.
#
#   C. Rambachan-Roth (2023) sensitivity analysis (HonestDiD):
#        Relaxes parallel trends; bounds ATT CI under violations of size M
#        (relative magnitudes). Reports breakdown M: largest violation under which
#        the ATT CI still excludes zero.
#
# Inputs  (all CSV bridge files, no arrow dependency):
#   data/processed/acs_panel_for_R.csv
#   data/processed/fire_treatment_for_R.csv
#   data/processed/ipw_weights_for_R.csv
#   data/processed/matching_covariates_for_R.csv
#   data/processed/housing_for_R.csv        vacancy_rate, owner_occ_rate
#
# Outputs:
#   results/wald_tests_R.csv            Wald F-stat + p-val per outcome × test
#   results/dr_twfe_coefs.csv           DR-TWFE event-study coefficients
#   results/dr_twfe_att.csv             DR-TWFE aggregate ATT
#   results/honestdid_<outcome>.csv     Rambachan-Roth sensitivity table
#   results/honestdid_plot_<outcome>.png Sensitivity plot

# ── 0. Isolate from incompatible C:/R/Library (built for R 4.3.3) ─────────────
#    Use a project-local library + the R 4.3.1 system library only.
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
dir.create(proj_lib, recursive = TRUE, showWarnings = FALSE)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))
message("Library paths: ", paste(.libPaths(), collapse = " | "))

# ── 1. Packages ───────────────────────────────────────────────────────────────
pkgs <- c("fixest", "dplyr", "ggplot2", "HonestDiD")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) {
  message("Installing: ", paste(new, collapse = ", "))
  # type = "binary": avoid source compilation (Rtools not required on Windows).
  # Binary fixest 0.12.1 and HonestDiD 0.2.6 are compatible with R 4.3.1.
  install.packages(new, lib = proj_lib,
                   repos  = "https://cloud.r-project.org",
                   type   = "binary",
                   quiet  = TRUE)
}
suppressPackageStartupMessages({
  library(fixest)
  library(dplyr)
  library(ggplot2)
  library(HonestDiD)
})
message("fixest  : ", packageVersion("fixest"))
message("HonestDiD: ", packageVersion("HonestDiD"))

# ── 2. Paths ──────────────────────────────────────────────────────────────────
root    <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../.."), mustWork = FALSE),
  error = function(e) normalizePath(".", mustWork = FALSE)
)
proc    <- file.path(root, "data", "processed")
res_dir <- file.path(root, "results")
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)

cat("======================================================================\n")
cat("ROBUST TESTS: Wald / Doubly-Robust TWFE / Rambachan-Roth (HonestDiD)\n")
cat("======================================================================\n")

# ── 3. Data loading ───────────────────────────────────────────────────────────
cat("\nLoading data ...\n")
panel <- read.csv(file.path(proc, "acs_panel_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
fire  <- read.csv(file.path(proc, "fire_treatment_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
wts   <- read.csv(file.path(proc, "ipw_weights_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
covs  <- read.csv(file.path(proc, "matching_covariates_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)

cat("  panel rows:", nrow(panel), "\n")
housing <- read.csv(file.path(proc, "housing_for_R.csv"),
                    stringsAsFactors = FALSE, check.names = FALSE)
cat("  housing rows:", nrow(housing), "\n")

# ── 4. Merge and prepare ───────────────────────────────────────────────────────
# wts has its own 'treated' column (subset of tracts); drop it to avoid
# treated.x / treated.y conflict — treatment status comes from fire file.
wts <- wts[, c("GISJOIN", "ipw_weight")]

df <- panel |>
  merge(fire,    by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
  merge(wts,     by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
  merge(covs,    by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
  merge(housing, by    = c("NHGISCODE", "acs_year"),    all.x = TRUE)

df <- df[df$treated == 1 | (!is.na(df$never_treated) & df$never_treated == 1), ]

year_to_h <- c("2010" = -3, "2012" = -2, "2014" = -1,
               "2022" =  0, "2023" =  1, "2024" =  2)
df$h <- year_to_h[as.character(df$acs_year)]
df$county_cluster <- ifelse(!is.na(df$COUNTYFP10), df$COUNTYFP10, df$COUNTYFP)
df$wt_ipw  <- ifelse(df$treated == 1, 1, df$ipw_weight)
df$wt_ipw[is.na(df$wt_ipw)] <- 0
df$log_pop_2014 <- log(pmax(df$pop_2014, 1))

n_treated  <- sum(df$treated == 1 & df$acs_year == 2014, na.rm = TRUE)
n_ctrl     <- sum(!is.na(df$never_treated) & df$never_treated == 1 &
                    df$acs_year == 2014, na.rm = TRUE)
cat(sprintf("  Analysis sample: %d treated + %d control tracts\n",
            n_treated, n_ctrl))

outcomes <- list(
  poverty_rate       = list(label = "Poverty rate (pp)",            scale = 100),
  log_med_income_2020= list(label = "Log median HH income (2020$)", scale = 1),
  employment_rate    = list(label = "Employment rate (pp)",          scale = 100),
  in_migration_rate  = list(label = "In-migration rate (pp)",        scale = 100)
)

# Housing channel outcomes (mechanism tests, medium priority)
housing_outcomes <- list(
  vacancy_rate   = list(label = "Vacancy rate (pp)",        scale = 100),
  owner_occ_rate = list(label = "Owner-occupancy rate (pp)", scale = 100)
)

# Pre/post coefficient names (fixest i() syntax)
pre_names  <- c("h::-3:treated", "h::-2:treated")
post_names <- c("h::0:treated",  "h::1:treated",  "h::2:treated")
all_names  <- c(pre_names, post_names)

# ── Helper: fit baseline event-study TWFE ────────────────────────────────────
fit_base <- function(outcome, data, wts_col = NULL) {
  fml <- as.formula(
    paste0(outcome, " ~ i(h, treated, ref = -1) | NHGISCODE + acs_year")
  )
  # fixest 0.12.1 rejects weights = NULL; branch to omit argument entirely.
  if (!is.null(wts_col)) {
    feols(fml, data = data, weights = data[[wts_col]],
          cluster = ~county_cluster, panel.id = ~NHGISCODE + acs_year,
          warn = FALSE, notes = FALSE)
  } else {
    feols(fml, data = data,
          cluster = ~county_cluster, panel.id = ~NHGISCODE + acs_year,
          warn = FALSE, notes = FALSE)
  }
}

# ── A. WALD TESTS ─────────────────────────────────────────────────────────────
cat("\n══════════════════════════════════════════════════════════════\n")
cat("A. Wald pre-trend tests\n")
cat("══════════════════════════════════════════════════════════════\n")
cat(sprintf("  %-28s %-12s %-32s %8s %8s\n",
            "Outcome", "Spec", "H0", "F-stat", "p-val"))
cat(sprintf("  %s\n", strrep("-", 92)))

df_cs <- df[df$treated == 1 | df$wt_ipw > 0, ]

wald_rows <- list()
all_outcomes <- c(outcomes, housing_outcomes)
for (nm in names(all_outcomes)) {
  for (spec_info in list(
    list(label = "unweighted", data = df,    wts = NULL),
    list(label = "ipw",        data = df_cs, wts = "wt_ipw")
  )) {
    fit <- fit_base(nm, spec_info$data, spec_info$wts)

    for (test_info in list(
      list(label = "H0: beta(-2)=0 [primary]",    params = "h::-2:treated"),
      list(label = "H0: beta(-3)=beta(-2)=0 [jt]", params = pre_names)
    )) {
      params_present <- intersect(test_info$params, names(coef(fit)))
      if (length(params_present) == 0) next

      w <- wald(fit, keep = params_present)
      # wald() returns a list; extract stat and p
      fstat  <- as.numeric(w["stat"])
      pval   <- as.numeric(w["p"])
      flag   <- if (!is.na(pval) && pval < 0.05) "[**]" else
                if (!is.na(pval) && pval < 0.10) "[*] " else "    "
      cat(sprintf("  %-28s %-12s %-32s %8.3f %8.4f %s\n",
                  nm, spec_info$label, test_info$label, fstat, pval, flag))
      wald_rows[[length(wald_rows) + 1]] <- data.frame(
        outcome = nm, spec = spec_info$label, test = test_info$label,
        fstat = fstat, pval = pval, stringsAsFactors = FALSE
      )
    }
  }
}
wald_df <- do.call(rbind, wald_rows)
write.csv(wald_df, file.path(res_dir, "wald_tests_R.csv"), row.names = FALSE)

cat(sprintf("\n  Note: [**] p<0.05, [*] p<0.10. Primary test: H0: beta(-2)=0 only.\n"))
cat(sprintf("  h=-3 uses 2000-vintage boundaries; joint test rejection expected there.\n"))

# ── B. DOUBLY-ROBUST TWFE ─────────────────────────────────────────────────────
cat("\n══════════════════════════════════════════════════════════════\n")
cat("B. Doubly-robust TWFE (baseline covariates × year interactions)\n")
cat("══════════════════════════════════════════════════════════════\n")
cat("  Formula: Y ~ i(h,treated,ref=-1) + cov*yr_dummies | NHGISCODE + acs_year\n")
cat("  (explicit covariate × year interactions; year 2014 is reference)\n\n")

# Doubly-robust: create explicit covariate × year interactions.
# Reference year = 2014 (the event-study reference period h=-1).
# For each non-reference year, multiply each baseline covariate by a year dummy.
# This allows each covariate's slope to differ by year (conditional parallel trends).
dr_covs  <- c("pov_rate_2014", "log_inc_2014", "wfp_mean_pct", "emp_rate_2014")
# log_pop_2014 excluded: pop_2014 is 100% NA in matching_covariates_for_R.csv
# (population loaded from raw TS file in 01_ipw_weights.py but not exported to CSV).
dr_years <- c(2010, 2012, 2022, 2023, 2024)   # all years except ref = 2014

int_cols <- unlist(lapply(dr_covs, function(cv) paste0(cv, "X", dr_years)))
dr_fml_rhs <- paste0(
  " ~ i(h, treated, ref = -1) + ",
  paste(int_cols, collapse = " + "),
  " | NHGISCODE + acs_year"
)

dr_coef_rows <- list()
dr_att_rows  <- list()

# Inline interaction creation — no function wrapper to avoid scope ambiguity
dr_df <- df
for (.yr in dr_years) {
  .yd <- as.integer(dr_df$acs_year == .yr)
  for (.cv in dr_covs) {
    dr_df[[paste0(.cv, "X", .yr)]] <- .yd * dr_df[[.cv]]
  }
}
cat(sprintf("  DR interactions built: %d columns added, pov_rate_2014X2010 NAs: %d\n",
            length(int_cols), sum(is.na(dr_df$pov_rate_2014X2010))))

for (nm in names(all_outcomes)) {
  cat(sprintf("  %s ...\n", nm))
  sc <- all_outcomes[[nm]]$scale

  fml <- as.formula(paste0(nm, dr_fml_rhs))
  fit <- feols(fml, data = dr_df, cluster = ~county_cluster,
               warn = FALSE, notes = FALSE)

  # Extract event-study coefficients only
  cn  <- names(coef(fit))
  es_idx <- grep("^h::", cn)
  est <- coef(fit)[es_idx]
  ci  <- confint(fit, level = 0.95)[es_idx, ]
  se  <- sqrt(diag(vcov(fit)))[es_idx]
  h_vals <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", names(est)))

  for (i in seq_along(h_vals)) {
    dr_coef_rows[[length(dr_coef_rows) + 1]] <- data.frame(
      outcome = nm, h = h_vals[i],
      coef = est[i], se = se[i], ci_lo = ci[i, 1], ci_hi = ci[i, 2],
      stringsAsFactors = FALSE
    )
  }

  post_idx <- h_vals >= 0
  att_est  <- mean(est[post_idx])
  att_se   <- max(se[post_idx])
  dr_att_rows[[length(dr_att_rows) + 1]] <- data.frame(
    outcome = nm,
    att = att_est, se = att_se,
    ci_lo = att_est - 1.96 * att_se, ci_hi = att_est + 1.96 * att_se,
    stringsAsFactors = FALSE
  )

  cat(sprintf("    ATT (DR-TWFE) = %+.4f  [%+.4f, %+.4f]\n",
              att_est * sc,
              (att_est - 1.96 * att_se) * sc,
              (att_est + 1.96 * att_se) * sc))

  # Pre-trends under DR-TWFE
  pre_idx <- h_vals %in% c(-3, -2)
  for (j in which(pre_idx)) {
    cat(sprintf("    h=%+d: %+.4f (se=%.4f)\n",
                h_vals[j], est[j] * sc, se[j] * sc))
  }
}

dr_coef_df <- do.call(rbind, dr_coef_rows)
dr_att_df  <- do.call(rbind, dr_att_rows)
write.csv(dr_coef_df, file.path(res_dir, "dr_twfe_coefs.csv"), row.names = FALSE)
write.csv(dr_att_df,  file.path(res_dir, "dr_twfe_att.csv"),   row.names = FALSE)

# Compare DR-TWFE vs unweighted ATTs
cat("\n  --- ATT comparison: unweighted vs. DR-TWFE (all outcomes, scaled) ---\n")
att_unwtd <- read.csv(file.path(res_dir, "att_aggregate.csv"),
                       stringsAsFactors = FALSE)
cat(sprintf("  %-28s %14s %14s %10s\n", "Outcome", "Unweighted", "DR-TWFE", "Diff"))
cat(sprintf("  %s\n", strrep("-", 70)))
for (nm in names(all_outcomes)) {
  sc   <- all_outcomes[[nm]]$scale
  uw   <- att_unwtd[att_unwtd$outcome == nm & att_unwtd$spec == "unweighted", "att"]
  dr   <- dr_att_df[dr_att_df$outcome == nm, "att"]
  if (length(uw) && length(dr)) {
    cat(sprintf("  %-28s %+14.4f %+14.4f %+10.4f\n",
                nm, uw * sc, dr * sc, (dr - uw) * sc))
  }
}

# ── C. RAMBACHAN-ROTH (HonestDiD) ────────────────────────────────────────────
cat("\n══════════════════════════════════════════════════════════════\n")
cat("C. Rambachan-Roth (2023) sensitivity analysis\n")
cat("══════════════════════════════════════════════════════════════\n")
cat("  Delta_RM (relative magnitudes): M = max trend violation / max |pre-coef|\n")
cat("  Mbarvec: 0.0, 0.5, 1.0, 1.5, 2.0\n")
cat("  l_vec: average of h=0,+1,+2 (aggregate ATT)\n\n")

Mbarvec <- c(0, 0.5, 1.0, 1.5, 2.0)
l_vec   <- matrix(rep(1/3, 3), ncol = 1)   # average post-period ATT
num_pre  <- 2L   # h=-3, h=-2
num_post <- 3L   # h=0, h=+1, h=+2

hd_all <- list()

for (nm in names(all_outcomes)) {
  cat(sprintf("  %s ...\n", nm))
  sc <- all_outcomes[[nm]]$scale

  fit <- fit_base(nm, df)

  cn    <- names(coef(fit))
  # Coefficient order from fixest: h=-3, -2, 0, +1, +2
  if (!all(all_names %in% cn)) {
    cat(sprintf("    [SKIP] expected coefficients not found: %s\n",
                paste(setdiff(all_names, cn), collapse = ", ")))
    next
  }
  betahat <- coef(fit)[all_names]
  sigma   <- vcov(fit)[all_names, all_names]

  # Run HonestDiD sensitivity (delta_RM = relative magnitudes)
  hd <- tryCatch(
    createSensitivityResults_relativeMagnitudes(
      betahat       = betahat,
      sigma         = sigma,
      numPrePeriods = num_pre,
      numPostPeriods= num_post,
      Mbarvec       = Mbarvec,
      l_vec         = l_vec
    ),
    error = function(e) {
      cat(sprintf("    [ERROR] HonestDiD failed: %s\n", conditionMessage(e)))
      NULL
    }
  )

  if (is.null(hd)) next

  hd$outcome <- nm
  hd_all[[nm]] <- hd

  write.csv(hd, file.path(res_dir, paste0("honestdid_", nm, ".csv")),
            row.names = FALSE)

  # Print table
  cat(sprintf("    %-6s %12s %12s %12s\n", "M", "CI_lo", "CI_hi", "Excl. 0?"))
  for (i in seq_len(nrow(hd))) {
    row    <- hd[i, ]
    lo_s   <- if ("lb" %in% names(row)) row$lb * sc else NA
    hi_s   <- if ("ub" %in% names(row)) row$ub * sc else NA
    M_val  <- if ("Mbar" %in% names(row)) row$Mbar else row[[1]]
    excl   <- !is.na(lo_s) && !is.na(hi_s) && (lo_s > 0 | hi_s < 0)
    cat(sprintf("    %-6.1f %+12.4f %+12.4f %12s\n",
                M_val, lo_s, hi_s, if (excl) "YES" else "NO"))
  }

  # Breakdown M: smallest M at which 0 enters CI
  if ("lb" %in% names(hd) && "ub" %in% names(hd) && "Mbar" %in% names(hd)) {
    zero_in  <- hd$lb <= 0 & hd$ub >= 0
    breakdown <- if (any(zero_in)) min(hd$Mbar[zero_in]) else "> max(Mbarvec)"
    cat(sprintf("    Breakdown M: %s\n\n", breakdown))
  }

  # Sensitivity plot
  p <- ggplot(hd, aes(x = Mbar)) +
    geom_ribbon(aes(ymin = lb * sc, ymax = ub * sc),
                fill = "#2166ac", alpha = 0.25) +
    geom_line(aes(y = lb * sc), colour = "#2166ac") +
    geom_line(aes(y = ub * sc), colour = "#2166ac") +
    geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey50") +
    scale_x_continuous(breaks = Mbarvec) +
    labs(
      x = "M (max trend violation / max |pre-period coef|)",
      y = outcomes[[nm]]$label,
      title = paste0("Rambachan-Roth sensitivity: ", outcomes[[nm]]$label),
      caption = paste0(
        "Shaded band: honest CI under relative-magnitudes violation ≤ M.\n",
        "M=0 recovers standard parallel trends CI. ATT = average of h=0,+1,+2."
      )
    ) +
    theme_minimal(base_size = 10) +
    theme(plot.caption = element_text(size = 7, colour = "grey50"),
          panel.grid.minor = element_blank())

  ggsave(file.path(res_dir, paste0("honestdid_plot_", nm, ".png")),
         p, width = 6, height = 4, dpi = 300)
  cat(sprintf("    [OK] honestdid_plot_%s.png\n\n", nm))
}

# ── D. Summary table: compare all three specifications ────────────────────────
cat("\n══════════════════════════════════════════════════════════════\n")
cat("D. ATT comparison: Unweighted vs. DR-TWFE (scaled units)\n")
cat("══════════════════════════════════════════════════════════════\n")
cat(sprintf("  %-28s %14s %14s %10s\n",
            "Outcome", "Unweighted", "DR-TWFE", "Stable?"))
cat(sprintf("  %s\n", strrep("-", 70)))
for (nm in names(all_outcomes)) {
  sc  <- all_outcomes[[nm]]$scale
  uw  <- att_unwtd[att_unwtd$outcome == nm & att_unwtd$spec == "unweighted", ]
  dr  <- dr_att_df[dr_att_df$outcome == nm, ]
  if (!nrow(uw) || !nrow(dr)) next
  diff  <- abs(dr$att - uw$att) * sc
  stable <- diff < 0.05 * abs(uw$att * sc + 1e-8)   # within 5% relative change
  cat(sprintf("  %-28s %+14.4f %+14.4f %10s\n",
              nm, uw$att * sc, dr$att * sc,
              if (stable) "[OK]" else "[DIFF]"))
}

cat("\n[OK] All outputs saved to results/\n")
cat("     wald_tests_R.csv\n")
cat("     dr_twfe_coefs.csv, dr_twfe_att.csv\n")
cat("     honestdid_<outcome>.csv (6 files)\n")
cat("     honestdid_plot_<outcome>.png (6 files)\n")
