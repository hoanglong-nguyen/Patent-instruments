# Revision R2 — instructions for Claude Code (local run)

Read this whole file before acting. You are helping a PhD researcher finish the second-round
revision of the manuscript "Technological Innovation and the Growth–Environment Relationship:
Evidence from Asia and Africa by Region and Income Group" (Environmental Development,
ENVDEV-D-26-01510R1). The analysis was prepared in a cloud session without Stata; every number in
the guidance comes from a Python replication. Your job is to run the real Stata and R code on the
researcher's machine, test the results against the expected values below, and prepare the material
for the manuscript edits. You do not edit the manuscript itself (the researcher does that with
Claude in Word).

## 1. Files

Put these files in the researcher's project (ask the researcher for the exact folders; the
do-file globals are `$raw_data`, `$clear_data` and `$results`):

| File | Where | Role |
|---|---|---|
| `do_10.6.do` | do-file folder | Main do-file: `do_10.5.do` plus changes tagged `[R2-#]` |
| `figures_R2.R` | do-file folder | Figures 1–3 on the estimation sample |
| `wipo_shiftshare_instrument.csv` | `$raw_data` | Shift-share instrument for patenting |
| `imf_ctot.csv` | `$raw_data` | IMF commodity price indices (source of `cepi` if needed) |
| `pwt110_cap_national_prices.csv` | `$raw_data` | PWT 11.0 capital formation, fills Ethiopia 2000–2010 |
| `R2_revision_guidance_for_Claude_in_Word.docx` | documents folder | Edits, tables, response drafts, citation list |
| `R2_data_description.docx` | documents folder | How the new data files were built |
| `Manuscript_10.5.docx`, `Response_10.5.docx` | documents folder | Current manuscript and response letter |

All files are also in GitHub: `hoanglong-nguyen/patent-instruments`, branch
`claude/wizardly-babbage-73c5ft`, folder `revision_R2/` (data in `revision_R2/data/`, expected
results in `revision_R2/results/*.csv`).

## 2. Rules (do not break)

1. **Never modify `do_10.5.do`** or any raw data file. Work on `do_10.6.do` only.
2. **Minimal fixes only.** If `do_10.6.do` fails, fix the smallest possible thing, tag the line
   `// [R2-fix] <reason>`, and record it in the run report. Never change a specification,
   sample, instrument set or variable definition to make a result look better.
3. **The study period is 2000–2023** and the sample is the balanced 43 countries. Do not change them.
4. **Errors.** Report the exact Stata/R error message. If the same error happens twice, stop and
   ask the researcher.
5. **Stop and ask** before: installing software other than the Stata/R packages listed below;
   overwriting any file the researcher did not create in this session; and continuing past a test
   marked STOP in Section 5.
6. Do not upload data or manuscript text to any external service. Web look-ups are allowed only
   for checking published references (Step 6).
7. Write reports in plain, formal English (academic register). Keep numbers to three decimals.

## 3. Setup (Step 0)

