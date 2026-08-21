# Mechanism DiD: Four Pre-Trend Correction Methods
#
# Target outcomes (|pre-trend / ATT| > 0.5 in baseline TWFE):
#   med_gross_rent, log_home_value, med_age_diffcounty, inmov_poverty_rate
#
# Methods:
#   (1) Unweighted TWFE (baseline, proper clustered SEs)
#   (2) Unit-specific linear time trends: NHGISCODE[h] in feols
#   (3) Outcome-specific IPW TWFE (pre-trend covariate augmentation)
#   (4) Synthetic DiD (Arkhangelsky et al. 2021, synthdid package)
#   (5) HonestDiD sensitivity bounds (Rambachan & Roth 2023)
#
# Outputs:
#   results/mechanism_es_coefs.csv         event-study coefficients, all methods x outcomes
#   results/mechanism_att_table.csv        aggregate ATTs, all methods x outcomes
#   results/mechanism_honestdid.csv        HonestDiD breakdown M and sensitivity CIs
#   results/mechanism_synthdid.csv         SDiD point estimates + permutation SEs
#   results/es_plot_mechanism_<outcome>.png event-study plots (methods 1-3)

# ── 0. Isolate from incompatible C:/R/Library (built for R 4.3.3) ─────────────
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
dir.create(proj_lib, recursive = TRUE, showWarnings = FALSE)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))
message("Library paths: ", paste(.libPaths(), collapse = " | "))

# ── Package setup ──────────────────────────────────────────────────────────────
pkgs <- c("fixest", "dplyr", "ggplot2", "tidyr", "HonestDiD")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) {
  message("Installing: ", paste(new, collapse = ", "))
  install.packages(new, lib = proj_lib,
                   repos = "https://cloud.r-project.org",
                   type  = "binary",
                   quiet = TRUE)
}
suppressPackageStartupMessages({
  library(fixest)
  library(dplyr)
  library(ggplot2)
  library(tidyr)
  library(HonestDiD)
})
# synthdid has no binary for R 4.3.1; estimated in Python (04_synthdid.py)
HAS_SYNTHDID <- requireNamespace("synthdid", quietly = TRUE)
if (HAS_SYNTHDID) suppressPackageStartupMessages(library(synthdid))

# ── Paths ──────────────────────────────────────────────────────────────────────
root <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../.."), mustWork = FALSE),
  error = function(e) normalizePath(".", mustWork = FALSE)
)
proc    <- file.path(root, "data", "processed")
res_dir <- file.path(root, "results")
dir.create(res_dir, showWarnings = FALSE, recursive = TRUE)

cat("======================================================================\n")
cat("MECHANISM DiD: Four pre-trend correction methods\n")
cat("======================================================================\n")

# ── Load data ──────────────────────────────────────────────────────────────────
mech <- read.csv(file.path(proc, "mechanism_panel_for_R.csv"),
                 stringsAsFactors = FALSE, check.names = FALSE)

# Outcome-specific IPW weights (long: GISJOIN x outcome x treated + ipw_weight)
ow <- read.csv(file.path(proc, "outcome_specific_weights_for_R.csv"),
               stringsAsFactors = FALSE, check.names = FALSE)

# WFP matching covariates (for SDiD control restriction)
covs <- read.csv(file.path(proc, "matching_covariates_for_R.csv"),
                 stringsAsFactors = FALSE, check.names = FALSE)

cat("Mechanism panel:", nrow(mech), "rows |",
    length(unique(mech$NHGISCODE)), "tracts\n")

# ── Relative time ──────────────────────────────────────────────────────────────
year_to_h <- c("2010" = -3L, "2012" = -2L, "2014" = -1L,
               "2022" =  0L, "2023" =  1L, "2024" =  2L)
mech$h <- year_to_h[as.character(mech$acs_year)]

# Restrict to treated + never-treated
df <- mech[mech$treated == 1 | (!is.na(mech$never_treated) & mech$never_treated == 1), ]
df$county_cluster <- df$COUNTYFP10

