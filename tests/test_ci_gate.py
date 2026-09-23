"""The push gate that reads the branch's last stage0-ci verdict (scripts/ci_gate.py, AF-AP-126).

Owner 2026-09-23: every push onto a red head mailed a failure notice, and the procedural rule
"read the run before the next push" was forgotten twice. The gate refuses while the verdict is
red unless the push names the red run it fixes (CI_FIX=<run id>), and waits (exit 75) while the
verdict is unknown (CI-GATE-R1, issue #34). The push_clean tests drive the real push_clean.sh
against a throwaway origin and prove each refusal happens before anything is pushed.
"""
import email.message
import importlib.util
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "scripts" / "ci_gate.py"
PUSH_CLEAN = REPO / "scripts" / "push_clean.sh"

spec = importlib.util.spec_from_file_location("ci_gate_under_test", GATE)
ci_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_gate)


def run(number, sha, status="completed", conclusion="success", branch="feat", event="push"):
    return {"id": 1000 + number, "run_number": number, "head_sha": sha, "status": status,
            "conclusion": conclusion if status == "completed" else None, "head_branch": branch, "event": event,
            "html_url": f"https://example.invalid/runs/{1000 + number}"}


IN_HISTORY = {"a" * 40, "b" * 40, "c" * 40}
UNFINISHED = ["requested", "queued", "pending", "waiting", "in_progress"]  # the contract's list (C2 f), typed here


def ancestor(sha):
    return sha in IN_HISTORY


def test_success_allows():
    rc, msg = ci_gate.decide([run(7, "c" * 40)], ancestor)
    assert (rc, msg) == (0, "ci-gate: run #7 (ccccccc) passed")


def test_failure_refuses_and_names_the_run():
    rc, msg = ci_gate.decide([run(7, "c" * 40, conclusion="failure"), run(6, "b" * 40)], ancestor)
    assert rc == 1
    assert msg.startswith("REFUSED by ci-gate: run #7 (ccccccc) concluded failure — https://example.invalid/runs/1007\n")
    assert msg.endswith("sets CI_FIX=1007.")


@pytest.mark.parametrize("conclusion", ["timed_out", "startup_failure", "action_required", "neutral", "skipped", "stale"])
def test_every_other_completed_result_refuses(conclusion):
    assert ci_gate.decide([run(7, "c" * 40, conclusion=conclusion)], ancestor)[0] == 1


def test_ci_fix_naming_the_red_run_allows():
    rc, msg = ci_gate.decide([run(7, "c" * 40, conclusion="failure")], ancestor, ci_fix="1007")
    assert (rc, msg) == (0, "ci-gate: run #7 (ccccccc) concluded failure; CI_FIX=1007 declares this push fixes it")


@pytest.mark.parametrize("ci_fix", ["1006", "yes", "007", " 1007x"])
def test_ci_fix_naming_another_run_refuses(ci_fix):
    assert ci_gate.decide([run(7, "c" * 40, conclusion="failure")], ancestor, ci_fix=ci_fix)[0] == 1


@pytest.mark.parametrize("status", UNFINISHED)
def test_unfinished_newest_run_waits(status):
    """F9, by decision: an unfinished verdict run no longer "supersedes" — the push waits for its verdict (75)."""
    runs = [run(7, "c" * 40, status=status), run(6, "b" * 40, conclusion="failure")]
    rc, msg = ci_gate.decide(runs, ancestor)
    assert (rc, msg) == (75, f"WAIT by ci-gate: run #7 (ccccccc) is {status} — https://example.invalid/runs/1007")


def test_cancelled_run_is_skipped_for_the_next_older_verdict():
    runs = [run(7, "c" * 40, conclusion="cancelled"), run(6, "b" * 40, conclusion="failure")]
    assert ci_gate.decide(runs, ancestor)[0] == 1
    runs = [run(7, "c" * 40, conclusion="cancelled"), run(6, "b" * 40)]
    assert ci_gate.decide(runs, ancestor) == (0, "ci-gate: run #6 (bbbbbbb) passed")


def test_run_outside_the_history_is_ignored():
    runs = [run(8, "d" * 40, conclusion="failure"), run(7, "c" * 40)]
    assert ci_gate.decide(runs, ancestor) == (0, "ci-gate: run #7 (ccccccc) passed")
    runs = [run(8, "d" * 40), run(7, "c" * 40, conclusion="failure")]
    assert ci_gate.decide(runs, ancestor)[0] == 1


def test_newest_is_chosen_by_run_number_not_list_order():
    runs = [run(6, "b" * 40), run(7, "c" * 40, conclusion="failure")]
    assert ci_gate.decide(runs, ancestor)[0] == 1


@pytest.mark.parametrize("runs", [[], [run(8, "d" * 40, conclusion="failure")]])
def test_no_run_in_the_history_allows_with_a_note(runs):
    assert ci_gate.decide(runs, ancestor) == (0, "ci-gate: no stage0-ci run in this branch's history; nothing to read")


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    for key in ("CI_FIX", "CI_GATE_OFFLINE", "CI_WAIT_SKIP", "CI_GATE_RUNS_JSON"):
        monkeypatch.delenv(key, raising=False)
    root = tmp_path / "work"
    root.mkdir()
    _git(root, "init", "-q", "-b", "feat")
    (root / "f.txt").write_text("1\n")
    _git(root, "add", "f.txt")
    _git(root, "commit", "-q", "-m", "one")
    return root


