"""House style, palette, colour roles, direct labels and a clutter check for matplotlib figures.

    import figkit as fk
    fk.use()                          # style, font and colour roles; size="paper" or "column" for print,
                                      # "post" for an image posted on its own
    fig, ax = plt.subplots()          # the size's default figure size; don't enlarge it
    ax.plot(x, a, color=fk.color("linear probe"), label="linear probe")
    ax.plot(x, b, color=fk.GREY, label="random baseline")
    fk.label_lines(ax)                # names at the line ends, no legend
    fk.title(fig, "A linear probe reads tense from layer 6 on")   # the finding, in one line
    fk.save(fig, "fig1.png")          # runs check() and prints what to fix

Uncertainty is drawn, not written: fk.interval and fk.difference compute an interval over the unit that was sampled
independently, fk.intervals, fk.paired and fk.differences draw it, and fk.title(fig, text, claims=d) ties a title
that states a difference to the interval of that difference.

Single file on purpose: the figures skill copies it, with fonts/, into a _kit/
folder in each project, and figure scripts import that copy. Fonts are read from
the fonts/ folder next to this file; without it they fall back to DejaVu Sans.
"""
import json
import math
import re
import statistics
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, ticker
from matplotlib.collections import LineCollection, PathCollection, PolyCollection, QuadMesh
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.text import Text

INK = "#1F1F1F"       # text and the most important dark mark
MUTED = "#6B6B6B"     # axis lines, tick labels, secondary text
GREY = "#A3A3A3"      # context series, and the control
LIGHT = "#D9D9D9"     # bands, reference regions, de-emphasised bars
ACCENT = "#D55E00"    # the one thing the figure is about (Okabe-Ito vermillion)
BLUE = "#0072B2"      # a second highlighted series, if the claim contrasts two
# Okabe-Ito, colour-blind safe; use only when the categories themselves are the point.
CATEGORICAL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]

# Colour roles: name each condition once in figure-roles.json, and every figure colours it the same way.
#   {"control": "plain fine-tune", "intervention": "honesty data", "second": "half the data",
#    "ordered": ["70M", "410M", "1.4B"]}
# Conditions without a role are GREY. "baseline" means the same as "control".
ROLE_COLORS = {"control": GREY, "intervention": ACCENT, "second": BLUE, "third": "#009E73", "fourth": "#CC79A7",
               "fifth": "#E69F00"}
ROLES_FILE = "figure-roles.json"

# Where a figure goes: its default size in inches, font sizes that read well there, the smallest text allowed,
# and the width it is shown at. A print figure wider than its width is scaled down, and its text with it.
SIZES = {
    "screen": {"figsize": (7, 4), "font": 13, "ticks": 12, "title": 14, "min_pt": 10, "width": 10},
    "slide": {"figsize": (10, 5.625), "font": 16, "ticks": 14, "title": 18, "min_pt": 14, "width": 10},
    "paper": {"figsize": (6.75, 3.2), "font": 9, "ticks": 8, "title": 10, "min_pt": 7, "width": 6.75},
    "column": {"figsize": (3.25, 2.4), "font": 8, "ticks": 7, "title": 9, "min_pt": 7, "width": 3.25},
    # an image posted on its own on X or in Slack, which crop or shrink wide images: 1200 x 960 px at 200 dpi
    "post": {"figsize": (6, 4.8), "font": 13, "ticks": 12, "title": 15, "min_pt": 11, "width": 6},
}

_FONTS = [Path(__file__).resolve().with_name("fonts")]
_size = "screen"
_roles = {}    # label -> (role, colour)
_roles_from = None
MOCK_GID = "figkit-mock"

STYLE = {
    "figure.dpi": 100,
    "figure.constrained_layout.use": True,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "axes.titlepad": 8,
    "legend.frameon": False,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": "#ECECEC",
    "axes.axisbelow": True,
    "axes.prop_cycle": mpl.cycler(color=CATEGORICAL),
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    "errorbar.capsize": 0,
    "patch.edgecolor": "none",
}


def use(size="screen", roles=None):
    """Apply the house style for where the figure goes (screen, slide, paper or column) and load the colour roles.

    Call after seaborn's set_theme, or instead of it. roles is a dict like the roles file; without it, the nearest
    figure-roles.json in the script's folder or above it (then the working folder or above it) is used.
    """
    global _size
    if size not in SIZES:
        raise ValueError(f"size={size!r}: use one of {', '.join(SIZES)}")
    _size = size
    s = SIZES[size]
    k = s["font"] / 13  # lines and markers scale with the text
    for d in _FONTS:
        for f in sorted(d.glob("*.ttf")) if d.is_dir() else []:
            font_manager.fontManager.addfont(str(f))
    have_inter = any(f.name == "Inter" for f in font_manager.fontManager.ttflist)
    mpl.rcParams.update(STYLE)
    mpl.rcParams.update({
        "figure.figsize": s["figsize"], "savefig.dpi": 300 if size in ("paper", "column") else 200,
        "font.size": s["font"], "axes.labelsize": s["font"], "axes.titlesize": s["font"],
        "xtick.labelsize": s["ticks"], "ytick.labelsize": s["ticks"], "legend.fontsize": s["ticks"],
        "lines.linewidth": 2.2 * k, "lines.markersize": 6 * k, "axes.linewidth": 0.9 * k, "grid.linewidth": 0.8 * k,
    })
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = (["Inter"] if have_inter else []) + ["DejaVu Sans"]
    _load_roles(roles)


def title(fig, text, claims=None):
    """Give the figure its title: the finding, stated literally in one line of about 10 words, left-aligned.

    If the title states a difference, pass that difference as claims (an Estimate from fk.difference, fk.paired or
    fk.differences, or a list of them). The check on save then refuses the title when the interval of the difference
    includes zero.
    """
    if claims is not None:
        fig._figkit_claims = list(claims) if isinstance(claims, (list, tuple)) else [claims]
    w = fig.get_size_inches()[0]
    pad = mpl.rcParams["figure.constrained_layout.w_pad"]
    return fig.suptitle(text, x=pad / w, ha="left", fontsize=SIZES[_size]["title"], fontweight="semibold")


