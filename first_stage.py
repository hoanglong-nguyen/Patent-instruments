"""
First-stage diagnostics for the WIPO shift-share instrument (offline).

Regresses the outcome (pat_abroad) on the instrument with country and year fixed effects,
standard errors clustered by country. Main instrument: mean over lags 1-10; lag 1 and lag 5
as robustness. Three samples:
  (i)   all origins with an instrument (40);
  (ii)  excluding thin shares (< 100 foreign filings into the origin's offices, 1990-1999);
  (iii) (ii) and also excluding OAPI and ARIPO members (shared regional offices).
Each sample is run with and without CN, JP and KR: they account for 93% of pat_abroad, so they
dominate PPML (which weights by levels), and they were outside the original share design.
Two specifications: OLS on log(1 + y) with log(1 + Z), and PPML on y with log(1 + Z).
F = squared cluster-robust t-statistic (single instrument).

Usage:  python first_stage.py      (reads wipo_*.csv; writes first_stage_results.csv)
"""
import numpy as np
import pandas as pd
import pyfixest as pf

from wipo_shift_share import REGIONAL

THIN = 100
INSTR = {"mean lags 1-10": "z_mean_lag1_10", "lag 1": "z_lag1", "lag 5": "z_lag5"}

def data():
    k = dict(keep_default_na=False, na_values=[""])
    y = pd.read_csv("wipo_pat_appl.csv", **k)
    z = pd.read_csv("wipo_instrument.csv", **k)
    d = y.merge(z, on=["country", "year"]).dropna(subset=["z_mean_lag1_10"])
    d["ly"] = np.log1p(d.pat_abroad)
    for v in INSTR.values():
        d["l" + v] = np.log1p(d[v])
    return d

def samples(d):
    shared = set(REGIONAL["OA"]) | set(REGIONAL["AP"])
    ii = d[d.inflow_90_99 >= THIN]
    base = {"(i) all": d, "(ii) no thin shares": ii,
            "(iii) no thin, no OAPI/ARIPO": ii[~ii.country.isin(shared)]}
    out = {}
    for k, v in base.items():
        out[k] = v
        out[k + ", no CN/JP/KR"] = v[~v.country.isin(["CN", "JP", "KR"])]
    return out

def main():
    d = data()
    rows = []
    for sname, s in samples(d).items():
        for iname, v in INSTR.items():
            for spec in ("OLS log", "PPML"):
                if spec == "OLS log":
                    m = pf.feols(f"ly ~ l{v} | country + year", data=s, vcov={"CRV1": "country"})
                else:
                    m = pf.fepois(f"pat_abroad ~ l{v} | country + year", data=s,
                                  vcov={"CRV1": "country"})
                t = m.tstat().iloc[0]
                rows.append({"sample": sname, "instrument": iname, "spec": spec,
                             "countries": s.country.nunique(), "obs": m._N,
                             "coef": m.coef().iloc[0], "se": m.se().iloc[0], "t": t, "F": t ** 2})
    r = pd.DataFrame(rows)
    r.to_csv("first_stage_results.csv", index=False)
    with pd.option_context("display.width", 140, "display.float_format", "{:.3f}".format):
        print(r.to_string(index=False))

if __name__ == "__main__":
    main()
