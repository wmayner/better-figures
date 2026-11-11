"""Bar plot: the comparison the claim is about, in four settings, with the method of interest in the accent colour
and an interval on every bar that resamples the unit that was sampled independently.

Answers: Is one condition higher than another?
Shows: bar plot: the loss increase from ablating the top heads by activation patching against random heads, on
four tasks
Claim: ablating the 10 heads that activation patching ranks highest raises the loss several times more
than ablating 10 random heads, on every task.
Caption: **Ablating the 10 heads that activation patching ranks highest raised the loss 4 times as much as ablating
10 random heads, on every task.** Mean increase in loss on the correct token when 10 attention heads are
mean-ablated, on the same 500 prompts per task for both ablations; error bars are 95% bootstrap intervals over
prompts. The title's comparison is computed prompt by prompt, since the prompts are shared. Tasks are in order of the
effect. Made-up data, drawn to show the style.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
PALETTE = {"random": fk.LIGHT, "top by patching": fk.ACCENT}
rows = []
for task, effect in [("Induction", 2.1), ("Indirect object", 1.6), ("Greater-than", 0.9), ("Bracket matching", 1.3)]:
    hardness = rng.gamma(4, 0.25, size=500)  # each prompt's own sensitivity, shared by both ablations
    for heads, scale in [("random", 0.25), ("top by patching", 1.0)]:
        for prompt, loss in enumerate(effect * scale * hardness * rng.lognormal(0, 0.2, size=500)):
            rows.append(dict(task=task, prompt=prompt, heads=heads, loss_increase=loss))
df = pd.DataFrame(rows)
wide = df.pivot(index=["task", "prompt"], columns="heads", values="loss_increase")  # one row per prompt
means = wide.groupby("task").mean()
order = list(means["top by patching"].sort_values(ascending=False).index)  # tasks in order of the effect
ratio = (means["top by patching"] / means["random"]).mean()
gap = fk.difference(wide["top by patching"], wide["random"], paired=True, unit="prompts")  # the same prompts in both

fk.use()
fig, ax = plt.subplots()
sns.barplot(df, x="task", y="loss_increase", hue="heads", order=order, hue_order=list(PALETTE), palette=PALETTE,
            errorbar=None, saturation=1, width=0.9)
for bars, heads in zip(ax.containers, PALETTE):  # an interval on each bar, resampling prompts
    fk.intervals(ax, [b.get_x() + b.get_width() / 2 for b in bars],
                 [fk.interval(wide.loc[task, heads], unit="prompts", seed=SEED) for task in order])
fk.label_bars(ax)
ax.set(xlabel=None, ylabel="Loss increase (nats)")
fk.title(fig, f"Ablating top heads raised loss {ratio:.0f} times as much as random heads", claims=gap)
fk.save(fig, HERE / "bar_comparison.png")
