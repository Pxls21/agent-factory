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

# The uid every canary must be exec'd as. Observations are evidence about the
# runtime user only if they were TAKEN as that user. The image's own default is
# `USER root` (hermes-agent Dockerfile:298), so a `podman exec` without
# `--user` observes a DIFFERENT subject than the one the security profile is
# about (VERIFY-G1 F3). The runner records the uid it used; this pins it.
CANARY_EXEC_UID = "10000"

# The hermes-agent commit the image must have been built from
# (upstream.lock.yaml:10-15; run_containment.sh refuses any other checkout).
# Without this the checker accepts a bundle captured from any image at all.
PINNED_IMAGE_SOURCE_COMMIT = "527da60844d4dced37879ea50259675371abe10e"

# The `podman run` argv the evidence must have been produced by, screened as
# EXACT tokens over the recorded LIST — never as a substring over a joined
# string, because `--network host` is two tokens and a substring screen also
# matches `--network hostile`. The three required pairs are the flags
# PC-BRIDGE.md:135-148 verified plus the containment run's own `--network none`.
REQUIRED_RUN_ARGV_PAIRS = (
    ("--runtime-flag", "ignore-cgroups"),
    ("--security-opt", "label=disable"),
    ("--network", "none"),
)
BANNED_RUN_ARGV_TOKENS = (
    "--privileged", "-v", "--volume", "--mount", "--pid=host", "--cap-add",
    "--network=host", "--net=host",
)

# The container's PID 1 comm, DERIVED from the image rather than assumed:
# `docker/entrypoint-dispatch.sh:18` execs `/init`, and s6-overlay 3.2.3.0's
# own `/init` execs away in its first act (`exec s6-overlay-suexec …
# libexec/stage0`, and `stage0` execs the s6-linux-init stage 1 — read from
# the release tarball the Dockerfile pins by sha256 at `Dockerfile:109`), so
# PID 1 settles on s6-svscan. `Dockerfile:68` states exactly that: "replaces
# tini with s6-overlay's /init (PID 1 = s6-svscan)".
CONTAINER_INIT_COMM = "s6-svscan"

# Upper bound on the container's OWN process table. Derived, not typed:
# s6-svscan (1) + s6-linux-init's supervised shutdownd (2) + one s6-supervise
# per declared user service plus its child — `docker/s6-rc.d/user/contents.d/`
# declares exactly two, `main-hermes` and `dashboard` (4) + the container's
# main program (1) + the canary's own shell and its command substitutions
# (~4) = ~12 at steady state. The bound is 32, ~2.5x headroom. What it must
# exclude is a HOST process table: the sandbox host measured 115 while this
# was derived, and a real gVisor cell measured 5.
CONTAINER_MAX_PIDS = 32

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
    """Every observation the canaries emit is a JSON STRING. Coercing with
    `str()` would silently accept an int (or a list) where a string is
    expected, so the type is named rather than converted."""
    if key not in observed:
        raise Failure(f"containment: {cid} observation {key!r} absent")
    value = observed[key]
    if not isinstance(value, str):
        raise Failure(f"containment: {cid} {key} is not a string")
    return value


