* ================================================================
* do_10.6.do  —  revision R2 (Reviewer 1, second round)
* Based on do_10.5.do. Every change is tagged [R2-#], where # is the
* number of the reviewer's major comment it answers (R2-4 = comment 4).
* Lines without a tag are unchanged from do_10.5.do.
* New inputs (in $raw_data, see R2_data_description.docx):
*   wipo_shiftshare_instrument.csv   shift-share instrument for PAT   [R2-4]
*   imf_ctot.csv                     IMF commodity price indices      [cepi]
* User-written commands used by the new blocks [R2]:
*   ssc install ivreg2, ranktest, ivreghdfe, reghdfe, weakiv, xtscc,
*   ssc install xtdcce2, xthst, boottest, xtcd2, multipurt, outreg2
* ================================================================
clear all
set more off
capture log close                                                  // [R2-17] log opened below; do_10.5 closed a log it never opened

global raw_data   "D:/Ère de FTU (2020 - 2025)/JIEM (2023 - 2024)/cô Thúy Anh/250701_ED_review/raw data"
global clear_data "D:/Ère de FTU (2020 - 2025)/JIEM (2023 - 2024)/cô Thúy Anh/250701_ED_review/5th submission/data"
global results    "D:\Ère de FTU (2020 - 2025)\JIEM (2023 - 2024)\cô Thúy Anh\250701_ED_review\5th submission\results"
log using "$results/do_10.6.log", replace text                    // [R2-17]

* ================================================================
**# DATA PREPARATION (Section 3.3, Table 1)
* ================================================================

* ----------------------------------------------------------------
**## GDP, CAP, URB — World Bank Data Bank
* ----------------------------------------------------------------
clear
import excel "$raw_data/wdi_raw", sheet("Data") firstrow
destring YR2000-YR2023, replace force
drop if missing(CountryCode)
isid SeriesCode CountryCode
reshape long YR, i(CountryCode SeriesCode) j(Year)

replace SeriesCode = "gdp" if SeriesCode == "NY.GDP.PCAP.KD"
replace SeriesCode = "cap" if SeriesCode == "NE.GDI.TOTL.ZS"
replace SeriesCode = "urb" if SeriesCode == "SP.URB.TOTL.IN.ZS"
keep if inlist(SeriesCode, "gdp", "cap", "urb")
drop SeriesName

reshape wide YR, i(CountryCode Year) j(SeriesCode) string
rename (YRgdp YRcap YRurb Year CountryCode) (gdp cap urb year country_3d)
label variable gdp "GDP per capita (constant 2015 US$)"
label variable cap "Gross capital formation (% of GDP)"
label variable urb "Urban population (% of total population)"
keep country_3d year gdp cap urb
save "$clear_data/wdi.dta", replace

* ----------------------------------------------------------------
**## HCI, population — Penn World Table 11.0
* ----------------------------------------------------------------
clear
use "$raw_data/pwt110.dta"
rename (countrycode hc) (country_3d hci)
label variable hci "Human capital index"
label variable pop "Population (millions)"
keep country_3d year hci pop
save "$clear_data/pwt.dta", replace

* ----------------------------------------------------------------
**## PAT — WIPO patent applications and patent stock
* ----------------------------------------------------------------
clear
import excel "$raw_data/patent_raw.xlsx", sheet("sheet1") firstrow
isid country_2d type
drop country_name
reshape long Y, i(country_2d type) j(year)
reshape wide Y, i(country_2d year) j(type) string
rename (YAbroad YResident YTotal) (pat_nr pat_r pat_total)
* [R2-14] WIPO "by applicant origin" series: Total = Resident + Abroad, where
*         Abroad = applications filed by residents of the country at foreign
*         offices (NOT applications by non-residents, as cleaning.do labelled it).
*         Indicator: "Total patent applications (direct and PCT national phase
*         entries)": PCT international-phase filings are not counted, so a PCT
*         application enters once per national/regional office it enters.
label variable pat_total "Patent applications by applicant origin, all offices (WIPO)"
label variable pat_nr    "Patent applications filed abroad by residents (WIPO)"
label variable pat_r     "Patent applications filed at the home office by residents (WIPO)"

* Fill total applications from components where missing
replace pat_total = 0      if missing(pat_total) &  missing(pat_nr)
replace pat_total = pat_nr if missing(pat_total) & !missing(pat_nr)

* Perpetual inventory method, depreciation rate 15% (Griliches, 1979)
* Initial stock: P0 / (g0 + delta), g0 = country-specific growth over the first five years
local delta 0.15
bysort country_2d (year): gen double g0 = (pat_total[6]/pat_total[1])^(1/5) - 1 if pat_total[1] > 0
replace g0 = 0.05 if missing(g0) | g0 <= 0                       // fallback growth rate

