const { P, H, B, N, Q, T, doc, save } = require('./lib.js');
const c = [];
const add = (...x) => c.push(...x);

add(H('Revision R2 — description of new data files', 1),
  P('This document describes every data file created or downloaded for revision R2, how it was constructed, and how do_10.6.do uses it. All files are in the folder revision_R2/data/ (repository hoanglong-nguyen/patent-instruments, branch claude/wizardly-babbage-73c5ft). Copy the CSV files into the folder set as $raw_data in do_10.6.do. Country codes are ISO 3166-1 alpha-2 (country_2d) and alpha-3 (country_3d); Namibia\'s alpha-2 code "NA" is text, not a missing value.'),
  T([['File', 'Content', 'Used in do_10.6.do'],
     ['wipo_shiftshare_instrument.csv', 'Shift-share instrument for patenting, 43 countries × 2000–2023', 'Block [R2-4] Shift-share instrument; Sections R2.1 and R2.8'],
     ['wipo_shiftshare_shares.csv', 'The 1990–1999 shares behind the instrument (one row per origin × source country)', 'Not read; documentation of the instrument'],
     ['wipo_patent_by_origin.csv', 'Annual patent applications by applicant origin: filed abroad and total, 43 countries × 2000–2023', 'Not read; cross-check of patent_raw.xlsx'],
     ['imf_ctot.csv', 'IMF commodity price indices (export, net export), 180 economies × 1980–2023', 'Block [cepi], only if clear.dta lacks cepi'],
     ['analysis_replica.csv', 'Python replication of analysis.dta (43 countries, 2000–2023)', 'Not read; used for the numbers in the revision guidance'],
     ['analysis_3yr_replica.csv', 'Non-overlapping 3-year averages of the replication panel', 'Not read; Section R2.8 rebuilds it in Stata']],
    [2700, 3800, 2860]));

add(H('1. Source data', 2),
  B('**WIPO office × origin table** (wipo_patent_office_origin.csv, supplied by the researcher): WIPO IP Statistics Data Center, indicator 1 "Total patent applications (direct and PCT national phase entries)", by filing office and applicant origin, 1980–2023, data updated May 2026. Blank cells mean that the office did not report the count (or reported zero) for that year. Origin names were mapped to ISO codes with pycountry plus a manual table for WIPO names (e.g. "Republic of Korea" → KR, "Zaire" → CD); historical entities keep their own codes (Soviet Union SU, Czechoslovakia CS, German Democratic Republic DD, Yugoslavia YU). Rows with origin "Unknown" (7.6 percent of all applications, mostly at the US, Canadian and Japanese offices) are dropped.'),
  B('**IMF Commodity Terms of Trade database** (dataflow IMF.RES:CTOT, version 5.0.1, updated 15 June 2026), downloaded on 11 October 2026 through the IMF SDMX 2.1 API. Query: https://api.imf.org/external/sdmx/2.1/data/IMF.RES,CTOT,5.0.1/.CEPI_CTOTX_GDP+CEPI_CTOTX_TX+CEMPI_CTOTXM_GDP.H_FW_IX+H_RW_IX.A (header Accept: application/vnd.sdmx.data+csv). Reference: Gruss and Kebhaj (2019); suggested citation: International Monetary Fund, Commodity Terms of Trade (CTOT), https://data.imf.org/en/datasets/IMF.RES:CTOT.'),
  B('**Researcher\'s files** (wdi.dta, pwt.dta, income.dta, gfn.dta) for the replication panel only.'));

