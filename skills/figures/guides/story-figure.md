# The story figure: data, task, result and method on one page

Paths in this guide are relative to the figures skill's directory, the parent of this `guides/` folder (`${CLAUDE_SKILL_DIR}` in `SKILL.md`). Sections 1 to 6 of `SKILL.md` apply here too.

A story figure tells a whole experiment in one tall image, read from top to bottom: the data, the task, the result, how each method works, and a close-up of the one new mechanism. A reader who sees only this image (in a Slack thread, at the top of a results page) can say what the data were, what was asked of the methods, which did best, and why the methods differ.

Use it instead of the summary figure (`guides/summary-figure.md`) when the result compares several methods or conditions on one task, and the reader needs to see the task and how the methods differ to read the comparison. Use the summary figure for one idea with one contrast, and a plain plot (`SKILL.md`) when the reader already knows the task and the methods.

Its panel headers are plain sentences that say what the panel shows, unlike the short names of `SKILL.md` section 3: they describe and define, and never state the verdict, which goes in the title and the caption. Its result rows also carry a grey line of training details under each method's name.

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
- **No paragraphs and no statistics outside the result panel.** Every string is a header, a label on a drawn thing, a real example, or a training detail. Definitions of the measure, n, how intervals were computed and the test split go in the caption (`SKILL.md` section 3a). Don't repeat a fact the image already states. No label uses a pronoun whose noun is not in the same label ("units it keeps" becomes "units the mask network keeps").
- **Text big enough for a slide:** nothing smaller than about 14 px at 1100 px wide (26 px at 2000 px), panel headers about 20 px, values at bar ends bold. No text crosses a line, a bar or other text.
- About 1100 px wide and as tall as it needs (roughly 1:1.5), stacking to one column on a phone without horizontal scroll.

The rules on text size, pronouns, illustrative values, sources, fair comparison and drawing the real computation are adapted from the figure guide in the SauersML/params repository by Scott Sauers ([@Sauers_](https://x.com/Sauers_)).

Plan it before drawing, as in `SKILL.md` section 1:

```
Question:  what the reader should be able to answer from the image alone (which method does the task best, and how they differ)
Example:   the running example, drawn as real content, and the highlight each actor's item keeps
Colours:   each actor and its colour; the trained colour; grey for untrained or unchanged
Panels:    in order, each with its header (a plain sentence saying what the panel shows) and its content
Result:    the measure (the result header), the rows and their groups, the reference line, the interval, the axis maximum
Control:   the obvious alternative, as a row in the chart and as a crossed box in the task panel
Text:      every string that will appear in the image, listed
Caption:   as in SKILL.md section 3a: bold takeaway, 0-3 sentences on the finding, then how to interpret it
```

Draw it in HTML that links `_kit/story.css` and `_kit/story.js` (cell stacks for layers, icon arrays, and the result chart drawn from JSON in the page), plus `_kit/summary.js` for network cartoons. `examples/story_figure.html` is a whole figure with made-up content, and its comment holds the caption; render yours with `sh render_html.sh figure.html figure.png 1100 1740` (the script in the skill's directory), with your page's height in place of 1740. `examples/story_figure_check.md` records how a fresh reader read it.

Before anyone sees it, open the PNG and look at each panel at full size (crop it if the whole image is shrunk on screen) for overlaps, cut-off text and text that is too small.

**The test:** as for the summary figure, a fresh reader shown only the image says what was done and what was found. Also ask what the numbers at the bar ends count; if the reader cannot say, the result header is not doing its job. In the template's test, the reader's worst confusions were what one test case was and whether a trained method was trained on the held-out copy; state both in the image (the held-out count with its inputs per copy, and a line in the zoom).
