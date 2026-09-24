# Day-of checklist — Thursday 24 September 2026, 13:45–15:15

FZJ / Cologne–Wuppertal summer school · ~20 MSc and early-PhD students
Demo budget: 40 min inside the 90-min lecture (confirmed 2026-09-24).

---

## The evening before

### 1. Create the live folder on the Desktop

The live session must **not** be able to see `prep/`. Copy only
`live_template/`, and rename it so nothing on screen says "template".

```powershell
$src = "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\live_template"
Copy-Item -Recurse $src "$env:USERPROFILE\Desktop\MONALISA_live"
```

Copies in about two seconds — 18.8 MB (one CSV), no venv inside. Measured 2.3 s for this folder and the fallback together.

### 2. Build the environment inside it (~24 s from a warm cache)

```powershell
cd "$env:USERPROFILE\Desktop\MONALISA_live"
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

**Then prove it works offline**, because the lecture-room network cannot be
trusted:

```powershell
.venv\Scripts\python.exe -c "import pandas, numpy, matplotlib, plotly, streamlit, docx, scipy; print('all imports ok')"
```

### 3. Put the fallback beside it, not inside it

```powershell
Copy-Item -Recurse `
  "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\checkpoints" `
  "$env:USERPROFILE\Desktop\MONALISA_fallback"
```

It is a **sibling** folder, so the live Claude session never sees it — but it is
one command away if the build stalls.

### 4. Verify the live folder gives nothing away

```powershell
cd "$env:USERPROFILE\Desktop\MONALISA_live"
Select-String -Path CLAUDE.md,requirements.txt -Pattern "trap|correct|shift|offset|noon|duplicate|local time|UTC|time zone"
```

**Expected: no hits at all.** `live_template/CLAUDE.md` is now three lines: the
data are unpublished, and where the venv is. No units, no instrument, no site
description, no column list, no time zone. Anything else, stop and fix it.

Also confirm the folder contains **no** `app.py`, `notes.json`, `prompts.json`
or `.git`.

### 5. Warm the import cache

The live folder has no `app.py` yet — the whole point is that you build it on
stage. But the first page costs about **22 s** warmed (17 s of imports plus 5 s
to read the CSV) — and **66.7 s** if the bytecode cache is cold. Warm it now:

```powershell
.venv\Scripts\python.exe -c "import streamlit, matplotlib.pyplot, pandas, docx, scipy; print('warm')"
```

Then, once segment C has produced `app.py`, the launch is quick. If you want to
be certain, run the fallback app once and close it:

```powershell
Copy-Item ..\MONALISA_fallback\app.py .\_warmup.py
.venv\Scripts\python.exe -m streamlit run _warmup.py    # Ctrl+C, then:
Remove-Item .\_warmup.py
```

**Do not leave `_warmup.py` in the folder.**

### 6. Record the backup screen recording

**⚠️ Do this after you have walked the demo yourself, and before you go to
bed.** If the live demo fails completely, you play the recording and narrate
over it. Nobody will know.

- Xbox Game Bar: `Win + Alt + R`, or OBS if you want the webcam too
- Record the **whole demo, all six segments A–F**, at the projector resolution
- Save it as `Desktop\MONALISA_demo_backup.mp4` and **open it once to confirm it
  plays** with audio
- Also export the slides to PDF as a second fallback

---

## 45 minutes before

### Accounts and settings

- [ ] Claude Code signed in — run one throwaway prompt to confirm the session
      is live and not asking to re-authenticate
- [ ] Check the usage/rate-limit indicator. A 32-min live build is a lot of
      tokens; know where you stand before you start
- [ ] **Model set to Claude Opus 5.** Confirm in `/status`
- [ ] Permission mode: **accept edits** for the demo folder. Being asked to
      approve every write in front of an audience is deadly
- [ ] `/status` also confirms the working directory is `MONALISA_live` and
      **not** the prep repo
- [ ] Notifications, Slack, Teams, email: **off**. Do Not Disturb on
- [ ] Disable OS and VS Code auto-update prompts

### Display

- [ ] Projector at **1920×1080**, mirrored not extended (extended is where
      windows go missing)
- [ ] **VS Code zoom level 2–3** (`Ctrl + =` three times from default, or
      `"window.zoomLevel": 2.5` in settings). Check readability from the
      **back row**, not from your seat
- [ ] Terminal font ≥ 16 pt; editor font ≥ 18 pt
- [ ] Browser zoom **150 %** for the Streamlit page
- [ ] **Light theme everywhere.** Dark themes wash out on most projectors
- [ ] Hide the VS Code minimap and breadcrumbs; close the sidebar (`Ctrl + B`)
- [ ] Laptop power plan on **high performance**, charger plugged in

### Files and windows

- [ ] `prompt_script.md` and **`gui_prompt.txt`** open **on your laptop screen
      only**, never mirrored. `gui_prompt.txt` is what you paste from
- [ ] `data_dictionary.md` open too — it is where you look up what any ion
      column actually is when someone asks
- [ ] Close every unrelated window and tab

### `prompts.json` — do NOT put it in the live folder before you start

It lists every prompt in order, so it would hand the live session the whole
plan. `prep/prompts_for_report.json` is pre-filled with the real prompts. Drop
it in **at the start of segment E**, once every prompt has actually been used:

```powershell
Copy-Item "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\prep\prompts_for_report.json" `
          "$env:USERPROFILE\Desktop\MONALISA_live\prompts.json"
```

Have this command ready in a scratch file so it is one paste. Without it the
provenance section reads *"prompts.json not found — prompts were not
recorded"*, which is honest but wastes the best line in the report.

---

## Window order

Set these up in this order, then move between them with `Alt + Tab` only. Do
not hunt for windows live.

