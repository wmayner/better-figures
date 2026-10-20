"""Plot the increase in loss from ablating each attention head.

Reads data.csv (columns: layer, head, loss_increase, sem, n_prompts) and writes
figure.png with two panels:
  (a) a layer x head heatmap showing where the important heads are, and
  (b) every head ranked by loss increase with 95% confidence intervals,
      showing how far the top heads stand above the rest.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
DATA = HERE / "data.csv"
OUT = HERE / "figure.png"

N_HIGHLIGHT = 3  # number of top heads to label and highlight
Z95 = 1.96

# Palette: one-hue sequential blue ramp, plus neutral inks.
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
HIGHLIGHT = "#2a78d6"
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "axes.titlecolor": INK,
    "axes.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_SECONDARY,
    "ytick.labelcolor": INK_SECONDARY,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def head_label(layer, head):
    return f"L{int(layer)}H{int(head)}"


def main():
    df = pd.read_csv(DATA)
    n_layers = df["layer"].max() + 1
    n_heads = df["head"].max() + 1
    grid = df.pivot(index="layer", columns="head", values="loss_increase")
    grid = grid.reindex(index=range(n_layers), columns=range(n_heads))

    ranked = df.sort_values("loss_increase", ascending=False).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    top = ranked.head(N_HIGHLIGHT)
    rest = ranked.iloc[N_HIGHLIGHT:]

    fig, (ax_map, ax_rank) = plt.subplots(
        1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.28}
    )

    # (a) Heatmap: layer x head, linear sequential scale from 0.
    cmap = LinearSegmentedColormap.from_list("blue_seq", BLUE_RAMP)
    vmax = df["loss_increase"].max()
    mesh = ax_map.pcolormesh(
        np.arange(n_heads + 1) - 0.5,
        np.arange(n_layers + 1) - 0.5,
        grid.values,
        cmap=cmap,
        vmin=0,
        vmax=vmax,
        edgecolors=SURFACE,
        linewidth=1.5,
    )
    ax_map.set_xlim(-0.5, n_heads - 0.5)
    ax_map.set_ylim(n_layers - 0.5, -0.5)  # layer 0 at top
    ax_map.set_aspect("equal")
    ax_map.set_xticks(range(n_heads))
    ax_map.set_yticks(range(n_layers))
    ax_map.tick_params(length=0)
    for side in ax_map.spines.values():
        side.set_visible(False)
    ax_map.set_xlabel("Head")
    ax_map.set_ylabel("Layer")

    for _, r in top.iterrows():
        val = r["loss_increase"]
        ax_map.text(
            r["head"], r["layer"], f"{val:.2f}",
            ha="center", va="center", fontsize=6,
            color="white" if val > 0.45 * vmax else INK,
        )

    cbar = fig.colorbar(mesh, ax=ax_map, fraction=0.046, pad=0.03)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(length=0, labelsize=8)
    cbar.set_label("Loss increase", color=INK_SECONDARY)

    # (b) All heads ranked, with 95% CIs.
    ax_rank.axhline(0, color=BASELINE, linewidth=0.8, zorder=1)
    ax_rank.grid(axis="y", color=GRID, linewidth=0.6)
    ax_rank.set_axisbelow(True)
    ax_rank.errorbar(
        rest["rank"], rest["loss_increase"], yerr=Z95 * rest["sem"],
        fmt="o", ms=2, color=MUTED, ecolor=BASELINE, elinewidth=0.7, capsize=0, zorder=2,
    )
    ax_rank.errorbar(
        top["rank"], top["loss_increase"], yerr=Z95 * top["sem"],
        fmt="o", ms=5, color=HIGHLIGHT, ecolor=HIGHLIGHT, elinewidth=1.2, capsize=0,
        zorder=3, markeredgecolor=SURFACE, markeredgewidth=1,
    )
    for _, r in top.iterrows():
        ax_rank.annotate(
            f"{head_label(r['layer'], r['head'])}  {r['loss_increase']:.2f}",
            (r["rank"], r["loss_increase"]),
            xytext=(8, 0), textcoords="offset points",
            ha="left", va="center", fontsize=8.5, color=INK,
        )
    tail_max = rest["loss_increase"].max()
    tail_median = rest["loss_increase"].median()
    ax_rank.annotate(
        f"Remaining {len(rest)} heads\nmedian {tail_median:.3f}, max {tail_max:.3f}",
        (len(ranked) * 0.55, tail_max), xytext=(0, 28), textcoords="offset points",
        ha="center", va="bottom", fontsize=8.5, color=INK_SECONDARY,
    )
    ax_rank.set_xlim(-2, len(ranked) + 3)
    ax_rank.set_ylim(-0.08, vmax * 1.15)
    ax_rank.set_xlabel("Head rank (by loss increase)")
    ax_rank.set_ylabel("Loss increase (mean ± 95% CI)")
    for side in ("top", "right"):
        ax_rank.spines[side].set_visible(False)
    ax_rank.tick_params(length=3, color=BASELINE)

    # Panel titles on a shared baseline (the heatmap axes is shorter because
    # of its equal aspect ratio).
    fig.canvas.draw()
    title_y = max(ax_map.get_position().y1, ax_rank.get_position().y1) + 0.04
    for ax, title in [
        (ax_map, "(a) Loss increase by layer and head"),
        (ax_rank, f"(b) All {len(ranked)} heads, ranked"),
    ]:
        fig.text(ax.get_position().x0, title_y, title, fontsize=10, color=INK, ha="left")

    fig.savefig(OUT, dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main()
