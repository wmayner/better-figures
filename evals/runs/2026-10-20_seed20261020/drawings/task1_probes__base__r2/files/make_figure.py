"""Plot probe accuracy by layer for each concept and mark where it becomes decodable.

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.png.

Onset criterion: the first layer from which the lower bound of the 95% CI
stays above chance at every later layer. Requiring it to *stay* above chance
keeps single-layer blips (e.g. sentiment at layer 1) from counting as onset.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data.csv"
OUT = HERE / "figure.png"

# Balanced binary probes: every concept sits at ~0.5 in the early layers.
CHANCE = 0.5

# Chart chrome and categorical slots 1-4 (reference palette, light mode).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

# Height at which each curve gets its direct label.
LABEL_Y = 0.76


def onset_layer(df):
    """First layer after which ci_low never drops back to chance or below."""
    df = df.sort_values("layer")
    above = (df["ci_low"] > CHANCE).to_numpy()
    for i in range(len(above)):
        if above[i:].all():
            return int(df["layer"].iloc[i])
    return None


def main():
    data = pd.read_csv(DATA)
    onsets = {c: onset_layer(g) for c, g in data.groupby("concept")}
    # Order series (and so colors and legend) by onset depth.
    concepts = sorted(onsets, key=lambda c: (onsets[c] is None, onsets[c]))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 10,
    })
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.axhline(CHANCE, color=MUTED, lw=1, zorder=1)
    ax.text(data["layer"].max() + 0.4, CHANCE + 0.004, "chance", color=MUTED,
            fontsize=9, va="bottom", ha="right")

    for concept, color in zip(concepts, SERIES):
        g = data[data["concept"] == concept].sort_values("layer")
        onset = onsets[concept]
        ax.fill_between(g["layer"], g["ci_low"], g["ci_high"], color=color,
                        alpha=0.15, lw=0, zorder=2)
        ax.plot(g["layer"], g["accuracy"], color=color, lw=2,
                solid_joinstyle="round", solid_capstyle="round", zorder=3,
                label=concept)
        if onset is None:
            continue
        acc = g.loc[g["layer"] == onset, "accuracy"].iloc[0]
        ax.plot(onset, acc, "o", ms=8, color=color, mec=SURFACE, mew=2,
                zorder=4)
        # Direct label in the empty space just left of where the curve
        # rises through LABEL_Y (between it and the earlier, higher curves).
        x_cross = np.interp(LABEL_Y, g["accuracy"].cummax(), g["layer"])
        ax.text(x_cross - 0.35, LABEL_Y, f"{concept}\nfrom layer {onset}",
                ha="right", va="center", fontsize=9, color=INK_2,
                linespacing=1.3, zorder=5)

    layers = data["layer"]
    ax.set_xlim(layers.min() - 0.5, layers.max() + 0.5)
    ax.set_ylim(0.45, 1.0)
    ax.set_xticks(range(layers.min(), layers.max() + 1, 2))
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelcolor=INK_2, length=0, pad=6)
    ax.set_xlabel("Layer", color=INK_2)
    ax.set_ylabel("Probe accuracy (held-out)", color=INK_2)

    fig.suptitle("Concepts become decodable at progressively deeper layers",
                 x=0.075, y=0.965, ha="left", fontsize=13, color=INK,
                 fontweight="semibold")
    leg = fig.legend(loc="upper left", bbox_to_anchor=(0.065, 0.925), ncol=4,
                     frameon=False, fontsize=9, handlelength=1.4,
                     columnspacing=1.4, handletextpad=0.5)
    for text in leg.get_texts():
        text.set_color(INK_2)

    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"Onset layers: {onsets}")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
