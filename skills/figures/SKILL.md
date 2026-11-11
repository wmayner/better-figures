---
name: figures
description: Use before making a figure that is planned or that goes to someone other than the person you are talking to: the figures of an experiment spec (designed and approved before anything runs), and figures for a mentor, collaborators, a deck, a report, a paper or a post (with a fresh critic, and the summary or story figure). Covers what to show, titles and captions, a house style with a check on save, colour roles, print sizes, worked examples, and HTML for figures on a page, diagrams, summary, story and text figures. For a quick figure the person you are talking to will look at now, use better-figures:sketch instead. Not for dashboards (use dataviz).
---

# Figures

The goal is a figure that a busy researcher understands in five seconds, made in one pass.

**Which tier.** Three kinds of request use this plugin:
- *A quick look for the person you are talking to* ("make me a figure of X", "plot Y"): use `better-figures:sketch`, which draws in under a minute without the steps below.
- *The figures of an experiment*, designed at the spec stage: sections 1 to 5 here, with the plan block approved before anything runs (`WORKFLOW.md`).
- *Figures for someone else*: a mentor, collaborators, a deck, a report, a paper or a post: sections 1 to 6, including the fresh critic, and the summary or story figure guides when the figure opens or carries a piece.

The files named below (`figkit.py`, `render_html.sh`, the CSS and JS, `guides/`, `examples/`, `references/`) are in this skill's directory, `${CLAUDE_SKILL_DIR}`.

**On first use in a project, copy the kit into the project.** `${CLAUDE_SKILL_DIR}` can be a folder in Claude Code's plugin cache whose name includes the plugin's version, so a script or page that points there breaks when the plugin updates, and on a collaborator's machine. Copy `figkit.py`, `fonts/` and the CSS and JS once, into a `_kit/` folder beside the figure scripts, and refer to that copy by a path relative to each script or HTML file. If the project already has a `_kit/` folder, use it. The colour roles go in a `figure-roles.json` beside the scripts (section 4).

```
mkdir -p figures/_kit
for f in figkit.py fonts diagram.css summary.css summary.js story.css story.js text.css text.js; do cp -R "${CLAUDE_SKILL_DIR}/$f" figures/_kit/; done
```

`render_html.sh` is a command rather than something a script saves, so run it from `${CLAUDE_SKILL_DIR}`.

Figures go wrong in two ways: they show every result, so the figure becomes a table drawn as a plot, and they put the caption's job into the image (definitions, statistics, hedges, annotation boxes). A title is welcome when it states the finding in one plain line (section 3). Reviewing a figure by asking "is every term defined?" makes labels longer; ask "what can I remove?"

## 1. Decide before drawing

Write this block in your notes, or in the spec when figures are designed there. It takes two minutes and replaces most revision rounds.

```
Claim:    the one sentence the figure argues
Title:    the claim as one line of about 10 words, stating what was compared and what happened (section 3), or none
Template: bar | line | scaling | calibration | diverging line | Pareto | scatter | heatmap
Shows:    the one comparison the claim needs (which series, which subset); the rest goes to a table
Control:  the comparison that tests the most obvious other explanation, drawn in grey on the same axis; or none, and why
Spread:   how the image shows uncertainty: every seed or unit (few), an interval over the unit sampled independently (many), each unit's difference (shared units)
Accent:   the one element the eye should land on (ACCENT colour; everything else grey)
Size:     screen | slide | paper | column | post (section 4)
Text:     every string that will appear in the image, listed, at most about 25 words outside the title, tick labels and numbers
Caption:  bold takeaway sentence; 0-3 sentences of detail on the finding; then what is plotted, how measured, n and its unit, error bars (section 3a)
Alt:      for a figure on a web page: the title, then the data in words, for screen readers
Sketch:   a 4-line ASCII sketch
```

Write the claim first, then choose the template that makes that argument. Each of six common templates usually makes one claim:
- bar plot: this one is higher than this one;
- line plot: the numbers go up or down;
- scaling law plot: the trend is linear in log or logit space;
- calibration plot: model A is much better calibrated than model B;
- diverging line plot: this line goes up, this one doesn't;
- Pareto frontier plot: we push the Pareto frontier.

Scatter plots and heatmaps cover a relation between two measures and a grid of values. If no template fits, the figure is probably trying to say more than one thing; split it or simplify it. Section 4 lists a worked example of each, by the question the figure answers.

At the spec stage, the person approves this block, not a prose description of encodings ("rows: methods × targets; filled vs open markers; verdict in the margin" reads as simple and draws as a wall). Better still, draw the figure once from fake data and show the image.

## 2. Choose what to show

