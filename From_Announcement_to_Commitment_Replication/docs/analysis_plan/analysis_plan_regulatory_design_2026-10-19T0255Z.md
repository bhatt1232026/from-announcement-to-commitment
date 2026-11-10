# V37 Analysis Protocol — Credibility of Announced Capacity by Sponsor Status

Frozen: 2026-10-19, before the Gate 1 completeness search, before any regulatory-date collection,
and before completion of Chinese commissioning dates. SHA-256 of this file is recorded in
`results/v37/V37_PROTOCOL_SHA256.txt` at freeze time. Any later change is an amendment and must be
logged in Section 11 with date and reason.

## 1. Disclosure of what has already been seen

1. The incumbent firm×chain×month design (V31–V35) failed its support gate. It stays frozen; no
   causal coefficient will be estimated from it.
2. On 2026-10-19 an exploratory descriptive run on the V36 U.S. project universe (71 projects) found:
   (a) no reliable incumbent–entrant difference in announcement-to-commitment lag (6 dated entrant
   commitments; p = 0.4–0.7); (b) a large difference in the share of announced projects that reach
   commitment (incumbents 44/45, entrants 10/23). Result (b) is therefore an EXPLORATORY finding.
   Re-estimating it on the same 71 projects is not confirmation.
3. A crude Chinese cut by ownership (central SOE/major vs private) was also seen (realized 50% vs 76%,
   p = 0.11), using a ledger whose commissioning dates are known to be incomplete.
4. The analyst performing the Gate 1 search has seen these results. The search is therefore not blind.
   Mitigation: the query set, inclusion rules and coding rules below are fixed in advance, applied
   symmetrically to incumbents and entrants, and every query and hit is logged.

## 2. Research question

Do capacity announcements by established incumbents and by chain entrants differ in how often, and
how quickly, they turn into binding investment commitments? Secondary: do they differ in how long
capacity is publicly visible before commitment?

## 3. Unit and universe

A U.S. capacity project of at least 50 kt/y in one of seven chains (ethylene, polyethylene,
polypropylene, propylene/PGP incl. PDH and metathesis, EO/MEG, methanol, PVC/VCM), whose first
capacity-specific public information falls in 2010-01..2025-12. Integrated complexes are one project
(classified on the primary chain of the V14 master); derivative chains are not separate projects here.

## 4. Classifications (fixed before outcomes are re-examined)

**Sponsor status.** Incumbent if the sponsor, or any JV partner with ≥25% equity, held U.S. capacity in
the same chain in the frozen 2010 share tables (V34). Ownership is evaluated at the first public date,
never at a later date. Affiliates of a 2010 incumbent group that are separate legal entities are coded
"incumbent_affiliate" and treated as ambiguous. Ambiguous cases are analysed both ways.

**Site type.** Brownfield if the project is at a site where the sponsor (or JV partner) already
operated a plant at the first public date, or reuses/relocates existing equipment (restart,
relocation, debottleneck, expansion). Greenfield otherwise. Coded from project descriptions and
source notes; disagreements with the V14 `project_type` text are logged.

**Outcome at 2025-12.**
- committed: a source-locked commitment (Tier 1–2 FID or equivalent) OR verified construction /
  operation implying commitment (date may be unknown);
- cancelled/abandoned: source-locked cancellation, abandonment, permit withdrawal/rescission,
  or partner withdrawal that ended the project;
- pending: neither (right-censored).
Post-FID pauses are not cancellations.

## 5. Gate 1 — universe completeness search (confirmatory input)

Purpose: test whether incumbents' announced-then-abandoned projects are missing from V14.

Query set (all run; all logged in `data/v37/gate1_query_log.csv`):
- Per chain c ∈ {ethylene cracker, polyethylene plant, polypropylene plant, propane dehydrogenation /
  propylene plant, ethylene oxide / glycol plant, methanol plant, PVC / vinyl chloride plant}:
  "{c} project cancelled United States", "{c} project shelved Texas OR Louisiana",
  "{c} plans scrapped Gulf Coast", "{c} final investment decision delayed".
