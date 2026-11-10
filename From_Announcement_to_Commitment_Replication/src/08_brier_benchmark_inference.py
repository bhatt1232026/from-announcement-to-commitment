# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Brier-score comparisons for the rolling-origin stage model (Section 8.1; Table 7; Figure 6; Equation 5).

The chain-specific base-rate benchmark is built to be comparable with the stage estimator:
  * strict rolling origin (only outcome windows closed by the focal origin),
  * focal physical project excluded,
  * repeated project-month observations averaged within physical project first,
  * then equal weight across physical projects,
  * shrinkage (strength 5) toward the focal-specific unconditional rate.
Differences are reported with project-clustered bootstrap intervals (2,000 draws).
The stage-model probabilities themselves are taken unchanged from step 07.

Outputs (results/rolling_origin/): brier_bootstrap.csv, brier_scored_rows.csv, chain_benchmark_audit.csv
Usage: python src/08_brier_benchmark_inference.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import CONFIG, ROLLING, SEED

CFG = CONFIG["rolling_origin"]
SCORE = ROLLING / "oos_scores.csv"
CHAIN_PRIOR_STRENGTH = float(CFG["chain_benchmark_prior_strength"])
BOOT_DRAWS = int(CFG["bootstrap_draws"])
EPS = float(CFG["benchmark_probability_clip"])


def add_months(m: str, h: int) -> str:
    return str(pd.Period(str(m)[:7], "M") + int(h))


def ordm(m: str) -> int:
    return int(pd.Period(str(m)[:7], "M").ordinal)


# One row per scored focal project-month-horizon, carrying the stage and unconditional predictions.
# The chain benchmark is constructed only from previously scoreable evaluation rows. This makes the
# benchmark strictly rolling-origin and avoids importing outcome-selected future rows into its history.
S = pd.read_csv(SCORE, dtype={"snapshot_month": str})
S = S[S.model.isin(["rolling_stage", "unconditional"])].copy()
W = S.pivot_table(
    index=["snapshot_month", "physical_project_id", "product_chain", "horizon_months"],
    columns="model", values=["probability", "y"], aggfunc="first"
).reset_index()
W.columns = ["_".join([c for c in col if c]) for col in W.columns]
W["y"] = W["y_rolling_stage"]
assert np.allclose(W.y_rolling_stage, W.y_unconditional, equal_nan=True)

parts, audit = [], []
for H, g in W.groupby("horizon_months", sort=True):
    H = int(H)
    g = g.copy()
    g["endpoint_month"] = g.snapshot_month.map(lambda x: add_months(x, H))
    g["endpoint_ord"] = g.endpoint_month.map(ordm)
    g["origin_ord"] = g.snapshot_month.map(ordm)
    vals = pd.Series(index=g.index, dtype=float)
    for (chain, origin), current in g.groupby(["product_chain", "snapshot_month"], sort=False):
        oo = ordm(origin)
        hist = g[g.product_chain.astype(str).eq(str(chain)) & g.endpoint_ord.le(oo)]
        byp = hist.groupby("physical_project_id").y.mean()
        total = float(byp.sum()); nall = int(len(byp))
        for idxrow, r in current.iterrows():
            pid = str(r.physical_project_id)
            if pid in byp.index.astype(str):
                # index is already string in the score file; use direct lookup when available.
                try: focal_hist = float(byp.loc[pid])
                except KeyError:
                    focal_hist = 0.0
                n = nall - 1
                raw = (total - focal_hist) / n if n else float(r.probability_unconditional)
            else:
                n = nall
                raw = total / n if n else float(r.probability_unconditional)
            post = (n * raw + CHAIN_PRIOR_STRENGTH * float(r.probability_unconditional)) / (n + CHAIN_PRIOR_STRENGTH)
            vals.loc[idxrow] = post
            audit.append({
                "snapshot_month": r.snapshot_month,
                "physical_project_id": r.physical_project_id,
                "product_chain": r.product_chain,
                "horizon_months": H,
                "eligible_prior_score_projects_same_chain": n,
                "raw_project_balanced_chain_rate": raw,
                "unconditional_probability": float(r.probability_unconditional),
                "probability_chain_base": post,
            })
    g["probability_chain_base"] = vals
    parts.append(g)
W = pd.concat(parts, ignore_index=True)
pd.DataFrame(audit).to_csv(ROLLING / "chain_benchmark_audit.csv", index=False)

for mdl in ["rolling_stage", "unconditional", "chain_base"]:
    p = W[f"probability_{mdl}"].clip(EPS, 1 - EPS)
    W[f"brier_{mdl}"] = (W.y - p) ** 2
    W[f"ll_{mdl}"] = -(W.y * np.log(p) + (1 - W.y) * np.log(1 - p))

rng = np.random.default_rng(SEED)
res = []
for H, gg0 in W.groupby("horizon_months", sort=True):
    gg = gg0.reset_index(drop=True)
    proj = gg.physical_project_id.astype(str).unique()
    idx = {p: np.where(gg.physical_project_id.astype(str).values == p)[0] for p in proj}
    for a, b in [("rolling_stage", "unconditional"), ("rolling_stage", "chain_base"), ("chain_base", "unconditional")]:
        for metric in ["brier", "ll"]:
            d = (gg[f"{metric}_{a}"] - gg[f"{metric}_{b}"]).to_numpy(float)
            # Cluster bootstrap, vectorized: resample physical projects with replacement while
            # retaining all rows belonging to each sampled project.
            cluster_sum = np.array([d[idx[p]].sum() for p in proj], dtype=float)
            cluster_n = np.array([len(idx[p]) for p in proj], dtype=float)
            draw_counts = rng.multinomial(len(proj), np.repeat(1/len(proj), len(proj)), size=BOOT_DRAWS)
            bs = (draw_counts @ cluster_sum) / (draw_counts @ cluster_n)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            res.append({
                "horizon": int(H), "comparison": f"{a} - {b}", "metric": metric,
                "n_rows": len(gg), "n_projects": len(proj), "diff": round(float(d.mean()), 4),
                "ci95_lo": round(float(lo), 4), "ci95_hi": round(float(hi), 4),
                "significant": bool(hi < 0 or lo > 0),
                "bootstrap_draws": BOOT_DRAWS,
            })
    for mdl in ["rolling_stage", "unconditional", "chain_base"]:
        res.append({
            "horizon": int(H), "comparison": f"level {mdl}", "metric": "brier",
            "n_rows": len(gg), "n_projects": len(proj),
            "diff": round(float(gg[f"brier_{mdl}"].mean()), 4),
            "ci95_lo": np.nan, "ci95_hi": np.nan, "significant": np.nan,
            "bootstrap_draws": BOOT_DRAWS,
        })

R = pd.DataFrame(res)
R.to_csv(ROLLING / "brier_bootstrap.csv", index=False)
W.to_csv(ROLLING / "brier_scored_rows.csv", index=False)
print(R.to_string(index=False))
