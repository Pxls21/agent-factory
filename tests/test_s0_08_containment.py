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
         "expect": "pid 1 uid 0 running s6 init; the main program (sleep infinity) runs as uid 10000",
         "observed": {"pid1_uid": "0", "pid1_comm": "init",
                      "pid1_cmdline": "/init /opt/hermes/docker/main-wrapper.sh sleep infinity",
                      "main_pid": "42", "main_uid": "10000", "proc_count": "6"},
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
                      "mounted_pid1_comm": "init", "mounted_pid_count": "6",
                      "own_pid1_comm": "init", "own_pid_count": "6",
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
        "image_source_commit": "527da60844d4dced37879ea50259675371abe10e",
        "run_argv": ["podman", "run", "-d", "--runtime", "/usr/local/bin/runsc",
                     "--runtime-flag", "ignore-cgroups", "--security-opt",
                     "label=disable", "--network", "none",
                     "localhost/hermes-s0-08:527da608", "sleep", "infinity"],
        "host_kernel": "6.17.11-200.fc42",
        "container_id": "0123456789ab",
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
    ("P2-UID-ROOT-ACCEPTED", "P2", "main_uid", "0",
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
     "containment: P6 mounted procfs PID 1 is systemd, not the container's own init"),
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
                               "S0_08_LIVE_PROBE_KEY": "not-a-secret"})
    live = json.loads(proc.stdout.strip())
    lines = [live if rec["canary"] == canary else rec for rec in passing_canaries()]
    bundle = write_bundle(tmp_path / "pc-runsc", canaries=lines)
    check = run_checker(bundle)

    assert check.returncode == 1, (
        f"{canary} ran uncontained on this host, so the checker must reject it: "
        f"{check.stdout}")
    assert "observation" not in check.stdout, (
        f"{canary}.sh no longer emits a field the checker reads: {check.stdout}")
    assert expected_reason_fragment in check.stdout, check.stdout


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
