# spec.md skeleton

Write this before drawing, then keep it current after every step: after the figure is built, its strings and layout should be the ones in the PNG, and at any point another agent should be able to continue the work from this file and the folder. A reader of the spec, such as the code's author, should be able to check every claim in the figure from it. The first test's spec is a full example: `~/explainers/pyphi-ces/spec.md`.

```markdown
# {Title of the explainer}: spec

{Date written. One paragraph: what the figure explains, for whom, and where it may go.}

Files in this folder: {the figure's HTML, its PNG (size in pixels), page.html, data/, checks/}.

## Source of truth

- **Code.** {repository} at **{commit}** ({date}); {configuration drawn, for example "the defaults at this commit", and the settings that matter}. Read: {files and functions, in the order the example passes through them, as the call trace listed them}.
- **Entry points.** {Which call runs which steps, if more than one.}
- **Published version.** {The paper or release the method comes from, and where the code's defaults differ from it, if they do.}
- **Terms.** {The paper or glossary used for terms.}
- **The running example.** {What it is, why it was chosen, who else uses it.} Every number about it comes from {data/script.py → data/output.json}, which {reproduces published values X and Y}.

## Plan block

    Claim:    the one sentence the figure argues (for a method figure: what the method does, end to end)
    Title:    one line
    Steps:    the list, one line each, and why each is its own step
    Template: method diagram laid out as a tall story figure
    Example:  the running example, in one line
    Colours:  each actor and its colour; the trained or optimized colour; grey for unchanged or context
    Size:     width in px, rough height; rendered at 2x
    Text:     about how many words, and why that many
    Caption:  in page.html (figures skill, section 3a)
    Alt:      the aria-label of the figure; also the PNG's alt text on the page

Sketch, top to bottom: {one line per panel}

## Colours and marks

| Actor or mark | Colour or style | Where |
|---|---|---|

## Symbols and conventions

{Every symbol and typographic convention the figure uses, each with its one meaning. This list also goes on the page.}

## Panels

{For each step: its header (number, bold name, grey line, code file) and what it draws, in the order drawn.}

## Every string in the image

{The output of scripts/figure_strings.py after the last render, by panel, with the total word count.}

## Checks

- **Render inspection.** {What the piece-by-piece look found and what was fixed.}
- **Fresh reader.** {What it rebuilt correctly; each misreading and what changed; what was not changed and why. The reply is in checks/.}

## Where the code differs from the brief, the docs or the paper

{Numbered, and written as each is found, not at the end. Each: what the other source says, what the code does, file and line.}

## Page

{The artifact URL, and what the page holds.}

## Changes since {commit}

{Only for an update: dated, one item per change, with file and line, and what the figure does about it.}
```
