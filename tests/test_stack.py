"""Tests for the stack runner (scripts/stack.py), its registry (scripts/stacks.toml) and its helpers
(scripts/gate_files.py, scripts/handback_extract.py, scripts/gate_union.py, scripts/lint_files.py): task #339, D-103,
brief tasks/briefs/labeling/LS-B9-brief.md; round 2 (ripwire and sentrux active, D-104) in the same report; round 4
(tasks/briefs/labeling/LS-B9-R4-brief.md: R3-F1, R3-F3, R3-F4, R3-F5, the catalog notes, local ids in a hand-back,
the SessionStart catalog) at the end.

The runner's rules run against temporary registries of tiny real programs (sys.executable on small scripts written
into a temporary git tree), never a stub of an instrument. The stacks: `explain` of each is pinned (it runs anywhere,
CI included); premise, gate, review and harvest run for real; the ripwire and sentrux steps run for real with their
binaries pointed at missing paths (they read unmapped, CI included), and gate's graph step runs real ripwire where it
is installed; echo runs where rg is installed. Where an instrument is absent the test skips with the reason (CI has no
graft, GitNexus, code-review-graph, ripwire, sentrux or rg).
Every run passes --log-dir under the test's own tmp_path, so no test writes the repository's .jev/. The exceptions
make the default log dir or its place their subject: the worktree test, and the gate run-step test, whose log dir lies
inside a temporary repository.
Each test's docstring names the mutant of the code under test that turns it into a FAILED test (AF-AP-223).
"""
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

import pytest

ROOT = Path(os.path.realpath(Path(__file__).resolve().parents[1]))
STACK = ROOT / "scripts" / "stack.py"
GATE_FILES = ROOT / "scripts" / "gate_files.py"
HANDBACK = ROOT / "scripts" / "handback_extract.py"
GATE_UNION = ROOT / "scripts" / "gate_union.py"
LINT_FILES = ROOT / "scripts" / "lint_files.py"
PY = sys.executable
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
NEEDS_RG = pytest.mark.skipif(shutil.which("rg") is None,
                              reason="rg (ripgrep) is not installed: the echo stack's code search needs it (CI has none)")
MARK = [PY, "mark.py", "MARKER"]
AGENT = "a0123456789abcdef"
# the wrappers' own missing-binary line ends in this (scripts/ripwire_review.sh, scripts/sentrux_review.sh)
MISSING_TEXT = "missing — run scripts/setup.sh"
MISSING_BINS = {"RIPWIRE_BIN": "/nonexistent-ls-b9/ripwire", "SENTRUX_BIN": "/nonexistent-ls-b9/sentrux"}


def ripwire_binary():
    """The binary scripts/ripwire_review.sh runs, by its own rule (RIPWIRE_BIN when set and nothing else; else
    ~/.local/bin, /root/.local/bin, the PATH), or None when the wrapper would print "missing". os.path.exists, not
    Path.exists: a /root path raises PermissionError from Path.exists for a non-root user (CI)."""
    given = os.environ.get("RIPWIRE_BIN")
    for c in [given] if given else [os.path.expanduser("~/.local/bin/ripwire"), "/root/.local/bin/ripwire",
                                    shutil.which("ripwire")]:
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


NEEDS_RIPWIRE = pytest.mark.skipif(ripwire_binary() is None, reason="ripwire is not installed: gate's graph step needs "
                                   "it (CI has none; the missing case is tested with RIPWIRE_BIN pointed away)")


# ---------- helpers ----------

def git(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env={**os.environ, **GIT_ENV},
                       timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def make_tree(path):
    """A git repository with one commit and the small programs the registries below run."""
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    (path / "a.txt").write_text("a\n")
    (path / "b.txt").write_text("b\n")
    (path / "mark.py").write_text("import sys\nopen(sys.argv[1], 'a').write('x')\nprint('marked', sys.argv[1])\n")
    (path / "argv.py").write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "--no-verify", "-m", "one")
    return Path(os.path.realpath(path))


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    return "{ " + ", ".join("%s = %s" % (k, toml_value(x)) for k, x in v.items()) + " }"


def stack_toml(label, params=None, steps=(), outward=False, rated=False):
    lines = ["[stacks.%s]" % label, 'summary = "a test stack"', 'replaces = "nothing"', "outward = %s" % toml_value(outward)]
    if rated:
        lines.append("rated = true")
    for name, spec in (params or {}).items():
        lines.append("[stacks.%s.params.%s]" % (label, name))
        lines += ["%s = %s" % (k, toml_value(v)) for k, v in spec.items()]
    for step in steps:
        lines.append("[[stacks.%s.steps]]" % label)
        lines += ["%s = %s" % (k, toml_value(v)) for k, v in step.items()]
    return "\n".join(lines) + "\n"


def registry(tmp_path, *stacks, version=1, tools=None):
    text = "version = %s\n[tools]\n" % version
    text += "".join("%s = %s\n" % (json.dumps(k), toml_value(v)) for k, v in (tools or {}).items())
    path = tmp_path / "stacks.toml"
    path.write_text(text + "\n".join(stacks))
    return path


def run(tmp_path, tree, reg, *args, timeout=120, log_dir=None):
    """GIT_CEILING_DIRECTORIES: git's upward search stops at tmp_path, so a tmp_path that lies inside another work
    tree (round 1's gate basetemp was <main tree>/.jev/stacks/<run>/bt, D12) cannot lend its repository to a test."""
    return subprocess.run([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir",
                           str(log_dir or tmp_path / "log"), *map(str, args)], cwd=str(tree), capture_output=True,
                          text=True, timeout=timeout, env={**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)})


def load_stack(name):
    """scripts/stack.py imported under its own module name, for fault injection into the real main()."""
    spec = importlib.util.spec_from_file_location(name, STACK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def records(log_dir):
    path = Path(log_dir) / "runs.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def alive(pid):
    """True while the pid runs (a zombie counts as dead)."""
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (FileNotFoundError, ProcessLookupError):
        return False


def wait_dead(pids, seconds=5.0):
    deadline = time.monotonic() + seconds
    while any(alive(p) for p in pids) and time.monotonic() < deadline:
        time.sleep(0.05)
    return [p for p in pids if alive(p)]


# ---------- no shell, option injection, the deny list, the tree ----------

def test_no_shell_a_text_value_reaches_the_program_as_one_literal_element(tmp_path):
    """Mutant: Popen(" ".join(argv), shell=True) — the shell runs $(touch X) and splits the element."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("show", {"q": {"type": "text", "required": True}},
                                        [{"id": "show", "argv": [PY, "argv.py", "{q}"]}]))
    value = "$(touch X) `touch Y`; touch Z && touch W | cat"
    r = run(tmp_path, tree, reg, "show", "q=" + value)
    assert r.returncode == 0, r.stdout + r.stderr
    step = records(tmp_path / "log")[-1]["steps"][0]
    assert json.loads(Path(step["out"]).read_text()) == [value]
    assert step["argv"][-1] == value
    assert [f for f in "XYZW" if (tree / f).exists()] == []


@pytest.mark.parametrize("token", ["q=-rf", "q=--help", "p=-x", "p=a.txt,-b"])
def test_a_value_that_begins_with_a_dash_is_refused_before_any_step(tmp_path, token):
    """Mutant: check_scalar and check_path without their startswith("-") checks — the marker step runs, exit 0."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"q": {"type": "text"}, "p": {"type": "paths"}},
                                        [{"id": "marker", "argv": MARK},
                                         {"id": "show", "argv": [PY, "argv.py", "{q?:-q}", "{p*}"]}]))
    r = run(tmp_path, tree, reg, "st", token)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "begins with '-' (option injection)" in r.stderr
    assert not (tree / "MARKER").exists() and not (tmp_path / "log").exists()


DENY_CASES = [  # (id, the value, a symlink target the value names or None, the entry the refusal names)
    ("pc-bridge-env", ".pc-bridge.env", None, ".pc-bridge.env"),
    ("dot-env", "secrets.env", None, "*.env"),
    ("nested-env", "sub/prod.env", None, "*.env"),
    ("git-dir", ".git/config", None, ".git/"),
    ("symlink-to-env", "notes.txt", ".pc-bridge.env", ".pc-bridge.env"),
    ("codiv", "codiv-link", "/root/.codiv/key", "/root/.codiv/"),
    ("claude-projects", "proj-link", "/root/.claude/projects/p/s/x.jsonl", "/root/.claude/projects/"),
    ("qwen-config", "qwen-link", "~/.config/qwen-local/key", "~/.config/qwen-*"),
    ("session-export", "sess-link", "/root/.config/session-export/x", "/root/.config/session-export/"),
]


@pytest.mark.parametrize("kind", ["path", "paths"])
@pytest.mark.parametrize("value, target, entry", [c[1:] for c in DENY_CASES], ids=[c[0] for c in DENY_CASES])
def test_the_deny_list_refuses_each_entry_before_any_step_runs(tmp_path, value, target, entry, kind):
    """Mutants, one per entry: the entry dropped from deny_rule() (the in-tree ones then run the marker; the others are
    refused as 'outside the tree', not by the deny list); the deny check made on the lexical path only (the symlink
    cases pass it)."""
    tree = make_tree(tmp_path / "t")
    if target is not None:
        os.symlink(os.path.expanduser(target), tree / value)   # dangling or not: nothing reads the target
    reg = registry(tmp_path, stack_toml("st", {"p": {"type": kind, "required": True}},
                                        [{"id": "marker", "argv": MARK}]))
    r = run(tmp_path, tree, reg, "st", "p=" + (value if kind == "path" else "a.txt," + value))
    assert r.returncode == 2, r.stdout + r.stderr
    assert "is on the deny list (%s)" % entry in r.stderr, r.stderr
    assert not (tree / "MARKER").exists() and not (tmp_path / "log").exists()


@pytest.mark.parametrize("value, link, message", [
    ("../outside.txt", None, "is outside the tree"),
    ("/etc/hostname", None, "is outside the tree"),
    ("out-link", "../outside.txt", "resolves outside the tree"),
    ("sub-link/x.txt", "..", "resolves outside the tree"),
], ids=["dotdot", "absolute", "symlink-file", "symlink-dir"])
def test_a_path_outside_the_tree_is_refused(tmp_path, value, link, message):
    """Mutant: check_path without its resolved-path containment check — the symlink cases run the marker."""
    tree = make_tree(tmp_path / "t")
    (tmp_path / "outside.txt").write_text("out\n")
    (tmp_path / "x.txt").write_text("x\n")
    if link is not None:
        os.symlink(link, tree / value.split("/")[0])
    reg = registry(tmp_path, stack_toml("st", {"p": {"type": "path", "required": True}},
                                        [{"id": "marker", "argv": MARK}]))
    r = run(tmp_path, tree, reg, "st", "p=" + value)
    assert r.returncode == 2, r.stdout + r.stderr
    assert message in r.stderr
    assert not (tree / "MARKER").exists()


def test_a_path_value_inside_the_tree_reaches_the_program_tree_relative(tmp_path):
    """The positive control of the refusals above. Mutant: the realpath substituted (a symlink's name is lost)."""
    tree = make_tree(tmp_path / "t")
    os.symlink("a.txt", tree / "alias.txt")
    reg = registry(tmp_path, stack_toml("st", {"p": {"type": "paths", "required": True}},
                                        [{"id": "show", "argv": [PY, "argv.py", "{p*}"]}]))
    r = run(tmp_path, tree, reg, "st", "p=./a.txt,%s/b.txt,alias.txt,sub/../a.txt" % tree)
    assert r.returncode == 0, r.stdout + r.stderr
    out = records(tmp_path / "log")[-1]["steps"][0]["out"]
    assert json.loads(Path(out).read_text()) == ["a.txt", "b.txt", "alias.txt", "a.txt"]


def test_the_tree_must_be_a_git_toplevel(tmp_path):
    """Mutant: resolve_tree without its toplevel check (a subdirectory is taken for the tree)."""
    tree = make_tree(tmp_path / "t")
    (tree / "sub").mkdir()
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "marker", "argv": MARK}]))
    r = run(tmp_path, tree / "sub", reg, "st")
    assert r.returncode == 2 and "not a toplevel" in r.stderr, r.stderr
    (tmp_path / "plain").mkdir()
    r = run(tmp_path, tmp_path / "plain", reg, "st")
    assert r.returncode == 2 and "not inside a git work tree" in r.stderr, r.stderr
    assert not (tree / "sub" / "MARKER").exists() and not (tmp_path / "plain" / "MARKER").exists()


# ---------- execution: timeouts, unmapped, chains, groups ----------

SPAWN = r'''import os, subprocess, sys, time
# two grandchildren: one ignores SIGTERM (only the SIGKILL 3 s later ends it), one records a SIGTERM and exits (only a
# SIGTERM sent to the whole process group reaches it)
deaf = subprocess.Popen([sys.executable, "-c", "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                         "open('ready1', 'w').close(); time.sleep(120)"])
hears = subprocess.Popen([sys.executable, "-c", "import signal, sys, time\n"
                          "def on_term(*a):\n    open('termed', 'w').close()\n    sys.exit(0)\n"
                          "signal.signal(signal.SIGTERM, on_term)\nopen('ready2', 'w').close()\ntime.sleep(120)"])
deadline = time.time() + 20
while not (os.path.exists("ready1") and os.path.exists("ready2")) and time.time() < deadline:
    time.sleep(0.01)
with open("pids", "w") as fh:
    fh.write("%d %d %d" % (os.getpid(), deaf.pid, hears.pid))
time.sleep(120)
'''


def test_a_step_past_its_timeout_loses_its_whole_process_group(tmp_path):
    """Mutants: SIGTERM to the leader only (not the group) — the listening grandchild never writes `termed`; no SIGKILL
    after the grace — the deaf grandchild lives on; SIGKILL at once (no 3 s grace) — the run ends too soon."""
    tree = make_tree(tmp_path / "t")
    (tree / "spawn.py").write_text(SPAWN)
    reg = registry(tmp_path, stack_toml("slow", None, [{"id": "spawn", "argv": [PY, "spawn.py"], "timeout": 2}]))
    t0 = time.monotonic()
    r = run(tmp_path, tree, reg, "slow", timeout=90)
    took = time.monotonic() - t0
    pids = [int(x) for x in (tree / "pids").read_text().split()]
    try:
        assert r.returncode == 1, r.stdout + r.stderr
        assert "## spawn · TIMEOUT after 2 s" in r.stdout
        assert records(tmp_path / "log")[-1]["steps"][0]["status"] == "timeout"
        assert len(pids) == 3 and wait_dead(pids) == []
        assert (tree / "termed").exists()    # the group's SIGTERM reached the grandchild that listens for it
        assert took >= 4.5, took          # 2 s to the timeout, then SIGKILL 3 s after SIGTERM
    finally:
        for p in pids:
            if alive(p):
                os.kill(p, signal.SIGKILL)


@pytest.mark.parametrize("required, exit_code", [(True, 1), (False, 0)], ids=["required", "optional"])
@pytest.mark.parametrize("argv, tool", [
    (["no-such-program-ls-b9", "x"], "no-such-program-ls-b9"),
    (["ghost-tool", "x"], "ghost-tool"),
    ([PY, "scripts/no_such_script.py"], "scripts/no_such_script.py"),
    (["./no-such-exe"], "./no-such-exe"),
], ids=["program", "tools-entry", "interpreter-script", "relative-path"])
def test_a_missing_instrument_prints_unmapped_and_fails_the_run_only_when_required(tmp_path, argv, tool, required,
                                                                                     exit_code):
    """Mutants: an unmapped step counted as ok (exit 0 when it is required); the interpreter's script check removed
    (python runs and exits 2: FAILED, never unmapped)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "fine", "argv": MARK},
                                                    {"id": "gone", "argv": argv, "required": required}]),
                   tools={"ghost-tool": ["/nonexistent/ghost-tool", "~/no-such-dir-ls-b9/ghost", "ghost-tool-ls-b9"]})
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == exit_code, r.stdout + r.stderr
    assert "## gone · unmapped — %s unavailable" % tool in r.stdout
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert steps["gone"]["status"] == "unmapped" and steps["gone"]["rc"] is None
    assert steps["fine"]["status"] == "ok" and (tree / "MARKER").exists()


WRAPPER = ("import sys\nstream = sys.stderr if sys.argv[1] == 'err' else sys.stdout\n"
           "stream.buffer.write(%s.encode('utf-8'))\n" % ascii("tool_review: /no/such/bin %s (pinned install)\n"
                                                              % MISSING_TEXT))


@pytest.mark.parametrize("stream", ["out", "err"])
@pytest.mark.parametrize("required, exit_code", [(True, 1), (False, 0)], ids=["required", "optional"])
def test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped(tmp_path, stream, required, exit_code):
    """A wrapper that prints "missing" and exits 0 when its binary is absent (task #345) reads unmapped, never ok.
    Mutants: unmapped_if ignored (it reads ok; a required one exits 0); stdout searched alone (the stderr case reads
    ok); the tool name dropped (the status names the interpreter); an unmapped body hidden (the wrapper's line lost)."""
    tree = make_tree(tmp_path / "t")
    (tree / "wrapper.py").write_text(WRAPPER)
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "wrap", "argv": [PY, "wrapper.py", stream], "required": required, "unmapped_if": MISSING_TEXT,
         "tool": "mytool"},
        {"id": "plain", "argv": [PY, "wrapper.py", stream]},                     # the same output, no unmapped_if
        {"id": "other", "argv": [PY, "-c", "print('all fine')"], "unmapped_if": MISSING_TEXT}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == exit_code, r.stdout + r.stderr
    assert "## wrap · unmapped — mytool unavailable%s\n" % ("" if required else " (not required)") in r.stdout
    body = r.stdout.split("## wrap · ")[1].split("\n## ")[0]
    assert "tool_review: /no/such/bin %s (pinned install)" % MISSING_TEXT in body
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert (steps["wrap"]["status"], steps["wrap"]["rc"]) == ("unmapped", 0)
    assert steps["plain"]["status"] == "ok" and steps["other"]["status"] == "ok"


def test_a_join_placeholder_passes_a_list_as_one_comma_joined_element(tmp_path):
    """{name,}: ripwire's documented multi-file form is one --test-gate=F1,F2 argument (its wrapper passes one flag per
    argument, and ripwire keeps the last). Mutants: joined with spaces; each element its own argument."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"p": {"type": "paths", "required": True}},
                                        [{"id": "show", "argv": [PY, "argv.py", "--files={p,}", "{p,}"]}]))
    for value, joined in (("a.txt,./b.txt", "a.txt,b.txt"), ("a.txt", "a.txt")):
        r = run(tmp_path, tree, reg, "st", "p=" + value)
        assert r.returncode == 0, r.stdout + r.stderr
        out = records(tmp_path / "log")[-1]["steps"][0]["out"]
        assert json.loads(Path(out).read_text()) == ["--files=" + joined, joined]


@pytest.mark.parametrize("source, why", [
    ([PY, "-c", "print('a.txt'); raise SystemExit(3)"], "its input step src failed (rc 3)"),
    ([PY, "-c", "print('')"], "its input step src printed nothing"),
    (["no-such-program-ls-b9"], "its input step src was unmapped"),
    ([PY, "-c", "print('../../etc/passwd')"], "a line of src refused: '../../etc/passwd' is outside the tree"),
    ([PY, "-c", "print('a' + chr(0) + '.txt')"], "holds a NUL or a newline"),   # argv cannot carry a NUL; stdout can
    ([PY, "-c", "import sys; print(sys.argv[1] + '/../x.txt')", "{run}"], "/../x.txt' is outside the tree"),
    ([PY, "-c", "import os, sys; os.symlink('/etc/hostname', sys.argv[1] + '/link'); print(sys.argv[1] + '/link')",
      "{run}"], "/link' is outside the tree"),
], ids=["failed", "silent", "unmapped", "line-refused", "line-nul", "run-dir-parent", "run-dir-symlink"])
def test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing(tmp_path, source, why):
    """Mutants: chain_input() ignores the source's status (the failed source's line reaches the consumer, which runs);
    an empty input runs the consumer with no line; a source line is not validated as a path; a line in the run's own
    dir accepted by its lexical path only (the symlink out of the run dir passes)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "src", "argv": source, "group": 1, "required": False},
        {"id": "use", "argv": [PY, "mark.py", "MARKER", "{@src*}"], "group": 2}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "## use · SKIPPED — " in r.stdout and why in r.stdout, r.stdout
    assert not (tree / "MARKER").exists()
    assert records(tmp_path / "log")[-1]["steps"][1]["status"] == "skipped"


def test_a_chained_step_receives_its_sources_non_empty_lines_as_paths(tmp_path):
    """The positive control of the skips. Mutant: stdout's blank lines kept (the consumer gets '' elements)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "src", "argv": [PY, "-c", "print('a.txt'); print(); print('  '); print('./b.txt')"], "group": 1},
        {"id": "use", "argv": [PY, "argv.py", "{@src*}", "end"], "group": 2}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stdout + r.stderr
    out = records(tmp_path / "log")[-1]["steps"][1]["out"]
    assert json.loads(Path(out).read_text()) == ["a.txt", "b.txt", "end"]


def test_a_chained_line_may_name_a_file_in_this_runs_own_dir(tmp_path):
    """The run dir lies outside the tree here (--log-dir), as it does for a worktree; harvest chains its extractor's
    file this way. Mutant: check_path without its run_dir branch (the line is refused, the consumer skipped)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "src", "argv": [PY, "-c", "import sys; p = sys.argv[1] + '/f.txt'; open(p, 'w').close(); print(p)",
                               "{run}"], "group": 1},
        {"id": "use", "argv": [PY, "argv.py", "{@src*}"], "group": 2}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stdout + r.stderr
    rec = records(tmp_path / "log")[-1]
    assert json.loads(Path(rec["steps"][1]["out"]).read_text()) == [str(tmp_path / "log" / rec["run"] / "f.txt")]


STAMP = ("import sys, time\nstart = time.time()\ntime.sleep(float(sys.argv[2]))\n"
         "open(sys.argv[1], 'w').write('%r %r' % (start, time.time()))\n")


def test_one_groups_steps_run_in_parallel_and_the_groups_in_order(tmp_path):
    """Mutants: each thread joined as soon as it starts (the two 1-second steps take 2 s together); the groups run in
    descending order (the group-2 step starts before group 1 ends)."""
    tree = make_tree(tmp_path / "t")
    (tree / "stamp.py").write_text(STAMP)
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "late", "argv": [PY, "stamp.py", "C", "0"], "group": 2},
        {"id": "one", "argv": [PY, "stamp.py", "A", "1"], "group": 1},
        {"id": "two", "argv": [PY, "stamp.py", "B", "1"], "group": 1}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stdout + r.stderr
    (sa, ea), (sb, eb), (sc, ec) = [tuple(float(x) for x in (tree / n).read_text().split()) for n in "ABC"]
    assert max(ea, eb) - min(sa, sb) < 1.8, (sa, ea, sb, eb)
    assert sc >= max(ea, eb), (sc, ea, eb)


# ---------- when, repeat, foreach ----------

