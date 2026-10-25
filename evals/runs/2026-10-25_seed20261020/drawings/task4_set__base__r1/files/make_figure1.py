"""Figure 1: final sycophancy rate by training condition (step 2000, 5 seeds)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CONDITIONS = ["no honesty data", "honesty data", "honesty data and steering"]
LABELS = ["No honesty data", "Honesty data", "Honesty data\n+ steering"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

df = pd.read_csv("data.csv")
syc = df[df["measure"] == "sycophancy_rate_percent"]
final = syc[syc["step"] == syc["step"].max()]

plt.rcParams.update({"font.size": 10, "text.color": TEXT, "axes.labelcolor": TEXT,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(5.5, 4.2))
rng = np.random.default_rng(0)

for i, (cond, color) in enumerate(zip(CONDITIONS, COLORS)):
    vals = final.loc[final["condition"] == cond, "value"].to_numpy()
    mean = vals.mean()
    ci = stats.sem(vals) * stats.t.ppf(0.975, len(vals) - 1)
    jitter = rng.uniform(-0.12, 0.12, len(vals))
    ax.scatter(i + jitter, vals, s=28, color=color, alpha=0.55,
               edgecolor="white", linewidth=0.8, zorder=2)
    ax.errorbar(i + 0.3, mean, yerr=ci, fmt="o", ms=8, color=color,
                mec="white", mew=1.5, elinewidth=2, capsize=4, capthick=2, zorder=3)
    ax.annotate(f"{mean:.1f}%", (i + 0.3, mean), xytext=(10, 0),
                textcoords="offset points", va="center", color=TEXT, fontsize=9)

ax.set_xticks(range(len(CONDITIONS)), LABELS)
ax.set_xlim(-0.5, len(CONDITIONS) - 0.2)
ax.set_ylim(0, 45)
ax.set_ylabel("Sycophantic answers at end of training (%)")
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="both", length=0)
ax.set_title("Final sycophancy rate by condition", loc="left", fontsize=11, fontweight="bold")

fig.tight_layout()
fig.savefig("figure1.png", dpi=200, facecolor="white")
