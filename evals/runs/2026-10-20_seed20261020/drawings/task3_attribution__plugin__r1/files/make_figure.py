"""Dot plot: agreement between each attribution method and head ablation, per model."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit as fk

HERE = Path(__file__).resolve().parent
MODELS = ["GPT-2 small", "Pythia-410M", "Gemma-2-2B"]
OFFSET = {m: 0.22 * (1 - i) for i, m in enumerate(MODELS)}  # first model on top within a row

df = pd.read_csv(HERE / "data.csv")
# Best method at the top: order rows by mean correlation across models.
order = df.groupby("method")["spearman_r"].mean().sort_values().index.tolist()
best = order[-1]
row = {m: i for i, m in enumerate(order)}

fk.use()
fig, ax = plt.subplots(figsize=(7, 4))
for _, r in df.iterrows():
    y = row[r.method] + OFFSET[r.model]
    color = fk.ACCENT if r.method == best else fk.GREY
    ax.plot([r.ci_low, r.ci_high], [y, y], color=color, lw=1.5, solid_capstyle="butt")
    ax.plot(r.spearman_r, y, "o", color=color, ms=6)
    if r.method == best:  # name the models once, in the empty space left of the highlighted row
        x = df.loc[df.method == best, "ci_low"].min()
        ax.annotate(r.model, (x, y), xytext=(-8, 0), textcoords="offset points",
                    va="center", ha="right", color=fk.MUTED, fontsize=10)

ax.set_yticks(range(len(order)), order)
ax.get_yticklabels()[row[best]].set_color(fk.ACCENT)
ax.tick_params(axis="y", length=0)
ax.set(xlim=(0, 1), ylim=(-0.5, len(order) - 0.5),
       xlabel="Rank correlation with ablation effect (Spearman ρ)")
ax.grid(False)
ax.spines["left"].set_visible(False)

fk.save(fig, HERE / "figure.png")