def _runs_file(tmp_path, runs, name="runs.json"):
    path = tmp_path / name
    path.write_text(json.dumps({"total_count": len(runs), "workflow_runs": runs}))
    return path


def _cli(root, runs_json, *extra, **env):
    return subprocess.run([sys.executable, str(GATE), "--branch", "feat", "--origin-ref", "HEAD", "--root", str(root),
                           "--runs-json", str(runs_json), *extra], capture_output=True, text=True, env={**os.environ, **env})


def _commit(root, path, text, message="more"):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    _git(root, "add", "--", path)
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def test_cli_refuses_a_red_head_and_allows_the_declared_fix(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, head, conclusion="failure")])
    refused = _cli(repo, runs_json)
    assert refused.returncode == 1
    assert f"REFUSED by ci-gate: run #9 ({head[:7]}) concluded failure" in refused.stderr
    allowed = _cli(repo, runs_json, CI_FIX="1009")
    assert allowed.returncode == 0
    assert "CI_FIX=1009 declares this push fixes it" in allowed.stdout


def test_cli_reads_ancestry_from_git(repo, tmp_path):
    fake = "0123456789abcdef0123456789abcdef01234567"
    result = _cli(repo, _runs_file(tmp_path, [run(9, fake, conclusion="failure")]))
    assert result.returncode == 0
    assert "no stage0-ci run in this branch's history" in result.stdout


@pytest.mark.parametrize("content", [None, "not json", '{"no_runs": []}'])
def test_cli_fails_closed_when_the_runs_cannot_be_read(repo, tmp_path, content):
    runs_json = tmp_path / "runs.json"
    if content is not None:
        runs_json.write_text(content)
    closed = _cli(repo, runs_json)
    assert closed.returncode == 2
    assert "REFUSED by ci-gate: the runs could not be read" in closed.stderr
    offline = _cli(repo, runs_json, CI_GATE_OFFLINE="network down in the test")
    assert offline.returncode == 0
    assert "WARNING: ci-gate could not read the runs" in offline.stderr


def test_push_clean_refuses_before_pushing_onto_a_red_head(repo, tmp_path, monkeypatch):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "origin", "feat")
    red = _git(repo, "rev-parse", "HEAD")
    (repo / "f.txt").write_text("2\n")
    _git(repo, "commit", "-q", "-am", "the fix")
    fix = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, red, conclusion="failure")])
    env = {**os.environ, "PUSH_BRANCH": "feat", "TRANSCRIPT_SYNC": "0", "CI_GATE_RUNS_JSON": str(runs_json),
           "FILTER_BRANCH_SQUELCH_WARNING": "1"}

    refused = subprocess.run(["bash", str(PUSH_CLEAN), "--no-delegates-live"], cwd=repo, env=env,
                             capture_output=True, text=True, timeout=120)
    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert f"REFUSED by ci-gate: run #9 ({red[:7]}) concluded failure" in refused.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == red

    pushed = subprocess.run(["bash", str(PUSH_CLEAN), "--no-delegates-live"], cwd=repo, env={**env, "CI_FIX": "1009"},
                            capture_output=True, text=True, timeout=120)
    assert pushed.returncode == 0, pushed.stdout + pushed.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == fix


# --- CI-GATE-R1 (task #166, issue #34): the contract lines C1-C6 -------------------------------------------------

@pytest.mark.parametrize("status", UNFINISHED)
def test_cli_waits_while_the_verdict_run_is_unfinished(repo, tmp_path, status):
    """C1/C2 f: 75 names the run, the waiter command and the escape; CI_WAIT_SKIP turns it into 0 + a WARNING."""
    head = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, head, status=status), run(8, head, conclusion="failure")])
    waited = _cli(repo, runs_json)
    assert waited.returncode == 75, waited.stdout + waited.stderr
    assert waited.stdout == ""
    assert f"WAIT by ci-gate: run #9 ({head[:7]}) is {status} — https://example.invalid/runs/1009\n" in waited.stderr
    assert (f"Wait for the verdict: python3 scripts/ci_gate.py --branch feat --origin-ref HEAD --root {repo} "
            f"--runs-json {runs_json} --wait 1800\nor push without waiting: CI_WAIT_SKIP=<reason>\n") in waited.stderr
    assert _cli(repo, runs_json, CI_GATE_OFFLINE="the API is down").returncode == 75  # not a read failure
    skipped = _cli(repo, runs_json, CI_WAIT_SKIP="the runner queue is stuck")
    assert skipped.returncode == 0, skipped.stdout + skipped.stderr
    assert (f"WARNING: ci-gate did not wait (run #9 ({head[:7]}) is {status} — https://example.invalid/runs/1009); "
            "pushing anyway: CI_WAIT_SKIP=the runner queue is stuck") in skipped.stderr


@pytest.mark.parametrize("status", [None, 7, "", "weird", "COMPLETED"])
def test_cli_cannot_decide_an_unknown_status(repo, tmp_path, status):
    """C2 d/f: a null or non-string status fails validation; any other string is not a status the gate knows."""
    head = _git(repo, "rev-parse", "HEAD")
    record = run(9, head, status="in_progress")
    record["status"] = status
    runs_json = _runs_file(tmp_path, [record, run(8, head)])
    result = _cli(repo, runs_json)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "REFUSED by ci-gate: the runs could not be read (" in result.stderr
    assert "status" in result.stderr
    assert _cli(repo, runs_json, CI_WAIT_SKIP="in a hurry").returncode == 2  # CI_WAIT_SKIP changes only a 75
    offline = _cli(repo, runs_json, CI_GATE_OFFLINE="the API sent a status we do not know")
    assert offline.returncode == 0
    assert "WARNING: ci-gate could not read the runs (" in offline.stderr


