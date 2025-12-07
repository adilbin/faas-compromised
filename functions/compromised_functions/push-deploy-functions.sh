#!/bin/bash

# Script to push and/or deploy OpenFaaS functions using faas-cli
# Comment out functions you don't want to process by adding # at the start of the line

set -e  # Exit on error

# =============================================================================
# FUNCTION LIST - Comment out functions you don't want to push/deploy
# =============================================================================
FUNCTIONS=(
    decisiontree-classifier-fileop-type
    decisiontree-classifier-info-type
    kmeans-clustering-code-type
    kmeans-clustering-command-type
    kmeans-clustering-fileop-type
    kmeans-clustering-info-type
    time-series-forecaster-code-type
    time-series-forecaster-command-type
    time-series-forecaster-fileop-type
    time-series-forecaster-info-type
)

# =============================================================================
# SCRIPT LOGIC - No need to modify below this line
# =============================================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "Functions to process:"
for func in "${FUNCTIONS[@]}"; do
    echo "  - $func"
done
echo ""

echo "What would you like to do?"
echo "  1) Publish (build + push)"
echo "  2) Push only (no build)"
echo "  3) Deploy only"
echo "  4) Publish and Deploy"
echo ""
read -p "Enter your choice [1-4]: " choice

if [[ ! "$choice" =~ ^[1-4]$ ]]; then
    echo -e "${RED}Invalid choice. Exiting.${NC}"
    exit 1
fi

echo ""
read -p "Continue with ${#FUNCTIONS[@]} function(s)? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""

for func in "${FUNCTIONS[@]}"; do
    yaml_file="${func}.yaml"
    
    if [ ! -f "$yaml_file" ]; then
        echo -e "${RED}[ERROR] ${yaml_file} not found. Skipping.${NC}"
        continue
    fi
    
    echo -e "${YELLOW}Processing: ${func}${NC}"
    
    case $choice in
        1)  faas-cli publish -f "$yaml_file" ;;
        2)  faas-cli push -f "$yaml_file" ;;
        3)  faas-cli deploy -f "$yaml_file" ;;
        4)  faas-cli up -f "$yaml_file" ;;
    esac
    
    echo -e "${GREEN}[DONE] ${func}${NC}"
    echo ""
done

echo "All done!"