# ---------------------------------------------------------------------------------------------- colour roles

def _find_roles_file():
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    starts = ([Path(main).resolve().parent] if main else []) + [Path.cwd()]
    for start in starts:
        for d in (start, *start.parents):
            if (d / ROLES_FILE).is_file():
                return d / ROLES_FILE
    return None


def _load_roles(spec):
    global _roles_from
    _roles.clear()
    _roles_from = "the roles passed to fk.use" if spec is not None else None
    if spec is None:
        f = _find_roles_file()
        if f is None:
            return
        spec, _roles_from = json.loads(f.read_text()), str(f)
    for role, labels in spec.items():
        role = "control" if role == "baseline" else role
        if role != "ordered" and role not in ROLE_COLORS:
            raise ValueError(f"unknown role {role!r} in {_roles_from}: use ordered or one of {', '.join(ROLE_COLORS)}")
        labels = [labels] if isinstance(labels, str) else [str(x) for x in labels]
        colors = ramp(len(labels)) if role == "ordered" else [ROLE_COLORS[role]] * len(labels)
        _roles.update({_key(lab): (role, c) for lab, c in zip(labels, colors)})


def roles():
    """The roles in effect, as {label: role}, and where they came from."""
    return {lab: r for lab, (r, _c) in _roles.items()}, _roles_from


def _key(label):
    return " ".join(str(label).split())  # a label wrapped onto two lines is still the same condition


def color(label, default=GREY):
    """The colour of a condition's role (fk.ACCENT for the intervention, and so on), or default without one."""
    return _roles[_key(label)][1] if _key(label) in _roles else default


def palette(labels, default=GREY):
    """{label: colour} for seaborn's palette=, from the roles."""
    return {lab: color(lab, default) for lab in labels}


def _mix(a, b, t):
    ra, rb = mpl.colors.to_rgb(a), mpl.colors.to_rgb(b)
    return mpl.colors.to_hex([x + (y - x) * t for x, y in zip(ra, rb)])


def ramp(n):
    """n colours from light to dark blue, for conditions with an order of their own (layers, sizes, steps, doses)."""
    lo, mid, hi = _mix(BLUE, "#FFFFFF", 0.55), BLUE, _mix(BLUE, "#000000", 0.5)
    if n == 1:
        return [mid]
    ts = [i / (n - 1) for i in range(n)]
    return [_mix(lo, mid, 2 * t) if t <= 0.5 else _mix(mid, hi, 2 * t - 1) for t in ts]


# ---------------------------------------------------------------------------------------------- labels

def label_lines(ax, lines=None, gap=1.25, pad=6, at="end"):
    """Write each labelled line's name at its right end, in its colour, and drop the legend. at="start" writes the
    names before the lines' left ends instead, for lines that bunch together at their right ends, and widens the
    axes to fit them. Call it after setting the axes' scales and limits.

    Labels that would collide are pushed apart vertically. Lines whose label starts with "_" are skipped.
    """
    lines = [l for l in (lines or ax.get_lines()) if not l.get_label().startswith("_")]
    ax.figure.canvas.draw()
    ends = []
    for l in lines:
        x, y = l.get_xdata(), l.get_ydata()
        ok = [i for i in range(len(x)) if x[i] == x[i] and y[i] == y[i]]  # drop NaN
        if ok:
            i = ok[-1] if at == "end" else ok[0]
            px, py = ax.transData.transform((x[i], y[i]))
            ends.append([py, px, l])
    ends.sort(key=lambda e: e[0])
    step = mpl.rcParams["font.size"] * gap * ax.figure.dpi / 72
    for i in range(1, len(ends)):  # push colliding labels upward
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + step)
    inv = ax.transData.inverted()
    made = []
    for py, px, l in ends:
        x, y = inv.transform((px, py))
        made.append(ax.annotate(l.get_label(), (x, y), xytext=(pad if at == "end" else -pad, 0),
                                textcoords="offset points", color=l.get_color(), va="center",
                                ha="left" if at == "end" else "right", annotation_clip=False))
    if ax.get_legend():
        ax.get_legend().remove()
    if at == "start":
        _make_room(ax, made, grow_low=True)


def label_bars(ax, pad=4):
    """Name each bar series above its first bar (in its colour, or grey if the bar is pale) and drop the legend.

    Works with seaborn's barplot(hue=...) and with repeated ax.bar(..., label=...) calls.
    """
    bars = [c for c in ax.containers if isinstance(c, BarContainer) and len(c.patches)]
    lg = ax.get_legend()
    names = [t.get_text() for t in lg.get_texts()] if lg else [c.get_label() for c in bars]
    for c, name in zip(bars, names):
        b = c.patches[0]
        cx = b.get_x() + b.get_width() / 2
        top = max(b.get_y() + b.get_height(), *_ends(ax, b, horizontal=False))
        r, g, b_, _ = mpl.colors.to_rgba(b.get_facecolor())
        color_ = MUTED if 0.299 * r + 0.587 * g + 0.114 * b_ > 0.75 else b.get_facecolor()
        ax.annotate(name, (cx, top), xytext=(0, pad), textcoords="offset points",
                    ha="center", va="bottom", color=color_, annotation_clip=False)
    if lg:
        lg.remove()


