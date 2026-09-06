"""S0-01 ACP conformance checker v2.2 — derives EVERYTHING from raw files, exact values.

Exit codes: 0 PASS / 1 `failure_reason: <leg>: <reason>` / 2 `deferred: <reason>` / 64 usage error.
DEFERRAL RULE: exits 2 iff golden/ is absent or NO leg directory contains timeline.jsonl.
Once ANY leg carries a timeline, EVERY absence of a required file is a Failure, never a deferral.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

# A15: optional fixtures-dir override (default: HERE / "fixtures").
# Set via --fixtures-dir on the CLI; tests use monkeypatch on this module attribute.
_FIXTURES_DIR = None


def _fixtures() -> Path:
    return Path(_FIXTURES_DIR) if _FIXTURES_DIR is not None else HERE / "fixtures"
sys.path.insert(0, str(HERE))
from pins import (  # noqa: E402
    ALLOWED_UPSTREAM_GET,
    ENV_ALLOWLIST_KEY,
    EXPECTED_MENTIONS,
    EXPECTED_MODEL,
    LEGS,
    MANIFEST_LINE_RE,
    MANIFEST_TREES,
    MENTION_TEXT,
    MENTION_WINDOW_SLACK_S,
    NEGATIVE_REQUIRED_FILES,
    PINNED_AGENT_CAPABILITIES,
    PINNED_AGENT_ENTRYPOINT_SHA256,
    PINNED_AGENT_INTERPRETER_REALPATH,
    PINNED_AGENT_INTERPRETER_SHA256,
    PINNED_AGENT_PROTOCOL_VERSION,
    PINNED_AGENT_REALPATH,
    PINNED_BASELINE_DIGESTS,
    PINNED_BASELINE_FILE_COUNTS,
    PINNED_BASELINE_GZ_SHA256,
    PINNED_BUZZ_ACP_EXE_REALPATH,
    PINNED_BUZZ_ACP_SHA256,
    PINNED_CLIENT_PROTOCOL_VERSION,
    PINNED_ENV_KEYS,
    PINNED_GOLDEN_SHA256,
    PINNED_HERMES_HOME,
    PINNED_HOME,
    PINNED_IDLE_TIMEOUT,
    PINNED_IDLE_TIMEOUT_ARG,
    PINNED_LAUNCH_ARGV,
    PINNED_LOG_LINES_TWO_USERS,
    PINNED_MAX_TURN,
    PINNED_MAX_TURN_DURATION_ARG,
    PINNED_PATH,
    PINNED_RELAY_URL,
    PINNED_ROUTE_PREFIX,
    PINNED_SESSION_POLICY,
    PINNED_STARTUP_AGENTS,
    PINNED_STARTUP_DEDUP,
    PINNED_STARTUP_IGNORE_SELF,
    PINNED_TEE_PATH,
    PINNED_UPSTREAM_HOST,
    REDACTED_ENV_KEY_RE,
    UPSTREAM_POST_PATH,
    UPSTREAM_WINDOW_SLACK_S,
)
import check_initialize as ci  # noqa: E402
import negative_contract as nc  # noqa: E402
sys.path.insert(0, str(HERE / "tools"))
import nostr_verify  # noqa: E402

VOLATILE_UPDATE_FIELDS = {"content", "text", "title", "rawInput", "rawOutput",
                          "locations", "_meta", "usage"}

# The expected key set for runtime-identity.json (§3 / A5).
EXPECTED_RID_KEYS = frozenset({
    "tee_path", "tee_sha256", "tee_pid", "agent_argv", "agent_realpath",
    "agent_entrypoint_sha256", "agent_child_pid", "agent_interpreter_realpath",
    "agent_interpreter_sha256", "python_dont_write_bytecode", "spawned_at_utc",
    "buzz_acp_pid", "buzz_acp_exe_realpath", "buzz_acp_exe_sha256",
    "buzz_acp_version", "launch_argv",
})

# The expected key set for upstream records (§6 / A3).
EXPECTED_RECORD_KEYS = frozenset({
    "seq", "received_at", "t_mono_ns", "remote_addr", "method", "path",
    "headers", "body", "authorization_fingerprint",
})

# The expected key set for mention receipts (§5 / A4).
EXPECTED_RECEIPT_KEYS = frozenset({"accepted", "event_id", "mention_pubkeys", "message"})

# The expected key set for redacted-dict values (5-F07: exactly {redacted, len, sha256_12}).
_REDACTED_DICT_KEYS = frozenset({"redacted", "len", "sha256_12"})

# A21d: expected key set for tee-status.json (running status, twelve keys).
_TEE_STATUS_KEYS = frozenset({
    "final", "agent_returncode", "drained", "stdin_reader_done",
    "recorded_c2a", "recorded_a2c", "forwarded_c2a", "forwarded_a2c",
    "write_errors", "exit_code", "updated_seq", "updated_utc",
})

# The filename pattern for upstream records (A3).
_RECORD_FILENAME_RE = re.compile(r"^\d{6}\.json$")

# The line format for manifest body lines (A13).
_MANIFEST_LINE_RE = re.compile(MANIFEST_LINE_RE)  # manifest v2.2 line shape, from pins

# The hex-leak guard pattern (A9/5-F14: case-insensitive 64-hex anywhere in the value).
_HEX64_ANYWHERE_RE = re.compile(r"[0-9a-fA-F]{64}")

# 5-F15: upstream record header screening patterns.
_SENSITIVE_HEADER_NAME_RE = re.compile(r"(?i)authorization|x-api-key|api-key|cookie|token")
_SENSITIVE_HEADER_VALUE_RE = re.compile(r"(?i)bearer\s|sk-|[0-9a-fA-F]{64}")

# 5-F19: agent-stderr screening patterns.
_STDERR_LEAK_RE = re.compile(r"(?i)[0-9a-fA-F]{64}|bearer\s|token[=:]\S")

# A20 v2.3: scan file enumeration header shape.
_SCAN_HEADER_RE = re.compile(
    r"^# process-scan v2\.3 mode=(after|teardown) rows=(\d+) buzz_acp_pid=(\d+|none) buzz_present=([01]) "
    r"owned=(\d+) owned_present=(\d+) pinned_present=(\d+) owned_zombies=(\d+) utc=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$")


class Deferred(Exception):
    pass


class Failure(Exception):
    pass


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_utc(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def _parse_utc_summary(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _reject_nan(line: str, leg: str, seq_hint: int):
    def _raise(c):
        raise Failure(f"{leg}: NaN or Infinity in timeline at seq {seq_hint}")
    return json.loads(line, parse_constant=_raise)


def _require_file(path: Path, leg: str, name: str):
    if not path.exists():
        raise Failure(f"{leg}: {name} absent")
    return path


def _require_dir(path: Path, leg: str, name: str):
    if not path.is_dir():
        raise Failure(f"{leg}: {name} absent")
    return path


def _is_strict_int(v):
    """True iff v is an int and NOT a bool."""
    return isinstance(v, int) and not isinstance(v, bool)


# --- dispatcher for the executed-check-sequence guard (A25/A12) ---
# Each check function is registered here and called through _run_check.
# The dispatcher appends (fn.__name__, leg) AFTER the function returns.
# A25: the FULL ordered (check, leg) sequence is compared, no dedup.
_executed = []

_CHECK_NAMES = [
    "check_timeline", "check_initialize_frames", "check_runtime_identity",
    "check_env", "check_mentions", "check_route",
    "check_prompt_turn", "check_config_echo", "check_manifests",
    "check_process_evidence", "check_buzzacp_log", "check_tee_status",
    "check_cancel", "check_shutdown", "check_two_users",
    "check_golden", "check_negative",
]

# A25: the complete ordered (check, leg) sequence — matches the actual dispatch order.
EXPECTED_CHECK_SEQUENCE = []
# First big loop: for leg in LEGS: timeline, init_frames, rid, env, mentions, route
for _lg in LEGS:
    for _cn in ("check_timeline", "check_initialize_frames", "check_runtime_identity",
                "check_env", "check_mentions", "check_route"):
        EXPECTED_CHECK_SEQUENCE.append((_cn, _lg))
# prompt_turn for run-1, run-2, shutdown
for _lg in ("run-1", "run-2", "shutdown"):
    EXPECTED_CHECK_SEQUENCE.append(("check_prompt_turn", _lg))
# config_echo, manifests, process_evidence, buzzacp_log, tee_status each for all LEGS
for _cn in ("check_config_echo", "check_manifests", "check_process_evidence", "check_buzzacp_log", "check_tee_status"):
    for _lg in LEGS:
        EXPECTED_CHECK_SEQUENCE.append((_cn, _lg))
EXPECTED_CHECK_SEQUENCE.append(("check_cancel", "cancel"))
EXPECTED_CHECK_SEQUENCE.append(("check_shutdown", "shutdown"))
EXPECTED_CHECK_SEQUENCE.append(("check_two_users", "two-users"))
EXPECTED_CHECK_SEQUENCE.append(("check_golden", "golden"))
EXPECTED_CHECK_SEQUENCE.append(("check_negative", "negative"))


def _run_check(fn, leg, *args, **kwargs):
    """Call fn and record (name, leg) in the executed list AFTER successful return."""
    result = fn(*args, **kwargs)
    _executed.append((fn.__name__, leg))
    return result


def check_timeline(entries, leg, leg_dir):
    if not entries:
        raise Failure(f"{leg}: timeline.jsonl is empty")
    valid_keys = {"seq", "dir", "t_utc", "t_mono_ns", "frame"}
    utc_re = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
    for i, e in enumerate(entries):
        ks = set(e.keys())
        if e.get("frame") is None:
            raise Failure(f"{leg}: non-JSON frame at seq {i + 1}")
        if ks != valid_keys:
            raise Failure(f"{leg}: timeline entry at seq {i + 1} has unexpected keys {sorted(ks)}")
        seq_val = e["seq"]
        if not _is_strict_int(seq_val):
            raise Failure(f"{leg}: timeline seq at index {i} is not int")
        if seq_val != i + 1:
            raise Failure(f"{leg}: timeline seq not strictly 1..N at index {i}")
        mono = e["t_mono_ns"]
        if not _is_strict_int(mono):
            raise Failure(f"{leg}: timeline t_mono_ns at seq {seq_val} is not int")
        t_utc = e["t_utc"]
        if not isinstance(t_utc, str) or not utc_re.match(t_utc):
            raise Failure(f"{leg}: timeline t_utc at seq {seq_val} does not match format")
        _parse_utc(t_utc)
        d = e["dir"]
        if d not in ("c2a", "a2c"):
            raise Failure(f"{leg}: timeline dir at seq {seq_val} is {d!r}, expected 'c2a' or 'a2c'")
    for i in range(1, len(entries)):
        if entries[i]["t_mono_ns"] < entries[i - 1]["t_mono_ns"]:
            raise Failure(f"{leg}: t_mono_ns not non-decreasing at seq {entries[i]['seq']}")
    for i in range(1, len(entries)):
        if _parse_utc(entries[i]["t_utc"]) < _parse_utc(entries[i - 1]["t_utc"]):
            raise Failure(f"{leg}: t_utc not non-decreasing at seq {entries[i]['seq']}")
    c2a_split = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c_split = [e["frame"] for e in entries if e["dir"] == "a2c"]
    c2a_path = _require_file(leg_dir / "frames-client-to-agent.jsonl", leg, "frames-client-to-agent.jsonl")
    a2c_path = _require_file(leg_dir / "frames-agent-to-client.jsonl", leg, "frames-agent-to-client.jsonl")

    def _load_dir(fpath, name, expected_split):
        raw = fpath.read_bytes()
        lines_raw = raw.split(b"\n")
        frames = []
        empty_count = 0
        for lineno, lb in enumerate(lines_raw, 1):
            if not lb and lineno == len(lines_raw):
                # trailing empty after final newline is ok
                continue
            if not lb or not lb.strip():
                # 5-F08/6-F9: empty/blank lines are Failures and count toward parity
                empty_count += 1
                if empty_count == 1:
                    raise Failure(f"{leg}: {name} blank line at line {lineno}")
                continue
            if lb.endswith(b"\r"):
                lb = lb[:-1]
            try:
                text = lb.decode("utf-8")
            except UnicodeDecodeError:
                raise Failure(f"{leg}: {name} line {lineno} not valid UTF-8")
            try:
                frames.append(json.loads(text))
            except json.JSONDecodeError:
                raise Failure(f"{leg}: {name} line {lineno} not valid JSON")
        if len(frames) != len(expected_split):
            raise Failure(f"{leg}: {name} line count {len(frames)} != timeline split count {len(expected_split)}")
        return frames

    c2a_file = _load_dir(c2a_path, "frames-client-to-agent.jsonl", c2a_split)
    a2c_file = _load_dir(a2c_path, "frames-agent-to-client.jsonl", a2c_split)
    if c2a_file != c2a_split:
        raise Failure(f"{leg}: frames-client-to-agent.jsonl does not match timeline c2a split")
    if a2c_file != a2c_split:
        raise Failure(f"{leg}: frames-agent-to-client.jsonl does not match timeline a2c split")
    # A23: frame class checks — a2c with method+id are agent REQUESTS (Failure);
    # c2a with id and no method are client RESPONSES (Failure).
    for e in entries:
        f = e["frame"]
        if e["dir"] == "a2c" and "method" in f and "id" in f:
            raise Failure(f"{leg}: a2c frame at seq {e['seq']} is an agent request (method={f['method']!r})")
        if e["dir"] == "c2a" and "id" in f and "method" not in f:
            raise Failure(f"{leg}: c2a frame at seq {e['seq']} is a client response (id={f['id']!r})")
    # A23: response cardinality — each request id has exactly one response
    req_ids = {}
    for e in entries:
        f = e["frame"]
        if "id" in f and "method" in f:
            k = json.dumps(f["id"], sort_keys=True)
            req_ids.setdefault(k, []).append(e["seq"])
    resp_ids = {}
    for e in entries:
        f = e["frame"]
        if "id" in f and "method" not in f:
            k = json.dumps(f["id"], sort_keys=True)
            resp_ids.setdefault(k, []).append(e["seq"])
    for k, seqs in resp_ids.items():
        if len(seqs) > 1:
            raise Failure(f"{leg}: duplicate response for id {k} at seqs {seqs}")
    # A23: response envelope must have jsonrpc "2.0" and exactly one of result/error
    for e in entries:
        f = e["frame"]
        if "id" in f and "method" not in f:
            if f.get("jsonrpc") != "2.0" or ("result" in f) == ("error" in f):
                raise Failure(f"{leg}: response at seq {e['seq']} is not a valid JSON-RPC envelope")
    return c2a_split, a2c_split


def check_initialize_frames(c2a, a2c, leg, schema=None):
    """A6/6-F19: schema loaded from --fixtures-dir by check_bundle and passed in."""
    init_reqs = [o for o in c2a if o.get("method") == "initialize"]
    if len(init_reqs) != 1:
        raise Failure(f"{leg}: expected one initialize request, got {len(init_reqs)}")
    req = init_reqs[0]
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
    resp = resps.get(json.dumps(req["id"], sort_keys=True))
    if resp is None or "error" in resp:
        raise Failure(f"{leg}: initialize has no successful response")
    v = ci.classify_request(req["params"], schema=schema)
    if v != "ok":
        raise Failure(f"{leg}: initialize request {v}")
    v = ci.classify_response(resp["result"], schema=schema)
    if v != "ok":
        raise Failure(f"{leg}: initialize response {v}")
    if req["params"].get("protocolVersion") != PINNED_CLIENT_PROTOCOL_VERSION:
        raise Failure(f"{leg}: client protocolVersion is not {PINNED_CLIENT_PROTOCOL_VERSION}")
    if resp["result"].get("protocolVersion") != PINNED_AGENT_PROTOCOL_VERSION:
        raise Failure(f"{leg}: agent protocolVersion is not {PINNED_AGENT_PROTOCOL_VERSION}")
    if resp["result"].get("agentCapabilities") != PINNED_AGENT_CAPABILITIES:
        raise Failure(f"{leg}: agentCapabilities differ from pinned")


def check_runtime_identity(leg_dir, leg):
    rid = json.loads(_require_file(leg_dir / "runtime-identity.json", leg, "runtime-identity.json").read_text())
    # A5: exact key set
    if set(rid.keys()) != EXPECTED_RID_KEYS:
        extra = sorted(set(rid.keys()) - EXPECTED_RID_KEYS)
        missing = sorted(EXPECTED_RID_KEYS - set(rid.keys()))
        raise Failure(f"{leg}: runtime-identity.json key set mismatch (extra={extra}, missing={missing})")
    # Type checks for tee_pid and agent_child_pid
    if not _is_strict_int(rid["tee_pid"]):
        raise Failure(f"{leg}: tee_pid is not int")
    if not _is_strict_int(rid["agent_child_pid"]):
        raise Failure(f"{leg}: agent_child_pid is not int")

    def _chk(field, expected, desc=None):
        if rid.get(field) != expected:
            raise Failure(f"{leg}: {desc or field} mismatch")

    _chk("buzz_acp_exe_sha256", PINNED_BUZZ_ACP_SHA256)
    _chk("buzz_acp_exe_realpath", PINNED_BUZZ_ACP_EXE_REALPATH)
    _chk("agent_entrypoint_sha256", PINNED_AGENT_ENTRYPOINT_SHA256)
    _chk("agent_realpath", PINNED_AGENT_REALPATH)
    _chk("agent_argv", [PINNED_AGENT_REALPATH])
    _chk("agent_interpreter_realpath", PINNED_AGENT_INTERPRETER_REALPATH)
    _chk("agent_interpreter_sha256", PINNED_AGENT_INTERPRETER_SHA256)
    _chk("tee_path", PINNED_TEE_PATH)
    tee_file = HERE / "tools" / "frame_tee.py"
    if not tee_file.exists():
        raise Failure(f"{leg}: tools/frame_tee.py absent (needed for tee_sha256)")
    _chk("tee_sha256", _sha256_file(tee_file))
    if rid.get("python_dont_write_bytecode") is not True:
        raise Failure(f"{leg}: python_dont_write_bytecode is not true")
    pid_path = _require_file(leg_dir / "buzz-acp.pid", leg, "buzz-acp.pid")
    try:
        expected_pid = int(pid_path.read_text().strip())
    except ValueError:
        raise Failure(f"{leg}: buzz-acp.pid is not a valid integer")
    pid_val = rid.get("buzz_acp_pid")
    if not _is_strict_int(pid_val) or pid_val != expected_pid:
        raise Failure(f"{leg}: buzz_acp_pid mismatch")
    argv_path = _require_file(leg_dir / "argv.txt", leg, "argv.txt")
    argv_lines = argv_path.read_text().splitlines()
    if argv_lines != PINNED_LAUNCH_ARGV:
        raise Failure(f"{leg}: argv.txt lines != PINNED_LAUNCH_ARGV")
    if rid.get("launch_argv") != PINNED_LAUNCH_ARGV:
        raise Failure(f"{leg}: launch_argv mismatch")


def check_env(leg_dir, leg, identities):
    env = json.loads(_require_file(leg_dir / "env.json", leg, "env.json").read_text())
    expected_keys = set(PINNED_ENV_KEYS)
    if leg == "two-users":
        expected_keys.add(ENV_ALLOWLIST_KEY)
    if set(env.keys()) != expected_keys:
        raise Failure(f"{leg}: env.json key set mismatch (extra={sorted(set(env.keys()) - expected_keys)}, missing={sorted(expected_keys - set(env.keys()))})")
    if leg != "two-users" and ENV_ALLOWLIST_KEY in env:
        raise Failure(f"{leg}: {ENV_ALLOWLIST_KEY} present in non-two-users leg")
    redact_re = re.compile(REDACTED_ENV_KEY_RE)
    for key, val in env.items():
        if redact_re.search(key):
            if not isinstance(val, dict):
                raise Failure(f"{leg}: env {key} should be redacted but is not a dict")
            # 5-F07: redacted-dict shape pinned to exactly {redacted, len, sha256_12}
            if set(val.keys()) != _REDACTED_DICT_KEYS:
                raise Failure(f"{leg}: env {key} redacted dict has unexpected keys {sorted(set(val.keys()) ^ _REDACTED_DICT_KEYS)}")
            if val.get("redacted") is not True:
                raise Failure(f"{leg}: env {key} redacted is not true")
            length = val.get("len")
            if not _is_strict_int(length) or length <= 0:
                raise Failure(f"{leg}: env {key} redacted len is not a positive int")
            sha12 = val.get("sha256_12")
            if not isinstance(sha12, str) or not re.fullmatch(r"[0-9a-f]{12}", sha12):
                raise Failure(f"{leg}: env {key} sha256_12 is not 12 hex chars")
        else:
            if isinstance(val, dict):
                raise Failure(f"{leg}: env {key} is a dict but does not match redaction regex")
    if env.get("BUZZ_ACP_AGENT_OWNER") != identities["owner"]:
        raise Failure(f"{leg}: env BUZZ_ACP_AGENT_OWNER mismatch")
    if env.get("BUZZ_ACP_SESSION_POLICY") != PINNED_SESSION_POLICY:
        raise Failure(f"{leg}: env BUZZ_ACP_SESSION_POLICY mismatch")
    if env.get("HERMES_HOME") != PINNED_HERMES_HOME:
        raise Failure(f"{leg}: env HERMES_HOME mismatch")
    if env.get("BUZZ_RELAY_URL") != PINNED_RELAY_URL:
        raise Failure(f"{leg}: env BUZZ_RELAY_URL mismatch")
    if env.get("S0_01_AGENT") != PINNED_AGENT_REALPATH:
        raise Failure(f"{leg}: env S0_01_AGENT mismatch")
    if env.get("PATH") != PINNED_PATH:
        raise Failure(f"{leg}: env PATH mismatch")
    if env.get("HOME") != PINNED_HOME:
        raise Failure(f"{leg}: env HOME mismatch")
    if env.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise Failure(f"{leg}: env PYTHONDONTWRITEBYTECODE is not '1'")
    framedir = env.get("S0_01_FRAMEDIR")
    if not isinstance(framedir, str) or not framedir:
        raise Failure(f"{leg}: env S0_01_FRAMEDIR empty or missing")
    rt = env.get("BUZZ_ACP_RESPOND_TO")
    if leg == "two-users":
        if rt != "allowlist":
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be 'allowlist' for two-users")
        if env.get(ENV_ALLOWLIST_KEY) != identities["user2"]:
            raise Failure(f"{leg}: env {ENV_ALLOWLIST_KEY} != identities.user2")
    else:
        if rt != "owner-only":
            raise Failure(f"{leg}: env BUZZ_ACP_RESPOND_TO should be owner-only")
    # A9/5-F07: hex-leak guard — case-insensitive 64-hex; descends into dicts
    exempt_keys = {"BUZZ_ACP_AGENT_OWNER", ENV_ALLOWLIST_KEY}
    for key, val in env.items():
        if key in exempt_keys:
            continue
        if isinstance(val, str) and _HEX64_ANYWHERE_RE.search(val):
            raise Failure(f"{leg}: env {key} contains a 64-hex string (possible secret leak)")
        if isinstance(val, dict):
            for vk, vv in val.items():
                if isinstance(vv, str) and _HEX64_ANYWHERE_RE.search(vv):
                    raise Failure(f"{leg}: env {key}.{vk} contains a 64-hex string (possible secret leak)")


def check_mentions(leg_dir, leg, identities, entries, post_summary_ts=None):
    expected = EXPECTED_MENTIONS.get(leg, [])
    mentions_dir = _require_dir(leg_dir / "mentions", leg, "mentions/")
    expected_files = set()
    for tag, _, _, _ in expected:
        expected_files.update({f"{tag}.receipt.json", f"{tag}.event.json", f"{tag}.receipt.err"})
    # 5-F09/6-F15: extra entries including dirs
    actual_entries = {f.name for f in mentions_dir.iterdir()}
    extra = actual_entries - expected_files
    if extra:
        raise Failure(f"{leg}: mentions/ has unexpected entries: {sorted(extra)}")
    # A1: window lower = floor(first timeline t_utc) - 5, upper = post summary ts + 5
    first_utc = _parse_utc(entries[0]["t_utc"])
    floor_first = int(first_utc.timestamp()) - MENTION_WINDOW_SLACK_S
    if post_summary_ts is not None:
        ceil_post = int(post_summary_ts.timestamp()) + 1 + MENTION_WINDOW_SLACK_S
    else:
        # Fallback: last timeline entry + 5
        last_utc = _parse_utc(entries[-1]["t_utc"])
        ceil_post = int(last_utc.timestamp()) + 1 + MENTION_WINDOW_SLACK_S
    event_ids = []
    for tag, id_key, content, replies_to in expected:
        event_path = _require_file(mentions_dir / f"{tag}.event.json", leg, f"mentions/{tag}.event.json")
        receipt_path = _require_file(mentions_dir / f"{tag}.receipt.json", leg, f"mentions/{tag}.receipt.json")
        err_path = _require_file(mentions_dir / f"{tag}.receipt.err", leg, f"mentions/{tag}.receipt.err")
        if err_path.read_text() != "":
            raise Failure(f"{leg}: mentions/{tag}.receipt.err is not empty")
        event = json.loads(event_path.read_text())
        receipt = json.loads(receipt_path.read_text())
        # A4: receipt exact key set
        if set(receipt.keys()) != EXPECTED_RECEIPT_KEYS:
            raise Failure(f"{leg}: mention {tag} receipt key set mismatch")
        if receipt.get("accepted") is not True:
            raise Failure(f"{leg}: mention {tag} receipt not accepted")
        # A4: event_id must be 64 lowercase hex
        eid = receipt.get("event_id")
        if not isinstance(eid, str) or not re.fullmatch(r"[0-9a-f]{64}", eid):
            raise Failure(f"{leg}: mention {tag} receipt event_id is not 64 lowercase hex")
        if eid != event.get("id"):
            raise Failure(f"{leg}: mention {tag} receipt event_id != event.id")
        # A4: mention_pubkeys is a list of 64-hex strings
        mpk = receipt.get("mention_pubkeys")
        if not isinstance(mpk, list):
            raise Failure(f"{leg}: mention {tag} receipt mention_pubkeys is not a list")
        for pk in mpk:
            if not isinstance(pk, str) or not re.fullmatch(r"[0-9a-f]{64}", pk):
                raise Failure(f"{leg}: mention {tag} receipt mention_pubkeys contains non-64-hex")
        # A4: message must be ""
        if receipt.get("message") != "":
            raise Failure(f"{leg}: mention {tag} receipt message is not empty string")
        # A4: kind must be int (not bool/float)
        kind_val = event.get("kind")
        if not _is_strict_int(kind_val) or kind_val != 9:
            raise Failure(f"{leg}: mention {tag} event kind is not 9")
        computed_id = nostr_verify.event_id(event)
        if computed_id != event["id"]:
            raise Failure(f"{leg}: mention {tag} NIP-01 id mismatch")
        ok, reason = nostr_verify.verify_event(event)
        if not ok:
            raise Failure(f"{leg}: mention {tag} BIP-340 signature invalid: {reason}")
        if event["pubkey"] != identities.get(id_key):
            raise Failure(f"{leg}: mention {tag} pubkey != identities[{id_key}]")
        tags = event.get("tags", [])
        if ["h", identities["channel"]] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['h', channel] tag")
        if ["p", identities["agent"]] not in tags:
            raise Failure(f"{leg}: mention {tag} missing ['p', agent] tag")
        if event.get("content") != content:
            raise Failure(f"{leg}: mention {tag} content mismatch")
        if replies_to is not None:
            ref_event = json.loads((mentions_dir / f"{replies_to}.event.json").read_text())
            e_tags = [t for t in tags if len(t) >= 2 and t[0] == "e"]
            if not any(t[1] == ref_event["id"] for t in e_tags):
                raise Failure(f"{leg}: mention {tag} e-tag does not reference {replies_to}")
        created_at = event.get("created_at")
        if not _is_strict_int(created_at):
            raise Failure(f"{leg}: mention {tag} created_at is not int")
        if not (floor_first <= created_at <= ceil_post):
            raise Failure(f"{leg}: mention {tag} created_at {created_at} outside window [{floor_first}, {ceil_post}]")
        event_ids.append(event["id"])
    return event_ids


def check_route(leg_dir, leg, entries):
    model_path = _require_file(leg_dir / "hermes-model.txt", leg, "hermes-model.txt")
    model_text = model_path.read_text().strip()
    expected_model = EXPECTED_MODEL[leg]
    expected_model_text = f"default: {PINNED_ROUTE_PREFIX}/{expected_model}"
    if model_text != expected_model_text:
        raise Failure(f"{leg}: hermes-model.txt is {model_text!r}, expected {expected_model_text!r}")
    rec_dir = leg_dir / "upstream-records"
    if not rec_dir.is_dir():
        raise Failure(f"{leg}: zero upstream records / upstream-records/ absent")
    # A3: only files matching ^\d{6}\.json$
    for item in rec_dir.iterdir():
        if not _RECORD_FILENAME_RE.match(item.name):
            raise Failure(f"{leg}: upstream-records/ contains invalid filename {item.name!r}")
    records = [json.loads(rp.read_text()) for rp in sorted(rec_dir.glob("*.json"))]
    if not records:
        raise Failure(f"{leg}: zero upstream records / upstream-records/ absent")
    # A3: validate upstream-token.fingerprint is exactly 64 lowercase hex
    fp_path = _require_file(_fixtures() / "upstream-token.fingerprint", leg, "fixtures/upstream-token.fingerprint")
    expected_fp = fp_path.read_text().strip()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_fp):
        raise Failure("golden: upstream-token.fingerprint is not a 64-hex digest")
    allowed_pairs = ALLOWED_UPSTREAM_GET | {("POST", UPSTREAM_POST_PATH)}
    for rec in records:
        # A3: validate record key set
        if set(rec.keys()) != EXPECTED_RECORD_KEYS:
            raise Failure(f"{leg}: upstream record key set mismatch: {sorted(set(rec.keys()) ^ EXPECTED_RECORD_KEYS)}")
        mp = (rec.get("method"), rec.get("path"))
        if mp not in allowed_pairs:
            raise Failure(f"{leg}: upstream record ({mp[0]}, {mp[1]}) not in allowed set")
        host = (rec.get("headers") or {}).get("host", "")
        if host != PINNED_UPSTREAM_HOST:
            raise Failure(f"{leg}: upstream record host is {host!r}, expected {PINNED_UPSTREAM_HOST!r}")
        # 5-F15: screen headers for sensitive names/values
        for hname, hval in (rec.get("headers") or {}).items():
            if _SENSITIVE_HEADER_NAME_RE.search(hname):
                raise Failure(f"{leg}: upstream record has sensitive header {hname!r}")
            if isinstance(hval, str) and _SENSITIVE_HEADER_VALUE_RE.search(hval):
                raise Failure(f"{leg}: upstream record header {hname!r} has sensitive value")
    post_records = [r for r in records if r.get("method") == "POST"]
    for rec in post_records:
        if rec.get("authorization_fingerprint") != expected_fp:
            raise Failure(f"{leg}: upstream record authorization_fingerprint mismatch")
        body = rec.get("body") or {}
        if body.get("model") != expected_model:
            raise Failure(f"{leg}: upstream record body.model is {body.get('model')!r}, expected {expected_model!r}")
    prompt_windows = _prompt_windows(entries, leg)
    slack = timedelta(seconds=UPSTREAM_WINDOW_SLACK_S)
    for rec in post_records:
        ra_str = rec.get("received_at", "")
        if not ra_str:
            raise Failure(f"{leg}: upstream POST record missing received_at")
        ra = _parse_utc(ra_str)
        if not any(s - slack <= ra <= e + slack for s, e in prompt_windows):
            raise Failure(f"{leg}: upstream POST record received_at {ra_str} outside all prompt windows")
    # A3: windows consume records one-to-one
    used = [False] * len(post_records)
    for pw_start, pw_end in prompt_windows:
        found = False
        for ri, rec in enumerate(post_records):
            if used[ri]:
                continue
            ra = _parse_utc(rec.get("received_at", "2000-01-01T00:00:00.000000Z"))
            if pw_start - slack <= ra <= pw_end + slack:
                body = rec.get("body") or {}
                if body.get("stream") is True:
                    for msg in body.get("messages", []):
                        if msg.get("role") == "user":
                            c = msg.get("content")
                            if isinstance(c, str) and MENTION_TEXT in c:
                                found = True
                            elif isinstance(c, list):
                                for part in c:
                                    if isinstance(part, dict) and MENTION_TEXT in str(part.get("text", "")):
                                        found = True
                        if found:
                            break
                if found:
                    used[ri] = True
                    break
        if not found:
            raise Failure(f"{leg}: no upstream POST with stream=true and mention text for a prompt window")


def _prompt_windows(entries, leg):
    resps = {}
    for e in entries:
        if e["dir"] == "a2c":
            f = e["frame"]
            if "id" in f and "method" not in f:
                resps[json.dumps(f["id"], sort_keys=True)] = _parse_utc(e["t_utc"])
    windows = []
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt":
            t_start = _parse_utc(e["t_utc"])
            t_end = resps.get(json.dumps(e["frame"].get("id"), sort_keys=True), t_start)
            windows.append((t_start, t_end))
    return windows


def check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn"):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    # A6: request discipline — the c2a request multiset must be exactly {initialize x1, session/new x1, session/prompt x1}
    c2a_requests = [o for o in c2a if "method" in o and "id" in o]
    c2a_methods = [o["method"] for o in c2a_requests]
    expected_methods = sorted(["initialize", "session/new", "session/prompt"])
    if sorted(c2a_methods) != expected_methods:
        raise Failure(f"{leg}: c2a request methods {sorted(c2a_methods)} != expected {expected_methods}")
    # A6: every a2c response id maps to one of those requests
    c2a_ids = {json.dumps(o["id"], sort_keys=True) for o in c2a_requests}
    a2c_resps = [o for o in a2c if "id" in o and "method" not in o]
    for r in a2c_resps:
        if json.dumps(r["id"], sort_keys=True) not in c2a_ids:
            raise Failure(f"{leg}: a2c response id {r['id']} does not map to any c2a request")
    # A6: c2a notifications allowed: session/cancel (cancel leg only, exactly once)
    c2a_notifs = [o for o in c2a if "method" in o and "id" not in o]
    if leg == "cancel":
        cancel_notifs = [o for o in c2a_notifs if o.get("method") == "session/cancel"]
        non_cancel = [o for o in c2a_notifs if o.get("method") != "session/cancel"]
        if len(cancel_notifs) != 1:
            raise Failure(f"{leg}: expected exactly 1 session/cancel notification, got {len(cancel_notifs)}")
        if non_cancel:
            raise Failure(f"{leg}: unexpected c2a notification method {non_cancel[0].get('method')!r}")
    else:
        if c2a_notifs:
            raise Failure(f"{leg}: unexpected c2a notification {c2a_notifs[0].get('method')!r}")
    if len(news) != 1 or len(prompts) != 1:
        raise Failure(f"{leg}: expected 1 session/new + 1 session/prompt, saw {len(news)}/{len(prompts)}")
    new_resp = resps.get(json.dumps(news[0]["id"], sort_keys=True))
    if not new_resp or "error" in new_resp or not (new_resp.get("result") or {}).get("sessionId"):
        raise Failure(f"{leg}: session/new has no sessionId response")
    sid = new_resp["result"]["sessionId"]
    if (prompts[0].get("params") or {}).get("sessionId") != sid:
        raise Failure(f"{leg}: session/prompt targets a different session")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    prompt_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    term_entries = [e for e in entries if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
                    and json.dumps(e["frame"]["id"], sort_keys=True) == json.dumps(prompts[0]["id"], sort_keys=True)]
    if not term_entries:
        raise Failure(f"{leg}: session/prompt has no terminal response")
    term_seq = term_entries[0]["seq"]
    chunk_between = [e for e in entries if e["dir"] == "a2c" and prompt_seq < e["seq"] < term_seq
                     and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"]
    if not chunk_between:
        raise Failure(f"{leg}: no agent_message_chunk between prompt and terminal")
    bad_sid = {(o.get("params") or {}).get("sessionId") for o in notifs} - {sid}
    if bad_sid:
        raise Failure(f"{leg}: notifications carry a foreign session id")
    term = resps.get(json.dumps(prompts[0]["id"], sort_keys=True))
    if not term or "error" in term:
        raise Failure(f"{leg}: session/prompt has no successful terminal response")
    stop = (term.get("result") or {}).get("stopReason")
    if stop != expect_stop:
        raise Failure(f"{leg}: terminal stopReason is {stop!r}, expected {expect_stop!r}")
    return sid


def _shape(value):
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in sorted(value.items()) if k not in VOLATILE_UPDATE_FIELDS}
    if isinstance(value, list):
        return [_shape(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    return type(value).__name__


def normalize_timeline(entries):
    """Structure-preserving normalization of interleaved timeline entries."""
    ids, sids = {}, {}

    def id_ph(v):
        key = json.dumps(v, sort_keys=True)
        return ids.setdefault(key, f"<ID{len(ids) + 1}>")

    def sid_ph(v):
        return sids.setdefault(str(v), f"<SID{len(sids) + 1}>")

    out = []
    for entry in entries:
        o = entry["frame"]
        d = entry["dir"]
        rec = {"dir": d}
        if d == "c2a":
            if "method" in o and "id" in o:
                params = o.get("params") or {}
                rec.update(kind="req", id=id_ph(o["id"]), method=o["method"])
                if o["method"] == "initialize":
                    rec["protocolVersion"] = params.get("protocolVersion")
                    rec["clientInfo.name"] = (params.get("clientInfo") or {}).get("name")
                    rec["clientCapabilities"] = _shape(params.get("clientCapabilities"))
                elif o["method"] == "session/new":
                    rec["mcpServers"] = len(params.get("mcpServers") or [])
                elif o["method"] == "session/prompt":
                    rec["sessionId"] = sid_ph(params.get("sessionId"))
                    rec["prompt"] = [b.get("type") for b in params.get("prompt") or []]
                else:
                    rec["params"] = _shape(params)
            elif "method" in o:
                params = o.get("params") or {}
                rec.update(kind="notif", method=o["method"])
                if "sessionId" in params:
                    rec["sessionId"] = sid_ph(params["sessionId"])
            else:
                rec.update(kind="resp", id=id_ph(o.get("id")),
                           result=_shape(o.get("result")), error="error" in o)
        else:
            if "method" in o and "id" not in o:
                params = o.get("params") or {}
                rec.update(kind="notif", method=o["method"],
                           sessionId=sid_ph(params.get("sessionId")))
                upd = params.get("update") if isinstance(params.get("update"), dict) else {}
                rec["sessionUpdate"] = upd.get("sessionUpdate")
                rec["update"] = _shape({k: v for k, v in upd.items()
                                        if k not in ("sessionUpdate",)})
            elif "method" in o:
                rec.update(kind="req", id=id_ph(o["id"]), method=o["method"],
                           params=_shape(o.get("params")))
            else:
                res = o.get("result")
                rec.update(kind="resp", id=id_ph(o.get("id")), error="error" in o)
                if isinstance(res, dict):
                    rec["result_keys"] = sorted(res)
                    if "protocolVersion" in res:
                        rec["protocolVersion"] = res["protocolVersion"]
                        rec["agentCapabilities"] = res.get("agentCapabilities")
                        rec["agentInfo.name"] = (res.get("agentInfo") or {}).get("name")
                    if "sessionId" in res:
                        rec["sessionId"] = sid_ph(res["sessionId"])
                    if "stopReason" in res:
                        rec["stopReason"] = res["stopReason"]
                else:
                    rec["result"] = _shape(res)
        out.append(rec)
    return [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in out]


def check_cancel(entries, c2a, a2c, leg_dir, leg="cancel"):
    cancels = [o for o in c2a if o.get("method") == "session/cancel"]
    if not cancels:
        raise Failure(f"{leg}: no session/cancel notification")
    sid = check_prompt_turn(c2a, a2c, leg, entries, expect_stop="cancelled")
    cancel_c2a = [e for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel"]
    if cancel_c2a:
        cancel_sid = (cancel_c2a[0]["frame"].get("params") or {}).get("sessionId")
        if cancel_sid != sid:
            raise Failure(f"{leg}: session/cancel targets a different session")
    prompt_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    chunk_entries = [e for e in entries if e["dir"] == "a2c"
                     and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"]
    cancel_seq = next(e["seq"] for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel")
    term_entries = [e for e in entries if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
                    and (e["frame"].get("result") or {}).get("stopReason") == "cancelled"]
    if not chunk_entries:
        raise Failure(f"{leg}: no agent_message_chunk before cancel")
    if not term_entries:
        raise Failure(f"{leg}: no cancelled terminal response")
    first_chunk_seq = chunk_entries[0]["seq"]
    term_seq = term_entries[0]["seq"]
    if not (prompt_seq < first_chunk_seq < cancel_seq < term_seq):
        raise Failure(f"{leg}: timeline order violation: prompt({prompt_seq}) < chunk({first_chunk_seq}) < cancel({cancel_seq}) < terminal({term_seq})")


def check_shutdown(entries, c2a, a2c, leg_dir, leg="shutdown"):
    check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn")
    exit_path = _require_file(leg_dir / "buzz-acp.exit", leg, "buzz-acp.exit")
    exit_val = exit_path.read_text().strip()
    if exit_val != "0":
        raise Failure(f"{leg}: buzz-acp.exit is {exit_val!r}, expected '0'")


def check_two_users(c2a, a2c, entries, identities, leg="two-users", *, leg_dir):
    resps = {json.dumps(o["id"], sort_keys=True): o for o in a2c if "id" in o and "method" not in o}
    news = [o for o in c2a if o.get("method") == "session/new"]
    prompts = [o for o in c2a if o.get("method") == "session/prompt"]
    # A6: request discipline for two-users: {initialize x1, session/new x2, session/prompt x2}
    c2a_requests = [o for o in c2a if "method" in o and "id" in o]
    c2a_methods = sorted([o["method"] for o in c2a_requests])
    expected_methods = sorted(["initialize", "session/new", "session/new", "session/prompt", "session/prompt"])
    if c2a_methods != expected_methods:
        raise Failure(f"{leg}: c2a request methods {c2a_methods} != expected {expected_methods}")
    # No c2a notifications allowed in two-users
    c2a_notifs = [o for o in c2a if "method" in o and "id" not in o]
    if c2a_notifs:
        raise Failure(f"{leg}: unexpected c2a notification {c2a_notifs[0].get('method')!r}")
    # A2c response ids map to c2a request ids
    c2a_ids = {json.dumps(o["id"], sort_keys=True) for o in c2a_requests}
    a2c_resps = [o for o in a2c if "id" in o and "method" not in o]
    for r in a2c_resps:
        if json.dumps(r["id"], sort_keys=True) not in c2a_ids:
            raise Failure(f"{leg}: a2c response id {r['id']} does not map to any c2a request")
    if len(news) != 2 or len(prompts) != 2:
        raise Failure(f"{leg}: expected 2 session/new + 2 session/prompt, saw {len(news)}/{len(prompts)}")
    sids = []
    for n_obj in news:
        r = resps.get(json.dumps(n_obj["id"], sort_keys=True))
        if not r or "error" in r or not (r.get("result") or {}).get("sessionId"):
            raise Failure(f"{leg}: a session/new lacks a sessionId response")
        sids.append(r["result"]["sessionId"])
    if len(set(sids)) != 2:
        raise Failure(f"{leg}: session ids collide")
    if sorted((o.get("params") or {}).get("sessionId") for o in prompts) != sorted(sids):
        raise Failure(f"{leg}: prompts do not map one-to-one onto the two sessions")
    notifs = [o for o in a2c if "method" in o and "id" not in o]
    foreign = {(o.get("params") or {}).get("sessionId") for o in notifs} - set(sids)
    if foreign:
        raise Failure(f"{leg}: notifications carry a foreign session id")
    for p_obj in prompts:
        r = resps.get(json.dumps(p_obj["id"], sort_keys=True))
        if not r or (r.get("result") or {}).get("stopReason") != "end_turn":
            raise Failure(f"{leg}: a user's turn did not reach end_turn")
    from collections import Counter
    per_session = Counter((o.get("params") or {}).get("sessionId") for o in notifs
                          if ((o.get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk")
    if set(per_session) != set(sids):
        raise Failure(f"{leg}: not every session streamed its own message chunks")
    # A4: two-users mention pubkeys must differ AND identities.owner != identities.user2
    if identities["owner"] == identities["user2"]:
        raise Failure(f"{leg}: identities owner and user2 are identical")
    # A24: assert INGRESS concurrency + OBSERVED serialization
    # Both mentions' created_at precede the FIRST session's terminal t_utc
    mentions_dir = leg_dir / "mentions"
    if not mentions_dir.is_dir():
        raise Failure(f"{leg}: mentions/ absent in {leg_dir.name}")
    owner_ev = json.loads((mentions_dir / "owner.event.json").read_text())
    user2_ev = json.loads((mentions_dir / "user2.event.json").read_text())
    # Find the first session's terminal t_utc
    first_term = None
    for e in entries:
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            r = e["frame"].get("result") or {}
            if r.get("stopReason") == "end_turn":
                first_term = _parse_utc(e["t_utc"])
                break
    if first_term is not None:
        first_term_epoch = int(first_term.timestamp())
        if not (owner_ev["created_at"] < first_term_epoch and user2_ev["created_at"] < first_term_epoch):
            raise Failure(f"{leg}: second mention not pending during the first turn")
    # The second session/new follows the first terminal
    new_seqs = [e for e in entries if e["dir"] == "c2a" and e["frame"].get("method") == "session/new"]
    term_seqs = [e for e in entries if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
                 and (e["frame"].get("result") or {}).get("stopReason") == "end_turn"]
    if len(new_seqs) >= 2 and len(term_seqs) >= 1:
        if new_seqs[1]["seq"] < term_seqs[0]["seq"]:
            raise Failure(f"{leg}: second session/new precedes the first terminal")


def check_manifests(leg_dir, leg, baseline_path, baseline_gz_sha):
    pre_gz = _require_file(leg_dir / "manifest-pre.txt.gz", leg, "manifest-pre.txt.gz")
    post_gz = _require_file(leg_dir / "manifest-post.txt.gz", leg, "manifest-post.txt.gz")
    pre_body = gzip.decompress(pre_gz.read_bytes())
    post_body = gzip.decompress(post_gz.read_bytes())
    _require_file(baseline_path, leg, "manifests/manifest-baseline.txt.gz")
    baseline_body = gzip.decompress(baseline_path.read_bytes())
    if _sha256_file(baseline_path) != baseline_gz_sha:
        raise Failure(f"{leg}: baseline gz sha256 mismatch")
    if pre_body != post_body:
        raise Failure(f"{leg}: manifest pre != post body")
    if pre_body != baseline_body:
        raise Failure(f"{leg}: manifest body != baseline body")
    pre_digests = _parse_manifest_body(pre_body, leg)
    if pre_digests != PINNED_BASELINE_DIGESTS:
        raise Failure(f"{leg}: manifest digests != pinned baseline")
    pre_sum = _require_file(leg_dir / "manifest-pre.summary", leg, "manifest-pre.summary")
    post_sum = _require_file(leg_dir / "manifest-post.summary", leg, "manifest-post.summary")
    pre_sum_d, pre_ts = _parse_summary(pre_sum, leg, "manifest-pre.summary")
    post_sum_d, post_ts = _parse_summary(post_sum, leg, "manifest-post.summary")
    if pre_sum_d != pre_digests:
        raise Failure(f"{leg}: manifest-pre.summary digests != body digests")
    if post_sum_d != pre_digests:
        raise Failure(f"{leg}: manifest-post.summary digests != body digests")
    rid = json.loads((leg_dir / "runtime-identity.json").read_text())
    start_dt = _parse_utc(rid["spawned_at_utc"])
    if not (pre_ts < start_dt < post_ts):
        raise Failure(f"{leg}: manifest timestamps not pre < start < post")
    tl_lines = [l for l in (leg_dir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    last_entry = json.loads(tl_lines[-1])
    if not (post_ts > _parse_utc(last_entry["t_utc"])):
        raise Failure(f"{leg}: manifest-post timestamp not after last timeline t_utc")
    return post_ts


def _parse_manifest_body(body: bytes, leg: str) -> dict:
    text = body.decode("utf-8")
    lines = text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    digests = {}
    current_tree = None
    tree_order = []
    line_counts = {}
    for line in lines:
        if line.startswith("## "):
            tree_name = line[3:].strip()
            if tree_name in digests:
                raise Failure(f"{leg}: duplicate manifest header '## {tree_name}'")
            current_tree = tree_name
            tree_order.append(tree_name)
            digests[tree_name] = ""
            line_counts[tree_name] = 0
        elif current_tree is not None:
            # A13: validate line format
            if not line:
                raise Failure(f"{leg}: manifest body has blank line in section {current_tree}")
            if not _MANIFEST_LINE_RE.match(line):
                raise Failure(f"{leg}: manifest body line does not match format in section {current_tree}")
            digests[current_tree] += line + "\n"
            line_counts[current_tree] += 1
        else:
            raise Failure(f"{leg}: manifest body has content before first header")
    if not tree_order or tree_order[0] != "hermes-agent":
        raise Failure(f"{leg}: manifest first header is not '## hermes-agent'")
    if tuple(tree_order) != MANIFEST_TREES:
        raise Failure(f"{leg}: manifest tree order {tree_order} != {list(MANIFEST_TREES)}")
    # A13: per-tree file counts == PINNED_BASELINE_FILE_COUNTS
    for tree in MANIFEST_TREES:
        if line_counts.get(tree, 0) != PINNED_BASELINE_FILE_COUNTS.get(tree, 0):
            raise Failure(f"{leg}: manifest {tree} file count {line_counts.get(tree, 0)} != pinned {PINNED_BASELINE_FILE_COUNTS.get(tree, 0)}")
    return {tree: _sha256_bytes(content.encode("utf-8")) for tree, content in digests.items()}


def _parse_summary(summary_path, leg, name):
    lines = summary_path.read_text().splitlines()
    expected = len(MANIFEST_TREES) + 1  # one digest line per pinned tree + the UTC timestamp
    if len(lines) != expected:
        raise Failure(f"{leg}: {name} has {len(lines)} lines, expected {expected}")
    digests = {}
    for i, tree_name in enumerate(MANIFEST_TREES):
        parts = lines[i].split()
        if len(parts) != 2 or parts[0] != tree_name:
            raise Failure(f"{leg}: {name} format error at line {i + 1}")
        digests[tree_name] = parts[1]
    return digests, _parse_utc_summary(lines[len(MANIFEST_TREES)].strip())


def check_config_echo(leg_dir, leg):
    startup_path = _require_file(leg_dir / "startup-line.txt", leg, "startup-line.txt")
    startup = startup_path.read_text().strip()
    # A7: startup-line.txt must equal the FIRST line of buzzacp.log containing "buzz-acp starting:"
    log_path = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log")
    log_text = log_path.read_text()
    log_startup = None
    for log_line in log_text.splitlines():
        if "buzz-acp starting:" in log_line:
            log_startup = log_line
            break
    if log_startup is None:
        raise Failure(f"{leg}: buzzacp.log has no line containing 'buzz-acp starting:'")
    if startup != log_startup:
        raise Failure(f"{leg}: startup-line.txt does not match buzzacp.log startup line")
    m = re.match(r'^(\S+)\s+INFO buzz_acp: buzz-acp starting: (.*)$', startup)
    if not m:
        raise Failure(f"{leg}: startup-line.txt does not match expected format")
    tokens = m.group(2).split(" ")
    required_keys = {"relay", "agent_cmd", "mcp_cmd", "idle_timeout", "max_turn",
                     "agents", "dedup", "session_policy", "ignore_self", "permission_mode", "respond_to"}
    kvs = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, _, val = token.partition("=")
        if key in required_keys:
            if key in kvs:
                raise Failure(f"{leg}: startup-line duplicate key {key!r}")
            kvs[key] = val
    missing = required_keys - set(kvs.keys())
    if missing:
        raise Failure(f"{leg}: startup-line missing keys: {sorted(missing)}")
    # A26: agents/dedup/ignore_self from pins, never local literals
    checks = {"relay": PINNED_RELAY_URL, "agent_cmd": PINNED_TEE_PATH, "mcp_cmd": "",
              "idle_timeout": PINNED_IDLE_TIMEOUT, "max_turn": PINNED_MAX_TURN,
              "agents": PINNED_STARTUP_AGENTS,
              "dedup": PINNED_STARTUP_DEDUP,
              "session_policy": PINNED_SESSION_POLICY,
              "ignore_self": PINNED_STARTUP_IGNORE_SELF,
              "permission_mode": "bypassPermissions"}
    for k, exp in checks.items():
        if kvs[k] != exp:
            raise Failure(f"{leg}: startup {k} is {kvs[k]!r}, expected {exp!r}")
    expected_rt = "owner-only" if leg != "two-users" else "allowlist(1)"
    if kvs["respond_to"] != expected_rt:
        raise Failure(f"{leg}: startup respond_to is {kvs['respond_to']!r}, expected {expected_rt!r}")
    argv_path = _require_file(leg_dir / "argv.txt", leg, "argv.txt")
    argv = argv_path.read_text().splitlines()
    if "--idle-timeout" not in argv:
        raise Failure(f"{leg}: argv.txt missing --idle-timeout")
    idx = argv.index("--idle-timeout")
    if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_IDLE_TIMEOUT_ARG:
        raise Failure(f"{leg}: argv --idle-timeout is not {PINNED_IDLE_TIMEOUT_ARG}")
    if "--max-turn-duration" not in argv:
        raise Failure(f"{leg}: argv.txt missing --max-turn-duration")
    idx = argv.index("--max-turn-duration")
    if idx + 1 >= len(argv) or argv[idx + 1] != PINNED_MAX_TURN_DURATION_ARG:
        raise Failure(f"{leg}: argv --max-turn-duration is not {PINNED_MAX_TURN_DURATION_ARG}")


def _parse_scan_v23(path, leg, name):
    """Parse v2.3 scan file: enumeration header (required) + body rows.
    Returns (header_match, [(pid, ppid, etimes, cmd), ...]).
    Raises Failure if the header is absent or does not match the v2.3 shape."""
    lines = path.read_text().splitlines()
    if not lines:
        raise Failure(f"{leg}: {name} has no enumeration header")
    m = _SCAN_HEADER_RE.match(lines[0])
    if not m:
        raise Failure(f"{leg}: {name} has no enumeration header")
    procs = []
    for lineno, line in enumerate(lines[1:], 2):
        if not line or not line.strip():
            raise Failure(f"{leg}: {name} blank line at line {lineno}")
        parts = line.split(None, 3)
        if len(parts) < 4:
            raise Failure(f"{leg}: {name} unparsable line: {line!r}")
        try:
            pid, ppid, etimes = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            raise Failure(f"{leg}: {name} unparsable line: {line!r}")
        procs.append((pid, ppid, etimes, parts[3]))
    return m, procs


def check_process_evidence(leg_dir, leg):
    pid_path = _require_file(leg_dir / "buzz-acp.pid", leg, "buzz-acp.pid")
    try:
        buzz_pid = int(pid_path.read_text().strip())
    except ValueError:
        raise Failure(f"{leg}: buzz-acp.pid is not a valid integer")
    # A2 / F28: buzz-acp.exit REQUIRED in every leg, must be "0"
    exit_path = _require_file(leg_dir / "buzz-acp.exit", leg, "buzz-acp.exit")
    exit_text = exit_path.read_text().strip()
    try:
        int(exit_text)
    except ValueError:
        raise Failure(f"{leg}: buzz-acp.exit is not a valid integer")
    if exit_text != "0":
        raise Failure(f"{leg}: buzz-acp.exit is {exit_text!r}, expected '0'")
    # A20 / F15: load and validate owned-pids.json shape
    owned_path = _require_file(leg_dir / "owned-pids.json", leg, "owned-pids.json")
    owned_data = json.loads(owned_path.read_text())
    if not isinstance(owned_data, dict):
        raise Failure(f"{leg}: owned-pids.json is not an object")
    _OWNED_REQUIRED_KEYS = {"buzz_acp_pid", "owned", "taken_at"}
    if not _OWNED_REQUIRED_KEYS.issubset(set(owned_data.keys())):
        missing = sorted(_OWNED_REQUIRED_KEYS - set(owned_data.keys()))
        raise Failure(f"{leg}: owned-pids.json missing required keys: {missing}")
    extra_owned_keys = set(owned_data.keys()) - _OWNED_REQUIRED_KEYS
    if extra_owned_keys:
        raise Failure(f"{leg}: owned-pids.json has extra keys: {sorted(extra_owned_keys)}")
    if not _is_strict_int(owned_data["buzz_acp_pid"]):
        raise Failure(f"{leg}: owned-pids.json buzz_acp_pid is not int")
    if not isinstance(owned_data["owned"], list) or not owned_data["owned"]:
        raise Failure(f"{leg}: owned-pids.json owned is empty or not a list")
    if not all(_is_strict_int(p) for p in owned_data["owned"]):
        raise Failure(f"{leg}: owned-pids.json owned contains non-int")
    if not isinstance(owned_data["taken_at"], str):
        raise Failure(f"{leg}: owned-pids.json taken_at is not a string")
    owned_set = set(owned_data["owned"])
    # F13: owned must contain buzz_acp_pid
    if buzz_pid not in owned_set:
        raise Failure(f"{leg}: owned-pids.json does not contain buzz-acp.pid {buzz_pid}")
    # F16: header buzz_acp_pid must equal buzz-acp.pid
    if owned_data["buzz_acp_pid"] != buzz_pid:
        raise Failure(f"{leg}: owned-pids.json buzz_acp_pid {owned_data['buzz_acp_pid']} != buzz-acp.pid {buzz_pid}")
    # F13/F14: the identity-binding check for rid pids in the scan-level
    # branch (non-shutdown) already validates tee_pid and agent_child_pid presence;
    # here we only enforce that the owned set is non-vacuous (contains buzz_pid).
    # A20 v2.3: parse and validate after-scan header
    scan_path = _require_file(leg_dir / "process-scan-after.txt", leg, "process-scan-after.txt")
    hdr, all_procs = _parse_scan_v23(scan_path, leg, "process-scan-after.txt")
    if hdr.group(1) != "after":
        raise Failure(f"{leg}: process-scan-after.txt header mode is '{hdr.group(1)}', expected 'after'")
    if int(hdr.group(2)) == 0:
        raise Failure(f"{leg}: process-scan-after.txt header rows=0 (enumeration did not run)")
    if int(hdr.group(5)) != len(owned_set):
        raise Failure(f"{leg}: process-scan-after.txt header owned={hdr.group(5)} != owned-pids.json ({len(owned_set)})")
    body_owned = sum(1 for pid, _, _, _ in all_procs if pid in owned_set)
    if int(hdr.group(6)) != body_owned:
        raise Failure(f"{leg}: process-scan-after.txt header owned_present={hdr.group(6)} inconsistent with body ({body_owned})")
    # F16: header buzz_acp_pid must equal buzz-acp.pid file
    if int(hdr.group(3)) != buzz_pid:
        raise Failure(f"{leg}: process-scan-after.txt header buzz_acp_pid={hdr.group(3)} != buzz-acp.pid {buzz_pid}")
    # F17: pinned_present must equal count of body rows whose cmd names a pinned path
    body_pinned = sum(1 for _, _, _, cmd in all_procs
                      if PINNED_BUZZ_ACP_EXE_REALPATH in cmd or PINNED_TEE_PATH in cmd or PINNED_AGENT_REALPATH in cmd)
    if int(hdr.group(7)) != body_pinned:
        raise Failure(f"{leg}: process-scan-after.txt header pinned_present={hdr.group(7)} inconsistent with body ({body_pinned})")
    if leg == "shutdown":
        # A20 v2.3 rule 4 / F10: shutdown after-scan body must be EMPTY — any row is a survivor
        for pid, ppid, etimes, cmd in all_procs:
            raise Failure(f"{leg}: process {pid} ({cmd[:40]}) survived shutdown")
        # A20 v2.3 rule 4: shutdown after-scan must have buzz_present=0
        if int(hdr.group(4)) != 0:
            raise Failure(f"{leg}: process-scan-after.txt buzz_present={hdr.group(4)} in shutdown (expected 0)")
    else:
        # A20d: non-shutdown legs require non-empty after-scan body
        if not all_procs:
            raise Failure(f"{leg}: process-scan-after.txt is empty")
        # A20a: recompute closure from ppid links starting at buzz_pid
        recomputed = {buzz_pid}
        changed = True
        while changed:
            changed = False
            for pid, ppid, _, _ in all_procs:
                if ppid in recomputed and pid not in recomputed:
                    recomputed.add(pid)
                    changed = True
        if recomputed != owned_set:
            raise Failure(f"{leg}: recomputed owned closure != owned-pids.json")
        # A20a: any line whose pid is not owned and whose cmd names no pinned path is a Failure
        for pid, ppid, _, cmd in all_procs:
            if pid not in owned_set:
                if not (PINNED_BUZZ_ACP_EXE_REALPATH in cmd or PINNED_TEE_PATH in cmd or PINNED_AGENT_REALPATH in cmd):
                    raise Failure(f"{leg}: process {pid} not owned and cmd names no pinned path")
        # A2 / 7-F24: buzz-acp line matched with cmd.split(" ")[0] == PINNED_BUZZ_ACP_EXE_REALPATH
        buzz_found = any(pid == buzz_pid and cmd.split(" ")[0] == PINNED_BUZZ_ACP_EXE_REALPATH
                         for pid, _, _, cmd in all_procs)
        if not buzz_found:
            raise Failure(f"{leg}: process-scan-after has no buzz-acp line with pid {buzz_pid}")
        tee_pids = {pid for pid, ppid, _, cmd in all_procs if PINNED_TEE_PATH in cmd and ppid == buzz_pid}
        if not tee_pids:
            raise Failure(f"{leg}: no tee process parented by buzz-acp")
        if not any(PINNED_AGENT_REALPATH in cmd and ppid in tee_pids for _, ppid, _, cmd in all_procs):
            raise Failure(f"{leg}: no agent process parented by a tee process")
        # A20b: identity binding from runtime-identity.json
        rid = json.loads((leg_dir / "runtime-identity.json").read_text())
        tee_pid = rid.get("tee_pid")
        agent_child_pid = rid.get("agent_child_pid")
        # tee_pid has ppid == buzz_pid and cmd containing PINNED_TEE_PATH
        tee_lines = [(p, pp, et, c) for p, pp, et, c in all_procs if p == tee_pid]
        if not tee_lines:
            raise Failure(f"{leg}: tee_pid {tee_pid} not found in scan")
        if tee_lines[0][1] != buzz_pid:
            raise Failure(f"{leg}: tee_pid {tee_pid} ppid is not buzz_acp_pid")
        if PINNED_TEE_PATH not in tee_lines[0][3]:
            raise Failure(f"{leg}: tee_pid {tee_pid} cmd does not contain PINNED_TEE_PATH")
        # agent_child_pid has ppid == tee_pid and cmd containing PINNED_AGENT_REALPATH
        agent_lines = [(p, pp, et, c) for p, pp, et, c in all_procs if p == agent_child_pid]
        if not agent_lines:
            raise Failure(f"{leg}: agent_child_pid {agent_child_pid} not found in scan")
        if agent_lines[0][1] != tee_pid:
            raise Failure(f"{leg}: agent_child_pid {agent_child_pid} ppid is not tee_pid")
        if PINNED_AGENT_REALPATH not in agent_lines[0][3]:
            raise Failure(f"{leg}: agent_child_pid {agent_child_pid} cmd does not contain PINNED_AGENT_REALPATH")
        # A2: descendant closure check — exempt only the launcher whose pid == buzz-acp ppid
        buzz_ppid = None
        for pid, ppid, _, cmd in all_procs:
            if pid == buzz_pid:
                buzz_ppid = ppid
                break
        # A20e: pc_launch.py line is the buzz-acp parent by ppid and never in the closure
        for pid, ppid, _, cmd in all_procs:
            if PINNED_TEE_PATH in cmd or PINNED_AGENT_REALPATH in cmd or PINNED_BUZZ_ACP_EXE_REALPATH in cmd:
                if buzz_ppid is not None and pid == buzz_ppid:
                    continue
                if pid not in recomputed:
                    raise Failure(f"{leg}: process {pid} ({cmd[:40]}) not in buzz-acp descendant tree")
    # A20c v2.3: teardown scan — header + survivor check (ALL legs)
    teardown_path = _require_file(leg_dir / "process-scan-teardown.txt", leg, "process-scan-teardown.txt")
    td_hdr, teardown_procs = _parse_scan_v23(teardown_path, leg, "process-scan-teardown.txt")
    if td_hdr.group(1) != "teardown":
        raise Failure(f"{leg}: process-scan-teardown.txt header mode is '{td_hdr.group(1)}', expected 'teardown'")
    if int(td_hdr.group(2)) == 0:
        raise Failure(f"{leg}: process-scan-teardown.txt header rows=0 (enumeration did not run)")
    if int(td_hdr.group(5)) != len(owned_set):
        raise Failure(f"{leg}: process-scan-teardown.txt header owned={td_hdr.group(5)} != owned-pids.json ({len(owned_set)})")
    td_body_owned = sum(1 for pid, _, _, _ in teardown_procs if pid in owned_set)
    if int(td_hdr.group(6)) != td_body_owned:
        raise Failure(f"{leg}: process-scan-teardown.txt header owned_present={td_hdr.group(6)} inconsistent with body ({td_body_owned})")
    # F12: teardown buzz_present must be 0
    if int(td_hdr.group(4)) != 0:
        raise Failure(f"{leg}: process-scan-teardown.txt buzz_present={td_hdr.group(4)} (expected 0)")
    # F30: duplicate scan rows for one pid
    td_pids = [pid for pid, _, _, _ in teardown_procs]
    if len(td_pids) != len(set(td_pids)):
        from collections import Counter
        dups = [p for p, c in Counter(td_pids).items() if c > 1]
        raise Failure(f"{leg}: process-scan-teardown.txt duplicate rows for pid(s) {dups}")
    # A20 v2.3 rule 5 / F11: teardown body must be EMPTY — any row is a survivor
    for pid, ppid, etimes, cmd in teardown_procs:
        raise Failure(f"{leg}: process {pid} ({cmd[:40]}) survived teardown")


def check_buzzacp_log(leg_dir, leg):
    log_path = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log")
    log_text = log_path.read_text()
    # 5-F14: case-insensitive 64-hex guard
    if _HEX64_ANYWHERE_RE.search(log_text):
        raise Failure(f"{leg}: buzzacp.log contains unmasked 64-hex string")
    if leg == "cancel":
        if "mode=Cancel" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'mode=Cancel'")
    elif leg == "shutdown":
        if "shutdown command from owner" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'shutdown command from owner'")
        if "buzz-acp stopped" not in log_text:
            raise Failure(f"{leg}: buzzacp.log missing 'buzz-acp stopped'")
    # A24: two-users log lines must appear exactly once
    if leg == "two-users":
        for expected_line in PINNED_LOG_LINES_TWO_USERS:
            count = log_text.count(expected_line)
            if count != 1:
                raise Failure(f"{leg}: buzzacp.log expected exactly 1 occurrence of {expected_line!r}, got {count}")


def check_tee_status(leg_dir, leg, entries):
    """A21d: validate tee-status.json — twelve-key running status."""
    ts_path = _require_file(leg_dir / "tee-status.json", leg, "tee-status.json")
    ts = json.loads(ts_path.read_text())
    if not isinstance(ts, dict):
        raise Failure(f"{leg}: tee-status.json is not an object")
    if set(ts.keys()) != _TEE_STATUS_KEYS:
        extra = sorted(set(ts.keys()) - _TEE_STATUS_KEYS)
        missing = sorted(_TEE_STATUS_KEYS - set(ts.keys()))
        raise Failure(f"{leg}: tee-status.json key set mismatch (extra={extra}, missing={missing})")
    if ts["drained"] is not True:
        raise Failure(f"{leg}: tee-status.json drained is not true")
    if ts["write_errors"] != []:
        raise Failure(f"{leg}: tee-status.json write_errors is not empty")
    if ts["forwarded_c2a"] != ts["recorded_c2a"]:
        raise Failure(f"{leg}: tee-status.json forwarded_c2a != recorded_c2a")
    if ts["forwarded_a2c"] != ts["recorded_a2c"]:
        raise Failure(f"{leg}: tee-status.json forwarded_a2c != recorded_a2c")
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    if ts["recorded_c2a"] != c2a_count:
        raise Failure(f"{leg}: tee-status.json recorded_c2a {ts['recorded_c2a']} != timeline c2a count {c2a_count}")
    if ts["recorded_a2c"] != a2c_count:
        raise Failure(f"{leg}: tee-status.json recorded_a2c {ts['recorded_a2c']} != timeline a2c count {a2c_count}")
    last_seq = entries[-1]["seq"] if entries else 0
    if ts["updated_seq"] != last_seq:
        raise Failure(f"{leg}: tee-status.json updated_seq {ts['updated_seq']} != timeline last seq {last_seq}")
    utc_re = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
    if not isinstance(ts["updated_utc"], str) or not utc_re.match(ts["updated_utc"]):
        raise Failure(f"{leg}: tee-status.json updated_utc does not match format")
    # A21d: when final, A21b exit_code rule; when not final, both exit fields null
    # F31: final must be a strict bool
    if ts["final"] is not True and ts["final"] is not False:
        raise Failure(f"{leg}: tee-status.json final is not a bool")
    # F32: stdin_reader_done must be True when final is true
    if ts["final"] is True and ts.get("stdin_reader_done") is not True:
        raise Failure(f"{leg}: tee-status.json stdin_reader_done is not true when final")
    if ts["final"] is True:
        rc = ts["agent_returncode"]
        if not _is_strict_int(rc):
            raise Failure(f"{leg}: tee-status.json final but agent_returncode is not int")
        expected_exit = rc if rc >= 0 else 128 + (-rc)
        if ts["exit_code"] != expected_exit:
            raise Failure(f"{leg}: tee-status.json exit_code {ts['exit_code']} != expected {expected_exit}")
    else:
        if ts["agent_returncode"] is not None:
            raise Failure(f"{leg}: tee-status.json not final but agent_returncode is not null")
        if ts["exit_code"] is not None:
            raise Failure(f"{leg}: tee-status.json not final but exit_code is not null")


def check_negative(neg_dir, leg="negative"):
    """A22: delegate to the shared negative_contract validator."""
    # 5-F09/6-F15: check for extra entries including dirs
    if neg_dir.is_dir():
        actual = {f.name for f in neg_dir.iterdir()}
        extra = actual - set(NEGATIVE_REQUIRED_FILES)
        if extra:
            raise Failure(f"{leg}: unexpected entries: {sorted(extra)}")
    try:
        observed = nc.validate_negative_dir(neg_dir, _fixtures())
    except nc.NegativeDeferred as d:
        raise Failure(f"{leg}: {d}")
    except nc.NegativeFailure as f:
        raise Failure(f"{leg}: negative: {f}")
    # 5-F19: screen agent-stderr.txt for secret shapes
    stderr_path = neg_dir / "agent-stderr.txt"
    if stderr_path.exists():
        stderr_text = stderr_path.read_text()
        if _STDERR_LEAK_RE.search(stderr_text):
            raise Failure(f"{leg}: agent-stderr.txt contains a secret-shaped string")
    return f"observed: {observed}"


def check_golden(golden_dir, leg="golden"):
    n1 = normalize_timeline(_load_timeline_raw(golden_dir / "run-1", "run-1"))
    n2 = normalize_timeline(_load_timeline_raw(golden_dir / "run-2", "run-2"))
    if n1 != n2:
        first = next((i for i, (a, b) in enumerate(zip(n1, n2)) if a != b), min(len(n1), len(n2)))
        raise Failure(f"{leg}: golden mismatch between run-1 and run-2 at normalized line {first}")
    frozen_path = _require_file(golden_dir / "golden.jsonl", leg, "golden.jsonl")
    frozen_bytes = frozen_path.read_bytes()
    frozen_sha = _sha256_bytes(frozen_bytes)
    if PINNED_GOLDEN_SHA256 is None:
        raise Failure(f"{leg}: golden not pinned")
    if frozen_sha != PINNED_GOLDEN_SHA256:
        raise Failure(f"{leg}: golden.jsonl sha256 {frozen_sha[:12]} != pinned {PINNED_GOLDEN_SHA256[:12]}")
    frozen_raw = frozen_bytes.decode("utf-8").splitlines()
    for lineno, fl in enumerate(frozen_raw, 1):
        if not fl or not fl.strip():
            raise Failure(f"{leg}: golden.jsonl blank line at line {lineno}")
    frozen_lines = frozen_raw
    if frozen_lines != n1:
        raise Failure(f"{leg}: normalized runs differ from the frozen golden.jsonl")
    if not n1:
        raise Failure(f"{leg}: golden is empty")
    # A6 / §8 structural assertions on the normalized sequence
    first_rec = json.loads(n1[0])
    if first_rec.get("dir") != "c2a" or first_rec.get("method") != "initialize":
        raise Failure(f"{leg}: first normalized line is not c2a initialize request")
    if first_rec.get("protocolVersion") != PINNED_CLIENT_PROTOCOL_VERSION:
        raise Failure(f"{leg}: first normalized line protocolVersion is not {PINNED_CLIENT_PROTOCOL_VERSION}")
    # §8: exactly one of each request kind
    req_methods = [json.loads(l).get("method") for l in n1
                   if json.loads(l).get("kind") == "req" and json.loads(l).get("dir") == "c2a"]
    if sorted(req_methods) != sorted(["initialize", "session/new", "session/prompt"]):
        raise Failure(f"{leg}: golden does not have exactly one of each request kind")
    # §8: a2c initialize response precedes c2a session/new
    init_resp_idx = None
    session_new_idx = None
    for i, line in enumerate(n1):
        r = json.loads(line)
        if r.get("dir") == "a2c" and r.get("kind") == "resp" and r.get("protocolVersion") is not None:
            if init_resp_idx is None:
                init_resp_idx = i
        if r.get("dir") == "c2a" and r.get("method") == "session/new":
            if session_new_idx is None:
                session_new_idx = i
    if init_resp_idx is not None and session_new_idx is not None and init_resp_idx >= session_new_idx:
        raise Failure(f"{leg}: a2c initialize response does not precede c2a session/new")
    # §8: session/new response precedes session/prompt
    new_resp_idx = None
    prompt_idx = None
    for i, line in enumerate(n1):
        r = json.loads(line)
        if r.get("dir") == "a2c" and r.get("kind") == "resp" and r.get("sessionId") is not None:
            if new_resp_idx is None:
                new_resp_idx = i
        if r.get("dir") == "c2a" and r.get("method") == "session/prompt":
            if prompt_idx is None:
                prompt_idx = i
    if new_resp_idx is not None and prompt_idx is not None and new_resp_idx >= prompt_idx:
        raise Failure(f"{leg}: session/new response does not precede session/prompt")
    # §8: every a2c notification carries <SID1>
    for i, line in enumerate(n1):
        r = json.loads(line)
        if r.get("dir") == "a2c" and r.get("kind") == "notif":
            if r.get("sessionId") != "<SID1>":
                raise Failure(f"{leg}: a2c notification at line {i} does not carry <SID1>")
    # §8: >= 1 agent_message_chunk
    chunks = [l for l in n1 if '"agent_message_chunk"' in l]
    if not chunks:
        raise Failure(f"{leg}: golden has no agent_message_chunk")
    last_rec = json.loads(n1[-1])
    if last_rec.get("stopReason") != "end_turn":
        raise Failure(f"{leg}: last normalized line is not end_turn terminal")
    run1_entries = _load_timeline_raw(golden_dir / "run-1", "run-1")
    run2_entries = _load_timeline_raw(golden_dir / "run-2", "run-2")

    def _raw_sid(ents):
        for e in ents:
            if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
                r = e["frame"].get("result") or {}
                if "sessionId" in r:
                    return r["sessionId"]
        return None

    sid1, sid2 = _raw_sid(run1_entries), _raw_sid(run2_entries)
    if sid1 is not None and sid2 is not None and sid1 == sid2:
        raise Failure(f"{leg}: run-1 and run-2 raw sessionIds are identical")
    if run1_entries[0]["t_utc"] == run2_entries[0]["t_utc"]:
        raise Failure(f"{leg}: run-1 and run-2 first t_utc are identical")
    r1m = golden_dir / "run-1" / "mentions" / "owner.event.json"
    r2m = golden_dir / "run-2" / "mentions" / "owner.event.json"
    if r1m.exists() and r2m.exists():
        if json.loads(r1m.read_text()).get("id") == json.loads(r2m.read_text()).get("id"):
            raise Failure(f"{leg}: run-1 and run-2 owner mention event ids are identical")
    return n1


def _load_timeline_raw(leg_dir, leg):
    tl_path = _require_file(leg_dir / "timeline.jsonl", leg, "timeline.jsonl")
    entries = []
    for lineno, line in enumerate(tl_path.read_text().splitlines(), 1):
        if not line or not line.strip():
            raise Failure(f"{leg}: timeline.jsonl blank line at line {lineno}")
        entries.append(_reject_nan(line, leg, lineno))
    return entries


def check_bundle(root: Path) -> str:
    golden = root / "golden"
    if not golden.is_dir():
        raise Deferred("v2 evidence not captured")
    has_any_timeline = any((golden / leg / "timeline.jsonl").exists() for leg in LEGS)
    if not has_any_timeline:
        raise Deferred("v2 evidence not captured")
    identities_path = _fixtures() / "identities.json"
    _require_file(identities_path, "golden", "fixtures/identities.json")
    identities = json.loads(identities_path.read_text())
    baseline_path = golden / "manifests" / "manifest-baseline.txt.gz"
    # A13: golden/manifests/ contains exactly manifest-baseline.txt.gz
    _require_dir(golden / "manifests", "golden", "manifests/")
    _require_file(baseline_path, "golden", "manifests/manifest-baseline.txt.gz")
    manifest_entries = {f.name for f in (golden / "manifests").iterdir()}
    if manifest_entries != {"manifest-baseline.txt.gz"}:
        raise Failure(f"golden: manifests/ contains unexpected entries: {sorted(manifest_entries - {'manifest-baseline.txt.gz'})}")
    expected_dirs = set(LEGS) | {"negative", "manifests"}
    expected_files = {"golden.jsonl"}
    for item in golden.iterdir():
        if item.is_dir() and item.name not in expected_dirs:
            raise Failure(f"golden: unexpected directory golden/{item.name}")
        if item.is_file() and item.name not in expected_files:
            raise Failure(f"golden: unexpected file golden/{item.name}")
    # 5-F18 / F19: any non-regular, non-directory entry (symlink, FIFO, socket, device) is a Failure
    import stat as _stat
    for dirpath, dirnames, filenames in os.walk(golden, followlinks=False):
        dp = Path(dirpath)
        for name in dirnames + filenames:
            p = dp / name
            try:
                st = p.lstat()
            except OSError as e:
                raise Failure(f"golden: cannot stat {p.relative_to(root)}: {e}")
            if p.is_symlink():
                raise Failure(f"golden: symlink in evidence tree: {p.relative_to(root)}")
            if not (_stat.S_ISREG(st.st_mode) or _stat.S_ISDIR(st.st_mode)):
                raise Failure(f"golden: non-regular entry in evidence tree: {p.relative_to(root)}")
    global _executed
    _executed = []
    all_mention_event_ids = []
    # 6-F19: load schema ONCE from fixtures dir
    schema_path = _fixtures() / "acp-schema-v1.json"
    schema = ci.load_schema(schema_path) if schema_path.exists() else None
    # A1: pre-read post-summary timestamps for the mention window
    post_summary_ts_map = {}
    for leg in LEGS:
        d = golden / leg
        post_sum_path = d / "manifest-post.summary"
        if post_sum_path.exists():
            _, post_ts = _parse_summary(post_sum_path, leg, "manifest-post.summary")
            post_summary_ts_map[leg] = post_ts
    # F20/F21: per-leg entry allowlist — required + optional files
    _LEG_REQUIRED_FILES = {
        "timeline.jsonl", "frames-client-to-agent.jsonl", "frames-agent-to-client.jsonl",
        "runtime-identity.json", "env.json", "hermes-model.txt", "startup-line.txt",
        "argv.txt", "buzz-acp.pid", "buzz-acp.exit", "buzzacp.log",
        "manifest-pre.txt.gz", "manifest-post.txt.gz", "manifest-pre.summary",
        "manifest-post.summary", "process-scan-after.txt", "process-scan-teardown.txt",
        "owned-pids.json", "tee-status.json", "agent-stderr.txt",
    }
    _LEG_OPTIONAL_DIRS = {"mentions", "upstream-records"}
    for leg in LEGS:
        d = golden / leg
        if not d.is_dir():
            raise Failure(f"golden: golden/{leg} absent")
        # F21: entry allowlist
        allowed = _LEG_REQUIRED_FILES | _LEG_OPTIONAL_DIRS
        for item in d.iterdir():
            if item.name not in allowed:
                raise Failure(f"{leg}: unexpected entry {item.name}")
        # F20: agent-stderr.txt is REQUIRED in every positive leg
        _require_file(d / "agent-stderr.txt", leg, "agent-stderr.txt")
        entries = _load_timeline_raw(d, leg)
        c2a_split, a2c_split = _run_check(check_timeline, leg, entries, leg, d)
        _run_check(check_initialize_frames, leg, c2a_split, a2c_split, leg, schema=schema)
        _run_check(check_runtime_identity, leg, d, leg)
        _run_check(check_env, leg, d, leg, identities)
        post_summary_ts = post_summary_ts_map.get(leg)
        leg_event_ids = _run_check(check_mentions, leg, d, leg, identities, entries, post_summary_ts)
        all_mention_event_ids.extend(leg_event_ids)
        _run_check(check_route, leg, d, leg, entries)
        # F20: screen agent-stderr.txt for secret shapes (unconditional — file is required)
        stderr_text = (d / "agent-stderr.txt").read_text()
        if _STDERR_LEAK_RE.search(stderr_text):
            raise Failure(f"{leg}: agent-stderr.txt contains a secret-shaped string")
    for leg in ("run-1", "run-2", "shutdown"):
        d = golden / leg
        entries = _load_timeline_raw(d, leg)
        c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
        a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
        _run_check(check_prompt_turn, leg, c2a, a2c, leg, entries)
    for leg in LEGS:
        _run_check(check_config_echo, leg, golden / leg, leg)
    for leg in LEGS:
        _run_check(check_manifests, leg, golden / leg, leg, baseline_path, PINNED_BASELINE_GZ_SHA256)
    for leg in LEGS:
        _run_check(check_process_evidence, leg, golden / leg, leg)
    for leg in LEGS:
        _run_check(check_buzzacp_log, leg, golden / leg, leg)
    for leg in LEGS:
        d = golden / leg
        entries = _load_timeline_raw(d, leg)
        _run_check(check_tee_status, leg, d, leg, entries)
    d = golden / "cancel"
    entries = _load_timeline_raw(d, "cancel")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    _run_check(check_cancel, "cancel", entries, c2a, a2c, d)
    d = golden / "shutdown"
    entries = _load_timeline_raw(d, "shutdown")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    _run_check(check_shutdown, "shutdown", entries, c2a, a2c, d)
    d = golden / "two-users"
    entries = _load_timeline_raw(d, "two-users")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    _run_check(check_two_users, "two-users", c2a, a2c, entries, identities, leg_dir=d)
    if len(all_mention_event_ids) != len(set(all_mention_event_ids)):
        raise Failure("golden: mention event id replayed across legs")
    golden_lines = _run_check(check_golden, "golden", golden)
    neg_dir = golden / "negative"
    _require_dir(neg_dir, "golden", "negative/")
    neg_observed = _run_check(check_negative, "negative", neg_dir)
    # A25: compare the FULL ordered (check, leg) sequence, no dedup
    if _executed != EXPECTED_CHECK_SEQUENCE:
        for pair in EXPECTED_CHECK_SEQUENCE:
            if pair not in _executed:
                raise Failure(f"golden: check sequence mismatch - first missing: {pair[0]}:{pair[1]}")
        raise Failure(f"golden: check sequence mismatch ({len(_executed)} vs {len(EXPECTED_CHECK_SEQUENCE)} expected)")
    count = len(golden_lines)
    golden_sha_12 = _sha256_bytes("\n".join(golden_lines).encode("utf-8") + b"\n")[:12]
    return (f"PASS: S0-01 acp-conformance - {len(_executed)} checks executed over "
            f"{len(LEGS)} legs; golden x2 identical ({count} normalized lines, "
            f"sha256 {golden_sha_12}); negative: {neg_observed}")


def main(argv) -> int:
    import signal as _signal
    global _FIXTURES_DIR
    # A15: optional --fixtures-dir <dir> (default: proofs/S0-01/fixtures).
    # spec.json does NOT pass it; tests use it to point at throwaway fixtures.
    args = list(argv[1:])
    timeout_s = 120  # F19: default wall-clock cap
    if "--fixtures-dir" in args:
        idx = args.index("--fixtures-dir")
        if idx + 1 >= len(args):
            print("usage: check_acp_conformance.py [--fixtures-dir <dir>] [--timeout-s N] <evidence-root>", file=sys.stderr)
            return 64
        _FIXTURES_DIR = args[idx + 1]
        del args[idx:idx + 2]
    if "--timeout-s" in args:
        idx = args.index("--timeout-s")
        if idx + 1 >= len(args):
            print("usage: check_acp_conformance.py [--fixtures-dir <dir>] [--timeout-s N] <evidence-root>", file=sys.stderr)
            return 64
        try:
            timeout_s = int(args[idx + 1])
        except ValueError:
            print("usage: --timeout-s requires an integer", file=sys.stderr)
            return 64
        del args[idx:idx + 2]
    if len(args) != 1:
        print("usage: check_acp_conformance.py [--fixtures-dir <dir>] [--timeout-s N] <evidence-root>", file=sys.stderr)
        return 64
    # F19: wall-clock cap — a FIFO in the evidence tree would hang read_text() forever
    def _timeout_handler(signum, frame):
        print(f"failure_reason: checker timed out after {timeout_s}s")
        sys.exit(70)
    _signal.signal(_signal.SIGALRM, _timeout_handler)
    _signal.alarm(timeout_s)
    try:
        print(check_bundle(Path(args[0])))
        return 0
    except Deferred as d:
        print(f"deferred: {d}")
        return 2
    except Failure as f:
        print(f"failure_reason: {f}")
        return 1
    except Exception as exc:
        print(f"failure_reason: malformed evidence: {type(exc).__name__}: {exc}")
        return 1
    finally:
        _signal.alarm(0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
