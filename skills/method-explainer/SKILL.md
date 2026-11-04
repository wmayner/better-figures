---
name: method-explainer
description: Make an illustrated explainer of how code computes something - one tall figure that follows a single real example through every step of a method, algorithm or pipeline, drawn from the code at a pinned commit, with every number about the example computed by saved scripts, published on a page that carries the explanation. Use whenever someone asks for an illustrated explainer, a method figure or method diagram, an algorithm walkthrough, a visual step-by-step of what a library or repository does, or "a figure that shows how X works", even if they don't say "explainer". Also use when handing such a figure to a subagent (there is a brief template), and when updating an explainer after the code changed. Not for plots of results or dashboards.
---

# Method explainer

The goal is a figure that lets a reader who knows the field, but not this code, follow what the code does to one real example, step by step, and check every number. The code's authors are a second reader: they should be able to find each step in their code and find nothing wrong.

The method comes from an explainer of a collaborator's unpublished method, which its reader liked a lot; that figure can't ship with this public plugin. What made it work, in order of importance:
- the code at a stated commit was read in full, and the code won wherever the brief, the docs or the paper disagreed;
- one real example ran through every step, and scripts saved beside the figure computed every number about it;
- the spec, with every string in the image, was written before drawing;
- each step got the space its explanation needs, not the space its importance to the results would suggest;
- the explanation went on the page beside the figure; the image held drawn things, real content, formulas and short labels;
- one fresh reader, given only the image, tried to rebuild the method, and what it misread was fixed.

To delegate the figure to a subagent, fill in `references/brief-template.md` and hand it over; the subagent then follows this file. `LESSONS.md` records what each test of this skill changed and why.

## Output

```
<name>/
  spec.md          source of truth, plan block, panels, every string, checks, where the code differs, artifact URL
  data/            scripts that compute every number about the example, and their JSON outputs
  _kit/            the figures skill's kit, copied
  <name>.html      the figure
  <name>.png       its render at 2x
  page.html        the published page: figure, caption, notes
  checks/          each fresh reader's reply, unedited
  briefs/          the brief, if one was given
```

## Keep the work in files

The task is long: reading the code alone can fill a 200,000-token context. After each step, bring `spec.md` up to date so that another agent could continue from the folder alone. Never keep a list (disagreements, fixes, open questions) in your head for the end. Look at render pieces one or two at a time. Run on the model with the longest context available.

## Steps

**1. Load what you build on.** Load the figures skill (`better-figures:figures`), which ships in this plugin: its directory is `${CLAUDE_SKILL_DIR}/../figures`, the `${CLAUDE_SKILL_DIR}` it mentions. Read its sections 1, 3 and 3a and its guides `story-figure.md`, `summary-figure.md` and `diagrams.md`, copy its kit into `_kit/` as it says, and look at `examples/story_figure.png` and `examples/diagram.png`. Load the field's terminology source if one exists (a glossary, the paper, a domain skill). Keep scratch files in a folder named for this explainer (`<scratchpad>/<name>/`): a session's scratchpad is shared by every agent in it.

