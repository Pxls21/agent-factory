"""S0-08 gVisor containment checker — deterministic, LLM-free.

Reads a containment evidence bundle (canaries.jsonl + runtime-identity.json)
produced by proofs/S0-08/tools/pc/run_containment.sh and asserts properties
P1-P6 of proofs/S0-08/CONTAINMENT-SPEC.md exactly. P7 (egress posture) and P8
(resource limits) are RECORDED — required to be present, never asserted.

Exit codes: 0 PASS / 1 `failure_reason: containment: <property> <reason>` /
2 `deferred: containment evidence not captured` / 64 usage error.

DEFERRAL RULE (the S0-01 shape): exits 2 iff the evidence DIRECTORY is absent.
Once the directory exists, EVERY missing or malformed file inside it is a
Failure, never a deferral — a half-written bundle must not read as "not run".
"""
from __future__ import annotations

import json
import stat as _stat
import sys
from pathlib import Path

# --- Pinned identity -------------------------------------------------------
# The runsc release the owner installed on the PC and the runsc spike
# downloaded in the sandbox are the SAME release binary.
#   release string: PC-BRIDGE.md:128 and spikes/runsc/result.json:30
#   sha256: PC-BRIDGE.md:128 records the prefix `048b89aa…` only; the full
#   digest below was measured from the identical release binary in the
#   sandbox (`sha256sum /tmp/runsc`, 2026-09-08) and its first 8 hex chars
#   match the PC's recorded prefix.
PINNED_RUNSC_VERSION = "release-20260817.0"
PINNED_RUNSC_SHA256 = "048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c"

# gVisor's kernel identity, measured under runsc release-20260817.0
# (spikes/runsc/result.json:35; PC-BRIDGE.md:137).
GVISOR_KERNEL = "4.19.0-gvisor"
GVISOR_DMESG_MARK = "Starting gVisor"

# The image's non-root runtime user (hermes-agent Dockerfile:150,
# `useradd -u 10000 -m -d /opt/data hermes`).
HERMES_UID = "10000"

# The secret-key pattern S0-01 already pins (proofs/S0-01/pins.py:50).
# The pinned image sets NO env key matching it, so the allowlist is EMPTY.
REDACTED_ENV_KEY_RE = r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)"
SECRET_ENV_ALLOWLIST: tuple[str, ...] = ()

ASSERTED = ("P1", "P2", "P3", "P4", "P5", "P6")
RECORDED = ("P7", "P8")
ALL_CANARIES = ASSERTED + RECORDED


class Deferred(Exception):
    """The run did not happen at all."""


class Failure(Exception):
    """The run happened and a property does not hold."""


def _require_file(path: Path, name: str) -> Path:
    """Reject non-regular files (FIFOs, directories, sockets, devices) with a
    named reason BEFORE any read; existence alone is not enough. A FIFO at an
    evidence path must be a refusal, never a hang."""
    if not path.exists():
        raise Failure(f"containment: {name} absent")
    if not _stat.S_ISREG(path.lstat().st_mode):
        raise Failure(f"containment: {name} is not a regular file")
    return path


def _load_json(path: Path, name: str):
    _require_file(path, name)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise Failure(f"containment: {name} is not readable JSON: {type(exc).__name__}")


def _load_canaries(path: Path) -> dict:
    """Parse canaries.jsonl into {canary_id: observed-dict}. A duplicate or
    unknown canary id is a Failure — the checker never silently keeps the last
    line for an id."""
    _require_file(path, "canaries.jsonl")
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise Failure("containment: canaries.jsonl is empty")
    out: dict = {}
    for index, line in enumerate(lines, start=1):
        try:
            rec = json.loads(line)
        except Exception as exc:
            raise Failure(f"containment: canaries.jsonl line {index} is not JSON: {type(exc).__name__}")
        if not isinstance(rec, dict):
            raise Failure(f"containment: canaries.jsonl line {index} is not an object")
        cid = rec.get("canary")
        if cid not in ALL_CANARIES:
            raise Failure(f"containment: canaries.jsonl line {index} has unknown canary id {cid!r}")
        if cid in out:
            raise Failure(f"containment: {cid} canary line duplicated")
        for key in ("expect", "observed", "rc"):
            if key not in rec:
                raise Failure(f"containment: {cid} canary line missing {key!r}")
        observed = rec["observed"]
        if not isinstance(observed, dict):
            raise Failure(f"containment: {cid} observed is not an object")
        rc = rec["rc"]
        if not isinstance(rc, int) or isinstance(rc, bool):
            raise Failure(f"containment: {cid} rc is not an integer")
        out[cid] = {"observed": observed, "rc": rc}
    return out


