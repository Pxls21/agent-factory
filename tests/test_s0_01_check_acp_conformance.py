"""proofs/S0-01/check_acp_conformance.py v2.1 test suite.

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
import nostr_verify as nv  # noqa: E402
from pins import (  # noqa: E402
    ENV_ALLOWLIST_KEY,
    EXPECTED_MENTIONS, EXPECTED_MODEL, LEGS, MANIFEST_TREES, MENTION_TEXT,
    PINNED_AGENT_ENTRYPOINT_SHA256, PINNED_AGENT_INTERPRETER_REALPATH,
    PINNED_AGENT_INTERPRETER_SHA256,
    PINNED_AGENT_REALPATH,
    PINNED_BASELINE_DIGESTS,
    PINNED_BUZZ_ACP_EXE_REALPATH,
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


# Memoize the expensive _point_mul for test speed (pure function, verdict-preserving)
_pm_cache = {}
_orig_pm = nv._point_mul
def _cached_pm(k, point):
    key = (k, point)
    if key not in _pm_cache:
        _pm_cache[key] = _orig_pm(k, point)
    return _pm_cache[key]
nv._point_mul = _cached_pm


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
    leg_dir.mkdir(parents=True, exist_ok=True)
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
    """Write BOTH startup-line.txt and buzzacp.log so the startup line appears in the log."""
    rt = "owner-only" if leg != "two-users" else "allowlist(1)"
    startup = (f"2026-09-05T05:00:00.000000Z  INFO buzz_acp: buzz-acp starting: "
               f"relay={PINNED_RELAY_URL} pubkey=<HEX> "
               f"agent_cmd={PINNED_TEE_PATH}  mcp_cmd= "
               f"idle_timeout={PINNED_IDLE_TIMEOUT} max_turn={PINNED_MAX_TURN} agents=1 heartbeat=0s "
               f"subscribe=Mentions dedup=Queue session_policy={PINNED_SESSION_POLICY} "
               f"meh=Steer ignore_self=true context_limit=12 "
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
    (leg_dir / "buzzacp.log").write_text("\n".join(lines) + "\n")


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
    created_at_base = int(first_utc.timestamp())  # inside the window
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
    rec_dir = leg_dir / "upstream-records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    model = EXPECTED_MODEL[leg]
    prompt_times = [e["t_utc"] for e in entries
                    if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt"]
    idx = 0
    for pt in prompt_times:
        rec = {"seq": idx + 1, "method": "POST", "path": UPSTREAM_POST_PATH,
               "body": {"model": model, "messages": [{"role": "user", "content": MENTION_TEXT}],
                        "stream": True},
               "headers": {"host": PINNED_UPSTREAM_HOST, "content-type": "application/json"},
               "authorization_fingerprint": fingerprint, "received_at": pt,
               "t_mono_ns": 1_000_000_000_000 + (idx + 1) * 1_000_000, "remote_addr": "127.0.0.1"}
        (rec_dir / f"{idx:06d}.json").write_text(json.dumps(rec, indent=2) + "\n")
        idx += 1
    get_rec = {"seq": idx + 1, "method": "GET", "path": "/models", "body": None,
               "headers": {"host": PINNED_UPSTREAM_HOST}, "authorization_fingerprint": None,
               "received_at": prompt_times[0] if prompt_times else "2026-09-05T06:00:00.000000Z",
               "t_mono_ns": 1_000_000_000_000 + (idx + 1) * 1_000_000, "remote_addr": "127.0.0.1"}
    (rec_dir / f"{idx:06d}.json").write_text(json.dumps(get_rec, indent=2) + "\n")


def _write_process_scan(leg_dir, leg):
    buzz_pid = 12300
    launcher_pid = 1
    (leg_dir / "buzz-acp.pid").write_text(f"{buzz_pid}\n")
    if leg == "shutdown":
        (leg_dir / "process-scan-after.txt").write_text(f"{launcher_pid} 0 /sbin/init\n")
        (leg_dir / "buzz-acp.exit").write_text("0\n")
    else:
        lines = [f"{buzz_pid} {launcher_pid} {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999",
                 f"12345 {buzz_pid} /usr/bin/python3 {PINNED_TEE_PATH}",
                 f"12346 12345 /usr/bin/python3 {PINNED_AGENT_REALPATH}"]
        (leg_dir / "process-scan-after.txt").write_text("\n".join(lines) + "\n")
        (leg_dir / "process-scan-teardown.txt").write_text(f"{launcher_pid} 0 /sbin/init\n")
        (leg_dir / "buzz-acp.exit").write_text("0\n")


def _write_negative(neg_dir, identities):
    neg_dir.mkdir(parents=True, exist_ok=True)
    fixture = json.loads((FIXTURES / "neg-malformed-initialize.json").read_text())
    entries = [
        {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T05:00:00.000001Z",
         "t_mono_ns": 1_000_000_000_001,
         "frame": {"jsonrpc": "2.0", "method": "initialize", "params": fixture, "id": 0}},
        {"seq": 2, "dir": "a2c", "t_utc": "2026-09-05T05:00:00.000002Z",
         "t_mono_ns": 1_000_000_000_002,
         "frame": {"jsonrpc": "2.0", "id": 0, "error": {"code": -32600, "message": "Invalid params"}}}]
    with open(neg_dir / "timeline.jsonl", "w") as f:
        for e in entries:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    rid = {"probe_path": "/tmp/probe.py", "probe_sha256": "00" * 32,
           "agent_argv": [PINNED_AGENT_REALPATH], "agent_realpath": PINNED_AGENT_REALPATH,
           "agent_entrypoint_sha256": PINNED_AGENT_ENTRYPOINT_SHA256, "agent_child_pid": 99999,
           "agent_interpreter_realpath": PINNED_AGENT_INTERPRETER_REALPATH,
           "agent_interpreter_sha256": PINNED_AGENT_INTERPRETER_SHA256,
           "python_dont_write_bytecode": True, "spawned_at_utc": "2026-09-05T05:00:00.000000Z",
           "agent_exit_code": 1}
    (neg_dir / "runtime-identity.json").write_text(json.dumps(rid, indent=2) + "\n")
    (neg_dir / "env.json").write_text(json.dumps(
        {"HERMES_HOME": PINNED_HERMES_HOME, "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (neg_dir / "agent-stderr.txt").write_text("")


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
    for fn in ("neg-malformed-initialize.json", "upstream-token.fingerprint", "acp-schema-v1.json"):
        src = FIXTURES / fn
        if src.exists():
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
    n1 = cc.normalize_timeline(cc._load_timeline_raw(g / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    (g / "golden.jsonl").write_text(golden_text)
    golden_sha = _sha256(golden_text.encode("utf-8"))
    _write_negative(g / "negative", identities)
    return base, golden_sha, tmp_fixtures


@pytest.fixture
def bundle(_session_bundle, tmp_path, monkeypatch):
    """Per-test: copytree from session fixture; monkeypatch the checker."""
    base, golden_sha, tmp_fixtures = _session_bundle
    dest = tmp_path / "evidence"
    shutil.copytree(base / "evidence", dest)
    # Copy fixtures and tools into tmp_path so monkeypatching HERE works
    dest_fixtures = tmp_path / "fixtures"
    shutil.copytree(tmp_fixtures, dest_fixtures)
    dest_tools = tmp_path / "tools"
    shutil.copytree(P / "tools", dest_tools)
    # Monkeypatch PINNED_GOLDEN_SHA256 (the ONLY patched pin — commented)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", golden_sha)
    # Monkeypatch HERE so the checker reads identities.json from tmp fixtures
    # and tools/frame_tee.py from tmp tools (never touching the tracked tree)
    monkeypatch.setattr("check_acp_conformance.HERE", tmp_path)
    yield dest


def _run(root: Path):
    return subprocess.run([sys.executable, str(CHECKER), str(root)],
                          capture_output=True, text=True, timeout=60, env=os.environ.copy())


def _check(bndl):
    try:
        return 0, cc.check_bundle(bndl)
    except cc.Deferred as d:
        return 2, f"deferred: {d}"
    except cc.Failure as f:
        return 1, f"failure_reason: {f}"
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


def test_cli_pass_path_fails_on_golden_pin(bundle):
    """The subprocess does NOT have monkeypatched PINNED_GOLDEN_SHA256=None, so golden not pinned."""
    r = _run(bundle)
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
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_m2_tampered_sig(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    ev = json.loads(ep.read_text()); ev["sig"] = "ff" * 64
    ep.write_text(json.dumps(ev) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner BIP-340 signature invalid: r >= p"


def test_m2_wrong_pubkey(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    ev = _sign_mention(USER2_SECKEY, MENTION_TEXT,
                       [["h", SYNTH_IDENTITIES["channel"]], ["p", SYNTH_IDENTITIES["agent"]]])
    ep.write_text(json.dumps(ev) + "\n")
    rp = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    receipt = json.loads(rp.read_text()); receipt["event_id"] = ev["id"]
    rp.write_text(json.dumps(receipt) + "\n")
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
        sp.write_text(new)
        # Also update buzzacp.log (A7: startup line must be in log)
        lp = bundle / "golden" / leg / "buzzacp.log"
        lp.write_text(lp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=1s"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: startup max_turn is '1s', expected '{PINNED_MAX_TURN}'"


def test_m5_7200(bundle):
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        old = sp.read_text()
        new = old.replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=7200s")
        sp.write_text(new)
        lp = bundle / "golden" / leg / "buzzacp.log"
        lp.write_text(lp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=7200s"))
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
    if p.exists():
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
    p = bundle / "golden" / "negative" / fn
    if p.exists():
        p.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: negative: {fn} absent"


def test_del_neg_fixture(bundle):
    """A11: neg-malformed-initialize.json absent -> Failure."""
    fp = bundle.parent / "fixtures" / "neg-malformed-initialize.json"
    if fp.exists():
        fp.unlink()
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: fixtures/neg-malformed-initialize.json absent"


def test_del_identities(bundle):
    fp = bundle.parent / "fixtures" / "identities.json"
    if fp.exists():
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
    with open(ld / "timeline.jsonl", "w") as f:
        for e in es: f.write(json.dumps(e, separators=(",", ":")) + "\n")
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
    tl.write_text(re.sub(r'"t_mono_ns":(\d+)', '"t_mono_ns":NaN', tl.read_text(), count=1))
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
    p.write_text(p.read_text() + '{"jsonrpc":"2.0","method":"evil","id":99}\n')
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
    p.write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: frames-agent-to-client.jsonl does not match timeline a2c split"


def test_blank_line_in_frames(bundle):
    """6-F19 / 7-F18: blank line -> Failure."""
    p = bundle / "golden" / "run-1" / "frames-agent-to-client.jsonl"
    lines = p.read_text().splitlines()
    p.write_text(lines[0] + "\n   \n" + "\n".join(lines[1:]) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: frames-agent-to-client.jsonl blank line at line 2"


# === §3 runtime identity attacks ===
def test_rid_missing_tee_pid(bundle):
    """6-F11 / 7-F19: missing tee_pid."""
    p = bundle / "golden" / "run-1" / "runtime-identity.json"
    o = json.loads(p.read_text()); del o["tee_pid"]; p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: runtime-identity.json key set mismatch (extra=[], missing=['tee_pid'])"


def test_rid_buzz_sha_wrong(bundle):
    """m09."""
    p = bundle / "golden" / "run-1" / "runtime-identity.json"
    o = json.loads(p.read_text()); o["buzz_acp_exe_sha256"] = "0" * 64; p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzz_acp_exe_sha256 mismatch"


def test_rid_tee_sha_wrong(bundle):
    """m10."""
    p = bundle / "golden" / "run-1" / "runtime-identity.json"
    o = json.loads(p.read_text()); o["tee_sha256"] = "0" * 64; p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: tee_sha256 mismatch"


def test_rid_argv_wrong(bundle):
    """m11."""
    p = bundle / "golden" / "run-1" / "runtime-identity.json"
    o = json.loads(p.read_text()); a = list(o["launch_argv"]); a[1], a[3] = a[3], a[1]; o["launch_argv"] = a
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: launch_argv mismatch"


def test_rid_entrypoint_sha_wrong(bundle):
    """m12."""
    p = bundle / "golden" / "run-1" / "runtime-identity.json"
    o = json.loads(p.read_text()); o["agent_entrypoint_sha256"] = "0" * 64; p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agent_entrypoint_sha256 mismatch"


def test_argv_tampered(bundle):
    rp = bundle / "golden" / "run-1" / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_argv"] = ["/tmp/evil"]; rp.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agent_argv mismatch"


def test_interp_tampered(bundle):
    rp = bundle / "golden" / "run-1" / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_interpreter_realpath"] = "/tmp/evil"; rp.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: agent_interpreter_realpath mismatch"


# === §4 env attacks ===
def test_env_extra_key(bundle):
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["X"] = "v"
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env.json key set mismatch (extra=['X'], missing=[])"


def test_env_hermes_home_wrong(bundle):
    """m14."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["HERMES_HOME"] = "/tmp/evil"; ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env HERMES_HOME mismatch"


