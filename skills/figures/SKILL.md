---
name: figures
description: Use before making any figure a person will read, such as a matplotlib or seaborn plot, a chart in a report or slide, or a diagram of a method or pipeline, and when designing the figures in an experiment spec. It covers choosing what to show, which text goes in the image (a one-line title that states the finding, values, direct labels) and which goes in the caption, a matplotlib house style with direct labels, colour roles shared by a set of figures, sizes for screens, slides and print, and a check that runs on save, worked examples of common interpretability plots, HTML routes for interactive figures on a page, for diagrams and for token scores and transcripts, each with a PNG for slides, the summary figure (Figure 1) that shows an idea, its method and its result with examples and cartoons, and the story figure that lays out the data, the task, a result comparing several methods, and how each method works on one tall page. Not for dashboards (use dataviz).
---

# Figures

The goal is a figure that a busy researcher understands in five seconds, made in one pass.

The files named below (`figkit.py`, `render_html.sh`, the CSS and JS, `examples/`, `references/`) are in this skill's directory, `${CLAUDE_SKILL_DIR}`.

**On first use in a project, copy the kit into the project.** `${CLAUDE_SKILL_DIR}` can be a folder in Claude Code's plugin cache whose name includes the plugin's version, so a script or page that points there breaks when the plugin updates, and on a collaborator's machine. Copy `figkit.py`, `fonts/` and the CSS and JS once, into a `_kit/` folder beside the figure scripts, and refer to that copy by a path relative to each script or HTML file. If the project already has a `_kit/` folder, use it. The colour roles go in a `figure-roles.json` beside the scripts (section 4).

```
mkdir -p figures/_kit
for f in figkit.py fonts diagram.css summary.css summary.js story.css story.js text.css text.js; do cp -R "${CLAUDE_SKILL_DIR}/$f" figures/_kit/; done
```

`render_html.sh` is a command rather than something a script saves, so run it from `${CLAUDE_SKILL_DIR}`.

Figures go wrong in two ways. They try to show every result, so the figure becomes a table drawn as a plot. And they put the caption's job into the image: definitions, statistics, hedges and annotation boxes, under a long title that explains instead of stating the finding. Writing "one idea per figure" doesn't prevent this, because the idea becomes a long title and everything is still drawn below it. A title is welcome when it states the finding in one plain line (section 3); everything a reader needs to interpret the figure goes in the caption. Reviewing a figure by asking "is every term defined?" makes labels longer. The question to ask is "what can I remove?"

## 1. Decide before drawing

Write this block in your notes, or in the spec when figures are designed there. It takes two minutes and replaces most revision rounds.

