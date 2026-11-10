# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Preliminary incumbent-response panel: news construction and fixed-effect support diagnostic
(Sections 3.3 and 8.2; Figure 7; Supporting Information, Appendix S1 and Table S1).

Builds lagged foreign (F), domestic announced (A) and domestic committed (C) rival-capacity news for a
firm x chain x month panel of 2010 U.S. incumbents, and evaluates, before any outcome model is
estimated, whether the candidate fixed-effect structures leave enough identifying variation.
No outcome coefficient is estimated in this script.

Measurement rules:
  * foreign news F contains information news only; commissioning (T2) exits and probability-model
    recalibration are separated using the same-origin probability function of the calibration ledger;
  * firm-chain-months whose commitment-event status is unresolved are removed from the support
    sample rather than coded as non-events;
  * Westlake-Axiall ownership applies only from the acquisition date (Aug 2016).

Support thresholds, fixed before the support statistics were computed:
  * variance surviving the fixed effects >= 0.01 for each of X_F, X_A, X_C;
  * >= 100 observations with non-negligible residualized variation per regressor;
  * >= 5 qualifying commitment events with non-negligible residualized variation per regressor;
  * effective-chain count >= 3.0 for each regressor (inverse HHI of residual variance);
  * maximum absolute pairwise residualized correlation among X_F, X_A, X_C <= 0.95.
The preferred fixed-effect structure is tested first; the fallback is considered only if it fails.
The minimum detectable effect is reported for information but is not a pass/fail criterion.

Outputs (results/incumbent_panel/): see the write block at the end of main().
Usage: python src/09_incumbent_panel_support.py
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from common import CONFIG, INPUTS as D, PANEL as R, ROLLING as R0

START = pd.Period("2010-01", freq="M")
END = pd.Period("2025-12", freq="M")
PRIMARY_H = 24
TOL = 1e-12
THRESH = {
    "min_variance_survival": 0.01,
    "min_nonzero_observations": 100,
    "min_contributing_events": 5,
    "min_effective_chains": 3.0,
    "max_abs_pairwise_corr": 0.95,
}

CHAIN_MAP = {
    "ethylene":"ethylene", "polyethylene":"polyethylene", "polypropylene":"polypropylene",
    "propylene_pdh":"propylene_PGP", "propylene_PDH":"propylene_PGP", "propylene_PGP":"propylene_PGP",
    "eo_meg":"EO_MEG", "EO_MEG":"EO_MEG", "edc_pvc":"PVC_VCM", "PVC_VCM":"PVC_VCM",
    "methanol":"methanol",
}
DENOM_SOURCE = {
    "ethylene":"ethylene", "polyethylene":"polyethylene", "polypropylene":"polypropylene",
    "propylene_PGP":"propylene_pdh", "EO_MEG":"eo_meg", "PVC_VCM":"edc_pvc", "methanol":"methanol",
}

# Explicit event-sponsor -> 2010 incumbent owner mapping. Absence means the
# project remains in the rival universe but is not a primary incumbent outcome.
EVENT_OWNER = {
    ("ethylene","Sasol"):"Sasol",
    ("ethylene","LyondellBasell"):"LyondellBasell",
    ("ethylene","Shell Chemical Appalachia"):"Shell Chemical",
    ("ethylene","Chevron Phillips Chemical"):"Chevron Phillips Chemical",
    ("ethylene","Chevron Phillips Chemical / QatarEnergy"):"Chevron Phillips Chemical",
    ("ethylene","Dow / Union Carbide"):"Dow Chemical",
    ("ethylene","ExxonMobil / SABIC"):"ExxonMobil",
    ("ethylene","Formosa Plastics Corporation USA"):"Formosa Plastics USA",
    ("ethylene","Westlake"):"Westlake",
    ("ethylene","Westlake Chemical"):"Westlake",
    ("ethylene","Williams / Williams Partners"):"Williams",
    # LACC is not mapped: committed 2015-12, before Westlake acquired Axiall (2016-08)
    ("polyethylene","Chevron Phillips Chemical"):"Chevron Phillips Chemical",
    ("polyethylene","Dow"):"Dow Chemical",
    ("polyethylene","ExxonMobil"):"ExxonMobil",
    ("polyethylene","ExxonMobil / SABIC"):"ExxonMobil",
    ("polyethylene","INEOS / Sasol"):"INEOS",
    ("polyethylene","LyondellBasell"):"LyondellBasell/Equistar",
    ("polyethylene","Bayport Polymers (Total/Borealis/NOVA)"):"Total Petrochemicals",
    ("polypropylene","Braskem"):"Braskem",
    ("polypropylene","ExxonMobil"):"ExxonMobil",
    ("propylene_PGP","Enterprise Products Partners"):"Enterprise Products Partners",
    ("propylene_PGP","LyondellBasell"):"LyondellBasell (Equistar)",
    ("PVC_VCM","Formosa Plastics Corporation U.S.A."):"Formosa Plastics USA",
    ("PVC_VCM","Formosa Plastics Corporation USA"):"Formosa Plastics USA",
    ("PVC_VCM","Shintech / Shin-Etsu"):"Shintech",
    ("PVC_VCM","Westlake Chemical"):"Westlake",
    ("methanol","LyondellBasell"):"LyondellBasell (La Porte Methanol)",
}

