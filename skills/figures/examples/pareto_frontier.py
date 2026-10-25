"""Pareto plot: each method as a line through its settings, names at the line ends, the method on the frontier in the
accent colour.

Answers: Which method gives the best trade-off?
Shows: Pareto plot: loss recovered against active latents per token for three SAE architectures
Claim: TopK SAEs recover more loss than ReLU and gated SAEs at every sparsity.
Caption: **TopK SAEs recovered more of the model's loss than ReLU and gated SAEs at every L0.** Each point is one SAE
trained on layer-8 residual stream activations; loss recovered compares the model's loss with the SAE spliced in
against its loss with the activations zero-ablated, on 10 million held-out tokens. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
gap_at_10 = {"TopK": 11, "gated": 14, "ReLU": 18}  # % of loss not recovered at L0 = 10
rows = []
for arch, gap in gap_at_10.items():
    l0 = np.array([10, 20, 40, 80, 160]) * np.exp(rng.normal(0, 0.06, 5))
    recovered = 100 - gap * (l0 / 10) ** -0.55 + rng.normal(0, 0.2, 5)
    rows += [dict(architecture=arch, l0=a, recovered=b) for a, b in zip(l0, recovered)]
df = pd.DataFrame(rows)

fk.use()
fig, ax = plt.subplots()
for arch, d in df.groupby("architecture"):
    color = fk.ACCENT if arch == "TopK" else fk.GREY
    ax.plot(d.l0, d.recovered, "o-", color=color, ms=5, label=arch)
ax.set(xscale="log", xlabel="Active latents per token (L0)", ylabel="Loss recovered")
ax.set_xticks([10, 20, 40, 80, 160])
fk.plain_ticks(ax.xaxis)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
fk.label_lines(ax, at="start")  # the lines bunch together at their right ends; label after the scales are set
fk.title(fig, "TopK recovered more loss than ReLU and gated SAEs at every L0")
fk.save(fig, HERE / "pareto_frontier.png")
