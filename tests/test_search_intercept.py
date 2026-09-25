""".claude/hooks/search-intercept.py: the search intercept and the Bash quirk guard (tasks #228, #225; D-072 item 4).

Deterministic and LLM-free. The search tests run the REAL graft and rg on this repository and the REAL hook as a
subprocess, each with its own state directory (AF_SEARCH_INTERCEPT_STATE), so no test touches .jev/ or another test's
escape-hatch record. Jev is never asked for an answer here: with its switch off it must not be called at all (its own
call log is the instrument), and with the switch on it is pointed at a closed port (Jev down). Quirk commands are only
ever handed to the hook as payloads, never run.

Mutation runs: SEARCH_INTERCEPT_UNDER_TEST=<scratch copy> makes every test load and run that copy as if it sat at the
real path (so ROOT, the nag and jev resolve to this repo). It is a seam of this test file only; the hook has none.

Tools (VERIFY-JT3 F-4): CI installs neither graft nor a graft index. A test that needs the real graft or rg to answer
carries a LOUD skip guard (NEEDS_GRAFT, NEEDS_RG), and so does a negative control that cannot discriminate without
them (with no graft every search passes anyway). A fail-open or quirk test builds its own PATH from its own scripts and
runs everywhere; test_the_pair_passes_where_graft_or_rg_is_absent runs this file and tests/test_session_hooks.py under
PATHs without graft and without graft and rg.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

NEEDS_GRAFT = pytest.mark.skipif(shutil.which("graft") is None, reason=(
    "LOUD SKIP: graft is absent here (CI installs none); this test needs the real graft for the hook to answer"))
NEEDS_RG = pytest.mark.skipif(shutil.which("rg") is None, reason=(
    "LOUD SKIP: ripgrep (rg) is absent here; this test needs the real rg for the hook to answer"))

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "search-intercept.py"
UNDER_TEST = Path(os.environ.get("SEARCH_INTERCEPT_UNDER_TEST") or HOOK)
RUNNER = ("import sys, types\n"
          "m = types.ModuleType('search_intercept'); m.__file__ = sys.argv[2]\n"
          "exec(compile(open(sys.argv[1], encoding='utf-8').read(), sys.argv[2], 'exec'), m.__dict__)\n"
          "for kv in sys.argv[3:]:\n"
          "    k, v = kv.split('=', 1); setattr(m, k, int(v))\n"
          "sys.exit(m.main())\n")
CLOSED = "http://127.0.0.1:1"      # nothing listens on port 1: a real refused connection (Jev down)


def _load():
    mod = types.ModuleType("search_intercept_under_test")
    mod.__file__ = str(HOOK)
    exec(compile(UNDER_TEST.read_text(encoding="utf-8"), str(HOOK), "exec"), mod.__dict__)
    return mod


si = _load()


def _argv(*overrides):
    if UNDER_TEST == HOOK and not overrides:
        return [sys.executable, str(HOOK)]
    return [sys.executable, "-c", RUNNER, str(UNDER_TEST), str(HOOK), *overrides]


def _env(state, **extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("AF_SEARCH_INTERCEPT")}
    env["AF_SEARCH_INTERCEPT_STATE"] = str(state)
    env.update(extra)
    return env


def run(payload, state, env=None, raw=None, overrides=(), timeout=120):
    data = raw if raw is not None else json.dumps(payload).encode("utf-8")
    return subprocess.run(_argv(*overrides), input=data, capture_output=True, timeout=timeout,
                          env=env if env is not None else _env(state))


def grep(pattern, path=None, **kw):
    ti = {"pattern": pattern, **({"path": path} if path else {}), **kw}
    return {"tool_name": "Grep", "tool_input": ti, "cwd": str(ROOT)}


def bash(command, description="probe"):
    return {"tool_name": "Bash", "tool_input": {"command": command, "description": description}, "cwd": str(ROOT)}


def err(r):
    return r.stderr.decode("utf-8", "replace")


def line_of(text, path="scripts/install_session_hooks.py"):
    """The 1-based line of the first line of `path` holding `text`: read from the file, never typed."""
    return next(i for i, ln in enumerate((ROOT / path).read_text().split("\n"), 1) if text in ln)


def lines(text):
    """The answer's lines, split on \\n only, as rg and the hook write them (str.splitlines also splits on
    \\x0c, \\x85 and U+2028, AF-AP-132)."""
    return text.rstrip("\n").split("\n")


def assert_silent_pass(r):
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b""), (r.returncode, r.stdout[:300], r.stderr[:300])


RG_NO_MATCH = "#!/bin/sh\nexit 1\n"        # rg's own "no match": a stand-in that lets the hook reach its graft step
GRAFT_ANSWERS = "#!/bin/sh\necho 'our_hooks · stand-in answer'\n"   # a graft that answers: see the stand-in control


def _bin(tmp_path, graft="real", rg="real"):
    """A PATH holding only what the hook may need. A tool is "real" (the host's; graft brings node), a script of the
    test's own, or None (absent). The fail-open tests use only their own scripts, so they run where the host has
    neither graft nor rg (VERIFY-JT3 F-4); a "real" tool is for NEEDS_GRAFT/NEEDS_RG tests only."""
    b = tmp_path / "bin"
    b.mkdir()
    for name, how in (("graft", graft), ("rg", rg)):
        if how == "real":
            (b / name).symlink_to(os.path.realpath(shutil.which(name)))
        elif how is not None:
            (b / name).write_text(how)
            (b / name).chmod(0o755)
    if graft == "real":
        (b / "node").symlink_to(shutil.which("node"))
    return str(b)


# ---------------------------------------------------------------- (a) the search intercept

@NEEDS_GRAFT
@NEEDS_RG
def test_semantic_grep_is_answered_once_then_the_identical_repeat_passes(tmp_path):
    r = run(grep("our_hooks", "scripts", output_mode="content"), tmp_path / "st")
    text = err(r)
    assert r.returncode == 2 and r.stdout == b""
    first = lines(text)[0]
    assert first.startswith("SEARCH INTERCEPT") and "did NOT run" in first and "repeat the identical call" in first
    assert "graft ask 'our_hooks' --in scripts" in text and "our_hooks · function" in text
    assert "scripts/install_session_hooks.py:%d: def our_hooks(root: Path) -> dict:" % line_of("def our_hooks(") in text
    assert_silent_pass(run(grep("our_hooks", "scripts", output_mode="content"), tmp_path / "st"))


def test_the_escape_key_ignores_only_the_description_label(tmp_path):
    """The key is the same for a search and a quirk (seen_key); a quirk block needs neither graft nor rg."""
    st = tmp_path / "st"
    assert run(bash("git rev-parse --short HEAD HEAD~1", "first label"), st).returncode == 2
    assert_silent_pass(run(bash("git rev-parse --short HEAD HEAD~1", "another label"), st))
    assert run(bash("git rev-parse --short HEAD HEAD~2", "first label"), st).returncode == 2


def test_the_window_expires_and_the_record_refreshes(tmp_path):
    st, p = str(tmp_path / "st"), bash("git rev-parse --short HEAD HEAD~1")
    assert si.decide(p, st, None, now=1_000.0)[0] == 2
    assert si.decide(p, st, None, now=1_060.0) == (0, "")
    assert si.decide(p, st, None, now=1_121.0)[0] == 2           # 121 s later: the window is 120 s
    assert si.decide(p, st, None, now=1_122.0) == (0, "")


@NEEDS_GRAFT
@NEEDS_RG
def test_a_literal_token_grep_passes(tmp_path):
    assert_silent_pass(run(grep("^PROOF-STATUS: S0-0[0-9]", "todo"), tmp_path / "st"))


@NEEDS_GRAFT
@NEEDS_RG
def test_a_simple_rg_bash_command_is_answered(tmp_path):
    r = run(bash("rg -n our_hooks scripts | head -20"), tmp_path / "st")
    assert r.returncode == 2 and "this Bash rg command was answered here" in lines(err(r))[0]
    # the definition line, not an implementation line: S1-L1-R1 rewrote the body and this local-only test (CI has no
    # graft) read a line that was gone for four hours (2026-09-25)
    assert "scripts/install_session_hooks.py:%d:" % line_of("def our_hooks(") in err(r)


@pytest.mark.parametrize("command", [
    "cd /home/user/agent-factory && grep -rn our_hooks scripts",
    "grep -rn our_hooks scripts; echo done",
    "grep -rn our_hooks scripts | grep def",
    "grep -rn our_hooks scripts > /tmp/out.txt",
    "grep -rn $NAME scripts",
    "grep -rn our_hooks $(echo scripts)",
    "rg our_hooks scripts &",
])
@NEEDS_GRAFT
@NEEDS_RG
def test_a_compound_or_dynamic_bash_search_is_never_intercepted(tmp_path, command):
    assert_silent_pass(run(bash(command), tmp_path / "st"))


@pytest.mark.parametrize("command", [
    "grep -n our_hooks scripts",              # no -r: grep refuses a directory
    "grep -rn 'our_hooks|merged' scripts",    # a basic-regex `|` is a literal character
    "grep -rvn our_hooks scripts",            # -v inverts the search
    "rg -r x our_hooks scripts",              # rg -r replaces
])
@NEEDS_GRAFT
@NEEDS_RG
def test_a_search_this_hook_cannot_reproduce_passes(tmp_path, command):
    assert_silent_pass(run(bash(command), tmp_path / "st"))


@NEEDS_GRAFT
@NEEDS_RG
def test_a_search_outside_the_repository_passes(tmp_path):
    code = tmp_path / "elsewhere" / "scripts"
    code.mkdir(parents=True)
    (code / "mod.py").write_text("def our_hooks():\n    return 1\n")
    p = {"tool_name": "Grep", "tool_input": {"pattern": "our_hooks", "path": str(code)}, "cwd": str(tmp_path)}
    assert si.nag_says_semantic({"pattern": "our_hooks", "path": str(code), "glob": "", "type": ""})   # de-vacuous
    assert_silent_pass(run(p, tmp_path / "st"))


@NEEDS_RG
def test_a_matched_line_holding_a_form_feed_stays_whole(tmp_path):
    """rg ends lines with \\n only; str.splitlines() would also split at \\x0c (and \\x85, U+2028), cutting the hit's text
    and dropping its tail (AF-AP-132)."""
    import shutil
    (tmp_path / "mod.py").write_text("x = our_hooks" + chr(0x0C) + " + 1\n")
    spec = dict(_spec(), paths=["mod.py"])
    hits, cut = si.run_rg(shutil.which("rg"), spec, str(tmp_path), [str(tmp_path / "mod.py")], time.monotonic() + 30)
    assert (hits, cut) == ([("mod.py", 1, "x = our_hooks" + chr(0x0C) + " + 1")], False)


def test_the_grep_tool_ignore_case_accepts_only_a_real_boolean():
    assert si.grep_tool_search({"pattern": "x", "-i": "false"})["i"] is False
    assert si.grep_tool_search({"pattern": "x", "-i": True})["i"] is True


@pytest.mark.parametrize("glob,globs", [
    ("*.sh,*.md", None), ("*.sh *.md", None), ("*.sh\t*.md", None), ("*.sh, *.md", None), ("{a,b", None), ("a}", None),
    ("*.{sh,md}", ["*.{sh,md}"]), ("src/**/*.{ts, tsx}", None), ("*.sh" + chr(0xFEFF) + "*.md", None),
    ("*.sh", ["*.sh"]), ("", []),
])
def test_a_glob_the_grep_tool_splits_is_never_answered_as_one(glob, globs):
    """VERIFY-JT3-R1 N-1: the Grep tool splits its glob on commas outside braces and on whitespace anywhere (U+FEFF too;
    R2-1, R2-2); rg reads one glob, so `*.sh,*.md` matched no file and the hook answered "0 hits" where the tool finds
    files. Such a call passes through."""
    spec = si.grep_tool_search({"pattern": "our_hooks", "path": "scripts", "glob": glob})
    assert (spec if spec is None else spec["globs"]) == globs


# ---------------------------------------------------------------- answer fidelity (VERIFY-JT3 F-1, F-2)

HOOK_REL = ".claude/hooks/search-intercept.py"
# The Grep tool's scope as probed on a scratch repo (JT3-R1-report.md section 2.1), written out here, never read from
# the hook: hidden paths yes, these six VCS directories no, ignore files honoured.
GREP_TOOL_SCOPE = ["--hidden"] + [a for d in (".git", ".svn", ".hg", ".bzr", ".jj", ".sl") for a in ("--glob", "!" + d)]
GREP_R_SKIPS = ("not searched, which grep -r reads: files that .gitignore or .ignore rules exclude, and binary files")


def _rg_part(text):
    """rg's part of an answer: its count line and the entries after it, the Cut line left out."""
    out = lines(text)
    i = next(k for k, ln in enumerate(out) if ln.startswith("rg: "))
    return out[i], [ln for ln in out[i + 1:] if not ln.startswith("Cut: ")]


def _raw(*argv):
    """The raw call itself, run here as the oracle: its stdout lines."""
    r = subprocess.run(list(argv), cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
    assert r.returncode in (0, 1), (argv, r.stderr[:300])
    return [ln for ln in r.stdout.split("\n") if ln]


def _skipped_by_rg(path):
    """True when rg's defaults skip `path`: ignore rules exclude it, or it is binary (holds a NUL byte)."""
    ignored = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0
    return ignored or b"\0" in (ROOT / path).read_bytes()


@NEEDS_GRAFT
@NEEDS_RG
def test_an_answer_searches_what_the_raw_call_searches(tmp_path):
    """F-1: _heredoc_delim is defined only under the hidden .claude/. The Grep tool searches hidden paths (probed on a
    scratch repo, JT3-R1-report.md section 2.1), so its answer lists the hook; a Bash grep -r answer reads hidden paths
    too and names what rg still skips; a Bash rg answer keeps rg's defaults, file for file."""
    g = err(run({"tool_name": "Grep", "tool_input": {"pattern": "_heredoc_delim"}, "cwd": str(ROOT)}, tmp_path / "g"))
    assert "./" + HOOK_REL in _rg_part(g)[1], g[-800:]
    b = err(run(bash("grep -rn _heredoc_delim"), tmp_path / "b"))
    count, shown = _rg_part(b)
    defining = "./%s:%d: def _heredoc_delim(s, i):" % (HOOK_REL, line_of("def _heredoc_delim(", HOOK_REL))
    assert defining in shown, b[-800:]
    assert count.endswith("; " + GREP_R_SKIPS + ":"), count
    r = err(run(bash("rg -l _heredoc_delim"), tmp_path / "r"))
    assert _rg_part(r)[1] == _raw("rg", "-l", "--sort", "path", "_heredoc_delim", ".")      # no hidden path in either


@NEEDS_GRAFT
@NEEDS_RG
def test_names_and_counts_are_answered_with_names_and_counts(tmp_path):
    """F-2: a names-only or count-only call is answered with names or counts, never with matching lines, and with the
    raw call's own files and numbers (the raw command runs here as the oracle)."""
    def rg_part(payload, name):
        return _rg_part(err(run(payload, tmp_path / name)))
    count, names = rg_part(bash("rg -l our_hooks scripts"), "rl")
    assert names == _raw("rg", "-l", "--sort", "path", "our_hooks", "scripts") and count.endswith("path order):")
    assert rg_part(bash("rg -c our_hooks scripts"), "rc")[1] == _raw(
        "rg", "-c", "--sort", "path", "our_hooks", "scripts")
    assert rg_part(grep("our_hooks", "scripts"), "gl")[1] == _raw(                         # the Grep tool's default
        "rg", "-l", "--sort", "path", *GREP_TOOL_SCOPE, "our_hooks", "scripts")
    assert rg_part(grep("our_hooks", "scripts", output_mode="count"), "gc")[1] == _raw(
        "rg", "-c", "--sort", "path", *GREP_TOOL_SCOPE, "our_hooks", "scripts")
    count, gnames = rg_part(bash("grep -rl our_hooks scripts"), "grl")
    raw_names = _raw("grep", "-rl", "our_hooks", "scripts")
    left_out = sorted(set(raw_names) - set(gnames))
    assert gnames and set(gnames) <= set(raw_names) and all(_skipped_by_rg(p) for p in left_out), left_out
    assert count.endswith("; " + GREP_R_SKIPS + ":"), count
    count, gcounts = rg_part(bash("grep -rc our_hooks scripts"), "grc")
    raw_counts = [ln for ln in _raw("grep", "-rc", "our_hooks", "scripts") if not ln.endswith(":0")]
    assert gcounts == sorted(c for c in raw_counts if not _skipped_by_rg(c.rsplit(":", 1)[0])), (gcounts, raw_counts)
    assert "files with no match are left out" in count, count
    for entries in (names, gnames, gcounts):                    # never a `path:line: text` entry
        assert not [e for e in entries if e.count(":") > 1 or ": " in e], entries


@NEEDS_GRAFT
@NEEDS_RG
@pytest.mark.parametrize("payload", [
    bash("grep -rn -o our_hooks scripts"), bash("grep -rn -A 3 our_hooks scripts"), bash("rg -C 2 our_hooks scripts"),
    bash("rg --count-matches our_hooks scripts"), bash("grep -rlc our_hooks scripts"),
    bash("grep -rna our_hooks scripts"),
    grep("our_hooks", "scripts", output_mode="content", **{"-A": 3}),
    grep("our_hooks", "scripts", output_mode="content", **{"-o": True}),
    grep("our_hooks", "scripts", head_limit=5), grep("our_hooks", "scripts", offset=2),
    grep("our_hooks", "scripts", multiline=True),
    grep("our_hooks", "scripts", glob="*.sh,*.md"), grep("our_hooks", "scripts", glob="*.py *.sh"),
], ids=["grep-o", "grep-A", "rg-C", "rg-count-matches", "grep-lc", "grep-a", "Grep-A", "Grep-o", "Grep-head_limit",
        "Grep-offset", "Grep-multiline", "Grep-glob-comma", "Grep-glob-space"])
def test_an_output_this_hook_cannot_reproduce_passes_through(tmp_path, payload):
    """F-2: context lines, -o, grep -a, rg --count-matches, -l with -c, an offset, a head_limit, multiline; N-1: a glob
    the Grep tool splits into several."""
    assert_silent_pass(run(payload, tmp_path / "st"))


# ---------------------------------------------------------------- size (A3) and the cut order (KC-J5)

def _spec(pattern="our_hooks", mode="content"):
    return {"prog": "Grep", "pattern": pattern, "paths": ["scripts"], "globs": [], "type": "", "i": False, "w": False,
            "F": False, "E": True, "r": True, "extra": [], "mode": mode}


def test_every_answer_stays_under_9000_characters_on_a_huge_synthetic_search():
    hits = [("scripts/some/deeply/nested/path/file_%04d.py" % (i // 7), i, "x" * 400) for i in range(5_000)]
    text = si.format_answer("Grep", _spec(), "'our_hooks' --in scripts", "g" * 50_000, hits, True)
    assert len(text) < 9_000, len(text)
    out = lines(text)
    assert out[0].startswith("SEARCH INTERCEPT") and "repeat the identical call" in out[0]
    assert "at least 5000 hits" in text and out[-1].startswith("Cut: at least ")


@NEEDS_GRAFT
@NEEDS_RG
def test_a_real_search_matching_thousands_of_lines_stays_under_the_cap(tmp_path):
    r = run({"tool_name": "Grep", "tool_input": {"pattern": "self", "output_mode": "content"}, "cwd": str(ROOT)},
            tmp_path / "st")
    text = err(r)
    assert r.returncode == 2 and len(text) < 9_000, (r.returncode, len(text))
    count = next(ln for ln in lines(text) if ln.startswith("rg: "))
    assert int(count.split()[1 if count.split()[1].isdigit() else 3]) >= 1_000, count
    assert lines(text)[-1].startswith("Cut: ") and "repeat the identical call" in lines(text)[-1]
    shown = lines(text)[lines(text).index(count) + 1:-1]
    assert len(shown) == 20 and all(ln.startswith("./") for ln in shown)   # an explicit ".", never rg's stdin guess


def test_the_shown_hits_are_a_prefix_of_file_order_and_jev_only_reorders_them():
    hits = [("scripts/f%02d.py" % (i % 5), i + 1, "use of our_hooks number %d" % i) for i in range(40)]
    plain = si.format_answer("Grep", _spec(), "q", "graft text", hits, False)
    seen = []

    def reverse(shown):
        seen.append(len(shown))
        return list(range(len(shown)))[::-1], "reordered (test)"
    jev = si.format_answer("Grep", _spec(), "q", "graft text", hits, False, reverse)
    shown_plain = [ln for ln in lines(plain) if ln.startswith("scripts/f")]
    shown_jev = [ln for ln in lines(jev) if ln.startswith("scripts/f")]
    n = len(shown_plain)
    assert 0 < n < len(hits) and seen == [n]                    # the reorder only ever saw the shown prefix
    assert shown_plain == [si._hit_line(h) for h in hits[:n]]   # file order, a prefix
    assert shown_jev == shown_plain[::-1]                       # same set, reordered
    assert lines(plain)[-1] == lines(jev)[-1]       # the same cut, whatever Jev says


def _hit_lines(text):
    return [ln for ln in lines(text) if ln.startswith("scripts/")]


@NEEDS_GRAFT
@NEEDS_RG
def test_the_same_search_twice_gives_the_same_answer(tmp_path):
    """rg's parallel walk prints files in completion order; unsorted, the shown prefix changed between two runs (this
    lane's first test run: index 10 was pc_lane.sh once and pc_suite.sh the next). A race, so its red is not certain."""
    a = run(grep("ROOT", "scripts", output_mode="content"), tmp_path / "a")
    b = run(grep("ROOT", "scripts", output_mode="content"), tmp_path / "b")
    assert a.returncode == b.returncode == 2 and a.stderr == b.stderr
    hit_lines = _hit_lines(err(a))
    assert hit_lines == sorted(hit_lines, key=lambda ln: (ln.split(":")[0], int(ln.split(":")[1])))


@NEEDS_GRAFT
@NEEDS_RG
def test_jev_is_not_called_while_its_switch_is_off(tmp_path):
    st = tmp_path / "st"
    r = run(grep("ROOT", "scripts", output_mode="content"), st, env=_env(st, AF_SEARCH_INTERCEPT_JEV_URL=CLOSED))
    assert r.returncode == 2 and "the first" in err(r)
    assert "Jev reorder" not in err(r) and "reordered by Jev" not in err(r)
    assert not (st / "calls.jsonl").exists()                    # jev logs every call, a failed one too


@NEEDS_GRAFT
@NEEDS_RG
def test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order(tmp_path):
    off, on = tmp_path / "off", tmp_path / "on"
    a = run(grep("ROOT", "scripts", output_mode="content"), off, env=_env(off, AF_SEARCH_INTERCEPT_JEV_URL=CLOSED))
    b = run(grep("ROOT", "scripts", output_mode="content"), on, env=_env(on, AF_SEARCH_INTERCEPT_JEV_URL=CLOSED,
                                                                         AF_SEARCH_INTERCEPT_JEV_RANK="1"))
    assert (a.returncode, b.returncode) == (2, 2)
    assert "the Jev reorder was unavailable" in err(b)
    assert _hit_lines(err(a)) == _hit_lines(err(b)) and len(_hit_lines(err(a))) > 12
    log = [json.loads(ln) for ln in lines((on / "calls.jsonl").read_text())]
    assert len(log) == 1 and log[0]["cmd"] == "rank" and log[0]["ok"] is False
    (tmp_path / "on2").mkdir()
    (tmp_path / "on2" / "intercept-jev-rank-on").write_text("")    # the file form of the switch
    c = run(grep("ROOT", "scripts", output_mode="content"), tmp_path / "on2",
            env=_env(tmp_path / "on2", AF_SEARCH_INTERCEPT_JEV_URL=CLOSED))
    assert c.returncode == 2 and "the Jev reorder was unavailable" in err(c)


# ---------------------------------------------------------------- (b) the quirk table

QUIRKS = {   # rule id: (positive, near miss)
    "trailing-amp": ("mkdir -p /tmp/jt3x && nohup sleep 1 > /dev/null 2>&1 &\necho $! > /tmp/jt3x/pid",
                     "mkdir -p /tmp/jt3x\nnohup sleep 1 > /dev/null 2>&1 &\necho $! > /tmp/jt3x/pid"),
    "pkill-self": ('pkill -f "[r]un_packs.sh"; nohup bash run_packs.sh > /dev/null 2>&1',
                   'pkill -f "[r]un_packs.sh"; echo done'),
    "safe-commit-backtick": ('bash scripts/safe_commit.sh -m "fix the `foo` bug" a.py',
                             'bash scripts/safe_commit.sh -m "fix the \\`foo\\` bug" a.py'),
    "rev-parse-two": ("git rev-parse --short HEAD HEAD~1", "git rev-parse --short HEAD 2>/dev/null"),
}


def test_the_quirk_table_is_closed_and_every_shipped_rule_is_tested():
    assert set(si.SHIPPED) == set(si.QUIRK_RULES) == set(QUIRKS)


@pytest.mark.parametrize("rid", sorted(QUIRKS))
def test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss(tmp_path, rid):
    positive, near_miss = QUIRKS[rid]
    r = run(bash(positive), tmp_path / "st")
    text = err(r)
    assert r.returncode == 2 and r.stdout == b"", (r.returncode, text)
    first = lines(text)[0]
    assert first.startswith("QUIRK GUARD") and "rule %s" % rid in first and "repeat the identical call" in first
    assert "Anchor: " in text and ("SKILL.md" in text or "CLAUDE.md" in text or "AF-AP-" in text)
    assert_silent_pass(run(bash(positive), tmp_path / "st"))        # the escape hatch
    assert_silent_pass(run(bash(near_miss), tmp_path / "st2"))


# CTX1 (D-089): the quoted sentences moved out of CLAUDE.md into .claude/skills/env-tool-quirks/SKILL.md. Each shipped
# anchor names the file that holds its quote, and the quote is really in that file (whitespace-normalized).
ANCHOR_QUOTES = {
    "trailing-amp": ["A trailing `&` backgrounds the WHOLE `&&` list"],
    "pkill-self": ["kill by pid, never by `pkill -f` inside a compound command that also names the target"],
    "safe-commit-backtick": ['`scripts/safe_commit.sh -m "\u2026"`: no backticks inside a double-quoted message'],
    "rev-parse-two": ["`git rev-parse --short REV1 REV2` fails", "one rev-parse per call"],
}


def anchor_problems(anchor, quotes):
    """What is wrong with an anchor: no cited file, a quote the anchor does not carry, or one its file lacks."""
    m = re.match(r"(\.claude/skills/[a-z0-9-]+/SKILL\.md|CLAUDE\.md) ", anchor)
    if not m:
        return ["no cited file"]
    text = " ".join((ROOT / m.group(1)).read_text(encoding="utf-8").split())
    return (["anchor lacks %r" % q for q in quotes if q not in anchor]
            + ["%s lacks %r" % (m.group(1), q) for q in quotes if " ".join(q.split()) not in text])


def test_every_shipped_anchor_cites_the_file_that_holds_its_quote():
    assert set(ANCHOR_QUOTES) == set(si.SHIPPED)
    for rid, quotes in ANCHOR_QUOTES.items():
        assert anchor_problems(si.QUIRK_RULES[rid][1][1], quotes) == [], rid


def test_negative_control_an_anchor_citing_a_file_without_its_quote_is_caught():
    moved = si.QUIRK_RULES["trailing-amp"][1][1].replace(si.QUIRK_SKILL, "CLAUDE.md", 1)   # the pre-CTX1 anchor
    assert moved.startswith("CLAUDE.md ")
    assert anchor_problems(moved, ANCHOR_QUOTES["trailing-amp"]) == [
        "CLAUDE.md lacks 'A trailing `&` backgrounds the WHOLE `&&` list'"]


@pytest.mark.parametrize("command", [
    "(cd /tmp && nohup sleep 1 > /dev/null 2>&1) &",
    "{ cd /tmp && sleep 1; } &",
    "nohup sh -c 'a && b' > /dev/null 2>&1 &",
    "echo 'a && b &'",
    "cat > /tmp/jt3x.sh <<'EOF'\na && b &\nEOF\nbash /tmp/jt3x.sh",
    "a && b &> /dev/null",
    'git commit -m "$(cat <<\'EOF\'\nfix `x` and don\'t\nEOF\n)"',
    "pkill -A -f foo; echo foo",
    "git -C /tmp rev-parse --short=8 HEAD",
])
def test_quoted_grouped_or_heredoc_text_never_fires_a_rule(command):
    assert si.quirk(si.Parsed(command)) is None


def test_a_substitution_body_is_checked_too():
    assert si.quirk(si.Parsed("echo $(git rev-parse --short A B)"))[0] == "rev-parse-two"


# The two live trailing-amp blocks of 2026-09-24 (VERIFY-JT3 section 3.2), verbatim from the transcripts: both
# commands would have run as intended.
LIVE_14_03_20 = ('SP=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad && nohup bash '
                 'scripts/lane_gate.sh -r HEAD -f "scripts/vendored_manifest.py tests/test_vendored_manifest_parse.py" '
                 '-t "tests/test_vendored_manifest_parse.py tests/test_vendored_manifest.py '
                 'tests/test_s0_12_license_sbom.py tests/test_laya_pin.py tests/test_upstream_lock_lane_runtime.py '
                 'tests/test_edit_snapshot_ap_screen.py" -n 2 -o $SP/k170gate > $SP/k170gate.log 2>&1 </dev/null &'
                 '\necho started')
LIVE_14_03_07 = ("cd /tmp/vj11r4 && nohup /root/venv-agent-factory/bin/python sweep_builder.py 31337 100000 "
                 "/tmp/vj11r4/s31337 > /tmp/vj11r4/sweep_31337.log 2>&1 &\necho started; date -u +%H:%M:%SZ")
DETACH = "( cd /tmp && nohup sleep 1 > /dev/null 2>&1 & )"


@pytest.mark.parametrize("command,fires", [
    (DETACH, False),                                                   # the detach form (VERIFY-JT3 F-3, T01)
    (DETACH + ' ; echo "launch started"', False),                      # this project's lane-launch idiom
    (DETACH + " ; echo $!", False),                   # the group ran in the foreground: $! is unset either way
    (LIVE_14_03_20, False),
    (LIVE_14_03_07, False),
    ("mkdir -p /tmp/jt3x && nohup sleep 1 > /dev/null 2>&1 &", False),  # nothing after the list reads what it took
    ("cd /tmp && nohup sleep 1 & echo 'pid=$!'", False),               # single-quoted: not an expansion
    ("cd /tmp && nohup a & nohup b & echo $!", False),                  # $! names the later job
    ('cd /tmp && nohup sleep 1 & echo "pid=$!"', True),                # $! names the subshell, not the job
    ("cd /tmp && nohup sleep 1 > log 2>&1 &\nkill $!", True),          # the job survives the kill
    ('SP=/tmp/x && nohup job > $SP/log 2>&1 &\necho "log $SP/log"', True),   # SP is unset after the list
    ("export SP=/tmp/x && nohup job &\ntail ${SP}/log", True),
    ("{ cd /tmp && sleep 1 & } ; echo $!", True),                       # a brace group is not a subshell
], ids=["detach", "detach-then-echo", "detach-then-bang", "live-14:03:20", "live-14:03:07", "nothing-read",
        "quoted-bang", "bang-of-later-job", "bang", "kill-bang", "var", "export-var", "brace-group"])
def test_trailing_amp_blocks_only_when_a_later_step_reads_what_the_list_took(command, fires):
    """F-3: the whole list running in the background matters only when a later step reads `$!` or a variable the list
    assigns; the detach form and a launch with nothing read after it would have run as intended."""
    hit = si.quirk(si.Parsed(command), rules=("trailing-amp",))
    assert (hit is not None) == fires, hit


def test_the_detach_form_passes_the_real_hook(tmp_path):
    assert_silent_pass(run(bash(DETACH), tmp_path / "st"))           # the brief's F-3 premise payload


# ---------------------------------------------------------------- fail-open (A2), the off switch, the state file

def test_the_stand_in_path_answers(tmp_path):
    """The control for the fail-open tests below, which run without the host's tools: with a graft that answers and
    an rg that finds nothing, the same PATH gives an answer (rc 2). Each fail-open test changes one tool from this."""
    env = _env(tmp_path / "st", PATH=_bin(tmp_path, graft=GRAFT_ANSWERS, rg=RG_NO_MATCH))
    r = run(grep("our_hooks", "scripts"), tmp_path / "st", env=env)
    assert r.returncode == 2 and "our_hooks · stand-in answer" in err(r) and "rg: 0 hits." in err(r)


def test_graft_absent_fails_open(tmp_path):
    env = _env(tmp_path / "st", PATH=_bin(tmp_path, graft=None, rg=RG_NO_MATCH))
    assert_silent_pass(run(grep("our_hooks", "scripts"), tmp_path / "st", env=env))


def test_rg_absent_fails_open(tmp_path):
    env = _env(tmp_path / "st", PATH=_bin(tmp_path, graft=GRAFT_ANSWERS, rg=None))
    assert_silent_pass(run(grep("our_hooks", "scripts"), tmp_path / "st", env=env))


@NEEDS_GRAFT
@NEEDS_RG
def test_the_minimal_path_still_answers(tmp_path):     # the control with the real tools: the minimal PATH works
    env = _env(tmp_path / "st", PATH=_bin(tmp_path))
    assert run(grep("our_hooks", "scripts"), tmp_path / "st", env=env).returncode == 2


def test_a_graft_error_fails_open(tmp_path):
    env = _env(tmp_path / "st", PATH=_bin(tmp_path, graft="#!/bin/sh\necho broken >&2\nexit 3\n", rg=RG_NO_MATCH))
    assert_silent_pass(run(grep("our_hooks", "scripts"), tmp_path / "st", env=env))
    assert not (tmp_path / "st" / "intercept-seen.json").exists()    # nothing recorded when nothing is blocked


def test_a_graft_timeout_fails_open_and_kills_graft(tmp_path):
    pidfile = tmp_path / "graft.pid"
    script = "#!/bin/sh\necho $$ > %s\nexec /bin/sleep 30\n" % pidfile
    env = _env(tmp_path / "st", PATH=_bin(tmp_path, graft=script, rg=RG_NO_MATCH))
    t0 = time.monotonic()
    r = run(grep("our_hooks", "scripts"), tmp_path / "st", env=env, overrides=("GRAFT_TIMEOUT_S=1",))
    assert_silent_pass(r)
    assert time.monotonic() - t0 < 15
    pid = int(pidfile.read_text())
    time.sleep(0.2)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_the_whole_hook_budget_is_a_backstop(tmp_path):
    proc = subprocess.Popen(_argv("HOOK_BUDGET_S=2"), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=_env(tmp_path / "st"))
    proc.stdin.write(b'{"tool_name": "Bash", "tool_input": {"command": ')    # stdin stays open: the read blocks
    proc.stdin.flush()
    t0 = time.monotonic()
    try:
        rc = proc.wait(timeout=15)
    finally:
        if proc.poll() is None:
            proc.kill()
    waited = time.monotonic() - t0
    out, errout = proc.stdout.read(), proc.stderr.read()
    proc.stdin.close()
    assert (rc, out, errout) == (0, b"", b"")
    assert 1.5 < waited < 10, waited               # it waited for the alarm, then gave up with no output


@pytest.mark.parametrize("raw", [
    b"", b"not json", b"[1, 2]", b"\xff\xfe", b'{"tool_name": "Grep"}', b'{"tool_name": "Grep", "tool_input": []}',
    b'{"tool_name": "Grep", "tool_input": {"pattern": 5}}', b'{"tool_name": "Bash", "tool_input": {"command": 7}}',
    b'{"tool_name": "Bash", "tool_input": {"command": "echo \'unterminated && x &"}}',
    b'{"tool_name": "Read", "tool_input": {"file_path": "/etc/hosts"}}',
])
def test_a_malformed_or_foreign_payload_fails_open(tmp_path, raw):
    assert_silent_pass(run(None, tmp_path / "st", raw=raw))


def test_the_off_switch_file_and_environment(tmp_path):
    st = tmp_path / "st"
    st.mkdir()
    (st / "intercept-off").write_text("")
    assert_silent_pass(run(grep("our_hooks", "scripts"), st))
    assert_silent_pass(run(bash(QUIRKS["rev-parse-two"][0]), st))
    for p in (grep("our_hooks", "scripts"), bash(QUIRKS["rev-parse-two"][0])):
        assert_silent_pass(run(p, tmp_path / "st2", env=_env(tmp_path / "st2", AF_SEARCH_INTERCEPT="0")))
    assert run(bash(QUIRKS["rev-parse-two"][0]), tmp_path / "st3").returncode == 2    # the control: switch absent


def test_a_state_that_cannot_be_written_never_blocks(tmp_path):
    (tmp_path / "afile").write_text("x")
    assert_silent_pass(run(bash(QUIRKS["rev-parse-two"][0]), tmp_path / "afile" / "st"))


def test_the_seen_file_is_0600_and_old_entries_are_pruned(tmp_path):
    st = tmp_path / "st"
    st.mkdir()
    now = 50_000.0
    (st / "intercept-seen.json").write_text(json.dumps({"old": now - 700, "mid": now - 300}))
    assert si.decide(bash(QUIRKS["rev-parse-two"][0]), str(st), None, now=now)[0] == 2
    data = json.loads((st / "intercept-seen.json").read_text())
    assert "old" not in data and data["mid"] == now - 300 and len(data) == 2
    assert (st / "intercept-seen.json").stat().st_mode & 0o777 == 0o600
    assert not [p for p in st.iterdir() if p.name.endswith(".tmp")]


# ---------------------------------------------------------------- the CI tool set (VERIFY-JT3 F-4)

def _path_without(tmp_path, drop):
    """A PATH holding every command of this one except those named in `drop`: the tool set of a runner with no graft
    (stage0-ci installs none), or with neither graft nor rg."""
    farm = tmp_path / ("bin-without-" + "-".join(drop))
    farm.mkdir()
    for d in os.environ.get("PATH", "").split(os.pathsep):
        for name in (os.listdir(d) if os.path.isdir(d) else ()):
            src = os.path.join(d, name)
            if name not in drop and not (farm / name).exists() and os.path.isfile(src) and os.access(src, os.X_OK):
                (farm / name).symlink_to(src)
    return str(farm)


@pytest.mark.skipif(os.environ.get("SEARCH_INTERCEPT_INNER_RUN") == "1", reason="the inner run of this very test")
@pytest.mark.parametrize("drop", [("graft",), ("graft", "rg")], ids=["no-graft", "no-graft-no-rg"])
def test_the_pair_passes_where_graft_or_rg_is_absent(tmp_path, drop):
    """F-4: the two hook suites pass on a runner without graft (CI), or without graft and rg: a test that needs a
    missing tool skips LOUDLY, and every other test still runs."""
    path = _path_without(tmp_path, drop)
    assert all(shutil.which(tool, path=path) is None for tool in drop)     # de-vacuous: the dropped tools are gone
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_search_intercept.py", "tests/test_session_hooks.py",
                        "-q", "-rs", "-p", "no:cacheprovider", "--basetemp", str(tmp_path / "bt")],
                       cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600,
                       env=dict(os.environ, PATH=path, SEARCH_INTERCEPT_INNER_RUN="1"))
    summary = r.stdout.rstrip("\n").split("\n")[-1]
    assert r.returncode == 0 and "failed" not in summary and "error" not in summary, r.stdout[-3000:]
    assert "LOUD SKIP" in r.stdout and " passed" in summary, summary
