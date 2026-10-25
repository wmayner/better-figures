"""Figure 1: final sycophancy rate by training condition."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CONDITIONS = ["no honesty data", "honesty data", "honesty data and steering"]
LABELS = ["No honesty data", "Honesty data", "Honesty data\n+ steering"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # fixed per condition across all figures
INK, INK_2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK_2,
    "xtick.color": INK_2, "ytick.color": MUTED, "text.color": INK,
})


def mean_ci(x, level=0.95):
    x = np.asarray(x, dtype=float)
    half = stats.t.ppf((1 + level) / 2, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), half


df = pd.read_csv("data.csv")
syc = df[df["measure"] == "sycophancy_rate_percent"]
final = syc[syc["step"] == syc["step"].max()]

fig, ax = plt.subplots(figsize=(5.0, 3.8), dpi=200)
rng = np.random.default_rng(0)
for i, (cond, color) in enumerate(zip(CONDITIONS, COLORS)):
    vals = final.loc[final["condition"] == cond, "value"].to_numpy()
    m, h = mean_ci(vals)
    # Seeds to the left, mean with 95% CI to the right, so neither hides the other.
    jitter = rng.uniform(-0.05, 0.05, len(vals))
    ax.scatter(i - 0.12 + jitter, vals, s=24, color=color, alpha=0.5, linewidths=0, zorder=2)
    ax.errorbar(i + 0.08, m, yerr=h, fmt="o", ms=5, color=color, mew=0,
                elinewidth=2, capsize=0, zorder=3)
    ax.text(i + 0.2, m, f"{m:.1f}%", va="center", ha="left", fontsize=9.5, color=INK)

ax.set_xticks(range(len(CONDITIONS)), LABELS)
ax.set_xlim(-0.5, len(CONDITIONS) - 0.3)
ax.set_ylim(0, 45)
ax.set_ylabel("Sycophantic answers at end of training (%)")
ax.yaxis.grid(True, color=GRID, lw=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", length=0, pad=6)
ax.set_title("Final sycophancy rate by condition", loc="left", fontsize=11, color=INK)

fig.tight_layout()
fig.savefig("figure1.png", facecolor="white")