def label_values(ax, fmt="{:g}", notes=None, pad=4):
    """Write each bar's value at its end, in bold, with an optional note beside it in grey ("164 of 400").

    fmt formats the value ("{:.0f}%", "{:.2f}"). notes maps a bar's category (its tick label) to its note, or is a
    list in the order the bars were drawn. Works with ax.bar, ax.barh and seaborn's barplot; values sit beyond any
    error bar.
    """
    fig = ax.figure
    fig.canvas.draw()
    made = []
    i = 0
    for c in [c for c in ax.containers if isinstance(c, BarContainer)]:
        horizontal = _horizontal(c)
        for p in c.patches:
            v = p.get_width() if horizontal else p.get_height()
            if v != v:  # NaN
                continue
            sign = -1 if v < 0 else 1
            if horizontal:
                cy = p.get_y() + p.get_height() / 2
                end = (max if sign > 0 else min)([p.get_x() + p.get_width(), *_ends(ax, p, horizontal=True)])
                xy, off, ha, va = (end, cy), (sign * pad, 0), "left" if sign > 0 else "right", "center"
                cat = _category(ax, cy, True)
            else:
                cx = p.get_x() + p.get_width() / 2
                end = (max if sign > 0 else min)([p.get_y() + p.get_height(), *_ends(ax, p, horizontal=False)])
                xy, off, ha, va = (cx, end), (0, sign * pad), "center", "bottom" if sign > 0 else "top"
                cat = _category(ax, cx, False)
            note = None
            if isinstance(notes, dict):
                note = notes.get(cat)
            elif notes is not None and i < len(notes):
                note = notes[i]
            t = ax.annotate(fmt.format(v), xy, xytext=off, textcoords="offset points", ha=ha, va=va,
                            fontweight="semibold", color=INK, annotation_clip=False)
            made.append((t, note, xy, off, ha, va, horizontal, sign))
            i += 1
    if any(m[1] for m in made):
        _add_notes(ax, made)
    _make_room(ax, [m[0] for m in made] + [n for m in made for n in m[8:]])


def _add_notes(ax, made):
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for k, (t, note, xy, off, ha, va, horizontal, sign) in enumerate(made):
        if not note:
            continue
        b = t.get_window_extent(r)
        if horizontal:  # the note follows the value on the same line
            dx = off[0] + sign * (b.width * 72 / fig.dpi + 4)
            n = ax.annotate(note, xy, xytext=(dx, 0), textcoords="offset points", ha=ha, va=va, color=MUTED,
                            annotation_clip=False)
        else:  # above the value
            dy = off[1] + sign * (b.height * 72 / fig.dpi + 1)
            n = ax.annotate(note, xy, xytext=(0, dy), textcoords="offset points", ha=ha, va=va, color=MUTED,
                            annotation_clip=False)
        made[k] = (*made[k], n)


