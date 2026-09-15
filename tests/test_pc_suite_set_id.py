"""`pc_suite.sh set-id -- <files>` — the SET a pasted test count belongs to. 2026-09-15: the ledger's joint-set floor
`1556 passed, 9 xfailed` had been produced by an 18-file run and was read against the 13-file `tests/test_s0_01_*.py`
glob (1354 collected) — a 215-test "drop" that was no drop (AF-AP-73 at the floor). `launch` records the set on the PC,
`wait` prints `pytest-set: <N> files set=<sha12> — <files>` beside the summary, and `set-id` prints the same id
standalone. The id is pinned here against an INDEPENDENT oracle (hashlib over the sorted list) so a ledger line's id can
be re-derived without the script."""
import hashlib
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GLOB_13 = [
    "tests/test_s0_01_acp_probe.py", "tests/test_s0_01_audit_cp5_controls.py",
    "tests/test_s0_01_check_acp_conformance.py", "tests/test_s0_01_check_initialize.py",
    "tests/test_s0_01_frame_tee.py", "tests/test_s0_01_initialize_capture.py",
    "tests/test_s0_01_negative_contract.py", "tests/test_s0_01_nostr_verify.py",
    "tests/test_s0_01_pc_post_scan.py", "tests/test_s0_01_pc_tools.py",
    "tests/test_s0_01_scripted_backend.py", "tests/test_s0_01_spec_runner.py",
    "tests/test_s0_01_turn_capture.py",
]
EXTRA_5 = [
    "tests/red/test_s0_01_adversarial.py", "tests/red/test_s0_01_backend_credential_screen.py",
    "tests/red/test_s0_01_round4.py", "tests/test_ap_screen.py", "tests/test_edit_snapshot_ap_screen.py",
]


def _run(*args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PC_")}
    return subprocess.run(["bash", str(ROOT / "scripts/pc_suite.sh"), "set-id", *args],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)


def _oracle(files):
    return hashlib.sha256(("\n".join(sorted(files)) + "\n").encode()).hexdigest()[:12]


def test_set_id_is_order_blind_and_counts_the_files():
    a = _run("--", "tests/b.py", "tests/a.py", "tests/c.py")
    b = _run("--", "tests/c.py", "tests/b.py", "tests/a.py")
    assert a.returncode == 0 and b.returncode == 0, (a.stderr, b.stderr)
    assert a.stdout == b.stdout, (a.stdout, b.stdout)
    assert a.stdout.strip() == f"3 files set={_oracle(['tests/a.py', 'tests/b.py', 'tests/c.py'])}"
    two = _run("--", "tests/a.py", "tests/b.py")
    assert two.stdout.startswith("2 files set=") and two.stdout != a.stdout


def test_the_18_file_floor_set_and_the_13_file_glob_have_different_ids():
    glob_id = _run("--", *GLOB_13).stdout.strip()
    floor_id = _run("--", *GLOB_13, *EXTRA_5).stdout.strip()
    assert glob_id == f"13 files set={_oracle(GLOB_13)}", glob_id
    assert floor_id == f"18 files set={_oracle(GLOB_13 + EXTRA_5)}", floor_id
    assert glob_id.split("set=")[1] != floor_id.split("set=")[1]


def test_set_id_refuses_an_empty_set():
    r = _run()
    assert r.returncode == 2 and "set-id needs files" in r.stderr, (r.returncode, r.stderr)
    r = _run("--")
    assert r.returncode == 2 and "set-id needs files" in r.stderr, (r.returncode, r.stderr)
