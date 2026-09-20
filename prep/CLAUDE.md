# Plan of record — "AI tools for scientists" (90 min lecture + live demo)

> This file is the authoritative brief for the lecture-demo preparation.
> Any new Claude Code session working in `prep/` should read this first.
> Written 2026-09-19 from Georgios Gkatzelis' briefing.

---

## 0. The event

| | |
|---|---|
| **Lecture** | "AI tools for scientists", 90 minutes |
| **When** | Thursday **24 September 2026, 13:45–15:15** |
| **Where** | FZJ / Universities of Cologne–Wuppertal summer school |
| **Audience** | ~20 Master's and early-PhD students, atmospheric science background |
| **Demo** | Live, audience-directed: Claude Code in VS Code builds a data-analysis tool from real measurement data, in front of the room |

The point of the demo is **not** that the AI succeeds. It is that the AI produces
plausible, runnable, confidently-worded output that is *wrong* in ways only a
domain scientist catches. The prepared "traps" below are the teaching material.

---

## 1. The data

**File:** `MONALISA_campaign_master_30min.csv` (unpublished, MONALISA campaign,
Paris urban ground site, 2025). All campaign members approved its use in this
lecture with AI.

### Hard rules

1. **Never modify, rename or move the original file.** Work on copies only.
2. **Never upload it anywhere.** No web service, no API, no cloud, no paste.
3. The original lives at the repo root *and* is copied to `data_original/`.
   Both are covered by `.gitignore`.

> ⚠️ **Remote risk, handled 2026-09-19.** This folder is a git repo with a
> GitHub remote (`github.com/GGkatzelis/FZJ-Condenses-Course-on-AI`) and had no
> `.gitignore`. A `.gitignore` now excludes `*.csv`, `data_original/`,
> `prep/rehearsal_*/` and `prep/checkpoints/`. **Do not relax those rules.**
> Verify with `git check-ignore -v <file>` before any commit.

### What Georgios reported about the file (to be reproduced, not trusted)

- 2,927 rows, 30-min grid, 1 Sep – 31 Oct 2025.
- 876 series: 427 `NH4_` ions + 430 `H3O_` ions (PTR-ToF-MS, 1-min native),
  11 `gas_` (15-min native), 8 `met_` (1-h native), plus 4 bookkeeping
  columns `n_NH4, n_H3O, n_gas, n_met`.
- **All timestamps UTC.**
- **Met is hourly, labelled end-of-hour**, each value copied into both the
  `h:00` and `h:30` bins (precipitation pairs identical in 100% of cases).
- **Met appears 45–60 min late relative to gas.** Solar-geometry fit of global
  radiation vs computed solar zenith angle for Paris (48.85 °N, 2.35 °E) gives
  a best offset of about **−55 min**. Solar noon in Paris in late September is
  about 11:40 UTC, but the radiation centroid sits on the 12:08 label.
- **Gas is on true UTC within ±15 min.** Photostationary proxy NO·O₃/NO₂
  (NO = µg/m³ ÷ 1.25, NO₂ ÷ 1.91, O₃ ÷ 2.0 → ppb) vs SZA gives about **−10 min**.
- **PTR timing cannot be tested this way** — no VOC responds cleanly to the sun.
- **Gas units are mixed:** NO, NO₂, O₃ in µg/m³; NOX in ppb; CO in mg/m³;
  CH₄/CO₂ in ppm. `eBCff`/`eBCwb` are **aerosol** black carbon (fossil fuel /
  wood burning), *not* gases.
- **Ion columns carry no units.** Range about −1,470 to 90,000; about 1.3 %
  negative (background subtraction).
- **NH₄⁺ formulas include the adduct** — e.g. `NH4_C3H10NO+` is acetone·NH₄⁺.
  The file also holds isotopologues (`[13C]`) and water clusters.

### Verification status

See `prep/data_verification.md` for the reproduced numbers and any
discrepancies. **If a claim above turns out wrong, correct it here and tell
Georgios immediately** — he would rather know now than on Thursday.

### ✅ Answers from Georgios, 2026-09-19

1. **The master grid is START-labelled.** `12:00` means 12:00–12:30, bin centre
   12:15.
2. **Ion units are raw cps** (counts per second, not normalised, not calibrated).
3. **`gas_CH4d` / `gas_CO2d`:** not formally answered. The data support "dry
   mole fraction" — `CO2d > CO2` and `CH4d > CH4` in every row, which is what
   removing water vapour does. Neither column is used in `live_template`, so
   nothing is blocked. **Confirm before quoting it in the lecture.**
