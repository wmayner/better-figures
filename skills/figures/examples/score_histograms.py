"""Two distributions: step histograms on one axis, each named beside its peak, the threshold as a thin dashed line.

Answers: How well does a probe or monitor separate two classes?
Shows: two histograms and a threshold: a deception probe's scores on honest and deceptive answers
Claim: deceptive answers score higher than honest ones, and most lie above the threshold.
Caption: **Deceptive answers scored higher than honest ones on the probe, and 64% were above the threshold.** Probe
scores on 1,000 honest and 1,000 deceptive answers held out from training, in bins of 0.2; the dashed line is the
threshold that flags 1% of honest answers. roc_probe.py shows the same scores as an ROC curve. Made-up data.
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
honest = rng.normal(0, 1, 1000)  # the same probe scores as roc_probe.py
deceptive = rng.normal(2.6, 1, 1000)
df = pd.DataFrame({"score": np.concatenate([honest, deceptive]), "answer": ["honest"] * 1000 + ["deceptive"] * 1000})
threshold = np.quantile(honest, 0.99)
above = 100 * (deceptive > threshold).mean()

fk.use()
fig, ax = plt.subplots()
colors = {"honest": fk.GREY, "deceptive": fk.ACCENT}
edges = np.arange(-4.4, 6.6, 0.2)
sns.histplot(df, x="score", hue="answer", palette=colors, element="step", fill=True, alpha=0.2, bins=edges,
             legend=False)
ax.axvline(threshold, color=fk.MUTED, lw=1, ls=(0, (4, 3)))
ax.annotate("threshold", (threshold, 1), xycoords=("data", "axes fraction"), xytext=(-4, -2),
            textcoords="offset points", ha="right", va="top", color=fk.MUTED)
for answer, scores, left in (("honest", honest, True), ("deceptive", deceptive, False)):
    counts, _ = np.histogram(scores, bins=edges)  # the bins seaborn drew
    tall = np.where(counts >= counts.max() / 2)[0]  # each name goes on the outer side, at half the peak's height
    x = edges[tall[0]] if left else edges[tall[-1] + 1]
    ax.annotate(answer, (x, counts.max() / 2), xytext=(-6 if left else 6, 0), textcoords="offset points",
                ha="right" if left else "left", va="center", color=fk.MUTED if left else fk.ACCENT,
                fontweight="semibold")
ax.set(xlabel="Probe score", ylabel="Answers")
fk.title(fig, "Deceptive answers scored higher than honest ones on the probe")
fk.save(fig, HERE / "score_histograms.png")
