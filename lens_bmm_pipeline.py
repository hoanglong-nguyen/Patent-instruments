"""
Lens.org pipeline: country-level patent-family counts and a BMM-style shift-share instrument
43 Asian and African origin countries, 2000-2023.

Design decisions (11 October 2026):
  * Country assignment: applicant residence (full counting of multi-country families).
  * Counting unit: simple families, dated by earliest priority year.
  * Block A (counts, all countries, 1980-2023): Patent Aggregation API (cardinality, approximate, ~1%).
  * Block B (citing records, priority 1990-1999): origin countries EXCLUDING CN, JP, KR.
  * Block C (cited records): only cited documents with earliest priority 1980-1998 (filtered server-side,
    so out-of-window citations cost no record allowance).

Limits observed on the trial (check headers before running):
  Search API:      1,000 requests / month, 100,000 records / month, 10 requests / minute.
  Aggregation API: 1,000 requests / month, 5 requests / minute, max 2 nested aggregations,
                   and no aggregation over more than 10,000,000 matching documents.
  Trials expire 25 October 2026; the monthly quota resets only on 10 November 2026,
  so Blocks B + C must fit in one run of about 99,900 records.

Usage:  export LENS_TOKEN=...   (never hard-code the token)
        python lens_bmm_pipeline.py counts      # Block A
        python lens_bmm_pipeline.py check       # size-0 volume check for B (no records used)
        python lens_bmm_pipeline.py blockB
        python lens_bmm_pipeline.py checkC      # size-0 volume check for C (no records used)
        python lens_bmm_pipeline.py blockC
        python lens_bmm_pipeline.py build       # shares + instrument (offline)
"""
import os, sys, json, time
import requests
import pandas as pd

