"""Follow-up: decompose the met offset, resolve the centroid discrepancy,
and list isotopologues / water clusters."""
import numpy as np
import pandas as pd

CSV = (r"C:\Users\g.gkatzelis\Desktop\My Folders\My Coding\Python\GitHub"
       r"\FZJ-Condenses-Course-on-AI\data_original\MONALISA_campaign_master_30min.csv")
LAT, LON = 48.85, 2.35

def hr(x):
    print("\n" + "=" * 78 + f"\n{x}\n" + "=" * 78)

def solar_zenith(times, lat=LAT, lon=LON):
    ti = pd.DatetimeIndex(times)
    doy = np.asarray(ti.dayofyear, dtype="float64")
    hrs = (np.asarray(ti.hour) + np.asarray(ti.minute) / 60).astype("float64")
    ydays = np.where(np.asarray(ti.is_leap_year), 366.0, 365.0)
    g = 2 * np.pi / ydays * (doy - 1 + (hrs - 12) / 24)
    eqtime = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g)
                       - 0.014615 * np.cos(2 * g) - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g)
            - 0.006758 * np.cos(2 * g) + 0.000907 * np.sin(2 * g)
            - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    ha = np.deg2rad((hrs * 60 + eqtime + 4 * lon) / 4 - 180)
    la = np.deg2rad(lat)
    return np.rad2deg(np.arccos(np.clip(
        np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha), -1, 1)))

def scan(series, times, label, lo=-150, hi=90, step=5):
    m = series.notna().to_numpy()
    y = series.to_numpy(dtype="float64")[m]
    tt = pd.DatetimeIndex(times)[m]
    rows = []
    for d in range(lo, hi + 1, step):
        x = np.cos(np.deg2rad(solar_zenith(tt + pd.Timedelta(minutes=d)))).clip(min=0)
        rows.append((d, np.corrcoef(x, y)[0, 1]))
    b = max(rows, key=lambda r: r[1])
    # parabolic refinement around the maximum
    i = rows.index(b)
    fine = ""
    if 0 < i < len(rows) - 1:
        y0, y1, y2 = rows[i-1][1], rows[i][1], rows[i+1][1]
        denom = (y0 - 2*y1 + y2)
        if denom != 0:
            fine = f"  refined peak = {b[0] - step * 0.5 * (y2 - y0) / denom:+.1f} min"
    print(f"  {label:38s} best = {b[0]:+4d} min  (r={b[1]:.4f}){fine}")
    return b

df = pd.read_csv(CSV)
t = pd.to_datetime(df["time"])
rad = "met_Global_Radiation (J/cm2)"
gname = {c.split(" ")[0]: c for c in df.columns if c.startswith("gas_")}

hr("A. MET OFFSET: full 30-min grid vs de-duplicated h:00-only vs h:30-only")
scan(df[rad], t, "radiation, all 30-min rows")
m00 = (t.dt.minute == 0).to_numpy()
m30 = (t.dt.minute == 30).to_numpy()
scan(df.loc[m00, rad], t[m00], "radiation, h:00 rows only")
scan(df.loc[m30, rad], t[m30], "radiation, h:30 rows only")
print("\n  Sunshine_Duration is also a clean solar variable:")
sd = "met_Sunshine_Duration (min)"
scan(df[sd], t, "sunshine duration, all rows")
scan(df.loc[m00, sd], t[m00], "sunshine duration, h:00 only")

hr("B. WHY -45? the duplication itself costs 15 min")
print("""  If the hourly value labelled H:00 is the mean over the hour ENDING at H:00,
  its true centre is H-0:30, i.e. -30 min from its label.
  Copying it to H:30 as well gives the pair a mean label of H:15,
  so the pair as a whole needs -45 min. That is exactly what the scan finds.
     -45 min  =  -30 min (end-of-hour labelling)  +  -15 min (duplication)
  De-duplicating to h:00 rows should therefore recover ~-30 min.""")

hr("C. RADIATION CENTROID: duplicated grid vs de-duplicated")
for name, mask in [("all 30-min rows (duplicated)", np.ones(len(df), bool)),
                   ("h:00 rows only (de-duplicated)", m00)]:
    sub = df.loc[mask, [rad]].copy()
    tt = t[mask]
    sub["h"] = (tt.dt.hour + tt.dt.minute / 60).to_numpy()
    p = sub.groupby("h")[rad].mean()
    w = p.clip(lower=0)
    c = (p.index * w).sum() / w.sum()
    print(f"  {name:34s} centroid = {int(c)}:{round((c % 1) * 60):02d}  "
          f"peak label = {p.idxmax():.1f} h")
print("\n  Georgios' claim: 12:08")

hr("D. GAS: is the 30-min grid start- or end-labelled?")
NO = df[gname["gas_NO"]] / 1.25
NO2 = df[gname["gas_NO2"]] / 1.91
O3 = df[gname["gas_O3"]] / 2.0
proxy = (NO * O3 / NO2).replace([np.inf, -np.inf], np.nan)
scan(proxy, t, "NO*O3/NO2 proxy", lo=-90, hi=90)
print("""
  Interpretation: a value representing a bin CENTRED c minutes from its label
  gives best offset ~= c.  Start-labelled 30-min bin -> c = +15.
  End-labelled -> c = -15.  Centre-labelled -> c = 0.""")

hr("E. ISOTOPOLOGUES AND WATER CLUSTERS")
ions = [c for c in df.columns if c.startswith(("NH4_", "H3O_"))]
print(f"  names containing '13C'  : {[c for c in ions if '13C' in c]}")
print(f"  names containing 'H2O'  : {[c for c in ions if 'H2O' in c]}")
import re
# H3O_ reagent-ion water clusters look like H3O_H5O2+, H7O3+, H9O4+ ...
wat = [c for c in ions if re.fullmatch(r"(NH4|H3O)_H\d+O\d+\+", c)]
print(f"  pure water-cluster ions : {wat}")
nh4w = [c for c in ions if re.fullmatch(r"NH4_H\d+N?\d*O\d+\+", c)]
print(f"  NH4 water-ish ions      : {nh4w[:12]}")

hr("F. MISC DATA QUIRKS WORTH KNOWING")
print(f"  gas_O3 negative values  : {(df[gname['gas_O3']] < 0).sum()} rows "
      f"(min {df[gname['gas_O3']].min()})")
print(f"  gas_NO negative values  : {(df[gname['gas_NO']] < 0).sum()} rows")
print(f"  ion NaN fraction overall: "
      f"{100 * df[ions].isna().to_numpy().mean():.1f} %")
nrow = df[["n_NH4", "n_H3O", "n_gas", "n_met"]].describe().T
print("\n  bookkeeping columns:")
print(nrow[["count", "mean", "min", "max"]].round(2).to_string())
print("\n  n_met value counts (expect 1 if hourly duplicated into 30-min bins):")
print(df["n_met"].value_counts().head().to_string())
print("\n  n_gas value counts (expect 2 if 15-min native -> 30 min):")
print(df["n_gas"].value_counts().head().to_string())
print("\n  n_H3O value counts (expect ~30 if 1-min native -> 30 min):")
print(df["n_H3O"].value_counts().head().to_string())
