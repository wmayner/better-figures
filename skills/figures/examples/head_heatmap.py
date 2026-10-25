"""Heatmap: one cell per attention head, shaded from white to the accent colour, the few heads that matter named in
their cells.

Answers: Where in the model is the effect?
Shows: heatmap: the loss increase from ablating each of a 12-layer model's 144 attention heads
Claim: three heads, in layers 9 and 10, carry the effect.
Caption: **Only three heads, in layers 9 and 10, raised the loss by more than 0.1 nats when ablated.** Mean
increase in loss on the correct name when one head at a time is mean-ablated, over 500 indirect-object prompts;
heads are named layer.head. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
effect = rng.gamma(1.0, 0.008, (12, 12))  # nats; layer by head
for (layer, head), nats in {(9, 6): 1.30, (9, 9): 0.95, (10, 0): 0.70}.items():
    effect[layer, head] = nats
df = pd.DataFrame(effect, index=pd.Index(range(12), name="Layer"), columns=pd.Index(range(12), name="Head"))
big = [(l, h) for l in range(12) for h in range(12) if effect[l, h] > 0.1]

fk.use()
fig, ax = plt.subplots()
cmap = LinearSegmentedColormap.from_list("accent", ["#FFFFFF", fk.ACCENT])
sns.heatmap(df, cmap=cmap, vmin=0,
            linewidths=0.5, linecolor="#EEEEEE", cbar_kws={"label": "Loss increase (nats)", "shrink": 0.8},
            ax=ax)
for layer, head in big:  # each big head named in its cell, in white on dark cells and ink on light ones
    r, g, b, _ = cmap(effect[layer, head] / effect.max())
    ax.text(head + 0.5, layer + 0.5, f"{layer}.{head}", ha="center", va="center", fontweight="semibold",
            color="white" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.45 else fk.INK,
            fontsize=fk.SIZES["screen"]["min_pt"])
ax.invert_yaxis()  # layer 0 at the bottom
ax.tick_params(length=0)
ax.set_xticks(np.arange(0, 12, 2) + 0.5, range(0, 12, 2))
ax.set_yticks(np.arange(0, 12, 2) + 0.5, range(0, 12, 2), rotation=0)
ax.grid(False)
fk.title(fig, f"Only {len(big)} heads raised loss by more than 0.1 nats when ablated")
fk.save(fig, HERE / "head_heatmap.png")