- One panel by default. Use small multiples (at most 4 panels, shared axes) only when the same comparison repeats across conditions.
- At most 4 series per panel. Keep the ones the claim needs; grey or drop the rest.
- If you want a verdict column, a statistic printed on every row, "two versions", or a panel per target, you are drawing a table. Put the table on the page and draw the one row that matters.
- **Draw the uncertainty in the image; don't leave it to the caption**, which doesn't travel with an image that is passed around. With few seeds or units (under about 10), draw every one: a dot per seed on its bar, or each seed as a faint line behind the bold mean. With many, draw an interval over the unit that was sampled independently (the model, not its questions): `fk.interval(values, groups=unit_of_each_row)` computes it and `fk.intervals(ax, positions, estimates)` draws it. A plotting library's default error bars resample rows, which is far too narrow when rows share a unit. Never show one run when there are more, or a bare mean.
- **When conditions share units** (the same models, seeds or prompts under each condition), compare each unit with itself: join each unit's two points (`fk.paired`), or draw each unit's difference with the mean's interval against a line at zero (`fk.differences`). Two bars with separate intervals hide a small consistent difference and can suggest one that isn't there.
- **A null is drawn, not dropped**: the planned figure, on the planned axes, where the interval of the difference crosses zero. A narrow interval around zero is a null and a wide one is inconclusive; the image shows which.
- **When the control is a set of matched random draws, draw every draw on the effect's own axis**: each unit's effect as a bar, with one grey tick per random draw in the same row (`fk.random_draws(ax, values, at=row)`), or the draws' range as a grey band. The reader sees whether the effect lies outside the draws, which a bar for their mean hides.
- **Show an intervention's size and where it acts**: mark the steering value on a histogram of the unit's usual activations, and draw the model's layers as a strip of cells with the intervened layers coloured.
- A single before-and-after is drawn like any comparison, with its seeds or its interval (`fk.paired` when the units are shared). Two large numbers with an arrow are for counts only, each with its denominator ("100 of 400 → 128 of 400"), with the control's beside them.
- Put categories in order of their values, unless their order means something (layers, model sizes, training steps). The check warns about bars out of order.
- Diagnostics and secondary results do not go in the figures someone is asked to read.

## 3. Text in the image

| Content | In the image? | Where instead |
|---|---|---|
| The finding | Yes, as the title: one line of about 10 words, stated literally (below) | and as the caption's bold first sentence |
| Definitions, interval method, thresholds, priors, Bayes factors, sampling notes | No (except short definitions in an image posted on its own, below) | caption or page text |
| Axis labels | Yes, at most about 6 words, with units | |
| Series names | Yes, next to the data (`fk.label_lines`, `fk.label_bars`) | a legend only for 5+ categories, and then you have too many |
| Values and counts | Yes: each bar's value at its end (`fk.label_values`), a count beside it ("164 of 400"), or the one key number next to its mark | |
| Panel names | Yes, at most 4 words, or a line stating that panel's finding (below) | |

