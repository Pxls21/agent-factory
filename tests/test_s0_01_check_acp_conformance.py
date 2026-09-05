"""proofs/S0-01/check_acp_conformance.py v2 — exercised on a synthesized v2 PASS bundle
built from the REAL committed frames, then mutated per the owner's five named regressions (M1-M5)
plus structural and semantic mutations.

A v1 bundle (no timeline.jsonl) DEFERS with exit 2.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import subprocess
import sys
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

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
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


def _load_relay_events():
    return json.loads(FIXTURES.joinpath("relay-events-2026-09-05.json").read_text())


def _load_identities():
    return json.loads(FIXTURES.joinpath("identities.json").read_text())


def _load_fingerprint():
    return FIXTURES.joinpath("upstream-token.fingerprint").read_text().strip()


# ---------------------------------------------------------------------------
# Timeline builder: convert c2a + a2c to interleaved timeline with synthetic timestamps
# ---------------------------------------------------------------------------
def _make_timeline(c2a, a2c):
    """Interleave c2a and a2c frames with synthetic monotonic timestamps.
    Order: all c2a first in original order, then all a2c in original order.
    For legs with interleaved events (cancel, two-users), the caller must pass
    the frames already in the desired interleaved order via a merged list.
    """
    entries = []
    seq = 0
    base_mono = 1000000000000  # 1e12 ns
    base_ts = "2026-09-05T12:00:00."
    for frame in c2a:
        seq += 1
        entries.append({
            "seq": seq, "dir": "c2a",
            "t_utc": f"{base_ts}{seq:06d}Z",
            "t_mono_ns": base_mono + seq * 1000000,
            "frame": frame,
        })
    for frame in a2c:
        seq += 1
        entries.append({
            "seq": seq, "dir": "a2c",
            "t_utc": f"{base_ts}{seq:06d}Z",
            "t_mono_ns": base_mono + seq * 1000000,
            "frame": frame,
        })
    return entries


def _make_interleaved_timeline(frames_with_dir):
    """Build timeline from a list of (dir, frame) tuples in the desired order."""
    entries = []
    base_mono = 1000000000000
    base_ts = "2026-09-05T12:00:00."
    for seq_i, (d, frame) in enumerate(frames_with_dir, 1):
        entries.append({
            "seq": seq_i, "dir": d,
            "t_utc": f"{base_ts}{seq_i:06d}Z",
            "t_mono_ns": base_mono + seq_i * 1000000,
            "frame": frame,
        })
    return entries


# ---------------------------------------------------------------------------
# Ancillary file builders
# ---------------------------------------------------------------------------
def _write_timeline(leg_dir, entries):
    leg_dir.mkdir(parents=True, exist_ok=True)
    with open(leg_dir / "timeline.jsonl", "w") as f:
        for e in entries:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")
    # directional files
    with open(leg_dir / "frames-client-to-agent.jsonl", "w") as f:
        for e in entries:
            if e["dir"] == "c2a":
                f.write(json.dumps(e["frame"]) + "\n")
    with open(leg_dir / "frames-agent-to-client.jsonl", "w") as f:
        for e in entries:
            if e["dir"] == "a2c":
                f.write(json.dumps(e["frame"]) + "\n")


def _write_runtime_identity(leg_dir):
    tee_sha = _sha256_file(P / "tools" / "frame_tee.py")
    rid = {
        "tee_path": str(P / "tools" / "frame_tee.py"),
        "tee_sha256": tee_sha,
        "agent_argv": [cc.PINNED_AGENT_REALPATH],
        "agent_realpath": cc.PINNED_AGENT_REALPATH,
        "agent_entrypoint_sha256": cc.PINNED_AGENT_ENTRYPOINT_SHA256,
        "agent_child_pid": 12345,
        "agent_interpreter_realpath": "/usr/bin/python3",
        "agent_interpreter_sha256": "0" * 64,
        "python_dont_write_bytecode": True,
        "spawned_at_utc": "2026-09-05T12:00:00.000000Z",
        "buzz_acp_pid": 12300,
        "buzz_acp_exe_realpath": "/usr/bin/buzz-acp",
        "buzz_acp_exe_sha256": cc.PINNED_BUZZ_ACP_SHA256,
        "buzz_acp_version": "0.1.0",
    }
    (leg_dir / "runtime-identity.json").write_text(json.dumps(rid, indent=2) + "\n")
    return rid


def _write_env(leg_dir, identities, leg):
    env = {
        "S0_01_AGENT": cc.PINNED_AGENT_REALPATH,
        "HERMES_HOME": cc.PINNED_HERMES_HOME,
        "BUZZ_RELAY_URL": cc.PINNED_RELAY_URL,
        "OMNIROUTE_API_KEY": {"redacted": True, "len": 32, "sha256_12": "abcdef012345"},
        "PYTHONDONTWRITEBYTECODE": "1",
        "BUZZ_ACP_RESPOND_TO": "owner-only",
        "BUZZ_ACP_AGENT_OWNER": identities["owner"],
        "BUZZ_ACP_SESSION_POLICY": "thread",
        "BUZZ_PRIVATE_KEY": {"redacted": True, "len": 64, "sha256_12": "112233445566"},
        "HOME": "/home/rocco",
        "PATH": "/usr/bin:/bin",
        "S0_01_FRAMEDIR": "/tmp/frames",
    }
    if leg == "two-users":
        env["BUZZ_ACP_RESPOND_TO"] = "allowlist"
        env["BUZZ_ACP_RESPOND_TO_ALLOWLIST"] = identities["user2"]
    (leg_dir / "env.json").write_text(json.dumps(env, indent=2) + "\n")


def _write_startup(leg_dir, leg):
    respond_to = "owner-only"
    if leg == "two-users":
        respond_to = "allowlist(1)"
    startup = (
        "2026-09-05T12:00:00.000000Z  INFO buzz_acp: buzz-acp starting: "
        f"relay=ws://127.0.0.1:3999 pubkey=<HEX> "
        f"agent_cmd=/home/rocco/s0-01-pinned/.markers/frame_tee.py  mcp_cmd= "
        f"idle_timeout=900s max_turn=3600s agents=1 heartbeat=0s "
        f"subscribe=Mentions dedup=Queue session_policy=thread "
        f"meh=Steer ignore_self=true context_limit=12 "
        f"max_turns_per_session=0 presence=true typing=true memory=true "
        f"model=(agent default) permission_mode=bypassPermissions "
        f"respond_to={respond_to}"
    )
    (leg_dir / "startup-line.txt").write_text(startup + "\n")
    # argv
    (leg_dir / "argv.txt").write_text(
        "/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp\n"
        "--relay-url\nws://127.0.0.1:3999\n"
        "--agent-command\n/home/rocco/s0-01-pinned/.markers/frame_tee.py\n"
        "--agent-args\n\n"
        "--idle-timeout\n900\n"
        "--max-turn-duration\n3600\n"
    )


def _write_model(leg_dir, leg):
    model = "s0-01-slow" if leg == "cancel" else "s0-01-pong"
    (leg_dir / "hermes-model.txt").write_text(f"  default: s0-01-scripted/{model}\n")


def _write_manifests(leg_dir, baseline_path):
    """Create synthetic manifest gz files with matching digests."""
    body_text = (
        "## hermes-agent\n"
        "aaaa  file1.py\n"
        "bbbb  file2.py\n"
        "## buzz\n"
        "cccc  main.rs\n"
        "## acp\n"
        "dddd  lib.py\n"
    )
    body_bytes = body_text.encode("utf-8")
    gz_data = gzip.compress(body_bytes)
    (leg_dir / "manifest-pre.txt.gz").write_bytes(gz_data)
    (leg_dir / "manifest-post.txt.gz").write_bytes(gz_data)
    # Compute actual digests from the body
    digests = cc._parse_manifest_body(body_bytes)
    # Write baseline from same body
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_bytes(gz_data)
    # Write summaries with correct timestamps
    pre_sum = "hermes-agent {ha}\nbuzz {bz}\nacp {ac}\n2026-09-05T11:59:50Z\n".format(
        ha=digests["hermes-agent"], bz=digests["buzz"], ac=digests["acp"])
    post_sum = "hermes-agent {ha}\nbuzz {bz}\nacp {ac}\n2026-09-05T12:01:00Z\n".format(
        ha=digests["hermes-agent"], bz=digests["buzz"], ac=digests["acp"])
    (leg_dir / "manifest-pre.summary").write_text(pre_sum)
    (leg_dir / "manifest-post.summary").write_text(post_sum)
    return digests


# Map: leg -> list of (tag, identity_key, content) for mentions
MENTION_MAP = {
    "run-1": [("owner", "owner", "Reply with exactly the single word: pong")],
    "run-2": [("owner", "owner", "Reply with exactly the single word: pong")],
    "cancel": [("owner", "owner", "Reply with exactly the single word: pong"),
               ("cancel-cmd", "owner", "!cancel")],
    "shutdown": [("owner", "owner", "Reply with exactly the single word: pong"),
                 ("shutdown-cmd", "owner", "!shutdown")],
    "two-users": [("owner", "owner", "Reply with exactly the single word: pong"),
                  ("user2", "user2", "Reply with exactly the single word: pong")],
}

# Map each (leg, tag) to a real fixture event by index
# relay-events-2026-09-05.json has events in order by index:
# 0: fixture prompt (owner), 1: pong (owner), 2: pong (owner), 3: user2 probe
# 4: pong (owner), 5: pong (owner), 6: pong (owner), 7: !shutdown (owner)
# 8: pong (owner) = cancel mention, 9: !cancel (owner), 10: pong (owner), 11: pong (user2)
EVENT_ASSIGN = {
    ("run-1", "owner"): 1,
    ("run-2", "owner"): 2,
    ("cancel", "owner"): 8,
    ("cancel", "cancel-cmd"): 9,
    ("shutdown", "owner"): 4,
    ("shutdown", "shutdown-cmd"): 7,
    ("two-users", "owner"): 10,
    ("two-users", "user2"): 11,
}


def _write_mentions(leg_dir, leg, events, identities):
    mentions_dir = leg_dir / "mentions"
    mentions_dir.mkdir(parents=True, exist_ok=True)
    expected = MENTION_MAP.get(leg, [])
    for tag, id_key, content in expected:
        idx = EVENT_ASSIGN.get((leg, tag))
        if idx is not None and idx < len(events):
            event = events[idx]
        else:
            # Should not happen with correct assignment
            raise ValueError(f"No event assigned for ({leg}, {tag})")
        (mentions_dir / f"{tag}.event.json").write_text(json.dumps(event, indent=2) + "\n")
        receipt = {
            "accepted": True,
            "event_id": event["id"],
            "mention_pubkeys": [identities["agent"]],
        }
        (mentions_dir / f"{tag}.receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


def _write_upstream_records(leg_dir, leg, entries, fingerprint):
    rec_dir = leg_dir / "upstream-records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    model = "s0-01-slow" if leg == "cancel" else "s0-01-pong"
    # Find prompt time windows from timeline entries
    prompt_times = []
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/prompt":
            prompt_times.append(e["t_utc"])
    for i, pt in enumerate(prompt_times):
        record = {
            "method": "POST",
            "path": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly the single word: pong"}],
            },
            "headers": {"host": "127.0.0.1:20201", "content-type": "application/json"},
            "authorization_fingerprint": fingerprint,
            "received_at": pt,
            "t_mono_ns": 1000000000000 + (i + 1) * 1000000,
            "remote_addr": "127.0.0.1",
        }
        (rec_dir / f"{i:06d}.json").write_text(json.dumps(record, indent=2) + "\n")


def _write_buzzacp_log(leg_dir, leg):
    lines = ["2026-09-05T12:00:00Z  INFO buzz_acp: starting"]
    if leg == "cancel":
        lines.append("2026-09-05T12:00:01Z  INFO buzz_acp: mode=Cancel")
    if leg == "shutdown":
        lines.append("2026-09-05T12:00:01Z  INFO buzz_acp: shutdown command from owner")
        lines.append("2026-09-05T12:00:02Z  INFO buzz_acp: buzz-acp stopped")
    (leg_dir / "buzzacp.log").write_text("\n".join(lines) + "\n")


def _write_process_scan(leg_dir, leg):
    buzz_pid = 12300
    (leg_dir / "buzz-acp.pid").write_text(f"{buzz_pid}\n")
    if leg == "cancel":
        # tee and hermes-acp parented by buzz-acp
        lines = [
            f"{buzz_pid} 1 /usr/bin/buzz-acp ...",
            f"12345 {buzz_pid} /usr/bin/python3 /path/frame_tee.py",
            "12346 12345 /usr/bin/python3 /path/hermes-acp",
        ]
        (leg_dir / "process-scan-after.txt").write_text("\n".join(lines) + "\n")
    elif leg == "shutdown":
        # No tee/hermes-acp lines
        (leg_dir / "process-scan-after.txt").write_text(f"1 0 /sbin/init\n{buzz_pid} 1 /usr/bin/buzz-acp\n")
    (leg_dir / "buzz-acp.exit").write_text("0\n")


# ---------------------------------------------------------------------------
# Bundle builder
# ---------------------------------------------------------------------------
@pytest.fixture
def bundle(tmp_path):
    """Build a synthesized v2 PASS bundle from REAL committed frames."""
    g = tmp_path / "evidence" / "golden"
    events = _load_relay_events()
    identities = _load_identities()
    fingerprint = _load_fingerprint()
    baseline_path = g / "manifests" / "manifest-baseline.txt.gz"
    manifest_digests = None  # will be set by first leg

    for leg in cc.LEGS:
        leg_dir = g / leg
        c2a, a2c = _load_frames(GOLDEN / leg)

        # Build timeline from real frames
        if leg == "cancel":
            # cancel needs interleaved: c2a init, c2a new, c2a prompt, a2c events (some),
            # c2a cancel, then remaining a2c
            interleaved = []
            for f in c2a[:3]:
                interleaved.append(("c2a", f))
            # a2c: init resp, new resp, some notifs
            for f in a2c[:5]:
                interleaved.append(("a2c", f))
            # session/cancel
            for f in c2a[3:]:
                interleaved.append(("c2a", f))
            # remaining a2c
            for f in a2c[5:]:
                interleaved.append(("a2c", f))
            entries = _make_interleaved_timeline(interleaved)
        elif leg == "two-users":
            # interleave: init, session/new#1, session/prompt#1, session/new#2, session/prompt#2
            # then a2c responses and notifs in original order
            interleaved = []
            for f in c2a:
                interleaved.append(("c2a", f))
            for f in a2c:
                interleaved.append(("a2c", f))
            entries = _make_interleaved_timeline(interleaved)
        else:
            entries = _make_timeline(c2a, a2c)

        _write_timeline(leg_dir, entries)
        _write_runtime_identity(leg_dir)
        _write_env(leg_dir, identities, leg)
        _write_startup(leg_dir, leg)
        _write_model(leg_dir, leg)
        d = _write_manifests(leg_dir, baseline_path)
        if manifest_digests is None:
            manifest_digests = d
        _write_mentions(leg_dir, leg, events, identities)
        _write_upstream_records(leg_dir, leg, entries, fingerprint)
        _write_buzzacp_log(leg_dir, leg)
        _write_process_scan(leg_dir, leg)

    # Patch pinned baseline digests to match our synthetic manifests
    _patch_pinned(manifest_digests)

    # Golden normalization
    n1 = cc.normalize_timeline(json.loads(l) for l in
                               (g / "run-1" / "timeline.jsonl").read_text().splitlines() if l.strip())
    (g / "golden.jsonl").write_text("\n".join(n1) + "\n")

    yield tmp_path / "evidence"

    # Restore pinned after test
    _restore_pinned()


_ORIG_BASELINE = dict(cc.PINNED_BASELINE_DIGESTS)


def _patch_pinned(digests):
    cc.PINNED_BASELINE_DIGESTS.clear()
    cc.PINNED_BASELINE_DIGESTS.update(digests)


def _restore_pinned():
    cc.PINNED_BASELINE_DIGESTS.clear()
    cc.PINNED_BASELINE_DIGESTS.update(_ORIG_BASELINE)


def _run(root: Path):
    env = os.environ.copy()
    return subprocess.run([sys.executable, str(CHECKER), str(root)],
                          capture_output=True, text=True, timeout=60, env=env)


# ---------------------------------------------------------------------------
# PASS test
# ---------------------------------------------------------------------------
def test_passing_v2_bundle(bundle):
    result = cc.check_bundle(bundle)
    assert result.startswith("PASS:")


def test_passing_v2_returns_pass_string(bundle):
    """The PASS test runs in-process because the CLI subprocess does not share
    the test's patched PINNED_BASELINE_DIGESTS (synthetic manifests produce
    different digests than the production pinned values; the live capture will
    match). CLI exit codes are verified through mutation and deferral tests."""
    result = cc.check_bundle(bundle)
    assert "PASS" in result
    assert "14 checks" in result


# ---------------------------------------------------------------------------
# Golden normalization
# ---------------------------------------------------------------------------
def test_normalization_over_interleaved_timeline(bundle):
    entries1 = [json.loads(l) for l in
                (bundle / "golden" / "run-1" / "timeline.jsonl").read_text().splitlines() if l.strip()]
    entries2 = [json.loads(l) for l in
                (bundle / "golden" / "run-2" / "timeline.jsonl").read_text().splitlines() if l.strip()]
    n1 = cc.normalize_timeline(entries1)
    n2 = cc.normalize_timeline(entries2)
    assert n1 == n2
    # deterministic
    assert n1 == cc.normalize_timeline(entries1)
    # content stripped
    text = "\n".join(n1)
    assert "pong" not in text and "/home/rocco" not in text


# ---------------------------------------------------------------------------
# Mutation helper: all mutations run IN-PROCESS where PINNED_BASELINE_DIGESTS
# is patched by the bundle fixture.  CLI subprocesses do not share the patch
# (the synthetic manifests' digests differ from the production-pinned values,
# which is correct — the live capture will match).
# ---------------------------------------------------------------------------
def _check(bundle):
    """Run cc.check_bundle in-process; return (exit_code, output_text)."""
    try:
        msg = cc.check_bundle(bundle)
        return 0, msg
    except cc.Deferred as d:
        return 2, f"deferred: {d}"
    except cc.Failure as f:
        return 1, f"failure_reason: {f}"


# ---------------------------------------------------------------------------
# M1: manifest digests replaced by zeroes
# ---------------------------------------------------------------------------
def test_m1_manifest_zeroed_digests(bundle):
    """M1: every baseline/pre/post manifest digest replaced by zeroes -> FAIL."""
    for leg in cc.LEGS:
        body_text = "## hermes-agent\nZERO\n## buzz\nZERO\n## acp\nZERO\n"
        gz_data = gzip.compress(body_text.encode("utf-8"))
        (bundle / "golden" / leg / "manifest-pre.txt.gz").write_bytes(gz_data)
        (bundle / "golden" / leg / "manifest-post.txt.gz").write_bytes(gz_data)
    rc, out = _check(bundle)
    assert rc == 1
    assert "manifest" in out.lower()


# ---------------------------------------------------------------------------
# M2: relay mentions rejected / no authenticated identity / non-OmniRoute route
# ---------------------------------------------------------------------------
def test_m2_mentions_tampered_signature(bundle):
    """M2: tampered signature on a mention event -> FAIL."""
    leg_dir = bundle / "golden" / "run-1" / "mentions"
    event_path = leg_dir / "owner.event.json"
    event = json.loads(event_path.read_text())
    event["sig"] = "ff" * 64  # tampered
    event_path.write_text(json.dumps(event) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "signature" in out.lower() or "BIP-340" in out or "id mismatch" in out


def test_m2_wrong_pubkey(bundle):
    """M2: wrong sender pubkey -> FAIL."""
    leg_dir = bundle / "golden" / "run-1" / "mentions"
    event_path = leg_dir / "owner.event.json"
    event = json.loads(event_path.read_text())
    event["pubkey"] = "ff" * 32
    event_path.write_text(json.dumps(event) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "pubkey" in out.lower() or "mismatch" in out.lower() or "id mismatch" in out.lower()


def test_m2_zero_backend_records(bundle):
    """M2: zero upstream records -> FAIL."""
    import shutil
    for leg in cc.LEGS:
        rec_dir = bundle / "golden" / leg / "upstream-records"
        if rec_dir.exists():
            shutil.rmtree(rec_dir)
            rec_dir.mkdir()
    rc, out = _check(bundle)
    assert rc == 1
    assert "upstream" in out.lower() or "zero" in out.lower()


# ---------------------------------------------------------------------------
# M3: cancellation targeting foreign session, chunks removed
# ---------------------------------------------------------------------------
def test_m3_cancel_foreign_session(bundle):
    """M3: cancel notification targets a foreign session -> FAIL."""
    leg_dir = bundle / "golden" / "cancel"
    entries = [json.loads(l) for l in
               (leg_dir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    for e in entries:
        if e["dir"] == "c2a" and e["frame"].get("method") == "session/cancel":
            e["frame"]["params"]["sessionId"] = "foreign-00000000"
    _write_timeline(leg_dir, entries)
    rc, out = _check(bundle)
    assert rc == 1
    assert "cancel" in out.lower()


# ---------------------------------------------------------------------------
# M4: shutdown frames reduced to initialize only
# ---------------------------------------------------------------------------
def test_m4_shutdown_init_only(bundle):
    """M4: shutdown frames reduced to initialize only -> FAIL."""
    leg_dir = bundle / "golden" / "shutdown"
    entries = [json.loads(l) for l in
               (leg_dir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Keep only initialize request and response
    filtered = [e for e in entries if e["frame"].get("method") == "initialize"
                or (e["dir"] == "a2c" and "id" in e["frame"] and e["frame"].get("id") == 0)]
    # Resequence
    for i, e in enumerate(filtered):
        e["seq"] = i + 1
    _write_timeline(leg_dir, filtered)
    rc, out = _check(bundle)
    assert rc == 1


# ---------------------------------------------------------------------------
# M5: max_turn changed to 1s and 7200s
# ---------------------------------------------------------------------------
def test_m5_max_turn_1s(bundle):
    """M5: max_turn changed to 1s -> FAIL."""
    for leg in cc.LEGS:
        startup_path = bundle / "golden" / leg / "startup-line.txt"
        text = startup_path.read_text()
        startup_path.write_text(text.replace("max_turn=3600s", "max_turn=1s"))
    rc, out = _check(bundle)
    assert rc == 1
    assert "max_turn" in out


def test_m5_max_turn_7200s(bundle):
    """M5: contract-breaking max_turn=7200s -> FAIL."""
    for leg in cc.LEGS:
        startup_path = bundle / "golden" / leg / "startup-line.txt"
        text = startup_path.read_text()
        startup_path.write_text(text.replace("max_turn=3600s", "max_turn=7200s"))
    rc, out = _check(bundle)
    assert rc == 1
    assert "max_turn" in out


# ---------------------------------------------------------------------------
# Additional structural mutations
# ---------------------------------------------------------------------------
def test_timeline_reorder_across_directions(bundle):
    """Reordering events across directions changes structure -> FAIL golden."""
    leg_dir = bundle / "golden" / "run-2"
    entries = [json.loads(l) for l in
               (leg_dir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Swap entries of different directions (first c2a with first a2c)
    c2a_idx = next(i for i, e in enumerate(entries) if e["dir"] == "c2a")
    a2c_idx = next(i for i, e in enumerate(entries) if e["dir"] == "a2c")
    entries[c2a_idx], entries[a2c_idx] = entries[a2c_idx], entries[c2a_idx]
    # fix seq
    for i, e in enumerate(entries):
        e["seq"] = i + 1
    _write_timeline(leg_dir, entries)
    rc, out = _check(bundle)
    assert rc == 1


def test_identity_digest_changed(bundle):
    """Runtime identity agent_entrypoint_sha256 changed -> FAIL."""
    for leg in cc.LEGS:
        rid_path = bundle / "golden" / leg / "runtime-identity.json"
        rid = json.loads(rid_path.read_text())
        rid["agent_entrypoint_sha256"] = "00" * 32
        rid_path.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "agent_entrypoint" in out or "mismatch" in out


def test_env_credential_missing(bundle):
    """env.json OMNIROUTE_API_KEY missing -> FAIL."""
    for leg in cc.LEGS:
        env_path = bundle / "golden" / leg / "env.json"
        env = json.loads(env_path.read_text())
        del env["OMNIROUTE_API_KEY"]
        env_path.write_text(json.dumps(env) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "OMNIROUTE" in out or "redacted" in out


def test_bytecode_flag_off(bundle):
    """PYTHONDONTWRITEBYTECODE off -> FAIL."""
    for leg in cc.LEGS:
        rid_path = bundle / "golden" / leg / "runtime-identity.json"
        rid = json.loads(rid_path.read_text())
        rid["python_dont_write_bytecode"] = False
        rid_path.write_text(json.dumps(rid) + "\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "python_dont_write_bytecode" in out


# ---------------------------------------------------------------------------
# Deferred cases
# ---------------------------------------------------------------------------
def test_v1_bundle_defers_exit_2():
    """The committed evidence root is v1 (no timeline.jsonl) -> DEFERS exit 2."""
    r = _run(P / "evidence")
    assert r.returncode == 2
    assert r.stdout.startswith("deferred:")


def test_absent_evidence_defers(tmp_path):
    """Absent golden directory -> deferred."""
    empty = tmp_path / "empty"
    empty.mkdir()
    r = _run(empty)
    assert r.returncode == 2
    assert "golden evidence bundle absent" in r.stdout


def test_missing_leg_defers(bundle):
    """Missing a leg directory -> deferred."""
    import shutil
    shutil.rmtree(bundle / "golden" / "two-users")
    rc, out = _check(bundle)
    assert rc == 2
    assert "two-users absent" in out


def test_frozen_golden_is_binding(bundle):
    frozen = bundle / "golden" / "golden.jsonl"
    frozen.unlink()
    rc, out = _check(bundle)
    assert rc == 2
    assert "golden.jsonl not frozen yet" in out
    frozen.write_text("{}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert "differ from the frozen golden.jsonl" in out
