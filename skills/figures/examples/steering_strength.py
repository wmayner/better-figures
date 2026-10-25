"""Line plot over a dose: one line per ordered condition in the light-to-dark ramp, each named where the lines are
far apart.

Answers: How does an effect grow with a dose?
Shows: lines in the ordered ramp: how often steered completions mention a concept as the steering coefficient
grows, for four model sizes
Claim: larger models need a larger steering coefficient before they mention the concept.
Caption: **Larger models needed stronger steering before half their completions mentioned the concept.** Share of
200 completions per point that mention the Golden Gate Bridge when its SAE latent, scaled by the coefficient, is
added to the residual stream at the middle layer; the dashed line marks half. The model sizes take the ordered ramp
from figure-roles.json in this folder. Made-up data.
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
coefficient = np.linspace(0, 10, 21)
halfway = {"70M": 2.0, "410M": 3.3, "1.4B": 4.7, "6.9B": 6.4}  # coefficient at which half mention the concept
rows = []
for model, mid in halfway.items():
    p = 1 / (1 + np.exp(-(coefficient - mid) * 1.4))
    share = 100 * rng.binomial(200, p) / 200
    rows += [dict(model=model, coefficient=c, mentions=s) for c, s in zip(coefficient, share)]
df = pd.DataFrame(rows)

fk.use()
fig, ax = plt.subplots()
ax.axhline(50, color=fk.MUTED, lw=0.9, ls=(0, (3, 3)), zorder=0)
for model, d in df.groupby("model", sort=False):
    ax.plot(d.coefficient, d.mentions, color=fk.color(model), label=model)
    # Lines that bunch together at their ends are named where they are far apart: here, where each crosses half.
    ax.annotate(model, (halfway[model], 50), xytext=(-8, 8), textcoords="offset points", ha="right", va="bottom",
                color=fk.color(model), fontweight="semibold")
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set(xlabel="Steering coefficient", ylabel="Completions mentioning the concept", xlim=(0, 10), ylim=(0, 100))
fk.title(fig, "Larger models needed stronger steering to mention the concept")
fk.save(fig, HERE / "steering_strength.png")
