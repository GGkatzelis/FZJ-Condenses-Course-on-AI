# Prompt script — live demo, Thursday 24 Sep 2026, 13:45–15:15

**Design (Georgios, 2026-09-20).** Build the GUI from scratch, live, in front of
the room. The audience has mostly never seen vibe coding, so **the build itself
is the content** — watching files appear and a working tool assemble is the
spectacle. The traps ride along inside it.

**Data: the full campaign file.** 2,927 rows × 881 columns, 1 Sep – 31 Oct 2025,
20.4 MB. Met corrected by −1 h; everything else exactly as the campaign
produced it, `n_` bookkeeping columns included.

**Metadata: almost none.** `live_template/CLAUDE.md` says only that the data are
unpublished and where the venv is. No units, no instrument, no site
description, no time zone, no column list. This is deliberate: it is what a real
file looks like, and **what the tool fails to ask about is the trap**.

**Target: 32 min.** Build order is deliberate — a complete working loop (look →
note → Word file) before anything optional. Correlations are last and droppable.

| Segment | Budget | Ends with |
|---|---|---|
| A · read and describe | 7 min | the "what did it *not* ask?" pause |
| B · architecture | 3 min | `ARCHITECTURE.md` on screen |
| C · the GUI: list + 2 plots | 10 min | working browser, **wind-direction trap live** |
| D · notes → JSON | 5 min | `notes.json` with the room's words in it |
| E · Word overview | 4 min | the .docx, provenance section open |
| F · correlations | 3 min | *drop this first if time is short* |

---

## Before you start (off the clock)

```powershell
cd "$env:USERPROFILE\Desktop\MONALISA_live"
code .
```

Terminal open, browser ready at `localhost:8501`. **Do not** put `prompts.json`
in the folder yet — it lists every prompt and gives away the plan. You drop it
in at segment E.

---

## Segment A · read and describe · 7 min

### A1

```
There is a CSV in data/. Read it and tell me what is in it: how many rows, what
period it covers, what the columns are, and how much of each column is actually
present. Tell me anything you cannot determine from the file itself. Do not plot
anything and do not clean anything yet.
```

**What it will do** (tested on an independent run): get 2,927 × 881 right, group
the columns into `NH4_` / `H3O_` / `gas_` / `met_` / `n_`, notice the units
embedded in the `gas_`/`met_` names, notice that **the ion columns have no units
anywhere**, and flag the time zone as undeterminable.

### A2 — the pause. **This is the most important 3 minutes of the lecture.**

Ask the room, in this order:

> **1. "What did it ask us for?"**

It will have asked about — or flagged as unknowable — the ion units, the time
zone, and probably what `eBC` is. **Credit that out loud.** This is the honest
lesson: a good tool tells you what it does not know.

> **2. "Now — what did it *not* ask about?"**

This is the real question. Things it will almost certainly *not* raise unless
prompted:

- **`met_Wind_Direction` is a circular variable.** It is just "a number in
  degrees" to the tool. ← *this becomes segment C*
- **`gas_NOX` is in ppb while `gas_NO` and `gas_NO2` are in µg/m³.** So
  `NO + NO2` does not equal `NOX` unless you convert.
- **The same compound appears twice**, once in each reagent-ion mode: acetone is
  both `NH4_C3H10NO+` and `H3O_C3H7O+`, with medians of 3,144 and 15,853 cps —
  a factor of five for the *same molecule*.
- **The campaign crosses a daylight-saving transition** (26 Oct 2025). Nothing
  in the file hints at it.
- **The met columns each hold their value twice.**

Do not reveal these. Let them find one or two, then move on — you will hit the
wind direction in C and can return to the rest if time allows.

> **3. "It said it cannot know the time zone. Does that matter?"**

Yes — everything diurnal depends on it. Park it; it returns in E.

---

## Segment B · architecture · 3 min

