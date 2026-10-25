"""Plot per-head ablation effects from data.csv and save figure.png.

Panel (a): layer x head grid of the loss increase from ablating each head.
Panel (b): the same 144 heads ranked by loss increase, with 95% CIs.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# Palette: sequential blue ramp (light -> dark) and chart chrome.
SURFACE = "#fcfcfb"
BLUE_RAMP = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
             "#256abf", "#184f95", "#0d366b"]
SERIES = "#2a78d6"
HIGHLIGHT = "#0d366b"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

N_TOP = 3  # heads called out by name

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

df = pd.read_csv("data.csv")
n_layers = df["layer"].max() + 1
n_heads = df["head"].max() + 1
df["label"] = "L" + df["layer"].astype(str) + "H" + df["head"].astype(str)
df["ci95"] = 1.96 * df["sem"]

grid = (df.pivot(index="layer", columns="head", values="loss_increase")
          .reindex(index=range(n_layers), columns=range(n_heads)))
ranked = df.sort_values("loss_increase", ascending=False).reset_index(drop=True)
top = ranked.head(N_TOP)
rest = ranked.iloc[N_TOP:]
vmax = df["loss_increase"].max()

cmap = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
fig, (ax_h, ax_r) = plt.subplots(
    1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.28})

# (a) Heatmap. Colour scale is linear from 0; the few slightly negative
# values (all within noise) render at the zero colour.
mesh = ax_h.pcolormesh(np.arange(n_heads + 1) - 0.5, np.arange(n_layers + 1) - 0.5,
                       grid.values, cmap=cmap, vmin=0, vmax=vmax,
                       edgecolors=SURFACE, linewidth=1.5)
ax_h.set_xlim(-0.5, n_heads - 0.5)
ax_h.set_ylim(n_layers - 0.5, -0.5)  # layer 0 at top
ax_h.set_aspect("equal")
ax_h.set_xticks(range(n_heads))
ax_h.set_yticks(range(n_layers))
ax_h.set_xlabel("Head")
ax_h.set_ylabel("Layer")
ax_h.tick_params(length=0)
for side in ax_h.spines.values():
    side.set_visible(False)
for _, r in top.iterrows():
    ax_h.text(r["head"], r["layer"], f"{r['loss_increase']:.2f}",
              ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
cb = fig.colorbar(mesh, ax=ax_h, fraction=0.046, pad=0.03)
cb.set_label("Loss increase when ablated", color=INK_2)
cb.outline.set_visible(False)
cb.ax.tick_params(length=0)
ax_h.set_title("a   Ablation effect by layer and head", loc="left",
               color=INK, fontsize=11, fontweight="bold")

# (b) Ranked dot plot with 95% CIs.
x = np.arange(1, len(ranked) + 1)
ax_r.axhline(0, color=AXIS, linewidth=1, zorder=1)
ax_r.errorbar(x[N_TOP:], rest["loss_increase"], yerr=rest["ci95"], fmt="o",
              ms=3, color=SERIES, ecolor=MUTED, elinewidth=0.8, capsize=0, zorder=2)
ax_r.errorbar(x[:N_TOP], top["loss_increase"], yerr=top["ci95"], fmt="o",
              ms=6, color=HIGHLIGHT, ecolor=INK_2, elinewidth=1.2, capsize=0, zorder=3)
for i, r in top.iterrows():
    ax_r.annotate(f"{r['label']}  ({r['loss_increase']:.2f})",
                  (x[i], r["loss_increase"]), xytext=(9, 0),
                  textcoords="offset points", va="center", color=INK, fontsize=9.5)
ax_r.annotate(
    f"Other {len(rest)} heads: median {rest['loss_increase'].median():.3f}, "
    f"max {rest['loss_increase'].max():.3f}",
    (len(ranked) / 2, rest["loss_increase"].max()), xytext=(0, 14),
    textcoords="offset points", ha="center", va="bottom", color=INK_2, fontsize=9.5)
ax_r.set_xlim(-3, len(ranked) + 3)
ax_r.set_ylim(-0.08, vmax * 1.12)
ax_r.set_xlabel("Head rank (by loss increase)")
ax_r.set_ylabel("Loss increase when ablated")
ax_r.grid(axis="y", color=GRID, linewidth=0.8)
ax_r.set_axisbelow(True)
ax_r.tick_params(length=0)
for name in ("top", "right", "left", "bottom"):
    ax_r.spines[name].set_visible(False)
ax_r.set_title(f"b   All {len(ranked)} heads, ranked (±95% CI)", loc="left",
               color=INK, fontsize=11, fontweight="bold")

fig.savefig("figure.png", dpi=200, bbox_inches="tight")