4. **Time zone IS a live trap.** `live_template/CLAUDE.md` stays silent about
   UTC. See the warning under Trap 2 in `trap_log.md` — the trap fires
   *backwards* and needs handling on stage.
5. **Met correction: de-duplicate, shift, re-duplicate.** Under start-labelling
   this reduces to a plain **−1 h shift** with zero residual (see below), so it
   is implemented as a uniform shift of the met block by 2 rows.

### Why −1 h is exact, not approximate

A met value labelled `H:00` is an hourly mean labelled at the **end** of its
hour, so it covers `[H−1:00, H:00]`. On a start-labelled 30-minute grid that
hour is precisely the two bins labelled `H−1:00` and `H−0:30`. Shifting the met
block −1 h moves the duplicated pair from `{H:00, H:30}` to `{H−1:00, H−0:30}` —
exactly the bins the hour covers. Verified: radiation centroid moves from 12:41
to **11:41** against a true solar noon of **11:42**, a −1 min residual. The
duplication survives at 100 %, so the doubling trap is intact.

---

## 2. Folder structure

```
FZJ-Condenses-Course-on-AI/
  MONALISA_campaign_master_30min.csv   original, untouched, git-ignored
  data_original/                        untouched copy
  prep/                                 EVERYTHING THAT KNOWS THE ANSWERS
    CLAUDE.md                           <- this file
    data_verification.md
    figures/
    case_study_numbers.md
    prompt_script.md
    trap_log.md
    day_of_checklist.md
    checkpoints/                        git repo, branches stage-3a ... stage-3e
    rehearsal_1/  rehearsal_2/
  live_template/                        CLEAN START FOR THE LIVE DEMO — NO ANSWERS
```

### 🔒 The most important rule

The live demo runs as a **fresh Claude Code session on a copy of
`live_template/` placed outside this folder** (e.g. the Desktop). That session
**must not be able to see `prep/`**, or it will read the trap documentation and
"catch" every trap in a way that looks clairvoyant and destroys the lesson.

**Nothing in `live_template/` may mention:** traps, the met correction, the met
duplication, solar noon, time-zone offsets, or this plan.
Before every rehearsal and before Thursday, grep `live_template/` for:
`trap, correct, shift, offset, solar, noon, UTC, duplicate, local time`.

---

## 3. `live_template/` contents

### Data subset

Window **22 Sep 00:00 – 5 Oct 23:30 2025 UTC** (two full weeks, two weekends).

| Group | Columns |
|---|---|
| Traffic | `H3O_C6H7+` (benzene), `H3O_C7H9+` (toluene), `H3O_C8H11+` (C8 aromatics), `gas_NO`, `gas_NO2`, `gas_CO`, `gas_eBCff` |
| VCP | `H3O_C10H31O5Si5+` (D5 siloxane) |
| Biogenic / mixed | `H3O_C5H9+` (isoprene), `H3O_C10H17+` (monoterpenes) |
| Cooking | `H3O_C9H19O+` (nonanal) |
| Oxidation products | `H3O_C3H7O+` (acetone), `H3O_C2H5O+` (acetaldehyde), `gas_O3` |
| Wood burning | `gas_eBCwb` |
| Met | temperature, RH, wind speed, wind direction, global radiation, precipitation |

### Treatments

- **Met alignment: CORRECT it** (shift per ⛔ Q1).
- **Met duplication: KEEP it.** Deliberate live trap — daily sums of
  precipitation and radiation come out **doubled**.
- **Timestamps: leave in UTC, do not label the time zone** in the data.
  (Time-zone-as-trap pending ⛔ Q4.)
- **Drop** the `n_*` bookkeeping columns.

### `live_template/CLAUDE.md`

Short, neutral data description. **Include:** instrument, site, columns and what
they are, ion units (⛔ Q2), gas units, that eBC is aerosol not gas, and that
negative ion values come from background subtraction.
**Leave out:** the time zone (unless Georgios says otherwise) and the met
duplication.

### `live_template/requirements.txt`

Pinned versions of everything the demo needs: pandas, numpy, plotly or
matplotlib, the GUI framework, python-docx. Installed in a **dedicated
environment inside this folder** and confirmed to work **offline**.

> **Environment note.** Georgios' shared venv is
> `C:\Users\g.gkatzelis\Desktop\My Folders\My Coding\Python\.venv`
> (Python 3.14.3; pandas 3.0.1, numpy 2.4.2, matplotlib 3.10.8, plotly 6.6.0,
> streamlit 1.58.0; **no python-docx**). Use it read-only for prep analysis; do
> **not** install into it — it is shared with his other projects. The demo gets
> its own venv inside this folder. `uv` 0.10.7 is available.

