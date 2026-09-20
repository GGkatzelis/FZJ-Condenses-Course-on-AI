# Day-of checklist — Thursday 24 September 2026, 13:45–15:15

FZJ / Cologne–Wuppertal summer school · ~20 MSc and early-PhD students
Demo budget: 32 min inside the 90-min lecture.

---

## The evening before

### 1. Create the live folder on the Desktop

The live session must **not** be able to see `prep/`. Copy only
`live_template/`, and rename it so nothing on screen says "template".

```powershell
$src = "$env:USERPROFILE\Desktop\My Folders\My Coding\Python\GitHub\FZJ-Condenses-Course-on-AI\live_template"
Copy-Item -Recurse $src "$env:USERPROFILE\Desktop\MONALISA_live"
```

Copies in about a second — 190 kB, no venv inside.

### 2. Build the environment inside it (~41 s)

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

**Expected: exactly one hit** — "global solar radiation", which is just the
variable's name. Anything else, stop and fix it.

Also confirm the folder contains **no** `app.py`, `notes.json`, `prompts.json`
or `.git`.

### 5. Start the app once, cold, and leave it

Cold start is **32 s**. Do it now, not in front of the room.

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

(There is no `app.py` yet — that is fine, this is just to warm the import cache.
Do it after stage A exists, or run the import check in step 2 instead.)

### 6. Record the backup screen recording

**⚠️ Do this after rehearsal 2 and before you go to bed.** If the live demo
fails completely, you play the recording and narrate over it. Nobody will know.

- Xbox Game Bar: `Win + Alt + R`, or OBS if you want the webcam too
- Record the **whole demo, all five segments**, at the projector resolution
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

- [ ] `prompt_script.md` open **on your laptop screen only**, never mirrored
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
| 3 | **Browser** at `localhost:8501` | B, C, D |
| 4 | **Word** — opens on its own for the report | E only |
| 5 | **File Explorer** at the live folder | E, to show the .docx appear |

Rehearse the switch 1 → 2 → 3 once before the room fills.

---

## Fallback plan, per segment

The fallback is always the same two lines. From the live folder:

```powershell
git -C ..\MONALISA_fallback checkout -q stage-3c
Copy-Item -Force ..\MONALISA_fallback\app.py .
```

Streamlit reloads on save, so the app is back in seconds. Substitute the stage
you need.

| Segment | If it stalls | Say this |
|---|---|---|
| **A** load and inspect | Fall back to `stage-3a`. Worst case, describe the file from the Overview table on the slide | *"Let's not watch it type — here's what it found."* |
| **B** time series / diurnals | `stage-3b`. If the audience's pick misbehaves, switch to **option 1** (toluene + NO), which is the most rehearsed | *"That one's interesting for a different reason — let's come back to it."* |
| **B4** the rainfall total | **Expect it to get this right** — rehearsal 2 did, unprompted, and produced the insolation-ceiling argument itself. Credit it, show the raw duplicated rows anyway, then hand the verification to the room. See the "if it catches it" branch in `prompt_script.md` | *"It got that right, and explained why. How would* you *have known?"* |
| **C** correlations | `stage-3c`. If the split-by-hour prompt fails, the numbers are on slide 8 — put the slide up and use those | *"We have this one prepared — here's the same analysis."* |
| **D** notes panel | `stage-3d`. If the form breaks, collect interpretations **on the whiteboard** and type them in later. Do not lose the segment — it is the one where the room owns something | *"Let's just write them up here."* |
| **E** Word report | `stage-3e`. If the .docx will not build, open the rehearsal report from the fallback folder and scroll to Provenance. The closing point is the *content* of that section, not the act of generating it | *"Here's one from the rehearsal — the section I want you to see is at the end."* |
| **Anything, catastrophically** | Play `MONALISA_demo_backup.mp4` and narrate | *"The live version is having a moment — luckily I recorded one."* |

### If Claude Code itself is down or rate-limited

Go straight to the recording, then run the rest of the lecture from the slides.
Say plainly that the tool is unavailable — an audience of scientists will
recognise that as the most honest possible demonstration of *"do not build a
workflow you cannot check"*.

---

## Known risks, ranked

0. **Scope creep, not failure, is the schedule risk.** Rehearsal 2 wrote
   **1161 lines** and **7 tabs** where rehearsal 1 wrote ~370 and 6 — three
   times the code, from the same prompts. That will not fit 32 minutes. Add
   *"keep it minimal, one tab, no extras"* to the prompts, be ready to
   interrupt, and use the checkpoint branches as a **time** fallback rather
   than a crash fallback. Never promise the audience a specific layout.
1. **Streamlit's 32 s cold start.** Start it before the audience is watching.
2. **The time-zone pushback in segment B3.** The wrong reading looks *more*
   convincing than the right one. Have the NO₂-at-08:00-local answer ready —
   see [trap_log.md](trap_log.md), Trap 2.
3. **The duplication trap needs prompt B4.** Every mean and median is immune to
   it. Skip B4 and the trap never appears.
4. **`scipy`.** Already fixed and pinned. If you ever rebuild the environment
   from something other than `requirements.txt`, check it is there — the
   correlation tab dies without it, and only when that tab renders.
5. **A running server is not a working app.** Streamlit returns HTTP 200 with a
   completely broken script. Look at the page, not the port.

---

## Immediately after

- [ ] Save `notes.json` and the generated `.docx` — the students' own words are
      worth keeping and they make a good follow-up email
- [ ] Note which menu options the audience actually chose, for next time
- [ ] **Do not commit the live folder to git.** It contains unpublished
      MONALISA data. The `.gitignore` in the prep repo covers the prep copies,
      but the Desktop folder is outside it and has no protection at all
