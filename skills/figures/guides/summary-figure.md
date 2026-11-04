# The summary figure (Figure 1)

Paths in this guide are relative to the figures skill's directory, the parent of this `guides/` folder (`${CLAUDE_SKILL_DIR}` in `SKILL.md`). Sections 1 to 6 of `SKILL.md` apply here too.

By default, the first figure of a post, deck, update or paper about a result is a summary figure, unless your venue or page requires otherwise. It shows the idea, the method and the result at once, with concrete examples and cartoons and almost no prose, so that a busy reader who looks at nothing else still knows what was done and what was found. It comes before any plot; quantitative results go in the figures after it.

When the result is a comparison of several methods, and the chart cannot be read without seeing the task and how the methods differ, use the story figure (`guides/story-figure.md`) instead: it draws the same kind of examples and cartoons, and puts the chart in the middle of them.

The grammar comes from the first figures of five papers from Owain Evans's group, listed in `references/README.md` with notes on what each does well. Before drawing, look at `examples/summary_example.png`, and at one of the five pages in `references/fetched/` if that folder exists (`sh references/fetch-references.sh` downloads them from arXiv, for personal use). A figure from How to Catch an AI Liar also ships in `references/`; it shows how to draw chat bubbles and a classifier, not a layout to copy.

Rules:
- **Two to four panels, laid out in one of two ways.** Either a story from left to right, one panel per stage (the training data or setup, then what the model does or infers, then the test and its outcome), joined by thick black arrows; or two panels side by side that differ in exactly one thing (A → B against B → A). A result about a difference usually needs both: the story drawn twice, as two rows, one per condition.
- **Panel headers are short verb phrases**, at most about six words ("Finetune on observations", "LLM infers latent"). They carry no jargon that the image has not shown.
- **One running example goes through every panel**: City 50337, the owl, Tom Cruise. Bold it inside the text where it appears.
- **Concrete examples carry the content.** Real User and Assistant exchanges in boxes with role labels, or a base model's prompt in a box without them; for interpretability, a real token, a real unit or a planted circuit. Show two or three examples and a "..." for the rest of a dataset.
- **Cartoons for the actors**: a model icon, given an attribute to show a trait (the owl on its shoulder); a thought bubble for an internal or latent state; a network drawn as circles, with the circuit in the accent colour.
- **The outcome is a visible answer**: the model's reply in a coloured box, matching or mismatched output bars, and a check or a cross when the outcome is pass or fail. Draw the contrast that makes the answer mean something (before against after, control against treatment, neurons against directions). Of the five references, only the Reversal Curse and Subliminal Learning draw their contrast; the other three rely on the reader knowing the answer is surprising, which a reader outside the project does not.
- **A title is optional**: one line above the panels stating the finding, as in `SKILL.md` section 3. None of the five references has one, because their papers' captions do that job; a figure posted on its own may need it.
- **No prose outside the examples, and almost no numbers.** None of the five references prints a result number. Two kinds are allowed. A real model output on an example card may carry its count, with the control's count beside it ("18/30 about the military", "0/600 for random pairs"), which answers "is this cherry-picked?" where the reader is looking. And one before-and-after may be two large numbers with an arrow ("25% → 32%"), with the control beside it. No other numbers. (A story figure does print its result's numbers, in the result panel only.) The caption follows `SKILL.md` section 3a: the bold takeaway, up to three sentences on the finding, then what a reader needs to interpret it.
- Keep the diagram rules of `guides/diagrams.md`: one accent colour for the thing the figure is about, red only for ablated or failed, green only for passed, a wide canvas.

Plan it before drawing, as in `SKILL.md` section 1:

```
Idea:      the finding in one sentence (this becomes the caption's bold first sentence)
Example:   the one running example that appears in every panel
Layout:    story (left to right) | contrast (side by side) | story in two rows, one per condition
Panels:    for each, the header (a verb phrase of at most 6 words) and what it shows
Contrast:  the two conditions whose outcomes differ
Outcome:   how the answer is shown (reply box, output bars, check and cross)
Text:      every string that will appear in the image, listed
Caption:   as in SKILL.md section 3a: bold takeaway, 0-3 sentences on the finding, then how to interpret it
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