---

## 4. Lecture figures → `prep/figures/`

**Style:** Aptos (fallback Calibri/Arial). Navy `#1F4E79`; orange `#C0622E` for
"goes wrong"; green `#55733D` for "verified"; dark red `#A11212` for errors
only; cream `#F6F4EC` background for case-study figures.
**Export:** PNG, 300 dpi, 16:9-friendly.

**Figure window = 6–13 Oct 2025** — deliberately *different* from the live
subset so the slides do not give the demo away. Check coverage in that window
first and report if it is poor.

| Slide | Figure | Notes |
|---|---|---|
| **8** | "correlation ≠ common source": benzene vs monoterpenes scatter, coloured night (00–05 UTC) vs midday (11–16 UTC). Annotate r for all / night / midday. | Georgios' demo-window values: r = 0.77 all, 0.83 night, 0.61 midday; wind speed anticorrelates about −0.5. **Report what the figure window gives; say so if the pattern does not hold.** |
| **9** | "defaults change the story": toluene diurnal as **mean** and as **median**. | Demo window: mean peaked 07 UTC, median 19 UTC. Axis label "hour (UTC)". Also draft one confident-sounding sentence an AI might write from the mean profile alone. |
| **7** | "it runs ≠ it's correct": ~6-line pandas snippet that runs cleanly and is wrong (e.g. `fillna(0)` before averaging). | Show its output beside the correct result, on real data. |
| **18, 21** | Case study, **from the original uncorrected file**: (a) radiation mean diurnal, vertical line at solar noon 11:40 UTC, peak marked; (b) photostationary proxy diurnal vs solar geometry, showing gas is on time; (c) radiation diurnal after correction. | Save the numbers behind each panel to `prep/case_study_numbers.md`. |

---

## 5. Rehearsal

Copy `live_template/` → `prep/rehearsal_1/`, open it as the working context,
and run the demo exactly as Thursday will go.

| Segment | Budget | Goal |
|---|---|---|
| **A** · load and inspect | 7 min | Describe the file. Pause: *what doesn't it know?* |
| **B** · time series + diurnals | 10 min | Audience picks compounds from a menu |
| **C** · correlations | 7 min | Audience picks pairs |
| **D** · notes panel | 5 min | Students' interpretations typed in, **their words** |
| **E** · Word report | 3 min | Report with figures, stats, the notes, and an automatic **provenance** section: data file, date range, averaging, time zone, tool, model, date, prompts used |

**GUI:** recommend a framework (Georgios leans Streamlit) and justify it.
Notes must be **written to a JSON file on every entry**, so an app restart
cannot lose them. The report reads the notes from that file.

### Deliverables

- `prep/prompt_script.md` — the exact prompt to type per segment, plus 3–4
  prepared menu options per segment that lead somewhere rehearsed.
