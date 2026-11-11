"""figkit's check: what it catches, and what it lets through."""
import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "figures"))
import figkit as fk


@pytest.fixture(autouse=True)
def house_style():
    fk.use(roles={})
    yield
    plt.close("all")


def line_figure():
    fig, ax = plt.subplots()
    x = np.arange(12)
    ax.plot(x, 0.5 + 0.04 * x, color=fk.ACCENT, label="trained model")
    ax.plot(x, 0.5 + 0.0 * x, color=fk.GREY, label="random labels")
    ax.set(xlabel="Layer", ylabel="Probe accuracy")
    fk.label_lines(ax)
    return fig, ax


def found(problems, phrase):
    return any(phrase in p for p in problems)


# ------------------------------------------------------------------------------------------------- titles

def test_a_plain_figure_with_a_plain_title_passes():
    fig, _ = line_figure()
    fk.title(fig, "A linear probe reads tense from layer 6 on")
    assert fk.check(fig) == []


def test_a_figure_without_a_title_passes():
    fig, _ = line_figure()
    assert fk.check(fig) == []


@pytest.mark.parametrize("title, phrase", [
    ("Probe accuracy rises with depth; controls stay at chance", "semicolon"),
    ("The key result: probes beat controls", "colon"),
    ("Do probes beat controls?", "question"),
    ("Probes beat controls — by a lot", "dash"),
    ("Probes beat controls.", "full stop"),
    ("Accuracy rose dramatically after layer 6", "dramatically"),
    ("Probe accuracy rises steadily from layer six through layer twenty and then holds", "words"),
    ("Probes beat controls\nat every layer", "lines"),
])
def test_title_rules(title, phrase):
    fig, _ = line_figure()
    fk.title(fig, title)
    assert found(fk.check(fig), phrase), fk.check(fig)


def test_a_single_panels_axes_title_counts_as_the_title():
    fig, ax = line_figure()
    ax.set_title("Do probes beat controls?")
    assert found(fk.check(fig), "question")


def test_a_title_too_wide_for_a_column_figure_is_caught():
    fk.use(size="column", roles={})
    fig, _ = line_figure()
    fk.title(fig, "A linear probe reads the tense of each sentence from layer 6")
    assert found(fk.check(fig), "wider than the figure")


def test_panel_titles_name_panels_briefly():
    fig, (a, b) = plt.subplots(1, 2)
    a.plot([0, 1], [0, 1], color=fk.ACCENT)
    b.plot([0, 1], [1, 0], color=fk.ACCENT)
    a.set_title("Induction")
    b.set_title("Indirect object identification on the templates from Wang et al.")
    fk.title(fig, "Patching recovers both circuits")
    problems = fk.check(fig)
    assert found(problems, "panel title of 10 words") and not found(problems, "title of 5 words")


# ------------------------------------------------------------------------------------------------- words

def test_values_and_counts_are_not_words():
    assert fk._words("41%  164 of 400") == 0
    assert fk._words("Loss increase (nats)") == 3
    assert fk._words("n = 400") == 1


def test_value_labels_with_counts_pass_a_small_word_budget():
    fig, ax = plt.subplots()
    cats = ["plain RL", "hacking penalty", "inoculation prompt"]
    ax.barh(cats, [41, 28, 12], color=[fk.GREY, fk.GREY, fk.ACCENT])
    fk.label_values(ax, fmt="{:.0f}%", notes={"plain RL": "164 of 400", "hacking penalty": "112 of 400",
                                              "inoculation prompt": "48 of 400"})
    ax.set(xlabel="Episodes with reward hacking")
    assert fk.check(fig, words=5) == []  # four words in the axis label; ticks, values and counts don't count


