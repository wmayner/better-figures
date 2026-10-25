"""Plot linear-probe accuracy by layer for each concept and mark where it becomes decodable.

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.png.

"Becomes decodable" = the first layer from which the lower confidence bound
(ci_low) stays above chance (50%) at every later layer.
"""

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
CHANCE = 0.5
LABEL_Y = 0.75  # accuracy at which each curve is direct-labeled

# Categorical slots 1-4, in fixed order (assigned by order of emergence).
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"


def onset_layer(g: pd.DataFrame) -> int | None:
    """First layer from which ci_low > chance holds for all later layers."""
    above = (g["ci_low"] > CHANCE).to_numpy()
    for i in range(len(above)):
        if above[i:].all():
            return int(g["layer"].iloc[i])
    return None


def main() -> None:
    df = pd.read_csv(HERE / "data.csv").sort_values(["concept", "layer"])
    groups = {c: g.reset_index(drop=True) for c, g in df.groupby("concept")}
    onsets = {c: onset_layer(g) for c, g in groups.items()}
    order = sorted(groups, key=lambda c: (onsets[c] is None, onsets[c] or 0))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
    })
    fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.axhline(CHANCE, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(df["layer"].max(), CHANCE - 0.012, "chance", color=MUTED,
            ha="right", va="top", fontsize=9)

    for color, concept in zip(COLORS, order):
        g = groups[concept]
        ax.fill_between(g["layer"], g["ci_low"], g["ci_high"],
                        color=color, alpha=0.18, lw=0, zorder=2)
        ax.plot(g["layer"], g["accuracy"], color=color, lw=2,
                solid_capstyle="round", label=concept, zorder=3)

        on = onsets[concept]
        if on is None:
            continue
        acc = g.loc[g["layer"] == on, "accuracy"].item()
        ax.plot(on, acc, "o", ms=7, color=color, mec=SURFACE, mew=2, zorder=4)

        # Direct label in the open space just left of the curve's rise.
        x_mid = np.interp(LABEL_Y, g["accuracy"].cummax(), g["layer"])
        ax.annotate(textwrap.fill(concept, 12), (x_mid, LABEL_Y),
                    xytext=(-8, 6), textcoords="offset points",
                    ha="right", va="bottom", fontsize=9, color=INK,
                    fontweight="semibold", linespacing=1.1)
        ax.annotate(f"from layer {on}", (x_mid, LABEL_Y),
                    xytext=(-8, 2), textcoords="offset points",
                    ha="right", va="top", fontsize=8.5, color=INK_2)

    ax.set_xlim(-0.5, df["layer"].max() + 0.5)
    ax.set_ylim(0.44, 1.0)
    ax.set_xticks(range(0, df["layer"].max() + 1, 2))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("Layer", color=INK_2)
    ax.set_ylabel("Probe accuracy (held-out)", color=INK_2)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, length=0, pad=4)

    ax.set_title("Concepts become linearly decodable at different depths",
                 loc="left", color=INK, fontsize=12, fontweight="semibold",
                 pad=26)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4,
              frameon=False, fontsize=9, labelcolor=INK_2,
              handlelength=1.6, columnspacing=1.4, borderaxespad=0.2)

    fig.tight_layout()
    fig.savefig(HERE / "figure.png", facecolor=SURFACE)

    for c in order:
        print(f"{c:>24}: decodable from layer {onsets[c]}")


if __name__ == "__main__":
    main()
