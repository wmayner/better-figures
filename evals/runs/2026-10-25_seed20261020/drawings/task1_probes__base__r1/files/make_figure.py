"""Plot layer-wise probe accuracy per concept and mark where each becomes decodable.

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.png.

"Decodable" onset = the (linearly interpolated) layer at which probe accuracy
first crosses THRESHOLD, halfway between chance and perfect accuracy.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data.csv"
OUT = HERE / "figure.png"

CHANCE = 0.5
THRESHOLD = 0.75

# Concepts in order of onset; colors are fixed categorical slots 1-4.
CONCEPTS = [
    ("part of speech", "#2a78d6"),
    ("sentiment", "#eb6834"),
    ("named entity type", "#1baf7a"),
    ("statement truthfulness", "#eda100"),
]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"


def onset_layer(layers, acc, threshold):
    """First layer where acc crosses threshold, interpolated between layers."""
    above = np.nonzero(acc >= threshold)[0]
    if len(above) == 0:
        return None
    i = above[0]
    if i == 0:
        return float(layers[0])
    x0, x1, y0, y1 = layers[i - 1], layers[i], acc[i - 1], acc[i]
    return float(x0 + (threshold - y0) / (y1 - y0) * (x1 - x0))


def main():
    df = pd.read_csv(DATA).sort_values(["concept", "layer"])

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
    })

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Reference lines: chance and the onset threshold.
    ax.axhline(CHANCE, color=AXIS, lw=1, zorder=1)
    ax.axhline(THRESHOLD, color=MUTED, lw=1, ls=(0, (1, 2)), zorder=1)
    ax.text(23.4, CHANCE + 0.008, "chance", color=MUTED, fontsize=8.5,
            ha="right", va="bottom")
    ax.text(11.2, THRESHOLD + 0.008, f"onset threshold ({THRESHOLD:.0%})",
            color=MUTED, fontsize=8.5, ha="center", va="bottom")

    for concept, color in CONCEPTS:
        d = df[df["concept"] == concept]
        x = d["layer"].to_numpy()
        y = d["accuracy"].to_numpy()

        ax.fill_between(x, d["ci_low"], d["ci_high"], color=color, alpha=0.15,
                        lw=0, zorder=2)
        ax.plot(x, y, color=color, lw=2, solid_joinstyle="round",
                solid_capstyle="round", zorder=3, label=concept)

        xo = onset_layer(x, y, THRESHOLD)
        if xo is None:
            continue
        ax.plot([xo, xo], [CHANCE, THRESHOLD], color=color, lw=1, alpha=0.6,
                zorder=2)
        ax.scatter([xo], [THRESHOLD], s=56, color=color, edgecolor=SURFACE,
                   linewidth=2, zorder=5)
        name = concept.replace("statement ", "statement\n")
        ax.annotate(f"{name}\nlayer {xo:.1f}",
                    xy=(xo, THRESHOLD), xytext=(xo + 0.45, THRESHOLD - 0.025),
                    ha="left", va="top",
                    fontsize=8.5, color=INK, linespacing=1.2, zorder=6)

    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0.44, 1.0)
    ax.set_xticks(range(0, 24, 2))
    ax.set_yticks(np.arange(0.5, 1.01, 0.1))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Layer")
    ax.set_ylabel("Probe accuracy")

    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="both", length=0, pad=6)

    ax.set_title("Concepts become decodable at successively deeper layers",
                 loc="left", color=INK, fontsize=12, fontweight="semibold",
                 pad=28)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4,
                    frameon=False, fontsize=9, handlelength=1.6,
                    columnspacing=1.6, borderaxespad=0.3)
    for text in leg.get_texts():
        text.set_color(INK_2)

    fig.tight_layout()
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
