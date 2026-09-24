"""scripts/stale_ids.py through the real scripts/push_clean.sh (task #243).

push_clean rewrites every commit of the range that carries a model-identifier trailer, and every commit after it. A
note added in the range that cites one of those commits by its LOCAL id points at nothing on origin (2026-09-24: four
commits cited that way in the ledger, the wiki and the incident log). Each test builds a work repo with a bare origin
and a green CI record for origin's head, then runs the real push_clean.sh.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PUSH_CLEAN = REPO / "scripts" / "push_clean.sh"
TRAILER = "Co-Authored-By: " + "Claude <noreply@example.invalid>"   # built from parts: a fixture, not a trailer
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


def _commit(root, path, text, message):
    (root / path).write_text(text)
    _git(root, "add", "--", path)
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


@pytest.fixture
def work(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    for key in ("CI_FIX", "CI_GATE_OFFLINE", "CI_WAIT_SKIP", "CI_GATE_RUNS_JSON", "STALE_ID_OK"):
        monkeypatch.delenv(key, raising=False)
    root, origin = tmp_path / "work", tmp_path / "origin.git"
    root.mkdir()
    _git(root, "init", "-q", "-b", "feat")
    base = _commit(root, "f.txt", "1\n", "one")
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(root, "remote", "add", "origin", str(origin))
    _git(root, "push", "-q", "origin", "feat")
    runs = tmp_path / "runs.json"
    runs.write_text(json.dumps({"total_count": 1, "workflow_runs": [
        {"id": 1001, "run_number": 1, "head_sha": base, "status": "completed", "conclusion": "success",
         "head_branch": "feat", "event": "push", "html_url": "https://example.invalid/runs/1001"}]}))
    return root, origin, base, runs


def _push(root, runs, **extra):
    env = {**os.environ, "PUSH_BRANCH": "feat", "TRANSCRIPT_SYNC": "0", "CI_GATE_RUNS_JSON": str(runs),
           "FILTER_BRANCH_SQUELCH_WARNING": "1", **extra}
    return subprocess.run(["bash", str(PUSH_CLEAN), "--no-delegates-live"], cwd=root, env=env, capture_output=True,
                          text=True, timeout=120)


def _new_id(root, old):
    """The id the rewrite gave the commit whose subject the old commit had."""
    subject = _git(root, "log", "-1", "--format=%s", old)
    return _git(root, "log", "--format=%H", "--grep", "^%s$" % subject, "-1", "HEAD")


def test_a_note_citing_a_rewritten_commit_is_refused_then_the_new_id_pushes(work):
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "fixed in %s (local)\n" % old[:7], "a note")
    r = _push(root, runs)
    assert r.returncode == 4, r.stdout + r.stderr
    new = _new_id(root, old)
    assert new != old
    assert "stale_ids: notes.md:1 cites %s, a commit this push rewrote; it is %s on origin" % (old[:7], new[:7]) \
        in r.stderr, r.stderr
    assert "REFUSED by stale_ids (rc 4): NOT pushed" in r.stderr and _git(origin, "rev-parse", "feat") == base
    _commit(root, "notes.md", "fixed in %s\n" % new[:7], "the note cites the new id")
    r = _push(root, runs)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(origin, "cat-file", "-t", new) == "commit" and _git(origin, "rev-parse", "feat") == \
        _git(root, "rev-parse", "HEAD")


def test_stale_id_ok_pushes_anyway_and_says_so(work):
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "see %s\n" % old[:10], "a note")
    r = _push(root, runs, STALE_ID_OK="the owner said so")
    assert r.returncode == 0 and "pushing anyway (STALE_ID_OK=the owner said so)" in r.stderr, r.stdout + r.stderr
    assert _git(origin, "rev-parse", "feat") == _git(root, "rev-parse", "HEAD")


def test_citing_a_commit_already_on_origin_or_a_kept_commit_pushes(work):
    root, origin, base, runs = work
    kept = _commit(root, "k.txt", "k\n", "no trailer, before any rewritten commit")
    _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "base %s, kept %s\n" % (base[:7], kept[:8]), "a note")
    r = _push(root, runs)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "stale_ids" not in r.stderr and _git(origin, "cat-file", "-t", kept) == "commit"


def test_a_message_citing_a_rewritten_commit_is_a_warning_only(work):
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "b.txt", "b\n", "follows %s" % old[:7])
    r = _push(root, runs)
    assert r.returncode == 0, r.stdout + r.stderr
    new = _new_id(root, old)
    assert "stale_ids: WARNING: a commit message cites %s, which this push rewrote to %s" % (old[:7], new[:7]) \
        in r.stderr, r.stderr


def test_a_citation_removed_again_in_the_range_and_hex_inside_a_word_are_not_citations(work):
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "see %s\n" % old[:7], "a note citing the local id")
    _commit(root, "notes.md", "x%s is not an id; nor is %sz\n" % (old[:7], old[:7]), "the citation removed")
    r = _push(root, runs)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "stale_ids" not in r.stderr, r.stderr


@pytest.mark.parametrize("shape", ["noprefix", "quoted path", "text starting with ++"])
def test_a_citation_is_found_whatever_the_diff_header_looks_like(work, shape):
    root, origin, base, runs = work
    if shape == "noprefix":
        _git(root, "config", "diff.noprefix", "true")
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    name = "n\u00f6tes.md" if shape == "quoted path" else "notes.md"
    text = "++ fixed in %s\n" % old[:7] if shape == "text starting with ++" else "fixed in %s\n" % old[:7]
    _commit(root, name, text, "a note")
    r = _push(root, runs)
    assert r.returncode == 4 and "cites %s, a commit this push rewrote" % old[:7] in r.stderr, r.stdout + r.stderr
    assert _git(origin, "rev-parse", "feat") == base


def test_the_checker_fails_loud_when_it_cannot_map_the_range(work, tmp_path):
    root, origin, base, runs = work
    _commit(root, "a.txt", "a\n", "one more")
    ids = tmp_path / "ids"
    ids.write_text("0" * 40 + "\n" + "1" * 40 + "\n")
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "stale_ids.py"), "--old", str(ids), "--origin-ref",
                        "refs/remotes/origin/feat"], cwd=root, capture_output=True, text=True, timeout=60)
    assert r.returncode == 2 and "had 2 commits before the rewrite and 1 after" in r.stderr, r.stderr