def test_cli_cannot_decide_a_completed_run_with_no_conclusion(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    record = run(9, head)
    record["conclusion"] = None
    runs_json = _runs_file(tmp_path, [record])
    result = _cli(repo, runs_json)
    assert result.returncode == 2
    assert f"run #9 ({head[:7]}) is completed with no conclusion" in result.stderr
    assert _cli(repo, runs_json, CI_GATE_OFFLINE="the API is inconsistent").returncode == 0


def test_ci_wait_skip_changes_only_a_wait(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    red = _cli(repo, _runs_file(tmp_path, [run(9, head, conclusion="failure")]), CI_WAIT_SKIP="in a hurry")
    assert red.returncode == 1
    assert f"REFUSED by ci-gate: run #9 ({head[:7]}) concluded failure" in red.stderr
    unreadable = _cli(repo, tmp_path / "missing.json", CI_WAIT_SKIP="in a hurry")
    assert unreadable.returncode == 2


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_blank_overrides_count_as_unset(repo, tmp_path, blank):
    head = _git(repo, "rev-parse", "HEAD")
    waiting = _runs_file(tmp_path, [run(9, head, status="queued")], "waiting.json")
    red = _runs_file(tmp_path, [run(9, head, conclusion="failure")], "red.json")
    assert _cli(repo, waiting, CI_WAIT_SKIP=blank).returncode == 75
    assert _cli(repo, tmp_path / "missing.json", CI_GATE_OFFLINE=blank).returncode == 2
    assert _cli(repo, red, CI_FIX=blank).returncode == 1


def test_a_padded_ci_fix_allows(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    allowed = _cli(repo, _runs_file(tmp_path, [run(9, head, conclusion="failure")]), CI_FIX=" 1009 ")
    assert allowed.returncode == 0, allowed.stderr
    assert allowed.stdout == f"ci-gate: run #9 ({head[:7]}) concluded failure; CI_FIX=1009 declares this push fixes it\n"


BROKEN_RECORDS = [
    *[pytest.param(lambda r, k=key: r.pop(k), f" has no {key}", id=f"no-{key}")
      for key in ("id", "run_number", "head_sha", "status", "conclusion", "head_branch", "event")],
    pytest.param(lambda r: r.update(run_number="9"), ": run_number is '9', not an integer", id="run_number-str"),
    pytest.param(lambda r: r.update(run_number=True), ": run_number is True, not an integer", id="run_number-bool"),
    pytest.param(lambda r: r.update(id=True), ": id is True, not an integer", id="id-bool"),
    pytest.param(lambda r: r.update(head_sha=r["head_sha"][:7]), ": head_sha is '", id="head_sha-short"),
    pytest.param(lambda r: r.update(head_sha=r["head_sha"].upper()), ": head_sha is '", id="head_sha-upper"),
    pytest.param(lambda r: r.update(head_sha="--help"), ": head_sha is '--help', not 40 lowercase hex", id="head_sha-option"),
    pytest.param(lambda r: r.update(conclusion=0), ": conclusion is 0, not a string or null", id="conclusion-int"),
    pytest.param(lambda r: r.update(head_branch="main"), ": head_branch is 'main', not 'feat'", id="head_branch-foreign"),
    pytest.param(lambda r: r.update(event="pull_request"), ": event is 'pull_request', not 'push'", id="event-pr"),
]


@pytest.mark.parametrize("mutate, detail", BROKEN_RECORDS)
def test_cli_validates_every_record_before_deciding(repo, tmp_path, mutate, detail):
    """C2 d (F6, F7, F19, F22): a green run on the head, broken in one field — never a traceback, never an allow."""
    head = _git(repo, "rev-parse", "HEAD")
    record = run(9, head)
    mutate(record)
    runs_json = _runs_file(tmp_path, [record])
    result = _cli(repo, runs_json)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "REFUSED by ci-gate: the runs could not be read (workflow_runs[0]" in result.stderr
    assert detail in result.stderr
    assert "Traceback" not in result.stderr
    offline = _cli(repo, runs_json, CI_GATE_OFFLINE="the API sent a bad page")
    assert offline.returncode == 0
    assert "WARNING: ci-gate could not read the runs (workflow_runs[0]" in offline.stderr


@pytest.mark.parametrize("payload, detail", [
    ({"workflow_runs": {}}, "the payload carries no workflow_runs list"),
    ([], "the payload carries no workflow_runs list"),
    ({"workflow_runs": ["x"]}, "workflow_runs[0] is not an object"),
])
def test_cli_refuses_a_payload_without_a_run_list(repo, tmp_path, payload, detail):
    runs_json = tmp_path / "runs.json"
    runs_json.write_text(json.dumps(payload))
    result = _cli(repo, runs_json)
    assert result.returncode == 2
    assert detail in result.stderr


def test_cli_refuses_a_repeated_run_number(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    result = _cli(repo, _runs_file(tmp_path, [run(9, head), run(9, head, conclusion="failure")]))
    assert result.returncode == 2
    assert "workflow_runs[1] (id 1009): run_number 9 repeats workflow_runs[0]" in result.stderr


def test_cli_refuses_an_origin_ref_that_is_not_a_commit(repo, tmp_path):
    """C2 b: the landed gate read a missing origin ref as "no run in the history" and allowed."""
    head = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, head)])
    for env in ({}, {"CI_GATE_OFFLINE": "a local git failure is never rescued"}):
        result = _cli(repo, runs_json, "--origin-ref", "refs/remotes/origin/feat", **env)
        assert result.returncode == 2, result.stdout + result.stderr
        assert ("REFUSED by ci-gate: the origin ref 'refs/remotes/origin/feat' does not resolve to a commit"
                in result.stderr)


def test_cli_refuses_a_shallow_clone_even_offline(repo, tmp_path):
    """C2 a: a real `git clone --depth 1` (file://: a local-path clone ignores --depth)."""
    _commit(repo, "f.txt", "2\n")
    clone = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(clone)], check=True, capture_output=True)
    assert _git(clone, "rev-parse", "--is-shallow-repository") == "true"
    runs_json = _runs_file(tmp_path, [run(9, _git(clone, "rev-parse", "HEAD"))])  # green on the clone's head
    for env in ({}, {"CI_GATE_OFFLINE": "a local git failure is never rescued"}):
        result = _cli(clone, runs_json, **env)
        assert result.returncode == 2, result.stdout + result.stderr
        assert "REFUSED by ci-gate: this clone is shallow" in result.stderr
        assert "git fetch --unshallow origin" in result.stderr


