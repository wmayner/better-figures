"""Summarize the figure test: words per arm, Bayes factors, fresh-reader matches, cost.

usage: python analyze.py <run_dir>
Reads <run_dir>/measures.csv and <run_dir>/readers/*/verdict.json.
Writes <run_dir>/per_run.csv (one row per drawing run, long format), <run_dir>/summary.json and
<run_dir>/table.csv (one row per task and arm); _v2 etc. if they exist.

Words: for each task, the ratio of mean words (plain Claude Code / with better-figures) and its log.
Bayes factor: one-sample JZS t-test of the three per-task log ratios against zero, with a Cauchy prior on the
standardized effect size (scale 0.707, checked with 1.0), two-sided.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import new_path  # noqa: E402


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


def main():
    run_dir = Path(sys.argv[1]).resolve()
    m = pd.read_csv(run_dir / "measures.csv")
    verdicts = [json.loads(p.read_text()) for p in sorted((run_dir / "readers").glob("reader_*/verdict.json"))]
    v = pd.DataFrame(verdicts)[["run", "reader_sentence", "verdict", "reason"]] if verdicts else pd.DataFrame(
        columns=["run", "reader_sentence", "verdict", "reason"])
    per_run = m.merge(v, on="run", how="left")
    per_run.to_csv(new_path(run_dir / "per_run.csv"), index=False)

    g = per_run.groupby(["task", "arm"])
    table = g.agg(mean_words=("words", "mean"), runs=("run", "count"),
                  reader_yes=("verdict", lambda s: int((s == "yes").sum())),
                  reader_partly=("verdict", lambda s: int((s == "partly").sum())),
                  reader_no=("verdict", lambda s: int((s == "no").sum())),
                  mean_cost_usd=("cost_usd", "mean"), mean_total_tokens=("total_tokens", "mean"),
                  mean_output_tokens=("output_tokens", "mean")).reset_index()
    table.to_csv(new_path(run_dir / "table.csv"), index=False)

    words = table.pivot(index="task", columns="arm", values="mean_words")
    ratio = words["base"] / words["plugin"]
    log_ratio = np.log(ratio)
    bf = {}
    for scale in (0.707, 1.0):
        b, t = jzs_bf10(log_ratio.values, scale)
        bf[str(scale)] = dict(bf10=b, bf01=1 / b, t=t)
    arm_totals = per_run.groupby("arm").agg(
        mean_words=("words", "mean"), mean_cost_usd=("cost_usd", "mean"), mean_total_tokens=("total_tokens", "mean"),
        reader_yes=("verdict", lambda s: int((s == "yes").sum())),
        reader_partly=("verdict", lambda s: int((s == "partly").sum())),
        reader_no=("verdict", lambda s: int((s == "no").sum())), runs=("run", "count"))
    summary = dict(
        per_task=pd.DataFrame(dict(mean_words_base=words["base"], mean_words_plugin=words["plugin"],
                                   ratio=ratio, log_ratio=log_ratio)).reset_index().to_dict("records"),
        geometric_mean_ratio=float(np.exp(log_ratio.mean())),
        bayes_factor_log_ratio_vs_zero=bf,
        per_arm=arm_totals.reset_index().to_dict("records"),
        skill_invoked_by_run=per_run.set_index("run")["skills_invoked"].fillna("").to_dict(),
    )
    out = new_path(run_dir / "summary.json")
    out.write_text(json.dumps(summary, indent=1, default=float))
    print(table.to_string())
    print(json.dumps({k: summary[k] for k in ("per_task", "geometric_mean_ratio", "bayes_factor_log_ratio_vs_zero")},
                     indent=1, default=float))
    print("wrote", out)


if __name__ == "__main__":
    main()
