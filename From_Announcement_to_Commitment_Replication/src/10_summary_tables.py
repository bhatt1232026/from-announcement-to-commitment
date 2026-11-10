# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Summary tables and figure data, built from the result files of steps 02 to 09 only.
No model is estimated here.

Outputs (results/):
  headline_results.csv              key numbers reported in the abstract and Section 5
  robustness_coefficients.csv       entrant coefficients and 95% intervals across specifications (Figure 2)
  brier_comparisons.csv             stage model versus base-rate benchmarks (Figure 6)
  expected_capacity_decomposition.csv  composition of foreign expected-capacity movement (Figure 7)
  results_summary.json              compact machine-readable summary
Usage: python src/10_summary_tables.py
"""
import json
import re

import pandas as pd

from common import CONFIG, PANEL, RESULTS, ROLLING

p = pd.read_csv(RESULTS / "us_primary_and_checks.csv")
rb = pd.read_csv(RESULTS / "us_companion_robustness.csv")
s = pd.read_csv(RESULTS / "us_supplementary.csv")
rv = pd.read_csv(RESULTS / "regulatory_visibility.csv")
ch = pd.read_csv(RESULTS / "china_contrast.csv").iloc[0]
br = pd.read_csv(ROLLING / "brier_bootstrap.csv")
g3 = json.loads((PANEL / "support_summary.json").read_text())
fn = pd.read_csv(PANEL / "foreign_chain_month_news.csv")
p0 = p.iloc[0]


def parse_ci(value):
    numbers = re.findall(r"-?\d+\.\d+", str(value))[:2]
    return float(numbers[0]), float(numbers[1])


# ---- Figure 2 data: entrant coefficient across specifications
rows = []
for r in p.itertuples():
    if r.sample.startswith("C5 leave out methanol"):
        continue
    label = r.sample.split(":")[0].replace("PRIMARY", "Primary")
    category = "Primary" if label.startswith("Primary") else "Pre-specified"
    rows.append((label, r.b_entrant, r.ci95_lo, r.ci95_hi, r.n, category))
for r in rb.itertuples():
    if r.analysis.startswith(("RB2", "RB3", "RB4", "RB5")):
        lo, hi = parse_ci(r.ci95)
        rows.append((r.analysis, r.estimate, lo, hi, r.n, "Companion"))
s1 = s[s["sample"].str.startswith("S1")].iloc[0]
lo, hi = parse_ci(s1.ci)
rows.append(("S1 brownfield only", s1.b, lo, hi, s1.n, "Supplementary"))
v = rv[rv.analysis.str.startswith("RV3 primary")].iloc[0]
lo, hi = parse_ci(v.note)
rows.append(("Regulatory-filing subset", v.value, lo, hi, v.n, "Regulatory"))
pd.DataFrame(rows, columns=["specification", "b", "ci_lo", "ci_hi", "n", "category"]).to_csv(
    RESULTS / "robustness_coefficients.csv", index=False)

# ---- Figure 6 data: Brier comparisons
bb = br[(br.metric == "brier") & br.comparison.isin(["rolling_stage - unconditional", "rolling_stage - chain_base"])].copy()
bb.to_csv(RESULTS / "brier_comparisons.csv", index=False)

# ---- Figure 7 data: composition of gross foreign expected-capacity movement
parts = {
    "Project information": float(fn.F_news_tpa.abs().sum()),
    "Commissioning exit": float(fn.F_commission_tpa.abs().sum()),
    "Model recalibration": float(fn.F_drift_tpa.abs().sum()),
}
total = sum(parts.values())
news = pd.DataFrame({"component": list(parts), "gross_abs_tpa": list(parts.values()),
                     "share_percent": [100 * x / total for x in parts.values()]})
news.to_csv(RESULTS / "expected_capacity_decomposition.csv", index=False)

# ---- Headline numbers
headline = [
    {"result": "U.S. primary sample projects", "value": int(p0.n), "unit": "projects"},
    {"result": "Incumbent commitment rate", "value": round(100 * p0.commit_rate_incumbent, 1), "unit": "percent"},
    {"result": "Entrant commitment rate", "value": round(100 * p0.commit_rate_entrant, 1), "unit": "percent"},
    {"result": "Adjusted entrant coefficient", "value": float(p0.b_entrant), "unit": "probability points"},
    {"result": "Adjusted coefficient 95% CI lower", "value": float(p0.ci95_lo), "unit": "probability points"},
    {"result": "Adjusted coefficient 95% CI upper", "value": float(p0.ci95_hi), "unit": "probability points"},
    {"result": "Within-chain permutation p", "value": float(p0.perm_p_within_chain), "unit": "p-value"},
    {"result": "China established realization rate", "value": round(100 * ch.realized_established, 1), "unit": "percent"},
    {"result": "China newcomer realization rate", "value": round(100 * ch.realized_newcomer, 1), "unit": "percent"},
    {"result": "Incumbent panel fixed-effect support sufficient", "value": str(g3["support_gate_pass"]), "unit": "boolean"},
]
pd.DataFrame(headline).to_csv(RESULTS / "headline_results.csv", index=False)

summary = {
    "study": CONFIG["study"],
    "authors": CONFIG["authors"],
    "us_primary": {"n": int(p0.n), "incumbent_rate": float(p0.commit_rate_incumbent), "entrant_rate": float(p0.commit_rate_entrant),
                   "b": float(p0.b_entrant), "ci95": [float(p0.ci95_lo), float(p0.ci95_hi)], "perm_p": float(p0.perm_p_within_chain)},
    "china_direction_consistent": bool(ch.direction_consistent),
    "incumbent_panel_support_sufficient": bool(g3["support_gate_pass"]),
    "incumbent_panel_outcome_model_estimated": bool(g3["outcome_model_estimated"]),
    "brier_stage_vs_chain_significant_any_horizon": bool((bb[bb.comparison.eq("rolling_stage - chain_base")].significant == True).any()),
    "brier_stage_vs_unconditional_significant_any_horizon": bool((bb[bb.comparison.eq("rolling_stage - unconditional")].significant == True).any()),
    "foreign_movement_composition_percent": dict(zip(news.component, news.share_percent.round(2))),
}
(RESULTS / "results_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
