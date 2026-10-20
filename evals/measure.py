"""Count the words each run's figure carries outside tick labels, and collect cost and tokens per run.

usage: python measure.py <run_dir>          writes <run_dir>/measures.csv and measures.json (long format; _v2 if they exist)
       python measure.py --one <make_figure.py> <out.json>   (internal: measure one script)

Each run's make_figure.py is re-run in a scratch copy of its directory with Figure.savefig patched, so nothing is
written. For every PNG the script would save, it records the words in visible text objects other than tick labels
(axis labels, titles, legends, annotations, colorbar labels), the number of panels, and the problems that the
plugin's figkit.check reports. Adapted from the 15 October 2026 test's counter.
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
        return dict(words=sum(len(s.split()) for s in free), n_text=len(free),
                    panels=len([a for a in fig.axes if a.get_label() != "<colorbar>"]),
                    free_text=free, tick_words=sum(len(s.split()) for s in tick_text))

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
        script = d / "files" / "make_figure.py"
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "w"
            shutil.copytree(d / "files", work)
            out = Path(tmp) / "m.json"
            p = subprocess.run([sys.executable, __file__, "--one", str(work / "make_figure.py"), str(out)],
                               capture_output=True, text=True)
            recs = json.loads(out.read_text()) if out.exists() else []
        rec = next((r for r in reversed(recs) if r["file"] == "figure.png"), recs[-1] if recs else None)
        if rec is None:
            row.update(words=None, method="failed: " + (p.stderr.strip().splitlines() or ["no PNG saved"])[-1])
        else:
            row.update(words=rec["words"], n_text=rec["n_text"], panels=rec["panels"], tick_words=rec["tick_words"],
                       n_check_problems=len(rec["problems"]), free_text=json.dumps(rec["free_text"]),
                       check_problems=json.dumps(rec["problems"]), method="matplotlib text objects",
                       script_exists=script.exists())
        rows.append(row)
        print(d.name, row.get("words"), row["method"])
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
