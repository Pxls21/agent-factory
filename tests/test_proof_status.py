"""Contract tests for the structured review-status guard (AF-AP-32).

The guard parses the canonical per-proof status markers in BUILD-TASKLIST.md and
requires REVIEW-PENDING until an owner-acceptance record exists. These are the
negative cases the owner flagged as previously untested: DONE, CLOSED, a deleted
marker, conflicting duplicate rows, and ACCEPTED with/without the owner record.
All mutations happen in a temporary copy; the repository is never modified.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-proof-status.py"
TASKLIST_REL = Path("todo") / "BUILD-TASKLIST.md"


def _make_root(tmp_path, tasklist_text, *, accepted=()):
    root = tmp_path / "repo"
    (root / "todo").mkdir(parents=True)
    (root / TASKLIST_REL).write_text(tasklist_text)
    for proof_id in accepted:
        record_dir = root / "proofs" / proof_id
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "OWNER-ACCEPTED").write_text("accepted by owner\n")
    return root


def _run(root):
    return subprocess.run([sys.executable, str(CHECKER), str(root)],
                          capture_output=True, text=True, timeout=30)


def test_review_pending_marker_passes(tmp_path):
    root = _make_root(tmp_path, "notes\n<!-- PROOF-STATUS S0-11 REVIEW-PENDING -->\n")
    assert _run(root).returncode == 0


def test_the_committed_tasklist_passes():
    # The real BUILD-TASKLIST must carry a valid S0-11 marker.
    assert _run(ROOT).returncode == 0


def test_done_marker_fails(tmp_path):
    root = _make_root(tmp_path, "<!-- PROOF-STATUS S0-11 DONE -->\n")
    result = _run(root)
    assert result.returncode == 1
    assert "only REVIEW-PENDING or ACCEPTED" in result.stderr


def test_closed_marker_fails(tmp_path):
    root = _make_root(tmp_path, "<!-- PROOF-STATUS S0-11 CLOSED -->\n")
    assert _run(root).returncode == 1


def test_deleted_marker_fails(tmp_path):
    # No S0-11 marker at all: a proof under review must carry one.
    root = _make_root(tmp_path, "the ledger with no status marker\n")
    result = _run(root)
    assert result.returncode == 1
    assert "no PROOF-STATUS marker" in result.stderr


def test_conflicting_duplicate_rows_fail(tmp_path):
    root = _make_root(
        tmp_path,
        "<!-- PROOF-STATUS S0-11 REVIEW-PENDING -->\n"
        "<!-- PROOF-STATUS S0-11 DONE -->\n")
    result = _run(root)
    assert result.returncode == 1
    assert "conflicting PROOF-STATUS markers" in result.stderr


def test_accepted_without_owner_record_fails(tmp_path):
    root = _make_root(tmp_path, "<!-- PROOF-STATUS S0-11 ACCEPTED -->\n")
    result = _run(root)
    assert result.returncode == 1
    assert "no owner-acceptance record" in result.stderr


def test_accepted_with_owner_record_passes(tmp_path):
    root = _make_root(tmp_path, "<!-- PROOF-STATUS S0-11 ACCEPTED -->\n", accepted=("S0-11",))
    assert _run(root).returncode == 0
