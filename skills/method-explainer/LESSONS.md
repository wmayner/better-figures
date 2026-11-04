# Lessons from the tests of this skill

## First test: how PyPhi computes an IIT 4.0 Φ-structure (3 November 2026)

**The test.** An orchestrator filled in the brief template and handed it to a subagent: an explainer of how PyPhi (commit 134a8f31) computes the Φ-structure of the IIT 4.0 paper's Fig 1A network, from the substrate's TPM through φ_s and the complexes to the distinctions, relations and Φ. Everything is in `~/explainers/pyphi-ces/` (both briefs, `spec.md`, the data scripts, the figure, the fresh reader's reply, the page), published privately at https://claude.ai/artifact/PCBYkS4EjVwz8EsZLUFzTx.

**What worked and stays.** A spec detailed enough that a second agent could finish the work from it. A data script that asserted the configuration, the brief's numbers and the paper's published values before anything was drawn. One real example through all eight steps. A fresh reader that rebuilt every step and gave findings specific enough to act on, and a worker that fixed most of them and recorded why it declined the rest.

**What changed in the skill, and why.**

| What happened | Change |
|---|---|
| The first worker, started with `model: opus` (a 200,000-token window), ran out of context while drawing; reading about 10,000 lines of code filled most of it. Its list of disagreements with the code, kept for the end, was lost. A second worker on the session's 1M-context model finished in an hour and about 760,000 tokens. | New section "Keep the work in files"; step 2: write each disagreement into the spec when found; brief template: omit the `model` override, expect one to two hours. |
| The worker found which functions to read by running the example under a call tracer (417 functions for one call). | Step 2. |
| `pyphi.analyze` analyzes one given candidate and never searches for complexes; `Substrate.complexes` searches and unfolds nothing. | Step 2: draw the method's order and say which call runs which steps. |
| Three steps opened with paragraphs of 37 to 60 words, against the rule. | `figure_strings.py` flags text blocks over 25 words; it also now separates table cells, which it used to run together. |
| The fresh reader redid the worked formulas by hand: nine were one unit off in the last digit and one 10% off, from rounding, which also hid a 0.0016 gap between two candidates. | Step 4: print operands to four significant digits and small values to three, and have the figure check each worked line. The fresh-reader prompt asks for the hand check. |
| Notation collided: a capital letter meant both a unit and its ON state; s̄ meant a past state in one step and a future state in the next; a dashed line meant both a cut and a boundary. The rule covered names only. | Step 5 covers symbols, line styles and typographic conventions, with a list of symbols on the page. |
| The second worker's recheck of every step against the code found a rule the draft stated for both sides that holds for one. | Step 6: check every label against the code once more before the fresh reader. |
| IIT colours cause vermilion and effect green; the figures skill keeps green for "passed". | Step 5: a field's own colour convention wins, with the reason on the page. |
| The worker wrote its own helpers to render at the figure's height, crop one panel, and find overflow and small text; it caught a table overflow only by eye. `figure_strings.py` ran table cells together and listed band headers under the panel before them. | New `scripts/render_check.py` (render, pieces, one crop per panel, overflow, small text); `figure_strings.py` separates cells and skips empty panels, and its docstring says to give bands their own `data-panel`. |
| The skill said to load `artifact-design`; the Artifact tool says to call its `quickstart` first. The tool also publishes only files under the working directory or scratchpad. | Step 9 defers to the tool's own instructions, and says to publish a copy from the scratchpad and record the URL. |
| The session's scratchpad is shared by every agent; the worker wrote into another agent's folder by mistake. | Step 1: a scratch folder named for the explainer. |
| Reports went to the wrong place: the worker's final report went to another agent name, and a retrieval report came back to the parent session; both arrived much later, relayed. | Brief template and fresh-reader reference: where a subagent's transcript is, and to say so rather than wait when a report doesn't arrive within a few minutes. |
| The fresh reader loaded the user's own CLAUDE.md, so it is fresh to the figure but not to the user's conventions. "The strongest model" for it was ambiguous. | Noted in the fresh-reader reference, which now names the model. |
| The fresh-reader prompt was written before the worked example's own prompt was found. That prompt also asked for the running example in the reader's words, what was hard to read, at most five changes, and "say so plainly rather than guessing confidently. Answer once and stop."; its second round added targeted questions about specific panels, which caught inconsistencies. | Merged into `references/fresh-reader-prompt.md`; the original request and feedback, in the reader's own words, are in the worked example, which is kept outside this public plugin. |

**Kept in the brief template from the orchestrator's brief:** running the example once first and quoting its numbers; naming the few terminology documents that matter rather than a domain skill's whole reading list; saying which configuration to draw when the code's defaults differ from the published method.

**Open for the next test.** The figure is long (5,252 px, about 2,800 words counting table cells) because the brief asked for each search in full; whether that density suits a reader who wants the gist is untested. A test on a different kind of code (a training pipeline, or an algorithm with no paper behind it) would show which rules are general.
