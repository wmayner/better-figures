"""Dot plot: for each attribution method, its rank correlation with ablation on each of three models, with 95%
intervals. The best method is in the accent colour and its three models are named once."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

df = pd.read_csv(HERE / "data.csv")
models = list(dict.fromkeys(df.model))  # file order, the same within every method
order = list(df.groupby("method").spearman_r.mean().sort_values().index)  # bottom to top, best on top
best = order[-1]
others_max = df[df.method != best].spearman_r.max()
best_min = df[df.method == best].spearman_r.min()
assert best_min > others_max, "the title claims the best method wins on every model"

fk.use()
fig, ax = plt.subplots()
offsets = dict(zip(models, (0.27, 0, -0.27)))
for y, method in enumerate(order):
    color = fk.ACCENT if method == best else fk.GREY
    for row in df[df.method == method].itertuples():
        yy = y + offsets[row.model]
        ax.hlines(yy, row.ci_low, row.ci_high, color=color, lw=1.6)
        ax.plot(row.spearman_r, yy, "o", color=color, ms=6)
        if method == best:
            ax.annotate(row.model, (row.ci_low, yy), xytext=(-6, 0), textcoords="offset points", ha="right",
                        va="center", color=fk.MUTED, fontsize=fk.SIZES["screen"]["ticks"])
ax.set_yticks(range(len(order)), [m[0].upper() + m[1:] for m in order])
ax.set(xlim=(0, 1), xlabel="Rank correlation with ablation (Spearman ρ)")
ax.grid(False, axis="y")
ax.grid(True, axis="x")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fk.title(fig, f"{best[0].upper() + best[1:]} matched ablation best on all three models")
fk.save(fig, HERE / "figure.png")