def test_value_labels_sit_above_seed_dots_and_stay_inside_the_axes():
    fig, ax = plt.subplots()
    ax.bar(["weight decay", "dropout", "no weight decay"], [99, 41, 32], color=[fk.ACCENT, fk.GREY, fk.GREY])
    ax.scatter([0, 0, 1, 1, 2, 2], [100, 98, 52, 30, 36, 28], color=fk.INK, zorder=3)
    fk.label_values(ax, fmt="{:.0f}%")
    fig.canvas.draw()
    labels = [t for t in ax.texts]
    assert [t.get_text() for t in labels] == ["99%", "41%", "32%"]
    assert labels[1].xy[1] == 52  # above the highest dot on its bar
    box = ax.get_window_extent()
    assert all(t.get_window_extent().y1 <= box.y1 + 0.5 for t in labels)


# ------------------------------------------------------------------------------------------------- colour roles

def test_roles_colour_each_condition():
    fk.use(roles={"baseline": "plain RL", "intervention": "inoculation prompt", "second": "penalty",
                  "ordered": ["70M", "410M", "1.4B"]})
    assert fk.color("inoculation prompt") == fk.ACCENT
    assert fk.color("plain RL") == fk.GREY
    assert fk.color("penalty") == fk.BLUE
    assert fk.color("something else") == fk.GREY
    assert fk.palette(["plain RL", "inoculation prompt"]) == {"plain RL": fk.GREY, "inoculation prompt": fk.ACCENT}
    shades = [sum(matplotlib.colors.to_rgb(fk.color(s))) for s in ["70M", "410M", "1.4B"]]
    assert shades[0] > shades[1] > shades[2]  # light to dark


def test_a_condition_coloured_against_its_role_is_caught():
    fk.use(roles={"control": "plain RL", "intervention": "inoculation prompt"})
    fig, ax = plt.subplots()
    x = np.arange(5)
    ax.plot(x, x, color=fk.BLUE, label="inoculation prompt")
    ax.plot(x, x / 2, color=fk.GREY, label="Plain RL (n=400)")
    fk.label_lines(ax)
    problems = fk.check(fig)
    assert found(problems, "its role (intervention)"), problems
    assert found(problems, "looks like \"plain RL\""), problems


def test_roles_apply_to_bars_named_by_their_tick_labels():
    fk.use(roles={"control": "plain RL", "intervention": "inoculation prompt"})
    fig, ax = plt.subplots()
    ax.bar(["plain RL", "inoculation prompt"], [41, 12], color=[fk.GREY, fk.BLUE])
    assert found(fk.check(fig), "\"inoculation prompt\" is #0072b2 here")


def test_roles_apply_to_seaborn_bars_with_one_hue_level_per_bar():
    import pandas as pd
    import seaborn as sns
    fk.use(roles={"control": "plain RL", "intervention": "inoculation prompt"})
    df = pd.DataFrame({"condition": ["plain RL", "inoculation prompt"], "rate": [41, 12]})
    fig, ax = plt.subplots()
    sns.barplot(df, x="condition", y="rate", hue="condition", palette={"plain RL": fk.GREY,
                "inoculation prompt": fk.BLUE}, saturation=1, legend=False)
    assert found(fk.check(fig), "\"inoculation prompt\" is #0072b2 here")


def test_a_label_wrapped_onto_two_lines_keeps_its_role():
    fk.use(roles={"control": "no honesty data", "intervention": "honesty data and steering"})
    assert fk.color("honesty data\nand steering") == fk.ACCENT
    fig, ax = plt.subplots()
    ax.bar(["no honesty data", "honesty data\nand steering"], [37, 9], color=[fk.GREY, fk.ACCENT])
    assert fk.check(fig) == []


def test_a_roles_file_above_the_script_is_found(tmp_path, monkeypatch):
    (tmp_path / "figure-roles.json").write_text('{"baseline": "closed book", "intervention": ["with search"]}')
    sub = tmp_path / "figures"
    sub.mkdir()
    monkeypatch.chdir(sub)
    monkeypatch.setattr(sys.modules["__main__"], "__file__", str(sub / "make_figure.py"), raising=False)
    fk.use()
    assert fk.color("with search") == fk.ACCENT and fk.color("closed book") == fk.GREY
    assert fk.roles()[1] == str(tmp_path / "figure-roles.json")