def test_cli_refuses_when_git_cannot_walk_the_history(repo, tmp_path, monkeypatch):
    """C2 e: a red run on a TRUE ancestor while a parent object is missing. git's walk is ordered by commit date: with
    the two commits in the same second, git 2.43 reads the red commit's missing parent first and answers exit 1 with
    `error: Could not read …` (measured); read as "not in history", the red verdict would be skipped. (One second
    apart, it proves the ancestry first and answers 0 — sound, and the reason the dates are pinned here.)"""
    monkeypatch.setenv("GIT_AUTHOR_DATE", "2026-09-23T00:00:00+00:00")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-09-23T00:00:00+00:00")
    root_commit = _git(repo, "rev-parse", "HEAD")
    red = _commit(repo, "f.txt", "2\n")
    _commit(repo, "f.txt", "3\n")
    (repo / ".git" / "objects" / root_commit[:2] / root_commit[2:]).unlink()
    runs_json = _runs_file(tmp_path, [run(9, red, conclusion="failure")])
    for env in ({}, {"CI_GATE_OFFLINE": "a local git failure is never rescued"}):
        result = _cli(repo, runs_json, **env)
        assert result.returncode == 2, result.stdout + result.stderr
        assert f"REFUSED by ci-gate: git cannot tell whether commit {red} is in the history of" in result.stderr


def test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses(repo, tmp_path, monkeypatch, capsys):
    """C2 e: exit 128 with the commit present is "cannot tell" (2), never "not in history". git 2.43 did not
    produce that pair in any probe here, so the exit code is injected at the git seam; everything else is real git."""
    head = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, head, conclusion="failure")])
    real = ci_gate._git

    def git(root, *args):
        if args[:2] == ("merge-base", "--is-ancestor"):
            return 128, "", "fatal: the walk failed\n"
        return real(root, *args)

    monkeypatch.setattr(ci_gate, "_git", git)
    rc = ci_gate.main(["--branch", "feat", "--origin-ref", "HEAD", "--root", str(repo), "--runs-json", str(runs_json)])
    err = capsys.readouterr().err
    assert rc == 2, err
    assert f"git cannot tell whether commit {head} is in the history of" in err
    assert "merge-base --is-ancestor exited 128 (fatal: the walk failed)" in err


def test_a_code_push_after_the_green_run_waits_for_its_run(repo, tmp_path):
    """C2 f, the expected-run check: the newest REGISTERED run is the previous head's (premise probe 4)."""
    green = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "transcripts/sandbox/digest.md", "a digest\n")
    _commit(repo, "code.py", "print(2)\n")
    result = _cli(repo, _runs_file(tmp_path, [run(9, green)]))
    assert result.returncode == 75, result.stdout + result.stderr
    assert (f"WAIT by ci-gate: the pushes after run #9 ({green[:7]}), which concluded success, change code.py "
            "and no newer run is registered yet\n") in result.stderr


def test_a_transcripts_only_push_keeps_the_green_verdict(repo, tmp_path):
    green = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "transcripts/sandbox/2026-09-23.md", "a digest\n")
    _commit(repo, "transcripts/é.md", "a non-ASCII name: git quotes it without -z\n")
    result = _cli(repo, _runs_file(tmp_path, [run(9, green)]))
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"ci-gate: run #9 ({green[:7]}) passed\n"


def test_a_rename_out_of_code_into_transcripts_waits(repo, tmp_path):
    """--no-renames: by default the rename shows only its new path, transcripts/a.py (premise probe 5)."""
    green = _commit(repo, "code/a.py", "print(1)\n")
    (repo / "transcripts").mkdir()
    _git(repo, "mv", "code/a.py", "transcripts/a.py")
    _git(repo, "commit", "-q", "-m", "move")
    result = _cli(repo, _runs_file(tmp_path, [run(9, green)]))
    assert result.returncode == 75, result.stdout + result.stderr
    assert f"the pushes after run #9 ({green[:7]}), which concluded success, change code/a.py" in result.stderr


def test_a_red_run_followed_by_a_transcripts_only_push_refuses(repo, tmp_path):
    red = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "transcripts/sandbox/2026-09-23.md", "a digest\n")
    result = _cli(repo, _runs_file(tmp_path, [run(9, red, conclusion="failure")]))
    assert result.returncode == 1
    assert f"REFUSED by ci-gate: run #9 ({red[:7]}) concluded failure" in result.stderr


