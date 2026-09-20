# Trap log — rehearsal 1

Build: `prep/rehearsal_1/`, driven through all five segments with Streamlit's
own `AppTest` harness (`prep/scripts/rehearse_app.py`), which executes the
script and surfaces real exceptions. Trap numbers from
`prep/scripts/check_traps.py`.

Environment: Python 3.12.12, pandas 3.0.6, streamlit 1.64.0, in `.venv_demo`.

---

## Headline: one trap will not fire unless you change the script

**The met-duplication trap is invisible to every mean and median.** The mean of
a duplicated value is the same value. Only a **sum** doubles.

| Statistic on `met_Precipitation (mm)` | all rows | de-duplicated | ratio |
|---|---|---|---|
| **sum** | 53.40 mm | 26.70 mm | **2.000** |
| mean | 0.0797 mm | 0.0797 mm | 1.0000 |

The app's "daily" averaging toggle uses `.mean()`, so as originally scripted
segments A–E would have run start to finish **without the trap ever
appearing**. Prompt **B4** was added to fix this and asks explicitly for a
total. Do not skip it.

---

## Trap-by-trap

### Trap 1 — met duplication → doubled sums ✅ fires, with B4

| | naive | true | ratio |
|---|---|---|---|
| Rainfall, 14 days | **53.4 mm** | 26.7 mm | 2.000 |
| Global radiation dose | **19.52 MJ/m²/day** | 9.76 MJ/m²/day | 2.000 |

**Use radiation, not rain, as the catch.** 53 mm of rain in two weeks in Paris
is high but not impossible — a weak tell. A **14-day mean of 19.5 MJ/m²/day at
48.85 °N in late September is physically impossible**: the clear-sky maximum is
about 18–20 MJ/m²/day and it was frequently cloudy. 9.76 MJ/m²/day is right.

**The ranking survives.** Every day doubles by exactly 2.000, so the wettest day
is still 4 Oct in both cases (14.6 mm vs 7.3 mm). The tell is therefore the
**magnitude**, never "the wrong day is wettest".

**Confirming prompt works:** asking for six daytime met rows shows every value
twice — 335 of 336 consecutive pairs identical (99.7 %). Use a **daytime** hour;
at night radiation is all zeros and the duplication is invisible.

```
2025-09-22 10:00:00   147.9   15.8
2025-09-22 10:30:00   147.9   15.8
2025-09-22 11:00:00   189.6   15.9
2025-09-22 11:30:00   189.6   15.9
```

### Trap 2 — time zone ⚠️ fires, but backwards. Read this before you present

The file is UTC and says so nowhere. Paris was on **CEST (UTC+2)**.

| Series | peak, file time | = local time |
|---|---|---|
| NO₂ | 06 | 08:00 |
| toluene / benzene | 07 | 09:00 |
| NO | 08 | 10:00 |
| evening maxima | 19–20 | **21–22** |

**The problem:** taken at face value as local time, the morning peaks sit at
06–08, which looks like a *textbook* European rush hour. Converted correctly to
local time they sit at 09–10, which is **late**. So the wrong reading is the
more convincing one.

That is a good lesson — *plausibility is not correctness* — but it means a sharp
student can push back and you need the answer ready:

- NO₂ at 06 UTC = **08:00 local, which is textbook.** Lead with NO₂, not NO.
- NO peaks later than NO₂ because of titration and boundary-layer growth; the
  peak of a secondary/reactive species is not the emission time.
- The evening maxima at **21–22 local are far too late for traffic**. That is
  positive evidence that the evening peak is **boundary-layer collapse**, not
  emissions — the same mechanism as slide 8. This is the strongest point in the
  segment; use it.

### Trap 3 — mixed gas units ✅ present, fires only if combined

| column | median |
|---|---|
| `gas_NO (microg/m3)` | 1.000 |
| `gas_NO2 (microg/m3)` | 15.650 |
| `gas_O3 (microg/m3)` | 36.800 |
| **`gas_CO (mg/m3)`** | **0.173** |

CO is a factor **1000** off the rest. Plotted on a shared axis it looks like a
flat zero. Because the unit is in the column name, an attentive AI does notice —
so this is a *soft* trap. It bites only if something sums or compares across
columns. The app's y-axis label joins the distinct units, which makes the
mismatch visible rather than hiding it.

### Trap 4 — `eBC` is aerosol, not gas ✅ present

`gas_eBCff` (0.655 µg/m³ median) and `gas_eBCwb` (0.161) carry the `gas_` prefix
but are particulate black carbon from an absorption instrument. Any "total
gas-phase burden" that adds them is wrong. `CLAUDE.md` states this, so a careful
run will catch it — worth asking the room *before* revealing it.

### Trap 5 — negative ion values ❌ DOES NOT EXIST. I got this wrong

I originally logged this as present. It is not. Verified column by column:

