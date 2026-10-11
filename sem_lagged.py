"""
Lagged-feedback simultaneous system (offline), estimated by FE-2SLS and 3SLS.

  (1) lnGDP_t = mu_i + d_t + a1 lnCAP_t + a2 HCI_t + a3 lnEF_{t-1} + a4 lnPAT_t + e1
  (2) lnEF_t  = mu_i + d_t + b1 lnGDP_{t-1} + b2 lnBIO_t + b3 URB_t + b4 lnPAT_t + e2
  (3) lnPAT_t = mu_i + d_t + c1 lnGDP_{t-1} + c2 lnEF_{t-1} + c3 lnZ_t + e3

Lagged GDP and EF are treated as predetermined; lnPAT is the only contemporaneous endogenous
regressor. Its instruments are chosen per equation (never a lag of the equation's own dependent
variable, which would be invalid under serially correlated errors):
  * "just-identified": lnZ only. With every equation exactly identified, 3SLS point estimates
    equal FE-2SLS; 3SLS still uses the cross-equation error covariance for inference.
  * "over-identified": lnZ plus the other equation's exogenous regressors ((1): lnBIO, URB;
    (2): lnCAP, HCI), so 3SLS can differ from 2SLS; Hansen J tests the extra exclusions.
Diagnostics: first-stage F for lnZ (and the full excluded set), Hansen J, Wooldridge serial-
correlation test (first-differenced residuals; coefficient -0.5 under no AR(1)), and
Anderson-Rubin 95% confidence sets for the lnPAT coefficient in (1) and (2).
Country and year dummies; SE clustered by country.

Usage:  python sem_lagged.py      (writes sem_lagged_results.csv, sem_lagged_diagnostics.csv)
"""
import warnings
import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS, IVGMM
from linearmodels.system import IV3SLS

from sem_estimation import panel, samples, dummies

warnings.filterwarnings("ignore")

EQS = {"(1) lnGDP": ("lnGDP", ["lnCAP", "HCI", "lnEF_L1"]),
       "(2) lnEF": ("lnEF", ["lnBIO", "URB", "lnGDP_L1"]),
       "(3) lnPAT": ("lnPAT", ["lnGDP_L1", "lnEF_L1", "lnZ"])}
ENDOG = {"(1) lnGDP": ["lnPAT"], "(2) lnEF": ["lnPAT"], "(3) lnPAT": []}
INSTR = {"just-identified": {"(1) lnGDP": ["lnZ"], "(2) lnEF": ["lnZ"]},
         "over-identified": {"(1) lnGDP": ["lnZ", "lnBIO", "URB"],
                             "(2) lnEF": ["lnZ", "lnCAP", "HCI"]}}
VARS = ["lnGDP", "lnEF", "lnPAT", "lnCAP", "HCI", "lnBIO", "URB", "lnZ", "lnGDP_L1", "lnEF_L1"]

def add_lags(d):
    d = d.sort_values(["country", "year"]).copy()
    prev = d[["country", "year", "lnGDP", "lnEF"]].assign(year=d.year + 1)
    return d.merge(prev.rename(columns={"lnGDP": "lnGDP_L1", "lnEF": "lnEF_L1"}),
                   on=["country", "year"], how="left")

def clustered_wald(y, X, names, groups):
    r = IV2SLS(y, X, None, None).fit(cov_type="clustered", clusters=groups)
    cols = list(r.params.index)
    R = np.zeros((len(names), len(cols)))
    for i, v in enumerate(names):
        R[i, cols.index(v)] = 1.0
    return r.wald_test(restriction=R, value=np.zeros(len(names)))

def first_stage_F(d, fe, inc, instr):
    X = pd.concat([d[inc + instr], fe], axis=1)
    w = clustered_wald(d["lnPAT"], X, instr, d.country)
    return w.stat / len(instr)

