"""Probe accuracy by layer for four concepts, with the layer where each becomes decodable marked.

Claim: the four concepts become decodable at successively later layers (4, 9, 14 and 20 of 24).
Reads data.csv beside this script; writes figure.pdf and figure.png for one column (3.25 in) of a two-column paper.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

THRESHOLD = 0.75  # "decodable": accuracy at or above this from this layer to the last
LABEL_Y = {"part of speech": 0.86}  # labels sit left of each curve at this accuracy; default below
NAMES = {"part of speech": "part of\nspeech", "named entity type": "named\nentity type",
         "statement truthfulness": "statement\ntruthfulness"}

rows = defaultdict(list)
with open(HERE / "data.csv") as f:
    for r in csv.DictReader(f):
        rows[r["concept"]].append((int(r["layer"]), float(r["accuracy"]), float(r["ci_low"]), float(r["ci_high"])))
data = {c: np.array(sorted(v)).T for c, v in rows.items()}


def onset(acc):
    """Index of the first layer from which accuracy stays at or above THRESHOLD."""
    above = acc >= THRESHOLD
    return next(i for i in range(len(acc)) if above[i:].all())


def crossing(layer, acc, y):
    """Layer at which the curve first rises through accuracy y, by linear interpolation."""
    i = next(i for i in range(1, len(acc)) if acc[i] >= y > acc[i - 1])
    return layer[i - 1] + (y - acc[i - 1]) / (acc[i] - acc[i - 1])


concepts = sorted(data, key=lambda c: onset(data[c][1]))  # order by onset, so colours follow depth
fk.use(size="column")
fig, ax = plt.subplots()
ax.axhline(0.5, color=fk.MUTED, lw=0.8, ls=":", zorder=0)
for concept, color in zip(concepts, fk.CATEGORICAL):
    layer, acc, lo, hi = data[concept]
    ax.fill_between(layer, lo, hi, color=color, alpha=0.2, lw=0)
    ax.plot(layer, acc, color=color, lw=1.4)
    i = onset(acc)
    ax.plot(layer[i], acc[i], "o", color=color, ms=4, zorder=3)
    ax.annotate(f"{layer[i]:.0f}", (layer[i], acc[i]), xytext=(4, -2), textcoords="offset points",
                color=color, ha="left", va="top", fontweight="semibold")
    y = LABEL_Y.get(concept, 0.62)
    ax.annotate(NAMES.get(concept, concept), (crossing(layer, acc, y), y), xytext=(-4, 0),
                textcoords="offset points", color=color, ha="right", va="center", linespacing=1.0)
ax.set(xlabel="Layer", ylabel="Probe accuracy", xlim=(0, 23), ylim=(0.45, 1.0),
       xticks=[0, 4, 8, 12, 16, 20], yticks=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
fk.save(fig, HERE / "figure.pdf")
fk.save(fig, HERE / "figure.png")