def _canary(canaries: dict, cid: str) -> dict:
    """Return a canary's observations. A canary whose own rc is non-zero did
    NOT take its observation, so an empty/absent field must not read as a
    passing property — that is the vacuous green this gate exists to stop."""
    if cid not in canaries:
        raise Failure(f"containment: {cid} canary line absent")
    rec = canaries[cid]
    if cid in ASSERTED and rec["rc"] != 0:
        raise Failure(
            f"containment: {cid} canary did not complete its observation (rc {rec['rc']})"
        )
    return rec["observed"]


def _field(observed: dict, cid: str, key: str) -> str:
    if key not in observed:
        raise Failure(f"containment: {cid} observation {key!r} absent")
    return str(observed[key])


# --- Identity --------------------------------------------------------------

def check_identity(identity: dict) -> None:
    version = str(identity.get("runsc_version", ""))
    if version != PINNED_RUNSC_VERSION:
        raise Failure(
            f"containment: runtime identity runsc {version or '(absent)'}, "
            f"expected {PINNED_RUNSC_VERSION}"
        )
    digest = str(identity.get("runsc_sha256", "")).lower()
    if digest != PINNED_RUNSC_SHA256:
        raise Failure(
            f"containment: runtime identity runsc sha256 {digest or '(absent)'}, "
            f"expected {PINNED_RUNSC_SHA256}"
        )


# --- The asserted properties ----------------------------------------------

def check_p1(canaries: dict) -> None:
    obs = _canary(canaries, "P1")
    kernel = _field(obs, "P1", "uname_r")
    if kernel != GVISOR_KERNEL:
        raise Failure(f"containment: P1 host kernel {kernel}, not gVisor")
    dmesg_first = _field(obs, "P1", "dmesg_first_line")
    if GVISOR_DMESG_MARK not in dmesg_first:
        raise Failure(f"containment: P1 dmesg line 1 does not announce gVisor: {dmesg_first}")


def check_p2(canaries: dict) -> None:
    obs = _canary(canaries, "P2")
    pid1_uid = _field(obs, "P2", "pid1_uid")
    if pid1_uid != "0":
        raise Failure(f"containment: P2 pid 1 uid {pid1_uid or '(absent)'}, expected 0")
    main_uid = _field(obs, "P2", "main_uid")
    if main_uid != HERMES_UID:
        raise Failure(
            f"containment: P2 main program uid {main_uid or '(not found)'}, "
            f"expected {HERMES_UID}"
        )


def check_p3(canaries: dict) -> None:
    obs = _canary(canaries, "P3")
    for tool, rc_key, out_key in (
        ("hermes", "hermes_rc", "hermes_out"),
        ("python3 -c import hermes_cli", "python_import_rc", "python_import_out"),
        ("node", "node_rc", "node_out"),
        ("uv", "uv_rc", "uv_out"),
    ):
        rc = _field(obs, "P3", rc_key)
        if rc != "0":
            detail = _field(obs, "P3", out_key)
            raise Failure(f"containment: P3 {tool} exited {rc}: {detail}")


