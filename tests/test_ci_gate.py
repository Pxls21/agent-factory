"""The push gate that reads the branch's last stage0-ci verdict (scripts/ci_gate.py, AF-AP-126).

Owner 2026-09-23: every push onto a red head mailed a failure notice, and the procedural rule
"read the run before the next push" was forgotten twice. The gate refuses while the verdict is
red unless the push names the red run it fixes (CI_FIX=<run id>). The last test drives the real
push_clean.sh against a throwaway origin and proves the refusal happens before anything is pushed.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "scripts" / "ci_gate.py"
PUSH_CLEAN = REPO / "scripts" / "push_clean.sh"

spec = importlib.util.spec_from_file_location("ci_gate_under_test", GATE)
ci_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_gate)


def run(number, sha, status="completed", conclusion="success"):
    return {"id": 1000 + number, "run_number": number, "head_sha": sha, "status": status,
            "conclusion": conclusion if status == "completed" else None,
            "html_url": f"https://example.invalid/runs/{1000 + number}"}


IN_HISTORY = {"a" * 40, "b" * 40, "c" * 40}


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


@pytest.mark.parametrize("status", ["queued", "in_progress", "waiting"])
def test_unfinished_newest_run_allows(status):
    runs = [run(7, "c" * 40, status=status), run(6, "b" * 40, conclusion="failure")]
    rc, msg = ci_gate.decide(runs, ancestor)
    assert (rc, msg) == (0, f"ci-gate: run #7 (ccccccc) is {status}; this push supersedes it")


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
    monkeypatch.delenv("CI_FIX", raising=False)
    monkeypatch.delenv("CI_GATE_OFFLINE", raising=False)
    root = tmp_path / "work"
    root.mkdir()
    _git(root, "init", "-q", "-b", "feat")
    (root / "f.txt").write_text("1\n")
    _git(root, "add", "f.txt")
    _git(root, "commit", "-q", "-m", "one")
    return root


def _runs_file(tmp_path, runs):
    path = tmp_path / "runs.json"
    path.write_text(json.dumps({"total_count": len(runs), "workflow_runs": runs}))
    return path


def _cli(root, runs_json, **env):
    return subprocess.run([sys.executable, str(GATE), "--branch", "feat", "--origin-ref", "HEAD", "--root", str(root),
                           "--runs-json", str(runs_json)], capture_output=True, text=True, env={**os.environ, **env})


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
