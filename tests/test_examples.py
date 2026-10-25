"""Every example passes its own check, has its picture beside it, and is listed in the README and SKILL.md."""
import runpy
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.figure
import matplotlib.pyplot as plt
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "skills" / "figures" / "examples"
sys.path.insert(0, str(EXAMPLES.parent))
import figkit as fk


@pytest.mark.parametrize("script", sorted(EXAMPLES.glob("*.py")), ids=lambda p: p.name)
def test_each_example_passes_its_own_check(script, monkeypatch):
    results = []
    real = fk.save
    monkeypatch.setattr(fk, "save", lambda fig, path, **kw: results.append(real(fig, path, **kw)))
    monkeypatch.setattr(matplotlib.figure.Figure, "savefig", lambda self, *a, **k: None)  # leave the PNGs alone
    runpy.run_path(str(script), run_name="__main__")
    plt.close("all")
    assert results, f"{script.name} saves no figure"
    assert all(r == [] for r in results), results


@pytest.mark.parametrize("example", sorted([*EXAMPLES.glob("*.py"), *EXAMPLES.glob("*.html")]), ids=lambda p: p.name)
def test_each_example_has_its_picture(example):
    assert example.with_suffix(".png").is_file()


def test_the_lists_of_examples_are_current():
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "gallery.py"), "--check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
