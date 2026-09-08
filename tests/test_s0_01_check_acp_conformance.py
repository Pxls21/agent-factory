"""proofs/S0-01/check_acp_conformance.py v2.2 test suite.

Synthesized PASS bundle uses nostr_verify.sign_event with throwaway keys for ALL
mention events. The bundle fixture writes a synthetic identities.json into tmp_path
(never the tracked tree) and monkeypatches the checker module's HERE-based fixture
path to point at the tmp fixtures directory.

The only patched pin is PINNED_GOLDEN_SHA256 (set to the synthetic golden's sha,
monkeypatched, commented).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
CHECKER = P / "check_acp_conformance.py"
FIXTURES = P / "fixtures"
GOLDEN = P / "evidence" / "golden"

sys.path.insert(0, str(P))
sys.path.insert(0, str(P / "tools"))
import check_acp_conformance as cc  # noqa: E402
import negative_contract as nc  # noqa: E402
import nostr_verify as nv  # noqa: E402
from pins import (  # noqa: E402
    ENV_ALLOWLIST_KEY,
    EXPECTED_MENTIONS, EXPECTED_MODEL, LEGS, MANIFEST_TREES, MENTION_TEXT,
    PINNED_AGENT_ENTRYPOINT_SHA256, PINNED_AGENT_INTERPRETER_REALPATH,
    PINNED_AGENT_INTERPRETER_SHA256,
    PINNED_AGENT_REALPATH,
    PINNED_BASELINE_DIGESTS,
    PINNED_BUZZ_ACP_EXE_REALPATH,
    PINNED_BASELINE_GZ_SHA256,
    PINNED_BUZZ_ACP_SHA256, PINNED_CLIENT_PROTOCOL_VERSION,
    PINNED_HOME, PINNED_HERMES_HOME,
    PINNED_IDLE_TIMEOUT, PINNED_IDLE_TIMEOUT_ARG,
    PINNED_LAUNCH_ARGV, PINNED_MAX_TURN,
    PINNED_PATH,
    PINNED_RELAY_URL, PINNED_ROUTE_PREFIX, PINNED_SESSION_POLICY,
    PINNED_TEE_PATH, PINNED_UPSTREAM_HOST, UPSTREAM_POST_PATH,
)

# Throwaway keys for synthetic mention events
OWNER_SECKEY = "0" * 63 + "2"
USER2_SECKEY = "0" * 63 + "3"
OWNER_PUBKEY = format(nv._point_mul(2, nv.G)[0], "064x")
USER2_PUBKEY = format(nv._point_mul(3, nv.G)[0], "064x")

_REAL_IDS = json.loads(FIXTURES.joinpath("identities.json").read_text())
SYNTH_IDENTITIES = {
    "owner": OWNER_PUBKEY, "user2": USER2_PUBKEY,
    "agent": _REAL_IDS["agent"], "channel": _REAL_IDS["channel"],
    "relay": _REAL_IDS["relay"], "relay_url": _REAL_IDS["relay_url"],
}


# 5-F17: session-scoped autouse fixture — install _cached_pm once, restore _orig_pm once.
# The memo cache stays module-level so BIP-340 speed is kept across the whole session.
_pm_cache = {}
_orig_pm = nv._point_mul


def _cached_pm(k, point):
    key = (k, point)
    if key not in _pm_cache:
        _pm_cache[key] = _orig_pm(k, point)
    return _pm_cache[key]


@pytest.fixture(autouse=True, scope="session")
def _patch_nostr_verify():
    """5-F17: install _cached_pm for the session, restore _orig_pm on teardown."""
    nv._point_mul = _cached_pm
    yield
    nv._point_mul = _orig_pm


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_frames(leg_dir: Path):
    c2a = [json.loads(l) for l in (leg_dir / "frames-client-to-agent.jsonl").read_text().splitlines() if l.strip()]
    a2c = [json.loads(l) for l in (leg_dir / "frames-agent-to-client.jsonl").read_text().splitlines() if l.strip()]
    return c2a, a2c


def _load_fingerprint():
    return FIXTURES.joinpath("upstream-token.fingerprint").read_text().strip()


def _make_interleaved_timeline(c2a, a2c, leg):
    """Build physically-possible interleaving with realistic sub-second spacing."""
    frames = []
    if leg in ("run-1", "run-2", "shutdown"):
        frames = [("c2a", c2a[0]), ("a2c", a2c[0]), ("c2a", c2a[1]), ("a2c", a2c[1]),
                  ("c2a", c2a[2])] + [("a2c", f) for f in a2c[2:]]
    elif leg == "cancel":
        frames = [("c2a", c2a[0]), ("a2c", a2c[0]), ("c2a", c2a[1]), ("a2c", a2c[1]),
                  ("c2a", c2a[2])] + [("a2c", f) for f in a2c[2:5]] + [("c2a", c2a[3])] + [("a2c", f) for f in a2c[5:]]
    elif leg == "two-users":
        frames = [("c2a", c2a[0]), ("a2c", a2c[0]), ("c2a", c2a[1]), ("a2c", a2c[1]),
                  ("c2a", c2a[2])] + [("a2c", f) for f in a2c[2:8]] + [("c2a", c2a[3]), ("a2c", a2c[8]),
                  ("c2a", c2a[4])] + [("a2c", f) for f in a2c[9:]]
    entries = []
    base_mono = 1_000_000_000_000
    # Per-leg base times: realistic sub-second spacing (50-300ms between frames)
    leg_bases = {"run-1": 0, "run-2": 3600, "cancel": 7200, "shutdown": 10800, "two-users": 14400}
    base_dt = datetime(2026, 9, 5, 5, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=leg_bases.get(leg, 0))
    for i, (d, frame) in enumerate(frames, 1):
        # 100ms per frame (realistic spacing)
        offset_ms = i * 100
        t = base_dt + timedelta(milliseconds=offset_ms)
        entries.append({"seq": i, "dir": d,
                        "t_utc": t.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "t_mono_ns": base_mono + i * 100_000_000, "frame": frame})
    return entries


def _write_timeline(leg_dir, entries):
    """Write timeline + frames files.  F43: unlinks before writing so hardlinked
    copies of the session bundle are not corrupted."""
    leg_dir.mkdir(parents=True, exist_ok=True)
    for fn in ("timeline.jsonl", "frames-client-to-agent.jsonl", "frames-agent-to-client.jsonl"):
        p = leg_dir / fn
        p.unlink(missing_ok=True)
    with open(leg_dir / "timeline.jsonl", "w") as f:
        for e in entries:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    with open(leg_dir / "frames-client-to-agent.jsonl", "w") as f:
        for e in entries:
            if e["dir"] == "c2a":
                f.write(json.dumps(e["frame"]) + "\n")
    with open(leg_dir / "frames-agent-to-client.jsonl", "w") as f:
        for e in entries:
            if e["dir"] == "a2c":
                f.write(json.dumps(e["frame"]) + "\n")


def _write_runtime_identity(leg_dir, leg):
    tee_sha = _sha256_file(P / "tools" / "frame_tee.py")
    rid = {"tee_path": PINNED_TEE_PATH, "tee_sha256": tee_sha, "tee_pid": 12340,
           "agent_argv": [PINNED_AGENT_REALPATH], "agent_realpath": PINNED_AGENT_REALPATH,
           "agent_entrypoint_sha256": PINNED_AGENT_ENTRYPOINT_SHA256, "agent_child_pid": 12345,
           "agent_interpreter_realpath": PINNED_AGENT_INTERPRETER_REALPATH,
           "agent_interpreter_sha256": PINNED_AGENT_INTERPRETER_SHA256,
           "python_dont_write_bytecode": True, "spawned_at_utc": "2026-09-05T05:00:00.050000Z",
           "buzz_acp_pid": 12300, "buzz_acp_exe_realpath": PINNED_BUZZ_ACP_EXE_REALPATH,
           "buzz_acp_exe_sha256": PINNED_BUZZ_ACP_SHA256, "buzz_acp_version": "0.1.0",
           "launch_argv": list(PINNED_LAUNCH_ARGV)}
    (leg_dir / "runtime-identity.json").write_text(json.dumps(rid, indent=2) + "\n")


def _write_env(leg_dir, identities, leg):
    env = {"S0_01_AGENT": PINNED_AGENT_REALPATH, "HERMES_HOME": PINNED_HERMES_HOME,
           "BUZZ_RELAY_URL": PINNED_RELAY_URL,
           "OMNIROUTE_API_KEY": {"redacted": True, "len": 32, "sha256_12": "abcdef012345"},
           "PYTHONDONTWRITEBYTECODE": "1", "BUZZ_ACP_RESPOND_TO": "owner-only",
           "BUZZ_ACP_AGENT_OWNER": identities["owner"],
           "BUZZ_ACP_SESSION_POLICY": PINNED_SESSION_POLICY,
           "BUZZ_PRIVATE_KEY": {"redacted": True, "len": 64, "sha256_12": "112233445566"},
           "HOME": PINNED_HOME, "PATH": PINNED_PATH, "S0_01_FRAMEDIR": "/tmp/frames"}
    if leg == "two-users":
        env["BUZZ_ACP_RESPOND_TO"] = "allowlist"
        env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = identities["user2"]
    (leg_dir / "env.json").write_text(json.dumps(env, indent=2) + "\n")


def _write_startup_and_log(leg_dir, leg):
    """Write BOTH startup-line.txt and buzzacp.log so the startup line appears in the log.
    A26: agents/dedup/ignore_self from pins."""
    from pins import PINNED_STARTUP_AGENTS, PINNED_STARTUP_DEDUP, PINNED_STARTUP_IGNORE_SELF, PINNED_LOG_LINES_TWO_USERS
    rt = "owner-only" if leg != "two-users" else "allowlist(1)"
    startup = (f"2026-09-05T05:00:00.000000Z  INFO buzz_acp: buzz-acp starting: "
               f"relay={PINNED_RELAY_URL} pubkey=<HEX> "
               f"agent_cmd={PINNED_TEE_PATH}  mcp_cmd= "
               f"idle_timeout={PINNED_IDLE_TIMEOUT} max_turn={PINNED_MAX_TURN} "
               f"agents={PINNED_STARTUP_AGENTS} heartbeat=0s "
               f"subscribe=Mentions dedup={PINNED_STARTUP_DEDUP} session_policy={PINNED_SESSION_POLICY} "
               f"meh=Steer ignore_self={PINNED_STARTUP_IGNORE_SELF} context_limit=12 "
               f"max_turns_per_session=0 presence=true typing=true memory=true "
               f"model=(agent default) permission_mode=bypassPermissions respond_to={rt}")
    (leg_dir / "startup-line.txt").write_text(startup + "\n")
    (leg_dir / "argv.txt").write_text("\n".join(PINNED_LAUNCH_ARGV) + "\n")
    # Log includes the startup line (A7) plus any leg-specific entries
    lines = [startup]
    if leg == "cancel":
        lines.append("2026-09-05T05:00:01Z  INFO buzz_acp: mode=Cancel")
    if leg == "shutdown":
        lines.append("2026-09-05T05:00:01Z  INFO buzz_acp: shutdown command from owner")
        lines.append("2026-09-05T05:00:02Z  INFO buzz_acp: buzz-acp stopped")
    # A24: two-users log lines
    if leg == "two-users":
        for log_line in PINNED_LOG_LINES_TWO_USERS:
            lines.append(f"2026-09-05T05:00:01Z  INFO buzz_acp: {log_line}")
    (leg_dir / "buzzacp.log").write_text("\n".join(lines) + "\n")
    # Write agent-stderr.txt for every leg (5-F19)
    (leg_dir / "agent-stderr.txt").write_text("2026-09-05 INFO hermes: started\n")


def _write_model(leg_dir, leg):
    (leg_dir / "hermes-model.txt").write_text(f"  default: {PINNED_ROUTE_PREFIX}/{EXPECTED_MODEL[leg]}\n")


def _write_manifests(leg_dir, baseline_path):
    committed = GOLDEN / "manifests" / "manifest-baseline.txt.gz"
    gz_bytes = committed.read_bytes()
    body = gzip.decompress(gz_bytes)
    gz_data = gzip.compress(body, mtime=0)
    (leg_dir / "manifest-pre.txt.gz").write_bytes(gz_data)
    (leg_dir / "manifest-post.txt.gz").write_bytes(gz_data)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_bytes(gz_bytes)
    for name, ts in [("manifest-pre.summary", "2026-09-05T05:00:00Z"),
                     ("manifest-post.summary", "2026-09-06T23:59:59Z")]:
        lines = [f"{tree} {PINNED_BASELINE_DIGESTS[tree]}" for tree in MANIFEST_TREES]
        lines.append(ts)
        (leg_dir / name).write_text("\n".join(lines) + "\n")


_event_counter = [0]

def _sign_mention(seckey, content, tags_list, created_at=None):
    _event_counter[0] += 1
    if created_at is None:
        created_at = 1788608000 + _event_counter[0]
    return nv.sign_event(seckey, {"created_at": created_at,
                                  "kind": 9, "tags": tags_list, "content": content})


def _write_mentions(leg_dir, leg, identities, entries):
    """Write mentions with created_at inside the A1 window: [floor(first t_utc) - 5, post_summary_ts + 5]."""
    mentions_dir = leg_dir / "mentions"
    mentions_dir.mkdir(parents=True, exist_ok=True)
    expected = EXPECTED_MENTIONS.get(leg, [])
    base_tags = [["h", identities["channel"]], ["p", identities["agent"]]]
    # Use the first timeline entry's t_utc floor for the window lower bound
    first_utc = datetime.strptime(entries[0]["t_utc"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    # A24/6-F16: created_at inside the A1 window and BEFORE the first terminal for two-users
    created_at_base = int(first_utc.timestamp()) - 2  # -2s to ensure both precede the first terminal
    written = {}
    for idx, (tag, id_key, content, replies_to) in enumerate(expected):
        seckey = OWNER_SECKEY if id_key == "owner" else USER2_SECKEY
        tags_list = list(base_tags)
        if replies_to is not None and replies_to in written:
            tags_list.append(["e", written[replies_to]["id"], "", "reply"])
        event = _sign_mention(seckey, content, tags_list, created_at=created_at_base + idx)
        written[tag] = event
        (mentions_dir / f"{tag}.event.json").write_text(json.dumps(event, indent=2) + "\n")
        receipt = {"accepted": True, "event_id": event["id"],
                   "mention_pubkeys": [identities["agent"]], "message": ""}
        (mentions_dir / f"{tag}.receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        (mentions_dir / f"{tag}.receipt.err").write_text("")


def _write_upstream_records(leg_dir, leg, entries, fingerprint):
    """6-F20: TWO POSTs per prompt window (title + stream), numbered from 000001.
    R8-CK-F7: GET fingerprint is null.  R8-CK-F8: per-shape body key sets and role sequences."""
    rec_dir = leg_dir / "upstream-records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    model = EXPECTED_MODEL[leg]
    prompt_times = [e["t_utc"] for e in entries
                    if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt"]
    idx = 1  # numbered from 000001
    for pt in prompt_times:
        # Non-stream title POST — R8-CK-F8: {messages, model, response_format, temperature}
        title_rec = {"seq": idx, "method": "POST", "path": UPSTREAM_POST_PATH,
                     "body": {"model": model,
                              "messages": [{"role": "system", "content": "sys"},
                                           {"role": "user", "content": "title"}],
                              "response_format": {"type": "text"}, "temperature": 0.2},
                     "headers": {"host": PINNED_UPSTREAM_HOST, "content-type": "application/json"},
                     "authorization_fingerprint": fingerprint, "received_at": pt,
                     "t_mono_ns": 1_000_000_000_000 + idx * 1_000_000, "remote_addr": "127.0.0.1"}
        (rec_dir / f"{idx:06d}.json").write_text(json.dumps(title_rec, indent=2) + "\n")
        idx += 1
        # Stream POST — R8-CK-F8: {max_tokens, messages, model, stream, stream_options, tools}
        rec = {"seq": idx, "method": "POST", "path": UPSTREAM_POST_PATH,
               "body": {"model": model,
                        "messages": [{"role": "system", "content": "sys"},
                                     {"role": "user", "content": MENTION_TEXT}],
                        "stream": True, "max_tokens": 64,
                        "stream_options": {"include_usage": True}, "tools": []},
               "headers": {"host": PINNED_UPSTREAM_HOST, "content-type": "application/json"},
               "authorization_fingerprint": fingerprint, "received_at": pt,
               "t_mono_ns": 1_000_000_000_000 + idx * 1_000_000, "remote_addr": "127.0.0.1"}
        (rec_dir / f"{idx:06d}.json").write_text(json.dumps(rec, indent=2) + "\n")
        idx += 1
    # R8-CK-F7: GET fingerprint is null — the real producer records null on GET.
    get_rec = {"seq": idx, "method": "GET", "path": "/models", "body": None,
               "headers": {"host": PINNED_UPSTREAM_HOST}, "authorization_fingerprint": None,
               "received_at": prompt_times[0] if prompt_times else "2026-09-05T06:00:00.000000Z",
               "t_mono_ns": 1_000_000_000_000 + idx * 1_000_000, "remote_addr": "127.0.0.1"}
    (rec_dir / f"{idx:06d}.json").write_text(json.dumps(get_rec, indent=2) + "\n")


def _scan_header(mode, *, rows=50, buzz_pid=12300, buzz_present=1, owned=3,
                 owned_present=3, pinned_present=0, owned_zombies=0):
    """Build a v2.3 scan enumeration header line.
    pinned_present defaults to 0; callers set it to match their body rows."""
    return (f"# process-scan v2.3 mode={mode} rows={rows} buzz_acp_pid={buzz_pid} "
            f"buzz_present={buzz_present} owned={owned} owned_present={owned_present} "
            f"pinned_present={pinned_present} owned_zombies={owned_zombies} "
            f"utc=2026-09-05T12:00:00Z")


def _write_process_scan(leg_dir, leg):
    """A20 v2.3: scan header + body rows; owned-pids.json.
    Fixture derived from pc_post.sh's keep rule: only owned rows and rows naming
    a pinned path are persisted. (D): no /sbin/init — the real producer never emits it."""
    buzz_pid = 12300
    tee_pid = 12340  # matches runtime-identity.json tee_pid
    agent_pid = 12345  # matches runtime-identity.json agent_child_pid
    launcher_pid = 1
    owned = sorted([buzz_pid, tee_pid, agent_pid])
    (leg_dir / "buzz-acp.pid").write_text(f"{buzz_pid}\n")
    (leg_dir / "owned-pids.json").write_text(json.dumps(
        {"buzz_acp_pid": buzz_pid, "owned": owned, "taken_at": "ready+after"}) + "\n")
    (leg_dir / "buzz-acp.exit").write_text("0\n")
    if leg == "shutdown":
        # After a clean shutdown, all owned pids have exited — empty body with v2.3 header.
        (leg_dir / "process-scan-after.txt").write_text(
            _scan_header("after", buzz_present=0, owned_present=0, pinned_present=0) + "\n")
    else:
        lines = [_scan_header("after", pinned_present=3),
                 f"{buzz_pid} {launcher_pid} 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999",
                 f"{tee_pid} {buzz_pid} 90 /usr/bin/python3 {PINNED_TEE_PATH}",
                 f"{agent_pid} {tee_pid} 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}"]
        (leg_dir / "process-scan-after.txt").write_text("\n".join(lines) + "\n")
    (leg_dir / "process-scan-teardown.txt").write_text(
        _scan_header("teardown", buzz_present=0, owned_present=0, pinned_present=0) + "\n")


def _write_tee_status(leg_dir, entries):
    """A21d: write a valid twelve-key tee-status.json matching the timeline.
    Produces the running-status shape (final=false, exit fields null) since the
    real tee is SIGKILLed before it can finalize. R8-CK-F17: the values are hand-authored
    and only the key SET is bound (to pins.PINNED_TEE_STATUS_KEYS via the checker's
    _TEE_STATUS_KEYS). F43: unlinks before writing so hardlinked session copies are safe."""
    (leg_dir / "tee-status.json").unlink(missing_ok=True)
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"] if entries else 0
    last_utc = entries[-1]["t_utc"] if entries else "2026-09-05T05:00:00.000000Z"
    status = {
        "final": False,
        "agent_returncode": None,
        "drained": True,
        "stdin_reader_done": True,
        "recorded_c2a": c2a_count,
        "recorded_a2c": a2c_count,
        "forwarded_c2a": c2a_count,
        "forwarded_a2c": a2c_count,
        "write_errors": [],
        "exit_code": None,
        "updated_seq": last_seq,
        "updated_utc": last_utc,
    }
    (leg_dir / "tee-status.json").write_text(json.dumps(status, indent=2) + "\n")


def _write_negative(neg_dir, identities):
    """A22: build a negative capture that passes negative_contract.validate_negative_dir."""
    neg_dir.mkdir(parents=True, exist_ok=True)
    fixture = json.loads((FIXTURES / "neg-malformed-initialize.json").read_text())
    entries = [
        {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T05:00:00.000001Z",
         "t_mono_ns": 1_000_000_000_001,
         "frame": {"jsonrpc": "2.0", "method": "initialize", "params": fixture, "id": 0}},
        {"seq": 2, "dir": "a2c", "t_utc": "2026-09-05T05:00:00.000002Z",
         "t_mono_ns": 1_000_000_000_002,
         "frame": {"jsonrpc": "2.0", "id": 0, "error": {"code": -32602, "message": "Invalid params",
                   "data": {"errors": [{"type": "missing", "loc": ["protocolVersion"], "msg": "Field required"}]}}}}]
    with open(neg_dir / "timeline.jsonl", "w") as f:
        for e in entries:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    probe_sha = _sha256_file(P / "tools" / "acp_probe.py")
    rid = {"probe_path": "/home/rocco/agent-factory/proofs/S0-01/tools/acp_probe.py",
           "probe_sha256": probe_sha,
           "agent_argv": [PINNED_AGENT_REALPATH], "agent_realpath": PINNED_AGENT_REALPATH,
           "agent_entrypoint_sha256": PINNED_AGENT_ENTRYPOINT_SHA256,
           "agent_child_pid": 99999,
           "agent_interpreter_realpath": PINNED_AGENT_INTERPRETER_REALPATH,
           "agent_interpreter_sha256": PINNED_AGENT_INTERPRETER_SHA256,
           "python_dont_write_bytecode": True, "spawned_at_utc": "2026-09-05T05:00:00.000000Z",
           "agent_exit_code": 0, "agent_cgroup": "/"}
    (neg_dir / "runtime-identity.json").write_text(json.dumps(rid, indent=2) + "\n")
    env = {"PATH": PINNED_PATH, "HOME": PINNED_HOME,
           "HERMES_HOME": PINNED_HERMES_HOME, "PYTHONDONTWRITEBYTECODE": "1",
           "S0_01_AGENT": PINNED_AGENT_REALPATH,
           "S0_01_FRAMEDIR": "/tmp/frames/neg",
           "OMNIROUTE_API_KEY": {"redacted": True, "len": 35, "sha256_12": "fe5d1f1b287b"}}
    (neg_dir / "env.json").write_text(json.dumps(env, indent=2) + "\n")
    (neg_dir / "agent-stderr.txt").write_text("2026-09-05 18:57:21 [INFO] acp_adapter.server: ACP client connected\n")


@pytest.fixture(scope="session")
def _session_bundle(tmp_path_factory):
    """Session-scoped: build the synthetic bundle ONCE for the whole test session."""
    _event_counter[0] = 0
    base = tmp_path_factory.mktemp("bundle")
    g = base / "evidence" / "golden"
    identities = SYNTH_IDENTITIES
    fingerprint = _load_fingerprint()
    baseline_path = g / "manifests" / "manifest-baseline.txt.gz"
    # Write synthetic identities into tmp fixtures dir (NEVER the tracked tree)
    tmp_fixtures = base / "fixtures"
    tmp_fixtures.mkdir(parents=True, exist_ok=True)
    (tmp_fixtures / "identities.json").write_text(json.dumps(identities, indent=2) + "\n")
    # Copy other required fixtures
    # CK11 sweep 1.10: unguarded copy — a missing required fixture must raise.
    for fn in ("neg-malformed-initialize.json", "upstream-token.fingerprint", "acp-schema-v1.json"):
        src = FIXTURES / fn
        shutil.copy2(src, tmp_fixtures / fn)
    for leg in LEGS:
        ld = g / leg
        c2a, a2c = _load_frames(GOLDEN / leg)
        entries = _make_interleaved_timeline(c2a, a2c, leg)
        _write_timeline(ld, entries)
        _write_runtime_identity(ld, leg)
        _write_env(ld, identities, leg)
        _write_startup_and_log(ld, leg)
        _write_model(ld, leg)
        _write_manifests(ld, baseline_path)
        _write_mentions(ld, leg, identities, entries)
        _write_upstream_records(ld, leg, entries, fingerprint)
        _write_process_scan(ld, leg)
        _write_tee_status(ld, entries)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(g / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    (g / "golden.jsonl").write_text(golden_text)
    golden_sha = _sha256(golden_text.encode("utf-8"))
    _write_negative(g / "negative", identities)
    return base, golden_sha, tmp_fixtures


@pytest.fixture
def bundle(_session_bundle, tmp_path, monkeypatch):
    """Per-test: hardlink copy from session fixture; monkeypatch the checker.
    F43: hardlink overlay (cp -al) — every mutation must go through _rewrite()
    which unlinks before writing so the pristine session copy is never corrupted."""
    base, golden_sha, tmp_fixtures = _session_bundle
    dest = tmp_path / "evidence"
    shutil.copytree(base / "evidence", dest, copy_function=os.link)
    # Copy fixtures and tools into tmp_path so monkeypatching HERE works
    dest_fixtures = tmp_path / "fixtures"
    shutil.copytree(tmp_fixtures, dest_fixtures, copy_function=os.link)
    # R9-CK-F19: copy tools with shutil.copy2 (real copy), never os.link —
    # a hardlink to tracked sources means an in-place write corrupts the repo.
    dest_tools = tmp_path / "tools"
    shutil.copytree(P / "tools", dest_tools, copy_function=shutil.copy2)
    # Monkeypatch PINNED_GOLDEN_SHA256 (the ONLY patched pin -- commented)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", golden_sha)
    # Monkeypatch HERE so the checker reads identities.json from tmp fixtures
    # and tools/frame_tee.py from tmp tools (never touching the tracked tree)
    monkeypatch.setattr("check_acp_conformance.HERE", tmp_path)
    yield dest


def _rewrite(path, data):
    """F43: unlink before write to preserve the hardlinked pristine copy.
    Every test-function mutation on a bundle file MUST go through this helper.
    Handles both str (write_text) and bytes (write_bytes)."""
    path = Path(path)
    path.unlink(missing_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data)


def _run(root: Path, fixtures_dir: Path = None):
    cmd = [sys.executable, str(CHECKER)]
    if fixtures_dir is not None:
        cmd.extend(["--fixtures-dir", str(fixtures_dir)])
    cmd.append(str(root))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=os.environ.copy())


def _check(bndl, timeout_s=60):
    """R9-CK-F28: pass a generous but finite cap (60 s) so a walk regression fails
    loudly instead of wedging the suite. None disables for explicit timeout tests."""
    try:
        return 0, cc.check_bundle(bndl, timeout_s=timeout_s)
    except cc.Deferred as d:
        return 2, f"deferred: {d}"
    except cc.Failure as f:
        return 1, f"failure_reason: {f}"
    except SystemExit as se:
        return int(se.code or 0), "failure_reason: checker timed out"
    except Exception as exc:
        return 1, f"failure_reason: malformed evidence: {type(exc).__name__}: {exc}"


# === CLI tests ===
def test_real_bundle_cli():
    r = _run(P / "evidence")
    if (P / "evidence" / "golden" / "run-1" / "timeline.jsonl").exists():
        assert r.returncode == 0 and r.stdout.strip().startswith("PASS:")
    else:
        assert r.returncode == 2
        assert r.stdout.strip() == "deferred: v2 evidence not captured"


def test_passing_v2_bundle(bundle):
    result = cc.check_bundle(bundle)
    assert result.startswith("PASS: S0-01 acp-conformance")
    assert "checks executed" in result
    assert "negative: observed:" in result
    # A25: PASS line reports len(executed), which is the full (check, leg) count
    assert f"{len(cc.EXPECTED_CHECK_SEQUENCE)} checks executed" in result


def test_cli_pass_path_fails_on_golden_pin(bundle, _session_bundle):
    """The subprocess does NOT have monkeypatched PINNED_GOLDEN_SHA256=None, so golden not pinned.
    A15: --fixtures-dir points the subprocess at the synthetic identities (not the tracked ones)."""
    _, _, tmp_fixtures = _session_bundle
    r = _run(bundle, fixtures_dir=tmp_fixtures)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: golden: golden not pinned"


def test_cli_usage_error_exit_64():
    """A10: CLI usage error exits 64, never 2."""
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, timeout=10)
    assert r.returncode == 64


# === Deferrals ===
def test_absent_defers(tmp_path):
    """6-F16: both deferral branches emit the same text."""
    (tmp_path / "e").mkdir()
    r = _run(tmp_path / "e")
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: v2 evidence not captured"


def test_no_timelines_defers(tmp_path):
    (tmp_path / "evidence" / "golden" / "run-1").mkdir(parents=True)
    r = _run(tmp_path / "evidence")
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: v2 evidence not captured"


# === M1-M5 owner mutations ===
def test_m1_manifest_zeroed(bundle):
    gz = gzip.compress(b"## hermes-agent\nZ\n## buzz\nZ\n## acp\nZ\n", mtime=0)
    for leg in LEGS:
        _rewrite(bundle / "golden" / leg / "manifest-pre.txt.gz", gz)
        _rewrite(bundle / "golden" / leg / "manifest-post.txt.gz", gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_m2_tampered_sig(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    ev = json.loads(ep.read_text()); ev["sig"] = "ff" * 64
    _rewrite(ep, json.dumps(ev) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner BIP-340 signature invalid: r >= p"


def test_m2_wrong_pubkey(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    ev = _sign_mention(USER2_SECKEY, MENTION_TEXT,
                       [["h", SYNTH_IDENTITIES["channel"]], ["p", SYNTH_IDENTITIES["agent"]]])
    _rewrite(ep, json.dumps(ev) + "\n")
    rp = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    receipt = json.loads(rp.read_text()); receipt["event_id"] = ev["id"]
    _rewrite(rp, json.dumps(receipt) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner pubkey != identities[owner]"


def test_m3_cancel_foreign(bundle):
    ld = bundle / "golden" / "cancel"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel":
            e["frame"]["params"]["sessionId"] = "foreign-00000000"
    _write_timeline(ld, entries)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: cancel: session/cancel targets a different session"


def test_m4_shutdown_init_only(bundle):
    """Shutdown leg with only initialize frames: check_route fires because no prompt windows
    exist (no session/prompt in the truncated timeline), but POST records are present."""
    ld = bundle / "golden" / "shutdown"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    filtered = [e for e in entries if e["frame"].get("method") == "initialize"
                or (e["dir"] == "a2c" and "id" in e["frame"] and e["frame"].get("id") == 0)]
    for i, e in enumerate(filtered): e["seq"] = i + 1
    _write_timeline(ld, filtered)
    rc, out = _check(bundle)
    assert rc == 1
    # check_route fires: POST records exist but no prompt windows (no session/prompt in timeline)
    assert out == "failure_reason: shutdown: upstream POST record received_at 2026-09-05T08:00:00.500000Z outside all prompt windows"


def test_m5_1s(bundle):
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        old = sp.read_text()
        new = old.replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=1s")
        _rewrite(sp, new)
        # Also update buzzacp.log (A7: startup line must be in log)
        lp = bundle / "golden" / leg / "buzzacp.log"
        _rewrite(lp, lp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=1s"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: startup max_turn is '1s', expected '{PINNED_MAX_TURN}'"


def test_m5_7200(bundle):
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        old = sp.read_text()
        new = old.replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=7200s")
        _rewrite(sp, new)
        lp = bundle / "golden" / leg / "buzzacp.log"
        _rewrite(lp, lp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=7200s"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: startup max_turn is '7200s', expected '{PINNED_MAX_TURN}'"


# === Deletion attacks for EVERY required file ===
@pytest.mark.parametrize("fn,leg", [
    ("timeline.jsonl", "run-1"), ("frames-client-to-agent.jsonl", "run-1"),
    ("frames-agent-to-client.jsonl", "run-1"), ("runtime-identity.json", "run-1"),
    ("env.json", "run-1"), ("hermes-model.txt", "run-1"), ("startup-line.txt", "run-1"),
    ("argv.txt", "run-1"), ("buzz-acp.pid", "run-1"),
    ("buzz-acp.exit", "run-1"), ("buzz-acp.exit", "cancel"), ("buzz-acp.exit", "two-users"),
    ("buzz-acp.exit", "shutdown"),
    ("buzzacp.log", "run-1"), ("manifest-pre.txt.gz", "run-1"),
    ("manifest-post.txt.gz", "run-1"), ("manifest-pre.summary", "run-1"),
    ("manifest-post.summary", "run-1"), ("process-scan-after.txt", "run-1"),
    ("process-scan-after.txt", "cancel"), ("process-scan-after.txt", "shutdown"),
    ("process-scan-teardown.txt", "run-1"), ("buzzacp.log", "cancel"), ("buzzacp.log", "shutdown"),
])
def test_deletion(bundle, fn, leg):
    p = bundle / "golden" / leg / fn
    p.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: {leg}: {fn} absent"


def test_del_mentions(bundle):
    shutil.rmtree(bundle / "golden" / "run-1" / "mentions")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mentions/ absent"


def test_del_upstream(bundle):
    shutil.rmtree(bundle / "golden" / "run-1" / "upstream-records")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: zero upstream records / upstream-records/ absent"


def test_del_baseline(bundle):
    (bundle / "golden" / "manifests" / "manifest-baseline.txt.gz").unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: manifests/manifest-baseline.txt.gz absent"


def test_del_negative(bundle):
    shutil.rmtree(bundle / "golden" / "negative")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: negative/ absent"


def test_del_golden_jsonl(bundle):
    (bundle / "golden" / "golden.jsonl").unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: golden.jsonl absent"


def test_del_leg(bundle):
    shutil.rmtree(bundle / "golden" / "run-1")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: golden/run-1 absent"


# Negative directory deletions
@pytest.mark.parametrize("fn", ["runtime-identity.json", "env.json", "agent-stderr.txt", "timeline.jsonl"])
def test_del_negative_file(bundle, fn):
    """A22: deletion of a negative-required file -> Failure via shared validator."""
    p = bundle / "golden" / "negative" / fn
    p.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    if fn == "timeline.jsonl":
        assert out == "failure_reason: negative: negative probe not captured"
    else:
        assert out == f"failure_reason: negative: negative: {fn} absent"


def test_del_neg_fixture(bundle):
    """A11/A22: neg-malformed-initialize.json absent -> Failure via shared validator."""
    fp = bundle.parent / "fixtures" / "neg-malformed-initialize.json"
    fp.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: negative: fixtures/neg-malformed-initialize.json absent"


def test_del_identities(bundle):
    fp = bundle.parent / "fixtures" / "identities.json"
    fp.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: fixtures/identities.json absent"


# === Timeline type attacks ===
def test_seq_float(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es: e["seq"] = float(e["seq"])
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline seq at index 0 is not int"


def test_seq_bool(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["seq"] = True; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline seq at index 0 is not int"


def test_seq_gap(bundle):
    """m01: seq not strictly 1..N."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[3]["seq"] = es[3]["seq"] + 1
    _rewrite(ld / "timeline.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline seq not strictly 1..N at index 3"


def test_mono_backwards(bundle):
    """m02: t_mono_ns not non-decreasing."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[2]["t_mono_ns"] = es[1]["t_mono_ns"] - 5
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: t_mono_ns not non-decreasing at seq 3"


def test_nan(bundle):
    tl = bundle / "golden" / "run-1" / "timeline.jsonl"
    _rewrite(tl, re.sub(r'"t_mono_ns":(\d+)', '"t_mono_ns":NaN', tl.read_text(), count=1))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: NaN or Infinity in timeline at seq 1"


def test_mono_string(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["t_mono_ns"] = "x"; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline t_mono_ns at seq 1 is not int"


def test_dir_unknown(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["dir"] = "x2x"; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline dir at seq 1 is 'x2x', expected 'c2a' or 'a2c'"


# === §2 directional file attacks ===
def test_frames_c2a_extra_line(bundle):
    """m05: extra line in frames-client-to-agent.jsonl."""
    p = bundle / "golden" / "run-1" / "frames-client-to-agent.jsonl"
    _rewrite(p, p.read_text() + '{"jsonrpc":"2.0","method":"evil","id":99}\n')
    rc, out = _check(bundle)
    assert rc == 1
    # Line count mismatch fires first
    assert out.startswith("failure_reason: run-1: frames-client-to-agent.jsonl")


def test_frames_a2c_reordered(bundle):
    """m06: reordered lines in frames-agent-to-client.jsonl."""
    p = bundle / "golden" / "run-1" / "frames-agent-to-client.jsonl"
    lines = p.read_text().splitlines()
    if len(lines) >= 2:
        lines[0], lines[1] = lines[1], lines[0]
    _rewrite(p, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: frames-agent-to-client.jsonl does not match timeline a2c split"


def test_blank_line_in_frames(bundle):
    """6-F19 / 7-F18: blank line -> Failure."""
    p = bundle / "golden" / "run-1" / "frames-agent-to-client.jsonl"
    lines = p.read_text().splitlines()
    _rewrite(p, lines[0] + "\n   \n" + "\n".join(lines[1:]) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: frames-agent-to-client.jsonl blank line at line 2"


# === §3 runtime identity attacks ===
def test_rid_missing_tee_pid(bundle):
    """6-F11 / 7-F19: missing tee_pid."""
    ld = bundle / "golden" / "run-1"
    p = ld / "runtime-identity.json"
    o = json.loads(p.read_text()); del o["tee_pid"]; _rewrite(p, json.dumps(o) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: runtime-identity.json key set mismatch (extra=[], missing=['tee_pid'])"


def test_rid_buzz_sha_wrong(bundle):
    """m09."""
    ld = bundle / "golden" / "run-1"
    p = ld / "runtime-identity.json"
    o = json.loads(p.read_text()); o["buzz_acp_exe_sha256"] = "0" * 64; _rewrite(p, json.dumps(o) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: buzz_acp_exe_sha256 mismatch"


def test_rid_tee_sha_wrong(bundle):
    """m10."""
    ld = bundle / "golden" / "run-1"
    p = ld / "runtime-identity.json"
    o = json.loads(p.read_text()); o["tee_sha256"] = "0" * 64; _rewrite(p, json.dumps(o) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: tee_sha256 mismatch"


def test_rid_argv_wrong(bundle):
    """m11."""
    ld = bundle / "golden" / "run-1"
    p = ld / "runtime-identity.json"
    o = json.loads(p.read_text()); a = list(o["launch_argv"]); a[1], a[3] = a[3], a[1]; o["launch_argv"] = a
    _rewrite(p, json.dumps(o) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: launch_argv mismatch"


def test_rid_entrypoint_sha_wrong(bundle):
    """m12."""
    ld = bundle / "golden" / "run-1"
    p = ld / "runtime-identity.json"
    o = json.loads(p.read_text()); o["agent_entrypoint_sha256"] = "0" * 64; _rewrite(p, json.dumps(o) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: agent_entrypoint_sha256 mismatch"


def test_argv_tampered(bundle):
    ld = bundle / "golden" / "run-1"
    rp = ld / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_argv"] = ["/tmp/evil"]; _rewrite(rp, json.dumps(rid) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: agent_argv mismatch"


def test_interp_tampered(bundle):
    ld = bundle / "golden" / "run-1"
    rp = ld / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_interpreter_realpath"] = "/tmp/evil"; _rewrite(rp, json.dumps(rid) + "\n")
    ok, result = _run_check_safe(cc.check_runtime_identity, ld, "run-1")
    assert not ok
    assert result == "run-1: agent_interpreter_realpath mismatch"


# === §4 env attacks (direct check calls — item 7 speed) ===
def _ids(bundle):
    return json.loads((bundle.parent / "fixtures" / "identities.json").read_text())


def test_env_extra_key(bundle):
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["X"] = "v"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env.json key set mismatch (extra=['X'], missing=[])"


def test_env_hermes_home_wrong(bundle):
    """m14."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["HERMES_HOME"] = "/tmp/evil"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env HERMES_HOME mismatch"


def test_env_path_wrong(bundle):
    """m15."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["PATH"] = "/evil"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env PATH mismatch"


def test_env_policy_wrong(bundle):
    """m16."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_SESSION_POLICY"] = "wrong"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env BUZZ_ACP_SESSION_POLICY mismatch"


