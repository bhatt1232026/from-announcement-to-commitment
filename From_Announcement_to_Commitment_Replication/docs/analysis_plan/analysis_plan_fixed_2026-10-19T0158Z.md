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