def test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled(repo, tmp_path):
    """VERIFY-CI-GATE F12, closed by the expected-run check coming before CI_FIX (C2 f): the fix push changed code and
    its run was cancelled by hand, so the red run is the verdict run again — but the pushes after it changed code."""
    red = _git(repo, "rev-parse", "HEAD")
    fix = _commit(repo, "code.py", "the fix\n")
    runs_json = _runs_file(tmp_path, [run(10, fix, conclusion="cancelled"), run(9, red, conclusion="failure")])
    result = _cli(repo, runs_json, CI_FIX="1009")
    assert result.returncode == 75, result.stdout + result.stderr
    assert f"the pushes after run #9 ({red[:7]}), which concluded failure, change code.py" in result.stderr


@pytest.mark.parametrize("count, rc", [(50, 2), (49, 0)])
def test_a_full_page_without_a_verdict_cannot_decide(repo, tmp_path, count, rc):
    """C2 g (F11): 50 records and none decides — the verdict may be on the next page."""
    runs = [run(n, f"{n:040x}", conclusion="failure") for n in range(1, count + 1)]  # absent commits: not in history
    runs_json = _runs_file(tmp_path, runs)
    result = _cli(repo, runs_json)
    assert result.returncode == rc, result.stdout + result.stderr
    if rc:
        assert "REFUSED by ci-gate: the runs could not be read (no verdict in the newest 50 runs" in result.stderr
        assert _cli(repo, runs_json, CI_GATE_OFFLINE="the page is the API's data").returncode == 0
    else:
        assert result.stdout == "ci-gate: no stage0-ci run in this branch's history; nothing to read\n"


class FakeUrlopen:
    def __init__(self, respond):
        self.calls, self.respond = [], respond

    def __call__(self, url, timeout=None):
        self.calls.append((url, timeout))
        return self.respond(url)


def _body(payload):
    return io.BytesIO(json.dumps(payload).encode())


def _raise(exc):
    def respond(url):
        raise exc
    return respond


def _http_error(code, reason, headers=()):
    message = email.message.Message()
    for name, value in headers:
        message[name] = value
    return urllib.error.HTTPError("https://api.github.com/x", code, reason, message, io.BytesIO(b"{}"))


@pytest.mark.parametrize("branch", ["fix#1", "fix&y", "claude/x", "feat-é"])
def test_the_runs_query_is_encoded(monkeypatch, branch):
    """C3 (F6): every legal ref name reaches the API as the branch it is, with event=push and per_page=50."""
    fake = FakeUrlopen(lambda url: _body({"workflow_runs": []}))
    monkeypatch.setattr(ci_gate.urllib.request, "urlopen", fake)
    assert ci_gate.fetch_runs("o/r", branch) == {"workflow_runs": []}
    (url, timeout), = fake.calls
    parts = urllib.parse.urlsplit(url)
    assert url.isascii()
    assert (parts.scheme, parts.netloc, parts.path, parts.fragment) == (
        "https", "api.github.com", "/repos/o/r/actions/workflows/stage0-ci.yml/runs", "")
    assert urllib.parse.parse_qs(parts.query, strict_parsing=True) == {
        "branch": [branch], "event": ["push"], "per_page": ["50"]}
    assert timeout == 20


@pytest.fixture
def github_repo(repo):
    _git(repo, "remote", "add", "origin", "https://github.com/o/r")  # nothing is fetched: urlopen is replaced
    return repo


def _gate(root, *extra):
    return ci_gate.main(["--branch", "feat", "--origin-ref", "HEAD", "--root", str(root), *extra])


def test_the_api_verdict_decides(github_repo, monkeypatch, capsys):
    head = _git(github_repo, "rev-parse", "HEAD")
    fake = FakeUrlopen(lambda url: _body({"total_count": 1, "workflow_runs": [run(9, head, conclusion="failure")]}))
    monkeypatch.setattr(ci_gate.urllib.request, "urlopen", fake)
    assert _gate(github_repo) == 1
    assert f"REFUSED by ci-gate: run #9 ({head[:7]}) concluded failure" in capsys.readouterr().err
    assert fake.calls[0][0].startswith("https://api.github.com/repos/o/r/actions/workflows/stage0-ci.yml/runs?")


@pytest.mark.parametrize("error, detail", [
    (_http_error(403, "Forbidden", [("X-RateLimit-Remaining", "0")]),
     "HTTP Error 403: Forbidden; X-RateLimit-Remaining: 0"),
    (_http_error(404, "Not Found"), "HTTP Error 404: Not Found)"),
    (_http_error(500, "Internal Server Error"), "HTTP Error 500: Internal Server Error)"),
    (urllib.error.URLError("no route to host"), "URLError: <urlopen error no route to host>"),
    (socket.timeout("timed out"), "timed out"),
], ids=["403-rate-limit", "404", "500", "urlerror", "timeout"])
def test_an_unreadable_api_cannot_decide(github_repo, monkeypatch, capsys, error, detail):
    """C3 (F4, F17): each read failure is a named 2; CI_GATE_OFFLINE turns it into 0 with a WARNING."""
    monkeypatch.setattr(ci_gate.urllib.request, "urlopen", FakeUrlopen(_raise(error)))
    assert _gate(github_repo) == 2
    err = capsys.readouterr().err
    assert "REFUSED by ci-gate: the runs could not be read (" in err
    assert detail in err
    monkeypatch.setenv("CI_GATE_OFFLINE", "the API is down")
    assert _gate(github_repo) == 0
    assert "WARNING: ci-gate could not read the runs (" in capsys.readouterr().err


