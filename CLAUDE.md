# Lens.org patent extraction: BMM-style innovation proxy and shift-share instrument

Guideline for Claude Code. Read this whole file before acting. The pipeline script is
`lens_bmm_pipeline.py` in this folder.

## 0. Current design: WIPO only (approved 11 October 2026)

The researcher replaced the Lens design. Lens `applicant.residence` is missing for most national
filings (country sums cover 15–72% of world families), and Lens counts diverge from WIPO even in
trend (2000–2023 log correlation −0.37 for CN and JP). Sections 1–8 describe the Lens pipeline,
kept for the record only; the IL leftover stage (`blockC_IL`) will not be run.

- **Script:** `wipo_shift_share.py` (offline). Input `wipo_patent_office_origin.csv`: WIPO IP
  Statistics Data Center, indicator 1 "Total patent applications (direct and PCT national phase
  entries)", filing office × applicant origin, 1980–2023, updated May 2026.
- **Outcome (`wipo_pat_appl.csv`):** `pat_abroad` = applications filed by origin *c* at offices
  not acting for *c* (national office plus OAPI/ARIPO/Eurasian office of which *c* is a member).
  Chosen because many African home offices report in few years. `pat_total_wipo` and
  `home_office_reported` are kept for robustness.
- **Shares (`wipo_shares.csv`):** s_od = 1990–1999 abroad filings by *d* at offices acting for *o*,
  divided by *d*'s 1990–1999 abroad filings.
- **Instrument (`wipo_instrument.csv`):** Z_ot = Σ_d s_od × (d's abroad filings at t − lag,
  excluding those into *o*). Columns for lag 1, lag 5 and the mean over lags 1–10.
- **Known limits:** no instrument for CD, KH and PH (no reported 1990s inflows); OAPI members share
  one office and ARIPO members largely share one, so their instruments are nearly identical;
  very thin shares for MG, NP, ET, MU, MN and IQ; regional membership is current, not historical.
- **Choices (11 October 2026):** main instrument = mean over lags 1–10 (lag 1 and lag 5 as
  robustness); main sample keeps all origins with an instrument, with (ii) no thin shares
  (< 100 foreign filings 1990–1999) and (iii) also no OAPI/ARIPO members as robustness.
- **First stage (`first_stage.py` → `first_stage_results.csv`):** two-way FE, SE clustered by
  country. With CN/JP/KR (93% of `pat_abroad`) the instrument is weak (F ≈ 4–6) and PPML has the
  wrong sign. Without CN/JP/KR: PPML F ≈ 40–46 in samples (i)–(ii); OLS-log F ≈ 5 in (i),
  11–19 in (ii); sample (iii) has only 12 clusters, so its F is unreliable.
- **Regional offices** acting for a country now include the EPO ("EP") and the GCC office ("GC")
  as well as OAPI, ARIPO and Eurasian (current membership; TR joined the EPO in 2000 and CY in
  1998, so their 1990s EP-based shares overstate exposure).
- **Extended sample:** `python wipo_shift_share.py asia-africa` and `python first_stage.py
  asia-africa` cover all 102 UN-M49 Asian and African WIPO origins (`*_aa.csv`; availability in
  `wipo_availability_aa.csv`). 75 have an instrument. Without CN/JP/KR: PPML F ≈ 55–57,
  OLS-log F ≈ 10–11. Not yet adopted as the study sample: the researcher decides.
- **No covariates:** first stages use only WIPO data and two-way fixed effects; no income,
  GDP or population data are in the project.
- **SEM (`sem_estimation.py` → `sem_results.csv`, `sem_diagnostics.csv`):** three equations
  (lnGDP, lnEF, lnPAT; lnPAT enters (1) and (2); lnZ only in (3)), FE-2SLS and 3SLS with country
  and year dummies, SE clustered by country. Data in `data/*.dta` (researcher's WDI, PWT, GFN,
  income class; not committed). First run (11 October 2026): identification weak (Sanderson-
  Windmeijer F mostly < 5) and Hansen J rejects in (1) and (3) in the main sample; results are
  not yet defensible. Do not tune specifications to obtain significant coefficients.
- **Lens files** (`*.jsonl`, `lens_family_counts.csv`, Lens build outputs) are kept; do not delete
  them without asking.

