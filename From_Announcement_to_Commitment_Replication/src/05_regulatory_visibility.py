# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Regulatory-visibility companion design (Sections 4.5 and 6; Table 5; Figure 4).

Input: data/inputs/us_regulatory_filings.csv, one row per project with a qualifying regulatory
visibility date (RVD). Projects without a row were searched and nothing qualifying was found; they
are coded missing and never imputed.
  RV1  filing coverage by sponsor status;
  RV2  visibility lead (months from first public announcement to RVD);
  RV3  primary linear probability model on projects with an RVD up to 2022-12, with within-chain permutation;
  RV4  commitment within 36 months of the RVD (undated commitments excluded);
  interpretation rule fixed before any regulatory date was collected.
Outputs (results/): regulatory_visibility.csv, regulatory_visibility_projects.csv
Usage: python src/05_regulatory_visibility.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from common import INPUTS, NPERM, RESULTS, SEED

P = pd.read_csv(RESULTS / "us_project_classification.csv")
for c in ["first_public", "commit_month"]: P[c] = pd.PeriodIndex(P[c].replace("NaT", None), freq="M")
d = P[P.fp_le_2022 & (P.sponsor_status != "ambiguous")].reset_index(drop=True)
r = pd.read_csv(INPUTS / "us_regulatory_filings.csv")
assert not r.project_id.duplicated().any() and set(r.project_id) <= set(P.project_id)
d = d.merge(r, on="project_id", how="left")
d["rvd_m"] = pd.PeriodIndex([str(x)[:7] if pd.notna(x) else None for x in d.rvd], freq="M")
EXACT = {"day", "month", "year"}
d["rvd_exact"] = d.precision.isin(EXACT)
rows = []
# RV1 coverage
for g, z in d.groupby("sponsor_status"):
    rows.append(dict(analysis="RV1 coverage", group=g, n=len(z), value=round(z.rvd.notna().mean(), 3),
                     note=f"{z.rvd.notna().sum()} with RVD; {z.rvd_exact.sum()} exact application dates"))
# RV2 visibility lead = RVD minus first public (months); positive = announced before filing.
# Amendment A2: no lead is computed from an imputed first-public date.
d["lead"] = [(rv - fp).n if (pd.notna(rv) and not imp) else np.nan for rv, fp, imp in zip(d.rvd_m, d.first_public, d.first_public_imputed.astype(bool))]
for label, mask in [("RV2 lead (exact application dates)", d.rvd_exact & d.lead.notna()), ("RV2 lead (all RVD incl. upper bounds)", d.rvd.notna() & d.lead.notna())]:
    z = d[mask]; a = z[z.entrant == 0].lead; b = z[z.entrant == 1].lead
    p = stats.mannwhitneyu(a, b).pvalue if len(a) and len(b) else np.nan
    rows.append(dict(analysis=label, group="incumbent", n=len(a), value=float(a.median()), note=f"share filed before first public: {(a < 0).mean():.2f}"))
    rows.append(dict(analysis=label, group="entrant", n=len(b), value=float(b.median()), note=f"share filed before first public: {(b < 0).mean():.2f}; Mann-Whitney p = {p:.3f}"))
# RV3 conditional credibility: projects that reached an RVD up to 2022-12
rng = np.random.default_rng(SEED); B = NPERM


def lpm_perm(z, label):
    cov = [c for c in ["entrant", "logcap", "greenfield", "post2015"] if z[c].nunique() > 1 or c == "entrant"]
    X = sm.add_constant(z[cov].astype(float)); y = z.committed.values.astype(float)
    f = sm.OLS(y, X).fit(cov_type="HC1"); b0 = f.params["entrant"]; ci = f.conf_int().loc["entrant"]
    Xv = X.values.copy(); j = list(X.columns).index("entrant"); lab = z.entrant.values
    gr = [np.where(z.chain.values == c)[0] for c in z.chain.unique()]; cnt = 0
    for _ in range(B):
        p = lab.copy()
        for g in gr: p[g] = rng.permutation(lab[g])
        Xv[:, j] = p; cnt += abs(np.linalg.lstsq(Xv, y, rcond=None)[0][j]) >= abs(b0) - 1e-12
    rate = z.groupby("entrant").committed.mean()
    rows.append(dict(analysis=label, group="entrant coefficient", n=len(z), value=round(b0, 3),
                     note=f"95% CI [{ci[0]:.3f}, {ci[1]:.3f}]; perm p = {(cnt+1)/(B+1):.4f}; commit rate inc {rate.get(0, np.nan):.3f} / ent {rate.get(1, np.nan):.3f}; n_inc {int((z.entrant==0).sum())}, n_ent {int(z.entrant.sum())}; controls {'+'.join(cov[1:])}"))
    return b0


z3 = d[d.rvd.notna() & (d.rvd_m <= pd.Period("2022-12", "M"))]
b_rv3 = lpm_perm(z3, "RV3 primary LPM on projects with RVD <= 2022-12")
lpm_perm(z3[z3.rvd_exact], "RV3 sensitivity: exact application dates only")
# RV4 commitment within 36 months of RVD (undated commitments excluded)
z4 = z3[~((z3.committed == 1) & z3.commit_month.isna())].copy()
z4["c36"] = [int(c == 1 and (cm - rv).n <= 36) for c, cm, rv in zip(z4.committed, z4.commit_month, z4.rvd_m)]
cov = [c for c in ["entrant", "logcap", "greenfield", "post2015"] if z4[c].nunique() > 1 or c == "entrant"]
f = sm.OLS(z4.c36.astype(float), sm.add_constant(z4[cov].astype(float))).fit(cov_type="HC1"); ci = f.conf_int().loc["entrant"]
rt = z4.groupby("entrant").c36.mean()
rows.append(dict(analysis="RV4 commitment within 36 months of RVD", group="entrant coefficient", n=len(z4), value=round(f.params["entrant"], 3),
                 note=f"95% CI [{ci[0]:.3f}, {ci[1]:.3f}]; rate inc {rt.get(0, np.nan):.3f} / ent {rt.get(1, np.nan):.3f}"))
verdict = ("gap remains large in the filing-covered subset; incomplete and unequal filing coverage prevents ruling out disclosure-stage selection in the full universe" if (b_rv3 <= -0.20 and f.params["entrant"] < 0)
           else "gap is strongly attenuated in the filing-covered subset" if b_rv3 > -0.10 else "partial attenuation in the filing-covered subset")
rows.append(dict(analysis="Interpretation rule", group="", n=len(z3), value=np.nan, note=verdict))
R = pd.DataFrame(rows); R.to_csv(RESULTS / "regulatory_visibility.csv", index=False)
d[["project_id", "sponsor_status", "chain", "first_public", "rvd", "precision", "filing_type", "lead", "outcome"]].astype(str).to_csv(RESULTS / "regulatory_visibility_projects.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200); print(R.to_string(index=False))