def test_when_selects_a_step_by_its_parameters(tmp_path):
    """Mutant: unselected() ignores `when` (the mode=run step runs in plan mode and writes R)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"mode": {"type": "choice", "choices": ["plan", "run"], "default": "plan"},
                                              "opt": {"type": "text"}}, [
        {"id": "always", "argv": [PY, "mark.py", "A"]},
        {"id": "only_run", "argv": [PY, "mark.py", "R"], "when": {"mode": "run"}},
        {"id": "only_set", "argv": [PY, "mark.py", "S", "{opt}"], "when": {"opt": "*"}},
        {"id": "only_unset", "argv": [PY, "mark.py", "U"], "when": {"opt": ""}}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stdout + r.stderr
    assert sorted(p.name for p in tree.iterdir() if len(p.name) == 1) == ["A", "U"]
    assert "not selected: only_run (when mode=run), only_set (when opt=*)" in r.stdout
    assert [s["id"] for s in records(tmp_path / "log")[-1]["steps"]] == ["always", "only_unset"]
    for n in "AU":
        (tree / n).unlink()
    r = run(tmp_path, tree, reg, "st", "mode=run", "opt=x")
    assert r.returncode == 0, r.stdout + r.stderr
    assert sorted(p.name for p in tree.iterdir() if len(p.name) == 1) == ["A", "R", "S"]


def test_repeat_runs_a_step_n_times_with_numbered_sections(tmp_path):
    """Mutant: invocations() ignores repeat (one call: the counter holds 1 and there is no [2/3] section)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"runs": {"type": "choice", "choices": ["1", "2", "3"], "default": "2"},
                                              "n": {"type": "int"}}, [
        {"id": "count", "argv": [PY, "mark.py", "COUNT"], "repeat": "{runs}"},
        {"id": "var", "argv": [PY, "mark.py", "VAR"], "repeat": "{n}", "when": {"n": "*"}}]))
    r = run(tmp_path, tree, reg, "st", "runs=3")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tree / "COUNT").read_text() == "xxx"
    assert all("## count[%d/3] · ok" % i in r.stdout for i in (1, 2, 3))
    steps = records(tmp_path / "log")[-1]["steps"]
    assert [(s["id"], s["n"]) for s in steps] == [("count", 1), ("count", 2), ("count", 3)]
    assert [Path(s["out"]).name for s in steps] == ["count.1.out", "count.2.out", "count.3.out"]
    r = run(tmp_path, tree, reg, "st", "n=0")           # a repeat count is refused before any step runs
    assert r.returncode == 2 and "a repeat count is 1 to 20" in r.stderr, r.stderr
    assert (tree / "COUNT").read_text() == "xxx"


def test_foreach_runs_a_step_once_per_element_with_each(tmp_path):
    """Mutant: {each} bound to the first element for every call (both calls print a.txt)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"files": {"type": "paths", "required": True}}, [
        {"id": "show", "argv": [PY, "argv.py", "--", "{each}"], "foreach": "files"}]))
    r = run(tmp_path, tree, reg, "st", "files=a.txt,b.txt")
    assert r.returncode == 0, r.stdout + r.stderr
    steps = records(tmp_path / "log")[-1]["steps"]
    assert [json.loads(Path(s["out"]).read_text()) for s in steps] == [["--", "a.txt"], ["--", "b.txt"]]
    assert [s["n"] for s in steps] == [1, 2] and "## show[2/2] · ok" in r.stdout


# ---------- the print ----------

BIG = "for i in range(30):\n    print(str(i).rjust(4, '0') + 'x' * 996)\n"


def test_the_whole_print_is_capped_at_9000_characters_cut_from_the_largest_section(tmp_path):
    """Mutant: assemble() returns the whole print (over 30,000 characters)."""
    tree = make_tree(tmp_path / "t")
    (tree / "big.py").write_text(BIG)
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "big", "argv": [PY, "big.py"], "cap_lines": 100},
        {"id": "small", "argv": [PY, "-c", "print('small-ok')"]}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stderr
    assert len(r.stdout) <= 9000, len(r.stdout)
    assert "print capped at 9,000 characters: shortened big\n" in r.stdout
    assert "small-ok" in r.stdout
    big = records(tmp_path / "log")[-1]["steps"][0]
    assert Path(big["out"]).read_text().count("\n") == 30 and big["bytes"] == 30 * 1001
    assert "characters cut (the 9,000-character print cap); full output: %s" % big["out"] in r.stdout
    assert "0000xxx" in r.stdout and "0029xxx" in r.stdout      # the head and the tail are kept


def test_a_section_over_cap_lines_keeps_its_first_and_last_lines(tmp_path):
    """Mutant: cap_lines() keeps the head only (the last line, often the verdict, is lost)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "many", "argv": [PY, "-c", "for i in range(1, 101): print('line', i)"], "cap_lines": 10}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stderr
    out = records(tmp_path / "log")[-1]["steps"][0]["out"]
    body = r.stdout.split("$ ", 1)[1].split("\n", 1)[1].rstrip("\n").split("\n")
    assert body == ["line %d" % i for i in range(1, 6)] + [
        "… 90 lines cut (cap_lines 10); full output: %s" % out] + ["line %d" % i for i in range(96, 101)]


def test_the_print_cap_holds_at_exactly_9000_characters(tmp_path):
    """V9: a print of exactly 9,000 characters goes out whole; one of 9,001 is cut to 9,000 or fewer. The body is the
    only part whose length moves (k keeps five digits). Mutant: the cap checked at a higher bound (the 9,001-character
    print goes out whole)."""
    tree = make_tree(tmp_path / "t")
    (tree / "size.py").write_text("import sys\nprint('x' * int(sys.argv[1]))\n")
    reg = registry(tmp_path, stack_toml("st", {"k": {"type": "int", "required": True}},
                                        [{"id": "size", "argv": [PY, "size.py", "{k}"], "cap_lines": 5}]))

    def printed(k):
        r = run(tmp_path, tree, reg, "st", "k=%05d" % k)
        assert r.returncode == 0, r.stderr
        return r.stdout

    rest = len(printed(100)) - 100
    whole = printed(9000 - rest)
    assert len(whole) == 9000 and "print capped" not in whole
    cut = printed(9001 - rest)
    assert "print capped at 9,000 characters: shortened size\n" in cut and len(cut) <= 9000


MIB = 1024 * 1024
CAP_BIG = "import sys, time\nsys.stdout.write('y' * (3 * %d))\nsys.stdout.flush()\ntime.sleep(60)\n" % MIB
CAP_LINE = "./" * 100 + "a.txt\n"          # 206 bytes, a path inside the tree
# stdout + stderr = the cap - 6 bytes: never over the cap while it runs, so never killed; saved with the 15-byte
# `--- stderr ---` line between them it is 9 bytes over, so the save truncates an ok step
CAP_EDGE = ("import sys\nn = 600000 // %d\nsys.stdout.write(%r * n)\nsys.stdout.flush()\n"
            "sys.stderr.write('e' * (%d - 6 - %d * n))\n" % (len(CAP_LINE), CAP_LINE, MIB, len(CAP_LINE)))
CAP_MARKER = "\n… saved output truncated at 1 MB (save_cap_mb 1); the rest was not saved\n".encode()


def test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain(tmp_path):
    """save_cap_mb (item 6). Mutants: no size check while a step runs (the 3 MB writer lives to its 20 s timeout); the
    saved output not truncated (3 MB saved, no marker); `truncated` left out of the record; a truncated source's lines
    fed to its chained consumer (it runs and writes MARKER)."""
    tree = make_tree(tmp_path / "t")
    (tree / "big.py").write_text(CAP_BIG)
    (tree / "edge.py").write_text(CAP_EDGE)
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "big", "argv": [PY, "big.py"], "save_cap_mb": 1, "timeout": 20, "group": 1},
        {"id": "edge", "argv": [PY, "edge.py"], "save_cap_mb": 1, "group": 1},
        {"id": "use", "argv": [PY, "mark.py", "MARKER", "{@edge*}"], "group": 2, "required": False}]))
    t0 = time.monotonic()
    r = run(tmp_path, tree, reg, "st")
    assert time.monotonic() - t0 < 15, "the capped step ran on toward its 20 s timeout"
    assert r.returncode == 1, r.stdout + r.stderr
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    for sid in ("big", "edge"):
        data = Path(steps[sid]["out"]).read_bytes()
        assert data.endswith(CAP_MARKER) and len(data) == MIB + len(CAP_MARKER), (sid, len(data))
        assert steps[sid]["truncated"] is True and steps[sid]["bytes"] == len(data)
    assert (steps["big"]["status"], steps["big"]["rc"]) == ("failed", -signal.SIGKILL)     # F-7: no SIGTERM first
    assert "## big · FAILED · rc %d · " % -signal.SIGKILL in r.stdout
    assert " — killed: its saved output passed the 1 MB cap\n" in r.stdout
    assert steps["edge"]["status"] == "ok" and steps["use"]["status"] == "skipped" and "truncated" not in steps["use"]
    assert "## use · SKIPPED — its input step edge was truncated at its save cap" in r.stdout
    assert not (tree / "MARKER").exists()


DEAF_WRITER = ('import os, signal, time\n'
               'signal.signal(signal.SIGTERM, lambda *a: open("got_term", "w").close())   # deaf: notes it, writes on\n'
               'chunk = b"y" * 262144\n'
               'for i in range(160):                 # at most 40 MB, about 25 MB a second\n'
               '    os.write(1, chunk)\n'
               '    open("written.tmp", "w").write(str((i + 1) * len(chunk)))\n'
               '    os.replace("written.tmp", "written")\n'
               '    time.sleep(0.01)\n')


def test_a_step_past_its_save_cap_gets_sigkill_at_once(tmp_path):
    """F-7: a writer that ignores SIGTERM, killed at its cap with no grace. Mutant: round 2's kill at the cap (SIGTERM,
    then SIGKILL 3 s later): the writer gets the SIGTERM and writes on through the grace (measured by the verifier:
    120 MB past a 1 MB cap)."""
    tree = make_tree(tmp_path / "t")
    (tree / "deaf.py").write_text(DEAF_WRITER)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "flood", "argv": [PY, "deaf.py"], "save_cap_mb": 1,
                                                      "timeout": 60}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 1, r.stdout + r.stderr
    [s] = records(tmp_path / "log")[-1]["steps"]
    assert (s["status"], s["rc"], s["truncated"]) == ("failed", -signal.SIGKILL, True)
    assert not (tree / "got_term").exists()                   # no SIGTERM was sent: no grace to write through
    assert int((tree / "written").read_text()) < 16 * MIB     # killed near its 1 MB cap, not at its 40 MB end


LEAVER = ('import os, subprocess, sys\n'
          'child = subprocess.Popen([sys.executable, "-c", "import os, time\\nwhile True:\\n'
          '    os.write(1, b\\"z\\" * 4096)\\n    time.sleep(0.01)\\n"])\n'
          'open("child.tmp", "w").write(str(child.pid))\n'
          'os.replace("child.tmp", "child")\n')


def test_a_step_whose_leader_exits_loses_what_it_left_running(tmp_path):
    """F-8: the leader exits at once and leaves a writing child in the step's process group; the child would write on
    to the step's unlinked stdout after the stack exits, past every cap and timeout. Mutant: no kill after the leader
    exits (the child lives on)."""
    tree = make_tree(tmp_path / "t")
    (tree / "leaver.py").write_text(LEAVER)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "leave", "argv": [PY, "leaver.py"]}]))
    r = run(tmp_path, tree, reg, "st")
    pid = int((tree / "child").read_text())
    try:
        assert r.returncode == 0, r.stdout + r.stderr
        assert wait_dead([pid]) == []
        [s] = records(tmp_path / "log")[-1]["steps"]
        assert (s["status"], s["strays_killed"]) == ("ok", True)
        assert "## leave · ok · rc 0 · " in r.stdout and " · killed what it left running\n" in r.stdout
    finally:
        if alive(pid):
            os.kill(pid, signal.SIGKILL)


def test_foreach_over_an_earlier_steps_lines_makes_one_call_per_line(tmp_path):
    """foreach = "@step" (the gate's per-file runs). Mutants: {each} bound to the first line for every call; the lines
    read without the chained-path checks (the refused line reaches a call)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"extra": {"type": "text", "required": True}}, [
        {"id": "src", "argv": [PY, "-c", "import sys; print('a.txt'); print('./b.txt'); print(sys.argv[1])",
                               "{extra}"], "group": 1},
        {"id": "per", "argv": [PY, "argv.py", "--file={each}", "{tree}/{each}"], "foreach": "@src", "group": 2}]))
    r = run(tmp_path, tree, reg, "st", "extra=a.txt")
    assert r.returncode == 0, r.stdout + r.stderr
    steps = [s for s in records(tmp_path / "log")[-1]["steps"] if s["id"] == "per"]
    assert [json.loads(Path(s["out"]).read_text()) for s in steps] == [
        ["--file=%s" % f, "%s/%s" % (tree, f)] for f in ("a.txt", "b.txt", "a.txt")]
    assert [s["n"] for s in steps] == [1, 2, 3] and "## per[3/3] · ok" in r.stdout
    r = run(tmp_path, tree, reg, "st", "extra=../outside.txt")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "## per · SKIPPED — a line of src refused: '../outside.txt' is outside the tree" in r.stdout


@pytest.mark.parametrize("empty_ok", [True, False], ids=["empty-ok", "not-empty-ok"])
def test_an_empty_chained_input_is_nothing_to_do_only_with_empty_ok(tmp_path, empty_ok):
    """Mutants: empty_ok ignored (an empty input fails the run); an empty input read as nothing to do without it."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "src", "argv": [PY, "-c", "pass"], "group": 1},
        {"id": "use", "argv": [PY, "mark.py", "MARKER", "{@src*}"], "group": 2, "empty_ok": empty_ok},
        {"id": "per", "argv": [PY, "mark.py", "{each}"], "foreach": "@src", "group": 2, "empty_ok": empty_ok}]))
    r = run(tmp_path, tree, reg, "st")
    ids = [s["id"] for s in records(tmp_path / "log")[-1]["steps"]]
    if empty_ok:
        assert r.returncode == 0, r.stdout + r.stderr
        assert ("not selected: use (its input step src printed nothing), per (its input step src printed nothing)"
                in header_of(r.stdout))
        assert ids == ["src"]
    else:
        assert r.returncode == 1, r.stdout + r.stderr
        assert "## use · SKIPPED — its input step src printed nothing" in r.stdout
        assert "## per · SKIPPED — its input step src printed nothing" in r.stdout
        assert ids == ["src", "use", "per"]
    assert not (tree / "MARKER").exists()


def test_needs_runs_a_step_only_after_its_prerequisite_ended_ok(tmp_path):
    """Mutants: needs ignored (the step runs after its prerequisite failed); needs checked before an empty input (a
    step with nothing to do reads as one more failure)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"ok": {"type": "choice", "choices": ["yes", "no"], "default": "yes"}}, [
        {"id": "check", "argv": [PY, "-c", "import sys; sys.exit(0 if sys.argv[1] == 'yes' else 1)", "{ok}"],
         "group": 1},
        {"id": "src", "argv": [PY, "-c", "print('a.txt')"], "group": 1},
        {"id": "empty", "argv": [PY, "-c", "pass"], "group": 1},
        {"id": "after", "argv": [PY, "mark.py", "AFTER", "{@src*}"], "group": 2, "needs": ["check"]},
        {"id": "idle", "argv": [PY, "mark.py", "IDLE", "{@empty*}"], "group": 2, "needs": ["check"],
         "empty_ok": True}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0 and (tree / "AFTER").read_text() == "x", r.stdout + r.stderr
    r = run(tmp_path, tree, reg, "st", "ok=no")
    assert r.returncode == 1, r.stdout + r.stderr
    header = header_of(r.stdout)
    assert header[0].endswith(" · exit 1 — required, not ok: after, check")
    assert "not selected: idle (its input step empty printed nothing)" in header
    assert "## after · SKIPPED — its prerequisite step check failed (rc 1)" in r.stdout
    assert (tree / "AFTER").read_text() == "x" and not (tree / "IDLE").exists()


def test_a_headline_steps_first_line_is_in_the_header_the_print_cap_never_cuts(tmp_path):
    """F-3's mechanism. Mutants: headline ignored (the line sits only in a section the cap cuts); its last line taken."""
    tree = make_tree(tmp_path / "t")
    (tree / "big.py").write_text(BIG)
    reg = registry(tmp_path, stack_toml("st", None, [
        {"id": "counts", "argv": [PY, "-c", "print('COUNTS a=1 b=2'); print('x' * 30000); print('LAST')"],
         "headline": True, "cap_lines": 5},
        {"id": "big", "argv": [PY, "big.py"], "cap_lines": 100}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stderr
    assert len(r.stdout) <= 9000 and "print capped at 9,000 characters: shortened " in r.stdout
    assert "counts · COUNTS a=1 b=2" in header_of(r.stdout)


# ---------- records, ratings, refusals ----------

def test_the_run_record_holds_every_field_and_each_output_is_saved_whole(tmp_path):
    """Mutant: the record's sha256 and bytes taken over stdout alone (the saved file holds the stderr block too)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"q": {"type": "text", "required": True}}, [
        {"id": "both", "argv": [PY, "-c", "import sys; print('out-line'); print('err-line', file=sys.stderr)"]}]))
    r = run(tmp_path, tree, reg, "st", "q=x y")
    assert r.returncode == 0, r.stderr
    [rec] = records(tmp_path / "log")
    assert set(rec) == {"v", "run", "ts", "label", "params", "tree", "head", "rc", "steps"}
    assert rec["v"] == 1 and rec["label"] == "st" and rec["rc"] == 0 and rec["params"] == {"q": "x y"}
    assert re.fullmatch(r"s-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}", rec["run"])
    assert re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", rec["ts"])
    assert rec["tree"] == str(tree) and rec["head"] == git(tree, "rev-parse", "HEAD")
    [step] = rec["steps"]
    assert set(step) == {"id", "argv", "rc", "status", "secs", "bytes", "sha256", "out"}
    data = Path(step["out"]).read_bytes()
    assert data == b"out-line\n--- stderr ---\nerr-line\n"
    assert step["bytes"] == len(data) and step["sha256"] == hashlib.sha256(data).hexdigest()
    assert Path(step["out"]).parent == tmp_path / "log" / rec["run"]
    assert step["status"] == "ok" and step["rc"] == 0 and step["argv"][0] == PY
    # no step names {tmp}: no dir is made (mutant: {tmp} made for every run, and its header line printed)
    assert [line for line in r.stdout.splitlines() if line.startswith("tmp ")] == []


def test_ratings_ride_on_a_run_and_on_rate_and_must_name_a_recorded_run(tmp_path):
    """Mutant: check_ratings() accepts any run id (the rating of an unknown run is appended)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "hello", "argv": MARK}], rated=True))
    assert run(tmp_path, tree, reg, "st").returncode == 0
    first = records(tmp_path / "log")[0]["run"]
    r = run(tmp_path, tree, reg, "st", "--rate", first + "=2/3")
    assert r.returncode == 0, r.stderr
    r = run(tmp_path, tree, reg, "rate", first + ".hello=1/0")
    assert r.returncode == 0 and r.stdout.startswith("rated: "), r.stderr
    lines = records(tmp_path / "log")
    assert [("rating" in x, "run" in x) for x in lines] == [(False, True), (True, False), (False, True), (True, False)]
    assert {k: v for k, v in lines[1].items() if k != "ts"} == {"v": 1, "rating": first, "rel": 2, "use": 3}
    assert {k: v for k, v in lines[3].items() if k != "ts"} == {"v": 1, "rating": first + ".hello", "rel": 1, "use": 0}
    assert set(lines[3]) == {"v", "rating", "rel", "use", "ts"}
    for bad in ("s-20000101T000000Z-000000=1/1", first + ".nostep=1/1", first + "=4/0", first + "=1", "x=1/1"):
        r = run(tmp_path, tree, reg, "rate", bad)
        assert r.returncode == 2, (bad, r.stderr)
        r = run(tmp_path, tree, reg, "st", "--rate", bad)
        assert r.returncode == 2, (bad, r.stderr)
    assert len(records(tmp_path / "log")) == 4


def test_the_record_waits_for_the_log_lock(tmp_path):
    """V1: every runs.jsonl line is one write under flock of <log dir>/.lock. The test holds the lock: the run's step
    ends, and its record waits until the lock is released. Mutant: flock removed (the record lands while the lock is
    held)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "hello", "argv": MARK}]))
    log = tmp_path / "log"
    log.mkdir()
    fd = os.open(log / ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    p = None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        p = subprocess.Popen([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir", str(log), "st"],
                             cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 30
        while not (tree / "MARKER").exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        time.sleep(1.5)                                       # the step is done; only the record is left to write
        assert (tree / "MARKER").exists() and p.poll() is None and records(log) == []
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        if p is not None:
            out, err = p.communicate(timeout=30)
    assert p.returncode == 0, out + err
    assert [x["label"] for x in records(log)] == ["st"]


def test_only_a_rated_stack_takes_ratings(tmp_path):
    """D19: ratings are for the content stacks (rated = true). Mutant: check_ratings() without the rated check (the
    rating of an unrated stack's run is appended; the refused --rate run goes ahead)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("plain", None, [{"id": "hello", "argv": MARK}]),
                   stack_toml("good", None, [{"id": "hello", "argv": [PY, "mark.py", "GOOD"]}], rated=True))
    assert run(tmp_path, tree, reg, "plain").returncode == 0
    assert run(tmp_path, tree, reg, "good").returncode == 0
    plain_run, good_run = [x["run"] for x in records(tmp_path / "log")]
    for args in (["rate", plain_run + "=1/1"], ["rate", plain_run + ".hello=1/1"],
                 ["good", "--rate", plain_run + "=1/1"]):
        r = run(tmp_path, tree, reg, *args)
        assert r.returncode == 2, (args, r.stdout, r.stderr)
        assert ("rating: run %s is a plain run, and only a rated stack takes ratings (good)" % plain_run) in r.stderr
    assert (tree / "GOOD").read_text() == "x" and len(records(tmp_path / "log")) == 2
    r = run(tmp_path, tree, reg, "plain", "--rate", good_run + "=2/1")     # the rated run's rating rides on any run
    assert r.returncode == 0, r.stderr
    assert [x.get("rating") for x in records(tmp_path / "log")] == [None, None, good_run, None]