# Focal ownership tokens are deliberately conservative. They are used only to remove
# a focal firm's own project from its domestic-rival series. No token means no removal.
OWN_TOKENS = {
 "BASF/FINA LP":["basf"], "Chevron Phillips Chemical":["chevronphillips"], "Dow Chemical":["dow"],
 "DuPont":["dupont"], "Eastman Chemical":["eastman"], "ExxonMobil":["exxonmobil"],
 "Flint Hills Resources":["flinthills"], "Formosa Plastics USA":["formosaplastics"], "Huntsman":["huntsman"],
 "INEOS":["ineos"], "Javelina":["javelina"], "LyondellBasell":["lyondellbasell"], "Sasol":["sasol"],
 "Shell Chemical":["shellchemical"], "Westlake":["westlake"], "Williams":["williams"],
 "Braskem":["braskem"], "ConocoPhillips":["conocophillips"], "Pinnacle Polymers":["pinnacle"],
 "Total Petrochemicals":["total","bayport"], "Enterprise Products Partners":["enterprise"],
 "LyondellBasell (Equistar)":["lyondellbasell","equistar"], "BP":["bp"], "Marathon Petroleum":["marathon"],
 "Sunoco":["sunoco"], "Shintech":["shintech"], "Oxy Vinyls":["oxy"], "Georgia Gulf":["georgiagulf"],
 "CertainTeed":["certainteed"], "PolyOne":["polyone"], "Tekni-Plex":["tekniplex"],
 "LyondellBasell (La Porte Methanol)":["lyondellbasell"], "CF Industries (Terra)":["cfindustries","terra"],
 "Praxair":["praxair"], "BASF":["basf"], "Formosa Plastics":["formosaplastics"], "Huntsman":["huntsman"],
 "Old World Industries":["oldworld"], "Shell Chemicals":["shell"], "Eastman Chemical":["eastman"],
 "LyondellBasell/Equistar":["lyondellbasell","equistar"], "Honeywell":["honeywell"], "Ticona":["ticona"],
 "Chevron Phillips/INEOS JV":["chevronphillipsineos"], "Chevron Phillips/Sumitomo JV":["chevronphillipssumitomo"],
 "Epsilon JV":["epsilon"], "Epsilon C3 Polymers":["epsilon"], "Enterprise/LyondellBasell JV":["enterpriselyondellbasell"],
 "Enterprise/Total JV":["enterprisetotal"], "Williams/SABIC":["williamssabic"], "Gulf Liquids":["gulfliquids"],
 "PL Propylene":["plpropylene"],
}

def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())

def pmonth(x):
    if pd.isna(x) or str(x).strip()=="": return None
    s=str(x).strip()
    try: return pd.Period(s[:7], freq="M")
    except Exception:
        try: return pd.Period(str(pd.to_datetime(s)).strip()[:7], freq="M")
        except Exception: return None

