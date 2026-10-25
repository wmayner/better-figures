"""Probe accuracy by layer for four concepts, with the first layer each reaches 80% marked.

Claim: the four concepts become decodable at different depths, from part of speech
in the early layers to statement truthfulness near the top of the model.
Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples); saves figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

THRESHOLD = 0.8  # "decodable": the first layer whose probe accuracy reaches this
NAME_AT = 0.7  # accuracy at which each concept's name sits beside its curve
WRAPPED = {"part of speech": "part of\nspeech", "named entity type": "named\nentity type",
           "statement truthfulness": "statement\ntruthfulness"}

df = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])
first = {c: int(g.loc[g.accuracy >= THRESHOLD, "layer"].min()) for c, g in df.groupby("concept")}
order = sorted(first, key=first.get)  # concepts from earliest to latest

fk.use()
fig, ax = plt.subplots()
for concept, colour in zip(order, fk.CATEGORICAL):
    g = df[df.concept == concept]
    ax.fill_between(g.layer, g.ci_low, g.ci_high, color=colour, alpha=0.18, lw=0)
    ax.plot(g.layer, g.accuracy, color=colour, label=concept)
    hit = g[g.layer == first[concept]].iloc[0]
    ax.plot(hit.layer, hit.accuracy, "o", color=colour, ms=7, mec="white", mew=1.5, zorder=5)
    ax.annotate(f"layer {first[concept]}", (hit.layer, hit.accuracy), xytext=(-8, 4),
                textcoords="offset points", ha="right", va="bottom", color=colour, fontsize="small")
    # name the concept left of its own rise, in the gap before the previous curve
    x = float(np.interp(NAME_AT, g.accuracy.cummax(), g.layer))
    ax.annotate(WRAPPED.get(concept, concept), (x, NAME_AT), xytext=(-8, 0),
                textcoords="offset points", ha="right", va="center", color=colour)

ax.axhline(THRESHOLD, color=fk.MUTED, lw=1, ls=":", zorder=0)
ax.set(xlabel="Layer", ylabel="Probe accuracy", ylim=(0.45, 1), xlim=(0, df.layer.max()))

lo, hi = order[0], order[-1]
fk.title(fig, f"{lo.capitalize()} reaches 80% at layer {first[lo]}, truthfulness at layer {first[hi]}")
fk.save(fig, HERE / "figure.png", order=False)
print({c: first[c] for c in order})
