"""Reproduce every claim Georgios made about MONALISA_campaign_master_30min.csv.
Read-only. Prints a report; writes nothing to the project."""
import numpy as np
import pandas as pd

CSV = (r"C:\Users\g.gkatzelis\Desktop\My Folders\My Coding\Python\GitHub"
       r"\FZJ-Condenses-Course-on-AI\data_original\MONALISA_campaign_master_30min.csv")
LAT, LON = 48.85, 2.35

def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)

df = pd.read_csv(CSV)
hr("1. SHAPE / GRID / DATE RANGE")
print(f"rows                : {len(df)}      (claim: 2927)")
print(f"cols                : {df.shape[1]}")
t = pd.to_datetime(df["time"])
print(f"first               : {t.iloc[0]}")
print(f"last                : {t.iloc[-1]}   (claim: 1 Sep - 31 Oct 2025)")
d = t.diff().dropna().value_counts()
print(f"spacing value counts:\n{d.to_string()}")
print(f"monotonic increasing: {t.is_monotonic_increasing}")
print(f"duplicated stamps   : {t.duplicated().sum()}")
print(f"tz-aware            : {t.dt.tz is not None}  (no tz label = naive)")
expected = pd.date_range(t.iloc[0], t.iloc[-1], freq="30min")
print(f"complete 30-min grid: {len(expected) == len(t) and (expected == t).all()}"
      f"  (expected {len(expected)} slots)")

hr("2. COLUMN GROUPS")
cols = list(df.columns)
groups = {}
for c in cols:
    g = c.split("_")[0] if "_" in c else c
    groups.setdefault(g, []).append(c)
for g, v in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    print(f"  {g:6s}: {len(v)}")
print("\nclaim: 427 NH4, 430 H3O, 11 gas, 8 met, 4 n, 1 time")

hr("3. ION VALUE RANGE AND NEGATIVES")
ioncols = [c for c in cols if c.startswith(("NH4_", "H3O_"))]
ions = df[ioncols]
vals = ions.to_numpy(dtype="float64")
finite = np.isfinite(vals)
print(f"ion columns         : {len(ioncols)}")
print(f"min                 : {np.nanmin(vals):,.1f}   (claim: about -1470)")
print(f"max                 : {np.nanmax(vals):,.1f}   (claim: about 90000)")
neg = (vals < 0) & finite
print(f"% negative (finite) : {100 * neg.sum() / finite.sum():.3f} %   (claim: ~1.3 %)")
print(f"% NaN               : {100 * (~finite).sum() / vals.size:.2f} %")
print(f"cols with any neg   : {sum((ions < 0).any())} of {len(ioncols)}")

hr("4. ION NAMING: ISOTOPOLOGUES, WATER CLUSTERS, ADDUCTS")
iso = [c for c in ioncols if "13C" in c]
h2o = [c for c in ioncols if "H2O" in c or "W" in c.split("_")[1][:2]]
print(f"[13C] isotopologues : {len(iso)}  e.g. {iso[:4]}")
print(f"names containing H2O: {len([c for c in ioncols if 'H2O' in c])}")
print(f"NH4_C3H10NO+ present (acetone.NH4+): {'NH4_C3H10NO+' in cols}")

hr("5. GAS AND MET COLUMNS (verbatim names)")
for c in groups.get("gas", []):
    s = df[c]
    print(f"  {c:34s} n={s.notna().sum():5d}  min={s.min():10.3f}  max={s.max():10.3f}")
print()
for c in groups.get("met", []):
    s = df[c]
    print(f"  {c:34s} n={s.notna().sum():5d}  min={s.min():10.3f}  max={s.max():10.3f}")

hr("6. MET DUPLICATION: h:00 vs h:30 identical?")
is30 = t.dt.minute == 30
for c in groups.get("met", []):
    a = df.loc[~is30.to_numpy(), c].reset_index(drop=True)   # h:00
    b = df.loc[is30.to_numpy(), c].reset_index(drop=True)    # h:30
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    both = a.notna() & b.notna()
    same = (a[both] == b[both]).sum()
    print(f"  {c:34s} pairs={both.sum():5d}  identical={same:5d} "
          f"({100*same/max(both.sum(),1):6.2f} %)")
print("\nclaim: each hourly value copied into BOTH h:00 and h:30; precip 100 % identical")
print("NOTE: the above pairs h:00 with the FOLLOWING h:30 of the same hour.")

hr("6b. MET DUPLICATION, alternative pairing (h:30 with FOLLOWING h+1:00)")
for c in groups.get("met", []):
    s = df[c]
    a = s[is30.to_numpy()].reset_index(drop=True)
    b = s[~is30.to_numpy()].reset_index(drop=True)
    b = b[1:].reset_index(drop=True)      # shift so h:30 pairs with h+1:00
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    both = a.notna() & b.notna()
    same = (a[both] == b[both]).sum()
    print(f"  {c:34s} pairs={both.sum():5d}  identical={same:5d} "
          f"({100*same/max(both.sum(),1):6.2f} %)")