@pytest.mark.parametrize("tokens, message", [
    (["q=a", "zz=1"], "unknown key 'zz' for stack st"),
    ([], "missing required key 'q' for stack st"),
    (["q=a", "q=b"], "repeated key 'q'"),
    (["q"], "'q' is not a key=value token"),
    (["q=a", "w=x"], "w is derived from q, never set"),
], ids=["unknown", "missing", "repeated", "no-equals", "derived"])
def test_a_bad_key_is_refused_with_exit_2_naming_the_known_keys(tmp_path, tokens, message):
    """Mutant: parse_tokens() lets a repeated key overwrite the first (exit 0, the marker runs)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"q": {"type": "text", "required": True}, "opt": {"type": "word"},
                                              "w": {"type": "words", "split_from": "q"}},
                                        [{"id": "marker", "argv": MARK}]))
    r = run(tmp_path, tree, reg, "st", *tokens)
    assert r.returncode == 2, r.stdout + r.stderr
    assert message in r.stderr and "known keys: q, opt" in r.stderr, r.stderr
    assert not (tree / "MARKER").exists() and not (tmp_path / "log").exists()


GOOD_STACK = stack_toml("st", None, [{"id": "hello", "argv": ["true"]}])
NOTES_BAD = "notes: a list of notes of 1 to 300 characters, each one line with no control character"


@pytest.mark.parametrize("text, message", [
    ("version = 2\n" + GOOD_STACK, "version: must be 1"),
    ('version = "1"\n' + GOOD_STACK, "version: must be 1"),
    ("version = 1\n" + GOOD_STACK.replace("outward = false", "outward = true"), "outward = true"),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", ""), "outward: must be declared false"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["echo", "{nope}"]}]), "{nope} is neither"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["{x}"]}]), "argv[0], the program"),
    ("version = 1\n" + stack_toml("st", {"p": {"type": "paths"}}, [{"id": "a", "argv": ["echo", "x{p*}"]}]),
     "the whole argv element"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["echo", "{@b*}"], "group": 1},
                                             {"id": "b", "argv": ["true"], "group": 2}]), "an earlier group"),
    ("version = 1\n" + stack_toml("st", {"t": {"type": "text"}}, [{"id": "a", "argv": ["echo", "{t}"]}]),
     "optional with no default"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"]}, {"id": "a", "argv": ["true"]}]),
     "the id repeats"),
    ("version = 1\n" + stack_toml("st", {"p": {"type": "path", "default": "-x"}}, [{"id": "a", "argv": ["true"]}]),
     "option injection"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "timeout": 0}]), "timeout: must be"),
    ("version = 1\n" + stack_toml("st", {"q": {"type": "text", "required": True}},
                                  [{"id": "a", "argv": ["echo", "{q,}"]}]), "{q,} must name a list parameter"),
    ("version = 1\n" + stack_toml("st", {"p": {"type": "paths"}}, [{"id": "a", "argv": ["echo", "{p,}"]}]),
     "{p,} is optional with no default"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "tool": "x"}]), "(it needs unmapped_if)"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "unmapped_if": "two\nlines"}]),
     "unmapped_if: a literal output text of one line"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "save_cap_mb": 0}]),
     "save_cap_mb: must be an integer from 1 to 1024"),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nrated = "yes"\n'),
     "rated: must be true or false"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "timeout": 3601}]),
     "timeout: must be an integer from 1 to 3600"),
    ("version = 1\n" + stack_toml("Bad", None, [{"id": "a", "argv": ["true"]}]), "a label matches ^[a-z][a-z0-9-]{1,23}$"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "needs": ["b"]},
                                             {"id": "b", "argv": ["true"], "group": 2}]),
     "needs b must name a step of an earlier group"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["echo", "{each}"], "foreach": "@b"},
                                             {"id": "b", "argv": ["true"], "group": 2}]),
     'foreach = "@b" must name a step of an earlier group'),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "empty_ok": True}]),
     "only a step with a chained input"),
    ("version = 1\n" + stack_toml("st", None, [{"id": "a", "argv": ["true"], "needs": "b"}]),
     "needs: a list of distinct step ids"),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nnotes = "one"\n'), NOTES_BAD),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nnotes = ["a\\rb"]\n'), NOTES_BAD),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nnotes = [""]\n'), NOTES_BAD),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nnotes = ["%s"]\n' % ("n" * 301)),
     NOTES_BAD),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", 'outward = false\nbody = "nope"\n'),
     "stacks.st.body: must name a parameter of this stack that a request sets (found 'nope'; those parameters: none)"),
    ("version = 1\n" + stack_toml("st", {"q": {"type": "text", "required": True},
                                         "w": {"type": "words", "split_from": "q"}},
                                  [{"id": "a", "argv": ["echo", "{q}"]}]).replace(
        "outward = false\n", 'outward = false\nbody = "w"\n'),
     "stacks.st.body: must name a parameter of this stack that a request sets (found 'w'; those parameters: q)"),
    ("version = 1\n" + GOOD_STACK.replace("outward = false\n", "outward = false\nbody = 1\n"),
     "stacks.st.body: must name a parameter of this stack that a request sets (found 1; those parameters: none)"),
], ids=["version-2", "version-string", "outward-true", "outward-missing", "unknown-placeholder", "program-placeholder",
        "splice-in-element", "chain-to-later-group", "optional-scalar-unguarded", "repeated-id", "bad-default",
        "timeout-0", "join-of-a-scalar", "join-unguarded", "tool-alone", "unmapped-if-two-lines", "save-cap-0",
        "rated-string", "timeout-3601", "label-uppercase", "needs-later-step", "foreach-later-step",
        "empty-ok-unchained", "needs-not-a-list", "notes-string", "note-cr", "note-empty", "note-301",
        "body-undeclared", "body-derived", "body-not-a-string"])
def test_a_bad_registry_exits_3_before_anything_runs(tmp_path, text, message):
    """Mutants: the version check removed; the outward check removed; a join of a scalar or of an unset list let
    through; the timeout bound widened (V4); the label regex loosened (V5); a needs or foreach source not checked; the
    notes check removed (a CR note printed raw by list and the catalog); the body check removed or loosened to any
    declared parameter (a derived one, which no request can set) — each lets `list` and the stack exit 0."""
    tree = make_tree(tmp_path / "t")
    path = tmp_path / "stacks.toml"
    path.write_text(text)
    for args in (["list"], ["st"]):
        r = run(tmp_path, tree, path, *args)
        assert r.returncode == 3, (args, r.stdout, r.stderr)
        assert message in r.stderr, r.stderr
    assert not (tmp_path / "log").exists()


def test_explain_runs_nothing_and_writes_no_record(tmp_path):
    """Mutant: explain executes the plan (the marker appears)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", {"q": {"type": "text", "required": True}},
                                        [{"id": "marker", "argv": MARK}, {"id": "show", "argv": [PY, "argv.py", "{q}"]}]))
    r = run(tmp_path, tree, reg, "explain", "st", "q=a b")
    assert r.returncode == 0, r.stderr
    assert "  show: %s argv.py 'a b'\n" % shlex.quote(PY) in r.stdout
    assert not (tree / "MARKER").exists() and not (tmp_path / "log").exists()
    r = run(tmp_path, tree, reg, "explain", "st", "q=a", "--rate", "s-20000101T000000Z-000000=1/1")
    assert r.returncode == 2 and "explain writes no record" in r.stderr


def test_a_defect_inside_a_step_thread_fails_the_step_loudly(tmp_path, monkeypatch, capsys):
    """Fault injection into the real main(): an exception inside a step's thread. Mutant: run_step() without its
    guard — the thread dies, the step vanishes from the record and the run exits 0."""
    mod = load_stack("ls_b9_stack_under_test")
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "boom", "argv": MARK},
                                                     {"id": "fine", "argv": [PY, "mark.py", "F"]}]))
    execute = mod.Runner.execute

    def failing_execute(self, step, n, argv, out):
        if step.id == "boom":
            raise RuntimeError("injected")
        return execute(self, step, n, argv, out)

    monkeypatch.setattr(mod.Runner, "execute", failing_execute)
    rc = mod.main(["--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"), "st"])
    out = capsys.readouterr().out
    assert rc == 1, out
    assert "## boom · FAILED · the runner failed: RuntimeError: injected" in out
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert steps["boom"]["status"] == "failed" and steps["fine"]["status"] == "ok" and (tree / "F").exists()


SLEEPER = "import os, time\nopen('pid', 'w').write(str(os.getpid()))\ntime.sleep(60)\n"


@pytest.mark.parametrize("sig", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP], ids=["INT", "TERM", "HUP"])
def test_a_signal_to_the_runner_kills_its_live_steps_and_writes_no_record(tmp_path, sig):
    """Each of the runner's three signals. Mutants: Runner.run() installs no signal handler — the signal kills the
    runner alone and its step, in its own session, sleeps on; handlers for SIGTERM only (V2: INT and HUP)."""
    tree = make_tree(tmp_path / "t")
    (tree / "sleeper.py").write_text(SLEEPER)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "nap", "argv": [PY, "sleeper.py"], "timeout": 120}]))
    p = subprocess.Popen([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"),
                          "st"], cwd=str(tree), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    deadline = time.monotonic() + 30
    while not (tree / "pid").exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    pid = int((tree / "pid").read_text())
    try:
        p.send_signal(sig)
        assert p.wait(timeout=15) == 128 + sig, p.stderr.read()
        assert "interrupted by signal %d" % sig in p.stderr.read()
        assert wait_dead([pid]) == []
        assert records(tmp_path / "log") == []
    finally:
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
        if p.poll() is None:
            p.kill()


@pytest.mark.parametrize("token", [
    "sym=a b", "sym=1abc", "word=.hidden", "word=" + "w" * 65, "agent=a0123456789abcde", "agent=a0123456789abcdef0",
    "agent=A0123456789abcdef", "n=12a", "n=1234567", "c=maybe", "t=" + "x" * 501, "t=line\nbreak",
    "t=line\rbreak", "syms=a,,b", "words=ok,-no"],
    ids=["symbol-space", "symbol-digit-first", "word-dot-first", "word-65", "agent-short", "agent-long", "agent-upper",
         "int-letter", "int-7-digits", "choice-other", "text-501", "text-newline", "text-cr", "symbols-empty-element",
         "words-dash"])
def test_every_type_refuses_a_value_outside_its_shape_before_any_step(tmp_path, token):
    """Mutants: fullmatch() weakened to match() in check_scalar (a valid prefix passes: agent-long, int-7-digits); a
    text that accepts a carriage return (V3: text-cr)."""
    tree = make_tree(tmp_path / "t")
    params = {"sym": {"type": "symbol"}, "syms": {"type": "symbols"}, "word": {"type": "word"},
              "words": {"type": "words"}, "agent": {"type": "agent"}, "n": {"type": "int"},
              "c": {"type": "choice", "choices": ["yes", "no"]}, "t": {"type": "text"}}
    reg = registry(tmp_path, stack_toml("st", params, [{"id": "marker", "argv": MARK}]))
    r = run(tmp_path, tree, reg, "st", token)
    assert r.returncode == 2, r.stdout + r.stderr
    assert " refused: " in r.stderr
    assert not (tree / "MARKER").exists() and not (tmp_path / "log").exists()
    r = run(tmp_path, tree, reg, "st", "sym=pkg.mod:Cls.meth", "syms=a,b_c", "word=v1.2-rc", "words=x,y",
            "agent=a0123456789abcdef", "n=123456", "c=no", "t=" + "x" * 500)
    assert r.returncode == 0, r.stdout + r.stderr    # the positive control: each shape at its edge passes


@pytest.mark.parametrize("sessions", [0, 2], ids=["none", "two"])
def test_the_transcript_of_an_agent_must_match_exactly_once(tmp_path, sessions):
    """Mutant: _transcript() takes the first of several matches (the `two` case runs)."""
    tree = make_tree(tmp_path / "t")
    for i in range(sessions):
        path = tmp_path / "tr" / "proj" / ("sess%d" % i) / "subagents" / ("agent-%s.jsonl" % AGENT)
        path.parent.mkdir(parents=True)
        path.write_text("")
    (tmp_path / "tr").mkdir(exist_ok=True)
    reg = registry(tmp_path, stack_toml("st", {"agent": {"type": "agent", "required": True}},
                                        [{"id": "marker", "argv": MARK},
                                         {"id": "show", "argv": [PY, "argv.py", "{transcript}"]}]))
    r = subprocess.run([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"),
                        "--transcript-root", str(tmp_path / "tr"), "st", "agent=" + AGENT], cwd=str(tree),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "{transcript}: %d matches of " % sessions in r.stderr and "exactly one is needed" in r.stderr
    assert not (tree / "MARKER").exists()


def test_a_run_from_a_worktree_logs_to_the_main_tree(tmp_path):
    """No --log-dir here: the default log dir IS the subject, and the main tree is a temporary repository.
    Mutant: the main tree taken from --show-toplevel (the tree itself): the record lands in the worktree's .jev/."""
    main = make_tree(tmp_path / "main")
    git(main, "worktree", "add", "-q", "--detach", str(tmp_path / "wt"))
    wt = Path(os.path.realpath(tmp_path / "wt"))
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "hello", "argv": MARK}]))
    r = subprocess.run([PY, str(STACK), "--registry", str(reg), "st"], cwd=str(wt), capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    [rec] = records(main / ".jev" / "stacks")
    assert rec["tree"] == str(wt) and (wt / "MARKER").exists()
    assert Path(rec["steps"][0]["out"]).parent == main / ".jev" / "stacks" / rec["run"]
    assert not (wt / ".jev").exists()


# ---------- the wave-1 registry ----------

def real(tmp_path, *args, timeout=300):
    return subprocess.run([PY, str(STACK), "--tree", str(ROOT), "--log-dir", str(tmp_path / "log"), *map(str, args)],
                          cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)


NOTES = {   # issue #80's pre-wiring list (VERIFY-LS-B9 round 3), each under its stack, and the round-4 brief's eighth;
            # the gate's second and harvest's first are amended for round 4's R3-F1 and R3-F3 fixes (the report says how);
            # changes' and fix-echo's are task #385's (LS-B12: how to read their output); the gate's fourth is the
            # 2026-10-02 22:2xZ retro's (the union section past the print cap)
    "harvest": ["On a resumed lane, check the `report:` line: the report window opens at the resume message, so no "
                "earlier round's text is this round's report (R3-F3).",
                "`report=` names an existing file to lint and hash; the hand-back itself is saved under the run "
                "directory as `handback.md`."],
    "gate": ["`runs=2` re-runs the pytest files only; `setid` covers the pytest files only.",
             "Read the counts line; `mode=run` refuses more than `max_files` (40).",
             "Pass `graph=no` where ripwire is missing and for a deleted path (F-18).",
             "With many paths the `union` section passes the print cap: take the list from the `union.out` file its "
             "cut line names (2026-10-02: a grep of the cut section missed 2 of 29 files)."],
    "ctx": ["`ctx` does not show a missing ripwire as unmapped (F-6)."],
    "review": ["`review mode=save` overwrites the shared sentrux baseline (F-5).",
               "`review`'s sentrux section is advisory; `tool exit N` is the only sign of a failed run."],
    "changes": ["`No changes detected.` covers only symbols the index holds; a `PARTIAL RESULT` or `LISTING CAPPED` "
                "header line is not a clean check."],
    "fix-echo": ["`fix-echo` prints JSON; it reads unmapped when no instrument answered (rg and graft missing); a diff "
                 "with nothing to echo reads ok, its ranking says why."],
}
WAVE1 = ["harvest", "gate", "ctx", "impact", "find", "premise", "echo", "review", "ci"]
NEW_LABELS = ["cbm", "changes", "why", "locate", "fix-echo"]      # task #385 (LS-B12), after wave 1 in the registry


def test_list_prints_one_line_per_stack_and_its_notes_under_it(tmp_path):
    """Round 4 item 6: each note under the stack it concerns; LS-B12: wave 1's nine, then task #385's five. Mutants: the
    notes not printed; a stack's notes printed before its own line (under the stack above)."""
    r = real(tmp_path, "list")
    assert r.returncode == 0, r.stderr
    lines = r.stdout.splitlines()
    assert [line.split()[0] for line in lines if not line.startswith(" ")] == WAVE1 + NEW_LABELS
    assert "gate  paths=<paths> [mode=plan|run] [runs=1|2] [graph=yes|no] [max_files=<int>]  — " in r.stdout
    assert sorted(line.split()[0] for line in lines if line.endswith(" · rated")) == [
        "cbm", "ctx", "echo", "find", "fix-echo", "impact", "locate", "review", "why"]
    under, label = {}, None
    for line in lines:
        if line.startswith(" "):
            assert line.startswith("  note: "), line
            under.setdefault(label, []).append(line[len("  note: "):])
        else:
            label = line.split()[0]
    assert under == NOTES


EXPLAIN = {
    "harvest": (["agent=" + AGENT], """\
explain harvest — a finished lane: its served models and refusal stops, its SubagentHandback message (tags neutralized), the report linted and hashed
tree {TREE} · HEAD {HEAD}
params: agent=a0123456789abcdef
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  models: python3 scripts/hiccup_scan.py --transcript {TR} --out '<run>/hiccup.md' (timeout 300 s)
  handback: python3 scripts/handback_extract.py --transcript {TR} --out '<run>/handback.md' --report-out '<run>/report.md' (timeout 120 s)
group 2
  agent_row: grep -F '| a0123456789abcdef |' '<run>/hiccup.md' (timeout 30 s, ok_rc 0,1)
  lint: not selected (when report=*)
  lint_handback: python3 scripts/report_lint.py --root {TREEQ} <lines of handback> (timeout 120 s, optional)
  local_ids: python3 scripts/handback_extract.py --local-ids '<run>/handback.md' <lines of handback> (optional)
  sha: not selected (when report=*)
"""),
    "harvest-report": (["agent=" + AGENT, "report=tasks/briefs/labeling/LS-B9-brief.md"], """\
explain harvest — a finished lane: its served models and refusal stops, its SubagentHandback message (tags neutralized), the report linted and hashed
tree {TREE} · HEAD {HEAD}
params: agent=a0123456789abcdef report=tasks/briefs/labeling/LS-B9-brief.md
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  models: python3 scripts/hiccup_scan.py --transcript {TR} --out '<run>/hiccup.md' (timeout 300 s)
  handback: python3 scripts/handback_extract.py --transcript {TR} --out '<run>/handback.md' --report-out '<run>/report.md' (timeout 120 s)
group 2
  agent_row: grep -F '| a0123456789abcdef |' '<run>/hiccup.md' (timeout 30 s, ok_rc 0,1)
  lint: python3 scripts/report_lint.py --root {TREEQ} tasks/briefs/labeling/LS-B9-brief.md (timeout 120 s, optional)
  lint_handback: not selected (when report='')
  local_ids: python3 scripts/handback_extract.py --local-ids '<run>/handback.md' <lines of handback> (optional)
  sha: sha256sum -- tasks/briefs/labeling/LS-B9-brief.md
"""),
    "gate": (["paths=scripts/report_lint.py,tests/test_report_lint.py", "mode=run"], """\
explain gate — every test that names each path, united with the tests ripwire's call graph links to the change (graph=yes); mode=run runs each file with its own runner: pytest, python3 or bash
tree {TREE} · HEAD {HEAD}
params: paths=scripts/report_lint.py,tests/test_report_lint.py mode=run runs=2 graph=yes max_files=40
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
<tmp> = /tmp/stack-<run id>, outside every git work tree; removed after the run
group 1
  tests: python3 scripts/gate_files.py scripts/report_lint.py tests/test_report_lint.py (timeout 120 s)
  why: python3 scripts/gate_files.py --why scripts/report_lint.py tests/test_report_lint.py (timeout 120 s)
  graph: bash scripts/ripwire_review.sh test-gate scripts/report_lint.py,tests/test_report_lint.py (timeout 300 s, ok_rc 0,4)
group 2
  sources: python3 scripts/gate_union.py --why --mode run --max-files 40 --graph yes --ripwire '<run>/graph.out' scripts/report_lint.py tests/test_report_lint.py (timeout 120 s, headline)
  union: python3 scripts/gate_union.py --runner pytest --graph yes --ripwire '<run>/graph.out' scripts/report_lint.py tests/test_report_lint.py (timeout 120 s)
  union_py: python3 scripts/gate_union.py --runner python3 --graph yes --ripwire '<run>/graph.out' scripts/report_lint.py tests/test_report_lint.py (timeout 120 s)
  union_sh: python3 scripts/gate_union.py --runner bash --graph yes --ripwire '<run>/graph.out' scripts/report_lint.py tests/test_report_lint.py (timeout 120 s)
group 3
  setid: bash scripts/pc_suite.sh set-id -- <lines of union> (nothing to do when its input is empty)
group 4
  run: bash scripts/test_summary.sh '--basetemp=<tmp>/bt' <lines of union> (×2, timeout 1800 s, needs sources, nothing to do when its input is empty)
group 5
  scripts: python3 {TREEQE} (timeout 600 s, one call per line of union_py, needs sources, nothing to do when its input is empty)
group 6
  shells: bash {TREEQE} (timeout 600 s, one call per line of union_sh, needs sources, nothing to do when its input is empty)
"""),
    "review-compare": (["files=scripts/gate_union.py,scripts/lint_files.py", "mode=compare"], """\
explain review — a change's review: sentrux architecture health (check, save a baseline, compare with it), and for the files ripwire's test gate, the pyflakes delta and the AP screen
tree {TREE} · HEAD {HEAD}
params: files=scripts/gate_union.py,scripts/lint_files.py mode=compare
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  sentrux: bash scripts/sentrux_review.sh compare (timeout 600 s, optional)
  ripwire: bash scripts/ripwire_review.sh test-gate scripts/gate_union.py,scripts/lint_files.py (timeout 300 s, ok_rc 0,4)
  lint: python3 scripts/lint_files.py scripts/gate_union.py scripts/lint_files.py (timeout 120 s)
  ap: python3 scripts/ap_screen.py scripts/gate_union.py scripts/lint_files.py (timeout 300 s)
"""),
    "review-save": (["mode=save"], """\
explain review — a change's review: sentrux architecture health (check, save a baseline, compare with it), and for the files ripwire's test gate, the pyflakes delta and the AP screen
tree {TREE} · HEAD {HEAD}
params: mode=save
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  sentrux: bash scripts/sentrux_review.sh save (timeout 600 s, optional)
  ripwire: not selected (when files=*)
  lint: not selected (when files=*)
  ap: not selected (when files=*)
"""),
    "ctx": (["files=scripts/stack.py,scripts/gate_files.py", "q=who runs the steps", "sym=Runner,cap_lines"], """\
explain ctx — the code-intel pack of files: graft skeletons and ask, GitNexus impact, code-review-graph, ripwire, the AP screen
tree {TREE} · HEAD {HEAD}
params: files=scripts/stack.py,scripts/gate_files.py q='who runs the steps' sym=Runner,cap_lines
body: q {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  pack: bash scripts/lane_context.sh -q 'who runs the steps' -s Runner -s cap_lines scripts/stack.py scripts/gate_files.py (timeout 900 s)
"""),
    "impact": (["sym=build_page"], """\
explain impact — the blast radius of one symbol from four instruments in parallel: GitNexus impact, code-review-graph callers and tests, ripwire edit-check
tree {TREE} · HEAD {HEAD}
params: sym=build_page
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  gitnexus: node .gitnexus/run.cjs impact build_page --direction upstream --repo . (timeout 120 s)
  crg_callers: code-review-graph query callers_of build_page (timeout 120 s)
  crg_tests: code-review-graph query tests_for build_page (timeout 120 s)
  ripwire: bash scripts/ripwire_review.sh edit-check build_page (timeout 180 s)
"""),
    "find": (["q=how does the stop hook drop a request"], """\
explain find — what the repo already holds on q: graft ask, the owner's rulings, the chat, the AF-AP registry rows
tree {TREE} · HEAD {HEAD}
params: q='how does the stop hook drop a request' words=stop,hook,drop,request
body: q {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  graft: graft ask 'how does the stop hook drop a request' (timeout 120 s)
  rulings: python3 scripts/owner_rulings.py stop hook drop request (ok_rc 0,1)
  chat: python3 scripts/chat_find.py 'how does the stop hook drop a request' --hits 5 --order lexical --no-jev-log (timeout 300 s)
  registry: git grep -n -i -e '^| AF-AP-' --and '(' -e stop -e hook -e drop -e request ')' -- docs/INCIDENT-LOG.md (ok_rc 0,1)
"""),
    "premise": (["files=scripts/premise_block.sh,scripts/test_summary.sh"], """\
explain premise — the premise facts of files: tracked or not, sha256, line count, the last commit that touched each
tree {TREE} · HEAD {HEAD}
params: files=scripts/premise_block.sh,scripts/test_summary.sh
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  tracked: git ls-files --error-unmatch -- scripts/premise_block.sh scripts/test_summary.sh (ok_rc 0,1)
  sha: sha256sum -- scripts/premise_block.sh scripts/test_summary.sh (ok_rc 0,1)
  lines: wc -l -- scripts/premise_block.sh scripts/test_summary.sh (ok_rc 0,1)
  last [1/2]: git log -1 '--format=%h %ci %s' -- scripts/premise_block.sh
  last [2/2]: git log -1 '--format=%h %ci %s' -- scripts/test_summary.sh
"""),
    "echo": (["pattern=start_new_session"], """\
explain echo — the bug-echo sweep: the pattern in the six code roots, the incident log's lines, the AP screen over the files hit
tree {TREE} · HEAD {HEAD}
params: pattern=start_new_session roots=scripts,harness-ports,src,proofs,.claude/hooks,.github
body: pattern {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  code: rg -n --no-heading --sort path -e start_new_session -- scripts harness-ports src proofs .claude/hooks .github (timeout 120 s, ok_rc 0,1)
  files: rg -l --sort path -e start_new_session -- scripts harness-ports src proofs .claude/hooks .github (timeout 120 s, ok_rc 0,1)
  registry: git grep -n -i -E -e start_new_session -- docs/INCIDENT-LOG.md (ok_rc 0,1)
group 2
  ap: python3 scripts/ap_screen.py <lines of files> (timeout 300 s, optional)
"""),
    "ci": (["branch=claude/soundbox-kit-migration-iz1jwf"], """\
explain ci — the branch's stage0-ci verdict through scripts/ci_gate.py: 0 passed, 75 not in yet, 1 red
tree {TREE} · HEAD {HEAD}
params: branch=claude/soundbox-kit-migration-iz1jwf
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  verdict: python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf (ok_rc 0,75)
"""),
}


@pytest.mark.parametrize("case", sorted(EXPLAIN))
def test_explain_of_each_wave1_stack_is_pinned(tmp_path, case):
    """The reviewed plan of each wave-1 stack, pinned; every argv was checked against the instrument's own usage
    (the LS-B9 report's interface table). Runs anywhere: explain resolves programs by name and runs nothing."""
    tokens, expected = EXPLAIN[case]
    transcript_root = tmp_path / "transcripts"
    transcript = transcript_root / "proj" / "sess" / "subagents" / ("agent-%s.jsonl" % AGENT)
    transcript.parent.mkdir(parents=True)
    transcript.write_text("")
    r = real(tmp_path, "--transcript-root", transcript_root, "explain", case.split("-")[0], *tokens)
    assert r.returncode == 0, r.stderr
    for key, value in (("{TREEQE}", shlex.quote(str(ROOT) + "/{each}")), ("{TREEQ}", shlex.quote(str(ROOT))),
                       ("{TREE}", str(ROOT)), ("{LOG}", str(tmp_path / "log")),
                       ("{HEAD}", git(ROOT, "rev-parse", "HEAD")[:12]), ("{TR}", shlex.quote(str(transcript))),
                       ("{BODYNOTE}", BODY_NOTE)):
        expected = expected.replace(key, value)
    assert r.stdout == expected
    assert not (tmp_path / "log").exists()


# LS-B11 (task #380): a stack's `body`, the parameter a chat-form box's lines below its divider fill
# (scripts/ls_req.py, THE BOX); the divider's characters built from escapes
BODY_NOTE = "(a chat-form box's lines below its %s divider fill it)" % ("\u2504" * 3)


def test_explain_names_a_stacks_body_and_only_when_it_has_one(tmp_path):
    """`explain` prints the body line right after `params:` for a stack that names a body, and none for a stack that
    does not; the body is taken as any parameter is (the run is unchanged). Mutants: the body line not printed;
    printed for every stack (`body: None`)."""
    tree = make_tree(tmp_path / "t")
    step = [{"id": "show", "argv": [PY, "argv.py", "{q}"]}]
    reg = registry(tmp_path, stack_toml("st", {"q": {"type": "text", "required": True}}, step).replace(
        "outward = false\n", 'outward = false\nbody = "q"\n'), stack_toml("plain", {"q": {"type": "text",
                                                                                              "required": True}}, step))
    r = run(tmp_path, tree, reg, "explain", "st", "q=a b")
    assert r.returncode == 0, r.stderr
    assert "\nparams: q='a b'\nbody: q %s\n<run> = " % BODY_NOTE in r.stdout, r.stdout
    r = run(tmp_path, tree, reg, "explain", "plain", "q=a b")
    assert r.returncode == 0 and "body" not in r.stdout and "\nparams: q='a b'\n<run> = " in r.stdout, r.stdout
    r = run(tmp_path, tree, reg, "st", "q=a b")
    assert r.returncode == 0 and '["a b"]' in r.stdout, r.stdout


def test_the_registry_names_a_body_for_find_ctx_echo_cbm_and_locate_only():
    """LS-B11 item 4, pinned: find and ctx name q (a question in prose), echo names pattern (a search pattern); no
    other stack has one free-text parameter a person writes as prose or a pattern (ci's branch is a name). LS-B12
    (task #385): cbm's q (a search text) and locate's q (a bug text); changes, why and fix-echo take a choice, a ref, a
    path or a symbol. Mutant: a body line dropped from or added to scripts/stacks.toml."""
    mod = load_stack("stack_body_registry")
    _tools, stacks = mod.load_registry(str(ROOT / "scripts" / "stacks.toml"))
    assert {label: st.body for label, st in stacks.items()} == {
        "harvest": None, "gate": None, "ctx": "q", "impact": None, "find": "q", "premise": None, "echo": "pattern",
        "review": None, "ci": None, "cbm": "q", "changes": None, "why": None, "locate": "q", "fix-echo": None}


def test_premise_runs_on_this_tree(tmp_path):
    """The real stack on the real tree; the oracle is computed here from the files themselves."""
    files = ["scripts/premise_block.sh", "scripts/test_summary.sh"]
    r = real(tmp_path, "premise", "files=" + ",".join(files))
    assert r.returncode == 0, r.stdout + r.stderr
    steps = {(s["id"], s.get("n")): s for s in records(tmp_path / "log")[-1]["steps"]}
    text = {k: Path(s["out"]).read_text() for k, s in steps.items()}
    assert text[("tracked", None)].split() == files
    assert text[("sha", None)].splitlines() == ["%s  %s" % (hashlib.sha256((ROOT / f).read_bytes()).hexdigest(), f)
                                                for f in files]
    counts = [(ROOT / f).read_bytes().count(b"\n") for f in files]
    assert [line.split() for line in text[("lines", None)].splitlines()] == [
        [str(n), f] for n, f in zip(counts, files)] + [[str(sum(counts)), "total"]]
    assert all(re.match(r"[0-9a-f]{7,} [0-9]{4}-[0-9]{2}-[0-9]{2} ", text[("last", n)]) for n in (1, 2))


def test_gate_plan_runs_on_this_tree(tmp_path):
    """The real stack on the real tree, graph=no (runs anywhere): each listed test names the path (read here), each file
    goes to the runner the oracle names (run-all.sh's mapping, pytest's default pattern), the counts are in the header,
    and the set id is pc_suite.sh's for exactly the pytest lines."""
    r = real(tmp_path, "gate", "paths=scripts/report_lint.py", "graph=no")
    assert r.returncode == 0, r.stdout + r.stderr
    rec = records(tmp_path / "log")[-1]
    steps = {s["id"]: s for s in rec["steps"]}
    assert sorted(steps) == ["setid", "sources", "tests", "union", "union_py", "union_sh", "why"]
    listed = Path(steps["tests"]["out"]).read_text().split()
    assert {"tests/test_report_lint.py", "tests/test_no_laya_in_gates.py",
            "harness-ports/tests/test_pc_lane.sh"} <= set(listed)
    assert listed == sorted(set(listed))
    assert all("scripts/report_lint.py" in (ROOT / f).read_text(errors="replace") for f in listed)
    lists = {k: Path(steps[k]["out"]).read_text().split() for k in ("union", "union_py", "union_sh")}
    assert lists == {k: [f for f in listed if runner_expected(f) == runner]
                     for k, runner in (("union", "pytest"), ("union_py", "python3"), ("union_sh", "bash"))}
    assert "harness-ports/tests/test_pc_lane.sh" in lists["union_sh"]
    n = {k: len(v) for k, v in lists.items()}
    header = r.stdout.split("\n\n")[0].splitlines()
    assert "sources · run list %d of union %d: pytest %d · python3 %d · bash %d · not run %d" % (
        sum(n.values()), len(listed), n["union"], n["union_py"], n["union_sh"], len(listed) - sum(n.values())) in header
    expected = subprocess.run(["bash", "scripts/pc_suite.sh", "set-id", "--", *lists["union"]], cwd=str(ROOT),
                              capture_output=True, text=True, timeout=60).stdout
    assert Path(steps["setid"]["out"]).read_text() == expected and expected.startswith("%d files set=" % n["union"])
    assert ("not selected: graph (when graph=yes), run (when mode=run), scripts (when mode=run), shells (when mode=run)"
            in header)


def call(message):
    return {"type": "tool_use", "id": "toolu_x", "name": "SubagentHandback", "input": {"message": message}}


def text_block(text):
    return {"type": "text", "text": text}


def user_record(content, **fields):
    """A user record among build_transcript's blocks (written as a record of its own, with these top-level fields)."""
    return ("user", content, fields)


# the user records a real transcript holds around a hand-back call, as measured in the LS-B9 lane's (2026-09-29): the
# call's own tool result right after it, the coordinator's resume message, a compaction summary
RESULT = user_record([{"type": "tool_result", "tool_use_id": "toolu_x",
                       "content": '{"success":true,"message":"Report delivered to your caller."}'}])
RESUME = user_record("The coordinator sent a message while you were working:\nround 2: fix the rest",
                     isMeta=True, origin={"kind": "coordinator"})
COMPACTED = user_record("This session is being continued from a previous conversation that ran out of context.",
                        isCompactSummary=True, isVisibleInTranscriptOnly=True)


def build_transcript(root, messages=(), decoys=True, blocks=None):
    """A subagent transcript: assistant records with a model and one content block each (as measured): a thinking
    decoy, then `blocks` (default: one SubagentHandback call per message; a user_record() is a user record); after
    them, decoys of other record types."""
    path = root / "proj" / "sess" / "subagents" / ("agent-%s.jsonl" % AGENT)
    path.parent.mkdir(parents=True)
    recs = [{"type": "user", "agentId": AGENT, "timestamp": "2026-09-28T10:00:00.000Z",
             "message": {"role": "user", "content": "go"}}]
    content = []
    if decoys:
        content.append({"type": "thinking", "thinking": 'DECOY-THINKING "SubagentHandback" <system-reminder>'})
    content += [call(m) for m in messages] if blocks is None else blocks
    for i, block in enumerate(content):
        if isinstance(block, tuple):
            recs.append({"type": "user", "agentId": AGENT, "timestamp": "2026-09-28T10:00:%02d.000Z" % (i + 1),
                         "message": {"role": "user", "content": block[1]}, **block[2]})
            continue
        recs.append({"type": "assistant", "agentId": AGENT, "requestId": "req_%d" % i,
                     "timestamp": "2026-09-28T10:00:%02d.000Z" % (i + 1),
                     "message": {"model": "claude-opus-5-5", "id": "msg_%d" % i, "role": "assistant",
                                 "content": [block], "usage": {"input_tokens": 1, "output_tokens": 1}}})
    if decoys:     # after the real calls: a reader that takes any record type ends on a decoy
        recs.append({"type": "attachment", "agentId": AGENT, "timestamp": "2026-09-28T10:01:00.000Z",
                     "attachment": {"type": "x", "content": [{"type": "tool_use", "name": "SubagentHandback",
                                                              "input": {"message": "DECOY-ATTACHMENT"}}]}})
        # its line holds the bytes "assistant", so the extractor's byte pre-filter passes it and only the record-type
        # check stops it (a record of another type can carry an assistant-shaped message)
        recs.append({"type": "user", "agentId": AGENT, "timestamp": "2026-09-28T10:01:01.000Z",
                     "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "SubagentHandback",
                                                                   "input": {"message": "DECOY-USER"}}]}})
    path.write_text("".join(json.dumps(x) + "\n" for x in recs))
    return path


