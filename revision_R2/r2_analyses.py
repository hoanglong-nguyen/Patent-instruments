"""
Revision R2: analyses requested by Reviewer 1 (comments 4-10, 15; minimum requirements 4-8).
Python replication of the Stata do-file do_10.6.do on analysis_replica.csv (build_analysis.py).
Every block writes one CSV in revision_R2/results/. Numbers are for drafting the revision;
the Stata do-file is the reference implementation for the final tables.

  A  Patent endogeneity: shift-share instrument (WIPO), FE-IV per equation and 3SLS        (R4)
  B  Leave-one-country-out for the higher-income countries (3SLS and FE-DK)               (R6)
  C  Alternative fixed development classifications                                         (R7)
  D  Joint Wald tests for H2 and H3                                                         (R17)
  E  3SLS vs FE (clustered) vs FE Driscoll-Kraay, coefficient by coefficient                (R5)
  F  Common correlated effects (pooled and mean group) and residual CD tests               (R9)
  G  Within-transformed correlations and VIFs                                               (R10)
  H  Biocapacity sensitivity                                                                (R15)
  I  Sample ending in 2022 (GFN marks 2023 as an estimate)                                  (R14 data)
  J  Wild cluster bootstrap p-values for PAT x INC (few treated clusters)                   (R6, R8)
  K  Cluster-robust 3SLS standard errors (inside block E)                                (R9)
  L  Non-overlapping 3-year averages (researcher's request)                                (R1, R5)
  M  Without Ethiopia (WDI reports CAP = 0 in 2000-2010)                                   (R17)
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from linearmodels.iv import IV2SLS
from linearmodels.panel import PanelOLS

sys.path.insert(0, os.path.dirname(__file__))
from r2lib import load, fe, reg3, coef, lincom, wald, TABLE10, cell

OUT = "revision_R2/results"
os.makedirs(OUT, exist_ok=True)
HI_ASIA, HI_AFRICA = ["IL", "JP", "KR", "MY"], ["BW", "MU", "ZA"]

def data():
    d = load()
    z = pd.read_csv("wipo_instrument.csv", keep_default_na=False, na_values=[""])
    z = z.rename(columns={"country": "country_2d"})[["country_2d", "year", "z_mean_lag1_10"]]
    d = d.merge(z, on=["country_2d", "year"], how="left")
    d["lnz"] = np.log1p(d.z_mean_lag1_10)
    d["lnz_inc"] = d.lnz * d.inc
    d["pat_inc_abr"] = d.lnpat_abr * d.inc
    return d

REGIONS = lambda d: {"Pooled": d, "Asia": d[d.asia == 1], "Africa": d[d.asia == 0]}

def save(rows, name):
    pd.DataFrame(rows).to_csv(f"{OUT}/{name}.csv", index=False)

# ---------------------------------------------------------------- helpers for single equations
def iv_fe(d, y, exog, endog, instr, clusters="country_2d"):
    d = d.reset_index(drop=True)
    X = pd.concat([d[exog], fe(d)], axis=1)
    return IV2SLS(d[y], X, d[endog], d[instr]).fit(cov_type="clustered", clusters=d[clusters])

def ols_fe(d, y, regs, clusters="country_2d"):
    d = d.reset_index(drop=True)
    X = pd.concat([d[regs], fe(d)], axis=1)
    return IV2SLS(d[y], X, None, None).fit(cov_type="clustered", clusters=d[clusters])

def wald_ols(res, names):
    cols = list(res.params.index)
    R = np.zeros((len(names), len(cols)))
    for i, v in enumerate(names):
        R[i, cols.index(v)] = 1
    return res.wald_test(restriction=R, value=np.zeros(len(names)))

def sw_f(d, exog, endog, instr):
    """Sanderson-Windmeijer conditional first-stage F (cluster-robust) per endogenous regressor."""
    out = {}
    L, K = len(instr), len(endog)
    for j in endog:
        others = [e for e in endog if e != j]
        dd = d.reset_index(drop=True)
        X = pd.concat([dd[exog], fe(dd)], axis=1)
        if others:
            r = IV2SLS(dd[j], X, dd[others], dd[instr]).fit(cov_type="unadjusted")
            e = r.resids
        else:
            e = dd[j]
        fs = ols_fe(dd.assign(_e=e.values), "_e", exog + instr)
        out[j] = wald_ols(fs, instr).stat / (L - K + 1)
    return out

def dwh(d, y, exog, endog_test, other_endog, instr, instr_all):
    """Regression-based (control-function) cluster-robust test that endog_test is exogenous.
    First stages use all excluded instruments (instr_all); other_endog keeps its own (instr)."""
    dd = d.reset_index(drop=True).copy()
    vs = []
    for j in endog_test:
        fs = ols_fe(dd, j, exog + instr_all)
        dd["v_" + j] = fs.resids.values
        vs.append("v_" + j)
    X = pd.concat([dd[exog + endog_test + vs], fe(dd)], axis=1)
    if other_endog:
        oi = [i for i in instr]
        r = IV2SLS(dd[y], X, dd[other_endog], dd[oi]).fit(cov_type="clustered", clusters=dd.country_2d)
    else:
        r = IV2SLS(dd[y], X, None, None).fit(cov_type="clustered", clusters=dd.country_2d)
    w = wald_ols(r, vs)
    return w.stat, w.pval

def anderson_rubin(d, y, exog, instr_all):
    """AR test of H0: all endogenous coefficients = 0 (reduced form: instruments jointly zero)."""
    r = ols_fe(d, y, exog + instr_all)
    w = wald_ols(r, instr_all)
    return w.stat / len(instr_all), w.pval

def dk(d, y, regs, lags=3):
    """Two-way FE with Driscoll-Kraay SE (Bartlett, `lags` lags), as xtscc ..., fe lag(3) + i.year."""
    p = d.set_index(["country_2d", "year"])
    m = PanelOLS(p[y], p[regs], entity_effects=True, time_effects=True)
    return m.fit(cov_type="kernel", kernel="bartlett", bandwidth=lags)

# ---------------------------------------------------------------- A: patent endogeneity
def block_A(d):
    rows = []
    for meas, pat, pinc in [("total stock (as in paper)", "lnpat", "pat_inc"),
                            ("abroad-filing stock", "lnpat_abr", "pat_inc_abr")]:
        for reg, s in REGIONS(d).items():
            s = s.dropna(subset=["lnz"])
            # growth equation: lnEF instrumented by lnBIO, URB; lnPAT by lnZ
            ex, en, ins = ["cap", "hci"], ["lnef", pat], ["lnbio", "urb", "lnz"]
            r = iv_fe(s, "lngdp_c", ex, en, ins)
            f = sw_f(s, ex, en, ins)
            st, p = dwh(s, "lngdp_c", ex, [pat], ["lnef"], ["lnbio", "urb"], ins)
            ar = anderson_rubin(s, "lngdp_c", ex, ins)
            rows.append({"measure": meas, "sample": reg, "equation": "GDP", "countries": s.country_2d.nunique(),
                         "obs": len(s), "b_lnpat": cell(r.params[pat], r.std_errors[pat], r.pvalues[pat]),
                         "b_patinc": "", "SW_F_lnpat": round(f[pat], 2), "SW_F_patinc": "",
                         "DWH_p_pat_exog": round(p, 3), "AR_p": round(ar[1], 3)})
            # environmental equation: lnGDP by CAP, HCI; lnPAT and PATxINC by lnZ, lnZxINC
            ex, en, ins = ["lnbio", "urb"], ["lngdp_c", pat, pinc], ["cap", "hci", "lnz", "lnz_inc"]
            r = iv_fe(s, "lnef", ex, en, ins)
            f = sw_f(s, ex, en, ins)
            st, p = dwh(s, "lnef", ex, [pat, pinc], ["lngdp_c"], ["cap", "hci"], ins)
            ar = anderson_rubin(s, "lnef", ex, ins)
            rows.append({"measure": meas, "sample": reg, "equation": "EF", "countries": s.country_2d.nunique(),
                         "obs": len(s), "b_lnpat": cell(r.params[pat], r.std_errors[pat], r.pvalues[pat]),
                         "b_patinc": cell(r.params[pinc], r.std_errors[pinc], r.pvalues[pinc]),
                         "SW_F_lnpat": round(f[pat], 2), "SW_F_patinc": round(f[pinc], 2),
                         "DWH_p_pat_exog": round(p, 3), "AR_p": round(ar[1], 3)})
    save(rows, "A_patent_endogeneity_FEIV")
    # 3SLS with patent stock endogenous (total stock), lnZ and lnZxINC added to the system instruments
    rows = []
    for reg, s in REGIONS(d).items():
        s = s.dropna(subset=["lnz"])
        base = reg3(s, TABLE10)
        eqs = {"GDP": ("lngdp_c", ["cap", "hci"], ["lnef", "lnpat"]),
               "EF": ("lnef", ["lnbio", "urb"], ["lngdp_c", "lnpat", "pat_inc"])}
        endo = reg3(s, eqs, extra_exog=["lnz", "lnz_inc"])
        for lab, r, eq_g, eq_e in [("PAT exogenous (paper), same 40-country sample", base, "GDP", "EF"),
                                   ("PAT endogenous (shift-share)", endo, "GDP", "EF")]:
            rows.append({"sample": reg, "model": lab, "countries": s.country_2d.nunique(),
                         "GDP_lnpat": cell(*coef(r, "GDP", "lnpat")), "EF_lnpat": cell(*coef(r, "EF", "lnpat")),
                         "EF_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "ME_higher_income": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")])),
                         "GDP_lnef": cell(*coef(r, "GDP", "lnef")), "EF_lngdp": cell(*coef(r, "EF", "lngdp_c"))})
    save(rows, "A_patent_endogeneity_3SLS")

# ---------------------------------------------------------------- B: leave one country out
def block_B(d):
    rows = []
    for reg, hi in [("Asia", HI_ASIA), ("Africa", HI_AFRICA)]:
        s0 = d[d.asia == (1 if reg == "Asia" else 0)]
        for drop in ["none"] + hi:
            s = s0 if drop == "none" else s0[s0.country_2d != drop]
            r = reg3(s, TABLE10)
            k = dk(s, "lnef", ["lngdp_c", "lnbio", "urb", "lnpat", "pat_inc"])
            a = np.zeros(len(k.params)); names = list(k.params.index)
            a[names.index("lnpat")] = a[names.index("pat_inc")] = 1
            me = a @ k.params.values; mse = np.sqrt(a @ k.cov.values @ a)
            rows.append({"region": reg, "dropped": drop, "n_higher_income_left": len(hi) - (drop != "none"),
                         "3SLS_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "3SLS_ME_higher": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")])),
                         "3SLS_GDP_lnpat": cell(*coef(r, "GDP", "lnpat")),
                         "DK_patinc": cell(k.params["pat_inc"], k.std_errors["pat_inc"], k.pvalues["pat_inc"]),
                         "DK_ME_higher": cell(me, mse, 2 * (1 - stats.norm.cdf(abs(me / mse))))})
    save(rows, "B_leave_one_out")

# ---------------------------------------------------------------- C: alternative classifications
def block_C(d):
    import pycountry
    inc = pd.read_stata("data/income.dta")
    inc["country_2d"] = inc.country_3d.map(lambda x: getattr(pycountry.countries.get(alpha_3=x), "alpha_2", None))
    hi = inc[inc.year.between(2000, 2023)].assign(h=lambda x: x.inc_class.isin(["UM", "H"]))
    hi = hi.pivot_table(index="country_2d", columns="year", values="h", aggfunc="first")
    defs = {"INC 2000 (paper)": hi[2000],
            "INC majority 2000-2004": hi.loc[:, 2000:2004].mean(axis=1) > 0.5,
            "INC 2005": hi[2005],
            "INC 2010 (mid-period, not predetermined)": hi[2010]}
    rows = []
    for lab, flag in defs.items():
        s = d.copy()
        s["inc"] = s.country_2d.map(flag.astype(int))
        s["pat_inc"] = s.lnpat * s.inc
        members = sorted(s[s.inc == 1].country_2d.unique())
        for reg, ss in REGIONS(s).items():
            r = reg3(ss, TABLE10)
            rows.append({"classification": lab, "sample": reg,
                         "higher_income": " ".join(c for c in members if c in set(ss.country_2d)),
                         "EF_lnpat": cell(*coef(r, "EF", "lnpat")), "EF_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "ME_higher": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")]))})
    # continuous development stage: lnGDP per capita in 2000, centred within the estimation sample
    for reg, ss in REGIONS(d).items():
        ss = ss.copy()
        g0 = ss[ss.year == 2000].set_index("country_2d").lngdp
        ss["dev"] = ss.country_2d.map(g0) - g0.mean()
        ss["pat_dev"] = ss.lnpat * ss.dev
        eqs = {"GDP": TABLE10["GDP"], "EF": ("lnef", ["lnbio", "urb", "lnpat", "pat_dev"], ["lngdp_c"])}
        r = reg3(ss, eqs)
        rows.append({"classification": "continuous: lnGDPpc 2000 (centred)", "sample": reg, "higher_income": "all",
                     "EF_lnpat": cell(*coef(r, "EF", "lnpat")), "EF_patinc": cell(*coef(r, "EF", "pat_dev")),
                     "ME_higher": "slope varies with 2000 income"})
    save(rows, "C_alternative_classification")

# ---------------------------------------------------------------- D: joint Wald tests
def block_D(d):
    rows = []
    for reg, s in REGIONS(d).items():
        r = reg3(s, TABLE10)
        tests = {"H2 growth margin: [GDP]lnPAT = 0": [("GDP", "lnpat")],
                 "Innovation unrelated to EF in both groups: [EF]lnPAT = [EF]PATxINC = 0":
                     [("EF", "lnpat"), ("EF", "pat_inc")],
                 "H3: [EF]PATxINC = 0": [("EF", "pat_inc")]}
        for lab, t in tests.items():
            st, p = wald(r, t)
            rows.append({"sample": reg, "test": lab, "chi2": round(st, 2), "df": len(t), "p": round(p, 4)})
        # dual role in the higher-income group: [GDP]lnPAT = 0 and [EF]lnPAT + [EF]PATxINC = 0
        names = list(r.params.index)
        R = np.zeros((2, len(names)))
        R[0, names.index("GDP_lnpat")] = 1
        R[1, names.index("EF_lnpat")] = R[1, names.index("EF_pat_inc")] = 1
        b = R @ r.params.values
        st = float(b @ np.linalg.solve(R @ r.cov.values @ R.T, b))
        rows.append({"sample": reg, "test": "H2 dual role, higher income: [GDP]lnPAT = 0 & [EF]lnPAT+PATxINC = 0",
                     "chi2": round(st, 2), "df": 2, "p": round(1 - stats.chi2.cdf(st, 2), 4)})
    save(rows, "D_joint_wald")

# ---------------------------------------------------------------- E: reconciliation
def block_E(d):
    rows = []
    for reg, s in REGIONS(d).items():
        r3 = reg3(s, TABLE10)
        r3c = reg3(s, TABLE10, cov="clustered", clusters="country_2d")
        for eq, y, regs in [("GDP", "lngdp_c", ["lnef", "cap", "hci", "lnpat"]),
                            ("EF", "lnef", ["lngdp_c", "lnbio", "urb", "lnpat", "pat_inc"])]:
            fc = ols_fe(s, y, regs)
            k = dk(s, y, regs)
            for v in regs:
                b3, s3, p3 = coef(r3, eq, v)
                bc, sc, pc = coef(r3c, eq, v)
                rows.append({"sample": reg, "equation": eq, "variable": v,
                             "3SLS (paper SE)": cell(b3, s3, p3), "3SLS (clustered SE)": cell(bc, sc, pc),
                             "FE (clustered)": cell(fc.params[v], fc.std_errors[v], fc.pvalues[v]),
                             "FE (Driscoll-Kraay)": cell(k.params[v], k.std_errors[v], k.pvalues[v]),
                             "same sign 3SLS vs FE": np.sign(b3) == np.sign(k.params[v]),
                             "both significant 10%": (p3 < .1) and (k.pvalues[v] < .1)})
    save(rows, "E_reconciliation")

# ---------------------------------------------------------------- F: CCE and CD tests
def pesaran_cd(e, ids, t):
    m = pd.DataFrame({"e": e, "i": ids, "t": t}).pivot(index="t", columns="i", values="e")
    N, T = m.shape[1], m.shape[0]
    rho = m.corr().values[np.triu_indices(N, 1)]
    cd = np.sqrt(2 * T / (N * (N - 1))) * np.nansum(rho)
    return cd, 2 * (1 - stats.norm.cdf(abs(cd)))

def block_F(d):
    rows = []
    for reg, s in REGIONS(d).items():
        s = s.reset_index(drop=True).copy()
        base = ["lngdp_c", "lnbio", "urb", "lnpat"]
        regs = base + ["pat_inc"]
        # FE residual CD
        fc = ols_fe(s, "lnef", regs)
        cd0 = pesaran_cd(fc.resids.values, s.country_2d, s.year)
        # CCE pooled: country FE + country-specific loadings on cross-section averages of y and x
        csa = s.groupby("year")[["lnef"] + base].transform("mean").add_prefix("csa_")
        X = [s[regs]]
        for c in sorted(s.country_2d.unique()):
            m = (s.country_2d == c).astype(float).values[:, None]
            X.append(pd.DataFrame(csa.values * m, columns=[f"{c}_{k}" for k in csa.columns]))
            X.append(pd.DataFrame({f"fe_{c}": m[:, 0]}))
        X = pd.concat(X, axis=1)
        X = X.loc[:, X.std() > 0]
        r = IV2SLS(s["lnef"], X, None, None).fit(cov_type="clustered", clusters=s.country_2d)
        cd1 = pesaran_cd(r.resids.values, s.country_2d, s.year)
        row = {"sample": reg, "FE_residual_CD": round(cd0[0], 2), "FE_CD_p": round(cd0[1], 3),
               "CCEP_residual_CD": round(cd1[0], 2), "CCEP_CD_p": round(cd1[1], 3)}
        for v in regs:
            row[f"CCEP_{v}"] = cell(r.params[v], r.std_errors[v], r.pvalues[v])
        row["CCEP_ME_higher"] = cell(*_lin(r, ["lnpat", "pat_inc"]))
        rows.append(row)
    save(rows, "F_CCE_pooled")
    # CCE mean group: country-specific lnPAT slopes, averaged within region x income cells
    rows = []
    for reg, s in REGIONS(d).items():
        if reg == "Pooled":
            continue
        s = s.reset_index(drop=True)
        base = ["lngdp_c", "lnbio", "urb", "lnpat"]
        csa = s.groupby("year")[["lnef"] + base].transform("mean").add_prefix("csa_")
        slopes = []
        for c, g in s.groupby("country_2d"):
            X = pd.concat([g[base], csa.loc[g.index]], axis=1).assign(const=1.0)
            X = X.loc[:, X.std() > 0].assign(const=1.0)
            b = np.linalg.lstsq(X.values, g.lnef.values, rcond=None)[0]
            slopes.append({"country": c, "inc": g.inc.iloc[0], "b_lnpat": b[list(X.columns).index("lnpat")]})
        sl = pd.DataFrame(slopes)
        for grp, g in sl.groupby("inc"):
            mg, se = g.b_lnpat.mean(), g.b_lnpat.std(ddof=1) / np.sqrt(len(g))
            rows.append({"sample": reg, "group": "higher income" if grp else "lower income", "countries": len(g),
                         "CCE-MG lnPAT on lnEF": cell(mg, se, 2 * (1 - stats.t.cdf(abs(mg / se), len(g) - 1))),
                         "country slopes": " ".join(f"{a}:{b:.3f}" for a, b in zip(g.country, g.b_lnpat))})
    save(rows, "F_CCE_mean_group")

def _lin(r, names):
    cols = list(r.params.index)
    a = np.zeros(len(cols))
    for v in names:
        a[cols.index(v)] = 1
    b = a @ r.params.values
    se = float(np.sqrt(a @ r.cov.values @ a))
    return b, se, 2 * (1 - stats.norm.cdf(abs(b / se)))

# ---------------------------------------------------------------- G: within correlations and VIF
def block_G(d):
    v = ["lngdp", "cap", "hci", "lnpat", "lnef", "lnbio", "urb"]
    w = d.copy()
    for x in v:      # balanced panel: two-way within transformation is exact
        w[x] = w[x] - w.groupby("country_2d")[x].transform("mean") - w.groupby("year")[x].transform("mean") + w[x].mean()
    pd.DataFrame(d[v].corr().round(3)).to_csv(f"{OUT}/G_correlation_pooled.csv")
    pd.DataFrame(w[v].corr().round(3)).to_csv(f"{OUT}/G_correlation_within.csv")
    rows = []
    for eq, regs in [("GDP", ["lnef", "cap", "hci", "lnpat"]), ("EF", ["lngdp", "lnbio", "urb", "lnpat"])]:
        for x in regs:
            o = [r for r in regs if r != x]
            Xo = np.column_stack([w[o].values, np.ones(len(w))])
            b = np.linalg.lstsq(Xo, w[x].values, rcond=None)[0]
            r2 = 1 - np.var(w[x].values - Xo @ b) / np.var(w[x].values)
            rows.append({"equation": eq, "regressor": x, "within_VIF": round(1 / (1 - r2), 2)})
    save(rows, "G_within_VIF")

# ---------------------------------------------------------------- H: biocapacity sensitivity
def block_H(d):
    rows = []
    specs = {"paper": TABLE10,
             "no lnBIO anywhere (EF control and GDP instrument)":
                 {"GDP": TABLE10["GDP"], "EF": ("lnef", ["urb", "lnpat", "pat_inc"], ["lngdp_c"])},
             "lnBIO as EF control only (not an instrument for lnEF)": None}
    for lab, eqs in specs.items():
        for reg, s in REGIONS(d).items():
            if eqs is None:
                # lnBIO stays in EF equation; GDP equation instrumented by URB only: emulate by
                # running FE-2SLS for GDP with URB only and 3SLS-equivalent EF with lnBIO
                r_g = iv_fe(s, "lngdp_c", ["cap", "hci", "lnpat"], ["lnef"], ["urb"])
                r_e = reg3(s, TABLE10)
                rows.append({"specification": lab, "sample": reg,
                             "GDP_lnef": cell(r_g.params["lnef"], r_g.std_errors["lnef"], r_g.pvalues["lnef"]),
                             "GDP_lnpat": cell(r_g.params["lnpat"], r_g.std_errors["lnpat"], r_g.pvalues["lnpat"]),
                             "EF_lngdp": cell(*coef(r_e, "EF", "lngdp_c")), "EF_patinc": cell(*coef(r_e, "EF", "pat_inc")),
                             "ME_higher": cell(*lincom(r_e, [("EF", "lnpat"), ("EF", "pat_inc")])),
                             "note": "GDP eq by FE-2SLS (clustered), instrument URB only"})
                continue
            r = reg3(s, eqs)
            rows.append({"specification": lab, "sample": reg, "GDP_lnef": cell(*coef(r, "GDP", "lnef")),
                         "GDP_lnpat": cell(*coef(r, "GDP", "lnpat")), "EF_lngdp": cell(*coef(r, "EF", "lngdp_c")),
                         "EF_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "ME_higher": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")])), "note": "3SLS"})
    save(rows, "H_biocapacity")

# ---------------------------------------------------------------- I: 2000-2022
def block_I(d):
    rows = []
    for lab, s0 in [("2000-2023 (paper)", d), ("2000-2022 (GFN accounts only)", d[d.year <= 2022])]:
        for reg, s in REGIONS(s0).items():
            r = reg3(s, TABLE10)
            rows.append({"period": lab, "sample": reg, "GDP_lnef": cell(*coef(r, "GDP", "lnef")),
                         "GDP_lnpat": cell(*coef(r, "GDP", "lnpat")), "EF_lngdp": cell(*coef(r, "EF", "lngdp_c")),
                         "EF_lnpat": cell(*coef(r, "EF", "lnpat")), "EF_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "ME_higher": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")]))})
    save(rows, "I_period_2022")

# ---------------------------------------------------------------- J: wild cluster bootstrap
def wcr(d, y, regs, target, B=9999, seed=12345):
    """Restricted wild cluster bootstrap-t (WCR, Webb weights) for one coefficient in a two-way FE
    regression, CRV1 t-statistic; FE and other regressors partialled out (FWL)."""
    rng = np.random.default_rng(seed)
    dd = d.reset_index(drop=True)
    F = fe(dd).values
    def resid(v):
        return v - F @ np.linalg.lstsq(F, v, rcond=None)[0]
    Y = resid(dd[y].values.astype(float))
    Xall = np.column_stack([resid(dd[r].values.astype(float)) for r in regs])
    k = regs.index(target)
    g = dd.country_2d.astype("category").cat.codes.values
    G = g.max() + 1
    def tstat(yv):
        b = np.linalg.lstsq(Xall, yv, rcond=None)[0]
        e = yv - Xall @ b
        XtXi = np.linalg.pinv(Xall.T @ Xall)
        meat = np.zeros((Xall.shape[1],) * 2)
        for c in range(G):
            s = Xall[g == c].T @ e[g == c]
            meat += np.outer(s, s)
        n, kk = Xall.shape
        adj = G / (G - 1) * (n - 1) / (n - kk)
        V = adj * XtXi @ meat @ XtXi
        return b[k] / np.sqrt(V[k, k]), b[k]
    t0, b0 = tstat(Y)
    Xr = np.delete(Xall, k, axis=1)
    br = np.linalg.lstsq(Xr, Y, rcond=None)[0]
    fit_r, e_r = Xr @ br, Y - Xr @ br
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
    tb = np.empty(B)
    for i in range(B):
        w = webb[rng.integers(0, 6, G)]
        tb[i] = tstat(fit_r + e_r * w[g])[0]
    return b0, t0, np.mean(np.abs(tb) >= abs(t0)), G

def block_J(d):
    rows = []
    regs = ["lngdp_c", "lnbio", "urb", "lnpat", "pat_inc"]
    for reg, s in REGIONS(d).items():
        b, t, p, G = wcr(s, "lnef", regs, "pat_inc")
        rows.append({"sample": reg, "model": "EF equation, two-way FE", "coef PATxINC": round(b, 3),
                     "CRV1 t": round(t, 2), "conventional p (t, G-1 df)": round(2 * (1 - stats.t.cdf(abs(t), G - 1)), 4),
                     "WCR bootstrap p (Webb, 9999)": round(p, 4), "clusters": G,
                     "treated clusters": int(s[s.inc == 1].country_2d.nunique())})
    save(rows, "J_wild_bootstrap")

# ---------------------------------------------------------------- K: clustered 3SLS (in block E)

# ---------------------------------------------------------------- L: 3-year averages
def three_year(d):
    """Non-overlapping 3-year averages (2000-02, ..., 2021-23): levels averaged, then logged;
    income group stays fixed at 2000; the instrument is the period mean of Z."""
    d = d.copy()
    d["year"] = 2000 + 3 * ((d.year - 2000) // 3)          # period label = first year
    lev = ["gdp", "ef", "bio", "cap", "hci", "urb", "patstock", "patstock_abr", "pop", "z_mean_lag1_10"]
    a = d.groupby(["country_2d", "year"]).agg({**{v: "mean" for v in lev},
                                               "inc": "first", "asia": "first"}).reset_index()
    a["lngdp"] = np.log(a.gdp); a["lngdp_c"] = a.lngdp - a.lngdp.mean()
    a["lnef"], a["lnbio"] = np.log(a.ef), np.log(a.bio)
    a["lnpat"] = np.log((a.patstock + 1) / a["pop"]); a["pat_inc"] = a.lnpat * a.inc
    a["lnz"] = np.log1p(a.z_mean_lag1_10); a["lnz_inc"] = a.lnz * a.inc
    return a

def block_L(d):
    a = three_year(d)
    rows, diag = [], []
    for reg, s in REGIONS(a).items():
        r = reg3(s, TABLE10)
        rc = reg3(s, TABLE10, cov="clustered", clusters="country_2d")
        fc = ols_fe(s, "lnef", ["lngdp_c", "lnbio", "urb", "lnpat", "pat_inc"])
        b, t, p, G = wcr(s, "lnef", ["lngdp_c", "lnbio", "urb", "lnpat", "pat_inc"], "pat_inc")
        for lab, x in [("3SLS (paper SE)", r), ("3SLS (clustered SE)", rc)]:
            rows.append({"sample": reg, "estimator": lab, "obs": len(s),
                         "GDP_lnef": cell(*coef(x, "GDP", "lnef")), "GDP_lnpat": cell(*coef(x, "GDP", "lnpat")),
                         "EF_lngdp": cell(*coef(x, "EF", "lngdp_c")), "EF_lnpat": cell(*coef(x, "EF", "lnpat")),
                         "EF_patinc": cell(*coef(x, "EF", "pat_inc")),
                         "ME_higher": cell(*lincom(x, [("EF", "lnpat"), ("EF", "pat_inc")]))})
        rows.append({"sample": reg, "estimator": "FE (clustered), EF eq; WCR p for PATxINC = %.3f" % p, "obs": len(s),
                     "EF_lngdp": cell(fc.params["lngdp_c"], fc.std_errors["lngdp_c"], fc.pvalues["lngdp_c"]),
                     "EF_lnpat": cell(fc.params["lnpat"], fc.std_errors["lnpat"], fc.pvalues["lnpat"]),
                     "EF_patinc": cell(fc.params["pat_inc"], fc.std_errors["pat_inc"], fc.pvalues["pat_inc"])})
        # identification strength in the averaged panel
        f_gdp = sw_f(s, ["lnbio", "urb", "lnpat", "pat_inc"], ["lngdp_c"], ["cap", "hci"])["lngdp_c"]
        f_ef = sw_f(s, ["cap", "hci", "lnpat"], ["lnef"], ["lnbio", "urb"])["lnef"]
        ss = s.dropna(subset=["lnz"])
        f_pat = sw_f(ss, ["cap", "hci"], ["lnpat"], ["lnz"])["lnpat"]
        diag.append({"sample": reg, "F lnGDP in EF eq (CAP, HCI)": round(f_gdp, 2),
                     "F lnEF in GDP eq (BIO, URB)": round(f_ef, 2), "F lnPAT on shift-share (lnZ)": round(f_pat, 2)})
    save(rows, "L_three_year_averages")
    save(diag, "L_three_year_first_stage")
    a.to_csv("revision_R2/analysis_3yr_replica.csv", index=False)

# ---------------------------------------------------------------- M: Ethiopia (CAP = 0 in 2000-2010)
def block_M(d):
    rows = []
    for lab, s0 in [("43 countries (paper)", d), ("without Ethiopia (CAP = 0 in 2000-2010)", d[d.country_2d != "ET"])]:
        for reg, s in REGIONS(s0).items():
            r = reg3(s, TABLE10)
            rows.append({"sample": lab, "region": reg, "GDP_lnef": cell(*coef(r, "GDP", "lnef")),
                         "GDP_cap": cell(*coef(r, "GDP", "cap")), "GDP_lnpat": cell(*coef(r, "GDP", "lnpat")),
                         "EF_lngdp": cell(*coef(r, "EF", "lngdp_c")), "EF_patinc": cell(*coef(r, "EF", "pat_inc")),
                         "ME_higher": cell(*lincom(r, [("EF", "lnpat"), ("EF", "pat_inc")]))})
    save(rows, "M_ethiopia_cap")

if __name__ == "__main__":
    d = data()
    for f in [block_A, block_B, block_C, block_D, block_E, block_F, block_G, block_H, block_I, block_J, block_L, block_M]:
        f(d)
        print("done", f.__name__)
