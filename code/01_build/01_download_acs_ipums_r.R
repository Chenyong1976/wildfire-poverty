#!/usr/bin/env Rscript
# Download IPUMS ACS data using ipumsr package
# Install: install.packages("ipumsr")

library(ipumsr)

# Set IPUMS API key
Sys.setenv(IPUMS_API_KEY = "59cba10d8a5da536fc06b59db19b0b9e06294acea3c72932868ac9d3")

# Output directory
output_dir <- "data/raw/acs_extracts"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Define IPUMS samples and variables
samples <- c("us2012a", "us2017a", "us2023a")  # ACS 2012, 2017, 2023
years <- c(2012, 2017, 2023)

variables <- c(
  "B17001",  # Poverty status
  "B19013",  # Median household income
  "B23025",  # Employment status
  "B07001"   # Residence 5 years ago
)

# Download each year
for (i in seq_along(samples)) {
  sample <- samples[i]
  year <- years[i]

  cat(sprintf("\n[%s] Downloading ACS %d (sample: %s)\n", Sys.time(), year, sample))

  # Define extract
  extract <- define_extract(
    project = "usa",
    samples = sample,
    variables = variables
  )

  # Submit extract
  cat("Submitting extract...\n")
  submitted_extract <- submit_extract(extract)

  # Wait for completion
  cat("Waiting for extract to complete...\n")
  completed_extract <- wait_for_extract(submitted_extract)

  # Download data
  output_file <- file.path(output_dir, sprintf("acs_%d_tract_extract.csv", year))
  cat(sprintf("Downloading to %s...\n", output_file))

  acs_data <- download_extract(completed_extract, file = output_file)

  cat(sprintf("[OK] Downloaded %d rows\n", nrow(acs_data)))
}

cat("\n[OK] All ACS downloads complete!\n")
