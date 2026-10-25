"""Count the words each run's figures carry outside tick labels, and collect cost and tokens per run.

usage: python measure.py <run_dir>          writes <run_dir>/measures.csv and measures.json (long format; _v2 if they exist)
       python measure.py --one <make_figure.py> <out.json>   (internal: measure one script)

Each run's make_figure.py is re-run in a scratch copy of its directory with Figure.savefig patched, so nothing is
written. For every PNG the script would save, it records the words in visible text objects other than tick labels
(axis labels, titles, legends, annotations, colorbar labels), the number of panels, and the problems that the
plugin's figkit.check reports. Adapted from the 15 October 2026 test's counter.

Added for the 25 October 2026 run, alongside the unchanged word count: the title (the figure's suptitle, or a
single panel's title), the words outside the title, tick labels and numbers (figkit's count, since values and
counts are allowed in the image from version 0.3.0), the figure's size and smallest font, and the colours each
label is drawn in (from labelled marks, legends and coloured direct labels), for the colour-consistency task.
A run with several figure scripts (make_figure1.py, ...) gets one row per figure.
"""
import contextlib
import io
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVALS = Path(__file__).resolve().parent
TICK_TOLERANCE = 1e-9


def measure_script(script, out):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.text import Text

    sys.path.insert(0, str(EVALS.parent / "skills" / "figures"))
    import figkit

    records = []

    def load(fig):
        fig.canvas.draw()
        hidden, ticks = set(), set()
        for a in fig.axes:
            for ax_, i in ((a.xaxis, 0), (a.yaxis, 1)):
                lo, hi = sorted(ax_.get_view_interval())
                tol = TICK_TOLERANCE * abs(hi - lo)
                for t in ax_.get_ticklabels(which="both"):
                    (ticks if lo - tol <= t.get_position()[i] <= hi + tol else hidden).add(t)
                ticks.add(ax_.get_offset_text())
        texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and t not in hidden]
        free = [t.get_text() for t in texts if t not in ticks]
        tick_text = [t.get_text() for t in texts if t in ticks]
        axes = [a for a in fig.axes if a.get_label() != "<colorbar>"]
        sup = getattr(fig, "_suptitle", None)
        titles = [sup] if sup is not None and sup.get_text().strip() else []
        if len(axes) == 1 and not titles:
            titles = [t for t in (axes[0]._left_title, axes[0].title, axes[0]._right_title) if t.get_text().strip()]
        body = [t for t in texts if t not in ticks and t not in titles]
        w, h = fig.get_size_inches()
        return dict(words=sum(len(s.split()) for s in free), n_text=len(free), panels=len(axes),
                    free_text=free, tick_words=sum(len(s.split()) for s in tick_text),
                    title=" | ".join(t.get_text() for t in titles),
                    words_body=sum(figkit._words(t.get_text()) for t in body),
                    fig_width_in=float(w), fig_height_in=float(h),
                    min_font_pt=float(min((t.get_fontsize() for t in texts), default=0)),
                    label_colors=label_colors(fig))

    def label_colors(fig):
        """{label: [colours]} from labelled marks, unlabelled dots sitting on a category's tick, legend entries, and
        text drawn in a colour (direct labels)."""
        import matplotlib.colors as mc
        from matplotlib.collections import PathCollection
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        out = {}

        def add(label, color):
            lab = " ".join(str(label).lower().split())
            if lab and not lab.startswith("_"):
                out.setdefault(lab, set()).add(mc.to_hex(color))

        for a in fig.axes:
            for lab, _shown, set_ in figkit._marks(a):
                add(lab, set_)
            ticks = [(t.get_position()[0], t.get_text()) for t in a.xaxis.get_ticklabels() if t.get_text().strip()]
            for coll in a.collections:  # dots drawn without a label, all within half a category of one tick
                if not isinstance(coll, PathCollection) or not len(coll.get_offsets()) or not len(coll.get_facecolor()):
                    continue
                xs = [o[0] for o in coll.get_offsets()]
                near = [lab for pos, lab in ticks if all(abs(x - pos) < 0.45 for x in xs)]
                L, a_, b_ = figkit.lab(coll.get_facecolor()[0])
                if len(near) == 1 and not (L < 25 and (a_ * a_ + b_ * b_) ** 0.5 < 8):  # black dots mark points, not a condition
                    add(near[0], coll.get_facecolor()[0])
        for lg in [a.get_legend() for a in fig.axes if a.get_legend()] + list(fig.legends):
            for txt, hd in zip(lg.get_texts(), lg.legend_handles):
                if isinstance(hd, Line2D):
                    add(txt.get_text(), hd.get_color())
                elif isinstance(hd, Patch):
                    add(txt.get_text(), hd.get_facecolor())
                elif isinstance(hd, PathCollection) and len(hd.get_facecolor()):
                    add(txt.get_text(), hd.get_facecolor()[0])
        for t in fig.findobj(Text):
            _L, a_, b_ = figkit.lab(t.get_color())
            if t.get_visible() and t.get_text().strip() and (a_ * a_ + b_ * b_) ** 0.5 > 15:
                add(t.get_text(), t.get_color())  # grey and black text (ticks, axis labels) says nothing about colour
        return {k: sorted(v) for k, v in out.items()}

    def patched(self, fname, *a, **k):
        if not str(fname).endswith(".png"):
            return
        with contextlib.redirect_stdout(io.StringIO()):
            problems = figkit.check(self)
        records.append(dict(file=os.path.basename(str(fname)), problems=problems, **load(self)))

    Figure.savefig = patched
    os.chdir(os.path.dirname(os.path.abspath(script)))
    sys.argv = [script]
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(script, run_name="__main__")
    json.dump(records, open(out, "w"), indent=1)


