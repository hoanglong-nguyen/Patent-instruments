"""
WIPO-only outcome and shift-share instrument for 43 Asian and African origin countries, 2000-2023.

Replaces the Lens design (approved 11 October 2026): Lens applicant residence is missing for most
national filings, so Lens counts diverge from WIPO even in trend (e.g. CN, JP, ID, KE).

Input:  wipo_patent_office_origin.csv - WIPO IP Statistics Data Center, indicator 1 "Total patent
        applications (direct and PCT national phase entries)", by filing office x applicant origin,
        1980-2023 (last updated May 2026). Blank cells = not reported (or zero) for that office-year.

Definitions (follow WIPO's resident / abroad split):
  * Offices acting for country c: its national office plus the regional offices it belongs to
    (OAPI "OA", ARIPO "AP", Eurasian "EA"; current membership).
  * Abroad filings A_{c,t}: applications by origin c at all offices NOT acting for c.
    This is the outcome (option a): destination offices report consistently, whereas many
    African home offices report in only a few years.
  * Inflow F_{o,d}: applications by origin d at offices acting for o, 1990-1999 (d != o).
  * Share s_{o,d} = F_{o,d} / sum_{t=1990..1999} A_{d,t}: the share of d's foreign patenting
    directed at o's market in the pre-period.
  * Shift: A^{-o}_{d,t} = d's abroad filings excluding those at offices acting for o (leave-out).
  * Instrument Z_{o,t} = sum_{d != o} s_{o,d} * A^{-o}_{d,t-lag}: predicted foreign filings into o.
    Reported for lag 1, lag 5 and the mean over lags 1-10.

Usage:  python wipo_shift_share.py      (offline; writes wipo_*.csv)
"""
import warnings
import pandas as pd
import pycountry

SRC = "wipo_patent_office_origin.csv"
ORIGIN = ["BJ", "BF", "BD", "BW", "CF", "CN", "CI", "CM", "CD", "CG", "EG", "ET", "GH", "ID", "IN",
          "IQ", "IL", "JP", "KE", "KH", "KR", "MG", "ML", "MN", "MZ", "MU", "MY", "NE", "NP", "PK",
          "PH", "RW", "SN", "SL", "TG", "TH", "TJ", "TN", "TZ", "UG", "VN", "ZA", "ZW"]
REGIONAL = {"OA": ["BJ", "BF", "CF", "CI", "CM", "CG", "ML", "NE", "SN", "TG", "GA", "GN", "GW", "GQ",
                   "KM", "MR", "TD"],
            "AP": ["BW", "CV", "SZ", "GM", "GH", "KE", "LS", "LR", "MW", "MZ", "NA", "RW", "ST", "SC",
                   "SL", "SO", "SD", "TZ", "UG", "ZM", "ZW"],
            "EA": ["AM", "AZ", "BY", "KZ", "KG", "RU", "TJ", "TM"]}
PRE = range(1990, 2000)
YEARS = range(2000, 2024)
LAGS = range(1, 11)

# WIPO names that pycountry does not resolve (or resolves wrongly); historical entities keep codes
FIX = {"Republic of Korea": "KR", "Democratic People's Republic of Korea": "KP",
       "Democratic Republic of the Congo": "CD", "Zaire": "CD", "Bolivia (Plurinational State of)": "BO",
       "China, Hong Kong SAR": "HK", "China, Macao SAR": "MO", "Iran (Islamic Republic of)": "IR",
       "Micronesia (Federated States of)": "FM", "Netherlands (Kingdom of the)": "NL",
       "Venezuela (Bolivarian Republic of)": "VE", "Czechoslovakia": "CS",
       "German Democratic Republic": "DD", "Soviet Union": "SU", "Yugoslavia": "YU",
       "Netherlands Antilles": "AN", "Unknown": None}

