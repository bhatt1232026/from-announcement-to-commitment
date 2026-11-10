#!/usr/bin/env bash
# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
#
# Reproduces every result, table input and figure of the article from data/inputs.
# Usage: bash run_all.sh      (about one to two minutes on a standard laptop)
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
"$PY" src/01_completeness_search.py
"$PY" src/02_us_primary_analysis.py
"$PY" src/03_us_supplementary_analyses.py
"$PY" src/04_us_companion_robustness.py
"$PY" src/05_regulatory_visibility.py
"$PY" src/06_china_contrast.py
"$PY" src/07_rolling_origin_stage_model.py
"$PY" src/08_brier_benchmark_inference.py
"$PY" src/09_incumbent_panel_support.py
"$PY" src/10_summary_tables.py
"$PY" src/11_paper_figures.py
"$PY" -m pytest -q tests
echo "All steps completed."
