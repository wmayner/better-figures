"""Dot plot of attribution–ablation agreement (Spearman ρ, 95% CI) per method and model.

Usage: python make_figure.py [data.csv] [figure.png]
"""

import sys

import matplotlib.pyplot as plt
import pandas as pd

DATA = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "figure.png"

# Models in order of size; color + marker follow the model, never its rank.
MODELS = ["GPT-2 small", "Pythia-410M", "Gemma-2-2B"]
COLORS = {"GPT-2 small": "#2a78d6", "Pythia-410M": "#eb6834", "Gemma-2-2B": "#1baf7a"}
MARKERS = {"GPT-2 small": "o", "Pythia-410M": "s", "Gemma-2-2B": "D"}

INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"

df = pd.read_csv(DATA)
missing = set(df["model"]) - set(MODELS)
assert not missing, f"unexpected models: {missing}"

# Best method (highest mean ρ across models) at the top.
order = df.groupby("method")["spearman_r"].mean().sort_values(ascending=False).index
n_heads = df.groupby("model")["n_heads"].first()

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 10,
    }
)
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

offsets = {m: o for m, o in zip(MODELS, (-0.22, 0.0, 0.22))}
for model in MODELS:
    sub = df[df["model"] == model].set_index("method").loc[order]
    y = [i + offsets[model] for i in range(len(order))]
    ax.hlines(y, sub["ci_low"], sub["ci_high"], color=COLORS[model], lw=2, zorder=2)
    ax.scatter(
        sub["spearman_r"],
        y,
        s=42,
        marker=MARKERS[model],
        color=COLORS[model],
        edgecolor=SURFACE,
        linewidth=1.2,
        zorder=3,
        label=f"{model} ({n_heads[model]} heads)",
    )

# Shade the winning row lightly so the answer reads first.
ax.axhspan(-0.45, 0.45, color="#f0efec", zorder=0, lw=0)

ax.set_yticks(range(len(order)))
ax.set_yticklabels(order, color=INK)
ax.invert_yaxis()
ax.set_ylim(len(order) - 0.5, -0.5)

ax.set_xlim(0, 1)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xlabel("Spearman ρ between attribution score and ablation effect (per head)", color=INK_2)
ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
ax.set_axisbelow(True)

for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
ax.tick_params(axis="x", colors=MUTED, length=0, pad=6)
ax.tick_params(axis="y", length=0, pad=8)

handles, labels = ax.get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="upper left",
    bbox_to_anchor=(0.01, 0.925),
    ncol=3,
    frameon=False,
    handletextpad=0.3,
    columnspacing=1.6,
    fontsize=9,
    labelcolor=INK_2,
)
fig.suptitle(
    "Integrated gradients agrees best with ablation in all three models",
    x=0.02,
    ha="left",
    fontsize=12,
    fontweight="bold",
    color=INK,
)

fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(OUT, facecolor=SURFACE)
print(f"saved {OUT}")
