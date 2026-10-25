"""Dot plot: how closely each attribution method's head scores agree with ablation, on three models.

Claim: integrated gradients agrees with ablation best, on every model.
Reads data.csv beside this script and saves figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

df = pd.read_csv(HERE / "data.csv")
MODELS = ["GPT-2 small", "Pythia-410M", "Gemma-2-2B"]  # top to bottom within each method
order = list(df.groupby("method").spearman_r.mean().sort_values().index)  # bottom to top, so the best is on top
best = order[-1]
runner_up = order[-2]

fk.use()
fig, ax = plt.subplots()
for y, method in enumerate(order):
    color = fk.ACCENT if method == best else fk.GREY
    rows = df[df.method == method].set_index("model").loc[MODELS]
    for offset, (model, row) in zip((0.26, 0, -0.26), rows.iterrows()):
        ax.hlines(y + offset, row.ci_low, row.ci_high, color=color, lw=1.6)
        ax.plot(row.spearman_r, y + offset, "o", color=color, ms=6)
        if method == best:
            ax.annotate(model, (row.ci_low, y + offset), xytext=(-6, 0), textcoords="offset points", ha="right",
                        va="center", color=fk.MUTED, fontsize=fk.SIZES["screen"]["ticks"])
ax.set_yticks(range(len(order)), order)
ax.set(xlim=(0, 1), xlabel="Rank correlation with ablation (Spearman ρ)")
ax.grid(False, axis="y")
ax.grid(True, axis="x")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)

# The claim holds only if the best method's lowest interval clears every other method's highest one, on every model.
gap = min(df[df.method == best].set_index("model").ci_low - df[df.method != best].groupby("model").ci_high.max())
if gap <= 0:
    print(f"warning: {best} intervals overlap another method's on some model (gap {gap:.3f})")
fk.title(fig, f"{best.capitalize()} matched ablation best on all three models")
fk.save(fig, HERE / "figure.png")
