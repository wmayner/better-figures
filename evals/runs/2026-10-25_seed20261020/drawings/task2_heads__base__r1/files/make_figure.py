"""Plot per-head ablation effects from data.csv and save figure.png."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# Palette (light mode, reference dataviz palette)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
ACCENT = "#2a78d6"
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

N_HIGHLIGHT = 3  # heads called out by name
Z = 1.96  # 95% CI from the SEM

df = pd.read_csv("data.csv")
df[["layer", "head"]] = df[["layer", "head"]].astype(int)
n_layers = df["layer"].max() + 1
n_heads = df["head"].max() + 1
grid = df.pivot(index="layer", columns="head", values="loss_increase").to_numpy()
n_prompts = df["n_prompts"].iloc[0]

ranked = df.sort_values("loss_increase", ascending=False).reset_index(drop=True)
top = ranked.head(N_HIGHLIGHT)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "axes.edgecolor": BASELINE,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
})

fig, (ax_map, ax_rank) = plt.subplots(
    1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.35], "wspace": 0.28}
)

# (a) Heatmap: layer x head, one-hue sequential scale starting at 0.
cmap = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
vmax = np.nanmax(grid)
mesh = ax_map.pcolormesh(
    np.clip(grid, 0, None), cmap=cmap, vmin=0, vmax=vmax,
    edgecolors=SURFACE, linewidth=1.5,
)
ax_map.set_xlim(0, n_heads)
ax_map.set_ylim(n_layers, 0)  # layer 0 at the top
ax_map.set_aspect("equal")
ax_map.set_xticks(np.arange(n_heads) + 0.5, range(n_heads))
ax_map.set_yticks(np.arange(n_layers) + 0.5, range(n_layers))
ax_map.tick_params(length=0)
for side in ax_map.spines.values():
    side.set_visible(False)
ax_map.set_xlabel("Head")
ax_map.set_ylabel("Layer")
ax_map.set_title("a   Loss increase per ablated head", loc="left", fontsize=10, fontweight="bold")
for r in top.itertuples():
    ax_map.text(r.head + 0.5, r.layer + 0.5, f"{r.loss_increase:.2f}",
                ha="center", va="center", fontsize=6.5, color="#ffffff", fontweight="bold")
cbar = fig.colorbar(mesh, ax=ax_map, fraction=0.046, pad=0.03)
cbar.set_label("Loss increase")
cbar.outline.set_visible(False)
cbar.ax.tick_params(length=0)

# (b) All heads ranked, with 95% CIs; the top heads are emphasized, the rest gray.
x = np.arange(len(ranked)) + 1
is_top = x <= N_HIGHLIGHT
ax_rank.axhline(0, color=BASELINE, linewidth=1, zorder=1)
ax_rank.errorbar(x[~is_top], ranked["loss_increase"][~is_top], yerr=Z * ranked["sem"][~is_top],
                 fmt="o", ms=3, color=MUTED, ecolor=GRID, elinewidth=1, capsize=0, zorder=2)
ax_rank.errorbar(x[is_top], ranked["loss_increase"][is_top], yerr=Z * ranked["sem"][is_top],
                 fmt="o", ms=6, color=ACCENT, ecolor=ACCENT, elinewidth=1.5, capsize=0,
                 markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
for i, r in enumerate(top.itertuples()):
    ax_rank.annotate(f"L{r.layer}.H{r.head}  ({r.loss_increase:.2f})",
                     (i + 1, r.loss_increase), xytext=(9, 0), textcoords="offset points",
                     va="center", fontsize=8.5, color=INK)
ax_rank.set_xlim(-2, len(ranked) + 3)
ax_rank.set_xticks([1, 25, 50, 75, 100, 125, len(ranked)])
ax_rank.set_xlabel("Head rank (by loss increase)")
ax_rank.set_ylabel("Loss increase (± 95% CI)")
ax_rank.yaxis.grid(True, color=GRID, linewidth=0.75)
ax_rank.set_axisbelow(True)
for side in ("top", "right"):
    ax_rank.spines[side].set_visible(False)
ax_rank.tick_params(length=0)
rest = ranked.iloc[N_HIGHLIGHT:]
ax_rank.text(0.97, 0.16,
             f"Remaining {len(rest)} heads: {rest['loss_increase'].min():.3f} to "
             f"{rest['loss_increase'].max():.3f}",
             transform=ax_rank.transAxes, ha="right", fontsize=8.5, color=INK_2)
ax_rank.set_title(f"b   All {len(ranked)} heads, ranked (n = {n_prompts} prompts)",
                  loc="left", fontsize=10, fontweight="bold")

# Match panel b's plot area to the (aspect-constrained) heatmap so the panels align.
fig.canvas.draw()
pm, pr = ax_map.get_position(), ax_rank.get_position()
ax_rank.set_position([pr.x0, pm.y0, pr.width, pm.height])

fig.savefig("figure.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