NS = "antml" + ":"   # built in code: a tag-shaped string typed with this prefix lost it on the way to the file
TAGS = ["<system-reminder>", "</system-reminder>", "<function_calls>", "</function_calls>", '<invoke name="x">',
        "</invoke>", '<parameter name="y">', "</parameter>", "<" + NS + "thing>", "</" + NS + "thing>",
        "<SYSTEM-REMINDER>"]
KEPT = ["<parameters>", "<invoked>", "<system-reminders>", "<b>", "< invoke>", "<\\system-reminder>"]


def neutralized_by_hand(text):
    """The independent oracle: each listed tag written out with `<\\` by plain string replacement."""
    for tag in TAGS:
        text = text.replace(tag, "<\\" + tag[1:])
    return text


def sha12(data):
    return hashlib.sha256(data).hexdigest()[:12]


NO_LONG = "report: none (no assistant text block of 1000 or more characters in the last round)\n"


def test_harvest_on_a_built_subagent_transcript(tmp_path):
    """The real harvest stack over a built transcript (hiccup_scan, the extractor, grep and report_lint for real): the
    extractor's one stdout line, the hand-back's path in the run dir, is chained to the lint. Mutant: check_path
    without its run_dir branch (that line is refused as outside the tree and the lint SKIPPED)."""
    message = "REPORT-BODY\n" + "\n".join(TAGS + KEPT) + "\nsee scripts/stack.py\n"
    build_transcript(tmp_path / "tr", ["FIRST-MESSAGE", message])
    r = real(tmp_path, "--transcript-root", tmp_path / "tr", "harvest", "agent=" + AGENT)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = records(tmp_path / "log")[-1]
    steps = {s["id"]: s for s in rec["steps"]}
    assert sorted(steps) == ["agent_row", "handback", "lint_handback", "local_ids", "models"]
    handback = tmp_path / "log" / rec["run"] / "handback.md"
    assert handback.read_text() == neutralized_by_hand(message)
    data = handback.read_bytes()
    assert Path(steps["handback"]["out"]).read_text() == (
        "%s\n--- stderr ---\nhandback: found calls=2 chars=%d bytes=%d neutralized=%d sha256=%s out=%s\n%s"
        % (handback, len(message), len(data), len(TAGS), sha12(data), handback, NO_LONG))
    assert (steps["lint_handback"]["status"], steps["lint_handback"]["argv"][-1]) == ("ok", str(handback))
    assert "assistant_usage_model=3" in Path(steps["models"]["out"]).read_text()
    assert Path(steps["agent_row"]["out"]).read_text().startswith("| %s |" % AGENT)
    assert "REPORT-BODY" not in r.stdout and "DECOY" not in handback.read_text()


def test_harvest_saves_and_lints_a_lanes_longer_text_report(tmp_path):
    """Item 7b (the scrubber repair wrote a 63,540-character report as text and a 3,568-character hand-back, and
    harvest saved only the hand-back). Mutant: the extractor's stdout left on the hand-back (the lint reads the
    summary, never the report)."""
    report = "LANE-REPORT\n" + "\n".join(TAGS) + "\n" + "r" * 2000 + "\n"
    message = "SUMMARY " * 25
    build_transcript(tmp_path / "tr", blocks=[text_block(report), call(message)])
    r = real(tmp_path, "--transcript-root", tmp_path / "tr", "harvest", "agent=" + AGENT)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = records(tmp_path / "log")[-1]
    steps = {s["id"]: s for s in rec["steps"]}
    run_dir = tmp_path / "log" / rec["run"]
    assert (run_dir / "report.md").read_text() == neutralized_by_hand(report)
    assert (run_dir / "handback.md").read_text() == message
    assert (steps["lint_handback"]["status"], steps["lint_handback"]["argv"][-1]) == ("ok", str(run_dir / "report.md"))
    assert "report: saved chars=%d " % len(report) in r.stdout


def test_harvest_prints_a_failing_lint_and_still_exits_0(tmp_path):
    """Item 7a: the lint is advisory; a report whose citation the linter reads as a MISS still harvests, and the lint's
    lines still print. Mutant: lint_handback required again (exit 1)."""
    build_transcript(tmp_path / "tr", ["REPORT\n- `def no_such_function_ls_b9` is at scripts/stack.py:1\n"])
    r = real(tmp_path, "--transcript-root", tmp_path / "tr", "harvest", "agent=" + AGENT)
    assert r.returncode == 0, r.stdout + r.stderr
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert (steps["lint_handback"]["status"], steps["lint_handback"]["rc"]) == ("failed", 1)
    section = r.stdout.split("## lint_handback · ")[1]
    assert section.startswith("FAILED · rc 1 · ") and section.split("\n")[0].endswith(" s (not required)")
    assert "MISS " in section and "MISS 1" in section


def test_harvest_with_no_handback_skips_the_lint(tmp_path):
    """D21: with no hand-back the extractor prints no path, so the chained lint is SKIPPED, never failed; the missing
    hand-back itself fails the harvest. Mutant: lint_handback given {run}/handback.md again (it FAILS on the absent
    file)."""
    build_transcript(tmp_path / "tr", [])
    r = real(tmp_path, "--transcript-root", tmp_path / "tr", "harvest", "agent=" + AGENT)
    assert r.returncode == 1, r.stdout + r.stderr
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert (steps["handback"]["status"], steps["handback"]["rc"], steps["lint_handback"]["status"]) == (
        "failed", 1, "skipped")
    assert "## lint_handback · SKIPPED — its input step handback failed (rc 1)" in r.stdout
    assert " · exit 1 — required, not ok: handback\n" in r.stdout


def extract(tmp_path, transcript, report_out=True):
    out, rep = tmp_path / "hb.md", tmp_path / "report.md"
    argv = [PY, str(HANDBACK), "--transcript", str(transcript), "--out", str(out)]
    r = subprocess.run(argv + (["--report-out", str(rep)] if report_out else []), capture_output=True, text=True,
                       timeout=60)
    return r, out, rep


def test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized(tmp_path):
    """Mutants: the first call's message kept (FIRST-MESSAGE written); no neutralization (a raw tag written); a
    non-assistant record read (the user-record decoy, last in the file, written); the message printed."""
    message = "SECOND\n" + "\n".join(TAGS + KEPT) + "\n"
    r, out, rep = extract(tmp_path, build_transcript(tmp_path, ["FIRST-MESSAGE", message]), report_out=False)
    assert r.returncode == 0, r.stderr
    data = out.read_bytes()
    assert data.decode() == neutralized_by_hand(message)
    assert all(k in data.decode() for k in KEPT)
    assert r.stdout == "%s\n" % out                  # the file to lint: never the message
    assert r.stderr == "handback: found calls=2 chars=%d bytes=%d neutralized=%d sha256=%s out=%s\n" % (
        len(message), len(data), len(TAGS), sha12(data), out)
    assert not rep.exists()


