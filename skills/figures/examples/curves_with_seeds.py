"""Line plot with every seed: each seed faint, the mean over seeds bold, names at the line ends.

Answers: How does a measure change over training, or across layers?
Shows: line plot with every seed: test accuracy on modular addition over training, with and without weight decay
Claim: with weight decay, test accuracy jumps to nearly 100% partway through training in every seed; without it,
accuracy stays low.
Caption: **With weight decay, every seed passed 98% test accuracy by step 12,000; without it, none passed 31%.**
Bold lines are means over five seeds and faint lines are the seeds. Accuracy is on 3,000 held-out pairs, every 250
steps. This is the diverging line template: one line goes up and the other doesn't. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
steps = np.arange(0, 30001, 250)
rows = []
for condition in ["weight decay", "no weight decay"]:
    for seed in range(5):
        if condition == "weight decay":  # each seed generalizes suddenly, at its own step
            accuracy = 2 + 97.5 / (1 + np.exp(-(steps - rng.uniform(7000, 10000)) / 500))
        else:
            accuracy = 2 + 28 * (1 - np.exp(-steps / 9000))
        accuracy = np.clip(accuracy + rng.normal(0, 0.8, len(steps)), 0, 100)
        rows += [dict(condition=condition, seed=seed, step=int(s), accuracy=float(a)) for s, a in zip(steps, accuracy)]
df = pd.DataFrame(rows)

fk.use()
fig, ax = plt.subplots()
for condition, d in df.groupby("condition"):
    for _, run in d.groupby("seed"):
        ax.plot(run.step, run.accuracy, color=fk.color(condition), lw=1, alpha=0.35, label="_seed")
    mean = d.groupby("step").accuracy.mean()
    ax.plot(mean.index, mean.values, color=fk.color(condition), label=condition)
fk.label_lines(ax)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set(xlabel="Training step", ylabel="Test accuracy", xlim=(0, 30000), ylim=(0, 100))
wd = df[df.condition == "weight decay"]
passed = wd[wd.accuracy >= 98].groupby("seed").step.min().max()  # the step by which every seed passed 98%
fk.title(fig, f"With weight decay, every seed passed 98% accuracy by step {int(np.ceil(passed / 1000)) * 1000:,}")
fk.save(fig, HERE / "curves_with_seeds.png")