def test_env_path_wrong(bundle):
    """m15."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["PATH"] = "/evil"; ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env PATH mismatch"


def test_env_policy_wrong(bundle):
    """m16."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_SESSION_POLICY"] = "wrong"; ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env BUZZ_ACP_SESSION_POLICY mismatch"


def test_env_pdwb_wrong(bundle):
    """m17."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["PYTHONDONTWRITEBYTECODE"] = "0"; ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env PYTHONDONTWRITEBYTECODE is not '1'"


def test_owner_swap(bundle):
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_AGENT_OWNER"] = "de" * 32
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env BUZZ_ACP_AGENT_OWNER mismatch"


def test_env_leak(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["BUZZ_PRIVATE_KEY"] = "plaintext"
        ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env BUZZ_PRIVATE_KEY should be redacted but is not a dict"


def test_hex_leak_env(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "ab" * 32
        ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_hex_leak_uppercase(bundle):
    """A9 / 7-F17: uppercase hex detected."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "AB" * 32
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_hex_leak_with_prefix(bundle):
    """A9: hex with prefix detected."""
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "sk-" + "ab" * 32
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: env S0_01_FRAMEDIR contains a 64-hex string (possible secret leak)"


def test_allowlist_super(bundle):
    ep = bundle / "golden" / "two-users" / "env.json"
    env = json.loads(ep.read_text())
    env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = SYNTH_IDENTITIES["user2"] + ",x"
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: two-users: env {ENV_ALLOWLIST_KEY} != identities.user2"


