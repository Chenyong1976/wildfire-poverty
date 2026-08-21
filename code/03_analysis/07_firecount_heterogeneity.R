# Fire-Count Heterogeneity Analysis
#
# Event-study DiD by prior fire stratum (0 / 1 / 2+ years with large fire 1984-2014).
# Primary outcome: in_migration_rate. Secondary: poverty_rate.
#
# Strata:
#   strat_0  - 0 prior fire years  (= baseline treated, N=218 tracts)
#   strat_1  - exactly 1 prior fire year  (~240-340 tracts)
#   strat_2p - 2+ prior fire years  (NOTE: only 51 controls — flagged, reported cautiously)
#
# Formal heterogeneity test: county block bootstrap (B=1,000 reps);
# difference ATT1-ATT0; two-sided p-value.
#
# Outputs:
#   results/heterogeneity_strata_atts.csv
#   results/fig_firecount_heterogeneity.png

# ── Package setup ──────────────────────────────────────────────────────────────
proj_lib <- tryCatch(
  normalizePath(file.path(dirname(sys.frame(1)$ofile), "../..", "rlib"),
                mustWork = FALSE),
  error = function(e) normalizePath("rlib", mustWork = FALSE)
)
sys_lib <- file.path(R.home(), "library")
.libPaths(c(proj_lib, sys_lib))

pkgs <- c("fixest", "dplyr", "ggplot2")
new  <- pkgs[!pkgs %in% installed.packages(lib.loc = .libPaths())[, "Package"]]
if (length(new)) install.packages(new, lib = proj_lib,
                                  repos = "https://cloud.r-project.org",
                                  type  = "binary", quiet = TRUE)
suppressPackageStartupMessages({
  library(fixest); library(dplyr); library(ggplot2)
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
cat("FIRE-COUNT HETEROGENEITY ANALYSIS\n")
cat("======================================================================\n")

BOOT_REPS <- 200
OUTCOMES <- c("in_migration_rate", "poverty_rate")

STRATA <- list(
  list(label = "strat_0",  desc = "0 prior fire years",
       fire_file = "fire_treatment_strat_0_for_R.csv",
       wts_file  = "ipw_weights_strat_0_for_R.csv",
       thin_ctrl = FALSE),
  list(label = "strat_1",  desc = "1 prior fire year",
       fire_file = "fire_treatment_strat_1_for_R.csv",
       wts_file  = "ipw_weights_strat_1_for_R.csv",
       thin_ctrl = FALSE),
  list(label = "strat_2p", desc = "2+ prior fire years",
       fire_file = "fire_treatment_strat_2p_for_R.csv",
       wts_file  = "ipw_weights_strat_2p_for_R.csv",
       thin_ctrl = TRUE)  # only 51 controls — flagged in outputs
)

# ── Shared panel ───────────────────────────────────────────────────────────────
panel <- read.csv(file.path(proc, "acs_panel_for_R.csv"),
                  stringsAsFactors = FALSE, check.names = FALSE)
year_to_h <- c("2010" = -3, "2012" = -2, "2014" = -1,
               "2022" =  0, "2023" =  1, "2024" =  2)
panel$h <- year_to_h[as.character(panel$acs_year)]

# ── Event-study estimation ─────────────────────────────────────────────────────
run_es <- function(outcome, df) {
  fml <- as.formula(paste0(outcome, " ~ i(h, treated, ref = -1) | NHGISCODE + acs_year"))
  tryCatch(
    feols(fml, data = df, cluster = ~county_cluster,
          panel.id = ~NHGISCODE + acs_year),
    error = function(e) { message("  [ERROR] ", conditionMessage(e)); NULL }
  )
}

extract_es_df <- function(fit, outcome, label, scale = 1) {
  if (is.null(fit)) return(NULL)
  cn   <- names(coef(fit))
  ci95 <- confint(fit, level = 0.95)
  keep <- grepl("^h::", cn)
  h_vals <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn[keep]))
  data.frame(
    stratum  = label,
    outcome  = outcome,
    h        = h_vals,
    coef     = coef(fit)[keep] * scale,
    ci_lo    = ci95[keep, 1] * scale,
    ci_hi    = ci95[keep, 2] * scale,
    se       = sqrt(diag(vcov(fit)))[keep] * scale,
    stringsAsFactors = FALSE
  )
}