```
Before you write any code: write ARCHITECTURE.md describing the tool we are
about to build. I want a list of series on the left, and on the right two plots
for whichever series I select - the timeseries, and the mean diurnal cycle split
into weekday and weekend. Plus a separate panel for correlating two series, a
way to type notes against each series that get saved to a JSON file, and a
button that turns those notes into a Word overview document. Keep it short.
```

**Why this earns its 3 minutes with this audience:** they have never seen a tool
plan its own work. Open `ARCHITECTURE.md` on the projector and read two lines of
it out. Then:

> **"It has now written down what it thinks we asked for. This is the cheapest
> moment to catch a misunderstanding — and the last easy one."**

---

## Segment C · the GUI · 10 min

### C1 — **paste block 3 from [`gui_prompt.txt`](gui_prompt.txt)**

The full GUI description lives in `gui_prompt.md` / `gui_prompt.txt` so you can
copy it in one go. It asks for the filterable left-hand list, the two plots, the
correlation panel, the notes file and the Word button, and it ends with *"keep
it minimal — just what I have asked for, no extra features."*

**Do not retype it from memory and do not drop the last line.**

```
.venv\Scripts\python.exe -m streamlit run app.py
```

⚠️ **Cold start is 14 s.** Say something while it boots.

### C2 — the audience picks

> **"Pick something to look at. Here is the menu."**

| Option | Filter to | Why it goes somewhere rehearsed |
|---|---|---|
| **1. Traffic** ⭐ | `C7H9` (toluene) + `gas_NO` | **The best science on screen.** Weekday peaks at **07:00** (3,831 cps); weekend peaks at **19:00** (2,575). The whole profile inverts between weekday and weekend — morning commute vs Saturday evening. Verified |
| **2. Wood burning vs traffic** | `eBCwb` + `eBCff` | Different evening behaviour; the ff/wb split is a real result |
| **3. Weekend effect** | `C6H7` (benzene) + `gas_NO2` | Weekend curves visibly lower — the cleanest science on screen |
| **4. Meteorology** | family = Meteorology | **Leads straight to the wind-direction trap.** Steer here if nobody picks it |

### C3 — ⚠️ THE CENTREPIECE. Get wind direction on screen

If the room has not chosen it, choose it yourself:

> **"Let's add the wind — direction tells us where the pollution came from."**

Select `met_Wind_Direction (degrees)`. You get a smooth, entirely plausible
diurnal curve sitting around **171°**, i.e. a southerly wind, with a weekday and
a weekend line. No error, no warning, nothing to suggest a problem.

**It is wrong.** Verified on this file:

| | value |
|---|---|
| naive arithmetic mean of degrees | **171° (south)** |
| correct vector / circular mean | **220° (southwest)** |
| worst single hour (15:00) | naive 174° vs true **249°** — off **75°** |
| mean absolute error across the 24 hours | **49°** |
| hours wrong by more than 45° | **13 of 24** |
| observations within 45° of north | 20.3 % |

Ask:

> **"That says the wind was southerly. Does anyone believe that number?"**

Then the reveal: **you cannot average a compass bearing.** The mean of 350° and
10° is 180° — due south — when the true answer is 0°, due north. Every
observation near north drags the average to the middle of the dial.

Then fix it live:

```
Wind direction is a circular variable - you cannot take an arithmetic mean of
degrees, because 350 and 10 average to 180 instead of 0. Use a vector mean
instead: average the sine and cosine and take the arctangent. Fix the diurnal
plot and record in the app which averaging method is being used.
```

**Watch the curve move by 50 degrees.** That is the whole lecture in one plot.

> **"Nothing failed. No error, no warning. The code was right; the physics was
> wrong. And the only reason we caught it is that somebody in this room knows
> what a wind rose is."**

Ask the closing question of the segment:

> **"How many other columns in these 881 have a problem like this that we
> haven't looked for?"**

---

## Segment D · notes → JSON · 5 min

