# Architecture

A single Streamlit app, `app.py`, reading one CSV.

## Layout
- **Left (sidebar).** The list of available series. The file holds ~880, so the
  list is filtered by family and by a name search rather than shown whole.
  Up to four series can be selected at once.
- **Right, "Time series" panel.** Two plots for the selected series:
  1. the series against time, with 30-minute / hourly / daily averaging
  2. the mean diurnal cycle, split into weekday and weekend
- **Right, "Correlations" panel.** Any two series as a scatter plot coloured by
  hour of day, with Pearson r, Spearman and n.
- **Right, "Overview report" panel.** A button that writes a Word document.

## Data flow
```
CSV --> pandas DataFrame (cached)
          |
          +--> plots (matplotlib, rendered to PNG in memory)
          |
          +--> statistics per selected series
          |
notes.json <--> notes panel        (written on every save)
          |
          v
    Word overview (.docx)  =  figures + statistics + notes + provenance
```

## Notes file
`notes.json` is a dictionary keyed by series name, each holding a list of
`{timestamp, author, text}`. Written atomically on every save so that
restarting the app cannot lose anything.

## Provenance
The Word document records, automatically: the data file and its SHA-256, row
and column counts, the date range, the time base, the time zone, which
averaging was selected, how wind direction was averaged, how missing data were
handled, the tool and model, library versions, the timestamp, and the prompts
used.