cat("Analysis sample:", nrow(df), "rows |",
    sum(df$treated == 1 & df$acs_year == 2014), "treated tracts\n\n")

# ── Outcome definitions ────────────────────────────────────────────────────────
OUTCOMES <- list(
  med_gross_rent     = list(label = "Median gross rent ($)",       scale = 1),
  log_home_value     = list(label = "Log home value",              scale = 1),
  med_age_diffcounty = list(label = "Median age, diff-county movers (yr)", scale = 1),
  inmov_poverty_rate = list(label = "Poverty rate of in-movers (pp)", scale = 100)
)

# ── Helper: extract event-study coefficients from feols fit ───────────────────
extract_es <- function(fit, outcome, method) {
  cn     <- names(coef(fit))
  h_vals <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn))
  ci     <- confint(fit, level = 0.95)
  tibble(
    outcome = outcome, method = method, h = h_vals,
    coef = coef(fit), se = sqrt(diag(vcov(fit))),
    ci_lo = ci[, 1], ci_hi = ci[, 2]
  )
}

# ── Helper: aggregate ATT (mean of h = 0, +1, +2) ────────────────────────────
agg_att <- function(es, outcome, method) {
  sub <- filter(es, h >= 0)
  if (nrow(sub) == 0) return(NULL)
  att <- mean(sub$coef)
  se  <- max(sub$se)   # conservative bound
  tibble(
    outcome = outcome, method = method,
    att = att, se = se,
    ci_lo = att - 1.96 * se, ci_hi = att + 1.96 * se
  )
}

# ── Storage ────────────────────────────────────────────────────────────────────
all_es  <- list()
all_att <- list()

# ══════════════════════════════════════════════════════════════════════════════
# METHOD 1: Unweighted TWFE (baseline, proper clustered SEs)
# ══════════════════════════════════════════════════════════════════════════════
cat("--- Method 1: Unweighted TWFE ---\n")
for (outcome in names(OUTCOMES)) {
  fml <- as.formula(paste0(outcome, " ~ i(h, treated, ref=-1) | NHGISCODE + acs_year"))
  fit <- feols(fml, data = df, cluster = ~county_cluster)
  es  <- extract_es(fit, outcome, "unweighted")
  all_es[[paste0(outcome, "_unweighted")]]  <- es
  all_att[[paste0(outcome, "_unweighted")]] <- agg_att(es, outcome, "unweighted")
  pre2 <- filter(es, h == -2)$coef * OUTCOMES[[outcome]]$scale
  att  <- mean(filter(es, h >= 0)$coef) * OUTCOMES[[outcome]]$scale
  cat(sprintf("  %-25s  beta(h=-2)=%+.4f  ATT=%+.4f\n", outcome, pre2, att))
}

# ══════════════════════════════════════════════════════════════════════════════
# METHOD 2: Unit-specific linear time trends
# ══════════════════════════════════════════════════════════════════════════════
cat("\n--- Method 2: Unit-trend TWFE (NHGISCODE[h]) ---\n")
for (outcome in names(OUTCOMES)) {
  fml <- as.formula(
    paste0(outcome, " ~ i(h, treated, ref=-1) | NHGISCODE + acs_year + NHGISCODE[[h]]")
  )
  tryCatch({
    fit <- feols(fml, data = df, cluster = ~county_cluster)
    es  <- extract_es(fit, outcome, "unit_trend")
    all_es[[paste0(outcome, "_unit_trend")]]  <- es
    all_att[[paste0(outcome, "_unit_trend")]] <- agg_att(es, outcome, "unit_trend")
    pre2 <- filter(es, h == -2)$coef * OUTCOMES[[outcome]]$scale
    att  <- mean(filter(es, h >= 0)$coef) * OUTCOMES[[outcome]]$scale
    cat(sprintf("  %-25s  beta(h=-2)=%+.4f  ATT=%+.4f\n", outcome, pre2, att))
  }, error = function(e) {
    cat(sprintf("  %-25s  ERROR: %s\n", outcome, conditionMessage(e)))
  })
}

