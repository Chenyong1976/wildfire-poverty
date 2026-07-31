#!/bin/bash
# Setup symlinks to shared data from wildfire-finance project
# Run this script from the project root directory

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_RAW="$PROJECT_ROOT/data/raw"

WILDFIRE_FINANCE_ROOT="$PROJECT_ROOT/../../wildfire-finance"

echo "=========================================="
echo "SETUP SYMLINKS TO WILDFIRE-FINANCE DATA"
echo "=========================================="

# Verify wildfire-finance exists
if [ ! -d "$WILDFIRE_FINANCE_ROOT" ]; then
    echo "Error: wildfire-finance project not found at $WILDFIRE_FINANCE_ROOT"
    exit 1
fi

# Create symlink for MTBS perimeters
MTBS_SOURCE="$WILDFIRE_FINANCE_ROOT/data/raw/mtbs_perims"
MTBS_LINK="$DATA_RAW/mtbs_perimeters"

if [ -d "$MTBS_SOURCE" ]; then
    if [ -L "$MTBS_LINK" ] && [ -e "$MTBS_LINK" ]; then
        echo "✓ MTBS symlink already exists: $MTBS_LINK"
    elif [ ! -e "$MTBS_LINK" ]; then
        ln -s "$MTBS_SOURCE" "$MTBS_LINK"
        echo "✓ Created MTBS symlink: $MTBS_LINK"
    else
        echo "✗ MTBS path exists but is not a valid symlink: $MTBS_LINK"
        exit 1
    fi
else
    echo "✗ MTBS source not found: $MTBS_SOURCE"
    exit 1
fi

# Create symlink for WFP 2012 raster
WFP2012_SOURCE="$WILDFIRE_FINANCE_ROOT/data/raw/WHP/Data/wfp_2012_continuous"
WFP2012_LINK="$DATA_RAW/whp_rasters/wfp_2012_continuous"

if [ -d "$WFP2012_SOURCE" ]; then
    mkdir -p "$(dirname "$WFP2012_LINK")"
    if [ -L "$WFP2012_LINK" ] && [ -e "$WFP2012_LINK" ]; then
        echo "✓ WFP2012 symlink already exists: $WFP2012_LINK"
    elif [ ! -e "$WFP2012_LINK" ]; then
        ln -s "$WFP2012_SOURCE" "$WFP2012_LINK"
        echo "✓ Created WFP2012 symlink: $WFP2012_LINK"
    else
        echo "✗ WFP2012 path exists but is not a valid symlink: $WFP2012_LINK"
        exit 1
    fi
else
    echo "✗ WFP2012 source not found: $WFP2012_SOURCE"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All symlinks created successfully"
echo "=========================================="