```
Add a way to write a note against whichever series I have selected - who said
it and what they said - and append it to notes.json on disk the moment I save,
so restarting the app cannot lose anything. Structure the file as one entry per
series so I can use it later. Show the notes for the selected series underneath
the plots.
```

Then **collect two or three interpretations from the room and type them in
verbatim.** Their words, not a tidied version.

Good ones to ask for:

- *"What should we write down about that wind direction?"* ← the best note in the
  file, and it is theirs
- *"Why is the weekend curve lower but not flat?"*
- *"What would you need to know before you put this in a paper?"*

Show them `notes.json` in the editor. Seeing their own sentence appear as
structured data lands well with people who have never done this.

---

## Segment E · Word overview · 4 min

Drop the prompt log in first (one paste, prepared in advance):

```powershell
Copy-Item "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\prompts_for_report.json" ".\prompts.json"
```

```
Add a button that builds a Word document from notes.json: a section per series
with its notes and basic statistics, the figures currently on screen, and a
provenance section filled in automatically - data file and its SHA-256, row and
column count, date range, time base, time zone, which averaging I used, how
wind direction was averaged, how missing data were handled, the tool, the model,
the Python and pandas versions, the timestamp, and the prompts from prompts.json.
```

Open the .docx on the projector and scroll to **Provenance**. Two rows carry the
whole lecture:

```
Wind direction averaging     vector (circular) mean
Time zone                    not stated in the data file
```

> **"Two rows. The first one only says 'vector mean' because somebody in this
> room caught it — an hour ago it said 'arithmetic mean of degrees' and the
> document would have been just as confident. The second one says we never knew,
> which is the honest answer, and it is in there because a person asked the
> question in the first ten minutes.**
>
> **Everything else in this document is reproducible. Those two rows are the
> reason it is also *correct* — and neither of them came from the tool."**

---

## Segment F · correlations · 3 min · **drop this first**

```
Add a panel where I pick any two series and see a scatter plot coloured by hour
of day, with Pearson r, Spearman and n.
```

Two rehearsed pairs:

| Pair | Result (verified on the full campaign) |
|---|---|
| `H3O_C6H7+` vs `H3O_C10H17+` | **r = 0.86** overall. High — but **not a shared source**: **0.95 at night** against **0.50 at midday**, and both anticorrelate with wind speed (−0.41 and −0.31). It is shared boundary-layer dilution, not chemistry |
| `NH4_C3H10NO+` vs `H3O_C3H7O+` | **r = 0.88** — and this is **the same compound measured two ways**, medians 3,144 vs 15,853 cps. A brilliant "what does r even mean here?" moment |

---

## If something stalls

```powershell
git -C ..\MONALISA_fallback checkout -q stage-3-notes
Copy-Item -Force ..\MONALISA_fallback\app.py .
```

Streamlit reloads on save. Per-segment fallbacks in
[day_of_checklist.md](day_of_checklist.md).

## Numbers to know cold

| | |
|---|---|
| Wind direction, naive vs true | **171° vs 220°**, worst hour off **75°** |
| NOX closure | raw `NO+NO2` = 14.3 vs NOX 7.9; converted = **7.92 vs 7.90**, r = 1.0000 |
| Acetone, two modes | 3,144 (NH₄⁺) vs 15,853 (H₃O⁺) cps, r = 0.88 |
| DST | transition at **26 Oct 01:00 UTC**; a naive `+2 h` mislabels **285 rows (9.7 %)** |
| Days averaged | 45 weekday, 16 weekend |
| Benzene vs monoterpenes | **0.86 all / 0.95 night / 0.50 midday** |
| Toluene diurnal | weekday peak **07:00** (3,831 cps); weekend peak **19:00** (2,575) |

> All numbers above are from the **full campaign** file the demo now uses. Earlier
> drafts of this script quoted values from a two-week subset (0.77 / 0.84 / 0.61)
> — those are superseded. Do not mix the two sets.
