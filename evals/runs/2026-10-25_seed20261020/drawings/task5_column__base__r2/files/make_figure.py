"""Probe accuracy by layer for four concepts (single-column figure, 3.25 in wide).

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.pdf and figure.png next to this script.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent

CHANCE = 0.5
# A concept counts as "decodable" once probe accuracy reaches halfway between
# chance (0.5) and perfect (1.0).
THRESHOLD = 0.75

# Categorical slots 1-4 of the reference palette, in fixed order. Concepts are
# ordered by when they become decodable, so color, legend order, and the
# left-to-right order of the curves all agree.
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
# Onset markers double as a non-color cue (grayscale print, CVD).
MARKERS = ["o", "s", "^", "D"]

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#8a8984"
GRID = "#e4e3df"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 7,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5,
        "axes.edgecolor": INK_SECONDARY,
        "axes.labelcolor": INK,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        # Embed TrueType fonts (required by most camera-ready checkers).
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def threshold_crossing(layers, acc, threshold):
    """First layer (linearly interpolated) at which acc reaches threshold."""
    above = np.flatnonzero(acc >= threshold)
    if len(above) == 0:
        return None
    i = above[0]
    if i == 0:
        return float(layers[0])
    x0, x1, y0, y1 = layers[i - 1], layers[i], acc[i - 1], acc[i]
    return float(x0 + (threshold - y0) * (x1 - x0) / (y1 - y0))


def main():
    df = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])

    series = []
    for concept, g in df.groupby("concept", sort=False):
        layers = g["layer"].to_numpy()
        acc = g["accuracy"].to_numpy()
        onset = threshold_crossing(layers, acc, THRESHOLD)
        series.append((concept, g, onset))
    series.sort(key=lambda s: np.inf if s[2] is None else s[2])

    fig, ax = plt.subplots(figsize=(3.25, 2.4), layout="constrained")

    # Reference lines: chance and the decodability threshold.
    ax.axhline(CHANCE, color=INK_MUTED, lw=0.6, ls=(0, (2, 2)), zorder=1)
    ax.axhline(THRESHOLD, color=GRID, lw=0.6, zorder=0)
    xmax = df["layer"].max()
    ax.text(xmax + 0.3, CHANCE + 0.008, "chance", ha="right", va="bottom",
            fontsize=6, color=INK_MUTED)
    ax.text(-0.3, THRESHOLD + 0.008, "threshold", ha="left", va="bottom",
            fontsize=6, color=INK_MUTED)

    handles = []
    for (concept, g, onset), color, marker in zip(series, COLORS, MARKERS):
        x = g["layer"].to_numpy()
        ax.fill_between(x, g["ci_low"], g["ci_high"], color=color, alpha=0.18,
                        lw=0, zorder=2)
        ax.plot(x, g["accuracy"], color=color, lw=1.3, zorder=3,
                solid_capstyle="round")
        if onset is not None:
            ax.plot(onset, THRESHOLD, marker=marker, ms=4.5, mfc=color,
                    mec="white", mew=0.8, zorder=4)
            ax.text(onset + 0.45, THRESHOLD - 0.012, f"{onset:.1f}",
                    ha="left", va="top", fontsize=6, color=INK_SECONDARY)
        handles.append(Line2D([], [], color=color, lw=1.3, marker=marker,
                              ms=4.5, mfc=color, mec="white", mew=0.8,
                              label=concept))

    ax.set_xlim(-0.5, xmax + 0.5)
    ax.set_ylim(0.44, 1.0)
    ax.set_xticks(np.arange(0, xmax + 1, 4))
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("Layer")
    ax.set_ylabel("Probe accuracy")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.02),
              ncol=2, frameon=False, handlelength=1.8, handletextpad=0.5,
              columnspacing=1.0, borderaxespad=0, labelcolor=INK)

    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02)
    fig.savefig(HERE / "figure.pdf")
    fig.savefig(HERE / "figure.png", dpi=600)

    for concept, _, onset in series:
        print(f"{concept}: reaches {THRESHOLD} at layer {onset}")


if __name__ == "__main__":
    main()