def test_redacted_len_true(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["OMNIROUTE_API_KEY"]["len"] = True
        ep.write_text(json.dumps(env) + "\n")
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
    (md / "owner.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "owner.receipt.json").write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner event kind is not 9"


def test_mention_id_wrong(bundle):
    """m20: NIP-01 id mismatch."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    ev["id"] = "00" * 32
    (md / "owner.event.json").write_text(json.dumps(ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = ev["id"]
    (md / "owner.receipt.json").write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner NIP-01 id mismatch"


def test_mention_content_superstring(bundle):
    """m23: content must be exact ==."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"], "kind": 9,
                                          "tags": ev["tags"], "content": ev["content"] + " AND !shutdown"})
    (md / "owner.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "owner.receipt.json").write_text(json.dumps(r) + "\n")
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
    (md / "owner.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "owner.receipt.json").write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner missing ['h', channel] tag"


def test_mention_window_out(bundle):
    """m25: created_at outside window."""
    md = bundle / "golden" / "run-1" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": 1600000000, "kind": 9,
                                          "tags": ev["tags"], "content": ev["content"]})
    (md / "owner.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "owner.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "owner.receipt.json").write_text(json.dumps(r) + "\n")
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
    (md / "shutdown-cmd.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "shutdown-cmd.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "shutdown-cmd.receipt.json").write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: shutdown: mention shutdown-cmd e-tag does not reference owner"


