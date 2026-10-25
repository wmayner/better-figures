"""Summarize the figure test: words per arm, Bayes factors, fresh-reader matches, cost, and the checks of later runs.

usage: python analyze.py <run_dir>
Reads <run_dir>/measures.csv and <run_dir>/readers/*/verdict.json.
Writes <run_dir>/per_run.csv (one row per figure, long format), <run_dir>/summary.json and
<run_dir>/table.csv (one row per task and arm); _v2 etc. if they exist.

Words: for each of the three original tasks, the ratio of mean words (plain Claude Code / with better-figures) and
its log. Bayes factor: one-sample JZS t-test of the three per-task log ratios against zero, with a Cauchy prior on
the standardized effect size (scale 0.707, checked with 1.0), two-sided.

Runs from 25 October 2026 on also have, when measure.py recorded them:
  words_body      the same ratio and Bayes factor for words outside the title, tick labels and numbers
  titles          the share of figures with a title, and the title's mean length, per arm
  task4_set       per run, whether each of the three conditions is drawn in one colour across the three figures
  task5_column    per run, the figure's width and its smallest text as printed in a 3.25 in column
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import new_path  # noqa: E402

ORIGINAL = ("task1_probes", "task2_heads", "task3_attribution")  # the 20 October tasks, with a reader check each
CONDITIONS = ("no honesty data", "honesty data", "honesty data and steering")  # task4_set's conditions
COLUMN_IN, MIN_PT = 3.25, 7


def jzs_bf10(x, scale):
    """Bayes factor for mean(x) != 0 against mean(x) = 0, effect size delta ~ Cauchy(0, scale).

    Rouder et al. (2009), equation 1, written as an integral over g with delta | g ~ Normal(0, g scale^2) and
    g ~ InverseGamma(1/2, 1/2)."""
    x = np.asarray(x, float)
    n = len(x)
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n))
    v = n - 1

    def integrand(g):
        a = 1 + n * g * scale**2
        return a**-0.5 * (1 + t**2 / (a * v)) ** (-(v + 1) / 2) * (2 * np.pi) ** -0.5 * g**-1.5 * np.exp(-1 / (2 * g))

    num, _ = integrate.quad(integrand, 0, np.inf, limit=500)
    return num / (1 + t**2 / v) ** (-(v + 1) / 2), t


def ratio_test(table, column):
    words = table.pivot(index="task", columns="arm", values=column)
    ratio = words["base"] / words["plugin"]
    log_ratio = np.log(ratio)
    bf = {}
    for scale in (0.707, 1.0):
        b, t = jzs_bf10(log_ratio.values, scale)
        bf[str(scale)] = dict(bf10=b, bf01=1 / b, t=t)
    per_task = pd.DataFrame({f"{column}_base": words["base"], f"{column}_plugin": words["plugin"], "ratio": ratio,
                             "log_ratio": log_ratio}).reset_index().to_dict("records")
    return dict(per_task=per_task, geometric_mean_ratio=float(np.exp(log_ratio.mean())),
                bayes_factor_log_ratio_vs_zero=bf)


def consistency(per_run):
    """task4_set: for each run, how many of the three conditions keep one colour across its three figures."""
    out = []
    for run, d in per_run[per_run.task == "task4_set"].groupby("run"):
        found, consistent, seen = 0, 0, {}
        for c in CONDITIONS:
            colours = set()
            for lc in d["label_colors"].dropna():
                colours |= set(json.loads(lc).get(c, []))
            seen[c] = sorted(colours)
            if colours:
                found += 1
                consistent += len(colours) == 1
        out.append(dict(run=run, arm=d["arm"].iloc[0], conditions_found=found, conditions_one_colour=consistent,
                        all_one_colour=found == len(CONDITIONS) and consistent == found, colours=seen))
    return out


def column(per_run):
    """task5_column: each figure's width and its smallest text as printed 3.25 in wide."""
    d = per_run[per_run.task == "task5_column"].copy()
    d["printed_scale"] = np.minimum(1, COLUMN_IN / d["fig_width_in"])
    d["min_font_printed_pt"] = d["min_font_pt"] * d["printed_scale"]
    d["text_below_7pt"] = d["min_font_printed_pt"] < MIN_PT
    return d[["run", "arm", "fig_width_in", "min_font_pt", "min_font_printed_pt", "text_below_7pt"]].to_dict("records")


def main():
    run_dir = Path(sys.argv[1]).resolve()
    m = pd.read_csv(run_dir / "measures.csv")
    verdicts = [json.loads(p.read_text()) for p in sorted((run_dir / "readers").glob("reader_*/verdict.json"))]
    v = pd.DataFrame(verdicts)[["run", "reader_sentence", "verdict", "reason"]] if verdicts else pd.DataFrame(
        columns=["run", "reader_sentence", "verdict", "reason"])
    per_run = m.merge(v, on="run", how="left")
    per_run.to_csv(new_path(run_dir / "per_run.csv"), index=False)
    new = "words_body" in per_run.columns  # measured by the 25 October version of measure.py

    orig = per_run[per_run.task.isin(ORIGINAL)]
    aggs = dict(mean_words=("words", "mean"), runs=("run", "count"),
                reader_yes=("verdict", lambda s: int((s == "yes").sum())),
                reader_partly=("verdict", lambda s: int((s == "partly").sum())),
                reader_no=("verdict", lambda s: int((s == "no").sum())),
                mean_cost_usd=("cost_usd", "mean"), mean_total_tokens=("total_tokens", "mean"),
                mean_output_tokens=("output_tokens", "mean"))
    if new:
        aggs.update(mean_words_body=("words_body", "mean"),
                    with_title=("title", lambda s: int(s.fillna("").astype(str).str.strip().ne("").sum())))
    table = per_run.groupby(["task", "arm"]).agg(**aggs).reset_index()
    table.to_csv(new_path(run_dir / "table.csv"), index=False)
    t_orig = table[table.task.isin(ORIGINAL)]

    arm_totals = orig.groupby("arm").agg(
        mean_words=("words", "mean"), mean_cost_usd=("cost_usd", "mean"), mean_total_tokens=("total_tokens", "mean"),
        reader_yes=("verdict", lambda s: int((s == "yes").sum())),
        reader_partly=("verdict", lambda s: int((s == "partly").sum())),
        reader_no=("verdict", lambda s: int((s == "no").sum())), runs=("run", "count"))
    summary = dict(**ratio_test(t_orig, "mean_words"), per_arm=arm_totals.reset_index().to_dict("records"),
                   skill_invoked_by_run=per_run.drop_duplicates("run").set_index("run")["skills_invoked"].fillna("").to_dict())
    if new:
        titles = orig.assign(has_title=orig["title"].fillna("").astype(str).str.strip().ne(""),
                             title_words=orig["title"].fillna("").astype(str).str.split().str.len())
        summary["words_body"] = ratio_test(t_orig, "mean_words_body")
        summary["titles"] = titles.groupby("arm").agg(figures=("run", "count"), with_title=("has_title", "sum"),
                                                      mean_title_words=("title_words", "mean")).reset_index().to_dict("records")
        summary["task4_set"] = consistency(per_run)
        summary["task5_column"] = column(per_run)
    out = new_path(run_dir / "summary.json")
    out.write_text(json.dumps(summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else float(o)))
    print(table.to_string())
    print(json.dumps({k: v for k, v in summary.items() if k != "skill_invoked_by_run"}, indent=1,
                     default=lambda o: o.item() if hasattr(o, "item") else float(o)))
    print("wrote", out)


if __name__ == "__main__":
    main()
