"""Calibration plot: accuracy against stated confidence in bins, the diagonal for perfect calibration, names at the
line ends.

Answers: Is one model better calibrated than another?
Shows: calibration plot: how often a model is right at each stated confidence, before and after fine-tuning
Claim: after fine-tuning the model's stated confidence matches its accuracy; before, it was overconfident.
Caption: **After fine-tuning, the model's stated confidence matched its accuracy to within 4 points in every bin.**
Each point is the share of answers that were right among those whose stated confidence fell in a 10-point bin, on
4,000 trivia questions held out from fine-tuning; the thin line is perfect calibration. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
stated = np.arange(5, 100, 10)  # bin centres, % confidence
before = np.clip(0.55 * stated + 8 + rng.normal(0, 1.5, len(stated)), 0, 100)
after = np.clip(stated + rng.normal(0, 1.5, len(stated)), 0, 100)

fk.use()
fig, ax = plt.subplots()
ax.plot([0, 100], [0, 100], color=fk.LIGHT, lw=1, zorder=0)
ax.plot(stated, before, "o-", color=fk.GREY, ms=5, label="before fine-tuning")
ax.plot(stated, after, "o-", color=fk.ACCENT, ms=5, label="after fine-tuning")
fk.label_lines(ax)
ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set(xlim=(0, 100), ylim=(0, 100), xlabel="Stated confidence", ylabel="Answers that were right")
fk.title(fig, "After fine-tuning, the model's stated confidence matched its accuracy")
fk.save(fig, HERE / "calibration.png")
