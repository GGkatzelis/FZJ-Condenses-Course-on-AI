# Reference build

`app.py` is the finished state of the demo app — what a good live run should
produce by the end of segment F. It matches the `stage-6-winddir-fix` branch,
so it uses the **vector mean** for wind direction.

It is kept here, outside `prep/sandbox/`, so that it is tracked in git: the
sandbox and checkpoint folders are git-ignored because they carry copies of the
MONALISA data.

To run it, drop it next to a folder containing
`data/MONALISA_Paris_2025.csv` — i.e. a copy of `live_template/` — and:

```
.venv\Scripts\python.exe -m streamlit run app.py
```

On its own it will raise `FileNotFoundError`, because there is no `data/`
directory beside it. That is expected.

## Staged versions

One per demo segment, on branches in `prep/checkpoints/` (a separate git repo,
also ignored here):

| Branch | Segment | Lines | Tabs |
|---|---|---|---|
| `stage-2-plots` | B | 234 | 1 |
| `stage-3-notes` | C | 249 | 1 |
| `stage-4-report` | D | 344 | 2 |
| `stage-5-correlations` | F | 370 | 3 |
| `stage-6-winddir-fix` | — | 370 | 3 |

Stages 2–5 deliberately carry the **naive** arithmetic mean for wind direction,
because that is what a live build might write. Only `stage-6` corrects it. In
the 2026-09-20 trial the tool used a vector mean unaided, so stage 6 is a
contingency rather than an expected step.

There is no architecture stage: block 2 of `gui_prompt.txt` asks for a spoken
summary before coding rather than an `ARCHITECTURE.md` file.

Regenerate all of them with `prep/scripts/make_checkpoints.py`.