# ---------------------------------------------------------------- solar geometry
def solar_zenith(times, lat=LAT, lon=LON):
    """NOAA solar position. `times` naive UTC DatetimeIndex. Returns SZA in degrees."""
    ti = pd.DatetimeIndex(times)
    doy = np.asarray(ti.dayofyear, dtype="float64")
    hrs = (np.asarray(ti.hour) + np.asarray(ti.minute) / 60
           + np.asarray(ti.second) / 3600).astype("float64")
    ydays = np.where(np.asarray(ti.is_leap_year), 366.0, 365.0)
    g = 2 * np.pi / ydays * (doy - 1 + (hrs - 12) / 24)
    eqtime = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g)
                       - 0.014615 * np.cos(2 * g) - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g)
            - 0.006758 * np.cos(2 * g) + 0.000907 * np.sin(2 * g)
            - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    tst = hrs * 60 + eqtime + 4 * lon          # true solar time, minutes (UTC base)
    ha = np.deg2rad(tst / 4 - 180)
    la = np.deg2rad(lat)
    cosz = np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha)
    return np.rad2deg(np.arccos(np.clip(cosz, -1, 1)))


def scan_offset(series, times, label, lo=-180, hi=180, step=5):
    """Find the offset D (minutes) such that SZA evaluated at t+D best explains series."""
    m = series.notna().to_numpy()
    y = series.to_numpy(dtype="float64")[m]
    tt = pd.DatetimeIndex(times)[m]
    best, rows = None, []
    for dmin in range(lo, hi + 1, step):
        sza = solar_zenith(tt + pd.Timedelta(minutes=dmin))
        x = np.cos(np.deg2rad(sza)).clip(min=0)      # solar elevation proxy
        if x.std() == 0:
            continue
        r = np.corrcoef(x, y)[0, 1]
        rows.append((dmin, r))
        if best is None or r > best[1]:
            best = (dmin, r)
    print(f"\n  {label}: best offset = {best[0]:+d} min   (r = {best[1]:.4f})")
    near = [f"{d:+d}:{r:.4f}" for d, r in rows if abs(d - best[0]) <= 30]
    print(f"    neighbourhood  {'  '.join(near)}")
    return best


hr("7. MET TIMING vs SOLAR GEOMETRY (claim: about -55 min)")
radcol = [c for c in groups["met"] if "Radiation" in c][0]
print(f"  using {radcol}")
scan_offset(df[radcol], t, "global radiation")

hr("8. GAS TIMING via PHOTOSTATIONARY PROXY (claim: about -10 min)")
gname = {c.split(" ")[0]: c for c in groups["gas"]}
NO = df[gname["gas_NO"]] / 1.25
NO2 = df[gname["gas_NO2"]] / 1.91
O3 = df[gname["gas_O3"]] / 2.0
proxy = (NO * O3 / NO2).replace([np.inf, -np.inf], np.nan)
print(f"  proxy n={proxy.notna().sum()}  median={proxy.median():.3f} ppb")
scan_offset(proxy, t, "NO*O3/NO2 proxy")
print("\n  control: same scan on O3 alone")
scan_offset(df[gname["gas_O3"]], t, "O3")

hr("9. RADIATION DIURNAL BY LABEL (where does the centroid sit?)")
rad = df[[radcol]].copy()
rad["h"] = t.dt.hour + t.dt.minute / 60
prof = rad.groupby("h")[radcol].mean()
print(prof.round(1).to_string())
w = prof.clip(lower=0)
centroid = (prof.index * w).sum() / w.sum()
print(f"\n  peak label     : {prof.idxmax():.1f} h  (value {prof.max():.1f})")
print(f"  centroid label : {centroid:.3f} h = {int(centroid)}:{round((centroid%1)*60):02d}"
      f"   (claim: 12:08)")
sza_noon = solar_zenith(pd.DatetimeIndex(
    pd.date_range("2025-09-25 10:00", "2025-09-25 13:00", freq="1min")))
tn = pd.date_range("2025-09-25 10:00", "2025-09-25 13:00", freq="1min")[sza_noon.argmin()]
print(f"  true solar noon Paris 25 Sep 2025: {tn.strftime('%H:%M')} UTC  (claim: ~11:40)")

hr("10. COLUMNS NEEDED BY live_template")
want = ["H3O_C6H7+", "H3O_C7H9+", "H3O_C8H11+", "H3O_C10H31O5Si5+", "H3O_C5H9+",
        "H3O_C10H17+", "H3O_C9H19O+", "H3O_C3H7O+", "H3O_C2H5O+"]
for c in want:
    print(f"  {c:22s} present={c in cols}")
print()
for c in ["gas_NO", "gas_NO2", "gas_CO", "gas_O3", "gas_eBCff", "gas_eBCwb"]:
    match = [x for x in cols if x.split(" ")[0] == c]
    print(f"  {c:12s} -> {match}")

hr("11. COVERAGE IN THE TWO WINDOWS")
for name, lo, hi in [("live subset  22 Sep - 5 Oct", "2025-09-22 00:00", "2025-10-05 23:30"),
                     ("figure window 6 - 13 Oct", "2025-10-06 00:00", "2025-10-13 23:30")]:
    m = (t >= lo) & (t <= hi)
    sub = df[m.to_numpy()]
    print(f"\n{name}   rows={len(sub)}")
    check = want + [gname[k] for k in
                    ["gas_NO", "gas_NO2", "gas_CO", "gas_O3", "gas_eBCff", "gas_eBCwb"]] \
            + groups["met"]
    for c in check:
        if c in sub.columns:
            pct = 100 * sub[c].notna().sum() / len(sub)
            flag = "  <-- POOR" if pct < 70 else ""
            print(f"    {c:36s} {pct:6.1f} % valid{flag}")