def anderson_rubin(d, fe, y, inc, instr, grid=np.linspace(-3, 3, 601)):
    """95% AR confidence set for the lnPAT coefficient (union of accepted grid points)."""
    X = pd.concat([d[inc + instr], fe], axis=1)
    ok = [b for b in grid if clustered_wald(d[y] - b * d["lnPAT"], X, instr, d.country).pval > 0.05]
    if not ok:
        return "empty on grid"
    edge = " (open: reaches grid edge)" if ok[0] == grid[0] or ok[-1] == grid[-1] else ""
    gaps = np.any(np.diff(ok) > (grid[1] - grid[0]) * 1.5)
    return f"[{ok[0]:.2f}, {ok[-1]:.2f}]" + (" with gaps" if gaps else "") + edge

def wooldridge_ar1(d, resid):
    """Regress de_t on de_{t-1} (first-differenced residuals); H0 coefficient = -0.5."""
    e = d[["country", "year"]].assign(e=resid.values).sort_values(["country", "year"])
    e["de"] = e.groupby("country").e.diff()
    e["de_l"] = e.groupby("country").de.shift()
    e = e.dropna()
    r = IV2SLS(e.de, e[["de_l"]], None, None).fit(cov_type="clustered", clusters=e.country)
    t = (r.params["de_l"] + 0.5) / r.std_errors["de_l"]
    return r.params["de_l"], 2 * (1 - __import__("scipy").stats.norm.cdf(abs(t)))

def run(d, label, iname):
    d = add_lags(d).dropna(subset=VARS).reset_index(drop=True)
    fe = dummies(d)
    rows, diag, eqs = [], [], {}
    for name, (y, inc) in EQS.items():
        endog, instr = ENDOG[name], INSTR[iname].get(name, [])
        x = pd.concat([d[inc], fe], axis=1)
        r = IV2SLS(d[y], x, d[endog] if endog else None, d[instr] if endog else None).fit(
            cov_type="clustered", clusters=d.country)
        for v in inc + endog:
            rows.append({"instruments": iname, "sample": label, "method": "FE-2SLS", "equation": name,
                         "var": v, "coef": r.params[v], "se": r.std_errors[v], "p": r.pvalues[v]})
        rho, rho_p = wooldridge_ar1(d, r.resids)
        dg = {"instruments": iname, "sample": label, "equation": name, "obs": r.nobs,
              "countries": d.country.nunique(), "years": f"{d.year.min()}-{d.year.max()}",
              "AR1_coef": rho, "AR1_p(H0:-0.5)": rho_p}
        if endog:
            dg["F_lnZ"] = first_stage_F(d, fe, inc, ["lnZ"])
            dg["F_all_instr"] = first_stage_F(d, fe, inc, instr)
            if len(instr) > 1:
                g = IVGMM(d[y], x, d[endog], d[instr]).fit(cov_type="clustered", clusters=d.country)
                dg["hansen_J_p"] = g.j_stat.pval
            dg["AR_95_lnPAT"] = anderson_rubin(d, fe, y, inc, instr)
        diag.append(dg)
        eqs[name] = {"dependent": d[y], "exog": x,
                     "endog": d[endog] if endog else None, "instruments": d[instr] if endog else None}
    s = IV3SLS(eqs).fit(cov_type="clustered", clusters=d.country.astype("category").cat.codes)
    for name, (y, inc) in EQS.items():
        for v in inc + ENDOG[name]:
            k = f"{name}_{v}"
            rows.append({"instruments": iname, "sample": label, "method": "3SLS", "equation": name,
                         "var": v, "coef": s.params[k], "se": s.std_errors[k], "p": s.pvalues[k]})
    return rows, diag

def main():
    d = panel()
    rows, diag = [], []
    for iname in INSTR:
        for label, s in samples(d).items():
            r, g = run(s, label, iname)
            rows += r
            diag += g
    pd.DataFrame(rows).to_csv("sem_lagged_results.csv", index=False)
    pd.DataFrame(diag).to_csv("sem_lagged_diagnostics.csv", index=False)

if __name__ == "__main__":
    main()
