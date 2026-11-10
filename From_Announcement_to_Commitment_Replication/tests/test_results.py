# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Checks that a fresh run reproduces the numbers reported in the article."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"


def test_primary_counts_and_estimate():
    p = pd.read_csv(RES / "us_primary_and_checks.csv").iloc[0]
    assert int(p.n) == 76
    assert int(p.n_incumbent) == 48 and int(p.n_entrant) == 28
    assert round(float(p.commit_rate_incumbent), 3) == round(46 / 48, 3)
    assert round(float(p.commit_rate_entrant), 3) == round(11 / 28, 3)
    assert round(float(p.b_entrant), 3) == -0.392
    assert (float(p.ci95_lo), float(p.ci95_hi)) == (-0.625, -0.159)
    assert float(p.perm_p_within_chain) == 0.0001


def test_permutation_pvalues_are_never_zero():
    p = pd.read_csv(RES / "us_primary_and_checks.csv")
    assert (p.perm_p_within_chain > 0).all()
    rb = pd.read_csv(RES / "us_companion_robustness.csv")
    perm = rb[rb.analysis.str.contains("permutation|Freedman", case=False, regex=True)]
    assert (perm.p.dropna() > 0).all()


def test_decision_criteria():
    c = json.loads((RES / "us_decision_criteria.json").read_text())
    assert c["ALL_CRITERIA_MET (R1-R4)"] is True


def test_chain_benchmark_not_significant():
    b = pd.read_csv(RES / "rolling_origin" / "brier_bootstrap.csv")
    q = b[(b.metric == "brier") & (b.comparison == "rolling_stage - chain_base")]
    assert len(q) == 3
    assert not q.significant.astype(bool).any()
    assert (q["diff"] < 0).all()


def test_regulatory_subset_and_interpretation():
    r = pd.read_csv(RES / "regulatory_visibility.csv")
    cov = r[r.analysis == "RV1 coverage"].set_index("group")
    assert int(round(cov.loc["incumbent", "value"] * 48)) == 16
    assert int(round(cov.loc["entrant", "value"] * 28)) == 17
    verdict = r[r.analysis == "Interpretation rule"].note.iloc[0]
    assert "incomplete and unequal filing coverage" in verdict


def test_china_direction_differs():
    c = pd.read_csv(RES / "china_contrast.csv").iloc[0]
    assert float(c.realized_newcomer) > float(c.realized_established)
    assert bool(c.direction_consistent) is False


def test_incumbent_panel_not_estimated():
    g = json.loads((RES / "incumbent_panel" / "support_summary.json").read_text())
    assert g["support_gate_pass"] is False
    assert g["selected_specification"] == "STOP"
    assert g["outcome_model_estimated"] is False


def test_all_figures_present():
    figs = sorted(p.name for p in (RES / "figures").glob("figure*.png"))
    assert len(figs) == 7
