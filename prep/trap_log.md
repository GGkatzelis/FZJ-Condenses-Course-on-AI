# Trap log — and why the traps were abandoned

**Verdict, 2026-09-20: planted traps do not survive this model. The demo was
reframed around the audit instead.** Staging in `prompt_script.md`.

---

## The trial that settled it

A genuinely independent session was given the bare file, the three-line
`CLAUDE.md`, and only Georgios' paste blocks — no hints, no access to `prep/`,
confined to the Desktop live folder. 18 tool calls, ~12 minutes, a 416-line app.

**It caught essentially everything, unprompted, before writing any plotting
code:**

| Trap | Outcome |
|---|---|
| **Wind direction is circular** | ☠️ **Caught and fixed itself.** It wrote `atan2(mean(sin), mean(cos))`, applied it *only* to wind direction, and quantified the error — *"the circular and arithmetic diurnal means differ by 12 to 75 degrees in every hour"*. Its numbers matched mine exactly. |
| **Met duplication** | ☠️ Caught — *"bit-identical for 100.0 % of pairs in every met column"* |
| **Hourly accumulations, not rates** | ☠️ Caught, via `Sunshine_Duration` reaching 60 min inside a 30-min slot |
| **DST straddle** | ☠️ Caught — noted the period crosses 26 Oct and that the grid shows no repeated hour, *"consistent with UTC or a fixed offset but not proof"* |
| **Time zone unknown** | ☠️ Flagged in four places in the app plus the report |
| **Negative values** | ☠️ Counted per group |
| **Instrument gaps / duty cycle** | ☠️ Characterised, with gap-block counts per reagent mode |
| **Wet/dry column pairs** | ☠️ Noticed `CH4`/`CH4d` and `CO2`/`CO2d` |
| **`gas_NOX` in ppb vs µg/m³** | ✅ **Survived** — never mentioned |
| **Same compound in two reagent modes** | ✅ **Survived** — never mentioned |

Its own generated code is kept as evidence in `prep/trial_output/trial_app.py` —
the `circular_mean` function is at line 78, and it is applied at exactly two
call sites, both wind direction.

**It also found a fault in the data that neither Georgios nor this preparation
had found:** `n_met` contradicts the met columns it describes, while the other
three counters are perfectly consistent. Verified independently. On the trimmed
file the fault is 2 + 2 rows; on the untrimmed master it was 6 + 4 — so on the
file that now ships it is a weaker signal and **may not surface**. Do not build
the segment on it; see the warning in `prompt_script.md` A3.

---

## What replaced the traps: the four judgement calls

The trial's own report documents four decisions it made without being asked.
Each is defensible, each changes the answer, and none can be automated away.
**This is the lecture** — staging in `prompt_script.md` C2.

1. **Averaged** the accumulated met variables instead of summing, so a "diurnal"
   reads as mean hourly accumulation, not a total
2. **Ignored the `n_*` sample counters** — every 30-min bin weighted equally
3. **Did not de-duplicate** the met half-hours before grouping, doubling the
   apparent sample count
4. **No per-day normalisation** — days with more valid data pull the mean harder

It got the genuinely hard one right and still left these four for a human to
ratify. That is a stronger and more honest lesson than any gotcha.

---

## Reference numbers, verified on the file that ships

`live_template/data/MONALISA_Paris_2025.csv` — **1,344 × 881**, 16 Sep – 13 Oct
2025, 20 weekday / 8 weekend days, 18.8 MB. Regenerate with
`prep/scripts/build_live_full.py`.

| | |
|---|---|
| Wind direction, whole file | arithmetic **140°** vs vector **45°** |
| Wind direction, per hour | **all 24 hours** disagree, by **53–150°**, mean **96°** |
| Worst hour (01:00) | 146° vs 356° |
| Observations near north | 36.4 % |
| `n_met` fault | 2 rows `>0` with no data; 2 rows `==0` with data |
| Met duplication | 100 % of pairs, all 8 columns |
| NOX closure | raw `NO+NO2` 18.25 vs NOX 9.95; converted **9.95 vs 9.95, r = 1.0000** |
| Acetone, two modes | 3,144 (NH₄⁺) vs 15,853 (H₃O⁺) cps, r = 0.881 |
| Toluene diurnal | weekday peak **07:00** (3,831 cps), weekend peak **19:00** (2,575) |
| Benzene vs monoterpenes | 0.860 all / 0.945 night / 0.499 midday |
| Negatives | 4,248 `NH4_`, 9,172 `H3O_`, 27 `gas_` |
| Sunshine > 30 min in a 30-min slot | 278 rows |
| First page load | **~22 s** warmed (17 s imports + 5 s CSV); **66.7 s** cold |

> ⚠️ Earlier drafts quoted figures from the untrimmed master and from a
> two-week subset. Those are superseded. Anything not in this table should be
> re-measured before it goes on a slide.

---

## What broke during preparation — still worth knowing

### 🔴 `scipy` missing would have killed the correlation panel on stage

`pandas.corr(method="spearman")` imports `scipy.stats` **lazily**, so it failed
at the moment the tab rendered, not at startup. Pinned at 1.18.1.

> And while the app was completely broken, `curl localhost:8501` still returned
> **HTTP 200**. Streamlit serves its shell regardless. **A running server is not
> a working app** — look at the page, not the port.

### 🟠 Bundled venv abandoned

Copying 381 MB of small files took **4 min 19 s** on this machine, and Pillow's
`_imaging` DLL failed to load at a long destination path. `live_template/` ships
no venv; building it from a warm `uv` cache takes **24 s**, and the 18.8 MB CSV
copies in about two seconds. One large file is nothing like 30,000 small ones.

### 🟠 Warming the bytecode cache matters more than expected

Clearing `__pycache__` inside the venv pushed the first import from **17.2 s to
66.7 s**. Warm it the night before — see `day_of_checklist.md` step 5.

### 🟠 Scope creep is the schedule risk, not failure

Independent runs wrote **416** and **1,161** lines from equivalent prompts, where
a hand build was 370. Keep the *"minimal — no extra features"* clause on every
build prompt and interrupt when it embellishes.

### 🟡 Four of my own errors, all caught by re-checking

- Logged the negative-ion trap without reading my own script output. There are
  **zero** negatives in the nine headline ion columns.
- Quoted subset correlations in a script whose data had changed to the full
  campaign.
- Quoted full-campaign figures in a script whose data had then been trimmed —
  six numbers were wrong, including the wind-direction error, which is
  **larger** on the trimmed file, not smaller.
- Renamed `prep/rehearsal_3` to `prep/sandbox` while `.gitignore` still only
  excluded `prep/rehearsal_*/`, which silently un-ignored a 19 MB data copy.
  Caught in the pre-commit audit.

**The pattern:** every one was caught by re-deriving the number rather than
trusting the previous draft. That is exactly the habit the lecture is about, so
it is worth saying out loud if the subject comes up.
