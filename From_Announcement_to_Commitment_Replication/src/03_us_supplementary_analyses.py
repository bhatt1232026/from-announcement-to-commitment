# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Supplementary U.S. analyses (Section 5.3; Table S3). These were not part of the pre-specified plan
and are reported as supplementary.
  S1   brownfield-only linear probability model (sponsor status holding site type fixed);
  S2   projects visible more than one month before any commitment (undated commitments excluded);
  S2b  projects excluding announcement-at-commitment cases only (undated commitments kept);
  plus announcement-at-commitment shares by sponsor status.
Outputs (results/): us_supplementary.csv, us_announce_at_commitment.csv
Usage: python src/03_us_supplementary_analyses.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from common import NPERM, RESULTS, SEED

P = pd.read_csv(RESULTS / "us_project_classification.csv")
for c in ["first_public", "commit_month"]: P[c] = pd.PeriodIndex(P[c].replace("NaT", None), freq="M")
prim = P[P.fp_le_2022 & (P.sponsor_status != "ambiguous")].copy()
rng = np.random.default_rng(SEED)


def fitperm(df, cols, n=NPERM):
    X = sm.add_constant(df[cols].astype(float)); y = df.committed.astype(float)
    f = sm.OLS(y, X).fit(cov_type="HC1"); Xv = X.values.copy(); j = list(X.columns).index("entrant")
    b0 = f.params["entrant"]; lab = df.entrant.values; gr = [np.where(df.chain.values == c)[0] for c in df.chain.unique()]; d = []
    for _ in range(n):
        p = lab.copy()
        for g in gr: p[g] = rng.permutation(lab[g])
        Xv[:, j] = p; d.append(np.linalg.lstsq(Xv, y.values, rcond=None)[0][j])
    return dict(n=len(df), n_inc=int((df.entrant == 0).sum()), n_ent=int(df.entrant.sum()),
                rate_inc=round(df[df.entrant == 0].committed.mean(), 3), rate_ent=round(df[df.entrant == 1].committed.mean(), 3),
                b=round(b0, 3), ci=f"[{b0-1.96*f.bse['entrant']:.3f}, {b0+1.96*f.bse['entrant']:.3f}]",
                perm_p=round(float(((np.abs(d) >= abs(b0) - 1e-12).sum() + 1) / (n + 1)), 4))


rows = [dict(sample="S1 brownfield only", **fitperm(prim[prim.site_type == "brownfield"], ["entrant", "logcap", "post2015"]))]
lag = (prim.commit_month - prim.first_public).apply(lambda x: x.n if pd.notna(x) else np.nan)
prim["lag"] = lag.where(~prim.first_public_imputed.astype(bool))   # amendment A2: no lag from imputed first-public dates
prim["announce_at_commit"] = prim.committed.eq(1) & prim.lag.le(1)
s2 = prim[~prim.announce_at_commit & ~(prim.committed.eq(1) & prim.lag.isna()) & ~prim.first_public_imputed.astype(bool)]
rows.append(dict(sample="S2 visible >1 month before any commitment (excl. undated commitments)", **fitperm(s2, ["entrant", "logcap", "greenfield", "post2015"])))
s2b = prim[~prim.announce_at_commit]
rows.append(dict(sample="S2b excl. announce-at-commitment only (undated commitments kept)", **fitperm(s2b, ["entrant", "logcap", "greenfield", "post2015"])))
S = pd.DataFrame(rows); S.to_csv(RESULTS / "us_supplementary.csv", index=False); print(S.to_string(index=False))
d = prim.groupby("sponsor_status").agg(projects=("committed", "size"), committed=("committed", "sum"),
      dated_commit=("lag", lambda s: s.notna().sum()), announce_at_commit=("announce_at_commit", "sum"),
      lag_gt_12=("lag", lambda s: (s > 12).sum()))
d.to_csv(RESULTS / "us_announce_at_commitment.csv"); print(d)
print(prim[prim.outcome != "committed"][["project_id", "sponsor_status", "chain", "site_type", "outcome", "first_public"]].to_string(index=False))
