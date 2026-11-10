# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Pre-specified U.S. analysis (Sections 3.2, 4.1 to 4.4 and 5.1 to 5.4; Tables 2 to 4; Table S3).

Builds the project universe (base register plus completeness-search admissions), codes sponsor
status and site type by the fixed rules, estimates the primary linear probability model with
within-chain permutation inference, runs the pre-specified checks C1 to C8 and evaluates the
decision criteria R1 to R4.

Outputs (results/):
  us_project_classification.csv, us_primary_and_checks.csv, us_capacity_weighted.csv,
  us_sponsor_by_site.csv, us_competing_risks.csv, us_commitment_lag.csv,
  us_decision_criteria.json, completeness_search_summary.json
Usage: python src/02_us_primary_analysis.py
"""
import json
import re

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from common import DERIVED, INPUTS, NPERM, RESULTS, SEED

HORIZON = pd.Period("2025-12", "M")

m = pd.read_csv(INPUTS / "us_project_register.csv")
ev = pd.read_csv(INPUTS / "us_project_events.csv")
rec = pd.read_csv(INPUTS / "us_first_public_dates.csv")
add = pd.read_csv(DERIVED / "completeness_search_admitted.csv")
corr = pd.read_csv(DERIVED / "register_corrections.csv")

CHAIN7 = {"ethylene": "ethylene", "polyethylene": "polyethylene", "polypropylene": "polypropylene",
          "propylene_PDH": "propylene", "EO_MEG": "EO_MEG", "methanol": "methanol", "PVC_VCM": "PVC_VCM"}

# ---- Sponsor status at the first public date and site type (amendment A3) for the 71 base-register projects
# (sponsor_status, site_type, note)
I, E, A, B, G = "incumbent", "entrant", "ambiguous", "brownfield", "greenfield"
CODE = {
 "US_ETH_SASOL_LCCP": (I, B, "Sasol 2010 ethylene; existing Lake Charles site"),
 "US_ETH_LYB_LAPORTE": (I, B, ""), "US_ETH_LYB_CHANNELVIEW_I": (I, B, ""), "US_ETH_LYB_CORPUS": (I, B, ""),
 "US_ETH_SHELL_PA": (I, G, "Monaca former zinc smelter, not a Shell site"),
 "US_ETH_CPCHEM_USGC": (I, B, "cracker at existing Cedar Bayou site"),
 "US_ETH_EXXON_BAYTOWN": (I, B, ""),
 "US_ETH_GCGV": (I, G, "new San Patricio County site"),
 "US_PE_BAYPORT": (I, B, "Total 2010 PE; at Total Bayport site"),
 "US_PE_LYB_HYPERZONE": (I, B, "La Porte site"),
 "US_ETHPE_PTTGC_OH": (E, G, ""),
 "US_MEOH_NWIW_TACOMA": (E, G, ""), "US_MEOH_NWIW_KALAMA": (E, G, ""), "US_MEOH_LEUCADIA_LC": (E, G, ""),
 "US_MEOH_SLM_STJAMES": (E, G, ""), "US_MEOH_YUHUANG_STJAMES": (E, G, ""),
 "US_MEOH_MX_G3": (E, B, "Methanex absent from 2010 table; contiguous with Geismar 1-2"),
 "US_ETHPE_GTP_ORANGE": (I, G, "new Orange County site"),
 "US_MEOH_MX_G1": (E, B, "relocation"), "US_MEOH_MX_G2": (E, B, "relocation"),
 "US_MEOH_NATGAS": (E, B, "OCI acquired adjacent Beaumont plant in 2011 (not in 2010 table); contiguous site"),
 "US_MEOH_LYB_CHV": (I, B, "restart"),
 "US_MEOH_FAIRWAY_CL": (E, B, "Celanese Clear Lake site; Celanese absent from 2010 methanol table"),
 "US_MEOH_PAMPA": (E, B, "restart"), "US_MEOH_BIGLAKE": (E, G, ""),
 "US_PE_GEMINI_LAPORTE": (I, B, "INEOS 2010 PE; Battleground site"),
 "US_PE_EXXON_BEAUMONT": (I, B, ""), "US_PE_FORMOSA_PC_EXP": (I, B, ""),
 "US_PE_DOW_FREEPORT_ELITE": (I, B, ""), "US_PE_DOW_PLAQUEMINE_LDPE": (I, B, ""),
 "US_MEOH_LIBERTYONE_WV": (E, B, "relocation/reconstruction"),
 "US_MEOH_SYNGAS_STJAMES": (E, G, ""), "US_MEOH_IGP_MYRtle": (E, G, ""),
 "US_PE_LYB_MATAGORDA_EXP": (I, B, ""), "US_PE_DOW_STCHARLES_DEBOT": (I, B, ""),
 "US_PE_ASCENT_WV": (E, G, "Braskem/Odebrecht absent from 2010 PE table"),
 "US_PE_BADLANDS_ND": (E, G, ""), "US_PE_APPRESINS_OH": (E, G, ""),
 "US_PE_DOW_SEADRIFT_EXP": (I, B, ""), "US_PE_DOW_POLY7_FREEPORT": (I, B, ""),
 "US_ETHPE_FORMOSA_SUNSHINE": (A, G, "incumbent_affiliate: FG LA / Formosa Petrochemical (Taiwan)"),
 "US_ETH_WLK_PETRO2_LC": (I, B, ""), "US_ETH_WLK_CALVERT14": (I, B, ""), "US_ETH_WLK_PETRO1_LC": (I, B, ""),
 "US_ETH_INEOS_CHOCBAY": (I, B, ""), "US_ETH_WILLIAMS_GEISMAR": (I, B, ""),
 "US_ETH_CPCHEM_SWEENY14": (I, B, ""), "US_ETH_BASF_TOTAL_PA14": (I, B, ""),
 "US_ETH_OXY_INGLESIDE": (E, B, "OxyChem/Mexichem absent from 2010 ethylene table; Ingleside vinyls site"),
 "US_ETH_LACC_LAKECHARLES": (E, B, "Lotte/Axiall absent from 2010 ethylene table; Axiall Lake Charles site"),
 "US_ETH_BAYSTAR_PORTARTHUR": (I, B, "A5: Total held 40% of BASF/FINA LP; Port Arthur site"),
 "US_ETH_FORMOSA_PC_OL3": (I, B, ""), "US_ETH_DOW_STCHARLES_RESTART": (I, B, "restart"),
 "US_PP_BRASKEM_DELTA": (I, B, "Braskem 2010 PP; La Porte site"),
 "US_PP_EXXON_BATON_ROUGE": (I, B, ""),
 "US_PDH_ENTERPRISE_1": (I, B, "Enterprise 2010 propylene; Mont Belvieu"), "US_PDH_ENTERPRISE_2": (I, B, ""),
 "US_PROP_LYB_FLEX2": (I, B, ""), "US_EO_HUNTSMAN_PORT_NECHES": (I, B, ""),
 "US_MEG_MEGLOBAL_OYSTER_CREEK": (A, B, "A5: MEGlobal owned by EQUATE (Dow 42.5%) at first public - indirect"),
 "US_PVC_SHINTECH_2013_EXP": (I, B, ""), "US_PVC_SHINTECH_2018_PHASE1": (I, B, ""), "US_PVC_SHINTECH_2021_PHASE2": (I, B, ""),
 "US_PP_FORMOSA_PP3": (I, B, ""), "US_PDH_FORMOSA_POINT_COMFORT": (I, B, ""),
 "US_PVC_FORMOSA_BATON_ROUGE_2017": (I, B, ""), "US_PVC_WESTLAKE_CALVERT_2012": (I, B, ""),
 "US_PVC_WESTLAKE_GEISMAR_2018": (I, B, ""),
 "US_PROP_BASF_FREEPORT_MTP": (I, B, "BASF via BASF/FINA LP (60%); Freeport site"),
 "US_PDH_ASCEND_CHOCBAY": (E, B, "Ascend absent from 2010 propylene table; Chocolate Bayou site"),
 "US_PDH_REXTAC_ODESSA": (E, B, "REXtac absent from 2010 propylene table; Odessa site"),
}
assert set(CODE) == set(m.project_id), set(m.project_id) ^ set(CODE)


def to_month(s):
    if pd.isna(s) or str(s).strip() in ("", "nan"): return None, None
    s = str(s).strip()
    if re.fullmatch(r"\d{4}", s): return pd.Period(f"{s}-07", "M"), "year"
    q = re.fullmatch(r"(\d{4})-Q([1-4])", s)
    if q: return pd.Period(f"{q.group(1)}-{3*int(q.group(2))-1:02d}", "M"), "quarter"
    return pd.Period(s[:7], "M"), "month_or_day"


ann_ev = ev[ev.event_type.astype(str).str.startswith("ANNOUNCEMENT")].groupby("project_id").event_date.min()
any_ev = ev.groupby("project_id").event_date.min()
cancel_ev = ev[ev.event_state_after.astype(str).eq("CANCELLED")].groupby("project_id").event_date.min()
recd = rec.set_index("project_id").recovered_first_public_date
CANCEL_KW = ["cancel", "abandon", "rescission", "rescinded", "not pursued", "denied", "lease terminated"]
COMMIT_KW = ["operating", "construction", "commission", "post-fid"]

rows = []
for r in m.itertuples(index=False):
    cands = [(p, pr, src) for src, val in [("register", r.first_announcement_date), ("first_public_dates", recd.get(r.project_id)),
             ("event_ledger", ann_ev.get(r.project_id))] for p, pr in [to_month(val)] if p is not None]
    c = corr[(corr.project_id == r.project_id) & (corr.field == "first_public")]
    if len(c): cands.append((pd.Period(c.corrected_value.iloc[0], "M"), "month_or_day", "register_correction"))
    fp = min(cands, key=lambda x: x[0]) if cands else (None, None, None)
    tier = r.fid_tier if pd.notna(r.fid_tier) else None
    fid, _ = to_month(r.fid_date) if tier in (1.0, 2.0) else (None, None)
    st = str(r.current_status).lower()
    canc, _ = to_month(cancel_ev.get(r.project_id))
    oc = corr[(corr.project_id == r.project_id) & (corr.field == "outcome")]
    if fid is not None or any(k in st for k in COMMIT_KW): outcome = "committed"
    elif len(oc): outcome = oc.corrected_value.iloc[0]; canc = pd.Period(oc.date.iloc[0], "M")
    elif canc is not None or any(k in st for k in CANCEL_KW): outcome = "cancelled"
    else: outcome = "pending"
    imputed = False
    if fp[0] is None:   # amendment A2: earliest dated milestone as an upper bound, used only for date filters
        alt = [x for x in [fid, to_month(any_ev.get(r.project_id))[0], to_month(r.construction_start_date)[0], to_month(r.startup_date)[0]] if x is not None]
        fp = (min(alt), "upper_bound", "earliest_dated_event_A2") if alt else (None, None, None); imputed = True
    s_status, s_site, note = CODE[r.project_id]
    register_says_green = "greenfield" in str(r.project_type).lower()
    rows.append(dict(project_id=r.project_id, source="base_register", sponsor=r.sponsor, chain=CHAIN7[r.chain],
        capacity_ktpa=r.capacity_ktpa, capacity_imputed=False, sponsor_status=s_status, site_type=s_site,
        site_disagrees_register_label=(register_says_green != (s_site == G)), register_project_type=r.project_type, coding_note=note,
        first_public=fp[0], first_public_precision=fp[1], first_public_source=fp[2], first_public_imputed=imputed,
        commit_month=fid if (outcome == "committed") else None,
        cancel_month=canc if outcome == "cancelled" else None, outcome=outcome))
for r in add.itertuples(index=False):
    rows.append(dict(project_id=r.project_id, source="completeness_search", sponsor=r.sponsor, chain=CHAIN7[r.chain],
        capacity_ktpa=float(r.capacity_ktpa), capacity_imputed="IMPUTED" in str(r.capacity_note),
        sponsor_status=r.sponsor_status, site_type=r.site_type, site_disagrees_register_label=False, register_project_type="",
        coding_note=r.sponsor_status_note, first_public=pd.Period(r.first_public, "M"),
        first_public_precision=r.first_public_precision, first_public_source="completeness_search", first_public_imputed=False,
        commit_month=pd.Period(r.commit_month, "M") if isinstance(r.commit_month, str) else None,
        cancel_month=pd.Period(r.outcome_date[:7], "M") if r.outcome == "cancelled" else None, outcome=r.outcome))
P = pd.DataFrame(rows)
# Capacity missing in the base register (Shell PA, PTTGC, Kalama, Leucadia): filled from sister tables / amendment A1
CAP_FILL = {"US_ETH_SHELL_PA": 1500.0, "US_ETHPE_PTTGC_OH": 1500.0, "US_MEOH_NWIW_KALAMA": 3600.0, "US_MEOH_LEUCADIA_LC": 2658.1}
for k, v in CAP_FILL.items():
    if P.loc[P.project_id == k, "capacity_ktpa"].isna().all(): P.loc[P.project_id == k, ["capacity_ktpa", "capacity_imputed"]] = [v, True]
assert P.capacity_ktpa.notna().all() and P.first_public.notna().all(), P[P.capacity_ktpa.isna() | P.first_public.isna()]
P["committed"] = P.outcome.eq("committed").astype(int)
P["entrant"] = P.sponsor_status.eq("entrant").astype(int)
P["greenfield"] = P.site_type.eq(G).astype(int)
P["post2015"] = (P.first_public >= pd.Period("2015-01", "M")).astype(int)
P["logcap"] = np.log(P.capacity_ktpa)
P["fp_le_2022"] = P.first_public <= pd.Period("2022-12", "M")
P.assign(first_public=P.first_public.astype(str), commit_month=P.commit_month.astype(str), cancel_month=P.cancel_month.astype(str)
        ).to_csv(RESULTS / "us_project_classification.csv", index=False)

# ---------------------------------------------------------------- estimation helpers
X_COLS = ["entrant", "logcap", "greenfield", "post2015"]


def design(df):
    cols = [c for c in X_COLS if df[c].nunique() > 1 or c == "entrant"]
    return sm.add_constant(df[cols].astype(float), has_constant="add"), cols


def lpm(df):
    X, cols = design(df)
    fit = sm.OLS(df.committed.astype(float), X).fit(cov_type="HC1")
    return fit, cols


def perm_p(df, rng, n=NPERM):
    """Two-sided within-chain permutation p-value with the (B+1) Monte Carlo correction (Equation 2)."""
    X, cols = design(df); y = df.committed.values.astype(float); Xv = X.values.copy(); j = list(X.columns).index("entrant")
    b0 = np.linalg.lstsq(Xv, y, rcond=None)[0][j]
    groups = [np.where(df.chain.values == c)[0] for c in df.chain.unique()]
    lab = df.entrant.values; draws = np.empty(n)
    for i in range(n):
        perm = lab.copy()
        for g in groups: perm[g] = rng.permutation(lab[g])
        Xv[:, j] = perm; draws[i] = np.linalg.lstsq(Xv, y, rcond=None)[0][j]
    return b0, float(((np.abs(draws) >= abs(b0) - 1e-12).sum() + 1) / (n + 1)), draws


def summarize(df, label, rng=None, do_perm=False):
    fit, cols = lpm(df); b = fit.params["entrant"]; se = fit.bse["entrant"]
    inc, ent = df[df.entrant == 0], df[df.entrant == 1]
    out = dict(sample=label, n=len(df), n_incumbent=len(inc), n_entrant=len(ent),
               commit_rate_incumbent=round(inc.committed.mean(), 3) if len(inc) else np.nan,
               commit_rate_entrant=round(ent.committed.mean(), 3) if len(ent) else np.nan,
               raw_gap=round(ent.committed.mean() - inc.committed.mean(), 3) if len(inc) and len(ent) else np.nan,
               b_entrant=round(b, 3), se_hc1=round(se, 3), ci95_lo=round(b - 1.96 * se, 3), ci95_hi=round(b + 1.96 * se, 3),
               p_hc1=round(fit.pvalues["entrant"], 6), controls="+".join(c for c in cols if c != "entrant"),
               chains_with_both=int(sum(df[df.chain == c].entrant.nunique() == 2 for c in df.chain.unique())))
    if len(inc) and len(ent):
        a = [[int(ent.committed.sum()), int((1 - ent.committed).sum())], [int(inc.committed.sum()), int((1 - inc.committed).sum())]]
        out["fisher_p"] = round(stats.fisher_exact(a)[1], 8)
    if do_perm:
        _, p, _ = perm_p(df, rng); out["perm_p_within_chain"] = round(p, 4)
    return out


rng = np.random.default_rng(SEED)
base = P[P.fp_le_2022]
prim = base[base.sponsor_status != A]
res = [summarize(prim, "PRIMARY: ambiguous excluded, first public <= 2022-12", rng, True)]
checks = {
 "C1a ambiguous as incumbent": base.assign(entrant=lambda d: d.sponsor_status.eq(E).astype(int)),
 "C1b ambiguous as entrant": base.assign(entrant=lambda d: d.sponsor_status.isin([E, A]).astype(int)),
 "C2 excluding methanol": prim[prim.chain != "methanol"],
 "C3 excluding >2500 kt/y": prim[prim.capacity_ktpa <= 2500],
 "C4 greenfield only": prim[prim.greenfield == 1],
}
for c in sorted(prim.chain.unique()): checks[f"C5 leave out {c}"] = prim[prim.chain != c]
checks["C6 including first public after 2022-12"] = P[P.sponsor_status != A]
for k, d in checks.items(): res.append(summarize(d, k, rng, True))
R = pd.DataFrame(res); R.to_csv(RESULTS / "us_primary_and_checks.csv", index=False)

# Check C7: capacity-weighted commitment shares (descriptive)
rows_cw = []
for sponsor_status, group in prim.groupby("sponsor_status", sort=True):
    rows_cw.append({
        "sponsor_status": sponsor_status,
        "projects": len(group),
        "capacity_kt": group.capacity_ktpa.sum(),
        "cap_weighted_commit": (group.capacity_ktpa * group.committed).sum() / group.capacity_ktpa.sum(),
        "project_commit": group.committed.mean(),
    })
cw = pd.DataFrame(rows_cw).set_index("sponsor_status")
cw.round(3).to_csv(RESULTS / "us_capacity_weighted.csv")

# Sponsor status by site type (descriptive; Table 2 and Figure 1)
tab = prim.groupby(["sponsor_status", "site_type"]).agg(projects=("committed", "size"), committed=("committed", "sum"),
        cancelled=("outcome", lambda s: (s == "cancelled").sum()), pending=("outcome", lambda s: (s == "pending").sum()))
tab["commit_rate"] = (tab.committed / tab.projects).round(3); tab.to_csv(RESULTS / "us_sponsor_by_site.csv")


# Check C8: Aalen-Johansen competing risks (Equation 3) on projects with dated outcomes, and commitment lag
def aj(df, months=(24, 36, 60, 96)):
    t = []
    for r in df.itertuples():
        if r.outcome == "committed": end, ev_ = r.commit_month, 1
        elif r.outcome == "cancelled": end, ev_ = r.cancel_month, 2
        else: end, ev_ = HORIZON, 0
        t.append((max(0, (end - r.first_public).n), ev_))
    t = np.array(t); S = 1.0; cif = {1: 0.0, 2: 0.0}; times = np.unique(t[:, 0])
    grid = {mm: None for mm in months}
    for u in times:
        atrisk = (t[:, 0] >= u).sum()
        d1 = ((t[:, 0] == u) & (t[:, 1] == 1)).sum(); d2 = ((t[:, 0] == u) & (t[:, 1] == 2)).sum()
        cif[1] += S * d1 / atrisk; cif[2] += S * d2 / atrisk; S *= 1 - (d1 + d2) / atrisk
        for mm in months:
            if u <= mm: grid[mm] = (cif[1], cif[2])
    return {f"CIF_commit_{mm}m": round(v[0], 3) if v else 0.0 for mm, v in grid.items()} | \
           {f"CIF_cancel_{mm}m": round(v[1], 3) if v else 0.0 for mm, v in grid.items()}


# Amendment A2: imputed first-public dates are used only for date filters, never for durations
dated = prim[~(((prim.outcome == "committed") & prim.commit_month.isna()) | ((prim.outcome == "cancelled") & prim.cancel_month.isna()) | prim.first_public_imputed)]
cr = []
for g, z in dated.groupby("sponsor_status"):
    row = dict(group=g, n=len(z)) | aj(z)
    bs = [aj(z.sample(len(z), replace=True, random_state=int(s)))["CIF_commit_60m"] for s in rng.integers(0, 1e9, 500)]
    row["CIF_commit_60m_boot95"] = f"[{np.percentile(bs, 2.5):.3f}, {np.percentile(bs, 97.5):.3f}]"; cr.append(row)
pd.DataFrame(cr).to_csv(RESULTS / "us_competing_risks.csv", index=False)
lag = dated[dated.outcome == "committed"].assign(lag=lambda d: [max(0, (c - f).n) for c, f in zip(d.commit_month, d.first_public)])
lagt = lag.groupby("sponsor_status").lag.agg(["count", "median", "mean"]).round(1)
lagp = stats.mannwhitneyu(lag[lag.entrant == 1].lag, lag[lag.entrant == 0].lag).pvalue if lag.entrant.nunique() == 2 else np.nan
lagt.assign(mannwhitney_p=round(lagp, 3)).to_csv(RESULTS / "us_commitment_lag.csv")

# ---------------------------------------------------------------- decision criteria R1 to R4
p0 = R.iloc[0]; c16 = R[R["sample"].str.match(r"C[1-6]")]
crit = {
 "R1 primary b <= -0.20": bool(p0.b_entrant <= -0.20),
 "R2 primary within-chain permutation p < 0.05": bool(p0.perm_p_within_chain < 0.05),
 "R3 b < 0 in every check 1-6 incl. every leave-one-chain-out": bool((c16.b_entrant < 0).all()),
 "R4 b <= -0.20 greenfield only": bool(R.loc[R["sample"] == "C4 greenfield only", "b_entrant"].iloc[0] <= -0.20),
}
crit["ALL_CRITERIA_MET (R1-R4)"] = all(crit.values())
json.dump(crit, open(RESULTS / "us_decision_criteria.json", "w"), indent=2)
search = dict(admitted=len(add), admitted_incumbent=int((add.sponsor_status == I).sum()),
              admitted_entrant=int((add.sponsor_status == E).sum()), admitted_ambiguous=int((add.sponsor_status == A).sum()),
              admitted_by_outcome=add.groupby(["sponsor_status", "outcome"]).size().to_dict().__repr__())
json.dump(search, open(RESULTS / "completeness_search_summary.json", "w"), indent=2)

pd.set_option("display.width", 250)
print(R[["sample", "n", "n_incumbent", "n_entrant", "commit_rate_incumbent", "commit_rate_entrant", "b_entrant", "ci95_lo",
         "ci95_hi", "p_hc1", "perm_p_within_chain", "fisher_p", "chains_with_both"]].to_string(index=False))
print(tab); print(cw.round(3)); print(pd.DataFrame(cr).to_string(index=False)); print(lagt, "Mann-Whitney p =", lagp)
print(json.dumps(crit, indent=1)); print(search)
print("site-type codings that differ from register text labels:", int(P.site_disagrees_register_label.sum()))
