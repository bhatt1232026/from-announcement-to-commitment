# Data

Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh

All data were compiled by the authors from publicly available sources: company press releases and
investor disclosures (including SEC filings), trade-press reports, U.S. federal and state regulatory
records (U.S. EPA Region 6 greenhouse-gas permit applications, Texas Comptroller Chapter 313
applications, state air-permit and incentive records in Louisiana, Texas, Pennsylvania and West
Virginia) and, for China, environmental approvals, government notices and listed-company disclosures.
Where a record is supported by a web document, its URL is stored in the `source_url` (or `source_1`,
`source_2`, `source`) column. Information cutoff: December 2025.

## `inputs/` (fixed inputs, read by the analysis scripts)

| File | Rows | Content |
|---|---:|---|
| `us_project_register.csv` | 71 | Base register of U.S. capacity projects (>= 50 kt/y, seven chains): sponsor, site, chain, capacity, announcement, FID, construction and start-up dates, status, source |
| `us_project_events.csv` | 176 | Dated project state transitions (announcement, FID, construction, cancellation, start-up) with source and source type |
| `us_first_public_dates.csv` | 13 | Earliest capacity-specific public disclosure recovered for projects whose register date was missing or later |
| `us_regulatory_filings.csv` | 33 | Regulatory visibility date (RVD) per project: earliest qualifying air-permit, tax-incentive or federal filing, with precision and filing type |
| `us_project_chain_map.csv` | 77 | Project to product-chain map used for rival-capacity news |
| `us_incumbent_commitment_events.csv` | 49 | Census of incumbent commitment (FID or equivalent) events |
| `us_2010_market_shares.csv` | 80 | 2010 U.S. capacity and market share by firm and chain (defines incumbency) |
| `world_capacity_2010.csv` | 7 | 2010 world capacity by chain (normalising denominators) |
| `china_project_register.csv` | 78 | Chinese project register (46 physical projects; chain rows), first public (T1) and commissioning (T2) dates |
| `china_stage_project_month.csv` | 1,955 | Monthly project stage panel (announced, approved, construction, ramp-up) with 12/24/36-month commissioning outcomes |
| `china_pre2010_training_history.csv` | 150 | Pre-2010 stage histories used only to calibrate the rolling-origin model |

## `derived/` (written by the scripts)

| File | Written by | Content |
|---|---|---|
| `completeness_search_query_log.csv` | `01` | All 48 queries and 4 register re-reads, run date and relevant hits |
| `completeness_search_admitted.csv` | `01` | 12 projects admitted to the universe, with coding notes and sources |
| `completeness_search_not_admitted.csv` | `01` | 5 logged candidates that failed the admission rule |
| `outside_query_candidates.csv` | `01` | 2 analyst-recalled candidates not admitted (amendment A4) |
| `register_corrections.csv` | `01` | Source-based corrections to 4 base-register projects |
| `china_outcome_completion.csv` | `06` | End-2025 realization status completed for 17 Chinese projects without a register T2 date |

## Main coding rules

- **Incumbent**: the sponsor, or a joint-venture partner with at least 25% equity, held U.S. capacity in
  the same chain in 2010; evaluated at the first public date. Separate affiliates are coded ambiguous.
- **Site type**: brownfield if the project is at, or contiguous with, a site where the sponsor already
  operated a plant, or reuses existing equipment; greenfield otherwise.
- **Outcome at December 2025**: committed (source-locked FID or equivalent, or verified construction or
  operation), cancelled (source-locked cancellation, abandonment or permit withdrawal) or pending.
- **Primary sample**: ambiguous sponsors excluded; first public date up to December 2022 (76 projects).
