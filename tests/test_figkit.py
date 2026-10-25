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
