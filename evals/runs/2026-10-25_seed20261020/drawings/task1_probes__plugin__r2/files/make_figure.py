"""Probe accuracy by layer for four concepts, with the layer where each first reaches 80% marked.

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples) beside this script and saves figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))  # the project's copy of the kit
import figkit as fk

THRESHOLD = 0.8  # "decodable": the first layer where probe accuracy reaches this
LABEL_Y = 0.75   # each concept's name sits just left of its curve at this accuracy
NAMES = {"part of speech": "part of\nspeech", "named entity type": "named entity\ntype", "statement truthfulness": "statement\ntruthfulness"}

df = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])


def onset(g):
    above = g[g["accuracy"] >= THRESHOLD]
    return int(above["layer"].iloc[0]) if len(above) else None


onsets = {c: onset(g) for c, g in df.groupby("concept")}
order = sorted(onsets, key=lambda c: (onsets[c] is None, onsets[c] or 0))  # earliest first

fk.use()
fig, ax = plt.subplots()
for concept, col in zip(order, fk.CATEGORICAL):
    g = df[df["concept"] == concept]
    ax.fill_between(g["layer"], g["ci_low"], g["ci_high"], color=col, alpha=0.18, lw=0)
    ax.plot(g["layer"], g["accuracy"], color=col, label=concept)
    if onsets[concept] is not None:
        row = g[g["layer"] == onsets[concept]].iloc[0]
        ax.plot(row["layer"], row["accuracy"], "o", color=col, ms=7, mec="white", mew=1.5, zorder=5)
        ax.annotate(str(onsets[concept]), (row["layer"], row["accuracy"]), xytext=(-8, 4), ha="right", va="bottom",
                    textcoords="offset points", color=col, fontweight="bold")
    rising = g[g["layer"] <= g.loc[g["accuracy"] >= LABEL_Y, "layer"].iloc[0]].tail(2)  # the segment crossing LABEL_Y
    x = np.interp(LABEL_Y, rising["accuracy"], rising["layer"])
    ax.annotate(NAMES.get(concept, concept), (x, LABEL_Y), xytext=(-8, 0), textcoords="offset points",
                ha="right", va="center", color=col, linespacing=1.1)

ax.axhline(0.5, color=fk.MUTED, lw=1, ls=":", zorder=0)
ax.axhline(THRESHOLD, color=fk.MUTED, lw=0.8, ls="--", zorder=1)
ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(0.45, 1), xlim=(0, df["layer"].max()))

first, last = order[0], order[-1]
fk.title(fig, f"{first.capitalize()} is decodable from layer {onsets[first]}, {last} from {onsets[last]}")
fk.save(fig, HERE / "figure.png")
