"""Plot agreement between attribution methods and head ablation.

Reads data.csv and writes figure.png: a dot plot of Spearman correlation
(with confidence intervals) between each method's head scores and the
ablation effect, one row per method, one marker per model.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data.csv"
OUT = HERE / "figure.png"

# Chart chrome and categorical slots 1-3 (validated all-pairs for CVD).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
MODEL_STYLE = {
    "GPT-2 small": dict(color="#2a78d6", marker="o"),
    "Pythia-410M": dict(color="#eb6834", marker="s"),
    "Gemma-2-2B": dict(color="#1baf7a", marker="D"),
}
DODGE = 0.22


def main():
    df = pd.read_csv(DATA)
    models = [m for m in MODEL_STYLE if m in set(df["model"])]

    # Best-agreeing method at the top.
    order = df.groupby("method")["spearman_r"].mean().sort_values().index.tolist()
    ypos = {m: i for i, m in enumerate(order)}

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
    })
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Faint band behind the top-ranked method.
    ax.axhspan(len(order) - 1.5, len(order) - 0.5, color="#f0efec", zorder=0, lw=0)

    for j, model in enumerate(models):
        sub = df[df["model"] == model]
        y = sub["method"].map(ypos) + (1 - j) * DODGE
        style = MODEL_STYLE[model]
        ax.hlines(y, sub["ci_low"], sub["ci_high"], color=style["color"],
                  lw=2, zorder=2)
        ax.scatter(sub["spearman_r"], y, s=46, marker=style["marker"],
                   color=style["color"], edgecolors=SURFACE, linewidths=1.5,
                   zorder=3,
                   label=f"{model} ({int(sub['n_heads'].iloc[0])} heads)")

    # Mean across models, labelled at the right edge of each row.
    means = df.groupby("method")["spearman_r"].mean()
    for method, y in ypos.items():
        ax.text(1.005, y, f"{means[method]:.2f}", transform=ax.get_yaxis_transform(),
                va="center", ha="left", color=INK_2, fontsize=9)
    ax.text(1.005, len(order) - 0.45, "mean ρ", transform=ax.get_yaxis_transform(),
            va="bottom", ha="left", color=MUTED, fontsize=8.5)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    for label in ax.get_yticklabels():
        label.set_color(INK)
        if label.get_text() == order[-1]:
            label.set_fontweight("bold")
    ax.set_ylim(-0.6, len(order) - 0.4)

    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("Spearman ρ between attribution score and ablation effect",
                  color=INK_2)
    ax.tick_params(axis="x", colors=MUTED, labelcolor=INK_2, length=0, pad=6)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=len(models),
              frameon=False, fontsize=9, handletextpad=0.3, columnspacing=1.4,
              labelcolor=INK_2)

    fig.tight_layout()
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
