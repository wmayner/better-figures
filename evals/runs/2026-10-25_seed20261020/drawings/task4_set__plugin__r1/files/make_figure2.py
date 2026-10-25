"""Figure 2: sycophancy rate over training, each seed faint and the mean over seeds bold."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_kit"))
import figkit as fk

df = pd.read_csv(HERE / "data.csv")
syc = df[df.measure == "sycophancy_rate_percent"]
order = ["no honesty data", "honesty data", "honesty data and steering"]

fk.use()
fig, ax = plt.subplots()
for condition in order:
    d = syc[syc.condition == condition]
    for _, run in d.groupby("seed"):
        ax.plot(run.step, run.value, color=fk.color(condition), lw=1, alpha=0.35, label="_seed")
    mean = d.groupby("step").value.mean()
    ax.plot(mean.index, mean.values, color=fk.color(condition), label=condition)
fk.label_lines(ax)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set(xlabel="Training step", ylabel="Sycophantic answers", xlim=(0, syc.step.max()), ylim=(0, None))
fk.title(fig, "Sycophancy fell during training only in the conditions with honesty data")
fk.save(fig, HERE / "figure2.png")