@pytest.mark.parametrize("url", ["https://github.com/o/r", "https://github.com/o/r.git", "https://github.com/o/r/",
                                 "git@github.com:o/r.git", "ssh://git@github.com/o/r.git"])
def test_repo_slug_reads_each_github_form(repo, url):
    _git(repo, "remote", "add", "origin", url)
    assert ci_gate.repo_slug(str(repo)) == "o/r"


@pytest.mark.parametrize("url", ["https://gitlab.example/o/r.git", "https://notgithub.com/o/r",
                                 "https://user:s3cret@gitlab.example/o/r.git"])
def test_a_non_github_origin_cannot_decide(repo, monkeypatch, capsys, url):
    _git(repo, "remote", "add", "origin", url)
    fake = FakeUrlopen(lambda url: _body({"workflow_runs": []}))
    monkeypatch.setattr(ci_gate.urllib.request, "urlopen", fake)
    assert _gate(repo) == 2
    err = capsys.readouterr().err
    assert "REFUSED by ci-gate: the runs could not be read (origin is not a github.com remote: " in err
    assert "s3cret" not in err
    assert fake.calls == []


@pytest.mark.parametrize("url", ["https://github.com/o/r", "git@github.com:o/r.git"])
def test_runs_json_never_decides_against_a_github_origin(repo, tmp_path, url):
    """C2 c (F5): a test input left exported can never decide a real push."""
    _git(repo, "remote", "add", "origin", url)
    result = _cli(repo, _runs_file(tmp_path, [run(9, _git(repo, "rev-parse", "HEAD"))]))
    assert result.returncode == 64, result.stdout + result.stderr
    assert "ci_gate.py: error: --runs-json is a test input and origin is a github.com remote" in result.stderr
    assert result.stdout == ""


def test_runs_json_with_a_local_origin_says_so_on_stderr(repo, tmp_path):
    _git(tmp_path, "init", "-q", "--bare", str(tmp_path / "o.git"))
    _git(repo, "remote", "add", "origin", str(tmp_path / "o.git"))
    head = _git(repo, "rev-parse", "HEAD")
    runs_json = _runs_file(tmp_path, [run(9, head)])
    result = _cli(repo, runs_json)
    assert result.returncode == 0
    assert f"WARNING: ci-gate: runs read from {runs_json} (a test input), not the Actions API\n" in result.stderr
    assert result.stdout == f"ci-gate: run #9 ({head[:7]}) passed\n"


@pytest.mark.parametrize("argv", [[], ["--branch"], ["--branch", "feat", "--no-such-flag"],
                                  ["--branch", "feat", "--wait", "-1"], ["--branch", "feat", "--wait", "soon"]])
def test_usage_errors_exit_64(argv):
    """C1 (F8): a usage error is 64, never 2 ("cannot decide")."""
    result = subprocess.run([sys.executable, str(GATE), *argv], capture_output=True, text=True)
    assert result.returncode == 64, result.stdout + result.stderr
    assert "ci_gate.py: error:" in result.stderr


class Clock:
    """The waiter's sleep and clock: each sleep advances the time, then moves the scenario to its next state."""

    def __init__(self, states, write, bound=200):
        self.t, self.slept, self.states, self.write, self.bound = 0.0, [], list(states), write, bound

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        assert len(self.slept) <= self.bound, "the waiter ignored its deadline"
        self.t += seconds
        if self.states:
            self.write(self.states.pop(0))


@pytest.fixture
def waiter(repo, tmp_path, monkeypatch):
    """start(first, *later, seconds=…) -> (rc, clock): an in-process wait; the runs file changes at each sleep."""
    runs_json = tmp_path / "runs.json"

    def write(state):
        runs_json.write_text(state if isinstance(state, str) else json.dumps({"workflow_runs": state}))

    def start(first, *later, seconds=3600):
        clock = Clock(later, write)
        write(first)
        monkeypatch.setattr(ci_gate, "_sleep", clock.sleep)
        monkeypatch.setattr(ci_gate, "_now", clock.now)
        rc = ci_gate.main(["--branch", "feat", "--origin-ref", "HEAD", "--root", str(repo),
                           "--runs-json", str(runs_json), "--wait", str(seconds)])
        return rc, clock

    return start


def _lines(stream):
    return [line for line in stream.splitlines() if not line.startswith("WARNING: ci-gate: runs read from")]


@pytest.mark.parametrize("repeat", [False, True], ids=["three-polls", "a-repeated-state"])
def test_the_waiter_follows_a_push_to_its_verdict(repo, waiter, capsys, repeat):
    """C4: [no newer run registered] -> [in_progress] -> [success]; one line per state change."""
    green = _git(repo, "rev-parse", "HEAD")
    head = _commit(repo, "code.py", "print(2)\n")
    states = [[run(9, green)], [run(10, head, status="in_progress"), run(9, green)], [run(10, head), run(9, green)]]
    if repeat:
        states.insert(1, states[0])
    rc, clock = waiter(*states)
    out, err = capsys.readouterr()
    assert rc == 0, err
    assert clock.slept == [30] * (len(states) - 1)
    assert _lines(err) == [
        f"WAIT by ci-gate: the pushes after run #9 ({green[:7]}), which concluded success, change code.py "
        "and no newer run is registered yet",
        f"WAIT by ci-gate: run #10 ({head[:7]}) is in_progress — https://example.invalid/runs/1010"]
    assert out == f"ci-gate: run #10 ({head[:7]}) passed\n"