def _make_room(ax, texts, grow_low=False):
    """Widen the axes' limits until every text stays inside the axes. A low limit grows only when it is below zero
    or grow_low is set: bars start at zero, so labels at their ends only push the far limit out."""
    fig = ax.figure
    for _ in range(3):
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        box = ax.get_window_extent(r)
        exts = [t.get_window_extent(r) for t in texts]
        if not exts:
            return
        inv = ax.transData.inverted()  # display back to data, so log axes grow in their own scale
        (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
        right, left = max(e.x1 for e in exts), min(e.x0 for e in exts)
        top, bottom = max(e.y1 for e in exts), min(e.y0 for e in exts)
        grew = False
        if right > box.x1 + 0.5:
            x1, grew = inv.transform((box.x1 + (right - box.x1) * 1.15, box.y0))[0], True
        if left < box.x0 - 0.5 and (grow_low or x0 < 0):
            x0, grew = inv.transform((box.x0 - (box.x0 - left) * 1.15, box.y0))[0], True
        if top > box.y1 + 0.5:
            y1, grew = inv.transform((box.x0, box.y1 + (top - box.y1) * 1.15))[1], True
        if bottom < box.y0 - 0.5 and (grow_low or y0 < 0):
            y0, grew = inv.transform((box.x0, box.y0 - (box.y0 - bottom) * 1.15))[1], True
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        if not grew:
            return


def random_draws(ax, values, at, horizontal=True, height=0.6, color=GREY):
    """Draw a control made of matched random draws as one grey tick mark per draw, on the effect's own axis.

    values are the draws' effects (say, 20 random neurons from the same layer, each steered like the real one); at
    is the row (or, with horizontal=False, the column) of the bar or dot they are the control for. The reader then
    sees whether the effect lies outside the draws, which one bar for their mean hides.
    """
    lo, hi = at - height / 2, at + height / 2
    if horizontal:
        return ax.vlines(values, lo, hi, color=color, linewidth=1.2 * mpl.rcParams["lines.linewidth"] / 2.2, zorder=3)
    return ax.hlines(values, lo, hi, color=color, linewidth=1.2 * mpl.rcParams["lines.linewidth"] / 2.2, zorder=3)


# ---------------------------------------------------------------------------------------------- uncertainty

class Estimate:
    """A mean, a proportion or a mean difference, with its interval and what the interval resamples.

    value, lo, hi: the estimate and its interval. n: the number of units. unit: what a unit is, in the plural
    ("fine-tunes", "seeds", "prompts"). method: how the interval was computed. kind: "mean", "proportion",
    "paired difference" or "difference". units: each unit's value (for a paired difference, each unit's difference).
    """

    def __init__(self, value, lo, hi, n, unit, level, method, kind, units=None):
        self.value, self.lo, self.hi, self.n, self.unit = float(value), float(lo), float(hi), n, unit
        self.level, self.method, self.kind, self.units = level, method, kind, units

    @property
    def clear(self):
        """Whether the interval excludes zero. For a difference: whether the figure may say the two differ."""
        return self.lo > 0 or self.hi < 0

    def caption(self):
        """The words for the caption: what the interval is and what it resamples."""
        return f"{self.level:.0%} {self.method} over {self.n} {self.unit}"

    def __repr__(self):
        return f"Estimate({self.value:.4g}, {self.lo:.4g} to {self.hi:.4g}; {self.kind}; {self.caption()})"


def _t_crit(df, level):
    """Two-sided critical value of Student's t, by integrating its density (no scipy needed)."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    target = (1 + level) / 2
    def cdf(x):
        t = np.linspace(0, x, 20001)
        y = c * (1 + t * t / df) ** (-(df + 1) / 2)
        return 0.5 + float(np.sum((y[1:] + y[:-1]) / 2) * (t[1] - t[0]))
    lo, hi = 0.0, 1e4
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < target else (lo, mid)
    return (lo + hi) / 2


def _unit_means(values, groups):
    """One number per unit: the values themselves, or each group's mean. Returns (unit ids or None, means)."""
    v = np.asarray(values, dtype=float).ravel()
    if np.isnan(v).any():
        raise ValueError("values contain NaN: drop or explain the missing rows before computing an interval")
    if groups is None:
        return None, v
    g = np.asarray(groups).ravel()
    if len(g) != len(v):
        raise ValueError(f"groups has {len(g)} entries for {len(v)} values")
    ids, inv = np.unique(g, return_inverse=True)
    return ids, np.bincount(inv, weights=v) / np.bincount(inv)


def _mean_interval(m, level, n_boot, seed):
    """Interval for the mean of one number per unit: Student's t below 10 units (a bootstrap over so few is too
    narrow), a percentile bootstrap that resamples units from 10 up."""
    n = len(m)
    if n < 2:
        raise ValueError("one unit has no spread: plot the point itself, and make no claim about a difference")
    if n < 10:
        half = _t_crit(n - 1, level) * m.std(ddof=1) / math.sqrt(n)
        return m.mean() - half, m.mean() + half, "t-interval"
    rng = np.random.default_rng(seed)
    boots, step = [], max(1, 2_000_000 // n)
    for start in range(0, n_boot, step):
        idx = rng.integers(0, n, size=(min(step, n_boot - start), n))
        boots.append(m[idx].mean(axis=1))
    lo, hi = np.quantile(np.concatenate(boots), [(1 - level) / 2, (1 + level) / 2])
    return lo, hi, "bootstrap interval"


def interval(values, groups=None, unit="units", level=0.95, n_boot=10_000, seed=0):
    """The mean with an interval that resamples the unit that was sampled independently.

    values holds one number per row. If several rows come from one unit (many questions about each fine-tune, many
    prompts per seed), pass groups, the unit of each row: each unit is reduced to its mean first, and units, not
    rows, are resampled. Resampling rows that share a unit gives an interval that is far too narrow. unit names the
    units in the plural, for the caption. Below 10 units the interval is Student's t; draw every unit as well.
    """
    _ids, m = _unit_means(values, groups)
    lo, hi, method = _mean_interval(m, level, n_boot, seed)
    return Estimate(m.mean(), lo, hi, len(m), unit, level, method, "mean", m)


def proportion(k, n, unit="items", level=0.95):
    """A proportion k of n independent items with its Wilson interval."""
    if not 0 <= k <= n or n < 1:
        raise ValueError(f"k={k}, n={n}: need 0 <= k <= n and n >= 1")
    z = statistics.NormalDist().inv_cdf((1 + level) / 2)
    ph = k / n
    mid = (ph + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return Estimate(ph, max(0.0, mid - half), min(1.0, mid + half), n, unit, level, "Wilson interval", "proportion")


def difference(a, b, *, paired, groups=None, groups_b=None, unit="units", level=0.95, n_boot=10_000, seed=0):
    """The mean of a minus the mean of b, with its interval. paired has no default: decide it.

    paired=True when the two conditions were measured on the same units (the same models, seeds or prompts): a and
    b are aligned row by row, the interval is of each unit's difference, and noise shared by a unit cancels. With
    groups (the unit of each row, the same for a and b), rows are first averaged within each unit.
    paired=False when the units differ: each side is resampled on its own (groups for a, groups_b for b).
    """
    if paired:
        a_, b_ = np.asarray(a, dtype=float).ravel(), np.asarray(b, dtype=float).ravel()
        if len(a_) != len(b_):
            raise ValueError(f"paired=True needs a and b aligned row by row, got {len(a_)} and {len(b_)} rows")
        _ids, d = _unit_means(a_ - b_, groups)
        lo, hi, method = _mean_interval(d, level, n_boot, seed)
        return Estimate(d.mean(), lo, hi, len(d), unit, level, method, "paired difference", d)
    _, ma = _unit_means(a, groups)
    _, mb = _unit_means(b, groups_b)
    value = ma.mean() - mb.mean()
    if min(len(ma), len(mb)) < 2:
        raise ValueError("one unit on a side has no spread: plot the points, and make no claim about a difference")
    if min(len(ma), len(mb)) < 10:  # Welch's t-interval
        va, vb = ma.var(ddof=1) / len(ma), mb.var(ddof=1) / len(mb)
        se = math.sqrt(va + vb)
        df = (va + vb) ** 2 / (va ** 2 / (len(ma) - 1) + vb ** 2 / (len(mb) - 1)) if se > 0 else 1.0
        half = _t_crit(df, level) * se
        lo, hi, method = value - half, value + half, "Welch t-interval"
    else:
        rng = np.random.default_rng(seed)
        boots = (ma[rng.integers(0, len(ma), size=(n_boot, len(ma)))].mean(axis=1)
                 - mb[rng.integers(0, len(mb), size=(n_boot, len(mb)))].mean(axis=1))
        lo, hi = np.quantile(boots, [(1 - level) / 2, (1 + level) / 2])
        method = "bootstrap interval"
    return Estimate(value, lo, hi, (len(ma), len(mb)), unit, level, method, "difference")


def _register(ax, est):
    fig = ax.figure
    fig._figkit_estimates = getattr(fig, "_figkit_estimates", []) + [est]
    return est


def intervals(ax, positions, estimates, horizontal=False, color=MUTED):
    """Draw each estimate's interval as a line at its position: on a bar, or through a dot.

    Use it in place of a plotting library's default error bars when rows share a unit, since those resample rows:
    fk.intervals(ax, x, [fk.interval(df.score[df.model == m], groups=df.finetune[df.model == m]) for m in models]).
    """
    lw = 1.6 * mpl.rcParams["lines.linewidth"] / 2.2
    los, his = [e.lo for e in estimates], [e.hi for e in estimates]
    for e in estimates:
        _register(ax, e)
    if horizontal:
        return ax.hlines(positions, los, his, color=color, linewidth=lw, zorder=4)
    return ax.vlines(positions, los, his, color=color, linewidth=lw, zorder=4)


def paired(ax, a, b, names=("A", "B"), unit="units", color=None, **interval_kw):
    """Two conditions measured on the same units: each unit's two values joined by a thin grey line, and the two
    means joined in the accent colour. Returns the Estimate of the paired difference (a minus b), for the title's
    claims and the caption. A reader sees at once whether the units move the same way."""
    a_, b_ = np.asarray(a, dtype=float).ravel(), np.asarray(b, dtype=float).ravel()
    est = difference(a_, b_, paired=True, unit=unit, **interval_kw)
    k = mpl.rcParams["lines.linewidth"] / 2.2
    alpha = float(np.clip(12 / max(len(a_), 1), 0.15, 0.9))
    ax.plot([0, 1], np.vstack([a_, b_]), color=GREY, linewidth=0.9 * k, alpha=alpha, zorder=2)
    ax.plot([0, 1], [a_.mean(), b_.mean()], color=color or ACCENT, marker="o", zorder=4)
    ax.set_xticks([0, 1], names)
    ax.set_xlim(-0.35, 1.35)
    ax.grid(False, axis="x")
    return _register(ax, est)


def differences(ax, est, at=0, horizontal=True, color=None, height=0.5, seed=0):
    """A paired difference drawn against zero: each unit's difference as a small grey dot, the mean as a dot in the
    accent colour with its interval as a line, and a thin line at zero. est comes from fk.difference(...,
    paired=True); at is the row (or column) it is drawn in, so several comparisons can share one axis. An interval
    that crosses the zero line is a difference the figure does not establish."""
    if est.units is None:
        raise ValueError("fk.differences draws each unit's difference: pass an Estimate from fk.difference(..., "
                         "paired=True)")
    k = mpl.rcParams["lines.linewidth"] / 2.2
    jitter = at + np.random.default_rng(seed).uniform(-height / 2, height / 2, len(est.units))
    zero = dict(color=MUTED, linewidth=0.9 * k, zorder=1)
    if horizontal:
        ax.scatter(est.units, jitter, s=14 * k, color=GREY, alpha=0.7, linewidths=0, zorder=2)
        ax.hlines(at, est.lo, est.hi, color=color or ACCENT, linewidth=2.4 * k, zorder=4)
        ax.plot([est.value], [at], "o", color=color or ACCENT, zorder=5)
        if not getattr(ax, "_figkit_zero", False):
            ax.axvline(0, **zero)
    else:
        ax.scatter(jitter, est.units, s=14 * k, color=GREY, alpha=0.7, linewidths=0, zorder=2)
        ax.vlines(at, est.lo, est.hi, color=color or ACCENT, linewidth=2.4 * k, zorder=4)
        ax.plot([at], [est.value], "o", color=color or ACCENT, zorder=5)
        if not getattr(ax, "_figkit_zero", False):
            ax.axhline(0, **zero)
    ax._figkit_zero = True
    return _register(ax, est)


def plain_ticks(axis):
    """Plain numbers (1, 10, 100, 0.01) instead of powers of ten on a log axis: plain_ticks(ax.yaxis)."""
    axis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    axis.set_minor_formatter(ticker.NullFormatter())


def _horizontal(c):
    o = getattr(c, "orientation", None)
    if o:
        return o == "horizontal"
    return len(c.patches) > 1 and len({round(p.get_x(), 9) for p in c.patches}) == 1


def _ends(ax, bar, horizontal):
    """How far error bars and dots drawn on a bar reach along its length: seaborn draws error bars as lines,
    ax.bar as collections, and stripplot draws each seed as a dot within the bar's width."""
    i, j = (1, 0) if horizontal else (0, 1)
    lo, hi = (bar.get_y(), bar.get_y() + bar.get_height()) if horizontal else (bar.get_x(), bar.get_x() + bar.get_width())
    pos = (lo + hi) / 2
    tol = 1e-6 * max(1, abs(pos))
    out = []
    for l in ax.get_lines():
        d = l.get_xydata()
        if len(d) == 2 and abs(d[0][i] - pos) < tol and abs(d[1][i] - pos) < tol:
            out += [d[0][j], d[1][j]]
    for coll in ax.collections:
        if isinstance(coll, LineCollection):
            for seg in coll.get_segments():
                if len(seg) == 2 and abs(seg[0][i] - pos) < tol and abs(seg[1][i] - pos) < tol:
                    out += [seg[0][j], seg[1][j]]
        elif isinstance(coll, PathCollection) and coll.get_offset_transform() == ax.transData:
            out += [o[j] for o in coll.get_offsets() if lo <= o[i] <= hi]
    return out


def _category(ax, pos, horizontal):
    """The tick label at a bar's centre, or None."""
    axis = ax.yaxis if horizontal else ax.xaxis
    for t in axis.get_ticklabels():
        if t.get_text() and abs(t.get_position()[1 if horizontal else 0] - pos) < 1e-6 * max(1, abs(pos)):
            return t.get_text()
    return None


# ---------------------------------------------------------------------------------------------- colour vision
# Colour-blindness simulation (Machado, Oliveira & Fernandes 2009, full severity) and CIEDE2000 distance
# (Sharma, Wu & Dalal 2005), ported from viz (https://github.com/safety-research/viz, src/viz/access.py).
# Copyright (c) 2026 Safety Research. Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

CVD = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def _lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _gamma(v):
    v = min(max(v, 0.0), 1.0)
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def simulate(c, kind):
    """The colour as seen with full protanopia, deuteranopia or tritanopia, as hex."""
    lin = [_lin(v) for v in mpl.colors.to_rgb(c)]
    out = [sum(CVD[kind][i][j] * lin[j] for j in range(3)) for i in range(3)]
    return mpl.colors.to_hex([_gamma(v) for v in out])


def lab(c):
    r, g, b = (_lin(v) for v in mpl.colors.to_rgb(c))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(lab1, lab2):
    """CIEDE2000 distance between two CIELAB colours; under about 10, two marks are hard to tell apart."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dtheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dtheta)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def worst_delta_e(a, b):
    """The smallest CIEDE2000 distance between two colours across normal vision and the three colour blindnesses."""
    out = [(delta_e(lab(a), lab(b)), "normal vision")]
    out += [(delta_e(lab(simulate(a, k)), lab(simulate(b, k))), k) for k in CVD]
    return min(out)


def _neutral(c):
    L, a, b = lab(c)
    return math.hypot(a, b) < 8 or L > 85  # greys and pale tints are context, not marks to tell apart


# ---------------------------------------------------------------------------------------------- the check

INTENSIFIERS = ("dramatically", "drastically", "sharply", "significantly", "substantially", "hugely", "massively",
                "vastly", "greatly", "barely", "strikingly", "surprisingly", "remarkably", "notably", "considerably",
                "far more", "far less", "far fewer", "much more", "much less", "way more", "way less", "skyrocketed",
                "plummeted", "soared", "collapsed", "tanked")


def _words(s):
    """Words a reader has to read: tokens with a letter and no digit, so values and counts ("41%", "164 of 400")
    don't count."""
    s = re.sub(r"\d[\d.,]*\s*(?:of|/)\s*\d[\d.,]*", " ", s)
    return sum(1 for w in s.split() if re.search(r"[A-Za-z]", w) and not re.search(r"\d", w))


def _is_number(s):
    return re.fullmatch(r"[-−+]?[\d.,]+\s*[%kKMB]?", s.strip()) is not None


def _title_problems(t, max_words):
    out = []
    lines = t.strip().split("\n")
    if len(lines) > 1:
        out.append(f"title has {len(lines)} lines: shorten it to one")
    n = len(t.split())
    if n > max_words:
        out.append(f"title of {n} words: state the finding in about 10")
    if ";" in t:
        out.append("title has a semicolon, which means two findings: make two figures")
    if re.search(r"[A-Za-z)”\"’']: ", t):
        out.append("title sets up with a colon (\"X: Y\"): state the finding as one plain sentence")
    if "?" in t:
        out.append("title is a question: state the finding")
    if re.search(r"\s[—–-]\s|—", t):
        out.append("title has a dash aside: use one plain sentence")
    if t.rstrip().endswith((".", "!")):
        out.append("drop the full stop at the end of the title")
    low = t.lower()
    for w in INTENSIFIERS:
        if re.search(rf"\b{re.escape(w)}\b", low):
            out.append(f"title says \"{w}\": give the numbers instead")
    return out


def _effective(c, alpha=None):
    """The colour a mark shows on white, after its transparency."""
    r, g, b, a = mpl.colors.to_rgba(c, alpha)
    return mpl.colors.to_hex([a * x + (1 - a) for x in (r, g, b)])


def _marks(ax):
    """(label, colour as drawn, colour as set) for each mark that carries a name: labelled lines and scatter
    points, labelled bar series, and unlabelled bars named by the tick labels at their centres."""
    out = []
    for l in ax.get_lines():
        lab_ = l.get_label()
        if lab_ and not lab_.startswith("_"):
            out.append((lab_, _effective(l.get_color(), l.get_alpha()), mpl.colors.to_hex(l.get_color())))
    for coll in ax.collections:
        lab_ = coll.get_label()
        if isinstance(coll, PathCollection) and lab_ and not lab_.startswith("_") and len(coll.get_facecolor()):
            fc = coll.get_facecolor()[0]
            out.append((lab_, _effective(fc), mpl.colors.to_hex(fc)))
    for c in [c for c in ax.containers if isinstance(c, BarContainer) and c.patches]:
        lab_ = c.get_label()
        if lab_ and not lab_.startswith("_"):
            fc = c.patches[0].get_facecolor()
            out.append((lab_, _effective(fc), mpl.colors.to_hex(fc)))
        else:  # an unlabelled series (seaborn draws one per hue level): each bar takes the tick label at its centre
            h = _horizontal(c)
            for p in c.patches:
                pos = p.get_y() + p.get_height() / 2 if h else p.get_x() + p.get_width() / 2
                cat = _category(ax, pos, h)
                if cat:
                    fc = p.get_facecolor()
                    out.append((cat, _effective(fc), mpl.colors.to_hex(fc)))
    return out


def _plain(s):
    s = re.sub(r"[\(\[].*?[\)\]]", " ", s.lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def _order_problem(ax):
    bars = [c for c in ax.containers if isinstance(c, BarContainer) and c.patches]
    if len(bars) != 1 or len(bars[0].patches) < 3:
        return None
    h = _horizontal(bars[0])
    pts = sorted(((p.get_y() + p.get_height() / 2, p.get_width()) if h else (p.get_x() + p.get_width() / 2,
                                                                           p.get_height())) for p in bars[0].patches)
    labels = [_category(ax, pos, h) for pos, _ in pts]
    vals = [v for _, v in pts if v == v]
    if not any(labels) or any(lab_ and _is_number(lab_) for lab_ in labels):
        return None  # unnamed bars, or numbers (layers, sizes, steps), which have an order of their own
    if all(_roles.get(_key(lab_), ("",))[0] == "ordered" for lab_ in labels if lab_):
        return None
    if all(a <= b for a, b in zip(vals, vals[1:])) or all(a >= b for a, b in zip(vals, vals[1:])):
        return None
    return ("bars aren't in order of their values: sort them, unless the order means something (layers, sizes, "
            "steps); fk.save(..., order=False) keeps it without this warning")


COMPARES = re.compile(
    r"\b(rais\w+|lower\w*|higher|highest|lowest|more|most|less|least|fewer|beat\w*|outperform\w*|improv\w+|increas\w+|"
    r"decreas\w+|reduc\w+|fell|falls?|rose|rises?|drop\w*|gain\w*|better|best|worse|worst|exceed\w*|faster|slower|"
    r"doubl\w+|halv\w+|tripl\w+|than|times as)\b|\bfrom\s+\S*\d\S*\s+to\s+\S*\d", re.IGNORECASE)
NO_DIFFERENCE = re.compile(r"\b(did not|didn't|does not|doesn't|not clearly|no clear|no difference|about the same|"
                           r"as well as|as much as|matched?)\b", re.IGNORECASE)


def _draws_spread(fig, axes):
    """Whether the image shows uncertainty or individual data: intervals, bands, every seed or unit as a mark."""
    if getattr(fig, "_figkit_estimates", None):
        return True
    for a in axes:
        if any(isinstance(c, ErrorbarContainer) for c in a.containers):
            return True
        for coll in a.collections:
            if isinstance(coll, (LineCollection, PolyCollection)) and not isinstance(coll, QuadMesh):
                return True  # interval lines, ticks for random draws, bands
            if isinstance(coll, PathCollection) and len(coll.get_offsets()) >= 3:
                return True  # individual points
        for l in a.get_lines():  # unnamed lines in data coordinates: error bars, a faint line per seed, seed dots
            if l.get_label().startswith("_") and l.get_transform().contains_branch(a.transData) and len(l.get_xdata()):
                return True
    return False


def _spread_problems(fig, axes, titles):
    out = []
    for est in getattr(fig, "_figkit_claims", []):
        if "difference" in est.kind and not est.clear:
            n = est.n if isinstance(est.n, int) else " and ".join(str(x) for x in est.n)
            out.append(f"the title states a difference, but the {est.level:.0%} interval of that difference "
                       f"({est.lo:.3g} to {est.hi:.3g}, over {n} {est.unit}) includes 0: the title says the two did "
                       "not clearly differ, and the drawn interval shows how wide the uncertainty is")
    text = " ".join(t.get_text() for t in titles)
    if getattr(fig, "_figkit_claims", None) or not COMPARES.search(text) or NO_DIFFERENCE.search(text):
        return out
    if any(a.images or any(isinstance(c, QuadMesh) for c in a.collections) for a in axes):
        return out  # a heatmap shows a grid of values, not a comparison with a spread
    named = {_key(m[0]) for a in axes for m in _marks(a)}
    if len(named) >= 2 and not _draws_spread(fig, axes):
        out.append("the title compares conditions, but the image draws no spread: draw every seed or unit as a dot "
                   "(few), or an interval over the unit that was sampled independently (fk.intervals, fk.paired, "
                   "fk.differences), so the image shows how sure the difference is. With one run per condition "
                   "there is nothing to draw: plot the two values as points, title the figure with what that run "
                   "measured, and pass spread=False")
    return out


def check(fig, words=25, min_pt=None, max_series=5, max_panels=4, title_words=12, panel_title_words=6, order=True,
          size=None, spread=True):
    """Return a list of problems: too much text, a title that doesn't state one finding plainly, a title that states
    a difference the drawn uncertainty doesn't support, boxed text, legends that could be direct labels, crowded
    panels, small text for where the figure goes, overlapping or clipped text, colours that break the roles or look
    alike to colour-blind readers, and bars out of order."""
    size = size or _size
    s = SIZES[size]
    min_pt = s["min_pt"] if min_pt is None else min_pt
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    axes = [a for a in fig.axes if a.get_label() != "<colorbar>"]
    ticks, hidden = set(), set()
    for a in fig.axes:
        for ax_, i in ((a.xaxis, 0), (a.yaxis, 1)):
            lo, hi = sorted(ax_.get_view_interval())
            for t in ax_.get_ticklabels(which="both"):  # labels of ticks outside the view are not drawn
                (ticks if lo - 1e-9 * abs(hi - lo) <= t.get_position()[i] <= hi + 1e-9 * abs(hi - lo) else hidden).add(t)
            ticks.add(ax_.get_offset_text())
    texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and t not in hidden]
    undrawn = [t for t in texts if isinstance(t, mpl.text.Annotation) and hasattr(t, "_check_xy")
               and not t._check_xy(r)]  # matplotlib skips a label whose point is outside the axes
    texts = [t for t in texts if t not in undrawn]
    sup = getattr(fig, "_suptitle", None)
    titles = [sup] if sup is not None and sup.get_text().strip() else []
    panel_titles = []
    for a in axes:
        for loc in ("left", "center", "right"):
            t = {"left": a._left_title, "center": a.title, "right": a._right_title}[loc]
            if t.get_text().strip():
                (titles if len(axes) == 1 and not titles else panel_titles).append(t)
    mock = [t for t in texts if t.get_gid() == MOCK_GID]
    free = [t for t in texts if t not in ticks and t not in titles and t not in mock]
    out = []
    if undrawn:
        out.append(f"labels whose point is outside the axes are not drawn: {[t.get_text()[:30] for t in undrawn][:5]}; "
                   "move the point inside, or pass annotation_clip=False")
    n_words = sum(_words(t.get_text()) for t in free)
    budget = words + 10 * (len(axes) - 1)
    if n_words > budget:
        out.append(f"{n_words} words outside the title, tick labels and numbers (budget {budget}): move definitions "
                   "and statistics into the caption")
    wide_title = False
    for t in titles:
        out += _title_problems(t.get_text(), title_words)
        if t.get_window_extent(r).x1 > fig.bbox.x1 + 1:
            wide_title = True
            out.append("title is wider than the figure at this size: shorten it to one line")
    for t in panel_titles:
        n = len(t.get_text().split())
        if n > panel_title_words:
            out.append(f"panel title of {n} words {t.get_text()[:50]!r}: name the panel in ≤ {panel_title_words} words")
    boxed = [t.get_text()[:40] for t in free if t.get_bbox_patch() is not None]
    if boxed:
        out.append(f"text in boxes {boxed}: no annotation boxes; label the mark directly or use the caption")
    legends = [a.get_legend() for a in fig.axes if a.get_legend()] + list(fig.legends)
    for lg in legends:
        if len(lg.get_texts()) > 4:
            out.append(f"legend with {len(lg.get_texts())} entries: cut series, or grey the context and label directly")
        elif any(isinstance(h, mpl.lines.Line2D) and h.get_linestyle() not in ("None", "")
                 for h in lg.legend_handles):
            out.append("legend for lines: use fk.label_lines(ax) to name them at their ends")
    if len(axes) > max_panels:
        out.append(f"{len(axes)} panels: is this a table drawn as a plot? Show the one comparison the claim needs")
    for a in axes:
        n = len([l for l in a.get_lines() if not l.get_label().startswith("_")]) + len(a.containers)
        if n > max_series:
            out.append(f"panel {a.get_title() or a.get_ylabel()!r} has {n} series: keep ≤ {max_series - 1}, grey the rest")
    w, _h = fig.get_size_inches()
    scale = min(1.0, s["width"] / w)
    if scale < 1:
        out.append(f"figure is {w:.1f} in wide: shown at the {size} width ({s['width']:g} in) it shrinks to "
                   f"{scale:.0%}, and its text with it; keep the default size, or fk.use(size=...)")
    small = sorted({round(float(t.get_fontsize() * scale), 1) for t in texts if t.get_fontsize() * scale < min_pt})
    if small:
        out.append(f"font sizes {small} pt{' as shown' if scale < 1 else ''} below {min_pt:g} pt for {size}")
    boxes = [(t, t.get_window_extent(r)) for t in texts]
    fb = fig.bbox
    clipped = [t.get_text()[:30] for t, b in boxes if (b.x0 < fb.x0 - 1 or b.x1 > fb.x1 + 1 or b.y0 < fb.y0 - 1
                                                       or b.y1 > fb.y1 + 1) and not (wide_title and t in titles)]
    if clipped:
        out.append(f"text cut off at the figure edge: {clipped[:5]}")
    hits = []
    for i, (t1, b1) in enumerate(boxes):
        for t2, b2 in boxes[i + 1:]:
            if b1.width and b2.width and b1.padded(-1).overlaps(b2.padded(-1)):
                hits.append((t1.get_text()[:20], t2.get_text()[:20]))
    if hits:
        out.append(f"{len(hits)} overlapping text pairs, e.g. {hits[:3]}")
    if any(len(t.get_text()) > 3 and t.get_rotation() not in (0, 90, 270) for t in ticks if t.get_visible()):
        out.append("rotated tick labels: shorten them, or swap axes so the labels run horizontally")
    marks = [m for a in axes for m in _marks(a)]
    for lab_, _shown, set_ in marks:  # each named condition takes its role's colour
        lab_ = _key(lab_)
        if lab_ in _roles:
            role, want = _roles[lab_]
            if set_.lower() != want.lower():
                out.append(f"\"{lab_}\" is {set_} here, but its role ({role}) gives {want}: use fk.color(\"{lab_}\")")
        else:
            near = next((k for k in _roles if _plain(k) == _plain(lab_)), None)
            if near:
                out.append(f"\"{lab_}\" has no role but looks like \"{near}\" ({_roles[near][0]}): use the exact name "
                           f"from {_roles_from}, or add it there")
    seen = {}  # colour as drawn -> a label that has it
    for lab_, shown, _set in marks:
        if not _neutral(shown) and _roles.get(_key(lab_), ("",))[0] != "ordered":
            seen.setdefault(shown.lower(), lab_)
    cols = list(seen)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            d, kind = worst_delta_e(cols[i], cols[j])
            if d < 10:
                out.append(f"\"{seen[cols[i]]}\" and \"{seen[cols[j]]}\" look alike with {kind} (distance {d:.0f}): "
                           "use colours from different roles, or label each mark directly")
    if order:
        for a in axes:
            p = _order_problem(a)
            if p:
                out.append(p)
    if spread:
        out += _spread_problems(fig, axes, titles)
    counts = {}
    for m in out:  # one line per kind of problem
        counts[m] = counts.get(m, 0) + 1
    return [m if n == 1 else f"{m} (x{n})" for m, n in counts.items()]


def save(fig, path, mock=False, sample=None, **check_kw):
    """Check the figure, print what to fix, and save it. The extension sets the format; PNG at 200 dpi on screens
    and slides, 300 dpi for print sizes.

    mock=True writes "Fake data" in the top right corner, for a figure drawn before the real results exist.
    sample="30 of 1,370 files" writes "Random sample: 30 of 1,370 files" there, for a figure drawn from a random
    subsample of the data; draw the subsample with a seeded generator.
    """
    stamp = "Fake data" if mock else f"Random sample: {sample}" if sample else None
    if stamp:  # on the title's line, at the right; without a title, a strip is kept for it
        fs = SIZES[_size]["ticks"]
        eng = fig.get_layout_engine()
        if getattr(fig, "_suptitle", None) is None and eng is not None and "rect" in eng.get():
            eng.set(rect=(0, 0, 1, 1 - fs * 1.8 / 72 / fig.get_size_inches()[1]))
        fig.text(0.995, 0.995, stamp, ha="right", va="top", color=MUTED, style="italic", fontsize=fs,
                 gid=MOCK_GID)
    problems = check(fig, **check_kw)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    if problems:
        print(f"FIGURE CHECK {path.name}: {len(problems)} to fix before anyone sees it")
        for p in problems:
            print("  -", p)
    else:
        print(f"FIGURE CHECK {path.name}: ok")
    return problems


if __name__ == "__main__":  # self-check: a cluttered figure fails, a clean one passes
    import numpy as np
    mpl.use("Agg")
    use()
    x = np.arange(1, 20)
    fig, axs = plt.subplots(2, 3, figsize=(14, 7))
    fig.suptitle("Methods differ dramatically in how fast the loss recovers when the top k heads are kept; why?")
    for a in axs.flat:
        for i in range(7):
            a.plot(x, x ** -(0.2 * i + 0.3), label=f"method {i}")
        a.text(5, 0.5, "BF10 = 1e+251 | 1e+252 meaningful", bbox=dict(fc="w"))
        a.legend()
    bad = check(fig)
    assert len(bad) >= 8, bad
    fig, ax = plt.subplots()
    ax.plot(x, x ** -0.9, color=ACCENT, label="linear probe")
    ax.plot(x, x ** -0.4, color=GREY, label="random baseline")
    label_lines(ax)
    ax.set(xlabel="Layer", ylabel="Probe error")
    title(fig, "The probe's error falls faster than the baseline's")
    assert any("draws no spread" in p for p in check(fig)), check(fig)  # two bare lines can't carry a comparison
    for power, c in ((-0.9, ACCENT), (-0.4, GREY)):  # a band for the interval over seeds
        ax.fill_between(x, 0.9 * x ** power, 1.1 * x ** power, color=c, alpha=0.2, linewidth=0)
    assert check(fig) == [], check(fig)
    rng = np.random.default_rng(0)
    base = rng.normal(60, 12, 20)
    assert difference(base + 2 + rng.normal(0, 1, 20), base, paired=True).clear
    assert not difference(base + 2 + rng.normal(0, 1, 20), base, paired=False).clear
    print("figkit self-check ok;", len(bad), "problems found in the cluttered figure")
