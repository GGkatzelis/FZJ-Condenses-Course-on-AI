# Rehearsal 2 — independent run, and what it means for the demo

**Method.** A genuinely independent session was given a fresh copy of
`live_template/` and **only the verbatim prompts** — no trap explanations, no
prompt script, no access to `prep/`. It was told to work only inside
`prep/rehearsal_2/`. ~20 tool calls, about 10 minutes wall clock.

This is the only way to measure what actually happens on Thursday, rather than
what I can make happen when I already know the answers.

---

## 🔴 The headline: it caught both flagship traps unprompted

### The met duplication — caught before it was asked

It reported **26.7 mm** of rain and **9.76 MJ/m²/day**. Both correct. It never
produced the doubled numbers at all.

It found the duplication *while profiling the columns*, from the raw values
(`33.4, 33.4, 92.7, 92.7, …`), then verified that the `:00` and `:30` values are
identical in **100 % of all 336 hours**, and de-duplicated before summing.

Worse (for the demo), it then ran **its own independent physics check**: it noted
that top-of-atmosphere insolation at 48.85 °N at this date is ~20–24 MJ/m²/day,
so the naive ~31 MJ/m²/day daily maximum would be impossible at the surface,
while the corrected 15.5 MJ/m² maximum sits just under the clear-sky ceiling.
**That is the exact argument scripted for you to make in prompt B4.**

### The time zone — caught and flagged prominently, unprompted

It reported the timestamps as timezone-naive with **no zone declared anywhere**,
and surfaced that in five places: the Overview tab, the Diurnal caption, every
hour-axis label (`"file-local, tz unknown"`), the scatter colourbar, and a
dedicated provenance row. It noted that a Paris site would be on CEST (UTC+2)
but stated explicitly that this was an assumption, **applied no conversion**, and
warned that no solar-noon argument should be read off the hour axis.

### And everything else, also unprompted

- Mixed gas units — CO in mg/m³ against µg/m³, factor 1000
- `gas_eBCff` / `gas_eBCwb` are aerosol, not gases, despite the prefix
- VOCs are uncalibrated cps: not inter-comparable, no ppb conversion
- Radiation and precipitation are hourly **accumulations**, not rates, so
  averaging them is not a dose
- The 11 % VOC gap is **not random** — isolated 30-min intervals recurring about
  every 3.5 h, i.e. an instrument duty cycle
- Met columns hold 336 independent values across 672 rows, so **n overstates the
  degrees of freedom by 2×**; it declined to quote p-values on autocorrelated
  series
- It refused to use dual-axis charts for differing units, using stacked panels
  sharing a time axis instead
- **It caught my documentation error** — `CLAUDE.md` promised negative ion
  values that do not exist in this file (see Trap 5 in `trap_log.md`)

### The science question, answered correctly

On benzene vs monoterpenes it concluded **not the same source**, for the right
reason — correlation stronger at night (0.838) than midday (0.612), both
anti-correlating with wind speed most strongly at night, i.e. shared
boundary-layer dilution rather than shared emission. It went further than the
script: partial correlation controlling for CO drops r from 0.77 to **0.46**;
monoterpenes show **zero** temperature dependence (r = −0.02), ruling out a
biogenic signal; they track D5 siloxane at +0.76. It closed by saying a
defensible answer needs PMF and wind-direction sectoring, not a pairwise r.

---

## What this means for Thursday

**The premise "watch the AI get it wrong" does not survive contact with
Claude Opus 5 on this dataset.** You should assume the live session will catch
the duplication, flag the time zone, and volunteer the unit problems — probably
within segment A.

Planning for it to fail is the risky bet. Planning for it to succeed is safe,
because *the lesson still works, and is arguably stronger*:

> It got all of this right. **You only know that because you checked.** Every
> check that confirmed it — solar geometry, the insolation ceiling, the
> boundary-layer argument — required knowing atmospheric science. The tool did
> not remove the need for expertise; it moved it from *doing the analysis* to
> *auditing the analysis*. And auditing is the harder skill, because a
> confident, correct-looking answer and a confident, wrong answer are
> indistinguishable until you do the work.

### Three concrete ways to run it

1. **Reframe to "audit the AI" (recommended).** Keep every prompt. When it
   catches something, stop and ask the room: *"It says the met data are
   duplicated. How would you check whether that's true?"* Then check it live.
   The audience does the verification, not the AI. This needs no new material
   and the slides still fit.

2. **Keep the traps but move the reveal earlier.** Ask the room the ⛔ questions
   from segment A2 *before* running anything, take bets, then let the AI answer.
   The tension becomes "did you spot it too?" rather than "will it fail?".
   Slides 7/8/9 still carry genuine failures, because those are *your* analysis
   of real defaults, not live AI output.

3. **Force a failure honestly, and label it.** Slide 7's `fillna(0)` case is a
   real, reproducible failure on this data (toluene's peak hour becomes `3`).
   Run it live as *"here is code I wrote that runs clean and is wrong"* — never
   as something the AI produced. Do not fake an AI mistake; this audience will
   smell it, and it would undercut the whole lecture.

**Do not** make the data harder to get right in order to rescue the trap. The
prep rules forbid altering the original, and a manufactured failure teaches the
wrong lesson.

---

## Run-to-run variation, which is what you asked to measure

| | Rehearsal 1 | Rehearsal 2 |
|---|---|---|
| Tabs | 6 | **7** (added a "Rain & radiation" tab) |
| `app.py` | ~370 lines | **1161 lines** |
| Notes persistence | plain `write_text` | atomic temp-file + `fsync` + `os.replace` |
| Differing units on one chart | shared axis, joined unit label | **refused**; stacked panels |
| Provenance rows | 14 | **18** |
| Extras | Pearson/Spearman divergence warning | partial correlations, log-x toggle, night/day segmenting |
| AppTest | clean | clean |

**The numbers were identical; the software was not.** Both runs got r = 0.771 /
0.838 / 0.612 and the same rainfall and radiation figures — the *analysis* is
reproducible. But one run produced **three times** the code of the other and
organised it differently, and only one added a tab that was never asked for.

**Implications for a 32-minute live budget:**

- **Scope creep is the real schedule risk, not failure.** A run that writes 1161
  lines will not fit. Say *"keep it minimal"* in the prompts, and be ready to
  interrupt.
- **Do not promise the audience a specific layout.** Say "a tab for X", never
  "it will look like this".
- The checkpoint branches matter more than expected — not as a crash fallback
  but as a **time** fallback, when the build is working fine and simply too slow.

---

## Verified

`prep/rehearsal_2/app.py`, 7 tabs, AppTest clean after every prompt. Widgets
driven end to end; a note was saved and confirmed on disk; the `.docx` verified
with 3 captioned figures, a 22×7 statistics table, an 18-row provenance table
and all 5 prompts. Test artifacts were removed so the build starts clean. The
CSV was never written to.
