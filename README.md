# better-figures

A Claude Code skill for making research figures that a busy researcher understands in five seconds. It is written for interpretability researchers who use Claude Code to run experiments and plot the results, though nothing in it is specific to interpretability.

Left to itself, Claude tends to make figures that show every result at once and put the caption's job into the image: sentence titles, definitions, statistics and verdicts drawn above the data. Asking it to "define every term" makes the labels longer. This skill asks a different question before and after drawing: what can be removed?

![A summary figure drawn with the skill: three heads chosen by attribution patching keep the model's answer when every other head is ablated, and three random heads do not. The result is made up.](skills/figures/examples/summary_example.png)

*A summary figure drawn with the skill's HTML parts. The result it shows is made up: three attention heads chosen by attribution patching keep the model's answer to the prompt when every other head is ablated, and three random heads do not.*

## What it does

The plugin has two parts.

**The skill** (`skills/figures/`) loads when Claude is about to make a figure. It has Claude:

- write a short plan before drawing: the one claim the figure argues, the plot template that makes that argument, the one comparison it shows, and every string that will appear in the image;
- keep definitions, n, intervals and verdicts in the caption, with axis labels and series names next to the data the only text in the image;
- draw with a matplotlib house style (`figkit.py`) that labels lines and bars directly and runs a check on save, which prints what to fix: too many words, a legend that could be direct labels, sentence titles, small or overlapping text;
- draw figures for web pages in HTML and SVG, with exact values in a tooltip, and render a PNG from the same file for slides;
- draw method diagrams and summary figures (the Figure 1 that opens a paper) from HTML parts: chat boxes, a model icon, thought bubbles, network cartoons, ablation marks, check and cross badges;
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

Either way, Claude loads the skill when you ask for a figure. You can also call it directly: `/figures:figures` for the plugin, `/figures` for the copy.

### Requirements

- Python with matplotlib for `figkit.py`; seaborn is optional. The Inter font ships in `skills/figures/fonts/`, and the style falls back to DejaVu Sans without it.
- A headless Chromium for `render_html.sh`, which turns HTML figures and diagrams into PNGs. The script looks for Playwright's headless shell (`uvx playwright install chromium-headless-shell`, or the `npx` equivalent), then Google Chrome or chromium, or uses the path in `$CHROME`.
- A network connection for the interactive example, which loads D3 from jsDelivr and Inter from Google Fonts.

## Examples

`skills/figures/examples/` has one worked example of each kind of figure, each with its source and the rendered PNG. All their data is made up.

| Example | Kind |
|---|---|
| `bar_comparison.py` | bar plot: the loss increase from ablating the top heads by activation patching against random heads, on four tasks |
| `line_direct_labels.py` | line plot with names at the line ends: probe accuracy by layer, against two controls |
| `interactive_dots.html` | HTML figure with a tooltip: how closely four attribution methods rank heads the way ablation does |
| `diagram.html` | method diagram: the three steps of activation patching |
| `summary_example.html` | summary figure, shown above |
| `summary_components.html` | each HTML part of a summary figure once, to copy from |

To re-render them, run the Python scripts with any working directory, and `sh skills/figures/render_html.sh <file>.html <file>.png <width> <height>` for the HTML files (the size of each is in a comment at its top).

## References

The rules for summary figures come from the first figures of five papers by Owain Evans's group: Connecting the Dots, the Reversal Curse, Subliminal Learning, Emergent Misalignment, and Tell Me About Yourself. These papers are under arXiv's default license, which doesn't allow redistribution, so their images are not in this repository. Run `sh skills/figures/references/fetch-references.sh` to download the pages from arXiv for your own reference. A sixth figure, from How to Catch an AI Liar, is under CC BY 4.0 and ships in the folder. [`skills/figures/references/README.md`](skills/figures/references/README.md) lists each paper with its license and the thread on X that announced it, with notes on what each figure does well.

The plot templates the skill chooses from (bar, line, scaling law, calibration, diverging line, Pareto frontier) come from Jo Jiao's post [Research lessons I learned at MATS and Redwood](https://www.lesswrong.com/posts/Q4rcvgjbgjTwmn8Xa/research-lessons-i-learned-at-mats-and-redwood), which argues that a plot is an argument in miniature and that plots matching a known template are much easier to read.

## Does it work?

<!-- EVIDENCE -->
*Results of a test of the skill will go here.*
<!-- /EVIDENCE -->

## License

MIT, copyright 2026 Will Mayner; see [`LICENSE`](LICENSE). The Inter font is under the SIL Open Font License 1.1 (`skills/figures/fonts/Inter-LICENSE.txt`). The figure from How to Catch an AI Liar is under CC BY 4.0 by its authors.
