# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Shared paths and settings used by every analysis script."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data" / "inputs"
DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
ROLLING = RESULTS / "rolling_origin"
PANEL = RESULTS / "incumbent_panel"
FIGURES = RESULTS / "figures"

CONFIG = json.loads((ROOT / "config" / "analysis_config.json").read_text())
SEED = int(CONFIG["random_seed"])
NPERM = int(CONFIG["permutation_draws"])

for _d in (DERIVED, RESULTS, ROLLING, PANEL, FIGURES):
    _d.mkdir(parents=True, exist_ok=True)