**2. Pin the source of truth.** Record the repository, the commit hash and date, and the configuration the run depends on. Read with `git show` or from the working tree, and run the project's own environment; never edit, commit, check out or push in the code's repository.
- **Read every function the example passes through**, in full, not only docstrings and docs. To find them, run the example once under a call tracer (in Python, `sys.setprofile` recording each function's file and line).
- **The code wins.** Wherever the brief, the docs or the paper disagree with the code, draw what the code does. Write each disagreement, and each error in the code's own docs, into `spec.md` with file and line as soon as you find it.
- **Published versions.** If the code's defaults differ from a published version of the method, draw the defaults, and say on the page what the published version gives and how to reproduce it.
- **Entry points.** If the code runs the method through several calls whose order differs from the method's, draw the method's order and say in one line under the title which call runs which steps.

**3. Choose one running example.** Small enough to compute in seconds and draw whole; big enough that every step does something. Prefer one the authors already use (the paper's figure, the docs' worked example, a collaborator's figure), so readers can check one against the other, and say so on the page.

**4. Compute every number with saved scripts.** Every number, token, list and label about the example comes from a script in `data/` that calls the project's own code, not a reimplementation, and writes JSON with the commit and configuration in it. The script asserts the configuration, and that it reproduces any published values and any values the brief quotes. Isolated seeds for anything random; never overwrite an output (add `_v2`); heavy jobs go to the cluster's scheduler. The figure embeds the JSON and writes its numbers from it, so it cannot drift from the scripts. Anything drawn but not computed is labelled "illustrative" in the image.

Readers redo worked formulas by hand, so each must come out from its operands as printed: print operands to about four significant digits and small values to three (0.0405, not 0.040), and have the figure's script check each worked line against the computed value and refuse to draw if they disagree.

**5. Write the spec before drawing.** Use `references/spec-template.md`. Settle in it:
- **Steps.** One per operation the reader must understand, in the order the computation runs. Size each by what its explanation needs. A path that is simple but different in kind gets its own step, at the same level of detail as the others, even when it matters less to the results: the point is to help the reader understand what is being done.
- **Step headers.** A number, a bold name of at most 4 words, one grey line of at most about 15 words saying what the step does, and the code file (or `file:function`) in small grey type at the right, so the code's authors can find it.
- **Colours and marks.** One colour per actor, fixed across every panel; one colour, and only one, for anything trained or optimized; grey for parts unchanged or only context; green and red only for passed and failed, unless the field has its own convention (IIT colours cause vermilion and effect green), which wins, with the reason on the page. No colour, line style or symbol means two things.
- **Names and notation.** One name per thing, everywhere: two words for one object, or one word for two, is the misreading fresh readers report most. The same holds for symbols and typographic conventions (a capital letter that means both a unit and its ON state; one symbol for a past state in one step and a future state in the next). List every symbol and convention with its one meaning, keep the list on the page, and where the paper's own notation collides, resolve it with one visible convention stated in the key.
- **The top.** The title says what the method does, in one line. A grey line under it names the code drawn ("The code as of <repo> <commit>, <date>"). A key names each colour and mark.
- **Every string** that will appear in the image.

**6. Draw, render, inspect.** Build the figure in HTML from the kit (`story.css` for the tall layout, `summary.css` and `summary.js` for cartoons, `diagram.css` for boxes and arrows), about 1200 px wide and as tall as it needs, inside one element with `id="figure"`. Run `scripts/render_check.py` on it: it renders at 2x at the figure's own height with the figures skill's `render_html.sh`, cuts the render into full-resolution pieces and one crop per panel, and reports each panel's position, anything past the right edge, and text under 12 px. Fix what it reports, then look at every piece for overlaps, cut-off text and crowding. Run `scripts/figure_strings.py`, paste its output into the spec, and act on its paragraph check. Render again until a piece-by-piece look finds nothing.

Then check every label against the code once more, step by step, with file and line, before anyone else reads the figure. A draft states rules more broadly than the code does.

**7. Put the explanation on the page, not in the image.** The image carries what the eye needs to follow the computation: drawn objects, the example's real content and numbers, each step's formula, and short labels. It can hold far more words than a results figure (the figure this method comes from has about 2,200), but no paragraphs and no sentence that says why. The page carries the caption (figures skill, section 3a), then notes: where the example comes from and what is computed or illustrative; the list of symbols; per-step notes where a step needs a caveat, a definition or a shortcut explained; what is not drawn and why; the code's names for the paper's terms; and where the code differs from the paper, docs or brief. Notes about other versions of the code (pending changes, older behaviour) go on the page; in the image they make readers unsure which version is drawn.

**8. One fresh-reader round.** Start one subagent with no context and the prompt in `references/fresh-reader-prompt.md`, on the final render's pieces. Save its reply unedited in `checks/fresh-reader-1.md`, and read it yourself. For each finding:
- a misreading: change the drawing or the label, since the next reader will misread it too;
- a term or symbol not defined: define it on the page, or replace it with plain words in the image if that is shorter;
- a worked calculation that doesn't come out: fix the printed digits (step 4);
- a request for more text in the image: usually decline, and put the answer on the page;
- a factual claim about the method: check it against the code before acting.

Record in the spec what the reader found, what changed, and what did not change and why. Run a second round only if the first changed the structure of a step.

**9. Publish.** Before writing the page, follow the Artifact tool's own instructions for a new page (its `quickstart` action, which carries the design guidance; or the `artifact-design` skill where there is no quickstart). Put the figure on its page at its drawn width, on a white plate that scrolls sideways on narrow screens, so its text is never shrunk; the PNG's alt text is the plan block's Alt line. Publish privately with the Artifact tool (icon "diagram"). The tool publishes only files under the session's working directory or scratchpad, so for a folder elsewhere, publish a copy from the scratchpad. Record the URL in `spec.md`. Don't send it to anyone; the person who asked decides who sees it.

## Updating an explainer after the code changed

Keep the design and the running example, and change only what the code now does differently. Before overwriting, copy the figure's HTML, PNG and page to names ending in the old commit (`<name>_<commit>.html`). Verify each reported change in the code (`git diff <old> <new>`), not from a changelog or a brief. Add a dated "Changes since <commit>" section to the spec, one item per change with file and line and what the figure does about it. Republish to the same artifact URL, reading it first. If the changes are big enough that the old layout would mislead, say so and propose a new layout instead of forcing it.

## Files

- `references/brief-template.md`: the brief an orchestrator fills in for a subagent, and how to run it.
- `references/spec-template.md`: the skeleton of `spec.md`.
- `references/fresh-reader-prompt.md`: the fresh reader's prompt, how to describe the reader, and what to expect.
- `scripts/render_check.py`: renders the figure at its own height, cuts it into pieces and checks its layout (`uv run --with pillow python render_check.py FIGURE.html OUT_DIR`).
- `scripts/split_png.py`: cuts any render into full-resolution pieces (`uv run --with pillow python ...`).
- `scripts/figure_strings.py`: lists every string in the rendered figure by panel, with word counts and a paragraph check.
- `LESSONS.md`: what each test of this skill changed, and why.
