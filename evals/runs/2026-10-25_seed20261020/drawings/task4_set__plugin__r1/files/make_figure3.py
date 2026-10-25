"""Figure 3: final helpfulness by condition, a bar per condition with every seed as a dot."""
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
helpful = df[df.measure == "helpfulness_1_to_10"]
means = helpful.groupby("condition").value.mean().sort_values(ascending=False)
order = list(means.index)  # categories in order of their values

fk.use()
fig, ax = plt.subplots()
sns.barplot(helpful, x="condition", y="value", hue="condition", order=order, palette=fk.palette(order),
            errorbar=None, saturation=1, width=0.6, legend=False)
for i, condition in enumerate(order):  # every seed as a dot, spread evenly across its bar
    seeds = helpful[helpful.condition == condition].value
    ax.scatter(i + np.linspace(-0.12, 0.12, len(seeds)), seeds, s=22, color=fk.INK, edgecolor="white",
               linewidth=0.8, zorder=3)
fk.label_values(ax, fmt="{:.1f}")
ax.set_xticks(range(len(order)), [c.replace(" and ", "\nand ") for c in order])
ax.set(xlabel=None, ylabel="Helpfulness (1 to 10)", ylim=(0, 10))
fk.title(fig, f"Final helpfulness was {means.min():.1f} to {means.max():.1f} of 10 in every condition")
fk.save(fig, HERE / "figure3.png")