- `prep/trap_log.md` — where each trap surfaced (or didn't), what the AI said,
  how long each step took, where anything stalled.
- `prep/checkpoints/` — git repo of the rehearsal build, branches
  `stage-3a` ... `stage-3e`, each a working state, plus the one-line command to
  switch to each. **If the live build stalls, switch branch instead of waiting.**

**Run the rehearsal twice.** Run 2 starts from scratch with the finished prompt
script, to measure how much the output varies between runs.

---

## 6. `prep/day_of_checklist.md`

Must cover:

- how to create the live copy on the Desktop
- account and settings to check
- VS Code zoom level for the projector
- window switching order (slides → VS Code → browser → Word)
- backup screen recording (**remind Georgios to record one after rehearsal 2**)
- fallback plan per segment

---

## 7. Working style (Georgios' instructions)

- Before each numbered task: **two lines** on what is about to happen.
  When done: a **short** statement of what was found.
- **If a claim about the data turns out wrong, say so plainly.** Better now
  than Thursday.
- **Stop and ask at every ⛔.** Do not guess those answers.
- Do not install anything globally. Do not touch anything outside this folder.
  (Agreed exception: read-only use of the shared venv above.)

---

## 8. Decisions taken

### GUI: Streamlit — agreed, and here is the argument

Recommended, and it is what the reference build uses (`prep/rehearsal_1/app.py`).

**Why Streamlit over the alternatives, for *this* use:**

- **It is the only one where the code an AI writes live is the app.** No
  callbacks, no layout tree, no component registration — a widget is one line
  that returns a value. That matters when the audience is watching the code
  appear, because they can read it. Dash needs a callback graph; PyQt needs an
  event loop and a `.ui` mental model; both produce code that a non-programmer
  cannot follow on a projector.
- **Hot reload on save.** Claude Code writes the file, Streamlit reloads. No
  restart, no lost state, no dead air — which is what makes the branch-switch
  fallback take seconds.
- **It is already in Georgios' shared venv** (1.58.0), so it is familiar.
- **`st.pyplot` takes a matplotlib figure directly**, and matplotlib is what the
  Word report needs anyway. One plotting stack for screen and document.
- **`streamlit.testing.v1.AppTest` exists**, which is how both rehearsals were
  driven programmatically. Nothing else in this space has a comparable harness.

**What it costs, and why it is acceptable here:**

- **32 s cold start.** Mitigated by starting it before the audience is watching.
- Reruns the whole script on every interaction — irrelevant at 672 rows, and
  `@st.cache_data` covers the read.
- Widget state lives in `st.session_state` and is lost on restart. **This is
  exactly why the notes must go to `notes.json` on every entry**, which they do.

Plotly is installed and available for interactive hover, but the reference build
uses matplotlib throughout so that the on-screen figure and the figure in the
report are the same object.

### Environment: no venv inside `live_template/`

Originally the plan was to ship a ready-made `.venv`. Abandoned — see
`trap_log.md`. Copying 381 MB of small files took **4 min 19 s** on this machine
and Pillow's DLL failed to load at a long destination path. `live_template/` is
now 190 kB and copies instantly; building the environment from a warm `uv`
cache takes **41 s**. That is the day-of procedure.

### `scipy` is a hard requirement

`pandas.corr(method="spearman")` imports `scipy.stats` lazily, so a missing
scipy kills the correlation tab *at render time*, not at startup. Pinned in
`requirements.txt`.

---

## 9. Progress log

| Date | Done |
|---|---|
| 2026-09-19 | Folder structure created. `.gitignore` written — the repo has a GitHub remote and had no ignore file, so the unpublished CSV was one `git add -A` from being published. Plan of record written. **Task 1:** all claims verified, 8 corrections recorded in `data_verification.md`. **Task 2:** structure built. **Task 3:** `live_template/` built — 672 rows × 22 cols, met shifted −1 h, duplication kept, `n_` dropped, neutral `CLAUDE.md`, pinned `requirements.txt`, leak-scanned clean. **Task 4:** six figures + `case_study_numbers.md` + `figure_numbers.json`. **Task 5:** rehearsal 1 complete (all 5 segments pass, scipy bug found and fixed), 5 checkpoint branches verified runnable, `prompt_script.md` and `trap_log.md` written; rehearsal 2 run independently. **Task 6:** `day_of_checklist.md` written. |

## 10. ⚠️ The premise changed — read `rehearsal_2_comparison.md`

An independent session given only the verbatim prompts **caught the met
duplication and the time zone unprompted, inside segment A**, computed the
correct 26.7 mm and 9.76 MJ/m²/day, produced the insolation-ceiling argument by
itself, and volunteered the mixed-units and eBC-is-aerosol problems as well.

**"Watch the AI get it wrong" is not a safe premise for this dataset.** The
recommended reframe is **"audit the AI"**: keep every prompt, and each time it
catches something, hand the verification to the room. The lesson is stronger —
*it was right, and only domain knowledge could establish that*. Slides 7/8/9
still carry genuine failures because those are analyses of real defaults, not
live AI output. Full reasoning and three concrete options in
`rehearsal_2_comparison.md`.

**Georgios needs to choose the framing before Thursday.**

## 11. Outstanding

- **Aptos is not installed on this machine** — figures fell back to Calibri. If
  the slides use Aptos there will be a visible mismatch. Either install Aptos
  and re-run `prep/scripts/make_figures.py`, or set the slides to Calibri.
- **Confirm the meaning of `d`** in `gas_CH4d` / `gas_CO2d` (⛔ 3 above) before
  quoting it.
- **Record the backup screen recording** after rehearsal 2 — see
  `day_of_checklist.md` step 6.
- **Slide 8 numbers: the briefing was right, for its own window.** Every figure
  Georgios quoted reproduces exactly in the **live** window (22 Sep – 5 Oct):
  r = 0.771 all / 0.838 night / 0.612 midday, wind speed vs benzene −0.516.
  The slide figure uses the **6–13 Oct** window instead, which gives 0.91 /
  0.98 / 0.40 and wind speed −0.34 / −0.31. The figure and its annotations are
  internally consistent, so nothing needs changing — but **do not mix the two
  sets of numbers**, and if you say "−0.5" out loud, that is the live-window
  value, not the one on the slide.
