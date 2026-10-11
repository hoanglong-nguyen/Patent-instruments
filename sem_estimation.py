"""
Simultaneous-equations model of income, ecological footprint and patenting (offline).

  (1) lnGDP = mu_i + d_t + a1 lnCAP + a2 HCI + a3 lnEF + a4 lnPAT + e1
  (2) lnEF  = mu_i + d_t + b1 lnGDP + b2 lnBIO + b3 URB + b4 lnPAT + e2
  (3) lnPAT = mu_i + d_t + c1 lnGDP + c2 lnEF + c3 lnZ + e3

Endogenous: lnGDP, lnEF, lnPAT. Exogenous: lnCAP, HCI, lnBIO, URB, lnZ (WIPO shift-share
instrument, mean over lags 1-10). Exclusions: (1) excludes lnBIO, URB, lnZ; (2) excludes lnCAP,
HCI, lnZ; (3) excludes lnCAP, HCI, lnBIO, URB. Each equation is over-identified.
Variants (SPECS): +AGE and +AGE+TRADE add regressors to (1) only, i.e. extra excluded
instruments for lnGDP in (2) and (3).

Estimators (same common sample for all equations, so FE-2SLS and 3SLS are comparable):
  * FE-2SLS equation by equation, country and year dummies, SE clustered by country;
    first-stage strength per endogenous regressor (Sanderson-Windmeijer F) and Hansen J (2-step
    GMM with clustered weight).
  * 3SLS on the full system with the same dummies; SE clustered by country.

Data (data/*.dta, supplied by the researcher; levels, logged here):
  GDP  WDI GDP per capita, constant 2015 US$        CAP  WDI gross capital formation, % of GDP
  HCI  PWT human capital index (level)              URB  WDI urban population, % of total
  EF   GFN ecological footprint of consumption per capita (gha); BIO  GFN biocapacity per capita
       (data/gfn_api.csv, National Footprint Accounts rows only, so the sample ends in 2022)
  PAT  WIPO applications filed abroad (wipo_pat_appl*.csv); lnPAT = ln(1 + PAT)
  Z    wipo_instrument*.csv; lnZ = ln(1 + Z)
  CTOT IMF commodity terms of trade (fetch_ctot.py -> data/imf/ctot.csv)

Usage:  python sem_estimation.py      (writes sem_results.csv and sem_diagnostics.csv)
"""
import warnings
import numpy as np
import pandas as pd
import pycountry
from scipy import stats
from linearmodels.iv import IV2SLS, IVGMM
from linearmodels.system import IV3SLS

warnings.filterwarnings("ignore")

def eqs(gdp_extra=()):
    """Equations as {name: (dependent, included exogenous, endogenous)}."""
    return {"(1) lnGDP": ("lnGDP", ["lnCAP", "HCI", *gdp_extra], ["lnEF", "lnPAT"]),
            "(2) lnEF": ("lnEF", ["lnBIO", "URB"], ["lnGDP", "lnPAT"]),
            "(3) lnPAT": ("lnPAT", ["lnZ"], ["lnGDP", "lnEF"])}

# Specifications: AGE (age dependency ratio) and lnTRADE (trade, % of GDP) enter the GDP
# equation only, so they are excluded instruments for lnGDP in (2) and (3). lnTRADE is reported
# with caution: openness may respond to the footprint (researcher's concern).
# lnCTOT: IMF commodity net export price index (Gruss and Kebhaj 2019), net exports / GDP weights,
# fixed weights (main); trade-weighted and rolling-weight versions as robustness. Common deflators
# (e.g. MUV) are absorbed by the year effects.
SPECS = {"base": eqs(), "+AGE": eqs(["AGE"]), "+AGE+TRADE": eqs(["AGE", "lnTRADE"]),
         "+CTOT": eqs(["lnCTOT"]), "+CTOT trade-wt": eqs(["lnCTOT_TT"]),
         "+CTOT rolling-wt": eqs(["lnCTOT_RW"])}
EQS = SPECS["base"]

def exog_all(eq):
    return list(dict.fromkeys(v for _, inc, _ in eq.values() for v in inc))

def iso2(c3):
    c = pycountry.countries.get(alpha_3=c3)
    return c.alpha_2 if c else None

def panel(tag="_aa"):
    k = dict(keep_default_na=False, na_values=[""])
    w = pd.read_csv(f"wipo_pat_appl{tag}.csv", **k).merge(
        pd.read_csv(f"wipo_instrument{tag}.csv", **k), on=["country", "year"])
    # GFN API export; keep National Footprint Accounts only (accounts == 1, i.e. up to 2022):
    # 2023-2025 rows are estimates, not accounts
    g = pd.read_csv("data/gfn_api.csv", keep_default_na=False, na_values=[""])
    g = g[(g.accounts == 1) & g.iso2.notna()].rename(columns={
        "iso2": "country", "EFConsPerCap": "ef", "BiocapPerCap": "bio"})[["country", "year", "ef", "bio"]]
    def by3(f, cols):
        x = pd.read_stata(f"data/{f}.dta")
        x["country"] = x.country_3d.map(iso2)
        return x[["country", "year"] + cols]
    d = (w.merge(g, on=["country", "year"], how="left")
          .merge(by3("wdi", ["gdp", "cap", "urb", "age", "trade"]), on=["country", "year"], how="left")
          .merge(by3("pwt", ["hci", "pop"]), on=["country", "year"], how="left")
          .merge(by3("income", ["inc_class"]), on=["country", "year"], how="left")
          .merge(pd.read_csv("data/imf/ctot.csv", keep_default_na=False, na_values=[""])
                 .drop(columns="country_3d"), on=["country", "year"], how="left"))
    d["lnGDP"], d["lnEF"], d["lnBIO"] = np.log(d.gdp), np.log(d.ef), np.log(d.bio)
    d["lnCAP"], d["HCI"], d["URB"] = np.log(d.cap.where(d.cap > 0)), d.hci, d.urb
    d["lnPAT"], d["lnZ"] = np.log1p(d.pat_abroad), np.log1p(d.z_mean_lag1_10)
    d["lnPATpc"] = np.log1p(d.pat_abroad / d["pop"])           # per million people (robustness)
    d["AGE"], d["lnTRADE"] = d.age, np.log(d.trade.where(d.trade > 0))
    d["lnCTOT"], d["lnCTOT_TT"], d["lnCTOT_RW"] = np.log(d.ctot_gdp_fw), np.log(d.ctot_tt_fw), np.log(d.ctot_gdp_rw)
    return d

