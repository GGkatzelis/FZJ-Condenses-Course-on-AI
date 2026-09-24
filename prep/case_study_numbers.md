# Case study — the numbers behind slides 18 and 21

Source: **the original, uncorrected** `MONALISA_campaign_master_30min.csv`,
**full campaign** 2025-09-01 00:00 → 2025-10-31 23:00.
Solar geometry: NOAA algorithm, Paris 48.85 °N, 2.35 °E, no external library.
Regenerate with `prep/scripts/make_figures.py`; raw values in `prep/figure_numbers.json`.

---

## Read this before you present it

The master grid is **start-labelled**: the label `12:00` means the interval
12:00–12:30, so its midpoint is **12:15**.

Every centroid below is therefore quoted on the **bin centre** (label + 15 min),
because that is the quantity actually comparable with solar noon. This matters:
if you quote the label-based centroid instead, a *perfectly aligned* series looks
15 minutes early, and the corrected panel appears to be over-corrected by
−16 min when it is in fact right. The figures use bin centres throughout.

---

## ⭐ `slide18_radiation_before_after.png` — use this one

Added 2026-09-24 at Georgios' request, and it supersedes panels (a) and (c) for
presentation purposes. One figure: solar geometry, the met as delivered, and the
same met shifted back an hour, with both centroids marked and the gap shaded.

| | centroid | vs sun |
|---|---|---|
| solar geometry | **11:42** | — |
| met as delivered | **12:41** | **+59 min** |
| met shifted back 1 h | **11:41** | **−1 min** |

### Why the old panel (a) was not usable

Georgios looked at it and said the solar-noon line appeared to sit *on* the
peak. He was right, and the figure was the problem, not the data. The
campaign-mean radiation profile is a **flat-topped plateau** — 11:00 to 14:00
varies by under 3 %, and 12:00 and 12:30 are exactly tied at 139.3169 because of
the met duplication. A one-hour shift of a plateau that flat is invisible, and
the +59 min is a property of the **centroid**, which the old figure never drew.
It asserted the error in a text box while showing apparent agreement.

The new figure fixes that by comparing two *curves* rather than a curve and a
line, and by drawing both centroids.

### ⚠️ A convention bug found while building it

The first version of the combined figure read **+44 min** instead of +59. Cause:
`centroid_of()` adds `BIN_MID` (+15 min) because the radiation values are **bin
means** whose label sits 15 min before the bin centre. The solar geometry is an
**instantaneous** function evaluated *at* the label, so it is already on true
time and must not get that correction. Applying it to both cancelled 15 of the
59 minutes. Fixed; the geometry centroid now prints as 11:42, matching true
solar noon exactly, which is the check that confirms it.

### If a student asks why the corrected curve sits above the sun in the morning

It does, and it is real, not a residual timing error:

| | radiation / geometry |
|---|---|
| morning 06:00–11:30 | **1.069** |
| afternoon 11:30–18:00 | **0.729** |

Afternoons were cloudier than mornings over this campaign. Total energy is
nearly balanced — 946 J/cm² morning against 912 afternoon — which is exactly why
the centroid still lands at −1 min despite the visible limb asymmetry.

---

## Panel (a) — `slide18a_radiation_uncorrected.png`

Mean diurnal of `met_Global_Radiation (J/cm2)` against the 30-minute label.

| Quantity | Value |
|---|---|
| Peak label | **12:00** |
| Radiation centroid (bin centre) | **12:41** |
| True solar noon, Paris, 25 Sep 2025 | **11:42 UTC** |
| Value used on the slide | 11:40 UTC |
| **Apparent lag** | **+59 min** |

The plotted profile is drawn as steps, which makes the **met duplication**
visible directly: every level is one hour wide because each hourly value occupies
two consecutive 30-minute bins.

## Panel (b) — `slide18b_gas_on_time.png`

Photostationary proxy **NO·O₃/NO₂**, with NO ÷ 1.25, NO₂ ÷ 1.91, O₃ ÷ 2.0 to
convert µg/m³ → ppb. n = 2,142; median 2.72 ppb. Plotted against normalised
`cos(SZA)`.