def demean_multi(df, cols, groups, max_iter=500, tol=1e-12):
    arr=df[cols].to_numpy(float).copy()
    # integer codes for speed and determinism
    codes=[]
    for keys in groups:
        if isinstance(keys, str): keys=[keys]
        mi=pd.MultiIndex.from_frame(df[list(keys)].astype(str))
        codes.append(pd.factorize(mi, sort=True)[0])
    for _ in range(max_iter):
        old=arr.copy()
        for c in codes:
            n=c.max()+1
            cnt=np.bincount(c, minlength=n).astype(float)
            for j in range(arr.shape[1]):
                sm=np.bincount(c, weights=arr[:,j], minlength=n)
                arr[:,j]-=sm[c]/cnt[c]
        if np.max(np.abs(arr-old))<tol: break
    return pd.DataFrame(arr, columns=[f"r_{c}" for c in cols], index=df.index)

def build_foreign():
    stage=pd.read_csv(D/'china_stage_project_month.csv', dtype={'snapshot_month':str})
    pred=pd.read_csv(R0/'predictions.csv', dtype={'snapshot_month':str})
    pred=pred[pred.horizon_months.eq(PRIMARY_H)].copy()
    x=stage.merge(pred[['snapshot_month','physical_project_id','product_chain','rolling_probability']],
                  on=['snapshot_month','physical_project_id','product_chain'], how='left', validate='one_to_one')
    if x.rolling_probability.isna().any(): raise RuntimeError('missing rolling probabilities in H24 merge')
    x['month']=x.snapshot_month.map(pmonth); x['chain']=x.product_chain.map(CHAIN_MAP)
    x['E_tpa']=x.harmonized_capacity_tpa.astype(float)*x.rolling_probability.astype(float)
    x['V_tpa2']=(x.harmonized_capacity_tpa.astype(float)**2)*x.rolling_probability*(1-x.rolling_probability)
    months=pd.period_range(START,END,freq='M')
    rows=[]
    for (pid,ch),g in x.groupby(['physical_project_id','chain']):
        q=g.set_index('month').sort_index()
        t2=next((pmonth(z) for z in g.t2_month if pmonth(z) is not None), None)
        tn=next((pmonth(z) for z in g.terminal_negative_month if pmonth(z) is not None), None)
        terminal=min([z for z in [t2,tn] if z is not None], default=None)
        first=q.index.min()
        for m in months:
            if m<first or (terminal is not None and m>=terminal): e=v=0.0
            elif m in q.index:
                rr=q.loc[m]
                if isinstance(rr,pd.DataFrame): rr=rr.iloc[0]
                e=float(rr.E_tpa); v=float(rr.V_tpa2)
            else:
                # Stage panel is intended monthly-contiguous while active. Missing interior
                # rows are not silently forward-filled.
                e=v=0.0
            rows.append((pid,ch,str(m),e,v))
    pm=pd.DataFrame(rows,columns=['physical_project_id','chain','month','expected_capacity_tpa','variance_tpa2'])
    pm['dE_tpa']=pm.groupby(['physical_project_id','chain'])['expected_capacity_tpa'].diff().fillna(pm.expected_capacity_tpa)
    # ---- decomposition of dE into information news / commissioning exit / probability-model recalibration
    led=pd.read_csv(R0/'calibration_ledger.csv', dtype={'snapshot_month':str})
    led=led[led.horizon_months.eq(PRIMARY_H)].drop_duplicates(['snapshot_month','physical_project_id'])
    pfun={(r.snapshot_month,r.physical_project_id):r for r in led.itertuples(index=False)}
    info=[];comm=[];drift=[]
    stg=x.set_index(['physical_project_id','chain','month'])
    for (pid,ch),g in pm.groupby(['physical_project_id','chain'],sort=False):
        t2=next((pmonth(z) for z in x[(x.physical_project_id==pid)&(x.chain==ch)].t2_month if pmonth(z) is not None), None)
        prev=None
        for idx,r in g.iterrows():
            m=pmonth(r.month); key=(pid,ch,m)
            cur=stg.loc[key] if key in stg.index else None
            if isinstance(cur,pd.DataFrame): cur=cur.iloc[0]
            dE=r.dE_tpa
            if abs(dE)<=TOL: info.append(0.0);comm.append(0.0);drift.append(0.0)
            elif cur is None:                      # exit month (E -> 0)
                if t2 is not None and m==t2: info.append(0.0);comm.append(dE);drift.append(0.0)
                else: info.append(dE);comm.append(0.0);drift.append(0.0)   # terminal negative = information
            elif prev is None: info.append(dE);comm.append(0.0);drift.append(0.0)  # entry = information
            else:
                q0,s0,p0=prev; q1=float(cur.harmonized_capacity_tpa); s1=cur.canonical_stage
                L=pfun.get((str(m),pid)); col='repaired_'+s0
                p_t_s0=float(getattr(L,col)) if (L is not None and hasattr(L,col) and pd.notna(getattr(L,col))) else p0
                d=q0*(p_t_s0-p0); drift.append(d); info.append(dE-d); comm.append(0.0)
            prev=(float(cur.harmonized_capacity_tpa),cur.canonical_stage,float(cur.rolling_probability)) if cur is not None else None
    pm['dE_info_tpa']=info; pm['dE_commission_tpa']=comm; pm['dE_drift_tpa']=drift
    assert np.allclose(pm.dE_tpa, pm.dE_info_tpa+pm.dE_commission_tpa+pm.dE_drift_tpa)
    cm=pm.groupby(['chain','month'],as_index=False).agg(F_news_total_tpa=('dE_tpa','sum'),F_news_tpa=('dE_info_tpa','sum'),
        F_commission_tpa=('dE_commission_tpa','sum'),F_drift_tpa=('dE_drift_tpa','sum'),E_stock_tpa=('expected_capacity_tpa','sum'),V_tpa2=('variance_tpa2','sum'))
    den=pd.read_csv(D/'world_capacity_2010.csv').set_index('chain').world_capacity_2010_ktpa.to_dict()
    cm['world_denom_ktpa']=cm.chain.map(lambda c:float(den[DENOM_SOURCE[c]]))
    cm['F_news_norm']=cm.F_news_tpa/(cm.world_denom_ktpa*1000.0)
    cm['sigma24_norm']=np.sqrt(cm.V_tpa2)/(cm.world_denom_ktpa*1000.0)
    cm['period']=cm.month.map(pmonth)
    cm=cm.sort_values(['chain','period'])
    cm['F_12']=cm.groupby('chain').F_news_norm.transform(lambda s:s.shift(1).rolling(12,min_periods=12).sum())
    cm['sigma24_lag1']=cm.groupby('chain').sigma24_norm.shift(1)
    return pm,cm

