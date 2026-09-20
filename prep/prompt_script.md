# Prompt script — live demo, Thursday 24 Sep 2026, 13:45–15:15

**Framing (Georgios, 2026-09-20): the audit is the point.**

No planted traps. A trial run on 2026-09-20 proved they do not survive — given
the bare file and no metadata, the tool found the wind-direction circularity,
the met duplication, the hourly accumulations and the DST straddle **by
itself**, and wrote a vector mean before anyone asked. Chasing gotchas against
this model is a losing bet.

What it cannot do is *sign off* on the choices it makes. That is the lecture.

> **"It audited this file better than I would have by hand — it found a problem
> in my own data that I didn't know about. And it still made four decisions on
> my behalf that only a domain scientist can approve. The expertise didn't
> become optional. It moved from doing the analysis to signing it off."**

**Data:** `MONALISA_Paris_2025.csv`, **1,344 rows × 881 columns**,
16 Sep – 13 Oct 2025, 18.8 MB. 28 days, 20 weekday and 8 weekend days. Trimmed
to the window where the PTR actually measured; met corrected by −1 h; nothing
else touched.

**Metadata: three lines.** The data are unpublished; the venv is in `.venv`.
Nothing about units, instrument, site, columns or time zone.

| Segment | Budget | Ends with |
|---|---|---|
| **A · the audit** | **12 min** | its findings on screen, including one you didn't know |
| B · architecture | 3 min | `ARCHITECTURE.md` |
| C · the GUI | 8 min | working browser, **the four judgement calls** |
| D · notes | 5 min | `notes.json` in the room's own words |
| E · Word overview | 4 min | the .docx, provenance open |
| F · correlations | 3 min | *drop this first* |

Paste everything from [`gui_prompt.txt`](gui_prompt.txt).

---

## Segment A · the audit · 12 min — **this is now the centrepiece**

### A1 — paste block 1

```
There is a CSV in data/. Read it and tell me what is in it: how many rows, what
period it covers, what the columns are, and how much of each column is actually
present. Tell me anything you cannot determine from the file itself. Do not plot
anything and do not clean anything yet.
```

Let it run. **Do not narrate over it** — let them watch it work. It takes a
couple of minutes and that is fine; the silence is part of the effect.

### A2 — what it will report

Measured in the trial. It will get the shape right and then volunteer, without
being asked:

| It will find | The actual number |
|---|---|
| All 8 met columns are hourly values **duplicated** onto both half-hours | bit-identical in **100 %** of pairs |
| **Wind direction is circular** and cannot be arithmetically averaged | 36 discrete values, all multiples of 10; 360 used for north, 0 never present |
| `Sunshine_Duration` reaching **60 min inside a 30-min slot** proves the met values are hourly **accumulations**, not rates | 278 rows exceed 30 |
| Negative values | 4,248 in `NH4_`, 9,172 in `H3O_`, 27 in `gas_` |
| Instrument gaps and the duty cycle | `H3O_` speckled with far more gap blocks than `NH4_` |
| `CH4`/`CH4d` and `CO2`/`CO2d` look like wet/dry pairs | flagged, not investigated |
| Thin weekend sampling | 20 weekday vs 8 weekend days |

