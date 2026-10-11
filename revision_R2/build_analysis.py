"""
Python replication of the data steps of do_10.5.do (analysis.dta), for checking the
revision analyses outside Stata. Inputs: data/*.dta supplied by the researcher and the
WIPO office x origin table (wipo_patent_office_origin.csv).

Patent series: WIPO total applications by applicant origin = sum over filing offices
(the do-file's patent_raw.xlsx "Total"; where the home office did not report, the sum
equals filings abroad, which is the do-file's fill rule).
"""
import warnings
import numpy as np
import pandas as pd
import pycountry
warnings.filterwarnings("ignore")
import sys; sys.path.insert(0, ".")
from wipo_shift_share import load, acting, AFRICA, ASIA

def iso2(c3):
    c = pycountry.countries.get(alpha_3=c3)
    return c.alpha_2 if c else None

def pim(series, delta=0.15):
    """Perpetual inventory as in do_10.5: S_1980 = P_1980/(g0+delta), g0 from 1980-1985."""
    p = series.reindex(range(1980, 2024), fill_value=0.0).values
    g0 = (p[5] / p[0]) ** (1 / 5) - 1 if p[0] > 0 else np.nan
    if not np.isfinite(g0) or g0 <= 0:
        g0 = 0.05
    s = np.zeros_like(p)
    s[0] = p[0] / (g0 + delta) if p[0] > 0 else 0.0
    for t in range(1, len(p)):
        s[t] = (1 - delta) * s[t - 1] + p[t]
    return pd.Series(s, index=range(1980, 2024))

def build():
    w = load()
    w["abroad"] = [o not in acting(c) for o, c in zip(w.office, w.origin)]
    tot = w.groupby(["origin", "year"]).n.sum()
    abr = w[w.abroad].groupby(["origin", "year"]).n.sum()
    rows = []
    for c in sorted(set(w.origin) & set(AFRICA + ASIA)):
        st = pim(tot.get(c, pd.Series(dtype=float)))
        sa = pim(abr.get(c, pd.Series(dtype=float)))
        for t in range(2000, 2024):
            rows.append((c, t, st[t], sa[t]))
    pat = pd.DataFrame(rows, columns=["country_2d", "year", "patstock", "patstock_abr"])

    def by3(f, cols):
        x = pd.read_stata(f"data/{f}.dta")
        x["country_2d"] = x.country_3d.map(iso2)
        return x[["country_2d", "country_3d", "year"] + cols] if "country_3d" in x else x
    d = (by3("pwt", ["hci", "pop"])
         .merge(pat, on=["country_2d", "year"])
         .merge(by3("income", ["inc_class"]).drop(columns="country_3d"), on=["country_2d", "year"])
         .merge(by3("wdi", ["gdp", "cap", "urb"]).drop(columns="country_3d"), on=["country_2d", "year"])
         .merge(pd.read_stata("data/gfn.dta").rename(columns={"country_2d": "country_2d"}),
                on=["country_2d", "year"]))
    d = d[d.year.between(2000, 2023)]
    # [R2-17] WDI reports gross capital formation = 0 for Ethiopia in 2000-2010. Fill WDI zeros with
    # PWT 11.0 national-accounts gross capital formation share, 100 * v_i / v_gdp (current national
    # prices; same concept as WDI NE.GDI.TOTL.ZS; WDI/PWT ratio for Ethiopia 2011-2023 = 1.002).
    na = pd.read_stata("data/pwt/pwt110_na_data.dta")
    na["cap_pwt"] = 100 * na.v_i / na.v_gdp
    na["country_2d"] = na.countrycode.map(lambda c: getattr(pycountry.countries.get(alpha_3=c), "alpha_2", None))
    d = d.merge(na[["country_2d", "year", "cap_pwt"]], on=["country_2d", "year"], how="left")
    d["cap_wdi"] = d.cap
    d["cap_filled"] = ((d.cap == 0) & d.cap_pwt.notna()).astype(int)
    d.loc[d.cap_filled == 1, "cap"] = d.cap_pwt
    d = d[~d.country_2d.isin(["CY", "TR"])]            # Europe in the researcher's iso.dta crosswalk
    d["continent_2d"] = np.where(d.country_2d.isin(ASIA), "AS", "AF")
    # exclusion rule of do_10.5: any missing on a model variable -> country dropped
    v = ["gdp", "ef", "bio", "cap", "hci", "urb", "patstock"]
    full = d.groupby("country_2d").apply(lambda g: len(g) == 24 and g[v].notna().all().all())
    d = d[d.country_2d.isin(full[full].index)].copy()
    d["lngdp"] = np.log(d.gdp)
    d["lngdp_c"] = d.lngdp - d.lngdp.mean()
    d["lnef"], d["lnbio"] = np.log(d.ef), np.log(d.bio)
    d["lnpat"] = np.log((d.patstock + 1) / d["pop"])
    d["lnpat_abr"] = np.log((d.patstock_abr + 1) / d["pop"])
    d["asia"] = (d.continent_2d == "AS").astype(int)
    c00 = d[d.year == 2000].set_index("country_2d").inc_class
    d["inc"] = d.country_2d.map(c00.isin(["UM", "H"]).astype(int))
    d["pat_inc"] = d.lnpat * d.inc
    return d.sort_values(["country_2d", "year"]).reset_index(drop=True)

if __name__ == "__main__":
    d = build()
    print(d.country_2d.nunique(), "countries;", d.asia.groupby(d.country_2d).first().sum(), "Asian;", len(d), "obs")
    print(sorted(d.country_2d.unique()))
    print("INC=1:", sorted(d[d.inc == 1].country_2d.unique()))
    print(d[["gdp", "ef", "cap", "hci", "bio", "urb"]].describe().loc[["mean", "min", "max"]].round(2))
    print("pat per million mean", (d.patstock / d["pop"]).mean().round(0), " lnpat mean/sd", d.lnpat.mean().round(3), d.lnpat.std().round(3))
    d.to_csv("revision_R2/analysis_replica.csv", index=False)