def build_domestic(ms):
    master=pd.read_csv(D/'us_project_register.csv')
    ev=pd.read_csv(D/'us_project_events.csv')
    cmap=pd.read_csv(D/'us_project_chain_map.csv')
    sponsor=master.drop_duplicates('project_id').set_index('project_id')['sponsor'].to_dict()
    # project-chain paths, one flow per source-locked state transition
    months=pd.period_range(START,END,freq='M')
    out=[]
    audit=[]
    for r in cmap.itertuples(index=False):
        pid=str(r.project_id); ch=CHAIN_MAP.get(str(r.chain)); q=float(r.capacity_ktpa)
        if ch is None: continue
        ee=ev[ev.project_id.astype(str).eq(pid)].copy()
        ee['m']=ee.event_date.map(pmonth); ee=ee[ee.m.notna()].sort_values('m')
        # earliest true information entry into pre-FID prospective stock
        ann=ee[ee.event_type.astype(str).str.startswith('ANNOUNCEMENT')]
        entry=ann.m.min() if len(ann) else None
        # master first announcement is used only if explicit and earlier
        mm=master[master.project_id.astype(str).eq(pid)]
        if len(mm):
            ma=pmonth(mm.first_announcement_date.iloc[0])
            if ma is not None and (entry is None or ma<entry): entry=ma
        commitset=ee[ee.event_state_after.astype(str).isin(['FID','COMMITTED'])]
        commit=commitset.m.min() if len(commitset) else None
        cancset=ee[ee.event_state_after.astype(str).eq('CANCELLED')]
        cancel=cancset.m.min() if len(cancset) else None
        opset=ee[ee.event_state_after.astype(str).eq('OPERATING')]
        startup=opset.m.min() if len(opset) else None
        # fall back to source-locked master startup only when it has month/day precision;
        # year-only startup is too coarse for a news month and is not imposed.
        if startup is None and len(mm):
            su=str(mm.startup_date.iloc[0])
            if re.match(r'^\d{4}-\d{2}',su): startup=pmonth(su)
        A=C=0.0
        for m in months:
            dA=dC=0.0
            if entry is not None and m==entry and (commit is None or entry<=commit):
                dA += q; A += q
            if commit is not None and m==commit:
                if A>0: dA -= A; A=0.0
                dC += q; C += q
            if cancel is not None and m==cancel:
                if A>0: dA -= A; A=0.0
                if C>0: dC -= C; C=0.0
            if startup is not None and m==startup and C>0:
                dC -= C; C=0.0
            if abs(dA)>TOL or abs(dC)>TOL:
                out.append((pid,ch,str(m),sponsor.get(pid,''),q,dA,dC))
        audit.append((pid,ch,q,sponsor.get(pid,''),str(entry) if entry else '',str(commit) if commit else '',str(cancel) if cancel else '',str(startup) if startup else ''))
    flows=pd.DataFrame(out,columns=['project_id','chain','month','sponsor','capacity_ktpa','A_news_ktpa','C_news_ktpa'])
    audit=pd.DataFrame(audit,columns=['project_id','chain','capacity_ktpa','sponsor','entry_month','commit_month','cancel_month','startup_month'])

    # The commitment-event census contains a small number of recurrent commitment events not
    # present in the physical-project state ledger. A source-locked >=50 kt/y
    # commitment must still enter the domestic committed-rival news universe. We add
    # only event-ready primary rows whose project-chain key is absent from the candidate
    # chain map; no announcement/startup month is invented.
    census=pd.read_csv(D/'us_incumbent_commitment_events.csv')
    cmap_keys=set((str(a), CHAIN_MAP.get(str(b),str(b))) for a,b in zip(cmap.project_id,cmap.chain))
    supplements=[]
    for rr in census.itertuples(index=False):
        ch=CHAIN_MAP.get(str(rr.chain),str(rr.chain)); key=(str(rr.project_id),ch)
        cm=pmonth(rr.commitment_date)
        if key not in cmap_keys and int(rr.event_ready_primary)==1 and int(rr.eligible_50kt)==1 and cm is not None and pd.notna(rr.capacity_ktpa):
            supplements.append({'project_id':str(rr.project_id),'chain':ch,'month':str(cm),'sponsor':str(rr.sponsor),
                                'capacity_ktpa':float(rr.capacity_ktpa),'A_news_ktpa':0.0,'C_news_ktpa':float(rr.capacity_ktpa)})
            audit.loc[len(audit)] = [str(rr.project_id),ch,float(rr.capacity_ktpa),str(rr.sponsor),'',str(cm),'','']
    if supplements:
        flows=pd.concat([flows,pd.DataFrame(supplements)],ignore_index=True)
    lacc=flows.project_id.eq('US_ETH_LACC_LAKECHARLES')&(flows.month<'2016-08')
    flows.loc[lacc,'sponsor']='Lotte Chemical / Axiall'   # Westlake ownership only from 2016-08
    # explode into focal firms and remove own project using conservative tokens
    den=pd.read_csv(D/'world_capacity_2010.csv').set_index('chain').world_capacity_2010_ktpa.to_dict()
    rows=[]
    for mr in ms.itertuples(index=False):
        firm=str(mr.firm_2010); ch=str(mr.chain)
        tok=[norm(t) for t in OWN_TOKENS.get(firm,[]) if norm(t)]
        g=flows[flows.chain.eq(ch)].copy()
        if len(g):
            sn=g.sponsor.map(norm)
            own=np.zeros(len(g),dtype=bool)
            for t in tok: own |= sn.str.contains(t,regex=False).to_numpy()
            g=g.loc[~own]
        agg=g.groupby('month',as_index=False)[['A_news_ktpa','C_news_ktpa']].sum() if len(g) else pd.DataFrame(columns=['month','A_news_ktpa','C_news_ktpa'])
        z=pd.DataFrame({'period':pd.period_range(START,END,freq='M')}); z['month']=z.period.astype(str)
        z=z.merge(agg,on='month',how='left').fillna({'A_news_ktpa':0.0,'C_news_ktpa':0.0})
        world=float(den[DENOM_SOURCE[ch]])
        z['A_news_norm']=z.A_news_ktpa/world; z['C_news_norm']=z.C_news_ktpa/world
        z['A_12']=z.A_news_norm.shift(1).rolling(12,min_periods=12).sum()
        z['C_12']=z.C_news_norm.shift(1).rolling(12,min_periods=12).sum()
        z['firm_2010']=firm; z['chain']=ch
        rows.append(z[['firm_2010','chain','month','A_news_ktpa','C_news_ktpa','A_news_norm','C_news_norm','A_12','C_12']])
    return flows,audit,pd.concat(rows,ignore_index=True)