# ══════════════════════════════════════════════════════════════════════════════
# METHOD 3: Outcome-specific IPW TWFE
# ══════════════════════════════════════════════════════════════════════════════
cat("\n--- Method 3: Outcome-specific IPW TWFE ---\n")
for (outcome in names(OUTCOMES)) {
  ow_sub <- filter(ow, outcome == !!outcome)
  if (nrow(ow_sub) == 0) {
    cat(sprintf("  %-25s  [SKIP] No weights found\n", outcome))
    next
  }
  # Merge weights: ow_sub uses GISJOIN, df uses NHGISCODE (same values)
  df_out <- df |>
    left_join(ow_sub |> select(GISJOIN, ipw_weight) |> rename(NHGISCODE = GISJOIN),
              by = "NHGISCODE")
  # Treated weight = 1; controls: outcome-specific weight; off-support = 0
  df_out$wt <- ifelse(df_out$treated == 1, 1.0,
                      ifelse(is.na(df_out$ipw_weight), 0.0, df_out$ipw_weight))
  df_cs <- df_out[df_out$treated == 1 | df_out$wt > 0, ]

  fml <- as.formula(paste0(outcome, " ~ i(h, treated, ref=-1) | NHGISCODE + acs_year"))
  tryCatch({
    fit <- feols(fml, data = df_cs, weights = ~wt, cluster = ~county_cluster)
    es  <- extract_es(fit, outcome, "outcome_ipw")
    all_es[[paste0(outcome, "_outcome_ipw")]]  <- es
    all_att[[paste0(outcome, "_outcome_ipw")]] <- agg_att(es, outcome, "outcome_ipw")
    pre2 <- filter(es, h == -2)$coef * OUTCOMES[[outcome]]$scale
    att  <- mean(filter(es, h >= 0)$coef) * OUTCOMES[[outcome]]$scale
    cat(sprintf("  %-25s  beta(h=-2)=%+.4f  ATT=%+.4f\n", outcome, pre2, att))
  }, error = function(e) {
    cat(sprintf("  %-25s  ERROR: %s\n", outcome, conditionMessage(e)))
  })
}

# ══════════════════════════════════════════════════════════════════════════════
# METHOD 4: Synthetic DiD
# ══════════════════════════════════════════════════════════════════════════════
cat("\n--- Method 4: Synthetic DiD ---\n")
# synthdid estimated in Python (code/03_analysis/04_synthdid.py) because
# the R package has no binary for R 4.3.1 and Rtools is unavailable.
# Results are read back here if the CSV exists.
sdid_csv <- file.path(res_dir, "mechanism_synthdid.csv")
if (file.exists(sdid_csv)) {
  sdid_table <- read.csv(sdid_csv, stringsAsFactors = FALSE)
  cat("  [OK] Loaded SDiD results from", sdid_csv, "\n")
  for (i in seq_len(nrow(sdid_table))) {
    cat(sprintf("  %-25s  ATT = %+.4f  [%+.4f, %+.4f]\n",
                sdid_table$outcome[i], sdid_table$att[i],
                sdid_table$ci_lo[i], sdid_table$ci_hi[i]))
  }
} else {
  cat("  [SKIP] mechanism_synthdid.csv not found. Run code/03_analysis/04_synthdid.py first.\n")
  sdid_table <- tibble()
}

# ══════════════════════════════════════════════════════════════════════════════
# METHOD 5: HonestDiD sensitivity bounds
# Applied to unweighted TWFE estimates (method 1)
# Uses numPrePeriods = 1 (h=-2 only; h=-3 excluded due to 2000-vintage boundary)
# ══════════════════════════════════════════════════════════════════════════════
cat("\n--- Method 5: HonestDiD ---\n")

honestdid_rows <- list()

