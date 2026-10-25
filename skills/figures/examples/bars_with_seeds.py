"""Bar plot with every seed: the mean as a bar, each seed as a dot on it, and the value at the bar's end.

Answers: Is one condition higher than another?
Shows: bar plot with every seed as a dot: test accuracy on modular addition with weight decay, with dropout and
with neither
Claim: with weight decay every seed generalizes, and with dropout or neither none does.
Caption: **Weight decay raised test accuracy on modular addition from 28% to 99%, in every seed.** Bars are means
over five seeds and dots are the seeds. Accuracy is on 3,000 held-out pairs after 30,000 training steps of a
one-layer transformer. The colours come from figure-roles.json in this folder, which curves_with_seeds.py shares.
Made-up data, drawn to show the style.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
mean = {"weight decay": 99.0, "dropout": 41.0, "no weight decay": 32.0}  # % of held-out pairs answered right
spread = {"weight decay": 0.5, "dropout": 7.0, "no weight decay": 5.0}
df = pd.DataFrame([dict(condition=c, seed=s, accuracy=float(np.clip(m + rng.normal(0, spread[c]), 0, 100)))
                   for c, m in mean.items() for s in range(5)])
means = df.groupby("condition").accuracy.mean().sort_values(ascending=False)
order = list(means.index)  # categories in order of their values

fk.use()
fig, ax = plt.subplots()
sns.barplot(df, x="condition", y="accuracy", hue="condition", order=order, palette=fk.palette(order),
            errorbar=None, saturation=1, width=0.6, legend=False)
for i, condition in enumerate(order):  # every seed as a dot, spread evenly across its bar
    seeds = df[df.condition == condition].accuracy
    ax.scatter(i + np.linspace(-0.12, 0.12, len(seeds)), seeds, s=22, color=fk.INK, edgecolor="white",
               linewidth=0.8, zorder=3)
fk.label_values(ax, fmt="{:.0f}%")
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set(xlabel=None, ylabel="Test accuracy")
fk.title(fig, f"Weight decay raised test accuracy from {means['no weight decay']:.0f}% to "
              f"{means['weight decay']:.0f}% in every seed")
fk.save(fig, HERE / "bars_with_seeds.png")
