# Lens.org patent extraction: BMM-style innovation proxy and shift-share instrument

Guideline for Claude Code. Read this whole file before acting. The pipeline script is
`lens_bmm_pipeline.py` in this folder.

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
| Shares | Citation lags 1–10 years; own-country links = 0 |
| Shifts | Actual lagged family counts of other countries (single step, not BMM's recursive prediction) |

**Consequence:** CN, JP and KR have no estimated shares, so their instrument is empty (`None`). They remain in `pat_appl` and in Block A.

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
5. **`python lens_bmm_pipeline.py blockC`.** Not resumable (same rule as step 3).
6. **`python lens_bmm_pipeline.py build`** (offline). Output files:
   - `pat_appl.csv`;
   - `shares.csv`;
   - `shift_share_instrument.csv`;
   - `coverage_check.csv`.

Steps 1–5 must finish before 25 October 2026.

## 6. Checks before reporting results

- `pat_appl.csv`: 43 countries × 24 years. CD, ET and KH may have zeros.
- Instrument: non-missing for the 40 Block-B origins, empty for CN, JP and KR.
- Flag implausible counts for manual review: TJ (925 documents in 1990–1999) and SL (70) look like residence-coding artefacts.
- `coverage_check.csv`: with full counting, the sum of the country counts can exceed the world total. Report the ratio; do not treat the difference as "missing residence".
- Families with priority 2022–2023 may still grow in later data.

## 7. Deviations from BMM to disclose in the paper

- Applicant residence instead of inventor residence.
- Full counting of multi-country families.
- Single-step shift-share using actual lagged foreign counts, not recursive prediction.
- Origin network limited to 43 countries.
- CN, JP and KR excluded from share estimation.
- Approximate (`cardinality`) family counts.

## 8. Final report to the researcher

Summarise:
- the steps completed;
- requests and records used and left (from the headers);
- row counts of each output file;
- checks passed or failed;
- exact error messages;
- anything that needs the researcher's decision.