bysort country_2d (year): gen double patstock = pat_total[1]/(g0 + `delta') if _n == 1 & pat_total[1] > 0
bysort country_2d (year): replace patstock = 0 if _n == 1 & pat_total[1] == 0
bysort country_2d (year): replace patstock = (1 - `delta')*patstock[_n-1] + pat_total if _n > 1

label variable patstock "Patent stock (perpetual inventory, delta = 0.15)"

* [R2-4] Alternative stock built from filings abroad only (same rule): used in the
*        patent-endogeneity sensitivity, because the shift-share instrument predicts
*        international filings and many African home offices report to WIPO only in
*        some years (Total then equals Abroad in the missing years).
replace pat_nr = 0 if missing(pat_nr)
bysort country_2d (year): gen double g0a = (pat_nr[6]/pat_nr[1])^(1/5) - 1 if pat_nr[1] > 0
replace g0a = 0.05 if missing(g0a) | g0a <= 0
bysort country_2d (year): gen double patstock_abr = pat_nr[1]/(g0a + `delta') if _n == 1 & pat_nr[1] > 0
bysort country_2d (year): replace patstock_abr = 0 if _n == 1 & pat_nr[1] == 0
bysort country_2d (year): replace patstock_abr = (1 - `delta')*patstock_abr[_n-1] + pat_nr if _n > 1
label variable patstock_abr "Patent stock of filings abroad (perpetual inventory, delta = 0.15)"

keep country_2d year patstock patstock_abr pat_total                // [R2-14] pat_total kept for Table 2 note
save "$clear_data/patent.dta", replace

* ----------------------------------------------------------------
**## INC — World Bank income classification
* ----------------------------------------------------------------
clear
import excel "$raw_data/income_raw.xlsx", sheet("Sheet1") firstrow
keep Country3 Y2000 Y2001 Y2002 Y2003 Y2004 Y2005 Y2006 Y2007 Y2008 Y2009 Y2010 Y2011 ///
     Y2012 Y2013 Y2014 Y2015 Y2016 Y2017 Y2018 Y2019 Y2020 Y2021 Y2022 Y2023
reshape long Y, i(Country3) j(year)
rename (Y Country3) (inc_class country_3d)
label variable inc_class "World Bank income class (L, LM, UM, H)"
save "$clear_data/income.dta", replace

* ----------------------------------------------------------------
**## EF, BIO — Global Footprint Network
* ----------------------------------------------------------------
import delimited "$raw_data/gfn_raw.csv", clear varnames(1) encoding(UTF-8)
rename (isoa2 biocappercap efconspercap) (country_2d bio ef)
label variable ef  "Ecological footprint of consumption per capita (gha)"
label variable bio "Biocapacity per capita (gha)"
keep country_2d year bio ef
save "$clear_data/gfn.dta", replace

* ----------------------------------------------------------------
**## [R2-4] Shift-share instrument for PAT (WIPO; constructed in Python, see data description)
* ----------------------------------------------------------------
import delimited "$raw_data/wipo_shiftshare_instrument.csv", clear varnames(1) encoding(UTF-8) stringcols(1 2)
keep country_3d year z_mean_lag1_10 z_lag1 z_lag5 inflow_90_99
label variable z_mean_lag1_10 "Shift-share predicted foreign filings into country, mean of lags 1-10"
label variable inflow_90_99   "Foreign filings into the country's offices, 1990-1999 (share base)"
save "$clear_data/instrument.dta", replace

* ----------------------------------------------------------------
**## [cepi] IMF Commodity Terms of Trade (only if clear.dta does not already contain cepi)
* ----------------------------------------------------------------
* The do_10.5 instrument set uses `cepi` but do_10.5 never creates it. If your cepi came
* from another file, keep that and skip this block. Otherwise set the series below to the
* one used in your revision of comments 1-3 (default: commodity export price index,
* exports/GDP weights, fixed weights, 2012 = 100).
import delimited "$raw_data/imf_ctot.csv", clear varnames(1) encoding(UTF-8) stringcols(1 2)
gen double cepi = cepi_gdp_fw
label variable cepi "IMF commodity export price index (exports/GDP weights, fixed weights)"
keep country_3d year cepi
save "$clear_data/cepi.dta", replace

* ----------------------------------------------------------------
**## Merge
* ----------------------------------------------------------------
clear
use "$clear_data/pwt.dta"
merge m:1 country_3d using "$clear_data/iso.dta", keep(match) nogen
merge 1:1 country_2d year using "$clear_data/patent.dta", keep(match) nogen
merge 1:1 country_3d year using "$clear_data/income.dta", keep(match) nogen
keep if inlist(continent_2d, "AS", "AF")
merge 1:1 country_3d year using "$clear_data/wdi.dta", keep(match) nogen
merge 1:1 country_2d year using "$clear_data/gfn.dta", keep(match) nogen
merge 1:1 country_3d year using "$clear_data/instrument.dta", keep(master match) nogen   // [R2-4] CD, KH, PH have no instrument
capture confirm variable cepi                                                           // [cepi]
if _rc merge 1:1 country_3d year using "$clear_data/cepi.dta", keep(master match) nogen

save "$clear_data/clear.dta", replace

* ================================================================
**# ESTIMATION SAMPLE (Section 3.3, Appendix A)
* ================================================================
global model_raw "gdp ef bio cap hci urb patstock"

clear
use "$clear_data/clear.dta"
encode country_3d, gen(id)
xtset id year

* Missingness rate (%) by country and variable — Appendix A
* Countries with any missing value on a model variable are excluded
preserve
    bysort id: gen int T = _N
    collapse (count) $model_raw (first) T, by(id country_3d continent_2d)
    foreach v of global model_raw {
        gen double miss_`v' = 100*(1 - `v'/T)
    }
    egen double max_miss = rowmax(miss_*)
    gen byte exclude = (max_miss > 0)
    keep country_3d continent_2d exclude miss_*
    save "$clear_data/excluded_list.dta", replace
restore

merge m:1 country_3d using "$clear_data/excluded_list.dta", ///
    keepusing(exclude) assert(match) nogen
drop if exclude == 1
drop exclude

* ================================================================
**# VARIABLE CONSTRUCTION (Section 3.1, Table 1)
* ================================================================

** Income: log level (Table 3, turning points) and mean-centred polynomial (estimation)
gen double lngdp = ln(gdp)
quietly summarize lngdp
scalar lngdp_bar = r(mean)
display "Centring constant = " lngdp_bar "  (USD " exp(lngdp_bar) ")"

gen double lngdp_c  = lngdp - scalar(lngdp_bar)
gen double lngdp_c2 = lngdp_c^2
gen double lngdp_c3 = lngdp_c^3

** Ecological footprint, biocapacity, innovation
gen double lnef  = ln(ef)
gen double lnbio = ln(bio)
gen double pat   = patstock/pop
gen double lnpat = ln((patstock + 1)/pop)

** Additional instruments (Kelejian, 1971)
gen double cap2 = cap^2
gen double cap3 = cap^3
gen double hci2 = hci^2
gen double hci3 = hci^3

** Region and development level (income class fixed at 2000)
gen byte asia = (continent_2d == "AS")

gen byte inc_num = .
replace  inc_num = 1 if inlist(inc_class, "H", "UM")
replace  inc_num = 0 if inlist(inc_class, "L", "LM")
gen byte inc = inc_num if year == 2000
bysort id (year): replace inc = inc[1]
drop inc_num

** Interaction PAT × INC
gen double pat_inc = lnpat * inc

* [R2-7] Alternative predetermined development classifications
*   inc_early : upper-middle/high income in the majority of 2000-2004
*   inc_2005  : classification fixed in 2005
*   inc_2010  : classification fixed in 2010 (mid-period; reported as a stress test only)
*   dev2000   : continuous, ln GDP per capita in 2000 (centred)
gen byte hi_tmp = inlist(inc_class, "H", "UM") if !missing(inc_class)
bysort id: egen double sh_0004 = mean(cond(inrange(year, 2000, 2004), hi_tmp, .))
gen byte inc_early = (sh_0004 > 0.5)
foreach y in 2005 2010 {
    gen byte t_`y' = hi_tmp if year == `y'
    bysort id: egen byte inc_`y' = max(t_`y')
    drop t_`y'
}
bysort id (year): gen double dev2000 = lngdp[1]
quietly summarize dev2000 if year == 2000
replace dev2000 = dev2000 - r(mean)
drop hi_tmp sh_0004
foreach k in early 2005 2010 {
    gen double pat_inc_`k' = lnpat * inc_`k'
}
gen double pat_dev = lnpat * dev2000

* [R2-4] Shift-share instrument and alternative (abroad-filing) patent stock
gen double lnz        = ln(1 + z_mean_lag1_10)
gen double lnz_inc    = lnz * inc
gen double lnpat_abr  = ln((patstock_abr + 1)/pop)
gen double pat_inc_abr = lnpat_abr * inc
label variable lnz       "ln(1 + shift-share instrument)"
label variable lnpat_abr "ln (stock of filings abroad + 1) per million people"

label variable lngdp    "ln GDP per capita"
label variable lngdp_c  "ln GDP per capita, mean-centred"
label variable lngdp_c2 "ln GDP per capita, mean-centred, squared"
label variable lngdp_c3 "ln GDP per capita, mean-centred, cubed"
label variable lnef     "ln ecological footprint per capita"
label variable lnbio    "ln biocapacity per capita"
label variable lnpat    "ln (patent stock + 1) per million people"
label variable asia     "Asia = 1, Africa = 0"
label variable inc      "Upper-middle/high income in 2000 = 1"
label variable pat_inc  "lnPAT × INC"

keep id country_3d continent_2d year gdp ef bio cap hci urb pat pop inc_class ///
     lngdp lngdp_c lngdp_c2 lngdp_c3 lnef lnbio lnpat cap2 cap3 hci2 hci3 asia inc pat_inc cepi ///
     patstock patstock_abr pat_total lnpat_abr pat_inc_abr lnz lnz_inc z_mean_lag1_10 inflow_90_99 ///  [R2-4]
     inc_early inc_2005 inc_2010 dev2000 pat_inc_early pat_inc_2005 pat_inc_2010 pat_dev             //  [R2-7]

* [R2-14/17] Data check: WDI reports gross capital formation = 0 for Ethiopia in 2000-2010.
*            This is not a plausible value; verify the WDI extract (NE.GDI.TOTL.ZS).
*            Results without Ethiopia are reported in Section R2.11 below.
list country_3d year cap if cap == 0, noobs
order id country_3d continent_2d year
xtset id year

** Sample checks: 43 countries (17 Asia, 26 Africa), 2000–2023, balanced, N = 1,032
egen byte tag = tag(id)
count if tag

save "$clear_data/analysis.dta", replace


* ================================================================
**# SECTION 4.1 — DESCRIPTIVE STATISTICS (Tables 2–4)
* ================================================================

** Table 2 — original scale (pooled, Africa, Asia)
* [R2-14/17] `pat' is the patent STOCK per million people. The PAT row in the
*            submitted Table 2 (mean 32,349; max 1,642,643) is the annual FLOW of
*            applications (pat_total); replace it with the row produced here.
local t2 "gdp ef pat cap hci bio urb inc"
tabstat `t2', statistics(n mean sd min max) columns(statistics) format(%14.3fc)
tabstat `t2' if asia == 0, statistics(n mean sd min max) columns(statistics) format(%14.3fc)
tabstat `t2' if asia == 1, statistics(n mean sd min max) columns(statistics) format(%14.3fc)

** Table 3 — log form
local t3 "lngdp lnef lnpat lnbio"
tabstat `t3', statistics(n mean sd min max) columns(statistics) format(%9.3f)
tabstat `t3' if asia == 0, statistics(n mean sd min max) columns(statistics) format(%9.3f)
tabstat `t3' if asia == 1, statistics(n mean sd min max) columns(statistics) format(%9.3f)

** Income structure of the sample (text of Section 4.1)
tab continent_2d inc if tag
tab continent_2d inc, row

** Table 4 — correlation matrix
correlate lngdp cap hci lnpat lnef lnbio urb

** [R2-10] Within-transformed correlations (country and year effects removed) and VIFs
foreach v in lngdp cap hci lnpat lnef lnbio urb {
    quietly reghdfe `v', absorb(id year) resid(w_`v')
}
correlate w_lngdp w_cap w_hci w_lnpat w_lnef w_lnbio w_urb          // new Table 4b
quietly regress w_lngdp w_lnef w_cap w_hci w_lnpat                   // growth-equation regressors
estat vif
quietly regress w_lnef w_lngdp w_lnbio w_urb w_lnpat                 // environmental-equation regressors
estat vif
drop w_*


