# Data verification — `MONALISA_campaign_master_30min.csv`

Every claim in Georgios' briefing, reproduced from the file on **2026-09-19**.
Read-only; the original was never opened for writing.
Scripts: `prep/scripts/verify.py`, `prep/scripts/verify2.py`.
Solar geometry: NOAA solar-position algorithm, Paris 48.85 °N, 2.35 °E, no external library.

Legend: ✅ confirmed · ⚠️ confirmed with a caveat · ❌ does not reproduce

---

## 1. Shape and grid — ✅ exact

| Claim | Found |
|---|---|
| 2,927 rows | **2,927** |
| 30-min grid | **2,926 intervals, all exactly 00:30:00**; monotonic; 0 duplicate stamps; complete grid, no gaps |
| 1 Sep – 31 Oct 2025 | first `2025-09-01 00:00`, last **`2025-10-31 23:00`** |
| — | Timestamps are **naive** (no tz offset in the strings) |

⚠️ Small correction: the file ends at **23:00**, not 23:30. 61 days × 48 = 2,928
slots; the file has 2,927. The last half-hour of October is simply absent. Harmless,
but do not assume `len(df) % 48 == 0`.

## 2. Column groups — ✅ exact

| Group | Claimed | Found |
|---|---|---|
| `NH4_` | 427 | **427** |
| `H3O_` | 430 | **430** |
| `gas_` | 11 | **11** |
| `met_` | 8 | **8** |
| `n_` | 4 | **4** |
| `time` | 1 | **1** |
| **total** | 881 | **881** |

⚠️ **The `gas_` and `met_` column names carry their units in the name**, e.g.
`gas_NO (microg/m3)`, `met_Global_Radiation (J/cm2)`. There is no bare `gas_NO`
column. Any code must match on the prefix, not the exact string. This matters for
building `live_template/` and it is itself a small live trap.

## 3. Ion values — ✅ exact

| Claim | Found |
|---|---|
| range ≈ −1,470 … 90,000 | **−1,471.4 … 90,049.7** |
| ≈1.3 % negative | **1.291 %** of finite values |
| — | 183 of 857 ion columns contain at least one negative |
| — | **58.5 % of all ion cells are NaN** (see §8) |

## 4. Ion naming — ⚠️ true but thinner than described

- `NH4_C3H10NO+` (acetone·NH₄⁺) is present ✅ — adducts are included in the formula.
- **Isotopologues: exactly one** — `H3O_[13C]C3H7+`. Not a population, a single column.
- **Water clusters: four** — `H3O_C2H6OH2OH+`, `H3O_C5H10O2H2OH+`,
  `H3O_C6H18O3Si3H2OH+`, and `NH4_H11O5+`.

Neither is a significant feature of the file. Fine as a remark; too thin to build a
demo beat on.

## 5. Gas and met columns

```
gas_eBCff (microg/m3)   n=1966   0.000 –   6.623
gas_eBCwb (microg/m3)   n=1969   0.000 –   1.627
gas_O3    (microg/m3)   n=2149  -1.000 –  98.900   <- 30 rows negative
gas_NO    (microg/m3)   n=2148  -0.050 – 161.300   <- 1 row negative
gas_NO2   (microg/m3)   n=2148   2.300 –  90.300
gas_NOX   (ppb)         n=2148   1.550 – 168.000
gas_CH4d  (ppm)         n=2155   2.000 –   2.450
gas_CH4   (ppm)         n=2155   2.000 –   2.400
gas_CO2   (ppm)         n=2155 410.875 – 521.855
gas_CO2d  (ppm)         n=2155 420.970 – 534.630
gas_CO    (mg/m3)       n=2154   0.066 –   0.729

met_Wind_Direction (degrees)     n=2921
met_Sunshine_Duration (min)      n=2891    0 – 60
met_Relative_Humidity (%)        n=2921   37 – 97
met_Atmospheric_Pressure (hPa)   n=2439  <- notably sparser than the other met vars
met_Precipitation (mm)           n=2905    0 – 5.2
met_Global_Radiation (J/cm2)     n=2891    0 – 275.9
met_Sheltered_Temperature (C)    n=2921  6.4 – 30.5
met_Wind_Speed (m/s)             n=2921  0.5 – 8.6
```

