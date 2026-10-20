"""Side by side: the r1 figures for task 3 from plain Claude Code and from Claude Code with better-figures.

usage: python results/before_after.py runs/2026-10-20_seed20261020
The r1 runs are used whatever they look like; they were not chosen for looks.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "skills" / "figures"))
import figkit as fk  # noqa: E402

run_dir = Path(sys.argv[1]).resolve()
panels = [("Claude Code", run_dir / "drawings" / "task3_attribution__base__r1" / "files" / "figure.png"),
          ("with better-figures", run_dir / "drawings" / "task3_attribution__plugin__r1" / "files" / "figure.png")]
images = [mpimg.imread(p) for _, p in panels]
ratios = [im.shape[1] / im.shape[0] for im in images]

fk.use()
fig, axs = plt.subplots(1, 2, figsize=(14, 14 / sum(ratios) + 0.6), width_ratios=ratios)
for ax, (name, _), im, colour in zip(axs, panels, images, (fk.MUTED, fk.ACCENT)):
    ax.imshow(im)
    ax.set_axis_off()
    ax.set_title(name, color=colour, fontsize=16)
fig.savefig(HERE / "before_after_task3.png", dpi=150)
