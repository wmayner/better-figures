"""Dot plot: agreement (Spearman rho) between each attribution method and head ablation."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

df = pd.read_csv("data.csv")

MODELS = ["GPT-2 small", "Pythia-410M", "Gemma-2-2B"]
COLORS = {"GPT-2 small": "#2a78d6", "Pythia-410M": "#eb6834", "Gemma-2-2B": "#1baf7a"}
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BF_THRESHOLD = 10  # below this, evidence for a nonzero correlation is weak

# Order methods best-to-worst by mean correlation across models.
order = df.groupby("method")["spearman_r"].mean().sort_values(ascending=False)
methods = list(order.index)
offsets = dict(zip(MODELS, [-0.22, 0.0, 0.22]))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

for i, method in enumerate(methods):
    if i % 2 == 0:
        ax.axhspan(i - 0.45, i + 0.45, color="#f1f0ed", zorder=0, lw=0)
    for model in MODELS:
        r = df[(df.method == method) & (df.model == model)].iloc[0]
        y = i + offsets[model]
        c = COLORS[model]
        ax.plot([r.ci_low, r.ci_high], [y, y], color=c, lw=2, solid_capstyle="round", zorder=2)
        weak = r.bayes_factor_10 < BF_THRESHOLD
        ax.scatter(r.spearman_r, y, s=46, zorder=3, linewidths=1.8,
                   facecolors=SURFACE if weak else c, edgecolors=c)
    ax.text(1.005, i, f"mean {order[method]:.2f}", va="center", ha="left",
            color=INK_2, fontsize=9, transform=ax.get_yaxis_transform())

ax.set_yticks(range(len(methods)))
ax.set_yticklabels(methods, color=INK)
ax.set_ylim(len(methods) - 0.5, -0.5)
ax.set_xlim(0, 1)
ax.set_xticks(np.arange(0, 1.01, 0.2))
ax.set_xlabel("Spearman ρ between attribution score and ablation effect (per head)", color=INK_2)
ax.tick_params(colors=INK_2, length=0)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=1)
for s in ax.spines.values():
    s.set_visible(False)

handles = [Line2D([], [], color=COLORS[m], marker="o", lw=2, ms=7, label=m) for m in MODELS]
handles.append(Line2D([], [], color=INK_2, marker="o", lw=0, ms=7, mfc=SURFACE, mew=1.6,
                      label=f"BF₁₀ < {BF_THRESHOLD}"))
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=4,
          frameon=False, fontsize=9, handletextpad=0.4, columnspacing=1.3, labelcolor=INK)
ax.set_title("Integrated gradients agrees best with ablation on every model",
             color=INK, fontsize=12, loc="left", x=-0.25, pad=30, fontweight="bold")

fig.tight_layout()
fig.savefig("figure.png", facecolor=SURFACE, bbox_inches="tight")
