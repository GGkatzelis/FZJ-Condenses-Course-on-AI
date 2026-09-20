"""Drive the demo app the way the lecture will, using Streamlit's AppTest.

Catches real runtime exceptions that a plain HTTP probe cannot see, and times
each segment. Usage:
    python prep/scripts/rehearse_app.py <path to the build folder>
"""
import json
import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

BUILD = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
APP = BUILD / "app.py"
TIMINGS = {}


def run(label, timeout=120, **widgets):
    t0 = time.perf_counter()
    at = AppTest.from_file(str(APP), default_timeout=timeout)
    at.run()
    if at.exception:
        print(f"\n!! {label}: EXCEPTION ON FIRST RUN")
        for e in at.exception:
            print("   ", e.value)
        return at, None
    for key, val in widgets.items():
        try:
            _set(at, key, val)
        except Exception as exc:                       # noqa: BLE001
            print(f"   [{label}] could not set {key}={val!r}: {exc}")
    if widgets:
        at.run()
    dt = time.perf_counter() - t0
    TIMINGS[label] = dt
    status = "EXCEPTION" if at.exception else "ok"
    print(f"  {label:34s} {dt:6.2f} s   {status}")
    if at.exception:
        for e in at.exception:
            print("     ", e.value)
    return at, dt


def _set(at, key, val):
    for coll in (at.multiselect, at.selectbox, at.radio, at.checkbox,
                 at.text_input, at.text_area, at.button):
        try:
            w = coll(key=key)
        except (KeyError, IndexError):
            continue
        if w is None:
            continue
        if hasattr(w, "set_value"):
            w.set_value(val)
        return
    raise KeyError(key)


print(f"rehearsing {BUILD.name}\n" + "=" * 60)

print("\nSegment A — load and inspect")
at, _ = run("A: cold start, overview", timeout=180)
if at.exception:
    sys.exit(1)
print(f"    metrics on screen : {[m.value for m in at.metric]}")
print(f"    dataframes        : {len(at.dataframe)}")
print(f"    markdown blocks   : {len(at.markdown)}")

print("\nSegment B — time series and diurnals")
run("B: toluene + benzene, hourly", ts_pick=["H3O_C7H9+", "H3O_C6H7+"],
    ts_res="hourly")
run("B: daily averaging", ts_res="daily")
run("B: diurnal, median", di_pick=["H3O_C7H9+"], di_stat="median")

print("\nSegment C — correlations")
run("C: benzene vs monoterpenes", cx="H3O_C6H7+", cy="H3O_C10H17+")
run("C: eBCff vs NO", cx="gas_eBCff (microg/m3)", cy="gas_NO (microg/m3)")
run("C: isoprene vs temperature", cx="H3O_C5H9+",
    cy="met_Sheltered_Temperature (C)")

print("\nSegment D — notes persistence")
notes_file = BUILD / "notes.json"
before = notes_file.exists()
at = AppTest.from_file(str(APP), default_timeout=120)
at.run()
t0 = time.perf_counter()
try:
    at.text_area[0].set_value("Morning peak looks like traffic, evening like cooking.")
    at.text_input[0].set_value("the room")
    at.button[0].click()
    at.run()
    ok = not at.exception
except Exception as exc:                                # noqa: BLE001
    ok = False
    print("   note entry failed:", exc)
TIMINGS["D: save one note"] = time.perf_counter() - t0
print(f"  {'D: save one note':34s} {TIMINGS['D: save one note']:6.2f} s   "
      f"{'ok' if ok else 'FAILED'}")
if notes_file.exists():
    data = json.loads(notes_file.read_text(encoding="utf-8"))
    print(f"    notes.json now holds {len(data)} note(s); "
          f"existed before: {before}")
    print(f"    last: {data[-1]}")
else:
    print("    !! notes.json was NOT written")

print("\nSegment E — Word report")
at = AppTest.from_file(str(APP), default_timeout=300)
at.run()
t0 = time.perf_counter()
built = False
for b in at.button:
    if "report" in (b.label or "").lower():
        b.click()
        at.run()
        built = not at.exception
        break
TIMINGS["E: build report"] = time.perf_counter() - t0
print(f"  {'E: build report':34s} {TIMINGS['E: build report']:6.2f} s   "
      f"{'ok' if built else 'FAILED'}")
if at.exception:
    for e in at.exception:
        print("     ", e.value)
rep = BUILD / "MONALISA_report.docx"
print(f"    report exists: {rep.exists()}"
      + (f", {rep.stat().st_size / 1024:.0f} kB" if rep.exists() else ""))

print("\n" + "=" * 60)
print("TIMINGS")
for k, v in TIMINGS.items():
    print(f"  {k:34s} {v:6.2f} s")
print(f"  {'TOTAL':34s} {sum(TIMINGS.values()):6.2f} s")
