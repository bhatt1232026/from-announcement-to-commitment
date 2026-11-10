# From Announcement to Commitment: Market Incumbency and the Credibility of U.S. Petrochemical Capacity Plans

Replication package

**Authors**

- Vivek Bhatt, PregleAI Research & Smart Solutions, India (corresponding author; bhatt123@gmail.com; ORCID 0009-0003-0495-8902)
- Kapil Dwivedi, PregleAI Research & Smart Solutions, India (kapildbackup@gmail.com; ORCID 0009-0005-1224-8112)
- Amaresh Chandra Singh, Isnartech Pvt. Ltd., India (corresponding author; amaresh0787@gmail.com; ORCID 0009-0006-6165-3904)

This repository contains the data, code and analysis plan needed to reproduce every estimate, table
entry and figure in the article. All results are computed from the files in `data/inputs/`; nothing is
copied in by hand.

## Quick start

```bash
python -m pip install -r requirements.txt
bash run_all.sh
```

The full run takes about one to two minutes on a standard laptop. It rewrites `data/derived/` and
`results/`, and ends by running the tests in `tests/`, which check the headline numbers reported in
the article (for example, 76 projects, commitment rates of 95.8% and 39.3%, entrant coefficient
-0.392 with 95% interval [-0.625, -0.159], permutation p = 0.0001).

Random procedures (permutation tests and bootstraps) use the fixed seed in `config/analysis_config.json`,
so repeated runs give identical output.

## Repository structure

```
config/analysis_config.json     seed, permutation draws and rolling-origin settings
data/inputs/                    fixed input data (see data/README.md)
data/derived/                   search logs and completed outcomes written by the scripts
docs/analysis_plan/             analysis plan as fixed, with SHA-256 hashes
src/                            analysis scripts, run in numbered order
results/                        all outputs (tables, intermediate panels, figures)
tests/test_results.py           checks against the numbers reported in the article
run_all.sh                      runs every step
```

## Scripts and where their results appear in the article

| Script | Article section | Tables and figures | Main outputs |
|---|---|---|---|
| `01_completeness_search.py` | 3.1; Appendix S3 | Table 1 | `data/derived/completeness_search_*.csv` |
| `02_us_primary_analysis.py` | 3.2, 4.1 to 4.4, 5.1 to 5.4 | Tables 2 to 4, S3; Figures 1, 3 | `us_project_classification.csv`, `us_primary_and_checks.csv`, `us_sponsor_by_site.csv`, `us_competing_risks.csv` |
| `03_us_supplementary_analyses.py` | 5.3 | Tables 3, S3 | `us_supplementary.csv` |
| `04_us_companion_robustness.py` | 4.2, 5.3 | Tables 3, S3 | `us_companion_robustness.csv` |
| `05_regulatory_visibility.py` | 4.5, 6 | Table 5; Figure 4 | `regulatory_visibility.csv` |
| `06_china_contrast.py` | 7 | Table 6; Figure 5 | `china_contrast.csv`, `china_classification.csv` |
| `07_rolling_origin_stage_model.py` | 8.1 (Equation 4) | | `rolling_origin/predictions.csv`, `rolling_origin/oos_scores.csv` |
| `08_brier_benchmark_inference.py` | 8.1 (Equation 5) | Table 7; Figure 6 | `rolling_origin/brier_bootstrap.csv` |
| `09_incumbent_panel_support.py` | 3.3, 8.2; Appendix S1 | Table S1; Figure 7 | `incumbent_panel/support_summary.json`, `incumbent_panel/fe_support_metrics.csv` |
| `10_summary_tables.py` | | Figures 2, 6, 7 (data) | `headline_results.csv`, `robustness_coefficients.csv` |
| `11_paper_figures.py` | | Figures 1 to 7 | `results/figures/*.png`, `*.pdf` |

Each script can also be run on its own from the repository root (for example,
`python src/05_regulatory_visibility.py`) once the steps it depends on have been run.

## Methods implemented

- Linear probability model of commitment on entrant status, log capacity, greenfield site and
  post-2015 announcement, with HC1 standard errors (Equation 1).
- Two-sided within-chain permutation test of the entrant coefficient, 10,000 draws, with the (B+1)
  Monte Carlo correction (Equation 2); companion permutation within chain by site type and
  Freedman-Lane residual permutation with chain fixed effects.
- Aalen-Johansen cumulative incidence of commitment and cancellation as competing risks (Equation 3).
- Rolling-origin, leave-project-out stage model with project-balanced beta-binomial shrinkage
  (lambda = 4) and monotone stage repair (Equation 4); Brier scores (Equation 5) compared with
  unconditional and chain-specific base rates using a project-clustered bootstrap (2,000 draws).

## Analysis plan

`docs/analysis_plan/` holds the analysis plan in the versions fixed before the completeness search and
before the regulatory collection, and the final version with all logged amendments. Each earlier
version is a byte-exact prefix of the final document; hashes are listed in `SHA256SUMS.txt`.

## Software

Python 3.13 with the package versions in `requirements.txt`. The code runs on Linux, macOS and
Windows (use Git Bash or run the scripts in order on Windows).

## Citation

Please cite the article and this repository; see `CITATION.cff`.
