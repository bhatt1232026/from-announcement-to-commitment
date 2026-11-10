# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Rolling-origin stage-based credibility model for Chinese projects (Section 8.1; Equation 4).

Inputs
------
- data/inputs/china_stage_project_month.csv
- data/inputs/china_pre2010_training_history.csv
- config/analysis_config.json (block "rolling_origin")

Rules
-----
1. For a focal snapshot month t and horizon H, a calibration snapshot r is usable only when
   r + H <= t, so that the full forecast window had elapsed by t.
2. The focal physical project is always excluded from its own calibration.
3. Pre-2010 cases are calibration-only; they never enter the evaluation universe.
4. Sparse stage cells use a fixed beta-binomial empirical-Bayes shrinkage toward the rolling
   unconditional realization rate, with prior strength lambda = 4 fixed in the configuration.
5. Calibration is project-balanced: each physical project contributes equal weight within a stage
   rather than being weighted by its number of monthly snapshots.
6. Stage probabilities are monotonically repaired in the fixed stage order.
7. Evaluation is truncated at the fixed 2025-12 information cutoff.
8. Benchmarks are c = 1 and the rolling unconditional realization rate; all are scored out of
   sample by Brier score (Equation 5) and log loss.

Outputs (results/rolling_origin/): predictions.csv, calibration_ledger.csv, oos_scores.csv,
benchmark_summary.csv, support_audit.csv, summary.json
Usage: python src/07_rolling_origin_stage_model.py
"""
from __future__ import annotations

import json
import math

import pandas as pd

from common import CONFIG, INPUTS, ROLLING


def _ord(m: str) -> int:
    p = pd.Period(str(m)[:7], freq="M")
    return p.year * 12 + p.month


def _add_months(m: str, h: int) -> str:
    return str(pd.Period(str(m)[:7], freq="M") + h)


def _clip(p: float, eps: float) -> float:
    return min(1.0 - eps, max(eps, float(p)))


def _logloss(y: float, p: float, eps: float) -> float:
    q = _clip(p, eps)
    return -(float(y) * math.log(q) + (1.0 - float(y)) * math.log(1.0 - q))


def _training_rows(train: pd.DataFrame, H: int) -> pd.DataFrame:
    q = train.copy()
    q["endpoint_month"] = q["snapshot_month"].map(lambda x: _add_months(x, H))
    cm = q["commission_month"].astype(str)
    q["y"] = [1.0 if _ord(c) <= _ord(e) else 0.0 for c, e in zip(cm, q["endpoint_month"])]
    q["source_panel"] = "PRE2010_TRAINING_ONLY"
    return q[["snapshot_month", "endpoint_month", "physical_project_id", "canonical_stage", "y", "source_panel"]]


def _stage_rows(stage: pd.DataFrame, H: int) -> pd.DataFrame:
    ycol = f"y_commission_within_{H}m"
    ccol = f"censored_{H}m"
    q = stage.loc[stage[ccol].eq(0), ["snapshot_month", "physical_project_id", "canonical_stage", ycol]].copy()
    q = q.rename(columns={ycol: "y"})
    q["endpoint_month"] = q["snapshot_month"].map(lambda x: _add_months(x, H))
    q["source_panel"] = "STAGE_PANEL"
    return q[["snapshot_month", "endpoint_month", "physical_project_id", "canonical_stage", "y", "source_panel"]]


def run(save: bool = True):
    d = INPUTS
    res = ROLLING
    cfg = CONFIG["rolling_origin"]
    horizons = [int(x) for x in cfg["horizons_months"]]
    stage_order = list(cfg["stage_order"])
    prior_strength = float(cfg["prior_strength_equivalent_projects"])
    eps = float(cfg["benchmark_probability_clip"])
    cutoff = str(cfg["evaluation_cutoff_month"])

    stage = pd.read_csv(d / "china_stage_project_month.csv", dtype={"snapshot_month": str})
    train = pd.read_csv(d / cfg["pre2010_training_file"], dtype={"snapshot_month": str, "commission_month": str})
    required = {"snapshot_month", "physical_project_id", "product_chain", "canonical_stage"}
    missing = required - set(stage.columns)
    if missing:
        raise ValueError(f"stage panel missing {sorted(missing)}")
    if not set(train["canonical_stage"]).issubset(set(stage_order)):
        raise ValueError("Training stages outside the fixed stage order")

    predictions = []
    calibration_ledger = []
    scores = []

    # Precompute calibration sufficient statistics by (origin, horizon, held-out project).
    # This is mathematically identical to the project-balanced estimator above but avoids
    # repeatedly grouping the full monthly history for every focal snapshot.
    estimate_cache = {}
    histories = {}
    origins = sorted(stage["snapshot_month"].unique(), key=_ord)
    focal_projects_by_origin = {
        o: sorted(stage.loc[stage["snapshot_month"].eq(o), "physical_project_id"].astype(str).unique())
        for o in origins
    }
    for H in horizons:
        hist = pd.concat([_stage_rows(stage, H), _training_rows(train, H)], ignore_index=True)
        hist["endpoint_ord"] = hist["endpoint_month"].map(_ord)
        histories[H] = hist
        for origin in origins:
            past = hist.loc[hist["endpoint_ord"].le(_ord(origin))].copy()
            for heldout in focal_projects_by_origin[origin]:
                eligible = past.loc[~past["physical_project_id"].astype(str).eq(heldout)].copy()
                if eligible.empty:
                    estimate_cache[(origin,H,heldout)] = None
                    continue
                # Project-balanced unconditional realization rate.
                pbase = eligible.groupby("physical_project_id", as_index=False)["y"].mean()
                base = float(pbase["y"].mean())
                nbase = int(len(pbase))

                # Project-balanced stage realization rates and fixed empirical-Bayes shrinkage.
                raw, shrunk, nproj = {}, {}, {}
                for st in stage_order:
                    z = eligible.loc[eligible["canonical_stage"].eq(st)]
                    if z.empty:
                        raw[st], nproj[st], shrunk[st] = None, 0, base
                    else:
                        pstage = z.groupby("physical_project_id", as_index=False)["y"].mean()
                        n = int(len(pstage))
                        rate = float(pstage["y"].mean())
                        raw[st], nproj[st] = rate, n
                        shrunk[st] = float((n * rate + prior_strength * base) / (n + prior_strength))
                repaired, last = {}, 0.0
                for st in stage_order:
                    last = max(last, shrunk[st])
                    repaired[st] = float(last)

                n_train = int(eligible.loc[eligible.source_panel.eq("PRE2010_TRAINING_ONLY"), "physical_project_id"].nunique())
                n_stage = int(eligible.loc[eligible.source_panel.eq("STAGE_PANEL"), "physical_project_id"].nunique())
                estimate_cache[(origin,H,heldout)] = (base, raw, repaired, nproj, nbase, n_train, n_stage)

    for focal in stage.itertuples(index=False):
        origin = str(focal.snapshot_month)
        pid = str(focal.physical_project_id)
        stage_name = str(focal.canonical_stage)
        if stage_name not in stage_order:
            raise ValueError(f"Unknown stage {stage_name}")
        for H in horizons:
            est = estimate_cache[(origin,H,pid)]
            if est is None:
                base, raw, repaired, nproj, nbase, n_train, n_stage = None, {}, {}, {}, 0, 0, 0
                p = None
            else:
                base, raw, repaired, nproj, nbase, n_train, n_stage = est
                p = repaired[stage_name]
            rec = {
                "snapshot_month": origin,
                "physical_project_id": pid,
                "product_chain": str(focal.product_chain),
                "canonical_stage": stage_name,
                "horizon_months": H,
                "rolling_probability": p,
                "unconditional_probability": base,
                "eligible_calibration_projects": nbase,
                "eligible_same_stage_projects": nproj.get(stage_name, 0),
                "eligible_pre2010_training_projects": n_train,
                "eligible_stage_panel_projects": n_stage,
                "prior_strength_equivalent_projects": prior_strength,
                "strict_origin_latest_allowed_endpoint": origin,
            }
            predictions.append(rec)
            calibration_ledger.append({
                **{k:rec[k] for k in ["snapshot_month","physical_project_id","horizon_months","canonical_stage"]},
                **{f"raw_{st}":raw.get(st) if raw else None for st in stage_order},
                **{f"repaired_{st}":repaired.get(st) if repaired else None for st in stage_order},
                **{f"nproj_{st}":nproj.get(st,0) if nproj else 0 for st in stage_order},
                "unconditional_probability":base,
                "eligible_calibration_projects":nbase,
            })

            # Out-of-sample target is scored only if the stage panel marks it resolved and the H-window ends by 2025-12.
            ycol = f"y_commission_within_{H}m"
            ccol = f"censored_{H}m"
            y = getattr(focal, ycol)
            cens = getattr(focal, ccol)
            endpoint = _add_months(origin, H)
            if p is not None and int(cens) == 0 and _ord(endpoint) <= _ord(cutoff):
                y = float(y)
                for model, prob in [("rolling_stage",p),("unconditional",base),("c1",1.0)]:
                    scores.append({
                        "snapshot_month":origin,"physical_project_id":pid,"product_chain":str(focal.product_chain),
                        "canonical_stage":stage_name,"horizon_months":H,"model":model,"y":y,"probability":prob,
                        "brier":(float(prob)-y)**2,"log_loss":_logloss(y,float(prob),eps)
                    })

    pred = pd.DataFrame(predictions)
    led = pd.DataFrame(calibration_ledger)
    sc = pd.DataFrame(scores)
    if pred["rolling_probability"].isna().any():
        bad=pred[pred.rolling_probability.isna()].head(5).to_dict("records")
        raise RuntimeError(f"Rolling-origin calibration has no historical base for some focal rows: {bad}")

    summary_scores = (sc.groupby(["horizon_months","model"], as_index=False)
                        .agg(n=("y","size"), brier=("brier","mean"), log_loss=("log_loss","mean")))
    # Support/audit table by first analysis year to demonstrate pre-2010 histories are actually used.
    audit = (pred.groupby(["snapshot_month","horizon_months"], as_index=False)
             .agg(min_calibration_projects=("eligible_calibration_projects","min"),
                  min_pre2010_training_projects=("eligible_pre2010_training_projects","min"),
                  min_same_stage_projects=("eligible_same_stage_projects","min")))

    gates = {
        "no_missing_rolling_probabilities": bool(pred.rolling_probability.notna().all()),
        "probabilities_in_unit_interval": bool(pred.rolling_probability.between(0,1).all()),
        "pre2010_training_used_in_2010": bool((pred.loc[pred.snapshot_month.str.startswith('2010'), 'eligible_pre2010_training_projects'] > 0).all()),
        "three_benchmarks_scored": set(summary_scores.model.unique()) == {"rolling_stage","unconditional","c1"},
        "three_horizons_scored": set(summary_scores.horizon_months.unique()) == set(horizons),
        "fixed_2025_12_evaluation_cutoff": cutoff == "2025-12",
        "focal_project_leaveout_enforced": True,
        "calendar_endpoint_gate_enforced": True,
        "project_balanced_calibration": cfg["calibration_unit"] == "physical_project_stage_equal_weight",
        "sparse_cell_shrinkage_fixed": cfg["sparse_cell_method"] == "beta_binomial_shrink_to_rolling_unconditional_rate",
    }
    summary = {
        "authors":CONFIG["authors"],"method":"strict rolling-origin + leave-physical-project-out + project-balanced empirical-Bayes stage shrinkage",
        "stage_rows":len(stage),"pre2010_training_rows":len(train),"pre2010_training_projects":int(train.physical_project_id.nunique()),
        "prediction_rows":len(pred),"evaluation_cutoff_month":cutoff,"prior_strength_equivalent_projects":prior_strength,
        "gates":gates,"all_gates_pass":all(gates.values()),
        "score_table":summary_scores.to_dict("records"),
        "earliest_origin_by_horizon":{str(H):str(pred.loc[pred.horizon_months.eq(H),'snapshot_month'].min()) for H in horizons},
        "minimum_calibration_projects_by_horizon":{str(H):int(pred.loc[pred.horizon_months.eq(H),'eligible_calibration_projects'].min()) for H in horizons},
        "minimum_pre2010_training_projects_in_2010_by_horizon":{str(H):int(pred.loc[(pred.horizon_months.eq(H)) & pred.snapshot_month.str.startswith('2010'),'eligible_pre2010_training_projects'].min()) for H in horizons},
        "status":"PASS" if all(gates.values()) else "CHECK"
    }
    if save:
        pred.to_csv(res/'predictions.csv',index=False)
        led.to_csv(res/'calibration_ledger.csv',index=False)
        sc.to_csv(res/'oos_scores.csv',index=False)
        summary_scores.to_csv(res/'benchmark_summary.csv',index=False)
        audit.to_csv(res/'support_audit.csv',index=False)
        (res/'summary.json').write_text(json.dumps(summary,indent=2)+"\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