def iso(name):
    if name in FIX:
        return FIX[name]
    try:
        return pycountry.countries.lookup(name).alpha_2
    except LookupError:
        return pycountry.countries.search_fuzzy(name)[0].alpha_2

def load(path=SRC):
    with warnings.catch_warnings():           # rows end with a trailing comma
        warnings.simplefilter("ignore")
        w = pd.read_csv(path, skiprows=6, dtype=str, keep_default_na=False, index_col=False)
    yrs = [c for c in w.columns if c.isdigit()]
    w["office"] = w["Office (Code)"].replace({"ZR": "CD"})
    w["origin"] = w["Origin"].map(iso)
    d = w.melt(id_vars=["office", "origin"], value_vars=yrs, var_name="year", value_name="n")
    d = d[(d.n != "") & d.origin.notna()]
    d["year"] = d.year.astype(int)
    d["n"] = d.n.str.replace(",", "").astype(float)
    return d.groupby(["office", "origin", "year"], as_index=False).n.sum()

def acting(c):
    """Offices acting for country c: national office plus regional offices it belongs to."""
    return {c} | {r for r, members in REGIONAL.items() if c in members}

def main():
    d = load()
    d["abroad"] = [o not in acting(c) for o, c in zip(d.office, d.origin)]
    A = d[d.abroad].groupby(["origin", "year"]).n.sum()             # abroad filings by origin-year
    T = d.groupby(["origin", "year"]).n.sum()                       # WIPO total by origin-year
    reported = set(zip(d.office, d.year))                           # office-years with any data
    Ad = A.to_dict()

    # Outcome (option a), with the WIPO total and a home-office reporting flag for robustness
    out = []
    for c in ORIGIN:
        for t in YEARS:
            out.append({"country": c, "year": t, "pat_abroad": A.get((c, t), 0.0),
                        "pat_total_wipo": T.get((c, t), 0.0),
                        "home_office_reported": int(any((o, t) in reported for o in acting(c)))})
    pd.DataFrame(out).to_csv("wipo_pat_appl.csv", index=False)

    # Shares from 1990-1999 inflows into offices acting for o
    pre = d[d.year.isin(PRE)]
    A_pre = A[A.index.get_level_values("year").isin(PRE)].groupby("origin").sum()
    shares, inst = [], []
    for o in ORIGIN:
        offs = acting(o)
        # abroad filings only: a co-member's filing at a shared regional office is resident for it
        F = pre[pre.office.isin(offs) & (pre.origin != o) & pre.abroad].groupby("origin").n.sum()
        yrs_rep = sum(any((x, t) in reported for x in offs) for t in PRE)
        s = {dd: f / A_pre[dd] for dd, f in F.items() if f > 0 and A_pre.get(dd, 0) > 0}
        for dd, v in s.items():
            shares.append({"origin": o, "dest": dd, "inflow_90_99": F[dd],
                           "dest_abroad_90_99": A_pre[dd], "share": v})
        # leave-out shift: d's abroad filings minus those at offices acting for o
        into_o = d[d.office.isin(offs) & d.abroad].groupby(["origin", "year"]).n.sum().to_dict()
        def shift(dd, t):
            return Ad.get((dd, t), 0.0) - into_o.get((dd, t), 0.0)
        for t in YEARS:
            z = {lag: sum(v * shift(dd, t - lag) for dd, v in s.items()) if s else None for lag in LAGS}
            inst.append({"country": o, "year": t, "z_lag1": z[1], "z_lag5": z[5],
                         "z_mean_lag1_10": (sum(z.values()) / len(LAGS)) if s else None,
                         "inflow_90_99": float(F.sum()), "n_source_countries": len(s),
                         "office_years_reported_90_99": yrs_rep,
                         "shared_regional_office": "OA" if "OA" in offs else ""})
    pd.DataFrame(shares).to_csv("wipo_shares.csv", index=False)
    pd.DataFrame(inst).to_csv("wipo_instrument.csv", index=False)

if __name__ == "__main__":
    main()
