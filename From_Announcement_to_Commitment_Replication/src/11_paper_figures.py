# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Figures 1 to 7 of the article, drawn from the result files only (PNG at 300 dpi and PDF).

No model is re-estimated, except that the Aalen-Johansen curves for Figure 3 are recomputed from the
project classification file and asserted equal to the competing-risk table before plotting.
Output: results/figures/
Usage: python src/11_paper_figures.py
"""
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import FIGURES as OUTDIR, RESULTS as R

INC, ENT, INK, GRID = "#2F5D8A", "#C8553D", "#222222", "#D9D9D9"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": "#555555", "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "savefig.dpi": 300, "figure.dpi": 110, "axes.unicode_minus": False,
})


def save(fig, stem):
    fig.savefig(OUTDIR / f"{stem}.png", bbox_inches="tight")
    fig.savefig(OUTDIR / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1
t = pd.read_csv(R / "us_sponsor_by_site.csv")
order = [("incumbent", "brownfield"), ("incumbent", "greenfield"), ("entrant", "brownfield"), ("entrant", "greenfield")]
t = t.set_index(["sponsor_status", "site_type"]).loc[order].reset_index()
fig, ax = plt.subplots(figsize=(6.6, 3.0))
y = np.arange(len(t))[::-1]
cols = [INC if s == "incumbent" else ENT for s in t.sponsor_status]
alph = [1.0 if st == "brownfield" else 0.55 for st in t.site_type]
for yy, r, c, a in zip(y, t.itertuples(), cols, alph):
    ax.barh(yy, r.commit_rate * 100, color=c, alpha=a, height=0.62, edgecolor="none")
    ax.text(r.commit_rate * 100 + 1.5, yy, f"{r.commit_rate*100:.1f}%  ({r.committed}/{r.projects})",
            va="center", fontsize=9, color=INK)
ax.set_yticks(y, [f"{s.capitalize()}, {st}" for s, st in zip(t.sponsor_status, t.site_type)])
ax.set_xlim(0, 125)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xlabel("Projects reaching binding commitment by December 2025 (%)")
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
save(fig, "figure1_commitment_by_sponsor_site")

# ---------------------------------------------------------------- Figure 2
f1 = pd.read_csv(R / "robustness_coefficients.csv")
label_map = {
    "Primary": "Primary specification",
    "C1a ambiguous as incumbent": "Ambiguous sponsors coded incumbent",
    "C1b ambiguous as entrant": "Ambiguous sponsors coded entrant",
    "C2 excluding methanol": "Methanol excluded",
    "C3 excluding >2500 kt/y": "Projects > 2,500 kt/y excluded",
    "C4 greenfield only": "Greenfield projects only",
    "C5 leave out EO_MEG": "Leave out EO/MEG",
    "C5 leave out PVC_VCM": "Leave out PVC/VCM",
    "C5 leave out ethylene": "Leave out ethylene",
    "C5 leave out polyethylene": "Leave out polyethylene",
    "C5 leave out polypropylene": "Leave out polypropylene",
    "C5 leave out propylene": "Leave out propylene",
    "C6 including first public after 2022-12": "Projects first public after 2022 included",
    "RB2 Freedman-Lane (chain FE, HC1 t)": "Chain fixed effects (Freedman-Lane)",
    "RB3 commitment within 36 months of first public": "Commitment within 36 months",
    "RB4 primary model + months of follow-up": "Follow-up months as control",
    "RB5 site type from register text labels": "Site type from descriptive labels",
    "S1 brownfield only": "Brownfield projects only",
    "Regulatory-filing subset": "Regulatory-filing subset",
}
f1 = f1[f1.specification.isin(label_map)].copy()
f1["label"] = f1.specification.map(label_map)
groups = ["Primary", "Pre-specified", "Companion", "Supplementary", "Regulatory"]
gtitle = {"Primary": "Primary", "Pre-specified": "Pre-specified robustness checks",
          "Companion": "Companion analyses", "Supplementary": "Supplementary analysis",
          "Regulatory": "Regulatory-visibility companion"}
marker = {"Primary": "D", "Pre-specified": "o", "Companion": "s", "Supplementary": "^", "Regulatory": "v"}
rows, ypos, yy = [], [], 0
heads = []
for g in groups:
    sub = f1[f1.category == g]
    if sub.empty:
        continue
    heads.append((yy, gtitle[g])); yy += 1
    for r in sub.itertuples():
        rows.append((yy, r, g)); yy += 1
    yy += 0.4
fig, ax = plt.subplots(figsize=(4.4, 7.4))
for y0, r, g in rows:
    col = INK if g == "Primary" else "#4A4A4A"
    ax.plot([r.ci_lo, r.ci_hi], [y0, y0], color=col, lw=1.4)
    ax.plot(r.b, y0, marker=marker[g], color=col, ms=6 if g == "Primary" else 5,
            mfc=col if g in ("Primary", "Pre-specified") else "white")
ax.axvline(0, color="#777777", lw=0.9)
ax.axvline(-0.20, color="#777777", lw=0.9, ls=(0, (4, 3)))
ax.text(-0.20, -1.15, "Pre-specified\nthreshold (-0.20)", ha="center", va="bottom", fontsize=8, color="#555555")
ax.set_yticks([y for y, _, _ in rows], [f"{r.label}  (n={r.n})" for _, r, _ in rows], fontsize=8.6)
for y0, txt in heads:
    ax.text(-1.17, y0, txt, fontweight="bold", fontsize=8.8, va="center", ha="left",
            transform=ax.transData)
ax.set_xlim(-1.15, 0.15)
ax.set_ylim(yy - 0.2, -1.4)
ax.set_xlabel("Entrant coefficient (probability points) with 95% HC1 interval")
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
save(fig, "figure2_entrant_coefficient_robustness")

# ---------------------------------------------------------------- Figure 3 (Aalen-Johansen, recomputed and checked)
u = pd.read_csv(R / "us_project_classification.csv")
prim = u[(u.sponsor_status != "ambiguous") & (u.fp_le_2022)].copy()
assert len(prim) == 76
for c in ["first_public", "commit_month", "cancel_month"]:
    prim[c] = pd.to_datetime(prim[c], format="%Y-%m", errors="coerce").dt.to_period("M")
HOR = pd.Period("2025-12", "M")
dated = prim[~(((prim.outcome == "committed") & prim.commit_month.isna())
              | ((prim.outcome == "cancelled") & prim.cancel_month.isna())
              | prim.first_public_imputed)]


def aj_curve(df):
    tt = []
    for r in df.itertuples():
        if r.outcome == "committed":
            end, e = r.commit_month, 1
        elif r.outcome == "cancelled":
            end, e = r.cancel_month, 2
        else:
            end, e = HOR, 0
        tt.append((max(0, (end - r.first_public).n), e))
    tt = np.array(tt)
    S, c1, c2 = 1.0, 0.0, 0.0
    xs, y1, y2 = [0], [0.0], [0.0]
    for v in np.unique(tt[:, 0]):
        risk = (tt[:, 0] >= v).sum()
        d1 = ((tt[:, 0] == v) & (tt[:, 1] == 1)).sum()
        d2 = ((tt[:, 0] == v) & (tt[:, 1] == 2)).sum()
        c1 += S * d1 / risk; c2 += S * d2 / risk; S *= 1 - (d1 + d2) / risk
        xs.append(int(v)); y1.append(c1); y2.append(c2)
    return np.array(xs), np.array(y1), np.array(y2), len(df)


def at(xs, ys, m):
    return ys[xs <= m][-1]


cr_table = pd.read_csv(R / "us_competing_risks.csv").set_index("group")
curves = {}
for g in ["incumbent", "entrant"]:
    xs, y1, y2, n = aj_curve(dated[dated.sponsor_status == g])
    assert n == cr_table.loc[g, "n"]
    for m in (24, 36, 60, 96):
        assert abs(round(at(xs, y1, m), 3) - cr_table.loc[g, f"CIF_commit_{m}m"]) < 1e-9, (g, m)
        assert abs(round(at(xs, y2, m), 3) - cr_table.loc[g, f"CIF_cancel_{m}m"]) < 1e-9, (g, m)
    curves[g] = (xs, y1, y2, n)
fig, ax = plt.subplots(figsize=(6.6, 3.8))
xmax = 120
for g, col in [("incumbent", INC), ("entrant", ENT)]:
    xs, y1, y2, n = curves[g]
    xs_e = np.r_[xs, xmax]
    ax.step(xs_e, np.r_[y1, y1[-1]] * 100, where="post", color=col, lw=1.9,
            label=f"{g.capitalize()}: commitment (n={n})")
    ax.step(xs_e, np.r_[y2, y2[-1]] * 100, where="post", color=col, lw=1.3, ls=(0, (4, 2.5)),
            label=f"{g.capitalize()}: cancellation")
for m in (24, 36, 60):
    ax.axvline(m, color=GRID, lw=0.7, zorder=0)
ax.set_xlim(0, xmax); ax.set_ylim(0, 100)
ax.set_xticks([0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120])
ax.set_xlabel("Months since first public announcement")
ax.set_ylabel("Cumulative incidence (%)")
ax.legend(frameon=False, fontsize=8.4, loc="center right", bbox_to_anchor=(1.0, 0.55))
save(fig, "figure3_cumulative_incidence")

# ---------------------------------------------------------------- Figure 4
rv = pd.read_csv(R / "regulatory_visibility.csv")
cov = rv[rv.analysis.eq("RV1 coverage")].set_index("group")
rv3 = rv[rv.analysis.str.startswith("RV3 primary")].iloc[0]
m_ = re.search(r"commit rate inc ([0-9.]+) / ent ([0-9.]+); n_inc (\d+), n_ent (\d+)", str(rv3.note))
inc_r, ent_r, ni, ne = float(m_.group(1)), float(m_.group(2)), int(m_.group(3)), int(m_.group(4))
fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0), gridspec_kw={"wspace": 0.55})
for ax, vals, ns, ylab in [
    (axs[0], [cov.loc["incumbent", "value"] * 100, cov.loc["entrant", "value"] * 100], [48, 28],
     "Projects with a qualifying\nregulatory filing (%)"),
    (axs[1], [inc_r * 100, ent_r * 100], [ni, ne], "Commitment rate in the\nfiling-covered subset (%)")]:
    b = ax.bar(["Incumbent", "Entrant"], vals, color=[INC, ENT], width=0.58)
    for bb, v, n in zip(b, vals, ns):
        ax.text(bb.get_x() + bb.get_width() / 2, v + 2, f"{v:.1f}%\n(n={n})", ha="center", va="bottom", fontsize=8.6)
    ax.set_ylim(0, 118); ax.set_yticks([0, 20, 40, 60, 80, 100]); ax.set_ylabel(ylab)
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[0].set_title("(a) Filing coverage", fontsize=9.5, loc="left")
axs[1].set_title("(b) Commitment, filing-covered", fontsize=9.5, loc="left")
save(fig, "figure4_regulatory_filing_subset")

# ---------------------------------------------------------------- Figure 5
pr = pd.read_csv(R / "us_primary_and_checks.csv").iloc[0]
ch = pd.read_csv(R / "china_contrast.csv").iloc[0]
fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0), gridspec_kw={"wspace": 0.5})
panels = [
    (axs[0], "(a) United States: binding commitment", ["Incumbent", "Entrant"],
     [pr.commit_rate_incumbent * 100, pr.commit_rate_entrant * 100], [int(pr.n_incumbent), int(pr.n_entrant)],
     "Committed by Dec 2025 (%)"),
    (axs[1], "(b) China: commercial operation", ["Established", "Newcomer"],
     [ch.realized_established * 100, ch.realized_newcomer * 100], [int(ch.n_established), int(ch.n_newcomer)],
     "Operating by Dec 2025 (%)"),
]
for ax, ttl, labs, vals, ns, ylab in panels:
    b = ax.bar(labs, vals, color=[INC, ENT], width=0.58)
    for bb, v, n in zip(b, vals, ns):
        ax.text(bb.get_x() + bb.get_width() / 2, v + 2, f"{v:.1f}%\n(n={n})", ha="center", va="bottom", fontsize=8.6)
    ax.set_ylim(0, 118); ax.set_yticks([0, 20, 40, 60, 80, 100]); ax.set_ylabel(ylab)
    ax.set_title(ttl, fontsize=9.5, loc="left")
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
save(fig, "figure5_us_china_contrast")

# ---------------------------------------------------------------- Figure 6
br = pd.read_csv(R / "brier_comparisons.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.2))
spec = {"rolling_stage - unconditional": ("Unconditional base rate", "#4A4A4A", "o", -0.14),
        "rolling_stage - chain_base": ("Chain-specific base rate", "#7A9CC6", "s", 0.14)}
for comp, (lab, col, mk, off) in spec.items():
    z = br[br.comparison.eq(comp)].sort_values("horizon")
    yv = np.arange(len(z)) + off
    ax.errorbar(z["diff"], yv, xerr=[z["diff"] - z.ci95_lo, z.ci95_hi - z["diff"]], fmt=mk, color=col,
                ms=5.5, capsize=2.5, lw=1.3, label=lab)
ax.axvline(0, color="#777777", lw=0.9)
ax.set_yticks(np.arange(3), ["12 months", "24 months", "36 months"])
ax.invert_yaxis()
ax.set_xlabel("Brier-score difference: stage model minus benchmark (negative favours stage model)")
ax.legend(frameon=False, fontsize=8.4, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
save(fig, "figure6_brier_differences")

# ---------------------------------------------------------------- Figure 7
d7 = pd.read_csv(R / "expected_capacity_decomposition.csv")
fig, ax = plt.subplots(figsize=(5.4, 2.4))
cols = [INC, "#9E9E9E", "#BDBDBD"]
labs = ["Project information", "Commissioning exits", "Probability-model recalibration"]
yv = np.arange(3)[::-1]
ax.barh(yv, d7.share_percent, color=cols, height=0.6)
for yy, v in zip(yv, d7.share_percent):
    ax.text(v + 0.8, yy, f"{v:.1f}%", va="center", fontsize=9)
ax.set_yticks(yv, labs)
ax.set_xlim(0, 50)
ax.set_xlabel("Share of gross absolute movement in foreign expected capacity (%)")
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
save(fig, "figure7_expected_capacity_decomposition")
print("figures written to", OUTDIR)
