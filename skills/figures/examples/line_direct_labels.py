"""Line plot: one series highlighted, the rest grey, names at the line ends.

Answers: How does a measure change over training, or across layers?
Shows: line plot with names at the line ends: probe accuracy by layer, against two controls
Claim: a linear probe reads the sentence's tense from the residual stream from layer 8 on; the controls
stay near chance.
Caption: **A linear probe reads tense above 90% accuracy from layer 8 on, and both controls stay near chance.**
Accuracy of a logistic-regression probe for past against present tense, trained on 2,000 sentences and tested on 500
held-out ones, at each layer of a 24-layer model. The control task uses random labels; the untrained model has the
same architecture with random weights. The dotted line is chance. Made-up data, drawn to show the style.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

rng = np.random.default_rng(0)
layer = np.arange(25)
trained = 0.5 + 0.45 / (1 + np.exp(-(layer - 5) * 0.9)) - 0.03 * np.clip(layer - 18, 0, None) / 6
curves = {
    "random labels": (0.5 + 0.04 * np.ones_like(layer, dtype=float), fk.GREY),
    "untrained model": (0.5 + 0.08 / (1 + np.exp(-(layer - 3))), fk.GREY),
    "trained model": (trained, fk.ACCENT),
}
fk.use()
fig, ax = plt.subplots()
for name, (y, color) in curves.items():
    y = np.clip(y + rng.normal(0, 0.008, len(layer)), 0, 1)
    ax.plot(layer, y, color=color, label=name)
    if name == "trained model":
        first = int(layer[np.argmax(y > 0.9)])  # the first layer above 90%
ax.axhline(0.5, color=fk.MUTED, lw=1, ls=":", zorder=0)
ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(0.4, 1), xlim=(0, 24))
fk.label_lines(ax)
fk.title(fig, f"A linear probe reads tense above 90% accuracy from layer {first} on")
fk.save(fig, HERE / "line_direct_labels.png")