def build_outcomes(panel):
    census=pd.read_csv(D/'us_incumbent_commitment_events.csv')
    census['chain']=census.chain.map(CHAIN_MAP).fillna(census.chain)
    census['firm_2010']=[EVENT_OWNER.get((c,s),None) for c,s in zip(census.chain,census.sponsor.astype(str))]
    census['event_month']=census.commitment_date.map(lambda x:str(pmonth(x)) if pmonth(x) else '')
    census['mapped_to_2010_incumbent']=census.firm_2010.notna().astype(int)
    census['primary_event_used']=((census.event_ready_primary==1)&(census.eligible_50kt==1)&census.firm_2010.notna()&census.event_month.ne('')).astype(int)
    # Verify mapped owners exist in the market-share table.
    keys=set(zip(panel.firm_2010,panel.chain))
    bad=census[census.primary_event_used.eq(1)&~census.apply(lambda r:(r.firm_2010,r.chain) in keys,axis=1)]
    if len(bad): raise RuntimeError('mapped outcome owner not in panel')
    panel=panel.copy(); panel['commitment_event_50']=0
    used=census[census.primary_event_used.eq(1)]
    evkeys=set((r.firm_2010,r.chain,r.event_month) for r in used.itertuples())
    panel['commitment_event_50']=[1 if (f,c,m) in evkeys else 0 for f,c,m in zip(panel.firm_2010,panel.chain,panel.month)]
    # Multiple same-month projects for one firm-chain remain one binary commitment event.
    return panel,census