TOKEN = os.environ["LENS_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SEARCH = "https://api.lens.org/patent/search"
AGG = "https://api.lens.org/patent/aggregate"
PACE = {SEARCH: 6.5, AGG: 12.5}          # seconds between calls (10/min and 5/min)

ORIGIN = ["BJ", "BF", "BD", "BW", "CF", "CN", "CI", "CM", "CD", "CG", "EG", "ET", "GH", "ID", "IN",
          "IQ", "IL", "JP", "KE", "KH", "KR", "MG", "ML", "MN", "MZ", "MU", "MY", "NE", "NP", "PK",
          "PH", "RW", "SN", "SL", "TG", "TH", "TJ", "TN", "TZ", "UG", "VN", "ZA", "ZW"]
BLOCKB_EXCLUDE = {"CN", "JP", "KR"}
BLOCKB_ORIGIN = [c for c in ORIGIN if c not in BLOCKB_EXCLUDE]

try:                                      # all ISO-2 codes as destinations
    import pycountry
    ALL_COUNTRIES = sorted(c.alpha_2 for c in pycountry.countries)
except ImportError:
    sys.exit("pip install pycountry")

RECORD_RESERVE = 500                      # keep a small safety margin of the record allowance
FIELDS = ["lens_id", "jurisdiction", "biblio.application_reference", "biblio.priority_claims",
          "biblio.parties.applicants", "biblio.references_cited", "families.simple_family"]
FIELDS_C = ["lens_id", "biblio.application_reference", "biblio.priority_claims",
            "biblio.parties.applicants", "families.simple_family"]   # no citations needed for C

_last_call = {}
LIMITS = {}

def post(url, body):
    """POST with pacing, 429 back-off and capture of the rate-limit headers."""
    while True:
        wait = PACE[url] - (time.time() - _last_call.get(url, 0))
        if wait > 0:
            time.sleep(wait)
        r = requests.post(url, headers=H, json=body, timeout=120)
        _last_call[url] = time.time()
        for k, v in r.headers.items():
            if k.lower().startswith("x-rate-limit-"):
                LIMITS[k.lower()] = v
        if r.status_code == 429:
            time.sleep(int(r.headers.get("x-rate-limit-retry-after-seconds", 60)) + 1)
            continue
        return r

def records_left():
    return int(LIMITS.get("x-rate-limit-remaining-record-per-month", 0))

def read_counts(path="lens_family_counts.csv"):
    # keep_default_na=False: otherwise pandas reads Namibia's code "NA" as missing
    return pd.read_csv(path, keep_default_na=False, na_values=[""])

def ok(r):
    """Stop with the exact API error message (raise_for_status drops the response body)."""
    if r.status_code != 200:
        sys.exit(f"HTTP {r.status_code} from {r.url}: {r.text}")
    return r

def prio(gte, lte):
    return {"range": {"earliest_priority_claim_date": {"gte": gte, "lte": lte}}}

# --------------------------------------------------------------------------------------
# Block A: family counts by applicant country x priority year, 1980-2023 (Aggregation API)
# --------------------------------------------------------------------------------------
def agg_years(cc, y0, y1):
    """Return {year: (docs, families)}; splits the period if >10M documents match."""
    f = [prio(f"{y0}-01-01", f"{y1}-12-31")]
    if cc:
        f.append({"term": {"applicant.residence": cc}})
    body = {"query": {"bool": {"filter": f}}, "size": 0,
            "aggregations": {"by_year": {"date_histogram": {
                "field": "earliest_priority_claim_date", "interval": "YEAR",
                "aggregations": {"families": {"cardinality": {"field": "family.simple.id"}}}}}}}
    r = post(AGG, body)
    if r.status_code == 400 and "10000000" in r.text and y1 > y0:
        mid = (y0 + y1) // 2
        out = agg_years(cc, y0, mid)
        out.update(agg_years(cc, mid + 1, y1))
        return out
    ok(r)
    by_year = (r.json().get("aggregations") or {}).get("by_year") or {}
    # Lens returns {"2010": {"doc_count": 64, "families": 30}, ...}
    return {int(y): (v["doc_count"], v["families"]) for y, v in by_year.items()}

def block_A(path="lens_family_counts.csv"):
    done = set(read_counts(path)["country"]) if os.path.exists(path) else set()
    for cc in ALL_COUNTRIES + [None]:
        name = cc or "WORLD"
        if name in done:
            continue
        rows = [{"country": name, "year": y, "docs": d, "families": f}
                for y, (d, f) in sorted(agg_years(cc, 1980, 2023).items())]
        if not rows:
            rows = [{"country": name, "year": None, "docs": 0, "families": 0}]
        pd.DataFrame(rows).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
        print(name, sum(r["families"] for r in rows), "families;",
              LIMITS.get("x-rate-limit-remaining-request-per-month"), "agg requests left")

# --------------------------------------------------------------------------------------
# Search helpers
# --------------------------------------------------------------------------------------
def count(query):
    r = post(SEARCH, {"query": query, "size": 0})
    ok(r)
    return r.json()["total"]

PAGE = None
def page_size():
    """Largest page the plan accepts; tested once on a tiny query (costs <= ~100 records)."""
    global PAGE
    if PAGE:
        return PAGE
    for s in (1000, 500, 250, 100):
        r = post(SEARCH, {"query": {"bool": {"filter": [{"term": {"applicant.residence": "BJ"}},
                                                         prio("1990-01-01", "1999-12-31")]}},
                          "include": ["lens_id"], "size": s, "scroll": "1m"})
        if r.status_code == 200:
            PAGE = s
            print("page size", s)
            return s
    sys.exit("No page size accepted: " + r.text)

def scroll(query, path, fields):
    body = {"query": query, "include": fields, "size": page_size(), "scroll": "1m"}
    n = 0
    with open(path, "a") as f:
        while True:
            r = post(SEARCH, body)
            if r.status_code in (204, 404):
                break
            ok(r)
            d = r.json()
            if not d.get("data"):
                break
            for rec in d["data"]:
                f.write(json.dumps(rec) + "\n")
            n += len(d["data"])
            body = {"scroll_id": d["scroll_id"], "scroll": "1m"}
    return n

def q_B(y):
    return {"bool": {"filter": [{"terms": {"applicant.residence": BLOCKB_ORIGIN}},
                                prio(f"{y}-01-01", f"{y}-12-31")]}}

# --------------------------------------------------------------------------------------
# Block B: citing records (origin minus CN/JP/KR), priority 1990-1999
# --------------------------------------------------------------------------------------
def check_B():
    tot = {y: count(q_B(y)) for y in range(1990, 2000)}
    print(tot, "total", sum(tot.values()), "| records left", records_left())
    return sum(tot.values())

def block_B(path="block_B.jsonl"):
    need = check_B()
    if need > records_left() - RECORD_RESERVE:
        sys.exit("Block B exceeds the remaining record allowance; stop.")
    for y in range(1990, 2000):
        print(y, scroll(q_B(y), path, FIELDS), "records")

# --------------------------------------------------------------------------------------
# Block C: cited documents, restricted server-side to priority 1980-1998
# --------------------------------------------------------------------------------------
def cited_ids(path="block_B.jsonl"):
    ids = set()
    for line in open(path):
        r = json.loads(line)
        for c in r.get("biblio", {}).get("references_cited", {}).get("citations", []):
            lid = (c.get("patcit") or {}).get("lens_id")
            if lid:
                ids.add(lid)
    return sorted(ids)

def q_C(chunk):
    return {"bool": {"filter": [{"terms": {"lens_id": chunk}}, prio("1980-01-01", "1998-12-31")]}}

def chunks(ids, k=10000):                  # Lens: <= 10,000 values per terms query
    return [ids[i:i + k] for i in range(0, len(ids), k)]

def check_C():
    ids = cited_ids()
    n = sum(count(q_C(ch)) for ch in chunks(ids))
    print(len(ids), "distinct cited docs;", n, "in priority window | records left", records_left())
    return n

def block_C(path="block_C.jsonl"):
    need = check_C()
    if need > records_left() - RECORD_RESERVE:
        sys.exit("Block C exceeds the remaining record allowance. Options: drop IL from Block B, "
                 "or narrow the citation-lag window.")
    for ch in chunks(cited_ids()):
        print(scroll(q_C(ch), path, FIELDS_C), "records")

# --------------------------------------------------------------------------------------
# Build: family-level shares and the single-step shift-share instrument
# --------------------------------------------------------------------------------------
def fam_info(path):
    out = {}
    for line in open(path):
        r = json.loads(line)
        b = r.get("biblio", {})
        sf = r.get("families", {}).get("simple_family", {})
        # Lens has no family_id field: use the smallest member lens_id as the family key
        key = min([m["lens_id"] for m in sf.get("members", [])] + [r["lens_id"]])
        date = ((b.get("priority_claims") or {}).get("earliest_claim") or {}).get("date") \
            or (b.get("application_reference") or {}).get("date")
        ctry = [a["residence"] for a in (b.get("parties") or {}).get("applicants", []) if a.get("residence")]
        refs = {c["patcit"]["lens_id"] for c in (b.get("references_cited") or {}).get("citations", [])
                if (c.get("patcit") or {}).get("lens_id")}
        info = out.setdefault(key, {"year": None, "countries": [], "refs": set(), "docs": set()})
        info["docs"].add(r["lens_id"])
        info["refs"] |= refs
        if date and (info["year"] is None or int(date[:4]) < info["year"]):
            info["year"] = int(date[:4])
        if ctry and not info["countries"]:
            info["countries"] = ctry
    return out

def build():
    N = read_counts().dropna(subset=["year"])
    N["year"] = N["year"].astype(int)
    Ni = N.set_index(["country", "year"])["families"]

    citing, cited_f = fam_info("block_B.jsonl"), fam_info("block_C.jsonl")
    doc2fam = {d: k for k, v in cited_f.items() for d in v["docs"]}

    num = {}
    for f in citing.values():
        t = f["year"]
        cfams = {doc2fam[d] for d in f["refs"] if d in doc2fam}
        if not t or not f["countries"] or not cfams:
            continue
        for co in set(f["countries"]) & set(BLOCKB_ORIGIN):
            w_o = f["countries"].count(co) / len(f["countries"])
            for cf in cfams:
                g = cited_f[cf]
                if not g["year"] or not g["countries"]:
                    continue
                lag = t - g["year"]
                if not 1 <= lag <= 10:
                    continue
                for cd in set(g["countries"]):
                    if cd == co:
                        continue                      # own-country links set to 0
                    w_d = g["countries"].count(cd) / len(g["countries"])
                    num[(co, cd, lag)] = num.get((co, cd, lag), 0) + w_o * w_d / len(cfams)

    m = {}
    for (co, cd, lag), v in num.items():
        den = sum(Ni.get((cd, t - lag), 0) for t in range(1990, 2000))
        if den > 0:
            m[(co, cd, lag)] = v / den
    pd.DataFrame([{"origin": k[0], "dest": k[1], "lag": k[2], "share": v} for k, v in m.items()]) \
        .to_csv("shares.csv", index=False)

    pred = []
    for co in ORIGIN:
        for t in range(2000, 2024):
            val = None
            if co in BLOCKB_ORIGIN:   # CN, JP, KR have no estimated shares -> instrument missing
                val = sum(s * Ni.get((cd, t - lag), 0) for (o, cd, lag), s in m.items() if o == co)
            pred.append({"country": co, "year": t, "pat_appl_hat": val})
    pd.DataFrame(pred).to_csv("shift_share_instrument.csv", index=False)

    grid = pd.MultiIndex.from_product([ORIGIN, range(2000, 2024)], names=["country", "year"])
    pat = Ni.reindex(grid, fill_value=0).rename("pat_appl").reset_index()
    pat.to_csv("pat_appl.csv", index=False)

    world = N[N.country == "WORLD"].set_index("year")["families"]
    summed = N[N.country != "WORLD"].groupby("year")["families"].sum()
    # Full counting means summed >= world; report the ratio, not a 'missing residence' residual.
    pd.DataFrame({"world": world, "sum_countries": summed}).to_csv("coverage_check.csv")

if __name__ == "__main__":
    {"counts": block_A, "check": check_B, "blockB": block_B,
     "checkC": check_C, "blockC": block_C, "build": build}[sys.argv[1]]()
    print("limits:", LIMITS)
