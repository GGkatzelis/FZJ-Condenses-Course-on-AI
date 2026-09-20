# Reference build

`app.py` is the finished state of the demo app — what a good live run should
produce by the end of segment E. It is the `stage-3e` state.

It is kept here, outside `prep/rehearsal_*/`, so that it is tracked in git:
the rehearsal folders are git-ignored because they contain copies of the
MONALISA data.

To run it, drop it next to a folder containing `data/MONALISA_Paris_2025.csv`
(i.e. a copy of `live_template/`) and:

```
.venv\Scripts\python.exe -m streamlit run app.py
```

Staged versions of this app, one per demo segment, are on the branches
`stage-3a` … `stage-3e` in `prep/checkpoints/` (a separate git repo, also
ignored here because it carries the data alongside each stage).