def support_metrics(df, resid, spec):
    regs=['X_F','X_A','X_C','X_sigma']
    z=pd.concat([df.reset_index(drop=True),resid.reset_index(drop=True)],axis=1)
    metrics=[]
    raw_var={c:float(np.var(z[c],ddof=0)) for c in regs}
    basehaz=float(z.commitment_event_50.mean())
    for c in regs:
        rc='r_'+c; rv=float(np.var(z[rc],ddof=0)); surv=(rv/raw_var[c] if raw_var[c]>0 else 0.0)
        nz=np.abs(z[rc].to_numpy())>1e-10
        # effective chains using residual sum-of-squares contributions
        ss=z.assign(_sq=z[rc]**2).groupby('chain')._sq.sum(); shares=ss/ss.sum() if ss.sum()>0 else ss
        eff=float(1/(shares.pow(2).sum())) if shares.pow(2).sum()>0 else 0.0
        # approximate independence-reference MDE for a one raw-SD shock in X
        sx=float(np.std(z[c],ddof=0)); ssx=float(np.sum(z[rc]**2))
        se_beta=np.sqrt(basehaz*(1-basehaz)/ssx) if ssx>0 and basehaz>0 else np.inf
        mde_1sd=float(2.80*se_beta*sx) if np.isfinite(se_beta) else np.inf
        metrics.append({'spec':spec,'regressor':c,'raw_variance':raw_var[c],'residual_variance':rv,'variance_survival_share':surv,
                        'nonzero_residual_observations':int(nz.sum()),'contributing_events':int(z.loc[nz,'commitment_event_50'].sum()),
                        'effective_chains':eff,'approx_mde_hazard_for_1sd_raw_shock':mde_1sd})
    m=pd.DataFrame(metrics)
    corr=z[['r_X_F','r_X_A','r_X_C','r_X_sigma']].corr()
    corr_long=corr.stack().reset_index(); corr_long.columns=['regressor_1','regressor_2','correlation']; corr_long['spec']=spec
    primary=corr.loc[['r_X_F','r_X_A','r_X_C'],['r_X_F','r_X_A','r_X_C']].copy()
    vals=[]
    for i in range(3):
        for j in range(i+1,3): vals.append(abs(float(primary.iloc[i,j])))
    maxcorr=max(vals) if vals else 0.0
    p=m[m.regressor.isin(['X_F','X_A','X_C'])]
    checks={
      'variance_survival':bool((p.variance_survival_share>=THRESH['min_variance_survival']).all()),
      'nonzero_observations':bool((p.nonzero_residual_observations>=THRESH['min_nonzero_observations']).all()),
      'contributing_events':bool((p.contributing_events>=THRESH['min_contributing_events']).all()),
      'effective_chains':bool((p.effective_chains>=THRESH['min_effective_chains']).all()),
      'pairwise_correlation':bool(maxcorr<=THRESH['max_abs_pairwise_corr']),
    }
    return m,corr_long,checks,maxcorr