| Quantity | Value |
|---|---|
| Best-fit offset, whole curve | **−5 min** (r = 0.832) |
| Refined optimum | −6.2 min |
| Flat across | −15 … 0 min (r = 0.8306 / 0.8314 / 0.8315 / 0.8311) |
| Solar-geometry peak label | 11:30 (bin centre 11:45) |
| Proxy plateau, ≥98 % of peak | 12:00–13:30 (labels) |

**Conclusion: the gas data are on true UTC within ±15 min.** The briefing's
"−10 min" is indistinguishable from the −5 min optimum.

### Two caveats, in case a student presses you

1. **Do not quote the proxy's peak hour.** Its argmax lands at 13:00 and is
   meaningless — the midday top is flat, and the profile is mildly skewed later
   than solar noon because NOx emissions themselves vary through the day. The
   robust statistic is the correlation over the whole curve, which is what
   gives −5 min. This is the same lesson as slide 7: `idxmax()` on a flat
   profile reports noise with full confidence.
2. **Ozone alone is a trap.** The identical scan run on `gas_O3` by itself
   returns **−165 min** (r = 0.57), because ozone lags the sun by hours through
   boundary-layer growth and NO titration. This is a free, genuine demonstration
   of why the photostationary *ratio* is the right probe and a single species is
   not. Strongly recommended as a slide-21 aside.

## Panel (c) — `slide21c_radiation_corrected.png`

Correction applied: **met columns shifted −1 h** (values moved 2 rows earlier).

| Quantity | Value |
|---|---|
| Peak label | **11:00** |
| Radiation centroid (bin centre) | **11:41** |
| True solar noon | **11:42 UTC** |
| **Residual** | **−1 min** |

### Why −1 h is exactly right, not approximately right

A met value labelled `H:00` is an hourly mean **labelled at the end of its
hour**, so it covers `[H−1:00, H:00]`. On a start-labelled 30-minute grid that
hour is precisely the two bins labelled `H−1:00` and `H−0:30`. Shifting the met
block by −1 h moves the duplicated pair from `{H:00, H:30}` to
`{H−1:00, H−0:30}` — exactly the two bins the hour covers.

So the shift is exact, **and the duplication is preserved**, which keeps the
doubled-daily-sums trap intact for the live demo.

### Independent confirmation from the fit

Fitting radiation against solar geometry separately on each copy:

| Rows used | Best offset vs label |
|---|---|
| `h:00` only | **−30 min** |
| `h:30` only | **−60 min** |
| pooled (all rows) | **−45 min** |

```
   -30 min   end-of-hour labelling
   -15 min   the duplication, which drags the pair's mean label 15 min right
   -------
   -45 min   pooled, which is what a naive fit reports
```

The pooled −45 min is label-relative. A correctly aligned start-labelled bin
should fit at **+15 min** (the label sits 15 min before its centre), so the
required shift is −45 − 15 = **−60 min**. Which is what panel (c) applies, and
the residual comes out at −1 min.

> **Correction to the briefing:** the point estimate "−55 min" does not
> reproduce. The pooled optimum is −45 min and the curve is broad and shallow
> (r = 0.8468 at −60, 0.8504 at −45, 0.8481 at −30), so −55 min sits inside the
> noise but is not the maximum. The briefing's "45–60 min" *range* is exactly
> right, and now there is a mechanism for why it is a range.

---

## One number to be careful with

The radiation centroid depends on whether you de-duplicate first:

| Computed on | Label centroid | Bin-centre centroid |
|---|---|---|
| all 30-min rows (as the file ships) | 12:26 | **12:41** |
| `h:00` rows only (de-duplicated) | 12:11 | 12:26 |

The briefing's **12:08** corresponds to the de-duplicated label centroid
(I reproduce 12:11). On the file as it ships, a student who computes the
centroid naively gets 12:26 on labels. The figures use **12:41**, the
bin-centre value on the full grid, because that is the one that compares
directly with solar noon.
