#!/bin/bash

# Script to remove all running OpenFaaS functions using faas-cli

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Fetching list of deployed functions..."
echo ""

# Get list of deployed functions (quiet mode returns just names)
functions=$(faas-cli list -q 2>/dev/null)

if [ -z "$functions" ]; then
    echo -e "${YELLOW}No functions currently deployed.${NC}"
    exit 0
fi

echo "Functions to remove:"
echo "$functions" | while read -r func; do
    echo "  - $func"
done
echo ""

read -p "Are you sure you want to remove all functions? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Remove each function
echo "$functions" | while read -r func; do
    if [ -n "$func" ]; then
        echo -e "${YELLOW}Removing: ${func}${NC}"
        if faas-cli remove "$func" 2>/dev/null; then
            echo -e "${GREEN}[DONE] Removed ${func}${NC}"
        else
            echo -e "${RED}[ERROR] Failed to remove ${func}${NC}"
        fi
        echo ""
    fi
done

echo "All done!"