```
Claim:    the one sentence the figure argues
Title:    the claim as one line of about 10 words, stating what was compared and what happened (section 3), or none
Template: bar | line | scaling | calibration | diverging line | Pareto | scatter | heatmap
Shows:    the one comparison the claim needs (which series, which subset); the rest goes to a table
Accent:   the one element the eye should land on (ACCENT colour; everything else grey)
Size:     screen | slide | paper | column | post (section 4)
Text:     every string that will appear in the image, listed, at most about 25 words outside the title, tick labels and numbers
Caption:  bold takeaway sentence; 0-3 sentences of detail on the finding; then what is plotted, how measured, n, error bars (section 3a)
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
- When there are several seeds or runs, draw every one: a dot per seed on its bar, or each seed as a faint line behind the bold mean. Never show one run when there are more.
- **When the control is a set of matched random draws, draw every draw, on the effect's own axis.** For each of seven neurons, a bar for the change it makes in the model's choice, with 20 grey tick marks in the same row for 20 random neurons from its layer, steered by the same amount (`fk.random_draws(ax, values, at=row)`), or the draws' range as a grey band behind the bar. The reader sees whether the effect lies outside the draws, which one grey bar or line for their mean hides, and an effect inside the spread shows as weak.
- **For steering or another intervention, show its size and where it acts.** Mark the steering value on a histogram of the unit's activations over ordinary text, so the reader sees how far outside its usual range it is set. Draw the model's layers as a strip of cells with the intervened layers coloured.
- A single before-and-after can be two large numbers with an arrow ("25% → 32%"), with the control's number beside it, in place of two bars.
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
- It names what the eye sees first: the accented series, or the biggest gap. If the point is a small difference, change the chart (accent it, drop the rest), not the words.
- Compute its numbers from the data in the script, as the examples do, so the title can't drift from the figure.
- No colon setups ("The fix: search"), questions, dash asides, full stops, metaphors or wordplay.
- If the result is mixed, the title says so. If no sentence is true of the whole figure, the figure has no title.

`fk.save` checks a title's length, that it fits on one line, its punctuation and its intensifiers; it can't tell whether the title is true.

Three rules for every word in the image and the caption, title included: say what was measured, not what it means ("chose to stop", not "wanted to stop"; "passed 98% test accuracy", not "generalized"); use numbers, not adjectives ("fell from 41% to 12%", not "dropped sharply"); and use no names coined inside the project, such as a code name for a condition or a nickname for a measure.

**Panel titles may state the panel's finding**, like the figure title, and may start with the model's name: "Qwen3-8B: zeroing 6 neurons lowers caving to pushback from 44% to 0%". A model name before the colon is not the colon setup forbidden above. Pass `panel_title_words=14` to `fk.save`. The figure still argues one idea: panels that make several unrelated claims are several figures.

**An image posted on its own** (on X or in Slack, where no caption travels with it) may define its terms in the image, briefly: one grey line of at most about 12 words under a bold label ("Layer targeting" over "the concept only at the layer asked for"), zero named in words ("0 = unsteered"), and both ends of an axis named in words. Raise `words=` for that figure. Statistics (p-values, n, how intervals were computed) still stay out of the image and go in the post's text.

The story figure (section 8) differs in one way: its panel headers are plain sentences that say what the panel shows ("The task: look at a network's activations and point to its planted circuit"). They describe and define, and never state the verdict, which goes in the title and the caption. Its result rows also carry a grey line of training details under each method's name.

There are no annotation boxes, no paragraphs, no rotated tick labels, no variable names from the code, and no numbers to four decimals. Rigor belongs in the caption. The image carries only what the eye needs.

## 3a. Write the caption

A caption has three parts, in this order:
1. **The takeaway, in bold:** one declarative sentence stating what the figure shows. It is the Claim from the plan block, and it can repeat the title with more precision. Never open with "How to read it", "This figure shows" or a description of the axes.
2. **Zero to three sentences on the finding:** the key numbers with their intervals, and the qualification a reader most needs.
3. **What a reader needs to interpret it correctly:** what each line, bar or band is; how it was measured; n; what the error bars are; any reference line; anything excluded.

Each sentence has only a few clauses: no semicolon chains and no parenthetical definitions inside long sentences. Aim for brevity without losing accuracy. A detail that doesn't change how the figure is read goes in the page text or a table.

Bad (one long "How to read it" paragraph, with the takeaway buried):

> **Figure 2. How to read it:** each line is the chosen circuit's overlap (units in both sets divided by units in either; 1 means identical) with the units worth their bits (orange) or with random sets of planted units, as many as the units worth their bits (grey), averaged over the confirmation run's 30 networks with 3 tasks each; bands are 95% bootstrap intervals over networks. Two empty sets count as identical, so both lines start high at small N, …

Good:

> **Figure 2. At every N, the chosen circuit overlaps the units worth their bits far more than random planted units.** At N = 1,000, leaving out cases where both sets are empty, the overlap is 0.48 [0.39, 0.57] against 0.09 [0.07, 0.11]. Above N = 10,000 the chosen circuit also takes in background units, which random planted sets never hold, so part of the gap there is built in.
> Overlap is units in both sets divided by units in either. Lines are means over 30 networks with 3 tasks each, and bands are 95% bootstrap intervals over networks. Two empty sets count as identical, so both lines start near 1 at small N. Both sets are chosen on the same 256 prompts; on 256 other prompts the overlap at N = 1,000 is 0.56 [0.47, 0.65].

## 4. Draw

Choose the medium first:
- A figure that will sit on an HTML page (a results page or an artifact): use HTML by default, as described in section 10. Use matplotlib when the page can't run scripts (a GitHub README, a forum post, most wikis and note apps) or the venue wants static images.
- A figure for a paper, or a quick look during analysis: use matplotlib, as below.
- A diagram of a method: use HTML, as described in section 9.
- The summary figure that opens a post, deck, update or paper: use HTML, as described in section 7.
- A result that compares several methods on one task, posted where the image must carry the whole story: the story figure, in HTML, as described in section 8.
- A score on every token, or model replies side by side: HTML, as described in section 11.

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
ax.set(xscale="log", xlabel="Heads ablated", ylabel="Loss increase (nats)")
fk.plain_ticks(ax.xaxis)     # 1, 10, 100 rather than powers of ten
fk.label_lines(ax)           # names at line ends; fk.label_bars(ax) names bar series, fk.label_values(ax) writes values
fk.title(fig, f"Ablating the top heads raised loss {ratio:.0f} times as much as random heads")
fk.save(fig, "fig1.png")     # prints FIGURE CHECK with anything to fix
```

