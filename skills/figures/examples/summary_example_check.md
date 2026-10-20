# Fresh-reader test of summary_example.png

Each round, one new headless Claude Code session (Opus 5.5) with no context was given only the PNG, no caption, and asked: what was done, what was found, and what was unclear or could be read more than one way. The sessions used the isolation flags of `evals/harness.py`: no user settings, skills, plugins, MCP servers or memory, and only the Read tool. 20 October 2026.

Intended reading: on an indirect-object prompt, keeping only the three attention heads that attribution patching ranks highest, and ablating every other head, keeps the model's answer (Mary); keeping three random heads flips it to John.

Before the test, two changes were made: the prompt was drawn as a plain completion prompt rather than a User and Assistant exchange, since the task is a completion on a base model, and each network was redrawn as three layers of four heads, so that every circle is a head and none is an input or output unit.

## Round 1

Done: "Choose three heads. The network is drawn as 3 columns of 4 heads. In one row the three heads are picked by attribution; in the other they are picked at random. Ablate every other head. All other heads are crossed out, so only the three chosen heads stay active. Compare the answer."

Found: "With only the three attribution-chosen heads, the model still prefers Mary over John ... With three random heads, the preference flips and John wins clearly. ... attribution finds a small set of heads that is enough to keep the model's behavior on this task, and a random set of the same size is not."

Unclear: what the bars measure; whether the check means "still answers Mary" or "matches the full model"; measured or schematic; one random draw or many; how heads were ablated; what the orange lines between the attribution heads mean; "the figure doesn't say how the heads were scored."

Change: the stamp on the top row said "attribution", which doesn't name a method; it now says "attribution patching".

## Round 2

Done: "compares two ways of picking three attention heads in a network: attribution patching and random selection ... For each method, the three chosen heads are kept, every other head is ablated, and the model's output is compared with the full, unablated model."

Found: "the heads chosen by attribution patching are enough to reproduce the behaviour, and a random set of three is not."

Unclear: measured or illustrative, and which model; one prompt or many; one random draw; what the bars measure and what the check means; the ablation method; and "the heading 'Ablate every other head' could also be misread as 'ablate alternating heads'".

Change: the middle header now reads "Ablate all other heads".

## Round 3 (final image)

Done: "Three attention heads were chosen in two ways: with attribution patching, or at random. Every other head was ablated, and the model's output with only those three heads left was compared to the full model's output on the Mary vs. John bars."

Found: "attribution patching finds a small set of heads that is enough to keep the behaviour, and a random set of the same size is not."

Unclear: what the bars measure; zeroing, mean ablation or resampling; one prompt or many, one random draw or many; what the check means; whether the connections between the chosen heads matter, since the random heads are spread differently across layers; the real model's size.

All three readings got the setup and the finding right, and none read an input or output unit as a head. What remains unclear (what the bars measure, the ablation method, how many prompts and random draws, whether the figure is schematic) is what the caption answers. The caption also says that lines join chosen heads in adjacent layers and that the random row is one draw.
