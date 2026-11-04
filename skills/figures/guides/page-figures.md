# Figures for a page: HTML, with a PNG rendered from the same file

Paths in this guide are relative to the figures skill's directory, the parent of this `guides/` folder (`${CLAUDE_SKILL_DIR}` in `SKILL.md`). Sections 1 to 6 of `SKILL.md` apply here too.

When a figure will live on an HTML page that can run scripts, draw it in HTML and SVG rather than matplotlib by default, unless your venue or page requires otherwise. There are two reasons. First, Claude's design judgment is much better in HTML and CSS. Second, a page can show details on demand. The static view stays clean, and the exact values, intervals, n, verdicts and identifiers appear on hover or click. That takes away the pull to print statistics in the image.

- Start from `examples/interactive_dots.html`. It has colour tokens for light and dark mode, the Inter font, D3 from a CDN, the data inline as JSON, a title, and a tooltip. Have your Python script write the data JSON into a copy of the file, and adapt `draw()`.
- The static view obeys `SKILL.md` sections 2 and 3. The tooltip, or a panel that opens on click, carries everything else.
- Give the chart `role="img"` and an `aria-label` with the data in words (the plan block's Alt line), as the examples do. A PNG on a page takes the same words as its alt text.
- Render the PNG for slides from the same file: `sh <skill directory>/render_html.sh figure.html figure.png 900 460`, where 900 and 460 are the size of the `.fig` box. Look at the PNG once, as in `SKILL.md` section 5. `fk.save`'s check doesn't run here, so apply its limits by eye: the title on one line, at most about 25 other words, no text under about 12 px.