- The Inter font and the palette below are defaults; keep them unless your venue or page requires otherwise. To match a venue's font or a lab's palette, set `rcParams` or the colours after `fk.use()`, and still keep one accent colour with the rest grey.
- **Size for where the figure goes.** `fk.use(size=...)` takes `"screen"` (7 × 4 in, the default), `"slide"` (10 × 5.6 in), `"paper"` (6.75 in, the full text width of a two-column paper), `"column"` (3.25 in, one column of it) or `"post"` (6 × 4.8 in, 1200 × 960 px, for an image posted on its own; X and Slack crop or shrink wide images, so keep such images about 1200 px wide and 1:1 to 4:3, in HTML too). Each sets the figure size, and font sizes that print at a readable size there, and the check measures the text at that size. A figure drawn wider than its size shrinks when it is placed, and its text with it; the check says by how much. Save print figures as PDF.
- **Colour roles.** Name each condition once in a `figure-roles.json` beside the figure scripts, and every figure colours it the same way: `{"control": "random heads", "intervention": "top heads", "second": "half the data", "ordered": ["70M", "410M", "1.4B"]}`. The control is grey, the intervention `fk.ACCENT`, a second intervention `fk.BLUE`, a third to fifth the next Okabe-Ito colours, and conditions with an order of their own (layers, sizes, steps, doses) a light-to-dark blue ramp; a condition without a role is grey. `fk.color(name)`, and `fk.palette(names)` for seaborn, read the file. The check warns when a named condition is drawn in another colour, and when a label nearly matches a role's name ("random heads (n=10)"). Write the file with the figures at the spec stage, so every script and agent working on the write-up uses it.
- Other colours: `fk.ACCENT` for the claim, `fk.GREY` or `fk.LIGHT` for context, and `fk.CATEGORICAL` only when the categories themselves are the point. The check warns about two colours that look alike to colour-blind readers.
- With seaborn, pass `saturation=1` to bar plots and `palette=fk.palette(...)` so the colours stay exact.
- Log axes need `fk.plain_ticks`. Draw the reference line (chance, threshold, y = x) thin and grey, and explain it in the caption.
- **Mocks say so.** Save a figure drawn from fake data, at the spec stage or before the results exist, with `fk.save(fig, path, mock=True)`. It writes "Fake data" in the top right corner, so the figure can't be mistaken for a result once it is passed around. In HTML, write the words in a corner yourself.

**Examples.** Each template has a worked example in `${CLAUDE_SKILL_DIR}/examples/`, with its code, its PNG, and its claim and caption in its header, all on made-up data. Copy the one closest to your question and change the data. The Python examples share `examples/figure-roles.json`.

<!-- examples -->
- Is one condition higher than another? `bar_comparison.py`, `bars_with_seeds.py`
- How do several methods rank, and how sure are we? `dot_intervals.py`, `interactive_dots.html`
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

1. `fk.save` prints `FIGURE CHECK`. Fix every item, or say in one line why it's deliberate. The limits are defaults: when a figure needs more, change them for that figure with `fk.save(fig, path, words=35, max_panels=6)` (also `max_series`, `min_pt`, `title_words`, `panel_title_words`, and `order=False` for bars whose order means something).
2. Read the PNG once and answer, one line each:
   - Without the caption, what does the figure say? Is that the Claim? If it has a title, does the chart show exactly what the title says?
   - What can you remove (text, series, panels, legend, gridlines) without losing the claim? Remove it.
   - Is anything hard to read: small, overlapping, or two colours that look alike?
3. Fix and save again. Stop there; a second look is needed only if the first changed the structure.

## 6. A fresh critic (only for figures going to a mentor, a deck or a paper)

