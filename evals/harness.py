"""Run one isolated headless Claude Code session and save everything it printed.

Both arms use the same command. Isolation comes from:
  --setting-sources local   no user or project settings: no ~/.claude/CLAUDE.md, user skills, user hooks or
                            installed plugins (the run directory is fresh and has no .claude/ of its own)
  --strict-mcp-config       no MCP servers or connectors
  --settings autoMemoryEnabled=false   no auto memory, which would otherwise be shared between runs
  a minimal environment     only HOME, USER, PATH (the eval's venv first), LANG and, if set, your API key or
                            CLAUDE_CONFIG_DIR, so no variables leak from a parent Claude Code session
The plugin arm adds only --plugin-dir <this repository>.
(--safe-mode would also isolate, but it ignores --plugin-dir, so it cannot give the plugin arm.)
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

EVALS = Path(__file__).resolve().parent
PLUGIN_ROOT = EVALS.parent
VENV_BIN = EVALS / ".venv" / "bin"
MODEL = "claude-opus-5-5"
EFFORT = "high"


def env():
    claude = shutil.which("claude")
    if claude is None:
        raise SystemExit("claude not found on PATH")
    keep = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "LANG", "ANTHROPIC_API_KEY", "CLAUDE_CONFIG_DIR")
            if k in os.environ}
    path = [str(VENV_BIN), str(Path(claude).resolve().parent), str(Path(claude).parent), "/usr/local/bin", "/usr/bin", "/bin"]
    return {**keep, "PATH": ":".join(dict.fromkeys(path)), "TERM": "dumb"}


def command(arm, prompt, tools=None, budget=10.0):
    cmd = ["claude", "-p", prompt, "--model", MODEL, "--effort", EFFORT,
           "--setting-sources", "local", "--strict-mcp-config",
           "--permission-mode", "bypassPermissions",
           "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--max-budget-usd", str(budget),
           "--settings", json.dumps({"autoMemoryEnabled": False})]
    if tools is not None:
        cmd += ["--tools", tools]
    if arm == "plugin":
        cmd += ["--plugin-dir", str(PLUGIN_ROOT)]
    elif arm != "base":
        raise ValueError(arm)
    return cmd


def public(text, cwd):
    """text with this machine's paths replaced by <work_root>, <repository> and ~, for files kept in git."""
    return (str(text).replace(str(Path(cwd).parent), "<work_root>").replace(str(PLUGIN_ROOT), "<repository>")
            .replace(os.path.expanduser("~"), "~"))


def run(arm, prompt, cwd, out_dir, transcript_dir=None, tools=None, timeout=1800, budget=10.0):
    """Run a session in cwd. Write result.json, command.json and stderr.txt to out_dir, and the full transcript
    (transcript.jsonl and its init event, init.json) to transcript_dir, which defaults to out_dir. The
    transcripts hold this machine's paths and are kept out of git; the other files have them replaced."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir = Path(transcript_dir or out_dir)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    cmd = command(arm, prompt, tools, budget)
    t0 = time.time()
    with open(transcript_dir / "transcript.jsonl", "w") as f, open(out_dir / "stderr.txt", "w") as e:
        try:
            p = subprocess.run(cmd, cwd=cwd, env=env(), stdout=f, stderr=e, timeout=timeout)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    events = [json.loads(line) for line in open(transcript_dir / "transcript.jsonl") if line.strip().startswith("{")]
    result = next((ev for ev in reversed(events) if ev.get("type") == "result"), {})
    init = next((ev for ev in events if ev.get("type") == "system" and ev.get("subtype") == "init"), {})
    (out_dir / "result.json").write_text(public(json.dumps(result, indent=1), cwd))
    (transcript_dir / "init.json").write_text(json.dumps(init, indent=1))
    (out_dir / "command.json").write_text(public(json.dumps(dict(
        arm=arm, cwd=str(cwd), exit=code, seconds=round(time.time() - t0, 1),
        argv=[c if c != prompt else "<prompt>" for c in cmd], prompt=prompt), indent=1), cwd))
    return result, events


def skills_invoked(events):
    """Names passed to the Skill tool during a session."""
    names = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                names.append(block.get("input", {}).get("skill", "?"))
    return names


def new_path(path):
    """path if it does not exist, else the first free path_v2, path_v3, ... (outputs are never overwritten)."""
    path = Path(path)
    k = 2
    out = path
    while out.exists():
        out = path.with_name(f"{path.stem}_v{k}{path.suffix}")
        k += 1
    return out
