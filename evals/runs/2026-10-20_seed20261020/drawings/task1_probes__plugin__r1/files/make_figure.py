"""Probe accuracy by layer for four concepts, with the layer at which each becomes decodable marked.

Claim: the four concepts become decodable at successively deeper layers (part of speech, then sentiment,
then named entity type, then statement truthfulness).

Onset = the first layer whose 95% CI lower bound is above chance and stays above it at every later layer.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, "<repository>/skills/figures")
import figkit as fk

HERE = Path(__file__).resolve().parent
CHANCE = 0.5
YMIN = 0.45
# (layer, accuracy) of each name's left end: beside its curve's rise, clear of the neighbouring curves
NAME_XY = {"part of speech": (0.3, 0.96), "sentiment": (7.7, 0.65), "named entity type": (14.0, 0.72),
           "statement truthfulness": (18.9, 0.65)}
NAMES = {"statement truthfulness": "statement\ntruthfulness"}  # fits inside the last layers

d = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])


def onset(g):
    above = (g.ci_low > CHANCE).to_numpy()
    for i in range(len(above)):
        if above[i:].all():
            return g.layer.iloc[i]
    return None


onsets = {c: onset(g) for c, g in d.groupby("concept")}
order = sorted(onsets, key=lambda c: onsets[c])  # earliest first, so colours follow depth
for c in order:
    print(f"{c}: decodable from layer {onsets[c]}")

fk.use()
fig, ax = plt.subplots()
ax.axhline(CHANCE, color=fk.MUTED, lw=1, ls=":", zorder=0)
for c, color in zip(order, fk.CATEGORICAL):
    g = d[d.concept == c]
    ax.fill_between(g.layer, g.ci_low, g.ci_high, color=color, alpha=0.18, lw=0)
    ax.plot(g.layer, g.accuracy, color=color)
    on = g[g.layer == onsets[c]].iloc[0]
    ax.plot(on.layer, on.accuracy, "o", color=color, ms=7, mec="white", mew=1.5, zorder=5)
    ax.plot([on.layer, on.layer], [YMIN, on.accuracy], color=color, lw=1, ls=":", zorder=4)
    ax.text(*NAME_XY[c], NAMES.get(c, c), color=color, ha="left", va="center")

last = d.layer.max()
ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(YMIN, 1), xlim=(0, last))
# x ticks only at the onset layers, each in its concept's colour
ax.set_xticks([onsets[c] for c in order])
for t, color in zip(ax.get_xticklabels(), fk.CATEGORICAL):
    t.set_color(color)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
fk.save(fig, HERE / "figure.png")
