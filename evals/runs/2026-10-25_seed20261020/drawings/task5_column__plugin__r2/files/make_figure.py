"""Probe accuracy by layer for four concepts, for one column of a two-column paper (3.25 in wide).

Claim: the four concepts become decodable at successively deeper layers (4, 9, 14 and 20).
Reads data.csv beside this script; writes figure.pdf and figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

THRESHOLD = 0.75  # halfway between chance (0.5) and perfect accuracy
LABELS = {  # two-line names fit the gaps between the rises
    "part of speech": "part of\nspeech",
    "sentiment": "sentiment",
    "named entity type": "named\nentity type",
    "statement truthfulness": "statement\ntruthfulness",
}

df = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])
onset = {c: int(g.loc[g.accuracy >= THRESHOLD, "layer"].min()) for c, g in df.groupby("concept")}
concepts = sorted(onset, key=onset.get)  # shallowest first

fk.use(size="column")
fig, ax = plt.subplots()
ax.axhline(0.5, color=fk.MUTED, lw=0.8, ls=":", zorder=0)
for i, c in enumerate(concepts):
    g = df[df.concept == c]
    color = fk.CATEGORICAL[i]
    ax.fill_between(g.layer, g.ci_low, g.ci_high, color=color, alpha=0.18, lw=0)
    ax.plot(g.layer, g.accuracy, color=color, lw=1.5, label="_" + c)
    y0 = g.loc[g.layer == onset[c], "accuracy"].item()
    ax.plot(onset[c], y0, "o", color=color, ms=4, mec="white", mew=0.8, zorder=5)
    # Name each curve just right of its rise; the last has no room there, so it goes left of its lower rise.
    if i < len(concepts) - 1:
        ax.annotate(LABELS.get(c, c), (onset[c], y0), xytext=(5, -4), textcoords="offset points",
                    ha="left", va="top", color=color, fontsize=7, linespacing=1.0)
    else:
        x1 = int(g.loc[g.accuracy >= 0.6, "layer"].min())
        ax.annotate(LABELS.get(c, c), (x1, g.loc[g.layer == x1, "accuracy"].item()), xytext=(-5, 0),
                    textcoords="offset points", ha="right", va="center", color=color, fontsize=7, linespacing=1.0)

n_layers = df.layer.max()
ax.set(xlabel="Layer", ylabel="Probe accuracy", xlim=(0, n_layers), ylim=(0.45, 1.0),
       xticks=[0] + [onset[c] for c in concepts] + [n_layers], yticks=[0.5, 0.75, 1.0])
ax.set_yticklabels(["50%", "75%", "100%"])
fk.title(fig, "Each concept becomes decodable at a deeper layer")
fk.save(fig, HERE / "figure.pdf", order=False)
fk.save(fig, HERE / "figure.png", order=False)
