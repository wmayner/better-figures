---
name: figures
description: Use before making any figure a person will read, such as a matplotlib or seaborn plot, a chart in a report or slide, or a diagram of a method or pipeline, and when designing the figures in an experiment spec. It covers choosing what to show, keeping text out of the image, a matplotlib house style with direct labels and a check that runs on save, HTML routes for interactive figures on a page and for diagrams, each with a PNG for slides, and the summary figure (Figure 1) that shows an idea, its method and its result with examples and cartoons. Not for dashboards.
---

# Figures

The goal is a figure that a busy researcher understands in five seconds, made in one pass.

The files named below (`figkit.py`, `render_html.sh`, the CSS and JS, `examples/`, `references/`) are in this skill's directory, `${CLAUDE_SKILL_DIR}`.

**On first use in a project, copy the kit into the project.** `${CLAUDE_SKILL_DIR}` can be a folder in Claude Code's plugin cache whose name includes the plugin's version, so a script or page that points there breaks when the plugin updates, and on a collaborator's machine. Copy `figkit.py`, `fonts/` and the CSS and JS once, into a `_kit/` folder beside the figure scripts, and refer to that copy by a path relative to each script or HTML file. If the project already has a `_kit/` folder, use it.

```
mkdir -p figures/_kit
for f in figkit.py fonts diagram.css summary.css summary.js; do cp -R "${CLAUDE_SKILL_DIR}/$f" figures/_kit/; done
```

`render_html.sh` is a command rather than something a script saves, so run it from `${CLAUDE_SKILL_DIR}`.

Figures go wrong in two ways. They try to show every result, so the figure becomes a table drawn as a plot. And they put the caption's job into the image: definitions, statistics, verdicts, and titles written as sentences. Writing "one idea per figure" doesn't prevent this, because the idea becomes the title and everything is still drawn below it. Reviewing a figure by asking "is every term defined?" makes labels longer. The question to ask is "what can I remove?"

## 1. Decide before drawing

Write this block in your notes, or in the spec when figures are designed there. It takes two minutes and replaces most revision rounds.

```
Claim:    the one sentence the figure argues
Template: bar | line | scaling | calibration | diverging line | Pareto | scatter | heatmap
Shows:    the one comparison the claim needs (which series, which subset); the rest goes to a table
Accent:   the one element the eye should land on (ACCENT colour; everything else grey)
Text:     every string that will appear in the image, listed, at most about 25 words outside tick labels
Caption:  at most 3 sentences under the image: what is plotted, how it was measured, n, what the error bars are
Sketch:   a 4-line ASCII sketch
```

Write the claim first, then choose the template that makes that argument. Each of six common templates usually makes one claim:
- bar plot: this one is higher than this one;
- line plot: the numbers go up or down;
- scaling law plot: the trend is linear in log or logit space;
- calibration plot: model A is much better calibrated than model B;
- diverging line plot: this line goes up, this one doesn't;
- Pareto frontier plot: we push the Pareto frontier.

Scatter plots and heatmaps cover a relation between two measures and a grid of values. If no template fits, the figure is probably trying to say more than one thing; split it or simplify it.

At the spec stage, the person approves this block, not a prose description of encodings ("rows: methods × targets; filled vs open markers; verdict in the margin" reads as simple and draws as a wall). Better still, draw the figure once from fake data and show the image.

## 2. Choose what to show

- One panel by default. Use small multiples (at most 4 panels, shared axes) only when the same comparison repeats across conditions.
- At most 4 series per panel. Keep the ones the claim needs; grey or drop the rest.
- If you want a verdict column, a statistic printed on every row, "two versions", or a panel per target, you are drawing a table. Put the table on the page and draw the one row that matters.
- Diagnostics and secondary results do not go in the figures someone is asked to read.

## 3. Keep text out of the image

| Content | In the image? | Where instead |
|---|---|---|
| The claim | No sentence titles, no suptitle | the heading or slide title above the figure, or the caption's first sentence |
| Definitions, n, interval method, thresholds, priors, Bayes factors, sampling notes | No | caption or page text |
| Axis labels | Yes, at most about 6 words, with units | |
| Series names | Yes, next to the data (`fk.label_lines`, `fk.label_bars`) | a legend only for 5+ categories, and then you have too many |
| One key number | Yes, if it is the point: one, next to its mark | |
| Panel names | Yes, at most 4 words | |

There are no annotation boxes, no paragraphs, no rotated tick labels, no variable names from the code, and no numbers to four decimals. Rigor belongs in the caption. The image carries only what the eye needs.

