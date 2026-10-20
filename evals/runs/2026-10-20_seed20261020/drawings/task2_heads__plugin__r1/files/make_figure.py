"""Ranked ablation effects of every attention head, with the few heads that matter highlighted.

Claim: three heads (L9H6, L9H9, L10H0) carry almost all of the ablation effect; every other head
raises the loss by less than a tenth as much.
Reads data.csv (layer, head, loss_increase, sem, n_prompts) and writes figure.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "<repository>/skills/figures")
import figkit as fk

HERE = Path(__file__).resolve().parent
N_HIGHLIGHT = 3  # heads drawn in the accent colour and named

df = pd.read_csv(HERE / "data.csv")
df = df.sort_values("loss_increase", ascending=False).reset_index(drop=True)
df["name"] = "L" + df["layer"].astype(str) + "H" + df["head"].astype(str)
top = df.index < N_HIGHLIGHT

fk.use()
fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(1, len(df) + 1)
ax.bar(x, df["loss_increase"], width=0.8, color=np.where(top, fk.ACCENT, fk.GREY))
ax.errorbar(x[top], df.loc[top, "loss_increase"], yerr=df.loc[top, "sem"],
            fmt="none", ecolor=fk.MUTED, elinewidth=1.2, capsize=0)
ax.axhline(0, color=fk.MUTED, lw=0.8)

for xi, row in zip(x[top], df[top].itertuples()):
    ax.annotate(row.name, (xi, row.loss_increase + row.sem), xytext=(6, 0),
                textcoords="offset points", ha="left", va="center", color=fk.ACCENT)

ax.set(xlim=(0, len(df) + 1), xlabel="Head, ranked by ablation effect", ylabel="Loss increase")
ax.set_xticks([1, 25, 50, 75, 100, 125, len(df)])
fk.save(fig, HERE / "figure.png")
