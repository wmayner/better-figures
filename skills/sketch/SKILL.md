---
name: sketch
description: Use when the person you are talking to asks for a quick figure, plot, chart or diagram to look at themselves ("make me a figure of X", "plot Y", "show me how Z works"), or tells you what to change in one you just drew. Draws in this session and sends a first image within about a minute, then changes it as they say what to cut. Not for a figure going to someone else (a mentor, a deck, a paper, a post) or for the planned figures of an experiment spec; use better-figures:figures for those.
---

# Sketch

A first image within a minute, then fast changes as the person says what to cut. The time goes almost entirely to what you write: you produce about 100 tokens a second, so every 1,000 tokens of thinking or code costs 10 seconds. Measured on earlier sessions, figures took 3 to 30 minutes, and 70 to 99% of that was thinking and writing, mostly at the planning and checking stages this tier skips. Decide quickly, write a short script, and let the person's reaction do the rest.

## Steps

1. **In one turn**, look at the data (one shell command that prints the columns or array shapes and a few rows) and read the gallery example closest to the request (below). Read only the code you need. Keep the Taste section below in mind; it is what the person will judge.
2. **Adapt that example.** No plan block, no caption, no figures skill, no subagent or critic. Plotting a saved table is light work and runs here.
   **If the data needs heavy processing** (hundreds of files, gigabytes, minutes of compute), don't queue a batch job for a sketch: on a shared cluster the queue alone can take ten minutes. Draw the sketch from a subsample that runs here in seconds (say 30 of 1,370 files), say so in your reply, and offer the full run as a batch job once the person likes the figure.
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
   Save the script and PNG together in a `sketches/` folder in your scratch directory (not in the repository), as `<slug>_v1.png`; each change is `_v2`, `_v3`, never an overwrite. Diagrams: write HTML that links `${CLAUDE_SKILL_DIR}/../figures/diagram.css` and render it with `sh ${CLAUDE_SKILL_DIR}/../figures/render_html.sh in.html out.png W H` (about 7 seconds).
4. **Look at the PNG once.** Fix only what is broken: overlapping or clipped text, an empty panel, unreadable labels, and any code name left in the image (a column value like `oasst1_es` or `rand0` becomes plain words such as "OpenAssistant, Spanish" or "random nodes"; if you can't tell what one means, keep it and say so in your reply). Don't polish.
5. **Send it.** Use SendUserFile with the PNG if you have the tool: it reaches the person's phone and the claude.ai app in about a second, even when they work in a terminal over SSH. Also print the PNG's absolute path. Add at most two lines: what the figure shows, and the one choice they may want changed ("log scale; MLP layers left out").
6. **When they say what to change**, edit the same script, rerun, look, send. Each round should take seconds, not minutes.

## Learn from each round

Speed comes from knowing the person's taste, the way another researcher's Claude learned it over days of feedback. If the private folder below exists:
- when the person says what they dislike or like about a sketch, add one dated line in their words to its `notes.md`;
- when they say a sketch is good, copy its script and PNG into its `gallery/`, and add a row to `gallery/README.md` with the one-line request that produced it.

Read `notes.md` and `gallery/README.md` at step 1 when they exist.

Private folder: `~/figure-references/sketch/` (it holds unpublished figures; never copy from it into a public repository).

## Taste

What this plugin's author has asked for, again and again, distilled from his comments on figures (October and November 2026). Quotes are his words.

**One idea, the crucial comparison.** "very simple and clear, showing the crucial comparison." Draw the one comparison the request is about. Leave the rest out, or offer it in one line of your reply. A figure that shows every result is a table drawn as a plot.

**Less text than you think.** His most frequent note is "there is still too much text"; AI figures are "polluted by a lot of verbiage and context that hasn't been defined." In the image: axis labels of a few plain words with units, series names, and tick labels. No definitions, statistics, method notes, hedges or annotation boxes. If a term needs defining, use a plainer term or say it in your reply.

**Labels a newcomer can read.** "short, clear text labels, that don't require a lot of familiarity with the setup." No variable names, column names or code names for conditions ("fisher estimates", `rand0`, `neurons_heads`); write what was measured in plain words.

**Proper charts.** "a proper figure": a standard template (bars, lines, scatter, histogram, heatmap) that a reader decodes at once. Grouped bars may carry a legend. No numbers on top of bars unless the number is the point.

**Show the spread honestly.** Draw every seed or run, faint behind the mean, or as range lines when there are many. Controls and random baselines go in grey beside the result, on the same axis.

**Titles: one plain line or none.** A title states the finding literally in about ten words. He has called a title on another researcher's figure "ridiculous"; when unsure, leave the title off.

**Diagrams: show what actually flows.** The diagram he called "a good figure" (another researcher's, of an oracle's inputs) runs left to right from the model's forward pass, gives each input kind one colour kept throughout, shows the real shapes and a concrete example of what lands in the prompt, and uses short pill labels instead of sentences. Method figures that show the method and the result together, with cartoons and almost no text, are what he wants for explainers; their point is "to help the reader understand what is being done."

**Style.** Inter, one accent colour for the thing the figure is about, greys for context, white background, big readable text, plenty of space. Screen proportions, about 7 by 4 inches; very wide figures were a complaint. Log axes with plain ticks (1, 10, 100) when values span orders of magnitude.

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