def tokens(usage):
    usage = usage or {}
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    return {k: usage.get(k, 0) for k in keys}


def measure_run_dir(run_dir):
    rows = []
    for d in sorted((run_dir / "drawings").iterdir()):
        if not d.is_dir():
            continue
        meta = json.loads((d / "meta.json").read_text())
        row = dict(run=d.name, task=meta["task"], arm=meta["arm"], rep=meta["rep"],
                   cost_usd=meta["total_cost_usd"], num_turns=meta["num_turns"], duration_s=(meta["duration_ms"] or 0) / 1000,
                   skills_invoked=";".join(meta["skills_invoked"]), figure_exists=meta["figure_exists"], **tokens(meta["usage"]))
        row["total_tokens"] = sum(tokens(meta["usage"]).values())
        numbered = sorted((d / "files").glob("make_figure[0-9]*.py"))
        scripts = numbered or [d / "files" / "make_figure.py"]  # several figures: one script and one row each
        for script in scripts:
            png = "figure" + script.stem[len("make_figure"):] + ".png"
            fig_row = dict(row, figure=png)
            with tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp) / "w"
                shutil.copytree(d / "files", work)
                out = Path(tmp) / "m.json"
                p = subprocess.run([sys.executable, __file__, "--one", str(work / script.name), str(out)],
                                   capture_output=True, text=True)
                recs = json.loads(out.read_text()) if out.exists() else []
            rec = next((r for r in reversed(recs) if r["file"] == png), recs[-1] if recs else None)
            if rec is None:
                fig_row.update(words=None, method="failed: " + (p.stderr.strip().splitlines() or ["no PNG saved"])[-1])
            else:
                fig_row.update(words=rec["words"], n_text=rec["n_text"], panels=rec["panels"],
                               tick_words=rec["tick_words"], n_check_problems=len(rec["problems"]),
                               free_text=json.dumps(rec["free_text"]), check_problems=json.dumps(rec["problems"]),
                               method="matplotlib text objects", script_exists=script.exists(), title=rec["title"],
                               words_body=rec["words_body"], fig_width_in=rec["fig_width_in"],
                               fig_height_in=rec["fig_height_in"], min_font_pt=rec["min_font_pt"],
                               label_colors=json.dumps(rec["label_colors"]))
            rows.append(fig_row)
            print(d.name, png, fig_row.get("words"), fig_row["method"])
    return rows


def main():
    if sys.argv[1] == "--one":
        measure_script(sys.argv[2], sys.argv[3])
        return
    import pandas as pd

    run_dir = Path(sys.argv[1]).resolve()
    rows = measure_run_dir(run_dir)
    sys.path.insert(0, str(EVALS))
    from harness import new_path

    csv_path, json_path = new_path(run_dir / "measures.csv"), new_path(run_dir / "measures.json")
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(rows, indent=1))
    print("wrote", csv_path, json_path)


if __name__ == "__main__":
    main()
