# Reference build

`app.py` is the finished state of the demo app — what a good live run should
produce by the end of segment E. It matches the `stage-5-winddir-fix` branch,
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
| `stage-3a-correlations` | C1 | 254 | 2 |
| `stage-3b-notes` | C2 | 275 | 2 |
| `stage-4-report` | D | 370 | 3 |
| `stage-5-winddir-fix` | — | 370 | 3 |

Correlations come before notes because the notes prompt wires notes into both
panels at once, and because the correlation is the thing worth writing a note
about.

Stages 2–4 deliberately carry the **naive** arithmetic mean for wind direction,
because that is what a live build might write. Only `stage-5-winddir-fix`
corrects it. In the 2026-09-20 trial the tool used a vector mean unaided, so
that stage is a contingency rather than an expected step.

There is no architecture *stage*: block 2 asks for a spoken summary before
coding. `ARCHITECTURE.md` is written in segment E instead, alongside the
README, once there is something real to describe.

Regenerate all of them with `prep/scripts/make_checkpoints.py`.
