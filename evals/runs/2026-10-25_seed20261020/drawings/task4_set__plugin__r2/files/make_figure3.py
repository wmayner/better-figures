"""Figure 3: final helpfulness by condition, the mean as a bar and each seed as a dot."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

df = pd.read_csv(HERE / "data.csv")
df = df[df.measure == "helpfulness_1_to_10"]
order = ["no honesty data", "honesty data", "honesty data and steering"]  # the same order as Figure 1
means = df.groupby("condition").value.mean()

fk.use()
fig, ax = plt.subplots()
sns.barplot(df, x="condition", y="value", hue="condition", order=order, palette=fk.palette(order),
            errorbar=None, saturation=1, width=0.6, legend=False)
for i, condition in enumerate(order):  # every seed as a dot, spread across its bar
    seeds = df[df.condition == condition].sort_values("seed").value
    ax.scatter(i + np.linspace(-0.12, 0.12, len(seeds)), seeds, s=22, color=fk.INK, edgecolor="white",
               linewidth=0.8, zorder=3)
fk.label_values(ax, fmt="{:.1f}")
ax.set(xlabel=None, ylabel="Helpfulness (1 to 10)", ylim=(1, 10), yticks=range(1, 11))
fk.title(fig, f"Final helpfulness was {means.min():.1f} to {means.max():.1f} "
              f"of 10 in all three conditions")
fk.save(fig, HERE / "figure3.png", order=False)
