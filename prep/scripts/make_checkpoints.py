"""Generate the stage builds for the live demo and commit each to
prep/checkpoints on its own branch, as a linear history.

Build order follows prompt_script.md. Correlations now come BEFORE notes,
because the notes prompt wires notes into both panels at once and the
correlation argument is the one worth writing down:
  stage-2-plots         left list + timeseries + weekday/weekend diurnal
  stage-3-notes         + notes saved to notes.json
  stage-4-report        + Word overview with provenance
  stage-5-correlations  + correlation panel
  stage-6-winddir-fix   + vector mean for wind direction (the reveal)

Stages 2-5 deliberately carry the NAIVE wind-direction mean, because that is
what a live build writes. Only the last stage fixes it, mirroring the demo arc.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
BUILD = ROOT / "prep" / "sandbox"
SRC = BUILD / "app.py"
CK = ROOT / "prep" / "checkpoints"

SECTIONS = ["Time series", "Correlations", "Overview report"]
MARK = {"Time series": "# ---- Time series + diurnal ----",
        "Correlations": "# ---- Correlations ----",
        "Overview report": "# ---- Word overview ----"}

# (branch, sections kept, notes?, circular wind?, message)
STAGES = [
    ("stage-2-plots", ["Time series"], False, False,
     "left-hand series list, timeseries and weekday/weekend diurnal"),
    ("stage-3a-correlations", ["Time series", "Correlations"], False, False,
     "+ correlation panel"),
    ("stage-3b-notes", ["Time series", "Correlations"], True, False,
     "+ notes, working on both the series and the correlation panel"),
    ("stage-4-report", ["Time series", "Correlations", "Overview report"], True,
     False, "+ Word overview with automatic provenance"),
    ("stage-5-winddir-fix", ["Time series", "Correlations", "Overview report"],
     True, True, "+ vector mean for wind direction (contingency only)"),
]

ARCH = """# Architecture

A single Streamlit app, `app.py`, reading one CSV.

## Layout
- **Left (sidebar).** The list of available series. The file holds ~880, so the
  list is filtered by family and by a name search rather than shown whole.
  Up to four series can be selected at once.
- **Right, "Time series" panel.** Two plots for the selected series:
  1. the series against time, with 30-minute / hourly / daily averaging
  2. the mean diurnal cycle, split into weekday and weekend
- **Right, "Correlations" panel.** Any two series as a scatter plot coloured by
  hour of day, with Pearson r, Spearman and n.
- **Right, "Overview report" panel.** A button that writes a Word document.

## Data flow
```
CSV --> pandas DataFrame (cached)
          |
          +--> plots (matplotlib, rendered to PNG in memory)
          |
          +--> statistics per selected series
          |
notes.json <--> notes panel        (written on every save)
          |
          v
    Word overview (.docx)  =  figures + statistics + notes + provenance
```

## Notes file
`notes.json` is a dictionary keyed by series name, each holding a list of
`{timestamp, author, text}`. Written atomically on every save so that
restarting the app cannot lose anything.

## Provenance
The Word document records, automatically: the data file and its SHA-256, row
and column counts, the date range, the time base, the time zone, which
averaging was selected, how wind direction was averaged, how missing data were
handled, the tool and model, library versions, the timestamp, and the prompts
used.
"""


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(CK), *args], check=check,
                          capture_output=True, text=True)


def build(keep, with_notes, circular) -> str:
    text = SRC.read_text(encoding="utf-8")

    if circular:
        text = text.replace("CIRCULAR_WIND = False", "CIRCULAR_WIND = True", 1)

    for name in SECTIONS:
        if name in keep:
            continue
        start = text.index(MARK[name])
        later = [text.index(MARK[n]) for n in SECTIONS
                 if n != name and MARK[n] in text and text.index(MARK[n]) > start]
        text = text[:start] + (text[min(later):] if later else "")

    if not with_notes:
        # drop the note form and the note listing, keep the plots
        text = re.sub(r"\n        with right:\n(?:.*?\n)*?(?=\n        notes = )",
                      "\n", text)
        text = re.sub(r"\n        notes = read_json\(NOTES, \{\}\)\n"
                      r"(?:.*?\n)*?(?=\n# ----|\Z)", "\n", text)
        text = text.replace('left, right = st.columns([1.05, 1])',
                            'left, = st.columns(1)')
        # and the correlation-panel note form, so a pre-notes stage has none
        text = re.sub(r"\n    with st\.form\(\"note_corr\"(?:.*?\n)*?(?=\n# ----|\Z)",
                      "\n", text)

    names = [n for n in SECTIONS if n in keep]
    lo = text.index("tab_ts, tab_corr, tab_report = st.tabs(")
    hi = text.index("\n\n", lo)
    handles = {"Time series": "tab_ts", "Correlations": "tab_corr",
               "Overview report": "tab_report"}
    assign = ", ".join(handles[n] for n in names)
    listed = ", ".join(f'"{n}"' for n in names)
    if len(names) == 1:
        assign += ","
    text = text[:lo] + f"{assign} = st.tabs([{listed}])" + text[hi:]
    return text


if not (CK / ".git").exists():
    sys.exit("prep/checkpoints is not a git repo")

for idx, (branch, keep, with_notes, circular, msg) in enumerate(STAGES):
    # -B for EVERY stage, not -b after the first. `-b` fails when the branch
    # already exists, and with check=False that failure was swallowed, so every
    # later stage committed onto whichever branch was still checked out. -B
    # force-creates-or-resets at the current HEAD, which is exactly the linear
    # history we want, and it is idempotent across re-runs.
    git("checkout", "-q", "-B", branch)

    for stale in ("app.py", "ARCHITECTURE.md"):
        (CK / stale).unlink(missing_ok=True)

    if keep:
        (CK / "app.py").write_text(build(keep, with_notes, circular),
                                   encoding="utf-8")
    for f in ("CLAUDE.md", "requirements.txt", "requirements-lock.txt"):
        if (BUILD / f).exists():
            shutil.copy2(BUILD / f, CK / f)
    (CK / "data").mkdir(exist_ok=True)
    shutil.copy2(BUILD / "data" / "MONALISA_Paris_2025.csv",
                 CK / "data" / "MONALISA_Paris_2025.csv")
    shutil.copytree(BUILD / ".streamlit", CK / ".streamlit", dirs_exist_ok=True)

    git("add", "-A")
    r = git("commit", "-q", "-m", f"{branch}: {msg}", check=False)
    state = "committed" if r.returncode == 0 else (r.stdout.strip() or "no change")

    # Verify what actually landed, not what was intended. The old version
    # printed `keep` - the intent - which hid the branch bug above completely.
    on_disk = (CK / "app.py").read_text(encoding="utf-8")
    got_tabs = on_disk.count("with tab_")
    got_notes = "note_ts" in on_disk
    got_wind = "CIRCULAR_WIND = True" in on_disk
    ok = (got_tabs == len(keep) and got_notes == with_notes
          and got_wind == circular)
    print(f"{branch:22s} {state:12s} {'OK ' if ok else '!! '}"
          f"tabs={got_tabs}/{len(keep)} "
          f"lines={len(on_disk.splitlines()):4d} "
          f"notes={got_notes} wind={got_wind}")
    if not ok:
        sys.exit(f"{branch}: built content does not match the stage definition")

print("\nbranches:")
print(git("branch", "--format=  %(refname:short)").stdout.rstrip())