def check_p4(canaries: dict) -> None:
    obs = _canary(canaries, "P4")
    sock = _field(obs, "P4", "docker_sock")
    if sock != "absent":
        raise Failure(f"containment: P4 docker socket {sock}")
    keys_raw = _field(obs, "P4", "secret_env_keys")
    keys = [k for k in keys_raw.split(",") if k]
    offending = [k for k in keys if k not in SECRET_ENV_ALLOWLIST]
    if offending:
        raise Failure(
            f"containment: P4 {len(offending)} secret-bearing env key(s) in the runtime env: "
            + ",".join(sorted(offending))
        )
    # The count the canary reported must agree with the names it reported;
    # a count of 0 beside a non-empty key list is a malformed observation.
    count = _field(obs, "P4", "secret_env_count")
    if count != str(len(keys)):
        raise Failure(
            f"containment: P4 secret_env_count {count} disagrees with "
            f"{len(keys)} reported key name(s)"
        )


def check_p5(canaries: dict, identity: dict) -> None:
    obs = _canary(canaries, "P5")
    readable = _field(obs, "P5", "sentinel_readable")
    path_inside = _field(obs, "P5", "sentinel_path")
    # POSITIVE CONTROL: the runner must have proven the sentinel readable ON
    # THE HOST at the same path. Without it, "unreadable inside" proves nothing
    # (the file may never have existed).
    host = identity.get("sentinel_host_read")
    if not isinstance(host, dict):
        raise Failure("containment: P5 runtime-identity.json records no sentinel_host_read control")
    if host.get("readable") is not True:
        raise Failure("containment: P5 host-side sentinel control did not read the sentinel")
    host_path = str(host.get("path", ""))
    if not host_path or host_path != path_inside:
        raise Failure(
            f"containment: P5 sentinel path mismatch: canary read {path_inside or '(absent)'}, "
            f"host control wrote {host_path or '(absent)'}"
        )
    if readable != "no":
        raise Failure("containment: P5 host sentinel readable inside the container")


def check_p6(canaries: dict) -> None:
    obs = _canary(canaries, "P6")
    dangerous = _field(obs, "P6", "dangerous_devices")
    if dangerous:
        raise Failure(f"containment: P6 raw host devices present: {dangerous}")
    # `mount -t proc` SUCCEEDS under gVisor (measured). The containment
    # signature is WHOSE process table it reveals: the container's own.
    mount_rc = _field(obs, "P6", "mount_proc_rc")
    if mount_rc == "0":
        mounted = _field(obs, "P6", "mounted_pid1_comm")
        own = _field(obs, "P6", "own_pid1_comm")
        if not mounted or not own:
            raise Failure("containment: P6 mounted procfs did not yield a PID 1 comm")
        if mounted != own:
            raise Failure(
                f"containment: P6 mounted procfs PID 1 is {mounted}, "
                f"not the container's own {own}"
            )


def check_recorded(canaries: dict) -> None:
    """P7 and P8 are required to be PRESENT so the run records its egress and
    cgroup posture. Nothing about their content is asserted."""
    for cid in RECORDED:
        _canary(canaries, cid)


# --- Entry point -----------------------------------------------------------

def check_bundle(evidence_dir: Path) -> str:
    if not evidence_dir.is_dir():
        raise Deferred("containment evidence not captured")
    identity = _load_json(evidence_dir / "runtime-identity.json", "runtime-identity.json")
    canaries = _load_canaries(evidence_dir / "canaries.jsonl")
    check_identity(identity)
    check_p1(canaries)
    check_p2(canaries)
    check_p3(canaries)
    check_p4(canaries)
    check_p5(canaries, identity)
    check_p6(canaries)
    check_recorded(canaries)
    return (
        f"PASS: S0-08 gvisor-containment - {len(ASSERTED)} properties asserted "
        f"over {evidence_dir.name}"
    )


def main(argv) -> int:
    args = list(argv[1:])
    if len(args) != 1:
        print("usage: check_containment.py <evidence-dir>", file=sys.stderr)
        return 64
    try:
        print(check_bundle(Path(args[0])))
        return 0
    except Deferred as d:
        print(f"deferred: {d}")
        return 2
    except Failure as f:
        print(f"failure_reason: {f}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