att_scalar <- function(es, scale = 1) {
  post <- es[es$h >= 0, ]
  if (nrow(post) == 0) return(c(att = NA, se_att = NA))
  att   <- mean(post$coef / scale) * scale
  se_att <- max(post$se / scale) * scale
  c(att = att, se_att = se_att)
}

# ── Build analysis datasets ────────────────────────────────────────────────────
build_df <- function(stratum_spec) {
  fire <- read.csv(file.path(proc, stratum_spec$fire_file),
                   stringsAsFactors = FALSE, check.names = FALSE)
  wts  <- read.csv(file.path(proc, stratum_spec$wts_file),
                   stringsAsFactors = FALSE, check.names = FALSE)
  wts_slim <- wts[, c("GISJOIN", "ipw_weight")]  # drop duplicate 'treated' column

  df <- panel |>
    merge(fire,     by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE) |>
    merge(wts_slim, by.x = "NHGISCODE", by.y = "GISJOIN", all.x = TRUE)
  df <- df[!is.na(df$treated) & (df$treated == 1 |
             (!is.na(df$never_treated) & df$never_treated == 1)), ]
  df$county_cluster <- ifelse(!is.na(df$COUNTYFP10), df$COUNTYFP10, df$COUNTYFP)
  df
}

# ── County block bootstrap for one stratum at given outcome ───────────────────
bootstrap_att <- function(df, outcome, B = BOOT_REPS, scale = 1, seed = 42) {
  set.seed(seed)
  counties <- unique(df$county_cluster[!is.na(df$county_cluster)])
  if (length(counties) < 10) {
    message("  [WARN] <10 county clusters; bootstrap unreliable.")
    return(rep(NA, B))
  }

  boot_atts <- numeric(B)
  fml <- as.formula(paste0(outcome, " ~ i(h, treated, ref = -1) | NHGISCODE + acs_year"))

  for (b in seq_len(B)) {
    # Sample counties with replacement
    samp_counties <- sample(counties, length(counties), replace = TRUE)
    # Expand to all tracts × periods in those counties
    boot_df <- do.call(
      rbind,
      lapply(seq_along(samp_counties), function(i) {
        sub <- df[df$county_cluster == samp_counties[i], ]
        if (nrow(sub) == 0) return(NULL)
        sub$county_boot <- paste0(samp_counties[i], "_", i)
        sub
      })
    )
    if (is.null(boot_df) || nrow(boot_df) < 10) { boot_atts[b] <- NA; next }

    fit <- tryCatch(
      feols(fml, data = boot_df, cluster = ~county_boot,
            panel.id = ~NHGISCODE + acs_year),
      error = function(e) NULL
    )
    if (is.null(fit)) { boot_atts[b] <- NA; next }

    cn   <- names(coef(fit))
    keep <- grepl("^h::", cn)
    h_b  <- as.integer(gsub(".*::(-?[0-9]+).*", "\\1", cn[keep]))
    post <- coef(fit)[keep][h_b >= 0]
    boot_atts[b] <- if (length(post) > 0) mean(post) * scale else NA
  }
  boot_atts
}

# ── Main loop ──────────────────────────────────────────────────────────────────
all_es   <- list()
all_atts <- list()
boot_dists <- list()   # for heterogeneity test
dfs <- list()          # cache built datasets

