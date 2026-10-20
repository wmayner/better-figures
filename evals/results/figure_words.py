"""Dot plot: words in each run's figure outside tick labels, by task, plain Claude Code against with better-figures.

usage: python results/figure_words.py runs/2026-10-20_seed20261020
Reads <run_dir>/per_run.csv; writes results/figure_words_data.csv (the plotted values) and results/figure_words.png.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "skills" / "figures"))
import figkit as fk  # noqa: E402

TASKS = {"task1_probes": "Probe accuracy by layer", "task2_heads": "Effect of ablating heads",
         "task3_attribution": "Attribution against ablation"}
ARMS = {"base": ("Claude Code", fk.GREY, 0.14), "plugin": ("with better-figures", fk.ACCENT, -0.14)}

run_dir = Path(sys.argv[1]).resolve()
df = pd.read_csv(run_dir / "per_run.csv")[["run", "task", "arm", "rep", "words"]]
df["task_name"] = df["task"].map(TASKS)
df["series"] = df["arm"].map(lambda a: ARMS[a][0])
df.to_csv(HERE / "figure_words_data.csv", index=False)

fk.use()
fig, ax = plt.subplots(figsize=(7, 3.2))
rows = {t: i for i, t in enumerate(reversed(list(TASKS)))}  # first task at the top
for arm, (name, colour, dy) in ARMS.items():
    d = df[df.arm == arm]
    stagger = (d.rep - 1.5) * 0.08  # the two runs of a task sit slightly apart, so equal counts stay visible
    ax.scatter(d.words, d.task.map(rows) + dy + stagger, s=70, color=colour, zorder=3, edgecolor="white", linewidth=0.8)
    top = d[d.task == next(iter(TASKS))]
    ax.annotate(name, (top.words.max(), rows[next(iter(TASKS))] + dy), xytext=(10, 0), textcoords="offset points",
                va="center", color=colour if arm == "plugin" else fk.MUTED, fontsize=12)
ax.set_xscale("log")
ax.set_xticks([5, 10, 20, 50, 100])
fk.plain_ticks(ax.xaxis)
ax.set_yticks(list(rows.values()), [TASKS[t] for t in rows])
ax.set_ylim(-0.6, len(TASKS) - 0.4)
lo, hi = df.words.min(), df.words.max()
ax.set_xlim(4, hi * 3.2)
ax.grid(axis="x", which="major", color="#ECECEC")
ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_xlabel("Words in the figure (log scale)")
fk.save(fig, HERE / "figure_words.png")
fig.savefig(HERE / "figure_words.pdf")