def test_handback_extract_absent_exits_1_and_writes_nothing(tmp_path):
    """Mutant: the hand-back's path printed when there is none (a chained lint would run on a missing file)."""
    r, out, rep = extract(tmp_path, build_transcript(tmp_path, []))
    assert (r.returncode, r.stdout, r.stderr) == (1, "", "handback: absent calls=0\n" + NO_LONG)
    assert not out.exists() and not rep.exists()
    r = subprocess.run([PY, str(HANDBACK), "--transcript", str(tmp_path / "none.jsonl"), "--out", str(out)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2 and "cannot read the transcript" in r.stderr


def test_handback_extract_saves_the_lanes_longer_text_report(tmp_path):
    """Item 7b. The report is the last text block of 1,000+ characters before the last hand-back call. Mutants: the
    last long text block overall taken (the epilogue after the call); the first one taken (EARLY); a thinking block
    read as text (the longer decoy between the report and the call); the lint target left on the hand-back."""
    report = "LANE-REPORT\n" + "\n".join(TAGS + KEPT) + "\n" + "r" * 3000 + "\n"
    message = "SUMMARY " * 25
    transcript = build_transcript(tmp_path, blocks=[
        text_block("EARLY " * 300), text_block(report), {"type": "thinking", "thinking": "THINKING-DECOY " * 400},
        text_block("short"), call(message), text_block("EPILOGUE " * 200)])
    r, out, rep = extract(tmp_path, transcript)
    assert r.returncode == 0, r.stderr
    assert r.stdout == "%s\n" % rep and out.read_text() == message
    data = rep.read_bytes()
    assert data.decode() == neutralized_by_hand(report)
    assert r.stderr.splitlines()[1] == (
        "report: saved chars=%d bytes=%d neutralized=%d sha256=%s out=%s (the longer: %d characters against the "
        "hand-back's %d)" % (len(report), len(data), len(TAGS), sha12(data), rep, len(report), len(message)))


def test_handback_extract_takes_the_report_only_from_the_last_round(tmp_path):
    """F-11: a resumed lane wrote its round-1 report as text before its first hand-back and only a short summary at
    its second: the round-1 text is not this round's report; a long text between the resume and the second call is.
    Mutant: the search not bounded by the previous call (the round-1 text is saved, and linted, as this round's
    report)."""
    round1 = "ROUND1-REPORT " * 400
    r, out, rep = extract(tmp_path / "a", build_transcript(tmp_path / "a", blocks=[
        text_block(round1), call("R1 SUMMARY"), RESULT, RESUME, text_block("short"), call("R2 SUMMARY " * 8)]))
    assert r.returncode == 0, r.stderr
    assert (r.stdout, rep.exists()) == ("%s\n" % out, False)
    assert r.stderr.splitlines()[1] == NO_LONG.rstrip("\n")
    round2 = "ROUND2-REPORT " * 200
    r, out, rep = extract(tmp_path / "b", build_transcript(tmp_path / "b", blocks=[
        text_block(round1), call("R1 SUMMARY"), RESULT, RESUME, text_block(round2), call("R2 SUMMARY")]))
    assert r.returncode == 0, r.stderr
    assert r.stdout == "%s\n" % rep and rep.read_text() == round2


@pytest.mark.parametrize("blocks, rc, line, saved", [
    ([text_block("T" * 1500), call("M" * 2000)], 0,
     "report: none longer than the hand-back (the last long text block: 1500 characters, the hand-back: 2000)", False),
    ([text_block("T" * 999), call("M" * 10)], 0, NO_LONG.rstrip("\n"), False),
    ([text_block("T" * 1000), call("M" * 10)], 0, "report: saved chars=1000 ", True),
    ([text_block("T" * 1500)], 1, "report: saved chars=1500 ", True),
], ids=["shorter", "999", "1000", "no-handback"])
def test_handback_extract_writes_a_report_only_when_it_is_longer(tmp_path, blocks, rc, line, saved):
    """Mutants: a report written that is not longer than the hand-back; the 1,000-character bound moved; with no
    hand-back, the report left unwritten or its path printed."""
    r, out, rep = extract(tmp_path, build_transcript(tmp_path, blocks=blocks))
    assert r.returncode == rc, r.stderr
    assert r.stderr.splitlines()[1].startswith(line), r.stderr
    assert rep.exists() == saved and out.exists() == (rc == 0)
    assert r.stdout == ("" if rc else "%s\n" % (rep if saved else out))     # the longer file, when there is a hand-back


def build_test_root(root):
    """A synthetic repository root for gate_files.py: what counts as a test file, and what names the path."""
    files = {
        "tests/test_code.py": "import x\nPATH = 'scripts/x.py'\n",
        "tests/test_comment.py": '"""Tests for scripts/x.py:\n\nthe docstring names it."""\n# scripts/x.py again\n'
                                 "def test_a():\n    '''scripts/x.py in a function docstring'''\n",
        "tests/red/test_nested.py": "P = 'scripts/x.py'  # a code line with a comment\n",
        "tests/helper.py": "P = 'scripts/x.py'\n",
        "tests/__pycache__/test_cached.py": "P = 'scripts/x.py'\n",
        "tests/test_self.py": "nothing here\n",
        "tests/test_other.py": "P = 'scripts/y.py'\n",
        "harness-ports/tests/run.sh": "#!/bin/sh\n# scripts/x.py in a shell comment\nbash scripts/x.py\n",
        "harness-ports/tests/__pycache__/x.pyc": "scripts/x.py\n",
        "docs/test_doc.py": "scripts/x.py\n",
    }
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    (root / "tests" / "test_binary.py").write_bytes(b"scripts/x.py\0\x01")


def test_gate_files_lists_every_test_that_names_a_path(tmp_path):
    """Mutants: harness-ports/tests/ not walked; __pycache__ walked; a binary file read; no recursion below tests/;
    a given path that is a test file not listed (self); a file not named test_*.py listed."""
    build_test_root(tmp_path)
    r = subprocess.run([PY, str(GATE_FILES), "--root", str(tmp_path), "./scripts/x.py", "tests/test_self.py",
                        str(tmp_path / "scripts" / "x.py")], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["harness-ports/tests/run.sh", "tests/red/test_nested.py", "tests/test_code.py",
                                     "tests/test_comment.py", "tests/test_self.py"]


def test_gate_files_why_names_code_and_comment_mentions_and_self(tmp_path):
    """Mutants: every mention classified as code; docstring lines not read as comment; `self` not printed."""
    build_test_root(tmp_path)
    r = subprocess.run([PY, str(GATE_FILES), "--root", str(tmp_path), "--why", "scripts/x.py", "tests/test_self.py"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["harness-ports/tests/run.sh  code:3  comment:2",
                                     "tests/red/test_nested.py  code:1",
                                     "tests/test_code.py  code:2",
                                     "tests/test_comment.py  comment:1,4,6",
                                     "tests/test_self.py  self"]
    r = subprocess.run([PY, str(GATE_FILES), "--root", str(tmp_path), "."], capture_output=True, text=True, timeout=60)
    assert r.returncode == 2 and "not the root itself" in r.stderr


# ---------- round 2: gate_union.py (item 1), lint_files.py (item 2) ----------

def ripwire_output(rows, attrs='tests_capped="0"', comment_row='<t p="tests/test_decoy.py" run="x"/>'):
    """The shape of `ripwire_review.sh test-gate` (ripwire 0.4.0, measured 2026-09-28; a real one is pasted in the
    LS-B9 report): an XML comment, then one <test-gate> element holding <t> rows (tests to run) and <u> rows."""
    return ('<!-- ripwire test-gate: tests to run for this change + the UNTESTED blast radius. %s is a decoy that sits '
            'in the comment; the <t> rows and the <u> rows follow. --><test-gate changed="1" impacted="3" tests="%d" '
            'untested="1" shown_tests="%d" %s shown_untested="1" untested_capped="0" limit="20">%s'
            '<u sym="main" p="scripts/x.py" l="1" ccx="3"/></test-gate>'
            % (comment_row, len(rows), len(rows), attrs,
               "".join('<t p="%s" run="python3 %s"/>' % (p, p) for p in rows)))


def runner_expected(path):
    """The runner the gate should give a file, restated here as the oracle: run-all.sh's own mapping inside
    harness-ports/tests/ (python3 for test_*.py, bash for test_*.sh and run-all.sh; its lines 12-16 and 21-67), pytest's
    default python_files elsewhere (the repo's pyproject.toml sets none); None for a file the gate names "not run"."""
    name = os.path.basename(path)
    if path == "tests/test_vendored_manifest.py":
        return None
    if os.path.dirname(path) == "harness-ports/tests":
        if name.startswith("test_") and name.endswith(".py"):
            return "python3"
        return "bash" if (name.startswith("test_") and name.endswith(".sh")) or name == "run-all.sh" else None
    if path.startswith("harness-ports/tests/"):
        return None
    return "pytest" if name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py")) else None


def union_root(tmp_path):
    """build_test_root, plus a file of each runner and each not-run reason that names scripts/x.py or that ripwire's
    rows below link."""
    build_test_root(tmp_path)
    files = {"tests/test_linked.py": "nothing named\n", "tests/test_decoy.py": "nothing named\n",
             "harness-ports/tests/check.sh": "nothing named\n", "tests/fixtures/make_x.py": "nothing named\n",
             "harness-ports/tests/test_script.py": "P = 'scripts/x.py'\n",
             "harness-ports/tests/test_shell.sh": "bash scripts/x.py\n",
             "harness-ports/tests/fixtures/data.txt": "scripts/x.py\n",
             "tests/test_vendored_manifest.py": "P = 'scripts/x.py'\n"}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    return tmp_path


def gate_union(root, *args):
    return subprocess.run([PY, str(GATE_UNION), "--root", str(root), *map(str, args)], capture_output=True, text=True,
                          timeout=60)


NOT_HARNESS = "not run: not a harness test (run-all.sh runs harness-ports/tests/test_*.py with python3, test_*.sh with bash)"
NOT_TEST = "not run: not a test file (pytest collects test_*.py and *_test.py; it would import this one and run nothing)"
HEAVY_LINE = ("not run: a whole-file run copies about 3.4 GB of vendored trees; run its one relevant test: python3 -m "
              "pytest tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation "
              "--basetemp=<a private dir outside every work tree>")
UNION_ROWS = ["tests/test_code.py", "tests/test_linked.py", "tests/test_gone.py", "harness-ports/tests/check.sh",
              "tests/fixtures/make_x.py"]


def test_gate_union_gives_each_file_its_runner_or_says_why_not(tmp_path):
    """F-1: a harness script goes to python3, a harness shell test to bash, a test_*.py elsewhere to pytest; every
    other file is named "not run" with its reason (F-2: the 3.4 GB manifest test with its one relevant test's command).
    Mutants: ripwire's rows ignored (test_linked missing); the comment read (the decoy, an existing file, joins); a gone
    row kept; the sources cut to gate_files; a harness script given to pytest (round 2's name rule); a fixture module
    or a shell file given a runner; the manifest test run whole; tests_capped not reported."""
    root = union_root(tmp_path / "root")
    rw = tmp_path / "graph.out"
    rw.write_text(ripwire_output(UNION_ROWS, attrs='tests_capped="2"'))
    lists = {}
    for runner in ("pytest", "python3", "bash"):
        r = gate_union(root, "--runner", runner, "--graph", "yes", "--ripwire", rw, "scripts/x.py")
        assert (r.returncode, r.stderr) == (0, ""), r.stderr
        lists[runner] = r.stdout.splitlines()
    assert lists == {"pytest": ["tests/red/test_nested.py", "tests/test_code.py", "tests/test_comment.py",
                                "tests/test_linked.py"],
                     "python3": ["harness-ports/tests/test_script.py"], "bash": ["harness-ports/tests/test_shell.sh"]}
    r = gate_union(root, "--why", "--graph", "yes", "--ripwire", rw, "scripts/x.py")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == [
        "run list 6 of union 11: pytest 4 · python3 1 · bash 1 · not run 5",
        "harness-ports/tests/check.sh  ripwire · " + NOT_HARNESS,
        "harness-ports/tests/fixtures/data.txt  gate_files · " + NOT_HARNESS,
        "harness-ports/tests/run.sh  gate_files · " + NOT_HARNESS,
        "harness-ports/tests/test_script.py  gate_files · python3",
        "harness-ports/tests/test_shell.sh  gate_files · bash",
        "tests/fixtures/make_x.py  ripwire · " + NOT_TEST,
        "tests/red/test_nested.py  gate_files · pytest",
        "tests/test_code.py  gate_files+ripwire · pytest",
        "tests/test_comment.py  gate_files · pytest",
        "tests/test_linked.py  ripwire · pytest",
        "tests/test_vendored_manifest.py  gate_files · " + HEAVY_LINE,
        "tests/test_gone.py  ripwire, left out: the file is gone (a stale index)",
        "gate_files 8 · ripwire 4 · ripwire untested blast radius: 1 symbols (1 shown) · ripwire capped its test list "
        "(tests_capped=2): the union may miss tests"]
    for line in r.stdout.splitlines()[1:12]:           # the oracle agrees with every row's runner
        path, rest = line.split("  ", 1)
        assert rest.endswith(" · " + runner_expected(path)) if runner_expected(path) else " · not run: " in rest, line


@pytest.mark.parametrize("mode, max_files, rc, tail", [
    ("run", 5, 1, " · REFUSED: mode=run runs at most max_files=5 files; pass max_files=6 to run these 6"),
    ("plan", 5, 0, " · over max_files=5: mode=run would refuse it; pass max_files=6 to run it"),
    ("run", 6, 0, ""),
], ids=["run-over", "plan-over", "run-at-bound"])
def test_gate_union_refuses_a_run_list_wider_than_max_files(tmp_path, mode, max_files, rc, tail):
    """F-2: mode=run refuses a run list over the bound and names the count; plan mode says it would. Mutants: no bound
    (run-over exits 0); the bound checked with >= (run-at-bound refused); the refusal in plan mode too."""
    root = union_root(tmp_path / "root")
    rw = tmp_path / "graph.out"
    rw.write_text(ripwire_output(UNION_ROWS))
    r = gate_union(root, "--why", "--mode", mode, "--max-files", max_files, "--graph", "yes", "--ripwire", rw,
                   "scripts/x.py")
    assert r.returncode == rc, r.stdout + r.stderr
    assert r.stdout.splitlines()[0] == "run list 6 of union 11: pytest 4 · python3 1 · bash 1 · not run 5" + tail


@pytest.mark.parametrize("path, tail", [
    ("scripts/nothing.py", "run list 0 of union 0: pytest 0 · python3 0 · bash 0 · not run 0 · NOTHING TO RUN: no test "
                           "file names these paths"),
    ("scripts/y.py", "run list 0 of union 1: pytest 0 · python3 0 · bash 0 · not run 1 · NOTHING TO RUN: no union "
                     "file has a runner (see each file's reason)"),
], ids=["nothing-names-it", "nothing-runnable"])
def test_gate_union_fails_when_nothing_runs(tmp_path, path, tail):
    """A gate with nothing to run is no green. Mutant: an empty run list exits 0."""
    root = union_root(tmp_path / "root")
    (root / "harness-ports" / "tests" / "fixtures" / "y.txt").write_text("scripts/y.py\n")   # gate_files lists it
    (root / "tests" / "test_other.py").write_text("nothing\n")
    r = gate_union(root, "--why", "--graph", "no", path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert r.stdout.splitlines()[0] == tail


@pytest.mark.parametrize("text, why", [
    (ripwire_output(["tests/test_code.py"]) * 2, "2 <test-gate> elements"),
    (ripwire_output(["tests/test_code.py"], attrs='tests_capped="0" tests_capped="5"'),
     "attribute(s) given twice: tests_capped"),
], ids=["two-elements", "repeated-attribute"])
def test_gate_union_refuses_an_ambiguous_ripwire_output(tmp_path, text, why):
    """AF-AP-41: never read last-wins. Mutants: the element count check removed; the repeated-attribute check
    removed (each exits 0)."""
    root = union_root(tmp_path / "root")
    rw = tmp_path / "graph.out"
    rw.write_text(text)
    r = gate_union(root, "--graph", "yes", "--ripwire", rw, "scripts/x.py")
    assert (r.returncode, r.stdout) == (2, ""), r.stdout + r.stderr
    assert "ambiguous ripwire output: " + why in r.stderr


def test_gate_union_without_an_answer_from_ripwire_says_so(tmp_path):
    """ripwire unmapped (its wrapper's missing line) or failed: the union is gate_files' list, and the summary says
    why. With graph=no the file is never read; graph=yes with no file is a usage error. Mutant: the no-answer note
    dropped (the list reads as if ripwire had agreed)."""
    root = union_root(tmp_path / "root")
    rw = tmp_path / "graph.out"
    rw.write_text("ripwire_review: /nonexistent/ripwire %s (pinned install)\n" % MISSING_TEXT)
    note = "ripwire gave no <test-gate> element (unmapped or failed): the union is gate_files' list"
    r = gate_union(root, "--graph", "yes", "--ripwire", rw, "scripts/x.py")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["tests/red/test_nested.py", "tests/test_code.py", "tests/test_comment.py"]
    r = gate_union(root, "--why", "--graph", "yes", "--ripwire", rw, "scripts/x.py")
    assert r.stdout.splitlines()[0] == "run list 5 of union 8: pytest 3 · python3 1 · bash 1 · not run 3"
    assert r.stdout.splitlines()[-1] == "gate_files 8 · ripwire no answer · " + note
    r = gate_union(root, "--why", "--graph", "no", "--ripwire", tmp_path / "absent.out", "scripts/x.py")
    assert r.returncode == 0 and r.stdout.splitlines()[-1] == "gate_files 8 · ripwire not run (graph=no)", r.stdout
    r = gate_union(root, "--graph", "yes", "--ripwire", tmp_path / "absent.out", "scripts/x.py")
    assert r.returncode == 2 and "--graph yes needs --ripwire FILE" in r.stderr


def test_lint_files_counts_only_the_hits_a_file_adds(tmp_path):
    """lint_delta.py's own rule (imported) over exactly the given files. Mutants: the HEAD version not subtracted (the
    old hit counts as new); an untracked file compared with itself (its hit vanishes); exit 0 with a NEW hit."""
    repo = make_tree(tmp_path / "r")
    (repo / "old.py").write_text("import os\n")
    git(repo, "add", "old.py")
    git(repo, "commit", "-q", "--no-verify", "-m", "two")
    (repo / "old.py").write_text("import os\nimport sys\n")          # one hit kept, one added
    (repo / "new.py").write_text("import json\n")                    # untracked: its hit is new
    (repo / "clean.py").write_text("X = 1\n")
    argv = [PY, str(LINT_FILES), "--root", str(repo)]
    r = subprocess.run(argv + ["old.py", "new.py", "clean.py", "a.txt", "gone.py", "../x.py"], cwd=str(repo),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1, r.stdout + r.stderr
    assert r.stdout.splitlines() == [
        "lint_files (worktree vs HEAD %s, the given files): 3 .py linted, 2 NEW pyflakes hit(s), 0 removed"
        % git(repo, "rev-parse", "HEAD")[:12],
        "  NEW  new.py: 'json' imported but unused  (untracked: every hit is new)",
        "  NEW  old.py: 'sys' imported but unused",
        "  skipped  a.txt (not a .py file)",
        "  skipped  gone.py (absent)",
        "  skipped  ../x.py (outside the root)"]
    (repo / "old.py").write_text("X = 2\n")
    r = subprocess.run(argv + ["old.py", "clean.py"], cwd=str(repo), capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.splitlines()[0].endswith(": 2 .py linted, 0 NEW pyflakes hit(s), 1 removed")


# ---------- round 2: ripwire and sentrux in the real stacks (items 1-3) ----------

def test_every_ripwire_and_sentrux_step_reads_unmapped_on_its_wrappers_missing_line():
    """Item 3: set on every ripwire and sentrux step. The oracle is each wrapper's own missing-binary line, read from
    its source. Mutant: unmapped_if deleted from impact's ripwire step (nothing else runs it on CI)."""
    mod = load_stack("ls_b9_stack_registry")
    _tools, stacks = mod.load_registry(str(ROOT / "scripts" / "stacks.toml"))
    missing = {}
    for tool in ("ripwire", "sentrux"):
        src = (ROOT / "scripts" / ("%s_review.sh" % tool)).read_text()
        [missing[tool]] = re.findall(r'echo "(%s_review: \$BIN missing[^"]*)"; exit 0' % tool, src)
    seen = []
    for label, stack in stacks.items():
        for step in stack.steps:
            words = [e[1] for e in step.elems if e[0] in ("lit", "tmpl")]
            tool = next((t for t in ("ripwire", "sentrux") if "scripts/%s_review.sh" % t in words), None)
            if tool is not None:
                seen.append("%s.%s" % (label, step.id))
                assert step.tool == tool and step.unmapped_if and step.unmapped_if in missing[tool], (label, step.id)
    assert sorted(seen) == ["gate.graph", "impact.ripwire", "review.ripwire", "review.sentrux"]


def test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing(tmp_path):
    """The real review and gate stacks with RIPWIRE_BIN and SENTRUX_BIN pointed at missing paths (runs anywhere, CI
    included). Mutants: unmapped_if deleted from review's ripwire step or gate's graph step (each reads ok); review's
    sentrux step made required (review mode=check exits 1)."""
    def go(sub, *args):
        return subprocess.run([PY, str(STACK), "--tree", str(ROOT), "--log-dir", str(tmp_path / sub / "log"), *args],
                              cwd=str(ROOT), capture_output=True, text=True, timeout=300,
                              env={**os.environ, **MISSING_BINS})

    def steps_of(sub):
        return {s["id"]: s for s in records(tmp_path / sub / "log")[-1]["steps"]}

    r = go("a", "review", "mode=check")
    assert r.returncode == 0, r.stdout + r.stderr
    assert [(s["id"], s["status"], s["rc"]) for s in steps_of("a").values()] == [("sentrux", "unmapped", 0)]
    assert "## sentrux · unmapped — sentrux unavailable (not required)\n" in r.stdout
    assert "sentrux_review: %s %s (pinned install)" % (MISSING_BINS["SENTRUX_BIN"], MISSING_TEXT) in r.stdout

    r = go("b", "review", "files=scripts/gate_union.py")
    assert r.returncode == 1, r.stdout + r.stderr
    assert {k: s["status"] for k, s in steps_of("b").items()} == {"sentrux": "unmapped", "ripwire": "unmapped",
                                                                   "lint": "ok", "ap": "ok"}
    assert " · exit 1 — required, not ok: ripwire\n" in r.stdout and "## ripwire · unmapped — ripwire unavailable\n" in r.stdout
    assert "ripwire_review: %s %s (pinned install)" % (MISSING_BINS["RIPWIRE_BIN"], MISSING_TEXT) in r.stdout

    r = go("c", "gate", "paths=scripts/report_lint.py")
    assert r.returncode == 1, r.stdout + r.stderr
    steps = steps_of("c")
    assert steps["graph"]["status"] == "unmapped" and "## graph · unmapped — ripwire unavailable\n" in r.stdout
    union = Path(steps["union"]["out"]).read_text().split("--- stderr ---")[0].split()
    assert union == [f for f in Path(steps["tests"]["out"]).read_text().split() if runner_expected(f) == "pytest"]
    assert "ripwire no answer" in Path(steps["sources"]["out"]).read_text()


@NEEDS_RIPWIRE
def test_gate_with_the_graph_unites_gate_files_and_ripwires_tests_on_this_tree(tmp_path):
    """The real gate stack with real ripwire (sandbox), over two paths: the oracle is ripwire's own element (its
    changed= is the number of paths, sent as ONE comma-joined argument) and its <t> rows, and gate_files' list.
    bounds.py is imported by tests/test_governance_bounds.py, which never names its path: only ripwire links it.
    Mutants: {paths,} spliced as {paths*} (ripwire keeps the last --test-gate flag: changed="1", the bounds test
    lost); the union step given --graph no (ripwire's tests left out)."""
    r = real(tmp_path, "gate", "paths=src/agent_factory/governance/bounds.py,scripts/gate_union.py", timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    steps = {s["id"]: s for s in records(tmp_path / "log")[-1]["steps"]}
    assert sorted(steps) == ["graph", "setid", "sources", "tests", "union", "union_py", "union_sh", "why"]
    assert steps["graph"]["status"] == "ok" and steps["graph"]["rc"] in (0, 4)
    [(attrs, body)] = re.findall(r"<test-gate ([^>]*)>(.*?)</test-gate>", Path(steps["graph"]["out"]).read_text(), re.S)
    assert re.search(r'(^| )changed="2"( |$)', attrs), attrs
    linked = {p for p in re.findall(r'<t p="([^"]+)"', body) if (ROOT / p).is_file()}
    named = set(Path(steps["tests"]["out"]).read_text().split())
    union = Path(steps["union"]["out"]).read_text().split("--- stderr ---")[0].split()
    assert union == sorted(p for p in named | linked if runner_expected(p) == "pytest")
    assert "tests/test_governance_bounds.py" in set(union) - named
    assert "tests/test_governance_bounds.py  ripwire · pytest\n" in Path(steps["sources"]["out"]).read_text()


# ---------- round 2: {tmp} (item 4, D12) ----------

OUTSIDE_TEST = '''import subprocess


def test_tmp_path_lies_outside_every_git_work_tree(tmp_path):
    """names scripts/thing.py"""
    r = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    assert r.returncode != 0, "tmp_path %s lies inside the work tree %s" % (tmp_path, r.stdout.strip())
'''


GATE_SCRIPTS = ("gate_files.py", "gate_union.py", "pc_suite.sh", "test_summary.sh")


def gate_tree(tmp_path, files):
    """A temporary repository holding the gate stack's real scripts (copied byte for byte), scripts/thing.py (the change
    under gate) and `files` (path: text)."""
    tree = make_tree(tmp_path / "t")
    (tree / "scripts").mkdir()
    for name in GATE_SCRIPTS:
        shutil.copy2(ROOT / "scripts" / name, tree / "scripts" / name)
    (tree / "scripts" / "thing.py").write_text("X = 1\n")
    for rel, text in files.items():
        (tree / rel).parent.mkdir(parents=True, exist_ok=True)
        (tree / rel).write_text(text)
    return tree


def run_gate(tmp_path, tree, *args, registry_text=None):
    """The real registry's gate stack over scripts/thing.py, graph=no (no ripwire here); the log dir lies inside the
    tree, as the default .jev/stacks/ does."""
    reg = tmp_path / "stacks.toml"
    reg.write_text((ROOT / "scripts" / "stacks.toml").read_text() if registry_text is None else registry_text)
    return run(tmp_path, tree, reg, "gate", "paths=scripts/thing.py", "graph=no", *args, timeout=300,
               log_dir=tree / ".jev" / "stacks")


def header_of(stdout):
    """The print's header lines: everything before the first section."""
    return stdout.split("\n\n")[0].splitlines()


@pytest.mark.parametrize("round1", [False, True], ids=["registry", "round-1-run-dir"])
def test_the_gates_run_step_gives_pytest_a_basetemp_outside_every_work_tree(tmp_path, round1):
    """D12, with the real registry's gate stack in a temporary repository that holds the gate's real scripts (copied
    byte for byte) and one test that needs its tmp_path outside every git work tree. The log dir lies inside the tree,
    as the default .jev/stacks/ does. The red control is round 1's form of the run step, --basetemp={run}/bt.
    Mutant: the registry's run step given --basetemp={run}/bt again (the `registry` case goes red)."""
    tree = gate_tree(tmp_path, {"tests/test_outside.py": OUTSIDE_TEST})
    text = (ROOT / "scripts" / "stacks.toml").read_text()
    if round1:
        assert text.count('"--basetemp={tmp}/bt"') == 1
        text = text.replace('"--basetemp={tmp}/bt"', '"--basetemp={run}/bt"')
    verdict = 1 if round1 else 0
    r = run_gate(tmp_path, tree, "mode=run", "runs=1", registry_text=text)
    assert r.returncode == verdict, r.stdout + r.stderr
    rec = records(tree / ".jev" / "stacks")[-1]
    steps = {s["id"]: s for s in rec["steps"]}
    assert Path(steps["union"]["out"]).read_text() == "tests/test_outside.py\n"
    out = Path(steps["run"]["out"]).read_text()
    tmp_lines = [line for line in r.stdout.splitlines() if line.startswith("tmp ")]
    if verdict == 0:
        assert "pytest-summary: 1 passed" in out, out
        assert tmp_lines == ["tmp /tmp/stack-%s · removed after the run" % rec["run"]]
        assert not os.path.exists("/tmp/stack-" + rec["run"])
    else:
        assert "lies inside the work tree %s" % tree in out and "pytest-summary: 1 failed" in out, out
        assert tmp_lines == []


# ---------- round 3: F-1, every file with its own runner; F-2, the width bound; F-3, the counts in the header ----------

PASSING_TEST = '"""A pytest test that names scripts/thing.py."""\n\n\ndef test_the_rest_holds():\n    assert True\n'
GUARDED = ('"""A harness script that names scripts/thing.py; its checks sit under __main__ (pytest collects nothing)."""\n'
           'import sys\n\n\ndef main():\n    ok = False     # the check the change broke\n'
           '    print("test_guarded: 1 check %s" % ("passed" if ok else "FAILED"))\n    return 0 if ok else 1\n\n\n'
           'if __name__ == "__main__":\n    sys.exit(main())\n')
EXITS = ('"""A harness script that names scripts/thing.py and ends in a module-level sys.exit."""\n'
         'import sys\nprint("test_exits: 1 check passed")\nsys.exit(0)\n')
COUNTS = ('"""A harness script that names scripts/thing.py; its check() counts a failure and never raises."""\n'
          'import sys\nFAIL = 0\n\n\ndef check(label, cond):\n    global FAIL\n    FAIL += 0 if cond else 1\n'
          '    print("[%s] %s" % ("PASS" if cond else "FAIL", label))\n\n\n'
          'def test_the_changed_rule():\n    check("the changed rule holds", False)\n\n\n'
          'def main():\n    test_the_changed_rule()\n    print("test_counts: %d failed" % FAIL)\n'
          '    return 1 if FAIL else 0\n\n\nif __name__ == "__main__":\n    sys.exit(main())\n')
FAILS_SH = '# a harness shell test that names scripts/thing.py\necho "test_fails: 1 check FAILED"\nexit 1\n'
FACES = {   # face: (the harness test, the gate's exit, the runner step, a line of that test's own output)
    "guarded-script": ("harness-ports/tests/test_guarded.py", GUARDED, 1, "scripts", "test_guarded: 1 check FAILED"),
    "module-exit": ("harness-ports/tests/test_exits.py", EXITS, 0, "scripts", "test_exits: 1 check passed"),
    "counting-check": ("harness-ports/tests/test_counts.py", COUNTS, 1, "scripts", "test_counts: 1 failed"),
    "shell-test": ("harness-ports/tests/test_fails.sh", FAILS_SH, 1, "shells", "test_fails: 1 check FAILED"),
}


@pytest.mark.parametrize("face", sorted(FACES))
def test_gate_runs_each_harness_test_with_its_own_runner(tmp_path, face):
    """F-1 (VERIFY-LS-B9, core-blocking), through the real registry: a change that a pytest test and one harness test
    name. Round 2 gave the harness test to pytest: a guarded script collected nothing and the gate read green over its
    failing check; a module-level sys.exit stopped the whole session, the pytest test with it; a counting check() never
    raised and read green; a shell test was named, not run, and the gate read green. Now each harness test runs with
    run-all.sh's own runner, one process per file, and its exit decides; the pytest test runs beside it; the header
    carries the counts (F-3). Mutants: harness scripts given to pytest again (round 2's name rule); the scripts step
    not required; the three runners' counts left out of the header."""
    path, text, verdict, step, line = FACES[face]
    tree = gate_tree(tmp_path, {path: text, "tests/test_other.py": PASSING_TEST})
    r = run_gate(tmp_path, tree, "mode=run", "runs=1")
    assert r.returncode == verdict, r.stdout + r.stderr
    steps = {(s["id"], s.get("n")): s for s in records(tree / ".jev" / "stacks")[-1]["steps"]}
    ran = steps[(step, 1)]
    assert (ran["status"], ran["rc"]) == (("ok", 0) if verdict == 0 else ("failed", 1))
    assert ran["argv"] == [{"scripts": "python3", "shells": "bash"}[step], str(tree / path)]
    assert line in Path(ran["out"]).read_text()
    assert "pytest-summary: 1 passed" in Path(steps[("run", None)]["out"]).read_text()    # the pytest test ran too
    counts = {"scripts": "pytest 1 · python3 1 · bash 0", "shells": "pytest 1 · python3 0 · bash 1"}[step]
    assert "sources · run list 2 of union 2: %s · not run 0" % counts in header_of(r.stdout)


MARKS = '"""A harness script that names scripts/thing.py and marks that it ran."""\nopen("RAN", "a").write("x")\n'


def test_gate_run_refuses_a_run_list_wider_than_max_files(tmp_path):
    """F-2 through the real registry: mode=run over more files than max_files runs nothing, fails, and names the
    count; max_files lifts the bound. Mutant: the run steps without `needs` (they run despite the refusal)."""
    tree = gate_tree(tmp_path, {"tests/test_other.py": PASSING_TEST, "harness-ports/tests/test_marks.py": MARKS})
    r = run_gate(tmp_path, tree, "mode=run", "runs=1", "max_files=1")
    assert r.returncode == 1, r.stdout + r.stderr
    assert ("sources · run list 2 of union 2: pytest 1 · python3 1 · bash 0 · not run 0 · REFUSED: mode=run runs at "
            "most max_files=1 files; pass max_files=2 to run these 2") in header_of(r.stdout)
    steps = {(s["id"], s.get("n")): s for s in records(tree / ".jev" / "stacks")[-1]["steps"]}
    assert steps[("run", None)]["status"] == steps[("scripts", None)]["status"] == "skipped"
    assert "## scripts · SKIPPED — its prerequisite step sources failed (rc 1)" in r.stdout
    assert not (tree / "RAN").exists()
    r = run_gate(tmp_path, tree, "mode=run", "runs=1", "max_files=2")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tree / "RAN").read_text() == "x"


def test_gate_with_nothing_to_run_fails_and_runs_nothing(tmp_path):
    """A change no test names: sources fails with NOTHING TO RUN; the run steps have nothing to do (not selected, not
    three more failures). Mutants: an empty run list exits 0 (a green over no test); empty_ok ignored."""
    tree = gate_tree(tmp_path, {"tests/test_other.py": "nothing named here\n"})
    r = run_gate(tmp_path, tree, "mode=run", "runs=1")
    assert r.returncode == 1, r.stdout + r.stderr
    header = header_of(r.stdout)
    assert header[0].endswith(" · exit 1 — required, not ok: sources")
    assert ("sources · run list 0 of union 0: pytest 0 · python3 0 · bash 0 · not run 0 · NOTHING TO RUN: no test file "
            "names these paths") in header
    assert ("not selected: graph (when graph=yes), setid (its input step union printed nothing), run (its input step "
            "union printed nothing), scripts (its input step union_py printed nothing), shells (its input step union_sh "
            "printed nothing)") in header


TMPUSE = '''import json, os, stat, subprocess, sys
d = sys.argv[1]
git = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
open(os.path.join(d, "scratch"), "w").write("x")
seen = {"tmp": d, "mode": oct(stat.S_IMODE(os.stat(d).st_mode)), "git_rc": git.returncode}
open("seen.json", "w").write(json.dumps(seen))
sys.exit(int(sys.argv[2]))
'''


@pytest.mark.parametrize("code", [0, 1], ids=["success", "failure"])
def test_tmp_is_a_private_dir_outside_every_work_tree_removed_after_the_run(tmp_path, code):
    """Mutants: {tmp} removed only when every step is ok (the failure case leaves it); made with the default mode."""
    tree = make_tree(tmp_path / "t")
    (tree / "tmpuse.py").write_text(TMPUSE)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "use", "argv": [PY, "tmpuse.py", "{tmp}", str(code)]}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == code, r.stdout + r.stderr
    seen = json.loads((tree / "seen.json").read_text())
    run_id = records(tmp_path / "log")[-1]["run"]
    try:
        assert seen == {"tmp": "/tmp/stack-" + run_id, "mode": "0o700", "git_rc": 128}
        assert "\ntmp /tmp/stack-%s · removed after the run\n" % run_id in r.stdout
        assert not os.path.exists(seen["tmp"])
    finally:
        shutil.rmtree(seen["tmp"], ignore_errors=True)


TMPSLEEP = ("import os, sys, time\nopen(os.path.join(sys.argv[1], 'x'), 'w').close()\n"
            "open('seen.tmp', 'w').write('%s %s' % (os.getpid(), sys.argv[1]))\nos.rename('seen.tmp', 'seen')\n"
            "time.sleep(60)\n")


def test_a_signal_to_the_runner_removes_its_tmp(tmp_path):
    """Mutant: the removal outside a `finally` (the signal ends the run before it)."""
    tree = make_tree(tmp_path / "t")
    (tree / "sleeper.py").write_text(TMPSLEEP)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "nap", "argv": [PY, "sleeper.py", "{tmp}"],
                                                      "timeout": 120}]))
    p = subprocess.Popen([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"),
                          "st"], cwd=str(tree), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    deadline = time.monotonic() + 30
    while not (tree / "seen").exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    pid, tmp = (tree / "seen").read_text().split(" ", 1)
    pid = int(pid)
    try:
        assert os.path.isfile(os.path.join(tmp, "x"))
        p.send_signal(signal.SIGTERM)
        assert p.wait(timeout=30) == 128 + signal.SIGTERM, p.stderr.read()
        assert wait_dead([pid]) == [] and not os.path.exists(tmp)
    finally:
        if alive(pid):
            os.kill(pid, signal.SIGKILL)
        if p.poll() is None:
            p.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def test_a_tmp_inside_a_git_work_tree_is_refused(tmp_path, monkeypatch, capsys):
    """Fault injection into the real main(): TMP_BASE moved inside a repository. Mutant: make_tmp without its git
    check (the step runs with a {tmp} that git takes for part of the tree)."""
    mod = load_stack("ls_b9_stack_tmp")
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "use", "argv": [PY, "mark.py", "MARKER", "{tmp}"]}]))
    monkeypatch.setattr(mod, "TMP_BASE", str(tree))
    rc = mod.main(["--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"), "st"])
    err = capsys.readouterr().err
    assert rc == 3, err
    assert "lies inside a git work tree; it must lie outside every one" in err
    assert not (tree / "MARKER").exists() and [p.name for p in tree.iterdir() if p.name.startswith("stack-")] == []
    assert records(tmp_path / "log") == []