def _csv(observed: dict, cid: str, key: str) -> list[str]:
    """A comma-joined observation as a list, empty entries dropped."""
    return [item for item in _field(observed, cid, key).split(",") if item]


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
    # WHICH IMAGE produced this evidence. Pinning runsc alone accepts a bundle
    # captured from any image at all (VERIFY-G1 F4, bundle A7).
    commit = str(identity.get("image_source_commit", ""))
    if commit != PINNED_IMAGE_SOURCE_COMMIT:
        raise Failure(
            f"containment: image_source_commit {commit or '(absent)'}, "
            f"expected {PINNED_IMAGE_SOURCE_COMMIT}"
        )
    # WHICH ARGV produced it. P7's whole claim — the containment run must not
    # inherit the compose file's host networking — is otherwise enforced only
    # by a static test on the runner's source, never on the evidence (A8).
    argv = identity.get("run_argv")
    if not isinstance(argv, list) or not all(isinstance(a, str) for a in argv):
        raise Failure("containment: runtime-identity.json run_argv is not a list of strings")
    for flag, value in REQUIRED_RUN_ARGV_PAIRS:
        if not any(a == flag and b == value for a, b in zip(argv, argv[1:])):
            raise Failure(f"containment: run_argv is missing {flag} {value}")
    for banned in BANNED_RUN_ARGV_TOKENS:
        if banned in argv:
            raise Failure(f"containment: run_argv carries {banned}")
    for a, b in zip(argv, argv[1:]):
        if a == "--network" and b != "none":
            raise Failure(f"containment: run_argv sets --network {b}, expected none")
    # WHO the observations were taken as. See CANARY_EXEC_UID.
    exec_user = str(identity.get("canary_exec_user", ""))
    if exec_user != CANARY_EXEC_UID:
        raise Failure(
            f"containment: canaries were exec'd as uid {exec_user or '(absent)'}, "
            f"expected {CANARY_EXEC_UID}"
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
    # EVERY process carrying the pinned main cmdline, not the first one the
    # canary's /proc glob happened to reach. The image ships a root no-op
    # `exec sleep infinity` (docker/s6-rc.d/main-hermes/run:27) that is up by
    # default, so a main cmdline of `sleep infinity` had TWO holders and P2's
    # subject was decided by glob order (VERIFY-G1 F2). Ambiguity is now a
    # named refusal, never a coin flip.
    main_pids = _csv(obs, "P2", "main_pids")
    main_uids = _csv(obs, "P2", "main_uids")
    if len(main_pids) > 1:
        raise Failure(
            f"containment: P2 main program cmdline is ambiguous "
            f"({len(main_pids)} processes)"
        )
    if len(main_pids) != len(main_uids):
        raise Failure(
            f"containment: P2 main program pid/uid lists disagree "
            f"({len(main_pids)} pid(s), {len(main_uids)} uid(s))"
        )
    if not main_pids:
        raise Failure(
            f"containment: P2 main program uid (not found), expected {HERMES_UID}"
        )
    if main_uids[0] != HERMES_UID:
        raise Failure(
            f"containment: P2 main program uid {main_uids[0]}, "
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
    # --- the capability-INDEPENDENT signature, asserted either way ---------
    # `mount -t proc` needs CAP_SYS_ADMIN. The runtime user (uid 10000) has no
    # capabilities at all, so in the venue this proof actually runs in the
    # mount FAILS (measured inside real gVisor as uid 65534: rc 32,
    # "must be superuser to use mount."). The shipped checker asserted nothing
    # at all in that case and passed a bundle whose own procfs named the
    # HOST's init (VERIFY-G1 F1, bundle A5c). These three assertions need no
    # capability and fire in both branches.
    own = _field(obs, "P6", "own_pid1_comm")
    if own != CONTAINER_INIT_COMM:
        raise Failure(
            f"containment: P6 container PID 1 is {own or '(absent)'}, "
            f"not the image's own {CONTAINER_INIT_COMM}"
        )
    # A second, independently exec'd observation of the same PID 1: P2 read
    # /proc/1/comm in its own process. Forging one line is not enough.
    p2_comm = _field(_canary(canaries, "P2"), "P2", "pid1_comm")
    if p2_comm != own:
        raise Failure(
            f"containment: P6 PID 1 comm {own} disagrees with P2's "
            f"{p2_comm or '(absent)'}"
        )
    own_count = _field(obs, "P6", "own_pid_count")
    if not own_count.isdigit():
        raise Failure(
            f"containment: P6 own_pid_count {own_count or '(absent)'} is not a count"
        )
    if int(own_count) > CONTAINER_MAX_PIDS:
        raise Failure(
            f"containment: P6 own process table has {own_count} processes, "
            f"over the image's bound of {CONTAINER_MAX_PIDS}"
        )
    # --- the mount signature, when the mount could run --------------------
    # `mount -t proc` SUCCEEDS under gVisor for a caller that HAS
    # CAP_SYS_ADMIN (measured). The containment signature is then WHOSE
    # process table it reveals: the container's own.
    mount_rc = _field(obs, "P6", "mount_proc_rc")
    if mount_rc == "0":
        mounted = _field(obs, "P6", "mounted_pid1_comm")
        if not mounted:
            raise Failure("containment: P6 mounted procfs did not yield a PID 1 comm")
        if mounted != own:
            raise Failure(
                f"containment: P6 mounted procfs PID 1 is {mounted}, "
                f"not the container's own {own}"
            )
    elif not _field(obs, "P6", "mount_proc_error"):
        raise Failure(
            f"containment: P6 mount -t proc failed with rc {mount_rc} and no reason"
        )


def check_recorded(canaries: dict) -> None:
    """P7 and P8 are required to be PRESENT so the run records its egress and
    cgroup posture. Nothing about their content is asserted — but a canary
    that never took its observation records nothing, so "recorded" would be
    satisfied by an empty record (VERIFY-G1 F15, bundle A12)."""
    for cid in RECORDED:
        _canary(canaries, cid)
        if canaries[cid]["rc"] != 0:
            raise Failure(
                f"containment: {cid} recorded canary did not observe "
                f"(rc {canaries[cid]['rc']})"
            )


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
