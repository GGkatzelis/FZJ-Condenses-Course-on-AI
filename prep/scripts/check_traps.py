"""Quantify each planted trap on the live_template data, so trap_log.md carries
real numbers and we know which prompts are needed to make each one surface."""
import numpy as np
import pandas as pd
from pathlib import Path

CSV = (Path(__file__).parents[2] / "live_template" / "data"
       / "MONALISA_Paris_2025.csv")
df = pd.read_csv(CSV)
t = pd.to_datetime(df["time"])
df["date"] = t.dt.date
is00 = (t.dt.minute == 0).to_numpy()

PRECIP = "met_Precipitation (mm)"
RAD = "met_Global_Radiation (J/cm2)"
SUN = None


def hdr(x):
    print("\n" + "=" * 74 + f"\n{x}\n" + "=" * 74)


hdr("TRAP 1 - met duplication: sums double, means do not")
for col, unit in [(PRECIP, "mm"), (RAD, "J/cm2")]:
    naive_total = df[col].sum()
    true_total = df.loc[is00, col].sum()
    naive_mean = df[col].mean()
    true_mean = df.loc[is00, col].mean()
    print(f"\n  {col}")
    print(f"    SUM  over all rows   {naive_total:12.2f} {unit}")
    print(f"    SUM  de-duplicated   {true_total:12.2f} {unit}"
          f"   ratio {naive_total / true_total:.3f}")
    print(f"    MEAN over all rows   {naive_mean:12.4f} {unit}")
    print(f"    MEAN de-duplicated   {true_mean:12.4f} {unit}"
          f"   ratio {naive_mean / true_mean:.4f}")

print("\n  >>> CONSEQUENCE FOR THE DEMO:")
print("      The trap only fires on a SUM. Any mean/median is immune, because the")
print("      mean of a duplicated value is unchanged. The app's 'daily' averaging")
print("      uses .mean(), so the trap will NOT surface unless a prompt explicitly")
print("      asks for a TOTAL (rainfall total, daily radiation dose, etc).")

hdr("TRAP 1b - wettest day, and does the ranking survive?")
naive = df.groupby("date")[PRECIP].sum()
true = df.loc[is00].groupby("date")[PRECIP].sum()
comp = pd.DataFrame({"naive_sum": naive, "true_sum": true})
comp["ratio"] = comp.naive_sum / comp.true_sum.replace(0, np.nan)
print(comp.round(2).to_string())
print(f"\n  wettest day naive: {naive.idxmax()} at {naive.max():.1f} mm")
print(f"  wettest day true : {true.idxmax()} at {true.max():.1f} mm")
print(f"  ranking identical: {list(naive.sort_values().index) == list(true.sort_values().index)}")
print("  -> the RANKING is preserved; only the magnitude is wrong. So the tell is")
print("     'that is twice the real rainfall', not 'the wrong day is wettest'.")

hdr("TRAP 1c - a sharper version: per-30-min-bin consecutive duplicates")
d = df[[PRECIP, RAD]].copy()
for col in [PRECIP, RAD]:
    pairs = df.loc[is00, col].reset_index(drop=True)
    pairs2 = df.loc[~is00, col].reset_index(drop=True)
    n = min(len(pairs), len(pairs2))
    same = (pairs[:n] == pairs2[:n]).sum()
    print(f"  {col:32s} {same}/{n} consecutive pairs identical "
          f"({100 * same / n:.1f} %)")
print("  -> a single df.head(6) on the met columns shows this immediately, if")
print("     anyone looks. Radiation at night is all zeros, so use daytime rows.")
print("\n  daytime sample (10:00-12:30):")
m = (t.dt.hour.between(10, 12)).to_numpy()
print(df.loc[m, ["time", RAD, "met_Sheltered_Temperature (C)"]].head(6).to_string(index=False))

hdr("TRAP 2 - time zone")
tol = "H3O_C7H9+"
prof = df.groupby(t.dt.hour)[tol].mean()
print(f"  toluene mean diurnal peaks at hour {int(prof.idxmax())} in file time")
print(f"  Paris local time in late Sep/early Oct = UTC+2 (CEST)")
print(f"  so a local-time reading would place that peak at "
      f"{(int(prof.idxmax()) + 2) % 24:02d}:00 local")
no = "gas_NO (microg/m3)"
pno = df.groupby(t.dt.hour)[no].mean()
print(f"  NO mean diurnal peaks at hour {int(pno.idxmax())} in file time "
      f"-> {(int(pno.idxmax()) + 2) % 24:02d}:00 local")
print("  -> morning traffic at 06-07 file time is 08-09 local, which is right for")
print("     Paris. Reading the file as local time makes rush hour look an hour")
print("     early twice over. The tell is a rush hour that sits too early.")

hdr("TRAP 3 - mixed units")
gas = [c for c in df.columns if c.startswith("gas_")]
for c in gas:
    print(f"  {c:32s} median {df[c].median():9.3f}")
print("\n  CO is in mg/m3, everything else in microg/m3: a factor 1000.")
print("  Plotting gas_CO on the same axis as gas_NO2 makes CO look like zero;")
print("  summing them silently under-weights CO by 1000x.")
print(f"  gas_CO median {df['gas_CO (mg/m3)'].median():.4f} mg/m3 "
      f"= {df['gas_CO (mg/m3)'].median() * 1000:.1f} microg/m3")

hdr("TRAP 4 - eBC is aerosol, not gas")
print("  gas_eBCff / gas_eBCwb carry the gas_ prefix but are particulate black")
print("  carbon from an absorption instrument. Any 'total gas-phase burden' that")
print("  adds them is wrong.")
print(f"  eBCff median {df['gas_eBCff (microg/m3)'].median():.3f} microg/m3, "
      f"eBCwb {df['gas_eBCwb (microg/m3)'].median():.3f}")

hdr("TRAP 5 - negative ion values")
ions = [c for c in df.columns if c.startswith("H3O_")]
tot = 0
for c in ions:
    n = int((df[c] < 0).sum())
    tot += n
    if n:
        print(f"  {c:22s} {n:4d} negative  (min {df[c].min():.1f})")
print(f"  total negative ion cells: {tot}")
print("  -> clipping them at zero, or dropping those rows, biases the low end.")
print("     They are real background-subtracted values.")

hdr("TRAP 6 - missing data")
for grp, cols in [("H3O ions", ions), ("gas", gas),
                  ("met", [c for c in df.columns if c.startswith("met_")])]:
    v = np.mean([df[c].notna().mean() for c in cols]) * 100
    print(f"  {grp:10s} mean coverage {v:5.1f} %")
print("  -> fillna(0) anywhere here drags every mean downward by ~11 %.")
