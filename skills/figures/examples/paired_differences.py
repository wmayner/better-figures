"""Paired differences: two methods compared with the same baseline on the same models, each model's difference as a
dot, the mean with its interval against a line at zero.

Answers: Do two conditions differ, when both were measured on the same units?
Shows: paired differences: how much more often an activation probe and sparse autoencoder features detect a hidden
objective than a black-box baseline, on the same 20 fine-tuned models
Claim: the activation probe detects the hidden objective more often than the black-box baseline, and sparse
autoencoder features do not clearly differ from it.
Caption: **The activation probe detected the hidden objective more often than the black-box baseline on the same 20
fine-tuned models; sparse autoencoder features did not clearly differ from the baseline.** Each grey dot is one
model's difference in detection accuracy from the baseline, in percentage points. Coloured dots are means, and lines
are 95% bootstrap intervals over models. Each model's accuracy is over 200 prompts. Models differ far more from each
other than the methods do, so bars of each method's mean would overlap; the differences within each model do not.
Made-up data, drawn to show the style.
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
N_MODELS = 20
ease = rng.normal(62, 12, N_MODELS)  # how detectable each model's objective is: shared by every method
df = pd.DataFrame({
    "model": np.arange(N_MODELS),
    "black-box baseline": ease + rng.normal(0, 3, N_MODELS),
    "Activation probe": ease + 7 + rng.normal(0, 4, N_MODELS),
    "Sparse autoencoder features": ease + 1 + rng.normal(0, 5, N_MODELS),
})
rows = ["Sparse autoencoder features", "Activation probe"]  # bottom to top
gains = {m: fk.difference(df[m], df["black-box baseline"], paired=True, unit="models", seed=SEED) for m in rows}

fk.use()
fig, ax = plt.subplots()
for y, method in enumerate(rows):
    fk.differences(ax, gains[method], at=y, color=fk.ACCENT if gains[method].clear else fk.MUTED, seed=SEED)
ax.set_yticks(range(len(rows)), rows)
ax.set(ylim=(-0.6, len(rows) - 0.4), xlabel="Accuracy gain over black-box baseline (points)")
ax.grid(False, axis="y")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
fk.title(fig, "Only the activation probe clearly beat the black-box baseline", claims=gains["Activation probe"])
fk.save(fig, HERE / "paired_differences.png")
