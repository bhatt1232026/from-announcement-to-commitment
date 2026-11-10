# Analysis plan

Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh

This folder archives the analysis plan described in Section 3.3 and Supporting Information, Appendix S2.
The files are kept byte-for-byte as they were fixed, so their SHA-256 hashes can be checked
(`sha256sum -c SHA256SUMS.txt`).

| File | Content | Fixed (UTC) |
|---|---|---|
| `analysis_plan_fixed_2026-10-19T0158Z.md` | Plan fixed before the completeness search, the regulatory collection and the completion of Chinese dates | 2026-10-19 01:58 |
| `analysis_plan_regulatory_design_2026-10-19T0255Z.md` | Plan with the regulatory-visibility design appended, before any regulatory filing was collected | 2026-10-19 02:55 |
| `analysis_plan_final.md` | Final document including the logged amendments A1 to A13 | final |

Each of the two earlier files is a byte-exact prefix of `analysis_plan_final.md`, so no text fixed
earlier was changed afterwards; later material was only appended.

## File names used in the plan and in this repository

The plan was written against the working layout of the project. The corresponding files in this
repository are:

| Name in the plan | File in this repository |
|---|---|
| V14 master / base register | `data/inputs/us_project_register.csv` |
| `data/v37/gate1_query_log.csv` | `data/derived/completeness_search_query_log.csv` |
| `data/v37/gate1_outside_query_candidates.csv` | `data/derived/outside_query_candidates.csv` |
| Gate 1 admitted projects | `data/derived/completeness_search_admitted.csv` |
| Regulatory visibility records | `data/inputs/us_regulatory_filings.csv` |
| 2010 share tables (V34) | `data/inputs/us_2010_market_shares.csv` |
| Gate 3 (incumbent panel support) | `src/09_incumbent_panel_support.py`, `results/incumbent_panel/` |
| `results/v37/V37_PROTOCOL_SHA256.txt` | `docs/analysis_plan/SHA256SUMS.txt` |
| `docs/frozen/` | `docs/analysis_plan/` |

Projects admitted by the completeness search carry identifiers beginning `US_CS_`.
