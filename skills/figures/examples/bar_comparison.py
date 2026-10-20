"""Bar plot: the comparison the claim is about, in four settings, with the method of interest in the accent colour.

Claim: ablating the 10 heads that activation patching ranks highest raises the loss several times more
than ablating 10 random heads, on every task.
Caption: mean increase in loss on the correct token when 10 attention heads are mean-ablated, over 500
prompts per task; error bars are 95% bootstrap intervals. Made-up data, drawn to show the style.
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
rows = []
for task, effect in [("Induction", 2.1), ("Indirect object", 1.6), ("Greater-than", 0.9), ("Bracket matching", 1.3)]:
    for heads, scale in [("random", 0.25), ("top by patching", 1.0)]:
        for loss in effect * scale * rng.gamma(4, 0.25, size=500):
            rows.append(dict(task=task, heads=heads, loss_increase=loss))
df = pd.DataFrame(rows)

fk.use()
fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(df, x="task", y="loss_increase", hue="heads",
            palette={"random": fk.LIGHT, "top by patching": fk.ACCENT},
            errorbar=("ci", 95), seed=SEED, saturation=1, width=0.9, err_kws={"color": fk.MUTED, "lw": 1.2})
fk.label_bars(ax)
ax.set(xlabel=None, ylabel="Loss increase (nats)")
fk.save(fig, HERE / "bar_comparison.png")