## 4. Draw

Choose the medium first:
- A figure that will sit on an HTML page (a results page or an artifact): use HTML by default, as described in section 9. Use matplotlib when the page can't run scripts (a GitHub README, a forum post, most wikis and note apps) or the venue wants static images.
- A figure for a paper, or a quick look during analysis: use matplotlib, as below.
- A diagram of a method: use HTML, as described in section 8.
- The summary figure that opens a post, deck, update or paper: use HTML, as described in section 7.

Write one standalone script per figure, about 100 lines or fewer. It reads saved tidy data (CSV or parquet) and does nothing else. Don't draw inside the analysis script: helpers built to take any number of rows let rows pile up.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "_kit"))   # the project's copy of the kit
import figkit as fk

fk.use()                     # house style and the Inter font; call after any sns.set_theme, or instead of it
fig, ax = plt.subplots()     # 7 x 4 in default; don't enlarge to fit more, since text shrinks when the image is scaled
ax.plot(k, loss_top, color=fk.ACCENT, label="top heads by patching")
ax.plot(k, loss_rand, color=fk.GREY, label="random heads")
ax.set(xscale="log", xlabel="Heads ablated", ylabel="Loss increase (nats)")
fk.plain_ticks(ax.xaxis)     # 1, 10, 100 rather than powers of ten
fk.label_lines(ax)           # names at line ends; fk.label_bars(ax) for bar charts
fk.save(fig, "fig1.png")   # prints FIGURE CHECK with anything to fix
```

- The Inter font and the palette below are defaults; keep them unless your venue or page requires otherwise. To match a venue's font or a lab's palette, set `rcParams` or the colours after `fk.use()`, and still keep one accent colour with the rest grey.
- Colours: `fk.ACCENT` for the claim, `fk.GREY` or `fk.LIGHT` for context, `fk.BLUE` for a second highlighted series, and `fk.CATEGORICAL` only when the categories themselves are the point. Keep each colour's meaning fixed across a set of figures.
- With seaborn, pass `saturation=1` to bar plots and `palette={level: colour}` so the accent stays exact.
- Log axes need `fk.plain_ticks`. Draw the reference line (chance, threshold, y = x) thin and grey, and explain it in the caption.
- Worked examples, with code and the rendered PNG, are in `${CLAUDE_SKILL_DIR}/examples/`. Their data is made up. View one if you're unsure what the target looks like.

## 5. Check it once (cheap; do it every time)

1. `fk.save` prints `FIGURE CHECK`. Fix every item, or say in one line why it's deliberate. The limits are defaults: when a figure needs more, change them for that figure with `fk.save(fig, path, words=35, max_panels=6)` (also `max_series`, `min_pt` and `title_words`).
2. Read the PNG once and answer, one line each:
   - Without the caption, what does the figure say? Is that the Claim?
   - What can you remove (text, series, panels, legend, gridlines) without losing the claim? Remove it.
   - Is anything hard to read: small, overlapping, or two colours that look alike?
3. Fix and save again. Stop there; a second look is needed only if the first changed the structure.

## 6. A fresh critic (only for figures going to a mentor, a deck or a paper)

Spawn one subagent that has none of your context. Give it only the PNG path and the Claim, with the prompt in `${CLAUDE_SKILL_DIR}/critic.md`. Apply its cuts, and do one round only. Use this sparingly: it costs a subagent, and step 5 catches most problems.

## 7. The summary figure (Figure 1)

By default, the first figure of a post, deck, update or paper about a result is a summary figure, unless your venue or page requires otherwise. It shows the idea, the method and the result at once, with concrete examples and cartoons and almost no prose, so that a busy reader who looks at nothing else still knows what was done and what was found. It comes before any plot; quantitative results go in the figures after it.

The grammar comes from the first figures of five papers from Owain Evans's group: Connecting the Dots ([arXiv:2406.14546](https://arxiv.org/abs/2406.14546)), the Reversal Curse ([arXiv:2309.12288](https://arxiv.org/abs/2309.12288)), Subliminal Learning ([arXiv:2507.14805](https://arxiv.org/abs/2507.14805)), Emergent Misalignment ([arXiv:2502.17424](https://arxiv.org/abs/2502.17424)) and Tell Me About Yourself ([arXiv:2501.11120](https://arxiv.org/abs/2501.11120)). Before drawing, look at `${CLAUDE_SKILL_DIR}/examples/summary_example.png`, and at one of the five pages in `${CLAUDE_SKILL_DIR}/references/fetched/` if that folder exists (`sh ${CLAUDE_SKILL_DIR}/references/fetch-references.sh` downloads them from arXiv, for personal use). `${CLAUDE_SKILL_DIR}/references/README.md` has notes on what each does well. A figure from How to Catch an AI Liar also ships in `references/`; it shows how to draw chat bubbles and a classifier, not a layout to copy.

Rules:
- **Two to four panels, laid out in one of two ways.** Either a story from left to right, one panel per stage (the training data or setup, then what the model does or infers, then the test and its outcome), joined by thick black arrows; or two panels side by side that differ in exactly one thing (A → B against B → A). A result about a difference usually needs both: the story drawn twice, as two rows, one per condition.
- **Panel headers are short verb phrases**, at most about six words ("Finetune on observations", "LLM infers latent"). They carry no jargon that the image has not shown.
- **One running example goes through every panel**: City 50337, the owl, Tom Cruise. Bold it inside the text where it appears.
- **Concrete examples carry the content.** Real User and Assistant exchanges in boxes with role labels, or a base model's prompt in a box without them; for interpretability, a real token, a real unit or a planted circuit. Show two or three examples and a "..." for the rest of a dataset.
- **Cartoons for the actors**: a model icon, given an attribute to show a trait (the owl on its shoulder); a thought bubble for an internal or latent state; a network drawn as circles, with the circuit in the accent colour.
- **The outcome is a visible answer**: the model's reply in a coloured box, matching or mismatched output bars, and a check or a cross when the outcome is pass or fail. Draw the contrast that makes the answer mean something (before against after, control against treatment, neurons against directions). Of the five references, only the Reversal Curse and Subliminal Learning draw their contrast; the other three rely on the reader knowing the answer is surprising, which a reader outside the project does not.
- **No prose outside the examples, and no numbers.** None of the five references prints a result number. If one number is truly needed, it goes in one small inset. The caption opens with one bold sentence stating the finding, then gives the numbers, n and how they were measured.
- Keep the diagram rules of section 8: one accent colour for the thing the figure is about, red only for ablated or failed, green only for passed, a wide canvas.

Plan it before drawing, as in section 1:

```
Idea:      the finding in one sentence (this becomes the caption's bold first sentence)
Example:   the one running example that appears in every panel
Layout:    story (left to right) | contrast (side by side) | story in two rows, one per condition
Panels:    for each, the header (a verb phrase of at most 6 words) and what it shows
Contrast:  the two conditions whose outcomes differ
Outcome:   how the answer is shown (reply box, output bars, check and cross)
Text:      every string that will appear in the image, listed
Caption:   bold finding, then what was measured, the numbers and n
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

## 8. Diagrams of a method, pipeline or setup

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
- A wide canvas, 2:1 to 3:1.

See `examples/diagram.html`.

## 9. Figures for a page: HTML, with a PNG rendered from the same file

When a figure will live on an HTML page that can run scripts, draw it in HTML and SVG rather than matplotlib by default, unless your venue or page requires otherwise. There are two reasons. First, Claude's design judgment is much better in HTML and CSS. Second, a page can show details on demand. The static view stays clean, and the exact values, intervals, n, verdicts and identifiers appear on hover or click. That takes away the pull to print statistics in the image.

- Start from `examples/interactive_dots.html`. It has colour tokens for light and dark mode, the Inter font, D3 from a CDN, the data inline as JSON, and a tooltip. Have your Python script write the data JSON into a copy of the file, and adapt `draw()`.
- The static view obeys sections 2 and 3. The tooltip, or a panel that opens on click, carries everything else.
- Render the PNG for slides from the same file: `sh ${CLAUDE_SKILL_DIR}/render_html.sh figure.html figure.png 900 420`, where 900 and 420 are the size of the `.fig` box. Look at the PNG once, as in step 5. `fk.save`'s check doesn't run here, so apply its limits by eye.

## Requirements

- `figkit.py` needs matplotlib; seaborn is optional. It loads the Inter font from `fonts/` next to it, which is why `fonts/` is copied into `_kit/` with it, and falls back to DejaVu Sans.
- `render_html.sh` needs a headless Chromium: Playwright's headless shell (`uvx playwright install chromium-headless-shell` or `npx playwright install chromium-headless-shell`), Google Chrome or chromium, or a browser path in `$CHROME`.
- `examples/interactive_dots.html` loads D3 from a CDN (jsDelivr) and Inter from Google Fonts, so the page and its render need a network connection.
