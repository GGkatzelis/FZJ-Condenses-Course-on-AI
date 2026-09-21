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

| Segment | Block | Budget | Ends with |
|---|---|---|---|
| **A · the audit** | 1 | **12 min** | its findings on screen, including one you didn't know |
| **B · the GUI** | 2 | 8 min | working browser, **the four judgement calls** |
| **C · correlations + notes** | 3a, 3b | **8 min** | the room's own argument about r = 0.86, in `notes.json` |
| D · Word report | 4 | 4 min | the .docx, provenance open |
| **E · the reveal** | 5 | 4 min | **README.md + ARCHITECTURE.md + the folder tree — the finale** |

**36 min total.** Correlations and notes were merged deliberately: a correlation
gives the room something genuinely arguable to write down, where a timeseries
mostly answers itself.

> ⚠️ **That merge removed the droppable segment.** There is no longer a whole
> beat to cut if you run over — the cut order is now *inside* the segments, and
> it is written out at the end of `gui_prompt.txt`: drop `ARCHITECTURE.md`
> (~1.5 min), then take one audience note instead of three (~2 min), then skip
> the B1 menu and pick option 1 yourself (~2 min). That gets you to ~30 min.
> **Never cut** block 1, the correlation argument in 3a, or the README.

**Build step by step, one block per segment.** Watching it correctly modify code
it wrote ten minutes ago is the moment the penny drops for an audience that has
never vibe-coded — a single big generation reads as fancy autocomplete and gives
you no partial result if it goes wrong.

**`ARCHITECTURE.md` moved to the end, it did not disappear.** Block 2 opens with
*"before you write any code, tell me in one paragraph what you are about to
build"* — the catch-the-misunderstanding-early lesson, spoken in thirty seconds,
without putting a document on the projector at minute ten when the room has not
used the app and cannot evaluate a plan for it. The document itself is written
in segment E, where it documents something real and is a payoff rather than an
abstraction.

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

## Segment B · the GUI · 8 min

Paste **block 2**. It opens by asking the tool to say what it is about to build,
before it writes anything:

> **"Read that back to us. Is that what I asked for? This is the cheapest moment
> in the whole project to catch a misunderstanding — and the last easy one."**

Then it builds.

```
.venv\Scripts\python.exe -m streamlit run app.py
```

⚠️ **~22 s to first page** (17 s imports + 5 s CSV) even warmed. Talk over it.

### B1 — the audience picks

| Option | Filter to | Rehearsed outcome |
|---|---|---|
| **1. Traffic** ⭐ | `C7H9` (toluene) + `gas_NO` | Weekday peaks 07:00, weekend peaks 19:00 — **the profile inverts**. Best science on screen |
| **2. Wood vs traffic** | `eBCwb` + `eBCff` | Different evening behaviour; a real result |
| **3. Weekend effect** | `C6H7` (benzene) + `gas_NO2` | Weekend curves clearly lower |
| **4. Meteorology** | family = Meteorology | Goes to the wind-direction discussion below |

### B2 — ⭐ **the four judgement calls.** This is where the lecture lands

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

## Segment C · correlations + notes · 8 min

**Two pastes, one segment.** Correlations first, so the room has something worth
arguing about before you ask them to write anything down.

### C1 — paste block 3a, the correlation panel

Then put **benzene (`H3O_C6H7+`) against monoterpenes (`H3O_C10H17+`)** and ask:

> **"r is 0.86. Do these two share a source?"**

They do not. Verified on this file:

| | r | n |
|---|---|---|
| all points | **0.860** | 1,164 |
| night 00–05 | **0.945** | 295 |
| midday 11–16 | **0.499** | 288 |

and both anticorrelate with wind speed (benzene **−0.41**, monoterpenes
**−0.31**). The correlation is strongest when the air is stagnant and weakest
when it is windy and the boundary layer is deep. That is **shared dilution, not
shared chemistry** — they rise and fall together because the same shallow
nocturnal layer concentrates everything, not because anything emits both.

**This is the argument worth writing down.** Hold it for C2.

> If a student pushes for a decisive test: monoterpenes here show **no**
> temperature dependence (r = −0.017) while isoprene in the same file does
> (**+0.229**). Same instrument, same period — so the monoterpene signal is not
> biogenic, which is a physical falsification rather than another coefficient.

### C2 — paste block 3b, the notes box

It wires notes into **both** panels: against a selected series, and against a
correlation pair. Then take the argument from the room and **type it verbatim**.

- *"So what should we write down about that correlation?"*
- *"Which number in that argument would you check first, and how?"*

Show them `notes.json` in the editor afterwards. Seeing their own sentence become
structured data lands with people who have never done this.

→ fallbacks: `stage-3a-correlations`, then `stage-3b-notes`

---

## Segment D · Word report · 4 min

Drop the prompt log in first:

```powershell
Copy-Item "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\prompts_for_report.json" ".\prompts.json"
```

Paste **block 4**. Open the .docx, scroll to **Provenance**.

> **"Time zone: not stated in the data file. Wind direction: vector mean.
> Missing data: excluded pairwise, gaps not filled.**
>
> **This document is honest about what it doesn't know and explicit about every
> choice it made. That is better provenance than most papers carry. And it is
> still not enough — because being explicit about a choice is not the same as
> that choice being right. Somebody with your training has to read those lines
> and agree with them. That is what you are for."**

---

## Segment E · the reveal · 4 min — **the finale**

Bring **File Explorer** to the front, showing the live folder. Then paste
**block 5**:

```
We started this hour with one CSV and three lines of text. Write two documents
for what we have built:

- README.md - what this tool does, how to run it, and what decisions you made
  while building it. Be specific about how you averaged each kind of column and
  what you did with missing data.

- ARCHITECTURE.md - how the pieces fit together. Include a diagram, drawn in
  plain text, showing how the data flows from the CSV through to the plots, the
  notes file and the Word report.
```

Three things happen at once, and all of them matter.

**They watch the tree fill.** `app.py`, `README.md`, `ARCHITECTURE.md`,
`notes.json`, `MONALISA_overview.docx` — none of which existed an hour ago. For
an audience that has never seen this, the folder is more persuasive than any of
the plots.

> **"One CSV. Three lines of text telling it the data are unpublished and where
> Python lives. Everything else in this folder, we talked into existence in
> forty minutes."**

**And it writes down its own judgement calls.** That last clause of the prompt
is doing the real work — *"what decisions you made while building it"*. Read two
of them out loud from the README it just wrote, then close:

> **"It is telling you, in writing, the choices it made on your behalf. That is
> better documentation than most papers carry. And it is still not enough —
> because writing a choice down is not the same as it being right. Somebody with
> your training has to read those lines and agree with them.**
>
> **That is the job. It didn't go away. It moved."**

**And the architecture diagram closes it.** Ask for it *in plain text* — an
ASCII data-flow box diagram reads from the back row, where prose does not. Put
it up as the very last thing on screen.

> If the README is thin on decisions, push once: *"be specific about how you
> averaged each kind of column."* That reliably produces the four calls from B2.
>
> `README.md` is requested **before** `ARCHITECTURE.md` on purpose: it carries
> the judgement calls, so it is the one you want if generation runs long.

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
