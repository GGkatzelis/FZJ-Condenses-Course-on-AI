# Trap log

**Design as of 2026-09-20:** build the GUI live from scratch; full campaign file
(2,927 × 881, 20.4 MB); almost no metadata handed to the AI. See
`prompt_script.md` for the run order and `rehearsal_2_comparison.md` for why the
framing is "audit the AI" rather than "watch it fail".

All numbers below were measured on the file the demo actually ships
(`live_template/data/MONALISA_Paris_2025.csv`), not on the original master.
Reproduce with `prep/scripts/build_live_full.py` and
`prep/scripts/check_traps.py`.

---

## The evidence that shapes everything else

An independent session, given only the prompts and no hints, **volunteered**:
the time zone is undeterminable (flagged in five places), CO is in mg/m³ against
µg/m³, `eBC` is aerosol not gas, VOCs are uncalibrated cps and not
inter-comparable, radiation is an accumulation not a rate, the missing data is
not random, and *n* overstates the degrees of freedom by 2×. It also caught the
met duplication unaided and checked it against the insolation ceiling.

**So do not plan for failure.** Plan for it to be right, and make the room do
the verifying. The traps that still work are the ones with **no textual cue** —
where nothing in a column name or a README hints at the problem.

---

## Tier 1 — traps that survive a competent AI

### 🥇 Wind direction is a circular variable · **the centrepiece**

`met_Wind_Direction (degrees)`, range 10–360°. To any code it is just a number.
A plain `groupby(hour).mean()` runs clean, plots a smooth believable diurnal,
and is wrong:

| | value |
|---|---|
| naive arithmetic mean of degrees | **171° (south)** |
| correct vector / circular mean | **220° (southwest)** |
| worst single hour (15:00) | naive 174° vs true **249°** — off **75°** |
| mean absolute error across 24 hours | **49°** |
| hours wrong by more than 45° | **13 of 24** |
| observations within 45° of north | 20.3 % |

The mean of 350° and 10° is 180° — due south — when the answer is 0°, due north.

**Why it survives:** there is no cue. Nothing in the column name says circular,
and with the metadata stripped there is no README to say so either. It is also
*unfixable by inspection* — the wrong curve looks entirely normal.

**Why it is the best one:** it is a genuine, reproducible, physics-level error
that changes a conclusion (source direction), and the fix is one prompt with a
visible 50° jump in the plot.

> On the two-week subset the effect was even larger (naive 127° vs true 45°,
> worst hour off 160°, 44.5 % of points near north). The full campaign has fewer
> northerly cases, so the trap is weaker but still decisive.

### 🥈 `gas_NOX` is in ppb while `gas_NO` and `gas_NO2` are in µg/m³

A self-contained unit trap with a definitive right answer *inside the file*:

| | value |
|---|---|
| median `gas_NO` | 1.08 µg/m³ |
| median `gas_NO2` | 12.68 µg/m³ |
| median `gas_NOX` | **7.90 ppb** |
| naive `NO + NO2` | 14.32 — off by **1.8×** |
| converted `NO/1.25 + NO2/1.91` | **7.92 ppb** |
| r(converted sum, NOX) | **1.0000**, ratio of medians 1.002 |

`NOX` really is `NO + NO2`, once the units match. So a "closure check" either
works perfectly or fails by a factor of 1.8, and the data itself proves which.
Excellent for a room of atmospheric scientists — no appeal to authority needed.

### 🥉 Daylight saving falls inside the campaign

Only possible because the demo now uses the full file.

- Transition at **26 Oct 2025 01:00 UTC** (CEST +2 → CET +1)
- **285 rows (9.7 %)** of the file are CET, not CEST
- A naive `t + 2 h` mislabels **all 285**, and every one lands in the **wrong
  hour of day** — so any local-time diurnal is silently corrupted
- A *correct* `tz_convert` produces a **repeated local hour** (02:00 and 02:30
  appear twice), which then breaks any `groupby` on local timestamps

There is no way to get this right without knowing it exists. Nothing in the file
hints at it.

### The same compound appears twice, in two reagent-ion modes

| | median | |
|---|---|---|
| `NH4_C3H10NO+` (acetone·NH₄⁺) | 3,144 cps | |
| `H3O_C3H7O+` (acetone·H₃O⁺) | 15,853 cps | **5× the same molecule** |
| r between them | **0.881** (n = 1,144) | |

Also `NH4_C10H17+` vs `H3O_C10H17+` (monoterpenes): 55 vs 412 cps, r = 0.862.

Two honest questions fall out: *"which one is the acetone?"* (both) and *"what
does r = 0.88 mean when it is the same compound?" * (it measures the instrument,
not the atmosphere). And `n_H3O == 0` in **60 %** of rows because the instrument
duty-cycles between reagent ions — which is also why the two modes barely
overlap in time.