| | negatives | min |
|---|---|---|
| all nine `H3O_` columns, live subset | **0** | lowest is +4.53 (D5) |
| all nine `H3O_` columns, **full campaign** | **0** | same |

The campaign-wide 1.3 % negative figure is real, but it lives in the *other*
~850 weak ion columns. All nine compounds chosen for `live_template` are
high-signal species far above background, so none of them ever goes negative.

The only negatives in the subset are **three slightly negative night-time
`gas_O3` values** (down to −0.2 µg/m³).

**Consequence:** `live_template/CLAUDE.md` originally promised negative values
that are not there. Rehearsal 2 spotted the mismatch unprompted and said so.
The wording has been corrected to describe the effect accurately and to point
at `gas_O3` instead. **Do not offer "the negative values" as a demo beat** —
there are none to find.

### Trap 6 — missing data / `fillna(0)` ✅ present

Coverage in the live window: ions **89.0 %**, gas 94–100 %, met 99.7 %. A
`fillna(0)` before averaging drags every ion mean down by roughly 11–13 % and,
worse, flattens diurnal profiles until `idxmax()` reports noise — which is
exactly slide 7. Not scripted as a live beat, but if the AI writes `fillna(0)`
on its own, stop and use it.

### Trap 7 — column names embed units 🎁 unplanned bonus

There is no `gas_NO` column; it is `gas_NO (microg/m3)`. Any code matching exact
strings fails. Cheap, real, and it appears in segment A for free.

---

## What actually broke in rehearsal 1

### 🔴 `scipy` missing — would have killed segment C on stage

`pandas.Series.corr(method="spearman")` imports `scipy.stats` lazily. `scipy`
was **not** in `requirements.txt`, so the first correlation raised
`ModuleNotFoundError: No module named 'scipy'` — and because the import is lazy,
it failed at the moment the tab rendered, not at startup.

**Fixed:** `scipy==1.18.1` added to `requirements.txt` and the lock file.

> **A second lesson worth repeating on the day:** while the app was completely
> broken, `curl http://localhost:8501/` still returned **HTTP 200**. Streamlit
> serves its shell HTML regardless; the traceback only appears in the browser
> session. "The server is up" is not "the app works". Always look at the page.

### 🟠 Bundled venv was unusable — design changed

Shipping `.venv` inside `live_template/` was abandoned:

- copying 381 MB of small files took **4 min 19 s** on this machine (antivirus)
- Pillow's `_imaging` DLL failed to load at a long destination path
  (`ImportError: DLL load failed ... filename or extension is too long`)

**Fixed:** `live_template/` now carries no venv (190 kB, copies instantly).
Building the environment fresh from a warm `uv` cache takes **41 s**. That is
the day-of procedure.

### 🟠 Streamlit's first load is slow

Cold start, including imports and the first data read: **31.8 s**. Every
interaction afterwards: **3–4 s**. Start the app *before* the audience is
watching.

### 🟡 Case-study centroid convention

Not a live trap, but it bit me while making the figures: quoting a label-based
centroid on a **start-labelled** grid makes a correctly aligned series look
15 min early, so the corrected panel appeared over-corrected by −16 min when it
was right. All figures now quote bin centres. See `case_study_numbers.md`.

---

## Timings, rehearsal 1

Measured via `AppTest`, so these are compute time only — they exclude the AI's
thinking and typing, which dominates the live budget.

| Step | Time | Status |
|---|---|---|
| A: cold start + overview | 31.79 s | ok |
| B: time series, 2 compounds, hourly | 4.29 s | ok |
| B: daily averaging | 3.44 s | ok |
| B: diurnal, median | 3.55 s | ok |
| C: benzene vs monoterpenes | 3.07 s | ok |
| C: eBCff vs NO | 3.39 s | ok |
| C: isoprene vs temperature | 3.40 s | ok |
| D: save one note | 1.15 s | ok |
| E: build report | 5.57 s | ok |
| **total compute** | **59.66 s** | |

Report output: **387 kB .docx**. `notes.json` written on the first save and
re-read correctly.

## Checkpoint branches — all five verified runnable

| Branch | Tabs | AppTest |
|---|---|---|
| `stage-3a` | Overview | ok |
| `stage-3b` | + Time series, Diurnal | ok |
| `stage-3c` | + Correlations | ok |
| `stage-3d` | + Notes | ok |
| `stage-3e` | + Report | ok |

## Where nothing stalled

Segments B, C, D and E were never blocked. The only hard failure was the scipy
import, now fixed. The genuine risks left on the day are **Streamlit's 32 s
cold start** and **the time-zone pushback in B3**, not the code.

---

## Rehearsal 2

See [rehearsal_2_comparison.md](rehearsal_2_comparison.md) — an independent run
from scratch given only the verbatim prompts, to measure how much the output
varies between runs.
