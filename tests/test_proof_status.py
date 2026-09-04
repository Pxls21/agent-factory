"""Contract tests for the structured review-status guard (AF-AP-32).

The guard reads a SINGLE, VISIBLE `PROOF-STATUS: <id> = <status>` line as the
authoritative status and enforces that the coordinator can record only
REVIEW-PENDING. These cover the cycle-7 bypasses the owner reproduced: a
contradictory VISIBLE task row, a coordinator self-accept, and a hidden marker
diverging from the visible ledger. All mutations happen in a temporary copy.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-proof-status.py"
VALIDATE_LEDGER = ROOT / "scripts" / "validate-ledger"
TASKLIST_REL = Path("todo") / "BUILD-TASKLIST.md"
GOOD = "notes\nPROOF-STATUS: S0-11 = REVIEW-PENDING\n"


def _make_root(tmp_path, tasklist_text):
    root = tmp_path / "repo"
    (root / "todo").mkdir(parents=True)
    (root / TASKLIST_REL).write_text(tasklist_text)
    return root


def _run(root):
    return subprocess.run([sys.executable, str(CHECKER), str(root)],
                          capture_output=True, text=True, timeout=30)


def test_review_pending_visible_marker_passes(tmp_path):
    assert _run(_make_root(tmp_path, GOOD)).returncode == 0


def test_the_committed_tasklist_passes():
    assert _run(ROOT).returncode == 0


def test_coordinator_cannot_record_accepted(tmp_path):
    # ACCEPTED is not a coordinator-writable status: it needs an owner-verifiable
    # anchor the coordinator cannot forge.
    result = _run(_make_root(tmp_path, "PROOF-STATUS: S0-11 = ACCEPTED\n"))
    assert result.returncode == 1
    assert "records ONLY REVIEW-PENDING" in result.stderr


def test_done_status_fails(tmp_path):
    assert _run(_make_root(tmp_path, "PROOF-STATUS: S0-11 = DONE\n")).returncode == 1


def test_deleted_marker_fails(tmp_path):
    result = _run(_make_root(tmp_path, "a ledger with no status line\n"))
    assert result.returncode == 1
    assert "no PROOF-STATUS line" in result.stderr


def test_duplicate_visible_markers_fail(tmp_path):
    result = _run(_make_root(
        tmp_path,
        "PROOF-STATUS: S0-11 = REVIEW-PENDING\nPROOF-STATUS: S0-11 = ACCEPTED\n"))
    assert result.returncode == 1
    assert "more than one PROOF-STATUS line" in result.stderr


def test_hidden_marker_fails(tmp_path):
    # A hidden HTML-comment marker can diverge from the visible ledger a human reads.
    result = _run(_make_root(
        tmp_path, GOOD + "<!-- PROOF-STATUS S0-11 ACCEPTED -->\n"))
    assert result.returncode == 1
    assert "hidden HTML-comment" in result.stderr


def test_contradictory_visible_task_row_fails(tmp_path):
    # The owner's attack: a visible Markdown task row keyed by the bare proof id
    # asserting DONE, while the authoritative marker stays REVIEW-PENDING.
    result = _run(_make_root(
        tmp_path, GOOD + "| S0-11 | DONE by coordinator without owner acceptance |\n"))
    assert result.returncode == 1
    assert "keyed by the bare proof id" in result.stderr


def test_slug_keyed_task_row_is_allowed(tmp_path):
    # A real task row keyed by a descriptive slug (mentioning S0-11 in later
    # cells) is NOT a status assertion and must pass.
    row = "| s0-18-s0-11-eval-hardening | #18 S0-11 runner design | REVIEW-PENDING; details |\n"
    assert _run(_make_root(tmp_path, GOOD + row)).returncode == 0


def test_transition_gate_review_pending_passes_planning_and_ledger(tmp_path):
    # End-to-end: the committed REVIEW-PENDING state passes BOTH the status guard
    # and ledger integrity, and a self-accept attempt is rejected by the status
    # guard while never touching the attested proof dir (so it cannot silently
    # invalidate the ledger the way an in-proof-dir acceptance file did).
    status = _run(ROOT)
    ledger = subprocess.run(
        [sys.executable, str(VALIDATE_LEDGER), "integrity", "--root", str(ROOT)],
        capture_output=True, text=True, timeout=60)
    assert status.returncode == 0
    assert ledger.returncode == 0 and "S0-11 PRESENT" in ledger.stdout

    self_accept = _run(_make_root(tmp_path, "PROOF-STATUS: S0-11 = ACCEPTED\n"))
    assert self_accept.returncode == 1
