"""Agreement between attribution scores and ablation effects, per method and model.

Reads data.csv and writes figure.png.
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, "<repository>/skills/figures")
import figkit as fk

BEST = "integrated gradients"
MODELS = ["GPT-2 small", "Pythia-410M", "Gemma-2-2B"]

df = pd.read_csv("data.csv")
# Order methods by mean agreement across models, best at the top.
order = df.groupby("method")["spearman_r"].mean().sort_values().index.tolist()
ypos = {m: i for i, m in enumerate(order)}

fk.use()
fig, axes = plt.subplots(1, len(MODELS), figsize=(7, 3), sharex=True, sharey=True)
for ax, model in zip(axes, MODELS):
    for row in df[df.model == model].itertuples():
        color = fk.ACCENT if row.method == BEST else fk.GREY
        y = ypos[row.method]
        ax.plot([row.ci_low, row.ci_high], [y, y], color=color, lw=2.5,
                solid_capstyle="butt")
        ax.plot(row.spearman_r, y, "o", color=color, ms=5)
    ax.axvline(0, color=fk.LIGHT, lw=1, zorder=0)
    ax.set_title(model)
    ax.set_xlim(-0.08, 1.08)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels(["0", "0.5", "1"])
    ax.tick_params(axis="y", length=0)

axes[0].set_yticks(range(len(order)))
axes[0].set_yticklabels([m.capitalize() for m in order])
for label, method in zip(axes[0].get_yticklabels(), order):
    if method == BEST:
        label.set_color(fk.ACCENT)
        label.set_fontweight("bold")
axes[1].set_xlabel("Rank correlation with ablation effect")

fk.save(fig, "figure.png")