* ================================================================
**# SECTION 4.2 — CSD AND UNIT ROOT TESTS (Tables 5–6)
* ================================================================
global test_var "lnef lngdp lnpat cap hci lnbio urb"

** Table 5 — Pesaran (2007) CD test
foreach v of global test_var {
    display _newline as text "=== `v' ==="
    xtcd2 `v'
}

** Table 6 — CIPS (Pesaran, 2007), constant, one lagged difference
multipurt $test_var, lags(1)


* ================================================================
**# APPENDIX B — IDENTIFICATION DIAGNOSTICS (Tables B1–B4)
* ================================================================
* Each equation estimated separately by 2SLS with country and year
* fixed effects and SEs clustered by country.
*   ffirst   -> SW conditional F, KP rk LM, KP Wald F (B1); AR Wald F (B4)
*   endog()  -> endogeneity test (B2)
*   default  -> Hansen J (B3)

** Growth equation (lnEF endogenous)
ivreg2 lngdp_c cap hci lnpat i.id i.year ///
    (lnef = lnbio urb), ///
    cluster(id) ffirst partial(i.id i.year) endog(lnef)

** Environmental equation — cubic
ivreg2 lnef lnpat lnbio urb i.id i.year ///
    (lngdp_c lngdp_c2 lngdp_c3 = cap cap2 cap3 hci hci2 hci3), ///
    cluster(id) ffirst partial(i.id i.year) endog(lngdp_c lngdp_c2 lngdp_c3)

** Environmental equation — quadratic
ivreg2 lnef lnpat lnbio urb i.id i.year ///
    (lngdp_c lngdp_c2 = cap cap2 hci hci2), ///
    cluster(id) ffirst partial(i.id i.year) endog(lngdp_c lngdp_c2)

** Environmental equation — linear
ivreg2 lnef lnpat lnbio urb i.id i.year ///
    (lngdp_c = cap hci cepi), ///
    cluster(id) ffirst partial(i.id i.year) endog(lngdp_c)


* ================================================================
**# SECTION 5.1 — EKC HYPOTHESIS (Tables 7–9)
* ================================================================

** Turning point of the quadratic EF equation (criterion iii), in USD
capture program drop ekc_tp
program define ekc_tp
    args sample_label
    quietly summarize lngdp if e(sample)
    local lo = r(min)
    local hi = r(max)
    local tp = -_b[EF:lngdp_c]/(2*_b[EF:lngdp_c2]) + scalar(lngdp_bar)
    display _newline as text "=== `sample_label', quadratic ==="
    display as text "b1 = " _b[EF:lngdp_c] "   b2 = " _b[EF:lngdp_c2] "   (b2 < 0 required)"
    display as text "Turning point = USD " exp(`tp')
    display as text "Sample range  = USD " exp(`lo') " to USD " exp(`hi')
    display as text "Interior?       " cond(`tp' > `lo' & `tp' < `hi', "YES", "NO")
end

* ----------------------------------------------------------------
**## Table 7 — Pooled sample
* ----------------------------------------------------------------
** Cubic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lngdp_c3 lnbio urb i.id i.year), ///
     endog(lngdp_c lngdp_c2 lngdp_c3 lnef) exog(cap2 cap3 hci2 hci3)
outreg2 using "$results/Table7_Pooled.xls", dec(3) replace ctitle(Cubic)

** Quadratic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lnbio urb i.id i.year), ///
     endog(lngdp_c lngdp_c2 lnef) exog(cap2 hci2)
outreg2 using "$results/Table7_Pooled.xls", dec(3) ctitle(Quadratic)

** Linear
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb i.id i.year), ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table7_Pooled.xls", dec(3) ctitle(Linear)

** Linear instruments sensitivity
reghdfe lnef lngdp_c lnbio urb, absorb(id year) vce(cluster id)
outreg2 using "$results/Table_FE.xls", dec(3) replace ctitle(Pooled, FE)

xtscc lnef lngdp_c lnbio urb i.year, fe lag(3)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Pooled, FE-DK) drop(i.year)

ivreghdfe lnef lnbio urb (lngdp_c = cap hci cepi), absorb(id year) cluster(id) first endog(lngdp_c)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Pooled, FE-IV)

weakiv ivreg2 lnef lnbio urb i.id i.year (lngdp_c = cap hci), cluster(id) partial(i.id i.year)

* ----------------------------------------------------------------
**## Table 8 — Asian countries
* ----------------------------------------------------------------
** Cubic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lngdp_c3 lnbio urb i.id i.year) if asia == 1, ///
     endog(lngdp_c lngdp_c2 lngdp_c3 lnef) exog(cap2 cap3 hci2 hci3)
outreg2 using "$results/Table8_Asia.xls", dec(3) replace ctitle(Cubic)

** Quadratic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lnbio urb i.id i.year) if asia == 1, ///
     endog(lngdp_c lngdp_c2 lnef) exog(cap2 hci2)
outreg2 using "$results/Table8_Asia.xls", dec(3) ctitle(Quadratic)
ekc_tp "ASIA"

** Linear
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb i.id i.year) if asia == 1, ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table8_Asia.xls", dec(3) ctitle(Linear)

** Linear instruments sensitivity
reghdfe lnef lngdp_c lnbio urb if asia == 1, absorb(id year) vce(cluster id)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Asia, FE)

xtscc lnef lngdp_c lnbio urb i.year if asia == 1, fe lag(3)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Asia, FE-DK) drop(i.year)

ivreghdfe lnef lnbio urb (lngdp_c = cap hci cepi) if asia == 1, absorb(id year) cluster(id) first endog(lngdp_c)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Asia, FE-IV)

weakiv ivreg2 lnef lnbio urb i.id i.year (lngdp_c = cap hci) if asia == 1, cluster(id) partial(i.id i.year)

* ----------------------------------------------------------------
**## Table 9 — African countries
* ----------------------------------------------------------------
** Cubic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lngdp_c3 lnbio urb i.id i.year) if asia == 0, ///
     endog(lngdp_c lngdp_c2 lngdp_c3 lnef) exog(cap2 cap3 hci2 hci3)
outreg2 using "$results/Table9_Africa.xls", dec(3) replace ctitle(Cubic)

** Quadratic
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lngdp_c2 lnbio urb i.id i.year) if asia == 0, ///
     endog(lngdp_c lngdp_c2 lnef) exog(cap2 hci2)
outreg2 using "$results/Table9_Africa.xls", dec(3) ctitle(Quadratic)
ekc_tp "AFRICA"

** Linear
reg3 (GDP: lngdp_c lnef cap hci i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb i.id i.year) if asia == 0, ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table9_Africa.xls", dec(3) ctitle(Linear)

* Linear instruments sensitivity
reghdfe lnef lngdp_c lnbio urb if asia == 0, absorb(id year) vce(cluster id)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Africa, FE)

xtscc lnef lngdp_c lnbio urb i.year if asia == 0, fe lag(3)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Africa, FE-DK) drop(i.year)

ivreghdfe lnef lnbio urb (lngdp_c = cap hci cepi) if asia == 0, absorb(id year) cluster(id) first endog(lngdp_c)
outreg2 using "$results/Table_FE.xls", dec(3) ctitle(Africa, FE-IV)

weakiv ivreg2 lnef lnbio urb i.id i.year (lngdp_c = cap hci) if asia == 0, cluster(id) partial(i.id i.year)

* ================================================================
**# SECTION 5.2 — ROLE OF INNOVATION (Tables 10–11)
* ================================================================
* Linear form retained from Section 5.1.
* Table 11: marginal effect of lnPAT on lnEF = b(lnPAT) for INC = 0,
*           b(lnPAT) + b(PAT × INC) for INC = 1; N from tab inc.

** [R2-data] Composition of the higher-income group (new compact table, Section 3.3)
tab country_3d continent_2d if inc == 1 & year == 2000

** Pooled
reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year), ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table10_Innovation.xls", dec(3) replace ctitle(Pooled)
* [R2-17] Joint Wald tests for H2 and H3 (new Table 11b)
test [GDP]lnpat                                         // H2 growth margin
test [EF]lnpat [EF]pat_inc                              // no EF association in either income group
test [EF]pat_inc                                        // H3
test ([GDP]lnpat = 0) ([EF]lnpat + [EF]pat_inc = 0)     // H2 dual role, higher-income group
lincom [EF]lnpat + [EF]pat_inc

** Asia
reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if asia == 1, ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table10_Innovation.xls", dec(3) ctitle(Asia)
test [GDP]lnpat                                         // [R2-17] H2 growth margin
test [EF]lnpat [EF]pat_inc                              // [R2-17]
test ([GDP]lnpat = 0) ([EF]lnpat + [EF]pat_inc = 0)     // [R2-17] H2 dual role, higher-income group

lincom [EF]lnpat                                   // Table 11: Asia, lower income
lincom [EF]lnpat + [EF]pat_inc                     // Table 11: Asia, higher income
tab inc if e(sample)

** Africa
reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
     (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if asia == 0, ///
     endog(lngdp_c lnef)
outreg2 using "$results/Table10_Innovation.xls", dec(3) ctitle(Africa)
test [GDP]lnpat                                         // [R2-17] H2 growth margin
test [EF]lnpat [EF]pat_inc                              // [R2-17]
test ([GDP]lnpat = 0) ([EF]lnpat + [EF]pat_inc = 0)     // [R2-17] H2 dual role, higher-income group

lincom [EF]lnpat                                   // Table 11: Africa, lower income
lincom [EF]lnpat + [EF]pat_inc                     // Table 11: Africa, higher income
tab inc if e(sample)


* ================================================================
**# SECTION 5.3 — ROBUSTNESS: DRISCOLL–KRAAY (Table 12)
* ================================================================
* [R2-5/8] Table 12 now reports BOTH equations, so that every 3SLS coefficient has a
*          fixed-effects counterpart (Table 12b: coefficient-by-coefficient comparison).
*          The growth equation is estimated without instrumenting lnEF (association).
foreach r in 1 0 {
    xtscc lngdp_c lnef cap hci lnpat i.year if asia == `r', fe lag(3)
    outreg2 using "$results/Table12b_GDP_DK.xls", dec(3) ctitle(asia=`r', GDP, DK) drop(i.year)
}
xtscc lngdp_c lnef cap hci lnpat i.year, fe lag(3)
outreg2 using "$results/Table12b_GDP_DK.xls", dec(3) ctitle(Pooled, GDP, DK) drop(i.year)

** Pooled
xtscc lnef lngdp_c lnbio urb lnpat pat_inc i.year, fe lag(3)
outreg2 using "$results/Table12_Robustness.xls", dec(3) replace ctitle(Pooled)
lincom lnpat + pat_inc                             // marginal effect, upper-income group

** Asia
xtscc lnef lngdp_c lnbio urb lnpat pat_inc i.year if asia == 1, fe lag(3)
outreg2 using "$results/Table12_Robustness.xls", dec(3) ctitle(Asia)
lincom lnpat + pat_inc

** Africa
xtscc lnef lngdp_c lnbio urb lnpat pat_inc i.year if asia == 0, fe lag(3)
outreg2 using "$results/Table12_Robustness.xls", dec(3) ctitle(Africa)
lincom lnpat + pat_inc


* ================================================================
**# [R2] SECTION 5.4 / APPENDIX D — SENSITIVITY ANALYSES FOR REVISION R2
* ================================================================
* Each block names the reviewer comment it answers. Results tables go to $results/R2_*.xls.
* Country codes of the higher-income group (inc == 1): Asia ISR JPN KOR MYS; Africa BWA MUS ZAF.

* ----------------------------------------------------------------
**## R2.1 [R2-4] Patent-stock endogeneity: shift-share instrument (Appendix D1)
* ----------------------------------------------------------------
* Instrument: lnz (predicted foreign filings into the country's patent offices, 1990s shares
* times lagged foreign filings of source countries, leave-out). Sample: 40 countries (no
* instrument for COD, KHM, PHL). ffirst: SW/KP first-stage F; endog(): robust C test of PAT
* exogeneity; weakiv: AR inference.
foreach s in "1" "asia == 1" "asia == 0" {
    * growth equation: lnEF (lnBIO, URB) and lnPAT (lnZ) endogenous
    ivreg2 lngdp_c cap hci i.id i.year (lnef lnpat = lnbio urb lnz) if `s', ///
        cluster(id) ffirst partial(i.id i.year) endog(lnpat)
    outreg2 using "$results/R2_D1_patent_IV.xls", dec(3) ctitle(`s', GDP, total stock)
    * environmental equation: lnGDP (CAP, HCI), lnPAT and PATxINC (lnZ, lnZxINC) endogenous
    ivreg2 lnef lnbio urb i.id i.year (lngdp_c lnpat pat_inc = cap hci lnz lnz_inc) if `s', ///
        cluster(id) ffirst partial(i.id i.year) endog(lnpat pat_inc)
    outreg2 using "$results/R2_D1_patent_IV.xls", dec(3) ctitle(`s', EF, total stock)
    * same with the stock of filings abroad
    ivreg2 lnef lnbio urb i.id i.year (lngdp_c lnpat_abr pat_inc_abr = cap hci lnz lnz_inc) if `s', ///
        cluster(id) ffirst partial(i.id i.year) endog(lnpat_abr pat_inc_abr)
    outreg2 using "$results/R2_D1_patent_IV.xls", dec(3) ctitle(`s', EF, abroad stock)
}
* 3SLS with the patent stock endogenous (lnZ, lnZxINC added to the system instruments)
foreach s in "1" "asia == 1" "asia == 0" {
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
         (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if `s' & !missing(lnz), ///
         endog(lngdp_c lnef lnpat pat_inc) exog(lnz lnz_inc)
    outreg2 using "$results/R2_D1_patent_3SLS.xls", dec(3) ctitle(`s', PAT endogenous)
    lincom [EF]lnpat + [EF]pat_inc
}

* ----------------------------------------------------------------
**## R2.2 [R2-6] Leave-one-country-out, higher-income countries (Table 13)
* ----------------------------------------------------------------
tempname H
postfile `H' str6 region str4 dropped double(b3 se3 me3 seme3 bdk sedk medk semedk) ///
    using "$results/R2_T13_LOO.dta", replace
foreach r in 1 0 {
    local region = cond(`r' == 1, "Asia", "Africa")
    local hi     = cond(`r' == 1, "none ISR JPN KOR MYS", "none BWA MUS ZAF")
    foreach c of local hi {
        local cond `"asia == `r' & country_3d != "`c'""'
        quietly reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
                     (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if `cond', ///
                     endog(lngdp_c lnef)
        local b3 = _b[EF:pat_inc]
        local se3 = _se[EF:pat_inc]
        quietly lincom [EF]lnpat + [EF]pat_inc
        local me3 = r(estimate)
        local seme3 = r(se)
        quietly xtscc lnef lngdp_c lnbio urb lnpat pat_inc i.year if `cond', fe lag(3)
        local bdk = _b[pat_inc]
        local sedk = _se[pat_inc]
        quietly lincom lnpat + pat_inc
        post `H' ("`region'") ("`c'") (`b3') (`se3') (`me3') (`seme3') (`bdk') (`sedk') (r(estimate)) (r(se))
    }
}
postclose `H'
* b3/se3 = 3SLS PAT x INC; me3/seme3 = 3SLS higher-income marginal effect;
* bdk/sedk and medk/semedk = the same from FE with Driscoll-Kraay SE. dropped = "none": full sample.
preserve
    use "$results/R2_T13_LOO.dta", clear
    list, noobs sep(0)
restore

* ----------------------------------------------------------------
**## R2.3 [R2-7] Alternative fixed development classifications (Table 14)
* ----------------------------------------------------------------
foreach k in early 2005 2010 {
    foreach r in 1 0 {
        reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
             (EF:  lnef lngdp_c lnbio urb lnpat pat_inc_`k' i.id i.year) if asia == `r', ///
             endog(lngdp_c lnef)
        outreg2 using "$results/R2_T14_classification.xls", dec(3) ctitle(INC `k', asia=`r')
        lincom [EF]lnpat + [EF]pat_inc_`k'
    }
}
* continuous development stage (ln GDP per capita in 2000)
foreach r in 1 0 {
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
         (EF:  lnef lngdp_c lnbio urb lnpat pat_dev i.id i.year) if asia == `r', ///
         endog(lngdp_c lnef)
    outreg2 using "$results/R2_T14_classification.xls", dec(3) ctitle(continuous, asia=`r')
}

* ----------------------------------------------------------------
**## R2.4 [R2-6/8] Few treated clusters: wild cluster bootstrap for PAT x INC (Table 15)
* ----------------------------------------------------------------
foreach r in 1 0 {
    regress lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year if asia == `r', vce(cluster id)
    boottest pat_inc, weight(webb) reps(9999) seed(12345) nograph
}

* ----------------------------------------------------------------
**## R2.5 [R2-5/8/9] 3SLS with country-clustered (bootstrap) standard errors (Table 12b)
* ----------------------------------------------------------------
* reg3 has no cluster option; a pairs-cluster bootstrap over countries is used instead.
foreach r in 1 0 {
    preserve
    keep if asia == `r'
    xtset, clear
    bootstrap, reps(499) seed(2026) cluster(id) idcluster(bid): ///
        reg3 (GDP: lngdp_c lnef cap hci lnpat i.bid i.year) ///
             (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.bid i.year), endog(lngdp_c lnef)
    lincom [EF]lnpat + [EF]pat_inc
    restore
}
xtset id year

* ----------------------------------------------------------------
**## R2.6 [R2-9] Cross-sectional dependence and slope heterogeneity (Appendix D2)
* ----------------------------------------------------------------
* (a) residual CD test after two-way FE; (b) CCE pooled (Pesaran 2006); (c) slope
* homogeneity test (Pesaran and Yamagata 2008); (d) CCE mean group by income cell.
foreach r in 1 0 {
    quietly reghdfe lnef lngdp_c lnbio urb lnpat pat_inc if asia == `r', absorb(id year) resid(e_fe)
    xtcd2 e_fe
    drop e_fe
    xtdcce2 lnef lngdp_c lnbio urb lnpat pat_inc if asia == `r', ///
        crosssectional(lnef lngdp_c lnbio urb lnpat) pooled(lngdp_c lnbio urb lnpat pat_inc)
    xthst lnef lngdp_c lnbio urb lnpat if asia == `r'
}
* CCE mean group: country-by-country regressions with regional cross-section averages
foreach r in 1 0 {
    preserve
    keep if asia == `r'
    foreach v in lnef lngdp_c lnbio urb lnpat {
        bysort year: egen double csa_`v' = mean(`v')
    }
    statsby b_lnpat = _b[lnpat], by(id inc) clear: ///
        regress lnef lngdp_c lnbio urb lnpat csa_lnef csa_lngdp_c csa_lnbio csa_urb csa_lnpat
    bysort inc: summarize b_lnpat                         // mean = CCE-MG slope; SE = sd/sqrt(n)
    restore
}

* ----------------------------------------------------------------
**## R2.7 [R2-15] Biocapacity sensitivity (Appendix D3)
* ----------------------------------------------------------------
foreach r in 1 0 {
    * lnBIO removed from the EF equation and from the instrument set of the GDP equation
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
         (EF:  lnef lngdp_c urb lnpat pat_inc i.id i.year) if asia == `r', ///
         endog(lngdp_c lnef)
    outreg2 using "$results/R2_D3_biocapacity.xls", dec(3) ctitle(no lnBIO, asia=`r')
    lincom [EF]lnpat + [EF]pat_inc
    * growth equation identified by URB only (lnBIO kept as EF control)
    ivreg2 lngdp_c cap hci lnpat i.id i.year (lnef = urb) if asia == `r', ///
        cluster(id) ffirst partial(i.id i.year)
}

* ----------------------------------------------------------------
**## R2.8 Non-overlapping 3-year averages (Appendix D4; smooths annual shocks)
* ----------------------------------------------------------------
preserve
gen int period = 2000 + 3*floor((year - 2000)/3)
collapse (mean) gdp ef bio cap hci urb patstock pop z_mean_lag1_10 ///
         (first) inc asia country_3d, by(id period)
gen double lngdp   = ln(gdp)
quietly summarize lngdp
gen double lngdp_c = lngdp - r(mean)
gen double lnef    = ln(ef)
gen double lnbio   = ln(bio)
gen double lnpat   = ln((patstock + 1)/pop)
gen double pat_inc = lnpat * inc
xtset id period
foreach r in 1 0 {
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.period) ///
         (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.period) if asia == `r', ///
         endog(lngdp_c lnef)
    outreg2 using "$results/R2_D4_3year.xls", dec(3) ctitle(3-year, asia=`r')
    lincom [EF]lnpat + [EF]pat_inc
    ivreg2 lnef lnbio urb lnpat pat_inc i.id i.period (lngdp_c = cap hci) if asia == `r', ///
        cluster(id) ffirst partial(i.id i.period)            // identification in the averaged panel
}
restore
xtset id year

* ----------------------------------------------------------------
**## R2.9 Sample ending in 2022 (GFN marks 2023 as an estimate) (Appendix D5)
* ----------------------------------------------------------------
foreach r in 1 0 {
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
         (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if asia == `r' & year <= 2022, ///
         endog(lngdp_c lnef)
    outreg2 using "$results/R2_D5_2022.xls", dec(3) ctitle(2000-2022, asia=`r')
}

* ----------------------------------------------------------------
**## R2.10 [R2-14/17] Without Ethiopia (CAP = 0 in 2000-2010 in the WDI extract)
* ----------------------------------------------------------------
foreach s in "1" "asia == 0" {
    reg3 (GDP: lngdp_c lnef cap hci lnpat i.id i.year) ///
         (EF:  lnef lngdp_c lnbio urb lnpat pat_inc i.id i.year) if `s' & country_3d != "ETH", ///
         endog(lngdp_c lnef)
    outreg2 using "$results/R2_D6_noETH.xls", dec(3) ctitle(`s', without ETH)
}

log close
