"""S0-08 containment: checker, marker gate and canary-shape tests.

Deterministic and LLM-free. Every mutation is applied to a COPY under the
test's tmp_path — the committed fixtures are never written to.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "proofs" / "S0-08" / "check_containment.py"
MARKER_GATE = ROOT / "proofs" / "S0-08" / "marker_gate.py"
CANARY_DIR = ROOT / "proofs" / "S0-08" / "canaries"
CRUN_BUNDLE = ROOT / "proofs" / "S0-08" / "fixtures" / "evidence-crun"
MALFORMED_MARKER = ROOT / "proofs" / "S0-08" / "fixtures" / "malformed-marker"

SENTINEL_PATH = "/home/owner/s0-08-host-sentinel-0123456789abcdef"

# The pinned identity the checker requires (proofs/S0-08/check_containment.py).
PINNED_RUNSC_VERSION = "release-20260817.0"
PINNED_RUNSC_SHA256 = "048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c"

ALL_CANARIES = ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8")

# The main program's cmdline, and the uid the canaries are exec'd as. Both are
# owned by proofs/S0-08/tools/pc/run_containment.sh; the tests that matter pin
# them against the runner's own bytes rather than trusting these copies.
MAIN_CMD = "sleep 2147483647"
CANARY_EXEC_UID = "10000"
PINNED_IMAGE_SOURCE_COMMIT = "527da60844d4dced37879ea50259675371abe10e"
# The container's PID 1 comm — Dockerfile:68 "PID 1 = s6-svscan".
CONTAINER_INIT_COMM = "s6-svscan"


def dmesg_restrict() -> str:
    """`kernel.dmesg_restrict`, or `(unavailable)` where the knob does not
    exist (gVisor has no such file)."""
    try:
        return Path("/proc/sys/kernel/dmesg_restrict").read_text().strip()
    except OSError:
        return "(unavailable)"


def dmesg_works() -> bool:
    """Can the user running this suite read the kernel ring buffer?

    A DIRECT probe, not a prediction from `os.geteuid()` + `dmesg_restrict`:
    CAP_SYSLOG grants it to a non-root caller, and inside gVisor there is no
    `dmesg_restrict` at all. P1's `rc` must TRACK this on every venue — that is
    the F13 property — so the tests below derive their expectation from it
    instead of assuming the sandbox's root."""
    return subprocess.run(["dmesg"], capture_output=True).returncode == 0


def venue() -> str:
    return (f"euid {os.geteuid()}, kernel.dmesg_restrict {dmesg_restrict()}, "
            f"dmesg readable here: {dmesg_works()}")


def run_checker(evidence_dir) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(evidence_dir)],
        capture_output=True, text=True, timeout=60,
    )


def run_marker_gate(proof_dir) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MARKER_GATE), "--proof-dir", str(proof_dir)],
        capture_output=True, text=True, timeout=60,
    )


# --- the synthetic PASSING bundle ------------------------------------------
# Built from the expected lines CONTAINMENT-SPEC.md pins. The gVisor-side
# values (P1, P6) are the ones measured under runsc release-20260817.0.

def passing_canaries() -> list[dict]:
    return [
        {"canary": "P1",
         "expect": "uname -r is 4.19.0-gvisor and dmesg line 1 contains Starting gVisor",
         "observed": {"uname_r": "4.19.0-gvisor",
                      "dmesg_first_line": "[    0.000000] Starting gVisor..."},
         "rc": 0},
        {"canary": "P2",
         "expect": "pid 1 uid 0 running s6 init; exactly one process has the main "
                   f"cmdline ({MAIN_CMD}) and it runs as uid 10000",
         "observed": {"pid1_uid": "0", "pid1_comm": CONTAINER_INIT_COMM,
                      "pid1_cmdline": "s6-svscan -St0 /run/service",
                      "main_cmdline": MAIN_CMD,
                      "main_pids": "42", "main_uids": "10000", "proc_count": "6"},
         "rc": 0},
        {"canary": "P3",
         "expect": "hermes, python3 -c import hermes_cli, node and uv each exit 0",
         "observed": {"hermes_rc": "0", "hermes_out": "hermes 0.21.0",
                      "python_import_rc": "0", "python_import_out": "import-ok",
                      "node_rc": "0", "node_out": "v26.0.0",
                      "uv_rc": "0", "uv_out": "uv 0.8.17"},
         "rc": 0},
        {"canary": "P4",
         "expect": "no docker socket; 0 env keys matching the redaction pattern (allowlist empty)",
         "observed": {"docker_sock": "absent", "secret_env_count": "0",
                      "secret_env_keys": "", "mount_count": "12",
                      "host_bind_roots": ""},
         "rc": 0},
        {"canary": "P5",
         "expect": "the host sentinel is UNREADABLE inside the container",
         "observed": {"sentinel_path": SENTINEL_PATH, "sentinel_readable": "no",
                      "sentinel_error": f"cat: {SENTINEL_PATH}: No such file or directory",
                      "home_entries": "", "container_hostname": "hermes-s0-08"},
         "rc": 0},
        {"canary": "P6",
         "expect": "no raw host devices; a mounted procfs shows the container PID 1, not the host",
         "observed": {"dangerous_devices": "",
                      "dev_entries": "char,fd,full,fuse,null,ptmx,pts,random,shm,stderr,stdin,stdout,tty,urandom,zero",
                      "mount_proc_rc": "0", "mount_proc_error": "",
                      "mounted_pid1_comm": CONTAINER_INIT_COMM,
                      "mounted_pid_count": "6",
                      "own_pid1_comm": CONTAINER_INIT_COMM, "own_pid_count": "6",
                      "unshare_net_rc": "0", "unshare_net_error": ""},
         "rc": 0},
        {"canary": "P7",
         "expect": "recorded only: S0-08 asserts no egress property (S0-05 owns egress)",
         "observed": {"interfaces": "lo", "net_namespace": "net:[4026532567]"},
         "rc": 0},
        {"canary": "P8",
         "expect": "recorded only: no resource limits under rootless runsc (ignore-cgroups)",
         "observed": {"cgroup": "0::/", "memory_max": "", "cpu_max": "", "pids_max": ""},
         "rc": 0},
    ]


def passing_identity() -> dict:
    return {
        "venue": "pc-bridge:fedora",
        "captured_at": "2026-09-08T00:00:00Z",
        "runtime": "/usr/local/bin/runsc",
        "runsc_version": PINNED_RUNSC_VERSION,
        "runsc_sha256": PINNED_RUNSC_SHA256,
        "runsc_path": "/usr/local/bin/runsc",
        "podman_version": "podman version 5.7.0",
        "image": "localhost/hermes-s0-08:527da608",
        "image_digest": "sha256:0badc0de",
        "image_source_commit": PINNED_IMAGE_SOURCE_COMMIT,
        "run_argv": ["podman", "run", "-d", "--runtime", "/usr/local/bin/runsc",
                     "--runtime-flag", "ignore-cgroups", "--security-opt",
                     "label=disable", "--network", "none",
                     "localhost/hermes-s0-08:527da608"] + MAIN_CMD.split(),
        "host_kernel": "6.17.11-200.fc42",
        "container_id": "0123456789ab",
        "canary_exec_user": CANARY_EXEC_UID,
        "main_program_user": "hermes",
        "main_hermes_service": "up (pid 30) 12 seconds",
        "ps_tree": "PID USER COMMAND\n1 root /init",
        "sentinel_host_read": {"path": SENTINEL_PATH, "readable": True},
    }