for (st in STRATA) {
  label <- st$label
  cat(sprintf("\n%s\n", strrep("-", 60)))
  cat(sprintf("Stratum: %s  (%s)\n", label, st$desc))
  if (st$thin_ctrl) cat("  [WARNING] Only 51 controls in this stratum — results are exploratory.\n")

  df <- build_df(st)
  dfs[[label]] <- df

  n_treated <- sum(df$treated == 1 & df$acs_year == 2014, na.rm = TRUE)
  n_ctrl    <- sum(!is.na(df$never_treated) & df$never_treated == 1 &
                   df$acs_year == 2014, na.rm = TRUE)
  cat(sprintf("  Treated: %d  |  Controls: %d\n", n_treated, n_ctrl))

  for (outcome in OUTCOMES) {
    scale <- if (outcome == "log_med_income_2020") 1 else 100
    fit   <- run_es(outcome, df)
    es    <- extract_es_df(fit, outcome, label, scale = scale)
    if (is.null(es)) next

    all_es[[length(all_es) + 1]] <- es

    v <- att_scalar(es, scale = scale)
    all_atts[[length(all_atts) + 1]] <- data.frame(
      stratum       = label,
      stratum_desc  = st$desc,
      thin_ctrl     = st$thin_ctrl,
      outcome       = outcome,
      n_treated     = n_treated,
      n_ctrl        = n_ctrl,
      att           = v["att"],
      se_att        = v["se_att"],
      ci_lo         = v["att"] - 1.96 * v["se_att"],
      ci_hi         = v["att"] + 1.96 * v["se_att"],
      beta_m2       = es$coef[es$h == -2][1],
      beta_m2_ci_lo = es$ci_lo[es$h == -2][1],
      beta_m2_ci_hi = es$ci_hi[es$h == -2][1],
      stringsAsFactors = FALSE
    )
    cat(sprintf("  %-22s ATT=%+.3f  beta(-2)=%+.3f [%+.3f,%+.3f]\n",
                outcome, v["att"], es$coef[es$h==-2][1],
                es$ci_lo[es$h==-2][1], es$ci_hi[es$h==-2][1]))
  }

  # Bootstrap for in_migration_rate (primary outcome)
  if (!st$thin_ctrl) {
    cat(sprintf("  Bootstrap ATT (%d reps) for in_migration_rate ...\n", BOOT_REPS))
    b_dist <- bootstrap_att(df, "in_migration_rate", B = BOOT_REPS,
                            scale = 100, seed = 42 + which(sapply(STRATA, `[[`, "label") == label))
    boot_dists[[label]] <- b_dist
    cat(sprintf("  Bootstrap ATT mean: %+.3f  SD: %.3f\n",
                mean(b_dist, na.rm = TRUE), sd(b_dist, na.rm = TRUE)))
  }
}

# ── Formal heterogeneity test: ATT1 - ATT0 ────────────────────────────────────
cat("\n--- Heterogeneity test: ATT(strat_1) - ATT(strat_0) ---\n")
if (!is.null(boot_dists[["strat_0"]]) && !is.null(boot_dists[["strat_1"]])) {
  diff_dist <- boot_dists[["strat_1"]] - boot_dists[["strat_0"]]
  diff_point <- mean(diff_dist, na.rm = TRUE)
  diff_se    <- sd(diff_dist, na.rm = TRUE)
  p_two_sided <- 2 * min(
    mean(diff_dist >= 0, na.rm = TRUE),
    mean(diff_dist <= 0, na.rm = TRUE)
  )
  cat(sprintf("  ATT1 - ATT0 (bootstrap): %+.3f pp\n", diff_point))
  cat(sprintf("  Bootstrap SE:            %.3f pp\n", diff_se))
  cat(sprintf("  95%% CI:                  [%+.3f, %+.3f]\n",
              diff_point - 1.96 * diff_se, diff_point + 1.96 * diff_se))
  cat(sprintf("  Two-sided p-value:       %.3f\n", p_two_sided))

  het_test <- data.frame(
    comparison   = "ATT1 - ATT0",
    diff_est     = diff_point,
    diff_se      = diff_se,
    ci_lo        = diff_point - 1.96 * diff_se,
    ci_hi        = diff_point + 1.96 * diff_se,
    p_two_sided  = p_two_sided,
    n_boot_valid = sum(!is.na(diff_dist)),
    outcome      = "in_migration_rate",
    stringsAsFactors = FALSE
  )
  write.csv(het_test, file.path(res_dir, "heterogeneity_test.csv"), row.names = FALSE)
  cat("  [OK] Saved: results/heterogeneity_test.csv\n")
} else {
  cat("  [SKIP] Bootstrap not available for both strata.\n")
}

# ── Save tables ────────────────────────────────────────────────────────────────
all_es_df  <- do.call(rbind, all_es)
all_att_df <- do.call(rbind, all_atts)

write.csv(all_es_df,  file.path(res_dir, "heterogeneity_es_coefs.csv"),  row.names = FALSE)
write.csv(all_att_df, file.path(res_dir, "heterogeneity_strata_atts.csv"), row.names = FALSE)
cat("\n[OK] Saved: results/heterogeneity_strata_atts.csv\n")

