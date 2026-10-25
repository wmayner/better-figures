# Run of 25 October 2026: better-figures 0.3.0

The same test as the run of 20 October 2026 (better-figures 0.1.0), on the same three datasets (seed 20261020 gives
tasks 1 to 3 byte-identical data), with two tasks added for parts of 0.3.0:

- `task4_set`: three figures for one write-up, one script each, sharing three conditions. Measures whether each
  condition is drawn in one colour across the three figures (the colour roles in `figure-roles.json`).
- `task5_column`: the probe figure for one column of a two-column paper, 3.25 in wide. Measures the figure's width
  and its smallest text as printed (the sizes in `fk.use(size=...)`).

Claude Code 2.1.310, Opus 5.5 at effort high, two runs per task and setup, 20 drawing sessions, run four at a time.
Both setups loaded their figure skill in every run (`dataviz` for plain Claude Code, `better-figures:figures` with
the plugin). Cost: $9.24 for drawing, $0.12 for the isolation check, $0.45 for readers and judges, $9.81 in all.

## Which measures file the analysis uses

`measure.py` was corrected twice after its first pass on this run, so the folder holds three measurements. None was
overwritten. The analysis (`per_run.csv`, `table.csv`, `summary.json`) uses `measures_v3.csv`:

    python analyze.py runs/2026-10-25_seed20261020 measures_v3.csv

- `measures.csv`: the first pass. Its colour detection for `task4_set` was wrong: it read the dark grey of tick
  labels as a condition's colour, missed bars that seaborn draws one group per hue level, and missed dots drawn
  without a label. Words, titles, sizes and fonts are the same as in v3.
- `measures_v2.csv`: bars and unlabelled dots fixed, but it read black seed dots as a condition's colour, and
  figkit's own check gave a false alarm on a tick label wrapped onto two lines ("honesty data\nand steering"
  reported as a near match of "honesty data and steering"). Both were fixed in figkit 0.3.0 and `measure.py`
  before v3; tests cover the figkit fixes.
- `measures_v3.csv`: used.

## Colour consistency, checked by eye

All twelve `task4_set` figures were looked at. In each of the four runs, every condition is drawn in one colour in
all three figures: blue, orange and green in both plain Claude Code runs (the `dataviz` palette), grey, blue and
orange in both plugin runs (the roles in the run's `figure-roles.json`). This agrees with `summary.json`. The task
does not separate the two setups: one session wrote all three scripts, and both setups kept the colours.

## Results

See `summary.json` and the README's "Does it work?" section.