def write_bundle(directory: Path, canaries=None, identity=None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    lines = passing_canaries() if canaries is None else canaries
    (directory / "canaries.jsonl").write_text(
        "".join(json.dumps(rec) + "\n" for rec in lines), encoding="utf-8")
    (directory / "runtime-identity.json").write_text(
        json.dumps(passing_identity() if identity is None else identity,
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return directory


# --- the committed negative bundle -----------------------------------------

def test_crun_bundle_fails_on_p1_with_the_exact_spec_reason():
    """The committed uncontained bundle must fail, and fail on P1 — the first
    property in order — with the exact string proofs/S0-08/spec.json pins."""
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    negative = next(leg for leg in spec["legs"]
                    if leg["leg"] == "negative" and "check_containment.py" in " ".join(leg["cmd"]))
    expected = negative["expect"]["failure_reason"]

    proc = run_checker(CRUN_BUNDLE)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert proc.stdout.strip() == f"failure_reason: {expected}"


def test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it():
    """The negative fixture carries a CORRECT pinned runsc identity. If the
    checker ever started trusting that metadata instead of the observations,
    this bundle would pass — which is exactly the hollow green under test."""
    identity = json.loads((CRUN_BUNDLE / "runtime-identity.json").read_text())
    assert identity["runsc_version"] == PINNED_RUNSC_VERSION
    assert identity["runsc_sha256"] == PINNED_RUNSC_SHA256
    proc = run_checker(CRUN_BUNDLE)
    assert proc.returncode == 1
    assert proc.stdout.startswith("failure_reason: containment: P1 host kernel ")


# --- the synthetic PASSING bundle ------------------------------------------

def test_synthetic_passing_bundle_passes(tmp_path):
    bundle = write_bundle(tmp_path / "pc-runsc")
    proc = run_checker(bundle)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc"


def test_passing_bundle_is_deterministic(tmp_path):
    bundle = write_bundle(tmp_path / "pc-runsc")
    first = run_checker(bundle)
    second = run_checker(bundle)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


# --- the deferral ----------------------------------------------------------

def test_absent_evidence_dir_defers(tmp_path):
    proc = run_checker(tmp_path / "never-captured")
    assert proc.returncode == 2
    assert proc.stdout.strip() == "deferred: containment evidence not captured"


def test_present_dir_with_missing_files_is_a_failure_not_a_deferral(tmp_path):
    """Once the directory exists the run happened; a half-written bundle must
    never read as 'not run'."""
    empty = tmp_path / "pc-runsc"
    empty.mkdir()
    proc = run_checker(empty)
    assert proc.returncode == 1
    assert "runtime-identity.json absent" in proc.stdout


# --- one mutation per property --------------------------------------------

MUTATIONS = [
    # (id, canary, field, value, expected substring)
    ("P1-HOST-KERNEL-ACCEPTED", "P1", "uname_r", "6.17.11-200.fc42",
     "containment: P1 host kernel 6.17.11-200.fc42, not gVisor"),
    ("P1-DMESG-NOT-GVISOR", "P1", "dmesg_first_line", "[    0.000000] Linux version 6.17.11",
     "containment: P1 dmesg line 1 does not announce gVisor"),
    ("P2-UID-ROOT-ACCEPTED", "P2", "main_uids", "0",
     "containment: P2 main program uid 0, expected 10000"),
    ("P2-PID1-NOT-ROOT", "P2", "pid1_uid", "10000",
     "containment: P2 pid 1 uid 10000, expected 0"),
    ("P3-TOOL-BROKEN-ACCEPTED", "P3", "python_import_rc", "1",
     "containment: P3 python3 -c import hermes_cli exited 1"),
    ("P4-DOCKER-SOCKET-ACCEPTED", "P4", "docker_sock", "present",
     "containment: P4 docker socket present"),
    ("P5-SENTINEL-READABLE-ACCEPTED", "P5", "sentinel_readable", "yes",
     "containment: P5 host sentinel readable inside the container"),
    ("P6-RAW-DEVICE-ACCEPTED", "P6", "dangerous_devices", "/dev/kvm",
     "containment: P6 raw host devices present: /dev/kvm"),
    ("P6-HOST-PROCFS-ACCEPTED", "P6", "mounted_pid1_comm", "systemd",
     "containment: P6 mounted procfs PID 1 is systemd, "
     "not the container's own s6-svscan"),
    ("P6-OWN-PROCFS-IS-THE-HOSTS", "P6", "own_pid1_comm", "systemd",
     "containment: P6 container PID 1 is systemd, not the image's own s6-svscan"),
    ("P6-HOST-SIZED-PROCESS-TABLE", "P6", "own_pid_count", "112",
     "containment: P6 own process table has 112 processes, "
     "over the image's bound of 32"),
    ("P2-MAIN-PROGRAM-AMBIGUOUS", "P2", "main_pids", "42,43",
     "containment: P2 main program cmdline is ambiguous (2 processes)"),
]


@pytest.mark.parametrize("mutant_id,canary,field,value,expected", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_each_property_mutation_is_caught(tmp_path, mutant_id, canary, field, value, expected):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == canary:
            rec["observed"][field] = value
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, f"{mutant_id} survived: {proc.stdout}"
    assert expected in proc.stdout, f"{mutant_id}: got {proc.stdout!r}"


def test_p4_secret_env_key_is_caught(tmp_path):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P4":
            rec["observed"]["secret_env_keys"] = "OPENAI_API_KEY"
            rec["observed"]["secret_env_count"] = "1"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P4 1 secret-bearing env key(s) in the runtime env: OPENAI_API_KEY" in proc.stdout


def test_p4_count_and_names_must_agree(tmp_path):
    """A canary reporting count 0 beside a non-empty key list is malformed, not
    a pass."""
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P4":
            rec["observed"]["secret_env_keys"] = ""
            rec["observed"]["secret_env_count"] = "3"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "secret_env_count 3 disagrees with 0 reported key name(s)" in proc.stdout


# --- the identity pins -----------------------------------------------------

def test_runsc_version_unpinned_is_caught(tmp_path):
    """RUNSC-VERSION-UNPINNED: a bundle from a different gVisor release must not
    satisfy the proof."""
    identity = passing_identity()
    identity["runsc_version"] = "release-20250101.0"
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "runtime identity runsc release-20250101.0, expected release-20260817.0" in proc.stdout


def test_runsc_sha_unpinned_is_caught(tmp_path):
    """SHA-UNPINNED: a runsc binary that is not the pinned artifact must not
    satisfy the proof, even when it reports the right version string."""
    identity = passing_identity()
    identity["runsc_sha256"] = "0" * 64
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "runsc sha256" in proc.stdout and "expected " + PINNED_RUNSC_SHA256 in proc.stdout


def test_identity_absent_fields_are_caught(tmp_path):
    identity = passing_identity()
    del identity["runsc_version"]
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "runtime identity runsc (absent)" in proc.stdout


# --- missing / duplicated / vacuous canary lines ---------------------------

@pytest.mark.parametrize("dropped", ALL_CANARIES)
def test_missing_canary_line_fails_by_name(tmp_path, dropped):
    """CANARY-MISSING-IGNORED: dropping ANY canary — including the two that are
    only recorded — must fail by name, never pass silently."""
    lines = [rec for rec in passing_canaries() if rec["canary"] != dropped]
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert f"containment: {dropped} canary line absent" in proc.stdout


def test_duplicate_canary_line_is_rejected(tmp_path):
    lines = passing_canaries()
    lines.append(lines[0])
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P1 canary line duplicated" in proc.stdout


def test_canary_that_did_not_observe_is_not_a_pass(tmp_path):
    """A canary reporting rc != 0 never took its observation. Its empty fields
    must not read as a satisfied property."""
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P4":
            rec["rc"] = 1
            rec["observed"]["secret_env_keys"] = ""
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "P4 canary did not complete its observation (rc 1)" in proc.stdout


def test_p5_without_the_sentinel_env_var_fails_closed(tmp_path):
    """The one environment input on a decision path in this proof. Unset, the
    canary reports rc 1 and the checker refuses the bundle — it must never read
    as 'the sentinel was unreadable, so containment holds'."""
    proc = subprocess.run(["sh", str(CANARY_DIR / "P5.sh")], capture_output=True,
                          text=True, timeout=60,
                          env={k: v for k, v in os.environ.items()
                               if k != "S0_08_SENTINEL_PATH"})
    rec = json.loads(proc.stdout.strip())
    assert rec["rc"] == 1
    assert rec["observed"]["sentinel_error"] == "S0_08_SENTINEL_PATH not supplied"

    lines = [rec if r["canary"] == "P5" else r for r in passing_canaries()]
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    check = run_checker(bundle)
    assert check.returncode == 1
    assert "P5 canary did not complete its observation (rc 1)" in check.stdout


def test_unknown_canary_id_is_rejected(tmp_path):
    lines = passing_canaries()
    lines[0] = dict(lines[0], canary="P9")
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "unknown canary id" in proc.stdout


# --- P5's positive control -------------------------------------------------

def test_p5_without_the_host_control_is_not_a_pass(tmp_path):
    """'Unreadable inside' proves nothing unless the runner proved the sentinel
    readable on the host at the same path."""
    identity = passing_identity()
    del identity["sentinel_host_read"]
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "records no sentinel_host_read control" in proc.stdout


def test_p5_path_mismatch_is_caught(tmp_path):
    """A canary that read a DIFFERENT path than the one the host control wrote
    proves nothing about that sentinel."""
    identity = passing_identity()
    identity["sentinel_host_read"]["path"] = "/home/owner/some-other-file"
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "P5 sentinel path mismatch" in proc.stdout


def test_p5_host_control_that_did_not_read_is_caught(tmp_path):
    identity = passing_identity()
    identity["sentinel_host_read"]["readable"] = False
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "host-side sentinel control did not read the sentinel" in proc.stdout


# --- FIFO / non-regular evidence paths -------------------------------------

@pytest.mark.parametrize("victim", ["canaries.jsonl", "runtime-identity.json"])
def test_fifo_at_an_evidence_path_is_refused_not_hung(tmp_path, victim):
    """FIFO-EVIDENCE-HANG: a FIFO must be a named refusal. The subprocess
    timeout is the negative control — if the guard were removed, the read would
    block and this test would raise TimeoutExpired instead of asserting."""
    bundle = write_bundle(tmp_path / "pc-runsc")
    (bundle / victim).unlink()
    os.mkfifo(bundle / victim)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert f"containment: {victim} is not a regular file" in proc.stdout


def test_directory_at_an_evidence_path_is_refused(tmp_path):
    bundle = write_bundle(tmp_path / "pc-runsc")
    (bundle / "canaries.jsonl").unlink()
    (bundle / "canaries.jsonl").mkdir()
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "canaries.jsonl is not a regular file" in proc.stdout


def test_malformed_jsonl_line_is_named(tmp_path):
    bundle = write_bundle(tmp_path / "pc-runsc")
    (bundle / "canaries.jsonl").write_text("not json\n", encoding="utf-8")
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "canaries.jsonl line 1 is not JSON" in proc.stdout


# --- the marker gate: four verdicts ----------------------------------------

def test_marker_gate_malformed_matches_the_spec_leg():
    """The committed malformed fixture must produce exactly the reason
    proofs/S0-08/spec.json pins for its marker leg."""
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    leg = next(l for l in spec["legs"] if "marker_gate.py" in " ".join(l["cmd"]))
    proc = run_marker_gate(MALFORMED_MARKER)
    assert proc.returncode == 1
    assert proc.stdout.strip() == leg["expect"]["failure_reason"]


def test_marker_gate_absent(tmp_path):
    empty = tmp_path / "S0-XX"
    empty.mkdir()
    proc = run_marker_gate(empty)
    assert proc.returncode == 1
    assert proc.stdout.strip() == "marker: absent"


def test_marker_gate_expired_without_result_is_red(tmp_path):
    """MARKER-EXPIRED-PASSES: a deferral may not outlive its blocker."""
    proof = tmp_path / "S0-08"
    proof.mkdir()
    shutil.copy(ROOT / "proofs" / "S0-08" / "blocked.json", proof / "blocked.json")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert proc.stdout.strip() == "marker: expired - the proof must run"


def test_marker_gate_completed_transition(tmp_path):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    (proof / "result.json").write_text('{"proof_id": "S0-08"}\n', encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "marker: completed transition"


def test_marker_gate_expired_with_result_is_green(tmp_path):
    """The transition is only complete once the proof actually ran."""
    proof = tmp_path / "S0-08"
    proof.mkdir()
    shutil.copy(ROOT / "proofs" / "S0-08" / "blocked.json", proof / "blocked.json")
    (proof / "result.json").write_text('{"proof_id": "S0-08"}\n', encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "marker: expired"


def test_marker_gate_honest_deferral_is_green(tmp_path):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    payload = json.loads((ROOT / "proofs" / "S0-08" / "blocked.json").read_text())
    payload["marker"]["blocker_status"] = "absent"
    (proof / "blocked.json").write_text(json.dumps(payload), encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "marker: absent"


@pytest.mark.parametrize("field", ["probe_run", "blocker_status", "unblock_condition"])
def test_marker_gate_names_each_missing_field(tmp_path, field):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    payload = json.loads((ROOT / "proofs" / "S0-08" / "blocked.json").read_text())
    del payload["marker"][field]
    (proof / "blocked.json").write_text(json.dumps(payload), encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert proc.stdout.strip() == f"marker: malformed: {field}"


def test_marker_gate_rejects_out_of_enum_status(tmp_path):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    payload = json.loads((ROOT / "proofs" / "S0-08" / "blocked.json").read_text())
    payload["marker"]["blocker_status"] = "fine"
    (proof / "blocked.json").write_text(json.dumps(payload), encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert proc.stdout.strip() == "marker: malformed: blocker_status 'fine'"


def test_marker_gate_result_presence_alone_does_not_retire_the_marker(tmp_path):
    """AF-AP-40: a file merely NAMED result.json is not a proof that ran."""
    proof = tmp_path / "S0-08"
    proof.mkdir()
    (proof / "result.json").write_text("not json\n", encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert proc.stdout.strip() == "marker: malformed: result.json is not readable JSON"


def test_marker_gate_rejects_a_result_from_another_proof(tmp_path):
    """AF-AP-10: one artifact's identity must not retire another proof's marker."""
    proof = tmp_path / "S0-08"
    proof.mkdir()
    (proof / "result.json").write_text('{"proof_id": "S0-07"}\n', encoding="utf-8")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert "result.json proof_id 'S0-07' does not match S0-08" in proc.stdout


def test_marker_gate_result_fifo_is_refused_not_hung(tmp_path):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    shutil.copy(ROOT / "proofs" / "S0-08" / "blocked.json", proof / "blocked.json")
    os.mkfifo(proof / "result.json")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert "marker: malformed: result.json is not a regular file" in proc.stdout


def test_marker_gate_fifo_is_refused_not_hung(tmp_path):
    proof = tmp_path / "S0-08"
    proof.mkdir()
    os.mkfifo(proof / "blocked.json")
    proc = run_marker_gate(proof)
    assert proc.returncode == 1
    assert "marker: malformed: blocked.json is not a regular file" in proc.stdout


def test_live_marker_is_expired_and_red():
    """The committed proofs/S0-08/blocked.json reads `expired` and no result.json
    exists yet, so the gate is RED on the real tree. When the coordinator mints
    result.json and removes blocked.json this flips to the completed
    transition — that is the state change this gate exists to force."""
    proc = run_marker_gate(ROOT / "proofs" / "S0-08")
    assert proc.returncode == 1
    assert proc.stdout.strip() == "marker: expired - the proof must run"


# --- canary shape ----------------------------------------------------------

def test_every_canary_script_exists_and_is_executable():
    for canary in ALL_CANARIES:
        script = CANARY_DIR / f"{canary}.sh"
        assert script.is_file(), f"{canary}.sh missing"
        assert os.access(script, os.X_OK), f"{canary}.sh is not executable"


def test_every_canary_script_is_shell_clean():
    for canary in ALL_CANARIES:
        proc = subprocess.run(["sh", "-n", str(CANARY_DIR / f"{canary}.sh")],
                              capture_output=True, text=True, timeout=30)
        assert proc.returncode == 0, f"{canary}.sh: {proc.stderr}"


def test_committed_bundle_carries_every_canary_and_parses():
    """Every one of the eight scripts' real output parses as a JSON object with
    the pinned key set and an id in P1..P8."""
    seen = set()
    for index, line in enumerate(
            (CRUN_BUNDLE / "canaries.jsonl").read_text().splitlines(), start=1):
        rec = json.loads(line)
        assert set(rec) == {"canary", "expect", "observed", "rc"}, f"line {index}"
        assert rec["canary"] in ALL_CANARIES
        assert isinstance(rec["observed"], dict) and rec["observed"]
        assert isinstance(rec["rc"], int) and not isinstance(rec["rc"], bool)
        seen.add(rec["canary"])
    assert seen == set(ALL_CANARIES)


@pytest.mark.parametrize("canary", ["P1", "P2", "P4", "P7", "P8"])
def test_read_only_canaries_emit_one_parseable_line_when_run(canary):
    """Run the side-effect-free canaries for real and parse their output. P3
    spawns tools, P5 needs a sentinel and P6 mounts, so they are covered by the
    committed bundle and by their own tests instead."""
    proc = subprocess.run(["sh", str(CANARY_DIR / f"{canary}.sh")],
                          capture_output=True, text=True, timeout=60)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert len(lines) == 1, f"{canary} emitted {len(lines)} lines"
    rec = json.loads(lines[0])
    assert rec["canary"] == canary
    assert set(rec) == {"canary", "expect", "observed", "rc"}


@pytest.mark.parametrize("canary,expected_reason_fragment", [
    ("P1", "containment: P1 host kernel "),
    ("P2", "containment: P2 "),
    ("P4", "containment: P4 "),
])
def test_live_canary_output_binds_to_the_fields_the_checker_reads(
        tmp_path, canary, expected_reason_fragment):
    """Class-14 guard: the synthetic bundles above mirror the canaries' field
    NAMES. If a canary renamed a field, every synthetic test would still pass
    while the real proof broke.

    So: run the canary FOR REAL, splice its line into an otherwise-passing
    bundle, and require the checker to fail on the PROPERTY. A rename shows up
    as "observation '<name>' absent" instead — a different message, and this
    test names the difference."""
    # The uncontained run must be OBSERVABLY uncontained on every host: P4 reads its OWN environ, and a
    # host whose test user carries no secret-named variable and no docker socket (the PC's pytest worker,
    # 2026-09-08: `PASS … 6 properties asserted` where the sandbox's root env made it fail) would let an
    # uncontained P4 look contained. So plant ONE secret-NAMED variable (a non-secret value) for the canary
    # to observe -- the binding is then proven by the checker naming it, on any host.
    proc = subprocess.run(["sh", str(CANARY_DIR / f"{canary}.sh")],
                          capture_output=True, text=True, timeout=60,
                          env={**os.environ, "S0_08_SENTINEL_PATH": SENTINEL_PATH,
                               "S0_08_MAIN_CMDLINE": MAIN_CMD,
                               "S0_08_LIVE_PROBE_KEY": "not-a-secret"})
    live = json.loads(proc.stdout.strip())
    lines = [live if rec["canary"] == canary else rec for rec in passing_canaries()]
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    check = run_checker(bundle)

    assert check.returncode == 1, (
        f"{canary} ran uncontained on this host, so the checker must reject it: "
        f"{check.stdout}")
    # The rename detector is `containment: <Pn> observation '<name>' absent`.
    # The QUOTE is load-bearing: "did not complete its observation (rc 1)" also
    # contains the bare word, and on a venue where a canary cannot observe it
    # would fire this guard for the wrong reason.
    assert "observation '" not in check.stdout, (
        f"{canary}.sh no longer emits a field the checker reads: {check.stdout}")

    # VENUE BRANCH, asserted rather than assumed. Whether a canary can take its
    # observation is a property of the RUNNING USER: P1 reads dmesg, which
    # kernel.dmesg_restrict=1 refuses to an unprivileged caller. The sandbox
    # runs this suite as root and never hits it; the PC's pytest user is uid
    # 1000 and does (2026-09-08). Inside gVisor dmesg works even for uid 65534,
    # so the REAL containment run takes neither of these paths.
    if canary == "P1":
        assert live["rc"] == (0 if dmesg_works() else 1), (
            f"P1's rc must track whether dmesg actually works here ({venue()}); "
            f"it reported rc {live['rc']} with "
            f"dmesg_first_line {live['observed']['dmesg_first_line']!r}")
    if live["rc"] != 0:
        assert live["observed"].get("dmesg_first_line", "") == "", (
            f"{canary} reported rc {live['rc']} beside a non-empty observation")
        assert (f"containment: {canary} canary did not complete its observation "
                f"(rc {live['rc']})") in check.stdout, (
            f"{canary} could not observe on this venue ({venue()}), so the checker "
            f"must refuse the line BY NAME rather than judge its empty fields: "
            f"{check.stdout}")
        # The field binding still has to be proven. Re-run with the canary's OWN
        # STATUS forced to 0 and every OBSERVATION untouched, so the reason now
        # comes from the live fields exactly as on a venue where it observed.
        observed_live = dict(live, rc=0)
        lines = [observed_live if rec["canary"] == canary else rec
                 for rec in passing_canaries()]
        check = run_checker(write_bundle(tmp_path / "pc-runsc-rc0", canaries=lines))
        assert check.returncode == 1, check.stdout
        assert "observation '" not in check.stdout, (
            f"{canary}.sh no longer emits a field the checker reads: {check.stdout}")
    assert expected_reason_fragment in check.stdout, check.stdout
    if canary == "P4":
        # The planted key is the ONLY host-independent thing P4 can be caught
        # on, and the generic "containment: P4 " prefix above is satisfied by
        # whichever P4 assertion fires FIRST — on a host with a docker socket
        # that is the socket, so P4.sh reverting to reading /proc/1/environ (a
        # DIFFERENT environment) went unnoticed (VERIFY-G1 F7, mutant 40).
        # check_p4 asserts the socket before the env, so clear that one field
        # and require the checker to name the key it read from the LIVE line.
        unsocketed = dict(live, observed=dict(live["observed"], docker_sock="absent"))
        lines = [unsocketed if rec["canary"] == "P4" else rec
                 for rec in passing_canaries()]
        env_check = run_checker(write_bundle(tmp_path / "pc-runsc-env", canaries=lines))
        assert env_check.returncode == 1, env_check.stdout
        assert "S0_08_LIVE_PROBE_KEY" in env_check.stdout, env_check.stdout


def test_canaries_never_print_a_verdict():
    """CANARY-VERDICT-IN-SCRIPT: a canary states observations. The moment one
    prints its own PASS/FAIL the checker stops being the only judge."""
    for canary in ALL_CANARIES:
        text = (CANARY_DIR / f"{canary}.sh").read_text()
        for banned in ('"PASS"', "'PASS'", '"FAIL"', "'FAIL'",
                       "echo PASS", "echo FAIL", "printf 'PASS", 'printf "PASS'):
            assert banned not in text, f"{canary}.sh emits a verdict: {banned}"


def test_a_canary_line_carrying_a_verdict_is_still_judged_by_the_checker(tmp_path):
    """Even if a canary were rewritten to shout PASS, the checker reads the
    OBSERVATIONS — the verdict word cannot rescue a failing property."""
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P1":
            rec["observed"]["uname_r"] = "6.17.11-200.fc42"
            rec["expect"] = "PASS"
            rec["observed"]["verdict"] = "PASS"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P1 host kernel 6.17.11-200.fc42, not gVisor" in proc.stdout


# --- the spec itself -------------------------------------------------------

def test_spec_validates_against_the_schema():
    schema = json.loads((ROOT / "proofs" / "schemas" / "spec.schema.json").read_text())
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    jsonschema.validate(spec, schema)


def test_spec_negative_legs_reproduce_their_pinned_reasons():
    """Every negative leg in the spec is executed here exactly as the runner
    would execute it, and must print the reason the spec pins. A drifted
    reason string (SPEC-REASON-DRIFT) fails this test, not a later PC run."""
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    for leg in spec["legs"]:
        if leg["leg"] != "negative":
            continue
        cmd = [sys.executable] + leg["cmd"][1:]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              timeout=leg["timeout_s"])
        assert proc.returncode == leg["expect"]["exit_code"], f"{leg['cmd']}: {proc.stdout}"
        combined = proc.stdout + "\n" + proc.stderr
        assert any(leg["expect"]["failure_reason"] in line
                   for line in combined.splitlines()), \
            f"{leg['cmd']} did not print its pinned reason: {combined!r}"


def test_spec_positive_leg_defers_until_the_pc_run_lands():
    """The positive leg's evidence directory does not exist yet. The runner
    treats exit 2 as capability-unavailable and preserves the artifact
    (scripts/proof-runner:181-185), so this is the honest pre-run state."""
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    leg = next(l for l in spec["legs"] if l["leg"] == "positive")
    evidence = ROOT / leg["cmd"][2]
    assert not evidence.exists(), "the PC run has landed; update this test's premise"
    proc = subprocess.run([sys.executable] + leg["cmd"][1:], cwd=ROOT,
                          capture_output=True, text=True, timeout=leg["timeout_s"])
    assert proc.returncode == 2
    assert proc.stdout.strip() == "deferred: containment evidence not captured"


def test_pc_runner_is_bash_clean():
    runner = ROOT / "proofs" / "S0-08" / "tools" / "pc" / "run_containment.sh"
    proc = subprocess.run(["bash", "-n", str(runner)],
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr


PC_RUNNER = ROOT / "proofs" / "S0-08" / "tools" / "pc" / "run_containment.sh"


def runner_code() -> str:
    """The runner's CODE, with whole-line comments dropped.

    AF-AP-25: a banned-substring scan over raw file text matches the file's own
    prose. Both of these assertions first fired on the comments that EXPLAIN why
    pkill and host networking are forbidden — the check must read code, not
    documentation."""
    return "\n".join(
        line for line in PC_RUNNER.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )


def test_pc_runner_tears_down_by_id_never_by_name():
    """AF-AP-34: this runs on the owner's shared host. A name match or a pkill
    could reap the owner's own containers."""
    code = runner_code()
    assert 'podman rm -f "$CID"' in code
    assert "pkill" not in code
    assert "killall" not in code
    assert "podman rm -f hermes" not in code


def test_pc_runner_pins_the_verified_runsc_flags():
    code = runner_code()
    assert "--runtime-flag ignore-cgroups" in code
    assert "--security-opt label=disable" in code
    # The containment run must not inherit the compose file's host networking.
    assert "--network none" in code
    assert "network_mode: host" not in code
    assert "--network host" not in code


def test_runner_code_filter_actually_removes_comments():
    """Negative control for the filter above: if it stopped stripping comments,
    the two tests it serves would go back to matching prose and pass/fail for
    the wrong reason."""
    raw = PC_RUNNER.read_text()
    assert "pkill" in raw, "the explanatory comment naming pkill is gone"
    assert "pkill" not in runner_code()


# ===========================================================================
# Round 2 (VERIFY-G1): the canaries observe as the RUNTIME USER, P6 asserts
# under the capability set that user HAS, the main program is unambiguous, and
# the evidence is bound to the image and argv it came from.
# ===========================================================================

# --- F1 · P6 under the runtime user's capability set -----------------------

def _mount_failed_p6(canaries, **overrides):
    """The P6 line the RUNTIME USER actually produces: `mount -t proc` needs
    CAP_SYS_ADMIN and uid 10000 has none. Measured inside real gVisor as uid
    65534 (2026-09-08): rc 32, `must be superuser to use mount.`"""
    for rec in canaries:
        if rec["canary"] == "P6":
            rec["observed"].update(
                mount_proc_rc="32",
                mount_proc_error="mount: /tmp/s0-08-p6-proc.2: must be superuser to use mount.",
                mounted_pid1_comm="", mounted_pid_count="")
            rec["observed"].update(overrides)
    return canaries


def test_p6_mount_failure_still_asserts_the_containment_signature(tmp_path):
    """The bundle the first PC run will produce: the mount could not run. That
    must still assert something."""
    bundle = write_bundle(tmp_path / "pc-runsc",
                          canaries=_mount_failed_p6(passing_canaries()))
    proc = run_checker(bundle)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip().startswith("PASS: S0-08 gvisor-containment")


def test_p6_mount_failure_is_not_a_silent_pass(tmp_path):
    """VERIFY-G1 bundle A5c. `if mount_rc == "0":` had no else, so a bundle
    whose OWN procfs says PID 1 is the host's init passed with six properties
    'asserted'. RED on 517c65e: returncode 0."""
    lines = _mount_failed_p6(passing_canaries(), own_pid1_comm="systemd")
    for rec in lines:                      # keep P2's view consistent with P6's
        if rec["canary"] == "P2":
            rec["observed"]["pid1_comm"] = "systemd"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert ("containment: P6 container PID 1 is systemd, "
            "not the image's own s6-svscan") in proc.stdout


def test_p6_mount_failure_without_a_reason_is_caught(tmp_path):
    """VERIFY-G1 bundle A5b: a mount that 'failed' with rc 32 and no message
    is an unexplained observation, not evidence."""
    lines = _mount_failed_p6(passing_canaries(), mount_proc_error="")
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: P6 mount -t proc failed with rc 32 and no reason" in proc.stdout


def test_p6_pid1_comm_must_agree_with_p2s_independent_read(tmp_path):
    """Two canaries, exec'd as two separate processes, read /proc/1/comm.
    Forging one line is not enough."""
    lines = _mount_failed_p6(passing_canaries())
    for rec in lines:
        if rec["canary"] == "P2":
            rec["observed"]["pid1_comm"] = "systemd"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: P6 PID 1 comm s6-svscan disagrees with P2's systemd" in proc.stdout


def test_p6_own_pid_count_must_be_a_count(tmp_path):
    lines = _mount_failed_p6(passing_canaries(), own_pid_count="")
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P6 own_pid_count (absent) is not a count" in proc.stdout


# --- F2 / F12 · one unambiguous main program, one source for its cmdline ----

def test_p2_ambiguous_main_cmdline_is_refused(tmp_path):
    """The image's supervised `main-hermes` service runs `exec sleep infinity`
    as root and is up by default, so `sleep infinity` had two holders and P2's
    subject was decided by /proc glob order. Ambiguity is a named refusal."""
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P2":
            rec["observed"]["main_pids"] = "17,42"
            rec["observed"]["main_uids"] = "0,10000"
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: P2 main program cmdline is ambiguous (2 processes)" in proc.stdout


def test_p2_pid_and_uid_lists_must_agree(tmp_path):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P2":
            rec["observed"]["main_uids"] = ""
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P2 main program pid/uid lists disagree (1 pid(s), 0 uid(s))" in proc.stdout


def test_p2_main_program_absent_is_named(tmp_path):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P2":
            rec["observed"]["main_pids"] = ""
            rec["observed"]["main_uids"] = ""
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: P2 main program uid (not found), expected 10000" in proc.stdout


def test_p2_without_the_main_cmdline_env_fails_closed():
    """The runner is the single source of the main cmdline. P2 has no default:
    unset, it reports rc 1 rather than inventing a subject to observe."""
    env = {k: v for k, v in os.environ.items() if k != "S0_08_MAIN_CMDLINE"}
    proc = subprocess.run(["sh", str(CANARY_DIR / "P2.sh")], capture_output=True,
                          text=True, timeout=60, env=env)
    rec = json.loads(proc.stdout.strip())
    assert rec["rc"] == 1, rec
    assert rec["observed"]["main_cmdline"] == ""
    assert rec["observed"]["main_pids"] == ""


def test_p2_reports_every_holder_of_the_main_cmdline(tmp_path):
    """LIVE: two processes carrying one cmdline. On 517c65e P2 stopped at the
    first match and reported that one uid — a coin flip decided by /proc glob
    order. Both must now appear, and the checker must refuse the pair."""
    # A cmdline unique to THIS test: the suite also runs under xdist, where a
    # shared literal would let another worker's processes join the match set.
    # One process each, no children to orphan.
    argv = [sys.executable, "-c", "import time; time.sleep(3600)",
            f"s0-08-collision-{tmp_path.name}"]
    cmdline = " ".join(argv)
    started = []
    try:
        for _ in range(2):
            started.append(subprocess.Popen(argv))
        proc = subprocess.run(["sh", str(CANARY_DIR / "P2.sh")], capture_output=True,
                              text=True, timeout=60,
                              env={**os.environ, "S0_08_MAIN_CMDLINE": cmdline})
        live = json.loads(proc.stdout.strip())
    finally:
        for child in started:
            child.kill()          # by handle — never by name, never pkill
            child.wait(timeout=30)
    pids = [p for p in live["observed"]["main_pids"].split(",") if p]
    assert sorted(pids) == sorted(str(c.pid) for c in started), live
    lines = [live if rec["canary"] == "P2" else rec for rec in passing_canaries()]
    check = run_checker(write_bundle(tmp_path / "pc-runsc", canaries=lines))
    assert check.returncode == 1, check.stdout
    assert "containment: P2 main program cmdline is ambiguous (2 processes)" in check.stdout


def test_runner_and_p2_share_one_source_for_the_main_cmdline():
    """MAINCMD-DRIFT: the two must not be able to disagree. The runner hands
    P2 the same string it gave `podman run`, and P2 has no literal at all."""
    code = runner_code()
    assert f'MAIN_CMD="{MAIN_CMD}"' in code
    assert '-e S0_08_MAIN_CMDLINE="$MAIN_CMD"' in code
    p2 = canary_code("P2")
    assert 'MAIN_CMDLINE="${S0_08_MAIN_CMDLINE:-}"' in p2
    assert "sleep infinity" not in p2 and MAIN_CMD not in p2
    # the readiness gate and the identity scan read the same shell variable
    assert code.count('[ "$c" = "\'"$MAIN_CMD"\'" ]') == 2


def test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper():
    """`sleep infinity` is the image's own supervised root no-op
    (hermes-agent docker/s6-rc.d/main-hermes/run:27, up by default via
    docker/s6-rc.d/user/contents.d/). Using it as the CMD gives the container
    two processes with one cmdline."""
    code = runner_code()
    assert 'MAIN_CMD="sleep infinity"' not in code
    assert f'MAIN_CMD="{MAIN_CMD}"' in code


# --- F3 · the canaries run as the runtime user -----------------------------

def test_pc_runner_execs_every_canary_as_the_runtime_user():
    """`podman exec` with no `--user` runs as the image's configured user,
    which is `USER root` (hermes-agent Dockerfile:298). P4 would then report a
    root exec's environment and P5 would attempt the host read as root."""
    code = runner_code()
    assert 'CANARY_EXEC_UID="10000"' in code
    assert 'podman exec -i --user "$CANARY_EXEC_UID"' in code


def test_pc_runner_checks_the_exec_status_not_only_its_output():
    """A canary that dies after printing its line is otherwise
    indistinguishable from one that succeeded."""
    code = runner_code()
    assert "exec_rc=$?" in code
    assert 'if [ "$exec_rc" -ne 0 ]; then' in code
    # and no pipeline between the exec and `$?`
    assert "sh -s < \"$script\" 2>/dev/null | tail -n 1)" not in code


def test_canaries_exec_d_as_root_are_refused(tmp_path):
    """The evidence must record WHO took it. A bundle whose canaries ran as
    uid 0 is evidence about a different subject. PASSED on 517c65e."""
    identity = passing_identity()
    identity["canary_exec_user"] = "0"
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: canaries were exec'd as uid 0, expected 10000" in proc.stdout


def test_canary_exec_user_absent_is_refused(tmp_path):
    identity = passing_identity()
    del identity["canary_exec_user"]
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "containment: canaries were exec'd as uid (absent), expected 10000" in proc.stdout


# --- F4 · the evidence is bound to its image and its argv ------------------

def test_evidence_from_another_image_is_refused(tmp_path):
    """VERIFY-G1 bundle A7: an alpine image at commit `deadbeef`. PASSED on
    517c65e — the checker pinned runsc and nothing else."""
    identity = passing_identity()
    identity["image"] = "docker.io/library/alpine:3.20"
    identity["image_source_commit"] = "deadbeef"
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert f"containment: image_source_commit deadbeef, expected {PINNED_IMAGE_SOURCE_COMMIT}" \
        in proc.stdout


def test_host_networked_privileged_run_argv_is_refused(tmp_path):
    """VERIFY-G1 bundle A8: `--network host --privileged` in the recorded argv.
    PASSED on 517c65e — P7's whole claim was enforced by a static test on the
    runner's source, never on the evidence."""
    identity = passing_identity()
    identity["run_argv"] = ["podman", "run", "-d", "--runtime", "/usr/local/bin/runsc",
                            "--runtime-flag", "ignore-cgroups", "--security-opt",
                            "label=disable", "--network", "host", "--privileged",
                            "localhost/hermes-s0-08:527da608"] + MAIN_CMD.split()
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: run_argv is missing --network none" in proc.stdout


@pytest.mark.parametrize("banned", ["--privileged", "-v", "--volume", "--mount",
                                    "--pid=host", "--cap-add", "--network=host",
                                    "--net=host"])
def test_each_banned_run_argv_token_is_refused(tmp_path, banned):
    identity = passing_identity()
    identity["run_argv"] = identity["run_argv"][:-2] + [banned] + identity["run_argv"][-2:]
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert f"containment: run_argv carries {banned}" in proc.stdout


@pytest.mark.parametrize("flag,value", [("--runtime-flag", "ignore-cgroups"),
                                        ("--security-opt", "label=disable"),
                                        ("--network", "none")])
def test_each_required_run_argv_pair_is_required(tmp_path, flag, value):
    identity = passing_identity()
    argv = list(identity["run_argv"])
    index = argv.index(flag)
    del argv[index:index + 2]
    identity["run_argv"] = argv
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert f"containment: run_argv is missing {flag} {value}" in proc.stdout


def test_a_second_network_flag_with_another_value_is_refused(tmp_path):
    """`--network none` being PRESENT is not the same as `--network` never
    naming anything else."""
    identity = passing_identity()
    identity["run_argv"] = identity["run_argv"] + ["--network", "slirp4netns"]
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: run_argv sets --network slirp4netns, expected none" in proc.stdout


def test_run_argv_of_the_wrong_type_is_named(tmp_path):
    identity = passing_identity()
    identity["run_argv"] = "podman run -d --network none"
    bundle = write_bundle(tmp_path / "pc-runsc", identity=identity)
    proc = run_checker(bundle)
    assert proc.returncode == 1
    assert "run_argv is not a list of strings" in proc.stdout


# --- F15 · a recorded canary that never observed ---------------------------

def test_recorded_canary_that_did_not_observe_is_refused(tmp_path):
    """VERIFY-G1 bundle A12. 'The run RECORDS its egress and cgroup posture'
    was satisfiable by an empty record. PASSED on 517c65e."""
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] in ("P7", "P8"):
            rec["rc"] = 7
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: P7 recorded canary did not observe (rc 7)" in proc.stdout


# --- F19 · observations are strings, not whatever JSON offered -------------

def test_a_non_string_observation_is_named_not_coerced(tmp_path):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P2":
            rec["observed"]["pid1_uid"] = 0
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    proc = run_checker(bundle)
    assert proc.returncode == 1, proc.stdout
    assert "containment: P2 pid1_uid is not a string" in proc.stdout


# --- helpers for the live-canary regressions -------------------------------

def canary_code(canary: str) -> str:
    """A canary's CODE, with whole-line comments dropped. AF-AP-25: a
    banned-substring scan over raw file text matches the file's own prose, and
    P2.sh's comments explain the very cmdline collision they must not match."""
    return "\n".join(
        line for line in (CANARY_DIR / f"{canary}.sh").read_text().splitlines()
        if not line.lstrip().startswith("#")
    )


def test_canary_code_filter_actually_removes_comments():
    """Negative control for the filter above."""
    raw = (CANARY_DIR / "P2.sh").read_text()
    assert "sleep infinity" in raw, "the comment naming the image's sleeper is gone"
    assert "sleep infinity" not in canary_code("P2")


def _fake_bin(tmp_path, name, body):
    """A directory holding one executable stand-in, to be prepended to PATH."""
    d = tmp_path / f"bin-{name}"
    d.mkdir(exist_ok=True)
    script = d / name
    script.write_text(body, encoding="utf-8")
    script.chmod(0o755)
    return d


def _run_canary(canary, tmp_path, extra_path=None, **env):
    environ = {**os.environ, **env}
    if extra_path is not None:
        environ["PATH"] = f"{extra_path}:{environ['PATH']}"
    proc = subprocess.run(["sh", str(CANARY_DIR / f"{canary}.sh")],
                          capture_output=True, text=True, timeout=60, env=environ)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


# --- F13 · P1's dmesg failure must be visible in rc ------------------------

def test_p1_records_a_failing_dmesg_as_not_observed(tmp_path):
    """`dmesg | head` reports HEAD's status, which is always 0, so a refused
    dmesg produced an empty first line beside rc 0 and the checker answered
    with an empty-tailed reason instead of 'did not observe'. Driven with a
    stand-in so the result does not depend on the venue's dmesg_restrict."""
    failing = _fake_bin(tmp_path, "dmesg", "#!/bin/sh\nexit 1\n")
    rec = _run_canary("P1", tmp_path, extra_path=failing)
    assert rec["rc"] == 1, rec
    assert rec["observed"]["dmesg_first_line"] == ""

    # NEGATIVE CONTROL: the same canary, a dmesg that works — rc 0 and the line
    # is carried through. Without this the test above passes on any P1 that
    # always reports rc 1.
    working = _fake_bin(tmp_path, "dmesg",
                        "#!/bin/sh\necho '[    0.000000] Starting gVisor...'\n")
    ok = _run_canary("P1", tmp_path, extra_path=working)
    assert ok["rc"] == 0, ok
    assert ok["observed"]["dmesg_first_line"] == "[    0.000000] Starting gVisor..."


# --- F8 · P3 captures each tool's OWN status -------------------------------

def test_p3_records_a_failing_tools_own_status(tmp_path):
    """The piped-rc fail-open: `TOOL_OUT=$("$@" 2>&1 | head -n 1); TOOL_RC=$?`
    reads HEAD's status and reports a broken tool as rc 0. Nothing ran P3.sh
    live before (VERIFY-G1 F8, mutant 37)."""
    broken = _fake_bin(tmp_path, "node",
                       "#!/bin/sh\necho 'node: cannot execute binary file'\nexit 3\n")
    rec = _run_canary("P3", tmp_path, extra_path=broken)
    assert rec["observed"]["node_rc"] == "3", rec
    assert rec["observed"]["node_out"] == "node: cannot execute binary file"

    # NEGATIVE CONTROL: a working stand-in must read 0 through the same path.
    working = _fake_bin(tmp_path, "node", "#!/bin/sh\necho v26.0.0\n")
    assert _run_canary("P3", tmp_path, extra_path=working)["observed"]["node_rc"] == "0"

    # and the checker names the failing tool and quotes its first line. The
    # three tools the checker asserts BEFORE node are the image's, absent on
    # this host, so only their fields are replaced — node's rc and output are
    # the live measurement above and they are what produces the reason.
    passing_tools = {"hermes_rc": "0", "hermes_out": "hermes 0.21.0",
                     "python_import_rc": "0", "python_import_out": "import-ok"}
    spliced = dict(rec, observed=dict(rec["observed"], **passing_tools))
    lines = [spliced if r["canary"] == "P3" else r for r in passing_canaries()]
    check = run_checker(write_bundle(tmp_path / "pc-runsc", canaries=lines))
    assert check.returncode == 1, check.stdout
    assert "containment: P3 node exited 3: node: cannot execute binary file" in check.stdout


# --- F10 · the device census has content -----------------------------------

def test_p6_device_census_names_the_hosts_raw_devices(tmp_path):
    """Mutant 41 emptied the census list and nothing noticed — and when the
    mount cannot run, the census is the only thing P6 asserts about devices.
    `/dev/kmsg` is present on any Linux host this suite runs on."""
    assert Path("/dev/kmsg").exists(), "premise: this host exposes /dev/kmsg"
    rec = _run_canary("P6", tmp_path)
    devices = rec["observed"]["dangerous_devices"].split(",")
    assert "/dev/kmsg" in devices, rec["observed"]["dangerous_devices"]
    assert "kmsg" in rec["observed"]["dev_entries"].split(",")

    lines = [rec if r["canary"] == "P6" else r for r in passing_canaries()]
    check = run_checker(write_bundle(tmp_path / "pc-runsc", canaries=lines))
    assert check.returncode == 1, check.stdout
    assert "containment: P6 raw host devices present: " in check.stdout
    assert "/dev/kmsg" in check.stdout


# --- F11 · P5 can actually detect a readable sentinel ----------------------

def test_p5_detects_a_readable_sentinel_and_the_checker_refuses_it(tmp_path):
    """Mutant 42 hardcoded `sentinel_readable="no"` — the answer P5 must give
    only when the host file is genuinely unreachable — and survived. Nothing
    tested that P5 can say `yes` at all."""
    sentinel = tmp_path / "s0-08-host-sentinel-deadbeefdeadbeef"
    sentinel.write_text("s0-08-host-sentinel deadbeef\n", encoding="utf-8")
    rec = _run_canary("P5", tmp_path, S0_08_SENTINEL_PATH=str(sentinel))
    assert rec["observed"]["sentinel_readable"] == "yes", rec
    assert rec["observed"]["sentinel_error"] == ""

    # NEGATIVE CONTROL: the same canary on a path that does not exist.
    missing = _run_canary("P5", tmp_path,
                          S0_08_SENTINEL_PATH=str(tmp_path / "never-written"))
    assert missing["observed"]["sentinel_readable"] == "no", missing
    assert missing["observed"]["sentinel_error"] != ""

    identity = passing_identity()
    identity["sentinel_host_read"] = {"path": str(sentinel), "readable": True}
    lines = [rec if r["canary"] == "P5" else r for r in passing_canaries()]
    check = run_checker(write_bundle(tmp_path / "pc-runsc", canaries=lines,
                                     identity=identity))
    assert check.returncode == 1, check.stdout
    assert "containment: P5 host sentinel readable inside the container" in check.stdout


# --- F6 · the identity generator emits the MEASURED host read --------------

def _identity_program() -> str:
    """The runner's embedded identity generator, extracted from its bytes."""
    text = PC_RUNNER.read_text()
    start = text.index("<<'PYIDENT'\n") + len("<<'PYIDENT'\n")
    end = text.index("\nPYIDENT\n", start)
    program = text[start:end]
    assert "sentinel_host_read" in program, "extraction missed the generator"
    return program


def _run_identity_program(tmp_path, **fields):
    meta = tmp_path / "meta"
    meta.mkdir(exist_ok=True)
    defaults = {
        "runsc_version": "release-20260817.0", "runsc_sha256": "0" * 64,
        "podman_version": "podman version 5.7.0", "image_digest": "sha256:0",
        "host_kernel": "6.17.11-200.fc42", "ps_tree": "1 root /init",
        "main_program_user": "hermes", "main_hermes_service": "up",
        "sentinel_path": SENTINEL_PATH, "sentinel_readable": "true",
        "canary_exec_user": CANARY_EXEC_UID, "container_id": "0123456789ab",
        "image": "localhost/hermes-s0-08:527da608",
        "runtime": "/usr/local/bin/runsc",
        "image_source_commit": PINNED_IMAGE_SOURCE_COMMIT,
        "captured_at": "2026-09-08T00:00:00Z",
    }
    defaults.update(fields)
    for name, value in defaults.items():
        (meta / name).write_text(value, encoding="utf-8")
    (meta / "run_argv").write_bytes(b"podman\0run\0-d\0")
    out = tmp_path / "runtime-identity.json"
    program = tmp_path / "ident.py"
    program.write_text(_identity_program(), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(program), str(meta), str(out)],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    return json.loads(out.read_text())


def test_identity_generator_emits_the_measured_sentinel_read(tmp_path):
    """`"readable": True` was a typed literal, never the SENTINEL_READABLE the
    runner measured — a positive control the producer asserts about itself.
    Mutant 38 changed it to the string "yes" and survived the whole suite."""
    assert _run_identity_program(tmp_path)["sentinel_host_read"]["readable"] is True
    unreadable = _run_identity_program(tmp_path, sentinel_readable="false")
    assert unreadable["sentinel_host_read"]["readable"] is False, unreadable

    # and the checker refuses the bundle that control produces
    identity = passing_identity()
    identity["sentinel_host_read"] = unreadable["sentinel_host_read"]
    identity["sentinel_host_read"]["path"] = SENTINEL_PATH
    check = run_checker(write_bundle(tmp_path / "pc-runsc", identity=identity))
    assert check.returncode == 1
    assert "host-side sentinel control did not read the sentinel" in check.stdout


def test_identity_generator_records_the_canary_exec_user(tmp_path):
    assert _run_identity_program(tmp_path)["canary_exec_user"] == CANARY_EXEC_UID
    assert _run_identity_program(tmp_path, canary_exec_user="0")["canary_exec_user"] == "0"


# --- F9 · the pinned-source refusal ----------------------------------------

def _preflight_snippet() -> str:
    """The runner's pinned-source preflight, extracted from its own bytes."""
    lines = PC_RUNNER.read_text().splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("s0_08_require_pinned_source() {"))
    end = next(i for i, l in enumerate(lines[start:], start=start) if l == "}")
    snippet = "\n".join(lines[start:end + 1])
    assert "rev-parse HEAD" in snippet, "extraction missed the git check"
    return snippet


def _scratch_repo(path: Path) -> str:
    path.mkdir(parents=True, exist_ok=True)
    (path / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (["git", "init", "-q"], ["git", "add", "Dockerfile"],
                ["git", "commit", "-q", "-m", "scratch"]):
        subprocess.run(cmd, cwd=path, check=True, capture_output=True, env=env)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, check=True,
                          capture_output=True, text=True, env=env)
    return head.stdout.strip()


def _drive_preflight(tmp_path, directory, expected):
    driver = tmp_path / "preflight.sh"
    driver.write_text(f"set -euo pipefail\n{_preflight_snippet()}\n"
                      f's0_08_require_pinned_source "$1" "$2"\necho ACCEPTED\n',
                      encoding="utf-8")
    return subprocess.run(["bash", str(driver), str(directory), expected],
                          capture_output=True, text=True, timeout=60)


def test_runner_refuses_a_source_checkout_at_the_wrong_commit(tmp_path):
    """`if [ "$actual_commit" != "$PINNED_COMMIT" ]` had no test at all
    (mutant 35: replaced with `if false`, 74 passed). Evidence built from a
    different checkout is evidence about a different system."""
    repo = tmp_path / "hermes-agent"
    head = _scratch_repo(repo)

    refused = _drive_preflight(tmp_path, repo, PINNED_IMAGE_SOURCE_COMMIT)
    assert refused.returncode == 2, refused.stdout + refused.stderr
    assert f"is at {head}, expected the pinned {PINNED_IMAGE_SOURCE_COMMIT}" in refused.stderr
    assert "ACCEPTED" not in refused.stdout

    # POSITIVE CONTROL: the same function, the same repo, its own commit — so
    # the refusal above is the commit comparison and not the function always
    # exiting 2.
    accepted = _drive_preflight(tmp_path, repo, head)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert accepted.stdout.strip() == "ACCEPTED"

    # a directory with no Dockerfile is the other refusal
    empty = tmp_path / "not-a-checkout"
    empty.mkdir()
    assert _drive_preflight(tmp_path, empty, head).returncode == 2


def test_runner_calls_the_preflight_with_the_pinned_commit():
    code = runner_code()
    assert f'PINNED_COMMIT="{PINNED_IMAGE_SOURCE_COMMIT}"' in code
    assert 's0_08_require_pinned_source "$SOURCE_DIR" "$PINNED_COMMIT"' in code


# --- F5 · the committed fixture is producible by the SHIPPED canaries -------

def _recapture_crun_bundle(tmp_path) -> dict:
    """Re-run PROVENANCE.md's capture command with the shipped canaries."""
    sentinel = tmp_path / "s0-08-crun-recapture-sentinel.txt"
    sentinel.write_text("s0-08 crun fixture sentinel\n", encoding="utf-8")
    clean = {"PATH": "/usr/bin:/bin"}
    out = {}
    for canary in ALL_CANARIES:
        env = dict(clean)
        if canary == "P2":
            env["S0_08_MAIN_CMDLINE"] = MAIN_CMD
        if canary == "P5":
            env["S0_08_SENTINEL_PATH"] = str(sentinel)
        proc = subprocess.run(["sh", f"proofs/S0-08/canaries/{canary}.sh"],
                              cwd=ROOT, capture_output=True, text=True,
                              timeout=120, env=env)
        assert proc.returncode == 0, f"{canary}: {proc.stderr}"
        out[canary] = json.loads(proc.stdout.strip())
    return out


def test_crun_fixture_is_producible_by_the_shipped_canaries(tmp_path):
    """AF-AP-42: the committed fixture's P4 line was the PRE-fix producer's
    output — the shipped P4.sh could no longer emit it, so a P4 regression
    would have been masked forever. Re-run the capture and hold the binding."""
    committed = {json.loads(line)["canary"]: json.loads(line)
                 for line in (CRUN_BUNDLE / "canaries.jsonl").read_text().splitlines()
                 if line.strip()}
    live = _recapture_crun_bundle(tmp_path)
    assert set(committed) == set(live) == set(ALL_CANARIES)

    # 1. every canary's observation KEY SET, exactly. A renamed or dropped
    #    field in any canary breaks this, on any host.
    for canary in ALL_CANARIES:
        assert set(committed[canary]["observed"]) == set(live[canary]["observed"]), canary
        assert committed[canary]["rc"] == 0, (
            f"the committed {canary} line was captured by a canary that observed")
        if canary != "P1":
            assert live[canary]["rc"] == 0, canary

    # 1b. P1 is the ONE canary whose rc depends on the RUNNING USER: it reads
    #     dmesg, and kernel.dmesg_restrict=1 refuses that to an unprivileged
    #     caller. The committed line was captured as root in the sandbox (rc 0);
    #     the PC re-runs this suite as uid 1000 and gets rc 1. Both arms assert
    #     — the expectation is DERIVED from a direct probe of this venue, never
    #     skipped. Inside gVisor dmesg works even for uid 65534, so the real
    #     containment run is unaffected either way (PROVENANCE.md says so too).
    readable = dmesg_works()
    assert live["P1"]["rc"] == (0 if readable else 1), (
        f"P1's rc must track whether dmesg works here ({venue()})")
    if readable:
        assert live["P1"]["observed"]["dmesg_first_line"], venue()
    else:
        assert live["P1"]["observed"]["dmesg_first_line"] == "", venue()

    # 2. the values the CAPTURE determines rather than the host: `env -i`
    #    means no secret-named variable is in scope, and an uncontained run
    #    can read the host sentinel it was pointed at.
    for source in (committed, live):
        assert source["P4"]["observed"]["secret_env_count"] == "0"
        assert source["P4"]["observed"]["secret_env_keys"] == ""
        assert source["P5"]["observed"]["sentinel_readable"] == "yes"
        assert source["P2"]["observed"]["main_cmdline"] == MAIN_CMD

    # 3. the host-dependent values, compared only when this IS the capture
    #    host. Stated, not silently skipped: PROVENANCE.md lists which values
    #    depend on the venue and the suite also runs on the PC.
    same_host = (live["P1"]["observed"]["uname_r"]
                 == committed["P1"]["observed"]["uname_r"])
    if same_host:
        for canary, field in (("P4", "docker_sock"), ("P6", "dangerous_devices"),
                              ("P6", "dev_entries"), ("P5", "home_entries")):
            assert committed[canary]["observed"][field] == live[canary]["observed"][field], \
                f"{canary}.{field} drifted on the capture host"
        # P1's boot line is the capture host's AND needs a user who can read it.
        if readable:
            assert (committed["P1"]["observed"]["dmesg_first_line"]
                    == live["P1"]["observed"]["dmesg_first_line"]), venue()
    else:
        assert live["P1"]["observed"]["uname_r"], "P1 still reports a kernel"


def test_crun_fixture_identity_carries_every_pinned_field(tmp_path):
    """The fixture's whole point: perfect identity metadata, observations from
    outside gVisor, and it must STILL fail — on P1, the first property."""
    identity = json.loads((CRUN_BUNDLE / "runtime-identity.json").read_text())
    assert identity["runsc_version"] == PINNED_RUNSC_VERSION
    assert identity["runsc_sha256"] == PINNED_RUNSC_SHA256
    assert identity["image_source_commit"] == PINNED_IMAGE_SOURCE_COMMIT
    assert identity["canary_exec_user"] == CANARY_EXEC_UID
    assert identity["run_argv"][-2:] == MAIN_CMD.split()
    proc = run_checker(CRUN_BUNDLE)
    assert proc.returncode == 1
    assert proc.stdout.startswith("failure_reason: containment: P1 host kernel ")


# --- F14 · the runner reaches both negative legs before it defers -----------

def _scratch_proof_root(tmp_path) -> Path:
    root = tmp_path / "root"
    (root / "proofs").mkdir(parents=True)
    (root / "scripts").mkdir()
    shutil.copytree(ROOT / "proofs" / "S0-08", root / "proofs" / "S0-08")
    shutil.copytree(ROOT / "proofs" / "schemas", root / "proofs" / "schemas")
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    for name in ("proof-runner", "validate-ledger"):
        shutil.copy(ROOT / "scripts" / name, root / "scripts" / name)
    return root


def _run_proof_runner(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "proof-runner"), "run",
         "--proof", "S0-08", "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=300)


def test_proof_runner_executes_both_negative_legs_before_deferring(tmp_path):
    """`scripts/proof-runner:181` raises Deferred on the FIRST leg that exits
    2, and the legs run in list order. With the positive leg first, neither
    negative control ever executed while the proof was deferred — the crun
    bundle and the marker gate were invisible to the ledger."""
    spec = json.loads((ROOT / "proofs" / "S0-08" / "spec.json").read_text())
    assert [leg["leg"] for leg in spec["legs"]] == ["negative", "negative", "positive"]

    root = _scratch_proof_root(tmp_path)
    deferred = _run_proof_runner(root)
    assert deferred.returncode == 2, deferred.stdout + deferred.stderr
    assert "capability-unavailable" in deferred.stderr
    assert not (root / "proofs" / "S0-08" / "result.json").exists()

    # Break the FIRST negative leg's fixture. If that leg really executes, the
    # runner now fails on it instead of deferring on the positive leg.
    fixture = root / "proofs" / "S0-08" / "fixtures" / "evidence-crun" / "canaries.jsonl"
    lines = fixture.read_text().splitlines()
    lines[0] = json.dumps({**json.loads(lines[0]), "observed": dict(
        json.loads(lines[0])["observed"], uname_r="9.9.9-not-the-pinned-kernel")})
    fixture.write_text("\n".join(lines) + "\n", encoding="utf-8")

    reached = _run_proof_runner(root)
    assert reached.returncode == 1, reached.stdout + reached.stderr
    assert "negative-control-unmet: S0-08" in reached.stderr

    # ORDER CONTROL: the same broken fixture with the positive leg first —
    # the runner defers before it ever reaches the negative leg. This is the
    # state 517c65e shipped.
    spec_path = root / "proofs" / "S0-08" / "spec.json"
    shipped = json.loads(spec_path.read_text())
    shipped["legs"] = ([leg for leg in shipped["legs"] if leg["leg"] == "positive"]
                       + [leg for leg in shipped["legs"] if leg["leg"] == "negative"])
    spec_path.write_text(json.dumps(shipped, indent=2) + "\n", encoding="utf-8")
    hidden = _run_proof_runner(root)
    assert hidden.returncode == 2, hidden.stdout + hidden.stderr
    assert "capability-unavailable" in hidden.stderr