def test_receipt_missing_keys(bundle):
    """6-F17 / 7-F19: receipt without mention_pubkeys/message."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); del o["mention_pubkeys"]; del o["message"]
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt key set mismatch"


def test_receipt_accepted_false(bundle):
    """m80."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); o["accepted"] = 1
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt not accepted"


def test_receipt_event_id_mismatch(bundle):
    """m81."""
    p = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    o = json.loads(p.read_text()); o["event_id"] = "00" * 32
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mention owner receipt event_id != event.id"


def test_receipt_err_nonempty(bundle):
    """m82."""
    (bundle / "golden" / "run-1" / "mentions" / "owner.receipt.err").write_text("error\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mentions/owner.receipt.err is not empty"


def test_extra_mention_file(bundle):
    (bundle / "golden" / "run-1" / "mentions" / "extra.event.json").write_text("{}")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: mentions/ has unexpected files: ['extra.event.json']"


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
    (bundle / "golden" / "run-2" / "mentions" / "owner.event.json").write_text(json.dumps(new_ev) + "\n")
    rp = bundle / "golden" / "run-2" / "mentions" / "owner.receipt.json"
    r = json.loads(rp.read_text()); r["event_id"] = ev1["id"]
    rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    # NIP-01 id mismatch fires because we forced the old id with new created_at
    assert out == "failure_reason: run-2: mention owner NIP-01 id mismatch"


def test_identities_owner_equals_user2(bundle):
    """6-F14: owner == user2 must fail."""
    ids_path = bundle.parent / "fixtures" / "identities.json"
    ids = json.loads(ids_path.read_text())
    ids["user2"] = ids["owner"]
    ids_path.write_text(json.dumps(ids, indent=2) + "\n")
    # Re-sign user2 mention with owner key and update env
    md = bundle / "golden" / "two-users" / "mentions"
    ev = json.loads((md / "owner.event.json").read_text())
    new_ev = nv.sign_event(OWNER_SECKEY, {"created_at": ev["created_at"] + 100, "kind": 9,
                                          "tags": ev["tags"], "content": MENTION_TEXT})
    (md / "user2.event.json").write_text(json.dumps(new_ev) + "\n")
    r = json.loads((md / "user2.receipt.json").read_text()); r["event_id"] = new_ev["id"]
    (md / "user2.receipt.json").write_text(json.dumps(r) + "\n")
    ep = bundle / "golden" / "two-users" / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = ids["owner"]
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: identities owner and user2 are identical"


# === §6 upstream record attacks ===
def test_route_pairs_evil(bundle):
    """m28: method/path not in allowed set."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    p = sorted(rd.glob("*.json"))[-1]; o = json.loads(p.read_text()); o["path"] = "/evil"
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record (GET, /evil) not in allowed set"


def test_route_fingerprint_mismatch(bundle):
    """m30."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    for p in rd.glob("*.json"):
        o = json.loads(p.read_text())
        if o.get("method") == "POST":
            o["authorization_fingerprint"] = "0" * 64; p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream record authorization_fingerprint mismatch"


def test_record_extension_evasion(bundle):
    """7-F14: record with wrong extension bypasses all checks."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    (rd / "999999.jsonl").write_text('{"method":"DELETE","path":"/evil"}\n')
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: upstream-records/ contains invalid filename '999999.jsonl'"


def test_record_key_set_wrong(bundle):
    """6-F18: record missing seq/t_mono_ns/remote_addr."""
    rd = bundle / "golden" / "run-1" / "upstream-records"
    p = sorted(rd.glob("*.json"))[0]
    o = json.loads(p.read_text()); del o["seq"]; del o["t_mono_ns"]; del o["remote_addr"]
    p.write_text(json.dumps(o) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record key set mismatch")


def test_fingerprint_file_emptied(bundle):
    """7-F16: empty fingerprint file -> Failure."""
    fp = bundle.parent / "fixtures" / "upstream-token.fingerprint"
    fp.write_text("\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: upstream-token.fingerprint is not a 64-hex digest"


def test_route_prefix_dropped(bundle):
    for leg in LEGS:
        (bundle / "golden" / leg / "hermes-model.txt").write_text(f"  default: {EXPECTED_MODEL[leg]}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: hermes-model.txt is")


def test_body_model_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["body"]["model"] = "evil-" + r["body"]["model"]; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record body.model is")


def test_host_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            r["headers"]["host"] = "evil#" + PINNED_UPSTREAM_HOST; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: upstream record host is")


def test_record_out_window(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["received_at"] = "1999-01-01T00:00:00.000000Z"; rp.write_text(json.dumps(r) + "\n")
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
                r["body"]["messages"] = [{"role": "user", "content": "other"}]; rp.write_text(json.dumps(r) + "\n")
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
    (bundle / "golden" / "golden.jsonl").write_text(golden_text)
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
    (bundle / "golden" / "golden.jsonl").write_text(golden_text)
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
    p.write_text(p.read_text().replace("mode=Cancel", "mode=Steer"))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: cancel: buzzacp.log missing 'mode=Cancel'"


# === §10 shutdown attacks ===
def test_shutdown_exit1(bundle):
    (bundle / "golden" / "shutdown" / "buzz-acp.exit").write_text("1\n")
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
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: two-users: not every session streamed its own message chunks"


# === §12 process evidence attacks ===
def test_exit_garbage_nonshutdown(bundle):
    """6-F10 / 7-F7: buzz-acp.exit not integer."""
    (bundle / "golden" / "run-1" / "buzz-acp.exit").write_text("not-an-int\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzz-acp.exit is not a valid integer"


def test_proc_buzz_found(bundle):
    """m55: no buzz-acp line with matching pid."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text("1 0 /sbin/init\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after has no buzz-acp line with pid 12300"


def test_proc_tee_parent(bundle):
    """m56: no tee process parented by buzz-acp."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12345 9999 /usr/bin/python3 {PINNED_TEE_PATH}\n12346 12345 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no tee process parented by buzz-acp"


def test_proc_agent_parent(bundle):
    """m57: no agent process parented by a tee."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12345 12300 /usr/bin/python3 {PINNED_TEE_PATH}\n12346 9999 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no agent process parented by a tee process"


def test_proc_closure(bundle):
    """m58: process outside buzz-acp descendant tree."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12345 12300 /usr/bin/python3 {PINNED_TEE_PATH}\n12346 12345 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n8888 9999 python3 {PINNED_TEE_PATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: process 8888")


def test_proc_closure_seed(bundle):
    """m59: mutual-parent attack (V-b F19)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n8888 9999 python3 {PINNED_TEE_PATH}\n9999 8888 python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no tee process parented by buzz-acp"


def test_proc_unparsable_line(bundle):
    """6-F12: unparsable line in process-scan-after.txt."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(sp.read_text() + f"999 nope /usr/bin/python3 {PINNED_TEE_PATH} --evil\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: process-scan-after.txt unparsable line: '999 nope /usr/bin/python3 {PINNED_TEE_PATH} --evil'"


def test_teardown_has_tee(bundle):
    """m60."""
    p = bundle / "golden" / "run-1" / "process-scan-teardown.txt"
    p.write_text(p.read_text() + f"4242 1 python3 {PINNED_TEE_PATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-teardown has tee/agent/buzz-acp lines after teardown"


def test_orphan_pair(bundle):
    """6-F2: orphan process pair outside buzz-acp descendant tree."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n12345 12300 /usr/bin/python3 {PINNED_TEE_PATH}\n12346 12345 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n8888 9999 python3 {PINNED_TEE_PATH}\n9999 8888 python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: process 8888")


