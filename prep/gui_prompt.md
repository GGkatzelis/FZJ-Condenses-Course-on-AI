# The GUI prompt — copy and paste these

Four blocks, in order. Each is written the way you would actually say it out
loud, so it reads naturally if you narrate while pasting. Everything between the
fences is what you paste — nothing else.

Plain-text versions with no markdown, for a clean paste, are in
[`gui_prompt.txt`](gui_prompt.txt).

---

## 1 · Look at the file first  *(segment A, ~7 min)*

```
There is a CSV in data/. Read it and tell me what is in it: how many rows, what
period it covers, what the columns are, and how much of each column is actually
present. Tell me anything you cannot determine from the file itself. Do not plot
anything and do not clean anything yet.
```

Then **stop and ask the room** what it did *not* ask about. That pause is the
most valuable three minutes of the lecture — see `prompt_script.md`, A2.

---

## 2 · Have it plan before it builds  *(segment B, ~3 min)*

```
Before you write any code, write ARCHITECTURE.md describing the tool we are
about to build, based on the description I am about to give you. Keep it to one
page. Then wait for me before writing any code.
```

Paste block 3 immediately after. Open `ARCHITECTURE.md` on the projector and
read two lines of it aloud — this audience has never seen a tool plan its own
work, and it is the cheapest moment to catch a misunderstanding.

---

## 3 · ⭐ The GUI itself — the main paste  *(segment C, ~10 min)*

```
I want a small app for browsing this dataset. Here is what it should look like:

- A list of all the available series down the left-hand side. There are hundreds
  of columns, so I need to be able to filter that list - both by group and by
  typing part of a name - rather than scrolling one enormous dropdown.

- When I select one or more series (let me pick up to four at once), show me two
  plots on the right:
  - the time series itself, with a switch for the raw resolution, hourly and
    daily averaging
  - the mean diurnal cycle for the same series, with weekdays and weekends drawn
    separately so I can compare them

- Label the axes properly, including units where the data gives them.

- A separate panel where I can choose any two series and see them plotted
  against each other, with the correlation coefficient and the number of points.

- A box where I can type a note about whichever series I am currently looking
  at, together with who said it. Save every note to a JSON file on disk the
  moment I press save, organised one entry per series, so that restarting the
  app cannot lose anything. Show the notes for the selected series underneath
  the plots.

- A button that turns those notes into a Word document: one section per series
  with its notes and some basic statistics, the plots that are currently on
  screen, and a provenance section recording which file the data came from, what
  period it covers, and how it was processed.

Build it with Streamlit. Keep it minimal - just what I have asked for, no extra
features.
```

> **Why the wording matters.** "Hundreds of columns, so I need to filter"
> prevents an unusable 880-item dropdown. "Weekdays and weekends drawn
> separately" is what puts the weekend effect on screen. "The moment I press
> save" is what gets you an atomic write instead of an in-memory list. "Keep it
> minimal" is the scope-control clause — an independent run wrote 1,161 lines
> without it. **Do not drop that last line.**

Then run it:

```
.venv\Scripts\python.exe -m streamlit run app.py
```

---

## 4 · Fix the wind direction  *(segment C, the reveal)*

Only after someone in the room has questioned the wind-direction curve. See
`prompt_script.md` C3 for the numbers and the exact staging.

```
Wind direction is a circular variable - you cannot take an arithmetic mean of
degrees, because 350 and 10 average to 180 instead of 0. Use a vector mean
instead: average the sine and the cosine and take the arctangent. Fix the
diurnal plot, and record in the app and in the report which averaging method is
being used.
```

---

## If you want it in one paste instead of four

Works, but you lose the architecture beat and the "what did it not ask?" pause,
and you get one long silent build with no partial result to fall back on. Only
do this if you are badly behind:

```
Read the CSV in data/, then build a Streamlit app for browsing it. A filterable
list of all the series down the left. When I select up to four, show the time
series and the mean diurnal cycle with weekdays and weekends separately. A
separate panel for correlating any two series. A box to type notes against the
selected series, appended to a JSON file on disk immediately. A button that
builds a Word document from those notes with the figures, basic statistics and a
provenance section. Keep it minimal.
```