def test_an_unknown_role_is_an_error():
    with pytest.raises(ValueError):
        fk.use(roles={"treatment": "x"})


# ------------------------------------------------------------------------------------------------- colour vision

def test_ciede2000_matches_the_published_test_pairs():
    pairs = [((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
             ((50.0, -1.3802, -84.2814), (50.0, 0.0, -82.7485), 1.0000),
             ((50.0, 2.5, 0.0), (73.0, 25.0, -18.0), 27.1492),
             ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
             ((2.0776, 0.0795, -1.1350), (0.9033, -0.0636, -0.5514), 0.9082)]
    for a, b, want in pairs:
        assert fk.delta_e(a, b) == pytest.approx(want, abs=1e-3)


def test_simulation_keeps_white_and_black_and_knows_the_hard_pairs():
    for kind in fk.CVD:
        assert fk.simulate("#FFFFFF", kind) == "#ffffff"
        assert fk.simulate("#000000", kind) == "#000000"
    assert fk.worst_delta_e("#FF7F0E", "#2CA02C")[0] < 5     # matplotlib's orange and green, for protanopes
    assert fk.worst_delta_e("#E69F00", "#56B4E9")[0] > 40


def test_the_house_palette_stays_apart():
    for a, b in itertools.combinations(fk.CATEGORICAL, 2):
        assert fk.worst_delta_e(a, b)[0] >= 10, (a, b)


def test_colours_that_look_alike_to_colour_blind_readers_are_caught():
    fig, ax = plt.subplots()
    x = np.arange(5)
    ax.plot(x, x, color="#FF7F0E", label="method A")
    ax.plot(x, x + 1, color="#2CA02C", label="method B")
    fk.label_lines(ax)
    assert found(fk.check(fig), "look alike with"), fk.check(fig)


# ------------------------------------------------------------------------------------------------- sizes

def test_a_figure_too_wide_for_a_paper_column_is_caught():
    fk.use(size="column", roles={})
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([0, 1], [0, 1], color=fk.ACCENT)
    ax.set(xlabel="Layer", ylabel="Accuracy")
    problems = fk.check(fig)
    assert found(problems, "shrinks to 46%"), problems
    assert found(problems, "below 7 pt for column"), problems


@pytest.mark.parametrize("size", list(fk.SIZES))
def test_each_size_draws_a_passing_figure_at_its_default_size(size):
    fk.use(size=size, roles={})
    fig, _ = line_figure()
    fk.title(fig, "A probe reads tense from layer 6 on")
    assert fk.check(fig) == []


# ------------------------------------------------------------------------------------------------- controls

def test_random_draws_put_one_tick_per_draw_in_the_effect_row_and_the_figure_still_passes():
    fig, ax = plt.subplots()
    ax.barh(["afraid", "relieved", "hope"], [2.4, 1.8, 0.5], color=fk.ACCENT)
    rng = np.random.default_rng(0)
    ticks = [fk.random_draws(ax, rng.normal(0, 0.6, 20), at=i) for i in range(3)]
    ax.set(xlabel="Change in choice preference (nats)")
    assert all(len(t.get_segments()) == 20 for t in ticks)
    y0, y1 = ticks[1].get_segments()[0][:, 1]
    assert y0 < 1 < y1
    assert fk.check(fig) == []


# ------------------------------------------------------------------------------------------------- order

def test_bars_out_of_value_order_get_a_warning_unless_told_otherwise():
    fig, ax = plt.subplots()
    ax.bar(["induction", "indirect object", "greater-than"], [2.2, 0.9, 1.6], color=fk.GREY)
    ax.set(ylabel="Loss increase (nats)")
    assert found(fk.check(fig), "order of their values")
    assert not found(fk.check(fig, order=False), "order of their values")


def test_sorted_bars_and_numbered_bars_pass():
    fig, (a, b) = plt.subplots(1, 2)
    a.bar(["A", "B", "C"], [2.2, 1.6, 0.9], color=fk.GREY)
    b.bar(["1", "2", "3"], [2.2, 0.9, 1.6], color=fk.GREY)
    assert not found(fk.check(fig), "order of their values")


# ------------------------------------------------------------------------------------------------- mocks

def test_a_mock_says_fake_data_and_still_passes(tmp_path):
    fig, _ = line_figure()
    assert fk.save(fig, tmp_path / "mock.png", mock=True) == []
    assert [t.get_text() for t in fig.texts] == ["Fake data"]


def test_a_mock_with_a_title_passes(tmp_path):
    fig, _ = line_figure()
    fk.title(fig, "A probe reads tense from layer 6 on")
    assert fk.save(fig, tmp_path / "mock.png", mock=True) == []


# ------------------------------------------------------------------------------------------------- clutter

def test_a_cluttered_figure_fails_on_every_count():
    fig, axs = plt.subplots(2, 3, figsize=(14, 7))
    fig.suptitle("Methods differ dramatically in how fast the loss recovers when the top k heads are kept; why?")
    x = np.arange(1, 20)
    for a in axs.flat:
        for i in range(7):
            a.plot(x, x ** -(0.2 * i + 0.3), label=f"method {i}")
        a.text(5, 0.5, "BF10 = 1e+251 | 1e+252 meaningful", bbox=dict(fc="w"))
        a.legend()
    problems = fk.check(fig)
    for phrase in ["title of 17 words", "semicolon", "question", "dramatically", "text in boxes", "legend with 7",
                   "6 panels", "7 series", "shrinks to 71%", "overlapping"]:
        assert found(problems, phrase), (phrase, problems)


# ------------------------------------------------------------------------------------------------ uncertainty

def two_bars(seeds=False, intervals=False):
    fig, ax = plt.subplots()
    ax.bar(["with weight decay", "without"], [0.9, 0.6], color=[fk.ACCENT, fk.GREY])
    ax.set(ylabel="Test accuracy")
    if seeds:
        ax.scatter([0, 0, 0, 1, 1, 1], [0.88, 0.9, 0.92, 0.55, 0.6, 0.65], s=20, color=fk.INK, zorder=3)
    if intervals:
        rng = np.random.default_rng(0)
        fk.intervals(ax, [0, 1], [fk.interval(rng.normal(m, 0.05, 30), unit="seeds") for m in (0.9, 0.6)])
    return fig


@pytest.mark.parametrize("df, want", [(1, 12.706), (4, 2.776), (30, 2.042), (7.5, 2.335)])
def test_students_t_critical_values_match_the_tables(df, want):
    assert fk._t_crit(df, 0.95) == pytest.approx(want, abs=2e-3)


def test_below_ten_units_the_interval_is_students_t():
    est = fk.interval([1.0, 2.0, 3.0, 4.0, 5.0], unit="seeds")
    half = 2.776 * np.std([1, 2, 3, 4, 5], ddof=1) / np.sqrt(5)
    assert (est.value, est.n, est.method) == (3.0, 5, "t-interval")
    assert (est.lo, est.hi) == pytest.approx((3 - half, 3 + half), abs=2e-3)
    assert est.caption() == "95% t-interval over 5 seeds"


def test_an_interval_resamples_units_not_the_rows_that_share_one():
    rng = np.random.default_rng(0)
    unit = np.repeat(np.arange(20), 200)                      # 20 fine-tunes, 200 questions each
    values = rng.normal(0, 1, 20)[unit] + rng.normal(0, 0.3, 4000)
    by_row, by_unit = fk.interval(values), fk.interval(values, groups=unit, unit="fine-tunes")
    assert (by_row.n, by_unit.n) == (4000, 20)
    assert by_unit.hi - by_unit.lo > 5 * (by_row.hi - by_row.lo)
    assert by_unit.method == "bootstrap interval"
    again = fk.interval(values, groups=unit, unit="fine-tunes")
    assert (again.lo, again.hi) == (by_unit.lo, by_unit.hi)   # seeded, so it repeats


def test_one_unit_has_no_interval():
    with pytest.raises(ValueError, match="no spread"):
        fk.interval([0.4, 0.5, 0.6], groups=["a", "a", "a"])


def test_a_proportion_gets_its_wilson_interval():
    est = fk.proportion(164, 400)
    assert (est.lo, est.hi) == pytest.approx((0.3629, 0.4588), abs=5e-4)


def test_a_paired_difference_sees_what_separate_intervals_hide():
    rng = np.random.default_rng(1)
    base = rng.normal(60, 12, 20)                             # units differ far more than the conditions do
    a, b = base + 2 + rng.normal(0, 1, 20), base
    assert fk.difference(a, b, paired=True, unit="models").clear
    assert not fk.difference(a, b, paired=False, unit="models").clear


def test_the_author_must_say_whether_a_difference_is_paired():
    with pytest.raises(TypeError):
        fk.difference([1, 2, 3], [1, 2, 4])
    with pytest.raises(ValueError, match="aligned"):
        fk.difference([1, 2, 3], [1, 2], paired=True)


def test_a_title_comparing_conditions_needs_spread_in_the_image():
    for kw, ok in [({}, False), ({"seeds": True}, True), ({"intervals": True}, True)]:
        fig = two_bars(**kw)
        fk.title(fig, "Weight decay raised test accuracy from 60% to 90%")
        hit = [p for p in fk.check(fig) if "draws no spread" in p]
        assert bool(hit) != ok, (kw, hit)
    fig = two_bars()
    fk.title(fig, "Weight decay raised test accuracy from 60% to 90%")
    assert not [p for p in fk.check(fig, spread=False) if "spread" in p]


def test_a_title_that_states_no_difference_or_names_one_series_is_left_alone():
    fig = two_bars()
    fk.title(fig, "The two settings did not clearly differ in test accuracy")
    assert not [p for p in fk.check(fig) if "spread" in p]
    fig, ax = plt.subplots()
    ax.plot(np.arange(10), np.linspace(3, 1, 10), color=fk.ACCENT, label="training loss")
    ax.set(xlabel="Step", ylabel="Loss")
    fk.title(fig, "Training loss fell from 3 to 1 in this run")
    assert not [p for p in fk.check(fig) if "spread" in p]


def test_a_claimed_difference_whose_interval_includes_zero_is_refused():
    rng = np.random.default_rng(2)
    base = rng.normal(60, 12, 20)
    for shift, ok in [(8.0, True), (0.3, False)]:
        fig, ax = plt.subplots()
        gain = fk.paired(ax, base + shift + rng.normal(0, 4, 20), base, names=("with circuits", "without"),
                         unit="fine-tunes")
        ax.set(ylabel="Accuracy (%)")
        fk.title(fig, "Adding circuits raised accuracy on held-out fine-tunes", claims=gain)
        hit = [p for p in fk.check(fig) if "includes 0" in p]
        assert bool(hit) != ok, (shift, gain, hit)
        assert not [p for p in fk.check(fig) if "draws no spread" in p]


def test_differences_draw_every_unit_the_interval_and_zero_and_the_figure_passes():
    rng = np.random.default_rng(3)
    base = rng.normal(60, 12, 20)
    gain = fk.difference(base + 6 + rng.normal(0, 3, 20), base, paired=True, unit="models")
    fig, ax = plt.subplots()
    assert fk.differences(ax, gain, at=0) is gain
    ax.set_yticks([0], ["Activation probe"])
    ax.set(xlabel="Accuracy gain over baseline (points)")
    fk.title(fig, "The probe beat the baseline on the same 20 models", claims=gain)
    assert fk.check(fig) == [], fk.check(fig)
    assert len(ax.collections[0].get_offsets()) == 20
    with pytest.raises(ValueError, match="paired=True"):
        fk.differences(ax, fk.difference(base, base[:15] + 1, paired=False))


def test_a_figure_from_a_random_subsample_says_so(tmp_path):
    fig, _ = line_figure()
    assert fk.save(fig, tmp_path / "sample.png", sample="30 of 1,370 files") == []
    assert any(t.get_text() == "Random sample: 30 of 1,370 files" for t in fig.texts)