1. Locate Stata. Windows: search `C:\Program Files\Stata*\` for `StataMP-64.exe`, `StataSE-64.exe`
   or `StataBE-64.exe`. macOS: `/Applications/Stata/Stata*.app/Contents/MacOS/stata-*`. Ask the
   researcher if not found.
2. Batch command (run from the do-file folder):
   - Windows (PowerShell): `& "<path>\StataMP-64.exe" /e do do_10.6.do`
   - macOS/Linux: `"<path>/stata-mp" -b do do_10.6.do`
   The batch log `do_10.6.log` appears in the working folder; the do-file also writes
   `$results/do_10.6.log`.
3. Check the Stata packages and install missing ones with one Stata batch file
   (`R2_setup.do`): `ivreg2 ranktest ivreghdfe reghdfe ftools weakiv xtscc xtdcce2 xthst boottest
   xtcd2 multipurt outreg2` (`ssc install <name>, replace`; `reghdfe` needs `ftools`).
4. Check R (`Rscript --version`) and the packages `tidyverse haven patchwork scales ggrepel
   countrycode` (install missing ones with `install.packages()`; ask first).
5. Open `do_10.6.do` and check the three globals at the top against the researcher's folders.
   Do not change anything else.

## 4. Steps

### Step 1 — Run `do_10.6.do`
Run it in batch mode. Read the whole log. Record every error and every `r(...)` code. If a
block fails, apply Rule 2 and rerun. Then run the tests in Section 5.

### Step 2 — Requirements 1–3 (already answered by the researcher)
`do_10.6.do` corrects Ethiopia's gross capital formation (CAP), which is an instrument for income.
So the researcher's own answers to comments 1–3 (Appendix B diagnostics, Tables 7–9, the FE and
FE-IV columns, `weakiv` results) change. Extract from the log, for the pooled, Asian and African
samples: the Sanderson–Windmeijer and Kleibergen–Paap F, the KP rk LM p-value, the endogeneity
test p-value, the Hansen J p-value and the Anderson–Rubin p-value for every `ivreg2` /
`ivreghdfe` / `weakiv` call in the "APPENDIX B" and "SECTION 5.1" blocks. Put them in the numbers
file (Step 5) next to the values printed in `Manuscript_10.5.docx` (Appendix B and Tables 7–9),
and list every change.

### Step 3 — Figures
Set the path to `analysis.dta` (written by `do_10.6.do` to `$clear_data`) in `figures_R2.R` and
run `Rscript figures_R2.R`. Check the printed regional means (Section 5, test F1) and that the
three PNG files exist. Do not change the styling.

### Step 4 — Numbers for the manuscript
Create `R2_numbers_for_manuscript.md`: for every table in Part C of the guidance (Tables 1b, 4b,
11b, 12b, 13, 14, 15, Appendix D1–D6) and for every number quoted in Part B (abstract, 5.1, 5.2,
5.3), give the guidance value, the Stata value and the difference. Mark each row OK (within the
tolerance in Section 5) or CHANGED. For CHANGED rows that alter a sign, a significance level or a
conclusion, quote the affected guidance sentence and propose replacement wording. Also give the
updated pooled and African columns of Tables 7, 9, 10 and 11 and the new Table 2 PAT row.

### Step 5 — Consistency scan of the manuscript
Convert `Manuscript_10.5.docx` to text (`pandoc -t plain`) and list, with section and a short
quote, every occurrence of: "sustainability transition", "raises", "promotes", "drives",
"driving", "drove", "contributes to", "no EKC", "absence of a valid EKC", "volatility",
"regional and income-group samples", "outlier", "Pesaran's (2007)", and the African figures
"$1,800", "$2,300", "1.4–1.5". Check that each is covered by an edit in Part B of the guidance;
list any that are not. Write `R2_consistency_audit.md`.

### Step 6 — Citation check (Part F of the guidance)
For each of the 18 citations in Part F, find the published article (DOI, journal page or
publisher abstract), state in one or two sentences what it studies and finds, and judge whether it
supports the claim quoted in Part F: SUPPORTS / PARTLY / DOES NOT / COULD NOT CHECK. For "DOES
NOT", propose removal or a replacement already in the reference list. Then verify the new
references in Part E3 of the guidance (authors, year, title, journal, volume, pages, DOI). If the
`research-desk:citation-check` skill is available, use it. Write `R2_citation_check.md`. Never
invent a reference; if you cannot verify one, say so.

### Step 7 — Run report
Write `R2_run_report.md`: environment (Stata version, R version, package versions), every step
with PASS / FAIL / CHANGED, the exact errors and the `[R2-fix]` changes, the test table of
Section 5, and a short list of decisions the researcher must make. Then stop and summarise for
the researcher in the chat.

## 5. Tests (expected values from the Python replication)

Tolerances: coefficients ±0.005 (±0.010 for patent-related coefficients, because the researcher's
`patent_raw.xlsx` may be a slightly different WIPO vintage: the replication gives mean lnPAT 2.179
against 2.168 in Table 3); standard errors ±10%; bootstrap p-values ±0.03. Outside tolerance →
CHANGED (report, do not stop) unless marked STOP.

| ID | Check | Expected | If it fails |
|---|---|---|---|
| S1 | Sample after the exclusion rule | 43 countries (17 AS, 26 AF), 1,032 obs, balanced | STOP |
| S2 | `list ... if cap_filled == 1` | Ethiopia (ETH) 2000–2010 only, CAP 22.2–29.0 | STOP |
| S3 | Higher-income group (`inc == 1`) | ISR JPN KOR MYS; BWA MUS ZAF | STOP |
| S4 | Instrument coverage | `lnz` missing only for COD, KHM, PHL | report |
| T7 | EKC, pooled (Table 7) | cubic lead −0.006***; quadratic −0.003 (p ≈ 0.39); linear lnGDP 1.065*** (0.196) | report |
| T8 | EKC, Asia (Table 8, unaffected by Ethiopia) | cubic −0.019***; quadratic −0.070***, TP ≈ $228,885; linear 0.763*** | STOP if Asia differs: data merge problem |
| T9 | EKC, Africa (Table 9) | cubic −0.053**; quadratic −0.019 (p ≈ 0.26); linear 1.675*** (0.432) | report |
| T10a | Table 10, Asia | GDP eq: lnEF 0.595, lnPAT 0.027 (0.009); EF eq: lnGDP 0.737, lnPAT 0.009, PAT×INC −0.086 (0.026); marginal effect INC=1 −0.077 (0.023) | STOP if PAT×INC differs by more than 0.010 |
| T10p | Table 10, pooled | GDP: lnEF 1.134, lnPAT 0.043; EF: lnGDP 1.023, lnPAT −0.047, PAT×INC 0.002; ME −0.046 | report |
| T10f | Table 10, Africa | GDP: lnEF 1.126, lnPAT 0.080; EF: lnGDP 1.241 (0.469), lnPAT −0.106, PAT×INC 0.004; ME −0.102 | report |
| W | Table 11b Wald tests | Asia: H2a χ² 8.35; EF joint 11.38; H3 11.05; dual role 14.02. Pooled: 35.46; 16.53; 0.45; 35.95. Africa: 75.17; 19.69; 0.08; 75.17 | report |
| L | Table 13 leave-one-out, Asia PAT×INC (3SLS) | none −0.086; −ISR −0.086; −JPN −0.100; −KOR −0.076; −MYS −0.148. DK marginal effect without KOR −0.042 (n.s.) | report |
| C | Table 14 classifications, Asia | majority 2000–04 and 2005 = main; 2010: PAT×INC −0.044, ME −0.028; continuous −0.017 | report |
| B | Table 15, wild cluster bootstrap (boottest), Asia PAT×INC | p ≈ 0.16 (Python 0.161) | report |
| BS | 3SLS pairs-cluster bootstrap SE, Asia PAT×INC | ≈ 0.08 (Python analytic 0.079) | report |
| DK | Table 12 / 12b, Asia EF eq | PAT×INC −0.093 (0.036); lnGDP 0.570 | report |
| D1 | Appendix D1 (ivreg2 ffirst) | SW F lnPAT: pooled GDP 2.77, Asia GDP 3.86, Asia EF 17.07, Africa EF 1.12; endog() p: Asia 0.85/0.78, Africa EF 0.001 | report |
| D2 | Appendix D2 | FE residual CD: pooled −2.77, Asia −2.07, Africa −3.21; CCE-MG lnPAT slope, Asia INC=1 −0.261 | report (xtdcce2 SEs differ from Python by design) |
| D3 | No biocapacity, Asia | PAT×INC −0.122, ME −0.106 | report |
| D4 | 3-year averages, Asia | PAT×INC −0.085 (0.040), ME −0.077 | report |
| D5 | 2000–2022, Asia | PAT×INC −0.082, ME −0.077 | report |
| D6 | As-submitted CAP (cap_wdi), Asia and pooled | reproduces the submitted Table 10 (pooled PAT×INC −0.003; Asia −0.086) | STOP if not reproduced: the data pipeline differs from the manuscript |
| G | Table 4b | within corr lnGDP–lnPAT 0.330, lnGDP–HCI 0.020; max within-VIF ≤ 1.6 | report |
| F1 | Figure means (printed by figures_R2.R) | Africa GDP 1,449 → 2,159, EF 1.31 → 1.37; Asia GDP 6,222 → 10,447, EF 2.26 → 2.65 | report |
| E1 | Identification after the CAP correction | SW F for income in EF eq (CAP, HCI): Asia 2.89, pooled 2.39, Africa 1.00 (the researcher's own instrument set includes `cepi`, so their values will differ; report both) | report |

## 6. Background the researcher has decided (do not reopen)

- Main estimator: 3SLS (`reg3`) with country and year dummies; income class fixed in 2000.
- Patent coefficients are reported as conditional associations: the shift-share instrument is too
  weak for the total patent stock to settle exogeneity (Appendix D1).
- Ethiopia's CAP for 2000–2010 comes from PWT 11.0 national accounts (100 × v_i / v_gdp), because
  WDI records zeros; Ethiopia stays in the sample.
- Figures are drawn from the estimation sample; shaded bands are the cross-country min–max range.
- The 2000–2022 and 3-year-average estimates are robustness checks only.
