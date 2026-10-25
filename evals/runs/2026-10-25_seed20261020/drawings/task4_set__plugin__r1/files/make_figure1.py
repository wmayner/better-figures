"""Figure 1: final sycophancy rate by condition, a bar per condition with every seed as a dot."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

df = pd.read_csv(HERE / "data.csv")
syc = df[df.measure == "sycophancy_rate_percent"]
final = syc[syc.step == syc.step.max()]
means = final.groupby("condition").value.mean().sort_values(ascending=False)
order = list(means.index)  # categories in order of their values

fk.use()
fig, ax = plt.subplots()
sns.barplot(final, x="condition", y="value", hue="condition", order=order, palette=fk.palette(order),
            errorbar=None, saturation=1, width=0.6, legend=False)
for i, condition in enumerate(order):  # every seed as a dot, spread evenly across its bar
    seeds = final[final.condition == condition].value
    ax.scatter(i + np.linspace(-0.12, 0.12, len(seeds)), seeds, s=22, color=fk.INK, edgecolor="white",
               linewidth=0.8, zorder=3)
fk.label_values(ax, fmt="{:.0f}%")
ax.set_xticks(range(len(order)), [c.replace(" and ", "\nand ") for c in order])
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set(xlabel=None, ylabel="Sycophantic answers")
fk.title(fig, f"Honesty data and steering cut final sycophancy from "
              f"{means['no honesty data']:.0f}% to {means['honesty data and steering']:.0f}%")
fk.save(fig, HERE / "figure1.png")
