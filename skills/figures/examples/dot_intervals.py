"""Dot plot with intervals: one row per method, a dot and its 95% interval for each model, the best method in the
accent colour and its models named once.

Answers: How do several methods rank, and how sure are we?
Shows: dot plot with intervals: how closely five attribution methods rank attention heads the way ablation does,
on three models
Claim: integrated gradients agrees with ablation best, on every model.
Caption: **Integrated gradients ranked attention heads most like ablation on all three models.** Each dot is the
Spearman correlation between a method's score for every head and the loss increase when that head is mean-ablated,
over 500 prompts; lines are 95% intervals (Fisher z, n = the model's number of heads). Within each method, the
three dots are GPT-2 small (144 heads), Pythia-410M (384) and Gemma-2-2B (208). Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
METHODS = {"integrated gradients": 0.84, "attribution patching": 0.61, "gradient times input": 0.47,
           "saliency": 0.31, "activation magnitude": 0.18}
MODELS = {"GPT-2 small": 144, "Pythia-410M": 384, "Gemma-2-2B": 208}  # model: number of heads ranked
rows = []
for method, rho in METHODS.items():
    for model, n in MODELS.items():
        r = float(np.clip(rho + rng.normal(0, 0.03), -0.99, 0.99))
        z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
        rows.append(dict(method=method, model=model, rho=r, lo=np.tanh(z - 1.96 * se), hi=np.tanh(z + 1.96 * se)))
df = pd.DataFrame(rows)
order = list(df.groupby("method").rho.mean().sort_values().index)  # bottom to top, so the best is on top
best = order[-1]

fk.use()
fig, ax = plt.subplots()
for y, method in enumerate(order):
    color = fk.ACCENT if method == best else fk.GREY
    for offset, row in zip((0.22, 0, -0.22), df[df.method == method].itertuples()):
        ax.hlines(y + offset, row.lo, row.hi, color=color, lw=1.6)
        ax.plot(row.rho, y + offset, "o", color=color, ms=6)
        if method == best:
            ax.annotate(row.model, (row.lo, y + offset), xytext=(-6, 0), textcoords="offset points", ha="right",
                        va="center", color=fk.MUTED, fontsize=fk.SIZES["screen"]["ticks"])
ax.set_yticks(range(len(order)), order)
ax.set(xlim=(0, 1), xlabel="Rank correlation with ablation (Spearman ρ)")
ax.grid(False, axis="y")
ax.grid(True, axis="x")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fk.title(fig, "Integrated gradients matched ablation best on every model")
fk.save(fig, HERE / "dot_intervals.png")
