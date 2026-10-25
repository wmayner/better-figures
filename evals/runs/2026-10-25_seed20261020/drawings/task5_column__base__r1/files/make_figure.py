"""Layer-wise probe accuracy for four concepts, sized for one column (3.25 in).

Reads data.csv (concept, layer, accuracy, ci_low, ci_high, n_test_examples)
and writes figure.pdf and figure.png next to this script.

Onset ("becomes decodable") is defined as the first layer at which probe
accuracy reaches the half-way point between chance and that concept's peak
accuracy, and stays at or above it for every later layer.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
CHANCE = 0.5  # binary probes; layer-0 accuracy sits at ~0.5 for every concept

# Categorical slots in fixed order, assigned by onset order (earliest first).
# Each color is paired with a distinct marker shape (on the curve and in the
# legend) so identity never rests on hue alone (slot 4 yellow is close to
# slot 2 orange under CVD).
SERIES = [
    # concept,                 label,           color,     marker
    ("part of speech",         "Part of speech", "#2a78d6", "o"),
    ("sentiment",              "Sentiment",      "#eb6834", "s"),
    ("named entity type",      "Entity type",    "#1baf7a", "D"),
    ("statement truthfulness", "Truthfulness",   "#eda100", "^"),
]

INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 7,
    "axes.labelsize": 7,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "pdf.fonttype": 42,  # embed TrueType so text stays editable/searchable
    "ps.fonttype": 42,
})


def onset_layer(df):
    """First layer where accuracy reaches the half-max threshold and stays there."""
    df = df.sort_values("layer")
    thresh = CHANCE + (df["accuracy"].max() - CHANCE) / 2
    above = (df["accuracy"] >= thresh).to_numpy()
    # stays above: every layer from i onward is above threshold
    stays = above[::-1].cumprod()[::-1].astype(bool)
    i = stays.argmax()
    return int(df["layer"].iloc[i]), float(df["accuracy"].iloc[i]), thresh


def main():
    data = pd.read_csv(HERE / "data.csv")
    missing = {c for c, *_ in SERIES} - set(data["concept"])
    if missing:
        raise ValueError(f"concepts not found in data.csv: {sorted(missing)}")

    fig, ax = plt.subplots(figsize=(3.25, 2.35))

    ax.axhline(CHANCE, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.text(23.4, CHANCE + 0.008, "chance", color=MUTED, fontsize=6,
            ha="right", va="bottom")

    handles = []
    for concept, label, color, marker in SERIES:
        d = data[data["concept"] == concept].sort_values("layer")
        x = d["layer"].to_numpy()
        ax.fill_between(x, d["ci_low"], d["ci_high"], color=color,
                        alpha=0.18, lw=0, zorder=2)
        ax.plot(x, d["accuracy"], color=color, lw=1.3, zorder=3,
                solid_capstyle="round")

        # Onset marker on the curve, with its layer number to the lower right
        # (below the curve, where it has already risen past this point).
        layer, acc, _ = onset_layer(d)
        ax.plot(layer, acc, marker=marker, ms=4.5, color=color,
                mec="white", mew=0.8, zorder=4, ls="none")
        ax.annotate(str(layer), (layer, acc), xytext=(4, -3),
                    textcoords="offset points", ha="left", va="top",
                    fontsize=6.5, color=INK, zorder=5)

        # Legend shows line + marker so identity doesn't rest on hue alone.
        handles.append(plt.Line2D([], [], color=color, lw=1.3, marker=marker,
                                  ms=4, mec="white", mew=0.6, label=label))

    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=2, frameon=False, fontsize=6.5, handlelength=1.8,
              handletextpad=0.5, columnspacing=1.5, labelspacing=0.3,
              borderaxespad=0.3, borderpad=0, labelcolor=INK)

    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0.45, 1.0)
    ax.set_xticks(range(0, 24, 4))
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticklabels(["50%", "60%", "70%", "80%", "90%", "100%"])
    ax.set_xlabel("Layer")
    ax.set_ylabel("Probe accuracy")
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.tight_layout(pad=0.3)
    fig.savefig(HERE / "figure.pdf")
    fig.savefig(HERE / "figure.png", dpi=300)

    for concept, label, *_ in SERIES:
        d = data[data["concept"] == concept]
        layer, acc, thresh = onset_layer(d)
        print(f"{label:15s} onset layer {layer:2d}  "
              f"(acc {acc:.3f}, threshold {thresh:.3f}, "
              f"peak {d['accuracy'].max():.3f})")


if __name__ == "__main__":
    main()
