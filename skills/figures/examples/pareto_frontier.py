"""Pareto plot: each method as a line through its settings, every seed as a faint dot, names at the line ends, the
method on the frontier in the accent colour.

Answers: Which method gives the best trade-off?
Shows: Pareto plot: loss recovered against active latents per token for three SAE architectures
Claim: TopK SAEs recover more loss than ReLU and gated SAEs at every sparsity.
Caption: **TopK SAEs recovered more of the model's loss than ReLU and gated SAEs at every L0, in every seed.** Lines
join the means of three training seeds, and faint dots are the seeds. Each SAE is trained on layer-8 residual stream
activations; loss recovered compares the model's loss with the SAE spliced in against its loss with the activations
zero-ablated, on 10 million held-out tokens. Made-up data.
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
    for setting in [10, 20, 40, 80, 160]:
        for seed in range(3):  # three training seeds at each sparsity setting
            l0 = setting * np.exp(rng.normal(0, 0.03))
            rows.append(dict(architecture=arch, setting=setting, seed=seed, l0=l0,
                             recovered=100 - gap * (l0 / 10) ** -0.55 + rng.normal(0, 0.25)))
df = pd.DataFrame(rows)
means = df.groupby(["architecture", "setting"])[["l0", "recovered"]].mean().reset_index()

fk.use()
fig, ax = plt.subplots()
for arch, d in means.groupby("architecture"):
    color = fk.ACCENT if arch == "TopK" else fk.GREY
    seeds = df[df.architecture == arch]
    ax.scatter(seeds.l0, seeds.recovered, s=12, color=color, alpha=0.45, linewidths=0)  # every seed
    ax.plot(d.l0, d.recovered, "o-", color=color, ms=5, label=arch)
ax.set(xscale="log", xlabel="Active latents per token (L0)", ylabel="Loss recovered")
ax.set_xticks([10, 20, 40, 80, 160])
fk.plain_ticks(ax.xaxis)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
fk.label_lines(ax, at="start")  # the lines bunch together at their right ends; label after the scales are set
fk.title(fig, "TopK recovered more loss than ReLU and gated SAEs at every L0")
fk.save(fig, HERE / "pareto_frontier.png")