add(H('2. wipo_shiftshare_instrument.csv — construction', 2),
  P('The instrument predicts how much foreign patenting enters each country\'s patent offices, using pre-sample (1990–1999) exposure shares and later foreign patenting trends that the country does not determine. It follows the shift-share logic (Goldsmith-Pinkham et al., 2020; Borusyak et al., 2022).'),
  N('**Offices acting for a country.** For each country c: its national office plus every regional office of which c is currently a member: OAPI (OA), ARIPO (AP), Eurasian Patent Organization (EA), GCC Patent Office (GC) and the European Patent Office (EP). Membership is current, not historical.'),
  N('**Filings abroad.** A_c,t = applications by applicants from c at all offices not acting for c, in year t. This follows WIPO\'s resident/abroad distinction.'),
  N('**Shares (1990–1999).** For origin o and source country d ≠ o: s_od = F_od / Σ_{t=1990..1999} A_d,t, where F_od is the number of 1990–1999 applications by applicants from d at offices acting for o, counting only filings that are abroad for d. A filing by one member state at a shared regional office is resident for that member and is excluded.'),
  N('**Leave-out shift.** A^(−o)_d,t = A_d,t minus d\'s applications at offices acting for o in year t, so that the country\'s own market does not enter its shift.'),
  N('**Instrument.** Z_o,t = Σ_d s_od × A^(−o)_d,t−ℓ for ℓ = 1 (z_lag1), ℓ = 5 (z_lag5) and the mean over ℓ = 1, …, 10 (z_mean_lag1_10, used in the revision). do_10.6.do uses lnz = ln(1 + z_mean_lag1_10) and lnz_inc = lnz × INC.'),
  P('Variables:'),
  T([['Variable', 'Definition'],
     ['country_2d, country_3d, year', 'Country codes; year 2000–2023'],
     ['z_lag1, z_lag5', 'Instrument with a 1-year or 5-year lag of the shift'],
     ['z_mean_lag1_10', 'Instrument, mean over lags 1–10 (main version)'],
     ['inflow_90_99', 'Total 1990–1999 foreign filings into the country\'s offices (base of the shares)'],
     ['n_source_countries', 'Number of source countries with a positive share'],
     ['office_years_reported_90_99', 'Number of years 1990–1999 in which at least one office acting for the country reported data'],
     ['regional_office', 'Regional offices counted as acting for the country']],
    [3000, 6360]),
  P('Known limits (disclose in Appendix D1):'),
  B('No instrument (empty) for DR Congo, Cambodia and the Philippines: their offices reported no foreign filings by origin in 1990–1999.'),
  B('The ten OAPI members in the sample share one office and therefore have identical shares; the ARIPO members largely share one office as well. Their instruments are close to identical.'),
  B('Thin share bases (fewer than 100 foreign filings in 1990–1999): Madagascar, Nepal, Ethiopia, Mauritius, Mongolia and Iraq.'),
  B('The EPO breakdown by origin starts in 1991, so 1990 European filings at the EPO are missing from the 1990 shift.'),
  B('In the manuscript\'s sample the instrument is weak for the total patent stock (Appendix D1 of the guidance), which is why the revision treats patent coefficients as conditional associations.'));

add(H('3. wipo_shiftshare_shares.csv', 2),
  T([['Variable', 'Definition'],
     ['origin', 'Country whose instrument is built (ISO alpha-2)'],
     ['dest', 'Source country of the foreign filings (ISO alpha-2; historical codes SU, CS, DD, YU possible)'],
     ['inflow_90_99', 'F_od: 1990–1999 filings by applicants from dest at offices acting for origin'],
     ['dest_abroad_90_99', 'Σ A_dest,t over 1990–1999: all filings abroad by applicants from dest'],
     ['share', 's_od = inflow_90_99 / dest_abroad_90_99']],
    [3000, 6360]));

add(H('4. wipo_patent_by_origin.csv', 2),
  T([['Variable', 'Definition'],
     ['pat_abroad', 'Applications filed by applicants from the country at offices not acting for it (A_c,t)'],
     ['pat_total_wipo', 'Applications by applicants from the country at all reporting offices; equals the WIPO "Total" by origin and the do-file\'s pat_total (filled with filings abroad when the home office did not report)'],
     ['home_office_reported', '1 if at least one office acting for the country reported data in that year']],
    [3000, 6360]),
  P('Use: cross-check of patent_raw.xlsx. In the replication the perpetual-inventory stock built from pat_total_wipo reproduces Table 3 (mean of lnPAT 2.179 vs 2.168; same maximum 10.338).'));

