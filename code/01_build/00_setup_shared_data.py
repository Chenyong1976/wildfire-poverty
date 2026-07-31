#!/usr/bin/env python3
"""
Setup shared data from wildfire-health project.
Creates symlinks or copies to critical shared datasets.
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
WILDFIRE_HEALTH = PROJECT_ROOT.parent / "wildfire-health"
DATA_RAW = PROJECT_ROOT / "data" / "raw"

def setup_symlinks():
    """Create symlinks (or copies on Windows) to shared data."""

    DATA_RAW.mkdir(parents=True, exist_ok=True)

    # MTBS perimeters
    mtbs_source = WILDFIRE_HEALTH / "data" / "raw" / "mtbs_perims"
    mtbs_target = DATA_RAW / "mtbs_perimeters"

    if mtbs_source.exists():
        if mtbs_target.exists():
            print(f"[OK] MTBS already linked/copied: {mtbs_target}")
        else:
            try:
                # Try symlink first
                mtbs_target.symlink_to(mtbs_source)
                print(f"[OK] Created symlink: {mtbs_target}")
            except (OSError, NotImplementedError):
                # Fall back to copy (Windows without symlink privilege)
                shutil.copytree(mtbs_source, mtbs_target, dirs_exist_ok=True)
                print(f"[OK] Copied (symlink unavailable): {mtbs_target}")
    else:
        print(f"[MISSING] MTBS source not found: {mtbs_source}")

    # WHP 2018 raster
    whp2018_source = WILDFIRE_HEALTH / "data" / "raw" / "WHP" / "Data" / "whp_2018_continuous"
    whp2018_target = DATA_RAW / "whp_rasters" / "whp_2018_continuous"

    whp2018_target.parent.mkdir(parents=True, exist_ok=True)

    if whp2018_source.exists():
        if whp2018_target.exists():
            print(f"[OK] WHP 2018 already linked/copied: {whp2018_target}")
        else:
            try:
                whp2018_target.symlink_to(whp2018_source)
                print(f"[OK] Created symlink: {whp2018_target}")
            except (OSError, NotImplementedError):
                shutil.copytree(whp2018_source, whp2018_target, dirs_exist_ok=True)
                print(f"[OK] Copied (symlink unavailable): {whp2018_target}")
    else:
        print(f"[MISSING] WHP 2018 source not found: {whp2018_source}")

    # WHP 2014 raster (for robustness)
    whp2014_source = WILDFIRE_HEALTH / "data" / "raw" / "WHP" / "Data" / "whp_2014_continuous"
    whp2014_target = DATA_RAW / "whp_rasters" / "whp_2014_continuous"

    if whp2014_source.exists():
        if whp2014_target.exists():
            print(f"[OK] WHP 2014 already linked/copied: {whp2014_target}")
        else:
            try:
                whp2014_target.symlink_to(whp2014_source)
                print(f"[OK] Created symlink: {whp2014_target}")
            except (OSError, NotImplementedError):
                shutil.copytree(whp2014_source, whp2014_target, dirs_exist_ok=True)
                print(f"[OK] Copied (symlink unavailable): {whp2014_target}")
    else:
        print(f"[INFO] WHP 2014 not found (optional): {whp2014_source}")

    print("\n[OK] Shared data setup complete")

if __name__ == "__main__":
    setup_symlinks()
