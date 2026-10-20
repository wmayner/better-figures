"""Line plot: one series highlighted, the rest grey, names at the line ends, no title.

Claim: a linear probe reads the sentence's tense from the residual stream from layer 6 on; the controls
stay near chance.
Caption (goes under the image, not in it): accuracy of a logistic-regression probe for past against present
tense, trained on 2,000 sentences and tested on 500 held-out ones, at each layer of a 24-layer model. The control
task uses random labels; the random model has the same architecture with untrained weights. Dotted line:
chance. Made-up data, drawn to show the style.
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
    ax.plot(layer, np.clip(y + rng.normal(0, 0.008, len(layer)), 0, 1), color=color, label=name)
ax.axhline(0.5, color=fk.MUTED, lw=1, ls=":", zorder=0)
ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(0.4, 1), xlim=(0, 24))
fk.label_lines(ax)
fk.save(fig, HERE / "line_direct_labels.png")
