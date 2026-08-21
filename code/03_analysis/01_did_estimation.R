# DiD Event-Study Estimation: Wildfire Impact on Poverty (Single Cohort)
#
# Design: Single clean cohort (fires 2015-2017), never-treated controls.
# Estimating equation:
#   Y_{it} = a_i + l_t + sum_{h != -1} b_h * D_i * 1[t=h] + e_{it}
#   h in {-3(2010), -2(2012), -1(2014,ref), 0(2022), +1(2023), +2(2024)}
#   D_i = 1 if treated (fire 2015-2017)
#   Cluster SE by county (COUNTYFP)
#
# With a single cohort, TWFE is numerically equivalent to
# Callaway & Sant'Anna (2021) -- no Goodman-Bacon decomposition concerns.
#
# Specifications:
#   (1) Unweighted TWFE (primary)
#   (2) IPW-weighted TWFE on common-support sample (robustness)
#
# Inputs:
#   data/processed/acs_tract_panel_xwalk.parquet
#   data/processed/fire_treatment_tracts.parquet
#   data/processed/ipw_weights.parquet   (WFP-restricted common-support sample)
#   data/processed/matching_covariates.parquet
#
# Outputs:
#   results/es_coefs_<outcome>.csv         event-study coefficients + 95% CI
#   results/att_aggregate.csv              aggregate ATT (mean h=0,+1,+2)
#   results/es_plot_poverty.png            event-study plot, primary outcome
#   results/es_plot_<outcome>.png          for all four outcomes

# ── Package setup ─────────────────────────────────────────────────────────────
# arrow is excluded: version mismatch with R 4.3.1 (built for 4.3.3).
# Data are read from CSV files exported by Python.
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))

pkgs <- c("fixest", "dplyr", "ggplot2")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) {
  message("Installing: ", paste(new, collapse = ", "))
  install.packages(new, lib = proj_lib, repos = "https://cloud.r-project.org",
                   type = "binary", quiet = TRUE)
}
suppressPackageStartupMessages({
  library(fixest); library(dplyr); library(ggplot2)
})

# ── Paths ──────────────────────────────────────────────────────────────────────
root <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../.."), mustWork = FALSE),
  error = function(e) normalizePath(".", mustWork = FALSE)
)
proc     <- file.path(root, "data", "processed")
res_dir  <- file.path(root, "results")
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)

cat("======================================================================\n")
cat("DiD EVENT-STUDY: Wildfire 2015-2017 -> Poverty / Income / Employment\n")
cat("======================================================================\n")