def main():
    ms=pd.read_csv(D/'us_2010_market_shares.csv')
    # residual pseudo-firm cannot be an identifiable incumbent unit
    ms=ms[~ms.firm_2010.astype(str).str.contains('residual',case=False,na=False)].copy()
    ms['chain']=ms.chain.map(CHAIN_MAP).fillna(ms.chain)
    foreign_pm,foreign=build_foreign()
    domestic_flows,dom_audit,dom_panel=build_domestic(ms)
    # complete firm-chain-month panel
    months=pd.DataFrame({'month':pd.period_range(START,END,freq='M').astype(str)})
    base=ms[['firm_2010','chain','market_share_m_fp0']].drop_duplicates().merge(months,how='cross')
    base=base.merge(foreign[['chain','month','F_news_tpa','F_news_norm','F_12','sigma24_lag1']],on=['chain','month'],how='left',validate='many_to_one')
    base=base.merge(dom_panel[['firm_2010','chain','month','A_news_ktpa','C_news_ktpa','A_12','C_12']],on=['firm_2010','chain','month'],how='left',validate='one_to_one')
    for c in ['A_news_ktpa','C_news_ktpa']: base[c]=base[c].fillna(0.0)
    base['lag_window_complete']=base[['F_12','A_12','C_12','sigma24_lag1']].notna().all(axis=1).astype(int)
    m=base.market_share_m_fp0.astype(float)
    base['X_F']=m*base.F_12; base['X_A']=m*base.A_12; base['X_C']=m*base.C_12; base['X_sigma']=m*base.sigma24_lag1
    base,census=build_outcomes(base)
    base['firm_chain']=base.firm_2010.astype(str)+'||'+base.chain.astype(str)
    base['firm_month']=base.firm_2010.astype(str)+'||'+base.month.astype(str)
    base['chain_month']=base.chain.astype(str)+'||'+base.month.astype(str)
    base['year']=base.month.str[:4]; base['firm_year']=base.firm_2010.astype(str)+'||'+base.year
    # unresolved commitment-event status is excluded, not coded as zero
    MASK=[('LyondellBasell','ethylene','2011-01','2013-12'),('ExxonMobil','polyethylene','2012-06','2014-12'),
          ('Formosa Plastics USA','PVC_VCM','2024-07','2024-07')]
    base['census_masked']=0
    for f_,c_,a_,b_ in MASK:
        sel=base.firm_2010.eq(f_)&base.chain.eq(c_)&base.month.between(a_,b_)
        assert sel.any(), (f_,c_); base.loc[sel,'census_masked']=1
    sample=base[base.lag_window_complete.eq(1)&base.census_masked.eq(0)].copy().reset_index(drop=True)
    regs=['X_F','X_A','X_C','X_sigma']
    pref=demean_multi(sample,regs,[['firm_chain'],['chain_month'],['firm_month']])
    pm,pc,pcheck,pmax=support_metrics(sample,pref,'preferred_firmxmonth')
    fall=demean_multi(sample,regs,[['firm_chain'],['chain_month'],['firm_year']])
    fm,fc,fcheck,fmax=support_metrics(sample,fall,'fallback_firmxyear')
    pref_pass=all(pcheck.values()); fall_pass=all(fcheck.values())
    chosen='preferred_firmxmonth' if pref_pass else ('fallback_firmxyear' if fall_pass else 'STOP')
    support_pass=pref_pass or fall_pass
    # concentration of treatment residual variance by chain for both specs
    conc=[]
    for spec,res in [('preferred_firmxmonth',pref),('fallback_firmxyear',fall)]:
      zz=pd.concat([sample[['chain']],res],axis=1)
      for c in regs:
        ss=zz.assign(_sq=zz['r_'+c]**2).groupby('chain')._sq.sum(); tot=ss.sum()
        for ch,val in ss.items(): conc.append({'spec':spec,'regressor':c,'chain':ch,'residual_ss':val,'variance_contribution_share':val/tot if tot else 0})
    conc=pd.DataFrame(conc)
    # firm/chain support counts and event coverage
    event_used=census[census.primary_event_used.eq(1)]
    summary={
      'authors':CONFIG['authors'],'scope':'F/A/C news construction and fixed-effect support diagnostic only','outcome_model_estimated':False,
      'masked_rows':int(base.census_masked.sum()),
      'thresholds_fixed_before_support_computation':THRESH,
      'panel_rows_all_2010_2025':int(len(base)),'support_sample_rows_full_12m_lag':int(len(sample)),
      'support_sample_start_month':str(sample.month.min()),'support_sample_end_month':str(sample.month.max()),
      'incumbent_firms':int(sample.firm_2010.nunique()),'firm_chain_units':int(sample.firm_chain.nunique()),'chains':int(sample.chain.nunique()),
      'qualifying_binary_commitment_events':int(sample.commitment_event_50.sum()),
      'source_locked_event_rows_mapped_to_primary_incumbents':int(event_used.shape[0]),
      'unconditional_monthly_incumbent_commitment_hazard':float(sample.commitment_event_50.mean()),
      'preferred_checks':pcheck,'preferred_pass':pref_pass,'preferred_max_abs_primary_corr':pmax,
      'fallback_checks':fcheck,'fallback_pass':fall_pass,'fallback_max_abs_primary_corr':fmax,
      'selected_specification':chosen,'support_gate_pass':support_pass,
      'decision':'PROCEED_TO_ESTIMATION' if support_pass else 'NOT_ESTIMATED_INSUFFICIENT_SUPPORT'
    }
    # write outputs
    foreign_pm.to_csv(R/'foreign_project_month_expected_capacity.csv',index=False)
    foreign.to_csv(R/'foreign_chain_month_news.csv',index=False)
    domestic_flows.to_csv(R/'us_project_chain_news_events.csv',index=False)
    dom_audit.to_csv(R/'us_project_chain_state_audit.csv',index=False)
    dom_panel.to_csv(R/'us_focal_rival_news.csv',index=False)
    census.to_csv(R/'incumbent_event_mapping.csv',index=False)
    base.to_csv(R/'firm_chain_month_panel.csv',index=False)
    pd.concat([pm,fm],ignore_index=True).to_csv(R/'fe_support_metrics.csv',index=False)
    pd.concat([pc,fc],ignore_index=True).to_csv(R/'fe_residual_correlations.csv',index=False)
    conc.to_csv(R/'treatment_concentration_by_chain.csv',index=False)
    (R/'support_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # compact pass/fail table
    rows=[]
    for spec,checks in [('preferred_firmxmonth',pcheck),('fallback_firmxyear',fcheck)]:
      for k,v in checks.items(): rows.append({'spec':spec,'check':k,'status':'PASS' if v else 'FAIL'})
    pd.DataFrame(rows).to_csv(R/'fe_support_checks.csv',index=False)
    print(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__': main()