### Mixed units on one axis

The left-hand multi-select invites it directly: toluene ~1,580 cps against
`gas_CO` 0.17 mg/m³ against temperature 12.6 °C. On a shared y-axis two of the
three become flat lines. The reference app prints a warning when selected series
have different units — worth pointing out as a cheap honest guard.

---

## Tier 2 — present, but weak or likely to be pre-empted

### Met duplication → doubled sums

Still 100 % on all eight met variables. **But it is invisible to every mean and
median** (the mean of a duplicated value is unchanged), and the GUI design
contains **no sums at all**. So it will not appear on its own.

| precipitation | all rows | de-duplicated |
|---|---|---|
| mean | 0.0797 | 0.0797 — identical |
| **sum** | **53.4 mm** | 26.7 mm — 2.000× |

To use it you must ask for a total, e.g. *"how much rain fell over the
campaign?"*. The strong tell is radiation: the doubled figure is
**19.5 MJ/m²/day** as a multi-week mean at 48.85 °N, which is physically
impossible (clear-sky ceiling ≈ 18–20 and it was often cloudy). 9.76 is right.

> Also: `n_met` sits at a constant 8 and `n_gas` at 22, which is a free clue for
> anyone who looks at the bookkeeping columns.

### Time zone

Will be flagged as unknown, correctly and prominently. Not a failure — the
lesson is that *you* then have to supply it, and the DST trap above is what
happens when you supply it carelessly.

### Weekend/weekday sample size

Weakened by the move to the full file: **45 weekday and 16 weekend days**, which
is respectable. On the two-week subset it was 10 and 4, where dropping any single
weekend day moved the curve 16–18 %. No longer worth a beat.

### Uncalibrated cps in correlations

**r is scale-invariant**, so "uncalibrated" does *not* break a correlation —
verified: scaling benzene by 1000 leaves r at 0.7710. It only breaks slopes,
ratios and any "which is more abundant" claim. Do not overstate this one.

### Negative ion values — ❌ does not exist

Logged as present in an earlier draft; that was wrong. **Zero** negatives across
the nine headline ion columns, in the subset *and* the full campaign. The
campaign-wide 1.3 % figure lives in the ~850 weak ions. Only `gas_O3` carries a
few slightly negative night values (to −0.2 µg/m³). Do not offer this as a beat.

---

## What broke during preparation

### 🔴 `scipy` missing — would have killed the correlation panel on stage

`pandas.corr(method="spearman")` imports `scipy.stats` **lazily**, so it failed
at the moment the tab rendered, not at startup. Now pinned at 1.18.1.

> And while the app was completely broken, `curl localhost:8501` still returned
> **HTTP 200**. Streamlit serves its shell regardless. *A running server is not
> a working app.*

### 🟠 Bundled venv abandoned

Copying 381 MB of small files took **4 min 19 s** here, and Pillow's `_imaging`
DLL failed to load at a long destination path. `live_template/` now ships no
venv; building it from a warm `uv` cache takes **41 s**. The 20 MB CSV copies in
seconds — one large file is nothing like 30,000 small ones.

### 🟠 Scope creep is the schedule risk, not failure

The independent run wrote **1,161 lines and 7 tabs** where the first run wrote
370 and 6, from equivalent prompts. Every build prompt now ends with *"Keep it
minimal — no extra features."*

### 🟡 Two of my own errors, both caught by checking

- I logged the negative-ion trap without reading my own script output. It does
  not exist (above).
- I quoted subset correlations (0.77 / 0.84 / 0.61) in a script whose data had
  changed to the full campaign. The correct values are **0.86 / 0.95 / 0.50**.

---

## Timings and verification

Cold start **13.6 s** with all 881 columns; interactions 1.6–6.5 s; Word
overview builds in ~5 s to a 424 kB .docx.

| Stage branch | App | AppTest |
|---|---|---|
| `stage-1-architecture` | `ARCHITECTURE.md` only | n/a |
| `stage-2-plots` | 234 lines, 1 tab | ok |
| `stage-3-notes` | 249 lines, notes form | ok |
| `stage-4-report` | 2 tabs, report button | ok |
| `stage-5-correlations` | 3 tabs, naive wind mean | ok |
| `stage-6-winddir-fix` | 3 tabs, **vector wind mean** | ok |

Verified end to end on the full file: series filter (880 → 8 by family, → 1 by
name search), notes written to `notes.json` keyed by series, and the provenance
table recording **"Wind direction averaging: arithmetic mean of degrees"** —
the report honestly confessing its own method, which is the closing beat.