def test_the_waiter_lists_the_failed_jobs_of_a_red_verdict(repo, waiter, capsys, monkeypatch):
    head = _git(repo, "rev-parse", "HEAD")
    jobs = {"jobs": [{"id": 501, "name": "tests", "conclusion": "failure"},
                     {"id": 502, "name": "planning", "conclusion": "success"},
                     {"id": 503, "name": "stage1-gate", "conclusion": "failure"}]}
    fake = FakeUrlopen(lambda url: _body(jobs))
    monkeypatch.setattr(ci_gate.urllib.request, "urlopen", fake)
    monkeypatch.setattr(ci_gate, "repo_slug", lambda root: "o/r")
    rc, clock = waiter([run(9, head, status="queued")], [run(9, head, conclusion="failure")])
    err = capsys.readouterr().err
    assert rc == 1, err
    assert clock.slept == [30]
    assert [url for url, _ in fake.calls] == ["https://api.github.com/repos/o/r/actions/runs/1009/jobs?per_page=100"]
    assert f"REFUSED by ci-gate: run #9 ({head[:7]}) concluded failure" in err
    assert err.endswith("  failed job: tests (id 501)\n  failed job: stage1-gate (id 503)\n")


def test_the_waiter_keeps_the_red_verdict_when_the_jobs_cannot_be_read(repo, waiter, capsys):
    head = _git(repo, "rev-parse", "HEAD")
    rc, _ = waiter([run(9, head, conclusion="failure")])  # the repo has no origin: the jobs read fails
    err = capsys.readouterr().err
    assert rc == 1
    assert _lines(err)[-1] == "WARNING: ci-gate could not read the failed jobs of run #9 (there is no origin remote)"


def test_the_waiter_stops_at_its_deadline(repo, waiter, capsys):
    head = _git(repo, "rev-parse", "HEAD")
    rc, clock = waiter([run(9, head, status="in_progress")], seconds=100)
    err = capsys.readouterr().err
    assert rc == 75, err
    assert clock.slept == [30, 30, 30, 10]
    assert err.count(f"WAIT by ci-gate: run #9 ({head[:7]}) is in_progress") == 1
    assert (f"WAIT by ci-gate: 100 s passed and the verdict is still unknown: run #9 ({head[:7]}) is in_progress"
            in err)
    assert "--wait 1800\nor push without waiting: CI_WAIT_SKIP=<reason>\n" in err


def test_the_waiter_retries_a_failed_read(repo, waiter, capsys):
    head = _git(repo, "rev-parse", "HEAD")
    rc, clock = waiter("not json", "not json", [run(9, head)])
    out, err = capsys.readouterr()
    assert rc == 0, err
    assert clock.slept == [30, 30]
    assert [line.split(" (")[0] for line in _lines(err)] == ["WAIT by ci-gate: the runs could not be read"] * 2
    assert _lines(err)[1].endswith("retry 2 of 2")
    assert out == f"ci-gate: run #9 ({head[:7]}) passed\n"


def test_the_waiter_gives_up_after_three_failed_reads_in_a_row(repo, waiter, capsys):
    head = _git(repo, "rev-parse", "HEAD")
    rc, clock = waiter([run(9, head, status="queued")], "not json", "not json", "not json")
    err = capsys.readouterr().err
    assert rc == 2, err
    assert clock.slept == [30, 30, 30]
    assert "REFUSED by ci-gate: the runs could not be read (JSONDecodeError: " in err
    assert "3 read(s) in a row failed while waiting" in err


def test_a_good_read_resets_the_waiters_failure_count(repo, waiter):
    head = _git(repo, "rev-parse", "HEAD")
    rc, clock = waiter("not json", [run(9, head, status="queued")], "not json", "not json", [run(9, head)])
    assert rc == 0
    assert clock.slept == [30, 30, 30, 30]


def test_the_waiter_ignores_the_push_overrides(repo, waiter, capsys, monkeypatch):
    """C4: the waiter reports the run's verdict, not a push decision."""
    head = _git(repo, "rev-parse", "HEAD")
    monkeypatch.setenv("CI_FIX", "1009")
    monkeypatch.setenv("CI_WAIT_SKIP", "in a hurry")
    monkeypatch.setenv("CI_GATE_OFFLINE", "no network")
    rc, _ = waiter([run(9, head, conclusion="failure")])
    assert rc == 1
    assert ("ci-gate: --wait ignores CI_FIX=1009, CI_WAIT_SKIP=in a hurry, CI_GATE_OFFLINE=no network: "
            "the waiter reports the run's verdict, not a push decision") in capsys.readouterr().err
    assert waiter([run(9, head, status="in_progress")], seconds=0)[0] == 75
    assert waiter("not json", seconds=0)[0] == 2


def _origin(repo, tmp_path):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "origin", "feat")
    return origin


def _push_clean(root, runs_json, *mode, script=PUSH_CLEAN, **env):
    return subprocess.run(["bash", str(script), *(mode or ("--no-delegates-live",))], cwd=root, capture_output=True,
                          text=True, timeout=120,
                          env={**os.environ, "PUSH_BRANCH": "feat", "TRANSCRIPT_SYNC": "0",
                               "FILTER_BRANCH_SQUELCH_WARNING": "1", "CI_GATE_RUNS_JSON": str(runs_json), **env})


