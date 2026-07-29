"""
Project setup and environment configuration.
Run once at project start to create directories and verify data paths.
"""

import os
from pathlib import Path


def create_directory_structure():
    """Create required directories if missing."""
    base = Path(__file__).parent.parent.parent  # wildfire-poverty-analysis root

    dirs = [
        base / "data" / "raw" / "acs_extracts",
        base / "data" / "raw" / "mtbs_perimeters",
        base / "data" / "raw" / "whp_rasters",
        base / "data" / "raw" / "county_shapefiles",
        base / "data" / "processed",
        base / "data" / "metadata",
        base / "results" / "tables",
        base / "results" / "figures",
        base / "results" / "rds",
        base / "notebooks",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Directory ready: {d.relative_to(base)}")

    return base


def verify_upstream_data():
    """Check if wildfire-finance data is available for symlink/reuse."""
    upstream = Path(__file__).parent.parent.parent.parent / "wildfire-finance" / "data" / "raw"

    checks = {
        "MTBS": upstream / "mtbs_perims",
        "WFP 2012": upstream / "WHP" / "Data" / "wfp_2012_continuous",
    }

    print("\nUpstream data availability:")
    for name, path in checks.items():
        if path.exists():
            print(f"  [FOUND] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: NOT FOUND at {path}")
            print(f"    -> Will need to download separately")

    return checks


def main():
    print("=" * 60)
    print("WILDFIRE-POVERTY-ANALYSIS: Project Setup")
    print("=" * 60)

    base = create_directory_structure()
    print(f"\nProject root: {base}\n")

    verify_upstream_data()

    print("\n" + "=" * 60)
    print("Setup complete. Ready for Week 1 data assembly.")
    print("=" * 60)


if __name__ == "__main__":
    main()
