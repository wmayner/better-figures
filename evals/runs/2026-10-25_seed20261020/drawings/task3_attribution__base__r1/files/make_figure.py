"""Dot plot: agreement between each attribution method and head ablation.

Reads data.csv, writes figure.png.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent

# Reference palette (light mode), categorical slots 1-3 in fixed order.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MODEL_COLORS = {
    "GPT-2 small": "#2a78d6",
    "Pythia-410M": "#eb6834",
    "Gemma-2-2B": "#1baf7a",
}
MODEL_MARKERS = {"GPT-2 small": "o", "Pythia-410M": "s", "Gemma-2-2B": "D"}

df = pd.read_csv(HERE / "data.csv")
models = list(MODEL_COLORS)
n_heads = df.groupby("model")["n_heads"].first()

# Order methods by mean correlation across models, best on top.
order = df.groupby("method")["spearman_r"].mean().sort_values()
methods = list(order.index)
ypos = {m: i for i, m in enumerate(methods)}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 10,
})
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

offsets = {m: d for m, d in zip(models, (0.22, 0.0, -0.22))}
for model in models:
    sub = df[df["model"] == model]
    y = sub["method"].map(ypos) + offsets[model]
    ax.hlines(y, sub["ci_low"], sub["ci_high"], color=MODEL_COLORS[model],
              lw=2, capstyle="round", zorder=2)
    ax.scatter(sub["spearman_r"], y, s=46, marker=MODEL_MARKERS[model],
               color=MODEL_COLORS[model], edgecolor=SURFACE, linewidth=1.5,
               zorder=3, label=f"{model} ({n_heads[model]} heads)")

# Mean across models, printed to the right of each method's row.
for m in methods:
    ax.text(1.02, ypos[m], f"{order[m]:.2f}", va="center", ha="left",
            color=INK, fontsize=10, transform=ax.get_yaxis_transform())
ax.text(1.02, len(methods) - 0.3, "mean ρ", va="center", ha="left",
        color=MUTED, fontsize=9, transform=ax.get_yaxis_transform())

ax.set_yticks(range(len(methods)))
ax.set_yticklabels([m.capitalize() for m in methods], color=INK)
ax.set_ylim(-0.6, len(methods) - 0.15)
ax.set_xlim(0, 1)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xlabel("Spearman ρ between attribution scores and ablation effect",
              color=INK_2)
ax.tick_params(axis="x", colors=MUTED, labelcolor=INK_2, length=0)
ax.tick_params(axis="y", length=0, pad=8)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
# Faint separators between method rows.
for i in range(len(methods) - 1):
    ax.axhline(i + 0.5, color=GRID, lw=0.6, zorder=0)

fig.suptitle("Integrated gradients agrees best with ablation on all three models",
             x=0.02, y=0.975, ha="left", color=INK, fontsize=11.5,
             fontweight="semibold")
leg = fig.legend(loc="upper left", bbox_to_anchor=(0.012, 0.925), ncol=3,
                 frameon=False, fontsize=9, handletextpad=0.3,
                 columnspacing=1.4)
for t in leg.get_texts():
    t.set_color(INK_2)

fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(HERE / "figure.png", facecolor=SURFACE)