✅ Mixed units confirmed exactly as claimed.
⚠️ `gas_CO2d > gas_CO2` and `gas_CH4d > gas_CH4` throughout — consistent with "d" =
**dry** mole fraction (removing water vapour raises the mole fraction). This supports
the guess in ⛔ Q3 but does not prove it.

## 6. Met duplication — ✅ 100 %, and for **all eight** variables

Pairing each `h:00` with the `h:30` of the same hour:

| Variable | pairs | identical |
|---|---|---|
| Wind_Direction | 1460 | 1460 — **100.00 %** |
| Sunshine_Duration | 1445 | 1445 — **100.00 %** |
| Relative_Humidity | 1460 | 1460 — **100.00 %** |
| Atmospheric_Pressure | 1219 | 1219 — **100.00 %** |
| Precipitation | 1452 | 1452 — **100.00 %** |
| Global_Radiation | 1445 | 1445 — **100.00 %** |
| Sheltered_Temperature | 1460 | 1460 — **100.00 %** |
| Wind_Speed | 1460 | 1460 — **100.00 %** |

Control — pairing `h:30` with the *following* `h+1:00` instead gives 5–27 % for the
continuous variables. So the duplication direction is unambiguous: **the value sits at
`h:00` and is copied forward into `h:30`.**

The claim was made for precipitation; it holds for **every** met variable. The doubling
trap therefore works on radiation, sunshine duration and precipitation alike.

## 7. Timing — ⚠️ the headline number is −45 min, not −55, and it decomposes cleanly

Method: for a candidate offset Δ, compute solar zenith angle at `label + Δ`, take
`max(cos SZA, 0)` and correlate with the measured series. Best Δ = the bin centre's
true position relative to its label. Scanned −180…+180 min in 5-min steps, with
parabolic refinement.

### Global radiation

| Subset | Best Δ | refined | r |
|---|---|---|---|
| all 30-min rows | **−45 min** | −43.3 | 0.8504 |
| `h:00` rows only | **−30 min** | −28.2 | 0.8534 |
| `h:30` rows only | **−60 min** | −58.2 | 0.8533 |

**This is the key result of the whole verification.** The −45 min is not a physical
offset — it is the average of two different offsets created by the duplication:

```
  h:00 copy needs  -30 min   (hourly value, end-of-hour label -> centre is 30 min earlier)
  h:30 copy needs  -60 min   (same value, sitting 30 min further right)
  --------------------------------------------------------------------
  pooled average   -45 min
```

So the "45–60 min late" range in the briefing is exactly right, and it is a *range*
because the two copies genuinely need different shifts. The point estimate "−55 min"
does not reproduce: on the pooled data the optimum is −45 min, and the curve is broad
and shallow (r = 0.8468 at −60, 0.8504 at −45, 0.8481 at −30), so −55 sits inside the
noise but is not the maximum.

**End-of-hour labelling is confirmed independently** by the `h:00`-only fit landing on
−30 min, which is precisely what an hour-ending-at-label convention predicts.

> ⚠️ **Consequence for task 3, needs a decision.** "Correct the met alignment but keep
> the duplication" cannot be done with one shift: after any single shift the two copies
> are still 30 min apart and one of them is wrong by 30 min. See the question below.

### Sunshine duration (second solar probe)

| Subset | Best Δ | r |
|---|---|---|
| all rows | −20 min | 0.5679 |
| `h:00` only | −10 min | 0.5697 |

⚠️ This does **not** agree with radiation (−10 vs −30 on the same rows). Sunshine
duration is a clipped hourly *sum* (0–60 min, saturating on clear days), so it is a much
weaker timing probe — r ≈ 0.57 against 0.85. I would not put it on a slide, but you
should know it disagrees in case a student runs it.

### Gas, photostationary proxy — ✅ confirmed

`NO·O₃/NO₂` with NO ÷ 1.25, NO₂ ÷ 1.91, O₃ ÷ 2.0 (µg/m³ → ppb); n = 2,142; median
2.72 ppb.

