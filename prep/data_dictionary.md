# MONALISA — Paris, autumn 2025

Measurement data from the MONALISA field campaign at an urban ground site in
Paris (48.85 °N, 2.35 °E), autumn 2025.

**These data are unpublished. Do not upload them to any external service.**

## The file

`data/MONALISA_Paris_2025.csv` — 672 rows on a 30-minute time base,
22 September to 5 October 2025.

The `time` column holds the timestamp of each 30-minute interval.
Missing values are empty cells.

> Column names carry their units in the name, e.g. `gas_NO (microg/m3)`.
> Match on the prefix rather than the full string.

## Instruments and columns

### VOCs — PTR-ToF-MS, H₃O⁺ reagent ion (`H3O_` prefix)

Proton-transfer-reaction time-of-flight mass spectrometer. Each column is one
detected ion, named by its chemical formula.

| Column | Usually attributed to |
|---|---|
| `H3O_C6H7+` | benzene |
| `H3O_C7H9+` | toluene |
| `H3O_C8H11+` | C8 aromatics (xylenes, ethylbenzene) |
| `H3O_C10H31O5Si5+` | D5, decamethylcyclopentasiloxane |
| `H3O_C5H9+` | isoprene |
| `H3O_C10H17+` | monoterpenes |
| `H3O_C9H19O+` | nonanal |
| `H3O_C3H7O+` | acetone |
| `H3O_C2H5O+` | acetaldehyde |

**Units: raw counts per second (cps).** These are instrument signal, not
calibrated mixing ratios — they are not comparable between different ions, and
they carry no unit conversion to ppb or µg/m³.

**Negative values can occur in PTR data generally.** They are a normal
consequence of background subtraction: when a signal sits at or below the
instrument background, the subtracted value can fall slightly below zero, and
such values are real data rather than errors. The nine ions selected here are
all well above background, so in practice none of them goes negative in this
file. `gas_O3` does carry a few slightly negative night-time values, for the
same reason.

### Trace gases and aerosol (`gas_` prefix)

| Column | Quantity | Unit |
|---|---|---|
| `gas_NO (microg/m3)` | nitrogen monoxide | µg/m³ |
| `gas_NO2 (microg/m3)` | nitrogen dioxide | µg/m³ |
| `gas_O3 (microg/m3)` | ozone | µg/m³ |
| `gas_CO (mg/m3)` | carbon monoxide | **mg/m³** |
| `gas_eBCff (microg/m3)` | equivalent black carbon, fossil-fuel fraction | µg/m³ |
| `gas_eBCwb (microg/m3)` | equivalent black carbon, wood-burning fraction | µg/m³ |

**Units are mixed.** NO, NO₂ and O₃ are in µg/m³ but CO is in **mg/m³** — a
factor of 1000 apart. Do not combine or compare these columns without
converting first.

**`eBCff` and `eBCwb` are aerosol, not gases**, despite the `gas_` prefix. They
come from a multi-wavelength absorption instrument and are the black carbon mass
attributed to fossil-fuel combustion and to wood burning respectively.

### Meteorology (`met_` prefix)

From a weather station at the site.

| Column | Quantity | Unit |
|---|---|---|
| `met_Sheltered_Temperature (C)` | air temperature | °C |
| `met_Relative_Humidity (%)` | relative humidity | % |
| `met_Wind_Speed (m/s)` | wind speed | m/s |
| `met_Wind_Direction (degrees)` | wind direction, meteorological convention | degrees |
| `met_Global_Radiation (J/cm2)` | global solar radiation | J/cm² |
| `met_Precipitation (mm)` | precipitation | mm |

## Environment

A virtual environment is in `.venv`. Use `.venv\Scripts\python.exe` to run
anything. Installed: pandas, numpy, matplotlib, plotly, streamlit, python-docx —
see `requirements.txt` for pinned versions.

Work offline. Everything needed is already installed.
