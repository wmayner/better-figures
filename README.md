# better-figures

A Claude Code skill for making research figures that a busy researcher understands in five seconds. It is written for interpretability researchers who use Claude Code to run experiments and plot the results, though nothing in it is specific to interpretability.

Left to itself, Claude tends to make figures that show every result at once and put the caption's job into the image: long titles that explain instead of stating a finding, definitions, statistics and verdicts drawn above the data. Asking it to "define every term" makes the labels longer. This skill asks a different question before and after drawing: what can be removed?

![A summary figure drawn with the skill: three heads chosen by attribution patching keep the model's answer when all other heads are ablated, and three random heads do not. The result is made up.](skills/figures/examples/summary_example.png)

*A summary figure drawn with the skill's HTML parts. The result it shows is made up: three attention heads chosen by attribution patching keep the model's answer to the prompt when all other heads are ablated, and three random heads do not.*

## What it does

The plugin has two parts.

**The skill** (`skills/figures/`) loads when Claude is about to make a figure. It has Claude:

- write a short plan before drawing: the one claim the figure argues, a one-line title that states it, the plot template that makes that argument, the one comparison it shows, and every string that will appear in the image;
- put in the image only what the eye needs: the title, axis labels, series names next to the data, and values at the ends of bars, with definitions, statistics and how things were measured in the caption;
- write each caption as the takeaway in bold, then the key numbers, then what a reader needs to interpret the figure;
- draw with a matplotlib house style (`figkit.py`) that labels lines, bars and values directly, sizes figures for screens, slides, posts on X or Slack, and print, and colours each condition by its role in a `figure-roles.json` that a set of figures shares. It runs a check on save, which prints what to fix: too many words, a title that runs long or doesn't state one finding plainly, a legend that could be direct labels, small, overlapping or clipped text, a condition drawn in the wrong colour, colours that look alike to colour-blind readers, and bars out of order;
- start from a worked example of each kind of figure, grouped by the question it answers, from bars with every seed to ROC curves, heatmaps of attention heads and token scores;
- mark a figure drawn from fake data as fake, in the image;
- draw figures for web pages in HTML and SVG, with exact values in a tooltip, and render a PNG from the same file for slides;
- draw method diagrams and summary figures (the Figure 1 that opens a paper) from HTML parts: chat boxes, a model icon, thought bubbles, network cartoons, ablation marks, check and cross badges;
- draw figures made of text in HTML: a score on every token, and model replies side by side;
- draw a story figure when a result compares several methods on one task: one tall image with the data, the task, the result and how each method works, for a reader who sees nothing else;
- look at the rendered PNG once, and for figures going to a mentor or a paper, ask a fresh subagent with none of the context what the figure says.

**The workflow** ([`WORKFLOW.md`](WORKFLOW.md)) covers the part a skill can't enforce on its own: figures are designed at the spec stage, before an experiment runs. You approve each figure as its plan block, or as a mock drawn from fake data, never as a prose description of its encodings. Each figure argues one claim, a set of experiments gets at most five figures, and they are published together on one page, each with a short caption. `WORKFLOW.md` ends with a block of rules you can paste into your own `CLAUDE.md`.

## Install

As a plugin, inside Claude Code:

```
/plugin marketplace add wmayner/better-figures
/plugin install better-figures@better-figures
```

On Claude Code 2.1.275 or later, `/plugin install better-figures --marketplace wmayner/better-figures` does both in one step.

Or copy the skill into your personal skills folder:

```
git clone https://github.com/wmayner/better-figures
cp -r better-figures/skills/figures ~/.claude/skills/
```

Either way, Claude loads the skill when you ask for a figure. You can also call it directly: `/better-figures:figures` for the plugin, `/figures` for the copy.

### Requirements

- Python with matplotlib for `figkit.py`; seaborn is optional. The Inter font ships in `skills/figures/fonts/`, and the style falls back to DejaVu Sans without it.
- A headless Chromium for `render_html.sh`, which turns HTML figures and diagrams into PNGs. The script looks for Playwright's headless shell (`uvx playwright install chromium-headless-shell`, or the `npx` equivalent), then Google Chrome or chromium, or uses the path in `$CHROME`.
- A network connection for the interactive example, which loads D3 from jsDelivr and Inter from Google Fonts.

## Examples

`skills/figures/examples/` has a worked example of each kind of figure, grouped by the question it answers, each with its source, the rendered PNG, and its claim and caption in its header. All their data is made up. This table is generated from the examples' headers by `tools/gallery.py`.

<!-- examples -->
| Question | Example | What it shows |
|---|---|---|
| Is one condition higher than another? | `bar_comparison.py` | bar plot: the loss increase from ablating the top heads by activation patching against random heads, on four tasks |
|  | `bars_with_seeds.py` | bar plot with every seed as a dot: test accuracy on modular addition with weight decay, with dropout and with neither |
| How do several methods rank, and how sure are we? | `dot_intervals.py` | dot plot with intervals: how closely five attribution methods rank attention heads the way ablation does, on three models |
|  | `interactive_dots.html` | HTML figure with a tooltip: how closely four attribution methods rank heads the way ablation does |
| How does a measure change over training, or across layers? | `curves_with_seeds.py` | line plot with every seed: test accuracy on modular addition over training, with and without weight decay |
|  | `line_direct_labels.py` | line plot with names at the line ends: probe accuracy by layer, against two controls |
| How does an effect grow with a dose? | `steering_strength.py` | lines in the ordered ramp: how often steered completions mention a concept as the steering coefficient grows, for four model sizes |
| Does a trend follow a scaling law? | `scaling_log.py` | scaling plot on log-log axes: SAE reconstruction error against dictionary size |
| Which method gives the best trade-off? | `pareto_frontier.py` | Pareto plot: loss recovered against active latents per token for three SAE architectures |
| How well does a probe or monitor separate two classes? | `roc_probe.py` | ROC curves: a deception probe against a black-box baseline, with the operating point at 1% false positives |
|  | `score_histograms.py` | two histograms and a threshold: a deception probe's scores on honest and deceptive answers |
| Is one model better calibrated than another? | `calibration.py` | calibration plot: how often a model is right at each stated confidence, before and after fine-tuning |
| Where in the model is the effect? | `head_heatmap.py` | heatmap: the loss increase from ablating each of a 12-layer model's 144 attention heads |
| Where in the text does a score fire? | `token_scores.html` | token scores: a deception probe's score on each token of two reports an agent wrote |
| What did the model say? | `transcripts.html` | replies side by side: a model's reply to a false claim with and without steering against sycophancy |
| How does the method work? | `diagram.html` | method diagram: the three steps of activation patching |
| What was done and what was found, at a glance? | `summary_components.html` | each HTML part of a summary figure once, to copy from |
|  | `summary_example.html` | summary figure, shown at the top of this page: three heads chosen by attribution patching keep the model's answer when all other heads are ablated, and three random heads do not; `summary_example_check.md` records how three fresh readers read it |
| Which method does the task best, and how do the methods differ? | `story_figure.html` | story figure: which of six methods finds the circuit planted in a toy network, with the data, the task and how each method works; `story_figure_check.md` records how a fresh reader read it |
<!-- /examples -->

To re-render them, run the Python scripts with any working directory, and `sh skills/figures/render_html.sh <file>.html <file>.png <width> <height>` for the HTML files (the size of each is in a comment at its top). The tests in `tests/` check `figkit.py`, check that every Python example passes its own check, and check that this table is current: `uv run --with-requirements evals/requirements.txt --with pytest pytest tests`.

## References

The rules for summary figures come from the first figures of five papers by Owain Evans's group: Connecting the Dots, the Reversal Curse, Subliminal Learning, Emergent Misalignment, and Tell Me About Yourself. These papers are under arXiv's default license, which doesn't allow redistribution, so their images are not in this repository. Run `sh skills/figures/references/fetch-references.sh` to download the pages from arXiv for your own reference. A sixth figure, from How to Catch an AI Liar, is under CC BY 4.0 and ships in the folder. [`skills/figures/references/README.md`](skills/figures/references/README.md) lists each paper with its license and the thread on X that announced it, with notes on what each figure does well.

The plot templates the skill chooses from (bar, line, scaling law, calibration, diverging line, Pareto frontier) come from Jo Jiao's post [Research lessons I learned at MATS and Redwood](https://www.lesswrong.com/posts/Q4rcvgjbgjTwmn8Xa/research-lessons-i-learned-at-mats-and-redwood), which argues that a plot is an argument in miniature and that plots matching a known template are much easier to read.

Several parts of `figkit.py` follow [viz](https://github.com/safety-research/viz), Joshua Fonseca Rivera's chart library for AI safety research: titles that state the finding and the check on them, colour roles in one file, sizes for where a figure goes, value labels at bar ends, the mark on mock figures, sorting categories by value, examples grouped by the question they answer, and the colour-blindness check, whose code is ported from viz under its MIT license.

## Does it work?

<!-- EVIDENCE -->
### First run: version 0.1.0, 20 October 2026

We ran a small test on 20 October 2026. Claude Code (Opus 5.5, effort high, headless) got the same made-up dataset and the same one-line request in two setups. Plain Claude Code had no CLAUDE.md, user skills, plugins, hooks or MCP servers; it still had Claude Code's built-in skills, and it loaded the built-in `dataviz` skill in every run. The other setup was identical except for `--plugin-dir` pointing at this repository, and it loaded the figures skill in every run. Each run started in an empty directory holding only `data.csv`.

There were three tasks, each with a planted answer: probe accuracy by layer for four concepts that become decodable at different depths ("Make a figure showing where each concept becomes decodable"), the loss increase from ablating each of 144 heads where three heads matter, and five attribution methods compared with ablation on three models where one method is clearly best. Each setup ran each task twice, for 12 runs.

We measured two things. The first is the number of words in the image other than tick labels (axis labels, titles, legends, annotations), counted from the matplotlib text objects. The second is a fresh-reader check: a new session saw only the PNG and wrote one sentence on what it shows, and a separate session compared that sentence with the planted answer and said whether they match (yes, partly or no) without knowing which setup drew the figure.

![Dot plot of words in each figure, by task: plain Claude Code's runs have 25 to 43 words, runs with better-figures have 7 to 12.](evals/results/figure_words.png)

*Each dot is one run of Claude Code (Opus 5.5) given the same data and request; grey runs were plain Claude Code, orange runs had better-figures installed. Words exclude tick labels; 2 runs per setup per task. Fresh-reader agreement is in the table below.*

| Task | Mean words: plain / with plugin | Fresh reader matched: plain / with plugin | Cost per run (USD): plain / with plugin |
|---|---|---|---|
| Probe accuracy by layer | 41 / 12 | 2 of 2 / 2 of 2 | 0.55 / 0.71 |
| Effect of ablating heads | 41 / 8.5 | 2 of 2 / 2 of 2 | 0.50 / 0.38 |
| Attribution against ablation | 27.5 / 10 | 2 of 2 / 1 of 2, 1 partly | 0.33 / 0.28 |

With the plugin, figures carried 2.8 to 4.8 times fewer words depending on the task (geometric mean 3.6), and every plugin run used fewer words than every plain run. With only three tasks the statistical evidence is moderate: a Bayes factor of 4.9 for the per-task log ratio of mean words differing from zero (one-sample JZS test, Cauchy prior with scale 0.707), and 6.0 with scale 1.0. Fresh readers got the planted answer from nearly every figure in both setups (6 of 6 without the plugin, 5 of 6 and one partial match with it), so the test shows that the plugin's figures carry less text, not that readers understand them better. Word count is the measure because less text in the image is what the skill aims for. The one partial match was a plugin figure whose reader gave the ranking of methods without saying how far ahead the best one was. Cost per run was the same on average ($0.46 in both setups; this is the API-equivalent cost Claude Code reports). These are 12 runs on made-up data with one model, so treat them as a first check, not a benchmark.

The first run of each setup on the attribution task:

![Two figures side by side. Left, plain Claude Code: five methods with a coloured dot and interval per model, a legend, a shaded best row and a column of mean values. Right, with better-figures: the same intervals in grey with integrated gradients in orange and the three model names written next to its dots.](evals/results/before_after_task3.png)

### Second run: version 0.3.0, 25 October 2026

Version 0.3.0 allows a one-line title that states the finding, and values and counts at the ends of bars, so its figures were expected to carry more words than those of 0.1.0. We reran the three tasks on the same data, two runs per setup, with Claude Code 2.1.310, and added two tasks for parts of 0.3.0. Both setups again loaded their figure skill in every run.

| Task | Words outside tick labels: plain / with plugin | Words outside the title, tick labels and numbers: plain / with plugin | Fresh reader matched: plain / with plugin |
|---|---|---|---|
| Probe accuracy by layer | 41 / 30 | 29.5 / 14 | 2 of 2 / 2 of 2 |
| Effect of ablating heads | 44.5 / 20.5 | 29 / 4.5 | 2 of 2 / 2 of 2 |
| Attribution against ablation | 35.5 / 19 | 14 / 6 | 2 of 2 / 2 of 2 |

- Counting every word outside tick labels, as on 20 October, the plugin's figures carried 1.4 to 2.2 times fewer words (geometric mean 1.8, down from 3.6), and the evidence for a difference is weak: a Bayes factor of 2.5 (Cauchy prior with scale 0.707; 2.7 with scale 1.0). Most of the change from 0.1.0 is the titles. Every plugin figure had one, 11 words long on average, stating the finding with its numbers ("Only 3 of 144 heads raised loss by over 0.1 nats"). Plain Claude Code titled 4 of its 6 figures, with 5.5 words on average, mostly naming the topic ("Concepts become linearly decodable at different depths").
- Leaving out the title and the numbers, which 0.3.0 allows, the plugin's figures carried 2.1 to 6.4 times fewer words (geometric mean 3.2). The Bayes factor is 1.9 with either prior, because the ratio varies too much across three tasks for strong evidence.
- Every fresh reader got the planted answer from both setups (6 of 6 each), so this test again shows a difference in text, not in understanding.
- Three figures for one write-up, one script each: in all four runs, each condition kept one colour across the three figures, in both setups. Plain Claude Code used the `dataviz` skill's palette the same way in each script, so this task showed no advantage for the colour roles. It does not test the case they are for, where separate sessions draw the figures.
- One column of a paper, 3.25 in wide: both setups drew the figure at that width. Plain Claude Code's smallest text was 6 pt in both runs. The plugin used `fk.use(size="column")` both times, and its smallest text was 7 pt, the least figkit allows for print.
- Cost per run on the three original tasks was $0.39 for plain Claude Code and $0.46 with the plugin; the whole run cost $9.81.

These are two runs per setup on made-up data with one model, so treat them as a check that 0.3.0 does what it says, not as a benchmark.

### Rerunning the test

From `evals/`: `python make_data.py --seed 20261020 --out runs/<new name>`, then `python run.py isolation`, `run.py draw`, `measure.py`, `run.py read` and `analyze.py` on that folder (the usage block at the top of `evals/run.py` lists them in order; `evals/requirements.txt` has the Python packages). Each run's script, figure, caption, cost and token counts are in its folder under `evals/runs/`, with the paths of the machine it ran on replaced by `<repository>` and `<work_root>`; `evals/runs/2026-10-25_seed20261020/NOTES.md` says which of that run's measurements the analysis uses and why. The full session transcripts are not in the repository: `run.py` writes them to a `transcripts/` folder in the run folder, which git ignores.
<!-- /EVIDENCE -->

## License

MIT, copyright 2026 Will Mayner; see [`LICENSE`](LICENSE). The Inter font is under the SIL Open Font License 1.1 (`skills/figures/fonts/Inter-LICENSE.txt`). The figure from How to Catch an AI Liar is under CC BY 4.0 by its authors.
