"""Build live_template/data from the FULL campaign file.

Georgios' decision (2026-09-20): use all the data, not a two-week subset - the
campaign approved it, and the full file is both more realistic and richer in
traps.

What is changed from the original, and nothing else:
  * met columns shifted -1 h (2 rows) to correct the end-of-hour labelling on a
    start-labelled grid. The duplication is deliberately preserved.
  * nothing dropped: all 881 columns are kept, n_ bookkeeping included.
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parents[2]
SRC = ROOT / "data_original" / "MONALISA_campaign_master_30min.csv"
OUT = ROOT / "live_template" / "data" / "MONALISA_Paris_2025.csv"
LAT, LON = 48.85, 2.35


def hdr(x):
    print("\n" + "=" * 74 + f"\n{x}\n" + "=" * 74)


def solar_zenith(times):
    ti = pd.DatetimeIndex(times)
    doy = np.asarray(ti.dayofyear, dtype="float64")
    hrs = (np.asarray(ti.hour) + np.asarray(ti.minute) / 60).astype("float64")
    ydays = np.where(np.asarray(ti.is_leap_year), 366.0, 365.0)
    g = 2 * np.pi / ydays * (doy - 1 + (hrs - 12) / 24)
    eq = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g)
                   - 0.014615 * np.cos(2 * g) - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g)
            - 0.006758 * np.cos(2 * g) + 0.000907 * np.sin(2 * g)
            - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    ha = np.deg2rad((hrs * 60 + eq + 4 * LON) / 4 - 180)
    la = np.deg2rad(LAT)
    return np.rad2deg(np.arccos(np.clip(
        np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha), -1, 1)))


def best_offset(series, times, lo=-150, hi=90, step=5):
    m = series.notna().to_numpy()
    y = series.to_numpy(dtype="float64")[m]
    tt = pd.DatetimeIndex(times)[m]
    rows = [(d, np.corrcoef(np.cos(np.deg2rad(solar_zenith(
        tt + pd.Timedelta(minutes=d)))).clip(min=0), y)[0, 1])
        for d in range(lo, hi + 1, step)]
    return max(rows, key=lambda r: r[1])


print("reading the full original ...")
df = pd.read_csv(SRC)
t = pd.to_datetime(df["time"])
met = [c for c in df.columns if c.startswith("met_")]
RAD = [c for c in met if "Radiation" in c][0]

hdr("MET ALIGNMENT")
d0, r0 = best_offset(df[RAD], t)
print(f"  before: best offset {d0:+d} min (r={r0:.4f})   expect about -45")
df[met] = df[met].shift(-2)
d1, r1 = best_offset(df[RAD], t)
print(f"  after : best offset {d1:+d} min (r={r1:.4f})   expect about +15")
print("  (+15 is correct on a START-labelled grid: the label sits 15 min before")
print("   the middle of its own 30-minute bin)")

hdr("DUPLICATION PRESERVED?")
is30 = (t.dt.minute == 30).to_numpy()
for c in met:
    a = df.loc[~is30, c].reset_index(drop=True)
    b = df.loc[is30, c].reset_index(drop=True)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    both = a.notna() & b.notna()
    print(f"  {c:34s} {100 * (a[both] == b[both]).sum() / max(both.sum(), 1):6.2f} %")

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"\nwrote {OUT}")
print(f"  {len(df)} rows x {df.shape[1]} columns, {OUT.stat().st_size / 1e6:.1f} MB")
print(f"  {t.iloc[0]} .. {t.iloc[-1]}")

# ----------------------------------------------------- traps the full file unlocks
hdr("NEW TRAP 1 - DST: the campaign spans the CEST -> CET transition")
print("  EU summer time ended on Sunday 26 October 2025 at 01:00 UTC.")
print(f"  The campaign runs {t.iloc[0].date()} to {t.iloc[-1].date()}, so the")
print("  transition is INSIDE the file.")
try:
    loc = t.dt.tz_localize("UTC").dt.tz_convert("Europe/Paris")
    off = loc.dt.utcoffset().dt.total_seconds() / 3600
    print(f"  UTC offset over the file: {sorted(off.unique())} hours")
    ch = off.diff().fillna(0) != 0
    if ch.any():
        i = int(np.argmax(ch.to_numpy()))
        print(f"  changes at UTC {t.iloc[i]}  ->  local {loc.iloc[i]}")
    # the ambiguous local hour
    naive_local = (t + pd.Timedelta(hours=2)).dt.strftime("%Y-%m-%d %H:%M")
    print(f"\n  If someone just does t + 2 h for the whole file, every timestamp")
    print(f"  after 26 Oct is wrong by one hour: {ch.sum()} rows affected -> "
          f"{(off == 1).sum()} rows are CET (+1), not CEST (+2).")
    print(f"  A correct tz_convert produces a REPEATED local hour on 26 Oct;")
    print(f"  a naive +2 h produces none, and silently shifts 10 % of the file.")
except Exception as exc:                                    # noqa: BLE001
    print("  (tz check unavailable:", exc, ")")

hdr("NEW TRAP 2 - NOX is in ppb while NO and NO2 are in microg/m3")
g = {c.split(" ")[0]: c for c in df.columns if c.startswith("gas_")}
NO, NO2, NOX = df[g["gas_NO"]], df[g["gas_NO2"]], df[g["gas_NOX"]]
naive = (NO + NO2)
print(f"  median NO   {NO.median():8.2f} microg/m3")
print(f"  median NO2  {NO2.median():8.2f} microg/m3")
print(f"  median NOX  {NOX.median():8.2f} ppb   <- DIFFERENT UNIT")
print(f"  naive NO+NO2 = {naive.median():.2f} 'microg/m3' vs NOX {NOX.median():.2f} ppb")
conv = (NO / 1.25 + NO2 / 1.91)
print(f"  converted to ppb: NO/1.25 + NO2/1.91 = {conv.median():.2f} ppb")
s = pd.concat([conv, NOX], axis=1).dropna()
print(f"  r(converted sum, NOX) = {s.iloc[:, 0].corr(s.iloc[:, 1]):.4f}, "
      f"ratio of medians = {conv.median() / NOX.median():.3f}")
print("  -> once converted they agree. Added raw, they do not. A 'NOX closure")
print("     check' is a perfect, self-contained unit trap.")

hdr("NEW TRAP 3 - the same compound appears twice, in two reagent-ion modes")
pairs = [("NH4_C3H10NO+", "H3O_C3H7O+", "acetone"),
         ("NH4_C10H17+", "H3O_C10H17+", "monoterpenes (if both present)")]
for a, b, name in pairs:
    if a in df.columns and b in df.columns:
        s = df[[a, b]].dropna()
        print(f"  {name}: {a} vs {b}")
        print(f"    n overlapping = {len(s)}  r = "
              f"{s[a].corr(s[b]):.3f}" if len(s) > 2 else "    no overlap")
        print(f"    medians {df[a].median():.0f} vs {df[b].median():.0f} cps "
              f"- same compound, different sensitivity, NOT interchangeable")
    else:
        print(f"  {name}: one of the pair is absent ({a in df.columns}, "
              f"{b in df.columns})")
print("\n  n_H3O == 0 in "
      f"{int((df['n_H3O'] == 0).sum())} of {len(df)} rows "
      f"({100 * (df['n_H3O'] == 0).mean():.0f} %) - the instrument duty-cycles")
print("  between reagent ions, so the two modes barely overlap in time.")