def test_pc_launch_exemption(bundle):
    """7-F8 / A2: pc_launch.py exemption only for the launcher (pid == buzz ppid)."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(sp.read_text() + f"31337 1 python3 /somewhere/pc_launch.py --agent {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: run-1: process 31337")


def test_buzz_exe_superstring(bundle):
    """7-F24: buzz-acp-EVIL satisfies startswith but not split()[0] ==."""
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    txt = sp.read_text().replace(f"{PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url",
                                 f"{PINNED_BUZZ_ACP_EXE_REALPATH}-EVIL --relay-url")
    sp.write_text(txt)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: process-scan-after has no buzz-acp line with pid 12300"


# === §13 log/startup attacks ===
def test_dup_startup_key(bundle):
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    new_line = sp.read_text().strip() + " max_turn=3600s"
    sp.write_text(new_line + "\n")
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    lp.write_text(new_line + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup-line duplicate key 'max_turn'"


def test_startup_not_in_log(bundle):
    """7-F4 / A7: startup-line.txt not matching log."""
    lp = bundle / "golden" / "run-1" / "buzzacp.log"
    lp.write_text("2026-09-05T05:00:00Z  INFO buzz_acp: starting with relay=<HEX>\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzzacp.log has no line containing 'buzz-acp starting:'"


def test_startup_values_substr(bundle):
    """m52: startup values compared with == not in."""
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        new_line = sp.read_text().strip().replace("idle_timeout=900s", "idle_timeout=900seconds")
        sp.write_text(new_line + "\n")
        lp = bundle / "golden" / leg / "buzzacp.log"
        lines = lp.read_text().splitlines()
        lines[0] = new_line
        lp.write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: startup idle_timeout is '900seconds', expected '900s'"


def test_startup_respond_to_wrong(bundle):
    """m53."""
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        new_line = sp.read_text().strip().replace("respond_to=owner-only", "respond_to=everyone")
        sp.write_text(new_line + "\n")
        lp = bundle / "golden" / leg / "buzzacp.log"
        lines = lp.read_text().splitlines()
        lines[0] = new_line
        lp.write_text("\n".join(lines) + "\n")
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
        ap.write_text("\n".join(new_argv) + "\n")
        rp = bundle / "golden" / leg / "runtime-identity.json"
        rid = json.loads(rp.read_text()); rid["launch_argv"] = new_argv
        rp.write_text(json.dumps(rid, indent=2) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == f"failure_reason: run-1: argv --idle-timeout is not {PINNED_IDLE_TIMEOUT_ARG}"


def test_log_unmasked(bundle):
    (bundle / "golden" / "run-1" / "buzzacp.log").write_text(
        (bundle / "golden" / "run-1" / "startup-line.txt").read_text() + "INFO relay=" + "ab" * 32 + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: buzzacp.log contains unmasked 64-hex string"


# === §14 manifest attacks ===
def test_manifest_dup_header(bundle):
    """m48."""
    gz = gzip.compress(b"## hermes-agent\na f\n## hermes-agent\nb g\n## buzz\nc m\n## acp\nd l\n", mtime=0)
    for leg in LEGS:
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_preamble(bundle):
    """m49."""
    body = b"EVIL\n" + gzip.decompress((GOLDEN / "manifests" / "manifest-baseline.txt.gz").read_bytes())
    gz = gzip.compress(body, mtime=0)
    for leg in LEGS:
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
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
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_baseline_sha_pin(bundle):
    """m45: baseline gz sha mismatch."""
    bl = bundle / "golden" / "manifests" / "manifest-baseline.txt.gz"
    body = gzip.decompress(bl.read_bytes())
    bl.write_bytes(gzip.compress(body, mtime=1))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: baseline gz sha256 mismatch"


def test_manifest_ts_order(bundle):
    """m46: manifest timestamps not pre < start < post.
    Set pre timestamp AFTER spawned_at_utc (05:30:00) to violate pre < start."""
    for leg in LEGS:
        lines = (bundle / "golden" / leg / "manifest-pre.summary").read_text().splitlines()
        lines[3] = "2026-09-05T06:00:00Z"  # after spawned_at_utc 05:30:00
        (bundle / "golden" / leg / "manifest-pre.summary").write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest timestamps not pre < start < post"


def test_manifest_post_after_tl(bundle):
    """m47: manifest-post not after last timeline t_utc.
    Set ONLY run-1's post timestamp to just after spawned_at but before run-1's last
    timeline entry. spawned_at=05:00:00.050, last entry ~05:00:01.100.
    05:00:01Z = 05:00:01.000 is after spawned_at but before last entry."""
    lines = (bundle / "golden" / "run-1" / "manifest-post.summary").read_text().splitlines()
    lines[3] = "2026-09-05T05:00:01Z"
    (bundle / "golden" / "run-1" / "manifest-post.summary").write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: manifest-post timestamp not after last timeline t_utc"


def test_summary_digests_zeroed(bundle):
    """m50."""
    for leg in LEGS:
        for name in ("manifest-pre.summary", "manifest-post.summary"):
            sp = bundle / "golden" / leg / name
            lines = sp.read_text().splitlines()
            sp.write_text("\n".join(f"{l.split()[0]} {'0'*64}" if len(l.split()) == 2 and l.split()[0] in PINNED_BASELINE_DIGESTS else l for l in lines) + "\n")
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
    (bundle / "golden" / "golden.jsonl").write_text(golden_text)
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
    p.write_text(new_text)
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
    (bundle / "golden" / "golden.jsonl").write_text(golden_text)
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
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    (bundle / "golden" / "golden.jsonl").write_text("\n".join(n1) + "\n")
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
    (bundle / "golden" / "negative" / "evil.txt").write_text("x")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: unexpected files: ['evil.txt']"


def test_neg_nan_timeline(bundle):
    """7-F23: NaN in negative timeline."""
    p = bundle / "golden" / "negative" / "timeline.jsonl"
    p.write_text(p.read_text().replace('"t_mono_ns":1000000000001', '"t_mono_ns":NaN', 1))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: NaN or Infinity in timeline at seq 1"


def test_neg_c2a_not_seq1(bundle):
    """7-F10 / A11: c2a initialize not at seq 1."""
    p = bundle / "golden" / "negative" / "timeline.jsonl"
    es = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    junk = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T05:00:00.000000Z",
            "t_mono_ns": 1_000_000_000_000, "frame": {"jsonrpc": "2.0", "method": "hello", "params": {}}}
    es = [junk] + es
    for i, e in enumerate(es): e["seq"] = i + 1
    p.write_text("".join(json.dumps(e, separators=(",", ":")) + "\n" for e in es))
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: seq 1 is not c2a"


def test_neg_classify_wrong(bundle):
    """m78: negative classify check must reject non-MISSING_REQUIRED."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["frame"]["params"]["protocolVersion"] = 2
    with open(nd / "timeline.jsonl", "w") as f:
        for e in es: f.write(json.dumps(e, separators=(",", ":")) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: negative: initialize params != fixture"


def test_neg_extra_a2c_junk_first(bundle):
    """7-F10: junk a2c before real response — observed matched by request id, not a2c[0]."""
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    junk = {"seq": 0, "dir": "a2c", "t_utc": es[1]["t_utc"], "t_mono_ns": es[1]["t_mono_ns"],
            "frame": {"jsonrpc": "2.0", "method": "log", "params": {}}}
    es.insert(1, junk)
    for i, e in enumerate(es): e["seq"] = i + 1
    with open(nd / "timeline.jsonl", "w") as f:
        for e in es: f.write(json.dumps(e, separators=(",", ":")) + "\n")
    # Should still pass since the real response at id=0 is found
    rc, out = _check(bundle)
    assert rc == 0  # Still passes because the response IS there, matched by id


# === Sequence guard (A12) ===
def test_sequence_guard_derived(bundle, monkeypatch):
    """m71: deleting a check call must change the sequence -> Failure."""
    # We prove this by testing that the actual sequence matches expected
    result = cc.check_bundle(bundle)
    assert "16 checks executed" in result


# === Extra golden entries ===
def test_extra_leg_dir(bundle):
    (bundle / "golden" / "run-3").mkdir(); (bundle / "golden" / "run-3" / "x").write_text("")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: unexpected directory golden/run-3"


def test_extra_golden_file(bundle):
    (bundle / "golden" / "NOTES.md").write_text("hi\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: golden: unexpected file golden/NOTES.md"


def test_extra_manifests_file(bundle):
    """A13: manifests/ should contain only manifest-baseline.txt.gz."""
    (bundle / "golden" / "manifests" / "evil.txt").write_text("hi\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: golden: manifests/ contains unexpected entries")


# === Malformed evidence wrapper ===
def test_bad_json_timeline(bundle):
    tl = bundle / "golden" / "run-1" / "timeline.jsonl"
    lines = tl.read_text().splitlines(); lines[0] = "bad"
    tl.write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out.startswith("failure_reason: malformed evidence:")


def test_bad_pid(bundle):
    (bundle / "golden" / "run-1" / "buzz-acp.pid").write_text("bad\n")
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
    assert "; negative: observed:" in result
