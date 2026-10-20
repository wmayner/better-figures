"""Plot per-head ablation effects from data.csv and save figure.png.

Panel a: layer x head heatmap of the mean increase in loss (linear color scale).
Panel b: the top-ranked heads with 95% confidence intervals (mean +/- 1.96 SEM).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import norm

DATA_PATH = "data.csv"
OUT_PATH = "figure.png"
N_RANKED = 15  # heads shown in panel b
N_HIGHLIGHT = 3  # heads called out as dominant
ALPHA = 0.05

# Palette (light mode).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
ACCENT = "#256abf"
BLUE_RAMP = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
             "#256abf", "#184f95", "#0d366b"]

df = pd.read_csv(DATA_PATH)
df["z"] = df["loss_increase"] / df["sem"]
n_layers = df["layer"].max() + 1
n_heads = df["head"].max() + 1
grid = df.pivot(index="layer", columns="head", values="loss_increase").to_numpy()

# Two-sided z-test against zero, Bonferroni-corrected across all heads.
z_crit = norm.isf(ALPHA / (2 * len(df)))
df["significant"] = df["z"] > z_crit
ranked = df.sort_values("loss_increase", ascending=False).reset_index(drop=True)
top_keys = set(zip(ranked["layer"].head(N_HIGHLIGHT),
                   ranked["head"].head(N_HIGHLIGHT)))

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

fig, (ax_a, ax_b) = plt.subplots(
    1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [1.15, 1]},
    layout="constrained",
)

# --- Panel a: heatmap -------------------------------------------------------
cmap = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
vmax = np.ceil(grid.max() * 10) / 10
im = ax_a.imshow(grid, cmap=cmap, vmin=0, vmax=vmax, origin="upper",
                 aspect="equal", interpolation="nearest")

# Surface-colored gaps between cells.
ax_a.set_xticks(np.arange(-0.5, n_heads), minor=True)
ax_a.set_yticks(np.arange(-0.5, n_layers), minor=True)
ax_a.grid(which="minor", color=SURFACE, linewidth=2)
ax_a.tick_params(which="minor", length=0)
ax_a.tick_params(which="major", length=0)
for spine in ax_a.spines.values():
    spine.set_visible(False)

ax_a.set_xticks(range(n_heads))
ax_a.set_yticks(range(n_layers))
ax_a.set_xlabel("Head")
ax_a.set_ylabel("Layer")

# Value labels on the dominant heads; a dot on other significant heads.
for _, r in df.iterrows():
    if (r["layer"], r["head"]) in top_keys:
        ax_a.text(r["head"], r["layer"], f"{r['loss_increase']:.2f}",
                  ha="center", va="center", fontsize=7, color=SURFACE,
                  fontweight="bold")
    elif r["significant"]:
        ax_a.plot(r["head"], r["layer"], "o", ms=3.5, color=INK_2,
                  markeredgewidth=0)

cbar = fig.colorbar(im, ax=ax_a, shrink=0.8, pad=0.02)
cbar.ax.set_title("Loss\nincrease", fontsize=8, color=INK_2, loc="left")
cbar.outline.set_visible(False)
cbar.ax.tick_params(length=0)

ax_a.plot([], [], "o", ms=3.5, color=INK_2, markeredgewidth=0,
          label=f"Significant after Bonferroni correction (p < {ALPHA})")
ax_a.legend(loc="upper left", bbox_to_anchor=(0, -0.11), frameon=False,
            fontsize=8, labelcolor=INK_2, handletextpad=0.3, borderaxespad=0)

ax_a.set_title("a   Loss increase when each head is ablated",
               loc="left", fontsize=10, color=INK, fontweight="bold")

# --- Panel b: ranked heads with 95% CIs -------------------------------------
shown = ranked.head(N_RANKED).iloc[::-1]  # largest at top
y = np.arange(len(shown))
half_width = norm.isf(ALPHA / 2) * shown["sem"].to_numpy()
is_top = shown.index.to_numpy() < N_HIGHLIGHT
colors = np.where(is_top, ACCENT, MUTED)

ax_b.hlines(y, shown["loss_increase"] - half_width,
            shown["loss_increase"] + half_width, color=colors, linewidth=2)
ax_b.scatter(shown["loss_increase"], y, s=28, c=colors, zorder=3,
             edgecolors=SURFACE, linewidths=0.8)

labels = [f"L{l}H{h}" for l, h in zip(shown["layer"], shown["head"])]
ax_b.set_yticks(y, labels)
for tick, hl in zip(ax_b.get_yticklabels(), is_top):
    tick.set_color(INK if hl else INK_2)
    tick.set_fontweight("bold" if hl else "normal")

for yi, (_, r) in zip(y[is_top], shown[is_top].iterrows()):
    ax_b.text(r["loss_increase"] + norm.isf(ALPHA / 2) * r["sem"] + 0.03, yi,
              f"{r['loss_increase']:.2f}", va="center", fontsize=8, color=INK)

ax_b.axvline(0, color=BASELINE, linewidth=1, zorder=0)
ax_b.set_xlim(-0.05, vmax + 0.15)
ax_b.set_ylim(-0.7, len(shown) - 0.3)
ax_b.set_xlabel("Increase in loss (mean ± 95% CI)")
ax_b.grid(axis="x", color=GRID, linewidth=0.6)
ax_b.set_axisbelow(True)
ax_b.tick_params(length=0)
for side in ("top", "right", "left"):
    ax_b.spines[side].set_visible(False)
ax_b.spines["bottom"].set_color(BASELINE)

ax_b.set_title(f"b   Top {N_RANKED} of {len(df)} heads, ranked",
               loc="left", fontsize=10, color=INK, fontweight="bold")

fig.savefig(OUT_PATH, dpi=200)
print(f"Saved {OUT_PATH}")
