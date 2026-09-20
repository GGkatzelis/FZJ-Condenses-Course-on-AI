# Prompt script — live demo, Thursday 24 Sep 2026, 13:45–15:15

Type these verbatim. Each segment has **prepared menu options** — offer the
audience only these, because these are the ones that have been rehearsed.

Total budget **32 min** of demo inside the 90-min lecture.
Timings measured in rehearsal are in [trap_log.md](trap_log.md).

## The framing: **audit the AI** (chosen 2026-09-19)

An independent run given only these prompts **caught the met duplication and the
time zone by itself, unprompted, inside segment A**, and volunteered the unit
problems too. See [rehearsal_2_comparison.md](rehearsal_2_comparison.md).

So the demo is **not** "watch it fail". It is:

> **The tool gets it right. You only know that because you checked — and every
> check required atmospheric science. Expertise did not become optional; it
> moved from doing the analysis to auditing it. That is the harder job, because
> a confident correct answer and a confident wrong answer look identical until
> you do the work.**

**Three rules that follow from this:**

1. **Every time it catches something, hand the verification to the room.** Do
   not confirm it yourself. Ask *"how would you check that?"* and then check it
   live. The audience does the science; the AI is the thing under audit.
2. **Credit it out loud when it is right.** Pretending to be disappointed reads
   as dishonest to this audience and wastes the stronger lesson.
3. **The genuine failures on slides 7, 8 and 9 are yours, not the AI's.** They
   are your analysis of real defaults on real data. Never present them as live
   AI output.

**Two mechanical notes:**

- The duplication only shows up in a **sum**. Means and medians are immune, so
  if you want the doubled number on screen at all you must ask for a total —
  prompt **B4**.
- **There are no negative ion values in this file.** Do not offer them as a
  beat; the nine chosen compounds never go negative. (`gas_O3` has three.)

**Scope control.** Rehearsal 2 wrote 1161 lines from these prompts where
rehearsal 1 wrote 370. Every build prompt below therefore ends with **"Keep it
minimal — one tab, no extra features."** Do not drop that clause, and interrupt
if it starts adding things you did not ask for.

---

## Before you start (not on the clock)

Terminal already open in the live folder, environment already built:

```
.venv\Scripts\python.exe -m streamlit run app.py
```

Leave the browser tab open at `localhost:8501` on a second window.

**Do not put `prompts.json` in the live folder yet** — it lists every prompt in
order and would hand the session the whole plan. You drop it in at the start of
segment E with one command; see `day_of_checklist.md`.

---

## Segment A · load and inspect · 7 min

### A1 — the opening prompt

```
Look at the CSV in data/. Tell me what is in it: how many rows, what time
period, what the columns are, what units they are in, and how much of each
column is actually present. Do not plot anything yet and do not clean
anything. Just describe what you find.
```

**What to expect:** a correct row/column count, the date range, and a coverage
table. It will read `CLAUDE.md` and repeat the units from there.

### A2 — the pause. Ask the room before you type anything

> **"It just described this file to us. What does it *not* know?"**

**Take bets before it answers.** Rehearsal 2 volunteered most of this list
unprompted in segment A, so asking the room *first* is what preserves the
tension — it becomes "did you spot it too?" rather than "will it fail?".

Let them answer. Steer towards, in this order:

1. **What time zone are these timestamps?** Nothing in the file says. *(If it
   has already flagged this itself — likely — credit it and ask the room what
   difference the answer would make to the diurnal plots.)*
2. **What do the ion numbers mean physically?** They are raw cps, so they are
   not comparable between ions and cannot be summed.
3. **Is `gas_eBCff` a gas?** No — it is aerosol black carbon with a misleading
   prefix.
4. **Is `gas_CO` on the same scale as the others?** No — mg/m³ against µg/m³, a
   factor of 1000.
5. **Where does the 11 % of missing VOC data go?** It is not random: isolated
   30-min gaps recurring roughly every 3.5 h, which is an instrument duty
   cycle. Anything that fills those gaps with zeros is fabricating data.

> **Do not ask about negative values.** There are none in these nine columns —
> see the correction in `trap_log.md`. If someone raises it, the honest answer
> is that PTR data *can* go negative from background subtraction but these
> compounds are all far above background; `gas_O3` has three such values.

### A3 — build the first working thing

```
Build a Streamlit app called app.py with an Overview tab that shows what you
just described: row count, date range, time step, and a table of every column
with its unit, percent valid, min, median and max. Then tell me how to run it.

Keep it minimal - one tab, no extra features.
```

→ **checkpoint `stage-3a`**

---

## Segment B · time series and diurnals · 10 min

### B1 — the audience picks

> **"Pick two compounds. Here is the menu."**

