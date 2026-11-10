# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Chinese cross-market contrast (Section 7; Table 6; Figure 5).
Step 1, completed from sources before any comparison: end-2025 realization status of every physical
project whose register row has no commissioning date (T2) up to 2025-12
(written to data/derived/china_outcome_completion.csv).
Step 2: competitive status (primary rule: 'established' if the sponsor group operated capacity in the
same chain in China before the first public date; chain = largest-capacity chain row) and ownership
(secondary moderator), coded from sponsor identity only.
Step 3: comparison of realization rates.
Outputs (results/): china_classification.csv, china_contrast.csv, china_ownership.csv
Usage: python src/06_china_contrast.py
"""
import csv

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from common import DERIVED, INPUTS, RESULTS

m = pd.read_csv(INPUTS / "china_project_register.csv")

# ---- Step 1: completion of open outcomes (status at 2025-12). flag=1 marks a coding with residual doubt.
T2C = [  # physical_project_id, realized_by_2025_12, evidence_date, flag, note, source
 ("CN_BOHAI_PDH_TECH_CHANGE", 0, "2024", 0, "fund-raising project withdrawn (register: terminal negative)", "project register audit note"),
 ("CN_COAL_YULIN", 0, "2026-07", 0, "construction completion (zhongjiao) only in Jul 2026", "https://finance.sina.com.cn/money/future/indu/2026-07-16/doc-inihyiyh4432661.shtml"),
 ("CN_DONGHUA_CAofeidian_P1", 0, "2017", 0, "could not start; funds reallocated (register: terminal)", "project register audit note"),
 ("CN_DONGHUA_NINGBO_P2", 1, "2019", 1, "broker report: Ningbo phase II put into operation", "https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/search/rptid/667957788047/index.phtml"),
 ("CN_ETH_HUAJIN_ARAMCO", 0, "2026-10", 0, "first crude cargo Oct 2026; start-up 2027", "https://www.rigzone.com/news/aramcos_new_china_refinery_venture_gets_1st_crude_cargo-14-oct-2026-184848-article"),
 ("CN_MEIJIN_HUASHENG_MEG", 1, "2022", 1, "mechanical completion Dec 2021; issuer later reports 300 kt/y EG capacity in operation", "https://news.futunn.com/en/post/71178120/meijin-energy-000723-sz-the-company-currently-has-an-ethylene"),
 ("CN_MEOH_HUADIAN_YUHENG", 0, "2018-07", 0, "original scope terminated/transferred (register)", "project register audit note"),
 ("CN_SHENHUA_BAOTOU_UPGRADE", 0, "2025-07", 0, "still under construction Jul 2025", "https://finance.sina.com.cn/roll/2025-07-23/doc-infhmxpv3770689.shtml"),
 ("CN_TANGSHAN_XUYANG", 0, "2021-08", 0, "project in 'reserve' status after ownership change", "https://chem.jgvogel.cn/c/2021-08-13/1127079.shtml"),
 ("CN_YANCHANG_YUHENG_REDESIGN", 0, "2024", 1, "still construction-in-progress in 2024 issuer accounts; no start-up found", "project register audit note"),
 ("CN_YULONG_ISLAND_P1", 1, "2025-09", 0, "first cracker in operation; second cracker Sep 2025", "https://energynews.oedigital.com/energy-markets/2025/09/29/sources-chinese-refiner-yulong-has-brought-a-second-steam-cracker-into-operation"),
 ("P2A_BASF_ZHANJIANG", 0, "2026-01", 1, "register T2 = 2026-01 (one month after horizon)", "project register"),
 ("P2A_GULEI_PHASE2", 0, "2024-11", 0, "groundbreaking Nov 2024", "https://wb.fujian.gov.cn/English/latest/202411/t20241120_6569418.htm"),
 ("P2A_SINOPEC_HENAN_ETH", 0, "2025-12", 1, "planned completion Dec 2025; no start-up found by horizon", "https://chem.jgvogel.cn/c1392657.shtml"),
 ("P2A_SINOPEC_MAOMING_ETH", 0, "2024-06", 0, "basic design review completed Jun 2024", "http://lpec.sinopec.com/lpec/en/news/com_news/20240611/news_20240611_612606215766.shtml"),
 ("P2A_SINOPEC_ZHENHAI_15", 0, "2023", 0, "construction start; no start-up by horizon", "https://www.gulfoilandgas.com/webpro1/main/mainnews.asp?id=985854"),
 ("P2A_TARIM_PHASE2", 0, "2026", 0, "first start-up announced 2026", "https://www.tradingview.com/news/reuters.com,2026:newsml_L1N43I0BD:0-petrochina-announces-first-start-up-of-ethylene-project-in-xinjiang/"),
]
with open(DERIVED / "china_outcome_completion.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["physical_project_id", "realized_by_2025_12", "evidence_date", "doubt_flag", "note", "source"]); w.writerows(T2C)
comp = {r[0]: r for r in T2C}

# ---- Step 2: classifications (sponsor identity only)
# pid: (competitive_status, ownership, flag, note)
EST, NEW = "established", "newcomer"
CLS = {
 "CN_BAOFENG_INNER_MONGOLIA_PHASE1": (EST, "private", 0, "Baofeng Ningdong PE/PP since 2014"),
 "CN_BOHAI_PDH_TECH_CHANGE": (EST, "local_SOE", 0, "Bohai PDH operating since 2013"),
 "CN_COAL_YULIN": (EST, "central_SOE", 0, "China Coal Yulin phase I / Mengda PE-PP"),
 "CN_DONGHUA_CAofeidian_P1": (EST, "private", 0, "Donghua Zhangjiagang PDH/PP operating from 2015-05"),
 "CN_DONGHUA_NINGBO_P1": (NEW, "private", 0, "Donghua had no PDH/PP before 2015"),
 "CN_DONGHUA_NINGBO_P2": (EST, "private", 0, "Zhangjiagang PDH operating before 2015-08"),
 "CN_DONGHUA_YANGZIJIANG_P1": (NEW, "private", 0, "LPG distributor entering PDH"),
 "CN_ETH_GULEI": (EST, "central_SOE", 0, "Sinopec-led JV"),
 "CN_ETH_HUAJIN_ARAMCO": (EST, "central_SOE", 0, "Norinco/Huajin operated ethylene in Panjin"),
 "CN_ETH_SHENGHONG": (EST, "private", 1, "Shenghong Sierbang MTO produced ethylene from 2016"),
 "CN_ETH_TIANJIN_NANGANG": (EST, "central_SOE", 0, "Sinopec"),
 "CN_ETH_WUHAN": (EST, "central_SOE", 0, "Sinopec"),
 "CN_FUJIAN_MEIDE_PDH_P1": (NEW, "private", 0, "China Soft Packaging/Meide new to PDH"),
 "CN_GUANGHUI_HAMI_MEG": (NEW, "private", 0, "Guanghui new to MEG"),
 "CN_JUZHENGYUAN_DONGGUAN_P1": (NEW, "private", 0, ""),
 "CN_JUZHENGYUAN_DONGGUAN_P2": (EST, "private", 0, "phase I operating since 2019"),
 "CN_MEIJIN_HUASHENG_MEG": (NEW, "private", 0, "coke producer new to MEG"),
 "CN_MEOH_HUADIAN_YUHENG": (NEW, "central_SOE", 1, "Huadian (power group) without prior methanol capacity"),
 "CN_MEOH_SHENHUA_YULIN": (EST, "central_SOE", 0, "primary chain methanol; Shenhua operated methanol (Baotou)"),
 "CN_QINGDAO_HAIWAN_PVC": (EST, "local_SOE", 0, ""),
 "CN_QIXIANG_PDH": (NEW, "private", 1, "no prior PDH/propylene unit"),
 "CN_SATELLITE_LYG_C2_STAGE2": (NEW, "private", 1, "no EO/EG operating before 2020-02 (stage I started 2021)"),
 "CN_SATELLITE_PINGHU_PDH_P1": (NEW, "private", 0, ""),
 "CN_SHENHUA_BAOTOU_UPGRADE": (EST, "central_SOE", 0, "Baotou CTO PP since 2010"),
 "CN_TANGSHAN_XUYANG": (NEW, "private", 0, "coke group new to refining/ethylene"),
 "CN_TIANJIN_BOHUA_PVC_P2": (EST, "local_SOE", 0, ""),
 "CN_WANHUA_YANTAI_ETHYLENE": (NEW, "local_SOE", 0, "Wanhua had PDH but no ethylene before 2018-11"),
 "CN_WANHUA_YANTAI_HDPE_PP": (NEW, "local_SOE", 1, "no PE/PP unit before 2019 (to be verified)"),
 "CN_YANCHANG_YUHENG_REDESIGN": (EST, "local_SOE", 0, "Yanchang operated methanol (Yulin/Jingbian)"),
 "CN_YULONG_ISLAND_P1": (NEW, "local_SOE", 0, "new entity; no prior ethylene"),
 "CN_ZHONGJIANG_PP1": (NEW, "private", 0, ""),
 "CN_ZHONGJING_PP1": (NEW, "private", 0, ""),
 "CN_ZHONGJING_PP_1200": (EST, "private", 0, "Zhongjing PP operating since 2016"),
 "CN_ZHONGTAI_FUKANG_PVC_P1": (EST, "local_SOE", 0, ""),
 "CN_ZPC_ZHOUSHAN_P1": (NEW, "private", 0, "Rongsheng-led; no prior ethylene"),
 "CN_ZPC_ZHOUSHAN_P2": (NEW, "private", 0, "same approval date as phase I"),
 "P2A_BASF_ZHANJIANG": (EST, "foreign", 0, "BASF-YPC Nanjing cracker"),
 "P2A_EXXON_HUIZHOU": (EST, "foreign", 0, "ExxonMobil in FREP Fujian cracker"),
 "P2A_FUJIAN_FREP_2007": (EST, "foreign_JV", 0, "Sinopec-led JV with Aramco/ExxonMobil"),
 "P2A_GUANGXI_TRANSFORMATION": (EST, "central_SOE", 0, "PetroChina"),
 "P2A_GULEI_PHASE2": (EST, "central_SOE", 0, "Sinopec-led JV"),
 "P2A_JILIN_TRANSFORMATION": (EST, "central_SOE", 0, "PetroChina"),
 "P2A_SINOPEC_HENAN_ETH": (EST, "central_SOE", 0, "Sinopec"),
 "P2A_SINOPEC_MAOMING_ETH": (EST, "central_SOE", 0, "Sinopec"),
 "P2A_SINOPEC_ZHENHAI_15": (EST, "central_SOE", 0, "Sinopec"),
 "P2A_TARIM_PHASE2": (EST, "central_SOE", 0, "PetroChina"),
}
# Explicit date parsing (robust across pandas versions; one row has no T1 anchor; amendment A10)
for c in ["t1_date_or_anchor", "t2_date"]:
    m[c] = m[c].map(lambda v: str(v)[:10] if isinstance(v, str) and v.strip() else None)
    m[c + "_dt"] = pd.to_datetime(m[c], errors="coerce", format="mixed")
g = m.groupby("physical_project_id", sort=True)
base_summary = g.agg(
    t1=("t1_date_or_anchor_dt", "min"),
    t2_min=("t2_date_dt", "min"),
    capacity_tpa=("capacity_tpa", "sum"),
).reset_index()
primary_chain = (
    m.sort_values(["physical_project_id", "capacity_tpa"], ascending=[True, False])
     .drop_duplicates("physical_project_id")[["physical_project_id", "product_chain"]]
     .rename(columns={"product_chain": "primary_chain"})
)
P = base_summary.merge(primary_chain, on="physical_project_id", how="left", validate="one_to_one")
P["t1"] = P["t1"].dt.strftime("%Y-%m-%d")
P["t2_min"] = P["t2_min"].dt.strftime("%Y-%m-%d")
assert set(P.physical_project_id) == set(CLS), set(P.physical_project_id) ^ set(CLS)
def realized(r):
    if r.physical_project_id in comp: return comp[r.physical_project_id][1]
    return int(pd.notna(r.t2_min) and str(r.t2_min)[:7] <= "2025-12")
P["realized"] = P.apply(realized, axis=1)
P["outcome_doubt"] = P.physical_project_id.map(lambda k: comp[k][3] if k in comp else 0)
P["status"] = P.physical_project_id.map(lambda k: CLS[k][0]); P["ownership"] = P.physical_project_id.map(lambda k: CLS[k][1])
P["status_doubt"] = P.physical_project_id.map(lambda k: CLS[k][2]); P["coding_note"] = P.physical_project_id.map(lambda k: CLS[k][3])
P["newcomer"] = P.status.eq(NEW).astype(int); P["t1_le_2022"] = P.t1.astype(str).str[:7] <= "2022-12"
P["logcap"] = np.log(P.capacity_tpa.fillna(P.capacity_tpa.median()))
P.to_csv(RESULTS / "china_classification.csv", index=False)

def compare(d, label):
    e, n = d[d.newcomer == 0], d[d.newcomer == 1]
    a = [[int(n.realized.sum()), int(len(n) - n.realized.sum())], [int(e.realized.sum()), int(len(e) - e.realized.sum())]]
    X = sm.add_constant(d[["newcomer", "logcap"]].astype(float)); f = sm.OLS(d.realized.astype(float), X).fit(cov_type="HC1")
    return dict(sample=label, n=len(d), n_established=len(e), n_newcomer=len(n),
                realized_established=round(e.realized.mean(), 3), realized_newcomer=round(n.realized.mean(), 3),
                gap=round(n.realized.mean() - e.realized.mean(), 3), fisher_p=round(stats.fisher_exact(a)[1], 4),
                b_newcomer_adj_logcap=round(f.params["newcomer"], 3), p_hc1=round(f.pvalues["newcomer"], 4),
                direction_consistent=bool(n.realized.mean() < e.realized.mean()))
flip_out = P.copy(); flip_out.loc[flip_out.outcome_doubt == 1, "realized"] = 1 - flip_out.loc[flip_out.outcome_doubt == 1, "realized"]
flip_st = P.copy(); flip_st.loc[flip_st.status_doubt == 1, "newcomer"] = 1 - flip_st.loc[flip_st.status_doubt == 1, "newcomer"]
rows = [compare(P, "PRIMARY: all 46 physical projects"),
        compare(P[P.t1_le_2022], "first public <= 2022-12 (>=36 months follow-up; analogous to U.S. rule)"),
        compare(flip_out, "doubtful outcome codings flipped"),
        compare(flip_st, "doubtful status codings flipped"),
        compare(P[P.ownership != "central_SOE"], "excluding central SOEs"),
        compare(P[P.ownership == "private"], "private sponsors only")]
R = pd.DataFrame(rows); R.to_csv(RESULTS / "china_contrast.csv", index=False)
own = P.groupby(["ownership", "status"]).realized.agg(["count", "sum", "mean"]).round(3); own.to_csv(RESULTS / "china_ownership.csv")
pd.set_option("display.width", 250); print(R.to_string(index=False)); print(own)
