"""Scaling plot: points on log-log axes, the fitted power law as a thin line, and its exponent as the one key number.

Answers: Does a trend follow a scaling law?
Shows: scaling plot on log-log axes: SAE reconstruction error against dictionary size
Claim: reconstruction error falls as a power law in dictionary size.
Caption: **Reconstruction error fell as a power law in dictionary size, by about 15% with each doubling.** Normalized
mean squared error of one SAE per size, trained on layer-8 residual stream activations of a 12-layer model and
measured on 10 million held-out tokens; the line is a least-squares fit in log-log space. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
size = 2.0 ** np.arange(12, 21)
error = 0.9 * (size / size[0]) ** -0.24 * np.exp(rng.normal(0, 0.03, len(size)))
slope, intercept = np.polyfit(np.log(size), np.log(error), 1)
fit = np.exp(intercept) * size ** slope

fk.use()
fig, ax = plt.subplots()
ax.plot(size, fit, color=fk.GREY, lw=1.4, zorder=1)
ax.plot(size, error, "o", color=fk.ACCENT, ms=7)
ax.annotate(f"error $\\propto$ size$^{{{slope:.2f}}}$", (size[5], fit[5]), xytext=(8, 12), textcoords="offset points",
            color=fk.MUTED)
ax.set(xscale="log", yscale="log", xlabel="Dictionary size (latents)", ylabel="Normalized MSE", ylim=(0.2, 1.0))
ax.set_xticks(size[::2], ["4k", "16k", "64k", "256k", "1M"])
ax.set_yticks([0.25, 0.5, 1.0])
fk.plain_ticks(ax.yaxis)
ax.xaxis.set_minor_locator(plt.NullLocator())
fk.title(fig, "Reconstruction error fell as a power law in dictionary size")
fk.save(fig, HERE / "scaling_log.png")
