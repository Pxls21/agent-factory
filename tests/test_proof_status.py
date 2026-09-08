"""Contract tests for the visible proof-review status consistency guard (AF-AP-32).

The guard binds a SINGLE, VISIBLE `PROOF-STATUS: <id> = <status>` line to the ONE
canonical task row for each tracked proof (exact proof->slug map). These cover
the cycle-8 slug bypass the owner reproduced — a `s0-18-s0-11-eval-hardening`-keyed
row whose status cell said DONE while the authoritative marker stayed
REVIEW-PENDING — plus the earlier divergence attacks (hidden marker, bare-id row,
duplicate marker) and the substring-collision hazard (the S0-10 row's slug
contains "s0-11"). All mutations happen in a temporary copy.

Honest boundary (AF-AP-32): this guard checks CONSISTENCY, not authenticity. It
cannot tell a real owner acceptance from a coordinator-written one — while the
agent pushes under the owner's GitHub identity, no in-repo status is structurally
owner-only. `ACCEPTED` records an explicit owner PROCESS decision; the
owner-verifiable anchor is the separate `acceptance-anchor-af-ap-32` task.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-proof-status.py"
VALIDATE_LEDGER = ROOT / "scripts" / "validate-ledger"
TASKLIST_REL = Path("todo") / "BUILD-TASKLIST.md"

HEADER = (
    "| slug | increment | status | blocked-by | gate |\n"
    "|---|---|---|---|---|\n"
)


def _load_checker():
    spec = importlib.util.spec_from_file_location("_check_proof_status", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical(status_cell):
    return (
        f"| s0-18-s0-11-eval-hardening | #18 S0-11 runner design | {status_cell} "
        f"| s0-02 | gate |\n"
    )


S0_01_MARKER = "PROOF-STATUS: S0-01 = REVIEW-PENDING"
S0_01_ROW = "| s0-07-s0-01-acp-conformance | #7 S0-01 ACP conformance | REVIEW-PENDING 2026-09-05; details | s0-02 | gate |\n"
S0_07_MARKER = "PROOF-STATUS: S0-07 = REVIEW-PENDING"
S0_07_ROW = "| s0-09-s0-07-fubuki | #9 S0-07 Fubuki corrections | REVIEW-PENDING 2026-09-07; details | s0-02 | gate |\n"


def _ledger(marker="PROOF-STATUS: S0-11 = REVIEW-PENDING", rows=None, s0_01_marker=S0_01_MARKER, s0_01_row=S0_01_ROW, s0_07_marker=S0_07_MARKER, s0_07_row=S0_07_ROW):
    """Fixture ledger: the S0-11 case under test plus a consistent S0-01 binding (both proofs are tracked)."""
    if rows is None:
        rows = [_canonical("REVIEW-PENDING; details")]
    return f"notes\n{marker}\n{s0_01_marker}\n{s0_07_marker}\n\n{HEADER}{''.join(rows)}{s0_01_row}{s0_07_row}"


def _make_root(tmp_path, tasklist_text):
    root = tmp_path / "repo"
    (root / "todo").mkdir(parents=True, exist_ok=True)
    (root / TASKLIST_REL).write_text(tasklist_text)
    return root


def _run(root, *flags):
    """The checker as CI and the coordinator run it: anchors ON (default) unless a flag says otherwise."""
    return subprocess.run([sys.executable, str(CHECKER), str(root), *flags],
                          capture_output=True, text=True, timeout=60)


def _run_status_only(root):
    """The status-logic fixtures live in plain directories, not git repos: anchors are skipped EXPLICITLY."""
    return _run(root, "--no-anchors")


# --- the committed tree ------------------------------------------------------

def test_the_committed_tasklist_passes():
    assert _run(ROOT).returncode == 0


def test_committed_state_passes_status_and_ledger():
    # The cycle-6 lesson: exercise the state through BOTH adjacent gates. The
    # committed ACCEPTED status must pass the status guard AND ledger integrity
    # (the status guard never touches the attested proof dir, so it cannot
    # silently invalidate the ledger).
    status = _run(ROOT)
    ledger = subprocess.run(
        [sys.executable, str(VALIDATE_LEDGER), "integrity", "--root", str(ROOT)],
        capture_output=True, text=True, timeout=60)
    assert status.returncode == 0, status.stderr
    assert ledger.returncode == 0 and "S0-11 PRESENT" in ledger.stdout


# --- consistent states pass --------------------------------------------------

def test_review_pending_consistent_passes(tmp_path):
    assert _run_status_only(_make_root(tmp_path, _ledger())).returncode == 0


def test_accepted_consistent_passes(tmp_path):
    # ACCEPTED is now a valid ledger status (an owner process decision). The
    # guard verifies the marker and the canonical row AGREE — it does not, and
    # cannot, authenticate that the decision was really the owner's.
    text = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", [_canonical("**ACCEPTED** owner decision")])
    assert _run_status_only(_make_root(tmp_path, text)).returncode == 0


# --- the cycle-8 slug bypass (the reported bug) ------------------------------

def test_slug_keyed_done_row_is_rejected(tmp_path):
    # THE cycle-8 bypass: a canonical slug row asserting DONE while the marker
    # stays REVIEW-PENDING. The old guard rejected only bare-id rows and let
    # this through; the new guard binds the slug row's status cell.
    text = _ledger("PROOF-STATUS: S0-11 = REVIEW-PENDING",
                   [_canonical("DONE by coordinator, not owner-accepted")])
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "must not contradict" in result.stderr


def test_accepted_marker_with_pending_row_is_rejected(tmp_path):
    # The contradiction in the other direction: marker ACCEPTED, row still
    # REVIEW-PENDING. Either surface leading the other is a divergence.
    text = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", [_canonical("REVIEW-PENDING still")])
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "must not contradict" in result.stderr


def test_duplicate_canonical_row_fails(tmp_path):
    text = _ledger(rows=[_canonical("REVIEW-PENDING"), _canonical("REVIEW-PENDING")])
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "found 2 task rows" in result.stderr


def test_missing_canonical_row_fails(tmp_path):
    # A marker with no canonical row: the status is not bound to anything visible.
    text = f"notes\nPROOF-STATUS: S0-11 = REVIEW-PENDING\n{S0_01_MARKER}\n{S0_07_MARKER}\n\n{HEADER}{S0_01_ROW}{S0_07_ROW}"
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "found 0 task rows" in result.stderr


# --- the substring-collision hazard ------------------------------------------

def test_unrelated_slug_with_s0_11_substring_is_ignored(tmp_path):
    # The S0-10 task row is keyed `s0-11-s0-10-gbrain-adr` — its first cell
    # contains the substring "s0-11". An exact proof->slug map must NOT bind it
    # as the S0-11 row, so its DONE status is irrelevant to S0-11's binding.
    rows = [
        "| s0-11-s0-10-gbrain-adr | #11 S0-10 ADR | DONE 2026-09-04 — accepted | s0-02 | g |\n",
        _canonical("**ACCEPTED** owner decision"),
    ]
    text = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", rows)
    assert _run_status_only(_make_root(tmp_path, text)).returncode == 0


# --- vocabulary and single-visible-source ------------------------------------

def test_unknown_status_vocabulary_fails(tmp_path):
    text = _ledger("PROOF-STATUS: S0-11 = DONE", [_canonical("DONE")])
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "ledger vocabulary" in result.stderr


def test_deleted_marker_fails(tmp_path):
    text = f"a ledger with no status line\n\n{HEADER}{_canonical('REVIEW-PENDING')}"
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "no PROOF-STATUS line" in result.stderr


def test_duplicate_visible_markers_fail(tmp_path):
    text = _ledger("PROOF-STATUS: S0-11 = REVIEW-PENDING\nPROOF-STATUS: S0-11 = ACCEPTED")
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "more than one PROOF-STATUS line" in result.stderr


def test_hidden_marker_fails(tmp_path):
    text = _ledger() + "<!-- PROOF-STATUS S0-11 ACCEPTED -->\n"
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "hidden HTML-comment" in result.stderr


def test_bare_proof_id_row_fails(tmp_path):
    # A visible row keyed by the bare proof id asserting a status.
    text = _ledger() + "| S0-11 | DONE by coordinator without owner acceptance |\n"
    result = _run_status_only(_make_root(tmp_path, text))
    assert result.returncode == 1
    assert "bare proof id" in result.stderr


# --- parser robustness on the real (malformed, multi-column) row -------------

def test_status_column_read_despite_inner_pipes(tmp_path):
    # The real S0-11 row is a malformed table row: unescaped pipes in the
    # narrative split it into extra columns, and it contains escaped `\|`. The
    # status is still content-column 2 and its leading token binds. Mimic that
    # shape and confirm both the pass and the contradiction fire correctly.
    messy = (
        "| s0-18-s0-11-eval-hardening | #18 S0-11 runner "
        "| **ACCEPTED** owner decision; a `\\| S0-11 \\| DONE \\|` attack is quoted here "
        "| **Cycle 4** more narrative | **Cycle 5** more | s0-02 | gate |\n"
    )
    ok = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", [messy])
    assert _run_status_only(_make_root(tmp_path, ok)).returncode == 0

    bad = messy.replace("**ACCEPTED** owner decision", "DONE by coordinator")
    text = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", [bad])
    assert _run_status_only(_make_root(tmp_path, text)).returncode == 1


def test_row_cells_splits_on_unescaped_pipes_only():
    checker = _load_checker()
    cells = checker._row_cells(r"| a | b with \| escaped pipe | c |")
    assert cells == ["a", r"b with \| escaped pipe", "c"]
    assert checker._row_cells("no pipes here") is None


def test_s0_01_binding_marker_and_canonical_row_must_agree(tmp_path):
    ok = _make_root(tmp_path / "ok", _ledger())
    assert _run_status_only(ok).returncode == 0
    # the S0-01 row still saying `pending` while the marker says REVIEW-PENDING is a contradiction
    bad = _make_root(tmp_path / "bad", _ledger(s0_01_row="| s0-07-s0-01-acp-conformance | #7 | pending | s0-02 | gate |\n"))
    r = _run_status_only(bad)
    assert r.returncode == 1 and "S0-01" in r.stdout + r.stderr
    # a DONE-style self-closure of S0-01 is not a governance word
    done = _make_root(tmp_path / "done", _ledger(s0_01_marker="PROOF-STATUS: S0-01 = DONE", s0_01_row="| s0-07-s0-01-acp-conformance | #7 | DONE | s0-02 | gate |\n"))
    assert _run_status_only(done).returncode == 1
    # a missing S0-01 marker fails: deletion is not a way out
    gone = _make_root(tmp_path / "gone", _ledger(s0_01_marker="", s0_01_row=""))
    assert _run_status_only(gone).returncode == 1


# --- the owner-verifiable ACCEPTED anchor (owner decision 2026-09-08, task #30) --------------------
# Throwaway GPG keys in isolated homes; the checker builds its own keyring from the committed
# key file, so a signature by any other key must fail against it.

import os


def _gpg_home(tmp_path, name):
    home = tmp_path / f"gnupg-{name}"
    home.mkdir()
    home.chmod(0o700)
    env = dict(os.environ, GNUPGHOME=str(home))
    subprocess.run(
        ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "",
         "--quick-generate-key", f"{name} <{name}@example.invalid>", "ed25519", "sign", "0"],
        check=True, capture_output=True, text=True, timeout=120, env=env,
    )
    listing = subprocess.run(["gpg", "--batch", "--with-colons", "--list-secret-keys"],
                             check=True, capture_output=True, text=True, timeout=30, env=env).stdout
    fingerprint = next(line.split(":")[9] for line in listing.splitlines() if line.startswith("fpr:"))
    armored = subprocess.run(["gpg", "--batch", "--armor", "--export", fingerprint],
                             check=True, capture_output=True, text=True, timeout=30, env=env).stdout
    return env, fingerprint, armored


def _git(root, *args, env=None):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          timeout=30, env=env, check=False)


ACCEPTED_LEDGER = _ledger("PROOF-STATUS: S0-11 = ACCEPTED", [_canonical("**ACCEPTED** owner decision")])
PENDING_LEDGER = _ledger(
    "PROOF-STATUS: S0-11 = ACCEPTED\nPROOF-ANCHOR: S0-11 = PENDING-OWNER-TAG (requested in a test)",
    [_canonical("**ACCEPTED** owner decision")],
)


def _anchored_repo(tmp_path, ledger_text, key_armored=None, result=b'{"proof_id": "S0-11"}\n'):
    root = _make_root(tmp_path, ledger_text)
    (root / "proofs" / "S0-11").mkdir(parents=True)
    (root / "proofs" / "S0-11" / "result.json").write_bytes(result)
    if key_armored is not None:
        (root / "docs" / "governance").mkdir(parents=True)
        (root / "docs" / "governance" / "owner-signing-key.asc").write_text(key_armored)
    for args in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
                 ("add", "-A"), ("commit", "-q", "-m", "base")):
        assert _git(root, *args).returncode == 0, args
    return root


def _sign_tag(root, env, fingerprint, target="HEAD"):
    completed = _git(root, "-c", f"user.signingkey={fingerprint}", "-c", "gpg.format=openpgp", "-c", "gpg.program=gpg",
                     "tag", "-s", "accepted/S0-11", "-m", "ACCEPTED: S0-11", target, env=env)
    assert completed.returncode == 0, completed.stderr


def test_anchor_signed_tag_by_the_owner_key_passes_with_no_warning(tmp_path):
    env, fingerprint, armored = _gpg_home(tmp_path, "owner")
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, armored)
    _sign_tag(root, env, fingerprint)
    completed = _run(root)
    assert completed.returncode == 0, completed.stderr
    assert "WARNING" not in completed.stderr


def test_anchor_missing_tag_without_a_declaration_is_refused(tmp_path):
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, key_armored="unused")
    completed = _run(root)
    assert completed.returncode == 1
    assert "S0-11: ACCEPTED but no signed tag accepted/S0-11 and no visible" in completed.stderr


def test_anchor_pending_declaration_is_a_warning_never_a_verification(tmp_path):
    root = _anchored_repo(tmp_path, PENDING_LEDGER, key_armored="unused")
    completed = _run(root)
    assert completed.returncode == 0, completed.stderr
    assert "WARNING S0-11: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-11" in completed.stderr


def test_anchor_stale_pending_declaration_beside_a_tag_is_refused(tmp_path):
    env, fingerprint, armored = _gpg_home(tmp_path, "owner")
    root = _anchored_repo(tmp_path, PENDING_LEDGER, armored)
    _sign_tag(root, env, fingerprint)
    completed = _run(root)
    assert completed.returncode == 1
    assert "the tag accepted/S0-11 exists but the ledger still declares PROOF-ANCHOR PENDING" in completed.stderr


def test_anchor_lightweight_tag_is_refused(tmp_path):
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, key_armored="unused")
    assert _git(root, "tag", "accepted/S0-11").returncode == 0
    completed = _run(root)
    assert completed.returncode == 1
    assert "accepted/S0-11 is a lightweight tag" in completed.stderr


def test_anchor_tag_signed_by_another_key_is_refused(tmp_path):
    _, _, owner_armored = _gpg_home(tmp_path, "owner")
    other_env, other_fingerprint, _ = _gpg_home(tmp_path, "other")
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, owner_armored)
    _sign_tag(root, other_env, other_fingerprint)
    completed = _run(root)
    assert completed.returncode == 1
    assert "the signature on accepted/S0-11 does not verify against the committed owner key" in completed.stderr


def test_anchor_without_the_committed_owner_key_is_refused(tmp_path):
    env, fingerprint, _ = _gpg_home(tmp_path, "owner")
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, key_armored=None)
    _sign_tag(root, env, fingerprint)
    completed = _run(root)
    assert completed.returncode == 1
    assert "the owner's public key is not committed at docs/governance/owner-signing-key.asc" in completed.stderr


def test_anchor_result_regenerated_after_the_tag_is_refused(tmp_path):
    env, fingerprint, armored = _gpg_home(tmp_path, "owner")
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, armored)
    _sign_tag(root, env, fingerprint)
    (root / "proofs" / "S0-11" / "result.json").write_bytes(b'{"proof_id": "S0-11", "regenerated": true}\n')
    assert _git(root, "commit", "-q", "-am", "regen").returncode == 0
    completed = _run(root)
    assert completed.returncode == 1
    assert "the minted proofs/S0-11/result.json changed since accepted/S0-11" in completed.stderr


def test_anchor_tag_outside_this_history_is_refused(tmp_path):
    env, fingerprint, armored = _gpg_home(tmp_path, "owner")
    root = _anchored_repo(tmp_path, ACCEPTED_LEDGER, armored)
    base = _git(root, "rev-parse", "HEAD").stdout.strip()
    assert _git(root, "checkout", "-q", "-b", "side").returncode == 0
    (root / "side.txt").write_text("side\n")
    assert _git(root, "add", "side.txt").returncode == 0 and _git(root, "commit", "-q", "-m", "side").returncode == 0
    _sign_tag(root, env, fingerprint)
    assert _git(root, "checkout", "-q", base).returncode == 0
    completed = _run(root)
    assert completed.returncode == 1
    assert "which is not in this branch's history" in completed.stderr


def test_anchor_check_needs_a_git_repository_and_no_anchors_skips_explicitly(tmp_path):
    root = _make_root(tmp_path, ACCEPTED_LEDGER)
    completed = _run(root)
    assert completed.returncode == 1
    assert "is not a git repository — the anchor tag accepted/S0-11 cannot be verified" in completed.stderr
    skipped = _run(root, "--no-anchors")
    assert skipped.returncode == 0, skipped.stderr
    assert "ACCEPTED anchor verification SKIPPED (--no-anchors)" in skipped.stderr


def test_pending_declaration_for_a_proof_that_is_not_accepted_is_refused(tmp_path):
    text = _ledger("PROOF-STATUS: S0-11 = REVIEW-PENDING\nPROOF-ANCHOR: S0-11 = PENDING-OWNER-TAG (wrong)")
    completed = _run_status_only(_make_root(tmp_path, text))
    assert completed.returncode == 1
    assert "a PROOF-ANCHOR PENDING declaration for a proof whose PROOF-STATUS is 'REVIEW-PENDING'" in completed.stderr


def test_committed_tree_anchor_state_is_the_declared_pending_one():
    """Today S0-11 is ACCEPTED with the anchor PENDING the owner's tag: the checker passes with exactly
    that warning. When the owner signs, the declaration must go and this test flips to no warning."""
    completed = _run(ROOT)
    assert completed.returncode == 0, completed.stderr
    tag = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", "refs/tags/accepted/S0-11"],
                         capture_output=True, text=True, timeout=30)
    if tag.returncode == 0:
        assert "WARNING" not in completed.stderr
    else:
        assert "WARNING S0-11: ACCEPTED with the anchor PENDING" in completed.stderr