# ── Load data (CSV, exported from Python to avoid arrow version conflict) ───────
panel <- read.csv(file.path(proc, "acs_panel_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
fire  <- read.csv(file.path(proc, "fire_treatment_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
wts   <- read.csv(file.path(proc, "ipw_weights_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)

cat("Panel rows:", nrow(panel), "\n")
cat("Panel tracts:", length(unique(panel$NHGISCODE)), "\n")

# ── Merge ──────────────────────────────────────────────────────────────────────
# Align key: panel uses NHGISCODE; fire/weights use GISJOIN (identical values)
wts_slim <- wts[, c("GISJOIN", "ipw_weight")]  # drop duplicate 'treated' column
df <- panel |>
  merge(fire,     by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
  merge(wts_slim, by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE)

# Restrict to treated + never-treated
df <- df[df$treated == 1 | (!is.na(df$never_treated) & df$never_treated == 1), ]
cat("Analysis sample:", nrow(df), "rows |",
    sum(df$treated == 1 & df$acs_year == 2014), "treated tracts\n")

# ── Relative time variable h ───────────────────────────────────────────────────
year_to_h <- c("2010" = -3, "2012" = -2, "2014" = -1,
               "2022" =  0, "2023" =  1, "2024" =  2)
df$h <- year_to_h[as.character(df$acs_year)]

# Reference period check (h = -1 is ACS 2014)
stopifnot(all(df$h[df$acs_year == 2014] == -1))

# ── IPW weight column ──────────────────────────────────────────────────────────
# Treated: w = 1; IPW-supported controls: w = ipw_weight; off-support: NA -> 0
df$wt_ipw <- ifelse(df$treated == 1, 1, df$ipw_weight)
df$wt_ipw[is.na(df$wt_ipw)] <- 0

# COUNTYFP for clustering (from fire file; backfill from COUNTYFP in panel)
df$county_cluster <- ifelse(!is.na(df$COUNTYFP10), df$COUNTYFP10, df$COUNTYFP)

# ── Outcomes ───────────────────────────────────────────────────────────────────
outcomes <- list(
  poverty_rate      = list(label = "Poverty rate (pp)", scale = 100),
  log_med_income_2020 = list(label = "Log median HH income (2020$)", scale = 1),
  employment_rate   = list(label = "Employment rate (pp)", scale = 100),
  in_migration_rate = list(label = "In-migration rate (pp)", scale = 100)
)

# ── Event-study estimation function ───────────────────────────────────────────
run_es <- function(outcome, df, weights_col = NULL, suffix = "") {
  fml <- as.formula(
    paste0(outcome, " ~ i(h, treated, ref = -1) | NHGISCODE + acs_year")
  )
  wts_vec <- if (!is.null(weights_col)) df[[weights_col]] else NULL

  fit <- feols(fml, data = df, weights = wts_vec,
               cluster = ~county_cluster, panel.id = ~NHGISCODE + acs_year)

  coef_names <- names(coef(fit))
  h_vals     <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", coef_names))
  ci         <- confint(fit, level = 0.95)

  tibble(
    outcome  = outcome,
    spec     = suffix,
    h        = h_vals,
    coef     = coef(fit),
    ci_lo    = ci[, 1],
    ci_hi    = ci[, 2],
    se       = sqrt(diag(vcov(fit)))
  )
}

# ── Run all outcomes × specifications ──────────────────────────────────────────
cat("\nRunning event-study regressions ...\n")

results_list <- list()

for (outcome in names(outcomes)) {
  cat(" ", outcome, "...\n")

  # (1) Unweighted
  es_unwtd <- run_es(outcome, df, weights_col = NULL, suffix = "unweighted")

  # (2) IPW-weighted (common-support sample only: wt_ipw > 0)
  df_cs <- df[df$treated == 1 | df$wt_ipw > 0, ]
  es_ipw <- run_es(outcome, df_cs, weights_col = "wt_ipw", suffix = "ipw")

  coefs_out <- bind_rows(es_unwtd, es_ipw)
  write.csv(coefs_out,
            file.path(res_dir, paste0("es_coefs_", outcome, ".csv")),
            row.names = FALSE)

  results_list[[outcome]] <- coefs_out
}

all_results <- bind_rows(results_list)

# ── Aggregate ATT (mean of h = 0, +1, +2) ─────────────────────────────────────
cat("\nComputing aggregate ATT ...\n")

att_rows <- list()

for (outcome in names(outcomes)) {
  for (spec in c("unweighted", "ipw")) {
    sub <- filter(all_results, outcome == !!outcome, spec == !!spec, h >= 0)
    if (nrow(sub) == 0) next

    # Simple average of post-period estimates (equal weights across h=0,+1,+2)
    # Delta-method SE: SE(mean) = sqrt(sum(Cov)) / n_periods -- approximate;
    # for a more precise estimate, refit with linear restriction.
    att_est <- mean(sub$coef)
    att_se  <- sqrt(sum(sub$se^2) / nrow(sub)^2 +
                      2 * sum(outer(sub$se, sub$se)) / (2 * nrow(sub)^2))
    # Simpler conservative bound: max SE of individual periods
    att_se_conservative <- max(sub$se)

    att_rows[[length(att_rows) + 1]] <- tibble(
      outcome   = outcome,
      spec      = spec,
      att       = att_est,
      se        = att_se_conservative,  # conservative bound
      ci_lo     = att_est - 1.96 * att_se_conservative,
      ci_hi     = att_est + 1.96 * att_se_conservative,
      n_periods = nrow(sub)
    )
  }
}

att_table <- bind_rows(att_rows)
write.csv(att_table, file.path(res_dir, "att_aggregate.csv"), row.names = FALSE)

cat("\n--- Aggregate ATT (unweighted, h=0,+1,+2 average) ---\n")
for (outcome in names(outcomes)) {
  row <- filter(att_table, outcome == !!outcome, spec == "unweighted")
  if (nrow(row) == 0) next
  scale <- outcomes[[outcome]]$scale
  cat(sprintf("  %-25s  ATT = %+.4f  [%+.4f, %+.4f]\n",
              outcome,
              row$att * scale,
              row$ci_lo * scale,
              row$ci_hi * scale))
}

# ── Pre-trend assessment ───────────────────────────────────────────────────────
cat("\n--- Pre-trend coefficients (unweighted) ---\n")
cat(sprintf("  %-25s  %10s  %10s\n", "Outcome", "h=-3 (2010)", "h=-2 (2012)"))
for (outcome in names(outcomes)) {
  sub <- filter(all_results, outcome == !!outcome, spec == "unweighted", h %in% c(-3, -2))
  vals <- setNames(sub$coef, sub$h)
  scale <- outcomes[[outcome]]$scale
  v_m3 <- if (!is.na(vals["-3"])) vals["-3"] else NA_real_
  v_m2 <- if (!is.na(vals["-2"])) vals["-2"] else NA_real_
  cat(sprintf("  %-25s  %+10.4f  %+10.4f\n", outcome, v_m3 * scale, v_m2 * scale))
}

# ── Event-study plots ──────────────────────────────────────────────────────────
cat("\nSaving event-study plots ...\n")

plot_es <- function(coefs, outcome_label, scale = 1, out_path) {
  df_plot <- filter(coefs, spec == "unweighted") |>
    mutate(across(c(coef, ci_lo, ci_hi), ~ .x * scale))

  df_ipw <- filter(coefs, spec == "ipw") |>
    mutate(across(c(coef, ci_lo, ci_hi), ~ .x * scale))

  acs_label <- c("-3\n(2010)", "-2\n(2012)", "-1\n(2014)",
                 "0\n(2022)", "+1\n(2023)", "+2\n(2024)")
  h_vals <- c(-3, -2, -1, 0, 1, 2)

  # Add reference period (h=-1, coef=0) for completeness
  ref_row <- tibble(h = -1, coef = 0, ci_lo = 0, ci_hi = 0, se = 0)
  df_plot <- bind_rows(df_plot, ref_row) |> arrange(h)
  df_ipw  <- bind_rows(df_ipw,  ref_row) |> arrange(h)

  p <- ggplot(df_plot, aes(x = h)) +
    # Shaded pre-treatment region
    annotate("rect", xmin = -3.5, xmax = -0.5,
             ymin = -Inf, ymax = Inf, fill = "grey90", alpha = 0.5) +
    # Reference line
    geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey50") +
    geom_vline(xintercept = -0.5, linewidth = 0.4, linetype = "dashed",
               colour = "grey60") +
    # IPW robustness (background)
    geom_ribbon(data = df_ipw, aes(ymin = ci_lo, ymax = ci_hi),
                fill = "#fc8d59", alpha = 0.15) +
    geom_line(data = df_ipw, aes(y = coef),
              colour = "#fc8d59", linewidth = 0.7, linetype = "dashed") +
    # Unweighted primary
    geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi),
                fill = "#2166ac", alpha = 0.2) +
    geom_line(aes(y = coef), colour = "#2166ac", linewidth = 1) +
    geom_point(aes(y = coef), colour = "#2166ac", size = 2.5) +
    scale_x_continuous(breaks = h_vals, labels = acs_label) +
    labs(
      x     = "Relative period (h)",
      y     = outcome_label,
      title = paste0("Event-study DiD: ", outcome_label),
      caption = paste0(
        "Blue: unweighted TWFE; orange-dashed: IPW-weighted (WFP-restricted common-support sample).\n",
        "Shaded region: pre-treatment. h = -1 (ACS 2014) is reference period (normalized to 0).\n",
        "95% CIs, cluster SE by county."
      )
    ) +
    theme_minimal(base_size = 11) +
    theme(plot.caption     = element_text(size = 7, colour = "grey50", hjust = 0),
          panel.grid.minor = element_blank(),
          plot.margin      = margin(t = 5, r = 10, b = 30, l = 10, unit = "pt"))

  ggsave(out_path, p, width = 7, height = 5, dpi = 300)
  invisible(p)
}

for (outcome in names(outcomes)) {
  coefs <- filter(all_results, outcome == !!outcome)
  info  <- outcomes[[outcome]]
  plot_es(coefs, info$label, info$scale,
          file.path(res_dir, paste0("es_plot_", outcome, ".png")))
  cat("  [OK]", paste0("es_plot_", outcome, ".png"), "\n")
}

cat("\n[OK] All outputs saved to results/\n")
cat("     es_coefs_<outcome>.csv  (4 files)\n")
cat("     att_aggregate.csv\n")
cat("     es_plot_<outcome>.png   (4 files)\n")
