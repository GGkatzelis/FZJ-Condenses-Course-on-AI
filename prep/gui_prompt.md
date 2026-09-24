# The GUI prompts — copy and paste these

Six blocks, one per segment, in order. Plain-text versions with no markdown —
which is what you should actually paste from — are in
[`gui_prompt.txt`](gui_prompt.txt).

**Build step by step, not in one shot.** Three reasons:

1. One-shot means 3–4 minutes of silence with no partial result if it goes wrong.
2. **Watching it correctly modify code it wrote ten minutes ago is the moment
   the penny drops.** This audience half-expects an AI to write code from
   scratch — that reads as fancy autocomplete. Adding a feature to a 300-line
   file without breaking it is the part they do not expect.
3. Each block is a pause where the audience directs the next step, and each maps
   to a fallback branch.

| Block | Segment | Budget |
|---|---|---|
| 1 · the audit | A | 12 min |
| 2 · the GUI: list + two plots | B | 8 min |
| **3a · correlation explorer** | **C** | **12 min for both** |
| **3b · notes** | **C** | |
| 4 · the Word report | D | 4 min |
| 5 · the reveal | E | 4 min |

Correlations and notes share one segment on purpose: a correlation gives the
room something genuinely arguable, where a timeseries mostly answers itself.
That merge also removed the droppable segment — the cut order is now inside the
segments, at the end of `gui_prompt.txt`.

---

## Block 1 · the audit

```
There is a CSV in data/. Read it and tell me what is in it: how many rows, what
period it covers, what the columns are, and how much of each column is actually
present. Tell me anything you cannot determine from the file itself. Do not plot
anything and do not clean anything yet.
```

Then **stop and ask the room what it did *not* ask about.** Expect roughly two
minutes of silence while it profiles 881 columns — that is the demo working, not
hanging. Do not fill it. Full staging in `prompt_script.md` A2–A4.

---

## Block 2 · the GUI

Note the opening line. It does the job the old `ARCHITECTURE.md` segment did —
catching a misunderstanding while it is still free — but spoken in thirty
seconds, with no document the room cannot yet evaluate. The document itself is
written in block 5, once there is something real to describe.

```
Before you write any code, tell me in one paragraph what you are about to
build, so I can check you understood me. Then build it.

I want a small app for browsing this dataset:

- A list of all the available series down the left-hand side. There are hundreds
  of columns, so I need to filter that list - both by group and by typing part
  of a name - rather than scrolling one enormous dropdown.

- When I select one or more series (let me pick up to four at once), show me two
  plots on the right:
  - the time series itself, with a switch for the raw resolution, hourly and
    daily averaging
  - the mean diurnal cycle for the same series, with weekdays and weekends drawn
    separately so I can compare them

- Label the axes properly, including units where the data gives them.

Build it with Streamlit, in app.py. Keep it minimal - just what I have asked
for, no extra features.
```

> **Why the wording matters.** *"Hundreds of columns, so I need to filter"*
> prevents an unusable 880-item dropdown. *"Weekdays and weekends drawn
> separately"* is what puts the weekend effect on screen. **Do not drop the last
> line** — independent runs wrote 416 and 1,161 lines, and only the constrained
> ones stayed inside the time budget.

```
.venv\Scripts\python.exe -m streamlit run app.py
```

⚠️ ~22 s to the first page. Talk over it.

---

## Block 3a · the correlation explorer

The most ambitious build in the demo. Paste it verbatim from
[`gui_prompt.txt`](gui_prompt.txt) — it asks for a ranked bar chart and table of
the twenty strongest correlations on the left, and a fitted scatter with full
statistics on the right, driven by selecting a table row.

**Selection is by table row, not by clicking a bar.** `st.dataframe(on_select=
"rerun", selection_mode="single-row")` is robust; reading back which *bar* was
clicked from Plotly's selection payload is the fiddliest part of that API and
not worth two or three correction rounds on stage. If it goes smoothly you can
ask for bar-clicking as a bonus.

**Demo `gas_NO`, not toluene.** Measured on this file:

| compound picked | what the top 20 looks like |
|---|---|
| **`gas_NO`** | NOX 0.88, **D5 siloxane 0.70**, eBCff 0.69, toluene 0.68, eBCwb 0.66, CO 0.66 — a recognisable traffic cluster, every label meaningful |
| **toluene** | all twenty are other PTR ions from the same instrument; `C7H8` at **0.989** is essentially the same molecule, then alkyl fragments. Twenty bars between 0.93 and 0.99, not one recognisable name |

The toluene case is the punchline, not a failure — see `prompt_script.md` C1.

Compute is not a concern: ranking one compound against all 880 series takes
**0.2 s**. Switching compound re-renders in about **4.6 s**.

## Block 3b · notes

```
Add a box where I can type a note about whatever I am currently looking at,
together with who said it - and make it work in both places: against a selected
series in the time-series panel, and against the pair I have chosen in the
correlation panel. Save every note to a JSON file on disk the moment I press
save, organised one entry per series or pair, so that restarting the app cannot
lose anything. Show the notes for the current selection underneath the plots.

Keep it minimal - no extra features.
```

*"The moment I press save"* is what gets you an atomic disk write rather than an
in-memory list. Then take the correlation argument from the room, **type it
verbatim**, and show them `notes.json` in the editor.

---

## Block 4 · the Word report

Drop the prompt log in **first**, so the provenance section is populated:

```powershell
Copy-Item "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\prompts_for_report.json" ".\prompts.json"
```

```
Add a button that turns those notes into a Word document: one section per
series with its notes and some basic statistics, the plots that are currently
on screen, and a provenance section recording which file the data came from,
what period it covers, and how it was processed.

Keep it minimal - no extra features.
```

Open the .docx and scroll to **Provenance**.

---

## Block 5 · ⭐ the reveal — the finale

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

**Have File Explorer visible.** They watch the tree fill: `app.py`,
`README.md`, `ARCHITECTURE.md`, `notes.json`, the `.docx` — from one CSV and
three lines of text.

Two things are doing the real work here.

**The README's last clause** makes the tool **state its own judgement calls in
writing**, as the closing artifact. Read two of them out loud — that is the
lecture's thesis, in the tool's own words. It is asked for first deliberately:
if you run out of time mid-generation, that is the document you want.

**The ARCHITECTURE diagram** is the visual payoff. Ask for it *in plain text* —
without that, you get prose paragraphs, which on a projector look like any
other wall of words. An ASCII data-flow diagram reads from the back row and is
the last thing they see.

> If the README is vague about decisions, push once: *"be specific about how you
> averaged each kind of column."* That reliably produces the four calls from B2.

---

## Contingency · if it used a plain mean on wind direction

In the trial it got this right unaided and used a vector mean. If a run does
not:

```
Wind direction is a circular variable - you cannot take an arithmetic mean of
degrees, because 350 and 10 average to 180 instead of 0. Use a vector mean
instead: average the sine and the cosine and take the arctangent. Fix the
diurnal plot, and record in the app and in the report which averaging method is
being used.
```

---

## One-paste fallback · only if badly behind

Loses every pause and gives one long silent build with no partial result.

```
Read the CSV in data/, then build a Streamlit app for browsing it. A filterable
list of all the series down the left. When I select up to four, show the time
series and the mean diurnal cycle with weekdays and weekends separately. A
separate panel for correlating any two series. A box to type notes against the
selected series, appended to a JSON file on disk immediately. A button that
builds a Word document from those notes with the figures, basic statistics and a
provenance section. Keep it minimal.
```