Spawn one subagent that has none of your context. Give it only the PNG path and the Claim, with the prompt in `${CLAUDE_SKILL_DIR}/critic.md`. Apply its cuts, and do one round only. Use this sparingly: it costs a subagent, and step 5 catches most problems.

## 7. The summary figure (Figure 1)

By default, the first figure of a post, deck, update or paper about a result is a summary figure, unless your venue or page requires otherwise. It shows the idea, the method and the result at once, with concrete examples and cartoons and almost no prose, so that a busy reader who looks at nothing else still knows what was done and what was found. It comes before any plot; quantitative results go in the figures after it.

When the result is a comparison of several methods, and the chart cannot be read without seeing the task and how the methods differ, use the story figure (section 8) instead: it draws the same kind of examples and cartoons, and puts the chart in the middle of them.

The grammar comes from the first figures of five papers from Owain Evans's group: Connecting the Dots ([arXiv:2406.14546](https://arxiv.org/abs/2406.14546)), the Reversal Curse ([arXiv:2309.12288](https://arxiv.org/abs/2309.12288)), Subliminal Learning ([arXiv:2507.14805](https://arxiv.org/abs/2507.14805)), Emergent Misalignment ([arXiv:2502.17424](https://arxiv.org/abs/2502.17424)) and Tell Me About Yourself ([arXiv:2501.11120](https://arxiv.org/abs/2501.11120)). Before drawing, look at `${CLAUDE_SKILL_DIR}/examples/summary_example.png`, and at one of the five pages in `${CLAUDE_SKILL_DIR}/references/fetched/` if that folder exists (`sh ${CLAUDE_SKILL_DIR}/references/fetch-references.sh` downloads them from arXiv, for personal use). `${CLAUDE_SKILL_DIR}/references/README.md` has notes on what each does well. A figure from How to Catch an AI Liar also ships in `references/`; it shows how to draw chat bubbles and a classifier, not a layout to copy.

Rules:
- **Two to four panels, laid out in one of two ways.** Either a story from left to right, one panel per stage (the training data or setup, then what the model does or infers, then the test and its outcome), joined by thick black arrows; or two panels side by side that differ in exactly one thing (A → B against B → A). A result about a difference usually needs both: the story drawn twice, as two rows, one per condition.
- **Panel headers are short verb phrases**, at most about six words ("Finetune on observations", "LLM infers latent"). They carry no jargon that the image has not shown.
- **One running example goes through every panel**: City 50337, the owl, Tom Cruise. Bold it inside the text where it appears.
- **Concrete examples carry the content.** Real User and Assistant exchanges in boxes with role labels, or a base model's prompt in a box without them; for interpretability, a real token, a real unit or a planted circuit. Show two or three examples and a "..." for the rest of a dataset.
- **Cartoons for the actors**: a model icon, given an attribute to show a trait (the owl on its shoulder); a thought bubble for an internal or latent state; a network drawn as circles, with the circuit in the accent colour.
- **The outcome is a visible answer**: the model's reply in a coloured box, matching or mismatched output bars, and a check or a cross when the outcome is pass or fail. Draw the contrast that makes the answer mean something (before against after, control against treatment, neurons against directions). Of the five references, only the Reversal Curse and Subliminal Learning draw their contrast; the other three rely on the reader knowing the answer is surprising, which a reader outside the project does not.
- **A title is optional**: one line above the panels stating the finding, as in section 3. None of the five references has one, because their papers' captions do that job; a figure posted on its own may need it.
- **No prose outside the examples, and almost no numbers.** None of the five references prints a result number. Two kinds are allowed. A real model output on an example card may carry its count, with the control's count beside it ("18/30 about the military", "0/600 for random pairs"), which answers "is this cherry-picked?" where the reader is looking. And one before-and-after may be two large numbers with an arrow ("25% → 32%"), with the control beside it. No other numbers. (A story figure, section 8, does print its result's numbers, in the result panel only.) The caption follows section 3a: the bold takeaway, up to three sentences on the finding, then what a reader needs to interpret it.
- Keep the diagram rules of section 9: one accent colour for the thing the figure is about, red only for ablated or failed, green only for passed, a wide canvas.

Plan it before drawing, as in section 1:

```
Idea:      the finding in one sentence (this becomes the caption's bold first sentence)
Example:   the one running example that appears in every panel
Layout:    story (left to right) | contrast (side by side) | story in two rows, one per condition
Panels:    for each, the header (a verb phrase of at most 6 words) and what it shows
Contrast:  the two conditions whose outcomes differ
Outcome:   how the answer is shown (reply box, output bars, check and cross)
Text:      every string that will appear in the image, listed
Caption:   as in section 3a: bold takeaway, 0-3 sentences on the finding, then how to interpret it
```

Draw it in HTML that links `_kit/summary.css` and `_kit/summary.js` (the network cartoon and the icons are inline SVG, so headless rendering is reliable), and render with `render_html.sh`. The parts:

| Part | Markup |
|---|---|
| Chat box, User and Assistant rows; colour by kind of example | `<div class="chat accent"><div class="user">..</div><div class="assistant">..</div></div>`, inside `.frame`, `.more` for "..." |
| Completion prompt for a base model, no role labels | `<div class="chat grey"><div class="text">.. gave a drink to <span class="tok accent">Mary</span></div></div>` |
| Model icon, with an attribute at the shoulder | `<span class="model trait" data-icon="model"><span class="attr tok">owl</span></span>` |
| Thought bubble | `<div class="thought">City 50337 is Paris</div>` above the model |
| Network: circuit, greyed and ablated units, directions | `<svg class="net" width="230" height="230" data-layers="3,5,4,2" data-on="1.1 2.2" data-ablate="1 2" data-dim="0" data-dirs="1" data-broken="1">` |
| Method stamp | `<span class="stamp" data-icon="magnifier">EAP-IG</span>` on the arrow from a model to its circuit |
| Check and cross | `<span class="badge check" data-icon="check"></span>`, `.badge.cross` |
| Stage arrow | `<span class="arrow" data-icon="arrow"></span>`, `arrow-dashed` |
| Token chip | `<span class="tok accent">Paris</span>` |
| Output bars, target against intervention | `.out` > `figure` > `.bars` > `.bar` (`.target`, `.on`) |

`examples/summary_components.html` shows each part once, `examples/summary_example.html` is a whole figure, and `examples/summary_example_check.md` records how fresh readers read it.

**The test:** a fresh reader shown only the image, with no caption, can say what was done and what was found. Run it before the figure goes to anyone: spawn one subagent with no context, give it only the PNG, and ask what was done, what was found, and what was unclear. Fix what it misreads, and stop after three rounds. Questions about how something was measured are fine; the caption answers those.

## 8. The story figure: data, task, result and method on one page

A story figure tells a whole experiment in one tall image, read from top to bottom: the data, the task, the result, how each method works, and a close-up of the one new mechanism. A reader who sees only this image (in a Slack thread, at the top of a results page) can say what the data were, what was asked of the methods, which did best, and why the methods differ.

Use it instead of the summary figure (section 7) when the result compares several methods or conditions on one task, and the reader needs to see the task and how the methods differ to read the comparison. Use the summary figure for one idea with one contrast, and a plain plot (sections 1 to 6) when the reader already knows the task and the methods.