| Option | Columns | Why it goes somewhere |
|---|---|---|
| **1. Traffic pair** | toluene `H3O_C7H9+` + `gas_NO` | Clean weekday morning peak; sets up the time-zone question |
| **2. Traffic vs wood burning** | `gas_eBCff` + `gas_eBCwb` | Very different evening behaviour; ff/wb split is a real result |
| **3. Biogenic vs anthropogenic** | isoprene `H3O_C5H9+` + benzene `H3O_C6H7+` | Isoprene tracks temperature, benzene does not |
| **4. A consumer-product VOC** | D5 siloxane `H3O_C10H31O5Si5+` | Peaks in the morning with people, not with traffic — surprises everyone |

```
Add a Time series tab. Let me choose up to four columns from a dropdown and
plot them against time, with a toggle for 30-minute, hourly and daily
averaging. Label the axes with the correct units.

Keep it minimal - one tab, no extra features.
```

### B2 — the diurnal

```
Add a Diurnal tab that shows the mean value for each hour of the day, averaged
over all days, for the columns I choose. Let me switch between mean and median.

Keep it minimal - one tab, no extra features.
```

### B3 — the time-zone moment

Plot **option 1** (toluene + NO) and ask:

> **"The morning peak is at hour 7 in this file. Is that plausible?"**

**Have this straight before you go on stage** — it is the one place the demo can
bite back:

- The file is **UTC**. Paris was on **CEST (UTC+2)** on these dates.
- So the file's 07:00 peak is **09:00 local**, and NO peaks at 08:00 file time
  = **10:00 local**.
- Taken at face value as local time, the peaks sit at 06–08, which looks like a
  *textbook* European rush hour. **The wrong reading looks more convincing than
  the right one.** That is the lesson — say it out loud.
- If a student objects that 09–10 local is late for rush hour: they are right to
  push. NO₂ peaks at 06 UTC = 08:00 local, which *is* textbook. The later NO
  peak reflects titration and boundary-layer growth, not the emission time.
- The evening maxima sit at 19–20 UTC = **21–22 local**, which is far too late
  for traffic. That is the clue that the evening peak is **boundary-layer
  collapse**, not emissions — the same lesson as slide 8.

### B4 — ⚠️ DO NOT SKIP. The centrepiece of the demo

```
How much rain fell over the whole two weeks, and which day was wettest? Also
give me the total global radiation dose per day in MJ/m2.
```

**Two reference answers. Know both numbers cold:**

| | de-duplicated (**correct**) | naive row-sum (**doubled**) |
|---|---|---|
| Rainfall, 14 days | **26.7 mm** | 53.4 mm |
| Radiation, mean | **9.76 MJ/m²/day** | 19.5 MJ/m²/day |
| Radiation, daily max | 15.5 MJ/m² | ~31 MJ/m² |
| Wettest day | 4 Oct, **7.3 mm** | 4 Oct, 14.6 mm |

Note the wettest *day* is 4 Oct either way — every day doubles by exactly
2.000, so the ranking is preserved. **The tell is always the magnitude.**

---

#### ✅ Path 1 — it de-duplicates correctly. **This is the likely path.**

Rehearsal 2 returned 26.7 mm and 9.76 MJ/m²/day, and volunteered the insolation
argument itself. Credit it, then hand the audit to the room:

> **"It got that right, and it explained why. How would *you* have known it was
> right?"**

Make them verify it:

```
Show me the first six rows of the met columns for a daytime hour.
```

They see the duplicated values for themselves. Then the question the lecture is
actually about:

> **"It claimed the doubled figure was physically impossible. Is that argument
> correct? What *is* the clear-sky maximum at this latitude in late September?"**

(About 18–20 MJ/m²/day at the surface; top-of-atmosphere is ~20–24. So
19.5 MJ/m²/day as a *fortnight mean*, in a period with rain on six days, is
impossible. 9.76 is right.)

The tool produced a correct answer *and* a correct justification — and nobody in
the room could confirm either without knowing the insolation ceiling at
48.85 °N. That is the whole lecture in one exchange.

---

#### Path 2 — it returns the doubled numbers

Then you have the classical version. Do not announce the error:

> **"53 millimetres in a fortnight, and 19.5 megajoules per square metre per
> day. Is either of those plausible?"**

Push them to the radiation, not the rain — 53 mm is high but arguable, whereas
19.5 MJ/m²/day is impossible. Then the same confirming prompt above, and the
same closing point: it ran clean, it looked plausible, and only the physics
caught it.

→ **checkpoint `stage-3b`**

---

## Segment C · correlations · 7 min

### C1 — the audience picks a pair

| Option | Pair | Rehearsed outcome |
|---|---|---|
| **1. Benzene vs monoterpenes** | `H3O_C6H7+` vs `H3O_C10H17+` | r ≈ 0.9. **The slide-8 trap** — high r, no shared source |
| **2. eBCff vs NO** | `gas_eBCff` vs `gas_NO` | Genuinely co-emitted by traffic. The honest positive control |
| **3. Isoprene vs temperature** | `H3O_C5H9+` vs `met_Sheltered_Temperature` | Real biogenic driver; a physical mechanism, not just r |
| **4. NO vs O₃** | `gas_NO` vs `gas_O3` | Strong **negative** r from titration — anticorrelation with a cause |