@NEEDS_RG
def test_echo_runs_on_this_tree_and_its_output_is_reproducible(tmp_path):
    """The real echo stack twice over the same tree: the same saved code search, sorted by path."""
    outs = []
    for i in range(2):
        r = real(tmp_path / str(i), "echo", "pattern=start_new_session=True")
        assert r.returncode == 0, r.stdout + r.stderr
        steps = {s["id"]: s for s in records(tmp_path / str(i) / "log")[-1]["steps"]}
        assert sorted(steps) == ["ap", "code", "files", "registry"] and steps["ap"]["status"] == "ok"
        outs.append((steps["code"]["sha256"], Path(steps["files"]["out"]).read_text().split()))
    assert outs[0] == outs[1]
    files = outs[0][1]                 # rg --sort path: the roots in the order given, each walked in path order
    roots = ["scripts", "harness-ports", "src", "proofs", ".claude/hooks", ".github"]
    assert files == sorted(files, key=lambda f: ([f.startswith(r + "/") for r in roots].index(True), f.split("/")))
    assert "scripts/stack.py" in files


# ---------- round 4: R3-F3, R3-F1, R3-F4 (X1, X2, X3, X6), R3-F5, local ids (6b), the catalog (7) ----------

def test_handback_extract_never_takes_the_previous_rounds_epilogue(tmp_path):
    """R3-F3 (VERIFY-LS-B9 round 3), the verifier's shape with the records a real transcript holds around a call: round
    1's report, call 1 (its tool result), a 4,000-character round-1 epilogue, the resume, a short text, a 160-character
    call 2 gives no report; with a compaction between call 1 and the resume (the LS-B9 lane's own shape from round 3 to
    round 4), the text after the compaction gives none either; the control, where round 2 writes its own long text,
    picks it. Mutants: the window opened at the previous call (round 3's rule: the epilogue saved); at the first user
    record after it (the call's own tool result: the epilogue saved); at a compaction summary (the text after the
    compaction saved)."""
    round1, epilogue = "ROUND1-REPORT " * 300, "ROUND1-EPILOGUE " * 250
    assert len(epilogue) == 4000
    shapes = {"epilogue": [RESULT, text_block(epilogue), RESUME],
              "compacted": [RESULT, COMPACTED, text_block(epilogue), RESUME]}
    for name, between in shapes.items():
        blocks = [text_block(round1), call("R1 SUMMARY")] + between + [text_block("short"), call("M" * 160)]
        r, out, rep = extract(tmp_path / name, build_transcript(tmp_path / name, blocks=blocks))
        assert r.returncode == 0, (name, r.stderr)
        assert (r.stdout, rep.exists()) == ("%s\n" % out, False), name
        assert r.stderr.splitlines()[1] == NO_LONG.rstrip("\n"), name
    round2 = "ROUND2-REPORT " * 200
    r, out, rep = extract(tmp_path / "control", build_transcript(tmp_path / "control", blocks=[
        text_block(round1), call("R1 SUMMARY"), RESULT, text_block(epilogue), RESUME, text_block(round2),
        call("M" * 160)]))
    assert r.returncode == 0 and r.stdout == "%s\n" % rep and rep.read_text() == round2, r.stderr


def test_the_gates_counts_line_stays_in_the_print_past_a_9562_character_paths_value(tmp_path):
    """R3-F1 (VERIFY-LS-B9 round 3): with a paths value of 9,562 characters or more the header alone passes the print
    cap, which cuts the print from its end; the headline line now comes right after the tree line, before params:, so
    the counts stay. Mutant: the headline lines after params: again (round 3's order: the counts line is cut)."""
    tree = gate_tree(tmp_path, {"tests/test_other.py": PASSING_TEST})
    value = ",".join(["scripts/thing.py"] + ["scripts/padding_%03d_%s.py" % (i, "p" * 30) for i in range(200)])
    assert len(value) >= 9562
    reg = tmp_path / "stacks.toml"
    reg.write_text((ROOT / "scripts" / "stacks.toml").read_text())
    r = run(tmp_path, tree, reg, "gate", "paths=" + value, "graph=no", timeout=300, log_dir=tree / ".jev" / "stacks")
    assert r.returncode == 0, r.stdout[:3000] + r.stderr
    assert len(r.stdout) <= 9000 and "… the print is cut at 9,000 characters" in r.stdout
    assert r.stdout.splitlines()[2] == "sources · run list 1 of union 1: pytest 1 · python3 0 · bash 0 · not run 0"


DEAF_CHILD = ('import os, signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\n'
              'open("child.tmp", "w").write(str(os.getpid()))\nos.replace("child.tmp", "child")\n'
              'while True:\n    time.sleep(0.05)\n')
DEAF_LEAVER = ('import os, subprocess, sys, time\nsubprocess.Popen([sys.executable, "deafchild.py"])\n'
               'while not os.path.exists("child"):     # the child ignores SIGTERM before the leader exits\n'
               '    time.sleep(0.01)\n')


def test_a_stray_that_ignores_sigterm_is_killed_all_the_same(tmp_path):
    """R3-F4 X1: the stray kill after a leader exits is a SIGKILL, so a child that ignores SIGTERM dies too. Mutant X1:
    the stray kill sends SIGTERM (the child lives on after the run)."""
    tree = make_tree(tmp_path / "t")
    (tree / "deafchild.py").write_text(DEAF_CHILD)
    (tree / "deafleaver.py").write_text(DEAF_LEAVER)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "leave", "argv": [PY, "deafleaver.py"]}]))
    r = run(tmp_path, tree, reg, "st")
    pid = int((tree / "child").read_text())
    try:
        assert r.returncode == 0, r.stdout + r.stderr
        assert wait_dead([pid]) == []
        [s] = records(tmp_path / "log")[-1]["steps"]
        assert (s["status"], s["strays_killed"]) == ("ok", True)
    finally:
        if alive(pid):
            os.kill(pid, signal.SIGKILL)


def test_a_headline_longer_than_headline_max_is_cut_with_an_ellipsis(tmp_path):
    """R3-F4 X2: the header keeps 500 characters of a headline and marks the cut. Mutant X2: no cut at HEADLINE_MAX
    (all 600 characters in the header)."""
    tree = make_tree(tmp_path / "t")
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "hl", "argv": [PY, "-c", "print('H' * 600)"],
                                                      "headline": True}]))
    r = run(tmp_path, tree, reg, "st")
    assert r.returncode == 0, r.stderr
    assert "hl · " + "H" * 500 + "…" in header_of(r.stdout)


# chr(), never a typed escape: the tools turn a typed backslash-u escape into the character itself (env-tool-quirks)
HEADCTL = ("import sys\nline = 'COUNTS ok' + chr(13) + 'FORGED exit 0' + chr(27) + '[2K' + chr(0x85) + chr(0x7f) + "
           "chr(0x2028) + chr(9) + '|'\nsys.stdout.buffer.write(line.encode('utf-8') + b'\\n')\n")


def test_a_headlines_control_characters_are_escaped_in_the_header(tmp_path):
    """R3-F5: a CR, an ESC, a C1 NEL, DEL, U+2028 and a TAB in a headline's first line reach the header as escapes,
    never raw (a raw CR lets the text after it overwrite the header line in a terminal). The print is read as bytes:
    text mode would turn a raw CR into a newline. Mutant: the first line copied raw."""
    tree = make_tree(tmp_path / "t")
    (tree / "hl.py").write_text(HEADCTL)
    reg = registry(tmp_path, stack_toml("st", None, [{"id": "hl", "argv": [PY, "hl.py"], "headline": True}]))
    r = subprocess.run([PY, str(STACK), "--tree", str(tree), "--registry", str(reg), "--log-dir", str(tmp_path / "log"),
                        "st"], cwd=str(tree), capture_output=True, timeout=120)
    assert r.returncode == 0, r.stderr
    header = r.stdout.decode("utf-8").split("\n\n")[0]
    assert "\nhl · COUNTS ok\\rFORGED exit 0\\x1b[2K\\x85\\x7f\\" + "u2028\\t|\n" in header
    assert not any(c in header for c in (chr(13), chr(27), chr(0x85), chr(0x7f), chr(0x2028), chr(9)))


RUN_ALL = ('#!/usr/bin/env bash\n# the harness suite runner; it checks scripts/thing.py\n'
           'python3 scripts/thing.py && echo "run-all: ALL SUITES PASSED" && echo x >> RAN_ALL\n')