Rules:
- **Panels in reading order, each answering the question the one above raises.** The data (full width). The task (left) beside the result (right), so the eye goes from the task straight to the bars. How each method works (a row of cards). A zoom into one mechanism (full width), only if one method is new or needs it. Each panel can be read with only the panels above it.
- **Headers are plain sentences that say what the panel shows**, about 6 to 14 words, with the panel's role first where it helps: "The data: copies of one small network, each trained with its own planted rule"; "The task: look at a network's activations and point to its planted circuit". The result panel's header names exactly what each number counts ("Test cases where the method picked exactly the planted circuit's units"), which also defines what counts as success, so it is the axis title too. No header states a verdict ("the mask network wins"); the verdict goes in the figure's title, if it has one, and in the caption.
- **One running example, drawn as real content.** Real inputs, tokens and outputs, not placeholders. Each actor's item (A's rule, B's rule) has one highlight, a tint and an underline in the actor's colour, and keeps it in every panel where it appears: the training data, the test input, the hidden answer, the method's answer and the zoom.
- **One colour per actor, fixed across every panel.** A light shade for an unchanged part and the full colour for the part being read or answered. One colour, and only one, for "trained for this task"; never reuse an actor's colour for it. Grey for untrained or unchanged. Green and red only for pass and fail.
- **Counts as icon arrays.** One small square per item next to one large number: filled for the items methods train on, hollow for the held-out items. The reader sees the split before reading the words.
- **The result: horizontal bars, one row per method.** The method's name in bold to the left, with one small grey line under it giving its training details ("trained on 24 copies"). The value in bold at the bar's end, a 95% interval as a whisker, and no tick labels. One dashed reference line labelled at its foot in words ("random guessing"), and the axis maximum written as words ("all 120") under a light line, so the reader sees both ends of the scale. Untrained methods first, in grey; then trained methods in groups by training size, with a gap between groups and the same method order in every group. A legend of at most three items (the two colours and the interval) above the bars, where no line crosses it. About ten rows at most; more than that belongs in a table.
- **The control is drawn twice.** The obvious alternative (a method that reads only the input, say) is a row in the chart, and in the task panel it is a dashed box with a red cross that says in a few words why it must fail ("Input alone: same digits → same answer for A and B").
- **Method cards share one layout and one visual vocabulary**, so only the method changes from card to card. A network is a stack of small cells, one row per layer, in the actor's light colour, with the layers the method reads in the full colour. Trained parts are in the trained colour, and every card ends in the same answer pill. Under each card, a legend of at most three items names each colour's actor and state in this card ("**Network A**, unchanged"; "layers 3–5, read"; "**probe**, trained").
- **The zoom** draws the small stack again with one layer highlighted, and a grey wedge from that layer into the expanded view. Inside, it uses the running example's own input, and shows the mechanism one level of detail below the method cards. Draw the real computation (the real number of layers, the real steps in order); a simplification that is false is worse than none. Mark whether what the zoom shows is correct (the units kept against the planted units, with a check), so the reader can judge it.
- **Illustrative values only inside mechanism drawings**, labelled as illustrative there, and never in the result panel. Every number in the result panel comes from a results file, and the data that draws it names that file (the `source` field in the example).
- **Compare methods fairly, and show it.** Every method is scored on the same test items, and each row's grey line gives its training-set size.
- **No paragraphs and no statistics outside the result panel.** Every string is a header, a label on a drawn thing, a real example, or a training detail. Definitions of the measure, n, how intervals were computed and the test split go in the caption (section 3a). Don't repeat a fact the image already states. No label uses a pronoun whose noun is not in the same label ("units it keeps" becomes "units the mask network keeps").
- **Text big enough for a slide:** nothing smaller than about 14 px at 1100 px wide (26 px at 2000 px), panel headers about 20 px, values at bar ends bold. No text crosses a line, a bar or other text.
- About 1100 px wide and as tall as it needs (roughly 1:1.5), stacking to one column on a phone without horizontal scroll.

