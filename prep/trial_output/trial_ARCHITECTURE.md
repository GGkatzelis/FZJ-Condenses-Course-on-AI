# ARCHITECTURE — MONALISA series browser

A single-file Streamlit app (`app.py`) for browsing `data/MONALISA_Paris_2025.csv`
(2927 rows x 881 columns, 30-min grid, 2025-09-01 00:00 to 2025-10-31 23:00).
Read-only with respect to the CSV. Runs fully offline.

## Data layer

`load_data()` (`@st.cache_data`) reads the CSV once, parses `time` and sets it as
the index. Timestamps are **naive** — the file carries no time-zone information,
so the app displays "time zone as given in file (not stated)" next to every
time axis and repeats it in the Word report.

`series_catalogue()` derives, per column:
- **group** from the name prefix: `NH4_` (427 PTR ions), `H3O_` (430 PTR ions),
  `gas_` (11 trace gases), `met_` (8 meteorology), `n_` (4 sample counters).
- **unit** from a trailing `(...)` in the name. `NH4_`/`H3O_` columns have no
  unit in the file, so their axes are labelled "unit not stated in file".
- coverage (non-null count / %) and first/last valid timestamp.

## Aggregation rules (single `resample_series()` used by every plot)

- default: arithmetic mean of the non-null values in each bin.
- `met_Wind_Direction (degrees)`: **circular (vector) mean** —
  `atan2(mean sin, mean cos)` wrapped to (0, 360]. An arithmetic mean of a
  compass bearing is wrong (350 deg and 10 deg average to 180, not 0).
- `n_*` columns: **summed**, because they are counts of raw samples per bin, not
  a measured quantity.
- `met_Precipitation (mm)`, `met_Sunshine_Duration (min)`,
  `met_Global_Radiation (J/cm2)` are hourly accumulations that the file repeats
  on both half-hour slots; they are averaged (giving "per hour" values) and
  labelled as such rather than summed, which would double-count.

## UI

Left sidebar: group multiselect + free-text substring filter over the ~880
column names, then a multiselect of the matching series capped at 4 picks.

Main area, three tabs:
1. **Time series & diurnal** — line plot at raw 30-min / hourly / daily
   resolution (radio), and the mean diurnal cycle of the same series with
   weekdays (Mon-Fri) and weekends drawn as separate traces. Hour of day is
   taken straight from the timestamp as stored.
2. **Scatter** — any two series, plotted against each other on the common
   30-min timestamps, with Pearson r and n shown.
3. **Notes** — free-text note + author for the currently selected series,
   written to `notes.json` immediately on save (write to temp file, then
   `os.replace`, so an interrupted save cannot lose earlier notes). Layout:
   `{"<series>": [{"author", "timestamp", "text"}, ...]}`. Notes for the
   selected series are listed under the plots.

## Report

"Export Word report" builds a `.docx` with `python-docx`: one section per series
that has notes, each with its notes, basic statistics (n, mean, median, std,
min, max, coverage %, first/last timestamp) and the currently configured time
series and diurnal figures (matplotlib -> PNG in memory), plus a provenance
section: source file path, row count, period covered, the resolution actually
used, the aggregation rules above, and the time-zone caveat.

## Non-goals

No cleaning, gap-filling, outlier removal, unit conversion or calibration. No
network access. No writes other than `notes.json` and the generated `.docx`.