def test_a_gate_on_a_path_only_run_all_names_runs_run_all_with_bash(tmp_path):
    """R3-F4 X3: a path only run-all.sh names (as harness-ports/bin/build-roles.py is named at run-all.sh:72) gets
    run-all.sh, run with bash as CI runs it, never NOTHING TO RUN. Mutant X3: run-all.sh no longer routed to bash (the
    gate reads NOTHING TO RUN, a false red)."""
    tree = gate_tree(tmp_path, {"harness-ports/tests/run-all.sh": RUN_ALL})
    r = run_gate(tmp_path, tree, "mode=run", "runs=1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "sources · run list 1 of union 1: pytest 0 · python3 0 · bash 1 · not run 0" in header_of(r.stdout)
    steps = {(s["id"], s.get("n")): s for s in records(tree / ".jev" / "stacks")[-1]["steps"]}
    assert steps[("shells", 1)]["argv"] == ["bash", str(tree / "harness-ports/tests/run-all.sh")]
    assert steps[("shells", 1)]["status"] == "ok" and (tree / "RAN_ALL").read_text() == "x\n"


MARKS_SH = '# a harness shell test that names scripts/thing.py and marks that it ran\necho x >> RAN_SH\n'


def test_a_refused_run_runs_no_shell_test(tmp_path):
    """R3-F4 X6: a REFUSED run list (wider than max_files) that holds a shell test runs none of it; with the bound
    lifted it runs. Mutant X6: the shells step without needs (it runs the shell test despite the refusal)."""
    tree = gate_tree(tmp_path, {"tests/test_other.py": PASSING_TEST, "harness-ports/tests/test_marks.sh": MARKS_SH})
    r = run_gate(tmp_path, tree, "mode=run", "runs=1", "max_files=1")
    assert r.returncode == 1, r.stdout + r.stderr
    assert ("sources · run list 2 of union 2: pytest 1 · python3 0 · bash 1 · not run 0 · REFUSED: mode=run runs at "
            "most max_files=1 files; pass max_files=2 to run these 2") in header_of(r.stdout)
    shells = [(s.get("n"), s["status"]) for s in records(tree / ".jev" / "stacks")[-1]["steps"] if s["id"] == "shells"]
    assert shells == [(None, "skipped")], shells
    assert "## shells · SKIPPED — its prerequisite step sources failed (rc 1)" in r.stdout
    assert not (tree / "RAN_SH").exists()
    r = run_gate(tmp_path, tree, "mode=run", "runs=1", "max_files=2")
    assert r.returncode == 0 and (tree / "RAN_SH").read_text() == "x\n", r.stdout + r.stderr


def origin_tree(tmp_path):
    """A repository with an origin (a bare repository beside it): its first commit pushed, a second one local."""
    bare = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", str(bare))
    tree = make_tree(tmp_path / "t")
    git(tree, "remote", "add", "origin", str(bare))
    git(tree, "push", "-q", "origin", "main")
    (tree / "c.txt").write_text("c\n")
    git(tree, "add", "c.txt")
    git(tree, "commit", "-q", "--no-verify", "-m", "the local one")
    return tree, git(tree, "rev-parse", "origin/main"), git(tree, "rev-parse", "HEAD")


def local_ids(tree, *files):
    return subprocess.run([PY, str(HANDBACK), "--local-ids", *map(str, files)], cwd=str(tree), capture_output=True,
                          text=True, timeout=60)


def test_local_ids_lists_a_cited_local_commit_with_its_line(tmp_path):
    """Round 4 item 6b: push_clean.sh rewrites every commit of origin/<branch>..HEAD, so an id the hand-back cites from
    that range is listed with its line (a path given twice is read once); a control that cites only an origin id lists
    nothing. Mutants: the range read as every commit of HEAD (the control's origin id listed); a match on the full id
    only (the 7-character citation missed)."""
    tree, pushed, local = origin_tree(tmp_path)
    hb = tmp_path / "handback.md"
    hb.write_text("# report\nthe fix is %s, on top of %s.\nthe end\n" % (local[:7], pushed[:9]))
    r = local_ids(tree, hb, hb)
    assert r.returncode == 1, r.stdout + r.stderr
    assert r.stdout.splitlines() == [
        "local ids: 1 cited — origin/main..HEAD holds 1 local commit; push_clean.sh rewrites them, so cite each by its "
        "subject (or by its origin id after the push)",
        '%s:2: %s is local %s "the local one" · the fix is %s, on top of %s.' % (hb, local[:7], local[:12], local[:7],
                                                                                pushed[:9])]
    control = tmp_path / "control.md"
    control.write_text("on top of %s and %s\n" % (pushed[:7], pushed))
    r = local_ids(tree, control)
    assert (r.returncode, r.stdout) == (0, "local ids: none cited (origin/main..HEAD holds 1 local commit)\n")


def test_local_ids_lists_an_id_an_earlier_push_rewrote(tmp_path):
    """2026-09-29, the LS-B10 report: the lane cited d6caa37, the local id of a commit that an EARLIER push had already
    rewritten (to 164bf49), so the id sat neither in origin/<branch>..HEAD nor on origin, and the check said "none
    cited". An id that resolves to a local commit origin does not hold is listed too; a control citing the rewritten
    commit's origin id lists nothing. Mutant: the range-only check (the old id missed, exit 0)."""
    tree, pushed, local = origin_tree(tmp_path)
    git(tree, "commit", "-q", "--amend", "--no-verify", "-m", "the local one, rewritten")   # push_clean's rewrite
    new = git(tree, "rev-parse", "HEAD")
    git(tree, "push", "-q", "origin", "main")
    hb = tmp_path / "handback.md"
    hb.write_text("# report\nHEAD has since moved to %s.\n" % local[:7])
    r = local_ids(tree, hb)
    assert r.returncode == 1, r.stdout + r.stderr
    assert r.stdout.splitlines() == [
        "local ids: 1 cited — origin/main..HEAD holds 0 local commits; 1 not on origin (an id an earlier push "
        "rewrote, or another branch's): cite each by its subject or its origin id",
        '%s:2: %s is not on origin %s "the local one" · HEAD has since moved to %s.' % (hb, local[:7], local[:12],
                                                                                    local[:7])]
    control = tmp_path / "control.md"
    control.write_text("HEAD has since moved to %s, on top of %s.\n" % (new[:7], pushed[:7]))
    r = local_ids(tree, control)
    assert (r.returncode, r.stdout) == (0, "local ids: none cited (origin/main..HEAD holds 0 local commits)\n")


def test_local_ids_never_reads_a_missing_object_as_not_on_origin(tmp_path):
    """AF-AP-141: `merge-base --is-ancestor` exits 1 with `error: Could not read <id>` when the walk meets a missing
    object (measured 2026-09-29), the same code as a plain no. With a commit of origin's history gone, a cited
    dangling id is "not checked" (exit 2, naming the walk), never "not on origin". Mutant: exit 1 read as a no (the id
    listed, exit 1)."""
    tree, pushed, local = origin_tree(tmp_path)
    (tree / "d.txt").write_text("d\n")
    git(tree, "add", "d.txt")
    git(tree, "commit", "-q", "--no-verify", "-m", "the top one")
    git(tree, "push", "-q", "origin", "main")                         # origin: pushed <- local <- top
    git(tree, "checkout", "-q", "-b", "side", pushed)
    (tree / "x.txt").write_text("x\n")
    git(tree, "add", "x.txt")
    git(tree, "commit", "-q", "--no-verify", "-m", "a side one")
    side = git(tree, "rev-parse", "HEAD")
    git(tree, "checkout", "-q", "main")
    git(tree, "branch", "-q", "-D", "side")                           # side is now a dangling commit
    (tree / ".git" / "objects" / local[:2] / local[2:]).unlink()      # a commit of origin's history is gone
    hb = tmp_path / "handback.md"
    hb.write_text("the fix is %s\n" % side[:7])
    r = local_ids(tree, hb)
    assert r.returncode == 2, r.stdout + r.stderr
    assert r.stdout.startswith("local ids: not checked — git merge-base --is-ancestor %s origin/main cannot tell"
                               % side[:12]), r.stdout


def test_local_ids_says_why_when_it_cannot_check(tmp_path):
    """Not checked is never read as none cited: a detached HEAD, and a branch origin does not hold, exit 2 with the
    reason. Mutant: a git failure read as an empty range (exit 0, "none cited")."""
    tree, pushed, local = origin_tree(tmp_path)
    hb = tmp_path / "handback.md"
    hb.write_text("the fix is %s\n" % local[:7])
    git(tree, "checkout", "-q", "--detach")
    r = local_ids(tree, hb)
    assert (r.returncode, r.stdout) == (2, "local ids: not checked — HEAD is detached: there is no "
                                           "origin/<branch>..HEAD\n")
    git(tree, "checkout", "-q", "-b", "unpushed")
    r = local_ids(tree, hb)
    assert r.returncode == 2 and r.stdout.startswith(
        "local ids: not checked — git log --format=%H%x00%s origin/unpushed..HEAD -- failed: "), r.stdout


def test_harvest_lists_the_local_ids_its_handback_cites(tmp_path):
    """6b through the real registry's handback and local_ids steps (their definitions read from scripts/stacks.toml) in
    a repository with an origin: the step runs on the hand-back the extractor saved and lists the planted id, and it is
    advisory like lint_handback (the harvest exits 0 with an id listed). Mutant: the step required (the harvest exits
    1)."""
    tree, pushed, local = origin_tree(tmp_path)
    (tree / "scripts").mkdir()
    for name in ("handback_extract.py", "stale_ids.py"):
        shutil.copy2(ROOT / "scripts" / name, tree / "scripts" / name)
    harvest = tomllib.loads((ROOT / "scripts" / "stacks.toml").read_text())["stacks"]["harvest"]
    steps = [s for s in harvest["steps"] if s["id"] in ("handback", "local_ids")]
    assert [s["id"] for s in steps] == ["handback", "local_ids"]
    reg = registry(tmp_path, stack_toml("harvest", harvest["params"], steps))
    build_transcript(tmp_path / "tr", ["REPORT: the fix is %s\n" % local[:7]])
    r = run(tmp_path, tree, reg, "--transcript-root", tmp_path / "tr", "harvest", "agent=" + AGENT)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = records(tmp_path / "log")[-1]
    s = {x["id"]: x for x in rec["steps"]}["local_ids"]
    handback = tmp_path / "log" / rec["run"] / "handback.md"
    assert (s["status"], s["rc"]) == ("failed", 1)
    assert s["argv"] == ["python3", "scripts/handback_extract.py", "--local-ids", str(handback), str(handback)]
    assert '%s:1: %s is local %s "the local one"' % (handback, local[:7], local[:12]) in Path(s["out"]).read_text()
    assert "## local_ids · FAILED · rc 1 · " in r.stdout


CATALOG_HEAD = ("Stacks (scripts/stacks.toml): `python3 scripts/stack.py <label> key=value ...` runs one in one call; "
                "`python3 scripts/stack.py explain <label> ...` prints its plan and runs nothing.")
CATALOG_RATE = ("Ratings, the content stacks only (%s): `--rate <run id>=<rel>/<use>` on the next stack call, or "
                "`python3 scripts/stack.py rate <run id>=<rel>/<use>`; rel and use are 0 to 3.")


def test_catalog_is_a_heading_the_list_and_one_line_on_ratings_under_4000_characters(tmp_path):
    """Round 4 item 7's text from the real registry: one heading line, `list`'s output as it is, one line on ratings
    that names the rated (content) stacks; under 4,000 characters (AF-AP-183); it writes no record. Mutants: the
    ratings line naming every stack (an unrated stack's run is refused a rating); the list left out."""
    r = real(tmp_path, "catalog")
    listed = real(tmp_path, "list")
    assert (r.returncode, r.stderr, listed.returncode) == (0, "", 0)
    lines = r.stdout.split("\n")
    assert lines[0] == CATALOG_HEAD
    assert "\n".join(lines[1:-2]) + "\n" == listed.stdout
    assert lines[-2] == CATALOG_RATE % "ctx, impact, find, echo, review, cbm, why, locate, fix-echo"
    assert lines[-1] == "" and len(r.stdout) < 4000
    assert not (tmp_path / "log").exists()


def test_catalog_drops_whole_stacks_to_stay_under_4000_characters(tmp_path):
    """The cap holds for any registry: sixty stacks with a 200-character note each are cut to whole stacks, a line
    naming how many are not shown, and the ratings line. Mutant: no cap (all sixty, about 15,000 characters)."""
    note = 'outward = false\nnotes = ["%s"]\n' % ("n" * 200)
    reg = registry(tmp_path, *[stack_toml("s%02d" % i, None, [{"id": "a", "argv": ["true"]}]).replace(
        "outward = false\n", note) for i in range(60)])
    r = subprocess.run([PY, str(STACK), "--registry", str(reg), "catalog"], capture_output=True, text=True, timeout=60)
    assert (r.returncode, r.stderr) == (0, "")
    assert len(r.stdout) < 4000
    lines = r.stdout.splitlines()
    shown = [ln for ln in lines if re.fullmatch(r"s\d\d  \(no parameters\)  — a test stack", ln)]
    assert len(shown) == sum(ln == "  note: " + "n" * 200 for ln in lines) > 0
    m = re.fullmatch(r"… (\d+) of 60 stacks not shown \(this catalog stays under 4,000 characters\): "
                     r"python3 scripts/stack\.py list", lines[-2])
    assert m and int(m.group(1)) + len(shown) == 60, lines[-2]
    assert lines[0] == CATALOG_HEAD and lines[-1] == CATALOG_RATE % "none"


def test_catalog_cuts_even_its_ratings_line_to_stay_under_4000_characters(tmp_path):
    """The last resort: 200 rated stacks make the ratings line alone pass 4,000 characters, so with every stack dropped
    the text is still over; it is cut to 3,999 characters, ending in an ellipsis. Mutant: no last-resort cut (4,000
    characters or more)."""
    (tmp_path / "r").mkdir()
    reg = registry(tmp_path / "r", *[stack_toml("r%03d-%s" % (i, "x" * 19), None, [{"id": "a", "argv": ["true"]}],
                                                rated=True) for i in range(200)])
    r = subprocess.run([PY, str(STACK), "--registry", str(reg), "catalog"], capture_output=True, text=True, timeout=60)
    assert (r.returncode, r.stderr) == (0, "")
    assert len(r.stdout) == 3999 and r.stdout.startswith(CATALOG_HEAD + "\n… 200 of 200 stacks not shown")
    assert r.stdout.endswith("…\n")


@pytest.mark.parametrize("args, text, line", [
    ([], "version = 2\n" + GOOD_STACK, "stacks: no catalog (registry: version: must be 1 (found 2))\n"),
    ([], None, "stacks: no catalog (registry {REG}: No such file or directory)\n"),
    (["x"], "version = 1\n" + GOOD_STACK, "stacks: no catalog (catalog takes no argument)\n"),
], ids=["bad-registry", "no-registry", "an-argument"])
def test_catalog_that_cannot_be_built_prints_one_line_naming_why_and_exits_0(tmp_path, args, text, line):
    """Fail loud, never silent, and never a failing exit: the SessionStart hook's reader gets ONE line naming why.
    Mutant: the registry refusal left to main's handler (stderr and exit 3: the hook's reader sees nothing)."""
    reg = tmp_path / "stacks.toml"
    if text is not None:
        reg.write_text(text)
    r = subprocess.run([PY, str(STACK), "--registry", str(reg), "catalog", *args], capture_output=True, text=True,
                       timeout=60)
    assert (r.returncode, r.stdout, r.stderr) == (0, line.replace("{REG}", str(reg)), "")


def test_catalog_turns_an_unexpected_error_into_one_line(tmp_path, monkeypatch):
    """A defect inside the catalog's own code is one line too, never a traceback. Mutant: only a Refusal caught."""
    mod = load_stack("stack_catalog_fault")

    def boom(stack):
        raise RuntimeError("boom\nsecond line")

    monkeypatch.setattr(mod, "list_lines", boom)
    assert mod.catalog(str(ROOT / "scripts" / "stacks.toml")) == "stacks: no catalog (RuntimeError: boom second line)\n"


# ---------- task #385 (LS-B12): five more labels ----------
# cbm, changes, why, locate and fix-echo (D-113, D-114; tasks/briefs/labeling/LS-B12-brief.md). Every step's interface
# was measured by hand on this tree on 2026-09-30 (the lane's report): the pins below are those measured forms.

REGISTRY = ROOT / "scripts" / "stacks.toml"
NEEDS_NODE = pytest.mark.skipif(shutil.which("node") is None,
                                reason="node is not installed: the changes stack's steps run node .gitnexus/run.cjs")


def bin_dir(path, **programs):
    """A PATH directory that holds only the named programs, each a symlink to the real one."""
    path.mkdir(parents=True)
    for name, target in programs.items():
        (path / name).symlink_to(target)
    return path


def run_env(tmp_path, tree, env, *args, timeout=300):
    """The committed registry run on a tree, with these environment variables changed for the runner and its steps."""
    return subprocess.run([PY, str(STACK), "--tree", str(tree), "--log-dir", str(tmp_path / "log"), *map(str, args)],
                          cwd=str(tree), capture_output=True, text=True, timeout=timeout, env={**os.environ, **env})


def cbm_binary():
    """The codebase-memory binary by the registry's own rule ([tools]: ~/.local/bin, then the PATH), or None.
    os.path.exists, not Path.exists: a /root path raises PermissionError from Path.exists for a non-root user (CI)."""
    for c in (os.path.expanduser("~/.local/bin/codebase-memory-mcp"), shutil.which("codebase-memory-mcp")):
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def gitnexus_runner_source():
    """The real GitNexus runner: this tree's .gitnexus/run.cjs (written by `gitnexus analyze`), else the installed
    package's hooks/claude/resolve-analyze-cmd.cjs, the file analyze copies there (its dist/cli/ai-context.js); None
    where neither exists (CI)."""
    cands = [ROOT / ".gitnexus" / "run.cjs"]
    gn = shutil.which("gitnexus")
    if gn:
        cands.append(Path(os.path.realpath(gn)).parents[2] / "hooks" / "claude" / "resolve-analyze-cmd.cjs")
    return next((c for c in cands if os.path.isfile(c)), None)


UNMAPPED_385 = {   # step: (unmapped_if, tool), the text its tool prints where it cannot answer (measured 2026-09-30)
    # LS-B12-R1: each is a text no repo text in that step's output can hold (the item-3 sweep and item 1); changes'
    # scope steps carry none (detect-changes prints headings verbatim): their probe reads the runner's launch failure
    "cbm.search": ('{"error":"project not found', "codebase-memory"),
    "changes.probe": ("gitnexus runner: could not launch", "gitnexus"),
    "changes.all": (None, None),
    "changes.staged": (None, None),
    "changes.unstaged": (None, None),
    "changes.compare": (None, None),
    "why.file": (None, None),
    "why.function": (None, None),
    "locate.pack": (None, None),
    "fix-echo.sites": ('"ranking": "no instrument answered', "rg-and-graft"),
}


def test_the_committed_registry_loads_with_fourteen_stacks_and_the_catalog_shows_all(tmp_path):
    """Items 6 and 8: the committed registry loads with wave 1's nine stacks, then task #385's five; the new ones are
    rated as the brief says (changes is a check, like ci); each step reads unmapped on its tool's own text where it has
    one (locate has none: its registry and quirk instruments answer in every checkout, so its pack never says
    `answered: none`); the two Jev tools run in their plain order (--order lexical, --no-jev-log: KC-J1, D-077); and
    the SessionStart catalog shows all fourteen under 4,000 characters. Mutants: a new stack dropped; unmapped_if
    deleted from a step; --order lexical or --no-jev-log dropped from locate or fix-echo; changes marked rated."""
    mod = load_stack("ls_b12_registry")
    _tools, stacks = mod.load_registry(str(REGISTRY))
    assert list(stacks) == WAVE1 + NEW_LABELS
    assert {label: stacks[label].rated for label in NEW_LABELS} == {
        "cbm": True, "changes": False, "why": True, "locate": True, "fix-echo": True}
    assert {"%s.%s" % (label, st.id): (st.unmapped_if, st.tool) for label in NEW_LABELS
            for st in stacks[label].steps} == UNMAPPED_385
    for label, script in (("locate", "scripts/jev_locate.py"), ("fix-echo", "scripts/jev_echo.py")):
        [step] = stacks[label].steps
        words = [e[1] for e in step.elems if e[0] == "lit"]
        assert words[:2] == ["python3", script] and "--no-jev-log" in words, words
        assert words[words.index("--order") + 1] == "lexical", words
        assert ("--json" in words) == (label == "fix-echo"), words      # LS-B12-R1: fix-echo's marker is JSON's
    r = real(tmp_path, "catalog")
    assert r.returncode == 0 and len(r.stdout) < mod.CATALOG_CAP and "not shown" not in r.stdout, r.stdout
    assert [ln.split()[0] for ln in r.stdout.splitlines()[1:-1] if not ln.startswith(" ")] == WAVE1 + NEW_LABELS


EXPLAIN_385 = {   # case: (label, tokens, the plan)
    "cbm": ("cbm", ["q=stack runner"], """\
explain cbm — codebase-memory's graph search (project home-user-agent-factory): ranked symbols with their file and lines
tree {TREE} · HEAD {HEAD}
params: q='stack runner'
body: q {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  search: codebase-memory-mcp cli search_graph --project home-user-agent-factory --query 'stack runner' (timeout 120 s)
"""),
    "changes": ("changes", [], """\
explain changes — GitNexus detect-changes: the changed symbols and the flows they touch, for all, staged or unstaged changes or since a base
tree {TREE} · HEAD {HEAD}
params: scope=all
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  probe: node .gitnexus/run.cjs --version
group 2
  all: node .gitnexus/run.cjs detect-changes --scope all --repo . (timeout 120 s, needs probe, headline)
  staged: not selected (when scope=staged)
  unstaged: not selected (when scope=unstaged)
  compare: not selected (when scope=compare)
"""),
    "changes-staged-with-base": ("changes", ["scope=staged", "base=main"], """\
explain changes — GitNexus detect-changes: the changed symbols and the flows they touch, for all, staged or unstaged changes or since a base
tree {TREE} · HEAD {HEAD}
params: scope=staged base=main
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  probe: node .gitnexus/run.cjs --version
group 2
  all: not selected (when scope=all)
  staged: node .gitnexus/run.cjs detect-changes --scope staged --repo . (timeout 120 s, needs probe, headline)
  unstaged: not selected (when scope=unstaged)
  compare: not selected (when scope=compare)
"""),
    "changes-unstaged": ("changes", ["scope=unstaged"], """\
explain changes — GitNexus detect-changes: the changed symbols and the flows they touch, for all, staged or unstaged changes or since a base
tree {TREE} · HEAD {HEAD}
params: scope=unstaged
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  probe: node .gitnexus/run.cjs --version
group 2
  all: not selected (when scope=all)
  staged: not selected (when scope=staged)
  unstaged: node .gitnexus/run.cjs detect-changes --scope unstaged --repo . (timeout 120 s, needs probe, headline)
  compare: not selected (when scope=compare)
"""),
    "changes-compare": ("changes", ["scope=compare", "base=origin/main"], """\
explain changes — GitNexus detect-changes: the changed symbols and the flows they touch, for all, staged or unstaged changes or since a base
tree {TREE} · HEAD {HEAD}
params: scope=compare base=origin/main
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  probe: node .gitnexus/run.cjs --version
group 2
  all: not selected (when scope=all)
  staged: not selected (when scope=staged)
  unstaged: not selected (when scope=unstaged)
  compare: node .gitnexus/run.cjs detect-changes --scope compare --base-ref origin/main --repo . (timeout 120 s, needs probe, headline)
"""),
    "why": ("why", ["file=scripts/why.sh"], """\
explain why — a file's or a function's chronology: its commits, the last change's full message, the docs that name it
tree {TREE} · HEAD {HEAD}
params: file=scripts/why.sh
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  file: bash scripts/why.sh scripts/why.sh (timeout 120 s)
  function: not selected (when fn=*)
"""),
    "why-fn": ("why", ["file=scripts/stack.py", "fn=cap_lines"], """\
explain why — a file's or a function's chronology: its commits, the last change's full message, the docs that name it
tree {TREE} · HEAD {HEAD}
params: file=scripts/stack.py fn=cap_lines
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  file: not selected (when fn='')
  function: bash scripts/why.sh scripts/stack.py cap_lines (timeout 120 s)
"""),
    "locate": ("locate", ["q=a step past its timeout"], """\
explain locate — a bug text to the files, lines and records to read: jev_locate.py's eight instruments, plain lexical order
tree {TREE} · HEAD {HEAD}
params: q='a step past its timeout'
body: q {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  pack: python3 scripts/jev_locate.py --order lexical --no-jev-log 'a step past its timeout' (timeout 120 s)
"""),
    "locate-scope": ("locate", ["q=a step past its timeout", "scope=scripts"], """\
explain locate — a bug text to the files, lines and records to read: jev_locate.py's eight instruments, plain lexical order
tree {TREE} · HEAD {HEAD}
params: q='a step past its timeout' scope=scripts
body: q {BODYNOTE}
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  pack: python3 scripts/jev_locate.py --order lexical --no-jev-log --in scripts 'a step past its timeout' (timeout 120 s)
"""),
    "fix-echo": ("fix-echo", ["diff=0de29b2"], """\
explain fix-echo — after a fix: other sites like the lines it removed, from jev_echo.py (rg and graft) in the plain lexical order
tree {TREE} · HEAD {HEAD}
params: diff=0de29b2
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  sites: python3 scripts/jev_echo.py --diff 0de29b2 --order lexical --no-jev-log --json (timeout 120 s)
"""),
    "fix-echo-patch": ("fix-echo", ["diff=tasks/briefs/labeling/LS-B12.patch"], """\
explain fix-echo — after a fix: other sites like the lines it removed, from jev_echo.py (rg and graft) in the plain lexical order
tree {TREE} · HEAD {HEAD}
params: diff=tasks/briefs/labeling/LS-B12.patch
<run> = {LOG}/s-<UTC yyyymmddTHHMMSSZ>-<6 hex>
group 1
  sites: python3 scripts/jev_echo.py --diff tasks/briefs/labeling/LS-B12.patch --order lexical --no-jev-log --json (timeout 120 s)
"""),
}


@pytest.mark.parametrize("case", sorted(EXPLAIN_385))
def test_explain_of_each_task_385_stack_is_pinned(tmp_path, case):
    """Item 8: the reviewed plan of each new stack, pinned. Each argv is the form measured by hand against the
    instrument's own usage (codebase-memory's `cli` usage, detect-changes --help, why.sh's usage line, the argparse of
    jev_locate.py and jev_echo.py). Runs anywhere: explain runs nothing and writes no record. Mutants: a wrong flag;
    --base-ref passed with a scope other than compare; a headline dropped; {file} and {fn} swapped."""
    label, tokens, expected = EXPLAIN_385[case]
    r = real(tmp_path, "explain", label, *tokens)
    assert r.returncode == 0, r.stderr
    for key, value in (("{TREE}", str(ROOT)), ("{LOG}", str(tmp_path / "log")),
                       ("{HEAD}", git(ROOT, "rev-parse", "HEAD")[:12]), ("{BODYNOTE}", BODY_NOTE)):
        expected = expected.replace(key, value)
    assert r.stdout == expected
    assert not (tmp_path / "log").exists()


REFUSALS_385 = [   # (label, tokens, the exact refusal): a value outside its parameter's type
    ("cbm", ["q=--project=other"], "q=--project=other refused: '--project=other' begins with '-' (option injection)"),
    ("changes", ["scope=head"], "scope=head refused: 'head' is not one of all|staged|unstaged|compare"),
    ("changes", ["scope=compare", "base=--output=/tmp/x"],
     "base=--output=/tmp/x refused: '--output=/tmp/x' begins with '-' (option injection)"),
    ("why", ["file=../elsewhere.py"], "file=../elsewhere.py refused: '../elsewhere.py' is outside the tree {TREE}"),
    ("why", ["file=scripts/stack.py", "fn=cap-lines"],
     "fn=cap-lines refused: 'cap-lines' is not a valid symbol ([A-Za-z_][A-Za-z0-9_.:]{0,127})"),
    ("locate", ["q=who kills a step", "scope=/etc"], "scope=/etc refused: '/etc' is outside the tree {TREE}"),
    ("fix-echo", ["diff=fix.env"], "diff=fix.env refused: 'fix.env' is on the deny list (*.env)"),
    ("fix-echo", ["diff=/etc/passwd"], "diff=/etc/passwd refused: '/etc/passwd' is outside the tree {TREE}"),
]


@pytest.mark.parametrize("label, tokens, message", REFUSALS_385,
                         ids=["cbm-dash", "changes-scope", "changes-base-dash", "why-outside", "why-fn-symbol",
                              "locate-scope-outside", "fix-echo-deny-list", "fix-echo-outside"])
def test_each_new_stack_refuses_a_value_outside_its_type_before_any_step(tmp_path, label, tokens, message):
    """Item 8, a negative control per new stack: the exact refusal, exit 2, nothing run and no record written; each pins
    a parameter's TYPE. fix-echo's diff is a path: a patch path stays inside the tree and off the deny list (as text,
    jev_echo.py would open any file on the box it names). changes' base, like every type, refuses a leading '-':
    GitNexus puts the ref into `git diff` with no `--`, where --output=<file> is an option. why's fn is a symbol, and
    locate's scope a path. The positive controls are the explain cases above. Mutants: diff, file, fn or scope given
    the text type (the value passes and the step runs)."""
    r = real(tmp_path, label, *tokens)
    assert (r.returncode, r.stdout) == (2, ""), r.stdout + r.stderr
    assert r.stderr == "stack: %s\n" % message.replace("{TREE}", str(ROOT))
    assert not (tmp_path / "log").exists()


ARGV_PY = "import json, sys\nprint(json.dumps(sys.argv[1:]))\n"


def test_cbm_reads_unmapped_when_its_binary_is_missing_and_runs_the_home_copy_first(tmp_path):
    """Item 8: the real cbm stack with its binary out of reach, faked as the missing-instrument tests fake one: HOME
    names an empty directory (the [tools] entry's ~/.local/bin candidate) and PATH holds git alone. The step reads
    unmapped and the run exits 1 (runs anywhere, CI included). Then a tiny real program at
    $HOME/.local/bin/codebase-memory-mcp that prints its arguments: the [tools] entry runs it before any PATH lookup,
    with the stack's exact arguments. Mutants: the [tools] entry removed (the home copy is never found: unmapped); an
    unmapped step counted as ok (exit 0)."""
    home = tmp_path / "home"
    home.mkdir()
    env = {"HOME": str(home), "PATH": str(bin_dir(tmp_path / "bin", git=shutil.which("git")))}
    r = run_env(tmp_path, ROOT, env, "cbm", "q=stack runner")
    assert r.returncode == 1, r.stdout + r.stderr
    assert " · exit 1 — required, not ok: search\n" in r.stdout
    assert "\n## search · unmapped — codebase-memory-mcp unavailable\n" in r.stdout
    [step] = records(tmp_path / "log")[-1]["steps"]
    assert (step["id"], step["status"], step["rc"]) == ("search", "unmapped", None)
    fake = home / ".local" / "bin" / "codebase-memory-mcp"
    fake.parent.mkdir(parents=True)
    fake.write_text("#!%s\n%s" % (PY, ARGV_PY))
    fake.chmod(0o755)
    r = run_env(tmp_path, ROOT, env, "cbm", "q=stack runner")
    assert r.returncode == 0, r.stdout + r.stderr
    [step] = records(tmp_path / "log")[-1]["steps"]
    assert (step["argv"][0], step["status"]) == (str(fake), "ok")
    assert json.loads(Path(step["out"]).read_text()) == [
        "cli", "search_graph", "--project", "home-user-agent-factory", "--query", "stack runner"]


@pytest.mark.skipif(cbm_binary() is None, reason="codebase-memory-mcp is not installed (CI has none): the oracle for "
                    "cbm's unmapped_if is the binary's own not-indexed error")
def test_cbms_unmapped_if_is_the_binarys_own_not_indexed_error(tmp_path):
    """The oracle for cbm's unmapped_if is the binary itself, run as the step runs it: a project with no index exits 1
    with {"error":"project not found or not indexed",...} on stderr (measured 2026-09-30, 0.10.8). The JSON is built
    at run time (the binary's strings hold the bare text and a `{"error":"project not found"}`, not this line), so
    the oracle is a run, not the message table: a private HOME and cache, and a project name no store holds (a search
    writes nothing to any store). Mutant: a marker the binary never prints, such as `"error": "` with a space (the
    step would read FAILED).

    The rendezvous is private too (R1-F3, issue #89): the binary keeps one daemon per account in CBM_RUNTIME_DIR
    (default /tmp/cbm-daemon-<uid>), and while any daemon on another cache lives there, a call on this private cache
    fails with "the active account daemon uses a different cache directory" (measured 2026-09-30 beside the MCP
    server's daemon: 1 failed in 1.85 s). A private CBM_RUNTIME_DIR also keeps this test's own daemon from blocking
    another caller's. The directory is short and under /tmp, not tmp_path: its socket path must fit in 108 bytes
    (a 125-byte one gave "secure CLI coordination could not be created (endpoint)")."""
    home = tmp_path / "home"
    cache = home / ".cache" / "codebase-memory-mcp"
    cache.mkdir(parents=True)
    runtime = tempfile.mkdtemp(prefix="cbmr.", dir="/tmp")
    env = {**os.environ, "HOME": str(home), "CBM_CACHE_DIR": str(cache), "XDG_CACHE_HOME": str(home / ".cache"),
           "CBM_RUNTIME_DIR": runtime}
    try:
        r = subprocess.run([cbm_binary(), "cli", "search_graph", "--project", "ls-b12-r1-no-such-project", "--query",
                            "stack runner"], cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=120)
    finally:
        shutil.rmtree(runtime, ignore_errors=True)
    assert "different cache directory" not in r.stderr, r.stderr   # the rendezvous was not private
    assert r.returncode == 1 and UNMAPPED_385["cbm.search"][0] in r.stderr, r.stdout + r.stderr
    assert '{"error":"project not found or not indexed",' in r.stderr and r.stdout == ""


# LS-B12-R1 item 3: codebase-memory prints a Route node's string literal verbatim, spaces and all. Measured 2026-09-30
# (0.10.8) on a tiny tree under a private HOME: `@app.route("/project not found or not indexed")` and a
# requests.get() URL holding the same words; the search's stdout, whole. A heading becomes a Section with its spaces
# turned to dashes; a name or path that holds a space is quoted, its quotes escaped (a path holding
# `{"error":"project not found or not indexed"}` printed as `"{\"error\":\"project ...`).
CBM_ROUTES = """total: 2
search_mode: bm25
results: 2  (cols: qn label file lines rank)
  "__route__ANY__/project not found or not indexed" Route - - -15.47
  "__route__GET__http://example.com/project not found or not indexed" Route - - -14.59
has_more: false
"""


def test_cbm_reads_ok_when_a_result_quotes_the_not_indexed_text(tmp_path):
    """Item 3: a search whose rows quote the not-indexed text (the capture above, replayed by a tiny program at
    $HOME/.local/bin, the [tools] entry's first candidate) is an answer: ok, exit 0, the rows in the print. RED at
    the PIN (74285a5): its unmapped_if was the bare `project not found or not indexed`, which the rows hold: unmapped,
    exit 1. The not-indexed error is JSON on stderr and starts `{"error":"`, which the table cannot hold (a quote in a
    row is escaped). Mutant: the old unmapped_if."""
    home = tmp_path / "home"
    fake = home / ".local" / "bin" / "codebase-memory-mcp"
    fake.parent.mkdir(parents=True)
    fake.write_text("#!%s\nimport sys\nsys.stdout.write(%r)\n" % (PY, CBM_ROUTES))
    fake.chmod(0o755)
    env = {"HOME": str(home), "PATH": str(bin_dir(tmp_path / "bin", git=shutil.which("git")))}
    r = run_env(tmp_path, ROOT, env, "cbm", "q=project not found")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## search · ok · rc 0 · " in r.stdout and CBM_ROUTES.splitlines()[3] + "\n" in r.stdout, r.stdout


CBM_NOT_INDEXED = (   # the binary's stderr for a project with no index (0.10.8, measured 2026-09-30), its last 2 lines
    "hint: this command started a temporary CBM daemon. `codebase-memory-mcp daemon start` keeps one warm and removes "
    "this startup cost from every CLI command.\n"
    '{"error":"project not found or not indexed","hint":"Use list_projects to see all indexed projects, then pass it as '
    'the \\"project\\" argument.","available_projects":["home-user-i59-landing"],"count":1}\n')


def test_cbm_reads_unmapped_on_the_not_indexed_error(tmp_path):
    """The control of the test above: the binary's own not-indexed error (replayed: stderr, exit 1) reads unmapped
    through the step's unmapped_if, the run exit 1. Mutants: an unmapped_if the binary never prints (the step reads
    FAILED); the unmapped_if deleted."""
    home = tmp_path / "home"
    fake = home / ".local" / "bin" / "codebase-memory-mcp"
    fake.parent.mkdir(parents=True)
    fake.write_text("#!%s\nimport sys\nsys.stderr.write(%r)\nsys.exit(1)\n" % (PY, CBM_NOT_INDEXED))
    fake.chmod(0o755)
    env = {"HOME": str(home), "PATH": str(bin_dir(tmp_path / "bin", git=shutil.which("git")))}
    r = run_env(tmp_path, ROOT, env, "cbm", "q=stack runner")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "\n## search · unmapped — codebase-memory unavailable\n" in r.stdout, r.stdout


@NEEDS_NODE
def test_changes_reads_unmapped_in_a_tree_without_the_gitnexus_runner(tmp_path):
    """A tree `gitnexus analyze` never ran in has no .gitnexus/run.cjs: the probe reads unmapped by the runner's script
    check, each scope's step is skipped, and the run exits 1 (runs anywhere node is, CI included). Mutant: an
    unmapped step counted as ok (exit 0)."""
    tree = make_tree(tmp_path / "t")
    for scope in ("all", "staged", "unstaged", "compare"):
        r = run_env(tmp_path, tree, {"GIT_CEILING_DIRECTORIES": str(tmp_path)}, "changes", "scope=" + scope)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "\n## probe · unmapped — .gitnexus/run.cjs unavailable\n" in r.stdout, r.stdout
        assert "\n## %s · SKIPPED — its prerequisite step probe was unmapped\n" % scope in r.stdout, r.stdout


def runner_tree(tmp_path, *programs):
    """A tree holding the real GitNexus runner, and a PATH of node, git and the named programs alone."""
    tree = make_tree(tmp_path / "t")
    (tree / ".gitnexus").mkdir()
    shutil.copyfile(gitnexus_runner_source(), tree / ".gitnexus" / "run.cjs")
    found = {name: shutil.which(name) for name in ("node", "git") + programs}
    return tree, {"PATH": str(bin_dir(tmp_path / "bin", **found)), "GIT_CEILING_DIRECTORIES": str(tmp_path)}


NEEDS_RUNNER = pytest.mark.skipif(shutil.which("node") is None or gitnexus_runner_source() is None,
                                  reason="no GitNexus runner here (CI has no GitNexus): the test runs the real run.cjs")


@NEEDS_RUNNER
def test_changes_reads_unmapped_when_the_gitnexus_runner_cannot_launch(tmp_path):
    """The real runner (.gitnexus/run.cjs) with PATH holding node and git alone: it finds no gitnexus, pnpm, bunx or
    npx and prints `gitnexus runner: could not launch ...` (exit 1), which the probe (`--version`) reads as unmapped;
    each scope's step is skipped. Mutant: unmapped_if deleted from the probe (it reads FAILED)."""
    tree, env = runner_tree(tmp_path)
    for scope in ("all", "staged", "unstaged", "compare"):
        r = run_env(tmp_path, tree, env, "changes", "scope=" + scope)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "\n## probe · unmapped — gitnexus unavailable\n" in r.stdout, r.stdout
        assert "gitnexus runner: could not launch `npx`" in r.stdout
        assert "\n## %s · SKIPPED — its prerequisite step probe was unmapped\n" % scope in r.stdout, r.stdout


@NEEDS_RUNNER
@pytest.mark.skipif(shutil.which("gitnexus") is None, reason="gitnexus is not installed: the control needs it to run")
def test_changes_reads_failed_when_gitnexus_itself_fails(tmp_path):
    """The control of the test above: with gitnexus on PATH too, the runner launches it; the probe is ok, and
    detect-changes fails on its own (this tree has no index: `Repository "." not found`, exit 1). That reads FAILED,
    not unmapped. Mutant: an unmapped_if on the scope step broad enough to take gitnexus's own error."""
    tree, env = runner_tree(tmp_path, "gitnexus")
    r = run_env(tmp_path, tree, env, "changes")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "\n## probe · ok · rc 0 · " in r.stdout, r.stdout
    assert "\n## all · FAILED · rc 1 · " in r.stdout and 'Repository "." not found' in r.stdout, r.stdout
    assert "could not launch" not in r.stdout


NEEDS_GITNEXUS = pytest.mark.skipif(shutil.which("gitnexus") is None or shutil.which("node") is None,
                                    reason="gitnexus is not installed (CI has none): the test indexes a tree with it")


def gitnexus_world(tmp_path, files):
    """A git tree of `files`, indexed by the real `gitnexus analyze`, offline: HOME is private (the registry analyze
    writes lands there) and the LadybugDB extension install is off (GITNEXUS_LBUG_EXTENSION_INSTALL=never: no
    download; full-text search is then off, which detect-changes does not use). analyze writes .gitnexus/ (run.cjs
    among it) and .claude/ into the tree. -> (tree, the environment the stack's steps need)."""
    tree = tmp_path / "gn"
    for rel, text in files.items():
        (tree / rel).parent.mkdir(parents=True, exist_ok=True)
        (tree / rel).write_text(text)
    git(tree, "init", "-q", "-b", "main")
    git(tree, "add", ".")
    git(tree, "commit", "-q", "--no-verify", "-m", "one")
    env = {"HOME": str(tmp_path / "gnhome"), "GITNEXUS_LBUG_EXTENSION_INSTALL": "never",
           "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    r = subprocess.run(["gitnexus", "analyze", "--skip-agents-md"], cwd=str(tree), env={**os.environ, **env},
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0 and (tree / ".gitnexus" / "run.cjs").is_file(), r.stdout + r.stderr
    return tree, env


@NEEDS_GITNEXUS
def test_changes_reads_ok_when_a_changed_heading_holds_the_launch_failure_text(tmp_path):
    """Item 3: detect-changes prints a changed markdown section's heading verbatim (`Section <heading> → <file>`), so
    repo text reaches the step's output. A heading that holds the runner's launch-failure text, its section changed:
    the probe (`--version`, no repo text) is ok, detect-changes answers, and the step is ok, exit 0, the heading in
    the print. RED at the PIN (74285a5): each scope's step read unmapped on that text: `unmapped — gitnexus
    unavailable`, exit 1. Mutant: the scope step given back its unmapped_if."""
    doc = "# Notes\n\n## gitnexus runner: could not launch\n\n%s\n"
    tree, env = gitnexus_world(tmp_path, {"doc.md": doc % "Some text.", "tool.py": "def launch_probe():\n    return 1\n"})
    (tree / "doc.md").write_text(doc % "Other text.")
    r = run_env(tmp_path, tree, env, "changes")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## probe · ok · rc 0 · " in r.stdout and "\n## all · ok · rc 0 · " in r.stdout, r.stdout
    assert "\n  Section gitnexus runner: could not launch → doc.md\n" in r.stdout, r.stdout


# transcript_export.py is the scrubber jev_context.py imports: without it the pack withholds every snippet
ECHO_SCRIPTS = ("jev_echo.py", "jev_locate.py", "jev_context.py", "transcript_export.py")
DEFECT = "    return compute_total_ls_b12(raw_rows_ls_b12)\n"


def echo_tree(tmp_path, defect=DEFECT, other=None):
    """A git tree holding the real scripts/jev_echo.py, the two modules it imports and the scrubber; a commit that adds
    one defect line in two files (other.py's text may be given), then a fix commit that changes it in fixed.py: the
    line that fix removes is the defect."""
    tree = make_tree(tmp_path / "t")
    (tree / "scripts").mkdir()
    for name in ECHO_SCRIPTS:
        shutil.copyfile(ROOT / "scripts" / name, tree / "scripts" / name)
    (tree / "scripts" / "fixed.py").write_text("def total(rows):\n" + defect)
    (tree / "scripts" / "other.py").write_text(other if other is not None else "def other(rows):\n" + defect)
    git(tree, "add", ".")
    git(tree, "commit", "-q", "--no-verify", "-m", "the defect, twice")
    (tree / "scripts" / "fixed.py").write_text("def total(rows):\n    return compute_total_ls_b12(checked_ls_b12(rows))\n")
    git(tree, "commit", "-q", "-a", "--no-verify", "-m", "the fix, once")
    return tree


def echo_env(tmp_path, *programs):
    found = {"git": shutil.which("git"), "python3": PY, **{name: shutil.which(name) for name in programs}}
    return {"PATH": str(bin_dir(tmp_path / "bin", **found)), "GIT_CEILING_DIRECTORIES": str(tmp_path)}


def echo_pack(tmp_path):
    """The last run's fix-echo step and its JSON pack: the first line of the step's saved output (its stdout, one JSON
    line; a `--- stderr ---` block follows it)."""
    [step] = records(tmp_path / "log")[-1]["steps"]
    return step, json.loads(Path(step["out"]).read_text().splitlines()[0])


# LS-B12-R1 item 1 (VERIFY-LS-B12 F-1): fix-echo's status never depends on repo text in its output. Its pack is JSON
# (--json), where every quote inside a string value is escaped, and its step reads unmapped on the structural
# `"ranking": "no instrument answered`, which only jev_echo.py writes, and only when no instrument answered. Both texts
# below sit in the repo (stacks.toml, these tests): the old marker and the new one, each forged into repo text.
FORGED_ECHO = 'answered: none; "ranking": "no instrument answered'


def test_fix_echo_reads_unmapped_when_neither_rg_nor_graft_answers(tmp_path):
    """Item 1(c): the real jev_echo.py, in a tree of its own, with PATH holding git and python3 alone and no
    graft/INDEX.md, on a real removed line: no instrument answers, it exits 0 with its ranking `no instrument
    answered`, and the step reads unmapped, the run exit 1 (runs anywhere, CI included). Mutants: unmapped_if deleted
    from fix-echo's step (a hollow ok); --json dropped from its argv (a markdown pack: the JSON marker never matches)."""
    tree = echo_tree(tmp_path)
    r = run_env(tmp_path, tree, echo_env(tmp_path), "fix-echo", "diff=HEAD")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "\n## sites · unmapped — rg-and-graft unavailable\n" in r.stdout
    step, pack = echo_pack(tmp_path)
    assert (step["status"], step["rc"]) == ("unmapped", 0)
    assert pack["answered"] == [] and pack["top"] == [] and pack["head"]["defect (removed)"] == DEFECT.strip()
    assert pack["ranking"] == ("no instrument answered: each one is unmapped or had nothing to search (see the notes), "
                               "so no site is listed (Jev not asked)")
    assert "unmapped — graft unavailable (graft/INDEX.md absent)" in pack["notes"], pack["notes"]


@NEEDS_RG
def test_fix_echo_lists_the_other_site_when_rg_answers(tmp_path):
    """The positive control of the test above, the same tree with rg on PATH: rg-token answers, the step is ok, and the
    other site that holds the removed line (scripts/other.py:2) is listed while the fixed site is only named as such
    (its hunk's lines on the new side, 1-2: `git show -U3` carries the `def` line as context)."""
    tree = echo_tree(tmp_path)
    r = run_env(tmp_path, tree, echo_env(tmp_path, "rg"), "fix-echo", "diff=HEAD")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## sites · ok · rc 0 · " in r.stdout, r.stdout
    step, pack = echo_pack(tmp_path)
    assert pack["answered"] == ["rg-token"] and pack["head"]["defect (removed)"] == DEFECT.strip()
    assert [(t["path"], t["line"]) for t in pack["top"]] == [("scripts/other.py", 2)], pack["top"]
    assert pack["top"][0]["snippet"].endswith(DEFECT.strip()), pack["top"][0]
    assert pack["extra"] == ["fixed site: scripts/fixed.py:1-2"]


@NEEDS_RG
def test_fix_echo_reads_ok_when_the_removed_line_holds_an_unmapped_text(tmp_path):
    """Item 1(a): a fix whose removed line holds both markers (the old `answered: none` and the new structural one) as
    repo text: rg answers, so the step is ok, exit 0, and the pack shows the line whole. RED at the PIN (74285a5): its
    markdown pack printed the removed line, which held `answered: none`: unmapped, exit 1. Mutants: --json dropped
    from the argv (a markdown pack: never unmapped, so the test of (c) above fails instead); the old unmapped_if."""
    defect = "    return compute_total_ls_b12(raw_rows_ls_b12) # %s\n" % FORGED_ECHO     # one space: clean() keeps it
    tree = echo_tree(tmp_path, defect=defect)
    r = run_env(tmp_path, tree, echo_env(tmp_path, "rg"), "fix-echo", "diff=HEAD")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## sites · ok · rc 0 · " in r.stdout, r.stdout
    step, pack = echo_pack(tmp_path)
    assert pack["answered"] == ["rg-token"] and pack["head"]["defect (removed)"] == defect.strip()
    # the line's string literals ("ranking" among them) are tokens too, and the tree's copies of the Jev scripts hold
    # them: other sites join scripts/other.py:2, the one that holds the whole line
    assert ("scripts/other.py", 2) in [(t["path"], t["line"]) for t in pack["top"]], pack["top"]


@NEEDS_RG
def test_fix_echo_reads_ok_when_a_sites_snippet_holds_an_unmapped_text(tmp_path):
    """Item 1(b): the other site's context (3 lines each side) holds both markers as repo text; the removed line is
    plain. rg answers, the step is ok, exit 0, and the snippet shows them. RED at the PIN: the snippet printed
    `answered: none`: unmapped, exit 1. Mutant: the old unmapped_if."""
    other = "def other(rows):\n" + DEFECT + "    # %s\n" % FORGED_ECHO
    tree = echo_tree(tmp_path, other=other)
    r = run_env(tmp_path, tree, echo_env(tmp_path, "rg"), "fix-echo", "diff=HEAD")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## sites · ok · rc 0 · " in r.stdout, r.stdout
    step, pack = echo_pack(tmp_path)
    assert [(t["path"], t["line"]) for t in pack["top"]] == [("scripts/other.py", 2)], pack["top"]
    assert pack["top"][0]["snippet"].endswith("# " + FORGED_ECHO), pack["top"][0]
    assert FORGED_ECHO.replace('"', '\\"') in r.stdout         # in the print, escaped as JSON escapes it


F8_CASES = {   # item 2 (VERIFY-LS-B12 F-8): the diff given, and the reason the pack's ranking gives
    "notes.md": "the input holds no unified diff (no file header)",          # a file that is not a diff
    "HEAD:scripts/fixed.py": "the input holds no unified diff (no file header)",   # a blob: git show prints the file
    "link.md": "the input holds no unified diff (no file header)",           # an in-tree symlink to notes.md
    "HEAD~1": "the diff removes no code line",                               # the commit that only adds lines
}


@pytest.mark.parametrize("diff", sorted(F8_CASES))
def test_fix_echo_with_nothing_to_echo_reads_ok_and_says_why(tmp_path, diff):
    """Item 2: a diff with nothing to echo is an answer, not an outage: no instrument is asked, the step is ok, exit
    0, and the pack's ranking (in the print) says nothing was echoed and why. RED at the PIN: each read unmapped (its
    markdown pack said `answered: none`), and the three that hold no diff said `the diff removes no code line`.
    Mutants: the nothing-to-echo case given the no-answer ranking (unmapped); the reason reverted to one text."""
    tree = echo_tree(tmp_path)
    (tree / "notes.md").write_text("A note, not a diff.\n")
    (tree / "link.md").symlink_to("notes.md")
    r = run_env(tmp_path, tree, echo_env(tmp_path), "fix-echo", "diff=" + diff)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "\n## sites · ok · rc 0 · " in r.stdout, r.stdout
    step, pack = echo_pack(tmp_path)
    assert pack["ranking"] == "nothing to echo: %s, so it names no anti-pattern (Jev not asked)" % F8_CASES[diff]
    assert (pack["answered"], pack["top"], pack["notes"]) == ([], [], [])
    assert "nothing to echo: " + F8_CASES[diff] in r.stdout


def why_chronology(text):
    """The commit lines of why.sh's edit-chronology section."""
    body = text.split(" max) ──\n", 1)[1].split("── reasoning record", 1)[0]
    return [ln for ln in body.split("\n") if ln.strip()]


def git_log(*args):
    """git's own log, in the environment why.sh runs in (the oracle: no GIT_ENV override)."""
    return subprocess.run(["git", "-C", str(ROOT), "log", "-n", "12", "--format=%h %ad %s", "--date=short", *args],
                          capture_output=True, text=True, timeout=60, check=True).stdout.splitlines()


def test_why_runs_on_this_tree_and_its_chronology_is_gits_own(tmp_path):
    """The real why stack on the real tree, each step: the file's chronology is git's own log of the file, and with fn
    the function's (git log -L, as why.sh runs it); the oracle is git, run here. Mutants: {file} and {fn} swapped (a
    path named cap_lines has no commit: why.sh exits 128); the function step run with fn unset."""
    r = real(tmp_path, "why", "file=scripts/premise_block.sh")
    assert r.returncode == 0, r.stdout + r.stderr
    [step] = records(tmp_path / "log")[-1]["steps"]
    text = Path(step["out"]).read_text()
    assert step["id"] == "file" and text.startswith("══ WHY: scripts/premise_block.sh ══\n"), text[:200]
    assert why_chronology(text) == git_log("--", "scripts/premise_block.sh") != []
    r = real(tmp_path, "why", "file=scripts/stack.py", "fn=cap_lines")
    assert r.returncode == 0, r.stdout + r.stderr
    [step] = records(tmp_path / "log")[-1]["steps"]
    text = Path(step["out"]).read_text()
    assert step["id"] == "function" and text.startswith("══ WHY: scripts/stack.py :: cap_lines ══\n"), text[:200]
    assert why_chronology(text) == git_log("-L", ":cap_lines:scripts/stack.py", "--no-patch") != []