- Per 2010 incumbent group (Dow, ExxonMobil, Chevron Phillips, LyondellBasell, Shell, Westlake,
  Formosa, INEOS, BASF, Total, Sasol, Braskem, Enterprise, Shintech, OxyChem, Huntsman, Eastman,
  Williams, Celanese, Methanex): "{firm} cancels OR shelves OR scraps U.S. plant project".
- Existing V6–V11 unresolved, reconciliation and expansion registers in the repository are re-read.

Inclusion: a hit enters the universe only if it meets Section 3 and a primary or reputable
secondary source states sponsor, U.S. location, chain and capacity ≥50 kt/y (or a capacity that is
clearly ≥50 kt/y). Studies or "evaluations" without a named site and capacity are logged but not
admitted. Each admitted project receives the same outcome coding as Section 4.

## 6. Primary analysis

Sample: universe after Gate 1, ambiguous cases excluded, first public date ≤ 2022-12 (≥36 months of
follow-up).

Primary estimand: difference between entrants and incumbents in the probability that an announced
project reaches commitment by 2025-12.

Primary model: linear probability model
committed = a + b·entrant + c·log(capacity) + d·greenfield + e·1[first public ≥ 2015] + error,
HC1 standard errors. Primary inference: within-chain permutation of the entrant label (10,000
draws; chain composition held fixed), two-sided.

## 7. Pre-specified checks

1. Ambiguous cases as incumbent; as entrant.
2. Excluding methanol.
3. Excluding projects >2,500 kt/y.
4. Greenfield projects only (separates firm status from site type).
5. Leave-one-chain-out (every chain).
6. Including projects first public after 2022-12.
7. Capacity-weighted shares (descriptive only).
8. Secondary: competing-risks cumulative incidence of commitment vs cancellation from first public
   date, on projects with dated outcomes; and announcement-to-commitment lag (secondary, expected to be
   underpowered).

## 8. Numeric criteria for treating the result as established

All of the following must hold:
- R1: primary b ≤ −0.20 (a gap of at least 20 percentage points);
- R2: primary within-chain permutation p < 0.05;
- R3: b < 0 in every check in Section 7 items 1–6, including every leave-one-chain-out run;
- R4: b ≤ −0.20 in the greenfield-only check.
If R1–R4 hold, the U.S. finding is reported as robust descriptive evidence within U.S.
petrochemicals. If any fails, it is reported as exploratory/industry-specific and the headline is
weakened accordingly.

## 9. External cross-market replication (China)

Commissioning status for Chinese projects with open/unresolved outcomes is completed first, from
sources, before any competitive-status comparison is computed.
Competitive status (primary): "established" if the sponsor group operated capacity in the same chain
in China before the project's first public date; "chain newcomer" otherwise. Ownership (central SOE /
local SOE / private / foreign JV) is a secondary moderator. Outcome: realized (commercial
operation by 2025-12) vs not. Replication is "directionally consistent" if newcomers' realization
share is lower than established sponsors'. It is reported regardless of direction.

## 10. Measurement corrections (disclosed data corrections, not redesign)

Census rule violations removed from the incumbent support sample; foreign news F split into
information news, commissioning exits and calibration drift (information news only enters F);
Westlake–Axiall ownership applied only from the acquisition date; Brier comparisons reported with
project-clustered bootstrap intervals and a chain-specific base-rate benchmark. Gate 3 is re-run once
on the corrected inputs and the result is frozen whatever it shows.

## 11. Stopping rule and amendments

After Sections 5–10 are executed once, no further universe, definition or model changes are made in
response to results. The paper is written around whatever Sections 8–9 establish.

Amendments: (none at freeze)

Amendments logged 2026-10-19, after the Gate 1 search and BEFORE any Section 6–8 estimate was run.
They settle data-handling cases the frozen text did not cover; none changes a definition or the model.
- A1 (capacity not disclosed). An admitted project described as world-scale but without a numeric
  capacity takes the median capacity of admitted projects in the same chain that have one; flagged
  `capacity_imputed`. Applies to one project (Shell Geismar MEG).
- A2 (first public date missing). If no first-public date is source-locked, the earliest dated
  commitment, construction or start-up event is used as an upper bound for the date filters
  (≤ 2022-12, ≥ 2015); flagged `first_public_imputed`.
