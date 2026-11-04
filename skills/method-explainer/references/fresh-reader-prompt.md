# The fresh reader

One subagent with no context reads only the image and tries to rebuild the method from it. It is the cheapest way to find where the figure fails a reader who doesn't share your context, because you cannot read your own figure without that context.

How to run it:
- Use the final render's pieces from `scripts/render_check.py` (or cut a render with `scripts/split_png.py`): `whole.png` for the layout and full-resolution pieces for the text.
- Start a new agent with the Agent tool (`subagent_type: general-purpose`; `model: opus`, or omit `model` to use the session's own). Never fork, and never reuse an earlier reader: either one carries context the real reader lacks.
- Give it the prompt below, filled in, and nothing else: not the page, not the caption, not the spec, not what you meant.
- Save its reply unedited in `checks/fresh-reader-<n>.md`, then triage it as SKILL.md step 8 says.
- Its reply can be delivered to the parent session instead of to you. If it hasn't arrived a few minutes after the reader finishes, look for it in the reader's transcript (`~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`), and say so in your report rather than waiting.

Describe the reader as the real one: what they know (the field's vocabulary? the paper? the library?) and what they don't (this code). Leave something out and the reader will flag it as unknown; put in more than the real reader knows and real gaps go unflagged.

A second round, when the first changed a step's structure, can add targeted questions about the panels that changed ("In step 4, which partition is selected, and why?"). In the worked example, such questions caught inconsistencies that the open questions missed.

What to expect, from the first test: the reader rebuilt all eight steps and recomputed numbers by hand, which found rounding errors no render inspection would. Its most useful findings were collisions of notation (a capital letter meaning both a unit and its ON state), quantities whose inputs appear nowhere in the image, and labels whose scope was ambiguous ("per connection cut" read as "for each cut"). Its suggested cuts were mostly declined, with reasons, because the brief asked for each search in full. It took about 15 minutes and 184,000 tokens. It also loaded the user's own instruction files (a user-level CLAUDE.md), so it is fresh to the figure but not to the user's conventions.

---

Thank you for reading this figure. It explains how a piece of software computes something, step by step, on one example. You are standing in for this reader: {reader description}. A page beside the figure will later say how things were measured and define what the image can't; your job is the image alone. Don't fill gaps with your own knowledge of the method: if you cannot work something out, say so plainly rather than guessing confidently.

Read `{dir}/whole.png` for the layout, then every piece in order, `{dir}/piece01.png` to `{dir}/piece{NN}.png`, at full resolution. Use only these images: open no other files and run no searches.

Reply with these parts, in order:
1. **The method, rebuilt.** For each step in the figure, in your own words: what goes in, what is computed, and what comes out, with the example's numbers where the figure gives them. Write this before rereading anything.
2. **The running example.** What it is, and what it shows at each step.
3. **Where you misread, guessed or got lost**, by panel. Quote the label and say what you needed at that point. Include anything that looks inconsistent between panels.
4. **Undefined terms.** Every term, symbol or acronym the figure never defines that this reader would not know.
5. **Names and marks that collide.** One word used for two things, two words for one thing, or one colour, line style or symbol with two meanings.
6. **The version.** Which version of the code or method does the figure show? Anything that made you unsure.
7. **Numbers.** Any number where you couldn't tell what it counts, what it is relative to, or whether it is computed or illustrative. Then redo by hand every worked calculation the figure prints, from the numbers as printed, and list each one that doesn't come out, with what you get.
8. **Hard to read.** Small text, overlaps, crowding, colours that look alike.
9. **At most five changes**, most important first. Don't suggest adding text unless a step cannot be followed without it.
{10. In a second round only: targeted questions about the panels that changed.}

Be blunt; the figure is meant to need work. Answer once and stop.