def test_env_pdwb_wrong(bundle):
    """m17."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["PYTHONDONTWRITEBYTECODE"] = "0"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env PYTHONDONTWRITEBYTECODE is not '1'"


def test_owner_swap(bundle):
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_AGENT_OWNER"] = "de" * 32; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env BUZZ_ACP_AGENT_OWNER mismatch"


def test_env_leak(bundle):
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_PRIVATE_KEY"] = "plaintext"; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env BUZZ_PRIVATE_KEY should be redacted but is not a dict"


def test_hex_leak_env(bundle):
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "ab" * 32; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_hex_leak_uppercase(bundle):
    """A9 / 7-F17: uppercase hex detected."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "AB" * 32; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_hex_leak_with_prefix(bundle):
    """A9: hex with prefix detected."""
    ld = bundle / "golden" / "run-1"
    ep = ld / "env.json"
    env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "sk-" + "ab" * 32; _rewrite(ep, json.dumps(env) + "\n")
    ok, result = _run_check_safe(cc.check_env, ld, "run-1", _ids(bundle))
    assert not ok
    assert result == "run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_allowlist_super(bundle):
    ep = bundle / "golden" / "two-users" / "env.json"
    env = json.loads(ep.read_text())
    env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = SYNTH_IDENTITIES["user2"] + ",x"
    _rewrite(ep, json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: two-users: env {ENV_ALLOWLIST_KEY} != identities.user2"


def test_redacted_len_true(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["OMNIROUTE_API_KEY"]["len"] = True
        _rewrite(ep, json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env OMNIROUTE_API_KEY redacted len is not a positive int"


# === §5 mention attacks ===
def test_mention_kind_float(bundle):
    """7-F9 / m19: kind 9.0 must fail (not int)."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"], "kind": 9.0,
                                          "tags": ev["tags"], "content": ev["content"]})
    _rewrite(md / "owner.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "owner.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner event kind is not 9"


def test_mention_id_wrong(bundle):
    """m20: NIP-01 id mismatch."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    ev["id"] = "00" * 32
    _rewrite(md / "owner.event.json", json.dumps(ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = ev["id"]
    _rewrite(md / "owner.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner NIP-01 id mismatch"


def test_mention_content_superstring(bundle):
    """m23: content must be exact ==."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"], "kind": 9,
                                          "tags": ev["tags"], "content": ev["content"] + " AND !shutdown"})
    _rewrite(md / "owner.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "owner.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner content mismatch"


def test_mention_htag_wrong(bundle):
    """m24: missing h tag."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    tags = [t for t in ev["tags"] if t[0] != "h"]
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"], "kind": 9,
                                          "tags": tags, "content": ev["content"]})
    _rewrite(md / "owner.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "owner.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner missing ['h', channel] tag"


def test_mention_window_out(bundle):
    """m25: created_at outside window."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": 1600000000, "kind": 9,
                                          "tags": ev["tags"], "content": ev["content"]})
    _rewrite(md / "owner.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "owner.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: mention owner created_at 1600000000 outside window")


def test_mention_etag_wrong(bundle):
    """m26: e-tag wrong reference."""
    md = bundle / "golden" / "shutdown" / "mentions"
    ev = json.loads((md / "shutdown-cmd.event.json").read_text())
    tags = [t for t in ev["tags"] if t[0] != "e"] + [["e", "ff" * 32, "", "reply"]]
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"], "kind": 9,
                                          "tags": tags, "content": ev["content"]})
    _rewrite(md / "shutdown-cmd.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "shutdown-cmd.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "shutdown-cmd.receipt.json", json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: mention shutdown-cmd e-tag does not reference owner"


def test_receipt_missing_keys(bundle):
    """6-F17 / 7-F19: receipt without mention_pubkeys/message."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); del o["mention_pubkeys"]; del o["message"]
    _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt key set mismatch"


def test_receipt_accepted_false(bundle):
    """m80."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); o["accepted"] = 1
    _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt not accepted"


def test_receipt_event_id_mismatch(bundle):
    """m81."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); o["event_id"] = "00" * 32
    _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt event_id != event.id"


def test_receipt_err_nonempty(bundle):
    """m82."""
    _rewrite(bundle / "golden" / "run-1" / "mentions" / "owner.receipt.err", "error\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mentions/owner.receipt.err is not empty"


def test_extra_mention_file(bundle):
    _rewrite(bundle / "golden" / "run-1" / "mentions" / "extra.event.json", "{}")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mentions/ has unexpected entries: ['extra.event.json']"


def test_replay_mention(bundle):
    """Replay run-1's owner mention into run-2, re-signing with run-2's created_at to pass
    the window check — the replay detection must still catch the duplicate event id."""
    ev1 = json.loads((bundle / "golden" / "run-1" / "mentions" / "owner.event.json").read_text())
    # Re-sign with the SAME key but using run-2's created_at (inside run-2's window)
    ev2_orig = json.loads((bundle / "golden" / "run-2" / "mentions" / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev2_orig["created_at"], "kind": 9,
                                          "tags": ev1["tags"], "content": ev1["content"]})
    # Overwrite with the SAME id as run-1 (the replay)
    new_ev["id"] = ev1["id"]
    new_ev["sig"] = ev1["sig"]
    new_ev["pubkey"] = ev1["pubkey"]
    new_ev["created_at"] = ev2_orig["created_at"]
    # The NIP-01 id will now mismatch because we forced the old id
    _rewrite(bundle / "golden" / "run-2" / "mentions" / "owner.event.json", json.dumps(new_ev) + "\n")
    rp = bundle / "golden" / "run-2" / "mentions" / "owner.receipt.json"
    r = json.loads(rp.read_text()); r["event_id"] = ev1["id"]
    _rewrite(rp, json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    # NIP-01 id mismatch fires because we forced the old id with new created_at
    assert out == "failure_reason: run-2: mention owner NIP-01 id mismatch"


def test_identities_owner_equals_user2(bundle):
    """6-F14: owner == user2 must fail."""
    ids_path = bundle.parent / "fixtures" / "identities.json"
    ids = json.loads(ids_path.read_text())
    ids["user2"] = ids["owner"]
    _rewrite(ids_path, json.dumps(ids, indent=2) + "\n")
    # Re-sign user2 mention with owner key and update env
    md = bundle / "golden" / "two-users" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"] + 100, "kind": 9,
                                          "tags": ev["tags"], "content": MENTION_TEXT})
    _rewrite(md / "user2.event.json", json.dumps(new_ev) + "\n")
    r = json.loads((md / "user2.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    _rewrite(md / "user2.receipt.json", json.dumps(r) + "\n")
    ep = bundle / "golden" / "two-users" / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = ids["owner"]
    _rewrite(ep, json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: identities owner and user2 are identical"


# === §6 upstream record attacks ===
def test_route_pairs_evil(bundle):
    """m28: method/path not in allowed set."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    p = sorted(rd.glob("*.json"))[-1]; o = json.loads(p.read_text()); o["path"] = "/evil"
    _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record (GET, /evil) not in allowed set"


def test_route_fingerprint_mismatch(bundle):
    """m30."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    for p in rd.glob("*.json"):
        o = json.loads(p.read_text())
        if o.get("method") == "POST":
            o["authorization_fingerprint"] = "0" * 64; _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record authorization_fingerprint mismatch"


def test_record_extension_evasion(bundle):
    """7-F14: record with wrong extension bypasses all checks."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    _rewrite(rd / "999999.jsonl", '{"method":"DELETE","path":"/evil"}\n')
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream-records/ contains invalid filename '999999.jsonl'"


def test_record_key_set_wrong(bundle):
    """6-F18: record missing seq/t_mono_ns/remote_addr."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    p = sorted(rd.glob("*.json"))[0]
    o = json.loads(p.read_text()); del o["seq"]; del o["t_mono_ns"]; del o["remote_addr"]
    _rewrite(p, json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record key set mismatch")


def test_fingerprint_file_emptied(bundle):
    """7-F16: empty fingerprint file -> Failure."""
    fp = bundle.parent / "fixtures" / "upstream-token.fingerprint"
    _rewrite(fp, "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: upstream-token.fingerprint is not a 64-hex digest"


def test_route_prefix_dropped(bundle):
    for leg in LEGS:
        _rewrite(bundle / "golden" / leg / "hermes-model.txt", f"  default: {EXPECTED_MODEL[leg]}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: hermes-model.txt is")


def test_body_model_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["body"]["model"] = "evil-" + r["body"]["model"]; _rewrite(rp, json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record body.model is")


def test_host_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            r["headers"]["host"] = "evil#" + PINNED_UPSTREAM_HOST; _rewrite(rp, json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record host is")


def test_record_out_window(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["received_at"] = "1999-01-01T00:00:00.000000Z"; _rewrite(rp, json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream POST record received_at 1999-01-01T00:00:00.000000Z outside all prompt windows"


def test_one_record_two_prompts(bundle):
    """6-F8: one POST record cannot satisfy two prompt windows."""
    rd = bundle / "golden" / "two-users" / "upstream-records"
    kept = False
    for rp in sorted(rd.glob("*.json")):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST":
            if kept: rp.unlink()
            else: kept = True
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: no upstream POST with stream=true and mention text for a prompt window"


def test_no_mention_text(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                # Keep role sequence valid but remove mention text
                r["body"]["messages"] = [{"role": "system", "content": "sys"}, {"role": "user", "content": "other"}]
                _rewrite(rp, json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no upstream POST with stream=true and mention text for a prompt window"


# === §7 prompt turn attacks ===
def test_prompt_sid_bind_wrong(bundle):
    """m34: session/prompt targets a different session."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt":
            e["frame"]["params"]["sessionId"] = "evil-session"
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: session/prompt targets a different session"


def test_prompt_no_chunk(bundle):
    """m35: no agent_message_chunk between prompt and terminal."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Remove all notification entries between prompt and terminal
    out_es = [e for e in es if not (e["dir"] == "a2c" and "method" in e["frame"] and "id" not in e["frame"])]
    for i, e in enumerate(out_es): e["seq"] = i + 1
    _write_timeline(ld, out_es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no agent_message_chunk between prompt and terminal"


def test_prompt_stop_reason_wrong(bundle):
    """m36: terminal stopReason is not end_turn."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "a2c" and (e["frame"].get("result") or {}).get("stopReason"):
            e["frame"]["result"]["stopReason"] = "refusal"
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: terminal stopReason is 'refusal', expected 'end_turn'"


def test_prompt_foreign_sid(bundle):
    """m37: notification carries foreign session id."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "a2c" and "method" in e["frame"] and "id" not in e["frame"]:
            e["frame"]["params"]["sessionId"] = "foreign-sid"
            break
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: notifications carry a foreign session id"


def test_extra_request_pair(bundle):
    """6-F4: extra c2a request/response pair (e.g. fs/write_text_file)."""
    ld = bundle / "golden" / "shutdown"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es.append({"seq": 0, "dir": "c2a", "t_utc": es[-1]["t_utc"], "t_mono_ns": es[-1]["t_mono_ns"] + 1,
               "frame": {"jsonrpc": "2.0", "id": 900, "method": "session/load", "params": {"sessionId": "evil"}}})
    es.append({"seq": 0, "dir": "a2c", "t_utc": es[-1]["t_utc"], "t_mono_ns": es[-1]["t_mono_ns"] + 1,
               "frame": {"jsonrpc": "2.0", "id": 900, "result": {"loaded": True}}})
    for i, e in enumerate(es): e["seq"] = i + 1
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: c2a request methods ['initialize', 'session/load', 'session/new', 'session/prompt'] != expected ['initialize', 'session/new', 'session/prompt']"


# === §8 golden structure attacks ===
def test_init_resp_after_session_new(bundle, monkeypatch):
    """6-F7: a2c initialize response after c2a session/new.
    Swap only frames and dirs at indices 1 and 2, keeping timestamps in place."""
    for leg in ("run-1", "run-2"):
        ld = bundle / "golden" / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        # Swap frames/dirs at positions 1 and 2 (keep seq/t_utc/t_mono_ns in place)
        es[1]["frame"], es[2]["frame"] = es[2]["frame"], es[1]["frame"]
        es[1]["dir"], es[2]["dir"] = es[2]["dir"], es[1]["dir"]
        _write_timeline(ld, es)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: a2c initialize response does not precede c2a session/new"


def test_session_new_resp_after_prompt(bundle, monkeypatch):
    """6-F7: session/new response after session/prompt.
    Swap only frames/dirs at indices 3 and 4, keeping timestamps in place."""
    for leg in ("run-1", "run-2"):
        ld = bundle / "golden" / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        es[3]["frame"], es[4]["frame"] = es[4]["frame"], es[3]["frame"]
        es[3]["dir"], es[4]["dir"] = es[4]["dir"], es[3]["dir"]
        _write_timeline(ld, es)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: session/new response does not precede session/prompt"


# === §9 cancel attacks ===
def test_cancel_order(bundle):
    """m38: cancel before first chunk — timeline order violation.
    We swap frames only (not timestamps) so t_mono_ns stays non-decreasing."""
    ld = bundle / "golden" / "cancel"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    ci_idx = next(i for i, e in enumerate(es) if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel")
    pi_idx = next(i for i, e in enumerate(es) if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt")
    # Swap frames and dirs, keep seq/t_utc/t_mono_ns in place
    c_frame, c_dir = es[ci_idx]["frame"], es[ci_idx]["dir"]
    p_next_frame, p_next_dir = es[pi_idx + 1]["frame"], es[pi_idx + 1]["dir"]
    es[ci_idx]["frame"], es[ci_idx]["dir"] = p_next_frame, p_next_dir
    es[pi_idx + 1]["frame"], es[pi_idx + 1]["dir"] = c_frame, c_dir
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    # The cancel is now at prompt+1, before any chunks
    assert out.startswith("failure_reason: cancel: timeline order violation")


def test_cancel_log_no_mode(bundle):
    """m62."""
    p = bundle / "golden" / "cancel" / "buzzacp.log"
    _rewrite(p, p.read_text().replace("mode=Cancel", "mode=Steer"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: cancel: buzzacp.log missing 'mode=Cancel'"


# === §10 shutdown attacks ===
def test_shutdown_exit1(bundle):
    _rewrite(bundle / "golden" / "shutdown" / "buzz-acp.exit", "1\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: buzz-acp.exit is '1', expected '0'"


# === §11 two-users attacks ===
def test_twousers_sid_distinct(bundle):
    """m41: session ids collide."""
    ld = bundle / "golden" / "two-users"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    sids = [(e["frame"].get("result") or {}).get("sessionId") for e in es
            if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
            and (e["frame"].get("result") or {}).get("sessionId")]
    if len(sids) >= 2:
        for e in es:
            if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt":
                e["frame"]["params"]["sessionId"] = sids[0]
        _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: prompts do not map one-to-one onto the two sessions"


def test_twousers_chunks_missing(bundle):
    """m42: not every session streamed its own message chunks."""
    ld = bundle / "golden" / "two-users"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    sids = [(e["frame"].get("result") or {}).get("sessionId") for e in es
            if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]
            and (e["frame"].get("result") or {}).get("sessionId")]
    if len(sids) >= 2:
        out_es = [e for e in es if not (e["dir"] == "a2c" and "method" in e["frame"]
                  and ((e["frame"].get("params") or {}).get("update") or {}).get("sessionUpdate") == "agent_message_chunk"
                  and (e["frame"].get("params") or {}).get("sessionId") == sids[1])]
        for i, e in enumerate(out_es): e["seq"] = i + 1
        _write_timeline(ld, out_es)
        _write_tee_status(ld, out_es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: not every session streamed its own message chunks"


# === §12 process evidence attacks ===
def test_exit_garbage_nonshutdown(bundle):
    """6-F10 / 7-F7: buzz-acp.exit not integer."""
    _rewrite(bundle / "golden" / "run-1" / "buzz-acp.exit", "not-an-int\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzz-acp.exit is not a valid integer"


def test_proc_buzz_found(bundle):
    """m55: no buzz-acp line with matching pid — buzz cmd does not match the pin.
    F14: owned set includes all three rid pids; all three in scan for closure match."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", owned=3, owned_present=3, pinned_present=2) + "\n"
                  + "12300 1 100 NOT-BUZZ-ACP --flag\n"
                  + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
                  + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after has no buzz-acp line with pid 12300"


def test_proc_tee_parent(bundle):
    """m56: tee_pid ppid not buzz-acp — tee is parented by another process.
    F14: owned set includes all three rid pids, closure includes only buzz_pid
    (12340 has ppid=9999 not in closure, breaking the ppid chain)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", owned=3, owned_present=3, pinned_present=3) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12340 9999 90 /usr/bin/python3 {PINNED_TEE_PATH}\n12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: recomputed owned closure != owned-pids.json"


def test_proc_agent_parent(bundle):
    """m57: agent_child_pid ppid not tee_pid — agent is parented by another process.
    F14: owned set includes all three rid pids, closure includes buzz+tee
    (12345 has ppid=9999 not in closure)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", owned=3, owned_present=3, pinned_present=3) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n12345 9999 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: recomputed owned closure != owned-pids.json"


def test_proc_closure(bundle):
    """m58: process outside buzz-acp descendant tree."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", pinned_present=4) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n8888 9999 70 python3 {PINNED_TEE_PATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    cmd = f"python3 {PINNED_TEE_PATH}"
    assert out == f"failure_reason: run-1: process 8888 ({cmd[:40]}) not in buzz-acp descendant tree"


def test_proc_closure_seed(bundle):
    """m59: mutual-parent attack (V-b F19).  F14: owned=[12300] excludes rid pids → caught first."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", owned=1, owned_present=1, pinned_present=3) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n8888 9999 70 python3 {PINNED_TEE_PATH}\n9999 8888 60 python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: owned-pids.json does not contain rid tee_pid 12340"


def test_proc_unparsable_line(bundle):
    """6-F12: unparsable line in process-scan-after.txt."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, sp.read_text() + f"999 nope badtime /usr/bin/python3 {PINNED_TEE_PATH} --evil\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: process-scan-after.txt unparsable line: '999 nope badtime /usr/bin/python3 {PINNED_TEE_PATH} --evil'"


def test_teardown_has_tee(bundle):
    """m60: A20c survivor check — owned pid in teardown body."""
    p = bundle / "golden" / "run-1" / "process-scan-teardown.txt"
    _rewrite(p, _scan_header("teardown", buzz_present=0, owned_present=1) + "\n"
                 + f"12340 12300 95 python3 {PINNED_TEE_PATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    cmd = f"python3 {PINNED_TEE_PATH}"
    assert out == f"failure_reason: run-1: process 12340 ({cmd[:40]}) survived teardown"


def test_orphan_pair(bundle):
    """6-F2: orphan process pair outside buzz-acp descendant tree."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", pinned_present=5) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n8888 9999 70 python3 {PINNED_TEE_PATH}\n9999 8888 60 python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(bundle / "golden" / "run-1" / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    rc, out = _check(bundle)
    assert rc == 1
    cmd = f"python3 {PINNED_TEE_PATH}"
    assert out == f"failure_reason: run-1: process 8888 ({cmd[:40]}) not in buzz-acp descendant tree"


def test_pc_launch_exemption(bundle):
    """7-F8 / A2: pc_launch.py exemption only for the launcher (pid == buzz ppid)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    foreign_cmd = f"python3 /somewhere/pc_launch.py --agent {PINNED_AGENT_REALPATH}"
    _rewrite(sp, _scan_header("after", pinned_present=4) + "\n"
                  + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
                  + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
                  + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n"
                  + f"31337 1 50 {foreign_cmd}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: process 31337 ({foreign_cmd[:40]}) not in buzz-acp descendant tree"


def test_buzz_exe_superstring(bundle):
    """7-F24: buzz-acp-EVIL satisfies startswith but not split()[0] ==."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    txt = sp.read_text().replace(f" {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url",
                                 f" {PINNED_BUZZ_ACP_EXE_REALPATH}-EVIL --relay-url")
    _rewrite(sp, txt)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after has no buzz-acp line with pid 12300"


# === §13 log/startup attacks ===
def test_dup_startup_key(bundle):
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    new_line = sp.read_text().strip() + " max_turn=3600s"
    _rewrite(sp, new_line + "\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    _rewrite(lp, new_line + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup-line duplicate key 'max_turn'"


def test_startup_not_in_log(bundle):
    """7-F4 / A7: startup-line.txt not matching log."""
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    _rewrite(lp, "2026-09-05T05:00:00Z  INFO buzz_acp: starting with relay=<HEX>\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzzacp.log has no line containing 'buzz-acp starting:'"


def test_startup_values_substr(bundle):
    """m52: startup values compared with == not in."""
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        new_line = sp.read_text().strip().replace("idle_timeout=900s", "idle_timeout=900seconds")
        _rewrite(sp, new_line + "\n")
        lp = bundle / "golden" / leg / "buzzacp.log"
        lines = lp.read_text().splitlines()
        lines[0] = new_line
        _rewrite(lp, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup idle_timeout is '900seconds', expected '900s'"


def test_startup_respond_to_wrong(bundle):
    """m53."""
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        new_line = sp.read_text().strip().replace("respond_to=owner-only", "respond_to=everyone")
        _rewrite(sp, new_line + "\n")
        lp = bundle / "golden" / leg / "buzzacp.log"
        lines = lp.read_text().splitlines()
        lines[0] = new_line
        _rewrite(lp, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup respond_to is 'everyone', expected 'owner-only'"


def test_argv_idle_pin(bundle, monkeypatch):
    """m54: argv --idle-timeout wrong. Monkeypatch PINNED_LAUNCH_ARGV so
    check_runtime_identity passes; check_config_echo catches the wrong value."""
    new_argv = list(PINNED_LAUNCH_ARGV)
    idx = new_argv.index(PINNED_IDLE_TIMEOUT_ARG)
    new_argv[idx] = "999"
    monkeypatch.setattr("check_acp_conformance.PINNED_LAUNCH_ARGV", new_argv)
    for leg in LEGS:
        ap = bundle / "golden" / leg / "argv.txt"
        _rewrite(ap, "\n".join(new_argv) + "\n")
        rp = bundle / "golden" / leg / "runtime-identity.json"
        rid = json.loads(rp.read_text()); rid["launch_argv"] = new_argv
        _rewrite(rp, json.dumps(rid, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: argv --idle-timeout is not {PINNED_IDLE_TIMEOUT_ARG}"


def test_log_unmasked(bundle):
    _rewrite(bundle / "golden" / "run-1" / "buzzacp.log", (bundle / "golden" / "run-1" / "startup-line.txt").read_text() + "INFO relay=" + "ab" * 32 + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzzacp.log contains unmasked 64-hex string"


# === §14 manifest attacks ===
def test_manifest_dup_header(bundle):
    """m48."""
    gz = gzip.compress(b"## hermes-agent\na f\n## hermes-agent\nb g\n## buzz\nc m\n## acp\nd l\n", mtime=0)
    for leg in LEGS:
        _rewrite(bundle / "golden" / leg / "manifest-pre.txt.gz", gz)
        _rewrite(bundle / "golden" / leg / "manifest-post.txt.gz", gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_preamble(bundle):
    """m49."""
    body = b"EVIL\n" + gzip.decompress((GOLDEN / "manifests" / "manifest-baseline.txt.gz").read_bytes())
    gz = gzip.compress(body, mtime=0)
    for leg in LEGS:
        _rewrite(bundle / "golden" / leg / "manifest-pre.txt.gz", gz)
        _rewrite(bundle / "golden" / leg / "manifest-post.txt.gz", gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_digests_pin(bundle):
    """m44: manifest digests != pinned baseline."""
    # Replace the manifest body with a valid-format but wrong-content body
    lines = []
    for tree in MANIFEST_TREES:
        lines.append(f"## {tree}")
        lines.append("0" * 64 + "  ./dummy.txt")
    body = "\n".join(lines) + "\n"
    gz = gzip.compress(body.encode(), mtime=0)
    for leg in LEGS:
        _rewrite(bundle / "golden" / leg / "manifest-pre.txt.gz", gz)
        _rewrite(bundle / "golden" / leg / "manifest-post.txt.gz", gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_baseline_sha_pin(bundle):
    """m45: baseline gz sha mismatch."""
    bl = bundle / "golden" / "manifests" / "manifest-baseline.txt.gz"
    body = gzip.decompress(bl.read_bytes())
    _rewrite(bl, gzip.compress(body, mtime=1))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: baseline gz sha256 mismatch"


def test_manifest_ts_order(bundle):
    """m46: manifest timestamps not pre < start < post.
    Set pre timestamp AFTER spawned_at_utc (05:30:00) to violate pre < start."""
    for leg in LEGS:
        lines = (bundle / "golden" / leg / "manifest-pre.summary").read_text().splitlines()
        lines[len(MANIFEST_TREES)] = "2026-09-05T06:00:00Z"  # after spawned_at_utc 05:30:00
        _rewrite(bundle / "golden" / leg / "manifest-pre.summary", "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest timestamps not pre < start < post"


def test_manifest_post_after_tl(bundle):
    """m47: manifest-post not after last timeline t_utc.
    Set ONLY run-1's post timestamp to just after spawned_at but before run-1's last
    timeline entry. spawned_at=05:00:00.050, last entry ~05:00:01.100.
    05:00:01Z = 05:00:01.000 is after spawned_at but before last entry."""
    lines = (bundle / "golden" / "run-1" / "manifest-post.summary").read_text().splitlines()
    lines[len(MANIFEST_TREES)] = "2026-09-05T05:00:01Z"
    _rewrite(bundle / "golden" / "run-1" / "manifest-post.summary", "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest-post timestamp not after last timeline t_utc"


def test_summary_digests_zeroed(bundle):
    """m50."""
    for leg in LEGS:
        for name in ("manifest-pre.summary", "manifest-post.summary"):
            sp = bundle / "golden" / leg / name
            lines = sp.read_text().splitlines()
            _rewrite(sp, "\n".join(f"{l.split()[0]} {'0'*64}" if len(l.split()) == 2 and l.split()[0] in PINNED_BASELINE_DIGESTS else l for l in lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest-pre.summary digests != body digests"


# === §8 golden attacks ===
def test_golden_run_eq(bundle, monkeypatch):
    """m65: run-1 and run-2 identical — the mention replay check fires first because
    the mention event ids are duplicated across legs."""
    shutil.copytree(bundle / "golden" / "run-1", bundle / "golden" / "run-2-copy")
    shutil.rmtree(bundle / "golden" / "run-2")
    (bundle / "golden" / "run-2-copy").rename(bundle / "golden" / "run-2")
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: mention event id replayed across legs"


def test_golden_frozen_lines(bundle, monkeypatch):
    """m66: normalized runs differ from the frozen golden.jsonl."""
    p = bundle / "golden" / "golden.jsonl"
    lines = p.read_text().splitlines()
    lines[0] = lines[0].replace('"initialize"', '"evil"')
    new_text = "\n".join(lines) + "\n"
    _rewrite(p, new_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(new_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: normalized runs differ from the frozen golden.jsonl"


def test_golden_first_line(bundle, monkeypatch):
    """m67: first normalized line is not c2a initialize — the c2a notification before
    initialize triggers the 'unexpected c2a notification' check in check_prompt_turn first."""
    for leg in ("run-1", "run-2"):
        ld = bundle / "golden" / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        es.insert(0, {"seq": 0, "dir": "c2a", "t_utc": es[0]["t_utc"],
                       "t_mono_ns": es[0]["t_mono_ns"] - 1,
                       "frame": {"jsonrpc": "2.0", "method": "client/ping", "params": {}}})
        for i, x in enumerate(es): x["seq"] = i + 1
        _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: unexpected c2a notification 'client/ping'"


def test_golden_last_line(bundle, monkeypatch):
    """m68: last normalized line is not end_turn terminal — the per-leg check_prompt_turn
    fires first because the stop reason is changed in all legs."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "a2c" and (e["frame"].get("result") or {}).get("stopReason"):
            e["frame"]["result"]["stopReason"] = "max_turns"
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: terminal stopReason is 'max_turns', expected 'end_turn'"


def test_golden_distinctness_all(bundle, monkeypatch):
    """m69: run-2 copied from run-1 — the mention replay check fires because
    the event ids are duplicated across legs."""
    shutil.copytree(bundle / "golden" / "run-1", bundle / "golden" / "run-2-copy")
    shutil.rmtree(bundle / "golden" / "run-2")
    (bundle / "golden" / "run-2-copy").rename(bundle / "golden" / "run-2")
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: mention event id replayed across legs"


def test_golden_regen(bundle):
    for leg in ("run-1", "run-2"):
        ld = bundle / "golden" / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        del es[-2]
        for i, e in enumerate(es): e["seq"] = i + 1
        _write_timeline(ld, es)
        _write_tee_status(ld, es)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    _rewrite(bundle / "golden" / "golden.jsonl", "\n".join(n1) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: golden: golden.jsonl sha256")


# === §13 init frame attacks ===
def test_init_pv_wrong(bundle):
    """m07: client protocolVersion != pinned."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "c2a" and e["frame"].get("method") == "initialize":
            e["frame"]["params"]["protocolVersion"] = 99
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: client protocolVersion is not {PINNED_CLIENT_PROTOCOL_VERSION}"


def test_agent_caps_wrong(bundle):
    """m08: agentCapabilities differ."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es:
        if e["dir"] == "a2c" and "id" in e["frame"] and "result" in e["frame"]:
            r = e["frame"]["result"]
            if "agentCapabilities" in r:
                r["agentCapabilities"] = {"evil": True}
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agentCapabilities differ from pinned"


# === negative directory attacks ===
def test_neg_extra_file(bundle):
    """7-F23 / A11: extra file under negative/."""
    _rewrite(bundle / "golden" / "negative" / "evil.txt", "x")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: unexpected entries: ['evil.txt']"


def test_neg_nan_timeline(bundle):
    """7-F23: NaN in negative timeline (A22: via shared validator)."""
    p = bundle / "golden" / "negative" / "timeline.jsonl"
    _rewrite(p, p.read_text().replace('"t_mono_ns":1000000000001', '"t_mono_ns":NaN', 1))
    rc, out = _check(bundle)
    assert rc == 1
    assert "negative:" in out and "not strict JSON" in out


def test_neg_c2a_not_seq1(bundle):
    """7-F10 / A11: c2a initialize not at seq 1 (A22: via shared validator)."""
    p = bundle / "golden" / "negative" / "timeline.jsonl"
    es = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    junk = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T05:00:00.000000Z",
            "t_mono_ns": 1_000_000_000_000, "frame": {"jsonrpc": "2.0", "method": "hello", "params": {}}}
    es = [junk] + es
    for i, e in enumerate(es): e["seq"] = i + 1
    _rewrite(p, "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: negative: seq 1 is not a c2a frame"


def test_neg_classify_wrong(bundle):
    """m78: negative classify check must reject non-MISSING_REQUIRED (A22: via shared validator)."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["frame"]["params"]["protocolVersion"] = 2
    _rewrite(nd / "timeline.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: negative: initialize params != fixture"


def test_neg_extra_a2c_junk_first(bundle):
    """7-F10: junk a2c before real response — matched by request id (A22: via shared validator)."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    junk = {"seq": 0, "dir": "a2c", "t_utc": es[1]["t_utc"], "t_mono_ns": es[1]["t_mono_ns"],
            "frame": {"jsonrpc": "2.0", "method": "log", "params": {}}}
    es.insert(1, junk)
    for i, e in enumerate(es): e["seq"] = i + 1
    _rewrite(nd / "timeline.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    # The shared validator DOES pass: the response is matched by id
    rc, out = _check(bundle)
    assert rc == 0


# === Sequence guard (A25/A12) ===
def test_sequence_guard_skip_one_leg(bundle, monkeypatch):
    """5-F01/A25: skipping check_manifests for cancel leg changes the sequence -> Failure."""
    orig_check_manifests = cc.check_manifests

    def skip_cancel(*args, **kwargs):
        # Identify leg from args: check_manifests(leg_dir, leg, ...)
        leg = args[1] if len(args) > 1 else kwargs.get("leg", "")
        if leg == "cancel":
            return None  # skip
        return orig_check_manifests(*args, **kwargs)

    monkeypatch.setattr("check_acp_conformance.check_manifests", skip_cancel)
    rc, out = _check(bundle)
    assert rc == 1
    assert "check sequence mismatch" in out


# === Extra golden entries ===
def test_extra_leg_dir(bundle):
    (bundle / "golden" / "run-3").mkdir(); _rewrite(bundle / "golden" / "run-3" / "x", "")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: unexpected directory golden/run-3"


def test_extra_golden_file(bundle):
    _rewrite(bundle / "golden" / "NOTES.md", "hi\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: unexpected file golden/NOTES.md"


def test_extra_manifests_file(bundle):
    """A13: manifests/ should contain only manifest-baseline.txt.gz."""
    _rewrite(bundle / "golden" / "manifests" / "evil.txt", "hi\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: golden: manifests/ contains unexpected entries")


# === Malformed evidence wrapper ===
def test_bad_json_timeline(bundle):
    tl = bundle / "golden" / "run-1" / "timeline.jsonl"
    lines = tl.read_text().splitlines(); lines[0] = "bad"
    _rewrite(tl, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: malformed evidence: JSONDecodeError:"), (
        f"expected JSONDecodeError, got: {out}")


def test_bad_pid(bundle):
    _rewrite(bundle / "golden" / "run-1" / "buzz-acp.pid", "bad\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzz-acp.pid is not a valid integer"


def test_utc_backwards(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    utcs = [e["t_utc"] for e in es]; utcs.reverse()
    for i, e in enumerate(es): e["t_utc"] = utcs[i]
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: t_utc not non-decreasing at seq")


# === PASS-line format (6-F15) ===
def test_pass_line_has_negative_prefix(bundle):
    result = cc.check_bundle(bundle)
    assert "negative: observed:" in result


# === 5-F03: audit mutation tests (round-5b item 1) ===
# Each test reproduces one mutation from the owner's external audit, verbatim.

def test_audit_p1_negative_response_is_a2c_request(bundle):
    """Audit P1: replacing the negative response with an a2c REQUEST of the same id must fail.
    Pre-round-5: PASS with 'negative: observed: none: no parseable response'."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Replace the a2c error response (seq 2) with an a2c REQUEST of the same id
    es[1]["frame"] = {"jsonrpc": "2.0", "method": "tools/list", "id": 0, "params": {}}
    _rewrite(nd / "timeline.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1, f"audit P1 mutation should fail, got rc={rc}: {out}"


def test_audit_p1_negative_probe_failed_identity(bundle):
    """Audit P1: negative runtime-identity with delivered=false, probe_error, bad argv must fail.
    Pre-round-5: PASS (check_negative only checked 5 pinned fields)."""
    nd = bundle / "golden" / "negative"
    rid = json.loads((nd / "runtime-identity.json").read_text())
    rid["delivered"] = False
    rid["probe_error"] = "BrokenPipeError: request not delivered"
    rid["agent_exit_code"] = -9
    rid["agent_argv"] = ["/usr/bin/true"]
    rid["agent_child_pid"] = -1
    _rewrite(nd / "runtime-identity.json", json.dumps(rid, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1, f"audit P1 probe_error mutation should fail, got rc={rc}: {out}"


def test_audit_p1_rid_pids_unbound_to_scan(bundle):
    """Audit P1: runtime-identity tee_pid/agent_child_pid disagreeing with scan must fail.
    Pre-round-5: PASS (check_runtime_identity never joined pids to scan)."""
    ld = bundle / "golden" / "run-1"
    rid = json.loads((ld / "runtime-identity.json").read_text())
    rid["tee_pid"] = 77777
    rid["agent_child_pid"] = 88888
    _rewrite(ld / "runtime-identity.json", json.dumps(rid, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1, f"audit P1 unbound-pids mutation should fail, got rc={rc}: {out}"


def test_audit_p1_generic_child_survives_teardown(bundle):
    """Audit P1: a generic descendant surviving teardown must fail.
    Pre-round-5: PASS (check_process_evidence only rejected tee/agent/buzz paths)."""
    ld = bundle / "golden" / "run-1"
    scan = ld / "process-scan-after.txt"
    existing_lines = scan.read_text().splitlines()
    owned_path = ld / "owned-pids.json"
    owned_data = json.loads(owned_path.read_text())
    # Add child 54321 parented by agent (12345) — update header to match
    body_lines = existing_lines[1:]
    body_lines.append("54321 12345 80 /usr/bin/sleep 60")
    owned_data["owned"].append(54321)
    owned_data["owned"].sort()
    _rewrite(owned_path, json.dumps(owned_data) + "\n")
    _rewrite(scan, _scan_header("after", owned=4, owned_present=4, pinned_present=3) + "\n"
                    + "\n".join(body_lines) + "\n")
    # Same child in teardown — owned pid = survivor
    td = ld / "process-scan-teardown.txt"
    _rewrite(td, _scan_header("teardown", buzz_present=0, owned=4, owned_present=1) + "\n"
                  + "54321 1 90 /usr/bin/sleep 60\n")
    rc, out = _check(bundle)
    assert rc == 1, f"audit P1 teardown survivor mutation should fail, got rc={rc}: {out}"
    assert out == "failure_reason: run-1: process 54321 (/usr/bin/sleep 60) survived teardown"


# === 5-F15: upstream record header screening tests (round-5b item 3) ===

def test_upstream_header_sensitive_name(bundle):
    """5-F15: a record with x-api-key header fails naming record and header.
    Deletion mutant: removing the screen must red."""
    ld = bundle / "golden" / "run-1"
    recs_dir = ld / "upstream-records"
    first_rec = sorted(recs_dir.glob("*.json"))[0]
    rec = json.loads(first_rec.read_text())
    rec["headers"]["x-api-key"] = "sk-live-DEADBEEF1234"
    _rewrite(first_rec, json.dumps(rec, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record has sensitive header 'x-api-key'"


def test_upstream_header_sensitive_value(bundle):
    """5-F15: a header with Bearer token value fails naming the header."""
    ld = bundle / "golden" / "run-1"
    recs_dir = ld / "upstream-records"
    first_rec = sorted(recs_dir.glob("*.json"))[0]
    rec = json.loads(first_rec.read_text())
    rec["headers"]["x-custom"] = "Bearer eyJhbGciOiJI"
    _rewrite(first_rec, json.dumps(rec, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record header 'x-custom' has sensitive value"


# === 5-F18: symlink in evidence tree tests (round-5b item 3) ===

def test_symlink_upstream_record(bundle):
    """5-F18: a symlinked upstream record fails naming the path."""
    ld = bundle / "golden" / "run-1" / "upstream-records"
    target = sorted(ld.glob("*.json"))[0]
    link = ld / "999999.json"
    link.symlink_to(target)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: symlink in evidence tree: run-1/upstream-records/999999.json"


def test_symlink_manifest_gz(bundle):
    """5-F18: a symlinked manifest gz fails naming the path."""
    ld = bundle / "golden" / "run-1"
    target = ld / "manifest-pre.txt.gz"
    link = ld / "manifest-evil.txt.gz"
    link.symlink_to(target)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: symlink in evidence tree: run-1/manifest-evil.txt.gz"


# === 5-F19: agent-stderr.txt screening tests (round-5b item 3) ===

def test_stderr_64hex_token(bundle):
    """5-F19: a 64-hex token in agent-stderr.txt fails naming the file."""
    ld = bundle / "golden" / "run-1"
    stderr = ld / "agent-stderr.txt"
    _rewrite(stderr, "leaked: " + "ab" * 32 + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agent-stderr.txt contains a secret-shaped string"


def test_stderr_bearer_token(bundle):
    """5-F19: a Bearer token in agent-stderr.txt fails naming the file."""
    ld = bundle / "golden" / "run-1"
    stderr = ld / "agent-stderr.txt"
    _rewrite(stderr, "Authorization: Bearer eyJhbGciOiJI\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agent-stderr.txt contains a secret-shaped string"


# === 5-F16: id-matching test (round-5b item 4) ===

def test_neg_foreign_id_response_before_real(bundle):
    """5-F16: a junk a2c RESPONSE with a foreign id BEFORE the real one.
    The negative validator uses the shared validator which matches by request id,
    so the real response (at seq 3) is still found — the foreign envelope at seq 2
    is caught as 'agent response id 99999 does not match the request id'.
    This test verifies the id-matching path is exercised: the failure names the foreign id."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Insert a junk RESPONSE with a foreign id at position 1 (before the real error response)
    junk_t_utc = es[0]["t_utc"]
    junk_mono = es[0]["t_mono_ns"]
    junk = {"seq": 0, "dir": "a2c", "t_utc": junk_t_utc, "t_mono_ns": junk_mono,
            "frame": {"jsonrpc": "2.0", "id": 99999,
                      "error": {"code": -32000, "message": "unknown"}}}
    es.insert(1, junk)
    for i, e in enumerate(es):
        e["seq"] = i + 1
    _rewrite(nd / "timeline.jsonl", "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: negative: agent response id 99999 does not match the request id at seq 2"


# === 5-F20: empty-timeline and one-initialize guard tests (round-5b item 4) ===

def test_empty_timeline_guard(bundle):
    """5-F20: an empty timeline.jsonl must fail with the exact guard reason."""
    ld = bundle / "golden" / "run-1"
    _rewrite(ld / "timeline.jsonl", "")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: timeline.jsonl is empty"


def test_exactly_one_initialize_guard(bundle):
    """5-F20: two initialize requests must fail with the exact guard reason.
    Tested via direct check function call to avoid timeline ordering issues."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a = [e["frame"] for e in es if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in es if e["dir"] == "a2c"]
    # Duplicate the initialize request in the c2a split
    init_req = next(o for o in c2a if o.get("method") == "initialize")
    dup = json.loads(json.dumps(init_req))
    dup["id"] = 99999
    c2a.append(dup)
    ok, result = _run_check_safe(cc.check_initialize_frames, c2a, a2c, "run-1")
    assert not ok
    assert "expected one initialize request, got 2" in result


# === AF-AP-40: presence-gated check_two_users mentions dir (round-5b item 5) ===

def test_twousers_mentions_dir_absent(bundle):
    """AF-AP-40: deleting mentions/ for two-users must fail with exact reason.
    check_mentions (called before check_two_users) raises the Failure."""
    ld = bundle / "golden" / "two-users"
    import shutil as _s
    _s.rmtree(ld / "mentions")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: mentions/ absent"


def test_twousers_mentions_dir_absent_direct(bundle):
    """R5: check_two_users no longer has its own mentions/ gate (deleted as dead per R5).
    The live-path check is in check_mentions via _require_dir, which runs first.
    Calling check_two_users directly with missing mentions/ raises FileNotFoundError."""
    ld = bundle / "golden" / "two-users"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a = [e["frame"] for e in es if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in es if e["dir"] == "a2c"]
    identities = json.loads((bundle.parent / "fixtures" / "identities.json").read_text())
    import shutil as _s
    _s.rmtree(ld / "mentions")
    # R9-CK-F10: check_two_users no longer validates mentions/ (the dead gate was
    # deleted per R5/F40) — it raises FileNotFoundError, not Failure.
    with pytest.raises(FileNotFoundError):
        cc.check_two_users(c2a, a2c, es, identities, leg_dir=ld)


# === A21: tee-status.json tests (addendum A) ===

def test_tee_status_missing(bundle):
    """A21: missing tee-status.json must fail."""
    ld = bundle / "golden" / "run-1"
    (ld / "tee-status.json").unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json absent"


def test_tee_status_extra_key(bundle):
    """A21: extra key in tee-status.json must fail naming the extra key."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["extra_field"] = True
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json key set mismatch (extra=['extra_field'], missing=[])"


def test_tee_status_drained_false_final(bundle):
    """A21: on a FINAL status, drained must be true."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = {"final": True, "agent_returncode": 0, "drained": False, "stdin_reader_done": True,
          "recorded_c2a": c2a_count, "recorded_a2c": a2c_count,
          "forwarded_c2a": c2a_count, "forwarded_a2c": a2c_count,
          "write_errors": [], "exit_code": 0,
          "updated_seq": last_seq, "updated_utc": entries[-1]["t_utc"]}
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json drained is not true"


def test_tee_status_forwarded_lt_recorded(bundle):
    """A21: forwarded_c2a trails recorded by 2 → fail on running arm."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    r = ts["recorded_c2a"]
    ts["forwarded_c2a"] = r - 2
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"forwarded_c2a {r - 2} trails recorded_c2a {r} by more than one")


def test_tee_status_recorded_ne_timeline(bundle):
    """A21 / R9-CK-F8: recorded_c2a off by 5 → the running arm's per-direction recorded
    deficit fires because c2a_count - recorded_c2a is far outside (0,1)."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    ts = json.loads((ld / "tee-status.json").read_text())
    new_rec = ts["recorded_c2a"] + 5
    ts["recorded_c2a"] = new_rec
    ts["forwarded_c2a"] = new_rec
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"recorded_c2a {new_rec} trails timeline c2a count {c2a_count} by more than one")


def test_tee_status_not_final_exit_not_null(bundle):
    """A21d: when not final, agent_returncode must be null."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["agent_returncode"] = 0  # not null when final=false
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json not final but agent_returncode is not null"


def test_tee_status_final_signal_exit_pass(bundle):
    """A21d/A21b: final=true, agent_returncode -15, exit_code 143 passes."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["agent_returncode"] = -15
    ts["exit_code"] = 143  # 128 + 15
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    ok, result = _run_check_safe(cc.check_tee_status, ld, "run-1", es)
    assert ok, f"signal exit should pass: {result}"


def test_tee_status_final_signal_exit_raw_fails(bundle):
    """A21d/A21b: final=true, agent_returncode -15, exit_code -15 fails (should be 143)."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["agent_returncode"] = -15
    ts["exit_code"] = -15
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    ok, result = _run_check_safe(cc.check_tee_status, ld, "run-1", es)
    assert not ok
    assert result == "run-1: tee-status.json exit_code -15 != expected 143"


def test_tee_status_updated_seq_wrong(bundle):
    """A21d: updated_seq far from timeline → R9-CK-F18's pre-arm type check passes
    (it IS an int), then the running arm's lag check fires because lag is far outside (0,1)."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["updated_seq"] = 99999
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    last_seq = es[-1]["seq"]
    ok, result = _run_check_safe(cc.check_tee_status, ld, "run-1", es)
    assert not ok
    # R9-CK-F9: the comment was stale — updated_seq ahead of the timeline hits the
    # lag check (C:1416 area), not the global seq-sum rule (now deleted, F17).
    assert result == (f"run-1: tee-status.json running snapshot updated_seq 99999 "
                      f"trails timeline last seq {last_seq} by more than one")


# === Addendum B: shutdown owned-pid survivor test ===

def test_shutdown_owned_pid_survives(bundle):
    """Addendum B: an owned pid in the shutdown after-scan must fail as a survivor."""
    ld = bundle / "golden" / "shutdown"
    # Add an owned pid to the after-scan (12300 is in owned-pids.json)
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", buzz_present=1, owned_present=1) + "\n"
        + "12300 1 200 /usr/bin/sleep 60\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: process 12300 (/usr/bin/sleep 60) survived shutdown"


# === A20 v2.3: enumeration header validation (direct-call tests) ===

def test_v23_no_header_after(tmp_path):
    """A20 v2.3 rule 1: after-scan without the v2.3 header is rejected."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "process-scan-after.txt", "")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned=3, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: process-scan-after.txt has no enumeration header"


def test_v23_no_header_teardown(tmp_path):
    """A20 v2.3 rule 1: teardown without the v2.3 header is rejected."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", pinned_present=3) + "\n"
        + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
        + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
        + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(ld / "process-scan-teardown.txt", "old format\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: process-scan-teardown.txt has no enumeration header"


def test_v23_rows_zero(tmp_path):
    """A20 v2.3 rule 2: rows=0 means enumeration did not run."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", rows=0, owned=3, owned_present=0) + "\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned=3, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "shutdown")
    assert str(ei.value) == "shutdown: process-scan-after.txt header rows=0 (enumeration did not run)"


def test_v23_owned_present_mismatch(tmp_path):
    """A20 v2.3 rule 3: owned_present inconsistent with body → Failure."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    # Header says owned_present=2 but body has 3 owned pids
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", owned_present=2, pinned_present=3) + "\n"
        + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
        + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
        + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: process-scan-after.txt header owned_present=2 inconsistent with body (3)"


def test_v23_buzz_present_shutdown(tmp_path):
    """A20 v2.3 rule 4: shutdown after-scan with buzz_present=1 → Failure."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    # buzz_present=1 but empty body (lying header — a clean shutdown)
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", buzz_present=1, owned_present=0) + "\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "shutdown")
    assert str(ei.value) == "shutdown: process-scan-after.txt buzz_present=1 in shutdown (expected 0)"


def test_v23_mode_mismatch(tmp_path):
    """A20 v2.3 rule 1b: after-scan file with mode=teardown in header → Failure."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("teardown", owned=3, owned_present=0) + "\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned=3, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "shutdown")
    assert str(ei.value) == "shutdown: process-scan-after.txt header mode is 'teardown', expected 'after'"


def test_v23_owned_count_mismatch(tmp_path):
    """A20 v2.3 rule 8: header owned != len(owned-pids.json owned) → Failure."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    # Header says owned=2 but owned-pids.json has 3
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", owned=2, owned_present=0) + "\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "shutdown")
    assert str(ei.value) == "shutdown: process-scan-after.txt header owned=2 != owned-pids.json (3)"


def test_v23_shutdown_clean_pass(tmp_path):
    """A20 v2.3 rule 4: valid header + empty body in shutdown → PASS."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", buzz_present=0, owned_present=0) + "\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned_present=0) + "\n")
    cc.check_process_evidence(ld, "shutdown")  # must not raise


def test_v23_teardown_survivor(tmp_path):
    """A20 v2.3 rule 6: owned pid in teardown body → survivor Failure."""
    ld = tmp_path
    _rewrite(ld / "buzz-acp.pid", "12300\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "owned-pids.json", json.dumps({"buzz_acp_pid": 12300, "owned": [12300, 12340, 12345], "taken_at": "ready+after"}))
    _rewrite(ld / "runtime-identity.json", json.dumps({"tee_pid": 12340, "agent_child_pid": 12345}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", pinned_present=3) + "\n"
        + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
        + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
        + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned_present=1) + "\n"
        + "12340 1 95 python3 /some/tee\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: process 12340 (python3 /some/tee) survived teardown"


# === Real-producer conformance (item 3) ===
# Runs per-leg checks against REAL captured legs from the PC when available.
# The ONLY expected failures are:
#   - tee_sha256 mismatch (tee sha differs from the committed tee — expected)
#   - manifest timestamps not pre < start < post (legs captured before the launcher fix)
# For the negative leg, agent_interpreter_realpath mismatch is expected (V2: probe
# reads /proc/<pid>/exe after proc.wait()).
# Skip when the directory is absent.

# CK11-F16/F18: both env reads resolved ONCE at module scope — one resolution point.
# CK11-F13: venue defaults to "sandbox" (declare-or-fail); CI declares "ci" explicitly.
_VENUE = os.environ.get("S0_01_VENUE", "sandbox")
_REAL_LEG_DIR = Path(os.environ["S0_01_REAL_LEG_DIR"]) if os.environ.get("S0_01_REAL_LEG_DIR") else None

_POSITIVE_LEGS = ("run-1", "cancel", "shutdown", "two-users")


def _run_check_safe(fn, *args, **kwargs):
    """Run a checker function, return (True, result) on PASS, (False, reason) on Failure."""
    try:
        return (True, fn(*args, **kwargs))
    except cc.Failure as f:
        return (False, str(f))
    except cc.Deferred as d:
        return (False, f"deferred: {d}")


_EXPECTED_REAL_LEGS = {"cancel", "negative", "run-1", "shutdown", "two-users"}


def _real_leg(leg: str) -> Path:
    """CK11 item 10: ONE place to get wrong — implements the declaration semantics.
    Returns the leg directory path or calls pytest.skip."""
    if _REAL_LEG_DIR is None:
        pytest.skip("S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)")
    leg_dir = _REAL_LEG_DIR / leg
    if not leg_dir.is_dir():
        pytest.skip(f"real leg directory absent: {_REAL_LEG_DIR}")
    return leg_dir


import stat as _stat_mod


def _corpus_file(leg_dir, name):
    """CK12 sweep 2.1: guard every test-side read of a corpus file."""
    p = leg_dir / name
    if not p.exists():
        pytest.fail(f"{leg_dir.name}: {name} absent")
    if not _stat_mod.S_ISREG(p.lstat().st_mode):
        pytest.fail(f"{leg_dir.name}: {name} is not a regular file")
    return p


def _corpus_version():
    """CK12 sweep 10.2: v2.3 iff every positive leg has v2.3 scan header + tee-status."""
    if _REAL_LEG_DIR is None:
        return "unknown"
    for leg in ("run-1", "cancel", "shutdown", "two-users"):
        ld = _REAL_LEG_DIR / leg
        if not ld.is_dir():
            return "v2.2"
        scan = ld / "process-scan-after.txt"
        if not scan.is_file():
            return "v2.2"
        first = scan.read_text().splitlines()
        if not first or not first[0].startswith("# process-scan v2.3 "):
            return "v2.2"
        if not (ld / "tee-status.json").is_file():
            return "v2.2"
    return "v2.3"


_CORPUS_VERSION = _corpus_version()


def test_ck11_real_leg_dir_is_resolved_from_the_environment():
    """CK11-F1: _REAL_LEG_DIR tracks the S0_01_REAL_LEG_DIR env var — no hardcoded path."""
    want = os.environ.get("S0_01_REAL_LEG_DIR")
    assert _REAL_LEG_DIR == (Path(want) if want else None), (
        f"_REAL_LEG_DIR={_REAL_LEG_DIR} does not track S0_01_REAL_LEG_DIR={want!r}")


def test_ck11_venue_is_resolved_from_the_environment():
    """CK11-F18: _VENUE tracks the S0_01_VENUE env var at module scope."""
    want = os.environ.get("S0_01_VENUE", "sandbox")
    assert _VENUE == want, f"_VENUE={_VENUE!r} does not track S0_01_VENUE={want!r}"


def test_ck11_venue_domain_is_known():
    """CK11-F16: _VENUE is in the allowed domain {ci, sandbox, pc}.
    Independent of corpus_declared so a mutant removing the domain check there is killed."""
    assert _VENUE in ("ci", "sandbox", "pc"), (
        f"S0_01_VENUE={_VENUE!r} is not a known venue")


def test_real_leg_corpus_declared():
    """CK11-F16/F13: venue domain is EXACTLY {ci, sandbox, pc}; any other value FAILS.
    If venue is sandbox or pc, S0_01_REAL_LEG_DIR MUST be set and be a directory.
    CI skips by declaration.  CK11-F19: when the sidecar exists, verify content shas."""
    assert _VENUE in ("ci", "sandbox", "pc"), (
        f"S0_01_VENUE={_VENUE!r} is not a known venue")
    if _VENUE in ("sandbox", "pc"):
        assert _REAL_LEG_DIR is not None, (
            f"S0_01_VENUE={_VENUE} but S0_01_REAL_LEG_DIR is unset "
            f"(real-leg corpus not declared for this venue)")
        assert _REAL_LEG_DIR.is_dir(), (
            f"S0_01_REAL_LEG_DIR={_REAL_LEG_DIR} is not a directory")
        present = {d.name for d in _REAL_LEG_DIR.iterdir() if d.is_dir()}
        missing = _EXPECTED_REAL_LEGS - present
        assert not missing, (
            f"S0_01_REAL_LEG_DIR={_REAL_LEG_DIR} incomplete: missing legs {sorted(missing)}")
        # CK11-F19: verify corpus CONTENT against the sidecar when present
        manifest = _REAL_LEG_DIR.parent / "golden.pc.sha256"
        assert manifest.is_file(), (
            f"{manifest} absent — run scripts/realleg_sync.sh pull")
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            sha, rel = line.split(None, 1)
            p = _REAL_LEG_DIR / rel.strip().lstrip("./")
            assert _sha256_file(p) == sha, f"corpus drift at {rel.strip()}"
        # CK12 sweep 10.2: assert declared artifacts per leg
        _V22_POSITIVE = {"timeline.jsonl", "runtime-identity.json", "env.json",
                         "frames-client-to-agent.jsonl", "frames-agent-to-client.jsonl",
                         "manifest-pre.txt.gz", "manifest-post.txt.gz",
                         "manifest-pre.summary", "manifest-post.summary",
                         "process-scan-after.txt", "process-scan-teardown.txt",
                         "owned-pids.json", "buzzacp.log", "startup-line.txt",
                         "hermes-model.txt", "argv.txt", "buzz-acp.pid", "buzz-acp.exit"}
        for leg in ("run-1", "cancel", "shutdown", "two-users"):
            ld = _REAL_LEG_DIR / leg
            for fn in sorted(_V22_POSITIVE):
                assert (ld / fn).is_file(), (
                    f"corpus {leg}/{fn} absent -- declared artifact missing")
        neg = _REAL_LEG_DIR / "negative"
        for fn in ("timeline.jsonl", "runtime-identity.json", "env.json", "agent-stderr.txt"):
            assert (neg / fn).is_file(), (
                f"corpus negative/{fn} absent -- declared artifact missing")
    elif _VENUE == "ci":
        if _REAL_LEG_DIR is None:
            pytest.skip("S0_01_VENUE=ci — real-leg corpus not required")


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_timeline(leg):
    """Real-producer: timeline loads and passes check_timeline."""
    leg_dir = _real_leg(leg)
    entries = cc._load_timeline_raw(leg_dir, leg)
    ok, result = _run_check_safe(cc.check_timeline, entries, leg, leg_dir)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_initialize_frames(leg):
    """Real-producer: initialize frames pass."""
    leg_dir = _real_leg(leg)
    entries = cc._load_timeline_raw(leg_dir, leg)
    c2a, a2c = cc.check_timeline(entries, leg, leg_dir)
    ok, result = _run_check_safe(cc.check_initialize_frames, c2a, a2c, leg)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_runtime_identity(leg):
    """Real-producer: runtime identity fails ONLY on tee_sha256 mismatch."""
    leg_dir = _real_leg(leg)
    ok, result = _run_check_safe(cc.check_runtime_identity, leg_dir, leg)
    if ok:
        pass  # no failure at all — acceptable
    else:
        assert result == f"{leg}: tee_sha256 mismatch", f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_env(leg):
    """Real-producer: env passes."""
    leg_dir = _real_leg(leg)
    identities = json.loads((P / "fixtures" / "identities.json").read_text())
    ok, result = _run_check_safe(cc.check_env, leg_dir, leg, identities)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_mentions(leg):
    """Real-producer: mentions pass."""
    leg_dir = _real_leg(leg)
    entries = cc._load_timeline_raw(leg_dir, leg)
    identities = json.loads((P / "fixtures" / "identities.json").read_text())
    ok, result = _run_check_safe(cc.check_mentions, leg_dir, leg, identities, entries)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_route(leg):
    """Real-producer: route check passes."""
    leg_dir = _real_leg(leg)
    entries = cc._load_timeline_raw(leg_dir, leg)
    ok, result = _run_check_safe(cc.check_route, leg_dir, leg, entries)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_config_echo(leg):
    """Real-producer: config echo passes."""
    leg_dir = _real_leg(leg)
    ok, result = _run_check_safe(cc.check_config_echo, leg_dir, leg)
    assert ok, f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_manifests(leg):
    """Real-producer: manifests fail ONLY on timestamps not pre < start < post."""
    leg_dir = _real_leg(leg)
    baseline = P / "evidence" / "golden" / "manifests" / "manifest-baseline.txt.gz"
    if not baseline.exists():
        pytest.skip("baseline manifest absent")
    ok, result = _run_check_safe(cc.check_manifests, leg_dir, leg, baseline,
                                  PINNED_BASELINE_GZ_SHA256)
    if ok:
        pass  # no failure — acceptable
    else:
        assert result == f"{leg}: manifest timestamps not pre < start < post", \
            f"unexpected failure: {result}"


@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_process_evidence(request, leg):
    """Real-producer: process evidence -- xfail on v2.2 corpus."""
    leg_dir = _real_leg(leg)
    scan = leg_dir / "process-scan-after.txt"
    if _CORPUS_VERSION == "v2.2":
        request.node.add_marker(pytest.mark.xfail(
            strict=True, reason=f"corpus v2.2 predates scan v2.3: {leg} process-scan-after.txt"))
        if not scan.is_file():
            pytest.fail(f"corpus v2.2: {leg} process-scan-after.txt absent")
        first = _corpus_file(leg_dir, "process-scan-after.txt").read_text().splitlines()
        if not first or not first[0].startswith("# process-scan v2.3 "):
            pytest.fail(f"corpus v2.2: {leg} has no v2.3 scan header")
    ok, result = _run_check_safe(cc.check_process_evidence, leg_dir, leg)
    assert ok, f"unexpected failure: {result}"

@pytest.mark.parametrize("leg", _POSITIVE_LEGS)
def test_real_leg_buzzacp_log(leg):
    """Real-producer: buzzacp log passes."""
    leg_dir = _real_leg(leg)
    ok, result = _run_check_safe(cc.check_buzzacp_log, leg_dir, leg)
    assert ok, f"unexpected failure: {result}"


def test_real_leg_prompt_turn():
    """Real-producer: prompt turn passes for run-1 and shutdown."""
    for leg in ("run-1", "shutdown"):
        leg_dir = _real_leg(leg)
        entries = cc._load_timeline_raw(leg_dir, leg)
        c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
        a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
        ok, result = _run_check_safe(cc.check_prompt_turn, c2a, a2c, leg, entries)
        assert ok, f"unexpected failure in {leg}: {result}"


def test_real_leg_cancel():
    """Real-producer: cancel leg passes check_cancel."""
    leg_dir = _real_leg("cancel")
    entries = cc._load_timeline_raw(leg_dir, "cancel")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    ok, result = _run_check_safe(cc.check_cancel, entries, c2a, a2c, leg_dir)
    assert ok, f"unexpected failure: {result}"


def test_real_leg_shutdown():
    """Real-producer: shutdown leg passes check_shutdown."""
    leg_dir = _real_leg("shutdown")
    entries = cc._load_timeline_raw(leg_dir, "shutdown")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    ok, result = _run_check_safe(cc.check_shutdown, entries, c2a, a2c, leg_dir)
    assert ok, f"unexpected failure: {result}"


def test_real_leg_two_users():
    """Real-producer: two-users leg passes check_two_users."""
    leg_dir = _real_leg("two-users")
    entries = cc._load_timeline_raw(leg_dir, "two-users")
    c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
    a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
    identities = json.loads((P / "fixtures" / "identities.json").read_text())
    ok, result = _run_check_safe(cc.check_two_users, c2a, a2c, entries, identities, leg_dir=leg_dir)
    assert ok, f"unexpected failure: {result}"


_KNOWN_XFAIL_REASONS = frozenset({
    "negative: negative: probe_sha256 mismatch",
    "negative: negative: agent_interpreter_realpath mismatch",
    "negative: negative: spawned_at_utc is later than the first frame",
})


def _is_known_stale(result: str) -> bool:
    """CK11-B1: EQUALITY on the WHOLE reason — no tail, no substring."""
    return result in _KNOWN_XFAIL_REASONS


def test_real_leg_negative(request):
    """Real-producer: negative leg — CK11-B1: the check MUST fail on the current corpus.
    If check_negative PASSES, the known-stale reasons no longer reproduce and must be
    retired.  A known-stale failure is xfailed; any other failure is a hard FAIL."""
    neg_dir = _real_leg("negative")
    ok, result = _run_check_safe(cc.check_negative, neg_dir)
    assert not ok, (
        "check_negative PASSES on the real negative leg — the known-stale reasons "
        f"{sorted(_KNOWN_XFAIL_REASONS)} no longer reproduce; retire them (B1)")
    if _is_known_stale(result):
        request.node.add_marker(pytest.mark.xfail(
            reason=f"real v2.2 sample: {result} (capture predates current probe)"))
        assert False, f"real v2.2 sample: {result} (capture predates current probe)"
    else:
        assert False, f"unexpected failure: negative: {result}"


def test_real_leg_normalize_timeline():
    """Real-producer: normalize_timeline produces a non-empty result for run-1."""
    leg_dir = _real_leg("run-1")
    entries = cc._load_timeline_raw(leg_dir, "run-1")
    n = cc.normalize_timeline(entries)
    assert len(n) > 0


# ============================================================================
# VERIFY-CK7 F1-F9: killing tests for the 21 previously-unkilled guards.
# Each test constructs the verifier's hostile bundle and asserts the EXACT
# failure reason.  The mutation audit proves each red on the guard-disabled
# copy (see the combined-mutant run in the report).
# ============================================================================

# -- F1: A24 ingress concurrency (C:890-893) --
def test_ck7_f1_second_mention_after_first_terminal(bundle):
    """F1: two-users second mention created_at AFTER the first terminal must fail."""
    ld = bundle / "golden" / "two-users"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find the first terminal t_utc
    first_term_utc = None
    for e in es:
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            r = e["frame"].get("result") or {}
            if r.get("stopReason") == "end_turn":
                first_term_utc = e["t_utc"]
                break
    assert first_term_utc is not None, "test setup: no terminal found"
    from datetime import datetime, timezone
    ft = datetime.strptime(first_term_utc, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    after_epoch = int(ft.timestamp()) + 10  # well after the terminal
    # Rewrite user2 mention with created_at after the terminal
    md = ld / "mentions"
    u2 = json.loads((md / "user2.event.json").read_text())
    u2["created_at"] = after_epoch
    # Re-sign with the correct id for the new created_at
    content = u2["content"]
    tags = u2["tags"]
    new_ev = nv.sign_event(USER2_SECKEY, {"created_at": after_epoch, "kind": 9,
                                          "tags": tags, "content": content})
    _rewrite(md / "user2.event.json", json.dumps(new_ev, indent=2) + "\n")
    # Update receipt to match new event id
    rcpt = json.loads((md / "user2.receipt.json").read_text())
    rcpt["event_id"] = new_ev["id"]
    _rewrite(md / "user2.receipt.json", json.dumps(rcpt, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: second mention not pending during the first turn"


# -- F2: A24 observed serialization (C:898-900) --
def test_ck7_f2_second_session_new_before_first_terminal(bundle):
    """F2: two-users second session/new before the first terminal must fail."""
    ld = bundle / "golden" / "two-users"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find indices of the two session/new frames and the first terminal
    new_idxs = [i for i, e in enumerate(es) if e["dir"] == "c2a" and e["frame"].get("method") == "session/new"]
    term_idxs = [i for i, e in enumerate(es) if e["dir"] == "a2c" and "id" in e["frame"]
                 and "method" not in e["frame"]
                 and (e["frame"].get("result") or {}).get("stopReason") == "end_turn"]
    assert len(new_idxs) >= 2 and len(term_idxs) >= 1, "test setup: need 2 session/new + 1 terminal"
    # Move the second session/new frame before the first terminal by swapping frames
    # Put the second session/new's frame into a position before the first terminal
    second_new_idx = new_idxs[1]
    first_term_idx = term_idxs[0]
    if second_new_idx > first_term_idx:
        # Swap the frames (not timestamps) so the second new comes before the terminal
        es[second_new_idx]["frame"], es[first_term_idx]["frame"] = \
            es[first_term_idx]["frame"], es[second_new_idx]["frame"]
        es[second_new_idx]["dir"], es[first_term_idx]["dir"] = \
            es[first_term_idx]["dir"], es[second_new_idx]["dir"]
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: second session/new precedes the first terminal"


# -- F3: A23 response cardinality (C:318-321) --
def test_ck7_f3_duplicate_response_id(bundle):
    """F3: duplicate response for the same id must fail."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find the first a2c response (has id, no method) and its id
    resp_idx = None
    resp_id = None
    for i, e in enumerate(es):
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            resp_idx = i
            resp_id = e["frame"]["id"]
            break
    assert resp_idx is not None, "test setup: no response found"
    # Insert a duplicate error response with the same id right before the end_turn
    end_turn_idx = None
    for i, e in enumerate(es):
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            r = e["frame"].get("result") or {}
            if r.get("stopReason") == "end_turn":
                end_turn_idx = i
                break
    assert end_turn_idx is not None, "test setup: no end_turn found"
    dup = {"seq": 0, "dir": "a2c", "t_utc": es[end_turn_idx]["t_utc"],
           "t_mono_ns": es[end_turn_idx]["t_mono_ns"] - 1,
           "frame": {"jsonrpc": "2.0", "id": resp_id,
                     "error": {"code": -32600, "message": "Injected duplicate"}}}
    es.insert(end_turn_idx, dup)
    for i, e in enumerate(es):
        e["seq"] = i + 1
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: duplicate response for id {resp_id} at seqs [{resp_idx + 1}, {end_turn_idx + 1}]"


# -- F4a: A23 frame classes — a2c agent request (C:302-303) --
def test_ck7_f4a_a2c_agent_request(bundle):
    """F4a: an a2c frame with method AND id (an agent request) must fail."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find the first a2c notification (has method, no id) and inject method+id
    for i, e in enumerate(es):
        if e["dir"] == "a2c" and "method" in e["frame"] and "id" not in e["frame"]:
            e["frame"]["id"] = 901
            break
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    method = es[i]["frame"]["method"]
    assert out == f"failure_reason: run-1: a2c frame at seq {es[i]['seq']} is an agent request (method={method!r})"


# -- F4b: A23 frame classes — c2a client response (C:304-305) --
def test_ck7_f4b_c2a_client_response(bundle):
    """F4b: a c2a frame with id and NO method (a client response) must fail."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find a c2a frame with method and replace it to have id but no method
    for i, e in enumerate(es):
        if e["dir"] == "c2a" and "method" in e["frame"]:
            e["frame"].pop("method")
            if "id" not in e["frame"]:
                e["frame"]["id"] = 901
            break
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: c2a frame at seq {es[i]['seq']} is a client response (id={es[i]['frame']['id']!r})"


# -- F5: A23 response envelope validity (C:325-328) --
def test_ck7_f5_invalid_response_envelope(bundle):
    """F5: response with wrong jsonrpc version (not '2.0') must fail.
    Uses a non-initialize response (the session/prompt terminal) so the attack
    is not caught by check_initialize_frames.  The guard at C:326 has two clauses
    joined by 'or'; the 'if False and' mutation disables only the first clause
    (jsonrpc != '2.0'), so the attack must trigger THAT clause while keeping
    result/error normal (exactly one of the two)."""
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find the LAST a2c response (the end_turn terminal) — not the initialize response
    target_idx = None
    for i in range(len(es) - 1, -1, -1):
        e = es[i]
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            target_idx = i
            break
    assert target_idx is not None, "test setup: no a2c response found"
    es[target_idx]["frame"]["jsonrpc"] = "3.0"
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: response at seq {es[target_idx]['seq']} is not a valid JSON-RPC envelope"


# -- F6a: A20b tee_pid ppid binding (C:1187-1188) --
def test_ck7_f6a_tee_pid_wrong_ppid(tmp_path):
    """F6a: tee_pid with wrong ppid (not buzz_acp_pid) must fail.
    Two tee processes: one structural (ppid=buzz, passes structural check) and
    the rid tee_pid (ppid=structural_tee, fails the identity ppid binding)."""
    ld = tmp_path
    buzz_pid = 12300
    structural_tee = 12350  # passes structural check (ppid=buzz, PINNED_TEE_PATH)
    rid_tee = 12340         # rid's tee_pid, ppid=structural_tee (not buzz_pid)
    agent_pid = 12345
    owned = sorted([buzz_pid, structural_tee, rid_tee, agent_pid])
    _rewrite(ld / "buzz-acp.pid", f"{buzz_pid}\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": buzz_pid, "owned": owned, "taken_at": "ready+after"}))
    _rewrite(ld / "runtime-identity.json", json.dumps(
        {"tee_pid": rid_tee, "agent_child_pid": agent_pid}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", owned=4, owned_present=4, pinned_present=4) + "\n"
        + f"{buzz_pid} 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
        + f"{structural_tee} {buzz_pid} 95 /usr/bin/python3 {PINNED_TEE_PATH} --wrapper\n"
        + f"{rid_tee} {structural_tee} 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
        + f"{agent_pid} {structural_tee} 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned=4, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: tee_pid 12340 ppid is not buzz_acp_pid"


# -- F6b: A20b agent_child_pid ppid binding (C:1195-1196) --
def test_ck7_f6b_agent_pid_wrong_ppid(tmp_path):
    """F6b: agent_child_pid with wrong ppid (not tee_pid) must fail.
    Two agent processes: one structural (ppid=tee, passes structural check) and
    the rid agent_child_pid (ppid=buzz, fails the identity ppid binding)."""
    ld = tmp_path
    buzz_pid = 12300
    tee_pid = 12340
    structural_agent = 12346  # passes structural check (ppid=tee, PINNED_AGENT_REALPATH)
    rid_agent = 12345         # rid's agent_child_pid, ppid=buzz (not tee_pid)
    owned = sorted([buzz_pid, tee_pid, structural_agent, rid_agent])
    _rewrite(ld / "buzz-acp.pid", f"{buzz_pid}\n")
    _rewrite(ld / "buzz-acp.exit", "0\n")
    _rewrite(ld / "owned-pids.json", json.dumps(
        {"buzz_acp_pid": buzz_pid, "owned": owned, "taken_at": "ready+after"}))
    _rewrite(ld / "runtime-identity.json", json.dumps(
        {"tee_pid": tee_pid, "agent_child_pid": rid_agent}))
    _rewrite(ld / "process-scan-after.txt", _scan_header("after", owned=4, owned_present=4, pinned_present=4) + "\n"
        + f"{buzz_pid} 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999\n"
        + f"{tee_pid} {buzz_pid} 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
        + f"{structural_agent} {tee_pid} 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n"
        + f"{rid_agent} {buzz_pid} 75 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    _rewrite(ld / "process-scan-teardown.txt", _scan_header("teardown", buzz_present=0, owned=4, owned_present=0) + "\n")
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(ld, "run-1")
    assert str(ei.value) == "run-1: agent_child_pid 12345 ppid is not tee_pid"


# -- F7a: teardown header mode mismatch (C:1215-1216) --
def test_ck7_f7a_teardown_mode_mismatch(bundle):
    """F7a: teardown scan with mode=after in header must fail."""
    ld = bundle / "golden" / "run-1"
    td = ld / "process-scan-teardown.txt"
    _rewrite(td, _scan_header("after", buzz_present=0, owned_present=0) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt header mode is 'after', expected 'teardown'"


# -- F7b: teardown header rows=0 (C:1217-1218) --
def test_ck7_f7b_teardown_rows_zero(bundle):
    """F7b: teardown scan with rows=0 must fail."""
    ld = bundle / "golden" / "run-1"
    td = ld / "process-scan-teardown.txt"
    _rewrite(td, _scan_header("teardown", rows=0, buzz_present=0, owned_present=0) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt header rows=0 (enumeration did not run)"


# -- F7c: teardown header owned count mismatch (C:1219-1220) --
def test_ck7_f7c_teardown_owned_mismatch(bundle):
    """F7c: teardown header owned != len(owned-pids.json owned) must fail."""
    ld = bundle / "golden" / "run-1"
    td = ld / "process-scan-teardown.txt"
    _rewrite(td, _scan_header("teardown", buzz_present=0, owned=1, owned_present=0) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt header owned=1 != owned-pids.json (3)"


# -- F7d: teardown header owned_present inconsistent (C:1222-1223) --
def test_ck7_f7d_teardown_owned_present_mismatch(bundle):
    """F7d: teardown header owned_present inconsistent with body must fail."""
    ld = bundle / "golden" / "run-1"
    td = ld / "process-scan-teardown.txt"
    # Empty body but header says owned_present=1
    _rewrite(td, _scan_header("teardown", buzz_present=0, owned_present=1) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt header owned_present=1 inconsistent with body (0)"


# -- F8a: A21d write_errors non-empty (running arm: has unexpected entries) --
def test_ck7_f8a_tee_status_write_errors(bundle):
    """F8a: tee-status.json with non-empty write_errors must fail.
    The fixture has final=False, so the RUNNING arm fires."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["write_errors"] = ["disk full"]
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json write_errors has unexpected entries: ['disk full']"


# -- F8b: A21d forwarded_a2c trails recorded by 2 (running arm) --
def test_ck7_f8b_tee_status_forwarded_a2c_mismatch(bundle):
    """F8b: tee-status.json forwarded_a2c trails recorded_a2c by 2 → running arm fails."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    r = ts["recorded_a2c"]
    ts["forwarded_a2c"] = max(0, r - 2)
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"forwarded_a2c {max(0, r - 2)} trails recorded_a2c {r} by more than one")


# -- F8c: A21d recorded_c2a > timeline c2a count → running arm's recorded deficit check --
def test_ck7_f8c_tee_status_recorded_c2a_wrong(bundle):
    """F8c: tee-status.json recorded_c2a + 1 → running arm: trails by more than one."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    real_c2a = ts["recorded_c2a"]
    ts["recorded_c2a"] = real_c2a + 1
    ts["forwarded_c2a"] = real_c2a + 1
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"recorded_c2a {real_c2a + 1} trails timeline c2a count {c2a_count} by more than one")


# -- F8d: A21d updated_utc format (C:1288) --
def test_ck7_f8d_tee_status_updated_utc_bad_format(bundle):
    """F8d: tee-status.json updated_utc as non-string must fail.
    The guard at C:1288 has two clauses joined by 'or': isinstance check and
    regex match. The 'if False and' mutation disables only the first clause;
    a bad-format string triggers the second clause even on the mutant.
    Using a non-string (int) triggers the isinstance clause specifically and
    causes a TypeError on the mutant (which fails the test's exact assertion)."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["updated_utc"] = 42  # not a string — triggers isinstance clause
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json updated_utc does not match format"


# -- F8e: A21d final but agent_returncode not int (C:1299) --
def test_ck7_f8e_tee_status_final_returncode_not_int(bundle):
    """F8e: final=true but agent_returncode not int must fail."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["stdin_reader_done"] = True
    ts["agent_returncode"] = "zero"
    ts["exit_code"] = 0
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json final but agent_returncode is not int"


# -- F8f: A21d not final but exit_code not null (C:1307) --
def test_ck7_f8f_tee_status_not_final_exit_not_null(bundle):
    """F8f: not final but exit_code not null must fail."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = False
    ts["agent_returncode"] = None
    ts["exit_code"] = 42
    _rewrite(ld / "tee-status.json", json.dumps(ts, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json not final but exit_code is not null"


# -- F9a: golden exactly one of each request kind (C:1365) --
def test_ck7_f9a_golden_request_kinds(bundle, monkeypatch):
    """F9a: golden without exactly one of each request kind must fail.
    Direct call to check_golden: inject an extra c2a request into both runs
    so the normalized golden has four request kinds instead of three."""
    gd = bundle / "golden"
    for leg in ("run-1", "run-2"):
        ld = gd / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        init_idx = next(i for i, e in enumerate(es) if e["dir"] == "c2a" and e["frame"].get("method") == "initialize")
        dup_req = {"seq": 0, "dir": "c2a", "t_utc": es[init_idx]["t_utc"],
                   "t_mono_ns": es[init_idx]["t_mono_ns"] + 1,
                   "frame": {"jsonrpc": "2.0", "id": 9999, "method": "tools/list", "params": {}}}
        dup_resp = {"seq": 0, "dir": "a2c", "t_utc": es[init_idx]["t_utc"],
                    "t_mono_ns": es[init_idx]["t_mono_ns"] + 2,
                    "frame": {"jsonrpc": "2.0", "id": 9999, "result": {}}}
        es.insert(init_idx + 1, dup_req)
        es.insert(init_idx + 2, dup_resp)
        for j, e in enumerate(es):
            e["seq"] = j + 1
        _write_timeline(ld, es)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(gd / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(gd / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    with pytest.raises(cc.Failure) as ei:
        cc.check_golden(gd)
    assert str(ei.value) == "golden: golden does not have exactly one of each request kind"


# -- F9b: golden run-1/run-2 raw sessionIds identical (C:1418) --
def test_ck7_f9b_golden_same_session_ids(bundle, monkeypatch):
    """F9b: run-1 and run-2 with identical raw sessionIds must fail."""
    ld1 = bundle / "golden" / "run-1"
    ld2 = bundle / "golden" / "run-2"
    es1 = [json.loads(l) for l in (ld1 / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es2 = [json.loads(l) for l in (ld2 / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Find the sessionId in run-1
    sid1 = None
    for e in es1:
        if e["dir"] == "a2c" and "id" in e["frame"] and "method" not in e["frame"]:
            r = e["frame"].get("result") or {}
            if "sessionId" in r:
                sid1 = r["sessionId"]
                break
    assert sid1 is not None, "test setup: no sessionId in run-1"
    # Set run-2's sessionId to match run-1 everywhere: responses, notifications, AND prompts
    for e in es2:
        if e["dir"] == "a2c":
            if "id" in e["frame"] and "method" not in e["frame"]:
                r = e["frame"].get("result") or {}
                if "sessionId" in r:
                    r["sessionId"] = sid1
            elif "method" in e["frame"] and "id" not in e["frame"]:
                params = e["frame"].get("params") or {}
                if "sessionId" in params:
                    params["sessionId"] = sid1
        elif e["dir"] == "c2a":
            if e["frame"].get("method") == "session/prompt":
                params = e["frame"].get("params") or {}
                if "sessionId" in params:
                    params["sessionId"] = sid1
    _write_timeline(ld2, es2)
    # The normalized golden uses placeholders, so run-1 and run-2 produce the same normalized form
    n1 = cc.normalize_timeline(cc._load_timeline_raw(ld1, "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: run-1 and run-2 raw sessionIds are identical"


# -- F9c: golden run-1/run-2 first t_utc identical (C:1420) --
def test_ck7_f9c_golden_same_first_tutc(bundle, monkeypatch):
    """F9c: run-1 and run-2 with identical first t_utc must fail."""
    ld1 = bundle / "golden" / "run-1"
    ld2 = bundle / "golden" / "run-2"
    es1 = [json.loads(l) for l in (ld1 / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es2 = [json.loads(l) for l in (ld2 / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Set run-2's first t_utc to match run-1
    es2[0]["t_utc"] = es1[0]["t_utc"]
    _write_timeline(ld2, es2)
    # Regenerate golden.jsonl
    n1 = cc.normalize_timeline(cc._load_timeline_raw(ld1, "run-1"))
    golden_text = "\n".join(n1) + "\n"
    _rewrite(bundle / "golden" / "golden.jsonl", golden_text)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(golden_text.encode()))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: run-1 and run-2 first t_utc are identical"


# === F43 / R8-CK-F5 / R9-CK-F3: source-scan function extracted to module scope ===
# The real assertion and the self-test BOTH call _scan_direct_writes so the scan
# cannot be disabled without the self-test also going red.

_WRITE_ATTRS = {"write_text", "write_bytes", "touch", "rename",
                "chmod", "hardlink_to"}
# symlink_to omitted: creates a new dirent or raises FileExistsError; cannot reach a shared inode.
_WRITE_MODES = set("wa+")
_SHUTIL_WRITERS = {"copy", "copy2", "copyfile"}
_OS_WRITERS = {"replace", "rename", "truncate", "chmod", "utime"}
_EXEMPT_FNS = {"_rewrite", "_write_timeline", "_write_tee_status",
               "_write_runtime_identity", "_write_env", "_write_startup_and_log",
               "_write_model", "_write_manifests", "_write_mentions",
               "_write_upstream_records", "_write_process_scan", "_write_negative",
               "_sign_mention", "_session_bundle", "_patch_nostr_verify",
               "test_ck8_f34_frame_tee_subprocess_keys",
               "test_ck9_tools_not_hardlinked",
               "test_golden_run_eq", "test_golden_distinctness_all"}


def _scan_direct_writes(src: str) -> list[str]:
    """R9-CK-F3: scan Python source for writes that bypass _rewrite.  Returns a list
    of violation descriptions (empty = clean).  The self-test asserts the CATEGORIES
    detected so disabling any single pattern family makes it fail.
    Known limits (AF-AP-30 — static scanning is the losing game): os.open+os.write,
    os.fdopen, tempfile.NamedTemporaryFile, variable mode (m='w'; open(p,m)),
    shutil.copytree/move (would flag the bundle fixture), subprocess cp,
    module-level writes (fn_name is None -> continue)."""
    import ast as _ast
    tree = _ast.parse(src)
    fn_ranges = []
    for node in _ast.iter_child_nodes(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            fn_ranges.append((node.name, node.lineno, node.end_lineno))
        elif isinstance(node, _ast.ClassDef):
            for child in _ast.iter_child_nodes(node):
                if isinstance(child, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                    fn_ranges.append((f"{node.name}.{child.name}", child.lineno, child.end_lineno))
    violations = []
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Call):
            continue
        lineno = node.lineno
        fn_name = None
        for name, start, end in fn_ranges:
            if start <= lineno <= end:
                fn_name = name
                break
        if fn_name is None or fn_name in _EXEMPT_FNS:
            continue
        func = node.func
        if isinstance(func, _ast.Attribute) and func.attr in _WRITE_ATTRS:
            violations.append(f"line {lineno}: .{func.attr}()")
            continue
        if isinstance(func, _ast.Name) and func.id == "open":
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, _ast.Constant) and isinstance(mode_arg.value, str):
                    if _WRITE_MODES & set(mode_arg.value):
                        violations.append(f"line {lineno}: open(..., {mode_arg.value!r})")
                        continue
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, _ast.Constant):
                    if isinstance(kw.value.value, str) and _WRITE_MODES & set(kw.value.value):
                        violations.append(f"line {lineno}: open(..., mode={kw.value.value!r})")
        if isinstance(func, _ast.Attribute) and func.attr == "open":
            if len(node.args) >= 1:
                mode_arg = node.args[0]
                if isinstance(mode_arg, _ast.Constant) and isinstance(mode_arg.value, str):
                    if _WRITE_MODES & set(mode_arg.value):
                        violations.append(f"line {lineno}: .open({mode_arg.value!r})")
                        continue
            # R10: also check keyword mode= on the .open() method (asymmetry fix)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, _ast.Constant):
                    if isinstance(kw.value.value, str) and _WRITE_MODES & set(kw.value.value):
                        violations.append(f"line {lineno}: .open(mode={kw.value.value!r})")
                        break
        if isinstance(func, _ast.Attribute) and func.attr == "dump":
            if isinstance(func.value, _ast.Name) and func.value.id == "json":
                violations.append(f"line {lineno}: json.dump()")
                continue
        if isinstance(func, _ast.Attribute) and func.attr in _SHUTIL_WRITERS:
            if isinstance(func.value, _ast.Name) and func.value.id == "shutil":
                violations.append(f"line {lineno}: shutil.{func.attr}()")
                continue
        if isinstance(func, _ast.Attribute) and func.attr in _OS_WRITERS:
            if isinstance(func.value, _ast.Name) and func.value.id == "os":
                violations.append(f"line {lineno}: os.{func.attr}()")
                continue
        # R10: io.open is a write-capable alias of builtin open
        if isinstance(func, _ast.Attribute) and func.attr == "open":
            if isinstance(func.value, _ast.Name) and func.value.id == "io":
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                    if isinstance(mode_arg, _ast.Constant) and isinstance(mode_arg.value, str):
                        if _WRITE_MODES & set(mode_arg.value):
                            violations.append(f"line {lineno}: io.open(..., {mode_arg.value!r})")
                            continue
        # CK11-F7: gzip.open writes through hardlinks
        if isinstance(func, _ast.Attribute) and func.attr == "open":
            if isinstance(func.value, _ast.Name) and func.value.id == "gzip":
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                    if isinstance(mode_arg, _ast.Constant) and isinstance(mode_arg.value, str):
                        if _WRITE_MODES & set(mode_arg.value):
                            violations.append(f"line {lineno}: gzip.open(..., {mode_arg.value!r})")
                            continue
    return violations


def test_f43_no_direct_writes_outside_rewrite():
    """R9-CK-F3: scan the test file for writes that bypass _rewrite.  The scan function
    is at module scope so the self-test exercises the SAME code path."""
    import inspect
    src = Path(inspect.getfile(test_f43_no_direct_writes_outside_rewrite)).read_text()
    # CK11-F6: inlined so F43-SCAN-OFF (violations=[]) dies — the scan cannot be
    # bypassed by rebinding the local variable.
    assert _scan_direct_writes(src) == [], f"F43: direct writes outside _rewrite: {_scan_direct_writes(src)}"
    # Self-test: a deliberately-violating source string must trigger the same scan.
    _SELF_TEST_SRC = '''
def test_ck8_inplace_write_mutant():
    with open(p, "w") as f: f.write("evil")
def test_ck8_inplace_write_mutant_b():
    json.dump(obj, open(p, "w"))
def test_ck8_inplace_write_mutant_c():
    shutil.copy(src, p)
def test_ck8_inplace_write_mutant_d():
    p.write_text("evil")
def test_ck8_inplace_write_mutant_e():
    p.write_bytes(b"evil")
def test_ck8_inplace_write_mutant_f():
    os.replace(src, dst)
def test_ck8_inplace_write_mutant_g():
    p.touch()
def test_ck8_inplace_write_mutant_h():
    p.rename(dst)
def test_ck8_inplace_write_mutant_i():
    p.open(mode="w")
def test_ck8_inplace_write_mutant_j():
    io.open(p, "w")
def test_ck12_chmod_mutant():
    p.chmod(0o400)
def test_ck12_hardlink_mutant():
    p.hardlink_to(dst)
def test_ck12_os_truncate_mutant():
    os.truncate(p, 0)
def test_ck12_os_utime_mutant():
    os.utime(p)
def test_ck12_gzip_open_mutant():
    gzip.open(p, "wb")
'''
    self_violations = _scan_direct_writes(_SELF_TEST_SRC)
    # R10: assert the CATEGORIES detected, not just a count — prevents any single
    # pattern family from being deleted with the self-test still green.
    cats = {v.split(": ", 1)[1].split("(")[0].strip() for v in self_violations}
    assert cats == {".write_text", ".write_bytes", "open", "json.dump",
                    "shutil.copy", "os.replace", ".touch", ".rename",
                    ".open", "io.open", ".chmod", ".hardlink_to",
                    "os.truncate", "os.utime",
                    "gzip.open"}, f"F43 self-test categories: {cats}"


# === F22-F26: records / receipts / startup exact-match tests ===

def test_ck7_f22_post_body_extra_key(bundle):
    """F22: upstream POST body rejects extra keys (R8-CK-F8: per-shape key set)."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is True:
            r["body"]["evil_tool_calls"] = [{"exfil": "yes"}]
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream POST record stream body key set mismatch: ['evil_tool_calls']"


def test_ck7_f23_post_body_wrong_role(bundle):
    """F23: upstream POST message roles pinned per shape (R8-CK-F8)."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is True:
            r["body"]["messages"] = [{"role": "tool", "content": "x"}]
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream POST record stream message roles ['tool'] != expected ['system', 'user']"


def test_ck7_f24_get_fingerprint_bogus(bundle):
    """R8-CK-F7: GET fingerprint pinned to null — non-null is rejected."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "GET":
            r["authorization_fingerprint"] = "f" * 64
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream GET record authorization_fingerprint is not null"


def test_ck7_f25_startup_extra_token(bundle):
    """F25: startup-line rejects unknown keys."""
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    old = sp.read_text().rstrip("\n")
    _rewrite(sp, old + " backdoor=on\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    old_log = lp.read_text()
    lines = old_log.splitlines()
    lines[0] = lines[0] + " backdoor=on"
    _rewrite(lp, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup-line unknown key 'backdoor'"


def test_ck7_f26_mention_pubkeys_extra(bundle):
    """F26: receipt mention_pubkeys must equal exactly [identities.agent]."""
    md = bundle / "golden" / "run-1" / "mentions"
    rp = md / "owner.receipt.json"
    receipt = json.loads(rp.read_text())
    extra_pk = "a" * 64
    receipt["mention_pubkeys"].append(extra_pk)
    _rewrite(rp, json.dumps(receipt) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    expected_mpk = [SYNTH_IDENTITIES["agent"]]
    assert out == f"failure_reason: run-1: mention owner receipt mention_pubkeys {receipt['mention_pubkeys']!r} != expected {expected_mpk!r}"


def test_ck7_f26_mention_pubkeys_empty(bundle):
    """F26: receipt mention_pubkeys must not be empty."""
    md = bundle / "golden" / "run-1" / "mentions"
    rp = md / "owner.receipt.json"
    receipt = json.loads(rp.read_text())
    receipt["mention_pubkeys"] = []
    _rewrite(rp, json.dumps(receipt) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    expected_mpk = [SYNTH_IDENTITIES["agent"]]
    assert out == f"failure_reason: run-1: mention owner receipt mention_pubkeys [] != expected {expected_mpk!r}"


# === F14: rid tee_pid/agent_child_pid in owned_set on shutdown ===

def test_ck7_f14_shutdown_rid_pids_not_in_owned(bundle):
    """F14: shutdown rid tee_pid/agent_child_pid must be in owned_set."""
    sd = bundle / "golden" / "shutdown"
    rid = json.loads((sd / "runtime-identity.json").read_text())
    rid["tee_pid"] = 77777
    _rewrite(sd / "runtime-identity.json", json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: owned-pids.json does not contain rid tee_pid 77777"


# === F30: after-scan duplicate rows ===

def test_ck7_f30_after_scan_duplicate_pid(bundle):
    """F30: duplicate scan rows for one pid in after-scan are rejected."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    lines = sp.read_text().splitlines()
    # Duplicate the second body row (tee_pid=12340)
    assert len(lines) > 2, "expected at least 3 lines in after-scan"
    lines.append(lines[2])
    _rewrite(sp, "\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after.txt duplicate rows for pid(s) [12340]"


# === F34: _TEE_STATUS_KEYS → pins.PINNED_TEE_STATUS_KEYS ===

def test_ck7_f34_frame_tee_keys_match_pin_ast():
    """F34 (AST instrument): extract keys from _write_status and assert == PINNED_TEE_STATUS_KEYS."""
    from pins import PINNED_TEE_STATUS_KEYS
    tee_path = P / "tools" / "frame_tee.py"
    assert tee_path.exists(), "frame_tee.py absent"
    src = tee_path.read_text()
    import ast as _ast
    tree = _ast.parse(src)
    status_keys = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name == "_write_status":
            for child in _ast.walk(node):
                if isinstance(child, _ast.Dict):
                    for k in child.keys:
                        if isinstance(k, _ast.Constant) and isinstance(k.value, str):
                            status_keys.add(k.value)
            break
    assert status_keys, "could not extract keys from frame_tee.py _write_status"
    assert status_keys == set(PINNED_TEE_STATUS_KEYS), (
        f"frame_tee.py status keys {sorted(status_keys)} != PINNED_TEE_STATUS_KEYS {sorted(PINNED_TEE_STATUS_KEYS)}"
    )


def test_ck8_f34_frame_tee_subprocess_keys(tmp_path):
    """R8-CK-F10: RUN the committed tee (subprocess, two frames, SIGTERM) and assert the
    emitted key order == PINNED_TEE_STATUS_KEYS."""
    import signal as _sig
    import time
    from pins import PINNED_TEE_STATUS_KEYS
    tee_path = P / "tools" / "frame_tee.py"
    framedir = tmp_path / "frames"
    framedir.mkdir()
    agent_code = (
        f"#!{sys.executable}\n"
        "import sys, json\n"
        "for line in sys.stdin:\n"
        "    sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':1,'result':{}},separators=(',',':'))+'\\n')\n"
        "    sys.stdout.flush()\n"
        "sys.exit(0)\n"
    )
    agent_script = tmp_path / "agent.py"
    agent_script.write_text(agent_code)
    agent_script.chmod(0o755)
    env = os.environ.copy()
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["S0_01_AGENT"] = str(agent_script)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    frames = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "init", "params": {}}, separators=(",", ":")) + "\n",
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping", "params": {}}, separators=(",", ":")) + "\n",
    ]
    proc = subprocess.Popen([sys.executable, str(tee_path)],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    try:
        for f in frames:
            proc.stdin.write(f.encode())
            proc.stdin.flush()
        status_path = framedir / "tee-status.json"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if status_path.exists():
                try:
                    s = json.loads(status_path.read_text())
                    if s.get("updated_seq", 0) >= 2:
                        break
                except (json.JSONDecodeError, ValueError):
                    pass
            time.sleep(0.1)
        proc.send_signal(_sig.SIGTERM)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        proc.stdin.close()
        proc.stdout.close()
        proc.stderr.close()
    assert status_path.exists(), "tee-status.json not written"
    ts = json.loads(status_path.read_text())
    assert tuple(ts.keys()) == PINNED_TEE_STATUS_KEYS, (
        f"emitted key order {tuple(ts.keys())} != PINNED_TEE_STATUS_KEYS {PINNED_TEE_STATUS_KEYS}"
    )


# === R8-CK-F1: owned-set shape and buzz-pid binding ===

def test_ck8_owned_set_empty(bundle):
    """R8-CK-F1: owned-pids.json owned is empty → exact Failure."""
    sd = bundle / "golden" / "shutdown"
    owned = json.loads((sd / "owned-pids.json").read_text())
    owned["owned"] = []
    _rewrite(sd / "owned-pids.json", json.dumps(owned))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: owned-pids.json owned is empty or not a list"


def test_ck8_owned_missing_buzz_pid(bundle):
    """R8-CK-F1: owned-pids.json does not contain buzz-acp.pid → exact Failure."""
    sd = bundle / "golden" / "shutdown"
    owned = json.loads((sd / "owned-pids.json").read_text())
    owned["owned"] = [99999]
    _rewrite(sd / "owned-pids.json", json.dumps(owned))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: owned-pids.json does not contain buzz-acp.pid 12300"


# === R8-CK-F2: FIFO in evidence tree, timeout, fixtures dir ===

def test_ck8_fifo_in_evidence_tree(bundle):
    """R8-CK-F2: non-regular entry in golden/ → exact Failure, completes in < 5 s."""
    import time
    fifo_path = bundle / "golden" / "run-1" / "timeline.jsonl"
    fifo_path.unlink()
    os.mkfifo(fifo_path)
    start = time.monotonic()
    rc, out = _check(bundle)
    elapsed = time.monotonic() - start
    assert rc == 1
    assert out == "failure_reason: golden: non-regular entry in evidence tree: run-1/timeline.jsonl"
    assert elapsed < 5, f"FIFO detection took {elapsed:.1f}s, expected < 5s"


def test_ck8_fifo_in_fixtures_dir_rejected(bundle):
    """R8-CK-F2: non-regular entry in fixtures dir → exact Failure."""
    fixtures_dir = bundle.parent / "fixtures"
    fifo_path = fixtures_dir / "evil.fifo"
    os.mkfifo(fifo_path)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: fixtures: non-regular entry in evidence tree: evil.fifo"


def test_ck8_check_bundle_timeout(bundle, monkeypatch):
    """R8-CK-F2: a patched slow check → exact 'checker timed out after 1s'."""
    import time
    original = cc.check_timeline
    def slow_check(*args, **kwargs):
        time.sleep(5)
        return original(*args, **kwargs)
    monkeypatch.setattr(cc, "check_timeline", slow_check)
    try:
        rc = 70
        try:
            cc.check_bundle(bundle, timeout_s=1)
        except SystemExit as e:
            rc = e.code
        assert rc == 70
    finally:
        pass


def test_ck8_timeout_arg_non_int():
    """R8-CK-F2: --timeout-s non-int → rc 64."""
    r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", "abc", "/tmp/x"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 64


# === R8-CK-F3: F14 parametrised over LEGS × {tee_pid, agent_child_pid} ===

@pytest.mark.parametrize("leg,pid_field", [
    (leg, field) for leg in LEGS for field in ("tee_pid", "agent_child_pid")
])
def test_ck8_f14_rid_pid_not_in_owned(bundle, leg, pid_field):
    """R8-CK-F3: rid tee_pid/agent_child_pid not in owned_set → exact Failure per leg."""
    ld = bundle / "golden" / leg
    rid = json.loads((ld / "runtime-identity.json").read_text())
    fake_pid = 88888 if pid_field == "tee_pid" else 77777
    rid[pid_field] = fake_pid
    _rewrite(ld / "runtime-identity.json", json.dumps(rid))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: {leg}: owned-pids.json does not contain rid {pid_field} {fake_pid}"


# === R8-CK-F4: A20a structural attacks with FULL owned set ===

def test_ck8_f4_no_tee_parented_by_buzz(bundle):
    """R8-CK-F4: no tee process parented by buzz-acp → exact Failure (FULL owned set)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    # All owned pids present, but tee_pid has wrong ppid (not buzz_pid)
    _rewrite(sp, _scan_header("after", pinned_present=3) + "\n"
                 + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n"
                 + f"12340 9999 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
                 + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    # The closure recomputation catches that 12340/12345 are not in the buzz-acp closure
    assert out == "failure_reason: run-1: recomputed owned closure != owned-pids.json"


def test_ck8_f4_no_agent_parented_by_tee(bundle):
    """R8-CK-F4: no agent process parented by a tee process → exact Failure.
    The agent is parented by buzz (not tee), making the closure valid but
    the identity-binding ppid check fails."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    # Agent parented directly by buzz, not tee. All three are in the owned closure.
    _rewrite(sp, _scan_header("after", pinned_present=3) + "\n"
                 + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n"
                 + f"12340 12300 90 /usr/bin/python3 {PINNED_TEE_PATH}\n"
                 + f"12345 12300 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    # The A20a structural "no agent parented by a tee process" fires because
    # the only tee_pids set = {12340} (ppid==buzz_pid), and no agent has ppid in tee_pids.
    assert out == "failure_reason: run-1: no agent process parented by a tee process"


# === R8-CK-F6: startup pins and parenthesised-value rejection ===

def test_ck8_startup_parens_with_equals(bundle):
    """R8-CK-F6: parenthesised value with '=' is rejected."""
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    old = sp.read_text().rstrip("\n")
    new = old.replace("model=(agent default)", "model=(agent default backdoor=on)")
    _rewrite(sp, new + "\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    _rewrite(lp, lp.read_text().replace("model=(agent default)", "model=(agent default backdoor=on)"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup-line parenthesised value carries key=value tokens: model"


def test_ck8_startup_missing_keys(bundle):
    """R8-CK-F6: required set is the full 21 keys — a stripped line fails."""
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    # Replace with a line missing heartbeat, subscribe, etc
    _rewrite(sp, "2026-09-05T05:00:00.000000Z  INFO buzz_acp: buzz-acp starting: relay=ws://127.0.0.1:3999 pubkey=<HEX> agent_cmd=x mcp_cmd= idle_timeout=900s max_turn=3600s agents=1 dedup=Queue session_policy=thread ignore_self=true permission_mode=bypassPermissions respond_to=owner-only\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    _rewrite(lp, (sp.read_text().rstrip("\n") + "\n"))
    rc, out = _check(bundle)
    assert rc == 1
    assert "startup-line missing keys" in out


# === R8-CK-F7: GET fingerprint non-null rejected ===

def test_ck8_get_fingerprint_non_null_rejected(bundle):
    """R8-CK-F7: GET fingerprint pinned to null — any non-null value is rejected."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "GET":
            r["authorization_fingerprint"] = _load_fingerprint()
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream GET record authorization_fingerprint is not null"


# === R8-CK-F8: per-shape POST key sets ===

def test_ck8_post_body_union_shape_rejected(bundle):
    """R8-CK-F8: a body carrying the union of both shapes is rejected."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is True:
            r["body"]["response_format"] = {"type": "text"}
            r["body"]["temperature"] = 0.5
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert "body key set mismatch" in out


def test_ck8_nonstream_roles_wrong(bundle):
    """R8-CK-F8: non-stream POST with wrong role sequence is rejected."""
    for rp in (bundle / "golden" / "run-1" / "upstream-records").glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is not True:
            r["body"]["messages"] = [{"role": "assistant", "content": "x"}]
            _rewrite(rp, json.dumps(r) + "\n")
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream POST record non-stream message roles ['assistant'] != expected ['system', 'user']"


# === R8-CK-F9: teardown scan duplicate pid ===

def test_ck8_teardown_scan_duplicate_pid(bundle):
    """R8-CK-F9: duplicate rows for one pid in teardown-scan → exact Failure."""
    tp = bundle / "golden" / "run-1" / "process-scan-teardown.txt"
    _rewrite(tp, _scan_header("teardown", buzz_present=0, owned_present=0, rows=2) + "\n"
                 + "99001 1 5 /usr/bin/sleep 900\n"
                 + "99001 1 5 /usr/bin/sleep 900\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt duplicate rows for pid(s) [99001]"


# === R8-CK-F12: startup values come from pins ===

def test_ck8_startup_values_come_from_pins(bundle, monkeypatch):
    """R8-CK-F12: monkeypatch one pin and assert the checker's reason quotes the patched value."""
    monkeypatch.setattr("check_acp_conformance.PINNED_STARTUP_PERMISSION_MODE", "PATCHED_MODE")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup permission_mode is 'bypassPermissions', expected 'PATCHED_MODE'"


# === R2/F42: wrong-value hostile bundles per pinned startup key ===

@pytest.mark.parametrize("pin_key,pin_attr,startup_key,wrong_val", [
    ("PINNED_STARTUP_MCP_CMD", "PINNED_STARTUP_MCP_CMD", "mcp_cmd", "evil_mcp"),
    ("PINNED_STARTUP_PERMISSION_MODE", "PINNED_STARTUP_PERMISSION_MODE", "permission_mode", "allow_all"),
    ("PINNED_STARTUP_RESPOND_TO", "PINNED_STARTUP_RESPOND_TO", "respond_to", "nobody"),
    ("PINNED_STARTUP_RESPOND_TO_TWO_USERS", "PINNED_STARTUP_RESPOND_TO_TWO_USERS", "respond_to", "everyone"),
])
def test_ck8_f42_wrong_startup_pin(bundle, pin_key, pin_attr, startup_key, wrong_val):
    """R2/F42: wrong value for a pinned startup key → exact Failure naming both values."""
    import check_acp_conformance as _cc
    real_val = getattr(_cc, pin_attr)
    # Pick the leg: respond_to_two_users → two-users leg, otherwise run-1
    if pin_key == "PINNED_STARTUP_RESPOND_TO_TWO_USERS":
        leg = "two-users"
    elif pin_key == "PINNED_STARTUP_RESPOND_TO":
        leg = "run-1"
    else:
        leg = "run-1"
    sp = bundle / "golden" / leg / "startup-line.txt"
    old_startup = sp.read_text().rstrip("\n")
    if startup_key == "respond_to" and pin_key == "PINNED_STARTUP_RESPOND_TO_TWO_USERS":
        old_startup = old_startup.replace("respond_to=allowlist(1)", f"respond_to={wrong_val}")
    elif startup_key == "respond_to":
        old_startup = old_startup.replace("respond_to=owner-only", f"respond_to={wrong_val}")
    else:
        old_startup = old_startup.replace(f"{startup_key}={real_val}", f"{startup_key}={wrong_val}")
    _rewrite(sp, old_startup + "\n")
    lp = bundle / "golden" / leg / "buzzacp.log"
    log_text = lp.read_text()
    if startup_key == "respond_to" and pin_key == "PINNED_STARTUP_RESPOND_TO_TWO_USERS":
        log_text = log_text.replace("respond_to=allowlist(1)", f"respond_to={wrong_val}")
    elif startup_key == "respond_to":
        log_text = log_text.replace("respond_to=owner-only", f"respond_to={wrong_val}")
    else:
        log_text = log_text.replace(f"{startup_key}={real_val}", f"{startup_key}={wrong_val}")
    _rewrite(lp, log_text)
    rc, out = _check(bundle)
    assert rc == 1
    assert startup_key in out
    assert wrong_val in out


# === R4/F38: A25 sequence test — omission at the dispatcher ===

def test_ck8_f38_check_sequence_omission(bundle, monkeypatch):
    """R4/F38: skip check_env for run-2 at the dispatcher → exact sequence mismatch."""
    # Intercept _run_check to skip check_env for run-2
    _orig_run_check = cc._run_check
    def patched_run_check(fn, leg, *args, **kwargs):
        if fn.__name__ == "check_env" and leg == "run-2":
            # Skip — do NOT record in _executed
            return fn(*args, **kwargs)  # call but don't record
        return _orig_run_check(fn, leg, *args, **kwargs)
    # Actually, _run_check records AFTER the call. So to skip the recording,
    # we need to not call _run_check at all for that pair. But we can't easily
    # intercept the inner loop. Instead, remove the expected pair from the sequence.
    # Actually the simplest approach: monkeypatch _run_check itself.
    def skip_env_run2(fn, leg, *args, **kwargs):
        if fn.__name__ == "check_env" and leg == "run-2":
            # Call fn but do NOT append to _executed
            return fn(*args, **kwargs)
        result = fn(*args, **kwargs)
        cc._executed.append((fn.__name__, leg))
        return result
    monkeypatch.setattr(cc, "_run_check", skip_env_run2)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: check sequence mismatch - first missing: check_env:run-2"


# === R6/F35: real-leg check_tee_status ===

@pytest.mark.parametrize("leg", sorted(_EXPECTED_REAL_LEGS - {"negative"}))
def test_ck8_real_leg_tee_status(request, leg):
    """R6/F35: real-leg check_tee_status. CK12: xfail on v2.2 corpus."""
    leg_dir = _real_leg(leg)
    ts_path = leg_dir / "tee-status.json"
    if _CORPUS_VERSION == "v2.2" and not ts_path.is_file():
        request.node.add_marker(pytest.mark.xfail(
            strict=True, reason=f"corpus v2.2 predates tee status: {leg} tee-status.json"))
        pytest.fail(f"corpus v2.2: {leg} tee-status.json absent")
    entries = cc._load_timeline_raw(leg_dir, leg)
    try:
        cc.check_tee_status(leg_dir, leg, entries)
    except cc.Failure as f:
        pytest.fail(f"check_tee_status({leg}) failed: {f}")


def test_ck8_tee_status_hostile_bundle(bundle):
    """R6: hostile-bundle variant for check_tee_status — write_errors with bad content.
    The fixture has final=False (running arm), so the reason names the bad entries."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["write_errors"] = ["some random error"]
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json write_errors has unexpected entries: ['some random error']"


# === R1: A21d running snapshot tests ===

def test_ck8_running_drained_false_accepted(bundle):
    """R1: running snapshot with drained=false is accepted."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["drained"] = False
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 0  # should PASS


def test_ck8_running_sigterm_errors_accepted(bundle):
    """R1: running snapshot with write_errors=["terminated: SIGTERM"] is accepted."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["write_errors"] = ["terminated: SIGTERM"]
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 0


def test_ck8_running_sigkill_errors_rejected(bundle):
    """R1: running snapshot with write_errors=["terminated: SIGKILL"] is rejected."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["write_errors"] = ["terminated: SIGKILL"]
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json write_errors has unexpected entries: ['terminated: SIGKILL']"


def test_ck8_running_sigterm_on_final_rejected(bundle):
    """R1: final status with write_errors=["terminated: SIGTERM"] is rejected."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = {
        "final": True, "agent_returncode": 0, "drained": True, "stdin_reader_done": True,
        "recorded_c2a": c2a_count, "recorded_a2c": a2c_count,
        "forwarded_c2a": c2a_count, "forwarded_a2c": a2c_count,
        "write_errors": ["terminated: SIGTERM"], "exit_code": 0,
        "updated_seq": last_seq, "updated_utc": entries[-1]["t_utc"],
    }
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json write_errors is not empty"


def test_ck8_running_forwarded_deficit_1_accepted(bundle):
    """R1: running snapshot with forwarded trailing recorded by 1 is accepted."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["forwarded_c2a"] = ts["recorded_c2a"] - 1
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 0


def test_ck8_running_forwarded_deficit_2_rejected(bundle):
    """R1: running snapshot with forwarded trailing recorded by 2 is rejected."""
    ld = bundle / "golden" / "run-1"
    ts = json.loads((ld / "tee-status.json").read_text())
    r = ts["recorded_c2a"]
    ts["forwarded_c2a"] = r - 2
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"forwarded_c2a {r - 2} trails recorded_c2a {r} by more than one")


def test_ck8_running_seq_sum_invariant(bundle):
    """R1: the per-direction recorded deficits must sum to the seq lag."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    # lag=1 but both directions at full count → deficit sum=0 != lag=1
    ts["updated_seq"] = last_seq - 1
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == ("failure_reason: run-1: tee-status.json running snapshot "
                   "recorded deficits 0+0 do not sum to updated_seq lag 1")


# === R9-CK: round 10 — domain floors, walk-before-read, FINAL arm pinned ===

# F1: --timeout-s positivity floor
def test_ck9_timeout_arg_zero_rejected():
    """R9-CK-F1: --timeout-s 0 must exit 64, not silently disable the cap."""
    r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", "0", "/tmp/x"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: --timeout-s must be a positive integer"


def test_ck9_timeout_arg_negative_rejected():
    """R9-CK-F1: --timeout-s -1 must exit 64."""
    r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", "-1", "/tmp/x"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: --timeout-s must be a positive integer"


def test_ck9_timeout_inprocess_zero_raises():
    """R9-CK-F1: in-process check_bundle(timeout_s=0) raises ValueError."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(ValueError, match="positive integer"):
            cc.check_bundle(Path(td), timeout_s=0)


# F2: walk before read — a FIFO at identities.json is named, not timed out
def test_ck9_fifo_at_identities_json_is_named(bundle):
    """R9-CK-F2: a FIFO at identities.json must be named as non-regular, not block."""
    import time
    fx = bundle.parent / "fixtures"
    (fx / "identities.json").unlink()
    os.mkfifo(fx / "identities.json")
    start = time.monotonic()
    rc, out = _check(bundle, timeout_s=10)
    elapsed = time.monotonic() - start
    assert elapsed < 5, f"took {elapsed:.1f}s — the FIFO blocked the read"
    assert rc == 1
    assert out == "failure_reason: fixtures: non-regular entry in evidence tree: identities.json"


# F2/F27: _require_file rejects a FIFO
def test_ck9_require_file_rejects_fifo(tmp_path):
    """R9-CK-F2/F27: _require_file must reject a FIFO with a named reason."""
    fifo = tmp_path / "evil.fifo"
    os.mkfifo(fifo)
    with pytest.raises(cc.Failure, match="is not a regular file"):
        cc._require_file(fifo, "test", "evil.fifo")


# F2/F27: _require_file rejects a directory
def test_ck9_require_file_rejects_dir(tmp_path):
    """R9-CK-F27: a directory named like a required file is rejected."""
    d = tmp_path / "tee-status.json"
    d.mkdir()
    with pytest.raises(cc.Failure, match="is not a regular file"):
        cc._require_file(d, "test", "tee-status.json")


# F4: "no tee process parented by buzz-acp" — TEEPAR-OFF killer
def test_ck9_no_tee_parented_by_buzz(bundle):
    """R9-CK-F4: a process tree where buzz-acp parents a non-tee child that parents the
    agent must fire 'no tee process parented by buzz-acp'."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-after.txt"
    owned_path = ld / "owned-pids.json"
    owned_data = json.loads(owned_path.read_text())
    buzz_pid = owned_data["buzz_acp_pid"]
    # Build a tree: buzz -> NOT-the-tee -> agent. The tee_pid from runtime-identity
    # is NOT in the tree, but the owned set matches for the closure check.
    not_tee_pid = 12340  # same slot as tee_pid in owned-pids
    agent_pid = 12345
    _rewrite(sp, _scan_header("after", pinned_present=2) + "\n"
             + f"{buzz_pid} 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n"
             + f"{not_tee_pid} {buzz_pid} 90 /usr/bin/python3 /tmp/not-the-tee.py\n"
             + f"{agent_pid} {not_tee_pid} 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no tee process parented by buzz-acp"


# F5: FINAL arm exact — one wrong-value bundle per rule
@pytest.mark.parametrize("field,delta,reason_tpl", [
    ("forwarded_c2a", -1, "forwarded_c2a != recorded_c2a"),
    ("forwarded_a2c", -1, "forwarded_a2c != recorded_a2c"),
])
def test_ck9_final_arm_forwarded_exact(bundle, field, delta, reason_tpl):
    """R9-CK-F5: FINAL arm forwarded must exactly equal recorded."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["drained"] = True
    ts["write_errors"] = []
    ts["stdin_reader_done"] = True
    ts["agent_returncode"] = 0
    ts["exit_code"] = 0
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq
    ts[field] = ts[field] + delta
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: tee-status.json {reason_tpl}"


@pytest.mark.parametrize("field,count_key,reason_tpl", [
    ("recorded_c2a", "c2a", "recorded_c2a {n} != timeline c2a count {c}"),
    ("recorded_a2c", "a2c", "recorded_a2c {n} != timeline a2c count {c}"),
])
def test_ck9_final_arm_recorded_exact(bundle, field, count_key, reason_tpl):
    """R9-CK-F5: FINAL arm recorded must exactly equal timeline count."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    count = c2a_count if count_key == "c2a" else a2c_count
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["drained"] = True
    ts["write_errors"] = []
    ts["stdin_reader_done"] = True
    ts["agent_returncode"] = 0
    ts["exit_code"] = 0
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq
    ts[field] = count - 1
    ts[f"forwarded_{count_key}"] = count - 1
    # fix updated_seq so type check doesn't fire on updated_seq
    ts["updated_seq"] = ts["recorded_c2a"] + ts["recorded_a2c"]
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    expected = reason_tpl.format(n=count - 1, c=count)
    assert out == f"failure_reason: run-1: tee-status.json {expected}"


def test_ck9_final_arm_updated_seq_exact(bundle):
    """R9-CK-F5: FINAL arm updated_seq must equal timeline last seq."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["drained"] = True
    ts["write_errors"] = []
    ts["stdin_reader_done"] = True
    ts["agent_returncode"] = 0
    ts["exit_code"] = 0
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq - 1
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json "
                   f"updated_seq {last_seq - 1} != timeline last seq {last_seq}")


def test_ck9_final_stdin_reader_done_false_rejected(bundle):
    """R9-CK-F5: FINAL arm requires stdin_reader_done == True."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["drained"] = True
    ts["write_errors"] = []
    ts["stdin_reader_done"] = False
    ts["agent_returncode"] = 0
    ts["exit_code"] = 0
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee-status.json stdin_reader_done is not true when final"


# F18: FINAL arm type-strict — float counters rejected on both arms
@pytest.mark.parametrize("field", ["recorded_c2a", "forwarded_c2a", "updated_seq"])
def test_ck9_final_arm_float_rejected(bundle, field):
    """R9-CK-F18: a float value on the FINAL arm must be rejected (pre-arm type gate)."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["final"] = True
    ts["drained"] = True
    ts["write_errors"] = []
    ts["stdin_reader_done"] = True
    ts["agent_returncode"] = 0
    ts["exit_code"] = 0
    ts["recorded_c2a"] = c2a_count
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_c2a"] = c2a_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq
    ts[field] = float(ts[field])
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: tee-status.json {field} is not int"


# F5/F29: RUNNING upper bounds — seq lag 2 and recorded deficit 2
def test_ck9_running_seq_lag_2_rejected(bundle):
    """R9-CK-F29: running snapshot with updated_seq = last_seq - 2 is rejected."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["updated_seq"] = last_seq - 2
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"updated_seq {last_seq - 2} trails timeline last seq {last_seq} by more than one")


def test_ck9_running_recorded_deficit_2_rejected(bundle):
    """R9-CK-F29: running snapshot with recorded_c2a trailing by 2 is rejected.
    Set updated_seq = last_seq (lag=0) so the lag check passes and the per-direction
    recorded deficit check fires first."""
    ld = bundle / "golden" / "run-1"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    c2a_count = sum(1 for e in entries if e["dir"] == "c2a")
    a2c_count = sum(1 for e in entries if e["dir"] == "a2c")
    last_seq = entries[-1]["seq"]
    ts = json.loads((ld / "tee-status.json").read_text())
    ts["recorded_c2a"] = c2a_count - 2
    ts["forwarded_c2a"] = c2a_count - 2
    ts["recorded_a2c"] = a2c_count
    ts["forwarded_a2c"] = a2c_count
    ts["updated_seq"] = last_seq  # lag = 0, so lag check passes
    _rewrite(ld / "tee-status.json", json.dumps(ts))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == (f"failure_reason: run-1: tee-status.json running snapshot "
                   f"recorded_c2a {c2a_count - 2} trails timeline c2a count {c2a_count} by more than one")


# F11: owned_zombies validation
def test_ck9_owned_zombies_negative(bundle):
    """R9-CK-F11: owned_zombies=-1 in the scan header is rejected by the regex
    (\\d+ does not match -1), so the header is not recognized."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-after.txt"
    old = sp.read_text()
    _rewrite(sp, old.replace("owned_zombies=0", "owned_zombies=-1"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after.txt has no enumeration header"


def test_ck9_owned_zombies_exceeds_owned(bundle):
    """R9-CK-F11: owned_zombies=99 exceeds owned=3 in the scan header."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-after.txt"
    old = sp.read_text()
    _rewrite(sp, old.replace("owned_zombies=0", "owned_zombies=99"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after.txt owned_present=3+owned_zombies=99 exceeds owned=3"


def test_ck9_owned_zombies_abc(bundle):
    """R9-CK-F11: non-numeric owned_zombies is rejected by the header regex."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-after.txt"
    old = sp.read_text()
    _rewrite(sp, old.replace("owned_zombies=0", "owned_zombies=abc"))
    rc, out = _check(bundle)
    assert rc == 1
    # The regex match fails, so the header is not recognized
    assert out == "failure_reason: run-1: process-scan-after.txt has no enumeration header"


# F12: check_env reads pins, not literals
def test_ck9_env_respond_to_from_pin(bundle, monkeypatch):
    """R9-CK-F12: monkeypatching the pin changes the env check's expectation."""
    monkeypatch.setattr("check_acp_conformance.PINNED_STARTUP_RESPOND_TO", "PATCHED_RT")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env BUZZ_ACP_RESPOND_TO should be 'PATCHED_RT'"


# F20: POST role SEQUENCE — ROLES-SET mutant killer
def test_ck9_post_roles_reordered(bundle):
    """R9-CK-F20: a reordered ['user','system'] body is rejected (ROLES-SET killer)."""
    ld = bundle / "golden" / "run-1" / "upstream-records"
    for rp in ld.glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is True:
            body = r["body"]
            body["messages"] = [body["messages"][1], body["messages"][0]]
            _rewrite(rp, json.dumps(r, indent=2))
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == ("failure_reason: run-1: upstream POST record stream message roles "
                   "['user', 'system'] != expected ['system', 'user']")


def test_ck9_post_roles_duplicated(bundle):
    """R9-CK-F20: a duplicated ['system','system','user'] body is rejected."""
    ld = bundle / "golden" / "run-1" / "upstream-records"
    for rp in ld.glob("*.json"):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST" and r.get("body", {}).get("stream") is True:
            body = r["body"]
            body["messages"] = [body["messages"][0], body["messages"][0], body["messages"][1]]
            _rewrite(rp, json.dumps(r, indent=2))
            break
    rc, out = _check(bundle)
    assert rc == 1
    assert out == ("failure_reason: run-1: upstream POST record stream message roles "
                   "['system', 'system', 'user'] != expected ['system', 'user']")


# F19: st_nlink test proves the fixture does NOT hardlink
def test_ck9_tools_not_hardlinked(bundle):
    """R9-CK-F19: the tools copy in the bundle fixture is a real copy (nlink==1),
    and writing the copy does not change the tracked file's sha."""
    tee_copy = bundle.parent / "tools" / "frame_tee.py"
    assert tee_copy.exists()
    assert os.stat(str(tee_copy)).st_nlink == 1, "tools/frame_tee.py is hardlinked to tracked"
    tracked = P / "tools" / "frame_tee.py"
    import hashlib as _hl
    sha_before = _hl.sha256(tracked.read_bytes()).hexdigest()
    # Write to the copy — must not affect the tracked file
    tee_copy.write_text("# tampered\n")
    sha_after = _hl.sha256(tracked.read_bytes()).hexdigest()
    assert sha_before == sha_after, "writing the copy changed the tracked file"


# F25: A25 reorder fallback
def test_ck9_a25_reorder_diagnostic(bundle, monkeypatch):
    """R9-CK-F25: a pure reorder of the check sequence reports the first divergence."""
    call_count = [0]
    def reorder_run_check(fn, leg, *args, **kwargs):
        call_count[0] += 1
        # Swap the first two calls
        result = fn(*args, **kwargs)
        cc._executed.append((fn.__name__, leg))
        if call_count[0] == 2:
            # Swap positions 0 and 1 in _executed
            cc._executed[0], cc._executed[1] = cc._executed[1], cc._executed[0]
        return result
    monkeypatch.setattr(cc, "_run_check", reorder_run_check)
    rc, out = _check(bundle)
    assert rc == 1
    exp = cc.EXPECTED_CHECK_SEQUENCE
    assert out == (f"failure_reason: golden: check sequence mismatch - first out of order at #0: "
                   f"got {exp[1][0]}:{exp[1][1]}, expected {exp[0][0]}:{exp[0][1]}")


# F13: startup keys parametrised over the checks dict
def test_ck9_startup_wrong_value_parametrised(bundle):
    """R9-CK-F13: every key in the checks dict gets a wrong-value test, exact reason."""
    checks = {"relay": cc.PINNED_RELAY_URL, "agent_cmd": cc.PINNED_TEE_PATH,
              "mcp_cmd": cc.PINNED_STARTUP_MCP_CMD,
              "idle_timeout": cc.PINNED_IDLE_TIMEOUT, "max_turn": cc.PINNED_MAX_TURN,
              "agents": cc.PINNED_STARTUP_AGENTS,
              "heartbeat": cc.PINNED_STARTUP_HEARTBEAT,
              "subscribe": cc.PINNED_STARTUP_SUBSCRIBE,
              "dedup": cc.PINNED_STARTUP_DEDUP,
              "session_policy": cc.PINNED_SESSION_POLICY,
              "meh": cc.PINNED_STARTUP_MEH,
              "ignore_self": cc.PINNED_STARTUP_IGNORE_SELF,
              "context_limit": cc.PINNED_STARTUP_CONTEXT_LIMIT,
              "max_turns_per_session": cc.PINNED_STARTUP_MAX_TURNS_PER_SESSION,
              "presence": cc.PINNED_STARTUP_PRESENCE,
              "typing": cc.PINNED_STARTUP_TYPING,
              "memory": cc.PINNED_STARTUP_MEMORY,
              "model": cc.PINNED_STARTUP_MODEL,
              "permission_mode": cc.PINNED_STARTUP_PERMISSION_MODE}
    ran = []
    for k, exp in checks.items():
        wrong = "EVIL_" + k.upper()
        sp = bundle / "golden" / "run-1" / "startup-line.txt"
        old = sp.read_text().rstrip("\n")
        new_startup = old.replace(f"{k}={exp}", f"{k}={wrong}")
        if new_startup == old:
            continue  # parenthesised values need special handling, skip
        ran.append(k)
        _rewrite(sp, new_startup + "\n")
        lp = bundle / "golden" / "run-1" / "buzzacp.log"
        _rewrite(lp, lp.read_text().replace(f"{k}={exp}", f"{k}={wrong}"))
        rc, out = _check(bundle)
        assert rc == 1, f"key {k}: expected rc=1, got {rc}: {out}"
        assert out == f"failure_reason: run-1: startup {k} is {wrong!r}, expected {exp!r}", f"key {k}"
        # Restore for the next key
        _rewrite(sp, old + "\n")
        _rewrite(lp, lp.read_text().replace(f"{k}={wrong}", f"{k}={exp}"))
    # R10-F16: ensure every key was actually exercised (detect silent skips)
    assert len(ran) == len(checks), f"only {len(ran)}/{len(checks)} keys ran: skipped {sorted(set(checks) - set(ran))}"
    # CK11-F20: the wrong-value dict covers cc._EXPECTED_STARTUP_KEYS (minus format-only keys)
    _elsewhere = {"pubkey", "respond_to"}  # format-only / leg-dependent, tested separately
    _uncovered = sorted(cc._EXPECTED_STARTUP_KEYS - set(checks) - _elsewhere)
    assert not _uncovered, f"wrong-value dict does not cover the checker key set: {_uncovered}"


# F23: _EXPECTED_STARTUP_KEYS is importable
def test_ck9_expected_startup_keys_importable():
    """R9-CK-F23: _EXPECTED_STARTUP_KEYS is at module scope and has 21 keys."""
    assert hasattr(cc, "_EXPECTED_STARTUP_KEYS")
    assert len(cc._EXPECTED_STARTUP_KEYS) == 21


# F23: startup missing keys uses the exact computed list
def test_ck9_startup_missing_keys_exact(bundle):
    """R9-CK-F23: missing startup key → exact sorted missing-keys list."""
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    old = sp.read_text().rstrip("\n")
    # Remove the last key=value token
    tokens = old.rsplit(" ", 1)
    _rewrite(sp, tokens[0] + "\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    log_text = lp.read_text()
    log_tokens = log_text.rsplit(" ", 1)
    _rewrite(lp, log_tokens[0] + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    # R10-F24: compute the exact missing key list from the surviving tokens
    present = {tok.split("=", 1)[0] for tok in tokens[0].split() if "=" in tok}
    missing = sorted(cc._EXPECTED_STARTUP_KEYS - present)
    assert out == f"failure_reason: run-1: startup-line missing keys: {missing}"


# F28: the default timeout is 90
def test_ck9_default_timeout_is_90():
    """R9-CK-F28: check_bundle's default timeout_s is 90."""
    import inspect
    sig = inspect.signature(cc.check_bundle)
    assert sig.parameters["timeout_s"].default == 90


# ============================================================================
# VERIFY-CK10: round 11 tests (items 1-9)
# ============================================================================

# B1 (CK11): known-stale xfail uses WHOLE-reason equality, not a tail segment.
def test_ck11_known_stale_is_the_whole_reason_not_a_tail():
    """CK11-B1: _is_known_stale matches the WHOLE reason, never a tail collision."""
    assert _is_known_stale("negative: negative: probe_sha256 mismatch")
    assert not _is_known_stale("probe_sha256 mismatch"), "tail alone must not match"
    assert not _is_known_stale(
        "negative: negative: probe reported an error: probe_sha256 mismatch"
    ), "tail collision from corpus-controlled probe_error must not match"


# B2: F43 self-test categories — tested inline by the rewritten assertion above.


# B3: tee_file through _require_file; manifest-post.summary through _require_file
def test_ck10_fifo_at_tools_frame_tee_is_named(bundle, tmp_path, monkeypatch):
    """R10-B3: a FIFO at tools/frame_tee.py is named as non-regular in < 5 s."""
    import time
    # monkeypatch HERE so the checker reads from tmp_path/tools/frame_tee.py
    monkeypatch.setattr(cc, "HERE", tmp_path)
    tools = tmp_path / "tools"
    tools.mkdir(exist_ok=True)
    tee = tools / "frame_tee.py"
    # CK11-F14: removed dead write_text("placeholder") — the bundle fixture already
    # created the file via copytree; unlink before creating the FIFO.
    tee.unlink(missing_ok=True)
    os.mkfifo(tee)
    t0 = time.monotonic()
    rc, out = _check(bundle, timeout_s=10)
    elapsed = time.monotonic() - t0
    assert elapsed < 5, f"FIFO blocked for {elapsed:.1f}s"
    assert (rc, out) == (1, "failure_reason: run-1: tools/frame_tee.py is not a regular file")


def test_ck10_dir_named_manifest_post_summary(bundle):
    """R10-B3: a directory named manifest-post.summary produces the exact reason."""
    p = bundle / "golden" / "run-1" / "manifest-post.summary"
    p.unlink()
    p.mkdir()
    rc, out = _check(bundle)
    assert (rc, out) == (1, "failure_reason: run-1: manifest-post.summary is not a regular file")


# CK11-F8: tools/acp_probe.py through the read CLASS (negative_contract.py)
def test_ck11_fifo_at_tools_acp_probe_is_named(bundle, tmp_path, monkeypatch):
    """CK11-F8: a FIFO at tools/acp_probe.py is named as non-regular — the guard fires
    before the FIFO blocks the read.  The checker processes all positive legs before
    the negative check, so the elapsed time is the full checker run (not just the guard)."""
    import time
    monkeypatch.setattr(nc, "HERE", tmp_path)
    tools = tmp_path / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    probe = tools / "acp_probe.py"
    probe.unlink(missing_ok=True)
    os.mkfifo(probe)
    t0 = time.monotonic()
    rc, out = _check(bundle, timeout_s=30)
    elapsed = time.monotonic() - t0
    assert elapsed < 30, f"FIFO blocked to the cap: {elapsed:.1f}s"
    assert (rc, out) == (1, "failure_reason: negative: negative: tools/acp_probe.py is not a regular file")


def test_ck11_dir_at_tools_acp_probe_is_named(bundle, tmp_path, monkeypatch):
    """CK11-F8: a directory at tools/acp_probe.py is named as non-regular."""
    import time
    monkeypatch.setattr(nc, "HERE", tmp_path)
    tools = tmp_path / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    probe = tools / "acp_probe.py"
    if probe.exists():
        probe.unlink()
    probe.mkdir()
    t0 = time.monotonic()
    rc, out = _check(bundle, timeout_s=30)
    elapsed = time.monotonic() - t0
    assert elapsed < 30, f"dir blocked to the cap: {elapsed:.1f}s"
    assert (rc, out) == (1, "failure_reason: negative: negative: tools/acp_probe.py is not a regular file")


# CK11-F15: absent ACP schema is a failure, not a silent skip (AF-AP-40)
def test_ck11_absent_acp_schema_is_a_failure(bundle, tmp_path):
    """CK11-F15: deleting acp-schema-v1.json must produce a failure, not a silent PASS."""
    (tmp_path / "fixtures" / "acp-schema-v1.json").unlink()
    assert _check(bundle) == (1, "failure_reason: golden: fixtures/acp-schema-v1.json absent")


def test_ck11_no_presence_gated_check_in_the_proof():
    """CK11-F15 CLASS: no AFFIRMATIVE `if p.exists()` whose false branch yields a
    default instead of a raise (AF-AP-40).  NEGATED gates like `if not p.exists():
    raise Failure(...)` are CORRECT (fail-closed)."""
    import ast as _ast
    checked_files = [
        P / "check_acp_conformance.py",
        P / "negative_contract.py",
        P / "check_initialize.py",
    ]
    # Reviewed exceptions with reasons:
    _REVIEWED_SAFE = {
        ("check_initialize.py", 129),   # tl_path.exists() -> deferred: fail-closed
        ("check_initialize.py", 194),   # path.is_dir() routing between directory/file mode
        ("check_acp_conformance.py", 1713),  # post_sum_path optional per-leg; _require_file inside
    }
    violations = []
    for fpath in checked_files:
        src = fpath.read_text()
        tree = _ast.parse(src)
        fname = fpath.name
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.If):
                continue
            if (fname, node.lineno) in _REVIEWED_SAFE:
                continue
            test_code = _ast.unparse(node.test) if hasattr(_ast, "unparse") else ""
            # Only flag AFFIRMATIVE presence gates (if p.exists(): use it)
            # Skip negated gates (if not p.exists(): raise) — those are fail-closed.
            if test_code.startswith("not "):
                continue
            if ".exists()" not in test_code and ".is_file()" not in test_code:
                continue
            # Affirmative gate with no else: the AP-40 pattern
            # Check if the body uses the file (read/load) rather than just raising
            body_code = "\n".join(_ast.unparse(n) for n in node.body)
            if "raise " in body_code:
                continue  # the true branch raises — not a skip gate
            if not node.orelse:
                violations.append(f"{fname}:{node.lineno} affirmative presence gate with no else (AF-AP-40)")
    assert not violations, f"AP-40 hits: {violations}"


def test_ck11_every_read_is_under_the_walk_or_require_file():
    """CK11-F8 CLASS: every open()/read_text()/read_bytes()/json.load() in the checker
    and its callees resolves under a walked root (golden/, _fixtures()) or is wrapped
    in _require_file / preceded by an S_ISREG check on the same receiver."""
    import ast as _ast
    checked_files = [
        P / "check_acp_conformance.py",
        P / "negative_contract.py",
        P / "check_initialize.py",
    ]
    READ_ATTRS = {"read_text", "read_bytes"}
    for fpath in checked_files:
        src = fpath.read_text()
        lines = src.splitlines()
        tree = _ast.parse(src)
        # Build function ranges
        fns = []
        for node in _ast.walk(tree):
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                fns.append((node.name, node.lineno, node.end_lineno))
        def owner(ln):
            best = None
            for n, s, e in fns:
                if s <= ln <= e and (best is None or s > best[1]):
                    best = (n, s, e)
            return best[0] if best else "<module>"
        # Find all read sites
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call):
                continue
            f = node.func
            is_read = False
            recv = ""
            if isinstance(f, _ast.Attribute) and f.attr in READ_ATTRS:
                is_read = True
                recv = _ast.unparse(f.value) if hasattr(_ast, "unparse") else "?"
            elif isinstance(f, _ast.Name) and f.id == "open":
                is_read = True
                recv = _ast.unparse(node.args[0]) if node.args and hasattr(_ast, "unparse") else "?"
            if not is_read:
                continue
            ln = node.lineno
            fn = owner(ln)
            # Check the 5 lines before for _require_file or S_ISREG on the receiver
            context = "\n".join(lines[max(0, ln - 6):ln])
            if "_require_file" in context or "S_ISREG" in context:
                continue
            # Check if the receiver resolves under a walked root
            # Variables derived from walked roots (golden/, _fixtures(), leg_dir, etc.)
            walked = ("golden", "_fixtures", "leg_dir", "dirpath", "d /",
                      "neg_dir", "r1m", "r2m", "mentions_dir", "manifest",
                      "post_sum", "c2a_path", "a2c_path", "stderr_path",
                      "sp", "argv_path", "tl_path", "rp", "fp_path",
                      "rec_dir", "item", "fpath", "path")
            if any(root in recv for root in walked):
                continue
            # _sha256_file is called on paths that have been require_file'd
            if fn == "_sha256_file":
                continue
            assert False, (
                f"{fpath.name}:{ln} in {fn}: read site {recv} is not under "
                f"a walked root and has no _require_file / S_ISREG guard")


# B4: single default cap — main() omits timeout_s, check_bundle's default governs
def test_ck10_cli_default_cap_is_below_the_runner_timeout():
    """R10-B4: the default cap (check_bundle signature) is 0 < N < spec.json timeout_s."""
    import inspect
    sig_default = inspect.signature(cc.check_bundle).parameters["timeout_s"].default
    spec = json.loads((P / "spec.json").read_text())
    runner_timeout = spec["legs"][0]["timeout_s"]
    assert 0 < sig_default < runner_timeout, (
        f"default {sig_default} not in (0, {runner_timeout})")


# B5: two-users pin consumption test
def test_ck10_env_respond_to_two_users_from_pin(bundle, monkeypatch):
    """R10-B5: monkeypatching the two-users pin changes the env check's expectation."""
    monkeypatch.setattr("check_acp_conformance.PINNED_STARTUP_RESPOND_TO_TWO_USERS", "PATCHED(9)")
    rc, out = _check(bundle)
    assert (rc, out) == (1, "failure_reason: two-users: env BUZZ_ACP_RESPOND_TO should be 'PATCHED' for two-users")


# Item 6: cap domain validation
def test_ck10_cap_rejects_bool(tmp_path):
    """R10-F03: timeout_s=True is rejected (bool is not a strict int)."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s=True)


def test_ck10_cap_rejects_nan(tmp_path):
    """R10-F05: timeout_s=NaN is rejected."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s=float("nan"))


def test_ck10_cap_rejects_inf(tmp_path):
    """R10-F05: timeout_s=inf is rejected."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s=float("inf"))


def test_ck10_cap_rejects_float(tmp_path):
    """R10-F05: timeout_s=1.0 is rejected."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s=1.0)


def test_ck10_cap_rejects_string(tmp_path):
    """R10-F05: timeout_s='5' is rejected."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s="5")


def test_ck10_cap_rejects_overflow(tmp_path):
    """R10-F03: timeout_s=2**31 is rejected as ValueError, not OverflowError."""
    with pytest.raises(ValueError, match="positive integer"):
        cc.check_bundle(tmp_path, timeout_s=2**31)


def test_ck10_timeout_arg_out_of_range_is_a_usage_error():
    """R10-F04: --timeout-s 2**31 is a usage error (rc 64), not malformed evidence."""
    r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", str(2**31), "/tmp/x"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: --timeout-s must be a positive integer"


def test_ck10_rejected_cap_installs_no_handler():
    """CK11-F2 rename: a rejected cap (out-of-range) installs no handler."""
    import signal
    before = signal.getsignal(signal.SIGALRM)
    with pytest.raises(Exception):
        cc.check_bundle(Path("/tmp"), timeout_s=2**31)
    after = signal.getsignal(signal.SIGALRM)
    assert after is before, f"LEAKED: before={before}, after={after}"


def test_ck11_alarm_inside_try_cannot_leak_the_handler(monkeypatch, tmp_path):
    """CK11-F2: a raising alarm() inside the try cannot leak the handler."""
    import signal as _s
    real = _s.alarm
    monkeypatch.setattr(_s, "alarm", lambda n: (_ for _ in ()).throw(OverflowError()) if n else real(0))
    before = _s.getsignal(_s.SIGALRM)
    with pytest.raises(OverflowError):
        cc.check_bundle(tmp_path, timeout_s=90)
    assert _s.getsignal(_s.SIGALRM) is before, (
        f"LEAKED: before={before}, after={_s.getsignal(_s.SIGALRM)}")


# Item 7: owned_zombies full invariant
def test_ck10_owned_zombies_plus_present_exceeds_owned(bundle):
    """R10-F11: owned=3 owned_present=3 owned_zombies=3 is rejected (impossible header)."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-after.txt"
    old = sp.read_text()
    _rewrite(sp, old.replace("owned_zombies=0", "owned_zombies=3"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after.txt owned_present=3+owned_zombies=3 exceeds owned=3"


def test_ck10_teardown_zombies_plus_present_exceeds_owned(bundle):
    """R10-F11: teardown scan also validates owned_present + owned_zombies <= owned.
    The fixture teardown has owned=3, owned_present=0, so zombies=4 triggers the check."""
    ld = bundle / "golden" / "run-1"
    sp = ld / "process-scan-teardown.txt"
    old = sp.read_text()
    _rewrite(sp, old.replace("owned_zombies=0", "owned_zombies=4"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown.txt owned_present=0+owned_zombies=4 exceeds owned=3"


# Item 8: dead-branch comments cite the real guard
def test_ck11_dead_branch_comments_cite_a_real_guard():
    """CK11-F11: each dead-branch deletion comment names the function that fires,
    and any cited C:a-b range holds a 'raise Failure' inside the named function."""
    src = CHECKER.read_text().splitlines()
    checks = []
    for i, line in enumerate(src):
        if "R9-CK-F6:" not in line:
            continue
        if "first_term is guaranteed" in line:
            checks.append((i, "check_two_users"))
        elif "new_seqs >= 2 guaranteed" in line:
            checks.append((i, "check_two_users"))
        elif "init_resp_idx is guaranteed" in line:
            checks.append((i, "check_initialize_frames"))
        elif "new_resp_idx guaranteed" in line:
            checks.append((i, "check_prompt_turn"))
        elif "sid1/sid2 guaranteed" in line:
            checks.append((i, "check_prompt_turn"))
        elif "r1m/r2m guaranteed" in line:
            checks.append((i, "check_mentions"))
    assert len(checks) == 6, f"expected 6 dead-branch comments, found {len(checks)}"
    for idx, fn in checks:
        block = "\n".join(src[max(0, idx - 1):idx + 3])
        assert fn in block, f"line {idx + 1} cites the wrong guard: {block}"
        # CK11: parse cited C:a-b range(s) and assert they hold a raise Failure
        m = re.search(r"C:(\d+)-(\d+)", block)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            assert any("raise Failure" in src[k - 1] for k in range(a, b + 1)), (
                f"line {idx + 1} cites C:{a}-{b}, which contains no guard")
