"""
Download the IMF Commodity Terms of Trade database (Gruss and Kebhaj 2019) via the IMF SDMX API.

Dataflow IMF.RES:CTOT(5.0.1). Series kept (annual, all countries):
  CEMPI_CTOTXM_GDP  commodity net export price index, commodities weighted by net exports / GDP
  CEMPI_CTOTNX_TT   same, weighted by net exports / total commodity trade (robustness)
with weight types H_FW_IX (fixed weights, main) and H_RW_IX (rolling 3-year weights, robustness).
Indices 2012 = 100.

Usage:  python fetch_ctot.py      (writes data/imf/ctot_raw.csv and data/imf/ctot.csv)
"""
import io
import requests
import pandas as pd
import pycountry

URL = ("https://api.imf.org/external/sdmx/2.1/data/IMF.RES,CTOT,5.0.1/"
       ".CEMPI_CTOTXM_GDP+CEMPI_CTOTNX_TT.H_FW_IX+H_RW_IX.A")
HDR = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}

def iso2(c3):
    c = pycountry.countries.get(alpha_3=c3)
    return c.alpha_2 if c else None

def main():
    r = requests.get(URL, headers=HDR, timeout=300)
    if r.status_code != 200:
        raise SystemExit(f"HTTP {r.status_code}: {r.text[:300]}")
    open("data/imf/ctot_raw.csv", "w").write(r.text)        # raw, as returned by the API
    d = pd.read_csv(io.StringIO(r.text), keep_default_na=False, na_values=[""])
    d = d[["COUNTRY", "INDICATOR", "WGT_TYPE", "TIME_PERIOD", "OBS_VALUE"]].dropna(subset=["OBS_VALUE"])
    d["series"] = d.INDICATOR.map({"CEMPI_CTOTXM_GDP": "ctot_gdp", "CEMPI_CTOTNX_TT": "ctot_tt"}) \
        + d.WGT_TYPE.map({"H_FW_IX": "_fw", "H_RW_IX": "_rw"})
    w = d.pivot_table(index=["COUNTRY", "TIME_PERIOD"], columns="series", values="OBS_VALUE").reset_index()
    w = w.rename(columns={"COUNTRY": "country_3d", "TIME_PERIOD": "year"})
    w.insert(0, "country", w.country_3d.map(iso2))
    w.to_csv("data/imf/ctot.csv", index=False)
    print(w.shape, w.country.nunique(), "countries", w.year.min(), "-", w.year.max())

if __name__ == "__main__":
    main()
