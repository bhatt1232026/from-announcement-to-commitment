# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Companion robustness analyses (Sections 4.2 and 5.3; Table S3; amendments A6 to A8 and A13).
They complement the pre-specified primary estimate and do not replace it.
  Primary  permutation within chain, re-computed with the (B+1) correction;
  RB1      permutation of the entrant label within chain x site type;
  RB2      Freedman-Lane residual permutation (chain fixed effects; HC1 t statistic; within chain);
  RB3      equal-window outcome: commitment within 36 months of first public (undated commitments excluded);
  RB4      primary model with months of follow-up to 2025-12 as a control;
  RB5      site type taken from the register's descriptive project-type labels.
Output (results/): us_companion_robustness.csv
Usage: python src/04_us_companion_robustness.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from common import NPERM, RESULTS, SEED

P = pd.read_csv(RESULTS / "us_project_classification.csv")
for c in ["first_public", "commit_month"]: P[c] = pd.PeriodIndex(P[c].replace("NaT", None), freq="M")
d = P[P.fp_le_2022 & (P.sponsor_status != "ambiguous")].reset_index(drop=True)
rng = np.random.default_rng(SEED); B = NPERM
COV = ["entrant", "logcap", "greenfield", "post2015"]
X = sm.add_constant(d[COV].astype(float)); y = d.committed.values.astype(float)
b0 = sm.OLS(y, X).fit().params["entrant"]
rows = []


def strat_perm(strata, label):
    Xv = X.values.copy(); lab = d.entrant.values; gr = [np.where(strata == s)[0] for s in np.unique(strata)]; cnt = 0
    for _ in range(B):
        p = lab.copy()
        for g in gr: p[g] = rng.permutation(lab[g])
        Xv[:, 1] = p; cnt += abs(np.linalg.lstsq(Xv, y, rcond=None)[0][1]) >= abs(b0) - 1e-12
    both = int(sum(pd.Series(lab).groupby(strata).nunique() == 2))
    rows.append(dict(analysis=label, n=len(d), estimate=round(b0, 3), ci95="", p=round((cnt + 1) / (B + 1), 4), note=f"strata with both groups: {both}"))


strat_perm(d.chain.values, "Primary: permutation within chain (re-computed, (B+1) correction)")
strat_perm((d.chain + "|" + d.site_type).values, "RB1 permutation within chain x site type")

# RB2 Freedman-Lane
Z = pd.get_dummies(d.chain, drop_first=True).astype(float)
Xr = sm.add_constant(pd.concat([d[["logcap", "greenfield", "post2015"]].astype(float), Z], axis=1))
Xf = pd.concat([d[["entrant"]].astype(float), Xr], axis=1)
ff = sm.OLS(y, Xf).fit(cov_type="HC1"); t0 = ff.tvalues["entrant"]
fr = sm.OLS(y, Xr).fit(); fit, res = fr.fittedvalues.values, fr.resid.values
gr = [np.where(d.chain.values == c)[0] for c in d.chain.unique()]; cnt = 0
XfV = Xf.values; XtXi = np.linalg.pinv(XfV.T @ XfV)


def hc1_t(yy):
    b = XtXi @ XfV.T @ yy; e = yy - XfV @ b; n, k = XfV.shape
    V = XtXi @ (XfV.T * e**2) @ XfV @ XtXi * n / (n - k); return b[0] / np.sqrt(V[0, 0])


for _ in range(B):
    e = res.copy()
    for g in gr: e[g] = rng.permutation(res[g])
    cnt += abs(hc1_t(fit + e)) >= abs(t0)
ci = ff.conf_int().loc["entrant"]
rows.append(dict(analysis="RB2 Freedman-Lane (chain FE, HC1 t)", n=len(d), estimate=round(ff.params["entrant"], 3),
                 ci95=f"[{ci[0]:.3f}, {ci[1]:.3f}]", p=round((cnt + 1) / (B + 1), 4), note="residuals of reduced model permuted within chain"))

# RB3 equal 36-month window (imputed first-public dates excluded, amendment A2)
lag = np.array([(c - f).n if pd.notna(c) else np.nan for c, f in zip(d.commit_month, d.first_public)])
undated = ((d.committed == 1).values & np.isnan(lag)) | d.first_public_imputed.astype(bool).values
dd = d[~undated].copy(); dd["c36"] = ((dd.committed == 1) & (lag[~undated] <= 36)).astype(int)
f = sm.OLS(dd.c36.astype(float), sm.add_constant(dd[COV].astype(float))).fit(cov_type="HC1"); ci = f.conf_int().loc["entrant"]
r = dd.groupby("entrant").c36.mean()
rows.append(dict(analysis="RB3 commitment within 36 months of first public", n=len(dd), estimate=round(f.params["entrant"], 3),
                 ci95=f"[{ci[0]:.3f}, {ci[1]:.3f}]", p=round(f.pvalues["entrant"], 4),
                 note=f"rates incumbent {r[0]:.3f} / entrant {r[1]:.3f}; {int(undated.sum())} undated commitments excluded"))

# RB4 follow-up control
d["follow_months"] = [(pd.Period("2025-12", "M") - fp).n for fp in d.first_public]
f = sm.OLS(y, sm.add_constant(d[COV + ["follow_months"]].astype(float))).fit(cov_type="HC1"); ci = f.conf_int().loc["entrant"]
rows.append(dict(analysis="RB4 primary model + months of follow-up", n=len(d), estimate=round(f.params["entrant"], 3),
                 ci95=f"[{ci[0]:.3f}, {ci[1]:.3f}]", p=round(f.pvalues["entrant"], 4), note=""))

# RB5 site type from the register's descriptive project-type labels instead of the coding rule
reg_green = d.register_project_type.fillna("").str.lower().str.contains("greenfield")
d5 = d.assign(greenfield=np.where(d.source.eq("base_register"), reg_green.astype(int), d.greenfield))
f = sm.OLS(y, sm.add_constant(d5[COV].astype(float))).fit(cov_type="HC1"); ci = f.conf_int().loc["entrant"]
rows.append(dict(analysis="RB5 site type from register text labels", n=len(d5), estimate=round(f.params["entrant"], 3), ci95=f"[{ci[0]:.3f}, {ci[1]:.3f}]",
                 p=round(f.pvalues["entrant"], 4), note=f"greenfield incumbents {int(d5[d5.entrant==0].greenfield.sum())}, entrants {int(d5[d5.entrant==1].greenfield.sum())}; {int(d.site_disagrees_register_label.sum())} recoded vs register text"))
R = pd.DataFrame(rows); R.to_csv(RESULTS / "us_companion_robustness.csv", index=False); print(R.to_string(index=False))
