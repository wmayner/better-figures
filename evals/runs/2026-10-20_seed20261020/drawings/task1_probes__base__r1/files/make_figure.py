"""Plot linear-probe accuracy by layer for each concept and mark where it becomes decodable.

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.png.
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data.csv"
FIG_PATH = HERE / "figure.png"

# All four probes sit at ~0.50 in the earliest layers, i.e. binary chance.
CHANCE = 0.5
# A concept counts as "decodable" from the first layer at which probe accuracy
# reaches the halfway point between chance and perfect accuracy.
THRESHOLD = 0.75

# Colors are tied to the concept, not to its rank (categorical slots 1-4).
COLORS = {
    "part of speech": "#2a78d6",
    "sentiment": "#eb6834",
    "named entity type": "#1baf7a",
    "statement truthfulness": "#eda100",
}

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"


def onset_layer(group: pd.DataFrame) -> int:
    """First layer from which accuracy stays at or above THRESHOLD for all deeper layers."""
    group = group.sort_values("layer")
    above = (group["accuracy"] >= THRESHOLD).to_numpy()
    layers = group["layer"].to_numpy()
    for i in range(len(layers)):
        if above[i:].all():
            return int(layers[i])
    raise ValueError(f"{group['concept'].iloc[0]!r} never stays above {THRESHOLD}")


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    missing = set(df["concept"]) - set(COLORS)
    if missing:
        raise ValueError(f"No color assigned for concepts: {sorted(missing)}")

    onsets = {c: onset_layer(g) for c, g in df.groupby("concept")}
    order = sorted(onsets, key=onsets.get)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 9,
            "axes.edgecolor": AXIS,
            "axes.labelcolor": INK_SECONDARY,
            "xtick.color": INK_MUTED,
            "ytick.color": INK_MUTED,
            "xtick.labelcolor": INK_SECONDARY,
            "ytick.labelcolor": INK_SECONDARY,
        }
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.4), facecolor=SURFACE, layout="constrained")
    ax.set_facecolor(SURFACE)

    # Reference lines: chance and the decodability threshold.
    ax.axhline(CHANCE, color=INK_MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.axhline(THRESHOLD, color=INK_MUTED, lw=1, ls=(0, (1, 2)), zorder=1)
    # Name the reference lines in the right margin, clear of the curves.
    for y, name in [(CHANCE, "chance"), (THRESHOLD, "threshold")]:
        ax.annotate(
            name,
            xy=(1, y),
            xycoords=("axes fraction", "data"),
            xytext=(4, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
            color=INK_MUTED,
        )

    for concept in order:
        g = df[df["concept"] == concept].sort_values("layer")
        color = COLORS[concept]
        onset = onsets[concept]
        ax.fill_between(g["layer"], g["ci_low"], g["ci_high"], color=color, alpha=0.18, lw=0, zorder=2)
        ax.plot(
            g["layer"],
            g["accuracy"],
            color=color,
            lw=2,
            solid_capstyle="round",
            label=f"{concept.capitalize()} (layer {onset})",
            zorder=3,
        )

        # Onset marker (with a surface-colored ring) and a direct label to its lower right,
        # which is empty because every curve rises from the lower left.
        y_onset = g.loc[g["layer"] == onset, "accuracy"].item()
        ax.plot(onset, y_onset, "o", ms=8, color=color, mec=SURFACE, mew=2, zorder=4)
        ax.annotate(
            f"{textwrap.fill(concept.capitalize(), 17)}\nlayer {onset}",
            xy=(onset, y_onset),
            xytext=(7, -7),
            textcoords="offset points",
            ha="left",
            va="top",
            bbox={"boxstyle": "square,pad=0.15", "fc": SURFACE, "ec": "none"},
            fontsize=8.5,
            color=INK,
            linespacing=1.15,
            zorder=5,
        )

    n_layers = df["layer"].max() + 1
    ax.set_xlim(-0.5, n_layers - 0.5)
    ax.set_ylim(0.4, 1.0)
    ax.set_xticks(range(0, n_layers, 2))
    ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("Layer")
    ax.set_ylabel("Probe accuracy (held-out)")
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.tick_params(length=3, width=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        ncol=2,
        frameon=False,
        fontsize=8,
        handlelength=1.6,
        columnspacing=1.2,
        borderaxespad=0,
        labelcolor=INK_SECONDARY,
    )

    fig.savefig(FIG_PATH, dpi=200, facecolor=SURFACE)
    print(f"Saved {FIG_PATH}")
    for concept in order:
        print(f"  {concept}: decodable from layer {onsets[concept]}")


if __name__ == "__main__":
    main()
