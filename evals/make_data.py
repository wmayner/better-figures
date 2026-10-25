"""Generate the made-up datasets for the figure test, each with a planted answer.

usage: python make_data.py --seed 20261020 --out runs/2026-10-20_seed20261020

Writes, under <out>/tasks/<task>/:
  data.csv        the only file a drawing run sees
Writes, under <out>/:
  answers.json    the planted fact for each task with a fresh-reader check, in one sentence (never copied into a run
                  directory); task4_set and task5_column test colour roles and print sizes, and have no reader check
  seed.json       the seed and the generator settings
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, special, stats

PROBE_CONCEPTS = {  # concept: layer at which accuracy is halfway between chance and its plateau
    "part of speech": 3.0,
    "sentiment": 8.0,
    "named entity type": 13.5,
    "statement truthfulness": 19.0,
}
KEY_HEADS = {(9, 6): 1.30, (9, 9): 0.95, (10, 0): 0.70}  # (layer, head): mean loss increase in nats
METHODS = {  # method: mean rank correlation with ablation across models
    "integrated gradients": 0.84,
    "attribution patching": 0.61,
    "gradient times input": 0.47,
    "saliency": 0.31,
    "activation magnitude": 0.18,
}
MODELS = {"GPT-2 small": 144, "Pythia-410M": 384, "Gemma-2-2B": 208}  # model: number of heads compared
CONDITIONS = {  # condition: final sycophancy rate (%), final helpfulness (1 to 10)
    "no honesty data": (38.0, 7.1),
    "honesty data": (21.0, 7.0),
    "honesty data and steering": (9.0, 6.9),
}


def task1_probes(rng):
    rows = []
    for concept, mid in PROBE_CONCEPTS.items():
        plateau = rng.uniform(0.88, 0.95)
        for layer in range(24):
            mean = 0.5 + (plateau - 0.5) / (1 + np.exp(-(layer - mid) / 1.1))
            acc = float(np.clip(mean + rng.normal(0, 0.008), 0.45, 0.99))
            half = rng.uniform(0.015, 0.03)
            rows.append(dict(concept=concept, layer=layer, accuracy=round(acc, 4),
                             ci_low=round(acc - half, 4), ci_high=round(acc + half, 4), n_test_examples=2000))
    order = sorted(PROBE_CONCEPTS, key=PROBE_CONCEPTS.get)
    answer = ("The four concepts become decodable at clearly different depths: part of speech first (around layer 3), "
              "then sentiment (around layer 8), named entity type (around layer 13 to 14), and statement truthfulness "
              "last (around layer 19).")
    return pd.DataFrame(rows), answer, dict(onset_layers=PROBE_CONCEPTS, order=order)


def task2_heads(rng):
    rows = []
    for layer in range(12):
        for head in range(12):
            mean = KEY_HEADS.get((layer, head), abs(rng.normal(0.0, 0.025)))
            effect = mean + rng.normal(0, 0.01 + 0.04 * mean)
            sem = abs(rng.normal(0.012 + 0.05 * mean, 0.003))
            rows.append(dict(layer=layer, head=head, loss_increase=round(float(effect), 4),
                             sem=round(float(sem), 4), n_prompts=500))
    answer = ("Three heads matter: layer 9 head 6, layer 9 head 9 and layer 10 head 0; ablating any of the other "
              "141 heads barely changes the loss.")
    return pd.DataFrame(rows), answer, dict(key_heads={f"L{l}H{h}": v for (l, h), v in KEY_HEADS.items()})


def log_bf10_correlation(r, n):
    """Log Bayes factor for a correlation against zero (Jeffreys-Zellner-Siow, Wetzels and Wagenmakers 2012)."""
    def logf(g):
        return ((n - 2) / 2) * np.log1p(g) - ((n - 1) / 2) * np.log1p((1 - r**2) * g) - 1.5 * np.log(g) - n / (2 * g)
    grid = np.logspace(-4, 6, 4000)
    m = logf(grid).max()
    val, _ = integrate.quad(lambda g: np.exp(logf(g) - m), 0, np.inf, limit=500, points=None)
    return np.log(np.sqrt(n / 2) / special.gamma(0.5)) + m + np.log(val)


def task3_methods(rng):
    rows = []
    for method, mean_r in METHODS.items():
        for model, n in MODELS.items():
            r = float(np.clip(mean_r + rng.normal(0, 0.035), -0.95, 0.95))
            z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
            lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
            bf = float(np.exp(log_bf10_correlation(r, n)))
            rows.append(dict(method=method, model=model, spearman_r=round(r, 3), ci_low=round(float(lo), 3),
                             ci_high=round(float(hi), 3), n_heads=n, bayes_factor_10=float(f"{bf:.3g}")))
    answer = ("Integrated gradients matches ablation best on all three models (rank correlation about 0.8 to 0.9), "
              "clearly ahead of the next best method, attribution patching (about 0.6).")
    return pd.DataFrame(rows), answer, dict(method_means=METHODS, models=MODELS)


def task4_set(rng):
    """Three figures for one write-up, sharing three conditions: does each condition keep one colour?"""
    rows = []
    steps = np.arange(0, 2001, 100)
    for condition, (final, helpful) in CONDITIONS.items():
        for seed in range(5):
            end = final + rng.normal(0, 1.5)
            curve = end + (40 - end) * np.exp(-steps / 500) + rng.normal(0, 1.0, len(steps))
            rows += [dict(condition=condition, seed=seed, step=int(t), measure="sycophancy_rate_percent",
                          value=round(float(v), 2)) for t, v in zip(steps, curve)]
            rows.append(dict(condition=condition, seed=seed, step=int(steps[-1]), measure="helpfulness_1_to_10",
                             value=round(float(helpful + rng.normal(0, 0.15)), 2)))
    answer = ("Honesty data cut final sycophancy from about 38% to 21%, and honesty data with steering to about 9%, "
              "with helpfulness unchanged at about 7 out of 10.")
    return pd.DataFrame(rows), answer, dict(conditions=CONDITIONS)


TASKS = {"task1_probes": task1_probes, "task2_heads": task2_heads, "task3_attribution": task3_methods,
         "task4_set": task4_set}  # new tasks go last, so a seed gives the earlier tasks the same data as before
COPIES = {"task5_column": "task1_probes"}  # the probe data again, for a figure in one column of a paper


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261020)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit(f"{args.out} exists; choose another --out (outputs are never overwritten)")
    rng = np.random.default_rng(args.seed)
    answers, settings = {}, {}
    for name, fn in TASKS.items():
        df, answer, planted = fn(rng)
        d = args.out / "tasks" / name
        d.mkdir(parents=True)
        df.to_csv(d / "data.csv", index=False)
        answers[name] = answer
        settings[name] = planted
    for name, source in COPIES.items():
        d = args.out / "tasks" / name
        d.mkdir(parents=True)
        (d / "data.csv").write_text((args.out / "tasks" / source / "data.csv").read_text())
        settings[name] = dict(copy_of=source)
    answers = {k: v for k, v in answers.items() if k in ("task1_probes", "task2_heads", "task3_attribution")}
    (args.out / "answers.json").write_text(json.dumps(answers, indent=1))
    (args.out / "seed.json").write_text(json.dumps(dict(seed=args.seed, planted=settings), indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
