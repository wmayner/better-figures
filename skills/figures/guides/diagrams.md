# Diagrams of a method, pipeline or setup

Paths in this guide are relative to the figures skill's directory, the parent of this `guides/` folder (`${CLAUDE_SKILL_DIR}` in `SKILL.md`). Sections 1 to 6 of `SKILL.md` apply here too.

Don't draw these in matplotlib. Write HTML that links `_kit/diagram.css` (cards, pills, numbered steps, chevrons, accent and muted colours, Inter), and render it to a PNG:

```
sh <skill directory>/render_html.sh diagram.html diagram.png 1600 500   # width and height of .canvas
```

The same rules apply, in this form:
- Each box gets a bold name of at most 5 words and one grey line of at most 12 words.
- No legend.
- One accent colour for the thing the diagram is about.
- Red only for ablated or failed, green only for passed.
- One concrete running example (a real token or a real unit) that appears in every panel.
- The same symbol always means the same thing.
- A wide canvas, 2:1 to 3:1, or square to 4:3 for an image posted on its own.

See `examples/diagram.html`. For an illustrated explainer of how code computes something, step by step, use the method-explainer skill in this plugin.