| # | Window | Used in |
|---|---|---|
| 1 | **Slides** (PowerPoint, presenter view) | throughout |
| 2 | **VS Code** with Claude Code | all segments |
| 3 | **Browser** at `localhost:8501` | C, D, F |
| 4 | **Word** — opens on its own for the report | E only |
| 5 | **File Explorer** at the live folder | **E**, the finale — they watch the tree fill |

Rehearse the switch 1 → 2 → 3 once before the room fills.

**File Explorer is the finale.** This audience has never watched a tool write
its own files. Bring the folder to the front in segment E, when `app.py`,
`README.md`, `notes.json` and the `.docx` are all sitting there and none of them
existed an hour ago. It is more persuasive than any of the plots.

---

## Fallback plan, per segment

The fallback is always the same two lines. From the live folder:

```powershell
git -C ..\MONALISA_fallback checkout -q stage-3b-notes
Copy-Item -Force ..\MONALISA_fallback\app.py .
```

Streamlit reloads on save, so the app is back in seconds. Substitute the stage
you need.

| Segment | Fall back to | If it stalls | Say this |
|---|---|---|---|
| **A** the audit | — | No app exists yet, so nothing to restore. Describe the file yourself from `data_verification.md`, then go to the "what did it *not* ask?" pause, which is the valuable part anyway | *"Let's not watch it type — here's what it found."* |
| **B** the GUI | `stage-2-plots` | If the audience's pick misbehaves, switch to **option 1** (toluene + `gas_NO`), the most rehearsed. If it used a plain mean on wind direction, paste the contingency block — or jump to `stage-5-winddir-fix` to show the corrected curve at once | *"Let me show you the version where that's handled."* |
| **C** correlations + notes | `stage-3a-correlations`, then `stage-3b-notes` | Two pastes, so two fallback points. If the notes form breaks, collect interpretations **on the whiteboard** and type them in later — do not lose this segment, it is where the room owns something. The r values are in `prompt_script.md` C1 if the panel itself fails | *"Let's just write them up here."* |
| **D** Word report | `stage-4-report` | If the .docx will not build, open the prepared one from the fallback folder and scroll to Provenance. The point is the *content* of those rows, not the act of generating them | *"Here's one from the rehearsal — the part I want you to see is at the end."* |
| **E** the reveal | — | Needs no code. If the README comes out thin, read the **provenance table** from the .docx instead — it carries the same judgement calls. Worst case, just show the folder tree and say the line about one CSV and three lines of text | *"Look at what's in this folder that wasn't there an hour ago."* |
| **Anything, catastrophically** | — | Play `MONALISA_demo_backup.mp4` and narrate | *"The live version is having a moment — luckily I recorded one."* |

**What to protect if you run short.** Merging correlations into the notes
segment removed the droppable beat, so the cuts are now inside segments:
**ARCHITECTURE.md** in block 5 (~1.5 min), then **one audience note instead of
three** in C2 (~2 min), then **skip the B1 menu** and pick option 1 yourself
(~2 min). That gets 36 min down to about 30. Never cut segment **A**, the
correlation argument in **C1**, or the README.
| **Anything, catastrophically** | Play `MONALISA_demo_backup.mp4` and narrate | *"The live version is having a moment — luckily I recorded one."* |

### If Claude Code itself is down or rate-limited

Go straight to the recording, then run the rest of the lecture from the slides.
Say plainly that the tool is unavailable — an audience of scientists will
recognise that as the most honest possible demonstration of *"do not build a
workflow you cannot check"*.

---

## Known risks, ranked

1. **Scope creep, not failure, is the schedule risk.** An independent run wrote
   **1,161 lines and 7 tabs** from equivalent prompts, where the first wrote
   370 and 6. That will not fit 32 minutes. Keep the *"minimal — no extra
   features"* clause on every build prompt, interrupt when it embellishes, and
   treat the stage branches as a **time** fallback, not just a crash fallback.
   Never promise the room a specific layout.
2. **The audit is the centrepiece now, not a trap.** Segment A carries the
   lecture. Give it its full 12 minutes and do not fill the silence while it
   profiles 881 columns.
3. **No droppable segment any more.** 40 min, which is the agreed budget, but
   with nothing whole left to cut. The cut order is inside the segments — see
   "What to protect" above.
4. **Block 3a is the most ambitious build.** A ranked bar chart, a selectable
   table and a linked fitted scatter. If it stalls, jump to
   `stage-3a-correlations` rather than debugging live.
4. **The `n_met` moment may not fire** on the trimmed file — 2 + 2 rows is a
   weak signal. Have the fallback line ready; see `prompt_script.md` A3.
4. **Getting wind direction on screen** still matters for B2, since the four
   judgement calls hang off it. If the room picks something else, steer there:
   *"let's add the wind — direction tells us where the pollution came from."*
5. **~22 s to the first page** with 881 columns, and **66.7 s** if the bytecode
   cache is cold. Warm the imports the night before (step 5) — measured, the
   difference is 17 s against 67 s.
6. **`scipy`.** Pinned. If you ever rebuild the environment from anything other
   than `requirements.txt`, check it is present — the correlation panel dies
   without it, and only at the moment that panel renders.
7. **A running server is not a working app.** Streamlit returns HTTP 200 with a
   completely broken script. Look at the page, not the port.
8. **880 series in the picker.** Always filter by family or name first; the list
   caps at 300 entries and will feel broken if you forget.

---

## Immediately after

- [ ] Save `notes.json` and the generated `.docx` — the students' own words are
      worth keeping and they make a good follow-up email
- [ ] Note which menu options the audience actually chose, for next time
- [ ] **Do not commit the live folder to git.** It contains unpublished
      MONALISA data. The `.gitignore` in the prep repo covers the prep copies,
      but the Desktop folder is outside it and has no protection at all
