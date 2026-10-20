"""Run the figure test: isolation check, drawing runs, and the fresh-reader test.

usage (from evals/):
  python make_data.py --seed 20261020 --out runs/2026-10-20_seed20261020
  python run.py isolation runs/2026-10-20_seed20261020
  python run.py draw      runs/2026-10-20_seed20261020 [--reps 2] [--parallel 4]
  python measure.py       runs/2026-10-20_seed20261020
  python run.py read      runs/2026-10-20_seed20261020
  python analyze.py       runs/2026-10-20_seed20261020

Every session runs in its own fresh directory outside this repository (under --work-root, a new temporary
directory by default), so a base-arm session cannot find the plugin's files by looking around. The drawing
directory holds only data.csv; the reader directory holds only figure.png. Outputs are copied back into the
run folder. Existing outputs are skipped, never overwritten, so an interrupted run can be resumed.
"""
import argparse
import json
import random
import secrets
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import harness

EVALS = Path(__file__).resolve().parent
SPEC = json.loads((EVALS / "tasks.json").read_text())
ARMS = ("base", "plugin")


def fresh_dir(root):
    d = Path(root) / secrets.token_hex(4)
    d.mkdir(parents=True)
    return d


def seed_of(run_dir):
    return json.loads((run_dir / "seed.json").read_text())["seed"]


def isolation(run_dir, work_root):
    for arm in ARMS:
        out = run_dir / "isolation" / arm
        if out.exists():
            print("exists, skipping", out)
            continue
        result, _ = harness.run(arm, SPEC["isolation_probe"], fresh_dir(work_root), out, budget=2)
        init = json.loads((out / "init.json").read_text())
        summary = dict(arm=arm, plugins=init.get("plugins"), skills=init.get("skills"),
                       mcp_servers=init.get("mcp_servers"), memory_paths=init.get("memory_paths"),
                       answer=result.get("result"))
        (out / "summary.json").write_text(json.dumps(summary, indent=1))
        print(json.dumps(summary, indent=1))


def draw_one(job, run_dir, work_root):
    task, arm, rep = job
    name = f"{task}__{arm}__r{rep}"
    out = run_dir / "drawings" / name
    if out.exists():
        return name, "exists, skipped"
    work = fresh_dir(work_root)
    shutil.copy(run_dir / "tasks" / task / "data.csv", work / "data.csv")
    prompt = SPEC["tasks"][task] + " " + SPEC["suffix"]
    result, events = harness.run(arm, prompt, work, out / "session")
    shutil.copytree(work, out / "files", ignore=shutil.ignore_patterns("__pycache__", ".venv", "*.pyc"))
    meta = dict(task=task, arm=arm, rep=rep, work_dir=str(work), skills_invoked=harness.skills_invoked(events),
                is_error=result.get("is_error"), total_cost_usd=result.get("total_cost_usd"),
                num_turns=result.get("num_turns"), duration_ms=result.get("duration_ms"), usage=result.get("usage"),
                figure_exists=(work / "figure.png").exists())
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    return name, f"cost {meta['total_cost_usd']}, skills {meta['skills_invoked']}, figure {meta['figure_exists']}"


def draw(run_dir, work_root, reps, parallel):
    jobs = [(t, a, r) for t in SPEC["tasks"] for a in ARMS for r in range(1, reps + 1)]
    random.Random(seed_of(run_dir)).shuffle(jobs)  # mix arms and tasks within each parallel batch
    (run_dir / "drawings").mkdir(exist_ok=True)
    (run_dir / "drawings" / "order.json").write_text(json.dumps(jobs))
    with ThreadPoolExecutor(parallel) as pool:
        for name, msg in pool.map(lambda j: draw_one(j, run_dir, work_root), jobs):
            print(name, msg, flush=True)


def parse_verdict(text):
    verdict, reason = None, None
    for line in (text or "").splitlines():
        low = line.strip().lower()
        if low.startswith("verdict:"):
            v = low.split(":", 1)[1].strip().strip("*. ")
            verdict = next((w for w in ("partly", "yes", "no") if v.startswith(w)), v)
        elif low.startswith("reason:"):
            reason = line.split(":", 1)[1].strip()
    return verdict, reason


def read_one(item, run_dir, work_root, answers):
    idx, name = item
    out = run_dir / "readers" / f"reader_{idx:02d}"
    if (out / "verdict.json").exists():
        return name, "exists, skipped"
    png = run_dir / "drawings" / name / "files" / "figure.png"
    reader_out, judge_out = out / "reader", out / "judge"
    if not (reader_out / "result.json").exists():
        work = fresh_dir(work_root)
        shutil.copy(png, work / "figure.png")
        harness.run("base", SPEC["reader"], work, reader_out, tools="Read", budget=2)
    sentence = json.loads((reader_out / "result.json").read_text()).get("result", "").strip()
    task = name.split("__")[0]
    prompt = SPEC["judge"].format(reader=sentence, answer=answers[task])
    result, _ = harness.run("base", prompt, fresh_dir(work_root), judge_out, tools="", budget=2)
    verdict, reason = parse_verdict(result.get("result"))
    rec = dict(reader=f"reader_{idx:02d}", run=name, task=task, reader_sentence=sentence, intended=answers[task],
               verdict=verdict, reason=reason)
    (out / "verdict.json").write_text(json.dumps(rec, indent=1))
    return name, f"{verdict}: {sentence[:90]}"


def read(run_dir, work_root, parallel):
    answers = json.loads((run_dir / "answers.json").read_text())
    names = sorted(p.name for p in (run_dir / "drawings").iterdir()
                   if p.is_dir() and (p / "files" / "figure.png").exists())
    random.Random(seed_of(run_dir) + 1).shuffle(names)  # reader ids do not reveal task or arm order
    (run_dir / "readers").mkdir(exist_ok=True)
    (run_dir / "readers" / "order.json").write_text(json.dumps(names))
    with ThreadPoolExecutor(parallel) as pool:
        for name, msg in pool.map(lambda it: read_one(it, run_dir, work_root, answers), enumerate(names, 1)):
            print(name, msg, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["isolation", "draw", "read"])
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--work-root", type=Path, default=None, help="where fresh session directories are made")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--parallel", type=int, default=4)
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    work_root = args.work_root or Path(tempfile.mkdtemp(prefix="figtest-"))
    work_root = work_root.resolve()
    if EVALS.parent in work_root.parents or work_root == EVALS.parent:
        raise SystemExit("--work-root must be outside the repository, or base-arm sessions could find the skill")
    if args.step == "isolation":
        isolation(run_dir, work_root)
    elif args.step == "draw":
        draw(run_dir, work_root, args.reps, args.parallel)
    else:
        read(run_dir, work_root, args.parallel)


if __name__ == "__main__":
    main()
