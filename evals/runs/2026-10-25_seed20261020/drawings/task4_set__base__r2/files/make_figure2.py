"""Figure 2: sycophancy rate over training, by condition."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CONDITIONS = ["no honesty data", "honesty data", "honesty data and steering"]
LABELS = ["No honesty data", "Honesty data", "Honesty data + steering"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # fixed per condition across all figures
INK, INK_2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK_2,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
})

df = pd.read_csv("data.csv")
syc = df[df["measure"] == "sycophancy_rate_percent"]

fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=200)
for cond, label, color in zip(CONDITIONS, LABELS, COLORS):
    g = syc[syc["condition"] == cond].groupby("step")["value"]
    mean, sd, n = g.mean(), g.std(ddof=1), g.count()
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    steps = mean.index.to_numpy()
    ax.fill_between(steps, mean - half, mean + half, color=color, alpha=0.15, linewidth=0)
    ax.plot(steps, mean, color=color, lw=2, solid_capstyle="round", solid_joinstyle="round",
            label=label)
    ax.plot(steps[-1], mean.iloc[-1], "o", ms=6, color=color, mec="white", mew=1.5, zorder=4)
    ax.annotate(f"{label}  {mean.iloc[-1]:.1f}%", (steps[-1], mean.iloc[-1]),
                xytext=(8, 0), textcoords="offset points", va="center", fontsize=9, color=INK)

ax.set_xlim(0, syc["step"].max())
ax.set_ylim(0, 45)
ax.set_xlabel("Training step")
ax.set_ylabel("Sycophantic answers (%)")
ax.yaxis.grid(True, color=GRID, lw=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(loc="lower left", frameon=False, fontsize=9, handlelength=1.6)
ax.set_title("Sycophancy rate over training", loc="left", fontsize=11, color=INK)

fig.tight_layout()
fig.savefig("figure2.png", facecolor="white", bbox_inches="tight", pad_inches=0.15)
