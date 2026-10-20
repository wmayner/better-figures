"""Probe accuracy by layer for four concepts, with the layer where each becomes decodable marked.

Claim: the four concepts become decodable at successively deeper layers, from part of speech (layer 4)
to statement truthfulness (layer 20).
Onset = first layer where probe accuracy reaches ONSET (halfway between chance and perfect).
Usage: python make_figure.py [data.csv] [figure.png]
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import patheffects

sys.path.insert(0, "<repository>/skills/figures")
import figkit as fk

HERE = Path(__file__).resolve().parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "data.csv"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "figure.png"

CHANCE, ONSET = 0.5, 0.75
LABEL_Y = 0.43  # top of the concept names, below the chance line
WRAP = {"named entity type": "named entity\ntype", "statement truthfulness": "statement\ntruthfulness"}

df = pd.read_csv(src).sort_values(["concept", "layer"])


def onset_layer(g):
    above = g[g["accuracy"] >= ONSET]
    return above["layer"].iloc[0] if len(above) else None


# Order concepts by onset so colours and labels follow the shallow-to-deep sequence.
onsets = {c: onset_layer(g) for c, g in df.groupby("concept")}
order = sorted(onsets, key=lambda c: (onsets[c] is None, onsets[c]))
colors = dict(zip(order, fk.CATEGORICAL))

fk.use()
fig, ax = plt.subplots()
ax.axhline(CHANCE, color=fk.GREY, lw=1, ls=":", zorder=0)
ax.axhline(ONSET, color=fk.LIGHT, lw=1, zorder=0)

halo = [patheffects.withStroke(linewidth=4, foreground="white")]
for concept in order:
    g = df[df["concept"] == concept]
    c = colors[concept]
    ax.fill_between(g["layer"], g["ci_low"], g["ci_high"], color=c, alpha=0.15, lw=0)
    ax.plot(g["layer"], g["accuracy"], color=c, label=concept)
    L = onsets[concept]
    if L is None:
        continue
    y = g.loc[g["layer"] == L, "accuracy"].iloc[0]
    ax.plot(L, y, "o", color=c, ms=7, mec="white", mew=1.5, zorder=5)
    # Name each concept below its onset layer, joined to the marker by a thin drop line.
    ax.plot([L, L], [LABEL_Y + 0.01, y], color=c, lw=0.8, alpha=0.6, zorder=1)
    ax.text(L, LABEL_Y, WRAP.get(concept, concept), ha="center", va="top", color=c,
            linespacing=1.1, path_effects=halo, zorder=6)

ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(0.33, 1), xlim=(0, df["layer"].max()))
ax.set_xticks(range(0, df["layer"].max() + 1, 4))
ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
fk.save(fig, out)
