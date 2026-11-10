# From Announcement to Commitment: Market Incumbency and the Credibility of
# U.S. Petrochemical Capacity Plans. Replication code.
# Authors: Vivek Bhatt, Kapil Dwivedi and Amaresh Chandra Singh
"""Structured completeness search (Section 3.1; Table 1; Supporting Information, Appendix S3).

Writes the logged search and its consequences for the project register:
  * completeness_search_query_log.csv       every query, its run date and its relevant hits
  * completeness_search_admitted.csv        the twelve projects admitted to the universe
  * completeness_search_not_admitted.csv    logged candidates that failed the admission rule
  * outside_query_candidates.csv            analyst-recalled candidates not admitted (amendment A4)
  * register_corrections.csv                source-based corrections to base-register projects

Every entry was transcribed from the searches run on 2026-10-19; source URLs are recorded.
Usage: python src/01_completeness_search.py
"""
import csv

from common import DERIVED

RUN_DATE = "2026-10-19"
CHAINS = ["ethylene cracker", "polyethylene plant", "polypropylene plant",
          "propane dehydrogenation / propylene plant", "ethylene oxide / glycol plant",
          "methanol plant", "PVC / vinyl chloride plant"]
TEMPL = ["{c} project cancelled United States", "{c} project shelved Texas OR Louisiana",
         "{c} plans scrapped Gulf Coast", "{c} final investment decision delayed"]
FIRMS = ["Dow", "ExxonMobil", "Chevron Phillips", "LyondellBasell", "Shell", "Westlake", "Formosa",
         "INEOS", "BASF", "Total", "Sasol", "Braskem", "Enterprise", "Shintech", "OxyChem", "Huntsman",
         "Eastman", "Williams", "Celanese", "Methanex"]