def common(d, eq=EQS):
    v = ["lnGDP", "lnEF", "lnPAT"] + exog_all(eq)
    return d.dropna(subset=v).reset_index(drop=True)

def dummies(d):
    fe = pd.get_dummies(d[["country", "year"]].astype(str), drop_first=True, dtype=float)
    fe.insert(0, "const", 1.0)
    return fe

def sw_f(d, fe, y_endog, endog, excl, exog_inc):
    """Sanderson-Windmeijer conditional first-stage F for each endogenous regressor."""
    out = {}
    L, K = len(excl), len(endog)
    for j in endog:
        others = [e for e in endog if e != j]
        x = pd.concat([d[exog_inc], fe], axis=1)
        r = IV2SLS(d[j], x, d[others], d[excl]).fit(cov_type="unadjusted")
        resid = r.resids
        fs = IV2SLS(resid, pd.concat([d[exog_inc + excl], fe], axis=1), None, None).fit(
            cov_type="clustered", clusters=d.country)
        names = list(fs.params.index)
        R = np.zeros((L, len(names)))
        for i, v in enumerate(excl):
            R[i, names.index(v)] = 1.0
        out[j] = fs.wald_test(restriction=R, value=np.zeros(L)).stat / (L - K + 1)
    return out

def run(d, label, eq=EQS, spec="base"):
    d = common(d, eq)
    EXOG_ALL = exog_all(eq)
    fe = dummies(d)
    rows, diag = [], []
    for name, (y, inc, endog) in eq.items():
        excl = [v for v in EXOG_ALL if v not in inc]
        x = pd.concat([d[inc], fe], axis=1)
        r = IV2SLS(d[y], x, d[endog], d[excl]).fit(cov_type="clustered", clusters=d.country)
        g = IVGMM(d[y], x, d[endog], d[excl]).fit(cov_type="clustered", clusters=d.country)
        for v in inc + endog:
            rows.append({"spec": spec, "sample": label, "method": "FE-2SLS", "equation": name, "var": v,
                         "coef": r.params[v], "se": r.std_errors[v], "p": r.pvalues[v]})
        sw = sw_f(d, fe, y, endog, excl, inc)
        diag.append({"spec": spec, "sample": label, "equation": name, "obs": r.nobs,
                     "countries": d.country.nunique(),
                     **{f"SW_F_{k}": v for k, v in sw.items()},
                     "hansen_J": g.j_stat.stat, "J_p": g.j_stat.pval, "J_df": len(excl) - len(endog)})
    eqs = {}
    for name, (y, inc, endog) in eq.items():
        excl = [v for v in EXOG_ALL if v not in inc]
        eqs[name] = {"dependent": d[y], "exog": pd.concat([d[inc], fe], axis=1),
                     "endog": d[endog], "instruments": d[excl]}
    s = IV3SLS(eqs).fit(cov_type="clustered", clusters=d.country.astype("category").cat.codes)
    for name, (y, inc, endog) in eq.items():
        for v in inc + endog:
            k = f"{name}_{v}"
            rows.append({"spec": spec, "sample": label, "method": "3SLS", "equation": name, "var": v,
                         "coef": s.params[k], "se": s.std_errors[k], "p": s.pvalues[k]})
    return rows, diag

def samples(d):
    from wipo_shift_share import ORIGIN, REGIONAL
    shared = set(REGIONAL["OA"]) | set(REGIONAL["AP"]) | set(REGIONAL["EP"])
    base = d[~d.country.isin(["CN", "JP", "KR"])]
    high = set(d[d.inc_class == "H"].country)                    # high income in any year
    return {"main: Asia-Africa, no CN/JP/KR": base,
            "no thin shares": base[base.inflow_90_99 >= 100],
            "no thin, no shared office": base[(base.inflow_90_99 >= 100) & ~base.country.isin(shared)],
            "no high-income": base[~base.country.isin(high)],
            "43-country list": base[base.country.isin(ORIGIN)]}

def main():
    d = panel()
    rows, diag = [], []
    for spec, eq in SPECS.items():
        for label, s in samples(d).items():
            r, g = run(s, label, eq, spec)
            rows += r
            diag += g
    pd.DataFrame(rows).to_csv("sem_results.csv", index=False)
    pd.DataFrame(diag).to_csv("sem_diagnostics.csv", index=False)

if __name__ == "__main__":
    main()
