#!/bin/bash
# Run the complete Ethereum Governance Analysis

# Default mode
NO_PLOTS=""

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --no-plots)
      NO_PLOTS="--no-plots"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: ./run_analysis.sh [--no-plots]"
      exit 1
      ;;
  esac
done

# Update submodules only if needed
if ! git submodule status | grep -q '^+'; then
    echo "Submodules already up to date, skipping update"
else
    echo "Submodules need updating..."
    git submodule update --remote --recursive
fi

# Record submodule commit hashes for reproducibility
EIPS_COMMIT=$(cd data/EIPs && git rev-parse HEAD)
PM_COMMIT=$(cd data/pm && git rev-parse HEAD)

# Update specs_versions.yml with commit hashes
sed -i '' "s|commit: # To be filled after running the analysis|commit: $EIPS_COMMIT|g" specs_versions.yml
sed -i '' "s|commit: # To be filled after running the analysis|commit: $PM_COMMIT|g" specs_versions.yml

echo "Running EIP analysis..."
python src/parse_eips.py --source data/EIPs --output output/authors.csv

echo "Running core dev meeting analysis..."
python src/parse_core_devs.py --source data/pm --output output/core_dev_attendance.csv

echo "Computing Nakamoto coefficients..."
python src/compute_nakamoto.py --input output/authors.csv \
  --client-data data/client_stats.json \
  --staking-data data/staking_distribution.csv \
  --output output/nakamoto.csv $NO_PLOTS

echo "Analysis complete. Results available in the output directory."
echo "Nakamoto coefficients:"
cat output/nakamoto.csv 