# Relevant hits per query (project-level candidates only; plant closures, non-chain projects,
# non-U.S. projects and projects already in the base register are summarised as other hits).
HITS = {
 ("ethylene cracker", 0): ("Motiva Port Arthur cracker; Energy Transfer Nederland", "US_CS_ETH_MOTIVA_PA; US_CS_ETH_ET_NEDERLAND"),
 ("ethylene cracker", 1): ("Enterprise Beaumont/Orange cracker; Indorama Lake Charles restart", "US_CS_ETH_ENTERPRISE_TX; US_CS_ETH_INDORAMA_LC"),
 ("ethylene cracker", 2): ("ExxonMobil Calhoun (Coastal Plain) complex paused 2025-10", "US_CS_PE_EXXON_CALHOUN"),
 ("ethylene cracker", 3): ("PTTGC Ohio (in base register); Lotte/Axiall LACC FID delay (in base register)", ""),
 ("polyethylene plant", 0): ("Braskem ASCENT (in base register; outcome corrected)", "CORR_US_PE_ASCENT_WV"),
 ("polyethylene plant", 1): ("Formosa Sunshine permits (in base register)", ""),
 ("polyethylene plant", 2): ("ExxonMobil Calhoun (duplicate)", ""),
 ("polyethylene plant", 3): ("CPChem/QP USGC II FID delay (in base register); PTTGC Ohio (in base register)", ""),
 ("polypropylene plant", 0): ("closures only (Sunoco Bayport, Braskem idling) - out of scope", ""),
 ("polypropylene plant", 1): ("closures only; Ascend PDH deferral (in base register)", ""),
 ("polypropylene plant", 2): ("ExxonMobil Calhoun (duplicate)", ""),
 ("polypropylene plant", 3): ("BASF Freeport MTP deferral (in base register); Canadian PDH/PP (out of scope)", ""),
 ("propane dehydrogenation / propylene plant", 0): ("no new in-scope candidate beyond the base register (PetroLogistics logged)", ""),
 ("propane dehydrogenation / propylene plant", 1): ("Ascend Chocolate Bayou indefinitely tabled (in base register)", ""),
 ("propane dehydrogenation / propylene plant", 2): ("PetroLogistics Gulf Coast PDH plan (no named site)", "NA_PETROLOGISTICS_PDH2"),
 ("propane dehydrogenation / propylene plant", 3): ("ICIS EPCA 2014 list: Dow Freeport PDH; Dow 2nd PDH option; PetroLogistics withdrawn; Formosa/Enterprise delays (in base register)", "US_CS_PDH_DOW_FREEPORT; NA_DOW_PDH2; NA_PETROLOGISTICS_PDH2"),
 ("ethylene oxide / glycol plant", 0): ("INEOS Oxide EO/EG plant indefinitely suspended 2014", "US_CS_EO_INEOS_LAPORTE"),
 ("ethylene oxide / glycol plant", 1): ("Shell Geismar MEG plan 2019; Nan Ya Point Comfort MEG", "US_CS_MEG_SHELL_GEISMAR; US_CS_MEG_NANYA_PC"),
 ("ethylene oxide / glycol plant", 2): ("INEOS (duplicate); Energy Transfer (duplicate)", ""),
 ("ethylene oxide / glycol plant", 3): ("INEOS site nomination 2011; Nan Ya delay (duplicates)", ""),
 ("methanol plant", 0): ("NWIW Kalama/Tacoma (in base register)", ""),
 ("methanol plant", 1): ("SLM on hold; Methanex G3 pause (in base register)", ""),
 ("methanol plant", 2): ("Nacero Gulf Coast methanol (no named site)", "NA_NACERO"),
 ("methanol plant", 3): ("Lake Charles Methanol II (2024); Syngas St James (in base register)", "US_CS_MEOH_LCM2"),
 ("PVC / vinyl chloride plant", 0): ("Westlake closures 2025 - out of scope", ""),
 ("PVC / vinyl chloride plant", 1): ("closures only", ""),
 ("PVC / vinyl chloride plant", 2): ("closures only", ""),
 ("PVC / vinyl chloride plant", 3): ("Orbia ~1 Mt PVC (site not set); Shintech phase 2 delay (in base register)", "NA_ORBIA_PVC"),
}
FIRM_HITS = {
 "Dow": ("plant closures, Canadian Path2Zero - no in-scope U.S. project", ""),
 "ExxonMobil": ("Calhoun complex (duplicate); Baytown hydrogen (out of scope)", ""),
 "Chevron Phillips": ("paraxylene closure (out of scope)", ""),
 "LyondellBasell": ("refinery/plant closures (out of scope)", ""),
 "Shell": ("GTL abandoned (out of scope); Monaca sale", ""),
 "Westlake": ("closures (out of scope)", ""),
 "Formosa": ("Sunshine permits (in base register); Nan Ya MEG suspension (duplicate)", ""),
 "INEOS": ("INEOS EO/EG La Porte (duplicate)", ""),
 "BASF": ("BASF/Yara ammonia (out of scope); BASF Freeport MTP (in base register)", ""),
 "Total": ("Motiva cessation 2021 (duplicate); Baystar (in base register)", ""),
 "Sasol": ("GTL cancelled (out of scope)", ""),
 "Braskem": ("ASCENT abandoned 2019-07 (outcome correction)", "CORR_US_PE_ASCENT_WV"),
 "Enterprise": ("pipeline/fractionator deferrals (out of scope)", ""),
 "Shintech": ("Plaquemine phase 2 delay (in base register)", ""),
 "OxyChem": ("closures (out of scope)", ""),
 "Huntsman": ("EO idling (out of scope)", ""),
 "Eastman": ("Longview recycling plant (out of scope)", ""),
 "Williams": ("Alberta PDH (non-U.S.)", ""),
 "Celanese": ("second U.S. methanol plant at Bishop, TX", "US_CS_MEOH_CELANESE_BISHOP"),
 "Methanex": ("G3 pause/restart (in base register)", ""),
}
with open(DERIVED / "completeness_search_query_log.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["query_id", "query_family", "query_text", "run_date", "relevant_hits", "candidate_ids"])
    i = 0
    for c in CHAINS:
        for k, t in enumerate(TEMPL):
            i += 1; h = HITS[(c, k)]
            w.writerow([f"Q{i:02d}", "chain", t.format(c=c), RUN_DATE, h[0], h[1]])
    for fm in FIRMS:
        i += 1; h = FIRM_HITS[fm]
        w.writerow([f"Q{i:02d}", "firm", f"{fm} cancels OR shelves OR scraps U.S. plant project", RUN_DATE, h[0], h[1]])
    w.writerow(["R01", "register_reread", "earlier U.S. ethylene reconciliation register", RUN_DATE,
                "US_ETH_DOW_TX9 matched in the reconciliation register but missing from the base register", "US_CS_ETH_DOW_TX9"])
    w.writerow(["R02", "register_reread", "earlier U.S. polyethylene reconciliation register", RUN_DATE,
                "label mismatches only (Gemini, Exxon Beaumont present under other IDs)", ""])
    w.writerow(["R03", "register_reread", "earlier six-chain expansion register", RUN_DATE,
                "Lotte MEG = derivative of integrated LACC complex (counted once); non-chain rows out of scope", ""])
    w.writerow(["R04", "register_reread", "earlier unresolved-project registers", RUN_DATE,
                "all rows already in the base register", ""])

ADD_COLS = ["project_id", "sponsor", "project_name", "site", "chain", "capacity_ktpa", "capacity_note",
            "site_type", "sponsor_status", "sponsor_status_note", "first_public", "first_public_precision",
            "commit_month", "outcome", "outcome_date", "outcome_note", "source_1", "source_2", "found_by"]
ADD = [
 ["US_CS_ETH_DOW_TX9", "Dow", "Freeport LHC-9 ethane cracker", "Freeport, TX", "ethylene", 1500, "EPA application 1.95 Mt; reconciliation register 1500",
  "brownfield", "incumbent", "Dow in 2010 ethylene table", "2012-04", "day", "2012-04", "committed", "2017", "release says Dow 'will construct'; EPC Q1 2013; startup 2017",
  "https://www.biospace.com/the-dow-chemical-company-to-build-new-ethylene-production-plant-at-b-dow-b-texas-operations",
  "https://www.ogj.com/articles/2013/05/dow-lets-contract-for-oyster-creek-complex-expansion--upgrade.html", "R01"],
 ["US_CS_PDH_DOW_FREEPORT", "Dow", "Oyster Creek/Freeport PDH", "Freeport, TX", "propylene_PDH", 750, "ICIS 2014",
  "brownfield", "incumbent", "Dow in 2010 propylene table", "2011-04", "day", "2013-05", "committed", "2015-12", "amendment A13: board funding for engineering Mar 2012 is not an FID; EPC contract let by May 2013 used as commitment; startup Dec 2015",
  "https://www.hydrocarbonprocessing.com/news/2011/04/dow-chemical-to-raise-us-ethylene-propylene-production-inks-shale-gas-supply-deals/",
  "https://www.ogj.com/articles/2013/05/dow-lets-contract-for-oyster-creek-complex-expansion--upgrade.html", "Q16"],
 ["US_CS_ETH_MOTIVA_PA", "Motiva Enterprises", "Port Arthur ethane cracker and derivatives", "Port Arthur, TX", "ethylene", 1900, "",
  "brownfield", "entrant", "Motiva absent from 2010 ethylene table; refinery site counts as sponsor-operated site", "2018-12", "day", "", "cancelled", "2021-07",
  "tax-abatement application withdrawn and plans ceased Jul 2021; air permits cancelled 2024-09-04",
  "https://www.icis.com/explore/resources/news/2021/07/20/10665189/motiva-withdraws-tax-break-application-for-texas-petchem-project/",
  "https://globalenergyinfrastructure.com/news/2021/07-july/motiva-ceases-plans-for-multibillion-dollar-petrochemical-expansion-in-texas", "Q01"],
 ["US_CS_ETH_INDORAMA_LC", "Indorama Ventures", "Lake Charles (Westlake, LA) cracker restart", "Westlake, LA", "ethylene", 370, "",
  "brownfield", "entrant", "Indorama absent from 2010 ethylene table; restart of idled unit", "2015-09", "day", "", "committed", "2017", "acquisition and restart announced 2015-09-24; operating",
  "https://www.indoramaventures.com/en/investor-relations/newsroom/press-releases/137/ivl-to-acquire-us-gas-cracker-transformative-deal-to-provide-early-access-to-shale-gas", "", "Q02"],
 ["US_CS_ETH_ENTERPRISE_TX", "Enterprise Products Partners", "Texas ethane steam cracker", "Beaumont, Jefferson County, TX", "ethylene", 2000, "S&P 2022-06-15",
  "greenfield", "entrant", "Enterprise in 2010 propylene table only; not ethylene", "2022-05", "day", "", "pending", "", "Chapter 313 application 2022-05-05; company said neither approved nor sanctioned (2022-07); no FID found to 2025-12",
  "https://www.spglobal.com/energy/en/news-research/latest-news/chemicals/061522-enterprise-planning-new-2-mil-mtyear-steam-cracker-in-texas-documents",
  "https://www.bicmagazine.com/departments/engineering-construction/enterprise-clarifies-media-reports-ethylene-cracker/", "Q02"],
 ["US_CS_ETH_ET_NEDERLAND", "Energy Transfer", "Nederland petrochemical complex", "Nederland, TX", "ethylene", 2000, "approximate",
  "greenfield", "entrant", "not in 2010 tables", "2023-06", "approx", "", "pending", "2026-05-06", "air-permit application withdrawn 2026-05-06 (after 2025-12 horizon)",
  "https://www.hydrocarbonprocessing.com/news/2026/05/energy-transfer-withdraws-air-permit-application-for-18-b-petrochemical-complex-in-texas/", "", "Q01"],
 ["US_CS_PE_EXXON_CALHOUN", "ExxonMobil", "Coastal Plain Venture, Calhoun County", "Calhoun County, TX", "polyethylene", 3000, "approximate",
  "greenfield", "incumbent", "ExxonMobil in 2010 PE table", "2024-12", "day", "", "pending", "2025-10", "JETI application 2024-12-23; paused Oct 2025 (headline 'scraps', body 'paused')",
  "https://www2.texastribune.org/2025/10/07/texas-exxon-plastics-plant-delayed-calhoun-county-school-taxes",
  "https://www.chemicalprocessing.com/industrynews/news/55322569/exxonmobil-scraps-plans-for-10b-texas-plastics-plant", "Q03"],
 ["US_CS_EO_INEOS_LAPORTE", "INEOS Oxide", "Gulf Coast EO/EG plant (Battleground, La Porte)", "La Porte, TX (shortlist incl. Chocolate Bayou, Plaquemine at first public)", "EO_MEG", 500, ">=500 kt EO stated",
  "brownfield", "entrant", "INEOS absent from 2010 EO table (incumbent in ethylene/PE only)", "2011-12", "day", "", "pending", "2014-10", "indefinitely suspended; the same article reports INEOS wrote to EPA that the project had been discontinued, while a spokesman said it had not been cancelled - coded pending (judgement; cancelled would change only cancellation incidence)",
  "https://www.ineos.com/businesses/ineos-oxide/news/ineos-oxide-nominates-3-sites-on-the-us-gulf-coast/",
  "https://www.plastemart.com/news-plastics-information/ineos-indefinitely-suspends-proposed-ethylene-oxide-ethylene-glycol-plant-at-la-porte/26196", "Q17"],
 ["US_CS_MEG_SHELL_GEISMAR", "Shell Chemical", "Geismar world-scale MEG plant", "Geismar, LA", "EO_MEG", 650, "IMPUTED: not disclosed; median of admitted EO_MEG projects with capacity (INEOS 500, Nan Ya 800) per amendment A1",
  "brownfield", "incumbent", "Shell in 2010 EO table", "2019-01", "day", "", "pending", "", "amendment A13: Ascension Parish Council approved ITEP abatement 2019-01-17 (public record, first public); feasibility stage, FID expected 2020; no FID or cancellation found to 2025-12",
  "https://bizneworleans.com/shell-advances-plans-for-potential-1-2-billion-louisiana-plant/",
  "https://www.areadevelopment.com/newsitems/5-21-2019/shell-chemicals-manufacturing-geismar-louisiana.shtml", "Q18"],
 ["US_CS_MEG_NANYA_PC", "Nan Ya Plastics (Formosa group)", "Point Comfort MEG plant", "Point Comfort, TX", "EO_MEG", 800, "S&P 2020",
  "brownfield", "ambiguous", "incumbent_affiliate: Nan Ya is a separate entity in the Formosa group (Formosa in 2010 EO table)", "2015-01", "day", "", "committed", "2020", "construction suspended Mar 2020, completed 2020-21",
  "https://www.plastemart.com/news-plastics-information/formosa-mulls-new-meg-plant-pe-unit-at-point-comfort-complex-in-texas/26556",
  "https://www.spglobal.com/energy/en/news-research/latest-news/chemicals/051520-nan-yas-texas-meg-plant-startup-pushed-back-to-late-2020-or-early-2021-source", "Q18"],
 ["US_CS_MEOH_CELANESE_BISHOP", "Celanese", "Second U.S. methanol plant, Bishop", "Bishop, TX", "methanol", 1300, "",
  "brownfield", "entrant", "Celanese absent from 2010 methanol table", "2014-03", "day", "", "pending", "", "preliminary engineering complete 2016; never sanctioned",
  "https://www.icis.com/resources/news/2014/03/31/9767812/celanese-considering-another-texas-methanol-facility/",
  "https://icis.com/resources/news/2016/06/07/10005938/celanese-advances-plans-for-2nd-us-methanol-plant", "Q47"],
 ["US_CS_MEOH_LCM2", "Lake Charles Methanol II", "Lake Charles Methanol II", "Lake Charles, LA", "methanol", 3600, "",
  "greenfield", "entrant", "not in 2010 tables", "2024-02", "day", "", "pending", "", "FEED and permitting; FID expected mid-2024 not found",
  "https://www.icis.com/explore/resources/news/2024/02/14/10971673/new-us-methanol-plant-planned-for-us-louisiana",
  "https://opportunitylouisiana.gov/news/lake-charles-methanol-announces-plan-for-new-3-2-billion-manufacturing-plant-in-southwest-louisiana", "Q24"],
]
with open(DERIVED / "completeness_search_admitted.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(ADD_COLS); w.writerows(ADD)

NA = [
 ["NA_DOW_PDH2", "Dow", "second PDH 'option', 2018", "no named site or capacity", "https://www.icis.com/resources/news/2014/10/05/9826545/epca-14-half-of-us-pdh-projects-to-be-delayed-or-shelved-exec/"],
 ["NA_PETROLOGISTICS_PDH2", "PetroLogistics / Flint Hills", "second Gulf Coast PDH", "no named site; withdrawn 2014", "https://ogj.com/refining-processing/petrochemicals/article/14036217/petrologistics-plans-us-gulf-coast-pdh-plant"],
 ["NA_NACERO", "Nacero", "Gulf Coast methanol", "no named site or capacity", "https://www.oaoa.com/?p=283593"],
 ["NA_ORBIA_PVC", "Orbia", "~1 Mt PVC, U.S. Gulf Coast", "final location not set (2022-05)", "https://www.argusmedia.com/en/news-and-insights/latest-market-news/2456734-orbia-aims-to-complete-us-pvc-plant-by-2028"],
 ["NA_LOTTE_MEG", "Lotte Chemical", "Lake Charles MEG", "derivative unit of integrated LACC complex (counted once)", ""],
]
with open(DERIVED / "completeness_search_not_admitted.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["candidate_id", "sponsor", "description", "reason_not_admitted", "source"]); w.writerows(NA)

OUTSIDE = [
 ["OCI Beaumont methanol restart/debottleneck (2011-12)", "methanol", "entrant (OCI absent from 2010 table; acquired plant 2011)", "committed",
  "analyst recall; not surfaced by any query or register", "NOT ADMITTED (amendment A4); unverified"],
 ["Valero St. Charles methanol plant proposal (c. 2012-13)", "methanol", "entrant", "not built",
  "analyst recall; not surfaced by any query or register", "NOT ADMITTED (amendment A4); unverified"],
]
with open(DERIVED / "outside_query_candidates.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["candidate", "chain", "likely_sponsor_status", "likely_outcome", "reason", "status"]); w.writerows(OUTSIDE)

CORR = [
 ["US_PE_ASCENT_WV", "outcome", "pending", "cancelled", "2019-07", "Braskem abandoned cracker/PE plans and is selling the site",
  "https://www.plasticsnews.com/news/braskem-ends-plans-build-cracker-and-pe-resin-units-west-virginia"],
 ["US_ETH_LYB_CORPUS", "first_public", "", "2013-03", "", "ICIS 2013-03-13: LyondellBasell plans 800m lb/yr ethylene expansion at Corpus Christi",
  "https://www.icis.com/resources/news/2013/03/13/9649437/lyondellbasell-plans-800m-lbyear-ethylene-expansion-at-texas/"],
 ["US_ETH_LACC_LAKECHARLES", "first_public", "", "2013-12", "", "Axiall selected Louisiana site for 1 Mt/y cracker 2013-12-19",
  "https://www.bicmagazine.com/projects-expansions/downstream/axiall-to-partner-with-korean-firm-on-louisiana-ethane-cracker/"],
 ["US_ETH_BAYSTAR_PORTARTHUR", "first_public", "2017-03", "2015-04", "", "amendment A13: Total disclosed 1 Mt/y Port Arthur cracker in TCEQ filing reported 2015-04-06",
  "https://www.hydrocarbonprocessing.com/news/2015/04/total-lists-capacity-for-new-texas-ethane-cracker/"],
]
with open(DERIVED / "register_corrections.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["project_id", "field", "original_value", "corrected_value", "date", "note", "source"]); w.writerows(CORR)
print("written", DERIVED)