# ── Figure: three-panel event-study plot ──────────────────────────────────────
cat("\nGenerating event-study figure ...\n")

es_imig <- all_es_df[all_es_df$outcome == "in_migration_rate", ]
es_imig$stratum_label <- factor(
  es_imig$stratum,
  levels = c("strat_0", "strat_1", "strat_2p"),
  labels = c("Stratum 0: 0 prior fire years\n(N=218 treated, N=36k controls)",
             "Stratum 1: 1 prior fire year\n(within-stratum IPW)",
             "Stratum 2+: 2+ prior fire years\n[Thin controls: N=51]")
)

n_treated_by_stratum <- sapply(all_atts, function(x) {
  if (x$outcome == "in_migration_rate") x$n_treated else NULL
})

dodge <- 0.2
p <- ggplot(es_imig[!is.na(es_imig$stratum_label), ],
            aes(x = h, y = coef, ymin = ci_lo, ymax = ci_hi)) +
  geom_hline(yintercept = 0, colour = "grey60", linewidth = 0.4) +
  geom_vline(xintercept = -0.5, colour = "grey40", linetype = "dashed", linewidth = 0.4) +
  geom_ribbon(alpha = 0.15, fill = "#1f77b4") +
  geom_line(colour = "#1f77b4", linewidth = 0.7) +
  geom_point(aes(shape = stratum == "strat_2p"),
             colour = "#1f77b4", size = 2.2) +
  scale_shape_manual(values = c(`FALSE` = 19, `TRUE` = 17), guide = "none") +
  facet_wrap(~stratum_label, ncol = 1) +
  scale_x_continuous(
    breaks = -3:2,
    labels = c("h=-3\n(ACS 2010)", "h=-2\n(ACS 2012)", "h=-1\n(ACS 2014, ref)",
               "h=0\n(ACS 2022)", "h=+1\n(ACS 2023)", "h=+2\n(ACS 2024)")
  ) +
  labs(
    title    = "Event-Study DiD: In-Migration Rate by Prior Fire Stratum",
    subtitle = "Single-cohort DiD with stratum-specific PS-IPW; SE clustered by county",
    x        = "Years relative to fire (event-study horizon h)",
    y        = "Coefficient (percentage points)",
    caption  = paste0(
      "Note: Stratum 2+ has only 51 matched controls after WFP floor (≥40th pct); ",
      "estimates are reported for completeness but are not suitable for causal inference.\n",
      "Reference period h=−1 (ACS 2014) normalised to zero. Shaded band = 95% CI."
    )
  ) +
  theme_bw(base_size = 10) +
  theme(
    panel.grid.minor  = element_blank(),
    strip.background  = element_rect(fill = "grey92", colour = NA),
    strip.text        = element_text(size = 9, face = "bold"),
    plot.caption      = element_text(size = 7, hjust = 0, colour = "grey40"),
    plot.title        = element_text(size = 11, face = "bold"),
    plot.subtitle     = element_text(size = 9, colour = "grey30")
  )

fig_path <- file.path(res_dir, "fig_firecount_heterogeneity.png")
ggsave(fig_path, plot = p, width = 7, height = 9, dpi = 300)
cat(sprintf("[OK] Saved: %s\n", fig_path))

# ── Print summary table ────────────────────────────────────────────────────────
cat("\n--- ATT summary: in_migration_rate by stratum ---\n")
imig_att <- all_att_df[all_att_df$outcome == "in_migration_rate", ]
cat(sprintf("  %-10s  %5s  %5s  %8s  %16s  %8s  %s\n",
            "Stratum", "N_trt", "N_ctr", "ATT(pp)", "95% CI", "beta(-2)", "Note"))
for (i in seq_len(nrow(imig_att))) {
  r <- imig_att[i, ]
  note <- if (r$thin_ctrl) "(thin controls)" else ""
  cat(sprintf("  %-10s  %5d  %5d  %+7.3f  [%+6.3f,%+6.3f]  %+7.3f  %s\n",
              r$stratum, r$n_treated, r$n_ctrl,
              r$att, r$ci_lo, r$ci_hi, r$beta_m2, note))
}

cat("\n[DONE] 07_firecount_heterogeneity.R\n")
