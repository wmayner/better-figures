"""ROC plot: each detector's curve on a log false-positive axis, chance as a thin line, and one marked operating point
with its value.

Answers: How well does a probe or monitor separate two classes?
Shows: ROC curves: a deception probe against a black-box baseline, with the operating point at 1% false positives
Claim: at a 1% false-positive rate, the probe catches most deceptive answers and the baseline few.
Caption: **At a 1% false-positive rate, the probe caught 64% of deceptive answers, against 13% for follow-up
questions.** True-positive rate against false-positive rate as the threshold varies, on 1,000 honest and 1,000
deceptive answers held out from training; the false-positive axis is logarithmic, and the dotted line marks 1%.
score_histograms.py shows the same probe scores. Made-up data.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, PercentFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the skill's directory, which holds figkit.py
import figkit as fk

SEED = 0
rng = np.random.default_rng(SEED)
honest = rng.normal(0, 1, 1000)  # probe scores, shared with score_histograms.py
deceptive = rng.normal(2.6, 1, 1000)
honest_q, deceptive_q = rng.normal(0, 1, 1000), rng.normal(1.0, 1, 1000)  # the baseline's scores


def roc(neg, pos):
    t = np.sort(np.concatenate([neg, pos]))[::-1]
    return 100 * (neg[None, :] >= t[:, None]).mean(1), 100 * (pos[None, :] >= t[:, None]).mean(1)


fpr, tpr = roc(honest, deceptive)
fpr_q, tpr_q = roc(honest_q, deceptive_q)
at_1 = tpr[fpr <= 1].max()
at_1_q = tpr_q[fpr_q <= 1].max()

fk.use()
fig, ax = plt.subplots()
chance = np.logspace(-1, 2, 50)
ax.plot(chance, chance, color=fk.LIGHT, lw=1, zorder=0)
ax.axvline(1, color=fk.MUTED, lw=0.9, ls=(0, (1, 2)), zorder=0)
ax.plot(fpr, tpr, color=fk.ACCENT, label="probe", drawstyle="steps-post")
ax.plot(fpr_q, tpr_q, color=fk.GREY, label="follow-up questions", drawstyle="steps-post")
ax.plot(1, at_1, "o", color=fk.ACCENT, ms=6)
ax.annotate(f"{at_1:.0f}%", (1, at_1), xytext=(-7, 0), textcoords="offset points", ha="right", va="center",
            fontweight="semibold")
# Both curves end at the top right corner, so each is named where it is far from the other.
ax.annotate("probe", (0.105, tpr[fpr <= 0.105].max()), xytext=(2, 5), textcoords="offset points", va="bottom",
            color=fk.ACCENT, fontweight="semibold")
ax.annotate("follow-up questions", (12, tpr_q[fpr_q <= 12].max()), xytext=(4, -16), textcoords="offset points",
            color=fk.MUTED, fontweight="semibold")
ax.annotate("chance", (30, 30), xytext=(4, -14), textcoords="offset points", color=fk.MUTED)
ax.set(xscale="log", xlim=(0.1, 100), ylim=(0, 102), xlabel="False-positive rate", ylabel="Deceptive answers caught")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
fk.title(fig, f"At a 1% false-positive rate, the probe caught {at_1:.0f}% of deceptive answers")
fk.save(fig, HERE / "roc_probe.png")