| Subset | Best Δ | refined | r |
|---|---|---|---|
| proxy, all rows | **−5 min** | −6.2 | 0.8315 |

Flat across −15…0 (0.8306 / 0.8314 / 0.8315 / 0.8311). **Gas is on true UTC within
±15 min** — confirmed. The claimed "−10 min" is indistinguishable from the −5 min
optimum.

**Control worth showing on a slide:** O₃ *alone*, scanned the same way, gives
**−165 min** (r = 0.57). Ozone lags the sun by hours because of boundary-layer growth
and titration — which is exactly why the photostationary ratio is the right probe and a
single species is not. This is a free, genuine teaching beat for slide 21.

## 8. Radiation centroid — ⚠️ method-dependent; the briefing's 12:08 needs de-duplication

| Computed on | Centroid | Peak label |
|---|---|---|
| all 30-min rows (duplicated) | **12:26** | 12:00 |
| `h:00` rows only (de-duplicated) | **12:11** | 12:00 |

Georgios' 12:08 ≈ the de-duplicated 12:11. The duplication shifts the centroid **+15
min** on its own, so quoting "12:08" only holds if you de-duplicate first. On the file
as it ships, a student computing the centroid naively gets **12:26**.

**True solar noon, Paris, 25 Sep 2025: 11:42 UTC** (claim: ~11:40 ✅).

## 9. PTR duty cycling — an undocumented feature worth knowing

The `n_` columns are **counts of valid values across all columns in the group**, not
sample counts:

| Column | max | ÷ n columns | meaning |
|---|---|---|---|
| `n_gas` | 22 | 22/11 = **2** | 15-min native → 2 per 30 min ✅ |
| `n_met` | 8 | 8/8 = **1** | hourly → 1 per 30 min ✅ |
| `n_H3O` | 4300 | 4300/430 = **10** | ~10 one-minute samples per 30 min |
| `n_NH4` | 8520 | 8520/427 = **~20** | ~20 one-minute samples per 30 min |

10 + 20 = 30 → **the PTR alternates reagent ion within each half hour**, roughly 20 min
in NH₄⁺ mode and 10 min in H₃O⁺ mode. `n_H3O == 0` in **1,763 of 2,927 rows (60 %)** —
which is where the 58.5 % ion-NaN figure comes from. H₃O⁺ coverage is not uniform across
the campaign.

**Good news:** both chosen windows sit in well-covered stretches (§10).

## 10. Window coverage — ✅ both windows are good

| Window | rows | H₃O ions | gas | met |
|---|---|---|---|---|
| **Live subset** 22 Sep – 5 Oct | 672 | **89.0 %** | 94–100 % | 99.7 % |
| **Figure window** 6 – 13 Oct | 384 | **87.2 %** | 99.2–99.5 % | 100 % |

All nine requested `H3O_` columns exist under exactly the requested names
(`H3O_C6H7+`, `H3O_C7H9+`, `H3O_C8H11+`, `H3O_C10H31O5Si5+`, `H3O_C5H9+`,
`H3O_C10H17+`, `H3O_C9H19O+`, `H3O_C3H7O+`, `H3O_C2H5O+`). **Coverage in the
6–13 Oct figure window is not poor** — it is marginally better than the live window
for gas and met, and 1.8 points worse for the ions. Proceed as planned.

---

## Summary of corrections to the briefing

1. **−45 min, not −55 min**, is the pooled met offset — and it decomposes exactly into
   −30 min (end-of-hour label) and −15 min (duplication). The physics is *more* legible
   than the briefing suggested, not less.
2. **Radiation centroid is 12:26 on the file as it ships**; 12:08–12:11 only after
   de-duplication.
3. **The duplication is 100 % for all eight met variables**, not just precipitation.
4. **`gas_`/`met_` column names embed their units** — there is no bare `gas_NO`.
5. **The file ends 31 Oct 23:00**, not 23:30.
6. **Isotopologues and water clusters are 1 and 4 columns**, not a population.
7. **The PTR duty-cycles between reagent ions**; 60 % of rows have no H₃O⁺ data at all.
8. Sunshine duration disagrees with global radiation on timing (−10 vs −30); it is the
   weaker probe and should not be used.

Everything else reproduced exactly.
