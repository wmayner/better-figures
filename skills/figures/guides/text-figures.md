# Figures made of text: token scores and replies

Paths in this guide are relative to the figures skill's directory, the parent of this `guides/` folder (`${CLAUDE_SKILL_DIR}` in `SKILL.md`). Sections 1 to 6 of `SKILL.md` apply here too.

For a score on every token (a probe, an attribution, an SAE latent's activation) or model replies side by side, write HTML that links `_kit/text.css` and loads `_kit/text.js`, and render it with `render_html.sh`.
- **Token scores** (`examples/token_scores.html`): one row per text, each token shaded on a diverging scale (blue below zero, the accent above), with the colour bar above the rows. Give each `.tokens` element its scores as `[[token, score], ...]` JSON in the `<script>` after it; `text.js` draws a token's leading space outside its shading, turns text white on dark shades, and shows the score on hover. Add a row that shows the contrast (the honest answer, the unsteered model), so the shading means something.
- **Replies side by side** (`examples/transcripts.html`): the prompt across the top, one card per condition, the intervention's card with the accent border, the phrase that matters in `.hl`, and an outcome dot (green for passed, red for failed) whose words stay in ink.
- Quote real outputs, cut with "…", never paraphrased. The title states the finding, as in `SKILL.md` section 3. Put the count on the card when you have one ("18/30 about the military", with the unsteered count beside it), and the caption says how the outputs were sampled.