**The title.** Readers look at a figure's title first and remember it better than the chart ([Borkin et al. 2016](https://vcg.seas.harvard.edu/publications/20150101-beyond-memorability-visualization-recognition-and-recall)), and they remember the title's message even when the chart contradicts it ([Kong et al. 2019](https://doi.org/10.1145/3290605.3300576)). So a title says exactly what the data shows, and nothing the data doesn't.
- One finding, stated literally: what was compared and what happened, in about 10 plain words, on one line at the figure's size. Draw it with `fk.title(fig, ...)`. If it needs a semicolon, make two figures.
- It names what the eye sees first: the accented series, or the biggest gap. If the point is a small difference, change the chart, not the words: draw the difference itself with its interval (section 2), which shows whether it is there.
- Compute its numbers from the data in the script, as the examples do, so the title can't drift from the figure.
- **It states a difference only when the drawn interval of that difference excludes zero.** Pass the difference to the title, `fk.title(fig, text, claims=fk.difference(a, b, paired=True))`, and the check refuses the title otherwise. When the interval includes zero, the title says the two did not clearly differ. The rule cuts both ways: a difference the interval supports is stated plainly, with no hedge.
- No colon setups ("The fix: search"), questions, dash asides, full stops, metaphors or wordplay.
- If the result is mixed, the title says so. If no sentence is true of the whole figure, the figure has no title.

`fk.save` checks a title's length, that it fits on one line, its punctuation and its intensifiers. It also checks that an image whose title compares conditions draws their spread, and that a difference passed as `claims` has an interval that excludes zero. Beyond that it can't tell whether the title is true.

Three rules for every word in the image and the caption, title included: say what was measured, not what it means ("chose to stop", not "wanted to stop"; "passed 98% test accuracy", not "generalized"); use numbers, not adjectives ("fell from 41% to 12%", not "dropped sharply"); and use no names coined inside the project, such as a code name for a condition or a nickname for a measure.

**Panel titles may state the panel's finding**, like the figure title, and may start with the model's name: "Qwen3-8B: zeroing 6 neurons lowers caving to pushback from 44% to 0%". A model name before the colon is not the colon setup forbidden above. Pass `panel_title_words=14` to `fk.save`. The figure still argues one idea: panels that make several unrelated claims are several figures.

**An image posted on its own** (on X or in Slack, where no caption travels with it) may define its terms in the image, briefly: one grey line of at most about 12 words under a bold label ("Layer targeting" over "the concept only at the layer asked for"), zero named in words ("0 = unsteered"), and both ends of an axis named in words. Raise `words=` for that figure. Statistics as text (p-values, n, how intervals were computed) still stay out of the image and go in the post's text; the uncertainty itself is in the image as marks (the seeds, the interval), so it travels with it.

There are no annotation boxes, no paragraphs, no rotated tick labels, no variable names from the code, and no numbers to four decimals. Rigor belongs in the caption. The image carries only what the eye needs.

## 3a. Write the caption

A caption has three parts, in this order:
1. **The takeaway, in bold:** one declarative sentence stating what the figure shows. It is the Claim from the plan block, and it can repeat the title with more precision. Never open with "How to read it", "This figure shows" or a description of the axes.
2. **Zero to three sentences on the finding:** the key numbers with their intervals, and the qualification a reader most needs.
3. **What a reader needs to interpret it correctly:** what each line, bar or band is; how it was measured; n; what the error bars are and which unit they resample (an estimate's `.caption()` gives the words: "95% bootstrap interval over 20 models"); any reference line; anything excluded. An example shown in the figure says how it was chosen: at random, as typical, or as the clearest case, with the share of cases like it.

Each sentence has only a few clauses: no semicolon chains and no parenthetical definitions inside long sentences. A detail that doesn't change how the figure is read goes in the page text or a table. For example (from `examples/bars_with_seeds.py`):

> **Weight decay raised test accuracy on modular addition from 28% to 99%, in every seed.** Bars are means over five seeds, and dots are the seeds. Accuracy is on 3,000 held-out pairs after 30,000 training steps of a one-layer transformer.

## 4. Draw

Choose the medium first. For anything but a plot in matplotlib, read the guide named here before drawing.
- A figure for a paper, or a quick look during analysis: matplotlib, as below.
- A figure that will sit on an HTML page (a results page or an artifact): HTML by default, as in `guides/page-figures.md`. Use matplotlib when the page can't run scripts (a GitHub README, a forum post, most wikis and note apps) or the venue wants static images.
- The summary figure that opens a post, deck, update or paper: HTML, as in `guides/summary-figure.md`.
- A result that compares several methods on one task, posted where the image must carry the whole story: the story figure, in HTML, as in `guides/story-figure.md`.
- A diagram of a method, pipeline or setup: HTML, as in `guides/diagrams.md`. An illustrated explainer of how code computes something, step by step, has its own skill in this plugin, method-explainer.
- A score on every token, or model replies side by side: HTML, as in `guides/text-figures.md`.

The HTML routes render to PNG with `render_html.sh`, which needs a headless Chromium (the README says how to install one).

Write one standalone script per figure, about 100 lines or fewer. It reads saved tidy data (CSV or parquet) and does nothing else. Don't draw inside the analysis script: helpers built to take any number of rows let rows pile up.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "_kit"))   # the project's copy of the kit
import figkit as fk

fk.use()                     # house style, Inter and the colour roles; call after any sns.set_theme, or instead of it
fig, ax = plt.subplots()     # the size's default (7 x 4 in); don't enlarge it, since text shrinks when the image is scaled
ax.plot(k, loss_top, color=fk.color("top heads"), label="top heads")
ax.plot(k, loss_rand, color=fk.color("random heads"), label="random heads")
ax.fill_between(k, top_lo, top_hi, color=fk.color("top heads"), alpha=0.2, lw=0)   # each k's interval, from fk.interval
ax.set(xscale="log", xlabel="Heads ablated", ylabel="Loss increase (nats)")
fk.plain_ticks(ax.xaxis)     # 1, 10, 100 rather than powers of ten
fk.label_lines(ax)           # names at line ends; fk.label_bars(ax) names bar series, fk.label_values(ax) writes values
gap = fk.difference(top, rand, paired=True, unit="prompts")   # the same prompts under both ablations
fk.title(fig, f"Ablating the top heads raised loss {ratio:.0f} times as much as random heads", claims=gap)
fk.save(fig, "fig1.png")     # prints FIGURE CHECK with anything to fix
```

- The Inter font and the palette below are defaults; keep them unless your venue or page requires otherwise. To match a venue's font or a lab's palette, set `rcParams` or the colours after `fk.use()`, and still keep one accent colour with the rest grey.
- **Size for where the figure goes**: `fk.use(size=...)` with `"screen"` (7 × 4 in, the default), `"slide"`, `"paper"` (6.75 in), `"column"` (3.25 in) or `"post"` (1200 × 960 px, for an image posted on its own; keep such images about 1:1 to 4:3, in HTML too). Text then prints at a readable size there, and the check warns when a figure is drawn wider than its size. Save print figures as PDF.
- **Colour roles**: name each condition once in a `figure-roles.json` beside the scripts, such as `{"control": "random heads", "intervention": "top heads", "ordered": ["70M", "410M", "1.4B"]}`, and colour with `fk.color(name)`, or `palette=fk.palette(names)` in seaborn. The control is grey, the intervention `fk.ACCENT`, `"second"` `fk.BLUE`, and ordered conditions (layers, sizes, steps, doses) a light-to-dark ramp; the check warns when a condition is drawn in another colour. Write the file at the spec stage, so every script and agent uses it.
- Other colours: `fk.ACCENT` for the claim, `fk.GREY` or `fk.LIGHT` for context, and `fk.CATEGORICAL` only when the categories themselves are the point. The check warns about two colours that look alike to colour-blind readers.
- With seaborn, pass `saturation=1` to bar plots and `palette=fk.palette(...)` so the colours stay exact.
- Log axes need `fk.plain_ticks`. Draw the reference line (chance, threshold, y = x) thin and grey, and explain it in the caption.
- **Mocks say so.** Save a figure drawn from fake data, at the spec stage or before the results exist, with `fk.save(fig, path, mock=True)`. It writes "Fake data" in the top right corner, so the figure can't be mistaken for a result once it is passed around. In HTML, write the words in a corner yourself. A figure drawn from a random subsample of the data says so the same way: draw the subsample with a seeded generator and save with `fk.save(fig, path, sample="30 of 1,370 files")`.

**Examples.** Each template has a worked example in `${CLAUDE_SKILL_DIR}/examples/`, with its code, its PNG, and its claim and caption in its header, all on made-up data. Copy the one closest to your question and change the data. The Python examples share `examples/figure-roles.json`.

<!-- examples -->
- Is one condition higher than another? `bar_comparison.py`, `bars_with_seeds.py`
- How do several methods rank, and how sure are we? `dot_intervals.py`, `interactive_dots.html`
- Do two conditions differ, when both were measured on the same units? `paired_differences.py`
- How does a measure change over training, or across layers? `curves_with_seeds.py`, `line_direct_labels.py`
- How does an effect grow with a dose? `steering_strength.py`
- Does a trend follow a scaling law? `scaling_log.py`
- Which method gives the best trade-off? `pareto_frontier.py`
- How well does a probe or monitor separate two classes? `roc_probe.py`, `score_histograms.py`
- Is one model better calibrated than another? `calibration.py`
- Where in the model is the effect? `head_heatmap.py`
- Where in the text does a score fire? `token_scores.html`
- What did the model say? `transcripts.html`
- How does the method work? `diagram.html`
- What was done and what was found, at a glance? `summary_components.html`, `summary_example.html`
- Which method does the task best, and how do the methods differ? `story_figure.html`
<!-- /examples -->

## 5. Check it once (cheap; do it every time)

1. `fk.save` prints `FIGURE CHECK`. Fix every item, or say in one line why it's deliberate. The limits are defaults: when a figure needs more, change them for that figure with `fk.save(fig, path, words=35, max_panels=6)` (also `max_series`, `min_pt`, `title_words`, `panel_title_words`, `order=False` for bars whose order means something, and `spread=False` for a figure of single runs whose title describes only those runs).
2. Read the PNG once and answer, one line each:
   - Without the caption, what does the figure say? Is that the Claim? If it has a title, does the chart show exactly what the title says?
   - Seeing only the image, how sure would a reader be of the result? Is that how sure the data make it? If the image looks surer, draw the seeds, the interval or the differences.
   - What can you remove (text, series, panels, legend, gridlines) without losing the claim? Remove it.
   - Is anything hard to read: small, overlapping, or two colours that look alike?
3. Fix and save again. Stop there; a second look is needed only if the first changed the structure.

## 6. A fresh critic (only for figures going to a mentor, a deck or a paper)

Spawn one subagent that has none of your context. Give it only the PNG path and the Claim, with the prompt in `${CLAUDE_SKILL_DIR}/critic.md`. Apply its cuts, and do one round only. Use this sparingly: it costs a subagent, and step 5 catches most problems.