The rules on text size, pronouns, illustrative values, sources, fair comparison and drawing the real computation are adapted from the figure guide in the SauersML/params repository by Scott Sauers ([@Sauers_](https://x.com/Sauers_)).

Plan it before drawing, as in section 1:

```
Question:  what the reader should be able to answer from the image alone (which method does the task best, and how they differ)
Example:   the running example, drawn as real content, and the highlight each actor's item keeps
Colours:   each actor and its colour; the trained colour; grey for untrained or unchanged
Panels:    in order, each with its header (a plain sentence saying what the panel shows) and its content
Result:    the measure (the result header), the rows and their groups, the reference line, the interval, the axis maximum
Control:   the obvious alternative, as a row in the chart and as a crossed box in the task panel
Text:      every string that will appear in the image, listed
Caption:   as in section 3a: bold takeaway, 0-3 sentences on the finding, then how to interpret it
```

Draw it in HTML that links `_kit/story.css` and `_kit/story.js` (cell stacks for layers, icon arrays, and the result chart drawn from JSON in the page), plus `_kit/summary.js` for network cartoons. `examples/story_figure.html` is a whole figure with made-up content, and its comment holds the caption; render yours with `sh ${CLAUDE_SKILL_DIR}/render_html.sh figure.html figure.png 1100 1740`, with your page's height in place of 1740. `examples/story_figure_check.md` records how a fresh reader read it.

Before anyone sees it, open the PNG and look at each panel at full size (crop it if the whole image is shrunk on screen) for overlaps, cut-off text and text that is too small.

**The test:** as in section 7, a fresh reader shown only the image says what was done and what was found. Also ask what the numbers at the bar ends count; if the reader cannot say, the result header is not doing its job. In the template's test, the reader's worst confusions were what one test case was and whether a trained method was trained on the held-out copy; state both in the image (the held-out count with its inputs per copy, and a line in the zoom).

## 9. Diagrams of a method, pipeline or setup

Don't draw these in matplotlib. Write HTML that links `_kit/diagram.css` (cards, pills, numbered steps, chevrons, accent and muted colours, Inter), and render it to a PNG:

```
sh ${CLAUDE_SKILL_DIR}/render_html.sh diagram.html diagram.png 1600 500   # width and height of .canvas
```

The same rules apply, in this form:
- Each box gets a bold name of at most 5 words and one grey line of at most 12 words.
- No legend.
- One accent colour for the thing the diagram is about.
- Red only for ablated or failed, green only for passed.
- One concrete running example (a real token or a real unit) that appears in every panel.
- The same symbol always means the same thing.
- A wide canvas, 2:1 to 3:1, or square to 4:3 for an image posted on its own.

See `examples/diagram.html`.

## 10. Figures for a page: HTML, with a PNG rendered from the same file

When a figure will live on an HTML page that can run scripts, draw it in HTML and SVG rather than matplotlib by default, unless your venue or page requires otherwise. There are two reasons. First, Claude's design judgment is much better in HTML and CSS. Second, a page can show details on demand. The static view stays clean, and the exact values, intervals, n, verdicts and identifiers appear on hover or click. That takes away the pull to print statistics in the image.

- Start from `examples/interactive_dots.html`. It has colour tokens for light and dark mode, the Inter font, D3 from a CDN, the data inline as JSON, a title, and a tooltip. Have your Python script write the data JSON into a copy of the file, and adapt `draw()`.
- The static view obeys sections 2 and 3. The tooltip, or a panel that opens on click, carries everything else.
- Give the chart `role="img"` and an `aria-label` with the data in words (the plan block's Alt line), as the examples do. A PNG on a page takes the same words as its alt text.
- Render the PNG for slides from the same file: `sh ${CLAUDE_SKILL_DIR}/render_html.sh figure.html figure.png 900 460`, where 900 and 460 are the size of the `.fig` box. Look at the PNG once, as in step 5. `fk.save`'s check doesn't run here, so apply its limits by eye: the title on one line, at most about 25 other words, no text under about 12 px.

## 11. Figures made of text: token scores and replies

For a score on every token (a probe, an attribution, an SAE latent's activation) or model replies side by side, write HTML that links `_kit/text.css` and loads `_kit/text.js`, and render it with `render_html.sh`.
- **Token scores** (`examples/token_scores.html`): one row per text, each token shaded on a diverging scale (blue below zero, the accent above), with the colour bar above the rows. Give each `.tokens` element its scores as `[[token, score], ...]` JSON in the `<script>` after it; `text.js` draws a token's leading space outside its shading, turns text white on dark shades, and shows the score on hover. Add a row that shows the contrast (the honest answer, the unsteered model), so the shading means something.
- **Replies side by side** (`examples/transcripts.html`): the prompt across the top, one card per condition, the intervention's card with the accent border, the phrase that matters in `.hl`, and an outcome dot (green for passed, red for failed) whose words stay in ink.
- Quote real outputs, cut with "…", never paraphrased. The title states the finding, as in section 3. Put the count on the card when you have one ("18/30 about the military", with the unsteered count beside it), and the caption says how the outputs were sampled.

## Sources

Random draws as the control, the size and place of an intervention, large before-and-after numbers, counts on example cards, short definitions and the square size for images posted on their own, and panel titles that state findings come from Scott Sauers's figures on X ([@Sauers_](https://x.com/Sauers_)), October 2026.

## Requirements

- `figkit.py` needs matplotlib; seaborn is optional. It loads the Inter font from `fonts/` next to it, which is why `fonts/` is copied into `_kit/` with it, and falls back to DejaVu Sans.
- `render_html.sh` needs a headless Chromium: Playwright's headless shell (`uvx playwright install chromium-headless-shell` or `npx playwright install chromium-headless-shell`), Google Chrome or chromium, or a browser path in `$CHROME`.
- `examples/interactive_dots.html` loads D3 from a CDN (jsDelivr) and Inter from Google Fonts, so the page and its render need a network connection.