And it will state plainly what it **cannot** determine: the time zone ("no
offset or UTC marker anywhere"), the units of all 857 ion columns, what the
`n_*` counters mean, whether the negatives are real or flags, whether the
formulas are confirmed identifications, what calibration was applied, whether
gaps are downtime or removed data, and the site and instrument identity.

### A3 — ⭐ **the moment.** It found a fault in your own data

It will report that **`n_met` contradicts the met columns**:

- **2 rows** have `n_met > 0` but no met values at all
- **2 rows** have `n_met == 0` but met values present
- and `n_NH4`, `n_H3O`, `n_gas` are **perfectly consistent** — it is only `n_met`

Both numbers verified independently. **Neither Georgios nor the preparation
found this** — the tool did, unaided.

> ⚠️ **It may not surface this time.** The trial ran on the *untrimmed* file,
> where the fault affects 6 + 4 rows. On the trimmed file it is only 2 + 2, a
> weaker signal, so it may not get mentioned. **Do not build the segment on it.**
> If it does not come up, raise it yourself — *"here's something it found when I
> gave it the longer file"* — and the beat still works. If it does come up, it is
> the best moment in the lecture.

Say so:

> **"I have worked with this file for weeks. I did not know that. It found it in
> ninety seconds, and it found it by checking a bookkeeping column against the
> data it is supposed to describe — which is exactly the check none of us
> bother to do."**

Then the honest question:

> **"So why do I still need you? Hold that thought — we'll answer it in ten
> minutes."**

### A4 — the pause: what did it *not* tell you?

Two things it did **not** raise in the trial, both real:

- **`gas_NOX` is in ppb while `gas_NO` and `gas_NO2` are in µg/m³.** So
  `NO + NO2` gives 18.25 against a `NOX` of 9.95 — off by 1.8×. Convert
  (`NO/1.25 + NO2/1.91`) and you get **9.95 against 9.95, r = 1.0000**. The file
  proves its own answer, and it said nothing about it.
- **The same compound appears twice**, once per reagent-ion mode: acetone is
  both `NH4_C3H10NO+` (median 3,144 cps) and `H3O_C3H7O+` (median 15,853 cps).
  Same molecule, factor of five, r = 0.88.

> **"It told us everything it could see in the numbers. It did not tell us the
> two things that need chemistry."**

---

## Segment B · architecture · 3 min

Paste block 2, then block 3. Have **File Explorer visible** — watching
`ARCHITECTURE.md` appear from nothing is most of the value for an audience that
has never seen this.

> **"It has written down what it thinks we asked for. Cheapest possible moment
> to catch a misunderstanding."**

---

## Segment C · the GUI · 8 min

Paste block 3 (already pasted in B — it builds now).

```
.venv\Scripts\python.exe -m streamlit run app.py
```

⚠️ **~22 s to first page** (17 s imports + 5 s CSV) even warmed. Talk over it.

### C1 — the audience picks

| Option | Filter to | Rehearsed outcome |
|---|---|---|
| **1. Traffic** ⭐ | `C7H9` (toluene) + `gas_NO` | Weekday peaks 07:00, weekend peaks 19:00 — **the profile inverts**. Best science on screen |
| **2. Wood vs traffic** | `eBCwb` + `eBCff` | Different evening behaviour; a real result |
| **3. Weekend effect** | `C6H7` (benzene) + `gas_NO2` | Weekend curves clearly lower |
| **4. Meteorology** | family = Meteorology | Goes to the wind-direction discussion below |

### C2 — ⭐ **the four judgement calls.** This is where the lecture lands

Put wind direction on screen, then tell them the tool did something clever:

> **"It averaged this one differently from everything else. It recognised that a
> compass bearing can't be arithmetically averaged — 350° and 10° average to
> 180°, due south, when the answer is due north — so it used a vector mean. It
> worked that out on its own. Did you?"**

It also quantified it. On this file the two disagree in **all 24 hours**, by
**53° to 150°**, mean error **96°**. The whole-file mean is **140° (southeast)
arithmetically against 45° (northeast)** by vector mean — a 95° error, pointing
at a completely different part of Paris. Worst hour is 01:00: **146° against
356°**. Verified.

Now turn it:

> **"It got the hard one right. So here are four more decisions it made, all
> reasonable, none of which it asked me about."**

| # | What it decided | Why it matters |
|---|---|---|
| **1** | **Averaged** the accumulated met variables (precipitation, radiation, sunshine) instead of summing | Your diurnal now reads "mean hourly accumulation", **not a total**. Ask for "daily rainfall" from this and you get the wrong thing |
| **2** | **Ignored the `n_*` sample counters** — every 30-min bin weighted equally | A bin built from 3 sub-samples counts as much as one built from 30 |
| **3** | **Did not de-duplicate** the met half-hours before grouping | Harmless for a mean, but it **doubles the apparent sample count**, so any error bar or p-value from it is wrong by √2 |
| **4** | **No per-day normalisation** — a plain mean over all samples | Days with more valid data **pull the mean harder**. Your "mean diurnal" is not the mean of the days |

> **"Every one of those is defensible. Every one changes the number. It
> documented all four in its own report — which is more than most papers do.
> But it cannot decide which is right for *your* science question, and it will
> never refuse to proceed. That is the job that did not go away."**

---

## Segment D · notes · 5 min

Paste the notes block, then **take two or three interpretations from the room
and type them verbatim.**

- *"Which of those four decisions would you change, and why?"* ← the best note
  you will get
- *"Why does the weekend curve drop but not flatten?"*
- *"What would you need before this went in a paper?"*

Show them `notes.json`. Seeing their own sentence become structured data lands
with people who have never done this.

---

## Segment E · Word overview · 4 min

Drop the prompt log in first:

```powershell
Copy-Item "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\prompts_for_report.json" ".\prompts.json"
```

Paste the report block. Open the .docx, scroll to **Provenance**.

> **"Time zone: not stated in the data file. Wind direction: vector mean.
> Missing data: excluded pairwise, gaps not filled.**
>
> **This document is honest about what it doesn't know and explicit about every
> choice it made. That is better provenance than most papers carry. And it is
> still not enough — because being explicit about a choice is not the same as
> that choice being right. Somebody with your training has to read those lines
> and agree with them. That is what you are for."**

---

## Segment F · correlations · 3 min · **drop this first**

| Pair | Result (verified) |
|---|---|
| `H3O_C6H7+` vs `H3O_C10H17+` | r = **0.86** overall — but **0.95 at night**, **0.50 at midday**, both anticorrelated with wind speed. Dilution, not a shared source |
| `NH4_C3H10NO+` vs `H3O_C3H7O+` | r = **0.88** — and it is **the same compound measured twice**. What does r even mean here? |

---

## Numbers to know cold

| | |
|---|---|
| File | 1,344 × 881, 16 Sep – 13 Oct, 20 weekday / 8 weekend days |
| `n_met` fault | **2** rows `n_met>0` with no data; **2** rows `n_met==0` with data |
| Wind direction | whole file **140° vs 45°**; all 24 hours off by 53–150°, mean 96°; 36.4 % of obs near north |
| NOX closure | raw `NO+NO2` 18.25 vs NOX 9.95; converted **9.95 vs 9.95, r = 1.0000** |
| Acetone, two modes | 3,144 (NH₄⁺) vs 15,853 (H₃O⁺) cps, r = 0.88 |
| Toluene diurnal | weekday peak **07:00**, weekend peak **19:00** |
| Met duplication | **100 %** of pairs bit-identical, all 8 columns |
| Sunshine 60 min in a 30-min slot | 278 rows > 30 min |
| First page load | ~22 s warmed; **66.7 s** if the bytecode cache is cold |
