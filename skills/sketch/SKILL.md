---
name: sketch
description: Use when the person you are talking to asks for a quick figure, plot, chart or diagram to look at themselves ("make me a figure of X", "plot Y", "show me how Z works"), or tells you what to change in one you just drew. Draws in this session and sends a first image within about a minute, then changes it as they say what to cut. Not for a figure going to someone else (a mentor, a deck, a paper, a post) or for the planned figures of an experiment spec; use better-figures:figures for those.
---

# Sketch

A first image within a minute, then fast changes as the person says what to cut. The time goes almost entirely to what you write: you produce about 100 tokens a second, so every 1,000 tokens of thinking or code costs 10 seconds. Measured on earlier sessions, figures took 3 to 30 minutes, and 70 to 99% of that was thinking and writing, mostly at the planning and checking stages this tier skips. Decide quickly, write a short script, and let the person's reaction do the rest.

## Steps

1. **In one turn**, look at the data (one shell command that prints the columns or array shapes and a few rows) and read the gallery example closest to the request (below). Read only the code you need.
2. **Adapt that example.** No plan block, no caption, no figures skill, no subagent or critic, no Slurm: plotting saved data is light work and runs here.
3. **Write the script and run it in one command**, with the house style from the figures skill:
   ```
   uv run --no-project --with matplotlib,seaborn,pandas,pyarrow python sketch_<slug>.py
   ```
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_SKILL_DIR}/../figures")
   import figkit as fk
   fk.use()                       # Inter, one accent colour, greys
   ...
   fk.save(fig, out)              # prints a check; act only on overlap, clipping or tiny text
   ```
   Save the script and PNG in a `sketches/` folder in your scratch directory, as `<slug>_v1.png`; each change is `_v2`, `_v3`, never an overwrite. Diagrams: write HTML that links `${CLAUDE_SKILL_DIR}/../figures/diagram.css` and render it with `sh ${CLAUDE_SKILL_DIR}/../figures/render_html.sh in.html out.png W H` (about 7 seconds).
4. **Look at the PNG once.** Fix only what is broken: overlapping or clipped text, an empty panel, unreadable labels. Don't polish.
5. **Send it.** Use SendUserFile with the PNG if you have the tool: it reaches the person's phone and the claude.ai app in about a second, even when they work in a terminal over SSH. Also print the PNG's absolute path. Add at most two lines: what the figure shows, and the one choice they may want changed ("log scale; MLP layers left out").
6. **When they say what to change**, edit the same script, rerun, look, send. Each round should take seconds, not minutes.

## Learn from each round

Speed comes from knowing the person's taste, the way another researcher's Claude learned it over days of feedback. If the private folder below exists:
- when the person says what they dislike or like about a sketch, add one dated line in their words to its `notes.md`;
- when they say a sketch is good, copy its script and PNG into its `gallery/`, and add a row to `gallery/README.md` with the one-line request that produced it.

Read `notes.md` and `gallery/README.md` at step 1 when they exist.

Private folder: `~/figure-references/sketch/` (it holds unpublished figures; never copy from it into a public repository).

## Taste

See `taste.md` in this folder (about 350 words). Read it at step 1, in the same turn.

## Gallery

Public examples are in `${CLAUDE_SKILL_DIR}/../figures/examples/`, each a short script with its PNG. Pick by the question the figure answers:

| Request | Example |
|---|---|
| Is one condition higher than another? | `bar_comparison.py`, `bars_with_seeds.py` (every seed as a dot) |
| How do several methods rank, with intervals? | `dot_intervals.py` |
| How does a measure change over training or across layers? | `line_direct_labels.py`, `curves_with_seeds.py` |
| How does an effect grow with a dose or a size (k, steering strength)? | `steering_strength.py` |
| Is the trend a power law? | `scaling_log.py` |
| Which method gives the best trade-off? | `pareto_frontier.py` |
| How is a quantity distributed; do two groups separate? | `score_histograms.py`, `roc_probe.py` |
| How do two measures relate? | a scatter from `fk.use()`; plain axes, one colour, a few points named |
| Is a model calibrated? | `calibration.py` |
| Where in the model (layer by head)? | `head_heatmap.py` |
| How does a method or pipeline work? | `diagram.html` |
| Scores on tokens; replies side by side | `token_scores.html`, `transcripts.html` |

Private examples, when present, are listed in `~/figure-references/sketch/gallery/README.md`; prefer them, since the person chose them.
