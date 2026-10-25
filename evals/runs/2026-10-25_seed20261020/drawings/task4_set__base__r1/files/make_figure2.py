"""Figure 2: sycophancy rate over training by condition (mean of 5 seeds, 95% CI)."""
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

CONDITIONS = ["no honesty data", "honesty data", "honesty data and steering"]
LABELS = ["No honesty data", "Honesty data", "Honesty data + steering"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

df = pd.read_csv("data.csv")
syc = df[df["measure"] == "sycophancy_rate_percent"]

plt.rcParams.update({"font.size": 10, "text.color": TEXT, "axes.labelcolor": TEXT,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(7, 4.2))

for cond, label, color in zip(CONDITIONS, LABELS, COLORS):
    g = syc[syc["condition"] == cond].groupby("step")["value"]
    mean, sem, n = g.mean(), g.sem(), g.count()
    ci = sem * stats.t.ppf(0.975, n - 1)
    ax.fill_between(mean.index, mean - ci, mean + ci, color=color, alpha=0.18, linewidth=0)
    ax.plot(mean.index, mean, color=color, linewidth=2, label=label)
    ax.annotate(f"{label}  {mean.iloc[-1]:.1f}%", (mean.index[-1], mean.iloc[-1]),
                xytext=(8, 0), textcoords="offset points", va="center",
                color=TEXT, fontsize=9)

ax.set_xlim(0, syc["step"].max())
ax.set_ylim(0, 45)
ax.set_xlabel("Training step")
ax.set_ylabel("Sycophantic answers (%)")
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="both", length=0)
ax.legend(loc="lower left", frameon=False, fontsize=9)
ax.set_title("Sycophancy rate over training", loc="left", fontsize=11, fontweight="bold")

fig.tight_layout()
fig.savefig("figure2.png", dpi=200, facecolor="white", bbox_inches="tight")
