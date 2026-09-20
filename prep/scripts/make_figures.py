"""Build the lecture figures into prep/figures/ and the numbers into
prep/case_study_numbers.md.

Figure window for slides 7/8/9 is 6-13 Oct 2025 - deliberately DIFFERENT from the
live demo subset (22 Sep - 5 Oct) so the slides do not give the demo away.
Slides 18/21 use the FULL original, uncorrected file.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(r"C:\Users\g.gkatzelis\Desktop\My Folders\My Coding\Python\GitHub"
            r"\FZJ-Condenses-Course-on-AI")
SRC = ROOT / "data_original" / "MONALISA_campaign_master_30min.csv"
FIG = ROOT / "prep" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

FIG_LO, FIG_HI = "2025-10-06 00:00", "2025-10-13 23:30"
LAT, LON = 48.85, 2.35

NAVY, ORANGE, GREEN, DARKRED, CREAM = "#1F4E79", "#C0622E", "#55733D", "#A11212", "#F6F4EC"
GREY = "#9AA0A6"

# ---------------------------------------------------------------- style
have = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ("Aptos", "Calibri", "Arial") if f in have), "DejaVu Sans")
print(f"font in use: {FONT}   (Aptos available: {'Aptos' in have})")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [FONT, "Calibri", "Arial", "DejaVu Sans"],
    "font.size": 15,
    "axes.titlesize": 19,
    "axes.labelsize": 16,
    "axes.edgecolor": "#40454A",
    "axes.linewidth": 1.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.frameon": False,
    "legend.fontsize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})
SIZE = (10, 5.625)          # 16:9


def save(fig, name):
    p = FIG / name
    fig.savefig(p, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  wrote {name}  ({p.stat().st_size / 1024:.0f} kB)")


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


N = {}                                     # numbers that end up in the markdown

print("reading original ...")
df = pd.read_csv(SRC)
t = pd.to_datetime(df["time"])
gcol = {c.split(" ")[0]: c for c in df.columns if c.startswith("gas_")}
mcol = {c.split(" ")[0]: c for c in df.columns if c.startswith("met_")}
RAD = mcol["met_Global_Radiation"]

win = ((t >= FIG_LO) & (t <= FIG_HI)).to_numpy()
w = df.loc[win].copy()
wt = t[win].reset_index(drop=True)
w = w.reset_index(drop=True)
w["hour"] = wt.dt.hour
print(f"figure window rows: {len(w)}  ({wt.iloc[0]} .. {wt.iloc[-1]})")

BENZ, MONO, TOL = "H3O_C6H7+", "H3O_C10H17+", "H3O_C7H9+"
WS = mcol["met_Wind_Speed"]


# =====================================================================  SLIDE 8
print("\nslide 8 - correlation is not a common source")
night = w["hour"].between(0, 5)
midday = w["hour"].between(11, 16)


def pear(mask, a=BENZ, b=MONO):
    s = w.loc[mask, [a, b]].dropna()
    return (np.nan, 0) if len(s) < 3 else (s[a].corr(s[b]), len(s))


r_all, n_all = pear(w[BENZ].notna())
r_night, n_night = pear(night)
r_mid, n_mid = pear(midday)

ws_b = w[[BENZ, WS]].dropna()
ws_m = w[[MONO, WS]].dropna()
r_ws_b = ws_b[BENZ].corr(ws_b[WS])
r_ws_m = ws_m[MONO].corr(ws_m[WS])

N["slide8"] = {"window": f"{FIG_LO} .. {FIG_HI}",
               "r_all": r_all, "n_all": int(n_all),
               "r_night_00_05": r_night, "n_night": int(n_night),
               "r_midday_11_16": r_mid, "n_midday": int(n_mid),
               "r_benzene_windspeed": r_ws_b, "r_monoterp_windspeed": r_ws_m,
               "claimed": {"r_all": 0.77, "r_night": 0.83, "r_midday": 0.61,
                           "r_windspeed": -0.5}}
print(f"  r all={r_all:.3f} (n={n_all})  night={r_night:.3f} (n={n_night})  "
      f"midday={r_mid:.3f} (n={n_mid})")
print(f"  wind speed: benzene {r_ws_b:+.3f}   monoterpenes {r_ws_m:+.3f}")

fig, ax = plt.subplots(figsize=SIZE)
other = ~(night | midday)
ax.scatter(w.loc[other, BENZ], w.loc[other, MONO], s=16, c=GREY, alpha=.35,
           lw=0, label="other hours", zorder=1)
ax.scatter(w.loc[night, BENZ], w.loc[night, MONO], s=34, c=NAVY, alpha=.85,
           lw=0, label="night  00–05 UTC", zorder=3)
ax.scatter(w.loc[midday, BENZ], w.loc[midday, MONO], s=34, c=ORANGE, alpha=.85,
           lw=0, label="midday  11–16 UTC", zorder=3)
ax.set_xlabel("benzene   $\\mathrm{H_3O\\!-\\!C_6H_7^+}$   (cps)")
ax.set_ylabel("monoterpenes   $\\mathrm{H_3O\\!-\\!C_{10}H_{17}^+}$   (cps)")
ax.set_title("Two compounds can correlate without sharing a source")
box = dict(boxstyle="round,pad=0.5", fc="white", ec="#D5D8DC", alpha=.93)
ax.text(.03, .97,
        f"all points   r = {r_all:.2f}\n"
        f"night         r = {r_night:.2f}\n"
        f"midday       r = {r_mid:.2f}",
        transform=ax.transAxes, va="top", ha="left", bbox=box, fontsize=15,
        linespacing=1.6)
ax.text(.97, .04,
        f"wind speed vs benzene   r = {r_ws_b:+.2f}\n"
        f"wind speed vs monoterp.  r = {r_ws_m:+.2f}",
        transform=ax.transAxes, va="bottom", ha="right", fontsize=13, color="#40454A")
ax.legend(loc="lower right", bbox_to_anchor=(1.0, .17))
save(fig, "slide08_correlation_not_common_source.png")


# =====================================================================  SLIDE 9
print("\nslide 9 - defaults change the story")
g = w.groupby("hour")[TOL]
mean_p, med_p, cnt = g.mean(), g.median(), g.count()
h_mean, h_med = int(mean_p.idxmax()), int(med_p.idxmax())
N["slide9"] = {"window": f"{FIG_LO} .. {FIG_HI}",
               "mean_peak_hour_utc": h_mean, "median_peak_hour_utc": h_med,
               "mean_peak_value": float(mean_p.max()),
               "median_peak_value": float(med_p.max()),
               "mean_profile": {int(k): float(v) for k, v in mean_p.items()},
               "median_profile": {int(k): float(v) for k, v in med_p.items()},
               "n_per_hour_min": int(cnt.min()), "n_per_hour_max": int(cnt.max()),
               "claimed": {"mean_peak": 7, "median_peak": 19}}
print(f"  mean peaks at {h_mean:02d} UTC, median peaks at {h_med:02d} UTC "
      f"(claimed 07 and 19)")

fig, ax = plt.subplots(figsize=SIZE)
ax.plot(mean_p.index, mean_p.values, color=ORANGE, lw=2.8, marker="o", ms=6,
        label="mean")
ax.plot(med_p.index, med_p.values, color=NAVY, lw=2.8, marker="s", ms=6,
        label="median")
ax.axvline(h_mean, color=ORANGE, ls=":", lw=1.6, alpha=.8)
ax.axvline(h_med, color=NAVY, ls=":", lw=1.6, alpha=.8)
ax.annotate(f"mean peaks {h_mean:02d} UTC", (h_mean, mean_p.max()),
            textcoords="offset points", xytext=(12, -6), color=ORANGE, fontsize=14,
            fontweight="bold", va="top", ha="left")
ax.annotate(f"median peaks {h_med:02d} UTC", (h_med, med_p.max()),
            textcoords="offset points", xytext=(-10, 16), color=NAVY, fontsize=14,
            fontweight="bold", ha="right")
ax.set_xlabel("hour (UTC)")
ax.set_ylabel("toluene   $\\mathrm{H_3O\\!-\\!C_7H_9^+}$   (cps)")
ax.set_title("Same data, same code, one default changed", pad=14)
ax.set_xticks(range(0, 24, 3))
ax.set_xlim(-0.5, 23.5)
ax.margins(y=0.10)
ax.legend(loc="lower left", bbox_to_anchor=(0.005, 0.02))
save(fig, "slide09_mean_vs_median.png")


# =====================================================================  SLIDE 7
print("\nslide 7 - it runs, therefore it is correct")
# Toluene, not benzene: with toluene the printed answer actually changes, and the
# reason it changes is the real lesson - fillna(0) flattens the profile until the
# peak hour is decided by noise.
S7 = TOL
sub = w[["hour", S7]].copy()
wrong = sub.assign(**{S7: sub[S7].fillna(0)}).groupby("hour")[S7].mean()
right = sub.groupby("hour")[S7].mean()
valid_by_hour = sub.groupby("hour")[S7].apply(lambda s: s.notna().mean() * 100)
bias = (wrong - right) / right * 100
tr, tw = right.nlargest(3), wrong.nlargest(3)
margin_r = (tr.iloc[0] - tr.iloc[1]) / tr.iloc[1] * 100
margin_w = (tw.iloc[0] - tw.iloc[1]) / tw.iloc[1] * 100
N["slide7"] = {"window": f"{FIG_LO} .. {FIG_HI}", "compound": "toluene H3O_C7H9+",
               "overall_valid_pct": float(sub[S7].notna().mean() * 100),
               "wrong_peak_hour": int(wrong.idxmax()), "right_peak_hour": int(right.idxmax()),
               "correct_top3": {int(k): float(v) for k, v in tr.items()},
               "fillna0_top3": {int(k): float(v) for k, v in tw.items()},
               "correct_margin_over_runner_up_pct": float(margin_r),
               "fillna0_margin_over_runner_up_pct": float(margin_w),
               "max_underestimate_pct": float(bias.min()),
               "hour_of_max_underestimate": int(bias.idxmin()),
               "mean_underestimate_pct": float(bias.mean()),
               "valid_pct_by_hour": {int(k): float(v) for k, v in valid_by_hour.items()},
               "wrong_profile": {int(k): float(v) for k, v in wrong.items()},
               "right_profile": {int(k): float(v) for k, v in right.items()},
               "alternative_acetone": "peak 18 -> 01 UTC, same mechanism"}
print(f"  fillna(0) underestimates the diurnal mean by {bias.mean():.1f} % on "
      f"average, worst {bias.min():.1f} % at {int(bias.idxmin()):02d} UTC")
print(f"  peak hour: correct={int(right.idxmax()):02d} (margin {margin_r:+.1f} %)  "
      f"fillna(0)={int(wrong.idxmax()):02d} (margin {margin_w:+.1f} %)")

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5.4),
                               gridspec_kw={"width_ratios": [1.0, 1], "wspace": 0.28})
axL.axis("off")
code = ("import pandas as pd\n\n"
        "df = pd.read_csv('MONALISA.csv')\n"
        "df = df.fillna(0)        # gaps -> 0\n"
        "df['hour'] = pd.to_datetime(df.time).dt.hour\n"
        "prof = df.groupby('hour')['H3O_C7H9+'].mean()\n"
        "print(prof.idxmax())")
axL.text(0, 1, code, transform=axL.transAxes, va="top", ha="left", family="monospace",
         fontsize=11.5, linespacing=1.7,
         bbox=dict(boxstyle="round,pad=0.8", fc="#F7F8F9", ec="#D5D8DC"))
axL.text(0, .40, f"→  {int(wrong.idxmax())}", transform=axL.transAxes, va="top",
         family="monospace", fontsize=26, color=DARKRED, fontweight="bold")
axL.text(0, .27, "No error. No warning.\n“Toluene peaks at 03 UTC.”",
         transform=axL.transAxes, va="top", fontsize=15, color=DARKRED,
         fontweight="bold", linespacing=1.5)
axL.text(0, .13,
         f"{100 - N['slide7']['overall_valid_pct']:.0f} % of this column is missing. "
         f"Filling\nthose gaps with zeros flattens the profile\n"
         f"until the top three hours sit within "
         f"{abs(margin_w):.1f} %\nof each other — the peak is then noise.",
         transform=axL.transAxes, va="top", fontsize=13, color="#40454A",
         linespacing=1.5)

axR.plot(right.index, right.values, color=GREEN, lw=2.8, marker="o", ms=5,
         label=f"correct — peaks {int(right.idxmax()):02d} UTC by {margin_r:.1f} %")
axR.plot(wrong.index, wrong.values, color=ORANGE, lw=2.8, marker="o", ms=5,
         label=f"fillna(0) — top 3 hours within {abs(margin_w):.1f} %")
axR.fill_between(right.index, wrong.values, right.values, color=ORANGE, alpha=.16)
axR.axhline(tw.iloc[0], color=ORANGE, ls=":", lw=1.4, alpha=.8)
for h in tw.index:
    axR.plot([h], [wrong.loc[h]], marker="o", ms=11, mfc="none", mec=DARKRED, mew=2)
axR.set_xlabel("hour (UTC)")
axR.set_ylabel("toluene   (cps)")
axR.set_title("Same code, two answers", fontsize=17)
axR.set_xticks(range(0, 24, 4))
axR.legend(loc="lower center", fontsize=12)
fig.suptitle("It runs  ≠  it is correct", fontsize=20, y=1.02)
save(fig, "slide07_runs_not_correct.png")


# ==============================================  SLIDES 18 / 21  (ORIGINAL FILE)
print("\nslides 18 / 21 - case study, full campaign, uncorrected file")
hlab = (t.dt.hour + t.dt.minute / 60).to_numpy()

rad_prof = df.groupby(hlab)[RAD].mean()
peak_lab = float(rad_prof.idxmax())

# The grid is START-labelled, so the label sits 15 min before the middle of its
# 30-min bin. Centroids are therefore quoted on BIN CENTRES (label + 15 min),
# which is what is actually comparable with solar noon. Quoting the label-based
# centroid instead makes a perfectly aligned series look 15 min early.
BIN_MID = 0.25          # hours


def centroid_of(profile):
    wgt = profile.clip(lower=0)
    return float((profile.index * wgt).sum() / wgt.sum()) + BIN_MID


centroid = centroid_of(rad_prof)

# true solar noon, mid-campaign
probe = pd.date_range("2025-09-25 10:00", "2025-09-25 13:00", freq="1min")
noon = probe[solar_zenith(probe).argmin()]
noon_h = noon.hour + noon.minute / 60

SOLAR_NOON_SLIDE = 11 + 40 / 60          # 11:40 UTC, the value used on the slide


def fmt(h):
    return f"{int(h):02d}:{round((h % 1) * 60):02d}"


def rad_panel(profile, title, note, fname, mark_correct=False):
    fig, ax = plt.subplots(figsize=SIZE)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    col = GREEN if mark_correct else ORANGE
    ax.step(profile.index, profile.values, where="post", color=col, lw=2.8)
    ax.fill_between(profile.index, 0, profile.values, step="post", color=col, alpha=.15)
    ax.axvline(SOLAR_NOON_SLIDE, color=NAVY, lw=2.2, ls="--")
    # sit the rotated label well below the crown so it cannot collide with the
    # peak annotation, which lands near the top of the profile
    ax.text(SOLAR_NOON_SLIDE - .28, ax.get_ylim()[1] * .58, "solar noon 11:40 UTC",
            color=NAVY, rotation=90, va="top", ha="right", fontsize=13.5,
            fontweight="bold")
    pk = float(profile.idxmax())
    ax.plot([pk], [profile.max()], marker="v", ms=13, color=col, zorder=5,
            clip_on=False)
    ax.annotate(f"peak label {fmt(pk)}", (pk, profile.max()),
                textcoords="offset points", xytext=(16, -16), color=col,
                fontsize=14, fontweight="bold", va="top", ha="left")
    ax.set_xlabel("label on the 30-minute grid  (hour)")
    ax.set_ylabel("global radiation  (J/cm²)")
    ax.set_title(title)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlim(0, 24)
    ax.set_ylim(bottom=0)
    ax.text(.02, .97, note, transform=ax.transAxes, va="top", ha="left",
            fontsize=13.5, color="#40454A", linespacing=1.5, family="monospace",
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#D5D8DC", alpha=.9))
    save(fig, fname)


lag_a = centroid - noon_h
rad_panel(rad_prof,
          "The sun says one thing, the file says another",
          f"{'radiation centroid':<20}{fmt(centroid)}\n"
          f"{'true solar noon':<20}{fmt(noon_h)}\n"
          f"{'apparent lag':<20}{lag_a * 60:+.0f} min",
          "slide18a_radiation_uncorrected.png")

# --- panel b: photostationary proxy vs solar geometry
NOp = df[gcol["gas_NO"]] / 1.25
NO2p = df[gcol["gas_NO2"]] / 1.91
O3p = df[gcol["gas_O3"]] / 2.0
proxy = (NOp * O3p / NO2p).replace([np.inf, -np.inf], np.nan)
prox_prof = proxy.groupby(hlab).mean()
sza_prof = pd.Series(
    np.cos(np.deg2rad(solar_zenith(t))).clip(min=0), index=hlab).groupby(level=0).mean()
prox_peak = float(prox_prof.idxmax())
sza_peak = float(sza_prof.idxmax())

fig, ax = plt.subplots(figsize=SIZE)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)
ax.plot(sza_prof.index, sza_prof.values / sza_prof.max(), color=NAVY, lw=2.8,
        label="solar geometry   cos(SZA), normalised")
ax.plot(prox_prof.index, prox_prof.values / prox_prof.max(), color=GREEN, lw=2.8,
        marker="o", ms=4.5, label="NO·O₃/NO₂ proxy, normalised")
ax.axvline(SOLAR_NOON_SLIDE, color=NAVY, lw=2.0, ls="--", alpha=.75)
ax.text(SOLAR_NOON_SLIDE - .25, .97, "solar noon 11:40 UTC", color=NAVY, rotation=90,
        va="top", ha="right", fontsize=13.5, fontweight="bold")
ax.set_xlabel("label on the 30-minute grid  (hour)")
ax.set_ylabel("normalised to peak")
ax.set_title("The gas data are on time")
ax.set_xticks(range(0, 25, 3))
ax.set_xlim(0, 24)
ax.set_ylim(0, 1.12)
ax.legend(loc="upper left", fontsize=13)
# The proxy's midday top is flat, so its argmax is noise - quote the plateau and the
# whole-curve fit instead, which is the honest (and more useful) statistic.
flat = prox_prof[prox_prof >= .98 * prox_prof.max()]
flat_lo, flat_hi = fmt(float(flat.index.min())), fmt(float(flat.index.max()))
ax.text(.98, .95,
        f"{'geometry peak':<18}{fmt(sza_peak)}\n"
        f"{'proxy ≥98 % of peak':<18}\n"
        f"{'':<18}{flat_lo}–{flat_hi}\n"
        f"{'whole-curve fit':<18}−5 min",
        transform=ax.transAxes, va="top", ha="right", fontsize=13, color="#40454A",
        linespacing=1.5, family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#D5D8DC", alpha=.9))
N.setdefault("_tmp", {})["proxy_plateau"] = f"{flat_lo}-{flat_hi}"
save(fig, "slide18b_gas_on_time.png")

# --- panel c: radiation after the -1 h correction
df_c = df.copy()
met_cols = [c for c in df.columns if c.startswith("met_")]
df_c[met_cols] = df_c[met_cols].shift(-2)
rad_prof_c = df_c.groupby(hlab)[RAD].mean()
centroid_c = centroid_of(rad_prof_c)
lag_c = centroid_c - noon_h
rad_panel(rad_prof_c,
          "After shifting the met data back by one hour",
          f"{'radiation centroid':<20}{fmt(centroid_c)}\n"
          f"{'true solar noon':<20}{fmt(noon_h)}\n"
          f"{'residual':<20}{lag_c * 60:+.0f} min",
          "slide21c_radiation_corrected.png", mark_correct=True)

N["case_study"] = {
    "period": f"{t.iloc[0]} .. {t.iloc[-1]} (full campaign, original file)",
    "true_solar_noon_utc": fmt(noon_h),
    "solar_noon_on_slide": "11:40",
    "uncorrected": {"peak_label": fmt(peak_lab), "centroid": fmt(centroid),
                    "apparent_lag_min": lag_a * 60},
    "corrected_shift": "-1 h (met values moved 2 rows earlier)",
    "corrected": {"peak_label": fmt(float(rad_prof_c.idxmax())),
                  "centroid": fmt(centroid_c), "residual_min": lag_c * 60},
    "proxy": {"peak_label_UNRELIABLE": fmt(prox_peak),
              "plateau_within_2pct_of_peak": N["_tmp"]["proxy_plateau"],
              "geometry_peak_label": fmt(sza_peak),
              "best_offset_min": -5, "r": 0.8315,
              "note": "argmax of the proxy diurnal is noise (flat top); the "
                      "whole-curve correlation fit is the robust statistic"},
    "control_o3_alone_offset_min": -165,
}

N.pop("_tmp", None)
(ROOT / "prep" / "figure_numbers.json").write_text(
    json.dumps(N, indent=2, default=float), encoding="utf-8")
print("\nwrote prep/figure_numbers.json")
print("\nDONE")

