"""Heatmap of the loss increase from ablating each attention head, with the heads that matter named in their cells.

Claim: three heads, 9.6, 9.9 and 10.0, carry almost all of the effect.
Reads data.csv (layer, head, loss_increase, sem, n_prompts) and saves figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

THRESHOLD = 0.1  # nats; heads above this are named in their cells

df = pd.read_csv(HERE / "data.csv")
grid = df.pivot(index="layer", columns="head", values="loss_increase")
n_layers, n_heads = grid.shape
big = df[df["loss_increase"] > THRESHOLD].sort_values("loss_increase", ascending=False)
vmax = grid.values.max()

fk.use()
fig, ax = plt.subplots()
cmap = LinearSegmentedColormap.from_list("accent", ["#FFFFFF", fk.ACCENT])
sns.heatmap(grid.rename_axis("Layer").rename_axis("Head", axis=1), cmap=cmap, vmin=0, vmax=vmax,
            linewidths=0.5, linecolor="#EEEEEE", cbar_kws={"label": "Loss increase (nats)", "shrink": 0.8},
            ax=ax)
for row in big.itertuples():  # each big head named layer.head, white on dark cells and ink on light ones
    r, g, b, _ = cmap(row.loss_increase / vmax)
    ax.text(row.head + 0.5, row.layer + 0.5, f"{row.layer}.{row.head}", ha="center", va="center",
            fontweight="semibold", fontsize=fk.SIZES["screen"]["min_pt"],
            color="white" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.45 else fk.INK)
ax.invert_yaxis()  # layer 0 at the bottom
ax.tick_params(length=0)
ax.set_xticks(np.arange(0, n_heads, 2) + 0.5, range(0, n_heads, 2))
ax.set_yticks(np.arange(0, n_layers, 2) + 0.5, range(0, n_layers, 2), rotation=0)
ax.grid(False)
fk.title(fig, f"Only {len(big)} of {len(df)} heads raised loss by over {THRESHOLD:g} nats")
fk.save(fig, HERE / "figure.png")