def test_push_clean_waits_for_an_unfinished_verdict(repo, tmp_path):
    """C5: 75 passes through and nothing is pushed; CI_WAIT_SKIP pushes with its WARNING."""
    origin = _origin(repo, tmp_path)
    pushed = _git(repo, "rev-parse", "HEAD")
    local = _commit(repo, "f.txt", "2\n")
    runs_json = _runs_file(tmp_path, [run(9, pushed, status="in_progress")])
    waited = _push_clean(repo, runs_json)
    assert waited.returncode == 75, waited.stdout + waited.stderr
    assert f"WAIT by ci-gate: run #9 ({pushed[:7]}) is in_progress" in waited.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == pushed
    skipped = _push_clean(repo, runs_json, CI_WAIT_SKIP="the runner queue is stuck")
    assert skipped.returncode == 0, skipped.stdout + skipped.stderr
    assert "WARNING: ci-gate did not wait (run #9" in skipped.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == local


def test_push_clean_passes_cannot_decide_through(repo, tmp_path):
    origin = _origin(repo, tmp_path)
    pushed = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "f.txt", "2\n")
    result = _push_clean(repo, tmp_path / "missing.json")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "REFUSED by ci-gate: the runs could not be read (FileNotFoundError: " in result.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == pushed


def test_push_clean_refuses_a_stale_origin_ref(repo, tmp_path):
    """C5 (F1): a fetch refspec narrowed to another branch leaves refs/remotes/origin/feat at the old green head
    while origin moved to a red one; the landed gate read the old green and pushed."""
    origin = _origin(repo, tmp_path)
    green = _git(repo, "rev-parse", "HEAD")
    _git(repo, "config", "remote.origin.fetch", "+refs/heads/main:refs/remotes/origin/main")
    red = _commit(repo, "f.txt", "2\n")
    _git(repo, "push", "-q", "origin", "HEAD:refs/heads/feat")
    assert _git(repo, "rev-parse", "refs/remotes/origin/feat") == green
    _commit(repo, "f.txt", "3\n")
    result = _push_clean(repo, _runs_file(tmp_path, [run(9, red, conclusion="failure"), run(8, green)]))
    assert result.returncode == 2, result.stdout + result.stderr
    assert "the fetch refspec (remote.origin.fetch) does not map the branch there" in result.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == red


def test_push_clean_reads_the_full_remote_ref_not_a_local_origin_branch(repo, tmp_path):
    """C5 (F1): a local branch named origin/feat shadows the short name origin/feat."""
    origin = _origin(repo, tmp_path)
    green = _git(repo, "rev-parse", "HEAD")
    red = _commit(repo, "f.txt", "2\n")
    _git(repo, "push", "-q", "origin", "feat")
    _git(repo, "branch", "origin/feat", green)
    _commit(repo, "f.txt", "3\n")
    result = _push_clean(repo, _runs_file(tmp_path, [run(9, red, conclusion="failure"), run(8, green)]))
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"REFUSED by ci-gate: run #9 ({red[:7]}) concluded failure" in result.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == red


def _worktrees(repo):
    return [line for line in _git(repo, "worktree", "list", "--porcelain").splitlines() if line.startswith("worktree ")]


@pytest.fixture
def lanes(repo, tmp_path):
    """A repo that COMMITS the scripts under test, pushed to a throwaway origin whose head's run is red, with a
    declared live lane file dirty. A worktree a mutant leaks is removed after the test."""
    (repo / "scripts").mkdir()
    shutil.copy(PUSH_CLEAN, repo / "scripts" / "push_clean.sh")
    shutil.copy(GATE, repo / "scripts" / "ci_gate.py")
    (repo / "lane.txt").write_text("lane\n")
    _git(repo, "add", "scripts", "lane.txt")
    _git(repo, "commit", "-q", "-m", "the scripts under test")
    origin = _origin(repo, tmp_path)
    red = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "f.txt", "2\n")
    (repo / ".lanes-live").write_text("lane.txt\nscripts/ci_gate.py\n")
    (repo / "lane.txt").write_text("a live lane's edit\n")
    yield origin, red, _runs_file(tmp_path, [run(9, red, conclusion="failure")])
    for line in _worktrees(repo)[1:]:
        path = line.split(" ", 1)[1]
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", path], capture_output=True)
        shutil.rmtree(path, ignore_errors=True)


def test_push_clean_lanes_live_refusal_leaves_no_worktree(repo, lanes):
    """C5 (F2): `( … ); rc=$?` under errexit skipped the cleanup and leaked the detached worktree."""
    origin, red, runs_json = lanes
    result = _push_clean(repo, runs_json, "--lanes-live", script="scripts/push_clean.sh")
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"REFUSED by ci-gate: run #9 ({red[:7]}) concluded failure" in result.stderr
    assert len(_worktrees(repo)) == 1, _worktrees(repo)
    assert _git(origin, "rev-parse", "refs/heads/feat") == red
    assert (repo / "lane.txt").read_text() == "a live lane's edit\n"


def test_push_clean_lanes_live_runs_the_committed_gate(repo, lanes):
    """C5 (F20): a lane's dirty copy of the gate that allows everything does not decide the push."""
    origin, red, runs_json = lanes
    (repo / "scripts" / "ci_gate.py").write_text("import sys\nsys.exit(0)\n")
    result = _push_clean(repo, runs_json, "--lanes-live", script="scripts/push_clean.sh")
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"REFUSED by ci-gate: run #9 ({red[:7]}) concluded failure" in result.stderr
    assert _git(origin, "rev-parse", "refs/heads/feat") == red