- A3 (site type). A site contiguous with a plant the sponsor or a JV partner already operated counts
  as that sponsor's site (brownfield); a marine terminal alone does not count as a plant.
  Disagreements with the V14 `project_type` text are logged in the classification file.
- A4 (candidates outside the query set). In-scope projects the analyst knows of but which none of the
  Section 5 queries or registers surfaced are listed in `data/v37/gate1_outside_query_candidates.csv`
  and NOT admitted, so that admission stays rule-based. They are reported as a disclosed limitation.
- A5 (JV holdings). A sponsor that held 2010 capacity through a ≥25% equity stake in a 2010 producer
  (Total held 40% of BASF/FINA LP) is an incumbent under Section 4, not an affiliate, so Baystar is
  coded incumbent (the exploratory run had it ambiguous). Holdings that are only indirect at the first
  public date stay ambiguous: MEGlobal was wholly owned by EQUATE in 2016, and Dow held 42.5% of EQUATE.

Amendments logged 2026-10-19 (V37.1) in response to external review, after the V37 results were seen.
They correct reporting and add companion analyses; the frozen primary estimate and criteria are unchanged.
- A6 (Monte Carlo p-values). Permutation p-values are reported as (exceedances + 1)/(B + 1).
- A7 (exchangeability). Two companion randomization tests are added: permutation within chain × site
  type, and Freedman–Lane residual permutation in a chain fixed-effects model (HC1 t statistic).
- A8 (heterogeneous follow-up). Two companion checks are added: commitment within 36 months of first
  public (equal window; undated commitments excluded), and the primary model with months of follow-up.
- A9 (reporting of R4). R4 is reported as an effect-size criterion on 16 projects (3 incumbent), with
  its permutation p-value (≈0.10) shown beside it; the U.S. result is described as "meets the frozen
  criteria, with the greenfield-only criterion underpowered", not as fully established by R4.
- A10 (reproducibility). Chinese dates are parsed explicitly so the pipeline runs on current pandas.

## 12. Regulatory-visibility analysis (frozen 2026-10-19, before any regulatory date was collected)

Purpose: test the alternative explanation that entrant projects look less credible only because they
become public earlier in the regulatory/financing process than incumbent projects.

**Regulatory visibility date (RVD).** The earliest date of a legally public application that necessarily
identifies the sponsor, the site and the capacity project. Qualifying filings, all treated equally
(the earliest one found is the RVD):
1. a state or federal air-permit application for the project (TCEQ NSR/PSD, LDEQ PSD/Title V, EPA GHG
   PSD, other states' construction-permit applications) — the application/received date;
2. a state tax-incentive application for the project (Texas Chapter 313 or JETI; Louisiana ITEP advance
   notification or application; comparable state programmes) — the application date;
3. a federal environmental filing for the project (e.g. Army Corps Section 404 / NEPA notice).
Exclusions: routine renewals or amendments unrelated to the capacity project; filings for a different
project at the same site; filings dated only by approval (approval dates are recorded but are not RVDs
unless the application date is unknown, in which case the record is flagged `approval_only`).
Search rule: for every primary-sample project the same query set is run — "{sponsor} {site} air permit
application {product}", "{sponsor} {site} {product} Chapter 313 OR ITEP OR JETI application", and
"{project name} permit application" — and the earliest qualifying hit is recorded with its URL. If none is
found the RVD is coded missing; missingness is reported by group and never imputed.

**Analyses (all reported whatever they show).**
- RV1 coverage: share of projects with an RVD, by sponsor status.
- RV2 visibility lead: months from first public announcement to RVD, by sponsor status (median;
  Mann–Whitney). A positive lead means the project was announced before it filed.
- RV3 conditional credibility (main test): the primary LPM re-estimated on projects that have an RVD
  dated ≤ 2022-12 (i.e. projects that reached a common regulatory milestone), with within-chain
  permutation p ((B+1) rule).
- RV4 regulatory clock: commitment within 36 months of the RVD (undated commitments excluded).
Interpretation rule, fixed now: if RV3's entrant coefficient is ≤ −0.20 and negative in RV4, the
"earlier visibility" explanation is rejected for projects that reached a regulatory filing; if RV3's
coefficient is above −0.10, the paper reports that the gap is largely explained by regulatory stage at
announcement; values in between are reported as partial attenuation.
