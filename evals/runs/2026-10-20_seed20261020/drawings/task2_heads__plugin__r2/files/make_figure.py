"""Heatmap of loss increase from ablating each attention head (layer x head)."""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, "<repository>/skills/figures")
import figkit as fk

N_TOP = 3  # heads whose values are printed in their cells

df = pd.read_csv("data.csv")
grid = df.pivot(index="layer", columns="head", values="loss_increase")
n_layers, n_heads = grid.shape

fk.use()
fig, ax = plt.subplots(figsize=(6, 5))
cmap = LinearSegmentedColormap.from_list("accent", ["white", fk.ACCENT])
# Clip at 0: negative values are all within noise (smallest is about -0.02).
vmax = grid.values.max()
im = ax.imshow(grid.values, cmap=cmap, vmin=0, vmax=vmax, aspect="equal")

# Thin cell borders so near-zero cells still read as a grid.
ax.set_xticks(np.arange(-0.5, n_heads), minor=True)
ax.set_yticks(np.arange(-0.5, n_layers), minor=True)
ax.grid(which="minor", color=fk.LIGHT, linewidth=0.5)
ax.grid(which="major", visible=False)
ax.tick_params(which="minor", length=0)
for s in ax.spines.values():
    s.set_visible(False)

ax.set_xticks(range(n_heads))
ax.set_yticks(range(n_layers))
ax.set(xlabel="Head", ylabel="Layer")

for _, r in df.nlargest(N_TOP, "loss_increase").iterrows():
    ax.text(r["head"], r["layer"], f"{r.loss_increase:.2f}", ha="center", va="center",
            color="white" if r.loss_increase > 0.7 * vmax else fk.INK,  # keep contrast on paler cells
            fontsize=10, fontweight="bold")

cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.03)
cb.set_label("Loss increase")
cb.outline.set_visible(False)

fk.save(fig, "figure.png")
