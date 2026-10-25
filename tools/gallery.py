"""Write the list of examples into README.md and SKILL.md from the examples' own headers.

Each example in skills/figures/examples/ opens with a docstring (Python) or a comment (HTML) holding an "Answers:"
line, the question the figure answers, and a "Shows:" line, what this example draws. The README gets a table and
SKILL.md a list, grouped by question in the order of QUESTIONS, between <!-- examples --> and <!-- /examples -->.

    python tools/gallery.py           rewrite both
    python tools/gallery.py --check   exit 1 if either is out of date (tests/test_examples.py runs this)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "skills" / "figures" / "examples"
TARGETS = [ROOT / "README.md", ROOT / "skills" / "figures" / "SKILL.md"]
QUESTIONS = [
    "Is one condition higher than another?",
    "How do several methods rank, and how sure are we?",
    "How does a measure change over training, or across layers?",
    "How does an effect grow with a dose?",
    "Does a trend follow a scaling law?",
    "Which method gives the best trade-off?",
    "How well does a probe or monitor separate two classes?",
    "Is one model better calibrated than another?",
    "Where in the model is the effect?",
    "Where in the text does a score fire?",
    "What did the model say?",
    "How does the method work?",
    "What was done and what was found, at a glance?",
    "Which method does the task best, and how do the methods differ?",
]
FIELD = re.compile(r"^\s*[A-Z][A-Za-z ,'()]*:")  # "Claim:", "Render, from this folder:", "Caption (goes under it):"


def header(path):
    text = path.read_text()
    m = re.match(r'\s*"""(.*?)"""', text, re.S) if path.suffix == ".py" else re.search(r"<!--(.*?)-->", text, re.S)
    return m.group(1) if m else ""


def field(text, name):
    """A field's value, with any lines that continue it, up to a blank line or the next field."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"^\s*{name}:", line):
            parts = [line.split(":", 1)[1].strip()]
            for nxt in lines[i + 1:]:
                if not nxt.strip() or FIELD.match(nxt):
                    break
                parts.append(nxt.strip())
            return " ".join(parts)
    return None


def examples():
    out = []
    for p in sorted(EXAMPLES.iterdir()):
        if p.suffix not in (".py", ".html"):
            continue
        h = header(p)
        q, shows = field(h, "Answers"), field(h, "Shows")
        if q is None or shows is None:
            sys.exit(f"{p.name}: its header needs an Answers: line and a Shows: line")
        if q not in QUESTIONS:
            sys.exit(f"{p.name}: {q!r} is not one of the questions in tools/gallery.py")
        out.append((QUESTIONS.index(q), p.name, q, shows))
    return sorted(out)


def readme_block(items):
    rows = ["| Question | Example | What it shows |", "|---|---|---|"]
    last = None
    for _i, name, q, shows in items:
        rows.append(f"| {q if q != last else ''} | `{name}` | {shows} |")
        last = q
    return "\n".join(rows)


def skill_block(items):
    by_q = {}
    for _i, name, q, _shows in items:
        by_q.setdefault(q, []).append(f"`{name}`")
    return "\n".join(f"- {q} {', '.join(names)}" for q, names in by_q.items())


def main():
    items = examples()
    stale = []
    for path, block in zip(TARGETS, (readme_block(items), skill_block(items))):
        old = path.read_text()
        pat = re.compile(r"(<!-- examples -->\n)(?:.*?\n)?(<!-- /examples -->)", re.S)
        if not pat.search(old):
            sys.exit(f"{path}: no <!-- examples --> and <!-- /examples --> markers")
        new = pat.sub(lambda m: m.group(1) + block + "\n" + m.group(2), old)
        if new != old:
            stale.append(path.name)
            if "--check" not in sys.argv:
                path.write_text(new)
    if "--check" in sys.argv and stale:
        print(f"out of date: {', '.join(stale)}; run python tools/gallery.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