## 1. Context

A PhD researcher (European Doctorate in Law and Economics) is building, from the Lens.org Patent API:

- `pat_appl`: simple-family counts by applicant country and earliest priority year, 2000–2023, for 43 Asian and African countries;
- a single-step shift-share instrument adapted from Berkes, Manysheva and Mestieri (2022, Section 5.3).

The work is non-commercial academic research. Lens must be credited as the data source.

## 2. Rules (do not break)

1. **Token.** The API token is read only from the environment variable `LENS_TOKEN`. Never print, log, echo, write to a file, commit or hard-code it. Never run `env`, `printenv` or `echo $LENS_TOKEN`. If `LENS_TOKEN` is missing, stop and ask the researcher to set it.
2. **Budget first.** Never start a record download (`blockB`, `blockC`) without first running its count step (`check`, `checkC`) and showing the result to the researcher. Ask for an explicit "yes" before each download.
3. **Do not change the study design** in Section 3 without the researcher's approval.
4. **No accounts, plans or purchases.** Do not request, renew or upgrade any Lens plan.
5. **Errors.** Report the exact error message. If the same error happens twice, stop and ask.
6. **Do not delete raw data** (`*.jsonl`, `lens_family_counts.csv`) without asking.

## 3. Study design

| Element | Choice |
|---|---|
| Origin countries (43) | BJ BF BD BW CF CN CI CM CD CG EG ET GH ID IN IQ IL JP KE KH KR MG ML MN MZ MU MY NE NP PK PH RW SN SL TG TH TJ TN TZ UG VN ZA ZW |
| Destination countries | All ISO-2 countries (from `pycountry`) |
| Country assignment | Applicant residence (`applicant.residence`), full counting |
| Counting unit | Simple families, dated by `earliest_priority_claim_date` |
| Block A (counts) | All countries + world, priority 1980–2023, Aggregation API |
| Block B (citing records) | Origin countries **excluding CN, JP, KR**, priority 1990–1999 |
| Block C (cited records) | Documents cited by Block B, filtered server-side to priority 1980–1998 |
| Share origins | Block B origins **excluding IL** (39 countries; approved 11 October 2026) |
| Shares | Citation lags 1–10 years; own-country links = 0 |
| Shifts | Actual lagged family counts of other countries (single step, not BMM's recursive prediction) |

**Consequence:** CN, JP, KR and IL have no estimated shares, so their instrument is empty (`None`). They remain in `pat_appl` and in Block A.

**IL decision (11 October 2026).** The trial accepts only page size 100, so after Block B (604 requests) only 334 search requests remained, enough for about 30,000 Block C records. Block C as designed needed about 69,000–85,000; 73,240 of the 107,925 cited documents are cited only by IL families. IL stays in `block_B.jsonl`, but Block C covers only documents cited by the other 39 origins. Leftover requests go to IL-only cited documents (`blockC_IL` → `block_C_IL.jsonl`, exploratory, not used by `build`).

## 4. API facts verified on 11 October 2026

- **Endpoints:** `POST https://api.lens.org/patent/search` and `POST https://api.lens.org/patent/aggregate`. Header: `Authorization: Bearer <token>`.
- **Search API trial:** 1,000 requests/month, 100,000 records/month, 10 requests/minute.
- **Aggregation API trial:** 1,000 requests/month, 5 requests/minute, at most 2 nested aggregations.
- **Usage at the time of writing:** about 948 search requests left; 99,990 records left; about 996 aggregation requests left.
- **Deadlines:** both trials expire on **25 October 2026**. The monthly quota resets only on 10 November 2026, so **Blocks B and C must fit together in one budget of about 99,900 records.**
- **Rate-limit headers:** every response carries `x-rate-limit-remaining-request-per-minute`, `x-rate-limit-remaining-request-per-month`, `x-rate-limit-remaining-record-per-month` and `x-rate-limit-reset-date`. A 429 response means wait and retry.
- **Aggregation response format:** `aggregations.by_year` is a dict keyed by year, e.g. `{"2010": {"doc_count": 64, "families": 30}}`. It is **not** a `buckets` list.
- **Size cap:** aggregation fails with **400** "Aggregations cannot be applied on results more than 10000000" when more than 10M documents match. The fix is to split the period (the script does this recursively).
- **Approximate family counts:** `cardinality` on `family.simple.id` is within about 1% of the exact count. Exact alternative: a search with `"size": 0, "group_by": "SIMPLE_FAMILY"` returns `group_by_count`, costs one request and no records.
- **No family ID field:** `families.simple_family` contains only `members` and `size`. Use the smallest member `lens_id` as the family key.
- **Field paths:** `biblio.priority_claims.earliest_claim.date` is present. `applicants[].residence` is filled. Citations are per document in `biblio.references_cited.citations[].patcit.lens_id`.
- **Invalid field:** `families.simple_family.family_id` in `include` returns 400 "Unrecognized fields".

Reference values for checking the output:

| Query | Documents | Families |
|---|---|---|
| Kenya, priority 2010 | 64 | 30 |
| World, priority 1990 | 1,592,927 | ≈ 804,000 |
| World, priority 2000 | 2,504,574 | ≈ 956,000–966,000 |
| World, priority 2020 | 7,764,608 | ≈ 5,000,000 |
| Block B, 43 countries, 1990–1999 | 2,174,327 | 1,150,183 |
| Block B, without CN/JP/KR/IN | 50,943 | 18,679 |
| Block B as designed (without CN/JP/KR) | ≈ 58,700 | ≈ 23,800 |

## 5. Procedure

Setup: `pip install requests pandas pycountry`. The researcher sets `LENS_TOKEN` themselves.

Run these steps in order, reporting after each one.

1. **`python lens_bmm_pipeline.py counts`** (Block A, about 1–1.5 hours, about 260–300 aggregation requests). The step can be resumed: it skips countries already in `lens_family_counts.csv`. Check:
   - Kenya 2010 = 30 families;
   - world rows exist for every year 1980–2023.
2. **`python lens_bmm_pipeline.py check`.** Report the per-year totals and the records left. Expect about 58,700. Ask before continuing.
3. **`python lens_bmm_pipeline.py blockB`.** Not resumable: if it fails, delete `block_B.jsonl` before rerunning. The first call tests page sizes 1000 → 100; report which size was accepted.
4. **`python lens_bmm_pipeline.py checkC`.** Report the number of distinct cited documents, the count inside the priority window, and the records left.
   - If Block C is larger than the records left minus 500, **stop**. Propose dropping IL from Block B (about 35,000 records) and ask the researcher.
5. **`python lens_bmm_pipeline.py blockC`.** Not resumable (same rule as step 3). Uses the counts saved by `checkC` (`block_C_check.json`) instead of counting again.
5b. **`python lens_bmm_pipeline.py blockC_IL`** (only after step 5, with the researcher's "yes"). Spends leftover requests on documents cited only by IL families until Lens stops.
6. **`python lens_bmm_pipeline.py build`** (offline). Output files:
   - `pat_appl.csv`;
   - `shares.csv`;
   - `shift_share_instrument.csv`;
   - `coverage_check.csv`.

Steps 1–5 must finish before 25 October 2026.

## 6. Checks before reporting results

- `pat_appl.csv`: 43 countries × 24 years. CD, ET and KH may have zeros.
- Instrument: non-missing for the 39 share origins, empty for CN, JP, KR and IL.
- Flag implausible counts for manual review: TJ (925 documents in 1990–1999) and SL (70) look like residence-coding artefacts.
- `coverage_check.csv`: with full counting, the sum of the country counts can exceed the world total. Report the ratio; do not treat the difference as "missing residence".
- Families with priority 2022–2023 may still grow in later data.

## 7. Deviations from BMM to disclose in the paper

- Applicant residence instead of inventor residence.
- Full counting of multi-country families.
- Single-step shift-share using actual lagged foreign counts, not recursive prediction.
- Origin network limited to 43 countries.
- CN, JP, KR and IL excluded from share estimation (IL for the request budget; see Section 3).
- Approximate (`cardinality`) family counts.

## 8. Final report to the researcher

Summarise:
- the steps completed;
- requests and records used and left (from the headers);
- row counts of each output file;
- checks passed or failed;
- exact error messages;
- anything that needs the researcher's decision.
