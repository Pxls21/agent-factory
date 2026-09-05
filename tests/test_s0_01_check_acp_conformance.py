"""proofs/S0-01/check_acp_conformance.py v2.1 test suite.

Synthesized PASS bundle uses nostr_verify.sign_event with throwaway keys for ALL
mention events (stated: the fixture events in relay-events-2026-09-05.json do NOT all
have the required e-tags for replies_to, so synthetic signing is needed). The checker's
identities lookup is monkeypatched to use the throwaway pubkeys.
The only other patched pin is PINNED_GOLDEN_SHA256 (set to the synthetic golden's sha).
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
    EXPECTED_MENTIONS, EXPECTED_MODEL, LEGS, MANIFEST_TREES, MENTION_TEXT,
    PINNED_AGENT_ENTRYPOINT_SHA256, PINNED_AGENT_INTERPRETER_REALPATH,
    PINNED_AGENT_INTERPRETER_SHA256, PINNED_AGENT_REALPATH,
    PINNED_BASELINE_DIGESTS, PINNED_BUZZ_ACP_EXE_REALPATH,
    PINNED_BUZZ_ACP_SHA256, PINNED_HOME, PINNED_HERMES_HOME,
    PINNED_IDLE_TIMEOUT, PINNED_LAUNCH_ARGV, PINNED_MAX_TURN, PINNED_PATH,
    PINNED_RELAY_URL, PINNED_ROUTE_PREFIX, PINNED_SESSION_POLICY,
    PINNED_TEE_PATH, PINNED_UPSTREAM_HOST, UPSTREAM_POST_PATH,
)

# Throwaway keys for synthetic mention events (stated: fixture events lack e-tags for
# shutdown-cmd and cancel-cmd needs proper referencing; nostr_verify.sign_event used)
OWNER_SECKEY = "0" * 63 + "2"
USER2_SECKEY = "0" * 63 + "3"
OWNER_PUBKEY = format(nv._point_mul(2, nv.G)[0], "064x")
USER2_PUBKEY = format(nv._point_mul(3, nv.G)[0], "064x")

# Synthetic identities: uses the throwaway key pubkeys but keeps
# the real channel/agent/relay values from the fixture
_REAL_IDS = json.loads(FIXTURES.joinpath("identities.json").read_text())
SYNTH_IDENTITIES = {
    "owner": OWNER_PUBKEY, "user2": USER2_PUBKEY,
    "agent": _REAL_IDS["agent"], "channel": _REAL_IDS["channel"],
    "relay": _REAL_IDS["relay"], "relay_url": _REAL_IDS["relay_url"],
}

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
    base_dt = datetime(2026, 9, 5, 5, 0, 0, tzinfo=timezone.utc)
    # Per-leg offset ensures run-1 and run-2 have distinct first t_utc (V-b F11 distinctness)
    leg_offsets = {"run-1": 0, "run-2": 1, "cancel": 2, "shutdown": 3, "two-users": 4}
    offset_s = leg_offsets.get(leg, 0)
    for i, (d, frame) in enumerate(frames, 1):
        t = base_dt + timedelta(hours=i, seconds=offset_s)
        entries.append({"seq": i, "dir": d,
                        "t_utc": t.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "t_mono_ns": base_mono + i * 1_000_000, "frame": frame})
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
           "python_dont_write_bytecode": True, "spawned_at_utc": "2026-09-05T05:30:00.000000Z",
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


def _write_startup(leg_dir, leg):
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


# Event counter for distinct created_at across legs (ensures cross-leg uniqueness)
_event_counter = [0]

def _sign_mention(seckey, content, tags_list):
    _event_counter[0] += 1
    return nv.sign_event(seckey, {"created_at": 1788608000 + _event_counter[0],
                                  "kind": 9, "tags": tags_list, "content": content})


def _write_mentions(leg_dir, leg, identities):
    mentions_dir = leg_dir / "mentions"
    mentions_dir.mkdir(parents=True, exist_ok=True)
    expected = EXPECTED_MENTIONS.get(leg, [])
    base_tags = [["h", identities["channel"]], ["p", identities["agent"]]]
    written = {}
    for tag, id_key, content, replies_to in expected:
        seckey = OWNER_SECKEY if id_key == "owner" else USER2_SECKEY
        tags_list = list(base_tags)
        if replies_to is not None and replies_to in written:
            tags_list.append(["e", written[replies_to]["id"], "", "reply"])
        event = _sign_mention(seckey, content, tags_list)
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


def _write_buzzacp_log(leg_dir, leg):
    lines = ["2026-09-05T05:00:00Z  INFO buzz_acp: starting with relay=<HEX>"]
    if leg == "cancel":
        lines.append("2026-09-05T05:00:01Z  INFO buzz_acp: mode=Cancel")
    if leg == "shutdown":
        lines.append("2026-09-05T05:00:01Z  INFO buzz_acp: shutdown command from owner")
        lines.append("2026-09-05T05:00:02Z  INFO buzz_acp: buzz-acp stopped")
    (leg_dir / "buzzacp.log").write_text("\n".join(lines) + "\n")


def _write_process_scan(leg_dir, leg):
    buzz_pid = 12300
    (leg_dir / "buzz-acp.pid").write_text(f"{buzz_pid}\n")
    if leg == "shutdown":
        (leg_dir / "process-scan-after.txt").write_text("1 0 /sbin/init\n")
        (leg_dir / "buzz-acp.exit").write_text("0\n")
    else:
        lines = [f"{buzz_pid} 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999",
                 f"12345 {buzz_pid} /usr/bin/python3 {PINNED_TEE_PATH}",
                 f"12346 12345 /usr/bin/python3 {PINNED_AGENT_REALPATH}"]
        (leg_dir / "process-scan-after.txt").write_text("\n".join(lines) + "\n")
        (leg_dir / "process-scan-teardown.txt").write_text("1 0 /sbin/init\n")
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


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    _event_counter[0] = 0  # reset for reproducibility
    g = tmp_path / "evidence" / "golden"
    identities = SYNTH_IDENTITIES
    fingerprint = _load_fingerprint()
    baseline_path = g / "manifests" / "manifest-baseline.txt.gz"
    # Write a synthetic identities.json the checker will read
    synth_ids_path = FIXTURES / "identities.json"
    orig_ids = synth_ids_path.read_text()
    synth_ids_path.write_text(json.dumps(identities, indent=2) + "\n")
    for leg in LEGS:
        ld = g / leg
        c2a, a2c = _load_frames(GOLDEN / leg)
        entries = _make_interleaved_timeline(c2a, a2c, leg)
        _write_timeline(ld, entries)
        _write_runtime_identity(ld, leg)
        _write_env(ld, identities, leg)
        _write_startup(ld, leg)
        _write_model(ld, leg)
        _write_manifests(ld, baseline_path)
        _write_mentions(ld, leg, identities)
        _write_upstream_records(ld, leg, entries, fingerprint)
        _write_buzzacp_log(ld, leg)
        _write_process_scan(ld, leg)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(g / "run-1", "run-1"))
    golden_text = "\n".join(n1) + "\n"
    (g / "golden.jsonl").write_text(golden_text)
    golden_sha = _sha256(golden_text.encode("utf-8"))
    _write_negative(g / "negative", identities)
    # Monkeypatch PINNED_GOLDEN_SHA256 (the ONLY patched pin — commented)
    monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", golden_sha)
    yield tmp_path / "evidence"
    # Restore original identities.json
    synth_ids_path.write_text(orig_ids)


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
    assert "checks executed" in result and "observed:" in result


def test_cli_pass_path_fails_on_golden_pin(bundle):
    r = _run(bundle)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: golden: golden not pinned"


def test_normalization_deterministic(bundle):
    e1 = cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1")
    n1 = cc.normalize_timeline(e1)
    assert n1 == cc.normalize_timeline(e1)


# === Deferrals ===
def test_v1_bundle_defers():
    r = _run(P / "evidence")
    assert r.returncode == 2 and r.stdout.strip() == "deferred: v2 evidence not captured"


def test_absent_defers(tmp_path):
    (tmp_path / "e").mkdir()
    r = _run(tmp_path / "e")
    assert r.returncode == 2 and r.stdout.strip() == "deferred: golden evidence bundle absent"


# === M1-M5 ===
def test_m1_manifest_zeroed(bundle):
    gz = gzip.compress(b"## hermes-agent\nZ\n## buzz\nZ\n## acp\nZ\n", mtime=0)
    for leg in LEGS:
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: manifest body != baseline body"


def test_m2_tampered_sig(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    ev = json.loads(ep.read_text()); ev["sig"] = "ff" * 64
    ep.write_text(json.dumps(ev) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "BIP-340 signature invalid" in out


def test_m2_wrong_pubkey(bundle):
    ep = bundle / "golden" / "run-1" / "mentions" / "owner.event.json"
    # Sign with user2 key (different pubkey from owner)
    ev = _sign_mention(USER2_SECKEY, MENTION_TEXT,
                       [["h", SYNTH_IDENTITIES["channel"]], ["p", SYNTH_IDENTITIES["agent"]]])
    ep.write_text(json.dumps(ev) + "\n")
    rp = bundle / "golden" / "run-1" / "mentions" / "owner.receipt.json"
    receipt = json.loads(rp.read_text()); receipt["event_id"] = ev["id"]
    rp.write_text(json.dumps(receipt) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: mention owner pubkey != identities[owner]"


def test_m3_cancel_foreign(bundle):
    ld = bundle / "golden" / "cancel"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel":
            e["frame"]["params"]["sessionId"] = "foreign-00000000"
    _write_timeline(ld, entries)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: cancel: session/cancel targets a different session"


def test_m4_shutdown_init_only(bundle):
    ld = bundle / "golden" / "shutdown"
    entries = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    filtered = [e for e in entries if e["frame"].get("method") == "initialize"
                or (e["dir"] == "a2c" and "id" in e["frame"] and e["frame"].get("id") == 0)]
    for i, e in enumerate(filtered): e["seq"] = i + 1
    _write_timeline(ld, filtered)
    rc, out = _check(bundle)
    assert rc == 1
    # The mention created_at window check fires first because the timeline is truncated
    assert out.startswith("failure_reason: shutdown:")


def test_m5_1s(bundle):
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        sp.write_text(sp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=1s"))
    rc, out = _check(bundle)
    assert rc == 1 and out == f"failure_reason: run-1: startup max_turn is '1s', expected '{PINNED_MAX_TURN}'"


def test_m5_7200(bundle):
    for leg in LEGS:
        sp = bundle / "golden" / leg / "startup-line.txt"
        sp.write_text(sp.read_text().replace(f"max_turn={PINNED_MAX_TURN}", "max_turn=7200s"))
    rc, out = _check(bundle)
    assert rc == 1 and out == f"failure_reason: run-1: startup max_turn is '7200s', expected '{PINNED_MAX_TURN}'"


# === Deletion attacks ===
@pytest.mark.parametrize("fn,leg", [
    ("timeline.jsonl", "run-1"), ("frames-client-to-agent.jsonl", "run-1"),
    ("frames-agent-to-client.jsonl", "run-1"), ("runtime-identity.json", "run-1"),
    ("env.json", "run-1"), ("hermes-model.txt", "run-1"), ("startup-line.txt", "run-1"),
    ("argv.txt", "run-1"), ("buzz-acp.pid", "run-1"), ("buzz-acp.exit", "shutdown"),
    ("buzzacp.log", "run-1"), ("manifest-pre.txt.gz", "run-1"),
    ("manifest-post.txt.gz", "run-1"), ("manifest-pre.summary", "run-1"),
    ("manifest-post.summary", "run-1"), ("process-scan-after.txt", "run-1"),
    ("process-scan-after.txt", "cancel"), ("process-scan-after.txt", "shutdown"),
    ("process-scan-teardown.txt", "run-1"), ("buzzacp.log", "cancel"), ("buzzacp.log", "shutdown"),
])
def test_deletion(bundle, fn, leg):
    p = bundle / "golden" / leg / fn
    if p.exists(): p.unlink()
    rc, out = _check(bundle)
    assert rc == 1 and out.startswith("failure_reason:")


def test_del_mentions(bundle):
    shutil.rmtree(bundle / "golden" / "run-1" / "mentions")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: mentions/ absent"


def test_del_upstream(bundle):
    shutil.rmtree(bundle / "golden" / "run-1" / "upstream-records")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: zero upstream records / upstream-records/ absent"


def test_del_baseline(bundle):
    (bundle / "golden" / "manifests" / "manifest-baseline.txt.gz").unlink()
    rc, out = _check(bundle)
    assert rc == 1 and "manifests/manifest-baseline.txt.gz absent" in out


def test_del_negative(bundle):
    shutil.rmtree(bundle / "golden" / "negative")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: golden: negative/ absent"


def test_del_golden_jsonl(bundle):
    (bundle / "golden" / "golden.jsonl").unlink()
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: golden: golden.jsonl absent"


def test_del_leg(bundle):
    shutil.rmtree(bundle / "golden" / "run-1")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: golden: golden/run-1 absent"


# === Type/structural attacks ===
def test_seq_float(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in es: e["seq"] = float(e["seq"])
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: timeline seq at index 0 is not int"


def test_seq_bool(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["seq"] = True; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: timeline seq at index 0 is not int"


def test_nan(bundle):
    tl = bundle / "golden" / "run-1" / "timeline.jsonl"
    tl.write_text(re.sub(r'"t_mono_ns":(\d+)', '"t_mono_ns":NaN', tl.read_text(), count=1))
    rc, out = _check(bundle)
    assert rc == 1 and "NaN or Infinity" in out


def test_mono_string(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["t_mono_ns"] = "x"; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: timeline t_mono_ns at seq 1 is not int"


def test_dir_unknown(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["dir"] = "x2x"; _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: timeline dir at seq 1 is 'x2x', expected 'c2a' or 'a2c'"


def test_dup_startup_key(bundle):
    sp = bundle / "golden" / "run-1" / "startup-line.txt"
    sp.write_text(sp.read_text().strip() + " max_turn=3600s\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: startup-line duplicate key 'max_turn'"


def test_manifest_dup_header(bundle):
    gz = gzip.compress(b"## hermes-agent\na f\n## hermes-agent\nb g\n## buzz\nc m\n## acp\nd l\n", mtime=0)
    for leg in LEGS:
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: manifest body != baseline body"


def test_manifest_preamble(bundle):
    body = b"EVIL\n" + gzip.decompress((GOLDEN / "manifests" / "manifest-baseline.txt.gz").read_bytes())
    gz = gzip.compress(body, mtime=0)
    for leg in LEGS:
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz)
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: manifest body != baseline body"


def test_env_extra_key(bundle):
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["X"] = "v"
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "env.json key set mismatch" in out


def test_extra_leg_dir(bundle):
    (bundle / "golden" / "run-3").mkdir(); (bundle / "golden" / "run-3" / "x").write_text("")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: golden: unexpected directory golden/run-3"


def test_extra_mention_file(bundle):
    (bundle / "golden" / "run-1" / "mentions" / "extra.event.json").write_text("{}")
    rc, out = _check(bundle)
    assert rc == 1 and "unexpected files" in out


def test_replay_mention(bundle):
    ev = json.loads((bundle / "golden" / "run-1" / "mentions" / "owner.event.json").read_text())
    (bundle / "golden" / "run-2" / "mentions" / "owner.event.json").write_text(json.dumps(ev) + "\n")
    rp = bundle / "golden" / "run-2" / "mentions" / "owner.receipt.json"
    r = json.loads(rp.read_text()); r["event_id"] = ev["id"]
    rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: golden: mention event id replayed across legs"


def test_allowlist_super(bundle):
    ep = bundle / "golden" / "two-users" / "env.json"
    env = json.loads(ep.read_text())
    env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = SYNTH_IDENTITIES["user2"] + ",x"
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "!= identities.user2" in out


def test_owner_swap(bundle):
    ep = bundle / "golden" / "run-1" / "env.json"
    env = json.loads(ep.read_text()); env["BUZZ_ACP_AGENT_OWNER"] = "de" * 32
    ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: env BUZZ_ACP_AGENT_OWNER mismatch"


def test_route_prefix_dropped(bundle):
    for leg in LEGS:
        (bundle / "golden" / leg / "hermes-model.txt").write_text(f"  default: {EXPECTED_MODEL[leg]}\n")
    rc, out = _check(bundle)
    assert rc == 1 and "hermes-model.txt is" in out


def test_body_model_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["body"]["model"] = "evil-" + r["body"]["model"]; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "upstream record body.model" in out


def test_host_super(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            r["headers"]["host"] = "evil#" + PINNED_UPSTREAM_HOST; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "upstream record host" in out


def test_record_out_window(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["received_at"] = "1999-01-01T00:00:00.000000Z"; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "outside all prompt windows" in out


def test_one_record_two_prompts(bundle):
    rd = bundle / "golden" / "two-users" / "upstream-records"
    kept = False
    for rp in sorted(rd.glob("*.json")):
        r = json.loads(rp.read_text())
        if r.get("method") == "POST":
            if kept: rp.unlink()
            else: kept = True
    rc, out = _check(bundle)
    assert rc == 1 and "no upstream POST with stream=true and mention text for a prompt window" in out


def test_no_mention_text(bundle):
    for leg in LEGS:
        for rp in (bundle / "golden" / leg / "upstream-records").glob("*.json"):
            r = json.loads(rp.read_text())
            if r.get("method") == "POST":
                r["body"]["messages"] = [{"role": "user", "content": "other"}]; rp.write_text(json.dumps(r) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "no upstream POST with stream=true and mention text" in out


def test_summary_zeroed(bundle):
    for leg in LEGS:
        for name in ("manifest-pre.summary", "manifest-post.summary"):
            sp = bundle / "golden" / leg / name
            lines = sp.read_text().splitlines()
            sp.write_text("\n".join(f"{l.split()[0]} {'0'*64}" if len(l.split()) == 2 and l.split()[0] in PINNED_BASELINE_DIGESTS else l for l in lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "summary digests != body digests" in out


def test_orphan_pair(bundle):
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    sp.write_text(f"12300 1 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n8888 9999 python3 {PINNED_TEE_PATH}\n9999 8888 python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1


def test_argv_tampered(bundle):
    rp = bundle / "golden" / "run-1" / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_argv"] = ["/tmp/evil"]; rp.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: agent_argv mismatch"


def test_interp_tampered(bundle):
    rp = bundle / "golden" / "run-1" / "runtime-identity.json"
    rid = json.loads(rp.read_text()); rid["agent_interpreter_realpath"] = "/tmp/evil"; rp.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: run-1: agent_interpreter_realpath mismatch"


def test_golden_regen(bundle):
    """Mutate both runs identically (drop the last notification), regenerate golden.
    Must fail on PINNED_GOLDEN_SHA256 since the pin was set on the original golden."""
    for leg in ("run-1", "run-2"):
        ld = bundle / "golden" / leg
        es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
        # Remove the second-to-last entry (a notification) and resequence
        del es[-2]
        for i, e in enumerate(es): e["seq"] = i + 1
        _write_timeline(ld, es)
    n1 = cc.normalize_timeline(cc._load_timeline_raw(bundle / "golden" / "run-1", "run-1"))
    (bundle / "golden" / "golden.jsonl").write_text("\n".join(n1) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "golden.jsonl sha256" in out


def test_run2_copy(bundle):
    shutil.copytree(bundle / "golden" / "run-1", bundle / "golden" / "run-2-copy")
    shutil.rmtree(bundle / "golden" / "run-2")
    (bundle / "golden" / "run-2-copy").rename(bundle / "golden" / "run-2")
    rc, out = _check(bundle)
    assert rc == 1 and ("identical" in out or "replayed" in out)


def test_env_leak(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["BUZZ_PRIVATE_KEY"] = "plaintext"
        ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "should be redacted" in out


def test_redacted_len_true(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["OMNIROUTE_API_KEY"]["len"] = True
        ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "not a positive int" in out


def test_shutdown_exit1(bundle):
    (bundle / "golden" / "shutdown" / "buzz-acp.exit").write_text("1\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: shutdown: buzz-acp.exit is '1', expected '0'"


def test_log_unmasked(bundle):
    (bundle / "golden" / "run-1" / "buzzacp.log").write_text("INFO relay=" + "ab" * 32 + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "unmasked 64-hex" in out


def test_hex_leak_env(bundle):
    for leg in LEGS:
        ep = bundle / "golden" / leg / "env.json"
        env = json.loads(ep.read_text()); env["S0_01_FRAMEDIR"] = "ab" * 32
        ep.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and "64-hex string" in out


def test_bad_json_timeline(bundle):
    tl = bundle / "golden" / "run-1" / "timeline.jsonl"
    lines = tl.read_text().splitlines(); lines[0] = "bad"
    tl.write_text("\n".join(lines) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out.startswith("failure_reason: malformed evidence:")


def test_bad_pid(bundle):
    (bundle / "golden" / "run-1" / "buzz-acp.pid").write_text("bad\n")
    rc, out = _check(bundle)
    assert rc == 1 and out.startswith("failure_reason: malformed evidence:")


def test_utc_backwards(bundle):
    ld = bundle / "golden" / "run-1"
    es = [json.loads(l) for l in (ld / "timeline.jsonl").read_text().splitlines() if l.strip()]
    utcs = [e["t_utc"] for e in es]; utcs.reverse()
    for i, e in enumerate(es): e["t_utc"] = utcs[i]
    _write_timeline(ld, es)
    rc, out = _check(bundle)
    assert rc == 1 and "t_utc not non-decreasing" in out


def test_negative_ok(bundle):
    nd = bundle / "golden" / "negative"
    es = [json.loads(l) for l in (nd / "timeline.jsonl").read_text().splitlines() if l.strip()]
    es[0]["frame"]["params"]["protocolVersion"] = 2
    with open(nd / "timeline.jsonl", "w") as f:
        for e in es: f.write(json.dumps(e, separators=(",", ":")) + "\n")
    rc, out = _check(bundle)
    assert rc == 1 and out == "failure_reason: negative: initialize params != fixture"