```
Add a Correlations tab. Let me pick any two columns, show a scatter plot with
the points coloured by hour of day, and print Pearson r, Spearman, and n.

Keep it minimal - one tab, no extra features.
```

### C2 — the point of the segment

Run **option 1**, then:

> **"r is 0.9. Do benzene and monoterpenes come from the same source?"**

They do not. Benzene is traffic and solvents; monoterpenes at an urban site are
largely consumer products and vegetation. They correlate because **both
accumulate under the same shallow nocturnal boundary layer and both get diluted
at midday**. Show it:

```
Split that correlation by time of day: night 00-05 against midday 11-16, and
also correlate both compounds against wind speed.
```

Night r is much higher than midday r, and both anticorrelate with wind speed.
The correlation is **dilution**, not chemistry.

**Reference numbers for this window (22 Sep – 5 Oct), know them cold:**

| | n | Pearson | Spearman |
|---|---|---|---|
| all points | 598 | **0.771** | 0.812 |
| night 00–05 | 148 | **0.838** | 0.776 |
| midday 11–16 | 149 | **0.612** | 0.736 |

Wind speed vs benzene **−0.516** (−0.762 at night); vs monoterpenes **−0.377**.

#### ✅ If it reaches the right conclusion by itself

Rehearsal 2 did, and went further than the script. Expect it to offer:

- **partial correlation controlling for CO collapses r from 0.77 to ~0.35–0.46**
  — most of the apparent association is shared combustion and dilution.
  *(I verify **+0.353** with the standard first-order formula; rehearsal 2
  reported 0.46. The number is method-dependent, so quote it as "roughly
  halves", not as a precise figure.)* Controlling for wind speed alone barely
  moves it: **+0.727**.
- **monoterpenes show no temperature dependence at all: r = −0.017** (verified)
- monoterpenes track **D5 siloxane at +0.756** (verified), pointing at consumer
  products rather than vegetation
- and that a defensible answer needs **PMF plus wind-direction sectoring**, not
  a pairwise r

Do not compete with it. Put the audit to the room instead:

> **"It says these don't share a source, and it's right. Which single number in
> that argument would you check first — and how?"**

The strongest answer is the **temperature test, with isoprene as the control**:

| | vs temperature |
|---|---|
| isoprene (genuinely biogenic) | **+0.229** |
| monoterpenes | **−0.017** |

If the monoterpene signal here were biogenic it *must* track temperature the way
isoprene does. It does not, while isoprene in the same file does — so the
instrument and the method are fine and the difference is real. That is a
**physical falsification test with a built-in positive control**, which is a
different and better thing than any correlation coefficient. It is also exactly
the kind of check the tool will not decide to care about on your behalf.

> Note: the app already warns you when Pearson and Spearman disagree by more
> than 0.15, which is a cheap, honest guard worth pointing out.

→ **checkpoint `stage-3c`**

---

## Segment D · notes panel · 5 min

```
Add a Notes tab. I want to type in an interpretation, tag it with a segment and
who said it, and have it appended to notes.json on disk the moment I press save
— so that restarting the app cannot lose anything. Show all notes so far
underneath, newest first.

Keep it minimal - one tab, no extra features.
```

Then **actually collect two or three interpretations from the room and type them
in verbatim.** Their words, not a tidied version — that is the point of the
segment and it is what makes the report theirs.

Good prompts to the room:

- *"Why is the evening peak later than the morning one?"*
- *"Would you trust the rainfall number now?"*
- *"What would you need to know before publishing any of this?"*

→ **checkpoint `stage-3d`**

---

## Segment E · Word report · 3 min

```
Add a Report tab with a button that writes a Word document containing the
figures currently on screen, a statistics table for the selected series, every
note from notes.json, and a provenance section that is filled in automatically:
data file name and SHA-256, row and column count, date range, time base, time
zone, the averaging and statistic I selected, how missing data were handled,
the tool, the model, the Python and pandas versions, the timestamp, and the
list of prompts from prompts.json.

Keep it minimal - one tab, no extra features.
```

**Open the .docx on the projector and scroll to Provenance.** The closing line:

> **"Time zone: not stated in the data file."** The report says so honestly,
> because nothing in the file ever told us. Everything else in this document is
> reproducible. That field is the one that would have sunk the analysis — and
> the only reason it is flagged is that a person in this room asked the
> question in the first ten minutes.

→ **checkpoint `stage-3e`**

---

## If something stalls

Fallback is one line. See [day_of_checklist.md](day_of_checklist.md) for the
exact command and the per-segment plan.

```
git -C ..\MONALISA_fallback checkout -q stage-3c
copy /Y ..\MONALISA_fallback\app.py .
```

Streamlit reloads on save, so the app is back within seconds.
