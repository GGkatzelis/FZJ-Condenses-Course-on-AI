"""Build live_template/data/MONALISA_Paris_2025.csv from the untouched original.

MUST live in prep/ — it documents the met correction and would give the demo away.

Decisions (Georgios, 2026-09-19):
  * master grid is START-labelled  -> 12:00 means 12:00-12:30
  * met is hourly, END-of-hour labelled, duplicated into h:00 and h:30
    => value labelled H:00 covers [H-1:00, H:00], which on a start-labelled
       30-min grid is exactly the two bins labelled H-1:00 and H-0:30.
    => a uniform -1 h shift (2 rows) puts both copies exactly right.
  * the duplication is KEPT (deliberate live trap: doubled daily sums)
  * timestamps stay UTC and stay unlabelled (time zone is a live trap)
  * n_* bookkeeping columns are dropped
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(r"C:\Users\g.gkatzelis\Desktop\My Folders\My Coding\Python\GitHub"
            r"\FZJ-Condenses-Course-on-AI")
SRC = ROOT / "data_original" / "MONALISA_campaign_master_30min.csv"
OUT = ROOT / "live_template" / "data" / "MONALISA_Paris_2025.csv"

WIN_LO, WIN_HI = "2025-09-22 00:00", "2025-10-05 23:30"
LAT, LON = 48.85, 2.35

IONS = ["H3O_C6H7+", "H3O_C7H9+", "H3O_C8H11+",        # benzene, toluene, C8 aromatics
        "H3O_C10H31O5Si5+",                             # D5 siloxane
        "H3O_C5H9+", "H3O_C10H17+",                     # isoprene, monoterpenes
        "H3O_C9H19O+",                                  # nonanal
        "H3O_C3H7O+", "H3O_C2H5O+"]                     # acetone, acetaldehyde
GAS = ["gas_NO", "gas_NO2", "gas_CO", "gas_O3", "gas_eBCff", "gas_eBCwb"]
MET = ["met_Sheltered_Temperature", "met_Relative_Humidity", "met_Wind_Speed",
       "met_Wind_Direction", "met_Global_Radiation", "met_Precipitation"]


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


def best_offset(series, times, lo=-150, hi=90, step=5):
    m = series.notna().to_numpy()
    y = series.to_numpy(dtype="float64")[m]
    tt = pd.DatetimeIndex(times)[m]
    rows = [(d, np.corrcoef(
        np.cos(np.deg2rad(solar_zenith(tt + pd.Timedelta(minutes=d)))).clip(min=0), y)[0, 1])
        for d in range(lo, hi + 1, step)]
    return max(rows, key=lambda r: r[1])


print("reading original ...")
df = pd.read_csv(SRC)
t = pd.to_datetime(df["time"])

# resolve the real column names (they embed units, e.g. "gas_NO (microg/m3)")
def resolve(stems):
    out = []
    for s in stems:
        hit = [c for c in df.columns if c.split(" ")[0] == s]
        if len(hit) != 1:
            raise SystemExit(f"column stem {s!r} matched {hit}")
        out.append(hit[0])
    return out

gas_cols, met_cols = resolve(GAS), resolve(MET)
missing = [c for c in IONS if c not in df.columns]
if missing:
    raise SystemExit(f"missing ion columns: {missing}")

# ---- 1. correct the met alignment: shift values 1 h earlier = 2 rows up --------
print("\nmet alignment check, BEFORE correction (global radiation vs solar geometry):")
rad = [c for c in met_cols if "Radiation" in c][0]
d0, r0 = best_offset(df[rad], t)
print(f"   best offset {d0:+d} min (r={r0:.4f})   <- expect about -45")

df[met_cols] = df[met_cols].shift(-2)

print("met alignment check, AFTER  correction:")
d1, r1 = best_offset(df[rad], t)
# NB expect about +15, not 0: on a START-labelled grid the bin labelled L covers
# [L, L+30], so a correctly aligned value sits 15 min after its label by construction.
print(f"   best offset {d1:+d} min (r={r1:.4f})   <- expect about +15")

# ---- 2. confirm the duplication survived the shift ----------------------------
is30 = (t.dt.minute == 30).to_numpy()
print("\nduplication check after the shift (h:00 vs h:30 of the same hour):")
for c in met_cols:
    a = df.loc[~is30, c].reset_index(drop=True)
    b = df.loc[is30, c].reset_index(drop=True)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    both = a.notna() & b.notna()
    print(f"   {c:34s} {100 * (a[both] == b[both]).sum() / max(both.sum(), 1):6.2f} % identical")

# ---- 3. subset ----------------------------------------------------------------
keep = ["time"] + IONS + gas_cols + met_cols
sub = df.loc[((t >= WIN_LO) & (t <= WIN_HI)).to_numpy(), keep].copy()

OUT.parent.mkdir(parents=True, exist_ok=True)
sub.to_csv(OUT, index=False)

print(f"\nwrote {OUT}")
print(f"   rows    : {len(sub)}   ({sub['time'].iloc[0]} .. {sub['time'].iloc[-1]})")
print(f"   columns : {sub.shape[1]}")
print(f"   size    : {OUT.stat().st_size / 1024:.0f} kB")
print("\ncolumn coverage:")
for c in sub.columns[1:]:
    print(f"   {c:36s} {100 * sub[c].notna().sum() / len(sub):6.1f} % valid")

# ---- 4. show the trap still fires ---------------------------------------------
st = pd.to_datetime(sub["time"])
precip = [c for c in met_cols if "Precip" in c][0]
daily_naive = sub.groupby(st.dt.date)[precip].sum()
daily_true = sub.loc[(st.dt.minute == 0).to_numpy()].groupby(
    st[(st.dt.minute == 0).to_numpy()].dt.date)[precip].sum()
print(f"\nTRAP CHECK - precipitation total over the window")
print(f"   naive sum over all 30-min rows : {daily_naive.sum():.1f} mm")
print(f"   correct (de-duplicated) sum    : {daily_true.sum():.1f} mm")
print(f"   ratio                          : {daily_naive.sum() / daily_true.sum():.3f}")