for (outcome in names(OUTCOMES)) {
  es_key <- paste0(outcome, "_unweighted")
  if (!es_key %in% names(all_es)) next
  es <- all_es[[es_key]]

  # Refit to extract full VCV matrix
  fml <- as.formula(paste0(outcome, " ~ i(h, treated, ref=-1) | NHGISCODE + acs_year"))
  fit <- feols(fml, data = df, cluster = ~county_cluster)

  # betahat: all non-reference period estimates, pre-periods first
  # h order: -3, -2, 0, +1, +2  (h=-1 is reference, excluded)
  cn       <- names(coef(fit))
  h_fit    <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn))
  betahat  <- coef(fit)
  sigma    <- vcov(fit)

  # numPrePeriods = 1 (h=-2 only; h=-3 flagged as unreliable due to boundary vintage)
  # Identify positions: pre = h<-1 (sorted ascending), post = h>=0
  pre_idx  <- which(h_fit < 0)
  post_idx <- which(h_fit >= 0)

  # Use only h=-2 as pre-period (drop h=-3 position)
  h_m2_idx <- which(h_fit == -2)
  keep_idx <- c(h_m2_idx, post_idx)

  beta_sub  <- betahat[keep_idx]
  sigma_sub <- sigma[keep_idx, keep_idx]

  l_vec <- rep(1/3, 3)  # aggregate post ATT = mean of 3 post periods (length = numPostPeriods)

  Mbarvec <- seq(0, 2, by = 0.5)

  tryCatch({
    hd_res <- createSensitivityResults_relativeMagnitudes(
      betahat        = beta_sub,
      sigma          = sigma_sub,
      numPrePeriods  = 1L,
      numPostPeriods = 3L,
      l_vec          = l_vec,
      Mbarvec        = Mbarvec
    )

    att_point <- mean(betahat[post_idx]) * OUTCOMES[[outcome]]$scale
    hd_res$outcome   <- outcome
    hd_res$att_point <- att_point
    hd_res$M         <- Mbarvec
    honestdid_rows[[outcome]] <- as_tibble(hd_res)

    ci_includes_zero <- hd_res$lb <= 0 & hd_res$ub >= 0
    breakdown_M <- if (any(ci_includes_zero)) Mbarvec[min(which(ci_includes_zero))] else NA_real_
    cat(sprintf("  %-25s  ATT=%+.4f  breakdown M=%s\n",
                outcome, att_point,
                if (is.na(breakdown_M)) ">2.0" else sprintf("%.1f", breakdown_M)))
  }, error = function(e) {
    cat(sprintf("  %-25s  ERROR: %s\n", outcome, conditionMessage(e)))
  })
}

honestdid_table <- bind_rows(honestdid_rows)

# ── Summary table ──────────────────────────────────────────────────────────────
cat("\n\n=== AGGREGATE ATT SUMMARY (all methods) ===\n")
all_att_table <- bind_rows(all_att)

for (outcome in names(OUTCOMES)) {
  cat(sprintf("\n%s:\n", outcome))
  sub <- filter(all_att_table, outcome == !!outcome)
  scale <- OUTCOMES[[outcome]]$scale
  for (i in seq_len(nrow(sub))) {
    cat(sprintf("  %-20s  ATT = %+.4f  [%+.4f, %+.4f]\n",
                sub$method[i],
                sub$att[i] * scale,
                sub$ci_lo[i] * scale,
                sub$ci_hi[i] * scale))
  }
  if (outcome %in% sdid_table$outcome) {
    sdid_row <- filter(sdid_table, outcome == !!outcome)
    cat(sprintf("  %-20s  ATT = %+.4f  [%+.4f, %+.4f]\n",
                "synthdid",
                sdid_row$att,
                sdid_row$ci_lo,
                sdid_row$ci_hi))
  }
}

