"""MONALISA Paris 2025 — interactive analysis tool.

Built live during the lecture. Run with:
    .venv\\Scripts\\python.exe -m streamlit run app.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
CSV = HERE / "data" / "MONALISA_Paris_2025.csv"
NOTES = HERE / "notes.json"
PROMPTS = HERE / "prompts.json"
REPORT = HERE / "MONALISA_report.docx"

# Set this once the time base has actually been established from the metadata.
DATA_TIMEZONE = "not stated in the data file"

NAMES = {
    "H3O_C6H7+": "benzene",
    "H3O_C7H9+": "toluene",
    "H3O_C8H11+": "C8 aromatics",
    "H3O_C10H31O5Si5+": "D5 siloxane",
    "H3O_C5H9+": "isoprene",
    "H3O_C10H17+": "monoterpenes",
    "H3O_C9H19O+": "nonanal",
    "H3O_C3H7O+": "acetone",
    "H3O_C2H5O+": "acetaldehyde",
}
NAVY, ORANGE, GREEN = "#1F4E79", "#C0622E", "#55733D"

st.set_page_config(page_title="MONALISA Paris 2025", layout="wide")


# --------------------------------------------------------------------- data
@st.cache_data
def load() -> pd.DataFrame:
    df = pd.read_csv(CSV)
    df["time"] = pd.to_datetime(df["time"])
    return df


def label(col: str) -> str:
    """Human-readable label for a column."""
    if col in NAMES:
        return f"{NAMES[col]}  ({col})"
    return col


def unit_of(col: str) -> str:
    if "(" in col:
        return col[col.index("(") + 1: col.rindex(")")]
    return "cps" if col.startswith(("H3O_", "NH4_")) else ""


df = load()
TIME = "time"
ions = [c for c in df.columns if c.startswith("H3O_")]
gases = [c for c in df.columns if c.startswith("gas_")]
mets = [c for c in df.columns if c.startswith("met_")]
measured = ions + gases + mets


# -------------------------------------------------------------------- notes
def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def add_note(segment: str, author: str, text: str) -> None:
    """Append a note and write it to disk immediately, so a restart cannot lose it."""
    notes = read_json(NOTES, [])
    notes.append({"timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                  "segment": segment, "author": author.strip(), "text": text.strip()})
    NOTES.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


# ------------------------------------------------------------------- plots
def style(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fig_timeseries(cols, resample=None):
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=120)
    for c, col in zip(cols, (NAVY, ORANGE, GREEN, "#7B5AA6")):
        s = df.set_index(TIME)[c]
        if resample and resample != "raw (30 min)":
            s = s.resample({"hourly": "1h", "daily": "1D"}[resample]).mean()
        ax.plot(s.index, s.values, lw=1.1, color=col, label=label(c))
    style(ax, "time", " / ".join(sorted({unit_of(c) for c in cols})))
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def diurnal(col, stat="mean"):
    h = df[TIME].dt.hour
    g = df.groupby(h)[col]
    return getattr(g, stat)()


def fig_diurnal(cols, stat):
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=120)
    for c, col in zip(cols, (NAVY, ORANGE, GREEN, "#7B5AA6")):
        p = diurnal(c, stat)
        ax.plot(p.index, p.values, marker="o", ms=4, lw=2, color=col, label=label(c))
    style(ax, f"hour of day  ({DATA_TIMEZONE})", stat)
    ax.set_xticks(range(0, 24, 3))
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def fig_scatter(x, y, colour_by_hour=True):
    fig, ax = plt.subplots(figsize=(6.4, 5.2), dpi=120)
    s = df[[x, y, TIME]].dropna()
    if colour_by_hour:
        sc = ax.scatter(s[x], s[y], c=s[TIME].dt.hour, cmap="twilight_shifted",
                        s=22, lw=0, alpha=.85)
        cb = fig.colorbar(sc, ax=ax)
        cb.set_label(f"hour  ({DATA_TIMEZONE})")
    else:
        ax.scatter(s[x], s[y], s=22, lw=0, alpha=.8, color=NAVY)
    r = s[x].corr(s[y])
    rs = s[x].corr(s[y], method="spearman")
    ax.set_title(f"Pearson r = {r:.2f}    Spearman = {rs:.2f}    n = {len(s)}",
                 fontsize=11)
    style(ax, f"{label(x)}  [{unit_of(x)}]", f"{label(y)}  [{unit_of(y)}]")
    fig.tight_layout()
    return fig, r, rs, len(s)


def png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    return buf.getvalue()


# --------------------------------------------------------------------- UI
st.title("MONALISA — Paris, autumn 2025")

tabs = st.tabs(["Overview", "Time series", "Diurnal", "Correlations",
                "Notes", "Report"])

# ---- Overview ----
with tabs[0]:
    st.subheader("What is in the file")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("rows", f"{len(df):,}")
    c2.metric("columns", df.shape[1])
    c3.metric("first", str(df[TIME].min()))
    c4.metric("last", str(df[TIME].max()))

    step = df[TIME].diff().dropna().value_counts()
    st.write(f"**Time step:** " + ", ".join(f"{v}× {k}" for k, v in step.items()))
    st.write(f"**Time zone:** {DATA_TIMEZONE}")

    st.subheader("Columns and coverage")
    cov = pd.DataFrame({
        "column": measured,
        "what": [NAMES.get(c, c.split(" ")[0].split("_", 1)[-1]) for c in measured],
        "unit": [unit_of(c) for c in measured],
        "% valid": [round(100 * df[c].notna().mean(), 1) for c in measured],
        "min": [round(df[c].min(), 3) for c in measured],
        "median": [round(df[c].median(), 3) for c in measured],
        "max": [round(df[c].max(), 3) for c in measured],
    })
    st.dataframe(cov, width="stretch", hide_index=True)

    neg = {c: int((df[c] < 0).sum()) for c in measured if (df[c] < 0).any()}
    if neg:
        st.caption("Columns containing negative values: "
                   + ", ".join(f"{c} ({n})" for c, n in neg.items()))

# ---- Time series ----
with tabs[1]:
    st.subheader("Time series")
    pick = st.multiselect("compounds", measured,
                          default=["H3O_C7H9+"], format_func=label, max_selections=4,
                          key="ts_pick")
    res = st.radio("averaging", ["raw (30 min)", "hourly", "daily"],
                   horizontal=True, key="ts_res")
    if pick:
        f = fig_timeseries(pick, res)
        st.pyplot(f)
        st.session_state["fig_ts"] = png(f)

# ---- Diurnal ----
with tabs[2]:
    st.subheader("Mean diurnal cycle")
    st.caption("Each point is the average over all days at that hour of day.")
    pick = st.multiselect("compounds", measured, default=["H3O_C7H9+"],
                          format_func=label, max_selections=4, key="di_pick")
    stat = st.radio("statistic", ["mean", "median"], horizontal=True, key="di_stat")
    if pick:
        f = fig_diurnal(pick, stat)
        st.pyplot(f)
        st.session_state["fig_di"] = png(f)
        st.dataframe(pd.DataFrame({label(c): diurnal(c, stat).round(2) for c in pick}),
                     width="stretch")

# ---- Correlations ----
with tabs[3]:
    st.subheader("Correlation between two series")
    c1, c2 = st.columns(2)
    x = c1.selectbox("x", measured, index=measured.index("H3O_C6H7+"),
                     format_func=label, key="cx")
    y = c2.selectbox("y", measured, index=measured.index("H3O_C10H17+"),
                     format_func=label, key="cy")
    by_hour = st.checkbox("colour points by hour of day", value=True, key="cbh")
    f, r, rs, n = fig_scatter(x, y, by_hour)
    st.pyplot(f)
    st.session_state["fig_sc"] = png(f)
    st.session_state["corr"] = {"x": x, "y": y, "pearson": r, "spearman": rs, "n": n}
    if abs(r - rs) > 0.15:
        st.warning(f"Pearson ({r:.2f}) and Spearman ({rs:.2f}) disagree by "
                   f"{abs(r - rs):.2f}. The relationship is not linear, or a few "
                   f"extreme points are doing the work.")

# ---- Notes ----
with tabs[4]:
    st.subheader("Interpretation notes")
    st.caption("Saved to notes.json the moment you press Save — a restart cannot "
               "lose them.")
    with st.form("note_form", clear_on_submit=True):
        seg = st.selectbox("segment", ["A load and inspect", "B time series",
                                       "C correlations", "D discussion", "E other"])
        who = st.text_input("who said it", placeholder="first name, or 'the room'")
        txt = st.text_area("their interpretation, in their words", height=110)
        if st.form_submit_button("Save note") and txt.strip():
            add_note(seg, who or "anon", txt)
            st.success("saved")

    notes = read_json(NOTES, [])
    st.write(f"**{len(notes)} note(s) on file**")
    for nt in reversed(notes):
        st.markdown(f"> {nt['text']}\n\n— *{nt['author']}*, {nt['segment']}, "
                    f"{nt['timestamp'][11:16]}")
    if notes:
        st.download_button("download notes.json",
                           json.dumps(notes, indent=2, ensure_ascii=False),
                           file_name="notes.json", mime="application/json")

# ---- Report ----
with tabs[5]:
    st.subheader("Word report")
    st.caption("Figures currently on screen, the statistics behind them, every "
               "note, and an automatic provenance section.")

    def build_report() -> Path:
        from docx import Document
        from docx.shared import Inches, Pt

        doc = Document()
        doc.add_heading("MONALISA — Paris, autumn 2025", 0)
        doc.add_paragraph(
            f"Interactive analysis produced during the lecture "
            f"“AI tools for scientists”, {dt.date.today().isoformat()}.")

        doc.add_heading("Figures", 1)
        for key, cap in (("fig_ts", "Time series"),
                         ("fig_di", "Mean diurnal cycle"),
                         ("fig_sc", "Correlation")):
            if st.session_state.get(key):
                doc.add_heading(cap, 2)
                doc.add_picture(io.BytesIO(st.session_state[key]), width=Inches(6.2))

        doc.add_heading("Statistics", 1)
        cols = sorted({*st.session_state.get("ts_pick", []),
                       *st.session_state.get("di_pick", []),
                       st.session_state.get("cx", ""), st.session_state.get("cy", "")})
        cols = [c for c in cols if c in df.columns]
        if cols:
            tb = doc.add_table(rows=1, cols=6)
            tb.style = "Light Grid Accent 1"
            for i, h in enumerate(["series", "unit", "n", "mean", "median", "max"]):
                tb.rows[0].cells[i].text = h
            for c in cols:
                s = df[c].dropna()
                r = tb.add_row().cells
                r[0].text = label(c)
                r[1].text = unit_of(c)
                r[2].text = f"{len(s)}"
                r[3].text = f"{s.mean():.3g}"
                r[4].text = f"{s.median():.3g}"
                r[5].text = f"{s.max():.3g}"

        cr = st.session_state.get("corr")
        if cr:
            doc.add_paragraph(
                f"Correlation: {label(cr['x'])} vs {label(cr['y'])} — "
                f"Pearson r = {cr['pearson']:.3f}, Spearman = {cr['spearman']:.3f}, "
                f"n = {cr['n']}.")

        doc.add_heading("Interpretations from the room", 1)
        notes = read_json(NOTES, [])
        if not notes:
            doc.add_paragraph("No notes were recorded.")
        for nt in notes:
            p = doc.add_paragraph(style="Intense Quote")
            p.add_run(nt["text"])
            doc.add_paragraph(f"— {nt['author']}, {nt['segment']}, {nt['timestamp']}"
                              ).runs[0].font.size = Pt(9)

        # ---------------- provenance, assembled automatically ----------------
        doc.add_heading("Provenance", 1)
        sha = hashlib.sha256(CSV.read_bytes()).hexdigest()
        prompts = read_json(PROMPTS, [])
        rows = [
            ("Data file", CSV.name),
            ("SHA-256 of data file", sha[:32] + "…"),
            ("Rows × columns", f"{len(df)} × {df.shape[1]}"),
            ("Date range", f"{df[TIME].min()} to {df[TIME].max()}"),
            ("Time base", "30 minutes"),
            ("Time zone", DATA_TIMEZONE),
            ("Averaging applied", st.session_state.get("ts_res", "raw (30 min)")),
            ("Diurnal statistic", st.session_state.get("di_stat", "mean")),
            ("Missing data", "excluded pairwise; gaps are not filled"),
            ("Tool", "Claude Code in VS Code"),
            ("Model", "Claude Opus 5"),
            ("Python", platform.python_version()),
            ("pandas / numpy", f"{pd.__version__} / {np.__version__}"),
            ("Report generated", dt.datetime.now().isoformat(timespec="seconds")),
        ]
        tb = doc.add_table(rows=0, cols=2)
        tb.style = "Light List Accent 1"
        for k, v in rows:
            c = tb.add_row().cells
            c[0].text = k
            c[1].text = str(v)

        doc.add_heading("Prompts used", 2)
        if prompts:
            for i, pr in enumerate(prompts, 1):
                doc.add_paragraph(f"{i}. {pr}", style="List Number"
                                  if False else None)
        else:
            doc.add_paragraph("prompts.json not found — prompts were not recorded.")

        doc.save(REPORT)
        return REPORT

    if st.button("Build the report", type="primary"):
        p = build_report()
        st.success(f"written: {p.name}")
        st.download_button("download the .docx", p.read_bytes(), file_name=p.name,
                           mime="application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document")
