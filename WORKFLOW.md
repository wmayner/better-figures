# Designing figures before the experiment runs

The skill makes a single figure readable. This file covers the other half: when figures are designed, who approves them, and how a set of them reaches a reader. It assumes you work with Claude in three phases: you agree on a task with it, it runs the task without you, and you review the result.

Most unreadable figures were never designed. Claude runs the experiment, then plots whatever came out, and the figure ends up showing every result because no one decided which result it was for. Designing the figures at the start fixes this, and it also improves the experiment: working backward from the most informative figure often shows which runs are needed and which are not.

## At the spec stage

1. **Decide what the set of experiments should show.** Keep to the fewest figures the result needs, and at most five. Results that don't earn a figure go in tables on the page.
2. **Write one plan block per figure** (section 1 of `SKILL.md`): the claim the figure argues, in one sentence; the template (bar, line, scaling law, calibration, diverging line, Pareto frontier, scatter, heatmap); the one comparison it shows; the one element in the accent colour; every string that will appear in the image; the caption; and a four-line sketch. Choose the template from the claim. If no template fits, the figure is trying to say two things, so split it.
3. **Approve the plan block, or a mock drawn from fake data.** Never approve a prose description of the encodings ("rows are methods by targets, filled against open markers, verdict in the margin"). It reads as simple and draws as a wall of marks. A mock from fake data is the best check, because you see the figure you will get.
4. **Nothing runs before the figures are approved**, not even a smoke test. Changing a figure after the results are in is fine, but the change is reported.

## When the results are in

1. **Draw the approved figures** with the skill. Fill in each claim from the actual results; if a result goes the other way, the claim says so.
2. **Report every figure that was dropped or changed**, and why.
3. **Save the PNG, a PDF, and the plotted data** next to each other, so a figure can be redrawn without rerunning anything.
4. **Publish the figures together on one page**, each with a caption of at most three sentences: what is plotted, how it was measured, n, and what the error bars are. The page holds the figures and their captions and nothing else. The figures are a deliverable in their own right, separate from any written report, which can show them too.

## What every figure must do

- It conveys one idea and shows only the comparison that idea needs.
- It stands on its own: a reader who missed the work can interpret it from the image and its caption. Definitions, statistics, n and verdicts go in the caption or on the page, not in the image.
- It is plain to read: axes labelled with units, names written next to the data instead of in a legend, and no variable names, internal shorthand or abbreviations the reader hasn't seen.

## A block for your CLAUDE.md

Paste this into your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md`) so the rules apply in every session.

```markdown
## Figures
- For any figure a person will read, use the `figures` skill.
- Design figures at the spec stage, before anything runs. Work backward from the most
  informative figure to the experiment that produces it.
- Each set of experiments gets at most five figures; fewer is better. Other results go in tables.
- Each figure argues one claim with one comparison, using a standard template (bar, line,
  scaling law, calibration, diverging line, Pareto frontier).
- I approve each figure as its plan block from the skill (claim, template, the comparison shown,
  every string in the image, caption) or as a mock drawn from fake data. A prose description
  of the encodings is not enough to approve.
- No experiment runs, not even a smoke test, before the figures are approved.
- Each figure stands on its own with a caption of at most three sentences. Definitions,
  statistics, n and verdicts go in the caption, not the image.
- Publish the figures together on one page, each with its caption. Report any figure that was
  dropped or changed after the results came in, and why.
```