# ── Save outputs ───────────────────────────────────────────────────────────────
all_es_df <- bind_rows(all_es)
write.csv(all_es_df,       file.path(res_dir, "mechanism_es_coefs.csv"),   row.names = FALSE)
write.csv(all_att_table,   file.path(res_dir, "mechanism_att_table.csv"),  row.names = FALSE)
write.csv(sdid_table,      file.path(res_dir, "mechanism_synthdid.csv"),   row.names = FALSE)
write.csv(honestdid_table, file.path(res_dir, "mechanism_honestdid.csv"),  row.names = FALSE)

cat("\n[OK] Saved:\n")
cat("     results/mechanism_es_coefs.csv\n")
cat("     results/mechanism_att_table.csv\n")
cat("     results/mechanism_synthdid.csv\n")
cat("     results/mechanism_honestdid.csv\n")

# ── Event-study plots (methods 1-3 overlaid) ──────────────────────────────────
cat("\nGenerating event-study plots ...\n")

method_colours <- c(
  unweighted  = "#2166ac",
  unit_trend  = "#1b7837",
  outcome_ipw = "#d6604d"
)
method_labels <- c(
  unweighted  = "Unweighted TWFE",
  unit_trend  = "Unit-trend TWFE",
  outcome_ipw = "Outcome-specific IPW"
)

acs_label <- setNames(
  c("-3\n(2010)", "-2\n(2012)", "-1\n(2014)", "0\n(2022)", "+1\n(2023)", "+2\n(2024)"),
  c(-3, -2, -1, 0, 1, 2)
)

for (outcome in names(OUTCOMES)) {
  info  <- OUTCOMES[[outcome]]
  scale <- info$scale

  df_plot <- all_es_df |>
    filter(outcome == !!outcome, method %in% names(method_colours)) |>
    mutate(across(c(coef, ci_lo, ci_hi), ~ .x * scale))

  # Add reference point h=-1, coef=0 for each method
  ref_rows <- expand.grid(
    outcome = outcome, method = unique(df_plot$method), h = -1L,
    coef = 0, se = 0, ci_lo = 0, ci_hi = 0, stringsAsFactors = FALSE
  )
  df_plot <- bind_rows(df_plot, ref_rows) |> arrange(method, h)

  p <- ggplot(df_plot, aes(x = h, colour = method, fill = method)) +
    annotate("rect", xmin = -3.5, xmax = -0.5,
             ymin = -Inf, ymax = Inf, fill = "grey92", alpha = 0.6) +
    geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey50") +
    geom_vline(xintercept = -0.5, linewidth = 0.4, linetype = "dashed", colour = "grey60") +
    geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi), alpha = 0.12, colour = NA) +
    geom_line(aes(y = coef), linewidth = 0.8) +
    geom_point(aes(y = coef), size = 2) +
    scale_colour_manual(values = method_colours, labels = method_labels, name = NULL) +
    scale_fill_manual(values = method_colours, labels = method_labels, name = NULL) +
    scale_x_continuous(breaks = -3:2, labels = acs_label[-3:2 + 4]) +
    labs(
      x       = "Relative period (h)",
      y       = info$label,
      title   = paste0("Event-study DiD: ", info$label),
      caption = paste0(
        "Methods: unweighted TWFE, unit-trend TWFE (NHGISCODE[h]), outcome-specific IPW TWFE.\n",
        "95% CIs, cluster SE by county. h = -1 (ACS 2014) reference period."
      )
    ) +
    theme_minimal(base_size = 11) +
    theme(
      legend.position    = "bottom",
      plot.caption       = element_text(size = 7, colour = "grey50"),
      panel.grid.minor   = element_blank()
    )

  out_path <- file.path(res_dir, paste0("es_plot_mechanism_", outcome, ".png"))
  ggsave(out_path, p, width = 7.5, height = 4.5, dpi = 300)
  cat(sprintf("  [OK] es_plot_mechanism_%s.png\n", outcome))
}

cat("\n[DONE] 02_mechanism_did.R complete.\n")