add(H('5. imf_ctot.csv', 2),
  T([['Variable', 'IMF code', 'Definition (index, 2012 = 100)'],
     ['cepi_gdp_fw', 'CEPI_CTOTX_GDP, H_FW_IX', 'Commodity export price index; commodities weighted by exports/GDP; fixed weights (average trade flows over several decades)'],
     ['cepi_gdp_rw', 'CEPI_CTOTX_GDP, H_RW_IX', 'Same, rolling weights (average of the preceding three years)'],
     ['cepi_tx_fw / cepi_tx_rw', 'CEPI_CTOTX_TX', 'Commodity export price index; weights = exports / total commodity exports'],
     ['ctot_gdp_fw / ctot_gdp_rw', 'CEMPI_CTOTXM_GDP', 'Commodity net export price index (commodity terms of trade); weights = net exports / GDP']],
    [2200, 2500, 4660]),
  P('Coverage: 180 economies, 1980–2023 in this file (the source runs 1962–2025). Of the 102 Asian and African economies, 97 are covered; North Korea, Macao, Somalia, South Sudan and Uzbekistan are missing. Common deflators (for example the MUV index) are absorbed by year fixed effects. do_10.6.do sets cepi = cepi_gdp_fw by default; change it if the series used for comments 1–3 differs.'));

add(H('6. Replication panels and scripts', 2),
  B('**analysis_replica.csv** — built by revision_R2/build_analysis.py with the same rules as do_10.5.do: WDI (gdp, cap, urb), PWT 11.0 (hci, pop), World Bank income classes, GFN (ef, bio), the WIPO patent series with the perpetual inventory (δ = 0.15; S_1980 = P_1980/(g0 + δ), g0 = 1980–1985 growth, 5 percent fallback), countries with any missing value dropped, Cyprus and Turkey treated as Europe (as in iso.dta). Result: 43 countries (17 Asian, 26 African), 1,032 observations; lnGDP, lnEF and lnBIO match Table 3 exactly. Extra columns: patstock_abr and lnpat_abr (stock of filings abroad).'),
  B('**analysis_3yr_replica.csv** — non-overlapping 3-year averages (2000–02, …, 2021–23; the year column holds the first year of the period). Levels are averaged and then logged; INC stays fixed at 2000; z_mean_lag1_10 is averaged.'),
  B('**Data check:** the WDI extract has gross capital formation = 0 for Ethiopia in 2000–2010 (see guidance, Part E1).'),
  B('**Scripts** (repository root unless stated): wipo_shift_share.py (instrument, shares, patents by origin), fetch_ctot.py (IMF API download), revision_R2/build_analysis.py (replication panel), revision_R2/r2_analyses.py (all revision analyses; results in revision_R2/results/*.csv).'));

add(H('References', 2),
  B('Borusyak K, Hull P and Jaravel X (2022) Quasi-experimental shift-share research designs. Review of Economic Studies 89(1): 181–213.'),
  B('Goldsmith-Pinkham P, Sorkin I and Swift H (2020) Bartik instruments: What, when, why, and how. American Economic Review 110(8): 2586–2624.'),
  B('Gruss B and Kebhaj S (2019) Commodity terms of trade: A new database. IMF Working Paper 19/21.'),
  B('World Intellectual Property Organization (2026) WIPO IP Statistics Data Center. Geneva: WIPO.'),
  P('^^Reference details were written from memory; automatic verification was unavailable in this session. Check them before citing.^^'));

save(doc(c, 'R2 data description'), 'R2_data_description.docx').then(() => console.log('saved'));
