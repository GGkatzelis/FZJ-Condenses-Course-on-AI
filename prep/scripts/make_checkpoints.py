"""Generate the five stage builds from the finished app and commit each to
prep/checkpoints on its own branch, as a linear history.

Each stage is a genuinely runnable app: the tab list and the tab indices are
rebuilt to match the sections that survive, so nothing dangles.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
BUILD = ROOT / "prep" / "rehearsal_1"
SRC = BUILD / "app.py"
CK = ROOT / "prep" / "checkpoints"

SECTIONS = ["Overview", "Time series", "Diurnal", "Correlations", "Notes", "Report"]
MARK = {n: f"# ---- {n} ----" for n in SECTIONS}
STAGES = [
    ("stage-3a", 1, "load and inspect: overview tab only"),
    ("stage-3b", 3, "+ time series and mean diurnal cycles"),
    ("stage-3c", 4, "+ correlation between two series"),
    ("stage-3d", 5, "+ notes panel persisted to notes.json"),
    ("stage-3e", 6, "+ Word report with automatic provenance"),
]
EXTRA = ["CLAUDE.md", "requirements.txt", "requirements-lock.txt"]


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(CK), *args], check=check,
                          capture_output=True, text=True)


def build(keep: int) -> str:
    text = SRC.read_text(encoding="utf-8")
    names = SECTIONS[:keep]

    # 1. cut every section not kept: from its marker to the next marker, or EOF
    for i, name in enumerate(SECTIONS):
        if name in names:
            continue
        start = text.index(MARK[name])
        later = [text.index(MARK[n]) for n in SECTIONS[i + 1:] if MARK[n] in text]
        text = text[:start] + text[min(later):] if later else text[:start]

    # 2. rebuild the tab list
    lo = text.index("tabs = st.tabs(")
    hi = text.index("\n\n", lo)
    text = text[:lo] + f'tabs = st.tabs([{", ".join(chr(34) + n + chr(34) for n in names)}])' \
        + text[hi:]

    # 3. renumber the surviving "with tabs[N]:" lines in the order they appear
    def renumber(m, _c=[0]):
        out = f"with tabs[{_c[0]}]:"
        _c[0] += 1
        return out

    renumber.__defaults__ = ([0],)
    text = re.sub(r"with tabs\[\d+\]:", renumber, text)
    return text


if not (CK / ".git").exists():
    sys.exit("prep/checkpoints is not a git repo - run git init there first")

for idx, (branch, keep, msg) in enumerate(STAGES):
    if idx == 0:
        git("checkout", "-q", "-B", branch, check=False)
    else:
        git("checkout", "-q", "-b", branch, check=False)

    (CK / "app.py").write_text(build(keep), encoding="utf-8")
    for f in EXTRA:
        if (BUILD / f).exists():
            shutil.copy2(BUILD / f, CK / f)
    (CK / "data").mkdir(exist_ok=True)
    shutil.copy2(BUILD / "data" / "MONALISA_Paris_2025.csv",
                 CK / "data" / "MONALISA_Paris_2025.csv")
    shutil.copytree(BUILD / ".streamlit", CK / ".streamlit", dirs_exist_ok=True)

    git("add", "-A")
    r = git("commit", "-q", "-m", f"{branch}: {msg}", check=False)
    state = "committed" if r.returncode == 0 else (r.stdout.strip() or "nothing to commit")
    print(f"{branch:10s} {state:18s} tabs: {', '.join(SECTIONS[:keep])}")

print("\nbranches in prep/checkpoints:")
print(git("branch", "--format=  %(refname:short)  %(subject)").stdout.rstrip())
