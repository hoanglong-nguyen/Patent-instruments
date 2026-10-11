"""Shared helpers for the R2 revision analyses (Python replication of the Stata do-file)."""
import warnings
import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS
from linearmodels.system import IV3SLS
warnings.filterwarnings("ignore")

def load(path="revision_R2/analysis_replica.csv"):
    return pd.read_csv(path, keep_default_na=False, na_values=[""])

def fe(d):
    x = pd.get_dummies(d[["country_2d", "year"]].astype(str), drop_first=True, dtype=float)
    x.insert(0, "const", 1.0)
    return x

def reg3(d, eqs, extra_exog=(), cov="unadjusted", clusters=None):
    """Emulates Stata reg3: every exogenous variable of the system (plus extra_exog) is an
    instrument in every equation. eqs = {name: (dep, [exog], [endog])}."""
    d = d.reset_index(drop=True)
    F = fe(d)
    sys_exog = list(dict.fromkeys([v for _, ex, _ in eqs.values() for v in ex] + list(extra_exog)))
    spec = {}
    for name, (y, ex, en) in eqs.items():
        ins = [v for v in sys_exog if v not in ex]
        spec[name] = {"dependent": d[y], "exog": pd.concat([d[ex], F], axis=1),
                      "endog": d[en] if en else None, "instruments": d[ins] if en else None}
    kw = {"cov_type": cov}
    if cov == "clustered":
        kw["clusters"] = d[clusters].astype("category").cat.codes.values
    return IV3SLS(spec).fit(**kw)

def coef(res, eq, v):
    k = f"{eq}_{v}"
    return res.params[k], res.std_errors[k], res.pvalues[k]

def lincom(res, terms):
    """Linear combination sum of params (list of (eq,var)) with its SE and p-value."""
    names = list(res.params.index)
    a = np.zeros(len(names))
    for eq, v in terms:
        a[names.index(f"{eq}_{v}")] = 1.0
    b = a @ res.params.values
    se = float(np.sqrt(a @ res.cov.values @ a))
    from scipy.stats import norm
    return b, se, 2 * (1 - norm.cdf(abs(b / se)))

def wald(res, terms):
    """Joint Wald test that all listed coefficients are zero (chi2)."""
    names = list(res.params.index)
    R = np.zeros((len(terms), len(names)))
    for i, (eq, v) in enumerate(terms):
        R[i, names.index(f"{eq}_{v}")] = 1.0
    b = R @ res.params.values
    V = R @ res.cov.values @ R.T
    stat = float(b @ np.linalg.solve(V, b))
    from scipy.stats import chi2
    return stat, 1 - chi2.cdf(stat, len(terms))

TABLE10 = {"GDP": ("lngdp_c", ["cap", "hci", "lnpat"], ["lnef"]),
           "EF": ("lnef", ["lnbio", "urb", "lnpat", "pat_inc"], ["lngdp_c"])}

def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""

def cell(b, se, p):
    return f"{b:.3f}{stars(p)} ({se:.3f})"
