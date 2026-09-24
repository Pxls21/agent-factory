"""scripts/stale_ids.py through the real scripts/push_clean.sh (task #243).

push_clean rewrites every commit of the range that carries a model-identifier trailer, and every commit after it. A
note added in the range that cites one of those commits by its LOCAL id points at nothing on origin (2026-09-24: four
commits cited that way in the ledger, the wiki and the incident log). Each test builds a work repo with a bare origin
and a green CI record for origin's head, then runs the real push_clean.sh.
"""
import json
import os
import re
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
    m = re.search(r"stale_ids: notes\.md:1 cites %s, a commit this push rewrote; it is ([0-9a-f]{7}) on origin" % old[:7],
                  r.stderr)
    assert m and m.group(1) != old[:7], r.stderr
    assert "REFUSED by stale_ids (rc 4): NOT pushed" in r.stderr and _git(origin, "rev-parse", "feat") == base
    _commit(root, "notes.md", "fixed in %s\n" % m.group(1), "the note cites the new id")
    r = _push(root, runs)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(origin, "rev-parse", "--verify", m.group(1) + "^{commit}").startswith(m.group(1))
    assert _git(origin, "rev-parse", "feat") == _git(root, "rev-parse", "HEAD")


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


# VERIFY-T243-245 A-F1..A-F5.
def test_a_refusal_is_sticky_the_branch_is_put_back_and_a_plain_rerun_refuses_again(work):
    """A-F1: a refused run left the branch rewritten, so the next run rewrote nothing and pushed the stale note."""
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    head = _commit(root, "notes.md", "fixed in %s\n" % old[:7], "a note")
    for _ in range(2):
        r = _push(root, runs)
        assert r.returncode == 4 and "cites %s" % old[:7] in r.stderr, r.stdout + r.stderr
        assert _git(root, "rev-parse", "HEAD") == head and _git(origin, "rev-parse", "feat") == base


def test_fixing_one_of_two_stale_notes_still_refuses_on_the_other(work):
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "one.md", "see %s\n" % old[:7], "two notes")
    _commit(root, "two.md", "and %s\n" % old[:8], "the second")
    r = _push(root, runs)
    new7 = re.search(r"one\.md:1 cites %s, a commit this push rewrote; it is ([0-9a-f]{7})" % old[:7], r.stderr).group(1)
    _commit(root, "one.md", "see %s\n" % new7, "one note fixed")
    r = _push(root, runs)
    assert r.returncode == 4 and "two.md:1 cites %s" % old[:8] in r.stderr and "one.md" not in r.stderr, r.stderr
    assert _git(origin, "rev-parse", "feat") == base


@pytest.mark.parametrize("shape", ["nul byte", "binary attribute", "-diff attribute", "bigFileThreshold", "textconv"])
def test_a_citation_is_found_in_a_file_git_would_call_binary(work, shape):
    """A-F2: without --text / --no-textconv the diff printed "Binary files differ" (or a converted text) and the
    citation was never read."""
    root, origin, base, runs = work
    if shape == "binary attribute":
        (root / ".gitattributes").write_text("notes.md binary\n")
    elif shape == "-diff attribute":
        (root / ".gitattributes").write_text("notes.md -diff\n")
    elif shape == "bigFileThreshold":
        _git(root, "config", "core.bigFileThreshold", "1")
    elif shape == "textconv":
        (root / ".gitattributes").write_text("notes.md diff=blank\n")
        _git(root, "config", "diff.blank.textconv", "sh -c 'echo nothing to see'")
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    body = ("fixed in %s\n" % old[:7]).encode() + (b"\0tail\n" if shape == "nul byte" else b"")
    (root / "notes.md").write_bytes(body)
    _git(root, "add", "--", "notes.md")
    _git(root, "commit", "-q", "-m", "a note")
    r = _push(root, runs)
    assert r.returncode == 4 and "notes.md:1 cites %s" % old[:7] in r.stderr, (shape, r.stdout + r.stderr)
    assert _git(origin, "rev-parse", "feat") == base


def test_a_file_that_is_not_utf8_is_read_not_a_crash(work):
    """A-F3: a Latin-1 byte made the checker raise, and push_clean printed a false refusal."""
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    (root / "latin.txt").write_bytes(b"caf\xe9 fixed in " + old[:7].encode() + b"\n")
    _git(root, "add", "--", "latin.txt")
    _git(root, "commit", "-q", "-m", "a latin-1 note")
    r = _push(root, runs)
    assert r.returncode == 4 and "latin.txt:1 cites %s" % old[:7] in r.stderr and "Traceback" not in r.stderr, r.stderr


def test_the_old_ids_file_never_leaks(work, tmp_path):
    """A-F5: the temp file of old ids leaked on the abort paths; an EXIT trap removes it on every path. The file lives
    under TMPDIR, so the test reads a directory of its own, never the shared /tmp (R1-A-F3: flaky beside parallel runs)."""
    root, origin, base, runs = work
    tmpd = tmp_path / "tmpdir"
    tmpd.mkdir()
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "see %s\n" % old[:7], "a note")
    assert _push(root, runs, TMPDIR=str(tmpd)).returncode == 4
    _commit(root, "notes.md", "no citation\n", "the note fixed")
    assert _push(root, runs, TMPDIR=str(tmpd)).returncode == 0
    assert list(tmpd.iterdir()) == []


def test_a_failed_push_puts_the_branch_back_so_a_note_citing_a_listed_id_is_refused(work):
    """R1-A-F1: only the stale-id refusal reset the branch. A push the origin rejected left it rewritten; a note citing
    the id the boundary listing had printed (the pre-rewrite one) then pushed with rc 0 on the next plain run."""
    root, origin, base, runs = work
    hook = origin / "hooks" / "pre-receive"
    hook.write_text('#!/bin/sh\n[ -f "$GIT_DIR/rejected-once" ] && exit 0\ntouch "$GIT_DIR/rejected-once"\nexit 1\n')
    hook.chmod(0o755)
    _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    head = _commit(root, "notes.md", "no citation yet\n", "a note")
    r = _push(root, runs)
    assert r.returncode != 0 and _git(origin, "rev-parse", "feat") == base, r.stdout + r.stderr
    assert _git(root, "rev-parse", "HEAD") == head, "the branch was left rewritten"
    listed = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" the fix")][0]
    _commit(root, "notes2.md", "fixed in %s\n" % listed, "a note citing the listed id")
    r = _push(root, runs)
    assert r.returncode == 4 and "notes2.md:1 cites %s" % listed in r.stderr, r.stdout + r.stderr
    assert _git(origin, "rev-parse", "feat") == base


def test_a_refusal_after_rc2_is_sticky(work, tmp_path):
    """R1-A-F2: a reset only on rc 4 survived every test; rc 2 (a blob the diff needs is missing) must leave the branch
    un-rewritten too, so the plain re-run after the blob is back still refuses the stale note."""
    root, origin, base, runs = work
    old = _commit(root, "a.txt", "a\n", "the fix\n\n" + TRAILER)
    _commit(root, "notes.md", "fixed in %s\n" % old[:7], "a note")
    blob = _git(root, "rev-parse", "HEAD:notes.md")
    obj, aside = root / ".git" / "objects" / blob[:2] / blob[2:], tmp_path / "aside"
    obj.rename(aside)
    r1 = _push(root, runs)
    aside.rename(obj)
    r2 = _push(root, runs)
    assert r1.returncode == 4 and "rc 2" in r1.stderr, r1.stdout + r1.stderr
    assert r2.returncode == 4 and "cites %s" % old[:7] in r2.stderr and _git(origin, "rev-parse", "feat") == base
